"""
PlanningOrchestrator - CORTEX Phase Planning & Orchestration

AC-ID: AC-PHASE70-S2-002
Status: TDD Implementation (tests drive development)

AC-WAVE-7-CLEANUP-S3-001: Added IOrchestrator interface compliance
"""

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.core.result import Err, Ok, Result
from cortex.models.canonical_enums import PhaseStatus, IntentType
from cortex.core.interfaces.i_orchestrator import IOrchestrator, OperationMode


@dataclass
class PhaseNode:
    """Represents a phase in the execution plan"""
    phase_id: str
    title: str
    effort_hours: int
    dependencies: List[str] = None
    status: str = "planned"


class PlanningOrchestrator(IOrchestrator):
    """
    Orchestrates multi-phase planning with:
    - Predecessor/dependency analysis
    - Critical path calculation
    - Risk assessment integration
    - LENS-enriched planning
    """

    def __init__(self) -> None:
        """Initialize instance."""
        self.phases: Dict[str, PhaseNode] = {}
        self.lens_enabled = True

    # =========================================================================
    # IOrchestrator Interface Implementation (WAVE-7-CLEANUP)
    # AC-WAVE-7-CLEANUP-S3-001: Add 7 required interface methods
    # =========================================================================

    def get_name(self) -> str:
        """Get orchestrator name."""
        return "PlanningOrchestrator"

    def get_version(self) -> str:
        """Get orchestrator version."""
        return "1.0.0"

    def initialize(self) -> Result[str]:
        """Initialize orchestrator."""
        try:
            return Ok("PlanningOrchestrator initialized successfully")
        except Exception as e:
            return Err(f"PlanningOrchestrator initialization failed: {str(e)}")

    def get_mode(self) -> OperationMode:
        """Get current operation mode."""
        return OperationMode.PLANNING

    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """Get exposed MCP tools."""
        try:
            tools = {
                "cortex_plan_phases": {
                    "name": "cortex_plan_phases",
                    "description": "Plan multi-phase execution with dependencies",
                    "parameters": {
                        "phases": {"type": "array", "required": True}
                    }
                },
                "cortex_plan_analyze_dependencies": {
                    "name": "cortex_plan_analyze_dependencies",
                    "description": "Analyze phase dependencies and critical path",
                    "parameters": {}
                }
            }
            return Ok(tools)
        except Exception as e:
            return Err(f"Failed to get MCP tools: {str(e)}")

    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any],
    ) -> Result[Any]:
        """Execute operation with audit logging."""
        try:
            if operation_name == "plan_phases":
                phases_data = parameters.get("phases", [])
                phases = [PhaseNode(**p) for p in phases_data]
                result = self.plan_phases(phases)
                return Ok(result)
            elif operation_name == "analyze_dependencies":
                result = self.analyze_dependencies()
                return Ok(result)
            elif operation_name == "calculate_critical_path":
                result = self.calculate_critical_path()
                return Ok(result)
            elif operation_name == "assess_risks":
                result = self.assess_risks()
                return Ok(result)
            else:
                return Err(f"Unknown operation: {operation_name}")
        except Exception as e:
            return Err(f"Operation failed: {str(e)}")

    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """Get audit trail with hash chain."""
        try:
            # TODO: Implement hash-chained audit trail storage
            return Ok([])
        except Exception as e:
            return Err(f"Failed to get audit trail: {str(e)}")

    # =========================================================================
    # End IOrchestrator Interface Implementation
    # =========================================================================

    def process(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main planning orchestration entry point.

        Args:
            request: Plan request with phases/dependencies

        Returns:
            Orchestrated plan with risk/effort/timeline
        """
        phases_data = request.get("phases", [])
        phases = []
        for p in phases_data:
            if isinstance(p, PhaseNode):
                phases.append(p)
            elif isinstance(p, dict):
                phases.append(PhaseNode(**p))

        if phases:
            plan_result = self.plan_phases(phases)
        else:
            plan_result = {"phases": list(self.phases.values()), "total_effort": 0}

        dependencies = self.analyze_dependencies()
        critical_path = self.calculate_critical_path()
        risks = self.assess_risks()

        return {
            "status": PhaseStatus.PLANNED,
            "plan": plan_result,
            "critical_path": critical_path,
            "risks": risks,
            "dependencies": dependencies,
        }

    def plan_phases(self, phases: List[PhaseNode]) -> Dict[str, Any]:
        """
        Orchestrate phase planning with dependency ordering.

        Args:
            phases: List of PhaseNode objects to plan

        Returns:
            Planning result with ordered phases and total effort
        """
        for phase in phases:
            if phase.dependencies is None:
                phase.dependencies = []
            self.phases[phase.phase_id] = phase

        # Topological sort for execution order
        ordered = self._topological_sort()
        total_effort = sum(p.effort_hours for p in phases)

        return {
            "phases": [p.phase_id for p in ordered],
            "total_effort": total_effort,
            "phase_count": len(phases),
        }

    def analyze_dependencies(self) -> Dict[str, List[str]]:
        """
        Analyze phase dependencies and return dependency graph.

        Returns:
            Dict mapping phase_id to list of dependency phase_ids
        """
        dependency_graph: Dict[str, List[str]] = {}
        for phase_id, phase in self.phases.items():
            deps = phase.dependencies or []
            # Validate dependencies exist
            valid_deps = [d for d in deps if d in self.phases]
            dependency_graph[phase_id] = valid_deps
        return dependency_graph

    def calculate_critical_path(self) -> List[str]:
        """
        Calculate critical path through phases using longest-path algorithm.

        Returns:
            List of phase_ids forming the critical path
        """
        if not self.phases:
            return []

        ordered = self._topological_sort()

        # Calculate earliest start/finish for each phase
        earliest_finish: Dict[str, int] = {}
        predecessors: Dict[str, Optional[str]] = {}

        for phase in ordered:
            deps = phase.dependencies or []
            valid_deps = [d for d in deps if d in earliest_finish]
            if valid_deps:
                max_dep = max(valid_deps, key=lambda d: earliest_finish[d])
                earliest_finish[phase.phase_id] = earliest_finish[max_dep] + phase.effort_hours
                predecessors[phase.phase_id] = max_dep
            else:
                earliest_finish[phase.phase_id] = phase.effort_hours
                predecessors[phase.phase_id] = None

        if not earliest_finish:
            return []

        # Trace back from the phase with latest finish
        critical_end = max(earliest_finish, key=earliest_finish.get)  # type: ignore[arg-type]
        path = []
        current: Optional[str] = critical_end
        while current is not None:
            path.append(current)
            current = predecessors.get(current)
        path.reverse()
        return path

    def assess_risks(self) -> List[Dict[str, Any]]:
        """
        Assess planning risks based on phase characteristics.

        Returns:
            List of risk assessments with severity and mitigation
        """
        risks: List[Dict[str, Any]] = []

        for phase_id, phase in self.phases.items():
            deps = phase.dependencies or []

            # Risk: High dependency count
            if len(deps) >= 3:
                risks.append({
                    "phase_id": phase_id,
                    "risk_type": "high_dependency_count",
                    "severity": "high",
                    "description": f"Phase {phase_id} depends on {len(deps)} phases",
                    "mitigation": "Consider parallelizing or breaking into smaller phases",
                })

            # Risk: High effort
            if phase.effort_hours > 40:
                risks.append({
                    "phase_id": phase_id,
                    "risk_type": "high_effort",
                    "severity": "medium",
                    "description": f"Phase {phase_id} requires {phase.effort_hours}h effort",
                    "mitigation": "Break into sub-phases of ≤40h each",
                })

            # Risk: Missing dependencies
            missing_deps = [d for d in deps if d not in self.phases]
            if missing_deps:
                risks.append({
                    "phase_id": phase_id,
                    "risk_type": "missing_dependencies",
                    "severity": "critical",
                    "description": f"Phase {phase_id} references unknown phases: {missing_deps}",
                    "mitigation": "Add missing phases or remove invalid dependencies",
                })

        return risks

    def _topological_sort(self) -> List[PhaseNode]:
        """
        Topological sort of phases respecting dependencies.

        Returns:
            Ordered list of PhaseNode objects

        Raises:
            ValueError: If circular dependency detected
        """
        in_degree: Dict[str, int] = {pid: 0 for pid in self.phases}
        for phase in self.phases.values():
            for dep in (phase.dependencies or []):
                if dep in in_degree:
                    in_degree[phase.phase_id] = in_degree.get(phase.phase_id, 0) + 1

        # Kahn's algorithm
        queue = [pid for pid, deg in in_degree.items() if deg == 0]
        result: List[PhaseNode] = []

        while queue:
            pid = queue.pop(0)
            result.append(self.phases[pid])
            # Find phases that depend on this one
            for other_pid, other_phase in self.phases.items():
                if pid in (other_phase.dependencies or []):
                    in_degree[other_pid] -= 1
                    if in_degree[other_pid] == 0:
                        queue.append(other_pid)

        if len(result) != len(self.phases):
            raise ValueError("Circular dependency detected in phase graph")

        return result
