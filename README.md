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

Just edit `resume.json` and restart:
```bash
./stop.sh && ./start.sh
```
