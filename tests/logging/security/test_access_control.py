"""
Tests for role-based access control (RBAC) functionality.

RED Phase - These tests should fail initially.
"""

import pytest
from datetime import datetime, timedelta

from src.logging.security.access_control import (
    AccessControl,
    Role,
    Permission,
    AccessPolicy,
    AccessDeniedError,
)


class TestAccessControl:
    """Test RBAC for audit logs."""

    @pytest.fixture
    def access_control(self):
        """Create AccessControl instance with default policies."""
        return AccessControl()

    @pytest.fixture
    def admin_user(self):
        """Admin user for testing."""
        return {"user_id": "admin001", "role": Role.ADMIN, "name": "Admin User"}

    @pytest.fixture
    def developer_user(self):
        """Developer user for testing."""
        return {"user_id": "dev001", "role": Role.DEVELOPER, "name": "Dev User"}

    @pytest.fixture
    def auditor_user(self):
        """Auditor user for testing."""
        return {"user_id": "audit001", "role": Role.AUDITOR, "name": "Auditor User"}

    @pytest.fixture
    def readonly_user(self):
        """Read-only user for testing."""
        return {"user_id": "ro001", "role": Role.READ_ONLY, "name": "Viewer User"}

    def test_role_hierarchy(self):
        """Test role permission hierarchy."""
        assert Role.ADMIN.level > Role.DEVELOPER.level
        assert Role.DEVELOPER.level > Role.AUDITOR.level
        assert Role.AUDITOR.level > Role.READ_ONLY.level

    def test_admin_full_access(self, access_control, admin_user):
        """Test admin has full access to all operations."""
        operations = [
            Permission.READ,
            Permission.WRITE,
            Permission.DELETE,
            Permission.CONFIGURE,
            Permission.AUDIT,
        ]
        
        for op in operations:
            assert access_control.has_permission(admin_user, op)

    def test_developer_read_write(self, access_control, developer_user):
        """Test developer can read and write logs."""
        assert access_control.has_permission(developer_user, Permission.READ)
        assert access_control.has_permission(developer_user, Permission.WRITE)
        assert not access_control.has_permission(developer_user, Permission.DELETE)
        assert not access_control.has_permission(developer_user, Permission.CONFIGURE)

    def test_auditor_read_audit_only(self, access_control, auditor_user):
        """Test auditor can read and audit but not modify."""
        assert access_control.has_permission(auditor_user, Permission.READ)
        assert access_control.has_permission(auditor_user, Permission.AUDIT)
        assert not access_control.has_permission(auditor_user, Permission.WRITE)
        assert not access_control.has_permission(auditor_user, Permission.DELETE)

    def test_readonly_read_only(self, access_control, readonly_user):
        """Test read-only user can only read logs."""
        assert access_control.has_permission(readonly_user, Permission.READ)
        assert not access_control.has_permission(readonly_user, Permission.WRITE)
        assert not access_control.has_permission(readonly_user, Permission.DELETE)
        assert not access_control.has_permission(readonly_user, Permission.AUDIT)

    def test_check_permission_raises_error(self, access_control, readonly_user):
        """Test check_permission raises error on denied access."""
        with pytest.raises(AccessDeniedError, match="read_only.*write"):
            access_control.check_permission(readonly_user, Permission.WRITE)

    def test_check_permission_passes(self, access_control, admin_user):
        """Test check_permission passes for allowed operation."""
        access_control.check_permission(admin_user, Permission.DELETE)
        # Should not raise exception

    def test_custom_access_policy(self):
        """Test custom access policies."""
        policy = AccessPolicy(
            role=Role.DEVELOPER,
            allowed_permissions=[Permission.READ, Permission.AUDIT]
        )
        
        ac = AccessControl(policies=[policy])
        dev_user = {"user_id": "dev001", "role": Role.DEVELOPER}
        
        assert ac.has_permission(dev_user, Permission.READ)
        assert ac.has_permission(dev_user, Permission.AUDIT)
        assert not ac.has_permission(dev_user, Permission.WRITE)

    def test_resource_level_permissions(self, access_control, developer_user):
        """Test permissions for specific resources."""
        # Developer can read own logs
        assert access_control.can_access_resource(
            developer_user,
            resource_id="logs/dev001/session.log",
            operation=Permission.READ
        )
        
        # Developer cannot delete own logs
        assert not access_control.can_access_resource(
            developer_user,
            resource_id="logs/dev001/session.log",
            operation=Permission.DELETE
        )

    def test_audit_trail_logging(self, access_control, developer_user):
        """Test access attempts are logged to audit trail."""
        access_control.check_permission(developer_user, Permission.READ)
        
        audit_log = access_control.get_audit_trail(user_id="dev001", limit=1)
        
        assert len(audit_log) == 1
        assert audit_log[0]["user_id"] == "dev001"
        assert audit_log[0]["permission"] == Permission.READ.value
        assert audit_log[0]["result"] == "granted"

    def test_audit_trail_denied_access(self, access_control, readonly_user):
        """Test denied access is logged."""
        try:
            access_control.check_permission(readonly_user, Permission.DELETE)
        except AccessDeniedError:
            pass
        
        audit_log = access_control.get_audit_trail(user_id="ro001", limit=1)
        
        assert len(audit_log) == 1
        assert audit_log[0]["result"] == "denied"

    def test_time_based_access(self, access_control):
        """Test time-based access restrictions."""
        business_hours_user = {
            "user_id": "bh001",
            "role": Role.DEVELOPER,
            "access_hours": {"start": 9, "end": 17}  # 9 AM - 5 PM
        }
        
        # Simulate time check
        current_hour = datetime.now().hour
        
        if 9 <= current_hour < 17:
            assert access_control.is_access_time_valid(business_hours_user)
        else:
            assert not access_control.is_access_time_valid(business_hours_user)

    def test_ip_whitelist(self, access_control):
        """Test IP-based access control."""
        user_with_ip = {
            "user_id": "ip001",
            "role": Role.DEVELOPER,
            "ip_whitelist": ["192.168.1.0/24", "10.0.0.1"]
        }
        
        assert access_control.is_ip_allowed(user_with_ip, "192.168.1.50")
        assert access_control.is_ip_allowed(user_with_ip, "10.0.0.1")
        assert not access_control.is_ip_allowed(user_with_ip, "203.0.113.1")

    def test_session_based_access(self, access_control, developer_user):
        """Test session-based access control."""
        session_id = access_control.create_session(developer_user, ttl_minutes=30)
        
        assert access_control.validate_session(session_id)
        assert access_control.get_session_user(session_id) == developer_user

    def test_session_expiration(self, access_control, developer_user):
        """Test session expiration."""
        session_id = access_control.create_session(developer_user, ttl_minutes=0.01)
        
        import time
        time.sleep(0.02 * 60)  # Wait for expiration
        
        assert not access_control.validate_session(session_id)

    def test_revoke_access(self, access_control, developer_user):
        """Test revoking user access."""
        session_id = access_control.create_session(developer_user)
        
        access_control.revoke_access(developer_user["user_id"])
        
        assert not access_control.validate_session(session_id)

    def test_permission_inheritance(self):
        """Test permission inheritance from higher roles."""
        policy_developer = AccessPolicy(
            role=Role.DEVELOPER,
            allowed_permissions=[Permission.READ, Permission.WRITE]
        )
        
        policy_admin = AccessPolicy(
            role=Role.ADMIN,
            allowed_permissions=[Permission.READ, Permission.WRITE, Permission.DELETE],
            inherits_from=Role.DEVELOPER
        )
        
        ac = AccessControl(policies=[policy_developer, policy_admin])
        
        admin = {"user_id": "admin", "role": Role.ADMIN}
        assert ac.has_permission(admin, Permission.READ)  # Inherited
        assert ac.has_permission(admin, Permission.DELETE)  # Direct

    def test_audit_trail_retention(self, access_control, developer_user):
        """Test audit trail retention and cleanup."""
        # Generate 100 access logs
        for _ in range(100):
            access_control.check_permission(developer_user, Permission.READ)
        
        # Get last 10
        recent = access_control.get_audit_trail(user_id="dev001", limit=10)
        assert len(recent) == 10
        
        # Cleanup old entries (>30 days)
        deleted = access_control.cleanup_audit_trail(days=30)
        assert deleted >= 0

    def test_concurrent_access_control(self, access_control, developer_user):
        """Test thread-safe access control."""
        import threading
        
        results = []
        
        def check_access():
            try:
                access_control.check_permission(developer_user, Permission.READ)
                results.append(True)
            except AccessDeniedError:
                results.append(False)
        
        threads = [threading.Thread(target=check_access) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()
        
        assert all(results)
        assert len(results) == 10

    def test_permission_escalation_prevention(self, access_control, developer_user):
        """Test prevention of privilege escalation."""
        # Developer cannot grant admin permissions
        with pytest.raises(AccessDeniedError):
            access_control.grant_permission(
                requester=developer_user,
                target_user_id="other_user",
                permission=Permission.CONFIGURE
            )

    def test_export_audit_trail(self, access_control, admin_user):
        """Test exporting audit trail for compliance."""
        # Generate some activity
        access_control.check_permission(admin_user, Permission.READ)
        access_control.check_permission(admin_user, Permission.DELETE)
        
        # Export last 24 hours
        start_time = datetime.now() - timedelta(hours=24)
        export_data = access_control.export_audit_trail(
            start_time=start_time,
            format="json"
        )
        
        assert "audit_entries" in export_data
        assert len(export_data["audit_entries"]) >= 2
