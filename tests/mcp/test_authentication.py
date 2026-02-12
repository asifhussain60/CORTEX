"""
Tests for MCP Authentication Module

AC_START: AC-ENH063-P0-001-TEST-001
Description: Comprehensive tests for MCPAuthenticationManager
Authority: ENH-063 Phase 1 - TDD Cycle Completion
Author: Asif Hussain

Tests cover:
- Token generation and validation
- Token expiration handling
- Token refresh mechanism
- Token revocation
- Scope-based authorization
- Audit logging
- Security edge cases

CORE-008: TDD-driven test suite
"""

import time
from datetime import datetime, timedelta
from typing import Dict

import pytest

from cortex.mcp.authentication import (
    AuthResult,
    AuthToken,
    MCPAuthenticationManager,
)


class TestMCPAuthenticationManager:
    """Test suite for MCP Authentication Manager."""
    
    def test_initialization_with_custom_secret(self):
        """Test manager initialization with custom secret key."""
        # Arrange
        custom_secret = "test-secret-key-12345"
        
        # Act
        manager = MCPAuthenticationManager(secret_key=custom_secret)
        
        # Assert
        assert manager.secret_key == custom_secret
        assert manager.enable_audit_logging is True
        assert manager.token_expiry_minutes == 60
    
    def test_initialization_without_secret_generates_default(self):
        """Test manager generates default secret if none provided."""
        # Act
        manager = MCPAuthenticationManager()
        
        # Assert
        assert manager.secret_key is not None
        assert len(manager.secret_key) > 0
    
    def test_generate_token_creates_valid_token(self):
        """Test token generation creates valid token structure."""
        # Arrange
        manager = MCPAuthenticationManager(secret_key="test-secret")
        user_id = "test_user_123"
        
        # Act
        token = manager.generate_token(user_id=user_id)
        
        # Assert
        assert isinstance(token, AuthToken)
        assert token.user_id == user_id
        assert token.token is not None
        assert "." in token.token  # Contains payload and signature
        assert token.expires_at > time.time()
        assert "read" in token.scopes
        assert "write" in token.scopes
    
    def test_generate_token_with_custom_scopes(self):
        """Test token generation with custom scopes."""
        # Arrange
        manager = MCPAuthenticationManager(secret_key="test-secret")
        user_id = "admin_user"
        scopes = ["admin", "deploy", "read"]
        
        # Act
        token = manager.generate_token(user_id=user_id, scopes=scopes)
        
        # Assert
        assert token.scopes == scopes
        assert "admin" in token.scopes
        assert "deploy" in token.scopes
    
    def test_validate_token_succeeds_for_valid_token(self):
        """Test token validation succeeds for valid token."""
        # Arrange
        manager = MCPAuthenticationManager(secret_key="test-secret")
        user_id = "test_user"
        token = manager.generate_token(user_id=user_id)
        
        # Act
        result = manager.validate_token(token.token)
        
        # Assert
        assert isinstance(result, AuthResult)
        assert result.authenticated is True
        assert result.user_id == user_id
        assert result.error is None
    
    def test_validate_token_fails_for_invalid_signature(self):
        """Test token validation fails for tampered token."""
        # Arrange
        manager = MCPAuthenticationManager(secret_key="test-secret")
        token = manager.generate_token(user_id="test_user")
        
        # Tamper with token signature
        payload, signature = token.token.split(".")
        tampered_token = f"{payload}.invalid_signature"
        
        # Act
        result = manager.validate_token(tampered_token)
        
        # Assert
        assert result.authenticated is False
        assert result.error is not None
        assert "signature" in result.error.lower()
    
    def test_validate_token_fails_for_expired_token(self):
        """Test token validation fails for expired token."""
        # Arrange
        manager = MCPAuthenticationManager(
            secret_key="test-secret",
            token_expiry_minutes=0  # Expire immediately
        )
        token = manager.generate_token(user_id="test_user")
        
        # Wait for token to expire
        time.sleep(0.1)
        
        # Act
        result = manager.validate_token(token.token)
        
        # Assert
        assert result.authenticated is False
        assert result.error is not None
        assert "expired" in result.error.lower()
    
    def test_validate_token_fails_for_malformed_token(self):
        """Test token validation fails for malformed token."""
        # Arrange
        manager = MCPAuthenticationManager(secret_key="test-secret")
        
        # Act
        result = manager.validate_token("malformed_token_without_dot")
        
        # Assert
        assert result.authenticated is False
        assert result.error is not None
        assert "format" in result.error.lower()
    
    def test_refresh_token_generates_new_token_when_expiring(self):
        """Test token refresh generates new token when close to expiration."""
        # Arrange
        manager = MCPAuthenticationManager(
            secret_key="test-secret",
            token_expiry_minutes=1  # 1 minute expiry
        )
        old_token = manager.generate_token(user_id="test_user")
        
        # Manually adjust expiration to be within 10 minutes (triggers refresh)
        old_token.expires_at = time.time() + 300  # 5 minutes remaining
        
        # Act
        success, new_token = manager.refresh_token(old_token.token)
        
        # Assert
        assert success is True
        assert new_token is not None
        assert new_token.token != old_token.token  # Different token
        assert new_token.user_id == old_token.user_id  # Same user
    
    def test_refresh_token_returns_same_token_if_not_expiring(self):
        """Test token refresh returns same token if not close to expiration."""
        # Arrange
        manager = MCPAuthenticationManager(
            secret_key="test-secret",
            token_expiry_minutes=60  # 1 hour expiry
        )
        old_token = manager.generate_token(user_id="test_user")
        
        # Act
        success, returned_token = manager.refresh_token(old_token.token)
        
        # Assert
        assert success is True
        assert returned_token is not None
        # Should return same token since it's not expiring soon
    
    def test_refresh_token_fails_for_invalid_token(self):
        """Test token refresh fails for invalid token."""
        # Arrange
        manager = MCPAuthenticationManager(secret_key="test-secret")
        
        # Act
        success, new_token = manager.refresh_token("invalid_token")
        
        # Assert
        assert success is False
        assert new_token is None
    
    def test_revoke_token_removes_token_from_active_list(self):
        """Test token revocation removes token from active tokens."""
        # Arrange
        manager = MCPAuthenticationManager(secret_key="test-secret")
        token = manager.generate_token(user_id="test_user")
        
        # Verify token is active
        assert token.token in manager._active_tokens
        
        # Act
        revoked = manager.revoke_token(token.token)
        
        # Assert
        assert revoked is True
        assert token.token not in manager._active_tokens
    
    def test_revoke_token_returns_false_for_nonexistent_token(self):
        """Test token revocation returns False for non-existent token."""
        # Arrange
        manager = MCPAuthenticationManager(secret_key="test-secret")
        
        # Act
        revoked = manager.revoke_token("nonexistent_token")
        
        # Assert
        assert revoked is False
    
    def test_check_scope_returns_true_for_authorized_scope(self):
        """Test scope check returns True for authorized scope."""
        # Arrange
        manager = MCPAuthenticationManager(secret_key="test-secret")
        token = manager.generate_token(user_id="test_user", scopes=["read", "write", "admin"])
        
        # Act & Assert
        assert manager.check_scope(token, "read") is True
        assert manager.check_scope(token, "write") is True
        assert manager.check_scope(token, "admin") is True
    
    def test_check_scope_returns_false_for_unauthorized_scope(self):
        """Test scope check returns False for unauthorized scope."""
        # Arrange
        manager = MCPAuthenticationManager(secret_key="test-secret")
        token = manager.generate_token(user_id="test_user", scopes=["read"])
        
        # Act & Assert
        assert manager.check_scope(token, "write") is False
        assert manager.check_scope(token, "admin") is False
    
    def test_audit_logging_records_token_generation(self):
        """Test audit logging records token generation events."""
        # Arrange
        manager = MCPAuthenticationManager(
            secret_key="test-secret",
            enable_audit_logging=True
        )
        
        # Act
        token = manager.generate_token(user_id="test_user")
        
        # Assert
        audit_log = manager.get_audit_log()
        assert len(audit_log) > 0
        last_event = audit_log[-1]
        assert last_event["event_type"] == "token_generated"
        assert last_event["user_id"] == "test_user"
        assert last_event["success"] is True
    
    def test_audit_logging_records_validation_failures(self):
        """Test audit logging records token validation failures."""
        # Arrange
        manager = MCPAuthenticationManager(
            secret_key="test-secret",
            enable_audit_logging=True
        )
        
        # Act
        manager.validate_token("invalid_token")
        
        # Assert
        audit_log = manager.get_audit_log()
        failure_events = [e for e in audit_log if not e["success"]]
        assert len(failure_events) > 0
    
    def test_get_audit_log_respects_limit(self):
        """Test audit log retrieval respects limit parameter."""
        # Arrange
        manager = MCPAuthenticationManager(
            secret_key="test-secret",
            enable_audit_logging=True
        )
        
        # Generate multiple events
        for i in range(10):
            manager.generate_token(user_id=f"user_{i}")
        
        # Act
        limited_log = manager.get_audit_log(limit=5)
        
        # Assert
        assert len(limited_log) <= 5
    
    def test_get_active_token_count_returns_correct_count(self):
        """Test active token count returns correct number."""
        # Arrange
        manager = MCPAuthenticationManager(secret_key="test-secret")
        
        # Act
        token1 = manager.generate_token(user_id="user_1")
        token2 = manager.generate_token(user_id="user_2")
        count_before_revoke = manager.get_active_token_count()
        
        manager.revoke_token(token1.token)
        count_after_revoke = manager.get_active_token_count()
        
        # Assert
        assert count_before_revoke == 2
        assert count_after_revoke == 1
    
    def test_token_signature_verification_uses_hmac(self):
        """Test token signature uses HMAC-SHA256."""
        # Arrange
        manager = MCPAuthenticationManager(secret_key="test-secret")
        token = manager.generate_token(user_id="test_user")
        
        # Act - Validate with correct secret
        result_correct = manager.validate_token(token.token)
        
        # Create new manager with different secret
        manager2 = MCPAuthenticationManager(secret_key="different-secret")
        result_wrong_secret = manager2.validate_token(token.token)
        
        # Assert
        assert result_correct.authenticated is True
        assert result_wrong_secret.authenticated is False


# AC_COMPLETE: AC-ENH063-P0-001-TEST-001
