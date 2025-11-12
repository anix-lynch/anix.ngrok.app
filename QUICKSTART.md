# Quick Start Guide - anix.ngrok.app

## 30-Second Setup

```bash
# Clone
git clone https://github.com/anix-lynch/anix.ngrok.app.git
cd anix.ngrok.app

# Configure
cp env.example .env
# Add your NGROK_AUTHTOKEN to .env

# Start
./start.sh
```

**Done!** Your resume is live at https://anix.ngrok.app

---

## One-Line Commands

```bash
# Start everything
./start.sh

# Stop everything
./stop.sh

# Check status
pgrep -fl "python.*server.py" && pgrep -fl ngrok

# View logs
tail -f server.log ngrok.log

# Test local
curl http://localhost:8000/health

# Test public
curl https://anix.ngrok.app/health
```

---

## File Structure (7 files)

```
anix.ngrok.app/
├── server.py         # HTTP server (pure Python)
├── resume.json       # Your data
├── start.sh          # Start script
├── stop.sh           # Stop script
├── env.example       # Config template
├── .gitignore        # Protect secrets
└── README.md         # Full docs
```

---

## API Endpoints

| Endpoint | What It Does |
|----------|--------------|
| `GET /` | HTML resume page |
| `GET /health` | Health check JSON |
| `GET /resume` | Full resume JSON |
| `GET /skills` | Skills list JSON |
| `GET /summary` | Resume summary JSON |

---

## Requirements

- Python 3 (no packages needed!)
- ngrok (free account)
- That's it!

---

## Get ngrok Token

1. Sign up: https://dashboard.ngrok.com/signup
2. Get token: https://dashboard.ngrok.com/get-started/your-authtoken
3. Add to `.env`:
   ```
   NGROK_AUTHTOKEN=your_token_here
   ```

---

## Troubleshooting

**Port already in use?**
```bash
./stop.sh
./start.sh
```

**ngrok offline?**
```bash
source .env
ngrok config add-authtoken $NGROK_AUTHTOKEN
./start.sh
```

**Check if running:**
```bash
# Should show 2 processes
ps aux | grep -E "(server.py|ngrok)"
```

---

## Update Your Resume

Edit `resume.json`:
```json
{
  "name": "Your Name",
  "title": "Your Title",
  "location": "Your Location",
  "skills": {
    "Python": 5,
    "JavaScript": 4
  },
  "target_roles": {
    "primary": ["Engineer", "Analyst"]
  }
}
```

Restart:
```bash
./stop.sh
./start.sh
```

---

**Live Demo:** https://anix.ngrok.app  
**GitHub:** https://github.com/anix-lynch/anix.ngrok.app  
**Full Docs:** [README.md](README.md)

