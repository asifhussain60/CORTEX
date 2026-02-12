"""
RegistryAccessControl - Role-Based Access Control for Registry Operations

Authority: Phase 76 S2 Task 4 - Registry Isolation & Multi-Tenant Foundation
AC-ID: AC-PHASE76-S2-T4-001

Provides advanced RBAC (role-based access control) for registry operations
with fine-grained permission management, role definitions, and audit logging.

Key Features:
- Role-based access control (viewer, editor, admin)
- Fine-grained permissions (read, write, delete, seal, unseal, etc.)
- Resource-level access control
- Audit logging of permission checks
- Permission inheritance and composition
"""

import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from cortex.registry.tenant_context import TenantContext

logger = logging.getLogger(__name__)


class Permission(Enum):
    """Fine-grained permissions for registry operations."""

    # Read operations
    READ = "read"
    LIST = "list"

    # Write operations
    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"

    # Artifact operations
    SEAL_ARTIFACT = "seal_artifact"
    UNSEAL_ARTIFACT = "unseal_artifact"
    VERIFY_ARTIFACT = "verify_artifact"

    # Workspace operations
    CREATE_WORKSPACE = "create_workspace"
    DELETE_WORKSPACE = "delete_workspace"
    SWITCH_WORKSPACE = "switch_workspace"

    # Administrative operations
    MANAGE_PERMISSIONS = "manage_permissions"
    MANAGE_ROLES = "manage_roles"
    VIEW_AUDIT_LOG = "view_audit_log"
    MANAGE_TENANTS = "manage_tenants"

    # System operations
    ADMIN = "admin"


class Role(Enum):
    """Predefined roles for registry operations."""

    VIEWER = "viewer"        # Read-only access
    EDITOR = "editor"        # Read + write access
    MAINTAINER = "maintainer"  # Read + write + manage
    ADMIN = "admin"           # Full access


@dataclass
class PermissionPolicy:
    """Definition of permissions for a role."""

    role: Role
    permissions: Set[Permission] = field(default_factory=set)
    description: str = ""
    resource_restrictions: Optional[Dict[str, List[str]]] = None

    def has_permission(self, permission: Permission) -> bool:
        """Check if role has permission."""
        return permission in self.permissions

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "role": self.role.value,
            "permissions": [p.value for p in self.permissions],
            "description": self.description,
            "resource_restrictions": self.resource_restrictions
        }


class AccessDeniedException(Exception):
    """Raised when access is denied."""
    pass


