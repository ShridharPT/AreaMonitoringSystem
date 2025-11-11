"""
FastAPI application for Area Monitoring System
Provides REST API for monitoring and control
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from app.api.routes import router
from app.utils import get_logger

logger = get_logger(__name__)


def create_app() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title="Area Monitoring System API",
        description="REST API for real-time person detection and zone monitoring",
        version="2.0.0",
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json"
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Mount static files (web dashboard) - BEFORE routes
    web_dir = Path(__file__).parent.parent / "web"
    if web_dir.exists():
        try:
            app.mount("/static", StaticFiles(directory=str(web_dir)), name="static")
            logger.info(f"Static files mounted from {web_dir}")
        except Exception as e:
            logger.error(f"Failed to mount static files: {e}")
    
    # Root endpoint - serve dashboard
    @app.get("/", include_in_schema=False)
    async def root():
        """Serve web dashboard"""
        dashboard_file = Path(__file__).parent.parent / "web" / "index.html"
        if dashboard_file.exists():
            return FileResponse(str(dashboard_file), media_type="text/html")
        return {
            "name": "Area Monitoring System",
            "version": "2.0.0",
            "api_docs": "/api/docs",
            "dashboard": "/",
            "status": "running"
        }
    
    # Serve CSS
    @app.get("/styles.css", include_in_schema=False)
    async def serve_css():
        """Serve CSS file"""
        css_file = Path(__file__).parent.parent / "web" / "styles.css"
        if css_file.exists():
            return FileResponse(str(css_file), media_type="text/css")
        return {"error": "CSS not found"}
    
    # Serve JavaScript
    @app.get("/dashboard.js", include_in_schema=False)
    async def serve_js():
        """Serve JavaScript file"""
        js_file = Path(__file__).parent.parent / "web" / "dashboard.js"
        if js_file.exists():
            return FileResponse(str(js_file), media_type="application/javascript")
        return {"error": "JavaScript not found"}
    
    # Dashboard endpoint
    @app.get("/dashboard", include_in_schema=False)
    async def dashboard():
        """Serve dashboard"""
        dashboard_file = Path(__file__).parent.parent / "web" / "index.html"
        if dashboard_file.exists():
            return FileResponse(str(dashboard_file), media_type="text/html")
        return {"error": "Dashboard not found"}
    
    # Exception handlers
    @app.exception_handler(Exception)
    async def general_exception_handler(request, exc):
        """Handle general exceptions"""
        logger.error(f"Unhandled exception: {exc}")
        return JSONResponse(
            status_code=500,
            content={"detail": "Internal server error"}
        )
    
    # Startup event
    @app.on_event("startup")
    async def startup_event():
        """Startup event"""
        logger.info("FastAPI application started")
    
    # Shutdown event
    @app.on_event("shutdown")
    async def shutdown_event():
        """Shutdown event"""
        logger.info("FastAPI application shutdown")
    
    return app


# Create app instance
app = create_app()


if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
