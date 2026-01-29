"""
CORTEX LENS Dashboard - Main Entry Point Application.

FastAPI server for serving self-contained LENS Dashboard SPA:
- Routes / → repo-dashboards.html (repository browser)
- Routes /cortex → cortex-dashboard.html (CORTEX direct access)
- Routes /api/* → Dashboard data endpoints
- Serves static assets from cortex/visualization/static/

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-007
Task: 020 - HTTP Server & Entry Points
"""

from pathlib import Path
from typing import Optional
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from cortex.visualization.scripts.lazy_module_loader import get_lazy_loader


# Initialize FastAPI app
app = FastAPI(
    title="CORTEX LENS Dashboard",
    description="AI-powered code intelligence dashboard",
    version="1.0.0",
)

# Path configuration
CORTEX_LENS_DIR = Path(__file__).parent
CORTEX_VISUALIZATION_DIR = Path(__file__).parent.parent / "cortex" / "visualization"

# Mount static files
app.mount(
    "/static",
    StaticFiles(directory=str(CORTEX_VISUALIZATION_DIR / "static")),
    name="static",
)

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(CORTEX_VISUALIZATION_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """
    Main entry point: Repository browser with tiles.
    
    Shows recent repository analyses as clickable tiles.
    Users can add new repositories or select existing ones.
    
    Returns:
        HTMLResponse with repo-dashboards.html content
    """
    # Load entry point HTML
    entry_point = CORTEX_LENS_DIR / "repo-dashboards.html"
    
    if not entry_point.exists():
        return HTMLResponse(
            content="<h1>Dashboard Not Found</h1><p>Please run: cortex lens dashboard setup</p>",
            status_code=404,
        )
    
    content = entry_point.read_text()
    return HTMLResponse(content=content)


@app.get("/cortex", response_class=HTMLResponse)
async def cortex_dashboard(request: Request) -> HTMLResponse:
    """
    Direct access to CORTEX repository 8-tab dashboard.
    
    Bypasses repository selection and shows full CORTEX analysis:
    - 5 universal tabs
    - 3 CORTEX-specific tabs
    
    Returns:
        HTMLResponse with cortex-dashboard.html content
    """
    entry_point = CORTEX_LENS_DIR / "cortex-dashboard.html"
    
    if not entry_point.exists():
        return HTMLResponse(
            content="<h1>CORTEX Dashboard Not Found</h1>",
            status_code=404,
        )
    
    content = entry_point.read_text()
    return HTMLResponse(content=content)


@app.get("/api/loader/manifest")
async def get_loader_manifest() -> JSONResponse:
    """
    Get lazy module loader manifest.
    
    Returns:
        JSON manifest with module metadata and tab requirements
    """
    loader = get_lazy_loader()
    manifest_str = loader.generate_manifest_json()
    
    import json
    manifest = json.loads(manifest_str)
    
    return JSONResponse(content=manifest)


@app.get("/api/loader/javascript")
async def get_loader_javascript() -> str:
    """
    Get lazy module loader JavaScript code.
    
    Returns:
        JavaScript code for lazy loading modules
    """
    loader = get_lazy_loader()
    js_code = loader.generate_loader_javascript(base_url="/static/")
    
    from fastapi import Response
    return Response(content=js_code, media_type="application/javascript")


@app.get("/api/repositories")
async def list_repositories() -> JSONResponse:
    """
    List recently analyzed repositories.
    
    Returns:
        JSON array of repository metadata
    """
    # TODO: Implement repository listing from cache
    # For now, return mock data
    repositories = [
        {
            "id": "cortex",
            "name": "CORTEX",
            "path": "/path/to/CORTEX",
            "is_cortex": True,
            "tabs": 8,
            "last_analyzed": "2026-01-29T10:00:00Z",
        },
    ]
    
    return JSONResponse(content=repositories)


@app.get("/api/dashboard/tabs/{repo_id}")
async def get_dashboard_tabs(repo_id: str) -> JSONResponse:
    """
    Get applicable tabs for a repository.
    
    Args:
        repo_id: Repository identifier
    
    Returns:
        JSON array of tab configurations
    """
    # TODO: Implement tab configuration logic
    # For now, return mock data
    tabs = [
        {"id": "repository_overview", "name": "Repository Overview", "icon": "📦"},
        {"id": "dependency_graph", "name": "Dependency Graph", "icon": "🕸️"},
        {"id": "class_diagram", "name": "Class Diagrams", "icon": "📊"},
        {"id": "git_timeline", "name": "Temporal Analysis", "icon": "📈"},
        {"id": "author_network", "name": "Author Network", "icon": "👥"},
    ]
    
    return JSONResponse(content=tabs)


@app.get("/health")
async def health_check() -> JSONResponse:
    """
    Health check endpoint.
    
    Returns:
        JSON with status and version
    """
    return JSONResponse(content={
        "status": "healthy",
        "version": "1.0.0",
        "service": "cortex-lens-dashboard",
    })


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8888)
