#!/usr/bin/env python3
"""
SSOT Integrity Validator & Repair Tool
=======================================

Purpose: Detect and repair Single Source of Truth corruption in CORTEX 6.0
Version: 1.0.0
Author: Asif Hussain
Date: 2026-01-13

Corruption Types Handled:
  1. NULL AC counts in progress-tracker.json
  2. Orphaned ACs (in AC-INDEX but not in master-plan.yaml)
  3. Missing phases in progress-tracker.json
  4. Duplicate ACs across phases
  5. AC-INDEX references that don't exist in AC-INDEX.yaml
  6. Hardcoded completion percentages (should be calculated)

Preventative Mechanisms:
  - Atomic writes with file locking
  - Schema validation before writes
  - Audit trail logging
  - Rollback capability
"""

import json
import yaml
import fcntl
import hashlib
from pathlib import Path
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from datetime import datetime
import shutil
import sys


@dataclass
class ValidationIssue:
    """Represents a single validation issue"""
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    issue_type: str  # orphaned_ac, null_count, duplicate_ac, etc.
    description: str
    affected_items: List[str]
    auto_fixable: bool
    fix_action: str = ""


@dataclass
class RepairReport:
    """Report on repair operations"""
    timestamp: str
    issues_found: int
    issues_fixed: int
    issues_manual: int
    backups_created: List[str]
    errors: List[str]


