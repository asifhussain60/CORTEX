"""
Tests for Real-Time Dashboard Authentication Layer

Tests:
    - Token generation (admin and user)
    - Token validation (valid, expired, revoked)
    - Token revocation
    - Session management
    - Expired token cleanup
    - Audit logging
    - Database persistence

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from datetime import datetime, timedelta
from pathlib import Path

from src.operations.realtime_dashboard_auth import (
    RealtimeDashboardAuth,
    TokenStatus,
    AuthToken,
    AuditLogEntry
)


@pytest.fixture
def temp_brain_dir():
    """Create temporary brain directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def auth(temp_brain_dir):
    """Create authentication instance."""
    return RealtimeDashboardAuth(
        brain_path=temp_brain_dir,
        token_duration_minutes=30,
        enable_audit_logging=True,
        enable_persistence=True
    )


def test_initialization(auth, temp_brain_dir):
    """Test auth layer initialization."""
    assert auth.brain_path == temp_brain_dir
    assert auth.token_duration == timedelta(minutes=30)
    assert auth.enable_audit_logging is True
    assert auth.enable_persistence is True
    assert len(auth.tokens) == 0


def test_generate_admin_token(auth):
    """Test admin token generation."""
    token = auth.generate_token('admin_user', is_admin=True)
    
    assert token is not None
    assert len(token) == 36  # UUID format
    assert token in auth.tokens
    
    auth_token = auth.tokens[token]
    assert auth_token.user_id == 'admin_user'
    assert auth_token.is_admin is True
    assert auth_token.status == TokenStatus.ACTIVE


def test_generate_user_token(auth):
    """Test user token generation."""
    token = auth.generate_token('regular_user', is_admin=False)
    
    assert token is not None
    assert token in auth.tokens
    
    auth_token = auth.tokens[token]
    assert auth_token.user_id == 'regular_user'
    assert auth_token.is_admin is False


def test_validate_valid_token(auth):
    """Test validation of valid token."""
    token = auth.generate_token('test_user', is_admin=True)
    
    user_info = auth.validate_token(token)
    
    assert user_info is not None
    assert user_info['user_id'] == 'test_user'
    assert user_info['is_admin'] is True
    assert 'created_at' in user_info
    assert 'expires_at' in user_info


def test_validate_invalid_token(auth):
    """Test validation of invalid token."""
    user_info = auth.validate_token('invalid_token')
    
    assert user_info is None


def test_validate_expired_token(auth, temp_brain_dir):
    """Test validation of expired token."""
    # Create auth with 0-minute duration (immediate expiration)
    short_auth = RealtimeDashboardAuth(
        brain_path=temp_brain_dir,
        token_duration_minutes=0
    )
    
    token = short_auth.generate_token('test_user', is_admin=True)
    
    # Token should be expired immediately
    user_info = short_auth.validate_token(token)
    
    assert user_info is None
    assert short_auth.tokens[token].status == TokenStatus.EXPIRED


def test_revoke_token(auth):
    """Test token revocation."""
    token = auth.generate_token('test_user', is_admin=True)
    
    # Revoke token
    result = auth.revoke_token(token)
    
    assert result is True
    assert auth.tokens[token].status == TokenStatus.REVOKED
    
    # Validation should fail
    user_info = auth.validate_token(token)
    assert user_info is None


def test_revoke_nonexistent_token(auth):
    """Test revoking non-existent token."""
    result = auth.revoke_token('nonexistent_token')
    
    assert result is False


def test_cleanup_expired_tokens(auth, temp_brain_dir):
    """Test cleanup of expired tokens."""
    # Create tokens with short duration
    short_auth = RealtimeDashboardAuth(
        brain_path=temp_brain_dir,
        token_duration_minutes=0
    )
    
    # Generate multiple tokens
    for i in range(5):
        short_auth.generate_token(f'user_{i}', is_admin=True)
    
    assert len(short_auth.tokens) == 5
    
    # Clean up expired tokens
    cleaned = short_auth.cleanup_expired_tokens()
    
    assert cleaned == 5
    assert len(short_auth.tokens) == 0


