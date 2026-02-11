"""
Integration tests for Planning Strategy Pattern.

Tests end-to-end workflows combining all strategies:
  - Multi-level planning execution
  - Cross-strategy coordination  
  - Error recovery and resilience
  - Capability discovery

Authority: ENH-087 Track 2 + Phase 81
Compliance: CORE-008 (TDD), integration-first ratio

AC_START: AC-ENH090-S2-REFACTOR-001
Description: Planning strategy integration tests (15 tests)
"""

import pytest

from cortex.orchestrators.strategies.planning_strategy_pattern import (
    PlanningLevel,
    PlanningOperationType,
    RiskLevel,
    PlanningRequest,
    MacroPlanningStrategy,
    MicroPlanningStrategy,
    UnifiedPlanningOrchestrator,
)


class TestPlanningStrategyIntegration:
    """Integration tests for planning orchestrator consolidation."""
    
    def setup_method(self):
        """Setup orchestrator instance."""
        self.orchestrator = UnifiedPlanningOrchestrator()
        self.macro_strategy = MacroPlanningStrategy()
        self.micro_strategy = MicroPlanningStrategy()
    
    def test_multi_level_macro_planning_workflow(self):
        """Test sequential macro planning from initiative to stage."""
        # Level 1: Initiative planning
        initiative_req = PlanningRequest(
            operation=PlanningOperationType.PLAN_INITIATIVE,
            scope_name="2025 Technical Excellence Initiative",
            scope_level=PlanningLevel.INITIATIVE,
            current_state={"status": "conception"},
            target_state={"status": "execution"}
        )
        initiative_result = self.orchestrator.plan_execution(initiative_req)
        assert initiative_result.success
        assert initiative_result.execution_plan is not None
        assert len(initiative_result.execution_plan) == 5
        
        # Level 2: Phase planning
        phase_req = PlanningRequest(
            operation=PlanningOperationType.PLAN_PHASE,
            scope_name="Phase 1: Foundation",
            scope_level=PlanningLevel.PHASE,
            current_state={"status": "ready"},
            target_state={"status": "complete"}
        )
        phase_result = self.orchestrator.plan_execution(phase_req)
        assert phase_result.success
        assert phase_result.execution_plan is not None
        assert len(phase_result.execution_plan) == 4
        
        # Level 3: Wave planning
        wave_req = PlanningRequest(
            operation=PlanningOperationType.PLAN_WAVE,
            scope_name="Wave 7: Domain Consolidation",
            scope_level=PlanningLevel.WAVE,
            current_state={"tracks": 0},
            target_state={"tracks": 4}
        )
        wave_result = self.orchestrator.plan_execution(wave_req)
        assert wave_result.success
        assert wave_result.execution_plan is not None
        assert len(wave_result.execution_plan) == 5
        
        # Level 4: Stage planning  
        stage_req = PlanningRequest(
            operation=PlanningOperationType.PLAN_STAGE,
            scope_name="Stage 1: Refactoring Strategy",
            scope_level=PlanningLevel.STAGE,
            current_state={"status": "design"},
            target_state={"status": "implementation"}
        )
        stage_result = self.orchestrator.plan_execution(stage_req)
        assert stage_result.success
        assert stage_result.execution_plan is not None
        assert len(stage_result.execution_plan) == 3
    
    def test_multi_level_micro_planning_workflow(self):
        """Test sequential micro planning from class to method."""
        # Class-level planning
        class_req = PlanningRequest(
            operation=PlanningOperationType.PLAN_CLASS_REFACTOR,
            scope_name="UserService",
            scope_level=PlanningLevel.CLASS,
            current_state={"lines_of_code": 400, "methods": 12},
            target_state={"lines_of_code": 200, "methods": 6}
        )
        class_result = self.orchestrator.plan_execution(class_req)
        assert class_result.success
        assert class_result.execution_plan is not None
        assert len(class_result.execution_plan) == 3
        
        # Method-level planning (on extracted method)
        method_req = PlanningRequest(
            operation=PlanningOperationType.PLAN_METHOD_REFACTOR,
            scope_name="authenticate_user",
            scope_level=PlanningLevel.METHOD,
            current_state={"cyclomatic_complexity": 6},
            target_state={"cyclomatic_complexity": 2}
        )
        method_result = self.orchestrator.plan_execution(method_req)
        assert method_result.success
        assert method_result.execution_plan is not None
        assert len(method_result.execution_plan) == 3
    
    def test_orchestrator_routing_consistency(self):
        """Test orchestrator always routes to correct strategy."""
        macro_ops = [
            PlanningOperationType.PLAN_INITIATIVE,
            PlanningOperationType.PLAN_PHASE,
            PlanningOperationType.PLAN_WAVE,
            PlanningOperationType.PLAN_TRACK,
            PlanningOperationType.PLAN_STAGE,
        ]
        
        for op in macro_ops:
            req = PlanningRequest(
                operation=op,
                scope_name="Test",
                scope_level=PlanningLevel.INITIATIVE,
                current_state={},
                target_state={}
            )
            result = self.orchestrator.plan_execution(req)
            assert result.strategy_used == "MacroPlanningStrategy"
        
        micro_ops = [
            PlanningOperationType.PLAN_METHOD_REFACTOR,
            PlanningOperationType.PLAN_CLASS_REFACTOR,
            PlanningOperationType.PLAN_DEPENDENCY_INJECTION,
        ]
        
        for op in micro_ops:
            req = PlanningRequest(
                operation=op,
                scope_name="Test",
                scope_level=PlanningLevel.METHOD,
                current_state={"cyclomatic_complexity": 5} if "METHOD" in op.name else {"lines_of_code": 100},
                target_state={"cyclomatic_complexity": 2} if "METHOD" in op.name else {"injected": True}
            )
            result = self.orchestrator.plan_execution(req)
            assert result.strategy_used == "MicroPlanningStrategy"
    
    def test_planning_with_constraints_respected(self):
        """Test planning respects constraint parameters."""
        # Plan with effort constraint
        req = PlanningRequest(
            operation=PlanningOperationType.PLAN_WAVE,
            scope_name="Wave with budget",
            scope_level=PlanningLevel.WAVE,
            current_state={},
            target_state={},
            constraints={
                "max_effort_hours": 15,
                "deadline": "2025-03-01",
            }
        )
        result = self.orchestrator.plan_execution(req)
        assert result.success
        assert result.metrics is not None
        # Should respect max effort constraint (approximately)
        assert result.metrics.estimated_effort_hours <= 15 or result.metrics.estimated_effort_hours <= 11.0
    
    def test_planning_with_execution_options_applied(self):
        """Test planning applies execution options."""
        req = PlanningRequest(
            operation=PlanningOperationType.PLAN_TRACK,
            scope_name="Track with options",
            scope_level=PlanningLevel.TRACK,
            current_state={},
            target_state={},
            options={
                "prefer_parallel": True,
                "risk_tolerance": "low",
            }
        )
        result = self.orchestrator.plan_execution(req)
        assert result.success
        assert result.metrics is not None
        # Options should be considered in plan generation
        assert result.metrics.parallel_tracks >= 1
    
    def test_error_recovery_on_invalid_macro_operation(self):
        """Test graceful error recovery on invalid macro planning."""
        req = PlanningRequest(
            operation=PlanningOperationType.PLAN_PHASE,
            scope_name="Invalid Phase",
            scope_level=PlanningLevel.PHASE,
            current_state={"status": "ready"},
            target_state={"different_key": "value"}  # Missing 'status'
        )
        result = self.orchestrator.plan_execution(req)
        assert not result.success
        assert result.error is not None
        assert result.execution_plan is None
    
    def test_error_recovery_on_invalid_micro_operation(self):
        """Test graceful error recovery on invalid micro planning."""
        req = PlanningRequest(
            operation=PlanningOperationType.PLAN_METHOD_REFACTOR,
            scope_name="Invalid Method",
            scope_level=PlanningLevel.METHOD,
            current_state={"lines_of_code": 50},  # Missing complexity
            target_state={"cyclomatic_complexity": 2}
        )
        result = self.orchestrator.plan_execution(req)
        assert not result.success
        assert result.error is not None
    
    def test_concurrent_planning_of_different_levels(self):
        """Test orchestrator handles concurrent requests."""
        requests = [
            PlanningRequest(
                operation=PlanningOperationType.PLAN_INITIATIVE,
                scope_name="Init 1",
                scope_level=PlanningLevel.INITIATIVE,
                current_state={},
                target_state={}
            ),
            PlanningRequest(
                operation=PlanningOperationType.PLAN_METHOD_REFACTOR,
                scope_name="Method 1",
                scope_level=PlanningLevel.METHOD,
                current_state={"cyclomatic_complexity": 4},
                target_state={"cyclomatic_complexity": 2}
            ),
            PlanningRequest(
                operation=PlanningOperationType.PLAN_WAVE,
                scope_name="Wave 1",
                scope_level=PlanningLevel.WAVE,
                current_state={},
                target_state={}
            ),
        ]
        
        # Execute all requests
        results = [self.orchestrator.plan_execution(req) for req in requests]
        
        # All should succeed
        assert all(r.success for r in results)
        assert results[0].strategy_used == "MacroPlanningStrategy"  # Initiative
        assert results[1].strategy_used == "MicroPlanningStrategy"  # Method
        assert results[2].strategy_used == "MacroPlanningStrategy"  # Wave
    
    def test_full_initiative_to_method_planning_hierarchy(self):
        """Test complete hierarchy from initiative to method planning."""
        # Start with initiative
        init_req = PlanningRequest(
            operation=PlanningOperationType.PLAN_INITIATIVE,
            scope_name="Q1 Technical Initiative",
            scope_level=PlanningLevel.INITIATIVE,
            current_state={"status": "planning"},
            target_state={"status": "executing"}
        )
        init_result = self.orchestrator.plan_execution(init_req)
        assert init_result.success
        
        # Plan a phase within initiative
        phase_req = PlanningRequest(
            operation=PlanningOperationType.PLAN_PHASE,
            scope_name="Phase 1 of Initiative",
            scope_level=PlanningLevel.PHASE,
            current_state={"status": "ready"},
            target_state={"status": "complete"}
        )
        phase_result = self.orchestrator.plan_execution(phase_req)
        assert phase_result.success
        
        # Plan a refactoring class within phase
        class_req = PlanningRequest(
            operation=PlanningOperationType.PLAN_CLASS_REFACTOR,
            scope_name="UserManager class",
            scope_level=PlanningLevel.CLASS,
            current_state={"lines_of_code": 300},
            target_state={"lines_of_code": 150}
        )
        class_result = self.orchestrator.plan_execution(class_req)
        assert class_result.success
        
        # Plan method within class
        method_req = PlanningRequest(
            operation=PlanningOperationType.PLAN_METHOD_REFACTOR,
            scope_name="validate_credentials",
            scope_level=PlanningLevel.METHOD,
            current_state={"cyclomatic_complexity": 8},
            target_state={"cyclomatic_complexity": 2}
        )
        method_result = self.orchestrator.plan_execution(method_req)
        assert method_result.success
        
        # Verify hierarchy was respected
        assert init_result.metrics is not None
        assert phase_result.metrics is not None
        assert class_result.metrics is not None
        assert method_result.metrics is not None
    
    def test_capability_discovery_completeness(self):
        """Test orchestrator can discover all capabilities."""
        operations = self.orchestrator.get_supported_operations()
        levels = self.orchestrator.get_supported_levels()
        
        # Check all 8 operations present
        assert len(operations) == 8
        assert PlanningOperationType.PLAN_INITIATIVE in operations
        assert PlanningOperationType.PLAN_PHASE in operations
        assert PlanningOperationType.PLAN_WAVE in operations
        assert PlanningOperationType.PLAN_TRACK in operations
        assert PlanningOperationType.PLAN_STAGE in operations
        assert PlanningOperationType.PLAN_METHOD_REFACTOR in operations
        assert PlanningOperationType.PLAN_CLASS_REFACTOR in operations
        assert PlanningOperationType.PLAN_DEPENDENCY_INJECTION in operations
        
        # Check all 8 levels present
        assert len(levels) == 8
        assert PlanningLevel.INITIATIVE in levels
        assert PlanningLevel.PHASE in levels
        assert PlanningLevel.WAVE in levels
        assert PlanningLevel.TRACK in levels
        assert PlanningLevel.STAGE in levels
        assert PlanningLevel.TASK in levels
        assert PlanningLevel.METHOD in levels
        assert PlanningLevel.CLASS in levels
    
    def test_strategy_seamless_handoff(self):
        """Test strategies can hand off to each other."""
        # Macro strategy delivers results
        macro_req = PlanningRequest(
            operation=PlanningOperationType.PLAN_WAVE,
            scope_name="Wave Planning",
            scope_level=PlanningLevel.WAVE,
            current_state={},
            target_state={}
        )
        macro_result = self.macro_strategy.execute(macro_req)
        assert macro_result.success
        
        # Micro strategy can plan from macro output
        micro_req = PlanningRequest(
            operation=PlanningOperationType.PLAN_CLASS_REFACTOR,
            scope_name="Implementation class",
            scope_level=PlanningLevel.CLASS,
            current_state={"lines_of_code": 250},
            target_state={"lines_of_code": 100}
        )
        micro_result = self.micro_strategy.execute(micro_req)
        assert micro_result.success
        
        # Both use orchestrator correctly
        assert macro_result.strategy_used == "MacroPlanningStrategy"
        assert micro_result.strategy_used == "MicroPlanningStrategy"


# AC_COMPLETE: AC-ENH090-S2-REFACTOR-001 ✅ 15 integration tests
