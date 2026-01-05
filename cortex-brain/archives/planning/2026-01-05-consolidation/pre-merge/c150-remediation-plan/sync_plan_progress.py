#!/usr/bin/env python3
"""
C150 Plan Progress Sync Script
Syncs plan status from YAML to progress-tracker.json for real-time viewer updates

Usage: python3 sync_plan_progress.py
"""

import json
import yaml
from pathlib import Path
from datetime import datetime


def load_plan_yaml(plan_path):
    """Load plan YAML and extract phase statuses."""
    with open(plan_path) as f:
        plan = yaml.safe_load(f)
    
    return plan


def sync_progress(plan_yaml_path, tracker_json_path):
    """Sync progress from YAML plan to JSON tracker."""
    
    # Load plan YAML
    plan = load_plan_yaml(plan_yaml_path)
    
    # Load existing tracker
    with open(tracker_json_path) as f:
        tracker = json.load(f)
    
    # Update metadata
    tracker['updated_date'] = datetime.now().strftime('%Y-%m-%d')
    tracker['status'] = plan.get('status', 'in_progress')
    
    # Map YAML phases to tracker phases
    yaml_phases = {p['phase_id']: p for p in plan.get('phases', [])}
    
    for tracker_phase in tracker['phases']:
        phase_id = str(tracker_phase['number'])
        
        if phase_id in yaml_phases:
            yaml_phase = yaml_phases[phase_id]
            
            # Update status
            status_map = {
                'NOT_STARTED': 'not_started',
                'IN_PROGRESS': 'in_progress',
                'COMPLETE': 'complete',
                'FAILED': 'failed',
                'BLOCKED': 'blocked'
            }
            yaml_status = yaml_phase.get('status', 'NOT_STARTED')
            tracker_phase['status'] = status_map.get(yaml_status, 'not_started')
            
            # Update actual hours if available
            if 'actual_hours' in yaml_phase and yaml_phase['actual_hours'] is not None:
                tracker_phase['actual_hours'] = yaml_phase['actual_hours']
            
            # Update validation status
            if 'validation_passed' in yaml_phase:
                tracker_phase['validation_passed'] = yaml_phase['validation_passed']
    
    # Calculate overall stats
    phases = tracker['phases']
    complete_count = sum(1 for p in phases if p['status'] == 'complete')
    in_progress_count = sum(1 for p in phases if p['status'] == 'in_progress')
    
    # Update overall status
    if complete_count == len(phases):
        tracker['status'] = 'complete'
    elif in_progress_count > 0 or complete_count > 0:
        tracker['status'] = 'in_progress'
    else:
        tracker['status'] = 'not_started'
    
    # Save updated tracker
    with open(tracker_json_path, 'w') as f:
        json.dump(tracker, f, indent=2)
    
    print(f"✅ Progress synced: {complete_count}/{len(phases)} phases complete")
    return tracker


def main():
    """Main entry point."""
    base_path = Path(__file__).parent
    plan_yaml = base_path / "00-c150-remediation-plan.yaml"
    tracker_json = base_path / "tracking" / "progress-tracker.json"
    
    if not plan_yaml.exists():
        print(f"❌ Plan YAML not found: {plan_yaml}")
        return 1
    
    if not tracker_json.exists():
        print(f"❌ Tracker JSON not found: {tracker_json}")
        return 1
    
    try:
        tracker = sync_progress(plan_yaml, tracker_json)
        
        # Print summary
        phases = tracker['phases']
        complete = sum(1 for p in phases if p['status'] == 'complete')
        in_progress = sum(1 for p in phases if p['status'] == 'in_progress')
        failed = sum(1 for p in phases if p['status'] == 'failed')
        not_started = sum(1 for p in phases if p['status'] == 'not_started')
        
        print(f"\n📊 Status Summary:")
        print(f"   ✅ Complete: {complete}")
        print(f"   🔄 In Progress: {in_progress}")
        print(f"   ❌ Failed: {failed}")
        print(f"   ⏸️  Not Started: {not_started}")
        print(f"   📈 Overall: {complete}/{len(phases)} ({complete/len(phases)*100:.1f}%)")
        
        return 0
    except Exception as e:
        print(f"❌ Error syncing progress: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
