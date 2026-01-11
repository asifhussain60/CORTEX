#!/usr/bin/env python3
"""
Log AC-ID Implementation to Audit Trail

Usage:
    python3 scripts/log_ac_implementation.py AC-ORCH-007 --tests-passed 5 --tests-total 5 --status implemented
    python3 scripts/log_ac_implementation.py AC-TDD-001 --tests-passed 8 --tests-total 10 --status partial

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.infrastructure.enhanced_audit_logger import (
    AuditStorage,
    ACImplementationTracker
)


def main():
    parser = argparse.ArgumentParser(
        description="Log AC-ID implementation with test evidence to audit trail"
    )
    parser.add_argument("ac_id", help="AC-ID to log (e.g., AC-ORCH-007)")
    parser.add_argument("--tests-passed", type=int, required=True, help="Number of tests passed")
    parser.add_argument("--tests-total", type=int, required=True, help="Total number of tests")
    parser.add_argument("--status", choices=["implemented", "partial", "planned"], 
                       default="implemented", help="Implementation status")
    parser.add_argument("--phase", help="Phase name (e.g., 'Phase 2: Orchestration Core')")
    parser.add_argument("--component", help="Component name (e.g., 'MasterOrchestrator')")
    parser.add_argument("--correlation-id", help="Correlation ID for tracking")
    
    args = parser.parse_args()
    
    # Initialize audit storage
    workspace_root = Path.cwd()
    db_path = workspace_root / "cortex-brain" / "database" / "audit.db"
    
    if not db_path.parent.exists():
        db_path.parent.mkdir(parents=True, exist_ok=True)
    
    storage = AuditStorage(db_path)
    tracker = ACImplementationTracker(storage)
    
    # Log the implementation
    tracker.log_ac_implementation(
        ac_id=args.ac_id,
        status=args.status,
        tests_passed=args.tests_passed,
        tests_total=args.tests_total,
        correlation_id=args.correlation_id,
        phase=args.phase,
        component=args.component
    )
    
    pass_rate = round((args.tests_passed / args.tests_total * 100), 1) if args.tests_total > 0 else 0
    
    print(f"✓ Logged {args.ac_id} implementation to audit trail")
    print(f"  Status: {args.status}")
    print(f"  Tests: {args.tests_passed}/{args.tests_total} ({pass_rate}%)")
    if args.phase:
        print(f"  Phase: {args.phase}")
    if args.component:
        print(f"  Component: {args.component}")


if __name__ == "__main__":
    main()
