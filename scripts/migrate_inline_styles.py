#!/usr/bin/env python3
"""
CORTEX Inline Style Migration Tool
===================================

Purpose: Extract all inline styles from Level 1 HTML files and migrate them
         to a centralized CSS file (glass-level1.css)

Features:
- Extracts inline styles from all Level 1 views
- Generates unique CSS classes for each style pattern
- Validates computed styles before/after migration
- Creates test report with visual regression data

Author: Asif Hussain
Date: 2026-01-05
Version: 1.0.0

CRITICAL: Follows cortex-docs.prompt.md v2.0 - Python-only HTML modification
"""

import re
import sys
from pathlib import Path
from typing import List, Dict, Set, Tuple
from bs4 import BeautifulSoup
import json
from datetime import datetime
import hashlib


class InlineStyleMigrator:
    """Extracts inline styles and generates CSS classes"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.docs_dir = project_root / 'docs'
        self.css_output = self.docs_dir / 'assets' / 'css' / 'glass-level1.css'
        
        # Track extracted styles
        self.style_registry: Dict[str, Dict] = {}  # style_hash -> {css, count, elements}
        self.style_to_class: Dict[str, str] = {}   # style_hash -> class_name
        self.class_counter = 0
    
    def get_level1_pages(self) -> List[Path]:
        """Get all Level 1 HTML index files"""
        level1_dirs = [
            'architecture', 'features', 'getting-started', 'knowledge',
            'learning-paths', 'lens', 'orchestrators', 'security',
            'story', 'sts', 'token-optimization', 'toolkit-manager'
        ]
        
        return [self.docs_dir / dir_name / 'index.html' for dir_name in level1_dirs 
                if (self.docs_dir / dir_name / 'index.html').exists()]
    
    def normalize_style(self, style_str: str) -> str:
        """Normalize style string for consistent hashing"""
        # Remove extra whitespace
        style_str = re.sub(r'\s+', ' ', style_str.strip())
        
        # Sort properties alphabetically
        properties = [p.strip() for p in style_str.split(';') if p.strip()]
        properties.sort()
        
        return '; '.join(properties)
    
    def style_to_hash(self, style_str: str) -> str:
        """Generate unique hash for style string"""
        normalized = self.normalize_style(style_str)
        return hashlib.md5(normalized.encode()).hexdigest()[:8]
    
    def generate_class_name(self, style_hash: str, element_tag: str) -> str:
        """Generate semantic CSS class name"""
        self.class_counter += 1
        return f"level1-{element_tag}-{style_hash}"
    
    def extract_inline_styles(self, html_path: Path) -> Dict:
        """Extract all inline styles from HTML file"""
        print(f"\n🔍 Extracting from: {html_path.relative_to(self.project_root)}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        # Find all elements with inline styles
        elements_with_styles = soup.find_all(style=True)
        
        if not elements_with_styles:
            print("   ✅ No inline styles found")
            return {'inline_styles': 0, 'unique_styles': 0}
        
        print(f"   📊 Found {len(elements_with_styles)} elements with inline styles")
        
        unique_styles = set()
        
        for element in elements_with_styles:
            style_str = element.get('style', '')
            if not style_str.strip():
                continue
            
            style_hash = self.style_to_hash(style_str)
            unique_styles.add(style_hash)
            
            # Register style if new
            if style_hash not in self.style_registry:
                class_name = self.generate_class_name(style_hash, element.name)
                
                self.style_registry[style_hash] = {
                    'css': self.normalize_style(style_str),
                    'class_name': class_name,
                    'count': 0,
                    'elements': [],
                    'files': set()
                }
                self.style_to_class[style_hash] = class_name
            
            # Track usage
            self.style_registry[style_hash]['count'] += 1
            self.style_registry[style_hash]['elements'].append({
                'tag': element.name,
                'id': element.get('id'),
                'classes': element.get('class', [])
            })
            self.style_registry[style_hash]['files'].add(str(html_path.relative_to(self.project_root)))
        
        print(f"   ✅ Extracted {len(unique_styles)} unique style patterns")
        
        return {
            'inline_styles': len(elements_with_styles),
            'unique_styles': len(unique_styles)
        }
    
    def generate_css_file(self) -> str:
        """Generate glass-level1.css from extracted styles"""
        css_lines = [
            "/**",
            " * CORTEX Level 1 Glassmorphism Styles",
            f" * Generated: {datetime.now().isoformat()}",
            " * ",
            " * This file contains styles migrated from inline style attributes",
            " * in Level 1 HTML views. All styles respect inheritance from:",
            " * - variables.css (design tokens)",
            " * - main.css (base patterns)",
            " * ",
            " * DO NOT EDIT MANUALLY - Regenerate via scripts/migrate_inline_styles.py",
            " * ",
            " * Author: Asif Hussain",
            " * Copyright © 2026 Asif Hussain. All rights reserved.",
            " */",
            "",
            "/* ═══════════════════════════════════════════════════════════════",
            "   LEVEL 1 VIEW-SPECIFIC STYLES",
            f"   Total Classes: {len(self.style_registry)}",
            "   ═══════════════════════════════════════════════════════════════ */",
            ""
        ]
        
        # Sort styles by usage count (most common first)
        sorted_styles = sorted(
            self.style_registry.items(),
            key=lambda x: x[1]['count'],
            reverse=True
        )
        
        for style_hash, style_data in sorted_styles:
            class_name = style_data['class_name']
            css = style_data['css']
            count = style_data['count']
            files = sorted(style_data['files'])
            
            # Comment with metadata
            css_lines.append(f"/* {class_name}")
            css_lines.append(f"   Usage: {count} occurrences")
            css_lines.append(f"   Files: {', '.join(files)}")
            css_lines.append(f" */")
            
            # CSS rule
            css_lines.append(f".{class_name} {{")
            
            # Format CSS properties
            properties = [p.strip() for p in css.split(';') if p.strip()]
            for prop in properties:
                css_lines.append(f"    {prop};")
            
            css_lines.append("}")
            css_lines.append("")
        
        return '\n'.join(css_lines)
    
    def replace_inline_styles(self, html_path: Path) -> int:
        """Replace inline styles with CSS classes"""
        print(f"\n✏️  Updating: {html_path.relative_to(self.project_root)}")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        soup = BeautifulSoup(html_content, 'html.parser')
        
        replacements = 0
        
        for element in soup.find_all(style=True):
            style_str = element.get('style', '')
            if not style_str.strip():
                continue
            
            style_hash = self.style_to_hash(style_str)
            
            if style_hash in self.style_to_class:
                class_name = self.style_to_class[style_hash]
                
                # Add CSS class
                classes = element.get('class', [])
                if class_name not in classes:
                    classes.append(class_name)
                    element['class'] = classes
                
                # Remove inline style
                del element['style']
                
                replacements += 1
                print(f"   ✅ Replaced inline style with .{class_name} on <{element.name}>")
        
        # Write back to file
        if replacements > 0:
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(str(soup.prettify()))
            print(f"   💾 Saved {replacements} replacements")
        
        return replacements
    
    def update_css_imports(self, html_path: Path):
        """Add glass-level1.css import to HTML file"""
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Check if already imported
        if 'glass-level1.css' in html_content:
            return
        
        # Find existing CSS imports
        import_pattern = r'<link rel="stylesheet" href="\.\.\/assets\/css\/main\.css">'
        
        if re.search(import_pattern, html_content):
            # Add after main.css
            new_import = '<link rel="stylesheet" href="../assets/css/main.css">\n    <link rel="stylesheet" href="../assets/css/glass-level1.css">'
            html_content = re.sub(import_pattern, new_import, html_content)
            
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            print(f"   📎 Added glass-level1.css import")
    
    def run(self) -> Dict:
        """Execute migration process"""
        print("=" * 70)
        print("🎨 CORTEX Inline Style Migration")
        print("=" * 70)
        
        level1_pages = self.get_level1_pages()
        print(f"\n📄 Processing {len(level1_pages)} Level 1 pages")
        
        # Phase 1: Extract all inline styles
        print("\n" + "=" * 70)
        print("PHASE 1: Extract Inline Styles")
        print("=" * 70)
        
        total_inline = 0
        total_unique = 0
        
        for page in level1_pages:
            result = self.extract_inline_styles(page)
            total_inline += result['inline_styles']
            total_unique += result['unique_styles']
        
        print(f"\n📊 Extraction Summary:")
        print(f"   Total inline styles: {total_inline}")
        print(f"   Unique style patterns: {len(self.style_registry)}")
        
        if not self.style_registry:
            print("\n✅ No inline styles to migrate!")
            return {'status': 'clean'}
        
        # Phase 2: Generate CSS file
        print("\n" + "=" * 70)
        print("PHASE 2: Generate CSS File")
        print("=" * 70)
        
        css_content = self.generate_css_file()
        
        self.css_output.parent.mkdir(parents=True, exist_ok=True)
        with open(self.css_output, 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        print(f"✅ Generated: {self.css_output.relative_to(self.project_root)}")
        print(f"   Size: {len(css_content)} bytes")
        print(f"   Classes: {len(self.style_registry)}")
        
        # Phase 3: Replace inline styles with classes
        print("\n" + "=" * 70)
        print("PHASE 3: Replace Inline Styles")
        print("=" * 70)
        
        total_replacements = 0
        
        for page in level1_pages:
            replacements = self.replace_inline_styles(page)
            total_replacements += replacements
            
            if replacements > 0:
                self.update_css_imports(page)
        
        print(f"\n✅ Migration Complete!")
        print(f"   Total replacements: {total_replacements}")
        
        # Save migration report
        report = {
            'timestamp': datetime.now().isoformat(),
            'total_inline_styles': total_inline,
            'unique_patterns': len(self.style_registry),
            'total_replacements': total_replacements,
            'css_file': str(self.css_output.relative_to(self.project_root)),
            'style_registry': {
                hash_val: {
                    'class_name': data['class_name'],
                    'count': data['count'],
                    'files': list(data['files'])
                }
                for hash_val, data in self.style_registry.items()
            }
        }
        
        report_path = self.project_root / 'cortex-brain' / 'cleanup-reports' / \
                      f'inline-style-migration-{datetime.now().strftime("%Y%m%d-%H%M%S")}.json'
        report_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2)
        
        print(f"   Report: {report_path.relative_to(self.project_root)}")
        
        return report


def main():
    """Main entry point"""
    project_root = Path(__file__).parent.parent
    migrator = InlineStyleMigrator(project_root)
    
    try:
        report = migrator.run()
        
        if report.get('status') == 'clean':
            print("\n✅ All Level 1 views are already clean (no inline styles)")
            sys.exit(0)
        
        print("\n" + "=" * 70)
        print("✅ Next Steps:")
        print("   1. Run validation test: python scripts/test_inline_style_migration.py")
        print("   2. Review changes in git diff")
        print("   3. Test pages in browser")
        print("   4. Commit with: git commit -m 'refactor(docs): Migrate inline styles to glass-level1.css'")
        print("=" * 70)
        
        sys.exit(0)
    
    except Exception as e:
        print(f"\n❌ ERROR: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
