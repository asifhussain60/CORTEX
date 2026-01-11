#!/usr/bin/env python3
"""
Query AC-ID Implementation Audit Trail

Usage:
    # Show all implementations
    python3 scripts/query_audit_trail.py

    # Show specific AC-ID history
    python3 scripts/query_audit_trail.py --ac-id AC-ORCH-007
    
    # Show phase completions
    python3 scripts/query_audit_trail.py --phase-completions
    
    # Show recent implementations
    python3 scripts/query_audit_trail.py --recent 10

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.enhanced_audit_logger import (
    AuditStorage,
    ACImplementationTracker,
    AuditCategory
)


def format_timestamp(ts_str):
    """Format ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(ts_str.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except:
        return ts_str


def main():
    parser = argparse.ArgumentParser(
        description="Query AC-ID implementation audit trail"
    )
    parser.add_argument("--ac-id", help="Show history for specific AC-ID")
    parser.add_argument("--phase-completions", action="store_true", 
                       help="Show phase completion milestones")
    parser.add_argument("--recent", type=int, metavar="N",
                       help="Show N most recent implementations")
    parser.add_argument("--summary", action="store_true",
                       help="Show implementation summary")
    
    args = parser.parse_args()
    
    # Initialize audit storage
    workspace_root = Path.cwd()
    db_path = workspace_root / "cortex-brain" / "database" / "audit.db"
    
    if not db_path.exists():
        print(f"✗ Audit database not found: {db_path}")
        print("  Run: python3 scripts/backfill_audit_trail.py")
        return 1
    
    storage = AuditStorage(db_path)
    tracker = ACImplementationTracker(storage)
    
    # Handle different query modes
    if args.summary:
        summary = tracker.get_implementation_summary()
        print("=" * 60)
        print("AC-ID IMPLEMENTATION SUMMARY")
        print("=" * 60)
        print(f"Total AC-IDs: {summary['total_ac_ids']}")
        print(f"Implemented: {summary['implemented']} ({summary['completion_rate']}%)")
        print(f"Partial: {summary['partial']}")
        print()
        print(f"Database: {db_path}")
        print(f"Size: {db_path.stat().st_size / 1024:.1f} KB")
        
    elif args.ac_id:
        history = tracker.query_ac_history(args.ac_id)
        
        if not history:
            print(f"No audit entries found for {args.ac_id}")
            return 1
        
        print(f"=" * 60)
        print(f"AUDIT HISTORY: {args.ac_id}")
        print(f"=" * 60)
        print()
        
        for entry in history:
            print(f"[{format_timestamp(entry['timestamp'])}] {entry['level'].upper()}")
            print(f"  Operation: {entry['operation']}")
            print(f"  Message: {entry['message']}")
            
            if entry.get('context'):
                context = json.loads(entry['context']) if isinstance(entry['context'], str) else entry['context']
                if context.get('tests_passed') is not None:
                    print(f"  Tests: {context['tests_passed']}/{context['tests_total']} passing ({context.get('pass_rate', 0)}%)")
                if context.get('phase'):
                    print(f"  Phase: {context['phase']}")
                if context.get('component'):
                    print(f"  Component: {context['component']}")
            print()
    
    elif args.phase_completions:
        entries = storage.query(
            category=AuditCategory.ORCHESTRATOR,
            page_size=50
        )
        
        phase_entries = [e for e in entries if e.get('operation') == 'phase_completion']
        
        if not phase_entries:
            print("No phase completion milestones found")
            return 1
        
        print("=" * 60)
        print("PHASE COMPLETION MILESTONES")
        print("=" * 60)
        print()
        
        for entry in phase_entries:
            context = json.loads(entry['context']) if isinstance(entry['context'], str) else entry['context']
            
            print(f"Phase {context.get('phase_number')}: {context.get('phase_name')}")
            print(f"  Completed: {format_timestamp(entry['timestamp'])}")
            print(f"  AC-IDs: {context.get('ac_ids_completed')}/{context.get('ac_ids_total')} ({context.get('completion_percentage')}%)")
            print(f"  Tests: {context.get('tests_passed')}/{context.get('tests_total')} ({context.get('pass_rate')}%)")
            print()
    
    elif args.recent:
        entries = storage.query(
            category=AuditCategory.VALIDATION,
            page_size=args.recent
        )
        
        impl_entries = [e for e in entries if e.get('operation') == 'ac_implementation']
        
        if not impl_entries:
            print("No implementation entries found")
            return 1
        
        print("=" * 60)
        print(f"RECENT {args.recent} IMPLEMENTATIONS")
        print("=" * 60)
        print()
        
        for entry in impl_entries[:args.recent]:
            context = json.loads(entry['context']) if isinstance(entry['context'], str) else entry['context']
            
            ac_id = entry.get('ac_id', 'N/A')
            status = context.get('status', 'unknown')
            tests_passed = context.get('tests_passed', 0)
            tests_total = context.get('tests_total', 0)
            pass_rate = context.get('pass_rate', 0)
            component = context.get('component', '')
            
            status_icon = "✓" if status == "implemented" else "⚠" if status == "partial" else "→"
            
            print(f"{status_icon} {ac_id} ({status})")
            print(f"   Tests: {tests_passed}/{tests_total} ({pass_rate}%)")
            if component:
                print(f"   Component: {component}")
            print(f"   Time: {format_timestamp(entry['timestamp'])}")
            print()
    
    else:
        # Default: show summary
        summary = tracker.get_implementation_summary()
        
        print("=" * 60)
        print("AC-ID IMPLEMENTATION AUDIT TRAIL")
        print("=" * 60)
        print()
        print(f"Total AC-IDs tracked: {summary['total_ac_ids']}")
        print(f"Implemented: {summary['implemented']} ({summary['completion_rate']}%)")
        print(f"Partial: {summary['partial']}")
        print()
        print("Recent implementations:")
        print()
        
        for impl in summary['implementations'][:10]:
            status_icon = "✓" if impl['status'] == "implemented" else "⚠" if impl['status'] == "partial" else "→"
            print(f"  {status_icon} {impl['ac_id']} - {impl['tests_passed']}/{impl['tests_total']} tests ({impl['pass_rate']}%)")
        
        if len(summary['implementations']) > 10:
            print(f"\n  ... and {len(summary['implementations']) - 10} more")
        
        print()
        print("Query options:")
        print("  --ac-id AC-XXX      Show full history for specific AC-ID")
        print("  --phase-completions Show phase milestones")
        print("  --recent N          Show N recent implementations")
        print("  --summary           Show summary statistics")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
