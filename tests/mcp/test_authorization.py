"""
TDD Test Suite for ENH-063 P1-011: RBAC Authorization
AC-ENH063-P1-011-TEST-001

Tests for cortex/mcp/authorization.py

RED → GREEN → REFACTOR cycle
"""

import pytest
from cortex.mcp.authorization import (
    Action,
    AuthorizationManager,
    Permission,
    Resource,
    Role,
    RolePolicy,
    extract_roles_from_token,
    get_authorization_manager,
    require_permission,
    reset_authorization_manager,
)


# ============================================================================
# TEST FIXTURES
# ============================================================================


@pytest.fixture(autouse=True)
def reset_auth_manager():
    """Reset global authorization manager before each test"""
    reset_authorization_manager()
    yield
    reset_authorization_manager()


@pytest.fixture
def auth_manager():
    """Create fresh authorization manager"""
    return AuthorizationManager()


# ============================================================================
# TEST 1-3: Permission Model
# ============================================================================


def test_permission_creation():
    """Test creating permissions"""
    perm = Permission(Resource.ORCHESTRATOR, Action.EXECUTE)
    assert perm.resource == Resource.ORCHESTRATOR
    assert perm.action == Action.EXECUTE
    assert str(perm) == "orchestrator:execute"


def test_permission_from_string():
    """Test parsing permission from string"""
    perm = Permission.from_string("repository:write")
    assert perm.resource == Resource.REPOSITORY
    assert perm.action == Action.WRITE


def test_permission_hashable():
    """Test permissions are hashable (for use in sets)"""
    perm1 = Permission(Resource.ORCHESTRATOR, Action.READ)
    perm2 = Permission(Resource.ORCHESTRATOR, Action.READ)
    perm3 = Permission(Resource.ORCHESTRATOR, Action.WRITE)

    # Same permissions should be equal and have same hash
    assert perm1 == perm2
    assert hash(perm1) == hash(perm2)

    # Can be used in sets
    perm_set = {perm1, perm2, perm3}
    assert len(perm_set) == 2  # perm1 and perm2 are duplicates


# ============================================================================
# TEST 4-6: Role Policies
# ============================================================================


def test_role_policy_has_permission():
    """Test role policy permission checking"""
    policy = RolePolicy(role=Role.DEVELOPER)
    perm = Permission(Resource.ORCHESTRATOR, Action.READ)

    assert not policy.has_permission(perm)

    policy.add_permission(perm)
    assert policy.has_permission(perm)


def test_role_policy_add_remove_permission():
    """Test adding and removing permissions"""
    policy = RolePolicy(role=Role.DEVELOPER)
    perm = Permission(Resource.ORCHESTRATOR, Action.READ)

    policy.add_permission(perm)
    assert perm in policy.permissions

    policy.remove_permission(perm)
    assert perm not in policy.permissions


def test_default_policies():
    """Test default role policies are correctly defined"""
    manager = AuthorizationManager()

    # Admin should have all permissions
    admin_policy = manager.get_policy(Role.ADMIN)
    assert admin_policy is not None
    assert len(admin_policy.permissions) >= 10

    # Developer should have limited permissions
    dev_policy = manager.get_policy(Role.DEVELOPER)
    assert dev_policy is not None
    assert Permission(Resource.ORCHESTRATOR, Action.EXECUTE) in dev_policy.permissions
    assert Permission(Resource.SECRETS, Action.DELETE) not in dev_policy.permissions

    # Viewer should only have read permissions
    viewer_policy = manager.get_policy(Role.VIEWER)
    assert viewer_policy is not None
    assert Permission(Resource.ORCHESTRATOR, Action.READ) in viewer_policy.permissions
    assert Permission(Resource.ORCHESTRATOR, Action.WRITE) not in viewer_policy.permissions


# ============================================================================
# TEST 7-10: Authorization Manager
# ============================================================================


def test_authorization_manager_check_allowed(auth_manager):
    """Test authorization check when user is allowed"""
    result = auth_manager.check_authorization(
        user_id="user123",
        roles=[Role.ADMIN],
        resource=Resource.ORCHESTRATOR,
        action=Action.EXECUTE
    )

    assert result.allowed is True
    assert "admin" in result.reason.lower()
    assert result.context is not None
    assert result.context.user_id == "user123"


def test_authorization_manager_check_denied(auth_manager):
    """Test authorization check when user is denied"""
    result = auth_manager.check_authorization(
        user_id="user456",
        roles=[Role.VIEWER],
        resource=Resource.DEPLOYMENT,
        action=Action.EXECUTE
    )

    assert result.allowed is False
    assert "no role has permission" in result.reason.lower()
    assert result.context is not None


def test_authorization_manager_multiple_roles(auth_manager):
    """Test authorization with multiple roles"""
    # Viewer + Developer should have developer permissions
    result = auth_manager.check_authorization(
        user_id="user789",
        roles=[Role.VIEWER, Role.DEVELOPER],
        resource=Resource.ORCHESTRATOR,
        action=Action.EXECUTE
    )

    assert result.allowed is True


def test_authorization_manager_audit_log(auth_manager):
    """Test authorization audit logging"""
    # Perform some authorization checks
    auth_manager.check_authorization(
        user_id="user1",
        roles=[Role.ADMIN],
        resource=Resource.ORCHESTRATOR,
        action=Action.EXECUTE
    )

    auth_manager.check_authorization(
        user_id="user2",
        roles=[Role.VIEWER],
        resource=Resource.SECRETS,
        action=Action.WRITE
    )

    # Check audit log
    log = auth_manager.get_audit_log()
    assert len(log) == 2

    assert log[0]["user_id"] == "user1"
    assert log[0]["allowed"] is True

    assert log[1]["user_id"] == "user2"
    assert log[1]["allowed"] is False


