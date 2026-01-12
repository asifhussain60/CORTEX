#!/usr/bin/env python3
"""
Sync plan-viewer-data.json from progress-tracker.json
Run after any progress updates to keep dashboard current
Translates AC-IDs to human-readable capability names
"""
import json
import yaml
from pathlib import Path
from datetime import datetime, timezone


def load_ac_index():
    """Load AC-INDEX.yaml to get AC-ID to name mappings"""
    ac_index_path = Path('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml')
    if not ac_index_path.exists():
        return {}
    
    try:
        with open(ac_index_path, 'r') as f:
            data = yaml.safe_load(f)
        
        ac_map = {}
        
        # Process foundation section (has all AC-IDs organized by category)
        foundation = data.get('foundation', {})
        for category_name, ac_list in foundation.items():
            if not isinstance(ac_list, list):
                continue
            for ac in ac_list:
                if not isinstance(ac, dict):
                    continue
                ac_id = ac.get('id')
                name = ac.get('name')
                desc = ac.get('description', '')
                if ac_id and name:
                    ac_map[ac_id] = {
                        'name': name,
                        'description': desc
                    }
        
        return ac_map
    except Exception as e:
        print(f'⚠️  Warning: Could not load AC-INDEX: {e}')
        import traceback
        traceback.print_exc()
        return {}


def translate_ac_list(ac_ids, ac_map):
    """Convert list of AC-IDs to human-readable capability list"""
    capabilities = []
    for ac_id in ac_ids:
        if ac_id in ac_map:
            capabilities.append({
                'id': ac_id,  # Keep for internal tracking
                'name': ac_map[ac_id]['name'],
                'description': ac_map[ac_id]['description']
            })
        else:
            # Fallback if AC not found
            capabilities.append({
                'id': ac_id,
                'name': ac_id,
                'description': ''
            })
    return capabilities


def sync_plan_viewer_data():
    """Generate plan-viewer-data.json from progress tracker"""
    
    # Load AC-ID mappings
    ac_map = load_ac_index()
    
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
        
        # Translate AC-IDs to capabilities
        verified_impl = p1.get('verified_implemented', [])
        capabilities = translate_ac_list(verified_impl, ac_map)
        
        data['phases'].append({
            'id': 1,
            'name': 'Foundation Enhancement',
            'completion_percentage': p1.get('completion_percentage', 0),
            'ac_ids_complete': completed,
            'ac_ids_total': p1.get('total_ac_count', 34),
            'status': p1.get('status', 'in_progress'),
            'description': 'Build core infrastructure (Audit, Governance, State, Lifecycle, Evidence, Security)',
            'verified_implemented': verified_impl,  # Keep for internal tracking
            'capabilities': capabilities  # Human-readable list
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
    
    # Add Phases 2-5 from completed_phases array
    for phase_data in tracker.get('completed_phases', []):
        phase_num = phase_data.get('number')
        completed = phase_data.get('completed_count', 0)
        total_completed += completed
        
        verified_impl = phase_data.get('completed_ac_ids', [])
        capabilities = translate_ac_list(verified_impl, ac_map)
        
        # Determine status
        pct = phase_data.get('completion_percentage', 0)
        if pct == 100:
            status = 'completed'
        elif pct > 0:
            status = 'in_progress'
        else:
            status = 'planned'
        
        data['phases'].append({
            'id': phase_num,
            'name': phase_data.get('name', f'Phase {phase_num}'),
            'completion_percentage': pct,
            'ac_ids_complete': completed,
            'ac_ids_total': phase_data.get('total_ac_count', 0),
            'status': status,
            'description': phase_data.get('description', ''),
            'verified_implemented': verified_impl,
            'capabilities': capabilities
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
