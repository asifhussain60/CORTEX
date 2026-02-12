#!/usr/bin/env python3
"""Analyze CORTEX production readiness based on phase registry."""

import yaml
from pathlib import Path
from collections import defaultdict

def main():
    # Load index
    with open('cortex-registry/_cortex-master/index.yaml') as f:
        data = yaml.safe_load(f)
    
    phases = data.get('active_phases', [])
    
    # Categorize phases
    categories = {
        'P0_BLOCKERS_NOT_STARTED': [],
        'P0_BLOCKERS_IN_PROGRESS': [],
        'P0_COMPLETE': [],
        'P1_ACTIVE': [],
        'OTHER': []
    }
    
    for p in phases:
        priority = p.get('priority', 'P3')
        status = p.get('status', 'unknown')
        is_blocker = p.get('production_blocker', False)
        stages = p.get('stages_complete', '0/0')
        
        # Parse stage completion
        try:
            if isinstance(stages, str) and '/' in stages:
                done, total = stages.split('/')
                pct = (int(done) / int(total) * 100) if int(total) > 0 else 0
            else:
                pct = 0
        except:
            pct = 0
        
        phase_data = {
            'id': p['id'],
            'name': p['name'],
            'status': status,
            'priority': priority,
            'blocker': is_blocker,
            'stages': stages,
            'pct': pct,
            'duration': p.get('estimated_duration', 'N/A'),
            'tests': f"{p.get('tests_passing', 0)}/{p.get('test_target', '?')}"
        }
        
        # Categorize
        if priority == 'P0' and status == 'completed':
            categories['P0_COMPLETE'].append(phase_data)
        elif priority == 'P0' and (pct > 0 or status in ['active', 'in_progress']):
            categories['P0_BLOCKERS_IN_PROGRESS'].append(phase_data)
        elif priority == 'P0' and is_blocker:
            categories['P0_BLOCKERS_NOT_STARTED'].append(phase_data)
        elif priority == 'P1' and status in ['active', 'in_progress']:
            categories['P1_ACTIVE'].append(phase_data)
        else:
            categories['OTHER'].append(phase_data)
    
    # Print report
    print('=' * 80)
    print('CORTEX PRODUCTION READINESS REPORT')
    print('=' * 80)
    print()
    
    print('🔴 P0 PRODUCTION BLOCKERS - NOT STARTED')
    print('-' * 80)
    if not categories['P0_BLOCKERS_NOT_STARTED']:
        print('  ✅ None')
    for p in categories['P0_BLOCKERS_NOT_STARTED']:
        print(f"  {p['id']}: {p['name'][:50]}")
        print(f"    Duration: {p['duration']} | Blocker: {p['blocker']}")
    print()
    
    print('🟠 P0 BLOCKERS - IN PROGRESS')
    print('-' * 80)
    if not categories['P0_BLOCKERS_IN_PROGRESS']:
        print('  ✅ None')
    for p in categories['P0_BLOCKERS_IN_PROGRESS']:
        print(f"  {p['id']}: {p['name'][:50]}")
        print(f"    Status: {p['status']} | Stages: {p['stages']} ({p['pct']:.0f}%) | Tests: {p['tests']}")
    print()
    
    print('✅ P0 COMPLETE')
    print('-' * 80)
    print(f"  Total: {len(categories['P0_COMPLETE'])} phases")
    for p in categories['P0_COMPLETE'][:8]:
        print(f"  - {p['id']}: {p['name'][:55]}")
    print()
    
    print('🟡 P1 ACTIVE WORK')
    print('-' * 80)
    if not categories['P1_ACTIVE']:
        print('  None')
    for p in categories['P1_ACTIVE']:
        print(f"  {p['id']}: {p['name'][:50]}")
        print(f"    Status: {p['status']} | Stages: {p['stages']} | Tests: {p['tests']}")
    print()
    
    # Summary
    total_p0 = len(categories['P0_BLOCKERS_NOT_STARTED']) + \
               len(categories['P0_BLOCKERS_IN_PROGRESS']) + \
               len(categories['P0_COMPLETE'])
    p0_done = len(categories['P0_COMPLETE'])
    
    print('=' * 80)
    print('SUMMARY')
    print('=' * 80)
    print(f"P0 Progress: {p0_done}/{total_p0} complete ({p0_done/total_p0*100:.0f}%)")
    print(f"P0 Blockers Remaining: {len(categories['P0_BLOCKERS_NOT_STARTED']) + len(categories['P0_BLOCKERS_IN_PROGRESS'])}")
    print(f"P1 Active: {len(categories['P1_ACTIVE'])}")
    print()
    
    if len(categories['P0_BLOCKERS_NOT_STARTED']) > 0 or len(categories['P0_BLOCKERS_IN_PROGRESS']) > 0:
        print('⚠️  PRODUCTION STATUS: BLOCKED')
    else:
        print('✅ PRODUCTION STATUS: READY')

if __name__ == '__main__':
    main()
