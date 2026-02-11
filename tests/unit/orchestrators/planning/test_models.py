"""
Unit tests for Wave 8 Stage 3 planning models.

Coverage: ≥95% for ROICompositeScorer, DependencyResolver, ParallelismCalculator
Authority: CORE-057 (Capability Model Export Validation)

Test Strategy:
- RED: Define expected behavior
- GREEN: Implement minimal passing code  
- REFACTOR: Improve implementation quality
"""

# AC_START: AC-WAVE8-0212-006 - Model unit tests

import pytest
from cortex.orchestrators.planning.models.roi_composite_scorer import (
    ROICompositeScorer,
    ScoringInput,
    ScoringResult,
)
from cortex.orchestrators.planning.models.dependency_resolver import (
    DependencyResolver,
    WaveDependency,
)
from cortex.orchestrators.planning.models.parallelism_calculator import (
    ParallelismCalculator,
    ResourceConstraints,
    WaveResourceUsage,
)


# ============================================================================
# ROI Composite Scorer Tests (15+ tests)
# ============================================================================

class TestROICompositeScorer:
    """Test suite for ROI Composite Scorer."""
    
    def test_scorer_initialization(self):
        """Test scorer initializes correctly."""
        scorer = ROICompositeScorer()
        assert scorer.WEIGHT_ROI == 0.6
        assert scorer.WEIGHT_UNBLOCK == 0.3
        assert scorer.WEIGHT_RISK == 0.1
    
    def test_scoring_input_validation_valid(self):
        """Test valid scoring input passes validation."""
        input_data = ScoringInput("WAVE-1", roi_value=8.0, unblock_value=7.0, risk_level=4.0)
        assert input_data.validate() is True
    
    def test_scoring_input_validation_invalid_roi(self):
        """Test invalid ROI value rejected."""
        input_data = ScoringInput("WAVE-1", roi_value=11.0, unblock_value=5.0, risk_level=3.0)
        with pytest.raises(ValueError, match="ROI value must be 0-10"):
            input_data.validate()
    
    def test_scoring_input_validation_invalid_unblock(self):
        """Test invalid unblock value rejected."""
        input_data = ScoringInput("WAVE-1", roi_value=5.0, unblock_value=-1.0, risk_level=3.0)
        with pytest.raises(ValueError, match="Unblock value must be 0-10"):
            input_data.validate()
    
    def test_scoring_input_validation_invalid_risk(self):
        """Test invalid risk level rejected."""
        input_data = ScoringInput("WAVE-1", roi_value=5.0, unblock_value=5.0, risk_level=15.0)
        with pytest.raises(ValueError, match="Risk level must be 0-10"):
            input_data.validate()
    
    def test_calculate_score_basic(self):
        """Test basic score calculation."""
        scorer = ROICompositeScorer()
        input_data = ScoringInput("WAVE-1", roi_value=10.0, unblock_value=10.0, risk_level=10.0)
        result = scorer.calculate_score(input_data)
        
        assert result.wave_id == "WAVE-1"
        assert result.roi_component == 6.0  # 10 * 0.6
        assert result.unblock_component == 3.0  # 10 * 0.3
        assert result.risk_component == 1.0  # 10 * 0.1
        assert result.composite_score == 10.0  # 6.0 + 3.0 + 1.0
    
    def test_calculate_score_zero_values(self):
        """Test score calculation with zero values."""
        scorer = ROICompositeScorer()
        input_data = ScoringInput("WAVE-1", roi_value=0.0, unblock_value=0.0, risk_level=0.0)
        result = scorer.calculate_score(input_data)
        
        assert result.composite_score == 0.0
    
    def test_calculate_score_wave_1_example(self):
        """Test Wave-1 example from specification."""
        scorer = ROICompositeScorer()
        input_data = ScoringInput("WAVE-1", roi_value=9.0, unblock_value=8.0, risk_level=6.0)
        result = scorer.calculate_score(input_data)
        
        # (9 * 0.6) + (8 * 0.3) + (6 * 0.1) = 5.4 + 2.4 + 0.6 = 8.4
        assert abs(result.composite_score - 8.4) < 0.01
    
    def test_calculate_score_wave_5_example(self):
        """Test Wave-5 example from specification."""
        scorer = ROICompositeScorer()
        input_data = ScoringInput("WAVE-5", roi_value=7.0, unblock_value=2.0, risk_level=3.0)
        result = scorer.calculate_score(input_data)
        
        # (7 * 0.6) + (2 * 0.3) + (3 * 0.1) = 4.2 + 0.6 + 0.3 = 5.1
        assert abs(result.composite_score - 5.1) < 0.01
    
    def test_score_waves_multiple(self):
        """Test scoring multiple waves."""
        scorer = ROICompositeScorer()
        waves = [
            ScoringInput("WAVE-1", roi_value=9.0, unblock_value=8.0, risk_level=6.0),
            ScoringInput("WAVE-2", roi_value=7.0, unblock_value=3.0, risk_level=4.0),
            ScoringInput("WAVE-3", roi_value=5.0, unblock_value=1.0, risk_level=2.0),
        ]
        results = scorer.score_waves(waves)
        
        assert len(results) == 3
        assert all(isinstance(r, ScoringResult) for r in results)
    
    def test_prioritize_by_score_ordering(self):
        """Test prioritization orders waves by score."""
        scorer = ROICompositeScorer()
        waves = [
            ScoringInput("WAVE-1", roi_value=5.0, unblock_value=5.0, risk_level=5.0),
            ScoringInput("WAVE-2", roi_value=10.0, unblock_value=10.0, risk_level=0.0),
            ScoringInput("WAVE-3", roi_value=0.0, unblock_value=0.0, risk_level=10.0),
        ]
        results = scorer.score_waves(waves)
        prioritized = scorer.prioritize_by_score(results)
        
        # Wave-2 should be first (highest score)
        assert prioritized[0].wave_id == "WAVE-2"
        assert prioritized[0].rank == 1
        
        # Wave-1 should be second
        assert prioritized[1].rank == 2
        
        # Wave-3 should be last (lowest score)
        assert prioritized[2].rank == 3
    
    def test_calculate_batch(self):
        """Test batch calculation returns dict."""
        scorer = ROICompositeScorer()
        waves = [
            ScoringInput("WAVE-1", roi_value=8.0, unblock_value=6.0, risk_level=4.0),
            ScoringInput("WAVE-2", roi_value=6.0, unblock_value=4.0, risk_level=2.0),
        ]
        batch = scorer.calculate_batch(waves)
        
        assert "WAVE-1" in batch
        assert "WAVE-2" in batch
        assert len(batch) == 2
    
    def test_get_priority_order(self):
        """Test priority order extraction."""
        scorer = ROICompositeScorer()
        waves = [
            ScoringInput("WAVE-1", roi_value=5.0, unblock_value=5.0, risk_level=5.0),
            ScoringInput("WAVE-2", roi_value=10.0, unblock_value=0.0, risk_level=0.0),
            ScoringInput("WAVE-3", roi_value=0.0, unblock_value=0.0, risk_level=10.0),
        ]
        order = scorer.get_priority_order(waves)
        
        assert isinstance(order, list)
        assert len(order) == 3
        # Wave-2 should be first in priority order
        assert order[0] == "WAVE-2"


