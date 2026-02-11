"""
CORTEX Registry Module

Handles cortex-registry/ management including dashboard generation,
tenant isolation, multi-tenant support, and workspace management.
"""

from cortex.registry.cortex_master_dashboard_generator import (
    CortexMasterDashboardGenerator,
    regenerate_dashboard,
)
from cortex.registry.health_monitor import (
    HealthCheckResult,
    RegistryHealthMonitor,
)
from cortex.registry.tenant_aware_git_backed_registry import (
    TenantAwareGitBackedRegistry,
)
from cortex.registry.tenant_context import (
    TenantContext,
    require_admin,
    require_permission,
    validate_tenant_context,
)
from cortex.registry.workspace_manager import (
    Workspace,
    WorkspaceManager,
)

__all__ = [
    "CortexMasterDashboardGenerator",
    "regenerate_dashboard",
    "TenantContext",
    "validate_tenant_context",
    "require_permission",
    "require_admin",
    "TenantAwareGitBackedRegistry",
    "WorkspaceManager",
    "Workspace",
    "RegistryHealthMonitor",
    "HealthCheckResult",
]
