"""
API Key Authentication for CORTEX MCP Server.

Provides simple API key validation for team access control.
API keys are loaded from environment variables for security.

Phase: 5.5 (Team Collaboration Layer)
Task: TEAM-003 (API Key Authentication)
Author: Asif Hussain
Date: 2026-01-27

CORE-030: Docker-first architecture - keys from environment, no database.

Environment Variables:
    CORTEX_AUTH_ENABLED: Set to "true" to enable authentication
    CORTEX_API_KEY_<USERNAME>: API key for each user
    
Example:
    export CORTEX_AUTH_ENABLED=true
    export CORTEX_API_KEY_ALICE=sk_alice_abc123xyz
    export CORTEX_API_KEY_BOB=sk_bob_def456uvw
"""

from __future__ import annotations

import hashlib
import hmac
import os
import secrets
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Callable, Optional

from cortex.collaboration.user_context import UserContext, set_current_user


@dataclass
class APIKeyInfo:
    """
    Information about a registered API key.
    
    Attributes:
        key_hash: SHA256 hash of the API key (never store plain keys)
        user_id: User ID associated with this key
        username: Display name for the user
        roles: Roles granted to this user
        created_at: When this key was registered
    """
    key_hash: str
    user_id: str
    username: str
    roles: list[str]
    created_at: datetime


# In-memory storage for API keys (loaded from environment)
_api_keys: dict[str, APIKeyInfo] = {}
_auth_enabled: bool = False
_initialized: bool = False


def _hash_key(api_key: str) -> str:
    """
    Hash an API key using SHA256.
    
    Args:
        api_key: Plain text API key
        
    Returns:
        SHA256 hash of the key
    """
    return hashlib.sha256(api_key.encode()).hexdigest()


def load_api_keys_from_env() -> int:
    """
    Load API keys from environment variables.
    
    Scans environment for variables matching CORTEX_API_KEY_<USERNAME>
    and registers them for authentication.
    
    Returns:
        Number of API keys loaded
        
    Environment Variables:
        CORTEX_AUTH_ENABLED: "true" to enable (default: false)
        CORTEX_API_KEY_<USERNAME>: API key for user
        
    Example:
        >>> os.environ["CORTEX_AUTH_ENABLED"] = "true"
        >>> os.environ["CORTEX_API_KEY_ALICE"] = "sk_alice_secret"
        >>> load_api_keys_from_env()
        1
    """
    global _api_keys, _auth_enabled, _initialized
    
    # Check if auth is enabled
    _auth_enabled = os.environ.get("CORTEX_AUTH_ENABLED", "").lower() == "true"
    
    # Clear existing keys
    _api_keys.clear()
    
    # Scan for API key environment variables
    prefix = "CORTEX_API_KEY_"
    loaded = 0
    
    for key, value in os.environ.items():
        if key.startswith(prefix) and value:
            username = key[len(prefix):].lower()
            
            # Hash the key (never store plain keys)
            key_hash = _hash_key(value)
            
            # Determine roles (admin keys get admin role)
            roles = ["user"]
            if username == "admin" or "_admin" in username.lower():
                roles = ["admin", "user"]
            
            # Register the key
            _api_keys[key_hash] = APIKeyInfo(
                key_hash=key_hash,
                user_id=username,
                username=username.replace("_", " ").title(),
                roles=roles,
                created_at=datetime.now(timezone.utc),
            )
            loaded += 1
    
    _initialized = True
    return loaded


def is_auth_enabled() -> bool:
    """
    Check if authentication is enabled.
    
    Returns:
        True if CORTEX_AUTH_ENABLED is set to "true"
    """
    global _initialized
    if not _initialized:
        load_api_keys_from_env()
    return _auth_enabled


