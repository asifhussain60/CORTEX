"""
CORTEX Collaboration Module - Team Collaboration Layer (Phase 5.5).

This module enables multi-user support for 2-10 users sharing a single MCP server.
It provides user session context, operation locking, and audit attribution.

Components:
    - UserContext: User identity and session management
    - OperationLock: File-based locking for concurrent operations
    - require_user_context: Decorator for user authentication

Usage:
    from cortex.collaboration import (
        get_current_user,
        set_current_user,
        UserContext,
        require_user_context,
        operation_lock,
    )

    # Set user context for a request
    user = UserContext(
        user_id="alice",
        username="Alice Smith",
        roles=["developer"],
        session_id="abc123"
    )
    set_current_user(user)

    # Get current user in any function
    current = get_current_user()
    print(f"Current user: {current.username}")

    # Use operation locking for concurrent safety
    with operation_lock("file:src/main.py"):
        # Exclusive access to file
        modify_file()

Phase: 5.5 (Team Collaboration Layer)
Author: Asif Hussain
Date: 2026-01-27
CORE-030: Docker-first architecture - no database dependencies
"""

from cortex.collaboration.operation_lock import (
    LockTimeoutError,
    OperationLockError,
    operation_lock,
)
from cortex.collaboration.user_context import (
    UserContext,
    clear_user_context,
    get_current_user,
    require_user_context,
    set_current_user,
)

__all__ = [
    # User Context
    "UserContext",
    "get_current_user",
    "set_current_user",
    "require_user_context",
    "clear_user_context",
    # Operation Locking
    "operation_lock",
    "OperationLockError",
    "LockTimeoutError",
]
