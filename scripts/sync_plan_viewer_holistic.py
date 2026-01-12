#!/usr/bin/env python3
"""
Holistic plan-viewer sync from SSOT files
Reads from master-plan.yaml + AC-INDEX.yaml + progress-tracker.json
Generates plan-viewer-data.json with accurate Phase 5 completion
"""
import json
import yaml
from pathlib import Path
from datetime import datetime, timezone


def load_master_plan():
    """Load master-plan.yaml"""
    mp_path = Path('cortex-brain/cx6-plan/master-plan.yaml')
    if mp_path.exists():
        return yaml.safe_load(mp_path.read_text())
    return {}


def load_ac_index():
    """Load AC-INDEX.yaml"""
    ac_path = Path('cortex-brain/tier1/acceptance-criteria/AC-INDEX.yaml')
    if ac_path.exists():
        try:
            data = yaml.safe_load(ac_path.read_text())
            # Map AC-IDs to details
            ac_map = {}
            for ac in data.get('acceptance_criteria', []):
                ac_id = ac.get('id')
                if ac_id:
                    ac_map[ac_id] = {
                        'title': ac.get('title', ac_id),
                        'description': ac.get('description', ''),
                        'status': ac.get('status', 'planned'),
                        'pass_rate': ac.get('pass_rate', '0%')
                    }
            return ac_map
        except Exception as e:
            print(f'Warning: AC-INDEX error: {e}')
            return {}
    return {}


def load_progress_tracker():
    """Load progress-tracker.json"""
    pt_path = Path('cortex-brain/tier1/tracking/progress-tracker.json')
    if pt_path.exists():
        try:
            return json.loads(pt_path.read_text())
        except Exception as e:
            print(f'Warning: progress-tracker error: {e}')
            return {}
    return {}


def extract_phase_acs(master_plan, phase_num):
    """Extract AC-IDs for a given phase from master-plan"""
    phase_section = f'phase_{phase_num}_' if phase_num != 5 else 'phase_5_'
    
    # Find matching phase section
    for key, value in master_plan.items():
        if key.startswith(phase_section) and isinstance(value, dict):
            # Extract from ac_ids sections
            ac_ids = []
            
            # Check direct ac_ids field
            if 'ac_ids' in value:
                ac_ids_field = value['ac_ids']
                if isinstance(ac_ids_field, dict) and 'range' in ac_ids_field:
                    # Parse range like "AC-CLEAN-301 to AC-CLEAN-328"
                    range_str = ac_ids_field['range']
                    if ' to ' in range_str:
                        start, end = range_str.split(' to ')
                        start_num = int(start.split('-')[-1])
                        end_num = int(end.split('-')[-1])
                        prefix = start.rsplit('-', 1)[0]
                        ac_ids = [f'{prefix}-{i}' for i in range(start_num, end_num + 1)]
                elif isinstance(ac_ids_field, list):
                    ac_ids = ac_ids_field
            
            # Check components for nested ac_ids
            if not ac_ids and 'components' in value:
                for comp_name, comp_data in value['components'].items():
                    if isinstance(comp_data, dict) and 'ac_ids' in comp_data:
                        ac_ids.extend(comp_data['ac_ids'])
                        
            return ac_ids
    
    return []


def sync_holistic():
    """Generate plan-viewer-data.json holistically"""
    
    master_plan = load_master_plan()
    ac_index = load_ac_index()
    progress_tracker = load_progress_tracker()
    
    # Build plan viewer data
    data = {
        'plan_metadata': {
            'plan_id': 'CORTEX-6.0-SNOWBALL-MASTER',
            'version': '1.4.0',
            'updated': datetime.now(timezone.utc).isoformat(),
            'total_ac_ids': len(ac_index),
            'updated_by': 'sync_plan_viewer_holistic'
        },
        'phases': [],
        'phase_summary': {}
    }
    
    # Define phases in order
    phases = [
        (1, 'Foundation Enhancement'),
        (1.5, 'Intelligent Discovery'),
        (2, 'Orchestration Core'),
        (3, 'Feature Orchestrators'),
        (4, 'Intelligence Layer'),
        (4.5, 'Audit Integration'),
        (5, 'Cleanup & Decommission')
    ]
    
    total_acs = 0
    total_tests = 0
    total_passing = 0
    
    for phase_num, phase_name in phases:
        # Extract AC-IDs for this phase from master plan
        phase_acs = extract_phase_acs(master_plan, phase_num)
        
        if not phase_acs:
            continue
        
        # Count passing tests
        phase_tests = 0
        phase_passing = 0
        phase_status = 'planned'
        
        for ac_id in phase_acs:
            total_acs += 1
            if ac_id in ac_index:
                ac_info = ac_index[ac_id]
                # Parse test counts from pass_rate field like "10/10 (100%)"
                if ac_info['pass_rate']:
                    try:
                        # Extract numbers from format like "10/10 (100%)"
                        count_part = ac_info['pass_rate'].split(' ')[0]
                        if '/' in count_part:
                            passing, total = count_part.split('/')
                            phase_tests += int(total)
                            phase_passing += int(passing)
                    except:
                        pass
                
                # Update phase status based on AC status
                if ac_info['status'] == 'implemented':
                    phase_status = 'completed'
        
        total_tests += phase_tests
        total_passing += phase_passing
        
        # Calculate completion percentage
        completion_pct = 100 if phase_status == 'completed' else 0
        
        phase_data = {
            'id': phase_num,
            'name': phase_name,
            'ac_ids_total': len(phase_acs),
            'ac_ids': phase_acs,
            'tests_total': phase_tests,
            'tests_passing': phase_passing,
            'pass_rate': f'{phase_passing}/{phase_tests}' if phase_tests > 0 else '0/0',
            'completion_percentage': completion_pct,
            'status': phase_status
        }
        
        data['phases'].append(phase_data)
        data['phase_summary'][f'phase_{phase_num}'] = {
            'status': phase_status,
            'acs': len(phase_acs),
            'completion': f'{completion_pct}%'
        }
    
    # Update overall metadata
    data['plan_metadata']['total_tests'] = total_tests
    data['plan_metadata']['tests_passing'] = total_passing
    if total_tests > 0:
        data['plan_metadata']['overall_pass_rate'] = f'{total_passing}/{total_tests} ({100*total_passing//total_tests}%)'
    
    # Write to file
    output_path = Path('cortex-brain/cx6-plan/viewer/plan-viewer-data.json')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(data, indent=2))
    
    # Print summary
    print('\n✅ Synced plan-viewer-data.json (holistic)')
    print(f'   Total AC-IDs: {total_acs}')
    print(f'   Total Tests: {total_tests}')
    print(f'   Tests Passing: {total_passing}')
    if total_tests > 0:
        print(f'   Overall Pass Rate: {100*total_passing//total_tests}%')
    print(f'\nPhase Status:')
    for phase_data in data['phases']:
        status_emoji = '✅' if phase_data['status'] == 'completed' else '🔄'
        print(f"   {status_emoji} Phase {phase_data['id']}: {phase_data['ac_ids_total']}/{phase_data['ac_ids_total']} ({phase_data['completion_percentage']}%)")
    
    return True


if __name__ == '__main__':
    sync_holistic()
