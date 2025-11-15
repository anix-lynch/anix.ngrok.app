# Making Resume Accessible to Perplexity and Other AI Tools

## Problem
Perplexity.ai and other AI tools cannot access `https://anix.ngrok.app/resume` due to authentication/access restrictions.

## Solution
Use the **PUBLIC version** with NO authentication.

---

## Quick Fix (2 Commands)

```bash
# 1. Stop current server
./stop.sh

# 2. Start PUBLIC server (no auth)
./start_public.sh
```

Done! Now test:
```bash
curl https://anix.ngrok.app/resume
```

You should see your resume JSON (not "Access denied").

---

## What Changed?

### Before (Private)
- `server.py` - Has authentication
- `start.sh` - May have ngrok auth/IP restrictions
- **Result**: "Access denied" for AI tools

### After (Public)
- `server_public.py` - **NO authentication**
- `start_public.sh` - **NO restrictions**
- **Result**: ✅ Accessible by Perplexity, ChatGPT, Claude, etc.

---

## Verify It's Public

### Test 1: Command Line
```bash
curl https://anix.ngrok.app/resume
# Should return JSON, not "Access denied"
```

### Test 2: Browser (Incognito)
Open in private/incognito window:
```
https://anix.ngrok.app/resume
```
Should see your resume JSON.

### Test 3: Perplexity
Ask Perplexity:
```
Read this resume and summarize it: https://anix.ngrok.app/resume
```

### Test 4: ChatGPT
Paste in ChatGPT:
```
Fetch and analyze this resume: https://anix.ngrok.app/resume
```

---

## Available Public Endpoints

| Endpoint | Description | Example |
|----------|-------------|---------|
| `/` | HTML interface | https://anix.ngrok.app/ |
| `/health` | Health check | https://anix.ngrok.app/health |
| `/resume` | Full resume JSON | https://anix.ngrok.app/resume |
| `/resume.json` | Same as /resume | https://anix.ngrok.app/resume.json |
| `/skills` | Skills only | https://anix.ngrok.app/skills |
| `/summary` | Quick summary | https://anix.ngrok.app/summary |

**All endpoints are PUBLIC - no auth required!**

---

## Troubleshooting

### Still Getting "Access denied"?

**Check 1: Is PUBLIC server running?**
```bash
ps aux | grep server_public.py
# Should show a process
```

**Check 2: Check logs**
```bash
tail -f server.log
# Should show "PUBLIC" in startup message
```

**Check 3: Restart ngrok**
```bash
./stop.sh
./start_public.sh
```

**Check 4: Check ngrok dashboard**
- Go to: https://dashboard.ngrok.com/endpoints
- Find your endpoint: `anix.ngrok.app`
- Click "Edit"
- Under "IP Restrictions": Should be EMPTY
- Under "OAuth": Should be DISABLED
- Under "Basic Auth": Should be DISABLED

If any auth is enabled, **DISABLE IT**.

---

## ngrok Dashboard Configuration

### Remove All Authentication:

1. Go to: https://dashboard.ngrok.com/cloud-edge/endpoints
2. Find your domain: `anix.ngrok.app`
3. Click "Edit"
4. Remove/Disable:
   - ❌ IP Restrictions
   - ❌ OAuth
   - ❌ Basic Auth
   - ❌ OIDC
   - ❌ SAML
   - ❌ Webhook Verification
5. Save

Now your ngrok endpoint is fully public!

---

## Security Note

**This makes your resume PUBLIC** - anyone can access it.

If you need privacy:
1. Use `server.py` + `start.sh` (with auth)
2. For AI tools, manually provide resume data
3. Or use token-based access with bearer tokens

---

## For Permanent Setup

### Option 1: Keep Public (Recommended for Job Search)
```bash
# Always use public version
./start_public.sh
```

**Pros:**
- ✅ AI tools can access
- ✅ Easy sharing with recruiters
- ✅ Works with job automation system

**Cons:**
- ⚠️ Anyone with URL can access (but that's fine for job search!)

### Option 2: Switch Between Public/Private
```bash
# Public (for AI tools / job search)
./start_public.sh

# Private (for personal use)
./start.sh
```

---

## Testing with Different AI Tools

### Perplexity
```
Prompt: "Read this resume: https://anix.ngrok.app/resume. What are the top 5 skills?"
```

### ChatGPT
```
Prompt: "Fetch https://anix.ngrok.app/resume and create a cover letter for a Data Engineer role at Amazon."
```

### Claude (via API)
```python
import anthropic
import requests

resume = requests.get("https://anix.ngrok.app/resume").json()
client = anthropic.Anthropic(api_key="...")
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{
        "role": "user",
        "content": f"Analyze this resume and suggest improvements: {resume}"
    }]
)
```

### Job Automation System
The job automation system you built will automatically use this endpoint:
```python
# In job_matcher.py
matcher = JobMatcher(resume_url="https://anix.ngrok.app/resume")
```

---

## Confirmation

Once running, you should see:

```bash
>> Resume API Server (PUBLIC) running on port 8000
>> Local:   http://localhost:8000
>> PUBLIC:  https://anix.ngrok.app
>>
>> ✓ NO AUTHENTICATION - Public access enabled
>> ✓ AI tools (Perplexity, ChatGPT, Claude) can access
```

And visiting `https://anix.ngrok.app/` should show:
```
✓ PUBLIC API - NO AUTH REQUIRED
```

---

## Summary

1. **Stop current server**: `./stop.sh`
2. **Start public server**: `./start_public.sh`
3. **Remove ngrok auth**: Dashboard → Endpoints → Remove restrictions
4. **Test**: `curl https://anix.ngrok.app/resume`
5. **Verify in Perplexity**: Ask it to read the URL

**Now Perplexity and all AI tools can access your resume!** ✅
