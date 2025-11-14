# Job Automation Quickstart Guide

## Goal: Apply to 2000+ Data Engineering Jobs

This system automates job applications across 17+ ATS platforms using AI-powered matching and browser automation.

---

## Installation

### 1. Install Python Dependencies

```bash
cd job_automation
pip install -r requirements.txt

# Install Playwright browsers
playwright install chromium
```

### 2. Verify Resume Endpoint

```bash
# Test that your resume is accessible
curl https://anix.ngrok.app/resume

# Should return your resume JSON
```

---

## Quick Start (Dry Run)

### Test the full pipeline without submitting applications:

```bash
# Scrape 50 jobs, score them, and simulate applications
python orchestrator.py \
  --keywords "data engineer" \
  --location "Remote" \
  --scrape-limit 50 \
  --min-score 70 \
  --tier1-apps 10 \
  --dry-run
```

**What this does:**
1. Scrapes 50 Data Engineer jobs from Indeed
2. Detects which ATS each job uses
3. Scores each job (0-100) based on your resume
4. Filters jobs with score >= 70
5. Shows which Tier 1 jobs it would auto-apply to (doesn't submit)

---

## Production Usage

### Phase 1: Test with 10 Applications

```bash
# Start small - actually submit 10 applications
python orchestrator.py \
  --keywords "data engineer" \
  --location "Remote" \
  --scrape-limit 100 \
  --min-score 75 \
  --tier1-apps 10 \
  --live
```

**Monitor:**
- Check email for confirmation emails
- Verify applications actually submitted
- Check error logs

### Phase 2: Scale to 50/day

```bash
# Morning batch (25 apps)
python orchestrator.py \
  --keywords "data engineer" \
  --location "Remote" \
  --scrape-limit 150 \
  --min-score 70 \
  --tier1-apps 25 \
  --live

# Evening batch (25 apps)
python orchestrator.py \
  --keywords "machine learning engineer" \
  --location "Remote" \
  --scrape-limit 150 \
  --min-score 70 \
  --tier1-apps 25 \
  --live
```

### Phase 3: Scale to 200/day (2000 in 10 days)

```bash
# Run 4 batches per day (50 apps each)
# Batch 1: 9am
python orchestrator.py --keywords "data engineer" --location "Remote" --scrape-limit 200 --min-score 65 --tier1-apps 50 --live

# Batch 2: 1pm
python orchestrator.py --keywords "ml engineer" --location "Remote" --scrape-limit 200 --min-score 65 --tier1-apps 50 --live

# Batch 3: 5pm
python orchestrator.py --keywords "analytics engineer" --location "Remote" --scrape-limit 200 --min-score 65 --tier1-apps 50 --live

# Batch 4: 9pm
python orchestrator.py --keywords "data platform engineer" --location "Remote" --scrape-limit 200 --min-score 65 --tier1-apps 50 --live
```

---

## Individual Components

### 1. Scrape Jobs Only

```bash
python scrapers/indeed_scraper.py
# Outputs: jobs_indeed.json
```

### 2. Classify ATS

```bash
python -c "
from ats_detector import ATSDetector
import json

detector = ATSDetector()

# Load jobs
with open('jobs_indeed.json') as f:
    jobs = json.load(f)

# Classify
for job in jobs:
    detector.classify_job(job)

# Save
with open('jobs_classified.json', 'w') as f:
    json.dump(jobs, f, indent=2)

print(f'Classified {len(jobs)} jobs')
"
```

### 3. Score Jobs

```bash
python job_matcher.py
# Reads: jobs_indeed.json or jobs_classified.json
# Outputs: jobs_scored.json
```

### 4. Apply to Tier 1 Jobs Only

```bash
python automation/tier1_automation.py
# Reads: jobs_scored.json (Tier 1 only)
# Outputs: applications_log.json
```

---

## Database Tracking

### View Statistics

```bash
python -c "
from tracker import ApplicationTracker

tracker = ApplicationTracker('output/applications.db')
tracker.print_stats()
"
```

### Query Database

```bash
sqlite3 output/applications.db

# Get all applications
SELECT * FROM applications;

# Get by status
SELECT company, job_title, status, match_score
FROM applications
WHERE status = 'submitted'
ORDER BY match_score DESC;

# Get by tier
SELECT tier, COUNT(*) as count
FROM applications
GROUP BY tier;
```

---

## Advanced Usage

### Different Job Titles

```bash
# Target multiple roles
for role in "data engineer" "ml engineer" "analytics engineer" "data scientist"
do
  python orchestrator.py \
    --keywords "$role" \
    --location "Remote" \
    --scrape-limit 100 \
    --min-score 70 \
    --tier1-apps 10 \
    --live

  sleep 300  # 5 min break between roles
done
```

### Different Locations

```bash
# Remote + specific cities
for loc in "Remote" "Los Angeles" "San Francisco" "New York"
do
  python orchestrator.py \
    --keywords "data engineer" \
    --location "$loc" \
    --scrape-limit 75 \
    --min-score 70 \
    --tier1-apps 15 \
    --live
done
```

### Lower Score Threshold (More Applications)

```bash
# Accept jobs with 60+ score (more volume, less precision)
python orchestrator.py \
  --keywords "data engineer" \
  --location "Remote" \
  --scrape-limit 300 \
  --min-score 60 \
  --tier1-apps 100 \
  --live
```

---

## Rate Limits & Best Practices

### Recommended Limits

| Tier | Apps/Hour | Apps/Day | Success Rate |
|------|-----------|----------|--------------|
| 1    | 30        | 100-150  | 70-80%       |
| 2    | 15        | 50-75    | 50-60%       |
| 3    | 10        | 30-50    | 30-40%       |

### Anti-Detection Tips

1. **Don't run 24/7** - Human hours only (9am-9pm)
2. **Random delays** - Built into automation
3. **Session breaks** - Every 10 apps, 30s break
4. **IP rotation** - Use proxies if applying >100/day
5. **Browser fingerprint** - Playwright handles this
6. **User agent rotation** - Built-in

### Avoid Getting Blocked

- **Max 200 apps/day** from single IP
- **Rotate between job boards** (Indeed, LinkedIn, Dice)
- **Use residential proxies** for >100/day
- **Monitor email confirmations** - if they stop, you're blocked

---

## Monitoring

### Check Logs

```bash
# Watch live logs
tail -f output/applications_tier1.json

# Count applications
cat output/applications_tier1.json | grep '"status": "submitted"' | wc -l
```

### Email Confirmations

- Set up email filter for "application received"
- Track response rate
- If responses stop, check for blocks

### Application Database

```bash
# Daily summary
python -c "
from tracker import ApplicationTracker

tracker = ApplicationTracker('output/applications.db')
stats = tracker.get_stats()

print(f'Total: {stats[\"total_applications\"]}')
print(f'Submitted: {stats[\"status_counts\"].get(\"submitted\", 0)}')
print(f'Success rate: {stats[\"success_rate\"]:.1f}%')
"
```

---

## Troubleshooting

### Resume not loading?

```bash
# Test manually
curl https://anix.ngrok.app/resume

# Restart ngrok
cd ..
./stop.sh
./start.sh
```

### Playwright errors?

```bash
# Reinstall browsers
playwright install chromium --force

# Run with visible browser
python automation/tier1_automation.py  # headless=False by default
```

### Jobs not scraping?

- Indeed may be blocking - try with proxies
- Use headless=False to see what's happening
- Try different keywords/locations

---

## Expected Results

### Timeline to 2000 Applications

| Strategy | Apps/Day | Days to 2000 | Effort |
|----------|----------|--------------|--------|
| Conservative | 50 | 40 days | Low |
| Moderate | 100 | 20 days | Medium |
| Aggressive | 200 | 10 days | High |

### Realistic Response Rates

- **Applications sent**: 2000
- **Confirmation emails**: 1800 (90%)
- **Recruiter responses**: 200-400 (10-20%)
- **Phone screens**: 100-200 (5-10%)
- **Interviews**: 40-80 (2-4%)
- **Offers**: 4-12 (0.2-0.6%)

### Best Case Scenario

With good resume and matching:
- **2000 applications** → **6-12 job offers**

---

## Next Steps

1. **Test with 10 apps** (--tier1-apps 10 --live)
2. **Review confirmations** (check email)
3. **Scale to 50/day** (2 batches)
4. **Monitor response rate**
5. **Scale to 200/day** (4 batches)
6. **Hit 2000 in 10 days**

**Good luck! 🚀**
