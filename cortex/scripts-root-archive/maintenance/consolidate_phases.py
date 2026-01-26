#!/usr/bin/env python3
"""
Consolidate all phase YAML files into cortex-master.yaml phases section.

This script:
1. Reads all phase-XX.yaml files from _workspaces/roadmap/phases/
2. Extracts AC-ID specs, testing, success_criteria
3. Generates unified phases: section for cortex-master.yaml
4. Validates consolidated data for consistency
5. Archives original phase files
"""

import yaml
import json
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime
import shutil


def load_phase_yaml(phase_file: Path) -> Dict[str, Any]:
    """Load a single phase YAML file."""
    with open(phase_file, 'r') as f:
        return yaml.safe_load(f)


def consolidate_all_phases() -> Dict[str, Any]:
    """Read all phase files and consolidate into single phases dict."""
    
    phases_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/phases")
    phases_data = {}
    
    # Get all phase YAML files sorted
    phase_files = sorted(phases_dir.glob("phase-*.yaml"))
    
    print(f"📂 Found {len(phase_files)} phase files")
    
    for phase_file in phase_files:
        print(f"\n🔍 Processing: {phase_file.name}")
        
        try:
            phase = load_phase_yaml(phase_file)
            
            # Extract phase name (PHASE-01, PHASE-REMEDIATION-07, etc.)
            phase_name = phase.get('metadata', {}).get('phase_id') or \
                         phase.get('phase_id') or \
                         phase_file.stem.upper().replace('-', '_')
            
            print(f"   ✓ Phase ID: {phase_name}")
            print(f"   ✓ AC-IDs: {len(phase.get('ac_ids', {}))}")
            
            # Store consolidated phase data
            phases_data[phase_name] = {
                'title': phase.get('metadata', {}).get('title') or phase.get('title', phase_name),
                'description': phase.get('metadata', {}).get('description') or phase.get('description', ''),
                'status': phase.get('metadata', {}).get('status') or phase.get('status', 'NOT_STARTED'),
                'locked': phase.get('metadata', {}).get('locked', False),
                'ac_ids': phase.get('ac_ids', {}),
                'testing': phase.get('testing', {}),
                'success_criteria': phase.get('success_criteria', []),
                'governance_rules': phase.get('governance_rules', []),
                'dependencies': phase.get('dependencies', []),
                'source_file': phase_file.name,
                'consolidated_date': datetime.now().isoformat(),
            }
            
        except Exception as e:
            print(f"   ❌ ERROR: {e}")
            continue
    
    return phases_data


def generate_yaml_snippet(phases_data: Dict[str, Any]) -> str:
    """Generate YAML snippet for cortex-master.yaml phases section."""
    
    yaml_lines = [
        "  # =============================================================================",
        "  # PHASES SECTION - Consolidated from individual phase YAML files",
        "  # Date Consolidated: " + datetime.now().isoformat(),
        "  # This section contains ALL phase specifications (replaces phase-XX.yaml files)",
        "  # =============================================================================",
        "  phases:",
        ""
    ]
    
    for phase_id, phase_spec in sorted(phases_data.items()):
        yaml_lines.append(f"    {phase_id}:")
        yaml_lines.append(f"      title: \"{phase_spec['title']}\"")
        yaml_lines.append(f"      description: \"{phase_spec['description'][:100]}...\"" if len(phase_spec['description']) > 100 else f"      description: \"{phase_spec['description']}\"")
        yaml_lines.append(f"      status: {phase_spec['status']}")
        yaml_lines.append(f"      locked: {str(phase_spec['locked']).lower()}")
        yaml_lines.append(f"      source_file: {phase_spec['source_file']}")
        
        # AC-IDs
        yaml_lines.append(f"      ac_ids:")
        for ac_id, ac_spec in phase_spec['ac_ids'].items():
            yaml_lines.append(f"        {ac_id}:")
            if isinstance(ac_spec, dict):
                for key, value in ac_spec.items():
                    if key != 'description' and key != 'testing':
                        formatted_value = f'"{value}"' if isinstance(value, str) and ':' in value else value
                        yaml_lines.append(f"          {key}: {formatted_value}")
            else:
                yaml_lines.append(f"          title: \"{ac_spec}\"")
        
        yaml_lines.append("")
    
    return "\n".join(yaml_lines)


