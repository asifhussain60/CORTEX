"""
ENH-063 P1-011: RBAC Authorization Layer
AC-ENH063-P1-011-001

Role-Based Access Control for MCP Server operations.
Integrates with authentication.py to provide authorization layer.

Components:
1. Role definitions (admin, developer, viewer)
2. Permission model (resource:action format)
3. Authorization manager (check access)
4. Policy enforcement (decorator-based)

TDD: Tests in tests/mcp/test_authorization.py
"""

import functools
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Callable, Dict, List, Optional, Set

# ============================================================================
# TYPE DEFINITIONS
# ============================================================================


class Role(Enum):
    """User roles with hierarchical permissions"""
    ADMIN = "admin"  # Full access
    DEVELOPER = "developer"  # Read/write, no destructive ops
    VIEWER = "viewer"  # Read-only access


class Resource(Enum):
    """Protected resources in MCP server"""
    ORCHESTRATOR = "orchestrator"
    REPOSITORY = "repository"
    CONFIGURATION = "configuration"
    SECRETS = "secrets"
    DEPLOYMENT = "deployment"
    HEALTH = "health"
    METRICS = "metrics"


class Action(Enum):
    """Actions that can be performed on resources"""
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    EXECUTE = "execute"


@dataclass(frozen=True)
class Permission:
    """Represents a resource:action permission"""
    resource: Resource
    action: Action

    def __str__(self) -> str:
        return f"{self.resource.value}:{self.action.value}"

    @classmethod
    def from_string(cls, permission_str: str) -> "Permission":
        """Parse permission from 'resource:action' string"""
        resource_str, action_str = permission_str.split(":")
        return cls(
            resource=Resource(resource_str),
            action=Action(action_str)
        )


@dataclass
class RolePolicy:
    """Defines permissions for a role"""
    role: Role
    permissions: Set[Permission] = field(default_factory=set)
    description: str = ""

    def has_permission(self, permission: Permission) -> bool:
        """Check if role has specific permission"""
        return permission in self.permissions

    def add_permission(self, permission: Permission) -> None:
        """Add permission to role"""
        self.permissions.add(permission)

    def remove_permission(self, permission: Permission) -> None:
        """Remove permission from role"""
        self.permissions.discard(permission)


@dataclass
class AuthorizationContext:
    """Context for authorization decision"""
    user_id: str
    roles: List[Role]
    resource: Resource
    action: Action
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, str] = field(default_factory=dict)


@dataclass
class AuthorizationResult:
    """Result of authorization check"""
    allowed: bool
    reason: str
    context: Optional[AuthorizationContext] = None


# ============================================================================
# DEFAULT ROLE POLICIES
# ============================================================================

# Admin role: Full access
ADMIN_POLICY = RolePolicy(
    role=Role.ADMIN,
    permissions={
        # All resources, all actions
        Permission(Resource.ORCHESTRATOR, Action.READ),
        Permission(Resource.ORCHESTRATOR, Action.WRITE),
        Permission(Resource.ORCHESTRATOR, Action.EXECUTE),
        Permission(Resource.ORCHESTRATOR, Action.DELETE),
        Permission(Resource.REPOSITORY, Action.READ),
        Permission(Resource.REPOSITORY, Action.WRITE),
        Permission(Resource.REPOSITORY, Action.DELETE),
        Permission(Resource.CONFIGURATION, Action.READ),
        Permission(Resource.CONFIGURATION, Action.WRITE),
        Permission(Resource.CONFIGURATION, Action.DELETE),
        Permission(Resource.SECRETS, Action.READ),
        Permission(Resource.SECRETS, Action.WRITE),
        Permission(Resource.SECRETS, Action.DELETE),
        Permission(Resource.DEPLOYMENT, Action.READ),
        Permission(Resource.DEPLOYMENT, Action.WRITE),
        Permission(Resource.DEPLOYMENT, Action.EXECUTE),
        Permission(Resource.HEALTH, Action.READ),
        Permission(Resource.METRICS, Action.READ),
    },
    description="Full administrative access"
)

# Developer role: Read/write, no destructive operations
DEVELOPER_POLICY = RolePolicy(
    role=Role.DEVELOPER,
    permissions={
        Permission(Resource.ORCHESTRATOR, Action.READ),
        Permission(Resource.ORCHESTRATOR, Action.WRITE),
        Permission(Resource.ORCHESTRATOR, Action.EXECUTE),
        Permission(Resource.REPOSITORY, Action.READ),
        Permission(Resource.REPOSITORY, Action.WRITE),
        Permission(Resource.CONFIGURATION, Action.READ),
        Permission(Resource.HEALTH, Action.READ),
        Permission(Resource.METRICS, Action.READ),
    },
    description="Development and execution access"
)

# Viewer role: Read-only access
VIEWER_POLICY = RolePolicy(
    role=Role.VIEWER,
    permissions={
        Permission(Resource.ORCHESTRATOR, Action.READ),
        Permission(Resource.REPOSITORY, Action.READ),
        Permission(Resource.CONFIGURATION, Action.READ),
        Permission(Resource.HEALTH, Action.READ),
        Permission(Resource.METRICS, Action.READ),
    },
    description="Read-only access"
)

DEFAULT_POLICIES: Dict[Role, RolePolicy] = {
    Role.ADMIN: ADMIN_POLICY,
    Role.DEVELOPER: DEVELOPER_POLICY,
    Role.VIEWER: VIEWER_POLICY,
}


# ============================================================================
# AUTHORIZATION MANAGER
# ============================================================================


