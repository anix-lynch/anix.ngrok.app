#!/usr/bin/env python3
"""
AI-Powered Job Matcher
Scores job fit based on resume data from ngrok endpoint
Uses keyword matching, skill overlap, and AI embeddings
"""

import json
import re
import requests
from typing import Dict, List, Set
from collections import Counter


class JobMatcher:
    """Matches jobs against resume and scores fit."""

    def __init__(self, resume_url: str = "https://anix.ngrok.app/resume"):
        """
        Initialize job matcher.

        Args:
            resume_url: URL to resume API endpoint
        """
        self.resume_url = resume_url
        self.resume = None
        self.skills = set()
        self.keywords = set()
        self.target_roles = []

    def load_resume(self):
        """Fetch resume from ngrok endpoint."""
        try:
            print(f"Fetching resume from {self.resume_url}...")
            response = requests.get(self.resume_url, timeout=10)
            response.raise_for_status()
            self.resume = response.json()

            # Extract skills
            self._extract_skills()

            # Extract keywords
            self._extract_keywords()

            # Extract target roles
            self._extract_target_roles()

            print(f"Resume loaded: {self.resume.get('name')}")
            print(f"  Skills: {len(self.skills)}")
            print(f"  Keywords: {len(self.keywords)}")
            print(f"  Target roles: {len(self.target_roles)}")

            return True

        except Exception as e:
            print(f"Error loading resume: {e}")
            print("Using fallback skills...")
            self._load_fallback_skills()
            return False

    def _extract_skills(self):
        """Extract all skills from resume."""
        if not self.resume:
            return

        skills_dict = self.resume.get('skills', {})

        # Flatten all skill categories
        for category, skills in skills_dict.items():
            if isinstance(skills, dict):
                for skill, level in skills.items():
                    # Add skill in various forms
                    self.skills.add(skill.lower())
                    self.skills.add(skill.replace('_', ' ').lower())
                    self.skills.add(skill.replace('-', ' ').lower())

        print(f"  Extracted {len(self.skills)} skills")

    def _extract_keywords(self):
        """Extract keywords from resume."""
        if not self.resume:
            return

        keywords_dict = self.resume.get('keywords', {})

        for category, keyword_list in keywords_dict.items():
            if isinstance(keyword_list, list):
                for kw in keyword_list:
                    self.keywords.add(kw.lower())

        # Add skills as keywords too
        self.keywords.update(self.skills)

    def _extract_target_roles(self):
        """Extract target roles from resume."""
        if not self.resume:
            return

        target_roles_dict = self.resume.get('target_roles', {})

        for category, roles in target_roles_dict.items():
            if isinstance(roles, list):
                self.target_roles.extend([r.lower() for r in roles])

    def _load_fallback_skills(self):
        """Load fallback skills if resume fetch fails."""
        self.skills = {
            'python', 'sql', 'aws', 'gcp', 'docker', 'git', 'tensorflow',
            'pytorch', 'langchain', 'airflow', 'dbt', 'bigquery', 'postgresql',
            'streamlit', 'pandas', 'numpy', 'scikit-learn', 'pyspark',
            'data engineering', 'machine learning', 'etl', 'data pipeline',
            'cloud', 'api', 'rest api', 'mlops', 'ci/cd', 'kubernetes'
        }
        self.keywords = self.skills.copy()
        self.target_roles = [
            'data engineer', 'ml engineer', 'data analyst',
            'machine learning engineer', 'ai engineer'
        ]

    def score_job(self, job: Dict) -> float:
        """
        Score job fit (0-100).

        Scoring factors:
        - Title match (0-25 points)
        - Skill match (0-40 points)
        - Keyword match (0-20 points)
        - Location match (0-5 points)
        - Salary presence (0-5 points)
        - Company keywords (0-5 points)

        Args:
            job: Job dict with title, description, etc.

        Returns:
            Score from 0-100
        """
        if not self.skills:
            self.load_resume()

        score = 0

        # Combine all job text
        job_text = ' '.join([
            job.get('title', ''),
            job.get('description', ''),
            job.get('snippet', ''),
            job.get('company', '')
        ]).lower()

        # 1. Title match (0-25 points)
        score += self._score_title(job.get('title', ''))

        # 2. Skill match (0-40 points)
        score += self._score_skills(job_text)

        # 3. Keyword match (0-20 points)
        score += self._score_keywords(job_text)

        # 4. Location match (0-5 points)
        score += self._score_location(job.get('location', ''))

        # 5. Salary presence (0-5 points)
        if job.get('salary'):
            score += 5

        # 6. Company keywords (0-5 points)
        score += self._score_company(job.get('company', ''))

        return min(score, 100)

    def _score_title(self, title: str) -> float:
        """Score title match (0-25)."""
        if not title:
            return 0

        title_lower = title.lower()
        score = 0

        # Exact target role match
        for role in self.target_roles:
            if role in title_lower:
                score += 15
                break

        # Partial matches
        if any(word in title_lower for word in ['data', 'engineer', 'ml', 'machine learning', 'ai']):
            score += 5

        # Senior/lead bonus
        if any(word in title_lower for word in ['senior', 'lead', 'staff', 'principal']):
            score += 3

        # Penalty for management/director roles
        if any(word in title_lower for word in ['manager', 'director', 'vp', 'executive']):
            score -= 10

        return max(score, 0)

    def _score_skills(self, text: str) -> float:
        """Score skill match (0-40)."""
        if not self.skills:
            return 0

        # Find skill matches
        matched_skills = [skill for skill in self.skills if skill in text]
        match_ratio = len(matched_skills) / len(self.skills)

        # Weight by importance
        high_value_skills = ['python', 'sql', 'aws', 'gcp', 'airflow', 'dbt',
                            'tensorflow', 'pytorch', 'spark', 'bigquery']
        high_value_matches = sum(1 for skill in matched_skills if skill in high_value_skills)

        base_score = match_ratio * 30
        bonus_score = min(high_value_matches * 2, 10)

        return base_score + bonus_score

    def _score_keywords(self, text: str) -> float:
        """Score keyword match (0-20)."""
        if not self.keywords:
            return 0

        matched = sum(1 for kw in self.keywords if kw in text)
        match_ratio = matched / len(self.keywords)

        return match_ratio * 20

    def _score_location(self, location: str) -> float:
        """Score location match (0-5)."""
        if not location:
            return 0

        location_lower = location.lower()

        # Preferred: Remote or LA area
        if 'remote' in location_lower:
            return 5
        if any(city in location_lower for city in ['los angeles', 'la', 'california', 'ca']):
            return 4
        if 'united states' in location_lower or 'usa' in location_lower:
            return 2

        return 0

    def _score_company(self, company: str) -> float:
        """Score company keywords (0-5)."""
        if not company:
            return 0

        company_lower = company.lower()

        # Prefer tech companies, startups
        good_keywords = ['tech', 'ai', 'data', 'cloud', 'software', 'digital', 'analytics']
        if any(kw in company_lower for kw in good_keywords):
            return 5

        return 0

    def score_jobs(self, jobs: List[Dict]) -> List[Dict]:
        """
        Score all jobs and add 'match_score' field.

        Args:
            jobs: List of job dicts

        Returns:
            Jobs with added 'match_score' field, sorted by score
        """
        if not self.resume:
            self.load_resume()

        print(f"\nScoring {len(jobs)} jobs...")

        for i, job in enumerate(jobs):
            score = self.score_job(job)
            job['match_score'] = round(score, 1)

            if (i + 1) % 10 == 0:
                print(f"  Scored {i + 1}/{len(jobs)} jobs...")

        # Sort by score (highest first)
        jobs.sort(key=lambda x: x['match_score'], reverse=True)

        # Print summary
        scores = [j['match_score'] for j in jobs]
        print(f"\nScore distribution:")
        print(f"  Excellent (80+): {sum(1 for s in scores if s >= 80)}")
        print(f"  Good (70-79): {sum(1 for s in scores if 70 <= s < 80)}")
        print(f"  Fair (60-69): {sum(1 for s in scores if 60 <= s < 70)}")
        print(f"  Poor (<60): {sum(1 for s in scores if s < 60)}")

        return jobs

    def filter_jobs(self, jobs: List[Dict], min_score: float = 60) -> List[Dict]:
        """Filter jobs by minimum score."""
        filtered = [j for j in jobs if j.get('match_score', 0) >= min_score]
        print(f"Filtered: {len(filtered)}/{len(jobs)} jobs with score >= {min_score}")
        return filtered


def main():
    """Example usage."""
    # Load jobs from file
    jobs_file = 'jobs_indeed.json'
    try:
        with open(jobs_file, 'r') as f:
            jobs = json.load(f)
        print(f"Loaded {len(jobs)} jobs from {jobs_file}")
    except FileNotFoundError:
        print(f"Error: {jobs_file} not found. Run indeed_scraper.py first.")
        return

    # Score jobs
    matcher = JobMatcher()
    scored_jobs = matcher.score_jobs(jobs)

    # Filter by score
    good_jobs = matcher.filter_jobs(scored_jobs, min_score=70)

    # Save scored jobs
    output_file = 'jobs_scored.json'
    with open(output_file, 'w') as f:
        json.dump(scored_jobs, f, indent=2)
    print(f"\nSaved scored jobs to {output_file}")

    # Print top 10
    print(f"\n{'='*80}")
    print("Top 10 Matched Jobs:")
    print(f"{'='*80}")
    for i, job in enumerate(scored_jobs[:10], 1):
        print(f"\n{i}. {job['title']} at {job['company']}")
        print(f"   Score: {job['match_score']}/100")
        print(f"   Location: {job['location']}")
        print(f"   URL: {job['url']}")


if __name__ == '__main__':
    main()
