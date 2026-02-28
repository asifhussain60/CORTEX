"""repo_detection_orchestrator.py — Repo Detection Orchestrator.

Detects repository type, language, and key metadata from a filesystem path
(Phase 84-d, GAP-84-14). Uses heuristics based on presence of config files
(pyproject.toml, package.json, Cargo.toml, etc.) and directory structure.

Authority: CORE-011 (type hints), CORE-012 (docstrings)
"""
from __future__ import annotations
from typing import Any
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
from cortex.core.workflow_enforcement_mixin import WorkflowEnforcementMixin  # Phase 94f


class RepoDetectionOrchestrator(OrchestratorProtocolMixin, WorkflowEnforcementMixin):
    """Detects and classifies repositories in the workspace."""

    orchestrator_name = "RepoDetectionOrchestrator"
    domain = "support"
    # Phase 94f — advisory: repo detection utility; not a primary code-touching entry point.
    PHASE90_GATEWAY_ENABLED: bool = False

    def __init__(self) -> None:
        """Initialise RepoDetectionOrchestrator."""
        self._request_count = 0
        self._success_count = 0

    def detect(self, path: str) -> dict[str, Any]:
        """Detect repository at path using filesystem heuristics.

        Args:
            path: Filesystem path to inspect.

        Returns:
            Detection result with repo metadata including language and type.
        """
        self._activate_cross_cutting_hooks(operation="detect")
        self._request_count += 1
        from pathlib import Path as _Path
        p = _Path(path)
        language = None
        repo_type = "unknown"
        detected = p.exists()
        if detected:
            if (p / "pyproject.toml").exists() or (p / "setup.py").exists() or (p / "requirements.txt").exists():
                language = "python"
                repo_type = "python-package"
            elif (p / "package.json").exists():
                language = "javascript"
                repo_type = "node-package"
            elif (p / "Cargo.toml").exists():
                language = "rust"
                repo_type = "rust-crate"
            elif (p / "go.mod").exists():
                language = "go"
                repo_type = "go-module"
            elif (p / "pom.xml").exists() or (p / "build.gradle").exists():
                language = "java"
                repo_type = "jvm-project"
        self._success_count += 1
        return {"path": path, "detected": detected, "language": language, "repo_type": repo_type}

    def health_check(self) -> dict[str, Any]:
        """Return health status."""
        return {"status": "healthy", "orchestrator": self.orchestrator_name,
                "uptime_requests": self._request_count, "success_count": self._success_count, "last_success": None}
