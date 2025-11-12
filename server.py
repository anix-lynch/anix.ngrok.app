#!/usr/bin/env python3
"""
Resume MCP Server
Simple HTTP server that serves resume data via ngrok
Zero dependencies - Python stdlib only!
"""

from http.server import HTTPServer, BaseHTTPRequestHandler
import json
from pathlib import Path
from urllib.parse import urlparse

# Configuration
PORT = 8000
RESUME_FILE = Path(__file__).parent / "resume.json"


def load_resume():
    """Load resume from JSON file."""
    if RESUME_FILE.exists():
        with open(RESUME_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"name": "Resume Not Found", "error": "resume.json missing"}


class ResumeHandler(BaseHTTPRequestHandler):
    """HTTP request handler for resume API."""
    
    def do_HEAD(self):
        """Handle HEAD requests (for ngrok health checks)."""
        path = urlparse(self.path).path
        if path in ['/', '/health', '/resume', '/skills', '/summary', '/mcp']:
            self.send_response(200)
            content_type = 'text/html; charset=utf-8' if path == '/' else 'application/json'
            self.send_header('Content-type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        else:
            self.send_error(404)
    
    def do_GET(self):
        """Handle GET requests."""
        path = urlparse(self.path).path
        resume = load_resume()
        
        # Health check
        if path == '/health':
            self._json_response({"status": "ok", "message": "Resume server running"})
            return
        
        # HTML interface
        if path == '/':
            self._html_response(resume)
            return
        
        # Full resume JSON
        if path == '/resume':
            self._json_response(resume)
            return
        
        # Skills endpoint
        if path == '/skills':
            skills = resume.get('skills', {})
            self._json_response({"skills": skills, "count": len(skills)})
            return
        
        # Summary endpoint
        if path == '/summary':
            summary = {
                "name": resume.get('name', 'N/A'),
                "title": resume.get('title', 'N/A'),
                "location": resume.get('location', 'N/A'),
                "years_experience": resume.get('years_experience', 'N/A'),
                "skills_count": len(resume.get('skills', {})),
                "target_roles": resume.get('target_roles', {}),
                "top_skills": list(resume.get('skills', {}).keys())[:10]
            }
            self._json_response(summary)
            return
        
        # MCP endpoint (Model Context Protocol)
        if path == '/mcp':
            mcp_response = {
                "protocol": "mcp",
                "version": "1.0",
                "server": {
                    "name": "anix-resume-mcp",
                    "version": "1.0.0",
                    "description": "Resume data API for anixlynch - skills, target roles, and career information"
                },
                "capabilities": {
                    "resources": True,
                    "tools": True
                },
                "resources": [
                    {
                        "uri": "resume://full",
                        "name": "Full Resume",
                        "description": "Complete resume data including all fields",
                        "mimeType": "application/json",
                        "endpoint": "/resume"
                    },
                    {
                        "uri": "resume://skills",
                        "name": "Skills List",
                        "description": "Technical and professional skills",
                        "mimeType": "application/json",
                        "endpoint": "/skills"
                    },
                    {
                        "uri": "resume://summary",
                        "name": "Resume Summary",
                        "description": "Quick overview of key resume data",
                        "mimeType": "application/json",
                        "endpoint": "/summary"
                    }
                ],
                "tools": [
                    {
                        "name": "get_resume",
                        "description": "Get full resume data",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "get_skills",
                        "description": "Get skills list and proficiency levels",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "get_target_roles",
                        "description": "Get target job roles and positions",
                        "inputSchema": {
                            "type": "object",
                            "properties": {}
                        }
                    },
                    {
                        "name": "search_skills",
                        "description": "Search for specific skills",
                        "inputSchema": {
                            "type": "object",
                            "properties": {
                                "query": {
                                    "type": "string",
                                    "description": "Skill name to search for"
                                }
                            },
                            "required": ["query"]
                        }
                    }
                ],
                "endpoints": {
                    "health": "/health",
                    "resume": "/resume",
                    "skills": "/skills",
                    "summary": "/summary"
                },
                "authentication": {
                    "type": "none"
                }
            }
            self._json_response(mcp_response)
            return
        
        # 404 for everything else
        self.send_error(404, f"Path {path} not found")
    
    def do_POST(self):
        """Handle POST requests (for MCP JSON-RPC protocol)."""
        path = urlparse(self.path).path
        
        # MCP endpoint - handle JSON-RPC requests
        if path == '/mcp':
            try:
                content_length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(content_length).decode('utf-8')
                request_data = json.loads(body)
                
                method = request_data.get('method')
                request_id = request_data.get('id')
                
                # Handle initialize request
                if method == 'initialize':
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "protocolVersion": "2024-11-05",
                            "capabilities": {
                                "tools": {},
                                "resources": {}
                            },
                            "serverInfo": {
                                "name": "anix-resume-mcp",
                                "version": "1.0.0"
                            }
                        }
                    }
                    self._json_response(response)
                    return
                
                # Handle tools/list request
                elif method == 'tools/list':
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "result": {
                            "tools": [
                                {
                                    "name": "get_resume",
                                    "description": "Get full resume data",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {}
                                    }
                                },
                                {
                                    "name": "get_skills",
                                    "description": "Get skills list",
                                    "inputSchema": {
                                        "type": "object",
                                        "properties": {}
                                    }
                                }
                            ]
                        }
                    }
                    self._json_response(response)
                    return
                
                # Handle tools/call request
                elif method == 'tools/call':
                    params = request_data.get('params', {})
                    tool_name = params.get('name')
                    
                    resume = load_resume()
                    
                    if tool_name == 'get_resume':
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps(resume, indent=2)
                                    }
                                ]
                            }
                        }
                    elif tool_name == 'get_skills':
                        skills = resume.get('skills', {})
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "result": {
                                "content": [
                                    {
                                        "type": "text",
                                        "text": json.dumps({"skills": skills}, indent=2)
                                    }
                                ]
                            }
                        }
                    else:
                        response = {
                            "jsonrpc": "2.0",
                            "id": request_id,
                            "error": {
                                "code": -32601,
                                "message": f"Unknown tool: {tool_name}"
                            }
                        }
                    
                    self._json_response(response)
                    return
                
                # Unknown method
                else:
                    response = {
                        "jsonrpc": "2.0",
                        "id": request_id,
                        "error": {
                            "code": -32601,
                            "message": f"Method not found: {method}"
                        }
                    }
                    self._json_response(response)
                    return
                    
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": request_data.get('id') if 'request_data' in locals() else None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                self._json_response(error_response)
                return
        
        # 404 for other POST endpoints
        self.send_error(404, f"POST not supported for {path}")
    
    def _json_response(self, data):
        """Send JSON response."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2).encode('utf-8'))
    
    def _html_response(self, resume):
        """Send HTML response."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{resume.get('name', 'Resume')} - Resume MCP</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 40px;
            text-align: center;
        }}
        .header h1 {{ font-size: 2.5em; margin-bottom: 10px; }}
        .header p {{ font-size: 1.2em; opacity: 0.9; }}
        .status {{
            display: inline-block;
            background: #50fa7b;
            color: #2d2d2d;
            padding: 5px 15px;
            border-radius: 15px;
            font-size: 0.9em;
            font-weight: bold;
            margin-top: 10px;
        }}
        .content {{ padding: 40px; }}
        .section {{ margin-bottom: 30px; }}
        .section h2 {{ color: #667eea; margin-bottom: 15px; font-size: 1.5em; }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 15px;
        }}
        .info-card {{
            background: #f8f9fa;
            padding: 15px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        .info-card h3 {{ font-size: 0.9em; color: #666; margin-bottom: 5px; }}
        .info-card p {{ font-size: 1.1em; color: #333; font-weight: 500; }}
        .skills {{
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }}
        .skill-tag {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9em;
        }}
        .api-endpoints {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 10px;
        }}
        .api-endpoints code {{
            color: #50fa7b;
            display: block;
            margin: 5px 0;
            font-family: 'Monaco', monospace;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{resume.get('name', 'Resume')}</h1>
            <p>{resume.get('title', 'Professional Profile')}</p>
            <span class="status">● LIVE</span>
        </div>
        <div class="content">
            <div class="section">
                <h2>Quick Info</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h3>Location</h3>
                        <p>{resume.get('location', 'Remote')}</p>
                    </div>
                    <div class="info-card">
                        <h3>Experience</h3>
                        <p>{resume.get('years_experience', 'N/A')} years</p>
                    </div>
                    <div class="info-card">
                        <h3>Total Skills</h3>
                        <p>{len(resume.get('skills', {}))} skills</p>
                    </div>
                    <div class="info-card">
                        <h3>Target Roles</h3>
                        <p>{len(resume.get('target_roles', {}))} categories</p>
                    </div>
                </div>
            </div>
            
            <div class="section">
                <h2>Top Skills</h2>
                <div class="skills">
                    {''.join(f'<span class="skill-tag">{skill}</span>' for skill in list(resume.get('skills', {}).keys())[:10])}
                </div>
            </div>
            
            <div class="section">
                <h2>Target Roles</h2>
                <div class="skills">
                    {''.join(f'<span class="skill-tag">{role}</span>' for roles in resume.get('target_roles', {}).values() for role in (roles[:5] if isinstance(roles, list) else []))}
                </div>
            </div>
            
            <div class="section">
                <h2>API Endpoints</h2>
                <div class="api-endpoints">
                    <code>GET  /              # This page</code>
                    <code>GET  /health        # Health check</code>
                    <code>GET  /resume        # Full resume JSON</code>
                    <code>GET  /skills        # Skills list</code>
                    <code>GET  /summary       # Resume summary</code>
                </div>
            </div>
            
            <div class="section">
                <h2>About This Server</h2>
                <p>Simple HTTP server exposing resume data via ngrok.</p>
                <p style="margin-top: 10px;"><strong>Powered by:</strong> Python 3 + ngrok</p>
            </div>
        </div>
    </div>
</body>
</html>"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(html.encode('utf-8'))
    
    def log_message(self, format, *args):
        """Custom log format."""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(port=PORT):
    """Run the HTTP server."""
    server_address = ('', port)
    httpd = HTTPServer(server_address, ResumeHandler)
    print(f">> Resume MCP Server running on port {port}")
    print(f">> Local:   http://localhost:{port}")
    print(f">> Network: http://0.0.0.0:{port}")
    print(f"\n>> Ready for ngrok! Run: ngrok http {port}")
    print(f"\n>> Press Ctrl+C to stop\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n>> Server stopped")


if __name__ == "__main__":
    run_server()

