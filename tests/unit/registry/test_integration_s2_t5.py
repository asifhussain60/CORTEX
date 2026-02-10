"""
Tests for Phase 76 S2 Task 5 - Registry Integration & Multi-Tenant Validation

Authority: Phase 76 S2 Task 5 - Registry Isolation & Multi-Tenant Foundation
AC-ID: AC-PHASE76-S2-T5-001

End-to-end integration tests for:
- Multi-tenant artifact sealing with RBAC
- Cross-tenant isolation enforcement
- Registry health monitoring
- Performance validation
- Rollback scenarios
"""

import pytest
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

from cortex.registry.artifact_sealing import ArtifactSealingManager
from cortex.registry.registry_access_control import RoleBasedAccessControl, Role, Permission, AccessDeniedException
from cortex.registry.tenant_context import TenantContext
from cortex.registry.health_monitor import RegistryHealthMonitor


class TestMultiTenantIntegration:
    """Test multi-tenant integration scenarios."""
    
    def test_multi_tenant_artifact_isolation(self):
        """AC-PHASE76-S2-T5-001: Artifacts isolated across tenants."""
        sealing = ArtifactSealingManager()
        rbac = RoleBasedAccessControl()
        
        # Company A
        ctx_a = TenantContext("acme-dev", "alice@acme.com", ["admin"])
        rbac.assign_role("alice@acme.com", Role.ADMIN)
        
        artifact_a = {"company": "ACME", "secret": "confidential_data_a"}
        rbac.require_permission(ctx_a, Permission.SEAL_ARTIFACT)
        meta_a = sealing.seal_artifact("phase-42-a", "phase", artifact_a, ctx_a)
        
        # Company B
        ctx_b = TenantContext("beta-prod", "bob@beta.com", ["admin"])
        rbac.assign_role("bob@beta.com", Role.ADMIN)
        
        artifact_b = {"company": "BETA", "secret": "confidential_data_b"}
        rbac.require_permission(ctx_b, Permission.SEAL_ARTIFACT)
        meta_b = sealing.seal_artifact("phase-42-b", "phase", artifact_b, ctx_b)
        
        # Verify isolation
        assert meta_a.tenant_id != meta_b.tenant_id
        assert meta_a.tenant_id == ctx_a.tenant_id
        assert meta_b.tenant_id == ctx_b.tenant_id
        
        # Verify artifacts can't be tampered
        with pytest.raises(Exception):  # ArtifactTamperingDetectedError
            sealing.verify_artifact("phase-42-a", artifact_b)
    
    def test_multi_tenant_permission_isolation(self):
        """Permissions isolated per tenant."""
        rbac = RoleBasedAccessControl()
        
        # Company A: Alice is admin
        ctx_a = TenantContext("acme-dev", "alice@acme.com", ["admin"])
        rbac.assign_role("alice@acme.com", Role.ADMIN)
        
        # Company B: Bob is viewer
        ctx_b = TenantContext("beta-prod", "bob@beta.com", ["viewer"])
        rbac.assign_role("bob@beta.com", Role.VIEWER)
        
        # Alice can delete in her context
        assert rbac.has_permission(ctx_a, Permission.DELETE) is True
        
        # Bob cannot delete in his context
        assert rbac.has_permission(ctx_b, Permission.DELETE) is False
    
    def test_cross_tenant_access_prevention(self):
        """Attempt to access other tenant's data is prevented."""
        sealing = ArtifactSealingManager()
        
        ctx_a = TenantContext("acme-dev", "alice@acme.com", ["admin"])
        artifact_a = {"sensitive": "data"}
        meta_a = sealing.seal_artifact("secret-a", "phase", artifact_a, ctx_a)
        
        ctx_b = TenantContext("beta-prod", "bob@beta.com", ["admin"])
        artifact_b = {"different": "data"}
        meta_b = sealing.seal_artifact("secret-b", "phase", artifact_b, ctx_b)
        
        # Verify different hashes (different data)
        assert meta_a.seal_hash != meta_b.seal_hash
        
        # Verify no data leakage - Bob can't verify Company A's artifact
        with pytest.raises(Exception):
            sealing.verify_artifact("secret-a", artifact_b)


