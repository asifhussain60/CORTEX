"""CORTEX LENS Dashboard Backend.

This module provides the backend infrastructure for the LENS Dashboard,
including API routes, orchestration, and cache management.

Components:
    - routes: FastAPI endpoints for dashboard data
    - orchestrator: Coordinates visualization generation
    - cache_manager: Manages dashboard output locations

Integration:
    All components are designed to work behind MCP (Model Context Protocol)
    and integrate with the existing CORTEX orchestrator infrastructure.
"""

# Use relative imports since cortex-lens has a hyphen (not valid Python module name)
# Import with graceful fallback for missing dependencies
try:
    from .cache_manager import CacheManager, CacheEntry, get_cache_manager
except ImportError as e:
    CacheManager = None  # type: ignore
    CacheEntry = None  # type: ignore
    get_cache_manager = None  # type: ignore

try:
    from .routes import router, DashboardRequest, DashboardResponse
except ImportError as e:
    router = None  # type: ignore
    DashboardRequest = None  # type: ignore
    DashboardResponse = None  # type: ignore

try:
    from .orchestrator import DashboardOrchestrator
except ImportError as e:
    DashboardOrchestrator = None  # type: ignore

__all__ = [
    "router",
    "DashboardRequest",
    "DashboardResponse",
    "DashboardOrchestrator",
    "CacheManager",
    "CacheEntry",
    "get_cache_manager",
]
