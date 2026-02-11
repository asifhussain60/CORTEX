#!/usr/bin/env python3
"""
CORE-035 Enforcement: Single Canonical Implementation

Detects and reports duplicate implementations across the codebase.
Used by pre-commit hooks and CI/CD pipelines.

Authority: cortex_brain/tier0/governance/core-rules.yaml (CORE-035)
AC-ID: AC-CORE-035-ENFORCEMENT-001

Usage:
    python cortex/ci_cd/enforce_core_035.py [--fix] [--verbose]

Author: Asif Hussain
Date: 2026-01-29
"""

import ast
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


class ViolationType(Enum):
    """Types of CORE-035 violations."""
    FORBIDDEN_FILENAME = "forbidden_filename"
    DUPLICATE_REGISTRY = "duplicate_registry"
    DUPLICATE_BOOTSTRAP = "duplicate_bootstrap"
    DUPLICATE_GET_ORCHESTRATOR = "duplicate_get_orchestrator"
    ALTERNATE_YAML_REGISTRY = "alternate_yaml_registry"
    COMPETING_IMPLEMENTATION = "competing_implementation"


@dataclass
class Violation:
    """CORE-035 violation record."""
    type: ViolationType
    severity: str  # "blocked", "warning"
    file_path: Path
    description: str
    remediation: str


