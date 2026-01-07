#!/usr/bin/env python3
"""
Update C50 tracking files with new folder references.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import json
from pathlib import Path


def update_tracking_files():
    """Update all tracking JSON files with C50 references."""
    
    c50_tracking = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/documents/planning/active/C50-cortex-v5-remediation/tracking")
    
    # Folder mappings
    mappings = {
        "00A-epic-structure-cleanup": "C50-00A",
        "00B-epic-feature-planner": "C50-00B",
        "00C-test-coverage-sprint": "C50-00C",
        "00D-vscode-cache-optimization": "C50-00D",
        "01-refinement-orchestrator": "C50-01",
        "02-debug-orchestrator": "C50-02",
        "03-knowledge-library-phase": "C50-03",
        "04-ast-scanning-planning": "C50-04",
        "05-context-middleware": "C50-05",
        "06-visual-progress": "C50-06",
        "07-refactor-enforcement": "C50-07",
        "08-orchestrator-migrations": "C50-08",
        "09-final-validation": "C50-09",
        "10-acceptance-validation-system": "C50-10",
        "11-cortex-lens-admin": "C50-11",
        "12-production-validation-pipeline": "C50-12",
        "13-onboarding-system": "C50-13",
        "14-demo-tutorials": "C50-14",
        "15-user-response-templates": "C50-15",
        "16-planning-system-v5-fix": "C50-16",
        "17-planning-v5-enhancement": "C50-17",
        "18-planning-v5-fix": "C50-18",
    }
    
    # Update epic-progress-tracker.json
    tracker_path = c50_tracking / "epic-progress-tracker.json"
    if tracker_path.exists():
        data = json.loads(tracker_path.read_text())
        
        # Update folder references
        json_str = json.dumps(data, indent=2)
        for old, new in mappings.items():
            json_str = json_str.replace(old, new)
        
        # Update epic metadata
        json_str = json_str.replace('"epic_id": "cortex-v5-gap-remediation"', '"epic_id": "C50"')
        json_str = json_str.replace('"CORTEX-5.0"', '"C50-cortex-v5-remediation"')
        json_str = json_str.replace('"total_child_plans": 18', '"total_child_plans": 22')
        
        tracker_path.write_text(json_str)
        print(f"✅ Updated: {tracker_path.name}")
    
    # Update child-plan-registry.json
    registry_path = c50_tracking / "child-plan-registry.json"
    if registry_path.exists():
        data = json.loads(registry_path.read_text())
        
        json_str = json.dumps(data, indent=2)
        for old, new in mappings.items():
            json_str = json_str.replace(old, new)
        
        json_str = json_str.replace('"epic_id": "cortex-v5-gap-remediation"', '"epic_id": "C50"')
        json_str = json_str.replace('"total": 18', '"total": 22')
        
        registry_path.write_text(json_str)
        print(f"✅ Updated: {registry_path.name}")
    
    # Update dependency-graph.json
    graph_path = c50_tracking / "dependency-graph.json"
    if graph_path.exists():
        data = json.loads(graph_path.read_text())
        
        json_str = json.dumps(data, indent=2)
        for old, new in mappings.items():
            json_str = json_str.replace(old, new)
        
        json_str = json_str.replace('"epic_id": "cortex-v5-gap-remediation"', '"epic_id": "C50"')
        json_str = json_str.replace('"total_nodes": 18', '"total_nodes": 22')
        
        graph_path.write_text(json_str)
        print(f"✅ Updated: {graph_path.name}")
    
    print(f"\n📊 Summary:")
    print(f"   • Updated 3 tracking files")
    print(f"   • Converted folder references to C50-* naming")
    print(f"   • Updated epic ID to 'C50'")
    print(f"   • Updated child plan count: 18 → 22")


if __name__ == "__main__":
    update_tracking_files()
