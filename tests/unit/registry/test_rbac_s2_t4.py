"""
Tests for Phase 76 S2 Task 4 - Role-Based Access Control

Authority: Phase 76 S2 Task 4 - Registry Isolation & Multi-Tenant Foundation
AC-ID: AC-PHASE76-S2-T4-001

Test Coverage:
- Role-based access control
- Permission management
- Permission enforcement
- Audit logging
- Multi-tenant access isolation
"""

import pytest
from datetime import datetime

from cortex.registry.registry_access_control import (
    RoleBasedAccessControl,
    Role,
    Permission,
    AccessDeniedException,
    PermissionPolicy,
)
from cortex.registry.tenant_context import TenantContext


class TestRoleAssignment:
    """Test role assignment and management."""
    
    def test_assign_role_to_user(self):
        """AC-PHASE76-S2-T4-001: Assign role to user."""
        rbac = RoleBasedAccessControl()
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        roles = rbac.get_user_roles("alice@acme.com")
        
        assert Role.EDITOR in roles
    
    def test_assign_multiple_roles(self):
        """Assign multiple roles to user."""
        rbac = RoleBasedAccessControl()
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        rbac.assign_role("alice@acme.com", Role.MAINTAINER)
        roles = rbac.get_user_roles("alice@acme.com")
        
        assert Role.EDITOR in roles
        assert Role.MAINTAINER in roles
    
    def test_revoke_role(self):
        """Revoke role from user."""
        rbac = RoleBasedAccessControl()
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        rbac.revoke_role("alice@acme.com", Role.EDITOR)
        roles = rbac.get_user_roles("alice@acme.com")
        
        assert Role.EDITOR not in roles
    
    def test_get_unassigned_user_roles(self):
        """Get roles for unassigned user returns empty."""
        rbac = RoleBasedAccessControl()
        
        roles = rbac.get_user_roles("unknown@acme.com")
        
        assert roles == set()


class TestPermissionChecks:
    """Test permission checking."""
    
    def test_viewer_has_read_permission(self):
        """Viewer role has read permission."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["viewer"])
        
        rbac.assign_role("alice@acme.com", Role.VIEWER)
        can_read = rbac.has_permission(ctx, Permission.READ)
        
        assert can_read is True
    
    def test_viewer_lacks_write_permission(self):
        """Viewer role lacks write permission."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["viewer"])
        
        rbac.assign_role("alice@acme.com", Role.VIEWER)
        can_write = rbac.has_permission(ctx, Permission.CREATE)
        
        assert can_write is False
    
    def test_editor_has_read_and_write(self):
        """Editor has both read and write permissions."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["editor"])
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        
        assert rbac.has_permission(ctx, Permission.READ) is True
        assert rbac.has_permission(ctx, Permission.CREATE) is True
        assert rbac.has_permission(ctx, Permission.UPDATE) is True
    
    def test_editor_lacks_delete_permission(self):
        """Editor cannot delete."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["editor"])
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        can_delete = rbac.has_permission(ctx, Permission.DELETE)
        
        assert can_delete is False
    
    def test_maintainer_has_delete_permission(self):
        """Maintainer can delete."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["maintainer"])
        
        rbac.assign_role("alice@acme.com", Role.MAINTAINER)
        can_delete = rbac.has_permission(ctx, Permission.DELETE)
        
        assert can_delete is True
    
    def test_admin_has_all_permissions(self):
        """Admin role has all permissions."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["admin"])
        
        rbac.assign_role("alice@acme.com", Role.ADMIN)
        
        all_permissions = [
            Permission.READ,
            Permission.CREATE,
            Permission.DELETE,
            Permission.SEAL_ARTIFACT,
            Permission.MANAGE_PERMISSIONS,
        ]
        
        for permission in all_permissions:
            assert rbac.has_permission(ctx, permission) is True
    
    def test_permission_check_requires_role(self):
        """Permission check returns False if user has no roles."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", [])
        
        # Don't assign any role
        can_read = rbac.has_permission(ctx, Permission.READ)
        
        assert can_read is False


class TestPermissionEnforcement:
    """Test permission enforcement with exceptions."""
    
    def test_require_permission_allowed(self):
        """Require permission succeeds for allowed permission."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["editor"])
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        
        # Should not raise
        rbac.require_permission(ctx, Permission.READ)
    
    def test_require_permission_denied(self):
        """Require permission raises for denied permission."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["viewer"])
        
        rbac.assign_role("alice@acme.com", Role.VIEWER)
        
        with pytest.raises(AccessDeniedException):
            rbac.require_permission(ctx, Permission.DELETE)
    
    def test_require_permission_with_resource(self):
        """Require permission with specific resource."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["editor"])
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        
        # Should not raise
        rbac.require_permission(ctx, Permission.READ, resource="phase-42")


