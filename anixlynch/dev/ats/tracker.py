#!/usr/bin/env python3
"""
Application Tracker
SQLite-based tracking system for job applications
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
from pathlib import Path


class ApplicationTracker:
    """Tracks job applications in SQLite database."""

    def __init__(self, db_path: str = 'applications.db'):
        """Initialize tracker with database."""
        self.db_path = db_path
        self.conn = None
        self._init_db()

    def _init_db(self):
        """Create database and tables."""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row

        cursor = self.conn.cursor()

        # Applications table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS applications (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_url TEXT UNIQUE NOT NULL,
                job_title TEXT,
                company TEXT,
                location TEXT,
                ats TEXT,
                tier INTEGER,
                match_score REAL,
                status TEXT DEFAULT 'pending',
                applied_at TEXT,
                response_at TEXT,
                notes TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Status history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS status_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                application_id INTEGER,
                old_status TEXT,
                new_status TEXT,
                changed_at TEXT DEFAULT CURRENT_TIMESTAMP,
                notes TEXT,
                FOREIGN KEY (application_id) REFERENCES applications(id)
            )
        ''')

        # Stats table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS daily_stats (
                date TEXT PRIMARY KEY,
                applications_submitted INTEGER DEFAULT 0,
                tier1_submitted INTEGER DEFAULT 0,
                tier2_submitted INTEGER DEFAULT 0,
                tier3_submitted INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0
            )
        ''')

        self.conn.commit()

    def add_application(self, job: Dict) -> int:
        """
        Add new application.

        Args:
            job: Job dict with url, title, company, etc.

        Returns:
            Application ID
        """
        cursor = self.conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO applications (
                    job_url, job_title, company, location,
                    ats, tier, match_score, status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                job.get('url'),
                job.get('title'),
                job.get('company'),
                job.get('location'),
                job.get('ats'),
                job.get('tier'),
                job.get('match_score'),
                'pending'
            ))

            self.conn.commit()
            return cursor.lastrowid

        except sqlite3.IntegrityError:
            # Already exists
            return self.get_application_id(job['url'])

    def update_status(self, app_id: int, new_status: str, notes: str = None):
        """Update application status."""
        cursor = self.conn.cursor()

        # Get old status
        cursor.execute('SELECT status FROM applications WHERE id = ?', (app_id,))
        row = cursor.fetchone()
        old_status = row['status'] if row else None

        # Update status
        cursor.execute('''
            UPDATE applications
            SET status = ?, applied_at = ?
            WHERE id = ?
        ''', (new_status, datetime.now().isoformat(), app_id))

        # Record history
        cursor.execute('''
            INSERT INTO status_history (application_id, old_status, new_status, notes)
            VALUES (?, ?, ?, ?)
        ''', (app_id, old_status, new_status, notes))

        self.conn.commit()

    def get_application_id(self, job_url: str) -> Optional[int]:
        """Get application ID by job URL."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT id FROM applications WHERE job_url = ?', (job_url,))
        row = cursor.fetchone()
        return row['id'] if row else None

    def get_stats(self) -> Dict:
        """Get overall statistics."""
        cursor = self.conn.cursor()

        # Total applications
        cursor.execute('SELECT COUNT(*) as total FROM applications')
        total = cursor.fetchone()['total']

        # By status
        cursor.execute('''
            SELECT status, COUNT(*) as count
            FROM applications
            GROUP BY status
        ''')
        status_counts = {row['status']: row['count'] for row in cursor.fetchall()}

        # By tier
        cursor.execute('''
            SELECT tier, COUNT(*) as count
            FROM applications
            GROUP BY tier
        ''')
        tier_counts = {row['tier']: row['count'] for row in cursor.fetchall()}

        # By ATS
        cursor.execute('''
            SELECT ats, COUNT(*) as count
            FROM applications
            GROUP BY ats
            ORDER BY count DESC
            LIMIT 10
        ''')
        ats_counts = {row['ats']: row['count'] for row in cursor.fetchall()}

        # Success rate
        submitted = status_counts.get('submitted', 0)
        success_rate = (submitted / total * 100) if total > 0 else 0

        return {
            'total_applications': total,
            'status_counts': status_counts,
            'tier_counts': tier_counts,
            'ats_counts': ats_counts,
            'success_rate': success_rate
        }

    def get_pending(self, tier: int = None, limit: int = 100) -> List[Dict]:
        """Get pending applications."""
        cursor = self.conn.cursor()

        if tier:
            cursor.execute('''
                SELECT * FROM applications
                WHERE status = 'pending' AND tier = ?
                ORDER BY match_score DESC
                LIMIT ?
            ''', (tier, limit))
        else:
            cursor.execute('''
                SELECT * FROM applications
                WHERE status = 'pending'
                ORDER BY match_score DESC
                LIMIT ?
            ''', (limit,))

        return [dict(row) for row in cursor.fetchall()]

    def mark_submitted(self, job_url: str):
        """Mark application as submitted."""
        app_id = self.get_application_id(job_url)
        if app_id:
            self.update_status(app_id, 'submitted')

    def mark_failed(self, job_url: str, reason: str = None):
        """Mark application as failed."""
        app_id = self.get_application_id(job_url)
        if app_id:
            self.update_status(app_id, 'failed', notes=reason)

    def print_stats(self):
        """Print statistics summary."""
        stats = self.get_stats()

        print(f"\n{'='*60}")
        print("Application Tracker Statistics")
        print(f"{'='*60}")
        print(f"Total Applications: {stats['total_applications']}")
        print(f"Success Rate: {stats['success_rate']:.1f}%")

        print(f"\nBy Status:")
        for status, count in stats['status_counts'].items():
            print(f"  {status}: {count}")

        print(f"\nBy Tier:")
        for tier, count in stats['tier_counts'].items():
            print(f"  Tier {tier}: {count}")

        print(f"\nTop ATS Systems:")
        for ats, count in list(stats['ats_counts'].items())[:5]:
            print(f"  {ats}: {count}")

        print(f"{'='*60}")

    def close(self):
        """Close database connection."""
        if self.conn:
            self.conn.close()


def main():
    """Example usage."""
    tracker = ApplicationTracker()

    # Example: Add some applications
    jobs = [
        {
            'url': 'https://jobs.lever.co/company/123',
            'title': 'Data Engineer',
            'company': 'TechCorp',
            'location': 'Remote',
            'ats': 'lever',
            'tier': 2,
            'match_score': 85.5
        },
        {
            'url': 'https://boards.greenhouse.io/company/456',
            'title': 'ML Engineer',
            'company': 'AI Startup',
            'location': 'SF',
            'ats': 'greenhouse',
            'tier': 2,
            'match_score': 92.0
        }
    ]

    for job in jobs:
        app_id = tracker.add_application(job)
        print(f"Added application {app_id}: {job['title']}")

    # Update status
    tracker.mark_submitted(jobs[0]['url'])

    # Print stats
    tracker.print_stats()

    tracker.close()


if __name__ == '__main__':
    main()