class AuthorizationManager:
    """Manages RBAC authorization for MCP server"""

    def __init__(self, policies: Optional[Dict[Role, RolePolicy]] = None):
        """
        Initialize authorization manager.

        Args:
            policies: Custom role policies (default: use DEFAULT_POLICIES)
        """
        self.policies = policies or DEFAULT_POLICIES.copy()
        self.logger = logging.getLogger(__name__)
        self._audit_log: List[Dict] = []

    def check_authorization(
        self,
        user_id: str,
        roles: List[Role],
        resource: Resource,
        action: Action,
        metadata: Optional[Dict[str, str]] = None
    ) -> AuthorizationResult:
        """
        Check if user is authorized for resource:action.

        Args:
            user_id: User identifier
            roles: User's assigned roles
            resource: Protected resource
            action: Action to perform
            metadata: Additional context

        Returns:
            AuthorizationResult with allowed status and reason
        """
        context = AuthorizationContext(
            user_id=user_id,
            roles=roles,
            resource=resource,
            action=action,
            metadata=metadata or {}
        )

        # Check if any role has required permission
        required_permission = Permission(resource, action)

        for role in roles:
            if role not in self.policies:
                continue

            policy = self.policies[role]
            if policy.has_permission(required_permission):
                result = AuthorizationResult(
                    allowed=True,
                    reason=f"Authorized via role: {role.value}",
                    context=context
                )
                self._log_authorization(result)
                return result

        # No role has permission
        result = AuthorizationResult(
            allowed=False,
            reason=f"No role has permission {required_permission}",
            context=context
        )
        self._log_authorization(result)
        return result

    def add_policy(self, policy: RolePolicy) -> None:
        """Add or update a role policy"""
        self.policies[policy.role] = policy
        self.logger.info(f"Added policy for role: {policy.role.value}")

    def remove_policy(self, role: Role) -> None:
        """Remove a role policy"""
        self.policies.pop(role, None)
        self.logger.info(f"Removed policy for role: {role.value}")

    def get_policy(self, role: Role) -> Optional[RolePolicy]:
        """Get policy for a role"""
        return self.policies.get(role)

    def get_permissions(self, role: Role) -> Set[Permission]:
        """Get all permissions for a role"""
        policy = self.policies.get(role)
        return policy.permissions if policy else set()

    def _log_authorization(self, result: AuthorizationResult) -> None:
        """Log authorization decision for audit"""
        if not result.context:
            return

        log_entry = {
            "timestamp": result.context.timestamp.isoformat(),
            "user_id": result.context.user_id,
            "roles": [r.value for r in result.context.roles],
            "resource": result.context.resource.value,
            "action": result.context.action.value,
            "allowed": result.allowed,
            "reason": result.reason,
            "metadata": result.context.metadata
        }

        self._audit_log.append(log_entry)

        # Log to standard logger
        if result.allowed:
            self.logger.info(
                f"AUTHORIZED: {result.context.user_id} "
                f"{result.context.resource.value}:{result.context.action.value}"
            )
        else:
            self.logger.warning(
                f"DENIED: {result.context.user_id} "
                f"{result.context.resource.value}:{result.context.action.value} "
                f"- {result.reason}"
            )

    def get_audit_log(self, limit: int = 100) -> List[Dict]:
        """Get recent authorization audit log entries"""
        return self._audit_log[-limit:]

    def clear_audit_log(self) -> None:
        """Clear audit log (for testing)"""
        self._audit_log.clear()


# ============================================================================
# GLOBAL INSTANCE
# ============================================================================

_authorization_manager: Optional[AuthorizationManager] = None


def get_authorization_manager() -> AuthorizationManager:
    """Get global authorization manager instance"""
    global _authorization_manager
    if _authorization_manager is None:
        _authorization_manager = AuthorizationManager()
    return _authorization_manager


def reset_authorization_manager() -> None:
    """Reset global instance (for testing)"""
    global _authorization_manager
    _authorization_manager = None


# ============================================================================
# DECORATOR-BASED ENFORCEMENT
# ============================================================================


def require_permission(resource: Resource, action: Action):
    """
    Decorator to enforce authorization on MCP tool functions.

    Usage:
        @require_permission(Resource.ORCHESTRATOR, Action.EXECUTE)
        def execute_orchestrator(user_id: str, roles: List[Role], ...):
            ...

    Args:
        resource: Protected resource
        action: Required action

    Raises:
        PermissionError: If user is not authorized
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Extract user_id and roles from kwargs
            user_id = kwargs.get("user_id")
            roles = kwargs.get("roles", [])

            if not user_id:
                raise ValueError("user_id required for authorization check")

            if not isinstance(roles, list):
                roles = [roles]

            # Check authorization
            auth_manager = get_authorization_manager()
            result = auth_manager.check_authorization(
                user_id=user_id,
                roles=roles,
                resource=resource,
                action=action
            )

            if not result.allowed:
                raise PermissionError(
                    f"Access denied: {result.reason} "
                    f"(resource={resource.value}, action={action.value})"
                )

            # Execute function if authorized
            return func(*args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# INTEGRATION WITH AUTHENTICATION
# ============================================================================


def extract_roles_from_token(token_payload: Dict) -> List[Role]:
    """
    Extract roles from JWT token payload.

    Args:
        token_payload: Decoded JWT payload from authentication.py

    Returns:
        List of Role enums

    Example token payload:
        {
            "user_id": "user123",
            "roles": ["developer"],
            "scopes": ["orchestrator:execute"],
            ...
        }
    """
    role_strings = token_payload.get("roles", [])
    roles = []

    for role_str in role_strings:
        try:
            roles.append(Role(role_str))
        except ValueError:
            logging.warning(f"Invalid role in token: {role_str}")

    return roles if roles else [Role.VIEWER]  # Default to viewer
