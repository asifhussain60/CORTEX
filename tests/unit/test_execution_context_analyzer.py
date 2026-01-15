"""Unit tests for ExecutionContextAnalyzer.

Acceptance Criteria: AC-EX-001-01
- Context analysis extracts task complexity
- Resource requirements estimated
- Required capabilities identified

Each test verifies a specific aspect of context analysis for adaptive routing.

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
from typing import Dict, Any, Set

from src.orchestrators.adaptive.execution_context_analyzer import (
    ExecutionContext,
    ExecutionContextAnalyzer,
)


class TestExecutionContextDataclass:
    """Test ExecutionContext dataclass initialization and validation."""
    
    def test_execution_context_creation(self) -> None:
        """Test creation of a valid ExecutionContext."""
        context = ExecutionContext(
            task_type="planning",
            task_input={"ac_ids": ["AC-001-01"]},
            complexity_score=0.5,
            resource_requirements={"memory_mb": 128},
            required_capabilities={"planning", "analysis"},
            estimated_duration=2.5,
            priority="HIGH",
        )
        
        assert context.task_type == "planning"
        assert context.complexity_score == 0.5
        assert context.priority == "HIGH"
        assert "planning" in context.required_capabilities
    
    def test_execution_context_with_defaults(self) -> None:
        """Test ExecutionContext with default values."""
        context = ExecutionContext(
            task_type="analysis",
            task_input={"data": "test"},
            complexity_score=0.3,
            resource_requirements={},
            required_capabilities=set(),
            estimated_duration=1.0,
        )
        
        assert context.priority == "MEDIUM"  # default
        assert context.dependencies == []  # default
        assert context.execution_hints == {}  # default
    
    def test_execution_context_complexity_validation(self) -> None:
        """Test that complexity_score must be between 0.0 and 1.0."""
        # Valid range: 0.0
        ExecutionContext(
            task_type="test",
            task_input={},
            complexity_score=0.0,
            resource_requirements={},
            required_capabilities=set(),
            estimated_duration=1.0,
        )
        
        # Valid range: 1.0
        ExecutionContext(
            task_type="test",
            task_input={},
            complexity_score=1.0,
            resource_requirements={},
            required_capabilities=set(),
            estimated_duration=1.0,
        )
        
        # Invalid: > 1.0
        with pytest.raises(ValueError, match="complexity_score must be between"):
            ExecutionContext(
                task_type="test",
                task_input={},
                complexity_score=1.5,
                resource_requirements={},
                required_capabilities=set(),
                estimated_duration=1.0,
            )
        
        # Invalid: < 0.0
        with pytest.raises(ValueError, match="complexity_score must be between"):
            ExecutionContext(
                task_type="test",
                task_input={},
                complexity_score=-0.1,
                resource_requirements={},
                required_capabilities=set(),
                estimated_duration=1.0,
            )
    
    def test_execution_context_priority_validation(self) -> None:
        """Test that priority must be one of valid levels."""
        valid_priorities = ["LOW", "MEDIUM", "HIGH", "CRITICAL"]
        
        for priority in valid_priorities:
            context = ExecutionContext(
                task_type="test",
                task_input={},
                complexity_score=0.5,
                resource_requirements={},
                required_capabilities=set(),
                estimated_duration=1.0,
                priority=priority,
            )
            assert context.priority == priority
        
        # Invalid priority
        with pytest.raises(ValueError, match="Invalid priority level"):
            ExecutionContext(
                task_type="test",
                task_input={},
                complexity_score=0.5,
                resource_requirements={},
                required_capabilities=set(),
                estimated_duration=1.0,
                priority="INVALID",
            )


class TestExecutionContextAnalyzerInitialization:
    """Test ExecutionContextAnalyzer initialization."""
    
    def test_analyzer_initialization(self) -> None:
        """Test that analyzer initializes with default orchestrators."""
        analyzer = ExecutionContextAnalyzer()
        
        # Verify default orchestrators are registered
        assert "PlanningOrchestrator" in analyzer._capability_registry
        assert "MasterOrchestrator" in analyzer._capability_registry
        assert "DomainOrchestrator" in analyzer._capability_registry
    
    def test_analyzer_has_complexity_thresholds(self) -> None:
        """Test that analyzer has complexity level thresholds."""
        analyzer = ExecutionContextAnalyzer()
        
        assert "low" in analyzer._complexity_thresholds
        assert "medium" in analyzer._complexity_thresholds
        assert "high" in analyzer._complexity_thresholds
        
        # Verify threshold ranges
        low_range = analyzer._complexity_thresholds["low"]
        medium_range = analyzer._complexity_thresholds["medium"]
        high_range = analyzer._complexity_thresholds["high"]
        
        assert low_range[0] == 0.0
        assert low_range[1] == 0.33
        assert medium_range[0] == 0.33
        assert medium_range[1] == 0.67
        assert high_range[0] == 0.67
        assert high_range[1] == 1.0


class TestComplexityAnalysis:
    """Test task complexity analysis."""
    
    def test_analyze_context_with_planning_task(self) -> None:
        """Test context analysis for planning task type."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="planning",
            task_input={"ac_ids": ["AC-001-01", "AC-001-02"]},
        )
        
        # Planning should have moderate-to-high complexity
        assert context.task_type == "planning"
        assert 0.3 <= context.complexity_score <= 0.8
        assert "planning" in context.required_capabilities
        assert "orchestration" in context.required_capabilities
    
    def test_analyze_context_with_simple_query(self) -> None:
        """Test context analysis for simple query task type."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="simple_query",
            task_input={"query": "test"},
        )
        
        # Simple query should have low complexity
        assert context.complexity_score <= 0.33
        assert "query_execution" in context.required_capabilities
        assert "caching" in context.required_capabilities
    
    def test_analyze_context_with_complex_orchestration(self) -> None:
        """Test context analysis for complex orchestration."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="complex_orchestration",
            task_input={"operations": list(range(100))},
        )
        
        # Complex orchestration should have high complexity
        assert 0.67 <= context.complexity_score <= 1.0
        assert "orchestration" in context.required_capabilities
        assert "composition" in context.required_capabilities
    
    def test_analyze_context_invalid_task_type_empty(self) -> None:
        """Test that empty task_type raises ValueError."""
        analyzer = ExecutionContextAnalyzer()
        
        with pytest.raises(ValueError, match="task_type cannot be empty"):
            analyzer.analyze_context(
                task_type="",
                task_input={},
            )
    
    def test_analyze_context_with_explicit_complexity_hint(self) -> None:
        """Test that explicit_complexity hint overrides default."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="simple_query",
            task_input={"query": "test"},
            context_hints={"explicit_complexity": 0.9},
        )
        
        # Should use explicit hint
        assert context.complexity_score == 0.9
    
    def test_complexity_affected_by_input_size(self) -> None:
        """Test that complexity increases with large input."""
        analyzer = ExecutionContextAnalyzer()
        
        # Small input
        small_context = analyzer.analyze_context(
            task_type="analysis",
            task_input={"data": "small"},
        )
        
        # Large input
        large_context = analyzer.analyze_context(
            task_type="analysis",
            task_input={"data": "x" * 50000},
        )
        
        # Large input should have higher complexity
        assert large_context.complexity_score > small_context.complexity_score


class TestResourceRequirementAnalysis:
    """Test resource requirement estimation."""
    
    def test_resource_requirements_include_memory(self) -> None:
        """Test that resource requirements include memory_mb."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="planning",
            task_input={"ac_ids": ["AC-001-01"]},
        )
        
        assert "memory_mb" in context.resource_requirements
        assert isinstance(context.resource_requirements["memory_mb"], int)
        assert context.resource_requirements["memory_mb"] > 0
    
    def test_resource_requirements_include_cpu(self) -> None:
        """Test that resource requirements include cpu_percentage."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="generation",
            task_input={"prompt": "generate code"},
        )
        
        assert "cpu_percentage" in context.resource_requirements
        assert isinstance(context.resource_requirements["cpu_percentage"], int)
        assert 0 <= context.resource_requirements["cpu_percentage"] <= 100
    
    def test_resource_requirements_include_disk(self) -> None:
        """Test that resource requirements include disk_mb."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="analysis",
            task_input={"large_dataset": "x" * 10000000},  # 10MB input
        )
        
        assert "disk_mb" in context.resource_requirements
        assert isinstance(context.resource_requirements["disk_mb"], int)
    
    def test_resource_requirements_include_threads(self) -> None:
        """Test that resource requirements include estimated_threads."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="simple_query",
            task_input={},
        )
        
        assert "estimated_threads" in context.resource_requirements
        assert isinstance(context.resource_requirements["estimated_threads"], int)
        assert context.resource_requirements["estimated_threads"] >= 1
    
    def test_resources_scale_with_complexity(self) -> None:
        """Test that resource requirements increase with complexity."""
        analyzer = ExecutionContextAnalyzer()
        
        # Low complexity task
        low_context = analyzer.analyze_context(
            task_type="simple_query",
            task_input={"query": "test"},
        )
        
        # High complexity task
        high_context = analyzer.analyze_context(
            task_type="complex_orchestration",
            task_input={"operations": list(range(100))},
        )
        
        # Higher complexity should require more resources
        assert (high_context.resource_requirements["memory_mb"] >= 
                low_context.resource_requirements["memory_mb"])
        assert (high_context.resource_requirements["cpu_percentage"] > 
                low_context.resource_requirements["cpu_percentage"])


class TestCapabilityAnalysis:
    """Test required capability identification."""
    
    def test_planning_task_requires_planning_capability(self) -> None:
        """Test that planning tasks require planning capability."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="planning",
            task_input={},
        )
        
        assert "planning" in context.required_capabilities
    
    def test_analysis_task_requires_analysis_capability(self) -> None:
        """Test that analysis tasks require analysis capability."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="analysis",
            task_input={},
        )
        
        assert "analysis" in context.required_capabilities
    
    def test_generation_task_requires_generation_capability(self) -> None:
        """Test that generation tasks require generation capability."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="generation",
            task_input={},
        )
        
        assert "generation" in context.required_capabilities
    
    def test_context_hints_add_required_capabilities(self) -> None:
        """Test that context hints can add required capabilities."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="simple_query",
            task_input={},
            context_hints={"required_capabilities": {"special", "custom"}},
        )
        
        # Should have both base capabilities and hinted capabilities
        assert "query_execution" in context.required_capabilities
        assert "special" in context.required_capabilities
        assert "custom" in context.required_capabilities


class TestDurationEstimation:
    """Test estimated execution duration."""
    
    def test_estimated_duration_is_positive(self) -> None:
        """Test that estimated duration is always positive."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="planning",
            task_input={},
        )
        
        assert context.estimated_duration > 0.0
    
    def test_estimated_duration_increases_with_complexity(self) -> None:
        """Test that duration increases with task complexity."""
        analyzer = ExecutionContextAnalyzer()
        
        # Low complexity
        low_context = analyzer.analyze_context(
            task_type="simple_query",
            task_input={},
        )
        
        # High complexity
        high_context = analyzer.analyze_context(
            task_type="complex_orchestration",
            task_input={},
        )
        
        assert high_context.estimated_duration > low_context.estimated_duration
    
    def test_estimated_duration_increases_with_input_size(self) -> None:
        """Test that duration increases with input size."""
        analyzer = ExecutionContextAnalyzer()
        
        # Small input
        small_context = analyzer.analyze_context(
            task_type="analysis",
            task_input={"data": "small"},
        )
        
        # Large input
        large_context = analyzer.analyze_context(
            task_type="analysis",
            task_input={"data": "x" * 50000},
        )
        
        assert large_context.estimated_duration > small_context.estimated_duration


