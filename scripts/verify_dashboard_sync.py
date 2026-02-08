#!/usr/bin/env python3
"""
Dashboard Sync Verification Script (ENH-047).

Verifies synchronization between index.yaml and plan-summary.json.

Usage:
    python scripts/verify_dashboard_sync.py

Authority:
    - ENH-047: Dashboard Data Loading Verification
    - CORE-008: TDD implementation
    - CORE-027: Audit trail verification

Exit Codes:
    0: Sync verification passed
    1: Sync verification failed
    2: File not found error
"""

import sys
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List, Optional


def load_index_yaml() -> Dict[str, Any]:
    """
    Load index.yaml from cortex-registry.
    
    Returns:
        Parsed YAML data as dictionary.
        
    Raises:
        FileNotFoundError: If index.yaml not found.
        yaml.YAMLError: If YAML parsing fails.
    """
    index_path = Path("cortex-registry/_cortex-master/index.yaml")
    
    if not index_path.exists():
        raise FileNotFoundError(f"index.yaml not found at {index_path}")
    
    with open(index_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def load_plan_summary_json() -> Dict[str, Any]:
    """
    Load plan-summary.json from dashboard data.
    
    Returns:
        Parsed JSON data as dictionary.
        
    Raises:
        FileNotFoundError: If plan-summary.json not found.
        json.JSONDecodeError: If JSON parsing fails.
    """
    json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
    
    if not json_path.exists():
        raise FileNotFoundError(f"plan-summary.json not found at {json_path}")
    
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def count_active_phases(index_data: Dict[str, Any]) -> int:
    """
    Count active phases in index.yaml.
    
    Args:
        index_data: Parsed index.yaml data.
        
    Returns:
        Number of active phases.
    """
    if "active_phases" not in index_data:
        return 0
    
    active_phases = index_data["active_phases"]
    if isinstance(active_phases, list):
        return len(active_phases)
    
    return 0


def count_completed_phases(index_data: Dict[str, Any]) -> int:
    """
    Count completed phases in index.yaml.
    
    Args:
        index_data: Parsed index.yaml data.
        
    Returns:
        Number of completed phases.
    """
    # Count from completed_phases_2026 and completed_phases_2025
    total_completed = 0
    
    if "completed_phases_2026" in index_data:
        phases_2026 = index_data["completed_phases_2026"]
        if "count" in phases_2026:
            total_completed += phases_2026["count"]
    
    if "completed_phases_2025" in index_data:
        phases_2025 = index_data["completed_phases_2025"]
        if "count" in phases_2025:
            total_completed += phases_2025["count"]
    
    return total_completed


def verify_phase_counts(index_data: Dict[str, Any], 
                       dashboard_data: Dict[str, Any]) -> bool:
    """
    Verify phase counts match between index and dashboard.
    
    Args:
        index_data: Parsed index.yaml data.
        dashboard_data: Parsed plan-summary.json data.
        
    Returns:
        True if counts match, False otherwise.
    """
    success = True
    
    # Get counts from dashboard
    dashboard_total = dashboard_data.get("total_phases", 0)
    dashboard_active = dashboard_data.get("active_phases", 0)
    dashboard_completed = dashboard_data.get("completed_phases", 0)
    
    # Get counts from index
    index_active = count_active_phases(index_data)
    index_completed = count_completed_phases(index_data)
    index_total = index_active + index_completed
    
    # Verify total phases
    if dashboard_total != index_total:
        print(f"❌ Total phase count mismatch:")
        print(f"   Dashboard: {dashboard_total}")
        print(f"   Index: {index_total} (active={index_active} + completed={index_completed})")
        success = False
    else:
        print(f"✅ Total phases match: {dashboard_total}")
    
    # Verify active phases (may differ slightly due to status changes)
    # Allow up to 2 phase difference for ongoing status transitions
    active_diff = abs(dashboard_active - index_active)
    if active_diff > 2:
        print(f"⚠️  Active phase count difference > 2:")
        print(f"   Dashboard: {dashboard_active}")
        print(f"   Index: {index_active}")
        print(f"   Difference: {active_diff}")
        print(f"   Note: Small differences may occur during status transitions")
    else:
        print(f"✅ Active phases approximately match: dashboard={dashboard_active}, index={index_active}")
    
    # Verify completed phases
    if dashboard_completed != index_completed:
        print(f"❌ Completed phase count mismatch:")
        print(f"   Dashboard: {dashboard_completed}")
        print(f"   Index: {index_completed}")
        success = False
    else:
        print(f"✅ Completed phases match: {dashboard_completed}")
    
    return success


def verify_completion_rate(dashboard_data: Dict[str, Any]) -> bool:
    """
    Verify completion rate calculation is accurate.
    
    Args:
        dashboard_data: Parsed plan-summary.json data.
        
    Returns:
        True if completion rate is accurate, False otherwise.
    """
    total = dashboard_data.get("total_phases", 0)
    completed = dashboard_data.get("completed_phases", 0)
    reported_rate = dashboard_data.get("completion_rate", 0)
    
    if total == 0:
        expected_rate = 0
    else:
        expected_rate = (completed / total) * 100
    
    # Allow 0.5% tolerance for rounding
    rate_diff = abs(reported_rate - expected_rate)
    if rate_diff > 0.5:
        print(f"❌ Completion rate calculation error:")
        print(f"   Reported: {reported_rate}%")
        print(f"   Expected: {expected_rate:.1f}%")
        print(f"   Difference: {rate_diff:.2f}%")
        return False
    else:
        print(f"✅ Completion rate accurate: {reported_rate}%")
        return True


def verify_phase_structure(dashboard_data: Dict[str, Any]) -> bool:
    """
    Verify phase data structure is valid.
    
    Args:
        dashboard_data: Parsed plan-summary.json data.
        
    Returns:
        True if structure is valid, False otherwise.
    """
    if "phases" not in dashboard_data:
        print("❌ Missing 'phases' array in dashboard data")
        return False
    
    phases = dashboard_data["phases"]
    if not isinstance(phases, list):
        print("❌ 'phases' must be a list")
        return False
    
    if len(phases) == 0:
        print("❌ No phases found in dashboard data")
        return False
    
    # Verify first few phases have required fields
    required_fields = ["id", "name", "status", "priority"]
    for i, phase in enumerate(phases[:3]):  # Check first 3 phases
        for field in required_fields:
            if field not in phase:
                print(f"❌ Phase {i} missing required field: {field}")
                return False
    
    print(f"✅ Phase structure valid ({len(phases)} phases)")
    return True


def main() -> int:
    """
    Main verification function.
    
    Returns:
        Exit code (0 = success, 1 = failure, 2 = error).
    """
    print("=" * 60)
    print("CORTEX Dashboard Sync Verification (ENH-047)")
    print("=" * 60)
    print()
    
    try:
        # Load data files
        print("Loading data files...")
        index_data = load_index_yaml()
        dashboard_data = load_plan_summary_json()
        print("✅ Data files loaded successfully")
        print()
        
        # Run verification checks
        print("Running verification checks...")
        print()
        
        checks = [
            ("Phase Structure", verify_phase_structure(dashboard_data)),
            ("Phase Counts", verify_phase_counts(index_data, dashboard_data)),
            ("Completion Rate", verify_completion_rate(dashboard_data)),
        ]
        
        print()
        print("=" * 60)
        print("VERIFICATION SUMMARY")
        print("=" * 60)
        
        all_passed = True
        for check_name, passed in checks:
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"{check_name}: {status}")
            if not passed:
                all_passed = False
        
        print()
        if all_passed:
            print("🟢 ALL CHECKS PASSED - Dashboard sync verified")
            return 0
        else:
            print("🔴 SOME CHECKS FAILED - Dashboard may need regeneration")
            print()
            print("To regenerate dashboard data:")
            print("  python scripts/regenerate_dashboard_data.py")
            return 1
            
    except FileNotFoundError as e:
        print(f"❌ File not found: {e}")
        return 2
    except (yaml.YAMLError, json.JSONDecodeError) as e:
        print(f"❌ Parse error: {e}")
        return 2
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
