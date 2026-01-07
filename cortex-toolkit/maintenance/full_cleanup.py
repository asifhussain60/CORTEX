#!/usr/bin/env python3
"""
CORTEX Full Cleanup - Comprehensive 5-phase cleanup orchestrator

Orchestrates all cleanup phases in sequence:
1. Cache Clear - VS Code and Python caches
2. Template Validation - Response templates and progress bars
3. Autonomous Verification - Default execution modes
4. Legacy Removal - Deprecated 5-part references
5. Duplicate Resolution - Conflicting files

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import os
import sys
import time
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any
import argparse

# Add toolkit to path
toolkit_root = Path(__file__).parent.parent
sys.path.insert(0, str(toolkit_root))

from maintenance.clear_caches import clear_caches
from maintenance.validate_templates import validate_templates, fix_autonomous_defaults
from maintenance.remove_legacy_refs import remove_legacy_references, check_5part_file
from maintenance.detect_duplicates import scan_for_duplicates, resolve_duplicates


class CleanupPhase:
    """Represents a cleanup phase with progress tracking."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.status = "not_started"  # not_started, in_progress, completed, failed
        self.issues_found = 0
        self.issues_fixed = 0
        self.start_time = None
        self.end_time = None
        self.errors = []
    
    @property
    def duration(self) -> float:
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0
    
    def start(self):
        self.status = "in_progress"
        self.start_time = time.time()
    
    def complete(self, issues_found: int = 0, issues_fixed: int = 0):
        self.status = "completed"
        self.end_time = time.time()
        self.issues_found = issues_found
        self.issues_fixed = issues_fixed
    
    def fail(self, error: str):
        self.status = "failed"
        self.end_time = time.time()
        self.errors.append(error)


def generate_progress_bar(percentage: float, width: int = 20) -> str:
    """Generate Unicode progress bar."""
    filled = int(width * percentage / 100)
    empty = width - filled
    return f"{'█' * filled}{'░' * empty}"


def print_progress_header(phases: List[CleanupPhase], current_idx: int, workspace: Path):
    """Print visual progress header."""
    completed = sum(1 for p in phases if p.status == "completed")
    total = len(phases)
    percentage = (completed / total) * 100
    
    current_phase = phases[current_idx] if current_idx < len(phases) else phases[-1]
    
    elapsed = sum(p.duration for p in phases if p.end_time)
    
    print(f"""
╔══════════════════════════════════════════════════════════════════════════╗
║  Operation: CORTEX Full Cleanup                                          ║
╠══════════════════════════════════════════════════════════════════════════╣
║  Overall: [{generate_progress_bar(percentage)}] {percentage:.0f}%  {'⏳' if percentage < 100 else '✅'}                                  ║
║  Phase {current_idx + 1}/{total}: {current_phase.name:<50} ║
║  Issues: {sum(p.issues_found for p in phases)} found | {sum(p.issues_fixed for p in phases)} fixed{' ' * 40}║
║  Time: {elapsed:.1f}s elapsed{' ' * 50}║
╚══════════════════════════════════════════════════════════════════════════╝
""")


def print_phase_table(phases: List[CleanupPhase]):
    """Print phase progress table."""
    print("\n### 📋 Cleanup Phases\n")
    print("| # | Phase | Status | Progress | Issues | Time |")
    print("|---|-------|--------|----------|--------|------|")
    
    for i, phase in enumerate(phases, 1):
        status_emoji = {
            "not_started": "⏸️",
            "in_progress": "⏳",
            "completed": "✅",
            "failed": "❌"
        }.get(phase.status, "❓")
        
        if phase.status == "completed":
            progress = "[██████████] 100%"
        elif phase.status == "in_progress":
            progress = "[█████░░░░░] 50%"
        else:
            progress = "[░░░░░░░░░░] 0%"
        
        issues = f"{phase.issues_fixed}/{phase.issues_found}" if phase.issues_found else "-"
        time_str = f"{phase.duration:.1f}s" if phase.duration else "-"
        
        print(f"| {i} | {status_emoji} **{phase.name}** | {phase.status} | {progress} | {issues} | {time_str} |")


