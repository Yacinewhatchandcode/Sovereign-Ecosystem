#!/usr/bin/env python3
"""
MINIMAL Working Dashboard Server
Serves the index.html and basic API endpoints without complex initialization
"""

from aiohttp import web
from pathlib import Path
import json

class MinimalServer:
    def __init__(self):
        self.port = 8082
        
    async def index_handler(self, request):
        """Serve index.html"""
        index_path = Path(__file__).parent / "index.html"
        if index_path.exists():
            return web.FileResponse(index_path)
        return web.Response(text="index.html not found", status=404)
    
    async def status_handler(self, request):
        """API status"""
        return web.json_response({"status": "ok", "message": "Minimal server running"})
    
    async def agents_config_handler(self, request):
        """Return empty agents for now"""
        return web.json_response([])
    
    def create_app(self):
        app = web.Application()
        
        # Routes
        app.router.add_get("/", self.index_handler)
        app.router.add_get("/api/status", self.status_handler)
        app.router.add_get("/api/agents/config", self.agents_config_handler)
        app.router.add_get("/api/agents/all", self.agents_config_handler)
        
        return app
    
    def run(self):
        app = self.create_app()
        print(f"🚀 Minimal server starting on http://localhost:{self.port}")
        print(f"   Dashboard: http://localhost:{self.port}")
        web.run_app(app, host='0.0.0.0', port=self.port, print=None)


if __name__ == '__main__':
    server = MinimalServer()
    server.run()
