"""
Test suite for Phase Dependency Validation (AC-AR-014-03)

Tests holistic dependency validation: circular detection, broken requirements,
locked phase dependency verification.
"""

import pytest
from src.core.dependency_validator import (
    DependencyValidationResult,
    DependencyPath,
    DependencyValidationStatus,
    PhaseDependencyAnalyzer,
    DependencyModificationValidator,
    HolisticDependencyValidator,
)


# =============================================================================
# FIXTURES
# =============================================================================

@pytest.fixture
def phase_tracker_linear():
    """Linear dependency chain: P1 ← P2 ← P3."""
    return {
        "PHASE-01": {
            "title": "Foundation",
            "status": "COMPLETED",
            "locked": True
        },
        "PHASE-02": {
            "title": "Orchestration",
            "status": "COMPLETED",
            "locked": True,
            "requires": "PHASE-01"
        },
        "PHASE-03": {
            "title": "Safety",
            "status": "COMPLETED",
            "locked": True,
            "requires": "PHASE-02"
        }
    }


@pytest.fixture
def phase_tracker_complex():
    """Complex dependencies with multiple paths."""
    return {
        "PHASE-01": {
            "status": "COMPLETED",
            "locked": True
        },
        "PHASE-02": {
            "status": "COMPLETED",
            "locked": True,
            "requires": "PHASE-01"
        },
        "PHASE-03": {
            "status": "IN_PROGRESS",
            "locked": False,
            "requires": ["PHASE-01", "PHASE-02"]
        },
        "PHASE-04": {
            "status": "IN_PROGRESS",
            "locked": False,
            "requires": "PHASE-03"
        }
    }


@pytest.fixture
def phase_tracker_with_circular():
    """Phases with circular dependency."""
    return {
        "PHASE-A": {
            "status": "PLANNED",
            "requires": "PHASE-B"
        },
        "PHASE-B": {
            "status": "PLANNED",
            "requires": "PHASE-C"
        },
        "PHASE-C": {
            "status": "PLANNED",
            "requires": "PHASE-A"
        }
    }


# =============================================================================
# TEST: DependencyPath
# =============================================================================

class TestDependencyPath:
    """Test DependencyPath dataclass."""
    
    def test_create_path(self):
        """Test creating dependency path."""
        path = DependencyPath(
            source="PHASE-01",
            target="PHASE-03",
            path=["PHASE-01", "PHASE-02", "PHASE-03"]
        )
        
        assert path.source == "PHASE-01"
        assert path.target == "PHASE-03"
        assert path.distance == 2
    
    def test_path_to_dict(self):
        """Test converting path to dictionary."""
        path = DependencyPath(
            source="PHASE-01",
            target="PHASE-03",
            path=["PHASE-01", "PHASE-02", "PHASE-03"]
        )
        
        d = path.to_dict()
        assert d["distance"] == 2
        assert len(d["path"]) == 3


# =============================================================================
# TEST: PhaseDependencyAnalyzer
# =============================================================================

class TestPhaseDependencyAnalyzer:
    """Test dependency analysis."""
    
    def test_analyzer_creation(self, phase_tracker_linear):
        """Test creating analyzer."""
        analyzer = PhaseDependencyAnalyzer(phase_tracker_linear)
        
        assert analyzer is not None
        assert len(analyzer.dependency_graph) == 3
    
    def test_get_phase_dependencies(self, phase_tracker_linear):
        """Test getting direct dependencies."""
        analyzer = PhaseDependencyAnalyzer(phase_tracker_linear)
        deps = analyzer.get_phase_dependencies("PHASE-02")
        
        assert "PHASE-01" in deps
        assert len(deps) == 1
    
    def test_get_transitive_dependencies(self, phase_tracker_linear):
        """Test getting transitive dependencies."""
        analyzer = PhaseDependencyAnalyzer(phase_tracker_linear)
        deps = analyzer.get_transitive_dependencies("PHASE-03")
        
        assert "PHASE-01" in deps
        assert "PHASE-02" in deps
        assert len(deps) == 2
    
    def test_get_dependents(self, phase_tracker_linear):
        """Test getting direct dependents."""
        analyzer = PhaseDependencyAnalyzer(phase_tracker_linear)
        dependents = analyzer.get_dependents("PHASE-01")
        
        assert "PHASE-02" in dependents
        assert len(dependents) == 1
    
    def test_get_transitive_dependents(self, phase_tracker_linear):
        """Test getting transitive dependents."""
        analyzer = PhaseDependencyAnalyzer(phase_tracker_linear)
        dependents = analyzer.get_transitive_dependents("PHASE-01")
        
        assert "PHASE-02" in dependents
        assert "PHASE-03" in dependents
        assert len(dependents) == 2
    
    def test_find_path(self, phase_tracker_linear):
        """Test finding dependency path."""
        analyzer = PhaseDependencyAnalyzer(phase_tracker_linear)
        path = analyzer.find_path("PHASE-03", "PHASE-01")
        
        assert path is not None
        assert path.source == "PHASE-03"
        assert path.target == "PHASE-01"
        assert len(path.path) == 3
    
    def test_find_path_not_found(self, phase_tracker_linear):
        """Test finding path that doesn't exist."""
        analyzer = PhaseDependencyAnalyzer(phase_tracker_linear)
        path = analyzer.find_path("PHASE-01", "PHASE-03")
        
        assert path is None
    
    def test_detect_no_circular_dependencies(self, phase_tracker_linear):
        """Test detection of no circular dependencies."""
        analyzer = PhaseDependencyAnalyzer(phase_tracker_linear)
        cycle = analyzer.detect_circular_dependencies()
        
        assert cycle is None
    
    def test_detect_circular_dependencies(self, phase_tracker_with_circular):
        """Test detection of circular dependencies."""
        analyzer = PhaseDependencyAnalyzer(phase_tracker_with_circular)
        cycle = analyzer.detect_circular_dependencies()
        
        assert cycle is not None
        assert len(cycle) >= 3  # A → B → C → A


