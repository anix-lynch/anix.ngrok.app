#!/usr/bin/env python3
"""
ATS Detection and Classification System
Detects which ATS system a job posting uses and classifies automation difficulty
"""

import re
import json
from typing import Dict, List, Tuple
from urllib.parse import urlparse


class ATSDetector:
    """Detects ATS system from job URL or HTML content."""

    # ATS signature patterns
    ATS_PATTERNS = {
        # Tier 1: Low Friction (Easy automation)
        'jazzhr': {
            'domains': ['applytojob.com', 'jazzhr.com'],
            'url_patterns': [r'applytojob\.com', r'jazzhr\.com'],
            'html_patterns': [r'JazzHR', r'jazz-hr'],
            'tier': 1,
            'success_rate': 0.75
        },
        'bamboohr': {
            'domains': ['bamboohr.com'],
            'url_patterns': [r'\.bamboohr\.com'],
            'html_patterns': [r'BambooHR', r'bamboo-hr'],
            'tier': 1,
            'success_rate': 0.70
        },
        'recruitee': {
            'domains': ['recruitee.com'],
            'url_patterns': [r'recruitee\.com'],
            'html_patterns': [r'recruitee', r'Recruitee'],
            'tier': 1,
            'success_rate': 0.75
        },
        'manatal': {
            'domains': ['manatal.com'],
            'url_patterns': [r'manatal\.com'],
            'html_patterns': [r'Manatal', r'manatal'],
            'tier': 1,
            'success_rate': 0.70
        },
        'pinpoint': {
            'domains': ['pinpointhq.com'],
            'url_patterns': [r'pinpointhq\.com'],
            'html_patterns': [r'Pinpoint', r'pinpoint-hq'],
            'tier': 1,
            'success_rate': 0.65
        },

        # Tier 2: Medium Friction (Smart automation needed)
        'lever': {
            'domains': ['lever.co', 'jobs.lever.co'],
            'url_patterns': [r'lever\.co', r'jobs\.lever\.co'],
            'html_patterns': [r'Lever', r'lever-portal'],
            'tier': 2,
            'success_rate': 0.55
        },
        'greenhouse': {
            'domains': ['greenhouse.io', 'boards.greenhouse.io'],
            'url_patterns': [r'greenhouse\.io', r'boards\.greenhouse\.io'],
            'html_patterns': [r'Greenhouse', r'greenhouse-portal'],
            'tier': 2,
            'success_rate': 0.60
        },
        'ashby': {
            'domains': ['ashbyhq.com'],
            'url_patterns': [r'ashbyhq\.com', r'jobs\.ashbyhq\.com'],
            'html_patterns': [r'Ashby', r'ashby-portal'],
            'tier': 2,
            'success_rate': 0.50
        },
        'bullhorn': {
            'domains': ['bullhornstaffing.com'],
            'url_patterns': [r'bullhorn'],
            'html_patterns': [r'Bullhorn', r'bullhorn-portal'],
            'tier': 2,
            'success_rate': 0.50
        },
        'trakstar': {
            'domains': ['trakstar.com'],
            'url_patterns': [r'trakstar\.com', r'hire\.trakstar'],
            'html_patterns': [r'Trakstar', r'trakstar-hire'],
            'tier': 2,
            'success_rate': 0.55
        },

        # Tier 3: High Friction (Difficult automation)
        'workday': {
            'domains': ['myworkdayjobs.com'],
            'url_patterns': [r'myworkdayjobs\.com', r'workday\.com'],
            'html_patterns': [r'Workday', r'workday-portal'],
            'tier': 3,
            'success_rate': 0.35
        },
        'icims': {
            'domains': ['icims.com'],
            'url_patterns': [r'icims\.com', r'careers-icims'],
            'html_patterns': [r'iCIMS', r'icims-portal'],
            'tier': 3,
            'success_rate': 0.30
        },
        'taleo': {
            'domains': ['taleo.net'],
            'url_patterns': [r'taleo\.net', r'oracle\.com/taleo'],
            'html_patterns': [r'Taleo', r'taleo-portal', r'Oracle Taleo'],
            'tier': 3,
            'success_rate': 0.25
        },
        'smartrecruiters': {
            'domains': ['smartrecruiters.com'],
            'url_patterns': [r'smartrecruiters\.com', r'jobs\.smartrecruiters'],
            'html_patterns': [r'SmartRecruiters', r'smartrecruiters-portal'],
            'tier': 3,
            'success_rate': 0.35
        },
        'successfactors': {
            'domains': ['successfactors.com', 'successfactors.eu'],
            'url_patterns': [r'successfactors\.com', r'successfactors\.eu', r'sap\.com/successfactors'],
            'html_patterns': [r'SuccessFactors', r'SAP SuccessFactors'],
            'tier': 3,
            'success_rate': 0.30
        },
        'jobvite': {
            'domains': ['jobvite.com'],
            'url_patterns': [r'jobvite\.com', r'jobs\.jobvite'],
            'html_patterns': [r'Jobvite', r'jobvite-portal'],
            'tier': 3,
            'success_rate': 0.40
        },
        'ukgpro': {
            'domains': ['ultipro.com'],
            'url_patterns': [r'ultipro\.com', r'ukg\.com'],
            'html_patterns': [r'UKG Pro', r'UltiPro'],
            'tier': 3,
            'success_rate': 0.30
        },
        'ceridian': {
            'domains': ['dayforcehcm.com'],
            'url_patterns': [r'dayforcehcm\.com', r'dayforce\.com'],
            'html_patterns': [r'Ceridian', r'Dayforce'],
            'tier': 3,
            'success_rate': 0.30
        },
        'avature': {
            'domains': ['avature.net'],
            'url_patterns': [r'avature\.net', r'careers-avature'],
            'html_patterns': [r'Avature', r'avature-portal'],
            'tier': 3,
            'success_rate': 0.35
        }
    }

    def detect_from_url(self, url: str) -> Tuple[str, int, float]:
        """
        Detect ATS from job URL.

        Returns:
            (ats_name, tier, success_rate)
        """
        url_lower = url.lower()
        domain = urlparse(url).netloc.lower()

        for ats_name, patterns in self.ATS_PATTERNS.items():
            # Check domain match
            if any(d in domain for d in patterns['domains']):
                return ats_name, patterns['tier'], patterns['success_rate']

            # Check URL pattern match
            if any(re.search(pattern, url_lower) for pattern in patterns['url_patterns']):
                return ats_name, patterns['tier'], patterns['success_rate']

        # Unknown ATS - default to Tier 3 (safest)
        return 'unknown', 3, 0.20

    def detect_from_html(self, html: str, url: str = None) -> Tuple[str, int, float]:
        """
        Detect ATS from HTML content.

        Returns:
            (ats_name, tier, success_rate)
        """
        # Try URL first if provided
        if url:
            ats, tier, rate = self.detect_from_url(url)
            if ats != 'unknown':
                return ats, tier, rate

        # Check HTML patterns
        for ats_name, patterns in self.ATS_PATTERNS.items():
            if any(re.search(pattern, html, re.IGNORECASE) for pattern in patterns['html_patterns']):
                return ats_name, patterns['tier'], patterns['success_rate']

        return 'unknown', 3, 0.20

    def classify_job(self, job: Dict) -> Dict:
        """
        Classify a job dict with ATS info.

        Args:
            job: Dict with 'url' and optionally 'html' keys

        Returns:
            Job dict with added 'ats', 'tier', 'success_rate' keys
        """
        url = job.get('url', '')
        html = job.get('html', '')

        if html:
            ats, tier, rate = self.detect_from_html(html, url)
        else:
            ats, tier, rate = self.detect_from_url(url)

        job['ats'] = ats
        job['tier'] = tier
        job['success_rate'] = rate
        job['automation_strategy'] = self._get_strategy(tier)

        return job

    def _get_strategy(self, tier: int) -> str:
        """Get automation strategy for tier."""
        strategies = {
            1: 'full_auto',
            2: 'smart_auto',
            3: 'semi_manual'
        }
        return strategies.get(tier, 'manual')

    def get_tier_stats(self) -> Dict:
        """Get statistics about ATS tiers."""
        tier_counts = {1: 0, 2: 0, 3: 0}
        for patterns in self.ATS_PATTERNS.values():
            tier_counts[patterns['tier']] += 1

        return {
            'total_ats': len(self.ATS_PATTERNS),
            'tier_1_count': tier_counts[1],
            'tier_2_count': tier_counts[2],
            'tier_3_count': tier_counts[3],
            'tier_1_avg_success': sum(p['success_rate'] for p in self.ATS_PATTERNS.values() if p['tier'] == 1) / tier_counts[1],
            'tier_2_avg_success': sum(p['success_rate'] for p in self.ATS_PATTERNS.values() if p['tier'] == 2) / tier_counts[2],
            'tier_3_avg_success': sum(p['success_rate'] for p in self.ATS_PATTERNS.values() if p['tier'] == 3) / tier_counts[3]
        }


def main():
    """Test ATS detector."""
    detector = ATSDetector()

    # Test URLs
    test_urls = [
        'https://jobs.lever.co/company/position',
        'https://boards.greenhouse.io/company/jobs/123',
        'https://company.applytojob.com/apply/xyz',
        'https://myworkdayjobs.com/company',
        'https://careers.smartrecruiters.com/company',
    ]

    print("ATS Detection Test\n" + "="*50)
    for url in test_urls:
        ats, tier, rate = detector.detect_from_url(url)
        print(f"\nURL: {url}")
        print(f"  ATS: {ats.upper()}")
        print(f"  Tier: {tier}")
        print(f"  Success Rate: {rate*100:.0f}%")

    print("\n" + "="*50)
    print("\nTier Statistics:")
    stats = detector.get_tier_stats()
    for key, value in stats.items():
        print(f"  {key}: {value if isinstance(value, int) else f'{value:.2%}'}")


if __name__ == '__main__':
    main()
