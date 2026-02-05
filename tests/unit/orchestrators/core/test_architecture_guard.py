"""
Tests for ArchitectureGuard orchestrator - Pre-Implementation Gate.

Purpose: Ensure requests align with master plan before execution.
Authority: PHASE-24 (Architecture Integrity System)
"""

import pytest
from pathlib import Path
from datetime import datetime

from cortex.orchestrators.core.architecture_guard import (
    ArchitectureGuard,
    ValidationResult,
    ValidationType,
)


@pytest.fixture
def architecture_guard():
    """Create ArchitectureGuard instance."""
    return ArchitectureGuard()


@pytest.fixture
def mock_registry_path(tmp_path):
    """Create mock registry with test data."""
    registry_dir = tmp_path / "cortex-registry" / "_cortex-master"
    registry_dir.mkdir(parents=True)
    
    # Create mock index.yaml
    index_yaml = registry_dir / "index.yaml"
    index_yaml.write_text("""
version: "1.0"
active_phases:
  - id: "phase-24"
    name: "Architecture Integrity System"
    status: "in-progress"
    priority: "P0"
  
  - id: "phase-25"
    name: "Future Enhancement"
    status: "planned"
    priority: "P1"

completed_phases_2026:
  count: 1
  phases:
    - "phase-23-static-dashboard-generator.yaml"
""")
    
    return registry_dir


class TestArchitectureGuardAllowsAlignedRequest:
    """Test that aligned requests are allowed to proceed."""
    
    def test_request_aligned_with_active_phase(self, architecture_guard, mock_registry_path):
        """Request matches active phase → PROCEED."""
        result = architecture_guard.validate_request(
            request_description="Add brittleness scanner to architecture guard",
            intent_type="IMPLEMENT",
            scope="ArchitectureGuard",
            registry_path=mock_registry_path
        )
        
        assert result.verdict == ValidationType.PROCEED
        assert result.confidence > 0.7
        assert "phase-24" in result.aligned_phase_id
        assert result.regression_risk < 0.3
    
    def test_request_aligned_with_planned_phase(self, architecture_guard, mock_registry_path):
        """Request matches planned phase → PROCEED (with note)."""
        result = architecture_guard.validate_request(
            request_description="Implement phase-25 enhancement",
            intent_type="IMPLEMENT",
            scope="FutureEnhancement",
            registry_path=mock_registry_path
        )
        
        assert result.verdict == ValidationType.PROCEED
        assert "phase-25" in result.aligned_phase_id


class TestArchitectureGuardBlocksContradictoryRequest:
    """Test that contradictory requests are blocked."""
    
    def test_request_contradicts_completed_phase(self, architecture_guard, mock_registry_path):
        """Request contradicts completed phase commitment → BLOCK."""
        result = architecture_guard.validate_request(
            request_description="Revert dashboard generator to v2",
            intent_type="REFACTOR",
            scope="DashboardGenerator",
            registry_path=mock_registry_path
        )
        
        assert result.verdict == ValidationType.BLOCK
        assert result.regression_risk > 0.7
        assert "phase-23" in result.violation_details
        assert "completed" in result.rationale.lower()
    
    def test_request_high_regression_risk(self, architecture_guard, mock_registry_path):
        """High regression risk → BLOCK with explanation."""
        result = architecture_guard.validate_request(
            request_description="Remove all test files and disable TDD",
            intent_type="REFACTOR",
            scope="CoreInfrastructure",
            registry_path=mock_registry_path
        )
        
        assert result.verdict == ValidationType.BLOCK
        assert result.regression_risk > 0.9
        assert "high risk" in result.rationale.lower()


class TestArchitectureGuardSuggestsPhaseCreation:
    """Test phase creation suggestion logic."""
    
    def test_new_feature_without_phase(self, architecture_guard, mock_registry_path):
        """New feature with no matching phase → CREATE_PHASE."""
        result = architecture_guard.validate_request(
            request_description="Implement machine learning model training pipeline",
            intent_type="IMPLEMENT",
            scope="NewCapability",
            registry_path=mock_registry_path
        )
        
        assert result.verdict == ValidationType.CREATE_PHASE
        assert result.suggested_phase_name is not None
        assert "machine learning" in result.suggested_phase_name.lower()
        assert result.suggested_phase_priority in ["P0", "P1", "P2"]
    
    def test_significant_scope_expansion(self, architecture_guard, mock_registry_path):
        """Request significantly expands existing phase → CREATE_PHASE."""
        result = architecture_guard.validate_request(
            request_description="Add 10 new orchestrators for data processing pipeline",
            intent_type="IMPLEMENT",
            scope="DataProcessing",
            registry_path=mock_registry_path
        )
        
        assert result.verdict == ValidationType.CREATE_PHASE
        assert "expansion" in result.rationale.lower() or "significant" in result.rationale.lower()


