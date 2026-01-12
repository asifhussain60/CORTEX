#!/usr/bin/env python3
"""
Regenerate plan-viewer-data.json from master-plan.yaml + AC-INDEX.yaml

This script is the SyncOrchestrator function for rebuilding dashboard JSON.
Used when Phase definitions or AC-IDs change.
"""
import json
import yaml
from pathlib import Path
from datetime import datetime, timezone
from collections import defaultdict


def load_master_plan():
    """Load master-plan.yaml to get all phase definitions"""
    plan_path = Path('cortex-brain/cx6-plan/master-plan.yaml')
    with open(plan_path, 'r') as f:
        return yaml.safe_load(f)


def load_ac_index():
    """Load AC-INDEX.yaml to get AC-ID names and metadata"""
    ac_path = Path('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml')
    with open(ac_path, 'r') as f:
        data = yaml.safe_load(f)
    
    # Build AC-ID lookup table by scanning entire YAML
    ac_map = {}
    
    # Recursively extract AC-IDs from the entire YAML structure
    def extract_ac_ids(obj, result_dict):
        """Recursively find all AC-ID entries in YAML"""
        if isinstance(obj, dict):
            for key, value in obj.items():
                # Check if this looks like an AC-ID (e.g., AC-AUDIT-001, AC-INTEG-001)
                if isinstance(key, str) and key.startswith('AC-') and key.count('-') >= 2:
                    if isinstance(value, dict):
                        # Extract metadata
                        ac_id = value.get('id', key)
                        result_dict[ac_id] = {
                            'name': value.get('name', ''),
                            'description': value.get('description', ''),
                            'status': value.get('status', 'planned'),
                            'phase': value.get('phase', 0)
                        }
                
                # Recurse into nested structures
                extract_ac_ids(value, result_dict)
        
        elif isinstance(obj, list):
            for item in obj:
                extract_ac_ids(item, result_dict)
    
    extract_ac_ids(data, ac_map)
    
    return ac_map, data


def load_progress_tracker():
    """Load progress-tracker.json to get current completion status"""
    tracker_path = Path('cortex-brain/tier1/tracking/progress-tracker.json')
    if tracker_path.exists():
        with open(tracker_path, 'r') as f:
            return json.load(f)
    return None


def extract_ac_ids_for_phase(master_plan, phase_num):
    """Extract AC-IDs for a specific phase from master-plan"""
    ac_ids = []
    
    # Map phase number to phase key in master-plan
    phase_keys = {
        1: 'phase_1_foundation',
        1.5: 'phase_1_5_intelligent_discovery',
        2: 'phase_2_orchestration_core',
        3: 'phase_3_feature_orchestrators',
        4: 'phase_4_intelligence',
        4.5: 'phase_4_5_integration_tests',
        5: 'phase_5_cortex_cleanup_decommission'
    }
    
    phase_key = phase_keys.get(phase_num)
    if not phase_key or phase_key not in master_plan:
        return ac_ids
    
    phase_def = master_plan[phase_key]
    
    # Extract AC-IDs from components
    if isinstance(phase_def, dict):
        if 'components' in phase_def:
            components = phase_def['components']
            if isinstance(components, dict):
                for comp_name, comp_data in components.items():
                    if isinstance(comp_data, dict) and 'ac_ids' in comp_data:
                        ac_list = comp_data['ac_ids']
                        if isinstance(ac_list, list):
                            ac_ids.extend(ac_list)
    
    return sorted(list(set(ac_ids)))  # Remove duplicates, sort


def count_completed_ac_ids(ac_ids, progress_tracker):
    """Count how many AC-IDs are completed based on progress tracker"""
    if not progress_tracker:
        return 0
    
    completed = progress_tracker.get('verified_implemented', [])
    return len([ac for ac in ac_ids if ac in completed])


def get_phase_info(master_plan, phase_num):
    """Get phase metadata from master-plan"""
    phase_keys = {
        1: 'phase_1_foundation',
        1.5: 'phase_1_5_intelligent_discovery',
        2: 'phase_2_orchestration_core',
        3: 'phase_3_feature_orchestrators',
        4: 'phase_4_intelligence',
        4.5: 'phase_4_5_integration_tests',
        5: 'phase_5_cortex_cleanup_decommission'
    }
    
    phase_key = phase_keys.get(phase_num)
    if not phase_key or phase_key not in master_plan:
        return None
    
    return master_plan[phase_key]


