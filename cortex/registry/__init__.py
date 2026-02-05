"""
CORTEX Registry Module

Handles cortex-registry/ management including dashboard generation.
"""

from cortex.registry.cortex_master_dashboard_generator import (
    CortexMasterDashboardGenerator,
    regenerate_dashboard
)

__all__ = [
    "CortexMasterDashboardGenerator",
    "regenerate_dashboard"
]