class TestRegressionRiskCalculation:
    """Test regression risk scoring algorithm."""
    
    def test_low_risk_localized_change(self, architecture_guard):
        """Localized change to single file → Low risk."""
        risk = architecture_guard.calculate_regression_risk(
            scope="SingleFile",
            affected_phases=[],
            completed_phase_overlap=0.0,
            architectural_impact=0.1
        )
        
        assert 0.0 <= risk < 0.3
    
    def test_medium_risk_multi_component(self, architecture_guard):
        """Change affecting multiple components → Medium risk."""
        risk = architecture_guard.calculate_regression_risk(
            scope="MultiComponent",
            affected_phases=["phase-23"],
            completed_phase_overlap=0.3,
            architectural_impact=0.5
        )
        
        assert 0.3 <= risk < 0.7
    
    def test_high_risk_core_infrastructure(self, architecture_guard):
        """Change to core infrastructure with completed phase overlap → High risk."""
        risk = architecture_guard.calculate_regression_risk(
            scope="CoreInfrastructure",
            affected_phases=["phase-20", "phase-21", "phase-23"],
            completed_phase_overlap=0.8,
            architectural_impact=0.9
        )
        
        assert risk >= 0.7


class TestPhaseAlignmentDetection:
    """Test phase alignment matching logic."""
    
    def test_exact_phase_name_match(self, architecture_guard, mock_registry_path):
        """Exact phase name in request → Strong alignment."""
        result = architecture_guard.validate_request(
            request_description="Continue work on Architecture Integrity System",
            intent_type="IMPLEMENT",
            scope="ArchitectureGuard",
            registry_path=mock_registry_path
        )
        
        assert result.confidence > 0.9
        assert "phase-24" in result.aligned_phase_id
    
    def test_semantic_similarity_match(self, architecture_guard, mock_registry_path):
        """Semantically similar description → Moderate alignment."""
        result = architecture_guard.validate_request(
            request_description="Add validation layer for implementation integrity",
            intent_type="IMPLEMENT",
            scope="IntegrityValidation",
            registry_path=mock_registry_path
        )
        
        assert result.confidence > 0.5
        assert result.aligned_phase_id is not None


class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_empty_registry(self, architecture_guard, tmp_path):
        """Empty registry → CREATE_PHASE."""
        empty_registry = tmp_path / "empty"
        empty_registry.mkdir()
        (empty_registry / "index.yaml").write_text("version: '1.0'\nactive_phases: []")
        
        result = architecture_guard.validate_request(
            request_description="Implement new feature",
            intent_type="IMPLEMENT",
            scope="NewFeature",
            registry_path=empty_registry
        )
        
        assert result.verdict == ValidationType.CREATE_PHASE
    
    def test_malformed_registry(self, architecture_guard, tmp_path):
        """Malformed registry → Graceful degradation to PROCEED with warning."""
        bad_registry = tmp_path / "bad"
        bad_registry.mkdir()
        (bad_registry / "index.yaml").write_text("invalid: yaml: content:")
        
        result = architecture_guard.validate_request(
            request_description="Implement feature",
            intent_type="IMPLEMENT",
            scope="Feature",
            registry_path=bad_registry
        )
        
        # Graceful degradation: proceed with warning
        assert result.verdict in [ValidationType.PROCEED, ValidationType.CREATE_PHASE]
        assert result.warnings is not None
    
    def test_missing_registry_path(self, architecture_guard):
        """Missing registry path → Use default workspace path."""
        result = architecture_guard.validate_request(
            request_description="Implement feature",
            intent_type="IMPLEMENT",
            scope="Feature"
        )
        
        # Should not crash, should attempt to find registry
        assert result.verdict in [ValidationType.PROCEED, ValidationType.CREATE_PHASE, ValidationType.BLOCK]
