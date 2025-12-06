#!/usr/bin/env python3
"""
Response Format v3.0 Template Migration Script

Migrates distributed templates from v2.0 to v3.0 format:
- understanding_content → understanding_scope_content
- challenge_content → approach_considerations_content
- request_echo_content → impact_changes_content

Preserves template structure and functionality.
"""

import os
import re
import yaml
from pathlib import Path
from typing import Dict, List, Any

# Section name mappings (v2.0 → v3.0)
SECTION_MAPPINGS = {
    'understanding_content': 'understanding_scope_content',
    'challenge_content': 'approach_considerations_content',
    'request_echo_content': 'impact_changes_content',
    # response_content and next_steps_content stay the same
}

# Content transformation for common phrases
CONTENT_TRANSFORMATIONS = {
    'No Challenge': 'No significant challenges',
    'Challenge:': 'Approach:',
    'My Understanding Of Your Request': 'Understanding & Scope',
    'Your Request:': 'Impact & Changes:',
}


def migrate_template_file(file_path: Path) -> Dict[str, Any]:
    """Migrate a single template file to v3.0 format."""
    print(f"  Processing: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    original_content = content
    changes_made = []
    
    # Replace section names in YAML structure
    for old_name, new_name in SECTION_MAPPINGS.items():
        if old_name in content:
            content = content.replace(old_name, new_name)
            changes_made.append(f"Renamed {old_name} → {new_name}")
    
    # Transform content phrases
    for old_phrase, new_phrase in CONTENT_TRANSFORMATIONS.items():
        if old_phrase in content:
            content = content.replace(old_phrase, new_phrase)
            changes_made.append(f"Updated phrase: {old_phrase} → {new_phrase}")
    
    if content != original_content:
        # Write updated content
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return {
            'file': str(file_path),
            'status': 'updated',
            'changes': changes_made
        }
    else:
        return {
            'file': str(file_path),
            'status': 'unchanged',
            'changes': []
        }


def find_template_files(base_dir: Path) -> List[Path]:
    """Find all YAML template files in distributed structure."""
    template_files = []
    
    # Search in known distributed template directories
    search_dirs = [
        base_dir / 'core',
        base_dir / 'operations',
        base_dir / 'orchestrators',
        base_dir / 'specialized',
    ]
    
    for search_dir in search_dirs:
        if search_dir.exists():
            template_files.extend(search_dir.rglob('*.yaml'))
    
    return sorted(template_files)


def main():
    """Execute template migration."""
    print("🔄 Response Format v3.0 Template Migration")
    print("=" * 60)
    
    # Get project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    templates_dir = project_root / 'cortex-brain' / 'response-templates'
    
    if not templates_dir.exists():
        print(f"❌ Templates directory not found: {templates_dir}")
        return 1
    
    print(f"\n📁 Scanning: {templates_dir}")
    
    # Find all template files
    template_files = find_template_files(templates_dir)
    print(f"\n✅ Found {len(template_files)} template files")
    
    # Migrate each file
    results = []
    print("\n🔄 Migrating templates...")
    for template_file in template_files:
        result = migrate_template_file(template_file)
        results.append(result)
    
    # Summary
    updated_count = sum(1 for r in results if r['status'] == 'updated')
    unchanged_count = sum(1 for r in results if r['status'] == 'unchanged')
    
    print("\n" + "=" * 60)
    print("📊 Migration Summary")
    print("=" * 60)
    print(f"✅ Updated: {updated_count} files")
    print(f"⚪ Unchanged: {unchanged_count} files")
    print(f"📝 Total: {len(results)} files")
    
    # Detailed changes
    if updated_count > 0:
        print("\n📋 Updated Files:")
        for result in results:
            if result['status'] == 'updated':
                print(f"\n  {result['file']}")
                for change in result['changes']:
                    print(f"    - {change}")
    
    print("\n✅ Migration Complete!")
    return 0


if __name__ == '__main__':
    exit(main())
