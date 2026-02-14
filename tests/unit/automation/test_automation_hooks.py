"""
Unit tests for automation hooks.

Tests StatusUpdateHook, RecommendationGate, and RegistryValidator
for phase completion, recommendation filtering, and consistency checks.

AC_START: AC-WAVE-3-AUTOMATION-HOOKS-001
Description: Comprehensive tests for automation hooks (20 total)
"""

import tempfile
from datetime import datetime
from pathlib import Path

import pytest
import yaml

from cortex.automation.status_update_hook import StatusUpdateHook
from cortex.automation.recommendation_gate import RecommendationGate
from cortex.validation.registry_validator import RegistryValidator


class TestStatusUpdateHook:
    """Tests for StatusUpdateHook."""
    
    @pytest.fixture
    def temp_registry(self, tmp_path):
        """Create temporary registry structure."""
        registry_path = tmp_path / "cortex-registry"
        phases_dir = registry_path / "_cortex-master" / "phases" / "active"
        phases_dir.mkdir(parents=True)
        
        # Create sample phase file
        phase_file = phases_dir / "phase-test.yaml"
        phase_data = {
            "id": "phase-test",
            "status": "ACTIVE",
            "created_at": datetime.now().isoformat()
        }
        with open(phase_file, "w") as f:
            yaml.dump(phase_data, f)
            
        return registry_path
        
    def test_init_default_registry(self):
        """Test initialization with default registry path."""
        hook = StatusUpdateHook()
        assert hook.registry_path == Path("cortex-registry")
        assert hook.sla_seconds == 300
        
    def test_init_custom_registry(self, temp_registry):
        """Test initialization with custom registry path."""
        hook = StatusUpdateHook(registry_path=temp_registry, sla_seconds=60)
        assert hook.registry_path == temp_registry
        assert hook.sla_seconds == 60
        
    def test_on_phase_complete_success(self, temp_registry):
        """Test successful phase completion update."""
        hook = StatusUpdateHook(registry_path=temp_registry)
        
        result = hook.on_phase_complete(
            phase_id="phase-test",
            status="COMPLETE",
            metrics={"tests": 10, "coverage": 95}
        )
        
        assert result is True
        assert hook.get_update_count() == 1
        
        # Verify file updated
        phase_file = temp_registry / "_cortex-master" / "phases" / "active" / "phase-test.yaml"
        with open(phase_file, "r") as f:
            data = yaml.safe_load(f)
            
        assert data["status"] == "COMPLETE"
        assert "updated_at" in data
        assert data["metrics"]["tests"] == 10
        
    def test_on_phase_complete_invalid_phase_id(self, temp_registry):
        """Test error handling for empty phase_id."""
        hook = StatusUpdateHook(registry_path=temp_registry)
        
        with pytest.raises(ValueError, match="phase_id cannot be empty"):
            hook.on_phase_complete(phase_id="", status="COMPLETE")
            
    def test_on_phase_complete_invalid_status(self, temp_registry):
        """Test error handling for invalid status."""
        hook = StatusUpdateHook(registry_path=temp_registry)
        
        with pytest.raises(ValueError, match="status must be one of"):
            hook.on_phase_complete(phase_id="phase-test", status="UNKNOWN")
            
    def test_on_phase_complete_phase_not_found(self, temp_registry):
        """Test handling of non-existent phase."""
        hook = StatusUpdateHook(registry_path=temp_registry)
        
        result = hook.on_phase_complete(
            phase_id="phase-nonexistent",
            status="COMPLETE"
        )
        
        assert result is False
        assert hook.get_update_count() == 0
        
    def test_find_phase_file_in_active(self, temp_registry):
        """Test finding phase file in active directory."""
        hook = StatusUpdateHook(registry_path=temp_registry)
        
        phase_file = hook._find_phase_file("phase-test")
        
        assert phase_file is not None
        assert phase_file.name == "phase-test.yaml"
        assert "active" in str(phase_file)
        
    def test_find_phase_file_in_completed(self, temp_registry):
        """Test finding phase file in completed directory."""
        # Move phase to completed
        active_dir = temp_registry / "_cortex-master" / "phases" / "active"
        completed_dir = temp_registry / "_cortex-master" / "phases" / "completed"
        completed_dir.mkdir(parents=True)
        
        phase_file = active_dir / "phase-test.yaml"
        phase_file.rename(completed_dir / "phase-test.yaml")
        
        hook = StatusUpdateHook(registry_path=temp_registry)
        found = hook._find_phase_file("phase-test")
        
        assert found is not None
        assert "completed" in str(found)


