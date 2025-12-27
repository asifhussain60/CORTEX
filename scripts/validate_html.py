#!/usr/bin/env python3
"""
Validate and report HTML issues across all documentation pages.
Uses HTML5 validation and checks for common structural problems.
"""

import re
import subprocess
from pathlib import Path
from typing import List, Dict, Tuple
from html.parser import HTMLParser

class HTMLValidator(HTMLParser):
    """Custom HTML parser to detect structural issues."""
    
    def __init__(self):
        super().__init__()
        self.tag_stack = []
        self.errors = []
        self.line_num = 1
        
    def handle_starttag(self, tag, attrs):
        """Track opening tags."""
        if tag not in ['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 
                       'link', 'meta', 'param', 'source', 'track', 'wbr']:
            self.tag_stack.append((tag, self.line_num))
    
    def handle_endtag(self, tag):
        """Check for mismatched closing tags."""
        if tag in ['area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 
                   'link', 'meta', 'param', 'source', 'track', 'wbr']:
            return
            
        if not self.tag_stack:
            self.errors.append(f"Line {self.line_num}: Closing tag </{tag}> without matching opening tag")
            return
            
        expected_tag, line = self.tag_stack.pop()
        if expected_tag != tag:
            self.errors.append(f"Line {self.line_num}: Expected </{expected_tag}> (opened at line {line}), found </{tag}>")
    
    def handle_data(self, data):
        """Track line numbers."""
        self.line_num += data.count('\n')

def check_common_issues(content: str, filepath: Path) -> List[str]:
    """Check for common HTML issues."""
    issues = []
    
    # Check for orphaned closing tags
    orphaned_closing = re.findall(r'^\s*</[^>]+>\s*$', content, re.MULTILINE)
    if orphaned_closing:
        issues.append(f"Found {len(orphaned_closing)} orphaned closing tags")
    
    # Check for duplicate opening tags without closing
    div_opens = content.count('<div')
    div_closes = content.count('</div>')
    if div_opens != div_closes:
        issues.append(f"Mismatched div tags: {div_opens} opening, {div_closes} closing (diff: {div_opens - div_closes})")
    
    a_opens = content.count('<a ')
    a_closes = content.count('</a>')
    if a_opens != a_closes:
        issues.append(f"Mismatched anchor tags: {a_opens} opening, {a_closes} closing (diff: {a_opens - a_closes})")
    
    # Check for malformed icon characters
    if '�' in content:
        count = content.count('�')
        issues.append(f"Found {count} malformed/broken emoji characters (�)")
    
    # Check for tags in wrong order
    wrong_order = re.findall(r'</[^>]+>\s*<div class="glass-card', content)
    if wrong_order:
        issues.append(f"Found {len(wrong_order)} instances of closing tags before card opening")
    
    return issues

def validate_file(filepath: Path) -> Dict:
    """Validate a single HTML file."""
    try:
        content = filepath.read_text(encoding='utf-8')
        
        # Use custom parser
        parser = HTMLValidator()
        try:
            parser.feed(content)
        except Exception as e:
            parser.errors.append(f"Parser error: {str(e)}")
        
        # Check for unclosed tags
        if parser.tag_stack:
            for tag, line in parser.tag_stack:
                parser.errors.append(f"Line {line}: Unclosed tag <{tag}>")
        
        # Check common issues
        common_issues = check_common_issues(content, filepath)
        
        return {
            'path': filepath,
            'parser_errors': parser.errors,
            'common_issues': common_issues,
            'has_errors': bool(parser.errors or common_issues)
        }
        
    except Exception as e:
        return {
            'path': filepath,
            'parser_errors': [f"Failed to read file: {str(e)}"],
            'common_issues': [],
            'has_errors': True
        }

def main():
    """Validate all HTML files in docs directory."""
    project_root = Path(__file__).parent.parent
    docs_dir = project_root / "docs"
    
    html_files = sorted(docs_dir.rglob("*.html"))
    
    print(f"🔍 Validating {len(html_files)} HTML files...\n")
    
    files_with_errors = []
    total_errors = 0
    
    for html_file in html_files:
        result = validate_file(html_file)
        
        if result['has_errors']:
            files_with_errors.append(result)
            error_count = len(result['parser_errors']) + len(result['common_issues'])
            total_errors += error_count
            
            rel_path = html_file.relative_to(docs_dir)
            print(f"❌ {rel_path}")
            
            if result['parser_errors']:
                print(f"   📋 Parser Errors ({len(result['parser_errors'])}):")
                for error in result['parser_errors'][:5]:  # Show first 5
                    print(f"      • {error}")
                if len(result['parser_errors']) > 5:
                    print(f"      ... and {len(result['parser_errors']) - 5} more")
            
            if result['common_issues']:
                print(f"   ⚠️  Common Issues ({len(result['common_issues'])}):")
                for issue in result['common_issues']:
                    print(f"      • {issue}")
            print()
    
    print("=" * 70)
    if files_with_errors:
        print(f"\n❌ Validation Failed")
        print(f"   Files with errors: {len(files_with_errors)}/{len(html_files)}")
        print(f"   Total issues: {total_errors}")
    else:
        print(f"\n✅ All HTML files valid!")
        print(f"   Files checked: {len(html_files)}")
    print()

if __name__ == "__main__":
    main()
