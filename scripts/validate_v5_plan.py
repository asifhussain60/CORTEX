#!/usr/bin/env python3
"""
CORTEX Planning System - V5 Plan Validation

Purpose: Validate that a plan meets V5 architecture requirements
Author: Asif Hussain
Created: January 3, 2026
Version: 1.0.0
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Tuple


class V5PlanValidator:
    """Validate V5 plan structure and compliance."""

    def __init__(self, plan_path: str):
        self.plan_path = Path(plan_path).resolve()
        self.validation_results: List[Dict] = []
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def validate_all(self) -> bool:
        """Run all validation checks."""
        checks = [
            ("Plan Path Exists", self.check_path_exists),
            ("V5 Folder Structure", self.check_v5_folders),
            ("V5 Master Plan", self.check_v5_master_plan),
            ("Phase Documents", self.check_phase_documents),
            ("Master Orch Integration", self.check_master_orch_docs),
            ("Continuation Prompt", self.check_continuation_prompt),
            ("V4 Files Preserved", self.check_v4_preserved),
        ]

        print(f"🔍 Validating V5 Plan: {self.plan_path.name}\n")
        print("="*60)

        all_passed = True
        for check_name, check_func in checks:
            passed, message = check_func()
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{status} | {check_name}")
            if message:
                print(f"        {message}")

            self.validation_results.append({
                "check": check_name,
                "passed": passed,
                "message": message
            })

            if not passed:
                all_passed = False
                self.errors.append(f"{check_name}: {message}")

        print("="*60)
        return all_passed

    def check_path_exists(self) -> Tuple[bool, str]:
        """Verify plan path exists and is a directory."""
        if not self.plan_path.exists():
            return False, f"Path does not exist: {self.plan_path}"
        if not self.plan_path.is_dir():
            return False, f"Path is not a directory: {self.plan_path}"
        return True, "Plan directory found"

    def check_v5_folders(self) -> Tuple[bool, str]:
        """Check for required V5 folders."""
        required_folders = [
            "context",
            "reports",
            "artifacts",
            "tracking",
            "architecture",  # V5
            "phases"  # V5
        ]

        missing = []
        for folder in required_folders:
            if not (self.plan_path / folder).exists():
                missing.append(folder)

        if missing:
            return False, f"Missing folders: {', '.join(missing)}"

        return True, "All 6 folders present (4 V4 + 2 V5)"

    def check_v5_master_plan(self) -> Tuple[bool, str]:
        """Verify V5 master plan exists and has required content."""
        v5_master = self.plan_path / "00-MASTER-PLAN-V5.md"

        if not v5_master.exists():
            return False, "00-MASTER-PLAN-V5.md not found"

        content = v5_master.read_text()

        # Check for required V5 sections
        required_sections = [
            "Visual Progress Tracker",
            "Executive Summary",
            "Phase -1: Knowledge Library",
            "Phase 0: Foundation",
            "Master Orchestrator Integration",
            "Final Phase: REFACTOR",
            "copilot_instructions"
        ]

        missing_sections = []
        for section in required_sections:
            if section not in content:
                missing_sections.append(section)

        if missing_sections:
            return False, f"Missing sections: {', '.join(missing_sections)}"

        return True, "V5 master plan complete with all sections"

    def check_phase_documents(self) -> Tuple[bool, str]:
        """Check for required phase documents."""
        required_phases = [
            "phase-minus-1-knowledge-library.md",
            "phase-0-foundation.md",
            "phase-final-refactor.md"
        ]

        phases_dir = self.plan_path / "phases"
        missing = []

        for phase_file in required_phases:
            if not (phases_dir / phase_file).exists():
                missing.append(phase_file)

        if missing:
            return False, f"Missing phase docs: {', '.join(missing)}"

        return True, "All 3 V5 phase documents present"

    def check_master_orch_docs(self) -> Tuple[bool, str]:
        """Check Master Orchestrator integration documentation."""
        arch_dir = self.plan_path / "architecture"
        integration_doc = arch_dir / "master-orchestrator-integration.md"

        if not integration_doc.exists():
            return False, "master-orchestrator-integration.md not found"

        content = integration_doc.read_text()

        # Check for key integration topics
        required_topics = [
            "Routing Configuration",
            "State Management",
            "Cross-Session Context",
            "Execution Engine"
        ]

        missing_topics = []
        for topic in required_topics:
            if topic not in content:
                missing_topics.append(topic)

        if missing_topics:
            self.warnings.append(f"Integration doc missing topics: {', '.join(missing_topics)}")

        return True, "Master Orch integration doc present"

    def check_continuation_prompt(self) -> Tuple[bool, str]:
        """Check for continuation prompt."""
        prompt = self.plan_path / "CONTINUATION-PROMPT.md"

        if not prompt.exists():
            return False, "CONTINUATION-PROMPT.md not found"

        return True, "Continuation prompt present"

    def check_v4_preserved(self) -> Tuple[bool, str]:
        """Verify V4 files were preserved."""
        v4_master = self.plan_path / "00-master-plan.md"

        if not v4_master.exists():
            self.warnings.append("Original 00-master-plan.md not found (may have been renamed)")

        return True, "V4 preservation check complete"

    def print_summary(self, all_passed: bool):
        """Print validation summary."""
        print(f"\n📊 Validation Summary")
        print("="*60)

        passed_count = sum(1 for r in self.validation_results if r["passed"])
        total_count = len(self.validation_results)

        print(f"Passed: {passed_count}/{total_count}")

        if self.errors:
            print(f"\n❌ Errors ({len(self.errors)}):")
            for error in self.errors:
                print(f"   - {error}")

        if self.warnings:
            print(f"\n⚠️  Warnings ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"   - {warning}")

        if all_passed:
            print("\n✅ Plan is V5 compliant!")
            print(f"\n🚀 Ready to execute:")
            print(f"   Say: 'start Phase -1 for {self.plan_path.name}' in CORTEX Chat")
        else:
            print("\n❌ Plan is NOT V5 compliant")
            print("   Run migration: python scripts/migrate_plan_to_v5.py --plan", self.plan_path)

        print("="*60)


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Validate CORTEX V5 plan structure and compliance"
    )

    parser.add_argument(
        "--plan",
        required=True,
        help="Path to V5 plan folder"
    )

    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON"
    )

    args = parser.parse_args()

    validator = V5PlanValidator(args.plan)
    all_passed = validator.validate_all()

    if args.json:
        result = {
            "plan": str(validator.plan_path),
            "valid": all_passed,
            "checks": validator.validation_results,
            "errors": validator.errors,
            "warnings": validator.warnings
        }
        print(json.dumps(result, indent=2))
    else:
        validator.print_summary(all_passed)

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
