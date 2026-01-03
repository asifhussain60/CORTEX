#!/usr/bin/env python3
"""
CSS Path Fixer for CORTEX Documentation
Corrects relative CSS paths in subdirectory HTML files
Author: Asif Hussain
Version: 1.0.0
"""

import os
import re
from pathlib import Path
from typing import List, Tuple


class CSSPathFixer:
    """Fix incorrect CSS paths in HTML files"""
    
    def __init__(self, docs_root: str = "docs"):
        self.docs_root = Path(docs_root)
        self.fixes_applied = 0
        self.files_modified = []
        
    def fix_all(self, dry_run: bool = False) -> dict:
        """Fix CSS paths in all HTML files"""
        print("\n🔧 CSS Path Fixer")
        print("="*80)
        
        # Patterns to fix
        fixes = self._scan_and_fix(dry_run)
        
        return {
            'files_scanned': fixes['scanned'],
            'files_modified': len(self.files_modified),
            'fixes_applied': self.fixes_applied,
            'modified_files': self.files_modified
        }
    
    def _scan_and_fix(self, dry_run: bool) -> dict:
        """Scan and fix CSS paths"""
        scanned = 0
        
        for html_file in self.docs_root.rglob('*.html'):
            # Skip archives
            if 'archives' in str(html_file):
                continue
                
            scanned += 1
            
            try:
                with open(html_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                original_content = content
                
                # Fix patterns based on directory depth
                content = self._fix_css_paths(html_file, content)
                
                if content != original_content:
                    if not dry_run:
                        with open(html_file, 'w', encoding='utf-8') as f:
                            f.write(content)
                    
                    fixes_count = content.count('href="../../assets/css') - original_content.count('href="../../assets/css')
                    fixes_count += content.count('href="../assets/css') - original_content.count('href="../assets/css')
                    
                    self.fixes_applied += abs(fixes_count)
                    self.files_modified.append(str(html_file.relative_to(self.docs_root)))
                    
                    if dry_run:
                        print(f"  🔍 Would fix: {html_file.relative_to(self.docs_root)}")
                    else:
                        print(f"  ✅ Fixed: {html_file.relative_to(self.docs_root)}")
                    
            except Exception as e:
                print(f"  ⚠️  Error processing {html_file}: {e}")
        
        return {'scanned': scanned}
    
    def _fix_css_paths(self, html_file: Path, content: str) -> str:
        """Fix CSS paths based on directory structure"""
        
        # Calculate depth from docs root
        relative_path = html_file.relative_to(self.docs_root)
        depth = len(relative_path.parts) - 1  # -1 for the file itself
        
        if depth == 0:
            # Root level - paths should be assets/css/...
            return content
        elif depth == 1:
            # One level deep (e.g., knowledge/*.html)
            # Should be ../assets/css/...
            content = re.sub(
                r'href="assets/css/([\w\-\.]+(\?[\w\-=]+)?)"',
                r'href="../assets/css/\1"',
                content
            )
            content = re.sub(
                r'src="assets/js/([\w\-\.]+(\?[\w\-=]+)?)"',
                r'src="../assets/js/\1"',
                content
            )
        elif depth == 2:
            # Two levels deep (e.g., knowledge/security/*.html)
            # Should be ../../assets/css/...
            
            # Fix single-level paths
            content = re.sub(
                r'href="assets/css/([\w\-\.]+(\?[\w\-=]+)?)"',
                r'href="../../assets/css/\1"',
                content
            )
            content = re.sub(
                r'src="assets/js/([\w\-\.]+(\?[\w\-=]+)?)"',
                r'src="../../assets/js/\1"',
                content
            )
            
            # Fix incorrect single ../ paths (with query params)
            content = re.sub(
                r'href="\.\./assets/css/([\w\-\.]+)(\?[\w\-=]+)?',
                r'href="../../assets/css/\1\2',
                content
            )
            content = re.sub(
                r'src="\.\./assets/js/([\w\-\.]+)(\?[\w\-=]+)?',
                r'src="../../assets/js/\1\2',
                content
            )
            
        elif depth >= 3:
            # Three or more levels deep
            correct_prefix = '../' * depth
            
            # Fix any incorrect path depth (with query params)
            content = re.sub(
                r'href="(?:\.\./)*(assets/css/[\w\-\.]+)(\?[\w\-=]+)?"',
                f'href="{correct_prefix}\\1\\2"',
                content
            )
            content = re.sub(
                r'src="(?:\.\./)*(assets/js/[\w\-\.]+)(\?[\w\-=]+)?"',
                f'src="{correct_prefix}\\1\\2"',
                content
            )
        
        return content


def main():
    """Main execution"""
    import sys
    
    dry_run = '--dry-run' in sys.argv
    
    print("\n" + "="*80)
    print("🔧 CORTEX Documentation CSS Path Fixer")
    print("="*80)
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be modified\n")
    
    fixer = CSSPathFixer()
    results = fixer.fix_all(dry_run=dry_run)
    
    print("\n" + "="*80)
    print("📊 RESULTS")
    print("="*80)
    print(f"Files Scanned: {results['files_scanned']}")
    print(f"Files Modified: {results['files_modified']}")
    print(f"Fixes Applied: {results['fixes_applied']}")
    
    if dry_run:
        print("\n💡 Run without --dry-run to apply fixes")
    else:
        print("\n✅ CSS path corrections applied successfully!")
    
    print("="*80 + "\n")
    
    return 0


if __name__ == "__main__":
    exit(main())
