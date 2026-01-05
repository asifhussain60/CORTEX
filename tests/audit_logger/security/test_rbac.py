"""
Task 4.3: RBAC Manager Tests (TDD RED Phase)

Role-based access control for audit logs with:
- 4 roles: admin, developer, auditor, read-only
- Granular permission matrix
- Complete audit trail logging
- Integration with security components

Author: Asif Hussain
Date: January 5, 2026
Status: RED (Tests failing - implementation pending)
"""

import pytest
from datetime import datetime
from typing import Dict, List, Any

# Import will fail initially (RED phase)
from src.audit_logger.security.rbac import (
    RBACManager,
    User,
    Permission,
    Resource,
    PermissionDeniedError,
    InvalidRoleError,
    ROLE_PERMISSIONS
)


class TestRBACManager:
    """Test suite for RBAC Manager"""
    
    @pytest.fixture
    def rbac(self) -> RBACManager:
        """Create RBAC Manager instance"""
        return RBACManager()
    
    # ========== User Creation Tests ==========
    
    def test_create_user_with_valid_role(self, rbac: RBACManager):
        """Test creating user with valid role"""
        user = rbac.create_user('user-123', 'developer')
        
        assert user.user_id == 'user-123'
        assert user.role == 'developer'
        assert user.level == 3
        assert isinstance(user.created_at, datetime)
    
    def test_create_user_with_invalid_role(self, rbac: RBACManager):
        """Test creating user with invalid role raises error"""
        with pytest.raises(InvalidRoleError):
            rbac.create_user('user-123', 'invalid_role')
    
    def test_user_has_permissions_property(self, rbac: RBACManager):
        """Test user has permissions property"""
        user = rbac.create_user('dev-1', 'developer')
        
        permissions = user.permissions
        assert isinstance(permissions, list)
        assert len(permissions) > 0
        assert Permission.CREATE_LOG in permissions
    
    # ========== Permission Matrix Tests ==========
    
    def test_admin_has_all_permissions(self, rbac: RBACManager):
        """Test admin role has all 12 permissions"""
        admin = rbac.create_user('admin-1', 'admin')
        
        all_permissions = [
            Permission.CREATE_LOG,
            Permission.READ_OWN_LOG,
            Permission.READ_ALL_LOGS,
            Permission.UPDATE_LOG,
            Permission.DELETE_LOG,
            Permission.ENCRYPT_LOG,
            Permission.DECRYPT_LOG,
            Permission.ROTATE_KEYS,
            Permission.ASSIGN_ROLE,
            Permission.VIEW_AUDIT_TRAIL,
            Permission.EXPORT_LOGS,
            Permission.SANITIZE_PII
        ]
        
        for permission in all_permissions:
            assert admin.has_permission(permission), f"Admin missing {permission}"
    
    def test_developer_permissions(self, rbac: RBACManager):
        """Test developer has correct permissions"""
        dev = rbac.create_user('dev-1', 'developer')
        
        # Has permissions
        assert dev.has_permission(Permission.CREATE_LOG)
        assert dev.has_permission(Permission.READ_OWN_LOG)
        assert dev.has_permission(Permission.UPDATE_LOG)
        assert dev.has_permission(Permission.ENCRYPT_LOG)
        assert dev.has_permission(Permission.DECRYPT_LOG)
        assert dev.has_permission(Permission.SANITIZE_PII)
        
        # Lacks permissions
        assert not dev.has_permission(Permission.READ_ALL_LOGS)
        assert not dev.has_permission(Permission.DELETE_LOG)
        assert not dev.has_permission(Permission.ROTATE_KEYS)
        assert not dev.has_permission(Permission.ASSIGN_ROLE)
    
    def test_auditor_permissions(self, rbac: RBACManager):
        """Test auditor has correct permissions"""
        auditor = rbac.create_user('auditor-1', 'auditor')
        
        # Has permissions
        assert auditor.has_permission(Permission.READ_ALL_LOGS)
        assert auditor.has_permission(Permission.DECRYPT_LOG)
        assert auditor.has_permission(Permission.VIEW_AUDIT_TRAIL)
        assert auditor.has_permission(Permission.EXPORT_LOGS)
        
        # Lacks permissions
        assert not auditor.has_permission(Permission.CREATE_LOG)
        assert not auditor.has_permission(Permission.UPDATE_LOG)
        assert not auditor.has_permission(Permission.DELETE_LOG)
        assert not auditor.has_permission(Permission.ROTATE_KEYS)
    
    def test_read_only_permissions(self, rbac: RBACManager):
        """Test read-only has minimal permissions"""
        viewer = rbac.create_user('viewer-1', 'read_only')
        
        # Has permission
        assert viewer.has_permission(Permission.READ_ALL_LOGS)
        
        # Lacks all other permissions
        assert not viewer.has_permission(Permission.CREATE_LOG)
        assert not viewer.has_permission(Permission.DECRYPT_LOG)
        assert not viewer.has_permission(Permission.UPDATE_LOG)
        assert not viewer.has_permission(Permission.VIEW_AUDIT_TRAIL)
    
    # ========== Permission Check Tests ==========
    
    def test_check_permission_returns_bool(self, rbac: RBACManager):
        """Test check_permission returns boolean"""
        dev = rbac.create_user('dev-1', 'developer')
        
        result = rbac.check_permission(dev, Permission.CREATE_LOG)
        assert result is True
        
        result = rbac.check_permission(dev, Permission.DELETE_LOG)
        assert result is False
    
    def test_check_permission_with_enforce_raises(self, rbac: RBACManager):
        """Test check_permission with enforce=True raises error"""
        dev = rbac.create_user('dev-1', 'developer')
        
        # Should not raise
        rbac.check_permission(dev, Permission.CREATE_LOG, enforce=True)
        
        # Should raise
        with pytest.raises(PermissionDeniedError) as exc_info:
            rbac.check_permission(dev, Permission.DELETE_LOG, enforce=True)
        
        assert 'delete_log' in str(exc_info.value)
    
    def test_has_permission_by_user_id(self, rbac: RBACManager):
        """Test has_permission quick check by user ID"""
        rbac.create_user('dev-1', 'developer')
        
        assert rbac.has_permission('dev-1', Permission.CREATE_LOG)
        assert not rbac.has_permission('dev-1', Permission.DELETE_LOG)
    
    def test_get_user_permissions(self, rbac: RBACManager):
        """Test getting all permissions for user"""
        rbac.create_user('dev-1', 'developer')
        
        permissions = rbac.get_user_permissions('dev-1')
        
        assert isinstance(permissions, list)
        assert Permission.CREATE_LOG in permissions
        assert Permission.DELETE_LOG not in permissions
    
    # ========== Resource Ownership Tests ==========
    
    def test_developer_can_access_own_resource(self, rbac: RBACManager):
        """Test developer can access resources they created"""
        dev = rbac.create_user('dev-1', 'developer')
        resource = Resource(id='log-123', created_by='dev-1')
        
        can_access = rbac.check_permission(
            dev, Permission.READ_OWN_LOG, resource=resource
        )
        assert can_access is True
    
    def test_developer_cannot_access_others_resource(self, rbac: RBACManager):
        """Test developer cannot access others' resources"""
        dev = rbac.create_user('dev-1', 'developer')
        resource = Resource(id='log-456', created_by='dev-2')
        
        can_access = rbac.check_permission(
            dev, Permission.UPDATE_LOG, resource=resource
        )
        assert can_access is False
    
    def test_admin_can_access_any_resource(self, rbac: RBACManager):
        """Test admin can access all resources regardless of ownership"""
        admin = rbac.create_user('admin-1', 'admin')
        resource = Resource(id='log-789', created_by='other-user')
        
        can_access = rbac.check_permission(
            admin, Permission.UPDATE_LOG, resource=resource
        )
        assert can_access is True
    
    # ========== Role Assignment Tests ==========
    
    def test_admin_can_assign_roles(self, rbac: RBACManager):
        """Test admin can assign roles to users"""
        admin = rbac.create_user('admin-1', 'admin')
        
        success = rbac.assign_role('user-123', 'auditor', by_user=admin)
        assert success is True
        
        # Verify role was assigned
        user = rbac.get_user('user-123')
        assert user.role == 'auditor'
    
    def test_non_admin_cannot_assign_roles(self, rbac: RBACManager):
        """Test non-admin cannot assign roles"""
        dev = rbac.create_user('dev-1', 'developer')
        
        with pytest.raises(PermissionDeniedError):
            rbac.assign_role('user-456', 'admin', by_user=dev)
    
    def test_cannot_assign_invalid_role(self, rbac: RBACManager):
        """Test cannot assign invalid role"""
        admin = rbac.create_user('admin-1', 'admin')
        
        with pytest.raises(InvalidRoleError):
            rbac.assign_role('user-789', 'invalid_role', by_user=admin)
    
    # ========== Audit Trail Tests ==========
    
    def test_successful_access_logged(self, rbac: RBACManager):
        """Test successful access is logged to audit trail"""
        dev = rbac.create_user('dev-1', 'developer')
        
        rbac.check_permission(dev, Permission.CREATE_LOG)
        
        audit_trail = rbac.get_audit_trail(user_id='dev-1')
        assert len(audit_trail) > 0
        
        entry = audit_trail[-1]
        assert entry['user_id'] == 'dev-1'
        assert entry['operation'] == 'create_log'
        assert entry['result'] == 'success'
    
    def test_denied_access_logged(self, rbac: RBACManager):
        """Test denied access is logged to audit trail"""
        dev = rbac.create_user('dev-1', 'developer')
        
        try:
            rbac.check_permission(dev, Permission.DELETE_LOG, enforce=True)
        except PermissionDeniedError:
            pass
        
        audit_trail = rbac.get_audit_trail(user_id='dev-1')
        assert len(audit_trail) > 0
        
        entry = audit_trail[-1]
        assert entry['user_id'] == 'dev-1'
        assert entry['operation'] == 'delete_log'
        assert entry['result'] == 'denied'
        assert 'reason' in entry['metadata']
    
    def test_audit_trail_includes_metadata(self, rbac: RBACManager):
        """Test audit trail includes metadata"""
        dev = rbac.create_user('dev-1', 'developer')
        resource = Resource(id='log-123', created_by='dev-1')
        
        rbac.check_permission(
            dev, Permission.READ_OWN_LOG, resource=resource,
            metadata={'ip': '192.168.1.100'}
        )
        
        audit_trail = rbac.get_audit_trail(user_id='dev-1')
        entry = audit_trail[-1]
        
        assert 'metadata' in entry
        assert entry['metadata']['ip'] == '192.168.1.100'
    
    def test_get_audit_trail_filtered_by_user(self, rbac: RBACManager):
        """Test getting audit trail filtered by user"""
        dev1 = rbac.create_user('dev-1', 'developer')
        dev2 = rbac.create_user('dev-2', 'developer')
        
        rbac.check_permission(dev1, Permission.CREATE_LOG)
        rbac.check_permission(dev2, Permission.CREATE_LOG)
        
        trail_dev1 = rbac.get_audit_trail(user_id='dev-1')
        assert all(entry['user_id'] == 'dev-1' for entry in trail_dev1)
    
    def test_get_full_audit_trail(self, rbac: RBACManager):
        """Test getting full audit trail (admin only)"""
        admin = rbac.create_user('admin-1', 'admin')
        dev = rbac.create_user('dev-1', 'developer')
        
        rbac.check_permission(admin, Permission.VIEW_AUDIT_TRAIL)
        rbac.check_permission(dev, Permission.CREATE_LOG)
        
        # Admin can see all
        full_trail = rbac.get_audit_trail()
        assert len(full_trail) >= 2
    
    # ========== Context Manager Tests ==========
    
    def test_context_manager_auto_logs(self, rbac: RBACManager):
        """Test context manager automatically logs operations"""
        dev = rbac.create_user('dev-1', 'developer')
        
        with rbac.as_user(dev):
            # Simulate operation
            pass
        
        audit_trail = rbac.get_audit_trail(user_id='dev-1')
        assert len(audit_trail) > 0
    
    def test_context_manager_logs_exceptions(self, rbac: RBACManager):
        """Test context manager logs even on exception"""
        dev = rbac.create_user('dev-1', 'developer')
        
        try:
            with rbac.as_user(dev):
                raise ValueError("Test error")
        except ValueError:
            pass
        
        audit_trail = rbac.get_audit_trail(user_id='dev-1')
        assert len(audit_trail) > 0
        entry = audit_trail[-1]
        assert 'error' in entry.get('metadata', {})
    
    # ========== Role Level Tests ==========
    
    def test_role_levels(self, rbac: RBACManager):
        """Test role levels are correct"""
        admin = rbac.create_user('admin-1', 'admin')
        dev = rbac.create_user('dev-1', 'developer')
        auditor = rbac.create_user('auditor-1', 'auditor')
        viewer = rbac.create_user('viewer-1', 'read_only')
        
        assert admin.level == 4
        assert dev.level == 3
        assert auditor.level == 2
        assert viewer.level == 1
    
    def test_higher_level_can_override_lower(self, rbac: RBACManager):
        """Test higher role level can override lower level restrictions"""
        admin = rbac.create_user('admin-1', 'admin')
        dev = rbac.create_user('dev-1', 'developer')
        
        # Developer's resource
        resource = Resource(id='log-123', created_by='dev-1')
        
        # Admin can still access even though not owner
        can_access = rbac.check_permission(
            admin, Permission.UPDATE_LOG, resource=resource
        )
        assert can_access is True


