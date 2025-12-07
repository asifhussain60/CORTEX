"""
Focused Template Migration - Only remove rigid headers from template content
"""

import re
from pathlib import Path
from datetime import datetime


def migrate_templates():
    """Remove rigid section headers only from within template content blocks"""
    
    template_file = Path('cortex-brain/response-templates.yaml')
    
    # Read file
    with open(template_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    # Patterns to remove (these appear in content blocks)
    patterns_to_remove = [
        '      ## 🎯 My Understanding Of Your Request\n',
        '      ## ⚡ Approach & Considerations\n',
        '      ## 💬 Response\n',
        '      ## 📊 Impact & Changes\n',
        '      ## 🔍 Next Steps\n'
    ]
    
    # Track changes
    removed_count = 0
    new_lines = []
    in_templates_section = False
    
    for i, line in enumerate(lines):
        # Track if we're in templates: section
        if line.strip() == 'templates:':
            in_templates_section = True
        
        # Check if line should be removed
        should_remove = False
        if in_templates_section:
            for pattern in patterns_to_remove:
                if line == pattern:
                    should_remove = True
                    removed_count += 1
                    break
        
        if not should_remove:
            new_lines.append(line)
    
    # Backup
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = template_file.parent / 'backups' / f'response-templates-focused-backup-{timestamp}.yaml'
    backup_file.parent.mkdir(exist_ok=True)
    
    with open(backup_file, 'w', encoding='utf-8') as f:
        f.writelines(lines)
    
    print(f"\n✅ Backup: {backup_file}")
    
    # Write migrated version
    with open(template_file, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    
    print(f"✅ Removed {removed_count} rigid section headers")
    print(f"✅ File written: {template_file}")
    
    # Verify
    with open(template_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    remaining = sum(1 for pattern in patterns_to_remove if pattern.strip() in content)
    print(f"\n🔍 Verification: {remaining} rigid headers remaining (should be 0)")
    
    return removed_count


if __name__ == '__main__':
    count = migrate_templates()
    print(f"\n✅ Migration complete - {count} headers removed")