class TestRecommendationGate:
    """Tests for RecommendationGate."""
    
    @pytest.fixture
    def temp_registry(self, tmp_path):
        """Create temporary registry with rejected recommendations."""
        registry_path = tmp_path / "cortex-registry"
        enh_dir = registry_path / "_cortex-master" / "enhancements"
        enh_dir.mkdir(parents=True)
        
        # Create rejected recommendations file
        rejected_file = enh_dir / "rejected_recommendations.yaml"
        rejected_data = {
            "rejected": {
                "REJ-001": {
                    "text": "Create new markdown documentation files",
                    "reason": "Violates CORE-002"
                },
                "REJ-002": {
                    "text": "Skip failing tests to save time",
                    "reason": "Violates CORE-008"
                }
            }
        }
        with open(rejected_file, "w") as f:
            yaml.dump(rejected_data, f)
            
        return registry_path
        
    def test_init_default_threshold(self):
        """Test initialization with default similarity threshold."""
        gate = RecommendationGate()
        assert gate.similarity_threshold == 0.3
        
    def test_init_custom_threshold(self, temp_registry):
        """Test initialization with custom threshold."""
        gate = RecommendationGate(registry_path=temp_registry, similarity_threshold=0.5)
        assert gate.similarity_threshold == 0.5
        
    def test_init_invalid_threshold(self):
        """Test error handling for invalid threshold."""
        with pytest.raises(ValueError, match="similarity_threshold must be in"):
            RecommendationGate(similarity_threshold=1.5)
            
    def test_check_recommendation_allowed(self, temp_registry):
        """Test recommendation that passes gate."""
        gate = RecommendationGate(registry_path=temp_registry)
        
        result = gate.check_recommendation("Implement new feature using TDD")
        
        assert result["allowed"] is True
        assert result["reason"] == "No conflicts detected"
        assert result["similarity"] == 0.0
        
    def test_check_recommendation_blocked_similar(self, temp_registry):
        """Test recommendation blocked due to similarity."""
        gate = RecommendationGate(registry_path=temp_registry, similarity_threshold=0.3)
        
        result = gate.check_recommendation("Create markdown documentation files for new features")
        
        assert result["allowed"] is False
        assert "Similar to rejected recommendation" in result["reason"]
        assert result["matched_id"] == "REJ-001"
        assert result["similarity"] > 0.3
        
    def test_check_recommendation_empty(self, temp_registry):
        """Test error handling for empty recommendation."""
        gate = RecommendationGate(registry_path=temp_registry)
        
        result = gate.check_recommendation("")
        
        assert result["allowed"] is False
        assert result["reason"] == "Empty recommendation"
        
    def test_calculate_similarity_identical(self, temp_registry):
        """Test similarity calculation for identical texts."""
        gate = RecommendationGate(registry_path=temp_registry)
        
        similarity = gate._calculate_similarity("test text", "test text")
        
        assert similarity == 1.0
        
    def test_calculate_similarity_different(self, temp_registry):
        """Test similarity calculation for different texts."""
        gate = RecommendationGate(registry_path=temp_registry)
        
        similarity = gate._calculate_similarity("foo bar", "baz qux")
        
        assert similarity == 0.0
        
    def test_get_stats(self, temp_registry):
        """Test gate statistics tracking."""
        gate = RecommendationGate(registry_path=temp_registry)
        
        gate.check_recommendation("Implement feature A")
        gate.check_recommendation("Create markdown documentation files")
        
        stats = gate.get_stats()
        
        assert stats["check_count"] == 2
        assert stats["blocked_count"] == 1
        assert stats["pass_rate"] == 50


