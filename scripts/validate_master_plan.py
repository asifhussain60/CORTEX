#!/usr/bin/env python3
"""
Master Plan Validation Script

Validates plan documents against Master Orchestrator architecture, SKULL rules,
and Planning System v5 structure requirements.

Usage:
    python scripts/validate_master_plan.py --plan cortex-v5-holistic-refactor
    python scripts/validate_master_plan.py --plan cortex-v5-holistic-refactor --fix
    python scripts/validate_master_plan.py --all  # Validate all active plans

Author: Asif Hussain
Copyright © 2026 Asif Hussain. All rights reserved.
"""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import Enum


class ValidationSeverity(str, Enum):
    """Validation issue severity levels."""
    CRITICAL = "critical"  # Blocks execution
    ERROR = "error"        # Must fix before commit
    WARNING = "warning"    # Should fix
    INFO = "info"          # Nice to have


@dataclass
class ValidationIssue:
    """A single validation issue."""
    severity: ValidationSeverity
    rule_id: str
    message: str
    file_path: str
    line_number: Optional[int] = None
    suggested_fix: Optional[str] = None
    
    def __str__(self) -> str:
        """Format issue for display."""
        location = f"{self.file_path}"
        if self.line_number:
            location += f":{self.line_number}"
        
        severity_emoji = {
            ValidationSeverity.CRITICAL: "🔴",
            ValidationSeverity.ERROR: "🟠",
            ValidationSeverity.WARNING: "🟡",
            ValidationSeverity.INFO: "🔵"
        }
        
        result = f"{severity_emoji[self.severity]} [{self.severity.value.upper()}] {self.rule_id}\n"
        result += f"  Location: {location}\n"
        result += f"  Issue: {self.message}\n"
        if self.suggested_fix:
            result += f"  Fix: {self.suggested_fix}\n"
        return result


@dataclass
class ValidationResult:
    """Result of validation run."""
    plan_id: str
    plan_path: Path
    passed: bool
    issues: List[ValidationIssue] = field(default_factory=list)
    
    def add_issue(
        self,
        severity: ValidationSeverity,
        rule_id: str,
        message: str,
        line_number: Optional[int] = None,
        suggested_fix: Optional[str] = None
    ) -> None:
        """Add a validation issue."""
        self.issues.append(ValidationIssue(
            severity=severity,
            rule_id=rule_id,
            message=message,
            file_path=str(self.plan_path),
            line_number=line_number,
            suggested_fix=suggested_fix
        ))
        if severity in [ValidationSeverity.CRITICAL, ValidationSeverity.ERROR]:
            self.passed = False
    
    def summary(self) -> str:
        """Generate summary report."""
        critical = sum(1 for i in self.issues if i.severity == ValidationSeverity.CRITICAL)
        errors = sum(1 for i in self.issues if i.severity == ValidationSeverity.ERROR)
        warnings = sum(1 for i in self.issues if i.severity == ValidationSeverity.WARNING)
        info = sum(1 for i in self.issues if i.severity == ValidationSeverity.INFO)
        
        result = f"\n{'='*80}\n"
        result += f"VALIDATION SUMMARY: {self.plan_id}\n"
        result += f"{'='*80}\n\n"
        result += f"Plan: {self.plan_path}\n"
        result += f"Status: {'✅ PASSED' if self.passed else '❌ FAILED'}\n\n"
        result += f"Issues:\n"
        result += f"  🔴 Critical: {critical}\n"
        result += f"  🟠 Errors:   {errors}\n"
        result += f"  🟡 Warnings: {warnings}\n"
        result += f"  🔵 Info:     {info}\n"
        result += f"  Total:      {len(self.issues)}\n\n"
        
        if self.issues:
            result += f"{'='*80}\n"
            result += f"DETAILED ISSUES\n"
            result += f"{'='*80}\n\n"
            for issue in sorted(self.issues, key=lambda x: (x.severity.value, x.rule_id)):
                result += str(issue) + "\n"
        
        return result


