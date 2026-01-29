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

from cortex_lens.backend.routes import router, DashboardRequest, DashboardResponse
from cortex_lens.backend.orchestrator import DashboardOrchestrator
from cortex_lens.backend.cache_manager import CacheManager

__all__ = [
    "router",
    "DashboardRequest",
    "DashboardResponse",
    "DashboardOrchestrator",
    "CacheManager",
]
