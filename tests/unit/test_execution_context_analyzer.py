"""Tests for Execution Context Analyzer.

This module tests the ExecutionContextAnalyzer component which analyzes
execution context including task complexity, resource requirements, and
required capabilities.

AC-EX-001-01: Context analysis extracts task complexity, resource requirements,
and required capabilities.

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
import unittest
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Set
from unittest.mock import MagicMock, Mock, patch

import pytest


@dataclass
class ExecutionContext:
    """Represents execution context for a task.
    
    Attributes:
        task_type: Type of task (e.g., 'planning', 'analysis', 'generation')
        task_input: The input/request for the task
        complexity_score: Estimated complexity (0.0-1.0)
        resource_requirements: Estimated resource needs
        required_capabilities: Set of required orchestrator capabilities
        estimated_duration: Estimated execution time in seconds
        priority: Task priority level (LOW, MEDIUM, HIGH, CRITICAL)
        dependencies: List of dependent AC-IDs or resources
        execution_hints: Optional hints for orchestrator selection
    """
    
    task_type: str
    task_input: Any
    complexity_score: float
    resource_requirements: Dict[str, Any]
    required_capabilities: Set[str]
    estimated_duration: float
    priority: str = "MEDIUM"
    dependencies: List[str] = None
    execution_hints: Optional[Dict[str, Any]] = None
    
    def __post_init__(self) -> None:
        """Validate context after initialization."""
        if not (0.0 <= self.complexity_score <= 1.0):
            raise ValueError("complexity_score must be between 0.0 and 1.0")
        if self.priority not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            raise ValueError("Invalid priority level")
        if self.dependencies is None:
            self.dependencies = []
        if self.execution_hints is None:
            self.execution_hints = {}


class ExecutionContextAnalyzer:
    """Analyzes execution context for adaptive routing.
    
    This analyzer examines task characteristics to determine:
    - Complexity of the task
    - Resource requirements (memory, CPU, disk)
    - Required orchestrator capabilities
    - Estimated execution duration
    - Priority and dependencies
    
    Used by adaptive execution framework for intelligent orchestrator selection.
    """
    
    def __init__(self) -> None:
        """Initialize the ExecutionContextAnalyzer."""
        self._capability_registry: Dict[str, List[str]] = {
            "PlanningOrchestrator": ["planning", "analysis", "parsing"],
            "MasterOrchestrator": ["orchestration", "delegation", "composition"],
            "DomainOrchestrator": ["domain-specific", "business-logic"],
        }
        self._complexity_thresholds = {
            "low": (0.0, 0.33),
            "medium": (0.33, 0.67),
            "high": (0.67, 1.0),
        }
    
    def analyze_context(
        self, 
        task_type: str,
        task_input: Any,
        context_hints: Optional[Dict[str, Any]] = None,
    ) -> ExecutionContext:
        """Analyze execution context from task input.
        
        Args:
            task_type: Type of task being analyzed
            task_input: The input/request for the task
            context_hints: Optional hints to influence analysis
            
        Returns:
            ExecutionContext object with analyzed characteristics
            
        Raises:
            ValueError: If task_type is invalid or analysis fails
        """
        if not task_type:
            raise ValueError("task_type cannot be empty")
        if context_hints is None:
            context_hints = {}
        
        complexity = self._analyze_complexity(task_type, task_input, context_hints)
        resources = self._analyze_resources(task_type, complexity, task_input)
        capabilities = self._analyze_capabilities(task_type, task_input, context_hints)
        duration = self._estimate_duration(complexity, len(str(task_input)))
        priority = context_hints.get("priority", "MEDIUM")
        dependencies = context_hints.get("dependencies", [])
        
        return ExecutionContext(
            task_type=task_type,
            task_input=task_input,
            complexity_score=complexity,
            resource_requirements=resources,
            required_capabilities=capabilities,
            estimated_duration=duration,
            priority=priority,
            dependencies=dependencies,
            execution_hints=context_hints,
        )
    
    def _analyze_complexity(
        self,
        task_type: str,
        task_input: Any,
        context_hints: Dict[str, Any],
    ) -> float:
        """Analyze task complexity based on type and input characteristics.
        
        Args:
            task_type: Type of task
            task_input: Task input
            context_hints: Contextual hints
            
        Returns:
            Complexity score between 0.0 and 1.0
        """
        base_complexity = {
            "simple_query": 0.1,
            "simple_command": 0.15,
            "analysis": 0.4,
            "planning": 0.5,
            "generation": 0.6,
            "complex_orchestration": 0.8,
            "governance_check": 0.3,
        }.get(task_type, 0.5)
        
        # Adjust based on input characteristics
        if isinstance(task_input, (list, dict)):
            input_size_factor = min(len(str(task_input)) / 10000, 0.3)
            base_complexity += input_size_factor
        
        # Check for explicit complexity hint
        if "explicit_complexity" in context_hints:
            base_complexity = context_hints["explicit_complexity"]
        
        return min(base_complexity, 1.0)
    
    def _analyze_resources(
        self,
        task_type: str,
        complexity: float,
        task_input: Any,
    ) -> Dict[str, Any]:
        """Analyze resource requirements.
        
        Args:
            task_type: Type of task
            complexity: Complexity score
            task_input: Task input
            
        Returns:
            Dictionary with resource requirements
        """
        base_memory_mb = 64 + (complexity * 256)
        input_size = len(str(task_input))
        memory_estimate = base_memory_mb + (input_size / 1000)
        
        return {
            "memory_mb": int(memory_estimate),
            "cpu_percentage": int(20 + (complexity * 60)),
            "disk_mb": int(max(0, (input_size / 1000000) * 100)),
            "estimated_threads": 1 if complexity < 0.5 else 2,
        }
    
    def _analyze_capabilities(
        self,
        task_type: str,
        task_input: Any,
        context_hints: Dict[str, Any],
    ) -> Set[str]:
        """Analyze required capabilities for the task.
        
        Args:
            task_type: Type of task
            task_input: Task input
            context_hints: Contextual hints
            
        Returns:
            Set of required capability names
        """
        base_capabilities = {
            "simple_query": {"query_execution", "caching"},
            "simple_command": {"command_execution"},
            "analysis": {"analysis", "parsing", "validation"},
            "planning": {"planning", "orchestration", "analysis"},
            "generation": {"generation", "templating", "formatting"},
            "complex_orchestration": {"orchestration", "composition", "delegation"},
            "governance_check": {"governance", "audit_logging"},
        }.get(task_type, {"general"})
        
        # Add capabilities from explicit requirements
        if "required_capabilities" in context_hints:
            base_capabilities.update(context_hints["required_capabilities"])
        
        return base_capabilities
    
    def _estimate_duration(self, complexity: float, input_size: int) -> float:
        """Estimate task execution duration in seconds.
        
        Args:
            complexity: Complexity score
            input_size: Size of input in characters
            
        Returns:
            Estimated duration in seconds
        """
        base_duration = 0.1 + (complexity * 5.0)
        size_factor = (input_size / 10000) * 0.5
        return base_duration + size_factor
    
    def get_complexity_level(self, complexity_score: float) -> str:
        """Get human-readable complexity level.
        
        Args:
            complexity_score: Complexity score (0.0-1.0)
            
        Returns:
            Complexity level: 'low', 'medium', or 'high'
        """
        if complexity_score < 0.33:
            return "low"
        elif complexity_score < 0.67:
            return "medium"
        else:
            return "high"
    
    def get_orchestrator_capabilities(self, orchestrator_name: str) -> Set[str]:
        """Get capabilities of a specific orchestrator.
        
        Args:
            orchestrator_name: Name of the orchestrator
            
        Returns:
            Set of capabilities the orchestrator provides
        """
        return set(self._capability_registry.get(orchestrator_name, []))
    
    def can_orchestrator_handle_task(
        self,
        orchestrator_name: str,
        context: ExecutionContext,
    ) -> bool:
        """Check if an orchestrator can handle a task.
        
        Args:
            orchestrator_name: Name of the orchestrator
            context: Execution context
            
        Returns:
            True if orchestrator has all required capabilities
        """
        orchestrator_caps = self.get_orchestrator_capabilities(orchestrator_name)
        return context.required_capabilities.issubset(orchestrator_caps)


class TestExecutionContextAnalyzer(unittest.TestCase):
    """Tests for ExecutionContextAnalyzer."""
    
    def setUp(self) -> None:
        """Set up test fixtures."""
        self.analyzer = ExecutionContextAnalyzer()
    
    def test_analyzer_initialization(self) -> None:
        """Test that analyzer initializes correctly."""
        self.assertIsNotNone(self.analyzer)
        self.assertIsNotNone(self.analyzer._capability_registry)
        self.assertIsNotNone(self.analyzer._complexity_thresholds)
    
    def test_analyze_simple_query_context(self) -> None:
        """Test analyzing a simple query task."""
        context = self.analyzer.analyze_context(
            task_type="simple_query",
            task_input="SELECT * FROM users WHERE id = 1",
        )
        
        self.assertEqual(context.task_type, "simple_query")
        self.assertLess(context.complexity_score, 0.25)
        self.assertGreater(context.estimated_duration, 0)
        self.assertGreater(len(context.required_capabilities), 0)
    
    def test_analyze_complex_planning_context(self) -> None:
        """Test analyzing a complex planning task."""
        context = self.analyzer.analyze_context(
            task_type="planning",
            task_input={"ac_ids": ["AC-001-01", "AC-002-01"], "depth": 5},
        )
        
        self.assertEqual(context.task_type, "planning")
        self.assertGreater(context.complexity_score, 0.3)
        self.assertIn("planning", context.required_capabilities)
    
    def test_analyze_context_with_hints(self) -> None:
        """Test analyzing context with explicit hints."""
        context = self.analyzer.analyze_context(
            task_type="analysis",
            task_input="large dataset",
            context_hints={
                "priority": "HIGH",
                "explicit_complexity": 0.75,
                "dependencies": ["dep-1", "dep-2"],
            },
        )
        
        self.assertEqual(context.complexity_score, 0.75)
        self.assertEqual(context.priority, "HIGH")
        self.assertEqual(len(context.dependencies), 2)
    
    def test_complexity_score_validation(self) -> None:
        """Test that complexity score is within valid range."""
        context = self.analyzer.analyze_context(
            task_type="generation",
            task_input="x" * 100000,  # Large input
        )
        
        self.assertLessEqual(context.complexity_score, 1.0)
        self.assertGreaterEqual(context.complexity_score, 0.0)
    
    def test_resource_estimation(self) -> None:
        """Test resource requirement estimation."""
        context = self.analyzer.analyze_context(
            task_type="complex_orchestration",
            task_input="large task",
        )
        
        self.assertGreater(context.resource_requirements["memory_mb"], 0)
        self.assertGreater(context.resource_requirements["cpu_percentage"], 0)
        self.assertGreaterEqual(context.resource_requirements["disk_mb"], 0)
        self.assertGreater(context.resource_requirements["estimated_threads"], 0)
    
    def test_execution_context_creation(self) -> None:
        """Test ExecutionContext dataclass creation."""
        context = ExecutionContext(
            task_type="test",
            task_input="input",
            complexity_score=0.5,
            resource_requirements={"memory": 128},
            required_capabilities={"test_cap"},
            estimated_duration=2.0,
        )
        
        self.assertEqual(context.task_type, "test")
        self.assertEqual(context.complexity_score, 0.5)
        self.assertEqual(context.priority, "MEDIUM")
        self.assertEqual(len(context.dependencies), 0)
    
    def test_execution_context_validation(self) -> None:
        """Test ExecutionContext validation."""
        with self.assertRaises(ValueError):
            ExecutionContext(
                task_type="test",
                task_input="input",
                complexity_score=1.5,  # Invalid: > 1.0
                resource_requirements={},
                required_capabilities=set(),
                estimated_duration=1.0,
            )
    
    def test_complexity_level_classification(self) -> None:
        """Test complexity level classification."""
        self.assertEqual(self.analyzer.get_complexity_level(0.1), "low")
        self.assertEqual(self.analyzer.get_complexity_level(0.5), "medium")
        self.assertEqual(self.analyzer.get_complexity_level(0.9), "high")
    
    def test_orchestrator_capability_lookup(self) -> None:
        """Test orchestrator capability lookup."""
        caps = self.analyzer.get_orchestrator_capabilities("PlanningOrchestrator")
        
        self.assertIsInstance(caps, set)
        self.assertIn("planning", caps)
        self.assertGreater(len(caps), 0)
    
    def test_orchestrator_task_compatibility(self) -> None:
        """Test checking if orchestrator can handle a task."""
        # Create context with capabilities that PlanningOrchestrator HAS
        context = ExecutionContext(
            task_type="test",
            task_input="test",
            complexity_score=0.5,
            resource_requirements={},
            required_capabilities={"planning", "analysis"},  # Both present in PlanningOrchestrator
            estimated_duration=1.0,
        )
        
        can_handle = self.analyzer.can_orchestrator_handle_task(
            "PlanningOrchestrator",
            context,
        )
        
        self.assertTrue(can_handle)
    
    def test_orchestrator_incompatibility(self) -> None:
        """Test that incompatible orchestrators are identified."""
        # Create context requiring unknown capability
        context = ExecutionContext(
            task_type="test",
            task_input="test",
            complexity_score=0.5,
            resource_requirements={},
            required_capabilities={"non_existent_capability"},
            estimated_duration=1.0,
        )
        
        can_handle = self.analyzer.can_orchestrator_handle_task(
            "PlanningOrchestrator",
            context,
        )
        
        self.assertFalse(can_handle)
    
    def test_invalid_task_type_raises_error(self) -> None:
        """Test that empty task_type raises ValueError."""
        with self.assertRaises(ValueError):
            self.analyzer.analyze_context("", "input")
    
    def test_duration_estimation_scales_with_complexity(self) -> None:
        """Test that duration estimation scales with complexity."""
        context_simple = self.analyzer.analyze_context(
            task_type="simple_query",
            task_input="x",
        )
        
        context_complex = self.analyzer.analyze_context(
            task_type="complex_orchestration",
            task_input="x" * 10000,
        )
        
        self.assertLess(context_simple.estimated_duration, context_complex.estimated_duration)
    
    def test_memory_estimation_scales_with_input_size(self) -> None:
        """Test that memory estimation scales with input size."""
        context_small = self.analyzer.analyze_context(
            task_type="analysis",
            task_input="x",
        )
        
        context_large = self.analyzer.analyze_context(
            task_type="analysis",
            task_input="x" * 100000,
        )
        
        small_mem = context_small.resource_requirements["memory_mb"]
        large_mem = context_large.resource_requirements["memory_mb"]
        
        self.assertLess(small_mem, large_mem)
    
    def test_unknown_orchestrator_returns_empty_capabilities(self) -> None:
        """Test that unknown orchestrator returns empty capability set."""
        caps = self.analyzer.get_orchestrator_capabilities("UnknownOrchestrator")
        
        self.assertEqual(len(caps), 0)
    
    def test_context_with_all_optional_fields(self) -> None:
        """Test creating context with all optional fields populated."""
        context = ExecutionContext(
            task_type="test",
            task_input="input",
            complexity_score=0.5,
            resource_requirements={"memory": 128},
            required_capabilities={"cap1", "cap2"},
            estimated_duration=2.5,
            priority="CRITICAL",
            dependencies=["dep1", "dep2"],
            execution_hints={"hint": "value"},
        )
        
        self.assertEqual(context.priority, "CRITICAL")
        self.assertEqual(len(context.dependencies), 2)
        self.assertIsNotNone(context.execution_hints)


if __name__ == "__main__":
    unittest.main()
