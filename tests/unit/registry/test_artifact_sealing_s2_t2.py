"""
Tests for Phase 76 S2 Task 2 - Artifact Sealing & Versioning

Authority: Phase 76 S2 Task 2 - Registry Isolation & Multi-Tenant Foundation
AC-ID: AC-PHASE76-S2-T2-001

Test Coverage:
- Artifact sealing with cryptographic hashing
- Integrity verification
- Tamper detection
- Version control
- Rollback support
- Multi-tenant artifact isolation
"""

import pytest
from pathlib import Path
from datetime import datetime

from cortex.registry.artifact_sealing import (
    ArtifactSealingManager,
    ArtifactMetadata,
    ArtifactAlreadySealedError,
    ArtifactTamperingDetectedError,
)
from cortex.registry.tenant_context import TenantContext


class TestArtifactSealing:
    """Test artifact sealing functionality."""
    
    def test_seal_artifact(self):
        """AC-PHASE76-S2-T2-001: Seal artifact with SHA-256 hash."""
        manager = ArtifactSealingManager()
        artifact = {"phase_id": "42", "status": "active", "priority": "P0"}
        
        meta = manager.seal_artifact("phase-42", "phase", artifact)
        
        assert meta.artifact_id == "phase-42"
        assert meta.artifact_type == "phase"
        assert meta.sealed is True
        assert meta.seal_hash is not None
        assert len(meta.seal_hash) == 64  # SHA-256 is 64 hex chars
        assert meta.version == 1
        assert meta.created_at is not None
    
    def test_seal_with_tenant_context(self):
        """Seal artifact with tenant context."""
        ctx = TenantContext("ws1", "user1", ["admin"])
        manager = ArtifactSealingManager()
        artifact = {"status": "active"}
        
        meta = manager.seal_artifact("phase-42", "phase", artifact, ctx)
        
        assert meta.tenant_id == ctx.tenant_id
        assert meta.created_by == "user1"
    
    def test_cannot_seal_twice(self):
        """Cannot seal same artifact twice."""
        manager = ArtifactSealingManager()
        artifact = {"status": "active"}
        
        manager.seal_artifact("phase-42", "phase", artifact)
        
        with pytest.raises(ArtifactAlreadySealedError):
            manager.seal_artifact("phase-42", "phase", artifact)
    
    def test_seal_hash_is_deterministic(self):
        """Same artifact produces same hash."""
        manager = ArtifactSealingManager()
        artifact = {"phase_id": "42", "status": "active"}
        
        meta1 = manager.seal_artifact("phase-42", "phase", artifact)
        
        # Create new manager to get fresh instance
        manager2 = ArtifactSealingManager()
        meta2 = manager2.seal_artifact("phase-43", "phase", artifact)
        
        assert meta1.seal_hash == meta2.seal_hash


class TestArtifactIntegrity:
    """Test artifact integrity verification."""
    
    def test_verify_intact_artifact(self):
        """Verify intact artifact passes integrity check."""
        manager = ArtifactSealingManager()
        artifact = {"status": "active"}
        
        manager.seal_artifact("phase-42", "phase", artifact)
        is_valid = manager.verify_artifact("phase-42", artifact)
        
        assert is_valid is True
    
    def test_detect_tampered_artifact(self):
        """Detect tampered artifact (hash mismatch)."""
        manager = ArtifactSealingManager()
        artifact = {"status": "active"}
        
        manager.seal_artifact("phase-42", "phase", artifact)
        
        # Attempt to verify tampered artifact
        tampered = {"status": "modified"}
        
        with pytest.raises(ArtifactTamperingDetectedError):
            manager.verify_artifact("phase-42", tampered)
    
    def test_verify_nonexistent_artifact(self):
        """Verify nonexistent artifact returns False."""
        manager = ArtifactSealingManager()
        artifact = {"status": "active"}
        
        is_valid = manager.verify_artifact("nonexistent", artifact)
        
        assert is_valid is False


