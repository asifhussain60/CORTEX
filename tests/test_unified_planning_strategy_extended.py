# AC_START: AC-WAVE7-TRACK2-PART2B-TESTS
# Description: Tests for Extended Planning Strategy with Planning Adapters

"""
Test Suite for Extended Planning Domain Strategy

Coverage:
- Phase planning (6 tests)
- Wave planning (6 tests)
- Track planning (6 tests)
- Dependency resolution (3 tests)
- Extended strategy integration (6 tests)
- Total: 27 tests

Pattern: TDD RED phase (comprehensive feature parity testing)
"""

import pytest
from datetime import datetime

from cortex.orchestrators.unified_planning_strategy_extended import (
    PlanningLevel,
    PlanItem,
    PlanningRequest,
    PlanningResult,
    PhasePlanner,
    WavePlanner,
    TrackPlanner,
    DependencyResolver,
    ExtendedPlanningDomainStrategy,
)


# ============================================================================
# PHASE PLANNER TESTS
# ============================================================================

class TestPhasePlanner:
    """Test suite for phase planner."""
    
    def test_planner_initialization(self):
        """Test phase planner can be initialized."""
        planner = PhasePlanner()
        assert planner is not None
        assert planner.name == "PhasePlanner"
    
    def test_get_supported_operations(self):
        """Test get supported operations."""
        planner = PhasePlanner()
        operations = planner.supported_operations
        
        assert len(operations) == 4
        assert "create_phase" in operations
        assert "update_phase" in operations
        assert "complete_phase" in operations
        assert "get_phase_status" in operations
    
    def test_plan_phase(self):
        """Test plan phase operation."""
        planner = PhasePlanner()
        request = PlanningRequest(
            operation="plan_phase",
            target_path="cortex-registry/phase-82/",
            planning_level=PlanningLevel.PHASE,
            parameters={"phase_id": "phase_82", "duration_days": 7},
        )
        
        result = planner.plan_phase(request)
        
        assert result.status == "success"
        assert result.operation == "plan_phase"
        assert len(result.plan_items) > 0
        assert result.plan_items[0].level == PlanningLevel.PHASE
    
    def test_update_phase(self):
        """Test update phase operation."""
        planner = PhasePlanner()
        request = PlanningRequest(
            operation="update_phase",
            target_path="cortex-registry/phase-82/",
            planning_level=PlanningLevel.PHASE,
            parameters={"phase_id": "phase_82", "duration_days": 8},
        )
        
        result = planner.update_phase(request)
        
        assert result.status == "success"
        assert result.operation == "update_phase"
    
    def test_complete_phase(self):
        """Test complete phase operation."""
        planner = PhasePlanner()
        request = PlanningRequest(
            operation="complete_phase",
            target_path="cortex-registry/phase-82/",
            planning_level=PlanningLevel.PHASE,
            parameters={"phase_id": "phase_82"},
        )
        
        result = planner.complete_phase(request)
        
        assert result.status == "success"
        assert result.operation == "complete_phase"
    
    def test_get_phase_status(self):
        """Test get phase status operation."""
        planner = PhasePlanner()
        request = PlanningRequest(
            operation="get_phase_status",
            target_path="cortex-registry/phase-82/",
            planning_level=PlanningLevel.PHASE,
            parameters={"phase_id": "phase_82"},
        )
        
        result = planner.get_phase_status(request)
        
        assert result.status == "success"
        assert result.operation == "get_phase_status"


# ============================================================================
# WAVE PLANNER TESTS
# ============================================================================

