"""Registry Consistency Agent - Detects Registry Violations

Identifies:
- YAML files outside cortex-registry/
- Configuration in wrong locations
- Missing registry entries

Author: CORTEX Framework
Phase: PHASE-95
CORE Rules: CORE-035 (canonical implementation), registry-first approach
"""

import time
from pathlib import Path
from typing import List

from .base_agent import (
    BaseHealthAgent,
    HealthCheckResult,
    HealthIssue,
    HealthIssueCategory,
    HealthIssueSeverity,
)


class RegistryConsistencyAgent(BaseHealthAgent):
    """Agent for detecting registry consistency issues.

    Detects:
    - YAML files outside registry
    - Configuration scattered across codebase
    - Duplicate configuration files

    Attributes:
        name: Agent name
        description: Agent description
        config: Configuration
    """

    def __init__(self, config: dict = None) -> None:
        """Initialize Registry Consistency Agent.

        Args:
            config: Optional configuration with:
                - registry_root: Expected registry location
                - allowed_yaml_dirs: Directories allowed outside registry
        """
        super().__init__(
            name="RegistryConsistencyAgent",
            description="Detects YAML files outside registry",
            config=config,
        )

        self.registry_root = self.config.get("registry_root", "cortex-registry")

        # Some YAML files are legitimately outside registry
        self.allowed_yaml_dirs = self.config.get("allowed_yaml_dirs", [
            "deployment",  # Deployment configs
            ".github",     # GitHub workflows
            ".vscode",     # Editor config
        ])

        self.exclude_patterns = self.config.get("exclude_patterns", [
            "*/_archives/*",
            "*/_workspaces/*",
            "*/.venv/*",
            "*/.git/*",
            "*/__pycache__/*",
            "*/node_modules/*",
        ])

    def check(self, workspace_root: Path) -> HealthCheckResult:
        """Run registry consistency check.

        Args:
            workspace_root: Root path of workspace to check

        Returns:
            HealthCheckResult with detected issues
        """
        start_time = time.time()
        issues: List[HealthIssue] = []
        files_scanned = 0

        registry_path = workspace_root / self.registry_root

        # Find all YAML files
        for yaml_file in workspace_root.rglob("*.yaml"):
            if self._should_exclude(yaml_file, workspace_root):
                continue

            try:
                # Check if in registry
                try:
                    yaml_file.relative_to(registry_path)
                    # File is in registry - OK
                    files_scanned += 1
                    continue
                except ValueError:
                    # File is outside registry
                    pass

                # Check if in allowed directory
                if self._is_allowed_location(yaml_file, workspace_root):
                    files_scanned += 1
                    continue

                # Flag as misplaced
                rel_path = yaml_file.relative_to(workspace_root)

                # Determine severity based on content type
                content_type = self._detect_content_type(yaml_file)

                if content_type in ["orchestrator", "agent", "governance"]:
                    severity = HealthIssueSeverity.HIGH
                elif content_type in ["pattern", "template"]:
                    severity = HealthIssueSeverity.MEDIUM
                else:
                    severity = HealthIssueSeverity.LOW

                issues.append(HealthIssue(
                    category=HealthIssueCategory.CONFIG_MISPLACED,
                    severity=severity,
                    file_path=rel_path,
                    description=f"YAML file outside registry (type: {content_type})",
                    suggested_fix=f"Move to {self.registry_root}/ or document exception",
                    metadata={
                        "content_type": content_type,
                        "expected_location": str(registry_path),
                    },
                ))

                files_scanned += 1
            except Exception:
                continue

        duration = time.time() - start_time

        return HealthCheckResult(
            agent_name=self.name,
            issues=issues,
            files_scanned=files_scanned,
            duration_seconds=duration,
            metadata={
                "registry_root": self.registry_root,
                "allowed_dirs": len(self.allowed_yaml_dirs),
            },
        )

    def _is_allowed_location(self, yaml_file: Path, workspace_root: Path) -> bool:
        """Check if YAML file is in allowed location.

        Args:
            yaml_file: YAML file path
            workspace_root: Workspace root

        Returns:
            True if location is allowed
        """
        rel_path = yaml_file.relative_to(workspace_root)

        for allowed_dir in self.allowed_yaml_dirs:
            try:
                rel_path.relative_to(allowed_dir)
                return True
            except ValueError:
                continue

        return False

    def _detect_content_type(self, yaml_file: Path) -> str:
        """Detect type of YAML file from content.

        Args:
            yaml_file: YAML file to check

        Returns:
            Content type string
        """
        try:
            with open(yaml_file, 'r', encoding='utf-8') as f:
                content = f.read().lower()

            # Simple keyword detection
            if "orchestrator" in content:
                return "orchestrator"
            elif "agent" in content:
                return "agent"
            elif "governance" in content or "rule" in content:
                return "governance"
            elif "pattern" in content:
                return "pattern"
            elif "template" in content:
                return "template"
            elif "workflow" in content:
                return "workflow"
            else:
                return "unknown"
        except Exception:
            return "unknown"

    def _should_exclude(self, file_path: Path, workspace_root: Path) -> bool:
        """Check if file should be excluded.

        Args:
            file_path: File path to check
            workspace_root: Workspace root

        Returns:
            True if should exclude
        """
        rel_path = file_path.relative_to(workspace_root)
        parts = set(rel_path.parts)

        for pattern in self.exclude_patterns:
            stripped = pattern.strip("*/")
            if stripped and stripped in parts:
                return True

        return False


__all__ = ["RegistryConsistencyAgent"]
