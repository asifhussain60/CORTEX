#!/usr/bin/env python3
"""
Sync plan-viewer-data.json from progress-tracker.json
Run after any progress updates to keep dashboard current
"""
import json
from pathlib import Path
from datetime import datetime, timezone


def sync_plan_viewer_data():
    """Generate plan-viewer-data.json from progress tracker"""
    
    # Load progress tracker
    tracker_path = Path('cortex-brain/tier1/tracking/progress-tracker.json')
    if not tracker_path.exists():
        print(f'❌ Tracker not found: {tracker_path}')
        return False
    
    tracker = json.loads(tracker_path.read_text())
    
    # Build plan viewer data
    data = {
        'plan_metadata': {
            'plan_id': 'CORTEX-6.0-SNOWBALL-MASTER',
            'total_ac_ids': 102,
            'completed_ac_ids': 0,
            'in_progress_ac_ids': 0,
            'version': '1.3.0',
            'updated': datetime.now(timezone.utc).isoformat(),
            'status': tracker.get('active_epic', {}).get('status', 'in_progress')
        },
        'phases': []
    }
    
    # Count total completed
    total_completed = 0
    
    # Add Phase 1
    if 'current_phase' in tracker:
        p1 = tracker['current_phase']
        completed = p1.get('completed_count', 0)
        total_completed += completed
        data['phases'].append({
            'id': 1,
            'name': 'Foundation Enhancement',
            'completion_percentage': p1.get('completion_percentage', 0),
            'ac_ids_complete': completed,
            'ac_ids_total': p1.get('total_ac_count', 34),
            'status': p1.get('status', 'in_progress'),
            'description': 'Build core infrastructure (Audit, Governance, State, Lifecycle, Evidence, Security)',
            'verified_implemented': p1.get('verified_implemented', [])
        })
    
    # Add Phase 1.5
    if 'phase_1_5_sts' in tracker:
        p15 = tracker['phase_1_5_sts']
        completed = p15.get('completed_count', 0)
        total_completed += completed
        data['phases'].append({
            'id': 1.5,
            'name': 'STS as Capability 0',
            'completion_percentage': p15.get('completion_percentage', 0),
            'ac_ids_complete': completed,
            'ac_ids_total': p15.get('total_ac_count', 3),
            'status': p15.get('status', 'in_progress'),
            'description': 'Validate orchestration framework with Golden Corpus'
        })
    
    # Add Phase 2
    if 'phase_2_orchestration' in tracker:
        p2 = tracker['phase_2_orchestration']
        completed = p2.get('completed_count', 0)
        total_completed += completed
        data['phases'].append({
            'id': 2,
            'name': 'Orchestration Core',
            'completion_percentage': p2.get('completion_percentage', 0),
            'ac_ids_complete': completed,
            'ac_ids_total': p2.get('total_ac_count', 17),
            'status': p2.get('status', 'in_progress'),
            'description': 'Establish default working mechanism (MasterOrchestrator, TodoManager, TDD-Master, Planning)',
            'verified_implemented': p2.get('verified_implemented', [])
        })
    
    # Add Phase 3
    if 'phase_3_features' in tracker:
        p3 = tracker['phase_3_features']
        completed = p3.get('completed_count', 0)
        total_completed += completed
        data['phases'].append({
            'id': 3,
            'name': 'Feature Orchestrators',
            'completion_percentage': p3.get('completion_percentage', 0),
            'ac_ids_complete': completed,
            'ac_ids_total': p3.get('total_ac_count', 16),
            'status': p3.get('status', 'in_progress'),
            'description': 'Build feature orchestrators (ADO, Vacuum, Investigation, Crawlers, Onboarding)',
            'verified_implemented': p3.get('verified_implemented', [])
        })
    
    # Add Phase 4
    if 'phase_4_intelligence' in tracker:
        p4 = tracker['phase_4_intelligence']
        completed = p4.get('completed_count', 0)
        total_completed += completed
        data['phases'].append({
            'id': 4,
            'name': 'Intelligence Layer',
            'completion_percentage': p4.get('completion_percentage', 0),
            'ac_ids_complete': completed,
            'ac_ids_total': p4.get('total_ac_count', 10),
            'status': p4.get('status', 'in_progress'),
            'description': 'Intelligence layer (LLM Intent Classifier, Vision API, Knowledge Practices, Knowledge Graph)',
            'verified_implemented': p4.get('verified_implemented', [])
        })
    
    # Update metadata totals
    data['plan_metadata']['completed_ac_ids'] = total_completed
    
    # Count in-progress
    in_progress = 0
    for phase in data['phases']:
        if phase['status'] in ['in_progress', 'partial', 'substantially_complete']:
            in_progress += phase['ac_ids_total'] - phase['ac_ids_complete']
    data['plan_metadata']['in_progress_ac_ids'] = in_progress
    
    # Write to JSON file
    output_path = Path('cortex-brain/cx6-plan/viewer/plan-viewer-data.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2))
    
    print(f'✅ Synced {output_path}')
    print(f'   Total: {total_completed}/102 AC-IDs ({round(total_completed/102*100)}%)')
    print(f'   Phases: {len(data["phases"])} phases')
    for phase in data['phases']:
        status_icon = '✅' if phase['status'] in ['completed', 'complete'] else '🔄'
        print(f'   {status_icon} Phase {phase["id"]}: {phase["ac_ids_complete"]}/{phase["ac_ids_total"]} ({phase["completion_percentage"]}%)')
    
    return True


if __name__ == '__main__':
    import sys
    success = sync_plan_viewer_data()
    sys.exit(0 if success else 1)
