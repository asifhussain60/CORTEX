"""
Code Level Planner — Phase 3 SDLC orchestrator component.

Generates file-level implementation plans from refined task descriptions,
including scope analysis, phase breakdown, and TDD step ordering.

Compliance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
AC-ID: AC-SDLC-PHASE3-001
"""
# noqa: CORE-035 — domain-scoped; class name is contextually appropriate here

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin


@dataclass
class FilePlan:
    """A single file targeted by a plan."""

    path: str
    action: str  # "create" | "modify" | "delete"
    functions: List[str] = field(default_factory=list)


@dataclass
class Phase:
    """An implementation phase grouping related files."""

    name: str
    files: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    security_review: bool = False


@dataclass
class CodePlan:
    """Complete code-level implementation plan."""

    scope: str
    files: List[FilePlan]
    phases: List[Phase]
    security_requirements: List[str] = field(default_factory=list)
    estimated_loc: int = 0

    def to_dict(self) -> Dict[str, Any]:
        """Serialise to plain dict."""
        return {
            "scope": self.scope,
            "files": [
                {"path": f.path, "action": f.action, "functions": f.functions}
                for f in self.files
            ],
            "phases": [
                {
                    "name": p.name,
                    "files": p.files,
                    "functions": p.functions,
                    "security_review": p.security_review,
                }
                for p in self.phases
            ],
            "security_requirements": self.security_requirements,
            "estimated_loc": self.estimated_loc,
        }


class CodeLevelPlanner(OrchestratorProtocolMixin):
    """
    Generates file-level implementation plans for SDLC tasks.

    Responsibilities:
        - Scope analysis: identify affected files and modules
        - Phase decomposition: group changes into ordered phases
        - TDD ordering: tests before implementation in each phase
        - Security annotation: flag phases requiring security review
    """

    def analyze_task_scope(self, task_description: str) -> Dict[str, Any]:
        """
        Identify the scope of files and components affected by a task.

        Args:
            task_description: Natural-language task description.

        Returns:
            Dict with scope summary, files list, and components list.
        """
        lower = task_description.lower()
        # Phase 58 — cross-cutting hooks
        self._activate_cross_cutting_hooks(operation="analyze_task_scope")

        # Heuristic scope detection
        files: List[Dict[str, str]] = []
        components: List[str] = []
        scope_parts: List[str] = []

        if "api" in lower or "endpoint" in lower:
            files.append({"path": "cortex/api/handler.py", "action": "modify"})
            components.append("API handler")
            scope_parts.append("cortex/api")

        if "util" in lower or "helper" in lower:
            files.append({"path": "cortex/common/utils.py", "action": "modify"})
            components.append("utility functions")
            scope_parts.append("utils.py")

        if "test" in lower or "spec" in lower:
            files.append({"path": "tests/unit/test_handler.py", "action": "create"})
            components.append("unit tests")

        if not files:
            files.append({"path": "cortex/core/handler.py", "action": "modify"})
            components.append("core handler")
            scope_parts.append("cortex/core")

        return {
            "scope": ", ".join(scope_parts) if scope_parts else "cortex/core",
            "files": files,
            "components": components,
        }

    def generate_plan(
        self,
        task_description: str,
        complexity_result: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Generate a full file-level implementation plan.

        Args:
            task_description: Natural-language task description.
            complexity_result: Optional output from ComplexityClassifier.

        Returns:
            Dict with phases, files, security_requirements, estimated_loc.
        """
        scope = self.analyze_task_scope(task_description)
        complexity_result = complexity_result or {}
        level = complexity_result.get("level", "SIMPLE")

        phases: List[Phase] = []
        security_requirements: List[str] = []

        # Phase 1: Tests (TDD first — CORE-008)
        test_files = [f["path"] for f in scope["files"] if "test" in f["path"]]
        impl_files = [f["path"] for f in scope["files"] if "test" not in f["path"]]

        phases.append(
            Phase(
                name="Tests",
                files=test_files or ["tests/unit/test_impl.py"],
                functions=["test_" + c.replace(" ", "_") for c in scope["components"]],
            )
        )
        phases.append(
            Phase(
                name="Implementation",
                files=impl_files,
                functions=scope["components"],
            )
        )

        if level in ("COMPLEX", "CRITICAL"):
            phases.append(
                Phase(name="Integration Tests", files=["tests/integration/test_e2e.py"])
            )

        if level == "CRITICAL":
            security_requirements = [
                "OWASP A02:2021 – Cryptographic Failures",
                "OWASP A07:2021 – Identification and Authentication Failures",
            ]
            for p in phases:
                p.security_review = True

        all_files = [FilePlan(path=f["path"], action=f["action"]) for f in scope["files"]]

        plan = CodePlan(
            scope=scope["scope"],
            files=all_files,
            phases=phases,
            security_requirements=security_requirements,
            estimated_loc=complexity_result.get("loc_estimate", 50),
        )
        return plan.to_dict()