def test_get_active_sessions(auth):
    """Test getting active sessions."""
    # Generate multiple tokens
    auth.generate_token('user_1', is_admin=True)
    auth.generate_token('user_2', is_admin=False)
    auth.generate_token('user_3', is_admin=True)
    
    sessions = auth.get_active_sessions()
    
    assert len(sessions) == 3
    assert all('user_id' in session for session in sessions)
    assert all('is_admin' in session for session in sessions)


def test_token_with_metadata(auth):
    """Test token generation with metadata."""
    metadata = {'ip_address': '127.0.0.1', 'user_agent': 'TestClient/1.0'}
    
    token = auth.generate_token('test_user', is_admin=True, metadata=metadata)
    
    user_info = auth.validate_token(token)
    
    assert user_info is not None
    assert user_info['metadata'] == metadata


def test_audit_logging_enabled(auth):
    """Test audit logging is working."""
    # Generate token
    token = auth.generate_token('test_user', is_admin=True)
    
    # Validate token
    auth.validate_token(token)
    
    # Revoke token
    auth.revoke_token(token)
    
    # Check audit log
    audit_log = auth.get_audit_log()
    
    assert len(audit_log) >= 3  # At least 3 events
    
    # Check event types
    actions = [entry['action'] for entry in audit_log]
    assert 'token_generated' in actions
    assert 'token_validation' in actions
    assert 'token_revoked' in actions


def test_audit_logging_disabled(temp_brain_dir):
    """Test auth layer with audit logging disabled."""
    auth = RealtimeDashboardAuth(
        brain_path=temp_brain_dir,
        enable_audit_logging=False
    )
    
    # Generate and validate token
    token = auth.generate_token('test_user', is_admin=True)
    auth.validate_token(token)
    
    # Audit log should be empty
    assert len(auth.audit_log) == 0


def test_database_persistence(auth, temp_brain_dir):
    """Test database persistence of tokens."""
    # Generate token
    token = auth.generate_token('test_user', is_admin=True)
    
    # Verify database file exists
    db_path = temp_brain_dir / "tier1" / "dashboard_auth.db"
    assert db_path.exists()
    
    # Create new auth instance (should load from database)
    auth2 = RealtimeDashboardAuth(
        brain_path=temp_brain_dir,
        enable_persistence=True
    )
    
    # Token should be loadable
    user_info = auth2.validate_token(token)
    assert user_info is not None
    assert user_info['user_id'] == 'test_user'


def test_get_audit_log_filtered_by_user(auth):
    """Test getting audit log filtered by user."""
    # Generate tokens for different users
    auth.generate_token('user_1', is_admin=True)
    auth.generate_token('user_2', is_admin=True)
    auth.generate_token('user_3', is_admin=True)
    
    # Get audit log for specific user
    user_1_log = auth.get_audit_log(user_id='user_1')
    
    assert len(user_1_log) >= 1
    assert all(entry['user_id'] == 'user_1' for entry in user_1_log)


def test_get_audit_log_with_limit(auth):
    """Test getting audit log with limit."""
    # Generate many tokens
    for i in range(10):
        auth.generate_token(f'user_{i}', is_admin=True)
    
    # Get limited audit log
    audit_log = auth.get_audit_log(limit=5)
    
    assert len(audit_log) <= 5


def test_token_expiration_calculation(auth):
    """Test token expiration is calculated correctly."""
    token = auth.generate_token('test_user', is_admin=True)
    
    auth_token = auth.tokens[token]
    expected_expiration = auth_token.created_at + timedelta(minutes=30)
    
    # Allow 1 second tolerance
    assert abs((auth_token.expires_at - expected_expiration).total_seconds()) < 1


def test_persistence_disabled(temp_brain_dir):
    """Test auth layer with persistence disabled."""
    auth = RealtimeDashboardAuth(
        brain_path=temp_brain_dir,
        enable_persistence=False
    )
    
    # Generate token
    auth.generate_token('test_user', is_admin=True)
    
    # Database should not be created
    db_path = temp_brain_dir / "tier1" / "dashboard_auth.db"
    assert not db_path.exists()


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
