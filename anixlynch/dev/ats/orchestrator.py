#!/usr/bin/env python3
"""
Job Application Orchestrator
Master script that coordinates all components:
1. Scrape jobs
2. Detect ATS
3. Score jobs
4. Apply automatically
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from scrapers.indeed_scraper import IndeedScraper
from ats_detector import ATSDetector
from job_matcher import JobMatcher
from automation.tier1_automation import Tier1Automation
from tracker import ApplicationTracker


class JobApplicationOrchestrator:
    """Orchestrates end-to-end job application pipeline."""

    def __init__(
        self,
        resume_url: str = "https://anix.ngrok.app/resume",
        output_dir: str = "output"
    ):
        """
        Initialize orchestrator.

        Args:
            resume_url: URL to resume API
            output_dir: Directory for output files
        """
        self.resume_url = resume_url
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)

        self.detector = ATSDetector()
        self.matcher = JobMatcher(resume_url)
        self.tracker = ApplicationTracker(
            db_path=str(self.output_dir / 'applications.db')
        )

    async def run_full_pipeline(
        self,
        keywords: str = "data engineer",
        location: str = "Remote",
        scrape_limit: int = 200,
        min_match_score: float = 70,
        tier1_max_apps: int = 50,
        dry_run: bool = True
    ):
        """
        Run full application pipeline.

        Args:
            keywords: Job search keywords
            location: Job location
            scrape_limit: How many jobs to scrape
            min_match_score: Minimum job match score
            tier1_max_apps: Max Tier 1 applications
            dry_run: If True, don't actually submit
        """
        print(f"\n{'='*80}")
        print(f"Job Application Pipeline - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*80}")

        # Step 1: Scrape jobs
        print(f"\n[1/5] Scraping jobs from Indeed...")
        jobs = await self._scrape_jobs(keywords, location, scrape_limit)

        if not jobs:
            print("No jobs scraped. Exiting.")
            return

        # Step 2: Detect ATS
        print(f"\n[2/5] Detecting ATS systems...")
        jobs = self._classify_ats(jobs)

        # Step 3: Score jobs
        print(f"\n[3/5] Scoring job matches...")
        jobs = self._score_jobs(jobs)

        # Step 4: Filter and prioritize
        print(f"\n[4/5] Filtering jobs (score >= {min_match_score})...")
        good_jobs = [j for j in jobs if j['match_score'] >= min_match_score]
        print(f"Found {len(good_jobs)} jobs matching criteria")

        # Save all jobs
        self._save_jobs(good_jobs, 'jobs_processed.json')

        # Add to tracker
        for job in good_jobs:
            self.tracker.add_application(job)

        # Step 5: Apply to jobs
        if not dry_run:
            print(f"\n[5/5] Applying to jobs...")
            await self._apply_to_jobs(good_jobs, tier1_max_apps)
        else:
            print(f"\n[5/5] DRY RUN - Skipping applications")
            print(f"Would apply to {min(len(good_jobs), tier1_max_apps)} Tier 1 jobs")

        # Print final stats
        print(f"\n{'='*80}")
        self.tracker.print_stats()
        print(f"\n✓ Pipeline complete!")
        print(f"Output directory: {self.output_dir}")

    async def _scrape_jobs(self, keywords: str, location: str, limit: int):
        """Scrape jobs from Indeed."""
        scraper = IndeedScraper(headless=True, slow_mo=50)
        jobs = await scraper.scrape_jobs(keywords, location, limit)

        # Save raw jobs
        self._save_jobs(jobs, 'jobs_raw.json')

        return jobs

    def _classify_ats(self, jobs):
        """Classify ATS for all jobs."""
        for job in jobs:
            self.detector.classify_job(job)

        # Print ATS distribution
        ats_counts = {}
        tier_counts = {1: 0, 2: 0, 3: 0}

        for job in jobs:
            ats = job.get('ats', 'unknown')
            tier = job.get('tier', 3)

            ats_counts[ats] = ats_counts.get(ats, 0) + 1
            tier_counts[tier] += 1

        print(f"\nATS Distribution:")
        for ats, count in sorted(ats_counts.items(), key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {ats}: {count}")

        print(f"\nTier Distribution:")
        for tier, count in tier_counts.items():
            print(f"  Tier {tier}: {count}")

        # Save classified jobs
        self._save_jobs(jobs, 'jobs_classified.json')

        return jobs

    def _score_jobs(self, jobs):
        """Score all jobs."""
        jobs = self.matcher.score_jobs(jobs)

        # Save scored jobs
        self._save_jobs(jobs, 'jobs_scored.json')

        return jobs

    async def _apply_to_jobs(self, jobs, max_apps):
        """Apply to jobs using automation."""
        # Get resume data
        import requests
        try:
            response = requests.get(self.resume_url)
            resume_data = response.json()
        except Exception as e:
            print(f"Error fetching resume: {e}")
            return

        # Tier 1 automation
        tier1_jobs = [j for j in jobs if j.get('tier') == 1]

        if tier1_jobs:
            print(f"\nTier 1 automation ({len(tier1_jobs)} jobs)...")
            automation = Tier1Automation(resume_data, headless=False)
            await automation.apply_to_jobs(tier1_jobs, max_apps)

            # Update tracker
            for app in automation.applications:
                self.tracker.mark_submitted(app['job_url'])

            # Save log
            automation.save_applications(
                str(self.output_dir / 'applications_tier1.json')
            )

        # Tier 2 and 3 would be handled separately

    def _save_jobs(self, jobs, filename):
        """Save jobs to JSON file."""
        filepath = self.output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(jobs, f, indent=2, ensure_ascii=False)
        print(f"  Saved to {filepath}")


async def main():
    """Run orchestrator with example config."""
    import argparse

    parser = argparse.ArgumentParser(description='Job Application Automation')
    parser.add_argument('--keywords', default='data engineer', help='Job search keywords')
    parser.add_argument('--location', default='Remote', help='Job location')
    parser.add_argument('--scrape-limit', type=int, default=100, help='Jobs to scrape')
    parser.add_argument('--min-score', type=float, default=70, help='Minimum match score')
    parser.add_argument('--tier1-apps', type=int, default=25, help='Max Tier 1 applications')
    parser.add_argument('--dry-run', action='store_true', help='Dry run (no actual applications)')
    parser.add_argument('--live', action='store_true', help='Live run (actually submit)')

    args = parser.parse_args()

    orchestrator = JobApplicationOrchestrator()

    await orchestrator.run_full_pipeline(
        keywords=args.keywords,
        location=args.location,
        scrape_limit=args.scrape_limit,
        min_match_score=args.min_score,
        tier1_max_apps=args.tier1_apps,
        dry_run=not args.live
    )


if __name__ == '__main__':
    asyncio.run(main())