class MasterPlanValidator:
    """
    Validates master plans against architectural rules.
    
    Validation Categories:
    1. Master Orchestrator Architecture Alignment
    2. SKULL Rule Compliance
    3. Planning System v5 Structure
    4. File Location Standards
    5. Mandatory Content Blocks
    """
    
    def __init__(self, workspace_root: Path):
        """
        Initialize validator.
        
        Args:
            workspace_root: Path to CORTEX workspace root
        """
        self.workspace_root = workspace_root
        self.planning_root = workspace_root / "cortex-brain" / "documents" / "planning" / "active"
    
    def validate_plan(self, plan_id: str) -> ValidationResult:
        """
        Validate a single plan.
        
        Args:
            plan_id: Plan ID (folder name)
        
        Returns:
            ValidationResult with all issues
        """
        plan_dir = self.planning_root / plan_id
        
        # Try different filename variations
        master_plan_variations = [
            "00-MASTER-PLAN-V5.md",
            "00-master-plan.md",
            "00-MASTER-PLAN.md",
            "master-plan.md"
        ]
        
        master_plan = None
        for filename in master_plan_variations:
            candidate = plan_dir / filename
            if candidate.exists():
                master_plan = candidate
                break
        
        if not master_plan:
            result = ValidationResult(plan_id, plan_dir / "00-master-plan.md", passed=False)
            result.add_issue(
                ValidationSeverity.CRITICAL,
                "MISSING_MASTER_PLAN",
                f"Master plan file not found in {plan_dir}. Tried: {', '.join(master_plan_variations)}",
                suggested_fix="Create master plan file (00-master-plan.md or 00-MASTER-PLAN-V5.md)"
            )
            return result
        
        result = ValidationResult(plan_id, master_plan, passed=True)
        
        # Read plan content
        content = master_plan.read_text(encoding='utf-8')
        lines = content.split('\n')
        
        # Run all validation checks
        self._validate_master_orchestrator_alignment(result, content, lines)
        self._validate_skull_compliance(result, content, lines)
        self._validate_folder_structure(result, plan_dir)
        self._validate_file_locations(result, plan_dir)
        self._validate_mandatory_content(result, content, lines)
        self._validate_response_template(result, content, lines)
        self._validate_phase_structure(result, content, lines)
        
        return result
    
    def _validate_master_orchestrator_alignment(
        self,
        result: ValidationResult,
        content: str,
        lines: List[str]
    ) -> None:
        """Validate Master Orchestrator architecture alignment."""
        
        # Check 1: Master Orchestrator mentioned in executive summary
        if "Master Orchestrator" not in content[:3000]:  # First 3000 chars
            result.add_issue(
                ValidationSeverity.ERROR,
                "MO_MISSING_EXECUTIVE_SUMMARY",
                "Master Orchestrator not mentioned in executive summary",
                suggested_fix="Add Master Orchestrator description in executive summary"
            )
        
        # Check 2: Pattern-based routing mentioned
        if "pattern" not in content.lower() and "routing" not in content.lower():
            result.add_issue(
                ValidationSeverity.WARNING,
                "MO_MISSING_ROUTING_DESCRIPTION",
                "Pattern-based routing not documented",
                suggested_fix="Document Master Orchestrator routing architecture"
            )
        
        # Check 3: FileLocationValidator integration mentioned (Task 10.2)
        if "FileLocationValidator" not in content:
            result.add_issue(
                ValidationSeverity.ERROR,
                "MO_MISSING_FILE_VALIDATOR",
                "FileLocationValidator integration not in plan (should be in Phase 10)",
                suggested_fix="Add Task 10.2: File Location Enforcement System"
            )
        
        # Check 4: write_artifact() API mentioned
        if "write_artifact(" not in content:
            result.add_issue(
                ValidationSeverity.WARNING,
                "MO_MISSING_WRITE_ARTIFACT_API",
                "BaseOrchestrator write_artifact() API not documented",
                suggested_fix="Document write_artifact() API in Phase 10.2"
            )
    
    def _validate_skull_compliance(
        self,
        result: ValidationResult,
        content: str,
        lines: List[str]
    ) -> None:
        """Validate SKULL rule compliance."""
        
        # Check 1: Phase -1 (Knowledge Library) exists
        has_phase_minus_one = False
        for i, line in enumerate(lines):
            if re.search(r'Phase -1:|Phase -1 ', line):
                has_phase_minus_one = True
                break
        
        if not has_phase_minus_one:
            result.add_issue(
                ValidationSeverity.CRITICAL,
                "SKULL_MISSING_PHASE_MINUS_ONE",
                "Phase -1 (Knowledge Library Consultation) missing - SKULL rule violation",
                suggested_fix="Insert Phase -1 before Phase 0 with knowledge graph queries"
            )
        
        # Check 2: Phase 10 (REFACTOR) has ≥18 tasks
        phase_10_match = re.search(r'## .*Phase 10:.*REFACTOR', content, re.IGNORECASE)
        if phase_10_match:
            phase_10_start = content.find(phase_10_match.group())
            phase_11_match = re.search(r'## .*Phase 11:', content[phase_10_start:])
            phase_10_end = phase_10_start + phase_11_match.start() if phase_11_match else len(content)
            phase_10_content = content[phase_10_start:phase_10_end]
            
            # Count Task 10.X patterns
            task_count = len(re.findall(r'### Task 10\.\d+:', phase_10_content))
            if task_count < 5:  # Should have at least 5 major tasks
                result.add_issue(
                    ValidationSeverity.WARNING,
                    "SKULL_REFACTOR_UNDERSPECIFIED",
                    f"Phase 10 has only {task_count} tasks - SKULL requires comprehensive cleanup",
                    suggested_fix="Expand Phase 10 with tasks for orphans, duplicates, imports, etc."
                )
        else:
            result.add_issue(
                ValidationSeverity.ERROR,
                "SKULL_MISSING_REFACTOR_PHASE",
                "Phase 10 (REFACTOR) not found - SKULL rule violation",
                suggested_fix="Add Phase 10 with comprehensive code cleanup tasks"
            )
        
        # Check 3: TDD enforcement mentioned
        if "RED→GREEN→REFACTOR" not in content and "RED->GREEN->REFACTOR" not in content:
            result.add_issue(
                ValidationSeverity.WARNING,
                "SKULL_MISSING_TDD_ENFORCEMENT",
                "TDD cycle (RED→GREEN→REFACTOR) not documented",
                suggested_fix="Add TDD enforcement to copilot_instructions block"
            )
        
        # Check 4: Git checkpoint references
        checkpoint_count = len(re.findall(r'checkpoint-', content))
        if checkpoint_count < 5:  # Should have checkpoint per phase
            result.add_issue(
                ValidationSeverity.INFO,
                "SKULL_FEW_CHECKPOINTS",
                f"Only {checkpoint_count} git checkpoints found - recommend one per phase",
                suggested_fix="Add checkpoint references to phase completion criteria"
            )
    
    def _validate_folder_structure(
        self,
        result: ValidationResult,
        plan_dir: Path
    ) -> None:
        """Validate plan folder structure matches Planning System v5 spec."""
        
        required_folders = ["tracking", "context", "reports", "artifacts"]
        
        for folder in required_folders:
            folder_path = plan_dir / folder
            if not folder_path.exists():
                result.add_issue(
                    ValidationSeverity.ERROR,
                    "PS5_MISSING_SUBFOLDER",
                    f"Required subfolder missing: {folder}/",
                    suggested_fix=f"Create {folder}/ subfolder in plan directory"
                )
    
    def _validate_file_locations(
        self,
        result: ValidationResult,
        plan_dir: Path
    ) -> None:
        """Validate files are in correct subfolders."""
        
        # Check for root-level files (except allowed ones)
        allowed_at_root = [
            "00-master-plan.md",
            "00-MASTER-PLAN.md",
            "00-MASTER-PLAN-V5.md",  # Version-specific naming
            "00-MASTER-PLAN-V4.md",
            "README.md",
            "MASTER-ORCHESTRATOR-INSTRUCTIONS.md",
            "MASTER-ORCHESTRATOR-INTEGRATION-SUMMARY.md"  # Integration docs
        ]
        
        for file_path in plan_dir.glob("*.md"):
            if file_path.name not in allowed_at_root:
                result.add_issue(
                    ValidationSeverity.ERROR,
                    "FILE_LOCATION_VIOLATION",
                    f"File in plan root should be in subfolder: {file_path.name}",
                    suggested_fix=f"Move to appropriate subfolder (tracking/, context/, reports/, artifacts/)"
                )
        
        # Check continuation prompt location
        tracking_dir = plan_dir / "tracking"
        if tracking_dir.exists():
            continuation_prompt = tracking_dir / "CONTINUATION-PROMPT.md"
            if not continuation_prompt.exists():
                result.add_issue(
                    ValidationSeverity.WARNING,
                    "MISSING_CONTINUATION_PROMPT",
                    "CONTINUATION-PROMPT.md not found in tracking/",
                    suggested_fix="Generate continuation prompt in tracking/ folder"
                )
    
    def _validate_mandatory_content(
        self,
        result: ValidationResult,
        content: str,
        lines: List[str]
    ) -> None:
        """Validate mandatory content blocks exist."""
        
        # Check 1: Response Template Reference block
        if "Response Template Reference" not in content:
            result.add_issue(
                ValidationSeverity.CRITICAL,
                "MISSING_RESPONSE_TEMPLATE_REF",
                "Response Template Reference block missing",
                suggested_fix="Add '## 🎯 Response Template Reference' block after executive summary"
            )
        
        # Check 2: Copilot Instructions block
        if "copilot_instructions:" not in content:
            result.add_issue(
                ValidationSeverity.CRITICAL,
                "MISSING_COPILOT_INSTRUCTIONS",
                "Copilot Instructions YAML block missing",
                suggested_fix="Add '## 🤖 Copilot Instructions' block with SKULL rules"
            )
        
        # Check 3: Visual Progress Tracker
        if "Visual Progress Tracker" not in content:
            result.add_issue(
                ValidationSeverity.ERROR,
                "MISSING_PROGRESS_TRACKER",
                "Visual Progress Tracker not found",
                suggested_fix="Add '## 📊 Visual Progress Tracker' with phase progress bars"
            )
    
    def _validate_response_template(
        self,
        result: ValidationResult,
        content: str,
        lines: List[str]
    ) -> None:
        """Validate response template references."""
        
        # Check autonomous_execution_progress template reference
        if "autonomous_execution_progress" not in content:
            result.add_issue(
                ValidationSeverity.WARNING,
                "MISSING_TEMPLATE_REFERENCE",
                "autonomous_execution_progress template not referenced",
                suggested_fix="Add template reference in Response Template Reference block"
            )
        
        # Check for 🛡️ shield emoji (indicates AUTONOMOUS orchestrator)
        if "🛡️" not in content:
            result.add_issue(
                ValidationSeverity.INFO,
                "MISSING_AUTONOMOUS_MARKER",
                "🛡️ shield emoji not found - should indicate AUTONOMOUS orchestrator type",
                suggested_fix="Add '**Orchestrator Type:** 🛡️ AUTONOMOUS' in header"
            )
    
    def _validate_phase_structure(
        self,
        result: ValidationResult,
        content: str,
        lines: List[str]
    ) -> None:
        """Validate phase structure and numbering."""
        
        # Extract all phase headers
        phase_pattern = re.compile(r'##\s+.*Phase\s+(-?\d+\.?\d*):', re.IGNORECASE)
        phases = []
        for i, line in enumerate(lines):
            match = phase_pattern.search(line)
            if match:
                phase_num = match.group(1)
                phases.append((phase_num, i + 1, line.strip()))
        
        if not phases:
            result.add_issue(
                ValidationSeverity.CRITICAL,
                "NO_PHASES_FOUND",
                "No phase headers found in plan",
                suggested_fix="Add phase structure with ## Phase N: headers"
            )
            return
        
        # Validate phase sequence (allowing sub-phases like 4.5, 6.5)
        expected_phase = -1 if phases[0][0] == "-1" else 0
        for phase_num_str, line_num, header in phases:
            try:
                num = float(phase_num_str)
                
                # Allow sub-phases (e.g., 4.5 between 4 and 5)
                if num < expected_phase:
                    result.add_issue(
                        ValidationSeverity.WARNING,
                        "PHASE_OUT_OF_ORDER",
                        f"Phase out of order at line {line_num}: expected >={expected_phase}, found {num}",
                        line_number=line_num
                    )
                
                # Update expected (integer part + 1)
                if num.is_integer():
                    expected_phase = int(num) + 1
                
            except ValueError:
                result.add_issue(
                    ValidationSeverity.ERROR,
                    "INVALID_PHASE_NUMBER",
                    f"Invalid phase number at line {line_num}: {phase_num_str}",
                    line_number=line_num
                )


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Validate master plans against Master Orchestrator architecture and SKULL rules"
    )
    parser.add_argument(
        "--plan",
        help="Plan ID to validate (e.g., cortex-v5-holistic-refactor)"
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Validate all active plans"
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Attempt to auto-fix issues (where possible)"
    )
    parser.add_argument(
        "--severity",
        choices=["critical", "error", "warning", "info"],
        default="error",
        help="Minimum severity to report (default: error)"
    )
    
    args = parser.parse_args()
    
    # Determine workspace root
    workspace_root = Path(__file__).parent.parent
    if not (workspace_root / "cortex-brain").exists():
        print("❌ Error: Not in CORTEX workspace root", file=sys.stderr)
        sys.exit(1)
    
    validator = MasterPlanValidator(workspace_root)
    
    # Determine which plans to validate
    if args.all:
        plan_dirs = [p for p in validator.planning_root.iterdir() if p.is_dir()]
        plan_ids = [p.name for p in plan_dirs]
    elif args.plan:
        plan_ids = [args.plan]
    else:
        print("❌ Error: Must specify --plan or --all", file=sys.stderr)
        parser.print_help()
        sys.exit(1)
    
    # Validate plans
    results = []
    for plan_id in plan_ids:
        print(f"\n🔍 Validating plan: {plan_id}")
        result = validator.validate_plan(plan_id)
        results.append(result)
        
        # Filter by severity
        severity_threshold = ValidationSeverity(args.severity)
        severity_order = [
            ValidationSeverity.CRITICAL,
            ValidationSeverity.ERROR,
            ValidationSeverity.WARNING,
            ValidationSeverity.INFO
        ]
        threshold_index = severity_order.index(severity_threshold)
        filtered_issues = [
            issue for issue in result.issues
            if severity_order.index(issue.severity) <= threshold_index
        ]
        result.issues = filtered_issues
        
        print(result.summary())
    
    # Overall summary
    total_plans = len(results)
    passed_plans = sum(1 for r in results if r.passed)
    failed_plans = total_plans - passed_plans
    
    print(f"\n{'='*80}")
    print(f"OVERALL SUMMARY")
    print(f"{'='*80}\n")
    print(f"Plans validated: {total_plans}")
    print(f"Passed: {passed_plans} ✅")
    print(f"Failed: {failed_plans} ❌")
    
    # Exit code
    sys.exit(0 if failed_plans == 0 else 1)


if __name__ == "__main__":
    main()
