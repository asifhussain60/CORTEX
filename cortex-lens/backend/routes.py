"""FastAPI Routes for LENS Dashboard.

Provides RESTful API endpoints for dashboard data generation and retrieval.
These routes integrate with the CORTEX MCP infrastructure.

Endpoints:
    POST /api/dashboard/generate - Generate dashboard for a repository
    GET /api/dashboard/tab/{tab_id} - Get data for a specific tab
    GET /api/dashboard/overview - Get repository overview
    GET /api/dashboard/cache - List cached dashboards
    DELETE /api/dashboard/cache/{repo_path} - Invalidate cache
"""

from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

# Use relative imports since cortex-lens has a hyphen
from .orchestrator import (
    DashboardOrchestrator,
    DashboardData,
    get_dashboard_orchestrator,
)
from .cache_manager import CacheManager, get_cache_manager


# Create router with prefix
router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


# ============================================================================
# Request/Response Models
# ============================================================================

class DashboardRequest(BaseModel):
    """Request model for dashboard generation.
    
    Attributes:
        repo_path: Path to the repository to analyze
        force_refresh: If True, ignore cache and regenerate
        tabs: Optional list of specific tabs to generate
    """
    repo_path: str = Field(..., description="Path to repository")
    force_refresh: bool = Field(False, description="Ignore cache and regenerate")
    tabs: Optional[List[str]] = Field(None, description="Specific tabs to generate")


class DashboardResponse(BaseModel):
    """Response model for dashboard data.
    
    Attributes:
        repo_path: Path to the analyzed repository
        repo_name: Name of the repository
        is_cortex: Whether this is CORTEX self-analysis
        tabs: List of tab data
        overview: Repository overview data
        generated_at: ISO timestamp of generation
        output_path: Path where dashboard was saved
    """
    repo_path: str
    repo_name: str
    is_cortex: bool
    tabs: List[Dict[str, Any]]
    overview: Dict[str, Any]
    generated_at: str
    output_path: Optional[str] = None


class TabDataResponse(BaseModel):
    """Response model for single tab data."""
    tab_id: str
    tab_name: str
    data: Dict[str, Any]
    metadata: Dict[str, Any]


class CacheEntryResponse(BaseModel):
    """Response model for cache entries."""
    repo_path: str
    output_path: str
    created_at: str
    expires_at: str
    is_cortex: bool
    is_expired: bool


class HealthResponse(BaseModel):
    """Response model for health check."""
    status: str
    version: str
    cache_entries: int


# ============================================================================
# API Endpoints
# ============================================================================