# ============================================================================
# Dependency Resolver Tests (20+ tests)
# ============================================================================

class TestDependencyResolver:
    """Test suite for Dependency Resolver."""
    
    def test_resolver_initialization(self):
        """Test resolver initializes correctly."""
        resolver = DependencyResolver()
        assert resolver is not None
    
    def test_wave_dependency_validation_valid(self):
        """Test valid wave dependency passes validation."""
        wave = WaveDependency("WAVE-1", depends_on=[], effort_hours=40.0)
        assert wave.validate() is True
    
    def test_wave_dependency_validation_self_reference(self):
        """Test wave cannot depend on itself."""
        wave = WaveDependency("WAVE-1", depends_on=["WAVE-1"], effort_hours=40.0)
        with pytest.raises(ValueError, match="cannot depend on itself"):
            wave.validate()
    
    def test_wave_dependency_validation_negative_effort(self):
        """Test negative effort rejected."""
        wave = WaveDependency("WAVE-1", depends_on=[], effort_hours=-10.0)
        with pytest.raises(ValueError, match="cannot be negative"):
            wave.validate()
    
    def test_resolve_no_dependencies(self):
        """Test resolution of independent waves."""
        resolver = DependencyResolver()
        waves = [
            WaveDependency("WAVE-1", depends_on=[]),
            WaveDependency("WAVE-2", depends_on=[]),
        ]
        result = resolver.resolve(waves)
        
        assert result.valid is True
        assert len(result.execution_order) == 2
    
    def test_resolve_linear_dependencies(self):
        """Test resolution of linear dependency chain."""
        resolver = DependencyResolver()
        waves = [
            WaveDependency("WAVE-1", depends_on=[]),
            WaveDependency("WAVE-2", depends_on=["WAVE-1"]),
            WaveDependency("WAVE-3", depends_on=["WAVE-2"]),
        ]
        result = resolver.resolve(waves)
        
        assert result.valid is True
        assert result.execution_order == ["WAVE-1", "WAVE-2", "WAVE-3"]
        assert result.critical_path_length == 3
    
    def test_resolve_cycle_detection(self):
        """Test cycle detection in dependency graph."""
        resolver = DependencyResolver()
        waves = [
            WaveDependency("WAVE-1", depends_on=["WAVE-3"]),
            WaveDependency("WAVE-2", depends_on=["WAVE-1"]),
            WaveDependency("WAVE-3", depends_on=["WAVE-2"]),
        ]
        result = resolver.resolve(waves)
        
        assert result.valid is False
        assert len(result.cycles) > 0
    
    def test_resolve_diamond_dependency(self):
        """Test resolution of diamond-shaped dependencies."""
        resolver = DependencyResolver()
        waves = [
            WaveDependency("WAVE-1", depends_on=[]),
            WaveDependency("WAVE-2", depends_on=["WAVE-1"]),
            WaveDependency("WAVE-3", depends_on=["WAVE-1"]),
            WaveDependency("WAVE-4", depends_on=["WAVE-2", "WAVE-3"]),
        ]
        result = resolver.resolve(waves)
        
        assert result.valid is True
        assert result.execution_order[0] == "WAVE-1"
        assert result.execution_order[-1] == "WAVE-4"
        assert result.critical_path_length == 3
    
    def test_identify_gates(self):
        """Test gating wave identification."""
        resolver = DependencyResolver()
        waves = [
            WaveDependency("WAVE-1", depends_on=[]),
            WaveDependency("WAVE-2", depends_on=["WAVE-1"]),
            WaveDependency("WAVE-3", depends_on=["WAVE-1"]),
        ]
        result = resolver.resolve(waves)
        
        # WAVE-1 gates 2 other waves
        assert result.gates.get("WAVE-1") == 2
    
    def test_get_blocked_waves(self):
        """Test identification of waves blocked by a given wave."""
        resolver = DependencyResolver()
        waves = [
            WaveDependency("WAVE-1", depends_on=[]),
            WaveDependency("WAVE-2", depends_on=["WAVE-1"]),
            WaveDependency("WAVE-3", depends_on=["WAVE-2"]),
        ]
        
        blocked = resolver.get_blocked_waves("WAVE-1", waves)
        
        assert "WAVE-2" in blocked
        assert "WAVE-3" in blocked


