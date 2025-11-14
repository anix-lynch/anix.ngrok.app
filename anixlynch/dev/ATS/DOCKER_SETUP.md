# Docker Setup for Job Automation

## For Your Local Machine (NOT VM!)

This Docker setup ensures all files are on YOUR local machine and accessible by any AI tool.

---

## Step 1: Get Files Locally

```bash
# On YOUR local machine
cd /path/to/your/projects

# Clone or pull the repo
git clone https://github.com/anix-lynch/anix.ngrok.app.git
cd anix.ngrok.app

# Switch to the branch with automation code
git fetch origin
git checkout claude/who-is-ani-01QEPsYDVHch9WQmaBNZqYgv
git pull

# Navigate to ATS directory
cd anixlynch/dev/ATS
```

**Now all files are on YOUR local machine!**

---

## Step 2: Run with Docker Desktop

```bash
# Make sure Docker Desktop is running

# Build the container
docker-compose build

# Start the container (files are mounted from your local machine)
docker-compose up -d

# Enter the container
docker exec -it ats-automation bash

# Inside container, you can now run:
python orchestrator.py --dry-run
```

---

## Step 3: Run Automation

### Inside Docker Container:

```bash
# Dry run (test without submitting)
python orchestrator.py \
  --keywords "data engineer" \
  --location "Remote" \
  --scrape-limit 50 \
  --tier1-apps 10 \
  --dry-run

# Live run (actually submit)
python orchestrator.py \
  --keywords "data engineer" \
  --location "Remote" \
  --scrape-limit 100 \
  --tier1-apps 25 \
  --live
```

---

## File Locations

### On Your Local Machine:
```
/your/path/anix.ngrok.app/anixlynch/dev/ATS/
├── All Python files (orchestrator.py, etc.)
├── output/                  # Results appear here
│   ├── jobs_raw.json
│   ├── jobs_scored.json
│   ├── applications.db
│   └── applications_tier1.json
```

### Inside Docker Container:
```
/app/
├── Same files (mounted from your local machine)
├── output/                  # Same output, visible on your machine
```

**Any file created in the container appears on your local machine instantly!**

---

## Alternative: Run Directly on Local Machine

If you don't want Docker:

```bash
# On your local machine
cd anixlynch/dev/ATS

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run
python orchestrator.py --dry-run
```

---

## For Other AI Tools

Since files are on your local machine, other AI tools can access them:

1. **ChatGPT**: Point it to `anixlynch/dev/ATS` directory
2. **Cursor**: Open the directory in Cursor IDE
3. **GitHub Copilot**: Works with local files
4. **Any AI**: Just needs access to your local file system

---

## Verify Files Are Local

```bash
# On YOUR machine (not in Docker)
cd anixlynch/dev/ATS
ls -la

# You should see:
# - orchestrator.py
# - ats_detector.py
# - job_matcher.py
# - etc.
```

If you DON'T see these files, you haven't pulled from git yet!

---

## TL;DR

1. **Pull from git**: `git checkout claude/who-is-ani-01QEPsYDVHch9WQmaBNZqYgv && git pull`
2. **Navigate**: `cd anixlynch/dev/ATS`
3. **Verify files exist**: `ls -la`
4. **Use Docker**: `docker-compose up -d && docker exec -it ats-automation bash`
5. **Run automation**: `python orchestrator.py --dry-run`

**Files are on YOUR machine, not in a VM!**
