#!/usr/bin/env python3
"""
Web-only entry point for Render deployment.
Serves the dashboard without camera/detection functionality.
"""

import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="Area Monitoring System - Web Dashboard",
    description="Web-based dashboard for area monitoring (demo mode)",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/web"), name="static")

@app.get("/", response_class=HTMLResponse)
async def dashboard():
    """Serve the main dashboard."""
    with open("app/web/index.html", "r") as f:
        return HTMLResponse(content=f.read())

@app.get("/dashboard.js")
async def dashboard_js():
    """Serve the dashboard JavaScript."""
    return FileResponse("app/web/dashboard.js", media_type="application/javascript")

@app.get("/styles.css")
async def dashboard_css():
    """Serve the dashboard CSS."""
    return FileResponse("app/web/styles.css", media_type="text/css")

@app.get("/api/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "mode": "web-only", "message": "Dashboard running in demo mode"}

@app.get("/api/status")
async def system_status():
    """System status endpoint."""
    return {
        "system": "online",
        "mode": "web-demo",
        "camera": "not available (server environment)",
        "detection": "not available (server environment)",
        "dashboard": "active"
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(
        "web_main:app",
        host="0.0.0.0",
        port=port,
        reload=False
    )
