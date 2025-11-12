# ChatGPT MCP Connection Setup

## 🔌 Connect Your Resume MCP to ChatGPT

### **Step 1: Open ChatGPT Settings**

Go to: https://chatgpt.com/gpts/editor

Or click: **"Explore GPTs"** → **"Create"** → **"Configure"**

---

### **Step 2: Add Custom MCP Server**

Click **"New Connector"** (BETA) button

---

### **Step 3: Fill in Connection Details**

#### **Icon:**
- Upload an icon (optional)
- Minimum size: 128 x 128 px

#### **Name:**
```
anix Resume MCP
```

#### **Description:**
```
Live resume API - skills, target roles, and career data for anixlynch
```

#### **MCP Server URL:**
```
https://anix.ngrok.app/mcp
```

#### **Authentication:**
```
Bearer Token
```

**Token:** `YOUR_RESUME_AUTH_TOKEN` (from your `.env` file)

*(This protects your master resume from public access!)*

#### **Accept Risk:**
- ☑️ Check: "I understand and want to continue"
- Note: This is your own authenticated server, so it's safe!

---

### **Step 4: Create Connection**

Click **"Create"** button

---

### **Step 5: Test the Connection**

Try asking ChatGPT:

```
What skills does anixlynch have?
```

```
What are anixlynch's target roles?
```

```
Show me the full resume data
```

---

## 📊 Available MCP Tools

Once connected, ChatGPT can use these tools:

| Tool | Description |
|------|-------------|
| `get_resume` | Get full resume data |
| `get_skills` | Get skills list and proficiency levels |
| `get_target_roles` | Get target job roles and positions |
| `search_skills` | Search for specific skills |

---

## 🔗 Available Resources

| Resource | URI | Description |
|----------|-----|-------------|
| Full Resume | `resume://full` | Complete resume data |
| Skills | `resume://skills` | Technical and professional skills |
| Summary | `resume://summary` | Quick overview |

---

## 🧪 Test Endpoints Manually

```bash
# Set your auth token
export TOKEN="YOUR_RESUME_AUTH_TOKEN"

# Health check (no auth required)
curl https://anix.ngrok.app/health

# MCP metadata (requires auth)
curl -H "Authorization: Bearer $TOKEN" https://anix.ngrok.app/mcp | jq '.'

# Full resume (requires auth)
curl -H "Authorization: Bearer $TOKEN" https://anix.ngrok.app/resume | jq '.'

# Skills only (requires auth)
curl -H "Authorization: Bearer $TOKEN" https://anix.ngrok.app/skills | jq '.'

# Summary (requires auth)
curl -H "Authorization: Bearer $TOKEN" https://anix.ngrok.app/summary | jq '.'
```

---

## ⚠️ Troubleshooting

### Connection Failed?

1. **Check if server is running:**
   ```bash
   pgrep -fl "server.py|ngrok"
   ```

2. **Restart server:**
   ```bash
   cd /Users/anixlynch/dev/anix.ngrok.app
   ./stop.sh
   ./start.sh
   ```

3. **Test endpoint manually:**
   ```bash
   curl https://anix.ngrok.app/mcp
   ```

### ngrok Offline (ERR_NGROK_3200)?

```bash
cd /Users/anixlynch/dev/anix.ngrok.app
./start.sh
```

### Authentication Issues?

- Make sure you selected **"Bearer Token"** (not "None" or "OAuth")
- Copy your token EXACTLY from `.env` file (`RESUME_AUTH_TOKEN`)
- Test authentication manually: `curl -H "Authorization: Bearer YOUR_TOKEN" https://anix.ngrok.app/health`
- If you get 401 Unauthorized, regenerate token: `openssl rand -hex 32`

---

## 🎯 What ChatGPT Can Do

Once connected, ChatGPT will be able to:

✅ Read your resume data in real-time  
✅ Answer questions about your skills  
✅ List your target job roles  
✅ Search specific technical skills  
✅ Provide career recommendations based on your data  
✅ Help with job applications using your actual skills  

---

## 🔄 Updating Your Resume

To update the data ChatGPT sees:

1. Edit `resume.json` in the repo
2. Restart the server:
   ```bash
   ./stop.sh
   ./start.sh
   ```
3. ChatGPT will immediately see the new data!

---

## 📝 Connection Summary

```
✅ Server:   https://anix.ngrok.app
✅ MCP URL:  https://anix.ngrok.app/mcp
✅ Auth:     Bearer Token (private & secure)
✅ Status:   Live
✅ Protocol: MCP 1.0
```

---

**Ready to connect!** 🚀

Follow the steps above to add your Resume MCP to ChatGPT.