class TestUser:
    """Test suite for User class"""
    
    def test_user_creation(self):
        """Test creating user instance"""
        user = User(
            user_id='user-123',
            role='developer',
            created_at=datetime.now()
        )
        
        assert user.user_id == 'user-123'
        assert user.role == 'developer'
    
    def test_user_permissions_property(self):
        """Test user permissions property"""
        user = User(
            user_id='dev-1',
            role='developer',
            created_at=datetime.now()
        )
        
        permissions = user.permissions
        assert Permission.CREATE_LOG in permissions
    
    def test_user_level_property(self):
        """Test user level property"""
        admin = User(user_id='admin-1', role='admin', created_at=datetime.now())
        dev = User(user_id='dev-1', role='developer', created_at=datetime.now())
        
        assert admin.level == 4
        assert dev.level == 3
    
    def test_can_access_resource(self):
        """Test user can check resource access"""
        dev = User(user_id='dev-1', role='developer', created_at=datetime.now())
        
        own_resource = Resource(id='log-1', created_by='dev-1')
        other_resource = Resource(id='log-2', created_by='dev-2')
        
        assert dev.can_access_resource(own_resource)
        assert not dev.can_access_resource(other_resource)


class TestPermission:
    """Test suite for Permission enum"""
    
    def test_all_permissions_defined(self):
        """Test all 12 permissions are defined"""
        expected_permissions = [
            'CREATE_LOG', 'READ_OWN_LOG', 'READ_ALL_LOGS',
            'UPDATE_LOG', 'DELETE_LOG', 'ENCRYPT_LOG',
            'DECRYPT_LOG', 'ROTATE_KEYS', 'ASSIGN_ROLE',
            'VIEW_AUDIT_TRAIL', 'EXPORT_LOGS', 'SANITIZE_PII'
        ]
        
        for perm_name in expected_permissions:
            assert hasattr(Permission, perm_name)
    
    def test_permission_values(self):
        """Test permission enum values"""
        assert Permission.CREATE_LOG.value == 'create_log'
        assert Permission.DELETE_LOG.value == 'delete_log'


class TestResource:
    """Test suite for Resource class"""
    
    def test_resource_creation(self):
        """Test creating resource instance"""
        resource = Resource(
            id='log-123',
            created_by='user-456',
            metadata={'type': 'audit_log'}
        )
        
        assert resource.id == 'log-123'
        assert resource.created_by == 'user-456'
        assert resource.metadata['type'] == 'audit_log'
    
    def test_resource_is_owned_by(self):
        """Test resource ownership check"""
        resource = Resource(id='log-123', created_by='user-456')
        
        assert resource.is_owned_by('user-456')
        assert not resource.is_owned_by('other-user')
