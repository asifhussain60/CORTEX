"""
User Context Management for CORTEX Team Collaboration.

Provides thread-safe, async-safe user identity propagation using contextvars.
This allows user identity to flow through all operations without explicit passing.

Phase: 5.5 (Team Collaboration Layer)
Task: TEAM-001 (User Session Context)
Author: Asif Hussain
Date: 2026-01-27

CORE-030: Docker-first architecture - no database dependencies.
Uses contextvars for thread-safe context propagation.
"""

from __future__ import annotations

import uuid
from contextvars import ContextVar
from dataclasses import dataclass, field
from datetime import datetime, timezone
from functools import wraps
from typing import Any, Callable, Optional, TypeVar

# Type variable for decorated functions
F = TypeVar("F", bound=Callable[..., Any])


@dataclass
class UserContext:
    """
    User context for request attribution and access control.
    
    This dataclass holds all information about the current user making a request.
    It is propagated through the entire request lifecycle using contextvars.
    
    Attributes:
        user_id: Unique identifier for the user (e.g., "alice", "user_123")
        username: Human-readable display name
        roles: List of roles for access control (e.g., ["developer", "admin"])
        session_id: Unique identifier for this session/request
        created_at: When this context was created
        metadata: Additional user metadata (optional)
    
    Example:
        >>> user = UserContext(
        ...     user_id="alice",
        ...     username="Alice Smith",
        ...     roles=["developer"],
        ...     session_id="abc123"
        ... )
        >>> user.is_authenticated
        True
        >>> user.has_role("developer")
        True
    """
    
    user_id: str
    username: str
    roles: list[str] = field(default_factory=list)
    session_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    metadata: dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def anonymous(cls) -> UserContext:
        """
        Create an anonymous user context.
        
        Used when no authentication is provided. Anonymous users have
        limited permissions (readonly role only).
        
        Returns:
            UserContext with anonymous identity
            
        Example:
            >>> anon = UserContext.anonymous()
            >>> anon.user_id
            'anonymous'
            >>> anon.is_authenticated
            False
        """
        return cls(
            user_id="anonymous",
            username="Anonymous User",
            roles=["readonly"],
            session_id=str(uuid.uuid4()),
        )
    
    @classmethod
    def system(cls) -> UserContext:
        """
        Create a system user context.
        
        Used for automated operations, background tasks, and system-initiated
        actions. System users have elevated permissions.
        
        Returns:
            UserContext with system identity
        """
        return cls(
            user_id="system",
            username="CORTEX System",
            roles=["system", "admin"],
            session_id=f"system-{uuid.uuid4()}",
        )
    
    @property
    def is_authenticated(self) -> bool:
        """Check if user is authenticated (not anonymous)."""
        return self.user_id not in ("anonymous", "")
    
    @property
    def is_system(self) -> bool:
        """Check if this is a system user context."""
        return self.user_id == "system"
    
    def has_role(self, role: str) -> bool:
        """
        Check if user has a specific role.
        
        Args:
            role: Role name to check
            
        Returns:
            True if user has the role
        """
        return role in self.roles
    
    def has_any_role(self, *roles: str) -> bool:
        """
        Check if user has any of the specified roles.
        
        Args:
            *roles: Role names to check
            
        Returns:
            True if user has at least one of the roles
        """
        return any(role in self.roles for role in roles)
    
    def to_dict(self) -> dict[str, Any]:
        """
        Convert to dictionary for serialization.
        
        Returns:
            Dictionary representation suitable for JSON/audit logging
        """
        return {
            "user_id": self.user_id,
            "username": self.username,
            "roles": self.roles,
            "session_id": self.session_id,
            "created_at": self.created_at.isoformat(),
            "is_authenticated": self.is_authenticated,
            "metadata": self.metadata,
        }


# Context variable for thread-safe user context storage
_current_user: ContextVar[Optional[UserContext]] = ContextVar(
    "cortex_current_user",
    default=None,
)


def get_current_user() -> UserContext:
    """
    Get the current user context.
    
    Returns the user context for the current execution context.
    If no user has been set, returns an anonymous user.
    
    This function is thread-safe and async-safe due to contextvars.
    
    Returns:
        Current UserContext (anonymous if not set)
        
    Example:
        >>> user = get_current_user()
        >>> print(f"Request by: {user.username}")
    """
    user = _current_user.get()
    if user is None:
        return UserContext.anonymous()
    return user


def set_current_user(user: UserContext) -> None:
    """
    Set the current user context.
    
    Sets the user context for the current execution context.
    This should be called at the beginning of each request/operation.
    
    Args:
        user: UserContext to set as current
        
    Example:
        >>> user = UserContext(user_id="alice", username="Alice", roles=["dev"])
        >>> set_current_user(user)
        >>> get_current_user().username
        'Alice'
    """
    _current_user.set(user)


def clear_user_context() -> None:
    """
    Clear the current user context.
    
    Resets the user context to None, causing subsequent calls to
    get_current_user() to return anonymous user.
    
    Should be called at the end of request handling for cleanup.
    """
    _current_user.set(None)


def require_user_context(func: F) -> F:
    """
    Decorator to ensure user context exists before function execution.
    
    Raises PermissionError if the current user is anonymous.
    Use this decorator on functions that require authentication.
    
    Args:
        func: Function to decorate
        
    Returns:
        Decorated function that checks authentication
        
    Raises:
        PermissionError: If user is not authenticated
        
    Example:
        >>> @require_user_context
        ... def sensitive_operation():
        ...     user = get_current_user()
        ...     return f"Hello, {user.username}"
        ...
        >>> sensitive_operation()  # Raises PermissionError if anonymous
    """
    @wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        user = get_current_user()
        if not user.is_authenticated:
            raise PermissionError(
                f"User authentication required for {func.__name__}. "
                "Please provide valid credentials via X-CORTEX-API-KEY header."
            )
        return func(*args, **kwargs)
    
    return wrapper  # type: ignore[return-value]


def require_role(*required_roles: str) -> Callable[[F], F]:
    """
    Decorator factory to ensure user has required role(s).
    
    Creates a decorator that checks if the current user has at least
    one of the specified roles before allowing function execution.
    
    Args:
        *required_roles: Role names that grant access
        
    Returns:
        Decorator function
        
    Raises:
        PermissionError: If user lacks required role
        
    Example:
        >>> @require_role("admin", "superuser")
        ... def admin_only_function():
        ...     return "Secret admin data"
        ...
        >>> admin_only_function()  # Raises if user lacks admin/superuser role
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            user = get_current_user()
            if not user.has_any_role(*required_roles):
                raise PermissionError(
                    f"Access denied to {func.__name__}. "
                    f"Required role: one of {required_roles}. "
                    f"User roles: {user.roles}"
                )
            return func(*args, **kwargs)
        
        return wrapper  # type: ignore[return-value]
    
    return decorator
