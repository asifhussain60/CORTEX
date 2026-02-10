"""
Tests for Phase 76 S2 Task 1 - Gap Analysis & Tenant Isolation Architecture

Authority: Phase 76 S2 Task 1 - Registry Isolation & Multi-Tenant Foundation
AC-ID: AC-PHASE76-S2-T1-001

Validates the tenant isolation architecture and gap analysis framework.
"""

import pytest
from cortex.registry.artifact_sealing import ArtifactSealingManager
from cortex.registry.registry_access_control import RoleBasedAccessControl, Role
from cortex.registry.tenant_context import TenantContext


class TestGapAnalysis:
    """Tests for registry isolation gap analysis."""
    
    def test_tenant_context_provides_isolation_boundaries(self):
        """AC-PHASE76-S2-T1-001: TenantContext identifies isolation boundaries."""
        ctx1 = TenantContext("acme-dev", "alice@acme.com", ["admin"])
        ctx2 = TenantContext("beta-prod", "bob@beta.com", ["admin"])
        
        assert ctx1.tenant_id != ctx2.tenant_id
        assert ctx1.workspace_id != ctx2.workspace_id
    
    def test_artifact_sealing_provides_integrity_verification(self):
        """Artifact sealing provides tamper detection."""
        manager = ArtifactSealingManager()
        artifact = {"critical": "data"}
        
        meta = manager.seal_artifact("critical-artifact", "phase", artifact)
        assert meta.seal_hash is not None
        
        # Verify detects tampering
        from cortex.registry.artifact_sealing import ArtifactTamperingDetectedError
        with pytest.raises(ArtifactTamperingDetectedError):
            manager.verify_artifact("critical-artifact", {"critical": "modified"})
    
    def test_rbac_provides_access_control(self):
        """RBAC provides role-based access control."""
        rbac = RoleBasedAccessControl()
        
        ctx_viewer = TenantContext("ws1", "viewer", ["viewer"])
        ctx_admin = TenantContext("ws1", "admin", ["admin"])
        
        rbac.assign_role("viewer", Role.VIEWER)
        rbac.assign_role("admin", Role.ADMIN)
        
        # Viewer read-only
        from cortex.registry.registry_access_control import Permission
        assert rbac.has_permission(ctx_viewer, Permission.READ) is True
        assert rbac.has_permission(ctx_viewer, Permission.DELETE) is False
        
        # Admin full access
        assert rbac.has_permission(ctx_admin, Permission.DELETE) is True