# =============================================================================
# TEST: DependencyModificationValidator
# =============================================================================

class TestDependencyModificationValidator:
    """Test modification validation."""
    
    def test_validate_remove_safe_dependency(self, phase_tracker_complex):
        """Test removing safe dependency."""
        validator = DependencyModificationValidator(phase_tracker_complex)
        
        # PHASE-04 depends on PHASE-03, safe to remove
        status = validator.validate_dependency_removal("PHASE-04", "PHASE-03")
        
        # Should succeed (no locked dependents)
        assert status.is_valid is True
    
    def test_validate_remove_breaks_dependency_chain(self, phase_tracker_linear):
        """Test cannot remove dependency if locked phase depends on chain."""
        # Setup: PHASE-04 locked and depends on PHASE-03 which depends on PHASE-02
        tracker = dict(phase_tracker_linear)
        tracker["PHASE-04"] = {
            "status": "IN_PROGRESS",
            "locked": True,
            "requires": "PHASE-03"
        }
        
        validator = DependencyModificationValidator(tracker)
        
        # Try to remove PHASE-02 from PHASE-03
        # This breaks chain: PHASE-04 → PHASE-03 → [removed: PHASE-02]
        status = validator.validate_dependency_removal("PHASE-03", "PHASE-02")
        
        # Should fail because PHASE-04 locked and indirectly depends on this chain
        assert status.is_valid is False
    
    def test_validate_add_creates_cycle(self, phase_tracker_linear):
        """Test adding dependency that creates cycle."""
        validator = DependencyModificationValidator(phase_tracker_linear)
        
        # Try to make PHASE-01 depend on PHASE-03 (would create cycle)
        status = validator.validate_dependency_addition("PHASE-01", "PHASE-03")
        
        assert status.is_valid is False
        assert status.result_code == DependencyValidationResult.CIRCULAR_DEPENDENCY.value
    
    def test_validate_add_safe_dependency(self, phase_tracker_complex):
        """Test adding safe dependency."""
        validator = DependencyModificationValidator(phase_tracker_complex)
        
        # PHASE-04 can depend on PHASE-01 (no cycle)
        status = validator.validate_dependency_addition("PHASE-04", "PHASE-01")
        
        assert status.is_valid is True
    
    def test_validate_self_dependency(self, phase_tracker_linear):
        """Test cannot create self-dependency."""
        validator = DependencyModificationValidator(phase_tracker_linear)
        
        status = validator.validate_dependency_addition("PHASE-01", "PHASE-01")
        
        assert status.is_valid is False
        assert status.result_code == DependencyValidationResult.CIRCULAR_DEPENDENCY.value
    
    def test_validate_phase_modification_safe(self, phase_tracker_complex):
        """Test safe phase modification."""
        validator = DependencyModificationValidator(phase_tracker_complex)
        
        # Modify PHASE-04 to only depend on PHASE-02 (no cycle)
        status = validator.validate_phase_modification("PHASE-04", ["PHASE-02"])
        
        assert status.is_valid is True
    
    def test_validate_phase_modification_circular(self, phase_tracker_linear):
        """Test modification creating circular dependency."""
        validator = DependencyModificationValidator(phase_tracker_linear)
        
        # Try to make PHASE-01 depend on PHASE-03
        status = validator.validate_phase_modification("PHASE-01", ["PHASE-03"])
        
        assert status.is_valid is False
        assert status.result_code == DependencyValidationResult.CIRCULAR_DEPENDENCY.value