def validate_consolidation(phases_data: Dict[str, Any]) -> Dict[str, Any]:
    """Validate consolidated data for consistency."""
    
    report = {
        'total_phases': len(phases_data),
        'total_ac_ids': 0,
        'total_tests': 0,
        'phases_completed': 0,
        'phases_locked': 0,
        'errors': [],
        'warnings': [],
    }
    
    for phase_id, phase_spec in phases_data.items():
        # Count AC-IDs
        ac_count = len(phase_spec.get('ac_ids', {}))
        report['total_ac_ids'] += ac_count
        
        # Count tests
        testing = phase_spec.get('testing', {})
        test_count = testing.get('unit_tests_expected', 0) + testing.get('integration_tests_expected', 0)
        report['total_tests'] += test_count
        
        # Check completion status
        if phase_spec['status'] == 'COMPLETED':
            report['phases_completed'] += 1
        
        if phase_spec['locked']:
            report['phases_locked'] += 1
        
        # Validation checks
        if phase_spec['locked'] and phase_spec['status'] != 'COMPLETED':
            report['warnings'].append(f"{phase_id}: Locked but not COMPLETED")
        
        if ac_count == 0:
            report['errors'].append(f"{phase_id}: No AC-IDs found")
    
    return report


def archive_phase_files():
    """Move original phase files to archives."""
    
    phases_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/phases")
    archives_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/_workspaces/roadmap/_archives/phase-yamls-v1")
    
    # Create archives directory if not exists
    archives_dir.mkdir(parents=True, exist_ok=True)
    
    phase_files = sorted(phases_dir.glob("phase-*.yaml"))
    
    print(f"\n📦 Archiving {len(phase_files)} phase files to _archives/phase-yamls-v1/")
    
    for phase_file in phase_files:
        try:
            dest = archives_dir / phase_file.name
            shutil.copy2(phase_file, dest)
            print(f"   ✓ {phase_file.name} → archived")
        except Exception as e:
            print(f"   ❌ Failed to archive {phase_file.name}: {e}")
    
    print(f"\n📍 Archive location: {archives_dir}")


def main():
    """Main consolidation workflow."""
    
    print("=" * 80)
    print("PHASE CONSOLIDATION SCRIPT")
    print("=" * 80)
    
    # Step 1: Consolidate
    print("\n[1/4] CONSOLIDATING phase files...")
    phases_data = consolidate_all_phases()
    
    # Step 2: Validate
    print("\n[2/4] VALIDATING consolidated data...")
    validation_report = validate_consolidation(phases_data)
    
    print(f"\n✅ Validation Report:")
    print(f"   Total Phases: {validation_report['total_phases']}")
    print(f"   Total AC-IDs: {validation_report['total_ac_ids']}")
    print(f"   Total Tests: {validation_report['total_tests']}")
    print(f"   Phases Completed: {validation_report['phases_completed']}")
    print(f"   Phases Locked: {validation_report['phases_locked']}")
    
    if validation_report['errors']:
        print(f"\n❌ ERRORS ({len(validation_report['errors'])}):")
        for error in validation_report['errors']:
            print(f"   - {error}")
    
    if validation_report['warnings']:
        print(f"\n⚠️ WARNINGS ({len(validation_report['warnings'])}):")
        for warning in validation_report['warnings']:
            print(f"   - {warning}")
    
    # Step 3: Generate YAML
    print("\n[3/4] GENERATING YAML snippet...")
    yaml_snippet = generate_yaml_snippet(phases_data)
    
    # Save snippet for review to reports/analysis/ with CORE-028 compliant naming
    snippet_file = Path("/Users/asifhussain/PROJECTS/CORTEX/reports/analysis/phases-consolidated-snippet.yaml")
    snippet_file.parent.mkdir(parents=True, exist_ok=True)
    with open(snippet_file, 'w') as f:
        f.write(yaml_snippet)
    
    print(f"   ✓ Saved to: {snippet_file}")
    print(f"   ✓ Size: {len(yaml_snippet)} bytes")
    
    # Step 4: Archive original files
    print("\n[4/4] ARCHIVING original phase files...")
    archive_phase_files()
    
    print("\n" + "=" * 80)
    print("✅ CONSOLIDATION COMPLETE")
    print("=" * 80)
    print("\nNext steps:")
    print("1. Review phases-consolidated-snippet.yaml")
    print("2. Append to cortex-master.yaml after final_status section")
    print("3. Run: python3 scripts/validate_phase_sync.py")
    print("4. Commit changes")
    print("\nOptional (cleanup):")
    print("5. Delete _workspaces/roadmap/phases/*.yaml (already archived)")
    print("=" * 80)


if __name__ == "__main__":
    main()
