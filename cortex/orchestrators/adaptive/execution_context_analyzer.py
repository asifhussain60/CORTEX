"""Execution Context Analyzer for adaptive orchestrator routing.

This module implements context analysis for task-aware orchestrator selection.
It analyzes execution context including task complexity, resource requirements,
and required capabilities to enable intelligent routing decisions.

AC-EX-001-01: Context analysis extracts task complexity, resource requirements,
and required capabilities.

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Set


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
    dependencies: List[str] = field(default_factory=list)
    execution_hints: Optional[Dict[str, Any]] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Validate context after initialization.

        Raises:
            ValueError: If complexity_score is outside [0.0, 1.0] or priority is invalid
        """
        if not (0.0 <= self.complexity_score <= 1.0):
            raise ValueError("complexity_score must be between 0.0 and 1.0")
        if self.priority not in ("LOW", "MEDIUM", "HIGH", "CRITICAL"):
            raise ValueError("Invalid priority level")


class ExecutionContextAnalyzer:
    """Analyzes execution context for adaptive orchestrator routing.

    This analyzer examines task characteristics to determine:
    - Complexity of the task
    - Resource requirements (memory, CPU, disk)
    - Required orchestrator capabilities
    - Estimated execution duration
    - Priority and dependencies

    Used by adaptive execution framework for intelligent orchestrator selection.

    Example:
        >>> analyzer = ExecutionContextAnalyzer()
        >>> context = analyzer.analyze_context(
        ...     task_type="planning",
        ...     task_input={"ac_ids": ["AC-001-01"]},
        ...     context_hints={"priority": "HIGH"}
        ... )
        >>> print(f"Complexity: {context.complexity_score}")
    """

    def __init__(self) -> None:
        """Initialize the ExecutionContextAnalyzer.

        Sets up capability registry and complexity thresholds for all known
        orchestrators in the system.
        """
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

        Comprehensively analyzes a task's characteristics including complexity,
        resource needs, and required capabilities to enable intelligent
        orchestrator selection.

        Args:
            task_type: Type of task being analyzed
            task_input: The input/request for the task
            context_hints: Optional hints to influence analysis (priority,
                explicit_complexity, required_capabilities, dependencies)

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
            Dictionary with resource requirements (memory_mb, cpu_percentage,
            disk_mb, estimated_threads)
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
            Set of capabilities the orchestrator provides. Empty set if
            orchestrator is unknown.
        """
        return set(self._capability_registry.get(orchestrator_name, []))

    def can_orchestrator_handle_task(
        self,
        orchestrator_name: str,
        context: ExecutionContext,
    ) -> bool:
        """Check if an orchestrator can handle a task.

        Verifies that an orchestrator has all required capabilities to handle
        the given execution context.

        Args:
            orchestrator_name: Name of the orchestrator
            context: Execution context

        Returns:
            True if orchestrator has all required capabilities, False otherwise
        """
        orchestrator_caps = self.get_orchestrator_capabilities(orchestrator_name)
        return context.required_capabilities.issubset(orchestrator_caps)

    def register_orchestrator(self, name: str, capabilities: List[str]) -> None:
        """Register a new orchestrator in the capability registry.

        Args:
            name: Orchestrator name
            capabilities: List of capabilities the orchestrator provides
        """
        self._capability_registry[name] = capabilities