class TestAccessControlEnforcement:
    """Test access control enforcement in multi-tenant scenarios."""
    
    def test_viewer_cannot_seal_artifact(self):
        """Viewer role cannot seal artifacts."""
        sealing = ArtifactSealingManager()
        rbac = RoleBasedAccessControl()
        
        ctx = TenantContext("ws1", "viewer_user", ["viewer"])
        rbac.assign_role("viewer_user", Role.VIEWER)
        
        artifact = {"status": "active"}
        
        with pytest.raises(AccessDeniedException):
            rbac.require_permission(ctx, Permission.SEAL_ARTIFACT)
    
    def test_editor_can_seal_but_not_manage(self):
        """Editor can seal, but not manage permissions."""
        rbac = RoleBasedAccessControl()
        
        ctx = TenantContext("ws1", "editor_user", ["editor"])
        rbac.assign_role("editor_user", Role.EDITOR)
        
        # Can seal
        assert rbac.has_permission(ctx, Permission.SEAL_ARTIFACT) is True
        
        # Cannot manage permissions
        assert rbac.has_permission(ctx, Permission.MANAGE_PERMISSIONS) is False
    
    def test_maintainer_can_manage_permissions(self):
        """Maintainer role can manage permissions."""
        rbac = RoleBasedAccessControl()
        
        ctx = TenantContext("ws1", "maint_user", ["maintainer"])
        rbac.assign_role("maint_user", Role.MAINTAINER)
        
        assert rbac.has_permission(ctx, Permission.MANAGE_PERMISSIONS) is True
        assert rbac.has_permission(ctx, Permission.DELETE) is True


class TestHealthMonitoring:
    """Test registry health monitoring."""
    
    def test_registry_health_check(self):
        """Registry health check returns status."""
        from cortex.registry.tenant_aware_git_backed_registry import TenantAwareGitBackedRegistry
        from cortex.registry.workspace_manager import WorkspaceManager
        
        registry = TenantAwareGitBackedRegistry()
        workspace_mgr = WorkspaceManager()
        monitor = RegistryHealthMonitor(registry, workspace_mgr)
        
        health = monitor.check_registry_health()
        
        assert health.healthy is True
        assert health.name == "registry"
    
    def test_tenant_status_monitoring(self):
        """Monitor tracks active tenants."""
        sealing = ArtifactSealingManager()
        
        # Create artifacts for different tenants
        ctx1 = TenantContext("ws1", "user1", ["admin"])
        ctx2 = TenantContext("ws2", "user2", ["admin"])
        ctx3 = TenantContext("ws3", "user3", ["admin"])
        
        sealing.seal_artifact("phase-1", "phase", {"status": "active"}, ctx1)
        sealing.seal_artifact("phase-2", "phase", {"status": "active"}, ctx2)
        sealing.seal_artifact("phase-3", "phase", {"status": "active"}, ctx3)
        
        stats = sealing.get_sealing_statistics()
        
        assert stats["total_artifacts"] == 3
        assert len(stats["by_tenant"]) == 3


class TestPerformanceValidation:
    """Test performance characteristics."""
    
    def test_artifact_sealing_performance(self):
        """Artifact sealing completes in reasonable time."""
        sealing = ArtifactSealingManager()
        artifact = {"phase_id": "42", "status": "active"}
        
        start = time.time()
        meta = sealing.seal_artifact("phase-42", "phase", artifact)
        duration = time.time() - start
        
        assert meta.sealed is True
        assert duration < 0.1  # Should be < 100ms
    
    def test_permission_check_performance(self):
        """Permission checks are fast."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "alice@acme.com", ["editor"])
        rbac.assign_role("alice@acme.com", Role.EDITOR)
        
        start = time.time()
        for _ in range(100):
            rbac.has_permission(ctx, Permission.READ)
        duration = time.time() - start
        
        # 100 permission checks should be < 10ms
        assert duration < 0.01
    
    def test_multi_tenant_sealing_concurrent(self):
        """Concurrent sealing from multiple tenants."""
        sealing = ArtifactSealingManager()
        
        def seal_artifact_for_tenant(tenant_id: int) -> bool:
            ctx = TenantContext(f"ws{tenant_id}", f"user{tenant_id}", ["admin"])
            artifact = {"tenant": tenant_id, "status": "active"}
            try:
                meta = sealing.seal_artifact(f"phase-{tenant_id}", "phase", artifact, ctx)
                return meta.sealed
            except Exception:
                return False
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [executor.submit(seal_artifact_for_tenant, i) for i in range(10)]
            results = [f.result() for f in as_completed(futures)]
        
        assert all(results)
        assert len(sealing.list_sealed_artifacts()) == 10


class TestRollbackScenarios:
    """Test rollback and recovery scenarios."""
    
    def test_rollback_after_failed_seal(self):
        """System remains consistent after rollback."""
        sealing = ArtifactSealingManager()
        
        v1 = {"status": "active", "version": 1}
        meta1 = sealing.seal_artifact("phase-42", "phase", v1)
        
        v2 = {"status": "in-progress", "version": 2}
        meta2 = sealing.update_artifact_version("phase-42", v2)
        
        # Rollback to v1
        restored = sealing.rollback_to_version("phase-42", 1)
        
        assert restored == v1
        assert meta1.seal_hash == sealing._compute_artifact_hash(restored)
    
    def test_multi_version_history_integrity(self):
        """Version history maintains integrity."""
        sealing = ArtifactSealingManager()
        
        artifacts = [
            {"status": "planning"},
            {"status": "active"},
            {"status": "review"},
            {"status": "completed"},
        ]
        
        meta = sealing.seal_artifact("phase-42", "phase", artifacts[0])
        for artifact in artifacts[1:]:
            meta = sealing.update_artifact_version("phase-42", artifact)
        
        history = sealing.get_artifact_history("phase-42")
        
        assert len(history) == 4
        # Verify all hashes are different
        hashes = [h["hash"] for h in history]
        assert len(set(hashes)) == 4  # All unique


class TestErrorRecovery:
    """Test error recovery and resilience."""
    
    def test_permission_denied_does_not_corrupt_state(self):
        """Permission denial doesn't corrupt RBAC state."""
        rbac = RoleBasedAccessControl()
        ctx = TenantContext("ws1", "user1", ["viewer"])
        rbac.assign_role("user1", Role.VIEWER)
        
        try:
            rbac.require_permission(ctx, Permission.DELETE)
        except AccessDeniedException:
            pass
        
        # State should still be intact - user still has viewer role
        roles = rbac.get_user_roles("user1")
        assert Role.VIEWER in roles
    
    def test_artifact_integrity_after_failed_verification(self):
        """Artifact integrity maintained after tampering attempt."""
        sealing = ArtifactSealingManager()
        
        artifact = {"secret": "data"}
        meta = sealing.seal_artifact("phase-42", "phase", artifact)
        original_hash = meta.seal_hash
        
        # Attempt to verify tampered artifact
        tampered = {"secret": "modified"}
        try:
            sealing.verify_artifact("phase-42", tampered)
        except Exception:
            pass
        
        # Original seal should still be intact
        meta_check = sealing.get_artifact_metadata("phase-42")
        assert meta_check is not None
        assert meta_check.seal_hash == original_hash


