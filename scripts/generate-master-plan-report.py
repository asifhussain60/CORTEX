#!/usr/bin/env python3
"""
Generate markdown report from extracted presentation data.
Authority: 5-section User Response Template
"""

import json
from pathlib import Path


def main():
    with open("master-plan-presentation.json") as f:
        data = json.load(f)
    
    # Build report
    lines = [
        "# 📊 CORTEX Master Plan Status",
        "",
        "## Executive Summary",
        data['summary'],
        "",
        "## Phase Progress",
        f"- ✅ Complete: {data['phase_counts']['complete']}/{data['phase_counts']['total']}",
        f"- 🔵 In Progress: {data['phase_counts']['in_progress']}",
        f"- ⚪ Pending: {data['phase_counts']['pending']}",
        "",
        "## Current State",
        data['current_state'],
        "",
        "## Health Status",
        f"- P0 Issues: {data['health']['p0_issues']}",
        f"- P1 Issues: {data['health']['p1_issues']}",
        f"- Regression: {data['health']['regression_status']}",
        "",
        "## Key Findings",
    ]
    
    if isinstance(data['key_findings'], list):
        for finding in data['key_findings']:
            lines.append(f"- {finding}")
    
    lines.extend([
        "",
        "## Recommendation",
        data['recommendation'],
        "",
        "## Next Steps (Immediate)",
    ])
    
    if isinstance(data['next_steps_immediate'], list):
        for i, step in enumerate(data['next_steps_immediate'], 1):
            lines.append(f"{i}. {step}")
    
    report = "\n".join(lines)
    
    # Write report
    Path("master-plan-report.md").write_text(report)
    print(report)


if __name__ == "__main__":
    main()