class TestPermissionPolicies:
    """Test permission policy definitions."""
    
    def test_get_permission_policy(self):
        """Get permission policy for role."""
        rbac = RoleBasedAccessControl()
        
        policy = rbac.get_permission_policy(Role.VIEWER)
        
        assert policy is not None
        assert policy.role == Role.VIEWER
        assert Permission.READ in policy.permissions
    
    def test_list_permissions_for_role(self):
        """List all permissions for role."""
        rbac = RoleBasedAccessControl()
        
        permissions = rbac.list_permissions(Role.EDITOR)
        
        assert "read" in permissions
        assert "create" in permissions
        assert "update" in permissions
    
    def test_policy_to_dict(self):
        """Policy serializable to dict."""
        rbac = RoleBasedAccessControl()
        policy = rbac.get_permission_policy(Role.VIEWER)
        
        assert policy is not None
        policy_dict = policy.to_dict()
        
        assert policy_dict["role"] == "viewer"
        assert "read" in policy_dict["permissions"]


class TestAuditLogging:
    """Test audit logging of access events."""
    
    def test_audit_log_on_permission_granted(self):
        """Audit log records permission grant."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["editor"])
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        rbac.require_permission(ctx, Permission.READ)
        
        audit_log = rbac.get_audit_log(user_id="alice@acme.com")
        
        # Should have entries for role assignment and permission grant
        assert len(audit_log) >= 2
    
    def test_audit_log_on_permission_denied(self):
        """Audit log records permission denial."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["viewer"])
        
        rbac.assign_role("alice@acme.com", Role.VIEWER)
        
        try:
            rbac.require_permission(ctx, Permission.DELETE)
        except AccessDeniedException:
            pass
        
        audit_log = rbac.get_audit_log(user_id="alice@acme.com", event_type="permission_denied")
        
        assert len(audit_log) >= 1
    
    def test_audit_log_on_role_revoked(self):
        """Audit log records role revocation."""
        rbac = RoleBasedAccessControl()
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        rbac.revoke_role("alice@acme.com", Role.EDITOR)
        
        audit_log = rbac.get_audit_log(user_id="alice@acme.com")
        
        # Should have entries for both assign and revoke
        events = [e["event"] for e in audit_log]
        assert "role_assigned" in events
        assert "role_revoked" in events
    
    def test_filter_audit_log_by_event_type(self):
        """Filter audit log by event type."""
        rbac = RoleBasedAccessControl()
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        rbac.assign_role("bob@acme.com", Role.VIEWER)
        
        audit_log = rbac.get_audit_log(event_type="role_assigned")
        
        assert all(e["event"] == "role_assigned" for e in audit_log)
        assert len(audit_log) == 2


class TestMultiTenantAccess:
    """Test multi-tenant access isolation."""
    
    def test_different_tenants_isolated_permissions(self):
        """Different tenants have separate permission contexts."""
        rbac = RoleBasedAccessControl()
        
        ctx1 = TenantContext("ws1", "alice@acme.com", ["editor"])
        ctx2 = TenantContext("ws2", "bob@beta.com", ["viewer"])
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        rbac.assign_role("bob@beta.com", Role.VIEWER)
        
        # Alice can create, Bob cannot
        assert rbac.has_permission(ctx1, Permission.CREATE) is True
        assert rbac.has_permission(ctx2, Permission.CREATE) is False
    
    def test_tenant_context_in_audit_log(self):
        """Audit log includes tenant context."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["editor"])
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        rbac.require_permission(ctx, Permission.READ)
        
        audit_log = rbac.get_audit_log(user_id="alice@acme.com")
        
        # Check for tenant_id in audit entries
        assert all("tenant_id" in entry for entry in audit_log)


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_assign_admin_role(self):
        """Assign admin role grants all permissions."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["admin"])
        
        rbac.assign_role("alice@acme.com", Role.ADMIN)
        
        assert rbac.has_permission(ctx, Permission.MANAGE_TENANTS) is True
        assert rbac.has_permission(ctx, Permission.DELETE) is True
        assert rbac.has_permission(ctx, Permission.READ) is True
    
    def test_multiple_roles_combined_permissions(self):
        """Multiple roles combine permissions."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["editor", "maintainer"])
        
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        rbac.assign_role("alice@acme.com", Role.MAINTAINER)
        
        # Has editor permissions (CREATE)
        assert rbac.has_permission(ctx, Permission.CREATE) is True
        # Has maintainer permissions (MANAGE_PERMISSIONS)
        assert rbac.has_permission(ctx, Permission.MANAGE_PERMISSIONS) is True
    
    def test_require_permission_logs_denied_event(self):
        """require_permission logs event even on deny."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["viewer"])
        
        rbac.assign_role("alice@acme.com", Role.VIEWER)
        
        try:
            rbac.require_permission(ctx, Permission.DELETE, resource="phase-42")
        except AccessDeniedException:
            pass
        
        audit_log = rbac.get_audit_log(user_id="alice@acme.com")
        
        # Should have role_assigned + permission_denied events
        assert len(audit_log) >= 2
    
    def test_permission_enum_values(self):
        """Permission enum has expected values."""
        assert Permission.READ.value == "read"
        assert Permission.CREATE.value == "create"
        assert Permission.ADMIN.value == "admin"
    
    def test_role_enum_values(self):
        """Role enum has expected values."""
        assert Role.VIEWER.value == "viewer"
        assert Role.EDITOR.value == "editor"
        assert Role.ADMIN.value == "admin"
