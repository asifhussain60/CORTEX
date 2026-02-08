#!/usr/bin/env python3
"""
Dashboard Data Regeneration Script (ENH-047).

Regenerates plan-summary.json from index.yaml master source.

Usage:
    python scripts/regenerate_dashboard_data.py

Authority:
    - ENH-047: Dashboard Data Loading Verification
    - CORE-008: TDD implementation
    - CORE-030: Implementation Truth
    
Exit Codes:
    0: Regeneration successful
    1: Regeneration failed
    2: File error
"""

import sys
import yaml
import json
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime


def load_index_yaml() -> Dict[str, Any]:
    """
    Load index.yaml from cortex-registry.
    
    Returns:
        Parsed YAML data as dictionary.
    """
    index_path = Path("cortex-registry/_cortex-master/index.yaml")
    
    if not index_path.exists():
        raise FileNotFoundError(f"index.yaml not found at {index_path}")
    
    with open(index_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)


def extract_phase_data(phase: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract phase data for dashboard display.
    
    Args:
        phase: Phase dictionary from index.yaml.
        
    Returns:
        Dictionary with display-friendly phase data.
    """
    return {
        "id": phase.get("id", "unknown"),
        "name": phase.get("name", "Unknown Phase"),
        "status": phase.get("status", "unknown"),
        "priority": phase.get("priority", "P2"),
        "progress": f"{phase.get('progress', 0)}%",
        "description": phase.get("description", "").strip()
    }


def generate_plan_summary(index_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate plan-summary.json content from index.yaml.
    
    Args:
        index_data: Parsed index.yaml data.
        
    Returns:
        Dictionary ready for JSON serialization.
    """
    # Extract active phases
    active_phases = index_data.get("active_phases", [])
    
    # Extract completed phases count
    completed_2026 = index_data.get("completed_phases_2026", {}).get("count", 0)
    completed_2025 = index_data.get("completed_phases_2025", {}).get("count", 0)
    completed_count = completed_2026 + completed_2025
    
    # Calculate totals
    active_count = len(active_phases)
    total_phases = active_count + completed_count
    
    # Calculate completion rate
    if total_phases > 0:
        completion_rate = round((completed_count / total_phases) * 100, 1)
    else:
        completion_rate = 0.0
    
    # Count in_progress and planned
    in_progress_count = sum(1 for p in active_phases if p.get("status") == "in_progress")
    planned_count = sum(1 for p in active_phases if p.get("status") == "planned")
    
    # Build phase list (show active phases first)
    phases = []
    for phase in active_phases:
        phases.append(extract_phase_data(phase))
    
    # Build summary
    summary = {
        "total_phases": total_phases,
        "active_phases": active_count,
        "completed_phases": completed_count,
        "completion_rate": completion_rate,
        "in_progress_count": in_progress_count,
        "planned_count": planned_count,
        "phases": phases,
        "generated_at": datetime.utcnow().isoformat() + "Z",
        "source": "index.yaml",
        "version": "1.0"
    }
    
    return summary


def save_plan_summary(data: Dict[str, Any]) -> None:
    """
    Save plan-summary.json to dashboard data directory.
    
    Args:
        data: Plan summary data to save.
    """
    json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
    
    # Ensure directory exists
    json_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Write JSON with pretty formatting
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write('\n')  # Add trailing newline


def main() -> int:
    """
    Main regeneration function.
    
    Returns:
        Exit code (0 = success, 1 = failure, 2 = error).
    """
    print("=" * 60)
    print("CORTEX Dashboard Data Regeneration (ENH-047)")
    print("=" * 60)
    print()
    
    try:
        # Load index.yaml
        print("Loading index.yaml...")
        index_data = load_index_yaml()
        print("✅ index.yaml loaded successfully")
        print()
        
        # Generate plan summary
        print("Generating plan-summary.json...")
        summary = generate_plan_summary(index_data)
        print(f"✅ Generated summary:")
        print(f"   - Total phases: {summary['total_phases']}")
        print(f"   - Active phases: {summary['active_phases']}")
        print(f"   - Completed phases: {summary['completed_phases']}")
        print(f"   - Completion rate: {summary['completion_rate']}%")
        print()
        
        # Save to file
        print("Saving plan-summary.json...")
        save_plan_summary(summary)
        print("✅ plan-summary.json saved successfully")
        print()
        
        # Show file location
        json_path = Path("cortex-registry/_cortex-master/dashboard/data/plan-summary.json")
        print(f"📁 File location: {json_path.absolute()}")
        print()
        
        print("🟢 REGENERATION COMPLETE")
        print()
        print("Next steps:")
        print("  1. Verify sync: python scripts/verify_dashboard_sync.py")
        print("  2. View dashboard: open cortex-registry/_cortex-master/dashboard/index.html")
        return 0
        
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
