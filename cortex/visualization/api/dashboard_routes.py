"""
FastAPI Dashboard Routes.

Provides REST API endpoints for CORTEX LENS Dashboard generation and serving.

AC-ID: LENS-DASH-013
Author: Asif Hussain
Phase: 14
"""

from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from pydantic import BaseModel

from cortex.orchestrators.support.lens_visualization_orchestrator import (
    LENSVisualizationOrchestrator,
)

# Configuration
DASHBOARD_ROOT = Path.cwd() / ".cortex" / "lens-dashboard"
VERSION = "1.0.0"

# Initialize FastAPI app
app = FastAPI(
    title="CORTEX LENS Dashboard API",
    description="REST API for generating and serving LENS dashboards",
    version=VERSION,
)

# Add CORS middleware for local development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict to specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class DashboardGenerateRequest(BaseModel):
    """Request model for dashboard generation."""

    repository_path: str
    output_path: Optional[str] = None

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "repository_path": "/path/to/repository",
                "output_path": "/custom/output/path",
            }
        }


class DashboardGenerateResponse(BaseModel):
    """Response model for dashboard generation."""

    status: str
    dashboard_path: str
    repository_name: str
    message: str

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "status": "success",
                "dashboard_path": "/path/to/dashboard",
                "repository_name": "my-repo",
                "message": "Dashboard generated successfully",
            }
        }


class HealthCheckResponse(BaseModel):
    """Response model for health check."""

    status: str
    version: str

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "status": "healthy",
                "version": "1.0.0",
            }
        }


class DashboardListResponse(BaseModel):
    """Response model for dashboard list."""

    dashboards: list[str]
    count: int

    class Config:
        """Pydantic config."""

        schema_extra = {
            "example": {
                "dashboards": ["repo1", "repo2", "repo3"],
                "count": 3,
            }
        }


# Endpoints
@app.get("/api/lens/dashboard/health", response_model=HealthCheckResponse)
async def health_check() -> HealthCheckResponse:
    """
    Health check endpoint.

    Returns:
        Health status and version information

    Example:
        >>> GET /api/lens/dashboard/health
        {"status": "healthy", "version": "1.0.0"}
    """
    return HealthCheckResponse(status="healthy", version=VERSION)


@app.post(
    "/api/lens/dashboard/generate",
    response_model=DashboardGenerateResponse,
    status_code=200,
)
async def generate_dashboard(
    request: DashboardGenerateRequest,
) -> DashboardGenerateResponse:
    """
    Generate LENS dashboard for a repository.

    Args:
        request: Dashboard generation request with repository path

    Returns:
        Dashboard generation response with output path

    Raises:
        HTTPException: If repository path doesn't exist or generation fails

    Example:
        >>> POST /api/lens/dashboard/generate
        >>> {"repository_path": "/path/to/repo"}
        {"status": "success", "dashboard_path": "...", ...}
    """
    repo_path = Path(request.repository_path)

    # Validate repository path
    if not repo_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Repository path not found: {request.repository_path}",
        )

    if not repo_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Repository path is not a directory: {request.repository_path}",
        )

    try:
        # Initialize orchestrator
        orchestrator = LENSVisualizationOrchestrator(repo_path=repo_path)

        # Determine output path
        output_path = (
            Path(request.output_path)
            if request.output_path
            else DASHBOARD_ROOT / repo_path.name
        )

        # Generate dashboard
        dashboard_path = orchestrator.generate_dashboard(output_dir=output_path)

        return DashboardGenerateResponse(
            status="success",
            dashboard_path=str(dashboard_path),
            repository_name=repo_path.name,
            message="Dashboard generated successfully",
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dashboard generation failed: {str(e)}",
        )


@app.get("/api/lens/dashboard/list", response_model=DashboardListResponse)
async def list_dashboards() -> DashboardListResponse:
    """
    List all available dashboards.

    Returns:
        List of dashboard directory names

    Example:
        >>> GET /api/lens/dashboard/list
        {"dashboards": ["repo1", "repo2"], "count": 2}
    """
    if not DASHBOARD_ROOT.exists():
        return DashboardListResponse(dashboards=[], count=0)

    dashboards = [
        d.name for d in DASHBOARD_ROOT.iterdir() if d.is_dir()
    ]

    return DashboardListResponse(
        dashboards=sorted(dashboards),
        count=len(dashboards),
    )


@app.get("/api/lens/dashboard/{repo_name}/metadata")
async def get_dashboard_metadata(repo_name: str) -> JSONResponse:
    """
    Get metadata for a specific dashboard.

    Args:
        repo_name: Repository/dashboard name

    Returns:
        Dashboard metadata JSON

    Raises:
        HTTPException: If dashboard or metadata doesn't exist

    Example:
        >>> GET /api/lens/dashboard/my-repo/metadata
        {"repository": "my-repo", "generated_at": "2026-01-29", ...}
    """
    dashboard_path = DASHBOARD_ROOT / repo_name
    metadata_file = dashboard_path / "metadata.json"

    if not dashboard_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Dashboard not found: {repo_name}",
        )

    if not metadata_file.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Metadata not found for dashboard: {repo_name}",
        )

    try:
        import json
        with open(metadata_file) as f:
            metadata = json.load(f)
        return JSONResponse(content=metadata)
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to read metadata: {str(e)}",
        )


@app.get("/api/lens/dashboard/{path:path}")
async def serve_dashboard_file(path: str) -> FileResponse:
    """
    Serve static dashboard files.

    Args:
        path: Relative file path within dashboard

    Returns:
        File response

    Raises:
        HTTPException: If file doesn't exist

    Example:
        >>> GET /api/lens/dashboard/my-repo/index.html
        <HTML content>
    """
    file_path = DASHBOARD_ROOT / path

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(
            status_code=404,
            detail=f"File not found: {path}",
        )

    return FileResponse(
        path=file_path,
        media_type="application/octet-stream",
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    """
    Global exception handler for unexpected errors.

    Args:
        request: Request object
        exc: Exception

    Returns:
        JSON error response
    """
    return JSONResponse(
        status_code=500,
        content={
            "detail": f"Internal server error: {str(exc)}",
            "type": type(exc).__name__,
        },
    )
