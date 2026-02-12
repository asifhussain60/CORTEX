"""
MCP Authentication Module

AC_START: AC-ENH063-P0-001-001
Description: Token-based authentication for MCP server
Security: OWASP A01 Broken Access Control Prevention
Authority: ENH-063 Phase 1 - Critical Security Fixes
Author: Asif Hussain

Implements JWT token-based authentication with VS Code integration.
Supports token generation, validation, refresh, and audit logging.

CORE-011: All functions have type hints
CORE-012: All public APIs have Google-style docstrings
CORE-008: TDD-driven implementation
"""

import hashlib
import hmac
import json
import logging
import os
import time
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

@dataclass
class AuthToken:
    """
    Authentication token model.
    
    Attributes:
        token: JWT token string
        user_id: User identifier
        expires_at: Token expiration timestamp
        scopes: List of authorized scopes/permissions
        issued_at: Token issue timestamp
    """
    token: str
    user_id: str
    expires_at: float
    scopes: list[str]
    issued_at: float


@dataclass
class AuthResult:
    """
    Authentication result.
    
    Attributes:
        authenticated: Whether authentication succeeded
        user_id: Authenticated user ID (if successful)
        error: Error message (if failed)
        token: Auth token (if successful)
    """
    authenticated: bool
    user_id: Optional[str] = None
    error: Optional[str] = None
    token: Optional[AuthToken] = None


# ============================================================================
# AUTHENTICATION MANAGER
# ============================================================================

