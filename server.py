#!/usr/bin/env python3
"""
Simple MCP Server - Just serves resume.json to ChatGPT
No job matching, no complex logic - just resume data.
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
from pathlib import Path

# Load resume once at startup
RESUME_FILE = Path(__file__).parent / "resume.json"

def load_resume():
    """Load resume data from JSON."""
    if not RESUME_FILE.exists():
        return None
    with open(RESUME_FILE, 'r') as f:
        return json.load(f)

# Create FastAPI app
app = FastAPI(title="Simple Resume MCP", version="1.0.0")

# CORS for OpenAI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Health check."""
    return {"status": "ok", "message": "Simple Resume MCP Server"}

@app.get("/mcp")
@app.post("/mcp")
async def mcp_endpoint(request: Request):
    """MCP endpoint for ChatGPT."""
    
    if request.method == "GET":
        # Health check
        return JSONResponse({
            "protocol": "mcp",
            "version": "2024-11-05",
            "capabilities": {"tools": True},
            "serverInfo": {"name": "simple-resume-mcp", "version": "1.0.0"}
        })
    
    # POST - handle JSON-RPC
    body = await request.json()
    
    # Initialize
    if body.get("method") == "initialize":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {"listChanged": True}},
                "serverInfo": {"name": "simple-resume-mcp", "version": "1.0.0"}
            }
        })
    
    # List tools
    elif body.get("method") == "tools/list":
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "tools": [
                    {
                        "name": "get_resume",
                        "description": "Get Anix Lynch's complete resume including skills, projects, experience, and contact info",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "get_skills",
                        "description": "Get Anix's technical skills with proficiency ratings",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "min_weight": {
                                    "type": "integer",
                                    "description": "Minimum skill weight (1-10)",
                                    "default": 0
                                }
                            }
                        }
                    },
                    {
                        "name": "get_projects",
                        "description": "Get Anix's portfolio projects",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "get_experience",
                        "description": "Get Anix's work experience",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    }
                ]
            }
        })
    
    # Call tool
    elif body.get("method") == "tools/call":
        params = body.get("params", {})
        tool_name = params.get("name")
        args = params.get("arguments", {})
        
        resume = load_resume()
        if not resume:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -32000,
                    "message": "Resume file not found"
                }
            })
        
        # Handle different tools
        if tool_name == "get_resume":
            result = resume
        
        elif tool_name == "get_skills":
            min_weight = args.get("min_weight", 0)
            skills = {k: v for k, v in resume.get("skills", {}).items() if v >= min_weight}
            result = {"skills": skills}
        
        elif tool_name == "get_projects":
            result = {"projects": resume.get("projects", [])}
        
        elif tool_name == "get_experience":
            result = {"experience": resume.get("experience", [])}
        
        else:
            return JSONResponse({
                "jsonrpc": "2.0",
                "id": body.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Unknown tool: {tool_name}"
                }
            })
        
        return JSONResponse({
            "jsonrpc": "2.0",
            "id": body.get("id"),
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, indent=2)
                    }
                ]
            }
        })
    
    # Unknown method
    return JSONResponse({
        "jsonrpc": "2.0",
        "id": body.get("id"),
        "error": {
            "code": -32601,
            "message": f"Unknown method: {body.get('method')}"
        }
    })

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Simple Resume MCP Server on http://localhost:8000")
    print("📄 Serving resume.json to ChatGPT")
    print("🌐 Expose via: ngrok http 8000 --domain anix.ngrok.app")
    uvicorn.run(app, host="0.0.0.0", port=8000)
