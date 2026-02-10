#!/usr/bin/env python3
"""Update index.yaml file paths for archived phases."""

import yaml
from pathlib import Path

def main():
    index_path = Path("cortex-registry/_cortex-master/index.yaml")
    
    # Load existing index
    with open(index_path) as f:
        data = yaml.safe_load(f)
    
    # Update file paths for completed phases
    archived_files = {
        'phase-45': 'phases/completed/2026/phase-45-enhanced-planning-system.yaml',
        'phase-46': 'phases/completed/2026/phase-46-infrastructure-discovery.yaml',
        'phase-47': 'phases/completed/2026/phase-47-company-cortex-separation.yaml',
        'phase-37': 'phases/completed/2026/phase-37-role-adaptive-personas.yaml',
        'phase-51': 'phases/completed/2026/phase-51-mcp-first-enforcement.yaml',
        'phase-55': 'phases/completed/2026/phase-55-dotnet-enterprise-lens-enhancement.yaml',
    }
    
    updated_count = 0
    for phase in data['active_phases']:
        phase_id = phase['id']
        if phase_id in archived_files:
            old_path = phase.get('file', '')
            new_path = archived_files[phase_id]
            phase['file'] = new_path
            print(f"✅ Updated {phase_id}: {new_path}")
            updated_count += 1
    
    # Write updated index
    with open(index_path, 'w') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print(f"\n✅ Index.yaml updated: {updated_count} file paths corrected")

if __name__ == '__main__':
    main()
