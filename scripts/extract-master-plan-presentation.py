#!/usr/bin/env python3
"""
Extract presentation layer from CORTEX master plan and generate reports.
Authority: 5-section User Response Template
"""

import yaml
import json
from pathlib import Path


def main():
    # Load master plan
    master_plan_path = Path("cortex-registry/planning/cortex-refactor-master.yaml")
    with open(master_plan_path) as f:
        master_plan = yaml.safe_load(f)
    
    # Extract presentation section
    presentation = master_plan.get("presentation", {})
    
    # Count phases
    phases = master_plan.get("phases", [])
    complete_count = sum(1 for p in phases if p.get("status") == "complete")
    in_progress_count = sum(1 for p in phases if p.get("status") == "in_progress")
    pending_count = sum(1 for p in phases if p.get("status") == "pending")
    
    # Extract key metrics
    health = master_plan.get("health_status", {})
    p0_issues = health.get("p0_issues", 0)
    p1_issues = health.get("p1_issues", 0)
    
    # Create output object
    output = {
        "summary": presentation.get("summary", "").strip(),
        "current_state": presentation.get("analysis", {}).get("current_state", "").strip(),
        "key_findings": presentation.get("analysis", {}).get("key_findings", []),
        "blockers": presentation.get("analysis", {}).get("blockers_and_risks", {}),
        "recommendation": presentation.get("recommendation", {}).get("primary_strategy", "").strip(),
        "next_steps_immediate": presentation.get("next_steps", {}).get("immediate", []),
        "phase_counts": {
            "complete": complete_count,
            "in_progress": in_progress_count,
            "pending": pending_count,
            "total": len(phases)
        },
        "health": {
            "p0_issues": p0_issues,
            "p1_issues": p1_issues,
            "regression_status": health.get("regression_status", "")
        }
    }
    
    # Write to file for other jobs
    with open("master-plan-presentation.json", "w") as f:
        json.dump(output, f, indent=2)
    
    print("✅ Presentation extracted:")
    print(f"  - Complete phases: {complete_count}")
    print(f"  - In progress: {in_progress_count}")
    print(f"  - Pending: {pending_count}")
    print(f"  - P0 issues: {p0_issues}")
    print(f"  - P1 issues: {p1_issues}")


if __name__ == "__main__":
    main()