def run_full_cleanup(
    workspace: Path,
    dry_run: bool = True,
    max_iterations: int = 5,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Run complete 5-phase cleanup.
    
    Returns:
        Dict with results summary
    """
    print(f"\n{'=' * 70}")
    print("🧹 CORTEX FULL CLEANUP - 5-Phase Orchestrator")
    print(f"{'=' * 70}")
    print(f"\n📂 Workspace: {workspace}")
    print(f"🔍 Mode: {'DRY RUN' if dry_run else 'EXECUTE'}")
    print(f"🔄 Max iterations: {max_iterations}")
    
    # Initialize phases
    phases = [
        CleanupPhase("Cache Clear", "VS Code and Python caches"),
        CleanupPhase("Template Validation", "Response templates and progress bars"),
        CleanupPhase("Autonomous Verify", "Default execution modes"),
        CleanupPhase("Legacy Removal", "Deprecated 5-part references"),
        CleanupPhase("Duplicate Resolution", "Conflicting files"),
    ]
    
    results = {
        "success": True,
        "dry_run": dry_run,
        "phases": [],
        "total_issues_found": 0,
        "total_issues_fixed": 0,
        "iterations": 0,
        "errors": []
    }
    
    iteration = 0
    issues_remaining = True
    
    while issues_remaining and iteration < max_iterations:
        iteration += 1
        print(f"\n{'=' * 70}")
        print(f"🔄 Iteration {iteration}/{max_iterations}")
        print(f"{'=' * 70}")
        
        issues_this_iteration = 0
        
        # Reset phases for new iteration
        for phase in phases:
            phase.status = "not_started"
            phase.issues_found = 0
            phase.issues_fixed = 0
            phase.start_time = None
            phase.end_time = None
        
        # Phase 1: Cache Clear
        print_progress_header(phases, 0, workspace)
        phases[0].start()
        try:
            items, size, errors = clear_caches(
                workspace,
                dry_run=dry_run,
                include_vscode=(iteration == 1),  # Only clear VS Code on first iteration
                include_python=True,
                include_workspace=True,
                verbose=verbose
            )
            phases[0].complete(issues_found=items, issues_fixed=items if not dry_run else 0)
        except Exception as e:
            phases[0].fail(str(e))
            results["errors"].append(f"Cache clear failed: {e}")
        
        # Phase 2: Template Validation
        print_progress_header(phases, 1, workspace)
        phases[1].start()
        try:
            validation_result = validate_templates(workspace)
            phases[1].complete(
                issues_found=validation_result.total_issues,
                issues_fixed=0  # Validation only, fixing in phase 3
            )
            issues_this_iteration += validation_result.total_issues
        except Exception as e:
            phases[1].fail(str(e))
            results["errors"].append(f"Template validation failed: {e}")
        
        # Phase 3: Autonomous Verification
        print_progress_header(phases, 2, workspace)
        phases[2].start()
        try:
            if validation_result.autonomous_issues and not dry_run:
                fixed = fix_autonomous_defaults(
                    workspace,
                    validation_result.autonomous_issues,
                    dry_run=False
                )
                phases[2].complete(
                    issues_found=len(validation_result.autonomous_issues),
                    issues_fixed=fixed
                )
            else:
                phases[2].complete(
                    issues_found=len(validation_result.autonomous_issues),
                    issues_fixed=0
                )
        except Exception as e:
            phases[2].fail(str(e))
            results["errors"].append(f"Autonomous verification failed: {e}")
        
        # Phase 4: Legacy Removal
        print_progress_header(phases, 3, workspace)
        phases[3].start()
        try:
            files_mod, refs_removed, errors = remove_legacy_references(
                workspace,
                dry_run=dry_run,
                verbose=verbose
            )
            phases[3].complete(
                issues_found=refs_removed,
                issues_fixed=refs_removed if not dry_run else 0
            )
            issues_this_iteration += refs_removed
        except Exception as e:
            phases[3].fail(str(e))
            results["errors"].append(f"Legacy removal failed: {e}")
        
        # Phase 5: Duplicate Resolution
        print_progress_header(phases, 4, workspace)
        phases[4].start()
        try:
            duplicates = scan_for_duplicates(workspace)
            if duplicates and not dry_run:
                resolved = resolve_duplicates(workspace, duplicates, auto=True)
                phases[4].complete(
                    issues_found=len(duplicates),
                    issues_fixed=resolved
                )
            else:
                phases[4].complete(
                    issues_found=len(duplicates),
                    issues_fixed=0
                )
            issues_this_iteration += len(duplicates)
        except Exception as e:
            phases[4].fail(str(e))
            results["errors"].append(f"Duplicate resolution failed: {e}")
        
        # Print phase table
        print_phase_table(phases)
        
        # Check if we should continue
        if issues_this_iteration == 0 or dry_run:
            issues_remaining = False
        
        # Update results
        results["iterations"] = iteration
        results["total_issues_found"] += sum(p.issues_found for p in phases)
        results["total_issues_fixed"] += sum(p.issues_fixed for p in phases)
    
    # Final summary
    print(f"\n{'=' * 70}")
    if dry_run:
        print("🔒 DRY RUN COMPLETE")
        print(f"\n   Would fix: {results['total_issues_found']} issue(s)")
        print("\n💡 Run with --execute to apply changes")
    else:
        print("🎉 CLEANUP COMPLETE!")
        print(f"\n   ✅ Fixed: {results['total_issues_fixed']} issue(s)")
        print(f"   🔄 Iterations: {results['iterations']}")
    
    if results["errors"]:
        print(f"\n   ⚠️  Errors: {len(results['errors'])}")
        results["success"] = False
    
    print(f"{'=' * 70}\n")
    
    # Store phase results
    results["phases"] = [
        {
            "name": p.name,
            "status": p.status,
            "issues_found": p.issues_found,
            "issues_fixed": p.issues_fixed,
            "duration": p.duration
        }
        for p in phases
    ]
    
    return results


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="CORTEX Full Cleanup - Comprehensive 5-phase cleanup orchestrator"
    )
    parser.add_argument(
        "--workspace",
        type=str,
        default=".",
        help="Workspace root directory (default: current)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually make changes (default is dry-run)"
    )
    parser.add_argument(
        "--max-iterations",
        type=int,
        default=5,
        help="Maximum validation loop iterations (default: 5)"
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    workspace = Path(args.workspace).resolve()
    
    if not workspace.exists():
        print(f"❌ Workspace not found: {workspace}")
        sys.exit(1)
    
    results = run_full_cleanup(
        workspace,
        dry_run=not args.execute,
        max_iterations=args.max_iterations,
        verbose=args.verbose
    )
    
    sys.exit(0 if results["success"] else 1)


if __name__ == "__main__":
    main()
