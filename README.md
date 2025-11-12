# anix.ngrok.app

**Live Resume API** - Simple HTTP server exposing resume data via ngrok.

🔗 **Live URL:** https://anix.ngrok.app

---

## 🚀 Quick Start

```bash
# 1. Clone repo
git clone https://github.com/anixlynch/anix.ngrok.app.git
cd anix.ngrok.app

# 2. Set up environment
cp .env.example .env
# Edit .env and add:
#   - NGROK_AUTHTOKEN (from ngrok.com)
#   - RESUME_AUTH_TOKEN (generate: openssl rand -hex 32)

# 3. Install dependencies (none! Pure Python stdlib)
# Optional: python3 -m venv venv && source venv/bin/activate

# 4. Start server + ngrok
./start.sh
```

## 🔒 Authentication

**All endpoints (except `/health`) are protected with Bearer token auth.**

### Generate a secure token:
```bash
openssl rand -hex 32
```

### Add to `.env`:
```bash
RESUME_AUTH_TOKEN=your_generated_token_here
```

### Test with curl:
```bash
# Without auth (will fail)
curl https://anix.ngrok.app/resume

# With auth (will succeed)
curl -H "Authorization: Bearer YOUR_TOKEN" https://anix.ngrok.app/resume
```

### For ChatGPT:
When connecting in ChatGPT's Custom API settings:
1. Authentication: **Bearer Token**
2. Token: `YOUR_TOKEN` (from `.env`)
3. All endpoints now private and secure!

---

## 📁 What's Inside

```
anix.ngrok.app/
├── server.py           # Simple HTTP server (pure Python)
├── resume.json         # Your resume data
├── start.sh            # Start server + ngrok
├── stop.sh             # Stop all processes
├── .env.example        # Environment template
├── .gitignore          # Don't commit secrets!
└── README.md           # This file
```

---

## 🔌 API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Beautiful HTML resume interface |
| `GET /health` | Health check (returns `{"status": "ok"}`) |
| `GET /resume` | Full resume JSON |
| `GET /skills` | Skills list JSON |
| `GET /summary` | Resume summary JSON |

---

## 🛠️ Manual Setup

### 1. Get ngrok Auth Token

```bash
# Sign up: https://dashboard.ngrok.com/signup
# Get token: https://dashboard.ngrok.com/get-started/your-authtoken

# Configure ngrok
ngrok config add-authtoken YOUR_TOKEN_HERE
```

### 2. Reserve Domain (Optional)

```bash
# Go to: https://dashboard.ngrok.com/domains
# Reserve: anix.ngrok.app (free tier: 1 static domain)
```

### 3. Update Resume Data

Edit `resume.json` with your information:
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
    "primary": ["Data Engineer", "ML Engineer"]
  }
}
```

---

## 🚦 Usage

### Start Everything

```bash
./start.sh
# Starts server on port 8000
# Starts ngrok tunnel to anix.ngrok.app
```

### Stop Everything

```bash
./stop.sh
# Kills server and ngrok processes
```

### Check Status

```bash
# Check if running
pgrep -fl "python.*server.py"
pgrep -fl ngrok

# Test locally
curl http://localhost:8000/health

# Test public
curl https://anix.ngrok.app/health
```

---

## 🔒 Environment Variables

Required in `.env`:

```bash
NGROK_AUTHTOKEN=your_ngrok_token_here
NGROK_DOMAIN=anix.ngrok.app
SERVER_PORT=8000
```

---

## 📊 Tech Stack

- **Server:** Python 3 (stdlib only - no dependencies!)
- **Tunnel:** ngrok (free tier)
- **Data:** JSON
- **Deployment:** Any machine with Python 3

---

## 🎯 Features

✅ **Zero Dependencies** - Pure Python standard library  
✅ **Clean Design** - No emojis, no broken encoding  
✅ **Fast Startup** - < 5 seconds to live  
✅ **Multiple Formats** - JSON API + HTML interface  
✅ **Easy Resume Updates** - Just edit `resume.json`  
✅ **Portable** - Runs anywhere Python 3 exists  

---

## 🔧 Troubleshooting

### Port Already in Use

```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Or use stop.sh
./stop.sh
```

### ngrok ERR_NGROK_3200 (Offline)

```bash
# Restart ngrok
pkill ngrok
ngrok http --domain=anix.ngrok.app 8000 &
```

### Authentication Failed

```bash
# Re-authenticate
source .env
ngrok config add-authtoken $NGROK_AUTHTOKEN
```

---

## 📝 License

MIT - Do whatever you want with it!

---

## 🤝 Contributing

This is a personal resume server, but feel free to fork and adapt for your own use!

---

**Built by anixlynch** | [GitHub](https://github.com/anixlynch) | [Live Resume](https://anix.ngrok.app)

