# AC_START: AC-PHASE38.0-IMPL-004
# Stage 11: FileGovernanceValidator - Validate optimal folder structure
# Author: CORTEX Architect | Date: 2026-02-09
# Description: Validates that folder structure matches CORTEX architectural standards

from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class FolderStructureStatus(Enum):
    """Status of folder structure validation."""
    OPTIMAL = "optimal"
    ACCEPTABLE = "acceptable"
    NEEDS_IMPROVEMENT = "needs_improvement"
    CRITICAL = "critical"


@dataclass
class ValidationResult:
    """Result of folder structure validation."""
    status: FolderStructureStatus
    issues: List[str]
    recommendations: List[str]
    missing_directories: List[str]
    misplaced_files: List[str]
    structure_score: float  # 0.0 to 1.0


class FileGovernanceValidator:
    """
    Validates that folder structure meets CORTEX architectural standards.

    Expected Structure:
    ```
    cortex/
    ├── orchestrators/          (Core orchestrators)
    ├── agents/                 (Core agents)
    ├── governance/             (Governance rules & enforcement)
    ├── knowledge/              (Best practices & standards)
    ├── lens/                   (LENS code intelligence)
    ├── infrastructure/         (Infrastructure & deployment)
    └── ...

    cortex-registry/            (Master registry)
    ├── _cortex-master/
    ├── phases/
    └── ...

    tests/                      (All tests)
    ├── unit/
    ├── integration/
    └── e2e/

    docs/                       (All documentation)
    ```

    Responsibilities:
    - Validate directory structure exists
    - Check file placement is correct
    - Identify orphaned files
    - Validate naming conventions
    - Generate improvement recommendations
    """

    def __init__(self, workspace_root: Path):
        """Initialize validator with workspace root."""
        self.workspace_root = Path(workspace_root)
        self.required_dirs = self._build_required_dirs()
        self.expected_structure = self._build_expected_structure()

    def _build_required_dirs(self) -> Dict[str, List[str]]:
        """Build mapping of required directories."""
        return {
            "cortex": [
                "orchestrators",
                "orchestrators/support",
                "agents",
                "governance",
                "knowledge",
                "lens",
                "infrastructure",
                "deployment",
                "models",
                "common",
            ],
            "cortex-registry": [
                "_cortex-master",
                "phases",
            ],
            "tests": [
                "unit",
                "integration",
                "e2e",
            ],
            "docs": [],
        }

    def _build_expected_structure(self) -> Dict[str, str]:
        """
        Build expected structure for different file types.
        Format: pattern -> expected_location
        """
        return {
            "*_orchestrator.py": "cortex/orchestrators",
            "*_agent.py": "cortex/agents",
            "*_lens*.py": "cortex/lens",
            "test_*.py": "tests/unit",
            "*.md": "docs",
            "governance*.py": "cortex/governance",
            "*knowledge*.py": "cortex/knowledge",
        }

    def validate_structure(self) -> ValidationResult:
        """Perform comprehensive folder structure validation."""
        issues = []
        recommendations = []
        missing_dirs = []
        misplaced = []

        # Check required directories exist
        for root_dir, subdirs in self.required_dirs.items():
            base_path = self.workspace_root / root_dir

            if not base_path.exists():
                issues.append(f"Missing root directory: {root_dir}")
                missing_dirs.append(root_dir)
                continue

            for subdir in subdirs:
                subdir_path = base_path / subdir
                if not subdir_path.exists():
                    recommendations.append(f"Create directory: {root_dir}/{subdir}")
                    missing_dirs.append(f"{root_dir}/{subdir}")

        # Check file placement
        for py_file in self.workspace_root.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            expected_location = self._get_expected_location(py_file)
            actual_location = py_file.relative_to(self.workspace_root).parts[0]

            if expected_location and actual_location not in expected_location:
                misplaced.append(str(py_file.relative_to(self.workspace_root)))
                issues.append(f"Misplaced file: {py_file.relative_to(self.workspace_root)}")

        # Calculate structure score
        structure_score = self._calculate_score(
            len(issues),
            len(missing_dirs),
            len(misplaced)
        )

        # Determine status
        status = self._determine_status(structure_score, len(issues))

        return ValidationResult(
            status=status,
            issues=issues,
            recommendations=recommendations,
            missing_directories=missing_dirs,
            misplaced_files=misplaced,
            structure_score=structure_score
        )

    def _get_expected_location(self, file_path: Path) -> Optional[str]:
        """Get expected location for a file based on naming patterns."""
        file_name = file_path.name

        for pattern, location in self.expected_structure.items():
            if self._matches_pattern(file_name, pattern):
                return location

        return None

    def _matches_pattern(self, filename: str, pattern: str) -> bool:
        """Check if filename matches a pattern."""
        # Simple wildcard matching
        if "*" in pattern:
            parts = pattern.split("*")
            if len(parts) == 2:
                return filename.startswith(parts[0]) and filename.endswith(parts[1])
            elif parts[0] and filename.startswith(parts[0]):
                return True
            elif parts[1] and filename.endswith(parts[1]):
                return True
        return filename == pattern

    def _calculate_score(self, num_issues: int, num_missing: int, num_misplaced: int) -> float:
        """Calculate structure score from 0.0 to 1.0."""
        # Base score 1.0, deduct for problems
        score = 1.0
        score -= min(0.3, num_issues * 0.05)  # Issues
        score -= min(0.3, num_missing * 0.1)  # Missing dirs
        score -= min(0.4, num_misplaced * 0.02)  # Misplaced files
        return max(0.0, score)

    def _determine_status(self, score: float, num_issues: int) -> FolderStructureStatus:
        """Determine overall status based on score."""
        if score >= 0.95 and num_issues == 0:
            return FolderStructureStatus.OPTIMAL
        elif score >= 0.85:
            return FolderStructureStatus.ACCEPTABLE
        elif score >= 0.70:
            return FolderStructureStatus.NEEDS_IMPROVEMENT
        else:
            return FolderStructureStatus.CRITICAL

    def validate_naming_conventions(self) -> Tuple[bool, List[str]]:
        """Validate that all files follow naming conventions."""
        issues = []

        for py_file in self.workspace_root.rglob("*.py"):
            if self._should_skip(py_file):
                continue

            file_name = py_file.stem

            # Check for SCREAMING_CASE (forbidden)
            if self._is_screaming_case(file_name):
                issues.append(f"SCREAMING_CASE file: {file_name} (use kebab-case)")

            # Check for CamelCase (should be kebab-case)
            if self._is_camel_case(file_name):
                issues.append(f"CamelCase file: {file_name} (use kebab-case)")

        return len(issues) == 0, issues

    def _is_screaming_case(self, name: str) -> bool:
        """Check if name is SCREAMING_CASE."""
        return name.isupper() and "_" in name

    def _is_camel_case(self, name: str) -> bool:
        """Check if name is CamelCase."""
        return any(c.isupper() for c in name[1:]) and "_" not in name

    def generate_improvement_plan(self, result: ValidationResult) -> Dict:
        """Generate detailed improvement plan."""
        return {
            "current_status": result.status.value,
            "structure_score": result.structure_score,
            "priority_level": self._get_priority(result.status),
            "immediate_actions": [
                f"Create {dir}" for dir in result.missing_directories
            ] + result.recommendations[:5],  # Top 5 recommendations
            "follow_up_actions": result.recommendations[5:],
            "estimated_effort": self._estimate_effort(result),
            "automation_level": self._assess_automation(result),
        }

    def _get_priority(self, status: FolderStructureStatus) -> str:
        """Get priority level based on status."""
        return {
            FolderStructureStatus.OPTIMAL: "low",
            FolderStructureStatus.ACCEPTABLE: "low",
            FolderStructureStatus.NEEDS_IMPROVEMENT: "medium",
            FolderStructureStatus.CRITICAL: "high",
        }.get(status, "medium")

    def _estimate_effort(self, result: ValidationResult) -> str:
        """Estimate effort to fix issues."""
        total_work = len(result.missing_directories) + len(result.misplaced_files)

        if total_work == 0:
            return "None needed"
        elif total_work < 5:
            return "< 30 minutes"
        elif total_work < 15:
            return "30 minutes - 1 hour"
        else:
            return "> 1 hour"

    def _assess_automation(self, result: ValidationResult) -> str:
        """Assess how automatable the fixes are."""
        if len(result.issues) < 5 and len(result.misplaced_files) < 10:
            return "Fully automatable"
        elif len(result.issues) < 15:
            return "Mostly automatable"
        else:
            return "Requires manual review"

    def _should_skip(self, file_path: Path) -> bool:
        """Check if file should be skipped."""
        skip_patterns = [".venv", "__pycache__", ".git", "node_modules", ".egg-info", ".pytest_cache"]
        return any(pattern in file_path.parts for pattern in skip_patterns)


# AC_COMPLETE: AC-PHASE38.0-IMPL-004 ✅
