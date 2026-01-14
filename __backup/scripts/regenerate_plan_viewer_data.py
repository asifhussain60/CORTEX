#!/usr/bin/env python3
"""
Regenerate plan-viewer-data.json from SSOT sources

SSOT ARCHITECTURE v1.6.0:
- master-plan.yaml: Architecture SSOT (phase definitions, AC-IDs)
- progress-tracker.json: Execution SSOT (completion state)
- AC-INDEX.yaml: Definition SSOT (AC-ID metadata)

This script is the SINGLE sync bridge between SSOT sources and dashboard.
"""
import json
import yaml
from pathlib import Path
from datetime import datetime, timezone


def load_master_plan():
    """Load master-plan.yaml (Architecture SSOT)"""
    plan_path = Path('cortex-brain/cx6-plan/master-plan.yaml')
    with open(plan_path, 'r') as f:
        return yaml.safe_load(f)


def load_progress_tracker():
    """Load progress-tracker.json (Execution SSOT)"""
    tracker_path = Path('cortex-brain/tier1/tracking/progress-tracker.json')
    with open(tracker_path, 'r') as f:
        return json.load(f)


def load_ac_index():
    """Load AC-INDEX.yaml (Definition SSOT)"""
    ac_path = Path('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml')
    with open(ac_path, 'r') as f:
        return yaml.safe_load(f)


def extract_ac_ids_for_phase(master_plan, phase_num):
    """Extract AC-IDs for a specific phase from master-plan.yaml"""
    phase_keys = {
        1: 'phase_1_foundation',
        1.5: 'archived_phase_1_5_sts_semantic_test_suite',
        2: 'phase_2_orchestration_core',
        3: 'phase_3_feature_orchestrators',
        4: 'archived_phase_4_intelligence',
        4.5: 'archived_phase_4_5_integration_tests',
        5: 'phase_5_cortex_cleanup_decommission',
        6: 'phase_6_security_routing',
        7: 'phase_7_copilot_bridge',
        8: 'phase_8_staged_rollout',
        9: 'phase_9_infrastructure_maturity',
        10: 'phase_10_template_migration',
        11: 'phase_11_intelligent_discovery'
    }
    
    phase_key = phase_keys.get(phase_num)
    if not phase_key or phase_key not in master_plan:
        return []
    
    phase_def = master_plan[phase_key]
    ac_ids = []
    
    if isinstance(phase_def, dict) and 'components' in phase_def:
        for comp_data in phase_def['components'].values():
            if isinstance(comp_data, dict) and 'ac_ids' in comp_data:
                ac_ids.extend(comp_data['ac_ids'])
    
    return sorted(list(set(ac_ids)))


def get_completed_ac_ids(progress_tracker):
    """Get list of completed AC-IDs from progress-tracker.json (FIX: use completed_ac_ids key)"""
    if 'completed_ac_ids' in progress_tracker:
        return progress_tracker['completed_ac_ids']
    if 'verified_implemented' in progress_tracker:
        return progress_tracker['verified_implemented']
    if 'current_phase' in progress_tracker:
        current = progress_tracker['current_phase']
        if current.get('status') == 'complete' and 'ac_ids' in current:
            return current['ac_ids']
    return []


def calculate_phase_status(phase_num, master_plan_ac_ids, completed_ac_ids, current_phase_num):
    """Calculate status for a phase"""
    completed_count = len([ac for ac in master_plan_ac_ids if ac in completed_ac_ids])
    total_count = len(master_plan_ac_ids)
    
    if completed_count == total_count and total_count > 0:
        return 'complete'
    elif phase_num == current_phase_num or completed_count > 0:
        return 'in-progress'
    else:
        return 'planned'


def calculate_phase_completion(master_plan_ac_ids, completed_ac_ids):
    """Calculate completion percentage for a phase"""
    if not master_plan_ac_ids:
        return 0
    completed_count = len([ac for ac in master_plan_ac_ids if ac in completed_ac_ids])
    return int((completed_count / len(master_plan_ac_ids)) * 100)