def validate_api_key(api_key: str) -> Optional[UserContext]:
    """
    Validate an API key and return user context.
    
    Checks if the provided API key matches a registered key and
    returns the associated user context.
    
    Args:
        api_key: API key to validate (from X-CORTEX-API-KEY header)
        
    Returns:
        UserContext if key is valid, None if invalid
        
    Example:
        >>> user = validate_api_key("sk_alice_secret")
        >>> if user:
        ...     print(f"Authenticated as: {user.username}")
        ... else:
        ...     print("Invalid API key")
    """
    global _initialized
    if not _initialized:
        load_api_keys_from_env()
    
    if not api_key:
        return None
    
    # Hash the provided key and look it up
    key_hash = _hash_key(api_key)
    key_info = _api_keys.get(key_hash)
    
    if key_info is None:
        return None
    
    # Create user context for this request
    return UserContext(
        user_id=key_info.user_id,
        username=key_info.username,
        roles=key_info.roles,
        session_id=str(uuid.uuid4()),
        metadata={"auth_method": "api_key"},
    )


def generate_api_key(prefix: str = "sk") -> str:
    """
    Generate a new secure API key.
    
    Creates a cryptographically secure random API key.
    Use this to generate keys for new users.
    
    Args:
        prefix: Prefix for the key (default: "sk")
        
    Returns:
        New API key string
        
    Example:
        >>> key = generate_api_key()
        >>> print(key)  # sk_a1b2c3d4e5f6...
    """
    random_part = secrets.token_urlsafe(32)
    return f"{prefix}_{random_part}"


def register_api_key(
    api_key: str,
    user_id: str,
    username: str,
    roles: Optional[list[str]] = None,
) -> APIKeyInfo:
    """
    Register a new API key programmatically.
    
    Note: In production, prefer using environment variables.
    This function is primarily for testing and development.
    
    Args:
        api_key: The API key to register
        user_id: User ID to associate with the key
        username: Display name for the user
        roles: List of roles (default: ["user"])
        
    Returns:
        APIKeyInfo for the registered key
    """
    global _api_keys
    
    key_hash = _hash_key(api_key)
    key_info = APIKeyInfo(
        key_hash=key_hash,
        user_id=user_id,
        username=username,
        roles=roles or ["user"],
        created_at=datetime.now(timezone.utc),
    )
    
    _api_keys[key_hash] = key_info
    return key_info


def revoke_api_key(api_key: str) -> bool:
    """
    Revoke an API key.
    
    Removes the key from the registry, preventing further use.
    
    Args:
        api_key: The API key to revoke
        
    Returns:
        True if key was found and revoked, False if not found
    """
    global _api_keys
    
    key_hash = _hash_key(api_key)
    if key_hash in _api_keys:
        del _api_keys[key_hash]
        return True
    return False


async def auth_middleware(request: Any, call_next: Callable) -> Any:
    """
    FastAPI middleware for API key authentication.
    
    Extracts API key from X-CORTEX-API-KEY header, validates it,
    and sets the user context for the request.
    
    Args:
        request: FastAPI Request object
        call_next: Next middleware in chain
        
    Returns:
        Response from downstream handler
        
    Usage in FastAPI:
        >>> app = FastAPI()
        >>> app.middleware("http")(auth_middleware)
    """
    # Check if auth is enabled
    if not is_auth_enabled():
        # Auth disabled - use anonymous context
        set_current_user(UserContext.anonymous())
        return await call_next(request)
    
    # Extract API key from header
    api_key = request.headers.get("X-CORTEX-API-KEY", "")
    
    if api_key:
        user = validate_api_key(api_key)
        if user:
            set_current_user(user)
        else:
            # Invalid key - still process but as anonymous
            set_current_user(UserContext.anonymous())
    else:
        # No key provided
        set_current_user(UserContext.anonymous())
    
    response = await call_next(request)
    return response


def get_registered_users() -> list[str]:
    """
    Get list of registered user IDs.
    
    Returns:
        List of user IDs with registered API keys
    """
    global _initialized
    if not _initialized:
        load_api_keys_from_env()
    
    return [info.user_id for info in _api_keys.values()]
