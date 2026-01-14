"""
Evidence Chain Automation (AC-VALIDATE-001 → AC-VALIDATE-003)

Permanent solution for brittleness: Automated evidence chain from test execution
to tracker update to dashboard sync.

Components:
- AC-VALIDATE-001: extract_ac_id_from_test_name(), create_evidence_entry()
- AC-VALIDATE-002: EvidenceAggregator (audit logs → tracker update)
- AC-VALIDATE-003: EvidenceGate (pre-commit false positive blocker)

Evidence Flow:
    Test Execution (pytest)
        ↓ (pytest plugin captures)
    Audit Log Entry (AC-ID + result + timestamp)
        ↓ (evidence aggregator reads)
    Progress Tracker Update (atomic)
        ↓ (regenerate script)
    Dashboard Sync (automatic)
        ↓
    Zero Manual State Manipulation = Zero Brittleness

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""
import json
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple


# =============================================================================
# AC-VALIDATE-001: Pytest Evidence Plugin Functions
# =============================================================================

def extract_ac_id_from_test_name(test_name: str) -> Optional[str]:
    """
    Extract AC-ID from test function name.
    
    Patterns matched:
    - test_AC_AUDIT_001_description → AC-AUDIT-001
    - test_AC_VALIDATE_002_more_words → AC-VALIDATE-002
    - test_AC_ORCH_007_with_3_retries → AC-ORCH-007
    
    Args:
        test_name: Test function name (e.g., "test_AC_AUDIT_001_creates_entry")
    
    Returns:
        AC-ID string (e.g., "AC-AUDIT-001") or None if no pattern found
    """
    # Pattern: AC_{CATEGORY}_{NUMBER}
    # Match AC_ followed by uppercase letters, underscore, then 3 digits
    pattern = r'AC_([A-Z]+)_(\d{3})'
    match = re.search(pattern, test_name)
    
    if match:
        category = match.group(1)
        number = match.group(2)
        return f"AC-{category}-{number}"
    
    return None


def create_evidence_entry(
    ac_id: str,
    test_name: str,
    outcome: str,
    duration: float,
    error_message: Optional[str] = None
) -> Dict:
    """
    Create evidence entry for audit log.
    
    Args:
        ac_id: AC-ID (e.g., "AC-AUDIT-001")
        test_name: Full test function name
        outcome: "passed", "failed", "skipped"
        duration: Test duration in seconds
        error_message: Error message if test failed
    
    Returns:
        Evidence entry dict ready for audit log
    """
    entry = {
        "ac_id": ac_id,
        "test_name": test_name,
        "outcome": outcome,
        "duration": duration,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "source": "pytest"
    }
    
    if error_message:
        entry["error_message"] = error_message
    
    return entry


# =============================================================================
# AC-VALIDATE-002: Evidence Aggregator
# =============================================================================

class EvidenceAggregator:
    """
    Aggregates test evidence from audit logs and updates progress tracker.
    
    Rules:
    - AC-ID is "verified" only if ALL related tests pass
    - AC-ID is "partial" if some tests pass, some fail
    - Tracker update is atomic (write to temp, then rename)
    """
    
    def aggregate(self, audit_entries: List[Dict]) -> Dict:
        """
        Aggregate audit log entries by AC-ID.
        
        Args:
            audit_entries: List of evidence entries from audit log
        
        Returns:
            {
                "verified": set of AC-IDs with all tests passing,
                "partial": set of AC-IDs with mixed results,
                "failed": set of AC-IDs with all tests failing,
                "stats": aggregation statistics
            }
        """
        # Group entries by AC-ID
        by_ac_id: Dict[str, List[Dict]] = {}
        for entry in audit_entries:
            ac_id = entry.get("ac_id")
            if ac_id:
                if ac_id not in by_ac_id:
                    by_ac_id[ac_id] = []
                by_ac_id[ac_id].append(entry)
        
        verified: Set[str] = set()
        partial: Set[str] = set()
        failed: Set[str] = set()
        
        for ac_id, entries in by_ac_id.items():
            outcomes = [e.get("outcome") for e in entries]
            
            passed_count = outcomes.count("passed")
            failed_count = outcomes.count("failed")
            
            if failed_count == 0 and passed_count > 0:
                verified.add(ac_id)
            elif passed_count == 0 and failed_count > 0:
                failed.add(ac_id)
            else:
                partial.add(ac_id)
        
        return {
            "verified": verified,
            "partial": partial,
            "failed": failed,
            "stats": {
                "total_entries": len(audit_entries),
                "unique_ac_ids": len(by_ac_id),
                "verified_count": len(verified),
                "partial_count": len(partial),
                "failed_count": len(failed)
            }
        }
    
    def update_tracker(self, tracker_path: Path, verified_ac_ids: Set[str]) -> None:
        """
        Update progress tracker with verified AC-IDs using atomic write.
        
        Args:
            tracker_path: Path to progress-tracker.json
            verified_ac_ids: Set of verified AC-IDs to add
        """
        # Read current tracker
        tracker_data = json.loads(tracker_path.read_text())
        
        # Get existing verified list
        current_verified = set(
            tracker_data.get("current_phase", {}).get("verified_implemented", [])
        )
        
        # Merge new verified AC-IDs
        updated_verified = current_verified | verified_ac_ids
        
        # Update tracker data
        if "current_phase" not in tracker_data:
            tracker_data["current_phase"] = {}
        tracker_data["current_phase"]["verified_implemented"] = sorted(list(updated_verified))
        tracker_data["last_updated"] = datetime.now(timezone.utc).isoformat()
        tracker_data["updated_by"] = "EvidenceAggregator (automated)"
        
        # Atomic write: write to temp file, then rename
        temp_path = tracker_path.with_suffix('.tmp')
        temp_path.write_text(json.dumps(tracker_data, indent=2))
        temp_path.rename(tracker_path)


# =============================================================================
# AC-VALIDATE-003: Evidence Gate (Pre-commit Blocker)
# =============================================================================

class EvidenceGate:
    """
    Pre-commit gate that blocks commits if claims exceed evidence.
    
    Rules:
    - Claimed AC-IDs must be backed by test evidence
    - Threshold is configurable (default 80%, strict mode 100%)
    - Reports unverified claims for remediation
    """
    
    def __init__(self, threshold: float = 80.0):
        """
        Initialize evidence gate.
        
        Args:
            threshold: Minimum verification rate to pass (default 80%)
        """
        self.threshold = threshold
    
    def check(self, claimed: Set[str], verified: Set[str]) -> Dict:
        """
        Check if claimed completion is backed by evidence.
        
        Args:
            claimed: Set of AC-IDs claimed as complete
            verified: Set of AC-IDs with passing test evidence
        
        Returns:
            {
                "passed": bool,
                "verification_rate": float,
                "verified": set of verified AC-IDs,
                "unverified": set of claimed but unverified,
                "extra_evidence": set of verified but not claimed
            }
        """
        if not claimed:
            # No claims = 100% verification rate (nothing to verify)
            return {
                "passed": True,
                "verification_rate": 100.0,
                "verified": set(),
                "unverified": set(),
                "extra_evidence": verified.copy()
            }
        
        # Calculate overlap
        verified_claims = claimed & verified
        unverified_claims = claimed - verified
        extra_evidence = verified - claimed
        
        # Calculate verification rate
        verification_rate = (len(verified_claims) / len(claimed)) * 100.0
        
        return {
            "passed": verification_rate >= self.threshold,
            "verification_rate": verification_rate,
            "verified": verified_claims,
            "unverified": unverified_claims,
            "extra_evidence": extra_evidence
        }


# =============================================================================
# CLI Entry Point
# =============================================================================

def main():
    """CLI entry point for evidence chain operations."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Evidence Chain Automation")
    parser.add_argument("command", choices=["aggregate", "check", "update"])
    parser.add_argument("--audit-log", type=Path, help="Path to audit log JSON")
    parser.add_argument("--tracker", type=Path, help="Path to progress-tracker.json")
    parser.add_argument("--threshold", type=float, default=80.0, help="Verification threshold")
    
    args = parser.parse_args()
    
    if args.command == "aggregate":
        if not args.audit_log:
            print("Error: --audit-log required for aggregate command")
            return 1
        
        entries = json.loads(args.audit_log.read_text())
        aggregator = EvidenceAggregator()
        result = aggregator.aggregate(entries)
        
        print(f"Verified: {len(result['verified'])} AC-IDs")
        print(f"Partial: {len(result['partial'])} AC-IDs")
        print(f"Failed: {len(result['failed'])} AC-IDs")
        
    elif args.command == "check":
        print("Evidence gate check - use in pre-commit hook")
        
    elif args.command == "update":
        if not args.tracker:
            print("Error: --tracker required for update command")
            return 1
        print(f"Would update tracker at: {args.tracker}")
    
    return 0


if __name__ == "__main__":
    exit(main())