class TestVersionControl:
    """Test version control and history."""
    
    def test_create_new_version(self):
        """Create new version of artifact."""
        manager = ArtifactSealingManager()
        
        v1 = {"status": "active"}
        meta1 = manager.seal_artifact("phase-42", "phase", v1)
        assert meta1.version == 1
        
        v2 = {"status": "completed", "duration_days": 5}
        meta2 = manager.update_artifact_version("phase-42", v2)
        assert meta2.version == 2
        assert meta2.sealed is True
    
    def test_version_has_different_hash(self):
        """Different versions have different hashes."""
        manager = ArtifactSealingManager()
        
        v1 = {"status": "active"}
        meta1 = manager.seal_artifact("phase-42", "phase", v1)
        
        v2 = {"status": "completed"}
        meta2 = manager.update_artifact_version("phase-42", v2)
        
        assert meta1.seal_hash != meta2.seal_hash
    
    def test_get_artifact_history(self):
        """Get complete version history."""
        manager = ArtifactSealingManager()
        
        v1 = {"status": "active"}
        manager.seal_artifact("phase-42", "phase", v1)
        
        v2 = {"status": "completed"}
        manager.update_artifact_version("phase-42", v2)
        
        v3 = {"status": "archived"}
        manager.update_artifact_version("phase-42", v3)
        
        history = manager.get_artifact_history("phase-42")
        
        assert len(history) == 3
        assert history[0]["version"] == 1
        assert history[1]["version"] == 2
        assert history[2]["version"] == 3
        assert history[0]["artifact"] == v1
        assert history[1]["artifact"] == v2
        assert history[2]["artifact"] == v3
    
    def test_version_preserves_metadata(self):
        """New version preserves original metadata."""
        ctx = TenantContext("ws1", "user1", ["admin"])
        manager = ArtifactSealingManager()
        
        v1 = {"status": "active"}
        meta1 = manager.seal_artifact("phase-42", "phase", v1, ctx)
        
        v2 = {"status": "completed"}
        meta2 = manager.update_artifact_version("phase-42", v2, ctx)
        
        assert meta1.tenant_id == meta2.tenant_id
        assert meta1.created_at == meta2.created_at
        assert meta1.artifact_type == meta2.artifact_type


class TestRollback:
    """Test rollback functionality."""
    
    def test_rollback_to_previous_version(self):
        """Rollback to previous version."""
        manager = ArtifactSealingManager()
        
        v1 = {"status": "active"}
        manager.seal_artifact("phase-42", "phase", v1)
        
        v2 = {"status": "completed"}
        manager.update_artifact_version("phase-42", v2)
        
        v3 = {"status": "archived"}
        manager.update_artifact_version("phase-42", v3)
        
        # Rollback to v2
        restored = manager.rollback_to_version("phase-42", 2)
        
        assert restored == v2
    
    def test_rollback_to_initial_version(self):
        """Rollback to initial version."""
        manager = ArtifactSealingManager()
        
        v1 = {"status": "active"}
        manager.seal_artifact("phase-42", "phase", v1)
        
        v2 = {"status": "completed"}
        manager.update_artifact_version("phase-42", v2)
        
        restored = manager.rollback_to_version("phase-42", 1)
        
        assert restored == v1
    
    def test_rollback_nonexistent_version_fails(self):
        """Rollback to nonexistent version raises error."""
        manager = ArtifactSealingManager()
        
        v1 = {"status": "active"}
        manager.seal_artifact("phase-42", "phase", v1)
        
        with pytest.raises(ValueError, match="Version 99 not found"):
            manager.rollback_to_version("phase-42", 99)


class TestMetadata:
    """Test artifact metadata operations."""
    
    def test_get_artifact_metadata(self):
        """Retrieve artifact metadata."""
        manager = ArtifactSealingManager()
        artifact = {"status": "active"}
        
        sealed_meta = manager.seal_artifact("phase-42", "phase", artifact)
        retrieved_meta = manager.get_artifact_metadata("phase-42")
        
        assert retrieved_meta == sealed_meta
    
    def test_metadata_to_dict(self):
        """Artifact metadata serializable to dict."""
        manager = ArtifactSealingManager()
        artifact = {"status": "active"}
        
        meta = manager.seal_artifact("phase-42", "phase", artifact)
        meta_dict = meta.to_dict()
        
        assert meta_dict["artifact_id"] == "phase-42"
        assert meta_dict["artifact_type"] == "phase"
        assert meta_dict["sealed"] is True
        assert meta_dict["seal_hash"] is not None


class TestMultiTenant:
    """Test multi-tenant artifact isolation."""
    
    def test_different_tenants_isolated(self):
        """Artifacts from different tenants are isolated."""
        ctx1 = TenantContext("ws1", "user1", ["admin"])
        ctx2 = TenantContext("ws2", "user2", ["admin"])
        
        manager = ArtifactSealingManager()
        
        artifact1 = {"status": "active"}
        meta1 = manager.seal_artifact("phase-42-a", "phase", artifact1, ctx1)
        
        artifact2 = {"status": "inactive"}
        meta2 = manager.seal_artifact("phase-42-b", "phase", artifact2, ctx2)
        
        assert meta1.tenant_id != meta2.tenant_id
    
    def test_list_artifacts_by_tenant(self):
        """List artifacts filtered by tenant."""
        ctx1 = TenantContext("ws1", "user1", ["admin"])
        ctx2 = TenantContext("ws2", "user2", ["admin"])
        
        manager = ArtifactSealingManager()
        
        manager.seal_artifact("phase-42", "phase", {"status": "active"}, ctx1)
        manager.seal_artifact("phase-43", "phase", {"status": "active"}, ctx1)
        manager.seal_artifact("phase-44", "phase", {"status": "active"}, ctx2)
        
        ctx1_artifacts = manager.list_sealed_artifacts(tenant_id=ctx1.tenant_id)
        
        assert len(ctx1_artifacts) == 2
        assert all(a.tenant_id == ctx1.tenant_id for a in ctx1_artifacts)