class Core035Enforcer:
    """Enforces CORE-035: Single Canonical Implementation."""

    FORBIDDEN_PATTERNS = [
        "*_unified.py",
        "*_refactored.py",
        "*_v2.py",
        "*_v3.py",
        "*_alternative.py",
        "*_new.py",
        "*_old.py",
        "*_legacy.py",
        "*_backup.py",
    ]

    CANONICAL_LOCATIONS = {
        "bootstrap_cortex": "cortex/wiring/bootstrap.py",
        "GitBackedRegistry": "cortex/wiring/registry/git_backed_registry.py",
        "get_registry": "cortex/wiring/registry/git_backed_registry.py",
        "wiring.yaml": "cortex/wiring/specifications/wiring.yaml",
    }

    def __init__(self, cortex_root: Path, verbose: bool = False):
        """
        Initialize enforcer.

        Args:
            cortex_root: Path to CORTEX repository root
            verbose: Enable verbose logging
        """
        self.cortex_root = cortex_root
        self.verbose = verbose
        self.violations: List[Violation] = []

    def log(self, message: str) -> None:
        """Log message if verbose."""
        if self.verbose:
            print(f"[CORE-035] {message}")

    def check_forbidden_filenames(self) -> List[Violation]:
        """Check for forbidden filename patterns."""
        violations: List[Violation] = []
        cortex_dir = self.cortex_root / "cortex"

        for pattern in self.FORBIDDEN_PATTERNS:
            for file_path in cortex_dir.rglob(pattern):
                if "test" in str(file_path):
                    continue

                violations.append(Violation(
                    type=ViolationType.FORBIDDEN_FILENAME,
                    severity="blocked",
                    file_path=file_path,
                    description=f"Forbidden filename pattern: {file_path.name}",
                    remediation=(
                        f"Rename to canonical name or delete if duplicate. "
                        f"Pattern '{pattern}' not allowed per CORE-035."
                    )
                ))
                self.log(f"Found forbidden file: {file_path.relative_to(self.cortex_root)}")

        return violations

    def check_duplicate_functions(self, function_name: str, canonical_path: str) -> List[Violation]:
        """Check for duplicate function implementations."""
        violations: List[Violation] = []
        locations: List[Path] = []
        cortex_dir = self.cortex_root / "cortex"

        for py_file in cortex_dir.rglob("*.py"):
            if "test" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.FunctionDef) and node.name == function_name:
                        locations.append(py_file)
                        break
            except Exception as e:
                self.log(f"Failed to parse {py_file}: {e}")

        if len(locations) > 1:
            canonical = self.cortex_root / canonical_path
            duplicates = [loc for loc in locations if loc != canonical]

            for dup in duplicates:
                violations.append(Violation(
                    type=ViolationType.DUPLICATE_BOOTSTRAP,
                    severity="blocked",
                    file_path=dup,
                    description=f"Duplicate {function_name}() implementation",
                    remediation=(
                        f"Remove duplicate. Canonical implementation: {canonical_path}"
                    )
                ))
                self.log(f"Found duplicate {function_name}: {dup.relative_to(self.cortex_root)}")

        return violations

    def check_duplicate_classes(self, class_pattern: str) -> List[Violation]:
        """Check for duplicate class implementations."""
        violations: List[Violation] = []
        class_locations: Dict[str, List[Path]] = {}
        cortex_dir = self.cortex_root / "cortex"

        for py_file in cortex_dir.rglob("*.py"):
            if "test" in str(py_file):
                continue

            try:
                content = py_file.read_text()
                tree = ast.parse(content)

                for node in ast.walk(tree):
                    if isinstance(node, ast.ClassDef):
                        if class_pattern in node.name:
                            if node.name not in class_locations:
                                class_locations[node.name] = []
                            class_locations[node.name].append(py_file)
            except Exception as e:
                self.log(f"Failed to parse {py_file}: {e}")

        for class_name, locations in class_locations.items():
            if len(locations) > 1:
                for loc in locations[1:]:  # First is canonical
                    violations.append(Violation(
                        type=ViolationType.DUPLICATE_REGISTRY,
                        severity="blocked",
                        file_path=loc,
                        description=f"Duplicate class: {class_name}",
                        remediation=(
                            f"Remove duplicate. Canonical: {locations[0].relative_to(self.cortex_root)}"
                        )
                    ))
                    self.log(f"Found duplicate class {class_name}: {loc.relative_to(self.cortex_root)}")

        return violations

    def check_alternate_yaml_registries(self) -> List[Violation]:
        """Check for alternate YAML registry files."""
        violations: List[Violation] = []
        canonical_yaml = self.cortex_root / self.CANONICAL_LOCATIONS["wiring.yaml"]
        cortex_dir = self.cortex_root / "cortex"

        yaml_files = list(cortex_dir.rglob("*orchestrator*.yaml"))
        yaml_files = [
            f for f in yaml_files
            if f != canonical_yaml and "test" not in str(f)
        ]

        for yaml_file in yaml_files:
            violations.append(Violation(
                type=ViolationType.ALTERNATE_YAML_REGISTRY,
                severity="blocked",
                file_path=yaml_file,
                description="Alternate orchestrator YAML registry",
                remediation=(
                    f"Remove or migrate to canonical: {self.CANONICAL_LOCATIONS['wiring.yaml']}"
                )
            ))
            self.log(f"Found alternate YAML: {yaml_file.relative_to(self.cortex_root)}")

        return violations

    def run_all_checks(self) -> bool:
        """
        Run all CORE-035 enforcement checks.

        Returns:
            True if no violations, False otherwise
        """
        self.log("Starting CORE-035 enforcement checks...")

        # Check 1: Forbidden filenames
        self.violations.extend(self.check_forbidden_filenames())

        # Check 2: Duplicate bootstrap_cortex
        self.violations.extend(
            self.check_duplicate_functions("bootstrap_cortex", self.CANONICAL_LOCATIONS["bootstrap_cortex"])
        )

        # Check 3: Duplicate Registry classes
        self.violations.extend(self.check_duplicate_classes("Registry"))

        # Check 4: Alternate YAML registries
        self.violations.extend(self.check_alternate_yaml_registries())

        return len(self.violations) == 0

    def report(self) -> str:
        """Generate violation report."""
        if not self.violations:
            return "✅ CORE-035 PASSED: No duplicate implementations found"

        blocked = [v for v in self.violations if v.severity == "blocked"]
        warnings = [v for v in self.violations if v.severity == "warning"]

        report = [
            "=" * 80,
            "❌ CORE-035 VIOLATIONS DETECTED",
            "=" * 80,
            f"Blocked: {len(blocked)} | Warnings: {len(warnings)}",
            ""
        ]

        if blocked:
            report.append("🚫 BLOCKED VIOLATIONS (Must fix before commit):")
            report.append("-" * 80)
            for v in blocked:
                report.append(f"  Type: {v.type.value}")
                report.append(f"  File: {v.file_path.relative_to(self.cortex_root)}")
                report.append(f"  Issue: {v.description}")
                report.append(f"  Fix: {v.remediation}")
                report.append("")

        if warnings:
            report.append("⚠️  WARNINGS (Review recommended):")
            report.append("-" * 80)
            for v in warnings:
                report.append(f"  Type: {v.type.value}")
                report.append(f"  File: {v.file_path.relative_to(self.cortex_root)}")
                report.append(f"  Issue: {v.description}")
                report.append("")

        report.append("=" * 80)

        return "\n".join(report)


def main() -> int:
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="CORE-035 Enforcement: Single Canonical Implementation"
    )
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--fix", action="store_true", help="Auto-fix violations (future)")

    args = parser.parse_args()

    cortex_root = Path(__file__).parent.parent.parent
    enforcer = Core035Enforcer(cortex_root, verbose=args.verbose)

    passed = enforcer.run_all_checks()
    print(enforcer.report())

    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(main())