class TestPriorityAndDependencies:
    """Test priority and dependency handling."""
    
    def test_priority_from_context_hints(self) -> None:
        """Test that priority can be specified via context hints."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="planning",
            task_input={},
            context_hints={"priority": "CRITICAL"},
        )
        
        assert context.priority == "CRITICAL"
    
    def test_dependencies_from_context_hints(self) -> None:
        """Test that dependencies can be specified via context hints."""
        analyzer = ExecutionContextAnalyzer()
        
        deps = ["AC-001-01", "AC-001-02"]
        context = analyzer.analyze_context(
            task_type="planning",
            task_input={},
            context_hints={"dependencies": deps},
        )
        
        assert context.dependencies == deps
    
    def test_execution_hints_stored(self) -> None:
        """Test that execution hints are stored in context."""
        analyzer = ExecutionContextAnalyzer()
        
        hints = {"priority": "HIGH", "custom_flag": True}
        context = analyzer.analyze_context(
            task_type="planning",
            task_input={},
            context_hints=hints,
        )
        
        assert context.execution_hints == hints


class TestComplexityLevelClassification:
    """Test get_complexity_level() method."""
    
    def test_complexity_level_low(self) -> None:
        """Test classification of low complexity."""
        analyzer = ExecutionContextAnalyzer()
        
        assert analyzer.get_complexity_level(0.0) == "low"
        assert analyzer.get_complexity_level(0.1) == "low"
        assert analyzer.get_complexity_level(0.32) == "low"
    
    def test_complexity_level_medium(self) -> None:
        """Test classification of medium complexity."""
        analyzer = ExecutionContextAnalyzer()
        
        assert analyzer.get_complexity_level(0.33) == "medium"
        assert analyzer.get_complexity_level(0.5) == "medium"
        assert analyzer.get_complexity_level(0.66) == "medium"
    
    def test_complexity_level_high(self) -> None:
        """Test classification of high complexity."""
        analyzer = ExecutionContextAnalyzer()
        
        assert analyzer.get_complexity_level(0.67) == "high"
        assert analyzer.get_complexity_level(0.8) == "high"
        assert analyzer.get_complexity_level(1.0) == "high"


class TestOrchestratorCapabilities:
    """Test orchestrator capability registry."""
    
    def test_get_planning_orchestrator_capabilities(self) -> None:
        """Test retrieval of PlanningOrchestrator capabilities."""
        analyzer = ExecutionContextAnalyzer()
        
        caps = analyzer.get_orchestrator_capabilities("PlanningOrchestrator")
        
        assert "planning" in caps
        assert "analysis" in caps
        assert isinstance(caps, set)
    
    def test_get_master_orchestrator_capabilities(self) -> None:
        """Test retrieval of MasterOrchestrator capabilities."""
        analyzer = ExecutionContextAnalyzer()
        
        caps = analyzer.get_orchestrator_capabilities("MasterOrchestrator")
        
        assert "orchestration" in caps
        assert "delegation" in caps
    
    def test_get_domain_orchestrator_capabilities(self) -> None:
        """Test retrieval of DomainOrchestrator capabilities."""
        analyzer = ExecutionContextAnalyzer()
        
        caps = analyzer.get_orchestrator_capabilities("DomainOrchestrator")
        
        assert "domain-specific" in caps
        assert "business-logic" in caps
    
    def test_get_capabilities_for_unknown_orchestrator(self) -> None:
        """Test that unknown orchestrator returns empty set."""
        analyzer = ExecutionContextAnalyzer()
        
        caps = analyzer.get_orchestrator_capabilities("UnknownOrchestrator")
        
        assert isinstance(caps, set)
        assert len(caps) == 0
    
    def test_register_new_orchestrator(self) -> None:
        """Test registration of a new orchestrator."""
        analyzer = ExecutionContextAnalyzer()
        
        new_caps = ["custom", "specialized"]
        analyzer.register_orchestrator("CustomOrchestrator", new_caps)
        
        caps = analyzer.get_orchestrator_capabilities("CustomOrchestrator")
        assert "custom" in caps
        assert "specialized" in caps


class TestCanOrchestratorHandleTask:
    """Test can_orchestrator_handle_task() method."""
    
    def test_planning_orchestrator_handles_planning_task(self) -> None:
        """Test that PlanningOrchestrator can handle planning tasks."""
        analyzer = ExecutionContextAnalyzer()
        
        # Update PlanningOrchestrator to include orchestration capability
        analyzer.register_orchestrator(
            "PlanningOrchestrator",
            ["planning", "analysis", "parsing", "orchestration"],
        )
        
        context = analyzer.analyze_context(
            task_type="planning",
            task_input={},
        )
        
        can_handle = analyzer.can_orchestrator_handle_task(
            "PlanningOrchestrator",
            context,
        )
        
        assert can_handle is True
    
    def test_master_orchestrator_handles_orchestration(self) -> None:
        """Test that MasterOrchestrator can handle orchestration tasks."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="complex_orchestration",
            task_input={},
        )
        
        can_handle = analyzer.can_orchestrator_handle_task(
            "MasterOrchestrator",
            context,
        )
        
        assert can_handle is True
    
    def test_simple_orchestrator_cannot_handle_complex_task(self) -> None:
        """Test that simple orchestrator cannot handle complex capabilities."""
        analyzer = ExecutionContextAnalyzer()
        
        # Register a simple orchestrator with limited capabilities
        analyzer.register_orchestrator(
            "SimpleOrchestrator",
            ["simple_operations"],
        )
        
        # Create a context requiring complex capabilities
        context = ExecutionContext(
            task_type="complex",
            task_input={},
            complexity_score=0.8,
            resource_requirements={},
            required_capabilities={"planning", "orchestration"},
            estimated_duration=5.0,
        )
        
        can_handle = analyzer.can_orchestrator_handle_task(
            "SimpleOrchestrator",
            context,
        )
        
        assert can_handle is False
    
    def test_orchestrator_with_superset_capabilities_handles_task(self) -> None:
        """Test that orchestrator with superset of capabilities handles task."""
        analyzer = ExecutionContextAnalyzer()
        
        # Register orchestrator with many capabilities
        analyzer.register_orchestrator(
            "SuperOrchestrator",
            ["planning", "orchestration", "analysis", "generation", "custom"],
        )
        
        # Create context requiring subset
        context = ExecutionContext(
            task_type="test",
            task_input={},
            complexity_score=0.5,
            resource_requirements={},
            required_capabilities={"planning", "analysis"},
            estimated_duration=2.0,
        )
        
        can_handle = analyzer.can_orchestrator_handle_task(
            "SuperOrchestrator",
            context,
        )
        
        assert can_handle is True


