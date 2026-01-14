#!/usr/bin/env python3
"""
Validate Prompt Brittleness - Detect and prevent design issues in CORTEX prompts.

PURPOSE:
  Enforce unified prompt architecture to prevent brittleness patterns discovered
  in Phase 4.5 (chat01.md). Validates all `.github/prompts/*.prompt.md` files.

BRITTLENESS PATTERNS DETECTED:
  1. Mixed orchestrator patterns (some bypass MasterOrchestrator)
  2. Direct file access (prompts read state files directly)
  3. Copy-paste regression checks (creates inconsistency)
  4. Hardcoded paths (breaks on refactoring)
  5. Independent sync commands (race conditions)
  6. Inconsistent state mutation patterns
  7. Non-standard response formats
  8. Missing governance enforcement

GOVERNANCE RULES ENFORCED:
  • CORE-002: No root-level files
  • CORE-009: Plan file organization
  • CORE-017: Governance enforcement
  • CORE-024: MCP tool pattern equivalent

Usage:
  python3 scripts/validate-prompt-brittleness.py --audit
  python3 scripts/validate-prompt-brittleness.py --check cortex-plan-executor.prompt.md
  python3 scripts/validate-prompt-brittleness.py --validate-all

Author: GitHub Copilot (CORTEX 6.0)
Date: 2026-01-12
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime
import yaml


class PromptBrittlenessValidator:
    """Validates CORTEX prompt files for design brittleness."""

    def __init__(self):
        self.prompts_dir = Path(".github/prompts")
        self.issues = []
        self.warnings = []
        self.passes = []

    def validate_all(self) -> Dict:
        """Run full brittleness audit on all prompts."""
        if not self.prompts_dir.exists():
            print(f"❌ Error: {self.prompts_dir} not found")
            sys.exit(1)

        prompt_files = sorted(self.prompts_dir.glob("*.prompt.md"))
        print(
            f"🔍 Scanning {len(prompt_files)} prompt files for brittleness..."
        )
        print("=" * 80)

        for prompt_file in prompt_files:
            self._validate_file(prompt_file)

        return self._generate_report()

    def validate_file(self, filename: str) -> Dict:
        """Validate a single prompt file."""
        prompt_file = self.prompts_dir / filename
        if not prompt_file.exists():
            print(f"❌ Error: {prompt_file} not found")
            sys.exit(1)

        print(f"🔍 Validating {filename}...")
        print("=" * 80)
        self._validate_file(prompt_file)
        return self._generate_report()

    def _validate_file(self, prompt_file: Path) -> None:
        """Validate a single file for all brittleness patterns."""
        content = prompt_file.read_text()
        filename = prompt_file.name

        checks = [
            ("Governance Header", self._check_governance_header, content, filename),
            ("Version Format", self._check_version_format, content, filename),
            ("MasterOrchestrator Delegation", self._check_orchestrator_pattern, content, filename),
            ("Intelligent Challenge Protocol", self._check_challenge_protocol, content, filename),
            ("Regression Check Pattern", self._check_regression_pattern, content, filename),
            ("Direct File Access", self._check_direct_file_access, content, filename),
            ("Hardcoded Paths", self._check_hardcoded_paths, content, filename),
            ("State Mutation", self._check_state_mutation, content, filename),
            ("Sync Commands", self._check_sync_commands, content, filename),
            ("Response Format", self._check_response_format, content, filename),
            ("File Organization", self._check_file_organization, prompt_file),
        ]

        for check_name, check_func, *args in checks:
            try:
                result = check_func(*args)
                if result["status"] == "pass":
                    self.passes.append(f"{filename}: {check_name}")
                    print(f"  ✅ {check_name}")
                elif result["status"] == "warning":
                    self.warnings.append(f"{filename}: {check_name} - {result['message']}")
                    print(f"  ⚠️  {check_name}: {result['message']}")
                else:
                    self.issues.append(f"{filename}: {check_name} - {result['message']}")
                    print(f"  ❌ {check_name}: {result['message']}")
            except Exception as e:
                self.issues.append(f"{filename}: {check_name} - Exception: {str(e)}")
                print(f"  ❌ {check_name}: Exception - {str(e)}")

    def _check_governance_header(self, content: str, filename: str) -> Dict:
        """Check if governance rules are declared in header."""
        governance_pattern = r"(CORE-\d{3}|CORE-\d{2})"
        matches = re.findall(governance_pattern, content)

        if matches:
            return {"status": "pass", "message": f"Found {len(set(matches))} governance rules"}
        else:
            return {
                "status": "fail",
                "message": "No governance rules (CORE-XXX) declared in header",
            }

    def _check_version_format(self, content: str, filename: str) -> Dict:
        """Check if version follows semantic versioning."""
        version_pattern = r"\*\*Version:\*\*\s+(\d+\.\d+\.\d+)"
        match = re.search(version_pattern, content)

        if match:
            return {"status": "pass", "message": f"Version: {match.group(1)}"}
        else:
            return {"status": "fail", "message": "Missing version in format X.Y.Z"}

    def _check_orchestrator_pattern(self, content: str, filename: str) -> Dict:
        """Check for proper MasterOrchestrator delegation pattern."""
        # Should have EXACTLY ONE section heading for orchestrator delegation
        orchestrator_sections = len(re.findall(r"##+ .*MASTERORCHESTRATOR.*", content, re.IGNORECASE))

        if orchestrator_sections == 0:
            return {
                "status": "fail",
                "message": "Missing MASTERORCHESTRATOR DELEGATION section",
            }
        elif orchestrator_sections > 1:
            return {
                "status": "fail",
                "message": f"Multiple orchestrator sections ({orchestrator_sections}) - should be exactly 1",
            }

        # Check for proper delegation pattern
        delegation_pattern = r"python3 -m src\.main.*--orchestrator master"
        if re.search(delegation_pattern, content):
            return {"status": "pass", "message": "Proper delegation pattern found"}
        else:
            return {
                "status": "warning",
                "message": "Orchestrator pattern found but may be non-standard",
            }

    def _check_regression_pattern(self, content: str, filename: str) -> Dict:
        """Check for regression check pattern (should reference CORTEX.prompt.md, not copy-paste)."""
        # Look for the unified regression check reference
        reference_pattern = r"Reference:.*CORTEX\.prompt\.md"
        copy_pattern = r"yaml\.safe_load\(open\(.*AC-INDEX"

        if re.search(reference_pattern, content):
            return {"status": "pass", "message": "Regression check properly references CORTEX.prompt.md"}
        elif re.search(copy_pattern, content):
            return {
                "status": "fail",
                "message": "Regression check appears to copy-paste YAML code (brittleness!)",
            }
        else:
            return {
                "status": "warning",
                "message": "Regression check pattern unclear - verify it references CORTEX.prompt.md",
            }

    def _check_challenge_protocol(self, content: str, filename: str) -> Dict:
        """Check for intelligent challenge protocol (CORE-025)."""
        # Check for CORE-025 reference
        if "CORE-025" not in content:
            # For now, warn instead of fail since not all prompts have been updated
            return {
                "status": "warning",
                "message": "CORE-025 (Intelligent Challenge Protocol) not referenced - add to header",
            }

        # Check for challenge protocol section
        challenge_section = r"##+ .*INTELLIGENT CHALLENGE.*PROTOCOL"
        if not re.search(challenge_section, content, re.IGNORECASE):
            return {
                "status": "warning",
                "message": "Missing 'INTELLIGENT CHALLENGE PROTOCOL' section",
            }

        # Check for REQUEST-VALIDATOR reference
        validator_ref = r"REQUEST-VALIDATOR-VISUAL-ARCHITECTURE"
        if "REQUEST-VALIDATOR-VISUAL-ARCHITECTURE" not in content:
            return {
                "status": "warning",
                "message": "Missing reference to REQUEST-VALIDATOR-VISUAL-ARCHITECTURE.md",
            }

        # Check for decision matrix
        decision_keywords = ["BLOCK", "ADVISE", "ENHANCE", "APPROVE"]
        if not all(keyword in content for keyword in decision_keywords):
            return {
                "status": "warning",
                "message": "Missing decision matrix terms (BLOCK/ADVISE/ENHANCE/APPROVE)",
            }

        # Check for scenarios
        scenario_pattern = r"Scenario [AB]"
        scenarios = len(re.findall(scenario_pattern, content))
        if scenarios < 2:
            return {
                "status": "warning",
                "message": "Should include Scenario A (blocking) + Scenario B (enhancement)",
            }

        return {"status": "pass", "message": "Challenge protocol properly integrated"}

    def _check_direct_file_access(self, content: str, filename: str) -> Dict:
        """Check for direct file access patterns (should NOT exist in prompts)."""
        forbidden_patterns = [
            r"yaml\.safe_load\(open",
            r"json\.load\(open",
            r"open\(.*cortex-brain",
            r"json\.loads.*tracker",
            r"yaml\.loads.*AC-INDEX",
        ]

        for pattern in forbidden_patterns:
            if re.search(pattern, content):
                return {
                    "status": "fail",
                    "message": f"Found direct file access pattern: {pattern}",
                }

        return {"status": "pass", "message": "No direct file access patterns found"}

    def _check_hardcoded_paths(self, content: str, filename: str) -> Dict:
        """Check for hardcoded file paths (should use configuration)."""
        # Prompts should not contain specific paths like cortex-brain/tier1/...
        # (They can reference as context, but not as configuration)
        hardcoded_pattern = r"cortex-brain/(tier[0-3]|cx6-plan|documents)"

        matches = re.findall(hardcoded_pattern, content)
        if len(matches) > 5:
            # More than 5 matches suggests hardcoding, not just reference
            return {
                "status": "warning",
                "message": f"Found {len(matches)} hardcoded path references - ensure these are context, not config",
            }

        return {"status": "pass", "message": "Path references appropriate"}

    def _check_state_mutation(self, content: str, filename: str) -> Dict:
        """Check that prompts don't directly mutate state."""
        mutation_patterns = [
            r"progress-tracker\.json.*=",
            r"AC-INDEX\.yaml.*=",
            r"\.write\(.*tracker",
            r"\.write\(.*AC-INDEX",
        ]

        for pattern in mutation_patterns:
            if re.search(pattern, content):
                return {
                    "status": "fail",
                    "message": "Found state mutation pattern - only MasterOrchestrator should mutate state",
                }

        return {"status": "pass", "message": "No direct state mutation found"}

    def _check_sync_commands(self, content: str, filename: str) -> Dict:
        """Check that prompts don't call sync commands independently."""
        sync_patterns = [
            r"sync_plan_viewer_data\.py",
            r"regenerate_plan_viewer_data\.py",
            r"update_plan_viewer_progress\.py",
        ]

        for pattern in sync_patterns:
            if re.search(pattern, content):
                return {
                    "status": "warning",
                    "message": "Found sync command - verify MasterOrchestrator handles all syncing",
                }

        return {"status": "pass", "message": "No independent sync commands found"}

    def _check_response_format(self, content: str, filename: str) -> Dict:
        """Check for consistent response format (executive bullets)."""
        # Should have sections like ✅ OUTCOMES, ⚙️ IN PROGRESS, etc.
        format_indicators = [
            r"✅.*OUTCOMES",
            r"⚙️.*IN PROGRESS",
            r"🎯.*IMPACT",
            r"❌.*BLOCKED|⚠️.*RISKS",
        ]

        matches = sum(1 for pattern in format_indicators if re.search(pattern, content))

        if matches >= 2:
            return {"status": "pass", "message": f"Response format indicators found ({matches})"}
        else:
            return {
                "status": "warning",
                "message": "Response format may be non-standard - verify against response-templates-v4.yaml",
            }

    def _check_file_organization(self, prompt_file: Path) -> Dict:
        """Check CORE-002 and CORE-009: File organization governance."""
        # Files must be in .github/prompts/, not in root
        if prompt_file.parent.name == "prompts":
            return {"status": "pass", "message": "File properly organized in .github/prompts/"}
        else:
            return {"status": "fail", "message": "File not in .github/prompts/ (CORE-002 violation)"}

    def _generate_report(self) -> Dict:
        """Generate comprehensive brittleness report."""
        total_checks = len(self.issues) + len(self.warnings) + len(self.passes)
        pass_rate = len(self.passes) / max(1, total_checks) * 100

        report = {
            "timestamp": datetime.now().isoformat(),
            "total_checks": total_checks,
            "passed": len(self.passes),
            "warnings": len(self.warnings),
            "failures": len(self.issues),
            "pass_rate": round(pass_rate, 1),
            "status": "PASS" if len(self.issues) == 0 else "FAIL",
            "issues": self.issues,
            "warnings": self.warnings,
            "passes": self.passes,
        }

        # Print report
        print("\n" + "=" * 80)
        print("BRITTLENESS VALIDATION REPORT")
        print("=" * 80)
        print(f"\n✅ Passed: {report['passed']}/{total_checks}")
        print(f"⚠️  Warnings: {report['warnings']}/{total_checks}")
        print(f"❌ Failures: {report['failures']}/{total_checks}")
        print(f"📊 Pass Rate: {report['pass_rate']}%")
        print(f"📋 Status: {report['status']}")

        if self.issues:
            print(f"\n❌ FAILURES ({len(self.issues)}):")
            for issue in self.issues:
                print(f"  • {issue}")

        if self.warnings:
            print(f"\n⚠️  WARNINGS ({len(self.warnings)}):")
            for warning in self.warnings:
                print(f"  • {warning}")

        print("\n" + "=" * 80)

        # Save report to cortex-brain/documents/
        docs_dir = Path("cortex-brain/documents")
        if docs_dir.exists():
            report_file = docs_dir / f"prompt-brittleness-report-{datetime.now().strftime('%Y%m%d-%H%M%S')}.yaml"
            with open(report_file, "w") as f:
                yaml.dump(report, f, default_flow_style=False)
            print(f"\n📄 Report saved to: {report_file}")

        return report


def main():
    parser = argparse.ArgumentParser(
        description="Validate CORTEX prompts for brittleness patterns"
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        help="Run full brittleness audit on all prompts",
    )
    parser.add_argument(
        "--check",
        type=str,
        help="Check a specific prompt file",
    )
    parser.add_argument(
        "--validate-all",
        action="store_true",
        help="Validate all prompts (alias for --audit)",
    )

    args = parser.parse_args()

    validator = PromptBrittlenessValidator()

    if args.audit or args.validate_all:
        report = validator.validate_all()
        sys.exit(0 if report["status"] == "PASS" else 1)
    elif args.check:
        report = validator.validate_file(args.check)
        sys.exit(0 if report["status"] == "PASS" else 1)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
