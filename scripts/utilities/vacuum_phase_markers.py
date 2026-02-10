#!/usr/bin/env python3
"""
Comprehensive Vacuum Script: Phase Markers & Cleanup.

Autonomous cleanup orchestration:
1. Scan repository recursively for phase marker files
2. Scan root-level files for categorization
3. Archive phase markers to docs/archive/phase-markers/
4. Report on all findings

CORE-002: Ensures clean repository (no temporary markers)
CORE-008: TDD-first validation
CORE-011: Full type hints
CORE-012: Google-style docstrings

Authority: VacuumOrchestrator enhanced algorithm
"""

import sys
from pathlib import Path
from typing import Dict, Any
import json
from datetime import datetime


def main() -> int:
    """
    Execute comprehensive vacuum cleanup workflow.
    
    Returns:
        0 on success, 1 on error
    """
    # Import orchestrator
    try:
        from cortex.orchestrators.support.vacuum_orchestrator import VacuumOrchestrator
    except ImportError as e:
        print(f"❌ Failed to import VacuumOrchestrator: {e}")
        return 1
    
    orchestrator = VacuumOrchestrator()
    repo_root = "."
    
    print("=" * 80)
    print("🧹 CORTEX VACUUM: Phase Markers & Comprehensive Cleanup")
    print("=" * 80)
    print()
    
    # PHASE 1: Scan phase markers
    print("📋 PHASE 1: Scanning Phase Markers (Recursive)")
    print("-" * 80)
    phase_marker_scan = orchestrator.scan_phase_markers(repo_root)
    
    if phase_marker_scan['status'] != 'success':
        print(f"❌ Scan failed: {phase_marker_scan.get('error')}")
        return 1
    
    print(f"✅ Scan complete: {phase_marker_scan['total_markers']} markers found")
    print(f"   Phase markers: {phase_marker_scan['summary']['phase_count']}")
    print(f"   Session markers: {phase_marker_scan['summary']['session_count']}")
    print(f"   Operation markers: {phase_marker_scan['summary']['operation_count']}")
    
    if phase_marker_scan['phase_markers_found']:
        print("\n   Markers by type:")
        for marker_type, markers in phase_marker_scan['by_type'].items():
            if markers:
                print(f"   - {marker_type}: {', '.join(markers)}")
        
        print("\n   Markers by directory:")
        for directory, markers in phase_marker_scan['by_directory'].items():
            if markers:
                rel_dir = directory if directory != "." else "[root]"
                print(f"   - {rel_dir}: {', '.join(markers)}")
    print()
    
    # PHASE 2: Scan root-level files
    print("📋 PHASE 2: Scanning Root-Level Files")
    print("-" * 80)
    root_scan = orchestrator.scan_root_level(repo_root)
    
    if root_scan['status'] != 'success':
        print(f"❌ Scan failed: {root_scan.get('error')}")
        return 1
    
    print(f"✅ Root scan complete:")
    summary = root_scan['summary']
    print(f"   Utility scripts: {summary['utility_scripts_count']}")
    print(f"   Test files: {summary['test_files_count']}")
    print(f"   Log files: {summary['log_files_count']}")
    print(f"   Phase markers: {summary['phase_markers_count']}")
    print(f"   Production files (keep): {summary['production_files_count']}")
    print(f"   Root directories: {summary['directories_count']}")
    print(f"   Total recommendations: {summary['total_recommendations']}")
    print()
    
    # PHASE 3: Analyze recommendations
    print("📋 PHASE 3: Analysis & Recommendations")
    print("-" * 80)
    
    if root_scan['recommendations']:
        # Group by priority
        by_priority = {}
        for rec in root_scan['recommendations']:
            priority = rec.get('priority', 'low')
            if priority not in by_priority:
                by_priority[priority] = []
            by_priority[priority].append(rec)
        
        # Display critical recommendations first
        for priority in ['critical', 'high', 'medium', 'low']:
            if priority in by_priority:
                recs = by_priority[priority]
                priority_icon = {
                    'critical': '🔴',
                    'high': '🟠',
                    'medium': '🟡',
                    'low': '🔵',
                }[priority]
                
                print(f"\n   {priority_icon} {priority.upper()} ({len(recs)} items):")
                for rec in recs:
                    action = rec.get('action', 'review').upper()
                    print(f"      • {rec['file']}")
                    print(f"        Action: {action}")
                    print(f"        Reason: {rec['reason']}")
                    if rec.get('destination'):
                        print(f"        Dest: {rec['destination']}")
    else:
        print("   ✅ No recommendations (root directory clean)")
    
    print()
    
    # PHASE 4: Summary report
    print("=" * 80)
    print("📊 SUMMARY REPORT")
    print("=" * 80)
    
    total_markers = phase_marker_scan['total_markers']
    total_recs = summary['total_recommendations']
    
    print(f"\nPhase Markers Detected: {total_markers}")
    print(f"Root-Level Issues Found: {total_recs}")
    
    if total_markers > 0:
        print(f"\n⚠️  ACTION REQUIRED:")
        print(f"   Archive {total_markers} phase marker file(s) to docs/archive/phase-markers/")
        print(f"   Command: orchestrator.execute_cleanup(plan)")
    else:
        print(f"\n✅ No phase markers detected - repository clean")
    
    print("\n" + "=" * 80)
    return 0


if __name__ == "__main__":
    sys.exit(main())
