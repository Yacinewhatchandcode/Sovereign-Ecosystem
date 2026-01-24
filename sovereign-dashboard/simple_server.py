#!/usr/bin/env python3
"""Ultra-minimal HTTP server for dashboard"""
import http.server
import socketserver
from pathlib import Path

PORT = 8083
DIRECTORY = Path(__file__).parent

class MyHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(DIRECTORY), **kwargs)

print(f"🚀 Server starting at http://localhost:{PORT}")
print(f"   Serving: {DIRECTORY}/index.html")

with socketserver.TCPServer(("", PORT), MyHandler) as httpd:
    print(f"✅ Server running! Open: http://localhost:{PORT}")
    httpd.serve_forever()
