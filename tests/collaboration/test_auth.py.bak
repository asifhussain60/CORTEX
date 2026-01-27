"""
Tests for API Key Authentication (TEAM-003).

Phase: 5.5 (Team Collaboration Layer)
Author: Asif Hussain
Date: 2026-01-27
"""

import os
from unittest.mock import patch, MagicMock

import pytest

from cortex.mcp.auth import (
    load_api_keys_from_env,
    validate_api_key,
    generate_api_key,
    register_api_key,
    revoke_api_key,
    is_auth_enabled,
    get_registered_users,
    _hash_key,
)
from cortex.collaboration.user_context import UserContext


class TestHashKey:
    """Tests for key hashing."""
    
    def test_hash_is_deterministic(self):
        """Test that same key produces same hash."""
        key = "test_key_12345"
        hash1 = _hash_key(key)
        hash2 = _hash_key(key)
        assert hash1 == hash2
    
    def test_different_keys_different_hashes(self):
        """Test that different keys produce different hashes."""
        hash1 = _hash_key("key_one")
        hash2 = _hash_key("key_two")
        assert hash1 != hash2
    
    def test_hash_is_sha256(self):
        """Test that hash is 64 characters (SHA256 hex)."""
        hash_val = _hash_key("any_key")
        assert len(hash_val) == 64
        assert all(c in "0123456789abcdef" for c in hash_val)


class TestGenerateApiKey:
    """Tests for API key generation."""
    
    def test_generates_key_with_prefix(self):
        """Test that generated keys have the specified prefix."""
        key = generate_api_key(prefix="sk")
        assert key.startswith("sk_")
    
    def test_generates_unique_keys(self):
        """Test that each generated key is unique."""
        keys = [generate_api_key() for _ in range(10)]
        assert len(set(keys)) == 10  # All unique
    
    def test_key_is_long_enough(self):
        """Test that generated keys are sufficiently long."""
        key = generate_api_key()
        assert len(key) >= 40  # Prefix + underscore + random part


class TestLoadApiKeysFromEnv:
    """Tests for loading API keys from environment."""
    
    def setup_method(self):
        """Save original environment."""
        self.original_env = os.environ.copy()
    
    def teardown_method(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_loads_keys_with_prefix(self):
        """Test that keys with CORTEX_API_KEY_ prefix are loaded."""
        os.environ["CORTEX_AUTH_ENABLED"] = "true"
        os.environ["CORTEX_API_KEY_ALICE"] = "sk_alice_test"
        os.environ["CORTEX_API_KEY_BOB"] = "sk_bob_test"
        
        loaded = load_api_keys_from_env()
        
        assert loaded == 2
    
    def test_auth_enabled_detection(self):
        """Test that CORTEX_AUTH_ENABLED is respected."""
        os.environ["CORTEX_AUTH_ENABLED"] = "true"
        load_api_keys_from_env()
        assert is_auth_enabled()
        
        os.environ["CORTEX_AUTH_ENABLED"] = "false"
        load_api_keys_from_env()
        assert not is_auth_enabled()
    
    def test_ignores_non_key_vars(self):
        """Test that non-CORTEX_API_KEY_ vars are ignored."""
        os.environ["CORTEX_AUTH_ENABLED"] = "true"
        os.environ["CORTEX_API_KEY_ALICE"] = "sk_alice"
        os.environ["OTHER_VAR"] = "value"
        os.environ["CORTEX_OTHER"] = "other"
        
        loaded = load_api_keys_from_env()
        
        assert loaded == 1


class TestValidateApiKey:
    """Tests for API key validation."""
    
    def setup_method(self):
        """Set up test keys."""
        self.original_env = os.environ.copy()
        os.environ["CORTEX_AUTH_ENABLED"] = "true"
        os.environ["CORTEX_API_KEY_ALICE"] = "sk_alice_secret"
        os.environ["CORTEX_API_KEY_BOB"] = "sk_bob_secret"
        load_api_keys_from_env()
    
    def teardown_method(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_validates_correct_key(self):
        """Test that correct keys are validated."""
        user = validate_api_key("sk_alice_secret")
        
        assert user is not None
        assert user.user_id == "alice"
        assert user.is_authenticated
    
    def test_rejects_incorrect_key(self):
        """Test that incorrect keys are rejected."""
        user = validate_api_key("sk_wrong_key")
        
        assert user is None
    
    def test_rejects_empty_key(self):
        """Test that empty keys are rejected."""
        assert validate_api_key("") is None
        assert validate_api_key(None) is None
    
    def test_returns_user_context(self):
        """Test that valid key returns proper UserContext."""
        user = validate_api_key("sk_alice_secret")
        
        assert isinstance(user, UserContext)
        assert user.session_id  # Should have session ID
        assert user.metadata.get("auth_method") == "api_key"


class TestRegisterAndRevokeApiKey:
    """Tests for programmatic key registration and revocation."""
    
    def setup_method(self):
        """Set up clean state."""
        self.original_env = os.environ.copy()
        os.environ["CORTEX_AUTH_ENABLED"] = "true"
        load_api_keys_from_env()
    
    def teardown_method(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_register_api_key(self):
        """Test registering a new API key."""
        key = "sk_charlie_programmatic"
        
        info = register_api_key(
            api_key=key,
            user_id="charlie",
            username="Charlie Brown",
            roles=["developer"],
        )
        
        assert info.user_id == "charlie"
        assert info.username == "Charlie Brown"
        
        # Verify key works
        user = validate_api_key(key)
        assert user is not None
        assert user.user_id == "charlie"
    
    def test_revoke_api_key(self):
        """Test revoking an API key."""
        key = "sk_temp_key"
        register_api_key(key, "temp", "Temp User")
        
        # Verify key works
        assert validate_api_key(key) is not None
        
        # Revoke
        revoked = revoke_api_key(key)
        assert revoked is True
        
        # Verify key no longer works
        assert validate_api_key(key) is None
    
    def test_revoke_nonexistent_key(self):
        """Test revoking a key that doesn't exist."""
        revoked = revoke_api_key("sk_nonexistent")
        assert revoked is False


class TestGetRegisteredUsers:
    """Tests for getting registered users."""
    
    def setup_method(self):
        """Set up test keys."""
        self.original_env = os.environ.copy()
        os.environ["CORTEX_AUTH_ENABLED"] = "true"
        os.environ["CORTEX_API_KEY_ALICE"] = "sk_alice"
        os.environ["CORTEX_API_KEY_BOB"] = "sk_bob"
        load_api_keys_from_env()
    
    def teardown_method(self):
        """Restore original environment."""
        os.environ.clear()
        os.environ.update(self.original_env)
    
    def test_returns_user_ids(self):
        """Test that registered user IDs are returned."""
        users = get_registered_users()
        
        assert "alice" in users
        assert "bob" in users
