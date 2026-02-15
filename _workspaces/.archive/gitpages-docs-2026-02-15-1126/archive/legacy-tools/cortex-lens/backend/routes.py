"""LENS Dashboard API Routes.

FastAPI routes for the LENS Dashboard backend, providing:
- Dashboard generation endpoints
- Repository analysis endpoints
- Cache management endpoints

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Optional, List, Dict, Any

try:
    from fastapi import APIRouter, HTTPException
    from pydantic import BaseModel
    HAS_FASTAPI = True
except ImportError:
    HAS_FASTAPI = False
    # Create placeholder for when FastAPI is not installed
    class BaseModel:
        """Placeholder BaseModel when FastAPI not available."""
        pass
    
    class APIRouter:
        """Placeholder APIRouter when FastAPI not available."""
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            pass
        
        def get(self, *args: Any, **kwargs: Any) -> Any:
            def decorator(func: Any) -> Any:
                return func
            return decorator
        
        def post(self, *args: Any, **kwargs: Any) -> Any:
            def decorator(func: Any) -> Any:
                return func
            return decorator


# Create router
router = APIRouter(prefix="/api/v1/dashboard", tags=["dashboard"])


class DashboardRequest(BaseModel):
    """Request model for dashboard generation.
    
    Attributes:
        repo_path: Path to repository to analyze
        is_cortex: Whether this is the CORTEX repository
        force_refresh: Force regeneration even if cached
        output_path: Custom output path (optional)
    """
    repo_path: str
    is_cortex: bool = False
    force_refresh: bool = False
    output_path: Optional[str] = None


class DashboardResponse(BaseModel):
    """Response model for dashboard generation.
    
    Attributes:
        success: Whether generation succeeded
        output_path: Path where dashboard was generated
        url: URL to access the dashboard
        tabs: List of generated tab names
        error: Error message if failed
    """
    success: bool
    output_path: Optional[str] = None
    url: Optional[str] = None
    tabs: List[str] = []
    error: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health check.
    
    Attributes:
        status: Service status (healthy/degraded/unhealthy)
        version: API version
        cache_entries: Number of cache entries
    """
    status: str
    version: str
    cache_entries: int


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """Check dashboard service health.
    
    Returns:
        HealthResponse with service status
    """
    from .cache_manager import get_cache_manager
    
    cache = get_cache_manager()
    return HealthResponse(
        status="healthy",
        version="1.0.0",
        cache_entries=len(cache._entries),
    )


@router.post("/generate", response_model=DashboardResponse)
async def generate_dashboard(request: DashboardRequest) -> DashboardResponse:
    """Generate dashboard for a repository.
    
    Args:
        request: Dashboard generation request
        
    Returns:
        DashboardResponse with generation result
    """
    from .orchestrator import DashboardOrchestrator
    from .cache_manager import get_cache_manager
    
    try:
        repo_path = Path(request.repo_path)
        
        if not repo_path.exists():
            return DashboardResponse(
                success=False,
                error=f"Repository path does not exist: {repo_path}",
            )
        
        # Check cache unless force refresh
        cache = get_cache_manager()
        if not request.force_refresh:
            entry = cache.get_entry(repo_path)
            if entry:
                return DashboardResponse(
                    success=True,
                    output_path=entry.output_path,
                    url=f"file://{entry.output_path}/index.html",
                    tabs=["overview", "orchestrators", "governance"],
                )
        
        # Generate dashboard
        orchestrator = DashboardOrchestrator(repo_path=repo_path)
        output_path = request.output_path or cache.get_output_path(
            repo_path,
            is_cortex=request.is_cortex,
        )
        
        result = orchestrator.generate(Path(output_path))
        
        if result:
            # Create cache entry
            cache.create_entry(
                repo_path=repo_path,
                output_path=Path(output_path),
                is_cortex=request.is_cortex,
            )
            
            return DashboardResponse(
                success=True,
                output_path=str(output_path),
                url=f"file://{output_path}/index.html",
                tabs=["overview", "orchestrators", "governance"],
            )
        else:
            return DashboardResponse(
                success=False,
                error="Dashboard generation failed",
            )
            
    except Exception as e:
        return DashboardResponse(
            success=False,
            error=str(e),
        )


@router.get("/cached")
async def list_cached() -> Dict[str, Any]:
    """List all cached dashboard entries.
    
    Returns:
        Dictionary with cached entries
    """
    from .cache_manager import get_cache_manager
    
    cache = get_cache_manager()
    entries = []
    
    for key, entry in cache._entries.items():
        entries.append({
            "key": key,
            "repo_path": entry.repo_path,
            "output_path": entry.output_path,
            "is_cortex": entry.is_cortex,
            "is_expired": entry.is_expired(),
            "created_at": entry.created_at.isoformat(),
            "expires_at": entry.expires_at.isoformat(),
        })
    
    return {"entries": entries, "count": len(entries)}


@router.post("/cleanup")
async def cleanup_cache(older_than_days: int = 30) -> Dict[str, Any]:
    """Cleanup old cache entries.
    
    Args:
        older_than_days: Remove entries older than this many days
        
    Returns:
        Dictionary with cleanup result
    """
    from .cache_manager import get_cache_manager
    
    cache = get_cache_manager()
    removed = cache.cleanup_older_than(older_than_days)
    
    return {
        "removed": removed,
        "remaining": len(cache._entries),
    }