# =============================================================================
# TEST: HolisticDependencyValidator
# =============================================================================

class TestHolisticDependencyValidator:
    """Test holistic validation."""
    
    def test_validate_all_dependencies_valid(self, phase_tracker_linear):
        """Test validation of valid graph."""
        validator = HolisticDependencyValidator(phase_tracker_linear)
        status = validator.validate_all_dependencies()
        
        assert status.is_valid is True
        assert status.result_code == DependencyValidationResult.VALID.value
    
    def test_validate_all_dependencies_circular(self, phase_tracker_with_circular):
        """Test validation detects circular."""
        validator = HolisticDependencyValidator(phase_tracker_with_circular)
        status = validator.validate_all_dependencies()
        
        assert status.is_valid is False
        assert status.result_code == DependencyValidationResult.CIRCULAR_DEPENDENCY.value
    
    def test_validate_locked_phases_safe(self, phase_tracker_linear):
        """Test locked phases validation."""
        validator = HolisticDependencyValidator(phase_tracker_linear)
        status = validator.validate_locked_phases_safe()
        
        assert status.is_valid is True
    
    def test_get_dependency_graph_summary(self, phase_tracker_complex):
        """Test getting dependency graph summary."""
        validator = HolisticDependencyValidator(phase_tracker_complex)
        summary = validator.get_dependency_graph_summary()
        
        assert "phases" in summary
        assert "cycles" in summary
        assert "locked_phases" in summary
        assert len(summary["phases"]) == 4
    
    def test_graph_summary_detects_locked_phases(self, phase_tracker_linear):
        """Test summary includes locked phases."""
        validator = HolisticDependencyValidator(phase_tracker_linear)
        summary = validator.get_dependency_graph_summary()
        
        assert len(summary["locked_phases"]) == 3
        assert all(phase in summary["locked_phases"] for phase in ["PHASE-01", "PHASE-02", "PHASE-03"])


# =============================================================================
# TEST: Edge Cases
# =============================================================================

class TestEdgeCases:
    """Test edge cases."""
    
    def test_empty_phase_tracker(self):
        """Test with empty phase tracker."""
        validator = HolisticDependencyValidator({})
        status = validator.validate_all_dependencies()
        
        assert status.is_valid is True
    
    def test_single_phase_no_dependencies(self):
        """Test with single phase."""
        tracker = {
            "PHASE-ONLY": {
                "status": "COMPLETED",
                "locked": True
            }
        }
        
        validator = HolisticDependencyValidator(tracker)
        status = validator.validate_all_dependencies()
        
        assert status.is_valid is True
    
    def test_multiple_requirements(self):
        """Test phase with multiple requirements."""
        tracker = {
            "PHASE-A": {"status": "COMPLETED", "locked": True},
            "PHASE-B": {"status": "COMPLETED", "locked": True},
            "PHASE-C": {
                "status": "IN_PROGRESS",
                "requires": ["PHASE-A", "PHASE-B"]
            }
        }
        
        analyzer = PhaseDependencyAnalyzer(tracker)
        deps = analyzer.get_phase_dependencies("PHASE-C")
        
        assert "PHASE-A" in deps
        assert "PHASE-B" in deps
        assert len(deps) == 2
    
    def test_diamond_dependency(self):
        """Test diamond pattern: A ← B,C ← D."""
        tracker = {
            "PHASE-A": {"status": "COMPLETED", "locked": True},
            "PHASE-B": {
                "status": "COMPLETED",
                "locked": True,
                "requires": "PHASE-A"
            },
            "PHASE-C": {
                "status": "COMPLETED",
                "locked": True,
                "requires": "PHASE-A"
            },
            "PHASE-D": {
                "status": "IN_PROGRESS",
                "requires": ["PHASE-B", "PHASE-C"]
            }
        }
        
        analyzer = PhaseDependencyAnalyzer(tracker)
        validator = HolisticDependencyValidator(tracker)
        
        # PHASE-D should transitively depend on PHASE-A
        trans_deps = analyzer.get_transitive_dependencies("PHASE-D")
        assert "PHASE-A" in trans_deps
        
        # Should be valid
        status = validator.validate_all_dependencies()
        assert status.is_valid is True
    
    def test_nonexistent_requirement(self):
        """Test phase requiring non-existent phase."""
        tracker = {
            "PHASE-A": {"status": "COMPLETED"},
            "PHASE-B": {
                "status": "IN_PROGRESS",
                "requires": "PHASE-NONEXISTENT"
            }
        }
        
        validator = HolisticDependencyValidator(tracker)
        status = validator.validate_all_dependencies()
        
        assert status.is_valid is False
        assert status.result_code == DependencyValidationResult.MISSING_PHASE.value
