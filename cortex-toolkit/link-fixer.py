#!/usr/bin/env python3
"""
🔗 CORTEX Broken Link Fixer
============================

Automatically fixes broken internal links in HTML files.

**Author:** Asif Hussain
**Version:** 1.0.0
**Date:** January 4, 2026
**Copyright:** © 2026 Asif Hussain. All rights reserved.
"""

import re
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from bs4 import BeautifulSoup


class LinkFixer:
    """Intelligent broken link detection and fixing."""
    
    def __init__(self, docs_dir: Path):
        self.docs_dir = docs_dir
        self.all_files = list(docs_dir.rglob('*.html'))
        self.file_index = {f.name: f for f in self.all_files}
        
        # Build path index for fuzzy matching
        self.path_index = {}
        for f in self.all_files:
            rel_path = f.relative_to(docs_dir)
            self.path_index[str(rel_path).replace('\\', '/')] = f
    
    def find_target_file(self, broken_link: str, source_file: Path) -> Optional[Path]:
        """Find the correct target file for a broken link."""
        
        # Extract filename
        filename = Path(broken_link).name
        
        # Remove fragment identifier
        if '#' in filename:
            filename = filename.split('#')[0]
        
        if not filename:
            return None
        
        # Direct match
        if filename in self.file_index:
            return self.file_index[filename]
        
        # Try fuzzy matching with path segments
        broken_parts = broken_link.split('/')
        
        # Search for files with matching name
        candidates = [f for f in self.all_files if f.name == filename]
        
        if len(candidates) == 1:
            return candidates[0]
        elif len(candidates) > 1:
            # Choose closest match by directory structure
            source_dir = source_file.parent
            min_distance = float('inf')
            best_match = None
            
            for candidate in candidates:
                # Calculate directory distance
                try:
                    rel_source = source_dir.relative_to(self.docs_dir)
                    rel_candidate = candidate.parent.relative_to(self.docs_dir)
                    distance = len(set(rel_source.parts) ^ set(rel_candidate.parts))
                    
                    if distance < min_distance:
                        min_distance = distance
                        best_match = candidate
                except ValueError:
                    continue
            
            return best_match
        
        return None
    
    def calculate_relative_path(self, source: Path, target: Path) -> str:
        """Calculate relative path from source to target."""
        try:
            # Get relative path
            rel_path = target.relative_to(source.parent)
            return str(rel_path).replace('\\', '/')
        except ValueError:
            # Files are in different branches, use .. notation
            source_parts = source.parent.relative_to(self.docs_dir).parts
            target_parts = target.relative_to(self.docs_dir).parts
            
            # Find common prefix
            common = 0
            for s, t in zip(source_parts, target_parts):
                if s == t:
                    common += 1
                else:
                    break
            
            # Build path
            up_levels = len(source_parts) - common
            down_path = '/'.join(target_parts[common:])
            
            if up_levels > 0:
                return '../' * up_levels + down_path
            else:
                return down_path
    
    def fix_links_in_file(self, html_file: Path) -> Tuple[int, List[Dict]]:
        """Fix broken links in a single HTML file."""
        try:
            content = html_file.read_text(encoding='utf-8')
            soup = BeautifulSoup(content, 'html.parser')
            
            fixes = []
            fixed_count = 0
            
            # Find all links
            for link in soup.find_all('a', href=True):
                href = link['href']
                
                # Skip external links
                if href.startswith(('http://', 'https://', 'mailto:', '#')):
                    continue
                
                # Extract path and fragment
                if '#' in href:
                    path, fragment = href.split('#', 1)
                else:
                    path, fragment = href, ''
                
                if not path:
                    continue
                
                # Check if target exists
                target_path = (html_file.parent / path).resolve()
                
                if not target_path.exists():
                    # Try to find correct target
                    correct_target = self.find_target_file(href, html_file)
                    
                    if correct_target:
                        # Calculate new relative path
                        new_href = self.calculate_relative_path(html_file, correct_target)
                        
                        # Add fragment back if exists
                        if fragment:
                            new_href += '#' + fragment
                        
                        # Update link
                        link['href'] = new_href
                        fixed_count += 1
                        
                        fixes.append({
                            'old_href': href,
                            'new_href': new_href,
                            'link_text': link.get_text(strip=True)
                        })
            
            if fixed_count > 0:
                # Write back
                html_file.write_text(str(soup), encoding='utf-8')
            
            return fixed_count, fixes
            
        except Exception as e:
            print(f"❌ Error processing {html_file}: {e}")
            return 0, []
    
    def fix_all_links(self) -> Dict:
        """Fix broken links across all HTML files."""
        total_fixed = 0
        files_modified = 0
        all_fixes = {}
        
        print(f"🔗 Scanning {len(self.all_files)} HTML files for broken links...")
        
        for html_file in self.all_files:
            fixed_count, fixes = self.fix_links_in_file(html_file)
            
            if fixed_count > 0:
                total_fixed += fixed_count
                files_modified += 1
                all_fixes[str(html_file.relative_to(self.docs_dir))] = fixes
                print(f"  ✅ Fixed {fixed_count} links in {html_file.name}")
        
        print(f"\n✅ Link fixing complete:")
        print(f"   Files modified: {files_modified}")
        print(f"   Total links fixed: {total_fixed}")
        
        return {
            'files_modified': files_modified,
            'total_fixed': total_fixed,
            'details': all_fixes
        }


if __name__ == '__main__':
    docs_dir = Path(__file__).parent.parent / 'docs'
    fixer = LinkFixer(docs_dir)
    results = fixer.fix_all_links()
    
    # Save results
    import json
    report_path = Path(__file__).parent.parent / 'reports' / 'link-fixing-report.json'
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(results, indent=2))
    print(f"\n📊 Report saved: {report_path}")