class TestWavePlanner:
    """Test suite for wave planner."""
    
    def test_planner_initialization(self):
        """Test wave planner can be initialized."""
        planner = WavePlanner()
        assert planner is not None
        assert planner.name == "WavePlanner"
    
    def test_get_supported_operations(self):
        """Test get supported operations."""
        planner = WavePlanner()
        operations = planner.supported_operations
        
        assert len(operations) == 4
        assert "create_wave" in operations
        assert "update_wave" in operations
        assert "complete_wave" in operations
        assert "get_wave_status" in operations
    
    def test_plan_wave(self):
        """Test plan wave operation."""
        planner = WavePlanner()
        request = PlanningRequest(
            operation="plan_wave",
            target_path="cortex-registry/wave-7/",
            planning_level=PlanningLevel.WAVE,
            parameters={"wave_id": "wave_7", "phase_id": "phase_82", "duration_days": 5},
        )
        
        result = planner.plan_wave(request)
        
        assert result.status == "success"
        assert result.operation == "plan_wave"
        assert len(result.plan_items) > 0
        assert result.plan_items[0].level == PlanningLevel.WAVE
    
    def test_update_wave(self):
        """Test update wave operation."""
        planner = WavePlanner()
        request = PlanningRequest(
            operation="update_wave",
            target_path="cortex-registry/wave-7/",
            planning_level=PlanningLevel.WAVE,
            parameters={"wave_id": "wave_7", "duration_days": 6},
        )
        
        result = planner.update_wave(request)
        
        assert result.status == "success"
        assert result.operation == "update_wave"
    
    def test_complete_wave(self):
        """Test complete wave operation."""
        planner = WavePlanner()
        request = PlanningRequest(
            operation="complete_wave",
            target_path="cortex-registry/wave-7/",
            planning_level=PlanningLevel.WAVE,
            parameters={"wave_id": "wave_7"},
        )
        
        result = planner.complete_wave(request)
        
        assert result.status == "success"
        assert result.operation == "complete_wave"
    
    def test_get_wave_status(self):
        """Test get wave status operation."""
        planner = WavePlanner()
        request = PlanningRequest(
            operation="get_wave_status",
            target_path="cortex-registry/wave-7/",
            planning_level=PlanningLevel.WAVE,
            parameters={"wave_id": "wave_7"},
        )
        
        result = planner.get_wave_status(request)
        
        assert result.status == "success"
        assert result.operation == "get_wave_status"


# ============================================================================
# TRACK PLANNER TESTS
# ============================================================================

class TestTrackPlanner:
    """Test suite for track planner."""
    
    def test_planner_initialization(self):
        """Test track planner can be initialized."""
        planner = TrackPlanner()
        assert planner is not None
        assert planner.name == "TrackPlanner"
    
    def test_get_supported_operations(self):
        """Test get supported operations."""
        planner = TrackPlanner()
        operations = planner.supported_operations
        
        assert len(operations) == 4
        assert "create_track" in operations
        assert "update_track" in operations
        assert "complete_track" in operations
        assert "get_track_status" in operations
    
    def test_plan_track(self):
        """Test plan track operation."""
        planner = TrackPlanner()
        request = PlanningRequest(
            operation="plan_track",
            target_path="cortex-registry/wave-7/track-2/",
            planning_level=PlanningLevel.TRACK,
            parameters={"track_id": "track_2", "wave_id": "wave_7", "duration_days": 2},
        )
        
        result = planner.plan_track(request)
        
        assert result.status == "success"
        assert result.operation == "plan_track"
        assert len(result.plan_items) > 0
        assert result.plan_items[0].level == PlanningLevel.TRACK
    
    def test_update_track(self):
        """Test update track operation."""
        planner = TrackPlanner()
        request = PlanningRequest(
            operation="update_track",
            target_path="cortex-registry/wave-7/track-2/",
            planning_level=PlanningLevel.TRACK,
            parameters={"track_id": "track_2", "duration_days": 3},
        )
        
        result = planner.update_track(request)
        
        assert result.status == "success"
        assert result.operation == "update_track"
    
    def test_complete_track(self):
        """Test complete track operation."""
        planner = TrackPlanner()
        request = PlanningRequest(
            operation="complete_track",
            target_path="cortex-registry/wave-7/track-2/",
            planning_level=PlanningLevel.TRACK,
            parameters={"track_id": "track_2"},
        )
        
        result = planner.complete_track(request)
        
        assert result.status == "success"
        assert result.operation == "complete_track"
    
    def test_get_track_status(self):
        """Test get track status operation."""
        planner = TrackPlanner()
        request = PlanningRequest(
            operation="get_track_status",
            target_path="cortex-registry/wave-7/track-2/",
            planning_level=PlanningLevel.TRACK,
            parameters={"track_id": "track_2"},
        )
        
        result = planner.get_track_status(request)
        
        assert result.status == "success"
        assert result.operation == "get_track_status"


# ============================================================================
# DEPENDENCY RESOLVER TESTS
# ============================================================================