@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Health check endpoint.
    
    Returns:
        Health status and basic metrics
    """
    cache_manager = get_cache_manager()
    entries = cache_manager.list_cached()
    
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        cache_entries=len(entries),
    )


@router.post("/generate", response_model=DashboardResponse)
async def generate_dashboard(request: DashboardRequest) -> DashboardResponse:
    """Generate dashboard for a repository.
    
    This endpoint triggers full dashboard generation including:
    - Repository type detection (CORTEX vs external)
    - Tab data generation (5 universal + 3 CORTEX-specific)
    - Business language overview generation
    - Cache registration
    
    Args:
        request: Dashboard generation request
        
    Returns:
        Complete dashboard data
        
    Raises:
        HTTPException: If repository path is invalid or generation fails
    """
    repo_path = Path(request.repo_path)
    
    # Validate repository path
    if not repo_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Repository not found: {request.repo_path}",
        )
    
    if not repo_path.is_dir():
        raise HTTPException(
            status_code=400,
            detail=f"Path is not a directory: {request.repo_path}",
        )
    
    try:
        orchestrator = get_dashboard_orchestrator()
        dashboard = orchestrator.generate_dashboard(
            repo_path,
            force_refresh=request.force_refresh,
        )
        
        # Save dashboard
        output_path = orchestrator.save_dashboard(dashboard)
        
        return DashboardResponse(
            repo_path=dashboard.repo_path,
            repo_name=dashboard.repo_name,
            is_cortex=dashboard.is_cortex,
            tabs=[t.to_dict() for t in dashboard.tabs],
            overview=dashboard.overview,
            generated_at=dashboard.generated_at,
            output_path=str(output_path),
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Dashboard generation failed: {str(e)}",
        )


@router.get("/tab/{tab_id}", response_model=TabDataResponse)
async def get_tab_data(
    tab_id: str,
    repo_path: str = Query(..., description="Path to repository"),
) -> TabDataResponse:
    """Get data for a specific tab.
    
    Args:
        tab_id: Tab identifier (overview, dependencies, classes, etc.)
        repo_path: Path to the repository
        
    Returns:
        Tab-specific data
        
    Raises:
        HTTPException: If tab not found or data unavailable
    """
    path = Path(repo_path)
    
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Repository not found: {repo_path}",
        )
    
    # Check cache first
    cache_manager = get_cache_manager()
    cached = cache_manager.get_cached(path)
    
    if cached:
        # Load from cache
        import json
        cache_path = Path(cached.output_path) / "dashboard_data.json"
        if cache_path.exists():
            with open(cache_path) as f:
                data = json.load(f)
            
            # Find the requested tab
            for tab in data.get("tabs", []):
                if tab["tab_id"] == tab_id:
                    return TabDataResponse(
                        tab_id=tab["tab_id"],
                        tab_name=tab["tab_name"],
                        data=tab["data"],
                        metadata=tab.get("metadata", {}),
                    )
    
    # Tab not in cache, generate on demand
    orchestrator = get_dashboard_orchestrator()
    dashboard = orchestrator.generate_dashboard(path)
    
    for tab in dashboard.tabs:
        if tab.tab_id == tab_id:
            return TabDataResponse(
                tab_id=tab.tab_id,
                tab_name=tab.tab_name,
                data=tab.data,
                metadata=tab.metadata,
            )
    
    raise HTTPException(
        status_code=404,
        detail=f"Tab not found: {tab_id}",
    )


@router.get("/overview")
async def get_overview(
    repo_path: str = Query(..., description="Path to repository"),
) -> Dict[str, Any]:
    """Get repository overview (business language description).
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Repository overview data including:
        - summary: Business language description
        - capabilities: Detected capabilities
        - tech_stack: Technology stack
        - architecture: Architecture patterns
        - confidence: Confidence score
    """
    path = Path(repo_path)
    
    if not path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Repository not found: {repo_path}",
        )
    
    # Check cache first
    cache_manager = get_cache_manager()
    cached = cache_manager.get_cached(path)
    
    if cached:
        import json
        cache_path = Path(cached.output_path) / "dashboard_data.json"
        if cache_path.exists():
            with open(cache_path) as f:
                data = json.load(f)
            return data.get("overview", {})
    
    # Generate fresh overview
    from cortex.visualization.business_language_generator import (
        BusinessLanguageGenerator,
    )
    
    generator = BusinessLanguageGenerator()
    try:
        description = generator.generate_description(path)
        return {
            "summary": description.summary,
            "capabilities": [c.to_dict() for c in description.capabilities],
            "tech_stack": description.tech_stack.to_dict() if description.tech_stack else {},
            "architecture": description.architecture.to_dict() if description.architecture else {},
            "confidence": description.confidence,
        }
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Overview generation failed: {str(e)}",
        )


@router.get("/cache", response_model=List[CacheEntryResponse])
async def list_cache() -> List[CacheEntryResponse]:
    """List all cached dashboards.
    
    Returns:
        List of cache entries with expiration status
    """
    cache_manager = get_cache_manager()
    entries = cache_manager.list_cached()
    
    return [
        CacheEntryResponse(
            repo_path=e.repo_path,
            output_path=e.output_path,
            created_at=e.created_at.isoformat(),
            expires_at=e.expires_at.isoformat(),
            is_cortex=e.is_cortex,
            is_expired=e.is_expired(),
        )
        for e in entries
    ]


@router.delete("/cache")
async def invalidate_cache(
    repo_path: str = Query(..., description="Path to repository"),
) -> Dict[str, Any]:
    """Invalidate cache for a repository.
    
    Args:
        repo_path: Path to the repository
        
    Returns:
        Status message
    """
    cache_manager = get_cache_manager()
    success = cache_manager.invalidate(Path(repo_path))
    
    return {
        "success": success,
        "message": "Cache invalidated" if success else "No cache entry found",
        "repo_path": repo_path,
    }


@router.post("/cache/cleanup")
async def cleanup_cache(
    max_age_days: int = Query(30, description="Maximum age in days"),
) -> Dict[str, Any]:
    """Cleanup old cached dashboards.
    
    Args:
        max_age_days: Maximum age before removal (default 30)
        
    Returns:
        Number of entries removed
    """
    cache_manager = get_cache_manager()
    
    # Cleanup expired entries
    expired_removed = cache_manager.cleanup_expired()
    
    # Cleanup old dashboards
    old_removed = cache_manager.cleanup_old_dashboards(max_age_days)
    
    return {
        "expired_removed": expired_removed,
        "old_removed": old_removed,
        "total_removed": expired_removed + old_removed,
    }


# ============================================================================
# MCP Tool Integration
# ============================================================================

def register_mcp_tools() -> Dict[str, Any]:
    """Register dashboard API as MCP tools.
    
    This function is called by the CORTEX MCP infrastructure to
    expose dashboard capabilities as MCP tools.
    
    Returns:
        Dictionary of MCP tool definitions
    """
    return {
        "lens_dashboard_generate": {
            "name": "lens_dashboard_generate",
            "description": "Generate LENS Dashboard for a repository",
            "parameters": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to the repository to analyze",
                    "required": True,
                },
                "force_refresh": {
                    "type": "boolean",
                    "description": "Ignore cache and regenerate",
                    "required": False,
                    "default": False,
                },
            },
            "handler": "cortex_lens.backend.routes:generate_dashboard",
        },
        "lens_dashboard_tab": {
            "name": "lens_dashboard_tab",
            "description": "Get data for a specific dashboard tab",
            "parameters": {
                "tab_id": {
                    "type": "string",
                    "description": "Tab identifier",
                    "required": True,
                },
                "repo_path": {
                    "type": "string",
                    "description": "Path to the repository",
                    "required": True,
                },
            },
            "handler": "cortex_lens.backend.routes:get_tab_data",
        },
        "lens_dashboard_overview": {
            "name": "lens_dashboard_overview",
            "description": "Get business language overview of a repository",
            "parameters": {
                "repo_path": {
                    "type": "string",
                    "description": "Path to the repository",
                    "required": True,
                },
            },
            "handler": "cortex_lens.backend.routes:get_overview",
        },
    }