def build_plan_viewer_data():
    """Build complete plan-viewer-data.json"""
    
    print("📖 Loading master-plan.yaml...")
    master_plan = load_master_plan()
    
    print("📋 Loading AC-INDEX.yaml...")
    ac_map, ac_index = load_ac_index()
    
    print("📊 Loading progress-tracker.json...")
    progress_tracker = load_progress_tracker()
    
    # Get all completed AC-IDs from progress-tracker
    all_completed_ac_ids = set()
    if progress_tracker:
        # Check various places where verified_implemented might be
        if 'current_phase' in progress_tracker and 'verified_implemented' in progress_tracker['current_phase']:
            all_completed_ac_ids.update(progress_tracker['current_phase']['verified_implemented'])
        
        # Check all phase_N sections
        for phase_key in ['phase_1', 'phase_2', 'phase_3', 'phase_4', 'phase_5', 'phase_1_5_sts', 'phase_2_orchestration', 'phase_3_features', 'phase_4_intelligence', 'completed_phases']:
            if phase_key in progress_tracker:
                phase_data = progress_tracker[phase_key]
                # Handle list of phases (completed_phases)
                if isinstance(phase_data, list):
                    for item in phase_data:
                        if isinstance(item, dict) and 'verified_implemented' in item:
                            all_completed_ac_ids.update(item['verified_implemented'])
                # Handle dict phases
                elif isinstance(phase_data, dict):
                    if 'verified_implemented' in phase_data:
                        all_completed_ac_ids.update(phase_data['verified_implemented'])
    
    # IMPORTANT: Use AC-INDEX count as total, not master-plan count
    # Master-plan only lists Phases 1-5 (59 ACs), but AC-INDEX declares 175 total ACs
    # This prevents the dashboard from showing >100% when we have ACs from STS, risk assessments, etc.
    total_ac_ids = ac_index.get('total_ac_count', len(ac_map))  # 175 from AC-INDEX
    completed_ac_ids = len(all_completed_ac_ids)  # 92 completed
    
    # Build phases array
    phases = []
    phase_numbers = [1, 2, 3, 4, 4.5, 5]
    
    for phase_num in phase_numbers:
        phase_info = get_phase_info(master_plan, phase_num)
        if not phase_info:
            continue
        
        ac_ids = extract_ac_ids_for_phase(master_plan, phase_num)
        
        # Get completed AC-IDs for this phase
        ac_completed_in_phase = len([ac for ac in ac_ids if ac in all_completed_ac_ids])
        
        # Get phase name
        phase_name = phase_info.get('name', f'Phase {phase_num}')
        
        # Build capability list with human-readable names
        capabilities = []
        for ac_id in ac_ids:
            if ac_id in ac_map:
                capabilities.append({
                    'ac_id': ac_id,
                    'name': ac_map[ac_id]['name'],
                    'status': 'completed' if ac_id in all_completed_ac_ids else 'planned'
                })
        
        # Calculate percentage
        total_in_phase = len(ac_ids)
        percentage = (ac_completed_in_phase / total_in_phase * 100) if total_in_phase > 0 else 0
        
        # Determine phase status
        if percentage == 100 and total_in_phase > 0:
            status = 'completed'
        elif percentage > 0:
            status = 'in_progress'
        else:
            status = 'planned'
        
        # Get verified_implemented list for this phase (actual completed AC-IDs)
        verified_in_phase = [ac for ac in ac_ids if ac in all_completed_ac_ids]
        
        phase_obj = {
            'id': int(phase_num) if phase_num != 4.5 else 4.5,
            'name': phase_name,
            'completion_percentage': int(percentage),
            'ac_ids_complete': ac_completed_in_phase,
            'ac_ids_total': total_in_phase,
            'status': status,
            'description': phase_info.get('description', ''),
            'verified_implemented': verified_in_phase,
            'capabilities': capabilities
        }
        
        phases.append(phase_obj)
    
    # Build metadata
    metadata = {
        'plan_id': master_plan.get('plan_metadata', {}).get('plan_id', 'CORTEX-6.0-SNOWBALL-MASTER'),
        'total_ac_ids': total_ac_ids,
        'completed_ac_ids': completed_ac_ids,
        'in_progress_ac_ids': 0,
        'version': master_plan.get('plan_metadata', {}).get('version', '1.3.0'),
        'updated': datetime.now(timezone.utc).isoformat(),
        'status': 'phases_1_to_5_defined_4.5_integration_tests_added'
    }
    
    result = {
        'plan_metadata': metadata,
        'phases': phases
    }
    
    return result


def save_plan_viewer_data(data):
    """Save generated data to plan-viewer-data.json"""
    output_path = Path('cortex-brain/cx6-plan/viewer/plan-viewer-data.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"✅ Saved to {output_path}")
    print(f"   Total AC-IDs: {data['plan_metadata']['total_ac_ids']}")
    print(f"   Completed: {data['plan_metadata']['completed_ac_ids']}")
    print(f"   Phases: {len(data['phases'])}")


if __name__ == '__main__':
    try:
        print("🔄 Regenerating plan-viewer-data.json from master-plan.yaml + AC-INDEX.yaml...\n")
        data = build_plan_viewer_data()
        save_plan_viewer_data(data)
        print("\n✅ Regeneration complete!")
        print("   Phase 4.5 Integration Tests now included in dashboard")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)
