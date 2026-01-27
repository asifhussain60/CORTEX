"""
Tests for User Context Management (TEAM-001).

Phase: 5.5 (Team Collaboration Layer)
Author: Asif Hussain
Date: 2026-01-27
"""

import pytest
from datetime import datetime, timezone

from cortex.collaboration.user_context import (
    UserContext,
    get_current_user,
    set_current_user,
    clear_user_context,
    require_user_context,
    require_role,
)


class TestUserContext:
    """Tests for UserContext dataclass."""
    
    def test_create_user_context(self):
        """Test creating a basic user context."""
        user = UserContext(
            user_id="alice",
            username="Alice Smith",
            roles=["developer"],
        )
        
        assert user.user_id == "alice"
        assert user.username == "Alice Smith"
        assert user.roles == ["developer"]
        assert user.session_id  # Should have auto-generated session ID
        assert user.created_at  # Should have auto-generated timestamp
    
    def test_anonymous_user(self):
        """Test anonymous user factory."""
        anon = UserContext.anonymous()
        
        assert anon.user_id == "anonymous"
        assert anon.username == "Anonymous User"
        assert "readonly" in anon.roles
        assert not anon.is_authenticated
    
    def test_system_user(self):
        """Test system user factory."""
        system = UserContext.system()
        
        assert system.user_id == "system"
        assert system.is_system
        assert "admin" in system.roles
        assert "system" in system.roles
    
    def test_is_authenticated(self):
        """Test authentication status."""
        # Authenticated user
        user = UserContext(user_id="alice", username="Alice", roles=[])
        assert user.is_authenticated
        
        # Anonymous user
        anon = UserContext.anonymous()
        assert not anon.is_authenticated
    
    def test_has_role(self):
        """Test role checking."""
        user = UserContext(
            user_id="alice",
            username="Alice",
            roles=["developer", "reviewer"],
        )
        
        assert user.has_role("developer")
        assert user.has_role("reviewer")
        assert not user.has_role("admin")
    
    def test_has_any_role(self):
        """Test checking for any of multiple roles."""
        user = UserContext(
            user_id="alice",
            username="Alice",
            roles=["developer"],
        )
        
        assert user.has_any_role("developer", "admin")
        assert user.has_any_role("admin", "developer")
        assert not user.has_any_role("admin", "superuser")
    
    def test_to_dict(self):
        """Test serialization to dictionary."""
        user = UserContext(
            user_id="alice",
            username="Alice",
            roles=["developer"],
            metadata={"team": "platform"},
        )
        
        d = user.to_dict()
        
        assert d["user_id"] == "alice"
        assert d["username"] == "Alice"
        assert d["roles"] == ["developer"]
        assert d["is_authenticated"] is True
        assert d["metadata"] == {"team": "platform"}
        assert "session_id" in d
        assert "created_at" in d


class TestContextManagement:
    """Tests for context variable management."""
    
    def teardown_method(self):
        """Clear context after each test."""
        clear_user_context()
    
    def test_get_current_user_default(self):
        """Test getting current user when none set."""
        clear_user_context()
        user = get_current_user()
        
        # Should return anonymous
        assert user.user_id == "anonymous"
        assert not user.is_authenticated
    
    def test_set_and_get_current_user(self):
        """Test setting and getting user context."""
        alice = UserContext(
            user_id="alice",
            username="Alice",
            roles=["developer"],
        )
        
        set_current_user(alice)
        current = get_current_user()
        
        assert current.user_id == "alice"
        assert current.username == "Alice"
    
    def test_clear_user_context(self):
        """Test clearing user context."""
        alice = UserContext(
            user_id="alice",
            username="Alice",
            roles=["developer"],
        )
        
        set_current_user(alice)
        clear_user_context()
        
        current = get_current_user()
        assert current.user_id == "anonymous"


class TestRequireUserContext:
    """Tests for require_user_context decorator."""
    
    def teardown_method(self):
        """Clear context after each test."""
        clear_user_context()
    
    def test_allows_authenticated_user(self):
        """Test that authenticated users can call decorated functions."""
        @require_user_context
        def protected_function():
            return "secret data"
        
        alice = UserContext(user_id="alice", username="Alice", roles=[])
        set_current_user(alice)
        
        result = protected_function()
        assert result == "secret data"
    
    def test_blocks_anonymous_user(self):
        """Test that anonymous users are blocked."""
        @require_user_context
        def protected_function():
            return "secret data"
        
        clear_user_context()  # Ensure anonymous
        
        with pytest.raises(PermissionError) as exc_info:
            protected_function()
        
        assert "authentication required" in str(exc_info.value).lower()
    
    def test_preserves_function_metadata(self):
        """Test that decorator preserves function metadata."""
        @require_user_context
        def my_function():
            """My docstring."""
            pass
        
        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."


class TestRequireRole:
    """Tests for require_role decorator."""
    
    def teardown_method(self):
        """Clear context after each test."""
        clear_user_context()
    
    def test_allows_user_with_role(self):
        """Test that users with required role can access."""
        @require_role("admin")
        def admin_function():
            return "admin data"
        
        admin = UserContext(user_id="admin", username="Admin", roles=["admin"])
        set_current_user(admin)
        
        result = admin_function()
        assert result == "admin data"
    
    def test_allows_user_with_any_required_role(self):
        """Test that any of multiple roles grants access."""
        @require_role("admin", "superuser")
        def privileged_function():
            return "privileged data"
        
        user = UserContext(user_id="su", username="Super", roles=["superuser"])
        set_current_user(user)
        
        result = privileged_function()
        assert result == "privileged data"
    
    def test_blocks_user_without_role(self):
        """Test that users without required role are blocked."""
        @require_role("admin")
        def admin_function():
            return "admin data"
        
        user = UserContext(user_id="alice", username="Alice", roles=["developer"])
        set_current_user(user)
        
        with pytest.raises(PermissionError) as exc_info:
            admin_function()
        
        assert "admin" in str(exc_info.value).lower()
