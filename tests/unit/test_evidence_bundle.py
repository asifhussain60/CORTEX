"""
Evidence Bundle Tests - TDD for AC-FR-004

Tests for:
- AC-FR-004-01: Evidence Bundle Completeness (<500ms capture)
- AC-FR-004-02: JSON Serialization + Integrity Verification
- AC-FR-004-03: Artifact Collection with AC-ID linkage

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import time

import pytest

from src.infrastructure.evidence_bundle import (
    EvidenceBundleGenerator,
    EvidenceBundle,
    Artifact,
    ArtifactType,
    EvidenceLevel,
)
from src.infrastructure.database import DatabaseManager, DatabaseConfig


@pytest.mark.ac("FR-004-01")
class TestBundleCreation:
    """Test AC-FR-004-01: Bundle creation with <500ms capture"""
    
    def test_create_bundle(self):
        """Should create evidence bundle."""
        generator = EvidenceBundleGenerator()
        
        result = generator.create_bundle(
            ac_id="AC-TEST-001",
            phase_id="PHASE-01"
        )
        
        assert result.is_ok()
        bundle = result.unwrap()
        assert bundle.ac_id == "AC-TEST-001"
        assert bundle.phase_id == "PHASE-01"
        assert len(bundle.artifacts) == 0
    
    def test_bundle_has_unique_id(self):
        """Each bundle should have unique ID."""
        generator = EvidenceBundleGenerator()
        
        result1 = generator.create_bundle("AC-TEST-001")
        result2 = generator.create_bundle("AC-TEST-001")
        
        bundle1 = result1.unwrap()
        bundle2 = result2.unwrap()
        
        assert bundle1.bundle_id != bundle2.bundle_id
    
    def test_bundle_capture_time_under_500ms(self):
        """Bundle capture should complete in <500ms."""
        generator = EvidenceBundleGenerator()
        
        result = generator.create_bundle("AC-TEST-001")
        bundle = result.unwrap()
        
        # Add some artifacts
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.METADATA,
            {"key": "value"}
        )
        
        # Finalize
        finalize_result = generator.finalize_bundle(bundle.bundle_id)
        
        assert finalize_result.is_ok()
        finalized = finalize_result.unwrap()
        assert finalized.capture_time_ms < 500
    
    def test_capture_time_exceeds_500ms_rejected(self):
        """Bundle should fail if capture exceeds 500ms."""
        generator = EvidenceBundleGenerator()
        
        result = generator.create_bundle("AC-TEST-001")
        bundle = result.unwrap()
        
        # Manually set created_at to 600ms ago
        import datetime
        old_time = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(milliseconds=600)
        bundle.created_at = old_time.isoformat()
        
        finalize_result = generator.finalize_bundle(bundle.bundle_id)
        
        # Should fail due to time limit
        assert finalize_result.is_err()
        assert "500ms" in str(finalize_result).lower()
    
    def test_bundle_with_evidence_level(self):
        """Bundle should store evidence level."""
        generator = EvidenceBundleGenerator()
        
        result = generator.create_bundle(
            "AC-TEST-001",
            evidence_level=EvidenceLevel.CRITICAL
        )
        
        bundle = result.unwrap()
        assert bundle.evidence_level == EvidenceLevel.CRITICAL


@pytest.mark.ac("FR-004-03")
class TestArtifactCollection:
    """Test AC-FR-004-03: Artifact collection with AC-ID linkage"""
    
    def test_add_artifact_to_bundle(self):
        """Should add artifact to bundle."""
        generator = EvidenceBundleGenerator()
        bundle_result = generator.create_bundle("AC-TEST-001")
        bundle = bundle_result.unwrap()
        
        content = {"result": "passed", "duration_ms": 125}
        artifact_result = generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.TEST_RESULT,
            content
        )
        
        assert artifact_result.is_ok()
        artifact = artifact_result.unwrap()
        assert artifact.artifact_type == ArtifactType.TEST_RESULT
        assert artifact.content == content
    
    def test_artifact_gets_unique_id(self):
        """Each artifact should have unique ID."""
        generator = EvidenceBundleGenerator()
        bundle_result = generator.create_bundle("AC-TEST-001")
        bundle = bundle_result.unwrap()
        
        art1_result = generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.METADATA,
            {"key": "value1"}
        )
        art2_result = generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.METADATA,
            {"key": "value2"}
        )
        
        art1 = art1_result.unwrap()
        art2 = art2_result.unwrap()
        
        assert art1.artifact_id != art2.artifact_id
    
    def test_artifact_includes_ac_id_in_id(self):
        """Artifact ID should include AC-ID."""
        generator = EvidenceBundleGenerator()
        bundle_result = generator.create_bundle("AC-TEST-001")
        bundle = bundle_result.unwrap()
        
        artifact_result = generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.METADATA,
            {"data": "test"}
        )
        
        artifact = artifact_result.unwrap()
        assert "AC-TEST-001" in artifact.artifact_id
    
    def test_multiple_artifact_types(self):
        """Bundle should support multiple artifact types."""
        generator = EvidenceBundleGenerator()
        bundle_result = generator.create_bundle("AC-TEST-001")
        bundle = bundle_result.unwrap()
        
        # Add different artifact types
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.SOURCE_CODE,
            {"file": "test.py", "lines": 150}
        )
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.TEST_RESULT,
            {"passed": 10, "failed": 0}
        )
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.AUDIT_LOG,
            {"entries": 42}
        )
        
        # Get bundle
        get_result = generator.get_bundle(bundle.bundle_id)
        retrieved = get_result.unwrap()
        
        assert len(retrieved.artifacts) == 3
        types = [a.artifact_type for a in retrieved.artifacts]
        assert ArtifactType.SOURCE_CODE in types
        assert ArtifactType.TEST_RESULT in types
        assert ArtifactType.AUDIT_LOG in types
    
    def test_artifact_content_preserved(self):
        """Artifact content should be fully preserved."""
        generator = EvidenceBundleGenerator()
        bundle_result = generator.create_bundle("AC-TEST-001")
        bundle = bundle_result.unwrap()
        
        content = {
            "nested": {"key": "value", "count": 42},
            "array": [1, 2, 3],
            "string": "test data"
        }
        
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.METADATA,
            content
        )
        
        get_result = generator.get_bundle(bundle.bundle_id)
        retrieved = get_result.unwrap()
        artifact = retrieved.artifacts[0]
        
        assert artifact.content == content


@pytest.mark.ac("FR-004-02")
class TestBundleSerialization:
    """Test AC-FR-004-02: JSON serialization and integrity"""
    
    def test_serialize_bundle_to_json(self):
        """Bundle should serialize to JSON."""
        generator = EvidenceBundleGenerator()
        bundle_result = generator.create_bundle("AC-TEST-001")
        bundle = bundle_result.unwrap()
        
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.METADATA,
            {"key": "value"}
        )
        generator.finalize_bundle(bundle.bundle_id)
        
        finalized = generator.get_bundle(bundle.bundle_id).unwrap()
        serialize_result = generator.serialize_bundle(finalized)
        
        assert serialize_result.is_ok()
        json_str = serialize_result.unwrap()
        
        # Should be valid JSON
        data = json.loads(json_str)
        assert data["ac_id"] == "AC-TEST-001"
        assert len(data["artifacts"]) == 1
    
    def test_deserialize_bundle_from_json(self):
        """Bundle should deserialize from JSON."""
        generator = EvidenceBundleGenerator()
        
        # Create and serialize
        bundle_result = generator.create_bundle("AC-TEST-001")
        bundle = bundle_result.unwrap()
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.METADATA,
            {"original": "content"}
        )
        generator.finalize_bundle(bundle.bundle_id)
        finalized = generator.get_bundle(bundle.bundle_id).unwrap()
        
        json_str = generator.serialize_bundle(finalized).unwrap()
        
        # Deserialize
        deserialize_result = generator.deserialize_bundle(json_str)
        
        assert deserialize_result.is_ok()
        restored = deserialize_result.unwrap()
        assert restored.ac_id == "AC-TEST-001"
        assert len(restored.artifacts) == 1
        assert restored.artifacts[0].content == {"original": "content"}
    
    def test_serialization_roundtrip(self):
        """Serialize and deserialize should be idempotent."""
        generator = EvidenceBundleGenerator()
        
        # Create bundle with artifacts
        bundle_result = generator.create_bundle("AC-TEST-001", phase_id="PHASE-01")
        bundle = bundle_result.unwrap()
        
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.TEST_RESULT,
            {"tests": 5, "passed": 5}
        )
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.CONFIGURATION,
            {"env": "test", "debug": True}
        )
        
        generator.finalize_bundle(bundle.bundle_id)
        original = generator.get_bundle(bundle.bundle_id).unwrap()
        
        # Serialize
        json_str1 = generator.serialize_bundle(original).unwrap()
        
        # Deserialize and re-serialize
        restored = generator.deserialize_bundle(json_str1).unwrap()
        json_str2 = generator.serialize_bundle(restored).unwrap()
        
        # Should produce same JSON
        data1 = json.loads(json_str1)
        data2 = json.loads(json_str2)
        
        assert data1 == data2
    
    def test_json_includes_all_metadata(self):
        """JSON should include all bundle metadata."""
        generator = EvidenceBundleGenerator()
        
        bundle_result = generator.create_bundle(
            "AC-TEST-001",
            phase_id="PHASE-01",
            evidence_level=EvidenceLevel.HIGH
        )
        bundle = bundle_result.unwrap()
        
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.METADATA,
            {"data": "test"}
        )
        
        generator.finalize_bundle(bundle.bundle_id)
        finalized = generator.get_bundle(bundle.bundle_id).unwrap()
        
        json_str = generator.serialize_bundle(finalized).unwrap()
        data = json.loads(json_str)
        
        assert "bundle_id" in data
        assert "ac_id" in data
        assert "phase_id" in data
        assert "artifacts" in data
        assert "bundle_hash" in data
        assert "capture_time_ms" in data
        assert "evidence_level" in data
        assert "artifact_count" in data


@pytest.mark.ac("FR-004-02")
class TestBundleIntegrity:
    """Test AC-FR-004-02: Integrity verification"""
    
    def test_bundle_hash_computed_on_finalize(self):
        """Bundle hash should be computed when finalized."""
        generator = EvidenceBundleGenerator()
        
        bundle_result = generator.create_bundle("AC-TEST-001")
        bundle = bundle_result.unwrap()
        
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.METADATA,
            {"key": "value"}
        )
        
        assert bundle.bundle_hash is None
        
        generator.finalize_bundle(bundle.bundle_id)
        finalized = generator.get_bundle(bundle.bundle_id).unwrap()
        
        assert finalized.bundle_hash is not None
        assert len(finalized.bundle_hash) == 64  # SHA-256 hex digest
    
    def test_artifact_hash_computed_on_add(self):
        """Artifact hash should be computed when added."""
        generator = EvidenceBundleGenerator()
        
        bundle_result = generator.create_bundle("AC-TEST-001")
        bundle = bundle_result.unwrap()
        
        artifact_result = generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.METADATA,
            {"key": "value"}
        )
        
        artifact = artifact_result.unwrap()
        assert artifact.content_hash is not None
        assert len(artifact.content_hash) == 64  # SHA-256 hex digest
    
    def test_verify_bundle_integrity_succeeds(self):
        """Bundle integrity verification should succeed for valid bundles."""
        generator = EvidenceBundleGenerator()
        
        bundle_result = generator.create_bundle("AC-TEST-001")
        bundle = bundle_result.unwrap()
        
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.METADATA,
            {"key": "value"}
        )
        
        generator.finalize_bundle(bundle.bundle_id)
        finalized = generator.get_bundle(bundle.bundle_id).unwrap()
        
        verify_result = generator.verify_bundle_integrity(finalized)
        
        assert verify_result.is_ok()
        assert verify_result.unwrap() is True
    
    def test_verify_artifact_integrity_succeeds(self):
        """Artifact integrity verification should succeed."""
        generator = EvidenceBundleGenerator()
        
        bundle_result = generator.create_bundle("AC-TEST-001")
        bundle = bundle_result.unwrap()
        
        artifact_result = generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.METADATA,
            {"key": "value"}
        )
        
        artifact = artifact_result.unwrap()
        verify_result = generator.verify_artifact_integrity(artifact)
        
        assert verify_result.is_ok()
        assert verify_result.unwrap() is True
    
    def test_different_content_produces_different_hash(self):
        """Different content should produce different hashes."""
        generator1 = EvidenceBundleGenerator()
        
        bundle1_result = generator1.create_bundle("AC-TEST-001")
        bundle1 = bundle1_result.unwrap()
        generator1.add_artifact(
            bundle1.bundle_id,
            ArtifactType.METADATA,
            {"key": "value1"}
        )
        generator1.finalize_bundle(bundle1.bundle_id)
        
        generator2 = EvidenceBundleGenerator()
        
        bundle2_result = generator2.create_bundle("AC-TEST-001")
        bundle2 = bundle2_result.unwrap()
        generator2.add_artifact(
            bundle2.bundle_id,
            ArtifactType.METADATA,
            {"key": "value2"}
        )
        generator2.finalize_bundle(bundle2.bundle_id)
        
        finalized1 = generator1.get_bundle(bundle1.bundle_id).unwrap()
        finalized2 = generator2.get_bundle(bundle2.bundle_id).unwrap()
        
        assert finalized1.bundle_hash != finalized2.bundle_hash


class TestBundleQueryAndRetrieval:
    """Test bundle querying and retrieval"""
    
    def test_get_bundles_by_ac_id(self):
        """Should retrieve all bundles for an AC-ID."""
        generator = EvidenceBundleGenerator()
        
        # Create multiple bundles for same AC
        created_bundles = []
        for i in range(3):
            bundle_result = generator.create_bundle("AC-TEST-001")
            bundle = bundle_result.unwrap()
            generator.finalize_bundle(bundle.bundle_id)
            created_bundles.append(bundle.bundle_id)
        
        # Create bundle for different AC
        bundle_result = generator.create_bundle("AC-TEST-002")
        generator.finalize_bundle(bundle_result.unwrap().bundle_id)
        
        # Query
        result = generator.get_bundles_by_ac_id("AC-TEST-001")
        
        assert result.is_ok()
        bundles = result.unwrap()
        assert len(bundles) == 3
        assert all(b.ac_id == "AC-TEST-001" for b in bundles)
        
        # Verify the bundles we created are there
        retrieved_ids = [b.bundle_id for b in bundles]
        for bundle_id in created_bundles:
            assert bundle_id in retrieved_ids
    
    def test_get_nonexistent_bundle_fails(self):
        """Getting nonexistent bundle should fail."""
        generator = EvidenceBundleGenerator()
        
        result = generator.get_bundle("NONEXISTENT")
        
        assert result.is_err()
        assert "not found" in str(result).lower()


class TestBundlePersistence:
    """Test bundle persistence to database"""
    
    def test_bundle_persisted_to_database(self, temp_dir):
        """Finalized bundles should be persisted to database."""
        db_path = temp_dir / "governance.db"
        db_config = DatabaseConfig(db_path=db_path)
        db = DatabaseManager(db_config)
        db.initialize()
        
        generator = EvidenceBundleGenerator(db)
        
        bundle_result = generator.create_bundle("AC-TEST-001", phase_id="PHASE-01")
        bundle = bundle_result.unwrap()
        
        generator.add_artifact(
            bundle.bundle_id,
            ArtifactType.TEST_RESULT,
            {"passed": 5, "failed": 0}
        )
        
        generator.finalize_bundle(bundle.bundle_id)
        
        # Verify persistence in audit log
        query_result = db.query_audit_by_ac_id("AC-TEST-001")
        assert query_result.is_ok()
        
        entries = query_result.unwrap()
        assert len(entries) > 0
        
        # Should find evidence bundle entry
        bundle_entries = [e for e in entries if "EVIDENCE_BUNDLE" in e.get("operation", "")]
        assert len(bundle_entries) > 0
        
        db.close()