def get_phase_metadata(master_plan, phase_num):
    """Get phase name and description from master-plan"""
    phase_keys = {
        1: 'phase_1_foundation',
        1.5: 'archived_phase_1_5_sts_semantic_test_suite',
        2: 'phase_2_orchestration_core',
        3: 'phase_3_feature_orchestrators',
        4: 'archived_phase_4_intelligence',
        4.5: 'archived_phase_4_5_integration_tests',
        5: 'phase_5_cortex_cleanup_decommission',
        6: 'phase_6_security_routing',
        7: 'phase_7_copilot_bridge',
        8: 'phase_8_staged_rollout',
        9: 'phase_9_infrastructure_maturity',
        10: 'phase_10_template_migration',
        11: 'phase_11_intelligent_discovery'
    }
    
    phase_key = phase_keys.get(phase_num)
    if not phase_key or phase_key not in master_plan:
        return None, None
    
    phase_def = master_plan[phase_key]
    name = phase_def.get('name', f'Phase {phase_num}')
    description = phase_def.get('description', '')
    
    return name, description


def generate_plan_viewer_data():
    """Generate plan-viewer-data.json from SSOT sources"""
    print("🔄 Regenerating plan-viewer-data.json from master-plan.yaml + AC-INDEX.yaml...")
    
    print("📖 Loading master-plan.yaml...")
    master_plan = load_master_plan()
    
    print("📋 Loading AC-INDEX.yaml...")
    ac_index = load_ac_index()
    
    print("📊 Loading progress-tracker.json...")
    progress_tracker = load_progress_tracker()
    
    completed_ac_ids = get_completed_ac_ids(progress_tracker)
    current_phase_num = progress_tracker.get('current_phase', {}).get('number', 1)
    
    phases = []
    all_ac_ids = []
    
    phase_numbers = [1, 1.5, 2, 3, 4, 4.5, 5, 6, 7, 8, 9, 10, 11]
    
    for phase_num in phase_numbers:
        phase_ac_ids = extract_ac_ids_for_phase(master_plan, phase_num)
        
        if not phase_ac_ids:
            continue
        
        all_ac_ids.extend(phase_ac_ids)
        
        phase_name, phase_desc = get_phase_metadata(master_plan, phase_num)
        
        completed_count = len([ac for ac in phase_ac_ids if ac in completed_ac_ids])
        total_count = len(phase_ac_ids)
        completion_pct = calculate_phase_completion(phase_ac_ids, completed_ac_ids)
        status = calculate_phase_status(phase_num, phase_ac_ids, completed_ac_ids, current_phase_num)
        
        phases.append({
            'id': phase_num,
            'name': phase_name or f'Phase {phase_num}',
            'description': phase_desc[:100] + '...' if phase_desc and len(phase_desc) > 100 else phase_desc,
            'ac_ids': phase_ac_ids,
            'ac_ids_total': total_count,
            'ac_ids_complete': completed_count,
            'completion_percentage': completion_pct,
            'status': status
        })
    
    viewer_data = {
        'plan_metadata': {
            'version': '1.6.0',
            'updated': datetime.now(timezone.utc).isoformat(),
            'total_phases': len(phases),
            'total_ac_ids': len(set(all_ac_ids)),
            'completed_ac_ids': len(set(completed_ac_ids))
        },
        'phases': phases,
        'current_phase': current_phase_num
    }
    
    output_path = Path('cortex-brain/cx6-plan/viewer/plan-viewer-data.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(viewer_data, f, indent=2)
    
    print(f"✅ Saved to {output_path}")
    print(f"   Total AC-IDs: {viewer_data['plan_metadata']['total_ac_ids']}")
    print(f"   Completed: {viewer_data['plan_metadata']['completed_ac_ids']}")
    print(f"   Phases: {viewer_data['plan_metadata']['total_phases']}")
    
    return viewer_data


def main():
    """Entry point"""
    try:
        viewer_data = generate_plan_viewer_data()
        
        print("\n✅ Regeneration complete!")
        
        current_phase = viewer_data['current_phase']
        for phase in viewer_data['phases']:
            if phase['id'] == current_phase:
                print(f"   Phase {phase['id']} Integration Tests now included in dashboard")
                break
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    exit(main())