# ============================================================================
# TEST 11-13: Policy Management
# ============================================================================


def test_add_custom_policy(auth_manager):
    """Test adding custom role policy"""
    custom_role = Role.DEVELOPER
    custom_policy = RolePolicy(
        role=custom_role,
        permissions={
            Permission(Resource.ORCHESTRATOR, Action.READ),
            Permission(Resource.ORCHESTRATOR, Action.EXECUTE),
        }
    )

    auth_manager.add_policy(custom_policy)

    retrieved_policy = auth_manager.get_policy(custom_role)
    assert retrieved_policy == custom_policy


def test_remove_policy(auth_manager):
    """Test removing role policy"""
    auth_manager.remove_policy(Role.VIEWER)

    assert auth_manager.get_policy(Role.VIEWER) is None


def test_get_permissions(auth_manager):
    """Test getting all permissions for a role"""
    permissions = auth_manager.get_permissions(Role.ADMIN)

    assert isinstance(permissions, set)
    assert len(permissions) > 0
    assert Permission(Resource.ORCHESTRATOR, Action.EXECUTE) in permissions


# ============================================================================
# TEST 14-16: Decorator Enforcement
# ============================================================================


def test_require_permission_decorator_allowed():
    """Test decorator allows authorized calls"""
    @require_permission(Resource.ORCHESTRATOR, Action.READ)
    def test_func(user_id: str, roles: list) -> str:
        return "success"

    result = test_func(user_id="user123", roles=[Role.ADMIN])
    assert result == "success"


def test_require_permission_decorator_denied():
    """Test decorator denies unauthorized calls"""
    @require_permission(Resource.SECRETS, Action.DELETE)
    def test_func(user_id: str, roles: list) -> str:
        return "success"

    with pytest.raises(PermissionError) as exc_info:
        test_func(user_id="user456", roles=[Role.VIEWER])

    assert "access denied" in str(exc_info.value).lower()


def test_require_permission_decorator_missing_user_id():
    """Test decorator requires user_id"""
    @require_permission(Resource.ORCHESTRATOR, Action.READ)
    def test_func(user_id: str, roles: list) -> str:
        return "success"

    with pytest.raises(ValueError) as exc_info:
        test_func(user_id=None, roles=[Role.ADMIN])

    assert "user_id required" in str(exc_info.value).lower()


# ============================================================================
# TEST 17-19: Global Instance
# ============================================================================


def test_get_authorization_manager_singleton():
    """Test global authorization manager singleton"""
    manager1 = get_authorization_manager()
    manager2 = get_authorization_manager()

    assert manager1 is manager2


def test_reset_authorization_manager_clears_instance():
    """Test resetting global instance"""
    manager1 = get_authorization_manager()
    reset_authorization_manager()
    manager2 = get_authorization_manager()

    assert manager1 is not manager2


def test_global_manager_state_persists():
    """Test global manager maintains state"""
    manager = get_authorization_manager()

    # Perform authorization
    manager.check_authorization(
        user_id="user1",
        roles=[Role.ADMIN],
        resource=Resource.ORCHESTRATOR,
        action=Action.EXECUTE
    )

    # Get same instance
    manager2 = get_authorization_manager()
    audit_log = manager2.get_audit_log()

    assert len(audit_log) == 1
    assert audit_log[0]["user_id"] == "user1"


# ============================================================================
# TEST 20-22: Token Integration
# ============================================================================


def test_extract_roles_from_token():
    """Test extracting roles from JWT token payload"""
    token_payload = {
        "user_id": "user123",
        "roles": ["developer", "viewer"],
        "scopes": ["orchestrator:execute"]
    }

    roles = extract_roles_from_token(token_payload)

    assert len(roles) == 2
    assert Role.DEVELOPER in roles
    assert Role.VIEWER in roles


def test_extract_roles_default_to_viewer():
    """Test default role when none provided"""
    token_payload = {"user_id": "user123"}

    roles = extract_roles_from_token(token_payload)

    assert roles == [Role.VIEWER]


def test_extract_roles_invalid_role():
    """Test handling invalid role in token"""
    token_payload = {
        "user_id": "user123",
        "roles": ["developer", "invalid_role"]
    }

    roles = extract_roles_from_token(token_payload)

    # Should only include valid roles
    assert Role.DEVELOPER in roles
    assert len(roles) == 1


# ============================================================================
# TEST 23-25: Edge Cases
# ============================================================================


def test_authorization_with_metadata(auth_manager):
    """Test authorization with additional metadata"""
    result = auth_manager.check_authorization(
        user_id="user123",
        roles=[Role.ADMIN],
        resource=Resource.ORCHESTRATOR,
        action=Action.EXECUTE,
        metadata={"request_id": "req-123", "ip": "192.168.1.1"}
    )

    assert result.allowed is True
    assert result.context.metadata["request_id"] == "req-123"


def test_authorization_empty_roles(auth_manager):
    """Test authorization with no roles"""
    result = auth_manager.check_authorization(
        user_id="user123",
        roles=[],
        resource=Resource.ORCHESTRATOR,
        action=Action.EXECUTE
    )

    assert result.allowed is False


def test_audit_log_limit(auth_manager):
    """Test audit log respects limit parameter"""
    # Generate 150 authorization checks
    for i in range(150):
        auth_manager.check_authorization(
            user_id=f"user{i}",
            roles=[Role.VIEWER],
            resource=Resource.ORCHESTRATOR,
            action=Action.READ
        )

    # Get last 50 entries
    log = auth_manager.get_audit_log(limit=50)
    assert len(log) == 50
    assert log[-1]["user_id"] == "user149"
