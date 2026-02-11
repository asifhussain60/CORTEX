"""CORE-028 file naming violation detector.

Scans workspace for Python files violating CORE-028 naming policy:
- Python files (.py) MUST use snake_case (underscores, not hyphens per PEP 8)
- File names MUST be ≤ 50 characters (excluding extension)
- Provides fix suggestions for violations

Phase 7.4, Task NAMING-001 (Updated for snake_case)
AC-ID: NAMING-001
"""

import enum
import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Dict, List, Optional


class ViolationType(enum.Enum):
    """Types of naming violations."""

    HYPHEN = "hyphen"  # Uses hyphen instead of underscore (Python should use snake_case)
    LENGTH = "length"  # Exceeds 50-character limit


@dataclass
class Violation:
    """Represents a single naming violation."""

    file_path: Path
    type: ViolationType
    current_name: str
    suggested_fix: str
    reason: str

    def to_dict(self) -> Dict:
        """Convert violation to dictionary for JSON serialization."""
        return {
            "file_path": str(self.file_path),
            "type": self.type.value,
            "current_name": self.current_name,
            "suggested_fix": self.suggested_fix,
            "reason": self.reason,
        }


class NamingViolationDetector:
    """Detects CORE-028 naming policy violations in Python files.

    Scans workspace for:
    1. Files using hyphens (should be snake_case per PEP 8)
    2. Files exceeding 50-character limit

    Provides fix suggestions for each violation.

    Args:
        workspace_root: Root directory to scan for violations

    Example:
        >>> detector = NamingViolationDetector(Path("/path/to/workspace"))
        >>> violations = detector.scan_workspace()
        >>> report = detector.generate_report(format="text")
        >>> print(report)
    """

    MAX_NAME_LENGTH = 50  # CORE-028 specification (excluding .py extension)

    def __init__(self, workspace_root: Path):
        """Initialize detector with workspace root.

        Args:
            workspace_root: Root directory to scan for violations
        """
        self.workspace_root = workspace_root
        self.violations: List[Violation] = []

    def scan_file(self, file_path: Path) -> List[Violation]:
        """Scan single file for naming violations.

        Args:
            file_path: Path to Python file to check

        Returns:
            List of violations found in file
        """
        violations = []

        # Only check .py files
        if file_path.suffix != ".py":
            return violations

        file_name = file_path.stem  # Name without extension

        # Check for hyphen violation (Python should use snake_case)
        if "-" in file_name:
            suggested = self.suggest_fix(file_path.name)
            violations.append(Violation(
                file_path=file_path,
                type=ViolationType.HYPHEN,
                current_name=file_path.name,
                suggested_fix=suggested,
                reason=f"File uses hyphens (CORE-028 requires snake_case for Python): {file_path.name}",
            ))

        # Check for length violation
        if len(file_name) > self.MAX_NAME_LENGTH:
            suggested = self.suggest_fix(file_path.name)
            violations.append(Violation(
                file_path=file_path,
                type=ViolationType.LENGTH,
                current_name=file_path.name,
                suggested_fix=suggested,
                reason=f"File name exceeds {self.MAX_NAME_LENGTH} characters (CORE-028): {len(file_name)} chars",
            ))

        return violations

    def scan_workspace(self) -> List[Violation]:
        """Scan entire workspace for naming violations.

        Returns:
            List of all violations found across workspace
        """
        self.violations = []

        # Recursively find all .py files
        for py_file in self.workspace_root.rglob("*.py"):
            file_violations = self.scan_file(py_file)
            self.violations.extend(file_violations)

        return self.violations

    def suggest_fix(self, file_name: str) -> str:
        """Suggest compliant file name for violation.

        Args:
            file_name: Current file name (with extension)

        Returns:
            Suggested compliant file name (snake_case)
        """
        # Split name and extension
        name_parts = file_name.rsplit(".", 1)
        name = name_parts[0]
        ext = f".{name_parts[1]}" if len(name_parts) > 1 else ""

        # Fix hyphens → underscores (convert to snake_case)
        name = name.replace("-", "_")

        # Fix length (truncate if needed)
        if len(name) > self.MAX_NAME_LENGTH:
            # Try to truncate at word boundary
            truncated = name[:self.MAX_NAME_LENGTH]

            # If truncation cuts mid-word, remove last partial word
            if "_" in truncated:
                parts = truncated.split("_")
                # Remove last part if it's incomplete
                if len(truncated) == self.MAX_NAME_LENGTH and name[self.MAX_NAME_LENGTH] != "_":
                    truncated = "_".join(parts[:-1])

            name = truncated

        return f"{name}{ext}"

    def generate_report(self, format: str = "text") -> str:
        """Generate violation report in specified format.

        Args:
            format: Report format ("text" or "json")

        Returns:
            Formatted report string
        """
        if format == "json":
            return self._generate_json_report()
        else:
            return self._generate_text_report()

    def _generate_json_report(self) -> str:
        """Generate JSON format report.

        Returns:
            JSON string with violations
        """
        report_data = {
            "total_violations": len(self.violations),
            "violations_by_type": {
                "hyphen": len([v for v in self.violations if v.type == ViolationType.HYPHEN]),
                "length": len([v for v in self.violations if v.type == ViolationType.LENGTH]),
            },
            "violations": [v.to_dict() for v in self.violations],
        }
        return json.dumps(report_data, indent=2)

    def _generate_text_report(self) -> str:
        """Generate human-readable text report.

        Returns:
            Text report with violations and fix suggestions
        """
        if not self.violations:
            return "✅ No CORE-028 naming violations found!"

        lines = [
            "=" * 80,
            "CORE-028 File Naming Violations",
            "=" * 80,
            f"\nTotal Violations: {len(self.violations)}",
            f"  - Hyphen violations: {len([v for v in self.violations if v.type == ViolationType.HYPHEN])}",
            f"  - Length violations: {len([v for v in self.violations if v.type == ViolationType.LENGTH])}",
            "\n" + "=" * 80,
            "Violations by File:",
            "=" * 80,
        ]

        # Group violations by file
        violations_by_file: Dict[Path, List[Violation]] = {}
        for violation in self.violations:
            if violation.file_path not in violations_by_file:
                violations_by_file[violation.file_path] = []
            violations_by_file[violation.file_path].append(violation)

        # Format each file's violations
        for file_path, file_violations in violations_by_file.items():
            lines.append(f"\n📄 {file_path}")
            for violation in file_violations:
                lines.append(f"   ❌ {violation.type.value.upper()}: {violation.reason}")
                lines.append(f"   ✅ Suggested fix: {violation.suggested_fix}")

        lines.append("\n" + "=" * 80)
        return "\n".join(lines)


def main() -> None:
    """CLI entry point for naming violation detector.

    Usage:
        python -m cortex.tools.naming_violation_detector [workspace_path]
    """
    import sys

    # Get workspace path from args or use current directory
    if len(sys.argv) > 1:
        workspace_path = Path(sys.argv[1])
    else:
        workspace_path = Path.cwd()

    print(f"Scanning workspace: {workspace_path}")

    # Run detector
    detector = NamingViolationDetector(workspace_root=workspace_path)
    violations = detector.scan_workspace()

    # Generate and print report
    report = detector.generate_report(format="text")
    print(report)

    # Exit with error code if violations found
    sys.exit(1 if violations else 0)


if __name__ == "__main__":
    main()