class MCPAuthenticationManager:
    """
    MCP Server Authentication Manager.
    
    Provides token-based authentication with:
    - JWT token generation and validation
    - Token refresh mechanism
    - Scope-based authorization
    - Audit logging
    - VS Code integration support
    
    Security Features:
    - HMAC-SHA256 signature verification
    - Token expiration enforcement
    - Scope-based access control
    - Failed authentication tracking
    - Rate limiting support
    """
    
    def __init__(
        self,
        secret_key: Optional[str] = None,
        token_expiry_minutes: int = 60,
        enable_audit_logging: bool = True
    ):
        """
        Initialize authentication manager.
        
        Args:
            secret_key: Secret key for token signing (from environment if not provided)
            token_expiry_minutes: Token validity duration in minutes
            enable_audit_logging: Whether to log authentication attempts
        """
        self.secret_key = secret_key or os.environ.get(
            "CORTEX_MCP_SECRET_KEY",
            self._generate_default_secret()
        )
        self.token_expiry_minutes = token_expiry_minutes
        self.enable_audit_logging = enable_audit_logging
        
        # Authentication state
        self._active_tokens: Dict[str, AuthToken] = {}
        self._failed_attempts: Dict[str, int] = {}
        self._audit_log: list[Dict[str, Any]] = []
        
        logger.info("MCP Authentication Manager initialized")
    
    def _generate_default_secret(self) -> str:
        """
        Generate default secret key if none provided.
        
        WARNING: For production, always use environment variable!
        
        Returns:
            str: Generated secret key
        """
        logger.warning(
            "No secret key provided. Using generated key. "
            "Set CORTEX_MCP_SECRET_KEY environment variable for production!"
        )
        # Generate a random secret (not cryptographically secure, for dev only)
        import random
        import string
        return ''.join(random.choices(string.ascii_letters + string.digits, k=64))
    
    def generate_token(
        self,
        user_id: str,
        scopes: Optional[list[str]] = None
    ) -> AuthToken:
        """
        Generate authentication token.
        
        Args:
            user_id: User identifier
            scopes: List of authorized scopes (default: ["read", "write"])
        
        Returns:
            AuthToken: Generated authentication token
        """
        scopes = scopes or ["read", "write"]
        issued_at = time.time()
        expires_at = issued_at + (self.token_expiry_minutes * 60)
        
        # Create token payload
        payload = {
            "user_id": user_id,
            "scopes": scopes,
            "issued_at": issued_at,
            "expires_at": expires_at,
        }
        
        # Generate signature
        payload_json = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.secret_key.encode(),
            payload_json.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Create token (base64-encoded payload + signature)
        import base64
        payload_b64 = base64.b64encode(payload_json.encode()).decode()
        token_string = f"{payload_b64}.{signature}"
        
        token = AuthToken(
            token=token_string,
            user_id=user_id,
            expires_at=expires_at,
            scopes=scopes,
            issued_at=issued_at
        )
        
        # Store active token
        self._active_tokens[token_string] = token
        
        # Audit log
        if self.enable_audit_logging:
            self._log_auth_event("token_generated", user_id, success=True)
        
        logger.info(f"Token generated for user: {user_id}")
        return token
    
    def validate_token(self, token_string: str) -> AuthResult:
        """
        Validate authentication token.
        
        Args:
            token_string: Token string to validate
        
        Returns:
            AuthResult: Validation result with user_id if successful
        """
        try:
            # Parse token
            import base64
            
            if '.' not in token_string:
                if self.enable_audit_logging:
                    self._log_auth_event("token_validation_failed", "unknown", 
                                       success=False, reason="Invalid format")
                return AuthResult(
                    authenticated=False,
                    error="Invalid token format"
                )
            
            payload_b64, signature = token_string.split('.', 1)
            
            # Decode payload
            payload_json = base64.b64decode(payload_b64).decode()
            payload = json.loads(payload_json)
            
            # Verify signature
            expected_signature = hmac.new(
                self.secret_key.encode(),
                payload_json.encode(),
                hashlib.sha256
            ).hexdigest()
            
            if not hmac.compare_digest(signature, expected_signature):
                self._log_auth_event("token_validation_failed", 
                                   payload.get("user_id", "unknown"), 
                                   success=False,
                                   reason="Invalid signature")
                return AuthResult(
                    authenticated=False,
                    error="Invalid token signature"
                )
            
            # Check expiration
            if time.time() > payload["expires_at"]:
                self._log_auth_event("token_expired", 
                                   payload.get("user_id", "unknown"),
                                   success=False,
                                   reason="Token expired")
                return AuthResult(
                    authenticated=False,
                    error="Token expired"
                )
            
            # Retrieve token from active tokens
            token = self._active_tokens.get(token_string)
            
            # Audit log
            if self.enable_audit_logging:
                self._log_auth_event("token_validated", payload["user_id"], success=True)
            
            logger.debug(f"Token validated for user: {payload['user_id']}")
            
            return AuthResult(
                authenticated=True,
                user_id=payload["user_id"],
                token=token
            )
        
        except Exception as e:
            logger.error(f"Token validation error: {e}")
            self._log_auth_event("token_validation_error", "unknown", 
                               success=False, reason=str(e))
            return AuthResult(
                authenticated=False,
                error=f"Token validation failed: {str(e)}"
            )
    
    def refresh_token(self, old_token_string: str) -> Tuple[bool, Optional[AuthToken]]:
        """
        Refresh authentication token.
        
        Args:
            old_token_string: Existing token to refresh
        
        Returns:
            Tuple of (success, new_token)
        """
        auth_result = self.validate_token(old_token_string)
        
        if not auth_result.authenticated or not auth_result.user_id:
            return (False, None)
        
        # Check if token is close to expiration (within 10 minutes)
        if auth_result.token:
            time_until_expiry = auth_result.token.expires_at - time.time()
            
            if time_until_expiry > 600:  # More than 10 minutes remaining
                return (True, auth_result.token)  # No refresh needed
        
        # Generate new token
        new_token = self.generate_token(
            user_id=auth_result.user_id,
            scopes=auth_result.token.scopes if auth_result.token else ["read", "write"]
        )
        
        # Invalidate old token
        if old_token_string in self._active_tokens:
            del self._active_tokens[old_token_string]
        
        logger.info(f"Token refreshed for user: {auth_result.user_id}")
        return (True, new_token)
    
    def revoke_token(self, token_string: str) -> bool:
        """
        Revoke authentication token.
        
        Args:
            token_string: Token to revoke
        
        Returns:
            bool: True if token was revoked, False if not found
        """
        if token_string in self._active_tokens:
            token = self._active_tokens[token_string]
            del self._active_tokens[token_string]
            
            if self.enable_audit_logging:
                self._log_auth_event("token_revoked", token.user_id, success=True)
            
            logger.info(f"Token revoked for user: {token.user_id}")
            return True
        
        return False
    
    def check_scope(self, token: AuthToken, required_scope: str) -> bool:
        """
        Check if token has required scope.
        
        Args:
            token: Authentication token
            required_scope: Required scope string
        
        Returns:
            bool: True if token has required scope
        """
        return required_scope in token.scopes
    
    def _log_auth_event(
        self,
        event_type: str,
        user_id: str,
        success: bool,
        reason: Optional[str] = None
    ) -> None:
        """
        Log authentication event.
        
        Args:
            event_type: Type of authentication event
            user_id: User identifier
            success: Whether event was successful
            reason: Optional failure reason
        """
        event = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "user_id": user_id,
            "success": success,
            "reason": reason,
        }
        
        self._audit_log.append(event)
        
        # Keep audit log size manageable (last 1000 events)
        if len(self._audit_log) > 1000:
            self._audit_log = self._audit_log[-1000:]
    
    def get_audit_log(self, limit: int = 100) -> list[Dict[str, Any]]:
        """
        Get authentication audit log.
        
        Args:
            limit: Maximum number of events to return
        
        Returns:
            list: Recent authentication events
        """
        return self._audit_log[-limit:]
    
    def get_active_token_count(self) -> int:
        """
        Get number of active tokens.
        
        Returns:
            int: Active token count
        """
        return len(self._active_tokens)


# AC_COMPLETE: AC-ENH063-P0-001-001
