#!/usr/bin/env python3
"""
CORTEX HTML Syntax Validator
Validates HTML files for syntax errors and malformed markup

Author: Asif Hussain
Date: December 27, 2025
"""

from pathlib import Path
from html.parser import HTMLParser
from typing import List, Tuple, Dict
import re

class HTMLValidator(HTMLParser):
    """HTML parser that tracks syntax errors"""
    
    def __init__(self):
        super().__init__()
        self.errors = []
        self.warnings = []
        self.tag_stack = []
        self.line_num = 1
        
    def error(self, message):
        """Override error handler"""
        self.errors.append(f"Line {self.line_num}: {message}")
    
    def handle_starttag(self, tag, attrs):
        """Track opening tags"""
        # Void elements don't need closing tags
        void_elements = {'img', 'br', 'hr', 'input', 'meta', 'link', 'area', 'base', 'col', 'embed', 'param', 'source', 'track', 'wbr'}
        if tag not in void_elements:
            self.tag_stack.append((tag, self.line_num))
        
        # Check for duplicate attributes
        attr_names = [name for name, _ in attrs]
        if len(attr_names) != len(set(attr_names)):
            duplicates = [name for name in attr_names if attr_names.count(name) > 1]
            self.warnings.append(f"Line {self.line_num}: Duplicate attributes in <{tag}>: {', '.join(set(duplicates))}")
    
    def handle_endtag(self, tag):
        """Track closing tags and validate nesting"""
        if not self.tag_stack:
            self.errors.append(f"Line {self.line_num}: Unexpected closing tag </{tag}> with no matching opening tag")
            return
        
        # Check if closing tag matches most recent opening tag
        expected_tag, open_line = self.tag_stack[-1]
        if tag == expected_tag:
            self.tag_stack.pop()
        else:
            # Look for tag in stack (possible nesting issue)
            for i, (stack_tag, stack_line) in enumerate(reversed(self.tag_stack)):
                if stack_tag == tag:
                    self.errors.append(
                        f"Line {self.line_num}: Closing tag </{tag}> doesn't match expected </{expected_tag}> "
                        f"(opened at line {open_line})"
                    )
                    # Remove the found tag and all tags after it (they're improperly nested)
                    self.tag_stack = self.tag_stack[:-(i+1)]
                    return
            
            # Tag not found in stack at all
            self.errors.append(f"Line {self.line_num}: Closing tag </{tag}> with no matching opening tag")
    
    def handle_data(self, data):
        """Count lines in data"""
        self.line_num += data.count('\n')

def validate_html_file(file_path: Path) -> Dict[str, any]:
    """Validate a single HTML file"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for common malformed patterns
        malformed_patterns = []
        
        # Pattern 1: Unclosed attribute quotes
        if re.search(r'<[^>]*=["\'][^"\']*(?:<|$)', content):
            malformed_patterns.append("Potentially unclosed attribute quotes")
        
        # Pattern 2: Missing closing angle bracket
        if re.search(r'<[^>]*\n[^<>]*<', content):
            malformed_patterns.append("Potentially missing closing angle bracket")
        
        # Run HTML parser
        validator = HTMLValidator()
        try:
            validator.feed(content)
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Parser exception: {str(e)}"],
                'warnings': [],
                'unclosed_tags': [],
                'malformed_patterns': malformed_patterns
            }
        
        # Check for unclosed tags
        unclosed_tags = []
        if validator.tag_stack:
            unclosed_tags = [f"<{tag}> opened at line {line}" for tag, line in validator.tag_stack]
        
        is_valid = len(validator.errors) == 0 and len(unclosed_tags) == 0 and len(malformed_patterns) == 0
        
        return {
            'valid': is_valid,
            'errors': validator.errors,
            'warnings': validator.warnings,
            'unclosed_tags': unclosed_tags,
            'malformed_patterns': malformed_patterns
        }
        
    except Exception as e:
        return {
            'valid': False,
            'errors': [f"File read error: {str(e)}"],
            'warnings': [],
            'unclosed_tags': [],
            'malformed_patterns': []
        }

def main():
    """Validate all modified HTML files"""
    docs_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/docs")
    
    # Get all HTML files (except story/viewer.html which wasn't modified by cleanup)
    html_files = []
    for html_file in docs_dir.rglob("*.html"):
        if "story/viewer.html" not in str(html_file):
            html_files.append(html_file)
    
    print(f"Validating {len(html_files)} HTML files...\n")
    
    results = {}
    valid_count = 0
    invalid_count = 0
    warning_count = 0
    
    for file_path in sorted(html_files):
        relative_path = file_path.relative_to(docs_dir)
        result = validate_html_file(file_path)
        results[str(relative_path)] = result
        
        if result['valid']:
            valid_count += 1
            if result['warnings']:
                warning_count += 1
                print(f"⚠️  {relative_path}")
                for warning in result['warnings']:
                    print(f"    {warning}")
        else:
            invalid_count += 1
            print(f"❌ {relative_path}")
            for error in result['errors']:
                print(f"    ERROR: {error}")
            for unclosed in result['unclosed_tags']:
                print(f"    UNCLOSED: {unclosed}")
            for pattern in result['malformed_patterns']:
                print(f"    MALFORMED: {pattern}")
            print()
    
    print(f"\n{'='*70}")
    print(f"VALIDATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total Files: {len(html_files)}")
    print(f"✅ Valid: {valid_count}")
    print(f"⚠️  Valid with Warnings: {warning_count}")
    print(f"❌ Invalid: {invalid_count}")
    
    if invalid_count == 0:
        print(f"\n🎉 ALL HTML FILES ARE SYNTACTICALLY CORRECT!")
    else:
        print(f"\n⚠️  {invalid_count} files have syntax errors that need fixing")
    
    return invalid_count == 0

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