class TestListingAndFiltering:
    """Test artifact listing and filtering."""
    
    def test_list_sealed_artifacts(self):
        """List all sealed artifacts."""
        manager = ArtifactSealingManager()
        
        manager.seal_artifact("phase-42", "phase", {"status": "active"})
        manager.seal_artifact("orch-1", "orchestrator", {"name": "orch1"})
        manager.seal_artifact("phase-43", "phase", {"status": "active"})
        
        artifacts = manager.list_sealed_artifacts()
        
        assert len(artifacts) == 3
    
    def test_list_artifacts_by_type(self):
        """List artifacts filtered by type."""
        manager = ArtifactSealingManager()
        
        manager.seal_artifact("phase-42", "phase", {"status": "active"})
        manager.seal_artifact("orch-1", "orchestrator", {"name": "orch1"})
        manager.seal_artifact("phase-43", "phase", {"status": "active"})
        
        phases = manager.list_sealed_artifacts(artifact_type="phase")
        
        assert len(phases) == 2
        assert all(a.artifact_type == "phase" for a in phases)
    
    def test_empty_list_when_no_artifacts(self):
        """List returns empty when no artifacts sealed."""
        manager = ArtifactSealingManager()
        
        artifacts = manager.list_sealed_artifacts()
        
        assert artifacts == []


class TestStatistics:
    """Test sealing statistics."""
    
    def test_get_sealing_statistics(self):
        """Get statistics on sealed artifacts."""
        manager = ArtifactSealingManager()
        
        manager.seal_artifact("phase-42", "phase", {"status": "active"})
        manager.seal_artifact("orch-1", "orchestrator", {"name": "orch1"})
        manager.seal_artifact("phase-43", "phase", {"status": "active"})
        
        stats = manager.get_sealing_statistics()
        
        assert stats["total_artifacts"] == 3
        assert stats["sealed"] == 3
        assert stats["unsealed"] == 0
        assert stats["by_type"]["phase"] == 2
        assert stats["by_type"]["orchestrator"] == 1
        assert stats["total_versions"] == 3
    
    def test_statistics_with_versions(self):
        """Statistics reflect multiple versions."""
        manager = ArtifactSealingManager()
        
        manager.seal_artifact("phase-42", "phase", {"status": "active"})
        manager.update_artifact_version("phase-42", {"status": "completed"})
        manager.update_artifact_version("phase-42", {"status": "archived"})
        
        stats = manager.get_sealing_statistics()
        
        assert stats["total_artifacts"] == 1
        assert stats["total_versions"] == 3


class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_seal_empty_artifact(self):
        """Seal empty artifact."""
        manager = ArtifactSealingManager()
        artifact = {}
        
        meta = manager.seal_artifact("phase-42", "phase", artifact)
        
        assert meta.sealed is True
        assert meta.seal_hash is not None
    
    def test_seal_large_artifact(self):
        """Seal large artifact."""
        manager = ArtifactSealingManager()
        
        # Create large artifact (1MB)
        artifact = {
            "data": "x" * (1024 * 1024)
        }
        
        meta = manager.seal_artifact("phase-42", "phase", artifact)
        
        assert meta.sealed is True
    
    def test_seal_deeply_nested_artifact(self):
        """Seal deeply nested artifact."""
        manager = ArtifactSealingManager()
        
        # Create deeply nested structure
        artifact = {"level1": {"level2": {"level3": {"level4": {"status": "active"}}}}}
        
        meta = manager.seal_artifact("phase-42", "phase", artifact)
        
        assert meta.sealed is True
    
    def test_update_version_nonexistent_artifact(self):
        """Cannot update version of unsealed artifact."""
        manager = ArtifactSealingManager()
        
        with pytest.raises(ValueError, match="not previously sealed"):
            manager.update_artifact_version("nonexistent", {"status": "active"})
    
    def test_special_characters_in_artifact_id(self):
        """Handle special characters in artifact ID."""
        manager = ArtifactSealingManager()
        artifact = {"status": "active"}
        
        artifact_id = "phase-42_v1.0+beta"
        meta = manager.seal_artifact(artifact_id, "phase", artifact)
        
        assert meta.artifact_id == artifact_id
        assert meta.sealed is True
