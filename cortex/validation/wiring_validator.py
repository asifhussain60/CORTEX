#!/usr/bin/env python3
"""
Wiring.yaml Accuracy Validator (Phase 76 S1 T6)

Validates that wiring.yaml specifications match actual orchestrator implementations.
Supports --strict mode for CI/CD gates.

AC_START: AC-PHASE76-S1-T6-001
Authority: Production Foundation Trilogy
Pattern: TDD + CI/CD Integration
"""

import os
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


class Severity(str, Enum):
    """Validation severity levels."""
    P0 = "P0_BLOCKER"      # Production blocker
    P1 = "P1_CRITICAL"     # Should fix before merge
    P2 = "P2_WARNING"      # Nice-to-have
    INFO = "INFO"          # Informational only


@dataclass
class ValidationResult:
    """Single validation result."""
    orchestrator: str
    severity: Severity
    status: str  # PASS | FAIL | SKIP
    reason: str
    module: str = ""
    expected_class: str = ""


class WiringValidator:
    """Validates wiring.yaml against actual implementations."""

    def __init__(self, wiring_path: str = "cortex/wiring/specifications/wiring.yaml"):
        self.wiring_path = wiring_path
        self.results: List[ValidationResult] = []

    def load_wiring(self) -> Dict:
        """Load wiring.yaml specification."""
        with open(self.wiring_path) as f:
            return yaml.safe_load(f)

    def check_implementation(self, module_path: str, class_name: str) -> Tuple[bool, str]:
        """
        Check if orchestrator implementation exists.

        Returns:
            (exists, reason) tuple
        """
        file_path = module_path.replace(".", "/") + ".py"

        if not os.path.exists(file_path):
            return False, f"FILE_MISSING: {file_path}"

        with open(file_path) as f:
            content = f.read()
            if f"class {class_name}" in content:
                return True, "IMPLEMENTED"
            else:
                return False, f"CLASS_MISSING: {class_name} not found in {file_path}"

    def validate_orchestrator(self, orch: Dict) -> ValidationResult:
        """Validate single orchestrator."""
        name = orch.get("name", "unknown")
        module = orch.get("module", "")
        cls = orch.get("class", "")
        status = orch.get("status", "active")
        target_phase = orch.get("target_phase", "")

        # Skip pending implementations (these are OK)
        if status in ["pending_implementation", "enhancement_integrated"]:
            return ValidationResult(
                orchestrator=name,
                severity=Severity.INFO,
                status="SKIP",
                reason=f"Marked as {status}, target: {target_phase}",
                module=module,
                expected_class=cls
            )

        # Skip if no module/class specified (incomplete spec)
        if not module or not cls:
            return ValidationResult(
                orchestrator=name,
                severity=Severity.P2,
                status="FAIL",
                reason="Incomplete specification (missing module or class)",
                module=module,
                expected_class=cls
            )

        # Check implementation
        exists, reason = self.check_implementation(module, cls)

        if exists:
            return ValidationResult(
                orchestrator=name,
                severity=Severity.INFO,
                status="PASS",
                reason="Implementation verified",
                module=module,
                expected_class=cls
            )
        else:
            # Missing implementation is P0 blocker
            return ValidationResult(
                orchestrator=name,
                severity=Severity.P0,
                status="FAIL",
                reason=reason,
                module=module,
                expected_class=cls
            )

    def validate_all(self) -> bool:
        """
        Validate all orchestrators.

        Returns:
            True if all validations pass (or are skipped), False otherwise
        """
        wiring = self.load_wiring()
        orchestrators_by_category = wiring.get("orchestrators", {})

        all_orchestrators = []
        for category, orch_list in orchestrators_by_category.items():
            if isinstance(orch_list, list):
                all_orchestrators.extend(orch_list)

        for orch in all_orchestrators:
            result = self.validate_orchestrator(orch)
            self.results.append(result)

        # Check if any P0/P1 failures
        p0_failures = [r for r in self.results if r.severity == Severity.P0 and r.status == "FAIL"]
        p1_failures = [r for r in self.results if r.severity == Severity.P1 and r.status == "FAIL"]

        return len(p0_failures) == 0 and len(p1_failures) == 0

    def report(self, strict: bool = False) -> None:
        """
        Print validation report.

        Args:
            strict: If True, fail on any P0/P1 issues. If False, warn only.
        """
        # Count results
        passed = [r for r in self.results if r.status == "PASS"]
        skipped = [r for r in self.results if r.status == "SKIP"]
        failed = [r for r in self.results if r.status == "FAIL"]

        p0_failures = [r for r in failed if r.severity == Severity.P0]
        p1_failures = [r for r in failed if r.severity == Severity.P1]
        p2_warnings = [r for r in failed if r.severity == Severity.P2]

        total = len(self.results)
        implemented = len(passed)
        pending = len(skipped)
        missing = len(p0_failures)

        accuracy = (implemented / (total - pending)) * 100 if (total - pending) > 0 else 0

        # Header
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print("🔍 Wiring.yaml Accuracy Validation")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()

        # Summary
        print(f"Total Orchestrators: {total}")
        print(f"├─ Implemented: {implemented} ({implemented/total*100:.1f}%)")
        print(f"├─ Pending: {pending} ({pending/total*100:.1f}%)")
        print(f"└─ Missing: {missing} ({missing/total*100:.1f}%)")
        print()
        print(f"🎯 Wiring Accuracy: {accuracy:.1f}%")
        print(f"   (excluding {pending} pending orchestrators)")
        print()

        # P0 failures (blockers)
        if p0_failures:
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("🔴 P0 BLOCKERS (Missing Implementations)")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print()
            for result in p0_failures:
                print(f"  {result.orchestrator}")
                print(f"    Module: {result.module}")
                print(f"    Class: {result.expected_class}")
                print(f"    Reason: {result.reason}")
                print()

        # P1 failures (critical)
        if p1_failures:
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("🟡 P1 CRITICAL")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print()
            for result in p1_failures:
                print(f"  {result.orchestrator}: {result.reason}")
            print()

        # P2 warnings
        if p2_warnings and not strict:
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("⚠️  P2 WARNINGS")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print()
            for result in p2_warnings:
                print(f"  {result.orchestrator}: {result.reason}")
            print()

        # Pending orchestrators (info)
        if skipped and not strict:
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("ℹ️  Pending Implementations")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print()

            # Group by target phase
            by_phase = {}
            for result in skipped:
                target = result.reason.split("target: ")[-1]
                if target not in by_phase:
                    by_phase[target] = []
                by_phase[target].append(result.orchestrator)

            for phase, orches in sorted(by_phase.items()):
                print(f"  {phase}: {len(orches)} orchestrators")
                for orch in orches:
                    print(f"    - {orch}")
            print()

        # Final verdict
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        if accuracy == 100.0 and len(p0_failures) == 0:
            print("✅ PASS: 100% wiring accuracy")
            if strict:
                print("   CI/CD gate: PASSED")
        else:
            if strict:
                print("❌ FAIL: CI/CD gate BLOCKED")
                print(f"   {len(p0_failures)} P0 blockers")
                print(f"   {len(p1_failures)} P1 critical issues")
            else:
                print(f"⚠️  WARNING: {accuracy:.1f}% accuracy")
                print(f"   {len(p0_failures)} missing implementations")
        print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
        print()


def main():
    """Main entry point."""
    strict = "--strict" in sys.argv

    if strict:
        print("🔒 Running in STRICT mode (CI/CD gate)")
        print()

    validator = WiringValidator()
    passed = validator.validate_all()
    validator.report(strict=strict)

    # Exit with error if strict mode and failures
    if strict and not passed:
        sys.exit(1)

    sys.exit(0)


if __name__ == "__main__":
    main()

# AC_COMPLETE: AC-PHASE76-S1-T6-001
