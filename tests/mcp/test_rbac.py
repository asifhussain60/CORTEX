# AC_START: AC-WAVEB-005
# Description: Tests for RBAC authorization layer (ENH-063 Phase 4)
# Wave: B, Phase: 4, Part: 2
# TDD Cycle: RED→GREEN→REFACTOR

"""
Test Suite: RBAC Authorization

Tests:
1. test_admin_full_access - Admin has full permissions
2. test_user_limited_access - User has limited permissions
3. test_readonly_no_execute - Readonly cannot execute
4. test_role_hierarchy - Role hierarchy (ADMIN > USER > READONLY)
5. test_resource_permissions - Resource-specific permissions
6. test_action_permissions - Action-specific permissions
7. test_resource_id_filtering - Specific resource ID permissions
8. test_authorization_context - Context creation
9. test_policy_management - Add/remove permissions
10. test_performance - Authorization <5ms

Authority: ENH-063 Phase 4
Governance: CORE-008 (TDD-first)
"""

import time

import pytest

from cortex.mcp.rbac import (
    Action,
    AuthorizationContext,
    Permission,
    RBACPolicy,
    Resource,
    Role,
    authorize,
    get_policy,
)


class TestRBACAuthorization:
    """Test RBAC authorization layer."""

    def test_admin_full_access(self):
        """Test admin has full access to all resources."""
        policy = RBACPolicy()

        # Test tool execution
        context = AuthorizationContext(
            user_id="admin1",
            role=Role.ADMIN,
            resource=Resource.TOOL,
            action=Action.EXECUTE,
        )
        result = policy.authorize(context)
        assert result.allowed
        assert "Allowed" in result.reason

        # Test governance admin
        context = AuthorizationContext(
            user_id="admin1",
            role=Role.ADMIN,
            resource=Resource.GOVERNANCE,
            action=Action.ADMIN,
        )
        result = policy.authorize(context)
        assert result.allowed

    def test_user_limited_access(self):
        """Test user has limited permissions."""
        policy = RBACPolicy()

        # User CAN execute tools
        context = AuthorizationContext(
            user_id="user1",
            role=Role.USER,
            resource=Resource.TOOL,
            action=Action.EXECUTE,
        )
        result = policy.authorize(context)
        assert result.allowed

        # User CANNOT admin governance
        context = AuthorizationContext(
            user_id="user1",
            role=Role.USER,
            resource=Resource.GOVERNANCE,
            action=Action.ADMIN,
        )
        result = policy.authorize(context)
        assert not result.allowed
        assert "No permission" in result.reason

    def test_readonly_no_execute(self):
        """Test readonly cannot execute, only read."""
        policy = RBACPolicy()

        # Readonly CANNOT execute tools
        context = AuthorizationContext(
            user_id="readonly1",
            role=Role.READONLY,
            resource=Resource.TOOL,
            action=Action.EXECUTE,
        )
        result = policy.authorize(context)
        assert not result.allowed

        # Readonly CAN read tools
        context = AuthorizationContext(
            user_id="readonly1",
            role=Role.READONLY,
            resource=Resource.TOOL,
            action=Action.READ,
        )
        result = policy.authorize(context)
        assert result.allowed

    def test_role_hierarchy(self):
        """Test role hierarchy (ADMIN > USER > READONLY)."""
        policy = RBACPolicy()

        # Add permission for USER role
        policy.add_permission(
            Permission(
                role=Role.USER,
                resource=Resource.SYSTEM,
                action=Action.READ,
            )
        )

        # ADMIN should inherit USER permissions
        context = AuthorizationContext(
            user_id="admin1",
            role=Role.ADMIN,
            resource=Resource.SYSTEM,
            action=Action.READ,
        )
        result = policy.authorize(context)
        assert result.allowed

        # USER should have permission
        context = AuthorizationContext(
            user_id="user1",
            role=Role.USER,
            resource=Resource.SYSTEM,
            action=Action.READ,
        )
        result = policy.authorize(context)
        assert result.allowed

        # READONLY should NOT inherit USER permissions
        context = AuthorizationContext(
            user_id="readonly1",
            role=Role.READONLY,
            resource=Resource.SYSTEM,
            action=Action.READ,
        )
        result = policy.authorize(context)
        assert not result.allowed

    def test_resource_permissions(self):
        """Test resource-specific permissions."""
        policy = RBACPolicy()

        # USER can execute TOOL
        context = AuthorizationContext(
            user_id="user1",
            role=Role.USER,
            resource=Resource.TOOL,
            action=Action.EXECUTE,
        )
        result = policy.authorize(context)
        assert result.allowed

        # USER cannot execute ORCHESTRATOR (only read)
        context = AuthorizationContext(
            user_id="user1",
            role=Role.USER,
            resource=Resource.ORCHESTRATOR,
            action=Action.EXECUTE,
        )
        result = policy.authorize(context)
        assert not result.allowed

    def test_action_permissions(self):
        """Test action-specific permissions."""
        policy = RBACPolicy()

        # USER can READ orchestrator
        context = AuthorizationContext(
            user_id="user1",
            role=Role.USER,
            resource=Resource.ORCHESTRATOR,
            action=Action.READ,
        )
        result = policy.authorize(context)
        assert result.allowed

        # USER cannot ADMIN orchestrator
        context = AuthorizationContext(
            user_id="user1",
            role=Role.USER,
            resource=Resource.ORCHESTRATOR,
            action=Action.ADMIN,
        )
        result = policy.authorize(context)
        assert not result.allowed

    def test_resource_id_filtering(self):
        """Test specific resource ID permissions."""
        policy = RBACPolicy()

        # Add permission for specific tool IDs
        policy.add_permission(
            Permission(
                role=Role.USER,
                resource=Resource.TOOL,
                action=Action.ADMIN,
                resource_ids={"tool1", "tool2"},
            )
        )

        # USER can admin tool1
        context = AuthorizationContext(
            user_id="user1",
            role=Role.USER,
            resource=Resource.TOOL,
            action=Action.ADMIN,
            resource_id="tool1",
        )
        result = policy.authorize(context)
        assert result.allowed

        # USER cannot admin tool3
        context = AuthorizationContext(
            user_id="user1",
            role=Role.USER,
            resource=Resource.TOOL,
            action=Action.ADMIN,
            resource_id="tool3",
        )
        result = policy.authorize(context)
        assert not result.allowed

    def test_authorization_context(self):
        """Test authorization context creation."""
        context = AuthorizationContext(
            user_id="user123",
            role=Role.USER,
            resource=Resource.TOOL,
            action=Action.EXECUTE,
            resource_id="cortex_lens_analyze",
            metadata={"ip": "192.168.1.1", "session": "abc123"},
        )

        assert context.user_id == "user123"
        assert context.role == Role.USER
        assert context.resource == Resource.TOOL
        assert context.action == Action.EXECUTE
        assert context.resource_id == "cortex_lens_analyze"
        assert context.metadata["ip"] == "192.168.1.1"

    def test_policy_management(self):
        """Test add/remove permissions."""
        policy = RBACPolicy()

        initial_count = len(policy.permissions)

        # Add custom permission
        custom_perm = Permission(
            role=Role.USER,
            resource=Resource.AUDIT,
            action=Action.READ,
        )
        policy.add_permission(custom_perm)

        assert len(policy.permissions) == initial_count + 1

        # Remove permission
        policy.remove_permission(custom_perm)
        assert len(policy.permissions) == initial_count

    def test_get_permissions_for_role(self):
        """Test querying permissions by role."""
        policy = RBACPolicy()

        admin_perms = policy.get_permissions_for_role(Role.ADMIN)
        user_perms = policy.get_permissions_for_role(Role.USER)
        readonly_perms = policy.get_permissions_for_role(Role.READONLY)

        # ADMIN should have most permissions
        assert len(admin_perms) > len(user_perms)
        assert len(user_perms) > len(readonly_perms)

    def test_performance(self):
        """Test authorization check is <5ms."""
        policy = RBACPolicy()

        context = AuthorizationContext(
            user_id="user1",
            role=Role.USER,
            resource=Resource.TOOL,
            action=Action.EXECUTE,
        )

        # Warmup
        for _ in range(10):
            policy.authorize(context)

        # Measure
        start = time.perf_counter()
        iterations = 1000
        for _ in range(iterations):
            policy.authorize(context)
        elapsed = time.perf_counter() - start

        avg_time_ms = (elapsed / iterations) * 1000

        # Verify <5ms per authorization check
        assert avg_time_ms < 5.0, f"Authorization too slow: {avg_time_ms:.3f}ms"

    def test_global_policy(self):
        """Test global policy singleton."""
        policy1 = get_policy()
        policy2 = get_policy()

        # Should return same instance
        assert policy1 is policy2

    def test_authorize_function(self):
        """Test convenience authorize() function."""
        context = AuthorizationContext(
            user_id="user1",
            role=Role.USER,
            resource=Resource.TOOL,
            action=Action.EXECUTE,
        )

        result = authorize(context)
        assert result.allowed


# AC_COMPLETE: AC-WAVEB-005 ✅ 13 RBAC tests complete
