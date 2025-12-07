"""
Response Template Migration Script
Migrates rigid 5-part format to flexible format
Version: 1.0
Author: Asif Hussain
"""

import re
from pathlib import Path
from typing import Tuple
from datetime import datetime


class TemplateMigrator:
    """Migrates response templates from rigid to flexible format"""
    
    # Patterns to detect and remove
    RIGID_SECTION_PATTERNS = [
        r'## 🎯 My Understanding Of Your Request\s*\n',
        r'## ⚡ Approach & Considerations\s*\n',
        r'## 💬 Response\s*\n',
        r'## 📊 Impact & Changes\s*\n',
        r'## 🔍 Next Steps\s*\n'
    ]
    
    # Pattern to preserve mandatory header
    HEADER_PATTERN = r'## 🧠 CORTEX .+?\n\*\*Author:\*\* Asif Hussain.*?\n\n---\n'
    
    def __init__(self, template_file: Path):
        self.template_file = template_file
        self.backup_file = None
        self.changes_made = []
        
    def backup_original(self) -> Path:
        """Create timestamped backup"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_dir = self.template_file.parent / 'backups'
        backup_dir.mkdir(exist_ok=True)
        
        self.backup_file = backup_dir / f'response-templates-backup-{timestamp}.yaml'
        with open(self.template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        with open(self.backup_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✅ Backup created: {self.backup_file}")
        return self.backup_file
    
    def detect_rigid_format(self, content: str) -> list[str]:
        """Find all rigid section headers"""
        matches = []
        for pattern in self.RIGID_SECTION_PATTERNS:
            found = re.findall(pattern, content)
            matches.extend(found)
        return matches
    
    def migrate_template_content(self, content: str, template_name: str) -> Tuple[str, int]:
        """Migrate a single template content block"""
        original = content
        changes = 0
        
        # Remove rigid section headers but preserve content
        for pattern in self.RIGID_SECTION_PATTERNS:
            if re.search(pattern, content):
                content = re.sub(pattern, '', content)
                changes += 1
        
        if changes > 0:
            self.changes_made.append({
                'template': template_name,
                'changes': changes,
                'original_length': len(original),
                'new_length': len(content)
            })
        
        return content, changes
    
    def process_yaml_templates(self) -> Tuple[str, int]:
        """Process entire YAML file and migrate all templates using string operations"""
        with open(self.template_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        original_content = content
        total_changes = 0
        
        # Track which templates are being modified
        template_context = None
        for line_num, line in enumerate(content.split('\n'), 1):
            # Detect template name lines (e.g., "  onboarding:")
            if re.match(r'^  \w[\w-]*:\s*$', line):
                template_context = line.strip().rstrip(':')
        
        # Apply all regex replacements
        for pattern in self.RIGID_SECTION_PATTERNS:
            matches = re.findall(pattern, content)
            if matches:
                content = re.sub(pattern, '', content)
                total_changes += len(matches)
                print(f"  - Removed {len(matches)}x: {pattern.strip()}")
        
        # Track what changed
        if content != original_content:
            print(f"\n✅ Total rigid sections removed: {total_changes}")
        
        return content, total_changes
    
    def write_migrated_yaml(self, content: str):
        """Write migrated content back to file"""
        output_path = str(self.template_file).replace('\\', '/')
        with open(output_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        
        print(f"✅ Migrated templates written to: {self.template_file}")
    
    def generate_report(self, total_changes: int):
        """Generate migration report"""
        print("\n" + "="*70)
        print("🧠 CORTEX Template Migration Report")
        print("="*70)
        print(f"\n📁 File: {self.template_file}")
        print(f"🔄 Total Changes: {total_changes}")
        print(f"📋 Templates Modified: {len(self.changes_made)}")
        
        if self.changes_made:
            print("\n📊 Modified Templates:")
            for change in self.changes_made:
                print(f"  - {change['template']}: {change['changes']} sections removed")
                print(f"    Original: {change['original_length']} chars → New: {change['new_length']} chars")
        
        print(f"\n💾 Backup: {self.backup_file}")
        print("\n✅ Migration Complete!")
        print("="*70)


def main():
    # Locate template file
    template_file = Path(__file__).parent.parent / 'cortex-brain' / 'response-templates.yaml'
    
    if not template_file.exists():
        print(f"❌ Template file not found: {template_file}")
        return 1
    
    print("🧠 CORTEX Response Template Migrator")
    print(f"📁 Target: {template_file}")
    print("\n🔍 Analyzing templates...")
    
    migrator = TemplateMigrator(template_file)
    
    # Create backup
    migrator.backup_original()
    
    # Process templates
    print("\n🔄 Migrating templates from rigid to flexible format...")
    migrated_data, total_changes = migrator.process_yaml_templates()
    
    # Write back
    migrator.write_migrated_yaml(migrated_data)
    
    # Report
    migrator.generate_report(total_changes)
    
    return 0


if __name__ == '__main__':
    exit(main())
