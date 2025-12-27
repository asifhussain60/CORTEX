#!/usr/bin/env python3
"""
CORTEX SAFE Inline Style Cleanup Script
Carefully removes inline styles while preserving HTML structure

Author: Asif Hussain
Date: December 27, 2025
"""

import re
from pathlib import Path
from typing import List, Tuple
from html.parser import HTMLParser

class SafeStyleRemover(HTMLParser):
    """HTML parser that safely removes inline styles"""
    
    def __init__(self):
        super().__init__()
        self.output = []
        self.changes = 0
        
    def handle_starttag(self, tag, attrs):
        """Process opening tags and remove style attributes"""
        new_attrs = []
        had_style = False
        
        for name, value in attrs:
            if name == 'style':
                had_style = True
                self.changes += 1
                # Skip the style attribute
                continue
            else:
                new_attrs.append((name, value))
        
        # Reconstruct tag
        attr_str = ' '.join([f'{name}="{value}"' if value else name for name, value in new_attrs])
        if attr_str:
            self.output.append(f'<{tag} {attr_str}>')
        else:
            self.output.append(f'<{tag}>')
    
    def handle_endtag(self, tag):
        """Process closing tags"""
        self.output.append(f'</{tag}>')
    
    def handle_startendtag(self, tag, attrs):
        """Process self-closing tags (like <br/>, <img/>)"""
        new_attrs = []
        had_style = False
        
        for name, value in attrs:
            if name == 'style':
                had_style = True
                self.changes += 1
                continue
            else:
                new_attrs.append((name, value))
        
        attr_str = ' '.join([f'{name}="{value}"' if value else name for name, value in new_attrs])
        if attr_str:
            self.output.append(f'<{tag} {attr_str} />')
        else:
            self.output.append(f'<{tag} />')
    
    def handle_data(self, data):
        """Process text content"""
        self.output.append(data)
    
    def handle_comment(self, data):
        """Process HTML comments"""
        self.output.append(f'<!--{data}-->')
    
    def handle_decl(self, decl):
        """Process declarations like DOCTYPE"""
        self.output.append(f'<!{decl}>')
    
    def get_output(self):
        """Get the processed HTML"""
        return ''.join(self.output)

def safe_cleanup_file(file_path: Path) -> Tuple[int, List[str]]:
    """Safely clean up inline styles from a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check if file has inline styles
        if 'style="' not in content:
            return 0, []
        
        parser = SafeStyleRemover()
        try:
            parser.feed(content)
            new_content = parser.get_output()
            
            # Verify we didn't break the HTML
            if len(new_content) < len(content) * 0.5:  # Sanity check
                return 0, ["ERROR: Output too small, possible parsing failure"]
            
            # Write back
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return parser.changes, []
            
        except Exception as e:
            return 0, [f"Parser error: {str(e)}"]
        
    except Exception as e:
        return 0, [f"File error: {str(e)}"]

def main():
    """Process all HTML files safely"""
    docs_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/docs")
    
    print("Scanning for HTML files with inline styles...")
    html_files = []
    for html_file in docs_dir.rglob("*.html"):
        # Skip story/viewer.html (allowed exception)
        if "story/viewer.html" in str(html_file):
            continue
        html_files.append(html_file)
    
    total_changes = 0
    files_modified = 0
    errors = []
    
    for file_path in sorted(html_files):
        relative_path = file_path.relative_to(docs_dir)
        changes, file_errors = safe_cleanup_file(file_path)
        
        if file_errors:
            print(f"⚠️  {relative_path}: {', '.join(file_errors)}")
            errors.extend(file_errors)
        elif changes > 0:
            print(f"✅ {relative_path}: {changes} inline styles removed")
            total_changes += changes
            files_modified += 1
    
    print(f"\n{'='*70}")
    print(f"SAFE CLEANUP COMPLETE")
    print(f"{'='*70}")
    print(f"Files Modified: {files_modified}")
    print(f"Inline Styles Removed: {total_changes}")
    print(f"Errors: {len(errors)}")
    
    if errors:
        print(f"\n⚠️  Some files had errors. Review above.")
    else:
        print(f"\n✅ All files cleaned successfully!")

if __name__ == "__main__":
    main()