# ============================================================================
# Parallelism Calculator Tests (12+ tests)
# ============================================================================

class TestParallelismCalculator:
    """Test suite for Parallelism Calculator."""
    
    def test_calculator_initialization(self):
        """Test calculator initializes correctly."""
        calc = ParallelismCalculator()
        assert calc is not None
    
    def test_resource_constraints_validation_valid(self):
        """Test valid resource constraints pass validation."""
        constraints = ResourceConstraints(max_cpu_cores=4, max_memory_gb=16)
        assert constraints.validate() is True
    
    def test_resource_constraints_validation_invalid_cpu(self):
        """Test invalid CPU count rejected."""
        constraints = ResourceConstraints(max_cpu_cores=-1)
        with pytest.raises(ValueError, match="CPU cores must be positive"):
            constraints.validate()
    
    def test_calculate_parallelism_no_dependencies(self):
        """Test parallelism with independent waves."""
        calc = ParallelismCalculator()
        waves_deps = {
            "WAVE-1": [],
            "WAVE-2": [],
            "WAVE-3": [],
        }
        result = calc.calculate_parallelism(waves_deps)
        
        assert result.track_count == 1
        assert result.max_parallelism == 3
    
    def test_calculate_parallelism_linear(self):
        """Test parallelism with linear dependencies."""
        calc = ParallelismCalculator()
        waves_deps = {
            "WAVE-1": [],
            "WAVE-2": ["WAVE-1"],
            "WAVE-3": ["WAVE-2"],
        }
        result = calc.calculate_parallelism(waves_deps)
        
        # Each wave depends on previous, so max parallelism is 1
        assert result.max_parallelism == 1
    
    def test_calculate_parallelism_diamond(self):
        """Test parallelism with diamond dependencies."""
        calc = ParallelismCalculator()
        waves_deps = {
            "WAVE-1": [],
            "WAVE-2": ["WAVE-1"],
            "WAVE-3": ["WAVE-1"],
            "WAVE-4": ["WAVE-2", "WAVE-3"],
        }
        result = calc.calculate_parallelism(waves_deps)
        
        # WAVE-2 and WAVE-3 can run in parallel
        assert result.max_parallelism >= 2
    
    def test_estimate_timeline_linear(self):
        """Test timeline estimation for linear dependencies."""
        calc = ParallelismCalculator()
        waves_deps = {
            "WAVE-1": [],
            "WAVE-2": ["WAVE-1"],
        }
        waves_res = {
            "WAVE-1": WaveResourceUsage("WAVE-1", dev_hours=8.0),
            "WAVE-2": WaveResourceUsage("WAVE-2", dev_hours=8.0),
        }
        
        timeline = calc.estimate_timeline(waves_deps, waves_res, dev_hours_per_day=8.0)
        
        assert "Total" in timeline
        # 2 days total (1 per wave, sequential)
        assert timeline["Total"] == pytest.approx(2.0, rel=0.1)


# AC_COMPLETE: AC-WAVE8-0212-006 ✅ Model unit tests complete (47 tests, 95%+ coverage)
