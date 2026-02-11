"""
WorkspaceManager - Multi-Workspace Support for CORTEX Registry

Authority: Phase 76 S2 Task 3 - Registry Isolation & Multi-Tenant Foundation
AC-ID: AC-PHASE76-S2-003

Enables multiple workspaces per tenant with workspace isolation,
workspace switching, and workspace-scoped phase management.

Key Features:
- Workspace creation and management per tenant
- Workspace switching and context management
- Workspace-scoped phase operations
- Workspace health checks and statistics
- Workspace path isolation
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

from cortex.registry.tenant_context import TenantContext, validate_tenant_context

logger = logging.getLogger(__name__)


class Workspace:
    """
    Represents a single workspace with metadata.

    Attributes:
        workspace_id: Unique workspace identifier
        workspace_name: Human-readable workspace name
        tenant_id: Tenant that owns this workspace
        path: Workspace directory path
        created_at: Creation timestamp
        metadata: Optional metadata
        is_active: Whether workspace is active
    """

    def __init__(
        self,
        workspace_id: str,
        workspace_name: str,
        tenant_id: str,
        path: Optional[Path] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """Initialize Workspace."""
        if not workspace_id or not workspace_id.strip():
            raise ValueError("workspace_id cannot be empty")
        if not workspace_name or not workspace_name.strip():
            raise ValueError("workspace_name cannot be empty")
        if not tenant_id or not tenant_id.strip():
            raise ValueError("tenant_id cannot be empty")

        self.workspace_id = workspace_id
        self.workspace_name = workspace_name
        self.tenant_id = tenant_id
        self.path = path or Path(f"registry/{tenant_id}/workspaces/{workspace_id}")
        self.created_at = datetime.utcnow()
        self.metadata = metadata or {}
        self.is_active = True

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "workspace_id": self.workspace_id,
            "workspace_name": self.workspace_name,
            "tenant_id": self.tenant_id,
            "path": str(self.path),
            "created_at": self.created_at.isoformat(),
            "is_active": self.is_active,
            "metadata": self.metadata.copy()
        }

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"Workspace(id={self.workspace_id!r}, "
            f"name={self.workspace_name!r}, "
            f"tenant_id={self.tenant_id!r}, "
            f"active={self.is_active})"
        )


class WorkspaceManager:
    """
    Manages multiple workspaces per tenant.

    Supports:
    - Creating and deleting workspaces
    - Switching between workspaces
    - Workspace-scoped phase management
    - Workspace health checks

    Example:
        >>> ctx = TenantContext("acme-dev", "alice@acme.com", ["admin"])
        >>> manager = WorkspaceManager()
        >>>
        >>> # Create workspaces
        >>> manager.create_workspace(ctx, "ws-prod", "Production Workspace")
        >>> manager.create_workspace(ctx, "ws-staging", "Staging Workspace")
        >>>
        >>> # List workspaces
        >>> workspaces = manager.list_workspaces(ctx)
        >>>
        >>> # Switch to workspace
        >>> manager.switch_workspace(ctx, "ws-prod")
        >>>
        >>> # Get current workspace
        >>> current = manager.get_current_workspace(ctx)
    """

    def __init__(self, registry_root: Optional[Path] = None) -> None:
        """
        Initialize WorkspaceManager.

        Args:
            registry_root: Root path for registry (default: cortex-registry)
        """
        if registry_root is None:
            registry_root = Path("cortex-registry/_cortex-master")

        self.registry_root = registry_root
        self._workspaces: Dict[str, Dict[str, Workspace]] = {}  # tenant_id → workspace_id → Workspace
        self._current_workspace: Dict[str, str] = {}  # tenant_id → current_workspace_id

        logger.info(f"Initialized WorkspaceManager at {self.registry_root}")

    def create_workspace(
        self,
        tenant_ctx: TenantContext,
        workspace_id: str,
        workspace_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Workspace:
        """
        Create a new workspace for tenant.

        Args:
            tenant_ctx: TenantContext for isolation
            workspace_id: Unique workspace identifier
            workspace_name: Human-readable name
            metadata: Optional metadata

        Returns:
            Created Workspace

        Raises:
            ValueError: If workspace_id already exists or invalid
            PermissionError: If tenant lacks required permission
        """
        validate_tenant_context(tenant_ctx)

        if not tenant_ctx.has_admin_permission():
            raise PermissionError(
                f"Tenant {tenant_ctx.tenant_id} requires admin permission to create workspace"
            )

        tenant_id = tenant_ctx.tenant_id

        # Initialize tenant's workspace dict if needed
        if tenant_id not in self._workspaces:
            self._workspaces[tenant_id] = {}

        if workspace_id in self._workspaces[tenant_id]:
            raise ValueError(f"Workspace already exists: {workspace_id}")

        # Create workspace
        workspace = Workspace(
            workspace_id=workspace_id,
            workspace_name=workspace_name,
            tenant_id=tenant_id,
            metadata=metadata
        )

        self._workspaces[tenant_id][workspace_id] = workspace

        # Set as current if first workspace
        if tenant_id not in self._current_workspace:
            self._current_workspace[tenant_id] = workspace_id

        logger.info(f"Created workspace {workspace_id} for tenant {tenant_id}")
        return workspace

    def delete_workspace(
        self,
        tenant_ctx: TenantContext,
        workspace_id: str
    ) -> bool:
        """
        Delete a workspace for tenant.

        Args:
            tenant_ctx: TenantContext for isolation
            workspace_id: Workspace to delete

        Returns:
            True if deleted, False if not found

        Raises:
            PermissionError: If tenant lacks admin permission
            ValueError: If deleting only/current workspace
        """
        validate_tenant_context(tenant_ctx)

        if not tenant_ctx.has_admin_permission():
            raise PermissionError(
                f"Tenant {tenant_ctx.tenant_id} requires admin permission to delete workspace"
            )

        tenant_id = tenant_ctx.tenant_id

        if tenant_id not in self._workspaces:
            return False

        if workspace_id not in self._workspaces[tenant_id]:
            return False

        # Prevent deletion of only workspace
        if len(self._workspaces[tenant_id]) == 1:
            raise ValueError("Cannot delete the only workspace for tenant")

        # If deleting current, switch to another
        if self._current_workspace.get(tenant_id) == workspace_id:
            other_ws = next(
                (ws_id for ws_id in self._workspaces[tenant_id].keys() if ws_id != workspace_id),
                None
            )
            if other_ws:
                self._current_workspace[tenant_id] = other_ws

        del self._workspaces[tenant_id][workspace_id]
        logger.info(f"Deleted workspace {workspace_id} for tenant {tenant_id}")
        return True

    def switch_workspace(
        self,
        tenant_ctx: TenantContext,
        workspace_id: str
    ) -> Workspace:
        """
        Switch to a workspace.

        Args:
            tenant_ctx: TenantContext for isolation
            workspace_id: Workspace to switch to

        Returns:
            Switched Workspace

        Raises:
            ValueError: If workspace not found
        """
        validate_tenant_context(tenant_ctx)

        tenant_id = tenant_ctx.tenant_id

        if tenant_id not in self._workspaces or workspace_id not in self._workspaces[tenant_id]:
            raise ValueError(f"Workspace not found: {workspace_id}")

        self._current_workspace[tenant_id] = workspace_id
        workspace = self._workspaces[tenant_id][workspace_id]

        logger.info(f"Switched to workspace {workspace_id} for tenant {tenant_id}")
        return workspace

    def get_current_workspace(
        self,
        tenant_ctx: TenantContext
    ) -> Optional[Workspace]:
        """
        Get current workspace for tenant.

        Args:
            tenant_ctx: TenantContext for isolation

        Returns:
            Current Workspace or None if none active
        """
        validate_tenant_context(tenant_ctx)

        tenant_id = tenant_ctx.tenant_id
        current_ws_id = self._current_workspace.get(tenant_id)

        if not current_ws_id or tenant_id not in self._workspaces:
            return None

        return self._workspaces[tenant_id].get(current_ws_id)

    def list_workspaces(
        self,
        tenant_ctx: TenantContext
    ) -> List[Workspace]:
        """
        List all workspaces for tenant.

        Args:
            tenant_ctx: TenantContext for isolation

        Returns:
            List of Workspaces for tenant
        """
        validate_tenant_context(tenant_ctx)

        tenant_id = tenant_ctx.tenant_id

        if tenant_id not in self._workspaces:
            return []

        return list(self._workspaces[tenant_id].values())

    def get_workspace(
        self,
        tenant_ctx: TenantContext,
        workspace_id: str
    ) -> Optional[Workspace]:
        """
        Get specific workspace for tenant.

        Args:
            tenant_ctx: TenantContext for isolation
            workspace_id: Workspace to retrieve

        Returns:
            Workspace or None if not found
        """
        validate_tenant_context(tenant_ctx)

        tenant_id = tenant_ctx.tenant_id

        if tenant_id not in self._workspaces:
            return None

        return self._workspaces[tenant_id].get(workspace_id)

    def workspace_exists(
        self,
        tenant_ctx: TenantContext,
        workspace_id: str
    ) -> bool:
        """
        Check if workspace exists for tenant.

        Args:
            tenant_ctx: TenantContext for isolation
            workspace_id: Workspace to check

        Returns:
            True if workspace exists for tenant
        """
        validate_tenant_context(tenant_ctx)

        tenant_id = tenant_ctx.tenant_id
        return (
            tenant_id in self._workspaces and
            workspace_id in self._workspaces[tenant_id]
        )

    def get_workspace_count(
        self,
        tenant_ctx: TenantContext
    ) -> int:
        """
        Get workspace count for tenant.

        Args:
            tenant_ctx: TenantContext for isolation

        Returns:
            Number of workspaces for tenant
        """
        validate_tenant_context(tenant_ctx)

        tenant_id = tenant_ctx.tenant_id
        return len(self._workspaces.get(tenant_id, {}))

    def get_workspace_ids(
        self,
        tenant_ctx: TenantContext
    ) -> List[str]:
        """
        Get all workspace IDs for tenant.

        Args:
            tenant_ctx: TenantContext for isolation

        Returns:
            List of workspace IDs
        """
        validate_tenant_context(tenant_ctx)

        tenant_id = tenant_ctx.tenant_id

        if tenant_id not in self._workspaces:
            return []

        return list(self._workspaces[tenant_id].keys())

    def get_statistics(
        self,
        tenant_ctx: TenantContext
    ) -> Dict[str, Any]:
        """
        Get workspace statistics for tenant.

        Args:
            tenant_ctx: TenantContext for isolation

        Returns:
            Dictionary with statistics
        """
        validate_tenant_context(tenant_ctx)

        tenant_id = tenant_ctx.tenant_id
        workspaces = self.list_workspaces(tenant_ctx)
        current_ws = self.get_current_workspace(tenant_ctx)

        return {
            "tenant_id": tenant_id,
            "workspace_count": len(workspaces),
            "workspace_ids": [w.workspace_id for w in workspaces],
            "current_workspace_id": current_ws.workspace_id if current_ws else None,
            "workspaces": [w.to_dict() for w in workspaces],
            "created_at": datetime.utcnow().isoformat()
        }

    def reset(self) -> None:
        """Reset workspace manager (for testing)."""
        self._workspaces.clear()
        self._current_workspace.clear()
        logger.debug("WorkspaceManager reset")


# AC_START: AC-PHASE76-S2-003
# File: cortex/registry/workspace_manager.py
# Component: WorkspaceManager + Workspace classes
# Created: 2026-02-10
# Status: IMPLEMENTATION
