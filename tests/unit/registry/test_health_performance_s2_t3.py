"""
Tests for Phase 76 S2 Task 3 - Advanced Registry Health & Performance

Authority: Phase 76 S2 Task 3 - Registry Isolation & Multi-Tenant Foundation
AC-ID: AC-PHASE76-S2-T3-001

Tests for registry health monitoring and performance characteristics.
"""

import pytest
import time
from cortex.registry.artifact_sealing import ArtifactSealingManager
from cortex.registry.registry_access_control import RoleBasedAccessControl, Role, Permission


class TestRegistryHealthMetrics:
    """Tests for registry health metrics."""
    
    def test_sealing_statistics_accuracy(self):
        """AC-PHASE76-S2-T3-001: Sealing statistics are accurate."""
        manager = ArtifactSealingManager()
        
        # Seal artifacts of different types
        manager.seal_artifact("phase-1", "phase", {"status": "active"})
        manager.seal_artifact("orch-1", "orchestrator", {"name": "orch"})
        manager.seal_artifact("phase-2", "phase", {"status": "active"})
        
        stats = manager.get_sealing_statistics()
        
        assert stats["total_artifacts"] == 3
        assert stats["sealed"] == 3
        assert stats["by_type"]["phase"] == 2
        assert stats["by_type"]["orchestrator"] == 1
    
    def test_rbac_audit_trail_completeness(self):
        """RBAC audit trail is complete and accurate."""
        rbac = RoleBasedAccessControl()
        
        rbac.assign_role("user1", Role.VIEWER)
        rbac.assign_role("user1", Role.EDITOR)
        rbac.revoke_role("user1", Role.VIEWER)
        
        audit = rbac.get_audit_log(user_id="user1")
        
        assert len(audit) == 3
        assert audit[0]["event"] == "role_assigned"
        assert audit[1]["event"] == "role_assigned"
        assert audit[2]["event"] == "role_revoked"


class TestPerformanceCharacteristics:
    """Tests for registry performance."""
    
    def test_artifact_sealing_scalable_performance(self):
        """Artifact sealing scales linearly."""
        manager = ArtifactSealingManager()
        
        times = []
        for i in range(5):
            artifact = {"index": i, "data": "x" * 1000}
            start = time.time()
            manager.seal_artifact(f"phase-{i}", "phase", artifact)
            times.append(time.time() - start)
        
        # All times should be roughly similar (no degradation)
        avg_time = sum(times) / len(times)
        assert all(t < avg_time * 2 for t in times)  # No massive outliers
    
    def test_permission_check_consistent_speed(self):
        """Permission checks maintain consistent speed."""
        rbac = RoleBasedAccessControl()
        rbac.assign_role("user1", Role.EDITOR)
        
        from cortex.registry.tenant_context import TenantContext
        ctx = TenantContext("ws1", "user1", ["editor"])
        
        times = []
        for _ in range(10):
            start = time.time()
            rbac.has_permission(ctx, Permission.READ)
            times.append(time.time() - start)
        
        # All checks should be very fast
        assert all(t < 0.001 for t in times)


class TestMultiTenantRegistryConsistency:
    """Tests for multi-tenant registry consistency."""
    
    def test_tenant_artifact_consistency(self):
        """Tenant artifacts remain consistent."""
        manager = ArtifactSealingManager()
        
        from cortex.registry.tenant_context import TenantContext
        
        ctx1 = TenantContext("ws1", "user1", ["admin"])
        ctx2 = TenantContext("ws2", "user2", ["admin"])
        
        artifact1 = {"value": 1}
        artifact2 = {"value": 2}
        
        meta1 = manager.seal_artifact("data", "phase", artifact1, ctx1)
        meta2 = manager.seal_artifact("data-b", "phase", artifact2, ctx2)
        
        # Both should be sealed consistently
        assert meta1.sealed is True
        assert meta2.sealed is True
        assert meta1.tenant_id != meta2.tenant_id
