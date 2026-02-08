"""Phase 47 S3: Code References Update.

Update imports and references to use dual-path resolver.
"""

from dataclasses import dataclass
from typing import Any, Dict, List, Tuple
from pathlib import Path
import re


@dataclass
class CodeReference:
    """A code reference to legacy paths."""

    file_path: str
    line_number: int
    original_code: str
    suggested_code: str
    reference_type: str  # "import", "path", "config", "variable"
    severity: str  # "high", "medium", "low"


class CodeReferenceAnalyzer:
    """Analyze code for legacy path references."""

    LEGACY_PATTERNS = [
        (r"company\s*=\s*['\"]([^'\"]+)['\"]", "legacy_path_assignment"),
        (r"from\s+company\s*\.", "legacy_import"),
        (r"import\s+company\b", "legacy_import"),
        (r"['\"]company/", "legacy_path_string"),
        (r"['\"].*_archive/", "archive_reference"),
    ]

    def __init__(self, root_dir: str = "/Users/asifhussain/PROJECTS/CORTEX"):
        """Initialize analyzer.

        Args:
            root_dir: Root directory to analyze
        """
        self.root_dir = root_dir
        self.references: List[CodeReference] = []

    def analyze_file(self, file_path: str) -> List[CodeReference]:
        """Analyze a single file for legacy references.

        Args:
            file_path: Path to file to analyze

        Returns:
            List of CodeReference objects found.
        """
        references = []

        if not Path(file_path).exists():
            return references

        try:
            with open(file_path, 'r') as f:
                lines = f.readlines()
        except Exception:
            return references

        for line_num, line in enumerate(lines, 1):
            for pattern, ref_type in self.LEGACY_PATTERNS:
                matches = re.finditer(pattern, line)
                for match in matches:
                    ref = CodeReference(
                        file_path=file_path,
                        line_number=line_num,
                        original_code=line.strip(),
                        suggested_code=self._suggest_fix(line, ref_type),
                        reference_type=ref_type,
                        severity=self._classify_severity(ref_type),
                    )
                    references.append(ref)

        self.references.extend(references)
        return references

    def analyze_directory(self, directory: str, pattern: str = "*.py") -> List[CodeReference]:
        """Analyze directory for legacy references.

        Args:
            directory: Directory to analyze
            pattern: File pattern to match

        Returns:
            List of all CodeReference objects found.
        """
        references = []

        for file_path in Path(directory).rglob(pattern):
            if ".venv" in str(file_path):
                continue
            if "__pycache__" in str(file_path):
                continue

            file_refs = self.analyze_file(str(file_path))
            references.extend(file_refs)

        return references

    def get_references_by_severity(self, severity: str) -> List[CodeReference]:
        """Get references by severity level.

        Args:
            severity: "high", "medium", or "low"

        Returns:
            List of CodeReference objects with specified severity.
        """
        return [ref for ref in self.references if ref.severity == severity]

    def get_references_by_type(self, ref_type: str) -> List[CodeReference]:
        """Get references by type.

        Args:
            ref_type: Reference type to filter by

        Returns:
            List of CodeReference objects of specified type.
        """
        return [ref for ref in self.references if ref.reference_type == ref_type]

    def _suggest_fix(self, line: str, ref_type: str) -> str:
        """Suggest fix for a reference.

        Args:
            line: Original line of code
            ref_type: Type of reference

        Returns:
            Suggested fixed code.
        """
        if ref_type == "legacy_import":
            # Handle both "from company." and "import company"
            if "from company" in line:
                return line.replace("from company.", "from cortex_brain.")
            else:
                return line.replace("import company", "from cortex.wiring import registry")
        elif ref_type == "legacy_path_assignment":
            return line.replace('company', 'resolver.resolve')
        elif ref_type == "legacy_path_string":
            return line.replace("'company/", "'registry_path/").replace('"company/', '"registry_path/')
        elif ref_type == "archive_reference":
            return line.replace("_archive/", "deprecated/")
        else:
            return line

    def _classify_severity(self, ref_type: str) -> str:
        """Classify severity of reference.

        Args:
            ref_type: Reference type

        Returns:
            Severity level: "high", "medium", "low"
        """
        if ref_type == "legacy_import":
            return "high"
        elif ref_type == "legacy_path_assignment":
            return "medium"
        elif ref_type == "archive_reference":
            return "high"
        else:
            return "low"

    def get_summary(self) -> Dict[str, Any]:
        """Get summary of analysis.

        Returns:
            Dictionary with analysis summary.
        """
        return {
            "total_references": len(self.references),
            "high_severity": len(self.get_references_by_severity("high")),
            "medium_severity": len(self.get_references_by_severity("medium")),
            "low_severity": len(self.get_references_by_severity("low")),
            "by_type": {
                "legacy_import": len(self.get_references_by_type("legacy_import")),
                "legacy_path": len(self.get_references_by_type("legacy_path_string")),
                "archive": len(self.get_references_by_type("archive_reference")),
            },
        }


class CodeReferenceUpdater:
    """Update code references to use dual-path resolver."""

    def __init__(self, resolver_path: str = "from cortex.orchestrators.company_separation import DualPathResolver"):
        """Initialize updater.

        Args:
            resolver_path: Import path for resolver
        """
        self.resolver_path = resolver_path
        self.updates: List[Tuple[str, str, str]] = []

    def apply_update(self, file_path: str, original: str, replacement: str) -> bool:
        """Apply update to file.

        Args:
            file_path: Path to file to update
            original: Original code
            replacement: Replacement code

        Returns:
            True if update successful.
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            if original not in content:
                return False

            updated_content = content.replace(original, replacement)

            with open(file_path, 'w') as f:
                f.write(updated_content)

            self.updates.append((file_path, original, replacement))
            return True
        except Exception:
            return False

    def get_update_count(self) -> int:
        """Get number of updates applied.

        Returns:
            Count of updates applied.
        """
        return len(self.updates)

    def get_update_summary(self) -> str:
        """Get summary of updates applied.

        Returns:
            Summary string.
        """
        return f"Applied {len(self.updates)} updates to {len(set(up[0] for up in self.updates))} files"


class MigrationPlan:
    """Migration plan for code reference updates."""

    def __init__(self):
        """Initialize migration plan."""
        self.steps: List[Dict[str, Any]] = []
        self.estimated_effort: float = 0.0

    def add_step(
        self,
        step_number: int,
        description: str,
        affected_files: List[str],
        estimated_hours: float,
        priority: str = "medium",
    ) -> None:
        """Add migration step.

        Args:
            step_number: Step number
            description: Step description
            affected_files: List of affected files
            estimated_hours: Estimated effort in hours
            priority: Step priority (low/medium/high)
        """
        self.steps.append(
            {
                "step": step_number,
                "description": description,
                "affected_files": affected_files,
                "estimated_hours": estimated_hours,
                "priority": priority,
            }
        )
        self.estimated_effort += estimated_hours

    def get_high_priority_steps(self) -> List[Dict[str, Any]]:
        """Get high priority steps.

        Returns:
            List of high priority migration steps.
        """
        return [s for s in self.steps if s["priority"] == "high"]

    def get_total_effort(self) -> float:
        """Get total estimated effort.

        Returns:
            Total estimated effort in hours.
        """
        return self.estimated_effort

    def get_affected_files(self) -> List[str]:
        """Get all affected files.

        Returns:
            List of all affected files.
        """
        files = set()
        for step in self.steps:
            files.update(step["affected_files"])
        return sorted(list(files))