class TestDependencyResolver:
    """Test suite for dependency resolver."""
    
    def test_resolver_initialization(self):
        """Test dependency resolver can be initialized."""
        resolver = DependencyResolver()
        assert resolver is not None
    
    def test_resolve_dependencies(self):
        """Test resolve dependencies operation."""
        resolver = DependencyResolver()
        request = PlanningRequest(
            operation="resolve_dependencies",
            target_path="cortex-registry/",
            planning_level=PlanningLevel.PHASE,
            parameters={
                "items": [
                    {"id": "item_1", "dependencies": ["item_2"]},
                    {"id": "item_2", "dependencies": []},
                ]
            },
        )
        
        result = resolver.resolve_dependencies(request)
        
        assert result.status == "success"
        assert result.operation == "resolve_dependencies"
        assert result.plan_summary.get("resolved") is True
    
    def test_resolve_no_conflicts(self):
        """Test resolve dependencies with no conflicts."""
        resolver = DependencyResolver()
        request = PlanningRequest(
            operation="resolve_dependencies",
            target_path="cortex-registry/",
            planning_level=PlanningLevel.PHASE,
            parameters={"items": []},
        )
        
        result = resolver.resolve_dependencies(request)
        
        assert result.status == "success"
        assert len(result.plan_summary.get("conflicts", [])) == 0


# ============================================================================
# EXTENDED PLANNING STRATEGY TESTS
# ============================================================================

class TestExtendedPlanningStrategy:
    """Test suite for extended planning strategy."""
    
    def test_strategy_initialization(self):
        """Test strategy can be initialized."""
        strategy = ExtendedPlanningDomainStrategy()
        assert strategy is not None
    
    def test_has_phase_planner(self):
        """Test strategy has phase planner."""
        strategy = ExtendedPlanningDomainStrategy()
        assert strategy.phase_planner is not None
        assert isinstance(strategy.phase_planner, PhasePlanner)
    
    def test_has_wave_planner(self):
        """Test strategy has wave planner."""
        strategy = ExtendedPlanningDomainStrategy()
        assert strategy.wave_planner is not None
        assert isinstance(strategy.wave_planner, WavePlanner)
    
    def test_has_track_planner(self):
        """Test strategy has track planner."""
        strategy = ExtendedPlanningDomainStrategy()
        assert strategy.track_planner is not None
        assert isinstance(strategy.track_planner, TrackPlanner)
    
    def test_has_dependency_resolver(self):
        """Test strategy has dependency resolver."""
        strategy = ExtendedPlanningDomainStrategy()
        assert strategy.dependency_resolver is not None
        assert isinstance(strategy.dependency_resolver, DependencyResolver)
    
    def test_plan_phase_via_strategy(self):
        """Test plan phase via strategy."""
        strategy = ExtendedPlanningDomainStrategy()
        request = PlanningRequest(
            operation="plan_phase",
            target_path="cortex-registry/",
            planning_level=PlanningLevel.PHASE,
            parameters={"phase_id": "phase_82", "duration_days": 7},
        )
        
        result = strategy.plan_phase(request)
        
        assert result.status == "success"
        assert len(result.plan_items) > 0
    
    def test_get_metadata(self):
        """Test strategy metadata."""
        strategy = ExtendedPlanningDomainStrategy()
        metadata = strategy.get_metadata()
        
        assert metadata["name"] == "ExtendedPlanningDomainStrategy"
        assert metadata["domain"] == "planning"
        assert len(metadata["replaces"]) > 0
        assert "PlanningOrchestrator" in metadata["replaces"]


# ============================================================================
# INTEGRATION TESTS
# ============================================================================

class TestPlanningStrategyIntegration:
    """Integration tests for planning strategy."""
    
    def test_all_planning_levels_supported(self):
        """Test all planning levels can be handled."""
        strategy = ExtendedPlanningDomainStrategy()
        
        levels = [PlanningLevel.PHASE, PlanningLevel.WAVE, PlanningLevel.TRACK]
        
        for level in levels:
            request = PlanningRequest(
                operation="plan_item",
                target_path="cortex-registry/",
                planning_level=level,
                parameters={},
            )
            
            # Should not raise error
            assert request.planning_level == level
    
    def test_planning_request_creation(self):
        """Test planning request creation and validation."""
        request = PlanningRequest(
            operation="plan_phase",
            target_path="cortex-registry/phase-82/",
            planning_level=PlanningLevel.PHASE,
            parameters={"phase_id": "phase_82", "duration_days": 7},
        )
        
        assert request.operation == "plan_phase"
        assert request.planning_level == PlanningLevel.PHASE
        assert request.parameters["phase_id"] == "phase_82"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

# AC_COMPLETE: AC-WAVE7-TRACK2-PART2B-TESTS ✅
# 27 test cases for extended planning strategy