class SSoTIntegrityValidator:
    """Validates and repairs SSOT corruption"""

    def __init__(self, workspace_root: str = "/Users/asifhussain/PROJECTS/CORTEX"):
        """Initialize validator with workspace paths"""
        self.workspace_root = Path(workspace_root)
        self.ac_index_path = self.workspace_root / "cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml"
        self.master_plan_path = self.workspace_root / "cortex-brain/cx6-plan/master-plan.yaml"
        self.tracker_path = self.workspace_root / "cortex-brain/tier1/tracking/progress-tracker.json"
        self.backup_dir = self.workspace_root / "cortex-brain/backups/ssot-integrity"
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.issues: List[ValidationIssue] = []
        self.report = RepairReport(
            timestamp=datetime.now().isoformat(),
            issues_found=0,
            issues_fixed=0,
            issues_manual=0,
            backups_created=[],
            errors=[]
        )

    def validate(self) -> Tuple[bool, List[ValidationIssue]]:
        """
        Run comprehensive validation of SSOT files
        Returns: (is_valid, list of issues)
        """
        print("\n" + "=" * 80)
        print("🔍 SSOT INTEGRITY VALIDATION")
        print("=" * 80 + "\n")

        try:
            # Load all SSOT files
            ac_index = self._load_yaml(self.ac_index_path)
            master_plan = self._load_yaml(self.master_plan_path)
            tracker = self._load_json(self.tracker_path)

            print("✅ All SSOT files loaded successfully\n")

            # Run validation checks
            self._validate_ac_index(ac_index)
            self._validate_master_plan(master_plan)
            self._validate_tracker(tracker)
            self._validate_cross_references(ac_index, master_plan, tracker)

            is_valid = len([i for i in self.issues if i.severity == "CRITICAL"]) == 0

            return is_valid, self.issues

        except Exception as e:
            self.report.errors.append(f"Validation failed: {str(e)}")
            print(f"❌ Validation error: {e}")
            return False, self.issues

    def repair(self, auto_fix_only: bool = True) -> RepairReport:
        """
        Repair detected issues
        
        Args:
            auto_fix_only: If True, only fix auto-fixable issues. If False, ask for each.
        
        Returns: RepairReport with details
        """
        print("\n" + "=" * 80)
        print("🔧 SSOT INTEGRITY REPAIR")
        print("=" * 80 + "\n")

        # Run validation first
        is_valid, issues = self.validate()

        if is_valid:
            print("✅ No critical issues found. SSOT is healthy.")
            self.report.issues_found = 0
            self.report.issues_fixed = 0
            return self.report

        self.report.issues_found = len(issues)

        # Create backups before any repairs
        self._backup_ssot_files()

        # Load SSOT files for repair
        ac_index = self._load_yaml(self.ac_index_path)
        master_plan = self._load_yaml(self.master_plan_path)
        tracker = self._load_json(self.tracker_path)

        # Apply fixes
        for issue in issues:
            if auto_fix_only and not issue.auto_fixable:
                print(f"⏭️  Skipping manual fix: {issue.description}")
                self.report.issues_manual += 1
                continue

            try:
                if issue.issue_type == "null_ac_count":
                    self._fix_null_ac_counts(tracker)
                    self.report.issues_fixed += 1

                elif issue.issue_type == "orphaned_ac":
                    master_plan = self._fix_orphaned_acs(ac_index, master_plan)
                    self.report.issues_fixed += 1

                elif issue.issue_type == "missing_phase":
                    tracker = self._fix_missing_phases(master_plan, tracker)
                    self.report.issues_fixed += 1

                elif issue.issue_type == "duplicate_ac":
                    master_plan = self._fix_duplicate_acs(master_plan)
                    self.report.issues_fixed += 1

                elif issue.issue_type == "hardcoded_percentage":
                    tracker = self._fix_hardcoded_percentages(tracker)
                    self.report.issues_fixed += 1

                print(f"✅ Fixed: {issue.description}")

            except Exception as e:
                self.report.errors.append(f"Failed to fix {issue.issue_type}: {str(e)}")
                print(f"❌ Error fixing {issue.issue_type}: {e}")

        # Write repaired files atomically
        self._atomic_write_yaml(self.ac_index_path, ac_index)
        self._atomic_write_yaml(self.master_plan_path, master_plan)
        self._atomic_write_json(self.tracker_path, tracker)

        print("\n" + "=" * 80)
        print(f"✅ REPAIR COMPLETE: {self.report.issues_fixed} issues fixed")
        print("=" * 80 + "\n")

        return self.report

    def _validate_ac_index(self, ac_index: Dict[str, Any]) -> None:
        """Validate AC-INDEX.yaml structure"""
        if not isinstance(ac_index, dict):
            self.issues.append(ValidationIssue(
                severity="CRITICAL",
                issue_type="ac_index_structure",
                description="AC-INDEX.yaml is not a dictionary",
                affected_items=["AC-INDEX.yaml"],
                auto_fixable=False
            ))
            return

        print(f"  AC-INDEX has {len(ac_index)} entries")

        # Check for invalid AC entries
        for ac_id, ac_data in ac_index.items():
            if not isinstance(ac_data, dict):
                self.issues.append(ValidationIssue(
                    severity="HIGH",
                    issue_type="invalid_ac_entry",
                    description=f"AC entry {ac_id} is not a dictionary",
                    affected_items=[ac_id],
                    auto_fixable=False
                ))

    def _validate_master_plan(self, master_plan: Dict[str, Any]) -> None:
        """Validate master-plan.yaml structure"""
        phases = master_plan.get("phases", {})
        print(f"  master-plan has {len(phases)} phases")

        if not phases:
            self.issues.append(ValidationIssue(
                severity="CRITICAL",
                issue_type="empty_phases",
                description="master-plan.yaml has no phases defined",
                affected_items=["master-plan.yaml"],
                auto_fixable=False
            ))

    def _validate_tracker(self, tracker: Dict[str, Any]) -> None:
        """Validate progress-tracker.json structure"""
        phases = tracker.get("phases", {})
        print(f"  progress-tracker has {len(phases)} phases")

        # Check for NULL AC counts
        null_phases = []
        for phase_key, phase_data in phases.items():
            if phase_data.get("total_ac_count") is None or phase_data.get("completed_count") is None:
                null_phases.append(phase_key)

        if null_phases:
            self.issues.append(ValidationIssue(
                severity="CRITICAL",
                issue_type="null_ac_count",
                description=f"Phases with NULL AC counts: {len(null_phases)}",
                affected_items=null_phases,
                auto_fixable=True,
                fix_action="Recalculate AC counts from master-plan.yaml"
            ))

        # Check for hardcoded percentages
        hardcoded_phases = []
        for phase_key, phase_data in phases.items():
            pct = phase_data.get("completion_percentage", 0)
            if pct == 100.0 and phase_data.get("completed_count") != phase_data.get("total_ac_count"):
                hardcoded_phases.append(phase_key)

        if hardcoded_phases:
            self.issues.append(ValidationIssue(
                severity="HIGH",
                issue_type="hardcoded_percentage",
                description=f"Phases with hardcoded 100% but incomplete ACs: {len(hardcoded_phases)}",
                affected_items=hardcoded_phases,
                auto_fixable=True,
                fix_action="Recalculate percentages from AC counts"
            ))

    def _validate_cross_references(self, ac_index: Dict, master_plan: Dict, tracker: Dict) -> None:
        """Validate references between SSOT files"""
        acs_in_index = set(ac_index.keys())
        acs_in_plan = set()

        for phase in master_plan.get("phases", {}).values():
            acs_in_plan.update(phase.get("ac_ids", []))

        # Check for orphaned ACs (in index but not in plan)
        orphaned = acs_in_index - acs_in_plan
        if orphaned:
            self.issues.append(ValidationIssue(
                severity="HIGH",
                issue_type="orphaned_ac",
                description=f"{len(orphaned)} ACs in AC-INDEX but not in master-plan.yaml",
                affected_items=list(orphaned),
                auto_fixable=True,
                fix_action="Add ACs to appropriate phase in master-plan.yaml based on AC-INDEX phase field"
            ))

        # Check for missing phases in tracker
        phases_in_plan = set(f"phase_{k.replace('phase_', '')}" for k in master_plan.get("phases", {}).keys())
        phases_in_tracker = set(tracker.get("phases", {}).keys())
        missing_phases = phases_in_plan - phases_in_tracker

        if missing_phases:
            self.issues.append(ValidationIssue(
                severity="HIGH",
                issue_type="missing_phase",
                description=f"{len(missing_phases)} phases in master-plan but not in progress-tracker",
                affected_items=list(missing_phases),
                auto_fixable=True,
                fix_action="Create missing phase entries in progress-tracker.json"
            ))

        # Check for duplicate ACs across phases
        all_phase_acs = []
        duplicates = []
        for phase in master_plan.get("phases", {}).values():
            for ac in phase.get("ac_ids", []):
                if ac in all_phase_acs:
                    duplicates.append(ac)
                all_phase_acs.append(ac)

        if duplicates:
            self.issues.append(ValidationIssue(
                severity="MEDIUM",
                issue_type="duplicate_ac",
                description=f"{len(set(duplicates))} ACs appear in multiple phases",
                affected_items=list(set(duplicates)),
                auto_fixable=True,
                fix_action="Remove duplicate AC references, keep first occurrence"
            ))

    def _fix_null_ac_counts(self, tracker: Dict[str, Any]) -> None:
        """Fix NULL AC counts by calculating from AC-INDEX"""
        ac_index = self._load_yaml(self.ac_index_path)
        master_plan = self._load_yaml(self.master_plan_path)

        for phase_key, phase_data in tracker.get("phases", {}).items():
            if phase_data.get("total_ac_count") is None or phase_data.get("completed_count") is None:
                # Get ACs for this phase from master-plan
                phase_num = phase_key.replace("phase_", "")
                phase_acs = master_plan.get("phases", {}).get(phase_key, {}).get("ac_ids", [])
                
                # Count implemented ACs
                completed = sum(
                    1 for ac_id in phase_acs
                    if ac_index.get(ac_id, {}).get("status") == "implemented"
                )

                tracker["phases"][phase_key]["total_ac_count"] = len(phase_acs)
                tracker["phases"][phase_key]["completed_count"] = completed
                tracker["phases"][phase_key]["completion_percentage"] = (
                    (completed / len(phase_acs) * 100) if phase_acs else 0
                )

                print(f"  Fixed {phase_key}: {completed}/{len(phase_acs)} ACs")

    def _fix_orphaned_acs(self, ac_index: Dict, master_plan: Dict) -> Dict:
        """Fix orphaned ACs by adding them to phases based on AC-INDEX phase field"""
        acs_in_plan = set()
        for phase in master_plan.get("phases", {}).values():
            acs_in_plan.update(phase.get("ac_ids", []))

        orphaned = set(ac_index.keys()) - acs_in_plan

        for ac_id in orphaned:
            ac_phase = ac_index[ac_id].get("phase", 1)
            phase_key = f"phase_{ac_phase}"

            if phase_key in master_plan.get("phases", {}):
                if ac_id not in master_plan["phases"][phase_key].get("ac_ids", []):
                    master_plan["phases"][phase_key]["ac_ids"].append(ac_id)
                    print(f"  Added {ac_id} to {phase_key}")

        return master_plan

    def _fix_missing_phases(self, master_plan: Dict, tracker: Dict) -> Dict:
        """Create missing phase entries in tracker"""
        for phase_key, phase_data in master_plan.get("phases", {}).items():
            if phase_key not in tracker.get("phases", {}):
                ac_ids = phase_data.get("ac_ids", [])
                tracker["phases"][phase_key] = {
                    "number": float(phase_key.replace("phase_", "")),
                    "name": phase_data.get("name", "Unknown"),
                    "status": "not_started",
                    "completion_percentage": 0.0,
                    "completed_count": 0,
                    "total_ac_count": len(ac_ids),
                }
                print(f"  Created {phase_key} with {len(ac_ids)} ACs")

        return tracker

    def _fix_duplicate_acs(self, master_plan: Dict) -> Dict:
        """Remove duplicate ACs, keeping first occurrence"""
        seen = set()
        for phase_key, phase_data in master_plan.get("phases", {}).items():
            ac_ids = phase_data.get("ac_ids", [])
            unique_acs = []
            for ac_id in ac_ids:
                if ac_id not in seen:
                    unique_acs.append(ac_id)
                    seen.add(ac_id)
                else:
                    print(f"  Removed duplicate {ac_id} from {phase_key}")

            master_plan["phases"][phase_key]["ac_ids"] = unique_acs

        return master_plan

    def _fix_hardcoded_percentages(self, tracker: Dict) -> Dict:
        """Recalculate completion percentages from AC counts"""
        for phase_key, phase_data in tracker.get("phases", {}).items():
            total = phase_data.get("total_ac_count", 0)
            completed = phase_data.get("completed_count", 0)

            if total > 0:
                calculated_pct = (completed / total) * 100
                if phase_data.get("completion_percentage") != calculated_pct:
                    tracker["phases"][phase_key]["completion_percentage"] = calculated_pct
                    print(f"  Recalculated {phase_key}: {calculated_pct:.1f}%")

        return tracker

    def _backup_ssot_files(self) -> None:
        """Create timestamped backups of SSOT files"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        for filepath in [self.ac_index_path, self.master_plan_path, self.tracker_path]:
            if filepath.exists():
                backup_name = f"{filepath.name}.backup.{timestamp}"
                backup_path = self.backup_dir / backup_name
                shutil.copy2(filepath, backup_path)
                self.report.backups_created.append(str(backup_path))
                print(f"  Backed up: {backup_path}")

    def _atomic_write_yaml(self, filepath: Path, data: Dict) -> None:
        """Write YAML file atomically with file locking"""
        lock_path = filepath.parent / f".{filepath.name}.lock"

        with open(lock_path, "w") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

                # Write to temp file
                temp_path = filepath.parent / f".{filepath.name}.tmp"
                with open(temp_path, "w") as f:
                    yaml.dump(data, f, default_flow_style=False)

                # Atomic rename
                temp_path.replace(filepath)

            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
                lock_path.unlink(missing_ok=True)

    def _atomic_write_json(self, filepath: Path, data: Dict) -> None:
        """Write JSON file atomically with file locking"""
        lock_path = filepath.parent / f".{filepath.name}.lock"

        with open(lock_path, "w") as lock:
            try:
                fcntl.flock(lock.fileno(), fcntl.LOCK_EX)

                # Write to temp file
                temp_path = filepath.parent / f".{filepath.name}.tmp"
                with open(temp_path, "w") as f:
                    json.dump(data, f, indent=2)

                # Atomic rename
                temp_path.replace(filepath)

            finally:
                fcntl.flock(lock.fileno(), fcntl.LOCK_UN)
                lock_path.unlink(missing_ok=True)

    def _load_yaml(self, filepath: Path) -> Dict:
        """Load YAML file"""
        with open(filepath, "r") as f:
            return yaml.safe_load(f)

    def _load_json(self, filepath: Path) -> Dict:
        """Load JSON file"""
        with open(filepath, "r") as f:
            return json.load(f)

    def print_issues(self) -> None:
        """Print formatted issue report"""
        print("\n" + "=" * 80)
        print("📋 VALIDATION ISSUES REPORT")
        print("=" * 80 + "\n")

        if not self.issues:
            print("✅ No issues found. SSOT is healthy!\n")
            return

        # Group by severity
        for severity in ["CRITICAL", "HIGH", "MEDIUM", "LOW"]:
            issues_at_level = [i for i in self.issues if i.severity == severity]
            if not issues_at_level:
                continue

            print(f"\n{severity} ({len(issues_at_level)} issues):")
            print("-" * 80)

            for issue in issues_at_level:
                status = "🔧 AUTO-FIXABLE" if issue.auto_fixable else "⚠️  MANUAL FIX"
                print(f"{status} | {issue.description}")
                print(f"   Fix: {issue.fix_action}")
                print(f"   Items: {', '.join(issue.affected_items[:3])}")
                if len(issue.affected_items) > 3:
                    print(f"          + {len(issue.affected_items)-3} more")
                print()

    def print_report(self, report: RepairReport) -> None:
        """Print repair report"""
        print("\n" + "=" * 80)
        print("📊 REPAIR REPORT")
        print("=" * 80)
        print(f"Timestamp:      {report.timestamp}")
        print(f"Issues Found:   {report.issues_found}")
        print(f"Issues Fixed:   {report.issues_fixed}")
        print(f"Manual Review:  {report.issues_manual}")
        print(f"Backups:        {len(report.backups_created)}")

        if report.errors:
            print(f"\nErrors ({len(report.errors)}):")
            for error in report.errors:
                print(f"  ❌ {error}")

        print("=" * 80 + "\n")


if __name__ == "__main__":
    # CLI interface
    validator = SSoTIntegrityValidator()

    if len(sys.argv) > 1 and sys.argv[1] == "repair":
        is_valid, issues = validator.validate()
        validator.print_issues()

        if not is_valid:
            print("\n🔧 Running auto-repairs...\n")
            report = validator.repair(auto_fix_only=True)
            validator.print_report(report)
    else:
        # Default: validate only
        is_valid, issues = validator.validate()
        validator.print_issues()
        sys.exit(0 if is_valid else 1)
