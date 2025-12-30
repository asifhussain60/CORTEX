#!/usr/bin/env python3
"""
Template Cleanup Script - Move Root-Level Templates into templates: Section

This script fixes the response-templates-v4.yaml structure by moving all incorrectly
placed root-level templates into the proper templates: section.

Author: Asif Hussain
Date: December 4, 2025
"""

import yaml
from pathlib import Path


def fix_template_structure(templates_file: Path) -> dict:
    """
    Fix template structure by moving root-level templates into templates: section.
    
    Args:
        templates_file: Path to response-templates-v4.yaml
    
    Returns:
        Dict with fix statistics
    """
    print("🔧 Template Structure Fix - Starting...")
    print("="*70)
    
    # Load current structure
    with open(templates_file, 'r', encoding='utf-8') as f:
        data = yaml.safe_load(f)
    
    # Expected top-level keys
    expected_top_level = {
        'schema_version', 'last_updated', 'optimization', 
        'shared', 'base_templates', 'templates', 
        'routing', 'formatting'
    }
    
    # Find root-level templates
    root_level_templates = {}
    keys_to_move = []
    
    for key in list(data.keys()):
        if key not in expected_top_level and isinstance(data[key], dict):
            # Check if it looks like a template
            value_str = str(data[key])
            if 'trigger_phrases' in value_str or 'response_profile' in value_str:
                root_level_templates[key] = data[key]
                keys_to_move.append(key)
    
    print(f"Found {len(root_level_templates)} templates at root level")
    print()
    
    if not root_level_templates:
        print("✅ No templates to move - structure is correct")
        return {"moved": 0, "errors": 0}
    
    # Ensure templates section exists
    if 'templates' not in data:
        print("⚠️  Creating templates: section")
        data['templates'] = {}
    
    # Move templates into templates: section
    moved_count = 0
    error_count = 0
    
    for key in keys_to_move:
        try:
            # Add to templates section
            data['templates'][key] = root_level_templates[key]
            # Remove from root
            del data[key]
            moved_count += 1
            print(f"  ✅ Moved: {key}")
        except Exception as e:
            error_count += 1
            print(f"  ❌ Error moving {key}: {e}")
    
    print()
    print(f"Moved: {moved_count}")
    print(f"Errors: {error_count}")
    print()
    
    # Write back with proper formatting
    print("Writing fixed structure...")
    with open(templates_file, 'w', encoding='utf-8') as f:
        yaml.dump(data, f, default_flow_style=False, sort_keys=False, allow_unicode=True)
    
    print("✅ Template structure fixed")
    print("="*70)
    
    return {
        "moved": moved_count,
        "errors": error_count,
        "total_templates": len(data.get('templates', {}))
    }


if __name__ == "__main__":
    # Get CORTEX root (5 levels up: realignment/ -> modules/ -> operations/ -> src/ -> CORTEX/)
    cortex_root = Path(__file__).resolve().parent.parent.parent.parent.parent
    templates_file = cortex_root / "cortex-brain" / "response-templates-v4.yaml"
    
    if not templates_file.exists():
        print(f"❌ Error: {templates_file} not found")
        exit(1)
    
    # Create backup
    backup_file = templates_file.with_suffix('.yaml.backup-before-cleanup')
    print(f"📦 Creating backup: {backup_file.name}")
    import shutil
    shutil.copy2(templates_file, backup_file)
    
    # Fix structure
    result = fix_template_structure(templates_file)
    
    print()
    print("📊 Summary:")
    print(f"  Templates moved: {result['moved']}")
    print(f"  Errors: {result['errors']}")
    print(f"  Total templates in section: {result['total_templates']}")
    print()
    print("✅ Cleanup complete")
