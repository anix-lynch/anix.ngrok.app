#!/usr/bin/env python3
"""
Resume API Server - PUBLIC VERSION
Simple HTTP server that serves resume data via ngrok
NO AUTHENTICATION - Public access for AI tools
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
    """HTTP request handler for resume API - PUBLIC ACCESS."""

    def do_HEAD(self):
        """Handle HEAD requests (for ngrok health checks)."""
        path = urlparse(self.path).path
        if path in ['/', '/health', '/resume', '/resume.json', '/skills', '/summary']:
            self.send_response(200)
            content_type = 'text/html; charset=utf-8' if path == '/' else 'application/json'
            self.send_header('Content-type', content_type)
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
        else:
            self.send_error(404)

    def do_GET(self):
        """Handle GET requests - ALL ENDPOINTS PUBLIC."""
        path = urlparse(self.path).path
        resume = load_resume()

        # Health check
        if path == '/health':
            self._json_response({"status": "ok", "message": "Resume server running", "public": True})
            return

        # HTML interface
        if path == '/':
            self._html_response(resume)
            return

        # Full resume JSON - PUBLIC
        if path == '/resume' or path == '/resume.json':
            self._json_response(resume)
            return

        # Skills endpoint - PUBLIC
        if path == '/skills':
            skills = resume.get('skills', {})
            self._json_response({"skills": skills, "count": len(skills)})
            return

        # Summary endpoint - PUBLIC
        if path == '/summary':
            summary = {
                "name": resume.get('name', 'N/A'),
                "title": resume.get('title', 'N/A'),
                "location": resume.get('location', 'N/A'),
                "email": resume.get('email', 'N/A'),
                "phone": resume.get('phone', 'N/A'),
                "linkedin": resume.get('linkedin', 'N/A'),
                "github": resume.get('github', 'N/A'),
                "skills_count": len(resume.get('skills', {})),
                "target_roles": resume.get('target_roles', {}),
                "top_skills": self._extract_top_skills(resume)
            }
            self._json_response(summary)
            return

        # 404 for everything else
        self.send_error(404, f"Path {path} not found")

    def _extract_top_skills(self, resume):
        """Extract top skills from all categories."""
        all_skills = []
        skills_dict = resume.get('skills', {})

        for category, skills in skills_dict.items():
            if isinstance(skills, dict):
                for skill, level in skills.items():
                    all_skills.append(skill.replace('_', ' '))

        return all_skills[:20]  # Top 20 skills

    def _json_response(self, data):
        """Send JSON response with CORS headers."""
        self.send_response(200)
        self.send_header('Content-type', 'application/json; charset=utf-8')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.send_header('Cache-Control', 'public, max-age=300')  # 5 min cache
        self.end_headers()
        self.wfile.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))

    def _html_response(self, resume):
        """Send HTML response."""
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{resume.get('name', 'Resume')} - PUBLIC API</title>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 900px;
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
        .badge {{
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
        .endpoints {{
            background: #2d2d2d;
            color: #f8f8f2;
            padding: 20px;
            border-radius: 10px;
            margin: 20px 0;
        }}
        .endpoints code {{
            color: #50fa7b;
            display: block;
            margin: 8px 0;
            font-family: 'Monaco', monospace;
            font-size: 0.95em;
        }}
        .info-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin-top: 20px;
        }}
        .info-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 4px solid #667eea;
        }}
        .info-card h3 {{ font-size: 0.9em; color: #666; margin-bottom: 8px; }}
        .info-card p {{ font-size: 1.1em; color: #333; font-weight: 500; }}
        .note {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 20px 0;
            border-radius: 5px;
        }}
        .note strong {{ color: #856404; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>{resume.get('name', 'Resume API')}</h1>
            <p>{resume.get('title', 'Professional Profile')}</p>
            <span class="badge">✓ PUBLIC API - NO AUTH REQUIRED</span>
        </div>
        <div class="content">
            <div class="note">
                <strong>For AI Tools:</strong> This API is publicly accessible. Use the endpoints below to fetch resume data.
            </div>

            <div class="section">
                <h2>Quick Info</h2>
                <div class="info-grid">
                    <div class="info-card">
                        <h3>Name</h3>
                        <p>{resume.get('name', 'N/A')}</p>
                    </div>
                    <div class="info-card">
                        <h3>Title</h3>
                        <p>{resume.get('title', 'N/A')}</p>
                    </div>
                    <div class="info-card">
                        <h3>Location</h3>
                        <p>{resume.get('location', 'N/A')}</p>
                    </div>
                    <div class="info-card">
                        <h3>Email</h3>
                        <p>{resume.get('email', 'N/A')}</p>
                    </div>
                </div>
            </div>

            <div class="section">
                <h2>Public API Endpoints</h2>
                <div class="endpoints">
                    <code>GET  https://anix.ngrok.app/              # This page</code>
                    <code>GET  https://anix.ngrok.app/health        # Health check</code>
                    <code>GET  https://anix.ngrok.app/resume        # Full resume JSON</code>
                    <code>GET  https://anix.ngrok.app/resume.json   # Same as /resume</code>
                    <code>GET  https://anix.ngrok.app/skills        # Skills list</code>
                    <code>GET  https://anix.ngrok.app/summary       # Resume summary</code>
                </div>
            </div>

            <div class="section">
                <h2>For Perplexity, ChatGPT, Claude, and other AI tools:</h2>
                <p style="line-height: 1.8;">
                    Simply fetch any endpoint above. No authentication required.<br>
                    Example: <code style="background:#f0f0f0;padding:5px;border-radius:3px;">curl https://anix.ngrok.app/resume</code>
                </p>
            </div>

            <div class="section">
                <h2>Response Format</h2>
                <p>All endpoints return JSON with:</p>
                <ul style="line-height: 2; margin-left: 20px; margin-top: 10px;">
                    <li>Content-Type: application/json</li>
                    <li>CORS: enabled (*)</li>
                    <li>Cache: 5 minutes</li>
                </ul>
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
    print(f">> Resume API Server (PUBLIC) running on port {port}")
    print(f">> Local:   http://localhost:{port}")
    print(f">> Network: http://0.0.0.0:{port}")
    print(f">> PUBLIC:  https://anix.ngrok.app")
    print(f"\n>> ✓ NO AUTHENTICATION - Public access enabled")
    print(f">> ✓ AI tools (Perplexity, ChatGPT, Claude) can access")
    print(f"\n>> Press Ctrl+C to stop\n")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n>> Server stopped")


if __name__ == "__main__":
    run_server()
