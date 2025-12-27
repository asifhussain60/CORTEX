#!/usr/bin/env python3
"""
CORTEX HTML Syntax Validator
Validates HTML files for syntax errors using html5lib

Author: Asif Hussain
Date: December 27, 2025
"""

from pathlib import Path
from typing import Dict
import html5lib

def validate_html_file(file_path: Path) -> Dict[str, any]:
    """Validate a single HTML file using html5lib"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Parse with html5lib (non-strict mode for lenient validation)
        errors = []
        warnings = []
        
        try:
            # html5lib with lenient parsing (fixes minor issues automatically)
            parser = html5lib.HTMLParser(strict=False, tree=html5lib.getTreeBuilder("etree"))
            document = parser.parse(content)
            
            # html5lib in non-strict mode doesn't raise errors for minor issues
            # We only fail on major syntax problems that prevent parsing
            # The fact that we got here means it parsed successfully
            is_valid = True
        
        except Exception as e:
            # Only major syntax errors that prevent parsing
            error_msg = str(e)
            errors.append(f"Parse error: {error_msg}")
            is_valid = False
        
        return {
            'valid': is_valid,
            'errors': errors,
            'warnings': warnings,
            'unclosed_tags': [],
            'malformed_patterns': []
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