class TestCompleteAnalysisWorkflow:
    """Integration tests for complete analysis workflow."""
    
    def test_end_to_end_analysis_planning_task(self) -> None:
        """Test complete analysis workflow for planning task."""
        analyzer = ExecutionContextAnalyzer()
        
        # Update PlanningOrchestrator to include orchestration capability for this test
        analyzer.register_orchestrator(
            "PlanningOrchestrator",
            ["planning", "analysis", "parsing", "orchestration"],
        )
        
        context = analyzer.analyze_context(
            task_type="planning",
            task_input={"ac_ids": ["AC-001-01", "AC-001-02", "AC-001-03"]},
            context_hints={"priority": "HIGH"},
        )
        
        # Verify all aspects are populated
        assert context.task_type == "planning"
        assert context.priority == "HIGH"
        assert context.complexity_score > 0.0
        assert len(context.required_capabilities) > 0
        assert context.resource_requirements["memory_mb"] > 0
        assert context.estimated_duration > 0.0
        
        # Verify complexity is moderate-to-high for planning
        complexity_level = analyzer.get_complexity_level(context.complexity_score)
        assert complexity_level in ["medium", "high"]
        
        # Verify PlanningOrchestrator can handle it
        can_handle = analyzer.can_orchestrator_handle_task(
            "PlanningOrchestrator",
            context,
        )
        assert can_handle is True
    
    def test_end_to_end_analysis_governance_task(self) -> None:
        """Test complete analysis workflow for governance task."""
        analyzer = ExecutionContextAnalyzer()
        
        context = analyzer.analyze_context(
            task_type="governance_check",
            task_input={"rules": ["CORE-008", "CORE-011"]},
            context_hints={"priority": "CRITICAL", "dependencies": ["PHASE-01"]},
        )
        
        # Verify all aspects are populated
        assert context.task_type == "governance_check"
        assert context.priority == "CRITICAL"
        assert context.dependencies == ["PHASE-01"]
        assert "governance" in context.required_capabilities
        assert "audit_logging" in context.required_capabilities
        
        # Complexity should be moderate (governance is moderately complex)
        complexity_level = analyzer.get_complexity_level(context.complexity_score)
        assert complexity_level in ["low", "medium"]
