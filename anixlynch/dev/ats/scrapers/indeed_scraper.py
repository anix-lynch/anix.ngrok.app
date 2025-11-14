#!/usr/bin/env python3
"""
Indeed Job Scraper
Scrapes job listings from Indeed for Data Engineering roles
Uses Playwright for JavaScript rendering and anti-bot measures
"""

import asyncio
import json
import time
import random
from typing import List, Dict
from pathlib import Path
from datetime import datetime
from playwright.async_api import async_playwright, Page, Browser


class IndeedScraper:
    """Scrapes job listings from Indeed."""

    BASE_URL = "https://www.indeed.com"

    def __init__(self, headless: bool = True, slow_mo: int = 100):
        """
        Initialize Indeed scraper.

        Args:
            headless: Run browser in headless mode
            slow_mo: Slow down operations by N milliseconds
        """
        self.headless = headless
        self.slow_mo = slow_mo
        self.jobs = []

    async def scrape_jobs(
        self,
        keywords: str = "data engineer",
        location: str = "Remote",
        limit: int = 100,
        date_posted: str = "7"  # 1, 3, 7, 14 days
    ) -> List[Dict]:
        """
        Scrape job listings from Indeed.

        Args:
            keywords: Job search keywords
            location: Job location
            limit: Maximum number of jobs to scrape
            date_posted: Jobs posted in last N days

        Returns:
            List of job dicts
        """
        async with async_playwright() as p:
            browser = await self._launch_browser(p)
            page = await browser.new_page()

            # Build search URL
            search_url = self._build_search_url(keywords, location, date_posted)
            print(f"Searching: {search_url}")

            try:
                await self._search_jobs(page, search_url, limit)
            finally:
                await browser.close()

        return self.jobs

    async def _launch_browser(self, playwright) -> Browser:
        """Launch browser with anti-detection measures."""
        return await playwright.chromium.launch(
            headless=self.headless,
            slow_mo=self.slow_mo,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
                '--no-sandbox'
            ]
        )

    def _build_search_url(self, keywords: str, location: str, date_posted: str) -> str:
        """Build Indeed search URL."""
        keywords_encoded = keywords.replace(' ', '+')
        location_encoded = location.replace(' ', '+')
        return f"{self.BASE_URL}/jobs?q={keywords_encoded}&l={location_encoded}&fromage={date_posted}"

    async def _search_jobs(self, page: Page, url: str, limit: int):
        """Search and paginate through job listings."""
        await page.goto(url, wait_until='networkidle')

        # Random delay to appear human
        await asyncio.sleep(random.uniform(2, 4))

        jobs_scraped = 0
        page_num = 1

        while jobs_scraped < limit:
            print(f"\nScraping page {page_num}...")

            # Extract job cards from current page
            job_cards = await self._extract_job_cards(page)

            if not job_cards:
                print("No more jobs found")
                break

            for card in job_cards:
                if jobs_scraped >= limit:
                    break

                job_data = await self._extract_job_details(page, card)
                if job_data:
                    self.jobs.append(job_data)
                    jobs_scraped += 1
                    print(f"  [{jobs_scraped}/{limit}] {job_data['title']} at {job_data['company']}")

                # Random delay between jobs
                await asyncio.sleep(random.uniform(0.5, 1.5))

            # Navigate to next page
            if jobs_scraped < limit:
                has_next = await self._go_to_next_page(page)
                if not has_next:
                    break
                page_num += 1
                await asyncio.sleep(random.uniform(2, 4))

        print(f"\nTotal jobs scraped: {jobs_scraped}")

    async def _extract_job_cards(self, page: Page) -> List:
        """Extract job card elements from page."""
        return await page.query_selector_all('div.job_seen_beacon')

    async def _extract_job_details(self, page: Page, card) -> Dict:
        """Extract job details from a job card."""
        try:
            # Extract basic info from card
            title_elem = await card.query_selector('h2.jobTitle span')
            title = await title_elem.inner_text() if title_elem else 'N/A'

            company_elem = await card.query_selector('span[data-testid="company-name"]')
            company = await company_elem.inner_text() if company_elem else 'N/A'

            location_elem = await card.query_selector('div[data-testid="text-location"]')
            location = await location_elem.inner_text() if location_elem else 'N/A'

            # Get job link
            link_elem = await card.query_selector('h2.jobTitle a')
            job_url = await link_elem.get_attribute('href') if link_elem else None
            if job_url and not job_url.startswith('http'):
                job_url = self.BASE_URL + job_url

            # Extract salary if available
            salary_elem = await card.query_selector('div.salary-snippet-container')
            salary = await salary_elem.inner_text() if salary_elem else None

            # Extract job snippet/description
            snippet_elem = await card.query_selector('div.job-snippet')
            snippet = await snippet_elem.inner_text() if snippet_elem else ''

            # Get full job description by clicking (optional - can be slow)
            # description = await self._get_full_description(page, link_elem)

            return {
                'title': title.strip(),
                'company': company.strip(),
                'location': location.strip(),
                'url': job_url,
                'salary': salary.strip() if salary else None,
                'snippet': snippet.strip(),
                'description': snippet.strip(),  # Use snippet for now
                'scraped_at': datetime.now().isoformat(),
                'source': 'indeed'
            }

        except Exception as e:
            print(f"    Error extracting job: {e}")
            return None

    async def _get_full_description(self, page: Page, link_elem) -> str:
        """Click job and get full description (slower but more complete)."""
        try:
            await link_elem.click()
            await asyncio.sleep(random.uniform(1, 2))

            desc_elem = await page.query_selector('div#jobDescriptionText')
            if desc_elem:
                return await desc_elem.inner_text()
        except Exception as e:
            print(f"    Error getting description: {e}")

        return ''

    async def _go_to_next_page(self, page: Page) -> bool:
        """Navigate to next page of results."""
        try:
            next_button = await page.query_selector('a[data-testid="pagination-page-next"]')
            if next_button:
                await next_button.click()
                await page.wait_for_load_state('networkidle')
                return True
        except Exception as e:
            print(f"  No next page or error: {e}")

        return False

    def save_jobs(self, filepath: str):
        """Save scraped jobs to JSON file."""
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.jobs, f, indent=2, ensure_ascii=False)
        print(f"\nSaved {len(self.jobs)} jobs to {filepath}")


async def main():
    """Example usage."""
    scraper = IndeedScraper(headless=False, slow_mo=50)

    # Scrape Data Engineer jobs
    jobs = await scraper.scrape_jobs(
        keywords="data engineer",
        location="Remote",
        limit=50,
        date_posted="7"
    )

    # Save to file
    output_file = 'jobs_indeed.json'
    scraper.save_jobs(output_file)

    # Print summary
    print(f"\n{'='*50}")
    print(f"Total jobs: {len(jobs)}")
    print(f"Companies: {len(set(j['company'] for j in jobs))}")
    print(f"With salary: {sum(1 for j in jobs if j['salary'])}")


if __name__ == '__main__':
    asyncio.run(main())
