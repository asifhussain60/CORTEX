"""
TenantContext - Multi-Tenant Isolation Layer for CORTEX Registry

Authority: Phase 76 S2 Task 1 - Registry Isolation & Multi-Tenant Foundation
AC-ID: AC-PHASE76-S2-001

Provides tenant-aware context with workspace isolation, user identification,
and permission management.

Key Features:
- Unique tenant_id derivation from workspace_id + user_id
- Permission enforcement at request level
- Access control validation decorator
- Cross-tenant contamination prevention
"""

import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class TenantContext:
    """
    Multi-tenant context information for registry operations.

    Attributes:
        workspace_id: Unique workspace identifier (e.g., "acme-dev", "beta-staging")
        user_id: Unique user identifier (e.g., "user-12345")
        permissions: List of permission strings (e.g., ["read", "write", "admin"])
        tenant_id: Derived unique tenant identifier (workspace_id + user_id hash)
        created_at: Timestamp when context was created
        metadata: Optional metadata dict for extensibility

    Example:
        >>> ctx = TenantContext(
        ...     workspace_id="acme-dev",
        ...     user_id="alice@acme.com",
        ...     permissions=["read", "write"]
        ... )
        >>> print(ctx.tenant_id)  # Derived from workspace + user
        >>> ctx.has_permission("write")
        True
    """

    workspace_id: str
    user_id: str
    permissions: List[str] = field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None

    # Computed fields
    _tenant_id: Optional[str] = field(default=None, init=False, repr=False)
    _created_at: Optional[datetime] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """
        Post-initialization setup.

        - Compute tenant_id from workspace_id + user_id
        - Set creation timestamp
        - Validate required fields
        """
        # Validate required fields
        if not self.workspace_id or not self.workspace_id.strip():
            raise ValueError("workspace_id cannot be empty")

        if not self.user_id or not self.user_id.strip():
            raise ValueError("user_id cannot be empty")

        # Ensure permissions is a list
        if self.permissions is None:
            self.permissions = []

        # Compute tenant_id
        self._compute_tenant_id()

        # Set creation timestamp
        self._created_at = datetime.utcnow()

        # Initialize metadata if None
        if self.metadata is None:
            self.metadata = {}

    def _compute_tenant_id(self) -> None:
        """
        Compute unique tenant_id from workspace_id + user_id.

        Uses SHA256 hash of "workspace_id|user_id" to create deterministic,
        collision-resistant tenant identifier.
        """
        combined = f"{self.workspace_id}|{self.user_id}"
        hash_obj = hashlib.sha256(combined.encode('utf-8'))
        self._tenant_id = f"tenant-{hash_obj.hexdigest()[:16]}"

    @property
    def tenant_id(self) -> str:
        """
        Get unique tenant identifier.

        Returns:
            Deterministic tenant_id derived from workspace_id + user_id
        """
        if self._tenant_id is None:
            self._compute_tenant_id()
        return self._tenant_id or ""

    @property
    def created_at(self) -> datetime:
        """Get context creation timestamp."""
        if self._created_at is None:
            self._created_at = datetime.utcnow()
        return self._created_at

    def has_permission(self, permission: str) -> bool:
        """
        Check if context has a specific permission.

        Args:
            permission: Permission to check (e.g., "read", "write", "admin")

        Returns:
            True if permission is in permissions list, False otherwise

        Example:
            >>> ctx = TenantContext("ws1", "user1", ["read", "write"])
            >>> ctx.has_permission("write")
            True
            >>> ctx.has_permission("delete")
            False
        """
        return permission in self.permissions

    def grant_permission(self, permission: str) -> None:
        """
        Grant a permission to this context.

        Args:
            permission: Permission to grant (e.g., "read", "write", "admin")

        Raises:
            ValueError: If permission is empty
        """
        if not permission or not permission.strip():
            raise ValueError("permission cannot be empty")

        if permission not in self.permissions:
            self.permissions.append(permission)
            logger.debug(f"Granted permission '{permission}' to {self.tenant_id}")

    def revoke_permission(self, permission: str) -> bool:
        """
        Revoke a permission from this context.

        Args:
            permission: Permission to revoke

        Returns:
            True if permission was revoked, False if not found
        """
        if permission in self.permissions:
            self.permissions.remove(permission)
            logger.debug(f"Revoked permission '{permission}' from {self.tenant_id}")
            return True
        return False

    def has_admin_permission(self) -> bool:
        """Check if context has admin permission."""
        return self.has_permission("admin")

    def has_read_permission(self) -> bool:
        """Check if context has read permission."""
        return self.has_permission("read")

    def has_write_permission(self) -> bool:
        """Check if context has write permission."""
        return self.has_permission("write")

    def is_admin(self) -> bool:
        """Alias for has_admin_permission()."""
        return self.has_admin_permission()

    def get_access_level(self) -> str:
        """
        Get access level based on permissions.

        Returns:
            "admin" if has admin permission
            "write" if has write permission
            "read" if has read permission
            "none" if no permissions
        """
        if self.has_admin_permission():
            return "admin"
        if self.has_write_permission():
            return "write"
        if self.has_read_permission():
            return "read"
        return "none"

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert context to dictionary representation.

        Returns:
            Dictionary with all context information
        """
        return {
            "tenant_id": self.tenant_id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "permissions": self.permissions[:],  # Copy of list
            "access_level": self.get_access_level(),
            "created_at": self._created_at.isoformat() if self._created_at else None,
            "metadata": self.metadata.copy() if self.metadata else {},
        }

    def __repr__(self) -> str:
        """Return string representation."""
        return (
            f"TenantContext(workspace_id={self.workspace_id!r}, "
            f"user_id={self.user_id!r}, "
            f"tenant_id={self.tenant_id!r}, "
            f"permissions={self.permissions}, "
            f"access_level={self.get_access_level()!r})"
        )


def validate_tenant_context(ctx: Optional[TenantContext]) -> None:
    """
    Validate that a TenantContext is present and properly initialized.

    Args:
        ctx: TenantContext to validate

    Raises:
        ValueError: If context is None or invalid
    """
    if ctx is None:
        raise ValueError("TenantContext required")

    if not isinstance(ctx, TenantContext):
        raise TypeError(f"Expected TenantContext, got {type(ctx)}")

    if not ctx.workspace_id or not ctx.user_id:
        raise ValueError("TenantContext must have workspace_id and user_id")


def require_permission(permission: str):
    """
    Decorator to enforce permission requirements on functions.

    Args:
        permission: Required permission (e.g., "read", "write", "admin")

    Example:
        >>> @require_permission("write")
        ... def update_phase(ctx: TenantContext, phase_id: str):
        ...     # This will only run if ctx.has_permission("write")
        ...     pass
    """
    def decorator(func):
        def wrapper(ctx: TenantContext, *args, **kwargs):
            if ctx is None:
                raise ValueError("TenantContext required")

            if not ctx.has_permission(permission):
                raise PermissionError(
                    f"Permission '{permission}' required for {func.__name__}. "
                    f"Tenant {ctx.tenant_id} has: {ctx.permissions}"
                )

            return func(ctx, *args, **kwargs)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


def require_admin(func):
    """
    Decorator to enforce admin permission on functions.

    Example:
        >>> @require_admin
        ... def delete_phase(ctx: TenantContext, phase_id: str):
        ...     # This will only run if ctx.is_admin()
        ...     pass
    """
    return require_permission("admin")(func)


# AC_START: AC-PHASE76-S2-001
# File: cortex/registry/tenant_context.py
# Component: TenantContext class
# Created: 2026-02-10
# Status: IMPLEMENTATION