class TestRegistryValidator:
    """Tests for RegistryValidator."""
    
    @pytest.fixture
    def temp_registry(self, tmp_path):
        """Create temporary registry structure."""
        registry_path = tmp_path / "cortex-registry"
        phases_dir = registry_path / "_cortex-master" / "phases" / "active"
        phases_dir.mkdir(parents=True)
        
        enh_dir = registry_path / "_cortex-master" / "enhancements"
        enh_dir.mkdir(parents=True)
        
        # Create valid phase
        phase_file = phases_dir / "phase-valid.yaml"
        phase_data = {
            "id": "phase-valid",
            "status": "ACTIVE",
            "updated_at": datetime.now().isoformat(),
            "enhancements": ["ENH-001"]
        }
        with open(phase_file, "w") as f:
            yaml.dump(phase_data, f)
            
        # Create enhancement
        enh_file = enh_dir / "enh-001.yaml"
        enh_data = {"id": "ENH-001", "title": "Test Enhancement"}
        with open(enh_file, "w") as f:
            yaml.dump(enh_data, f)
            
        return registry_path
        
    def test_init_default_staleness(self):
        """Test initialization with default staleness threshold."""
        validator = RegistryValidator()
        assert validator.staleness_days == 30
        
    def test_validate_phase_success(self, temp_registry):
        """Test validation of valid phase."""
        validator = RegistryValidator(registry_path=temp_registry)
        
        result = validator.validate_phase("phase-valid")
        
        assert result["valid"] is True
        assert len(result["issues"]) == 0
        assert result["stale"] is False
        
    def test_validate_phase_not_found(self, temp_registry):
        """Test validation of non-existent phase."""
        validator = RegistryValidator(registry_path=temp_registry)
        
        result = validator.validate_phase("phase-nonexistent")
        
        assert result["valid"] is False
        assert "Phase file not found" in result["issues"][0]
        
    def test_validate_phase_broken_reference(self, temp_registry):
        """Test detection of broken enhancement reference."""
        # Add phase with broken reference
        phases_dir = temp_registry / "_cortex-master" / "phases" / "active"
        phase_file = phases_dir / "phase-broken.yaml"
        phase_data = {
            "id": "phase-broken",
            "status": "ACTIVE",
            "updated_at": datetime.now().isoformat(),
            "enhancements": ["ENH-999"]  # Non-existent
        }
        with open(phase_file, "w") as f:
            yaml.dump(phase_data, f)
            
        validator = RegistryValidator(registry_path=temp_registry)
        result = validator.validate_phase("phase-broken")
        
        assert result["valid"] is False
        assert any("Broken reference" in issue for issue in result["issues"])
        
    def test_validate_registry(self, temp_registry):
        """Test validation of entire registry."""
        validator = RegistryValidator(registry_path=temp_registry)
        
        result = validator.validate_registry()
        
        assert result["valid"] is True
        assert result["phase_count"] == 1
        assert result["issue_count"] == 0
        
    def test_enhancement_exists(self, temp_registry):
        """Test enhancement existence check."""
        validator = RegistryValidator(registry_path=temp_registry)
        
        assert validator._enhancement_exists("ENH-001") is True
        assert validator._enhancement_exists("ENH-999") is False
        
    def test_get_validation_count(self, temp_registry):
        """Test validation counter."""
        validator = RegistryValidator(registry_path=temp_registry)
        
        validator.validate_phase("phase-valid")
        validator.validate_phase("phase-nonexistent")
        
        assert validator.get_validation_count() == 2
