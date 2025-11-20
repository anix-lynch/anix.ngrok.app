# anix.ngrok.app

**Simple MCP Resume Server** - Expose your resume.json to ChatGPT via ngrok

🔗 **Live URL:** https://anix.ngrok.app

## 🎯 What This Does

Serves your `resume.json` to ChatGPT as an MCP (Model Context Protocol) server.
Designed for **OpenAI SDK Tool Calling** (Dev Mode).

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/anix-lynch/anix.ngrok.app.git
cd anix.ngrok.app

# 2. Set up environment
cp .env.example .env
# Edit .env:
# NGROK_AUTHTOKEN=...
# OPENAI_API_KEY=... (for testing SDK)

# 3. Install dependencies
pip install -r requirements.txt

# 4. Start server + ngrok
./start.sh
```

## 💻 Using with OpenAI SDK (Python)

See `test_openai_sdk.py` for a complete working example.

```python
# 1. Define tools
tools = [{
    "type": "function",
    "function": {
        "name": "get_resume_info",
        "description": "Get Anix Lynch's complete resume",
        "parameters": {"type": "object", "properties": {}}
    }
}]

# 2. Call OpenAI
response = client.chat.completions.create(
    model="gpt-4-turbo-preview",
    messages=[{"role": "user", "content": "Who is Anix?"}],
    tools=tools
)

# 3. Handle tool call (see test_openai_sdk.py for full logic)
# ... call https://anix.ngrok.app/mcp ...
```

## ��‍♂️ Run the Test

```bash
python test_openai_sdk.py
```

## 🔌 MCP Tools

- **`get_resume_info`** - Get full resume
- **`get_skills`** - Get skills (optional `min_weight`)
- **`get_projects`** - Get portfolio projects
- **`get_experience`** - Get work experience

## 📁 Files

```
anix.ngrok.app/
├── server.py          # FastAPI MCP server
├── resume.json        # Your resume data
├── test_openai_sdk.py # OpenAI SDK Example
├── start.sh          # Start server + ngrok
└── requirements.txt   # Dependencies
```

## 📝 Updating Your Resume

Edit `resume.json` directly:
```bash
nano resume.json
```

Changes are served live at `https://anix.ngrok.app/resume`

**No restart needed** - server auto-reads the file on each request.

---

## 🔧 Setup & Troubleshooting Log

### Current Setup (Nov 20, 2025)

**Problem:** ngrok tunnel kept failing, needed permanent solution

**Solution Implemented:**
1. **Created ngrok config** at `~/.ngrok2/ngrok.yml` with reserved domain `anix.ngrok.app`
2. **Set up launchd auto-start** at `~/Library/LaunchAgents/com.anix.ngrok-resume.plist`
3. **Service now:**
   - ✅ Auto-starts on Mac boot
   - ✅ Auto-restarts if crashes
   - ✅ Keeps tunnel alive 24/7
   - ✅ No manual `./start.sh` needed

**Verify it's working:**
```bash
# Check service status
launchctl list | grep ngrok

# View logs
tail -f /tmp/ngrok-resume.log
tail -f /tmp/ngrok-resume-error.log

# Test endpoints
curl https://anix.ngrok.app/            # Status
curl https://anix.ngrok.app/resume      # Resume JSON
curl https://anix.ngrok.app/mcp         # MCP capabilities
```

**If it breaks:**
```bash
# Restart service
launchctl unload ~/Library/LaunchAgents/com.anix.ngrok-resume.plist
launchctl load ~/Library/LaunchAgents/com.anix.ngrok-resume.plist

# Check if processes are running
ps aux | grep -E "(uvicorn|ngrok)" | grep -v grep
```

### Endpoints
- `https://anix.ngrok.app/` - Health check
- `https://anix.ngrok.app/resume` - Raw resume JSON (Perplexity, browsing)
- `https://anix.ngrok.app/mcp` - MCP endpoint (ChatGPT SDK tool calling)
