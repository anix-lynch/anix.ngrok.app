# AI-Powered Job Application Automation System

**Goal:** Apply to 2000+ Data Engineering jobs using intelligent automation and AI customization

## System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Job Application Pipeline                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  1. Job Scraper (Indeed, LinkedIn, Dice, etc.)              │
│           ↓                                                   │
│  2. ATS Detector & Classifier                                │
│           ↓                                                   │
│  3. AI Job Matcher (Score: 0-100)                           │
│           ↓                                                   │
│  4. Resume Customizer (AI-powered)                          │
│           ↓                                                   │
│  5. Application Router (by ATS type)                        │
│           ↓                                                   │
│  6. Browser Automation (Playwright)                         │
│           ↓                                                   │
│  7. Application Tracker & Analytics                         │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Components

### 1. Job Scraper (`scrapers/`)
- Indeed API/scraper
- LinkedIn Jobs scraper
- Dice, Glassdoor, ZipRecruiter
- Company career pages
- Output: Unified job listing JSON

### 2. ATS Detector (`ats_detector.py`)
- Detects ATS system from job URL/page
- Classifies as Tier 1/2/3
- Maps to automation strategy

### 3. AI Job Matcher (`job_matcher.py`)
- Consumes resume from https://anix.ngrok.app/resume
- Scores job fit (0-100) using embeddings
- Prioritizes applications

### 4. Resume Customizer (`resume_customizer.py`)
- AI-powered cover letter generation
- Resume keyword optimization per job
- Screening question answering

### 5. Application Router (`application_router.py`)
- Routes to correct automation strategy
- Tier 1: Full auto
- Tier 2: Smart auto with delays
- Tier 3: Pre-fill + manual review

### 6. Browser Automation (`automation/`)
- Playwright-based automation
- Anti-detection techniques
- Session management
- Rate limiting

### 7. Application Tracker (`tracker.py`)
- SQLite database
- Status tracking
- Analytics dashboard
- Retry logic

## ATS Classification

### Tier 1: Low Friction (70-80% success)
- JazzHR
- BambooHR
- Recruitee
- Manatal
- Pinpoint
- **Strategy:** Direct automation, minimal delays

### Tier 2: Medium Friction (50-60% success)
- Lever
- Greenhouse
- Ashby
- Bullhorn
- Trakstar Hire
- **Strategy:** Human-like behavior, randomized timing

### Tier 3: High Friction (30-40% success)
- Workday
- iCIMS
- Oracle Taleo
- SAP SuccessFactors
- Jobvite
- SmartRecruiters
- UKG Pro
- Ceridian Dayforce
- Avature
- **Strategy:** Pre-fill only, manual submit

## Anti-Detection Techniques

1. **Random delays** (2-8 seconds between actions)
2. **Mouse movement simulation**
3. **Session rotation** (new browser context every 10 apps)
4. **User-Agent rotation**
5. **Residential proxy rotation** (optional)
6. **Cookie management**
7. **Human-like typing speed** (50-120ms per char)
8. **Scroll simulation**
9. **Tab switching simulation**
10. **Random break times** (15-30 min after 50 apps)

## Usage

```bash
# 1. Scrape jobs
python scrapers/indeed_scraper.py --keywords "data engineer" --location "remote" --limit 500

# 2. Classify ATS
python ats_detector.py --input jobs.json --output jobs_classified.json

# 3. Score and prioritize
python job_matcher.py --input jobs_classified.json --output jobs_scored.json --min-score 70

# 4. Run automation (Tier 1)
python automation/tier1_automation.py --input jobs_scored.json --tier 1 --max-apps 100

# 5. Run automation (Tier 2)
python automation/tier2_automation.py --input jobs_scored.json --tier 2 --max-apps 50

# 6. Review Tier 3 (semi-manual)
python automation/tier3_prefill.py --input jobs_scored.json --tier 3
```

## Rate Limits

- **Tier 1:** 30 apps/hour (100-150/day)
- **Tier 2:** 15 apps/hour (50-75/day)
- **Tier 3:** 10 apps/hour (30-50/day)

**Total:** 180-275 applications per day
**Timeline:** 8-12 days for 2000 applications

## Success Metrics

- Total applications submitted
- Success rate by ATS tier
- Response rate
- Interview conversion
- Applications per day
- Error rate

## Tech Stack

- **Python 3.11+**
- **Playwright** (browser automation)
- **BeautifulSoup4** (scraping)
- **OpenAI/Anthropic API** (AI customization)
- **SQLite** (tracking)
- **FastAPI** (API server)
- **Streamlit** (dashboard)

## Safety Features

- **Dry run mode** (test without submitting)
- **Manual review checkpoints**
- **Rollback capabilities**
- **Rate limit enforcement**
- **Error logging and recovery**
- **Application deduplication**

## Next Steps

1. Install dependencies
2. Configure API keys
3. Test with 10 applications
4. Scale to 50/day
5. Monitor and optimize
6. Scale to 200/day