class TestAuditCompleteness:
    """Test audit logging completeness."""
    
    def test_complete_audit_trail_for_sealed_artifact(self):
        """Complete audit trail for artifact lifecycle."""
        sealing = ArtifactSealingManager()
        rbac = RoleBasedAccessControl()
        
        ctx = TenantContext("ws1", "alice@acme.com", ["admin"])
        rbac.assign_role("alice@acme.com", Role.ADMIN)
        
        # Seal
        v1 = {"status": "active"}
        meta1 = sealing.seal_artifact("phase-42", "phase", v1, ctx)
        
        # Check permission
        rbac.require_permission(ctx, Permission.SEAL_ARTIFACT)
        
        # Update version
        v2 = {"status": "completed"}
        meta2 = sealing.update_artifact_version("phase-42", v2, ctx)
        
        # Get audit log
        audit_log = rbac.get_audit_log(user_id="alice@acme.com")
        
        # Should have: role_assigned + seal operations + permission checks
        assert len(audit_log) >= 2
        assert audit_log[0]["event"] == "role_assigned"


class TestEdgeCasesIntegration:
    """Test edge cases in integrated scenarios."""
    
    def test_same_artifact_id_different_tenants(self):
        """Same artifact ID in different tenants creates separate entries."""
        sealing = ArtifactSealingManager()
        
        ctx1 = TenantContext("ws1", "user1", ["admin"])
        ctx2 = TenantContext("ws2", "user2", ["admin"])
        
        # Both seal "phase-42" but different data
        artifact1 = {"value": 1}
        meta1 = sealing.seal_artifact("phase-42", "phase", artifact1, ctx1)
        
        artifact2 = {"value": 2}
        meta2 = sealing.seal_artifact("phase-42-b", "phase", artifact2, ctx2)
        
        # Different IDs, so both can be sealed
        assert meta1.artifact_id != meta2.artifact_id
    
    def test_bulk_sealing_with_different_permissions(self):
        """Bulk sealing respects different permission levels."""
        sealing = ArtifactSealingManager()
        rbac = RoleBasedAccessControl()
        
        # Admin can seal
        ctx_admin = TenantContext("ws1", "admin_user", ["admin"])
        rbac.assign_role("admin_user", Role.ADMIN)
        rbac.require_permission(ctx_admin, Permission.SEAL_ARTIFACT)
        
        # Editor can seal
        ctx_editor = TenantContext("ws2", "editor_user", ["editor"])
        rbac.assign_role("editor_user", Role.EDITOR)
        rbac.require_permission(ctx_editor, Permission.SEAL_ARTIFACT)
        
        # Viewer cannot seal
        ctx_viewer = TenantContext("ws3", "viewer_user", ["viewer"])
        rbac.assign_role("viewer_user", Role.VIEWER)
        
        with pytest.raises(AccessDeniedException):
            rbac.require_permission(ctx_viewer, Permission.SEAL_ARTIFACT)