class RoleBasedAccessControl:
    """
    Role-based access control for registry operations.

    Manages:
    - Role definitions and permissions
    - User role assignments
    - Resource-level access checks
    - Audit logging

    Example:
        >>> from cortex.registry.registry_access_control import RoleBasedAccessControl
        >>> rbac = RoleBasedAccessControl()
        >>> ctx = TenantContext("ws1", "alice@acme.com", ["editor", "maintainer"])
        >>>
        >>> # Check permission
        >>> can_create = rbac.has_permission(ctx, Permission.CREATE)
        >>>
        >>> # Enforce permission
        >>> rbac.require_permission(ctx, Permission.DELETE)
    """

    # Default role permissions
    DEFAULT_PERMISSIONS = {
        Role.VIEWER: {
            Permission.READ,
            Permission.LIST,
            Permission.VERIFY_ARTIFACT,
        },
        Role.EDITOR: {
            Permission.READ,
            Permission.LIST,
            Permission.CREATE,
            Permission.UPDATE,
            Permission.SEAL_ARTIFACT,
            Permission.VERIFY_ARTIFACT,
            Permission.CREATE_WORKSPACE,
            Permission.SWITCH_WORKSPACE,
        },
        Role.MAINTAINER: {
            Permission.READ,
            Permission.LIST,
            Permission.CREATE,
            Permission.UPDATE,
            Permission.DELETE,
            Permission.SEAL_ARTIFACT,
            Permission.UNSEAL_ARTIFACT,
            Permission.VERIFY_ARTIFACT,
            Permission.CREATE_WORKSPACE,
            Permission.DELETE_WORKSPACE,
            Permission.SWITCH_WORKSPACE,
            Permission.MANAGE_PERMISSIONS,
            Permission.VIEW_AUDIT_LOG,
        },
        Role.ADMIN: set(Permission),  # All permissions
    }

    def __init__(self) -> None:
        """Initialize RBAC system."""
        self._role_policies: Dict[Role, PermissionPolicy] = {}
        self._user_roles: Dict[str, Set[Role]] = {}
        self._audit_log: List[Dict[str, Any]] = []
        self._resource_policies: Dict[str, Set[Permission]] = {}

        # Initialize default policies
        self._init_default_policies()

        logger.info("Initialized RoleBasedAccessControl")

    def _init_default_policies(self) -> None:
        """Initialize default role policies."""
        role_descriptions = {
            Role.VIEWER: "Read-only access to registry",
            Role.EDITOR: "Read and write access to registry",
            Role.MAINTAINER: "Management access including deletion and permission management",
            Role.ADMIN: "Full administrative access",
        }

        for role, permissions in self.DEFAULT_PERMISSIONS.items():
            policy = PermissionPolicy(
                role=role,
                permissions=permissions.copy(),
                description=role_descriptions.get(role, "")
            )
            self._role_policies[role] = policy

    def assign_role(
        self,
        user_id: str,
        role: Role,
        tenant_ctx: Optional[TenantContext] = None
    ) -> None:
        """
        Assign role to user.

        Args:
            user_id: User identifier
            role: Role to assign
            tenant_ctx: Optional TenantContext for auditing
        """
        if user_id not in self._user_roles:
            self._user_roles[user_id] = set()

        self._user_roles[user_id].add(role)

        self._log_audit(
            "role_assigned",
            user_id,
            {"role": role.value},
            tenant_ctx
        )

        logger.info(f"Assigned role {role.value} to user {user_id}")

    def revoke_role(
        self,
        user_id: str,
        role: Role,
        tenant_ctx: Optional[TenantContext] = None
    ) -> None:
        """
        Revoke role from user.

        Args:
            user_id: User identifier
            role: Role to revoke
            tenant_ctx: Optional TenantContext for auditing
        """
        if user_id in self._user_roles:
            self._user_roles[user_id].discard(role)

        self._log_audit(
            "role_revoked",
            user_id,
            {"role": role.value},
            tenant_ctx
        )

        logger.info(f"Revoked role {role.value} from user {user_id}")

    def get_user_roles(self, user_id: str) -> Set[Role]:
        """
        Get roles assigned to user.

        Args:
            user_id: User identifier

        Returns:
            Set of roles
        """
        return self._user_roles.get(user_id, set())

    def has_permission(
        self,
        tenant_ctx: TenantContext,
        permission: Permission,
        resource: Optional[str] = None
    ) -> bool:
        """
        Check if context has permission.

        Args:
            tenant_ctx: TenantContext to check
            permission: Permission to check
            resource: Optional resource to check (for resource-level ACL)

        Returns:
            True if permission granted, False otherwise
        """
        # Get user roles
        user_roles = self.get_user_roles(tenant_ctx.user_id)

        if not user_roles:
            return False

        # Check if any role has permission
        for role in user_roles:
            policy = self._role_policies.get(role)
            if policy and policy.has_permission(permission):
                # Check resource restrictions if applicable
                if resource and policy.resource_restrictions:
                    restrictions = policy.resource_restrictions.get(permission.value)
                    if restrictions and resource not in restrictions:
                        continue

                return True

        return False

    def require_permission(
        self,
        tenant_ctx: TenantContext,
        permission: Permission,
        resource: Optional[str] = None
    ) -> None:
        """
        Require specific permission or raise exception.

        Args:
            tenant_ctx: TenantContext to check
            permission: Permission to require
            resource: Optional resource

        Raises:
            AccessDeniedException: If permission not granted
        """
        if not self.has_permission(tenant_ctx, permission, resource):
            self._log_audit(
                "permission_denied",
                tenant_ctx.user_id,
                {"permission": permission.value, "resource": resource},
                tenant_ctx
            )

            raise AccessDeniedException(
                f"User {tenant_ctx.user_id} lacks permission: {permission.value}"
            )

        self._log_audit(
            "permission_granted",
            tenant_ctx.user_id,
            {"permission": permission.value, "resource": resource},
            tenant_ctx
        )

    def get_permission_policy(self, role: Role) -> Optional[PermissionPolicy]:
        """
        Get permission policy for role.

        Args:
            role: Role to get policy for

        Returns:
            PermissionPolicy or None
        """
        return self._role_policies.get(role)

    def list_permissions(self, role: Role) -> List[str]:
        """
        List permissions for role.

        Args:
            role: Role to list permissions for

        Returns:
            List of permission names
        """
        policy = self._role_policies.get(role)
        if policy:
            return [p.value for p in sorted(policy.permissions, key=lambda x: x.value)]
        return []

    def _log_audit(
        self,
        event: str,
        user_id: str,
        details: Dict[str, Any],
        tenant_ctx: Optional[TenantContext] = None
    ) -> None:
        """
        Log audit event.

        Args:
            event: Event name
            user_id: User ID
            details: Event details
            tenant_ctx: Optional TenantContext
        """
        audit_entry = {
            "event": event,
            "user_id": user_id,
            "tenant_id": tenant_ctx.tenant_id if tenant_ctx else "local",
            "details": details,
            "timestamp": datetime.utcnow().isoformat()
        }
        self._audit_log.append(audit_entry)

    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        event_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get audit log entries.

        Args:
            user_id: Optional filter by user
            event_type: Optional filter by event type

        Returns:
            List of audit log entries
        """
        entries = self._audit_log

        if user_id:
            entries = [e for e in entries if e["user_id"] == user_id]

        if event_type:
            entries = [e for e in entries if e["event"] == event_type]

        return entries
