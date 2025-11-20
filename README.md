# anix.ngrok.app

**Simple MCP Resume Server** - Expose your resume.json to ChatGPT via ngrok

🔗 **Live URL:** https://anix.ngrok.app

## 🎯 What This Does

Serves your `resume.json` to ChatGPT as an MCP (Model Context Protocol) server so ChatGPT can:
- Read your full resume
- Query your skills
- List your projects
- View your experience

**Zero complexity** - just FastAPI + resume.json + ngrok.

## 🚀 Quick Start

```bash
# 1. Clone
git clone https://github.com/anix-lynch/anix.ngrok.app.git
cd anix.ngrok.app

# 2. Set up environment
cp .env.example .env
# Edit .env and add your NGROK_AUTHTOKEN from ngrok.com

# 3. Install dependencies
pip install -r requirements.txt

# 4. Update your resume
# Edit resume.json with your info

# 5. Start server + ngrok
./start.sh
```

## 📁 Files

```
anix.ngrok.app/
├── server.py          # FastAPI MCP server (180 lines)
├── resume.json        # Your resume data
├── openapi.yaml       # OpenAPI schema for ChatGPT
├── requirements.txt   # FastAPI + uvicorn
├── start.sh          # Start server + ngrok
├── stop.sh           # Stop all processes
├── .env.example      # Environment template
└── README.md         # This file
```

## 🔌 MCP Tools

The server exposes these tools to ChatGPT:

- **`get_resume`** - Get full resume
- **`get_skills`** - Get skills (with optional min_weight filter)
- **`get_projects`** - Get portfolio projects
- **`get_experience`** - Get work experience

## 🛠️ Usage

### Start Everything
```bash
./start.sh
```

This will:
1. Start FastAPI server on port 8000
2. Start ngrok tunnel to https://anix.ngrok.app
3. Server logs go to `server.log`
4. Ngrok logs go to `ngrok.log`

### Stop Everything
```bash
./stop.sh
```

### Check Status
```bash
# Check if server is running
curl http://localhost:8000

# Check ngrok tunnel
curl https://anix.ngrok.app/mcp

# Test a tool
curl -X POST https://anix.ngrok.app/mcp \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "id": 1,
    "method": "tools/call",
    "params": {
      "name": "get_resume",
      "arguments": {}
    }
  }'
```

## 🤖 ChatGPT Integration

1. Go to ChatGPT → **My GPTs** → **Create a GPT**
2. **Configure** → **Create new action**
3. **Import from URL** or paste the content of `openapi.yaml`
4. The server URL is already set to `https://anix.ngrok.app`
5. **Authentication:** None (or API Key if you add auth)
6. **Test** the actions

Now ChatGPT can read your resume!

## 🔧 Environment Variables

Create `.env` from `.env.example`:

```bash
# Required
NGROK_AUTHTOKEN=your_ngrok_token_here

# Optional (if you reserved a domain)
NGROK_DOMAIN=anix.ngrok.app
```

## 📊 Tech Stack

- **FastAPI** - Modern Python web framework
- **Uvicorn** - ASGI server
- **ngrok** - Secure tunnel to localhost
- **MCP Protocol** - Model Context Protocol (JSON-RPC 2.0)

## ✅ Features

- ✅ **Zero dependencies** (except FastAPI + uvicorn)
- ✅ **No modification to resume.json** - use it as-is
- ✅ **Instant responses** - no timeouts
- ✅ **MCP compliant** - works with ChatGPT
- ✅ **OpenAPI schema** - for easy integration
- ✅ **Simple deployment** - just run `./start.sh`

## 🔒 Security Note

This is a **public demo** setup with no authentication. For production:
1. Add Bearer token auth
2. Use environment variables for secrets
3. Add rate limiting
4. Enable HTTPS only

## 📝 Updating Your Resume

Just edit `resume.json` and restart:

```bash
./stop.sh
./start.sh
```

ChatGPT will see the updated data immediately.

## 🔧 Troubleshooting

### Port Already in Use
```bash
lsof -ti:8000 | xargs kill -9
```

### ngrok ERR_NGROK_3200
Your ngrok tunnel is offline. Check:
- Is `NGROK_AUTHTOKEN` set in `.env`?
- Is ngrok running? Check `ngrok.log`
- Try: `ngrok http 8000 --authtoken YOUR_TOKEN`

### Server Not Starting
```bash
# Check logs
tail -f server.log

# Check if FastAPI is installed
pip install -r requirements.txt
```

## 📄 License

MIT

## 🤝 Contributing

PRs welcome! Keep it simple.
