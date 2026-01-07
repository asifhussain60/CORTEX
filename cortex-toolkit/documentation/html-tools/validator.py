#!/usr/bin/env python3
"""
CORTEX Native HTML Validator
Pure Python HTML validation using html.parser (zero dependencies)

Features:
- Syntax validation (unclosed tags, nesting errors)
- Attribute validation (duplicates, malformed)
- Structure validation (required elements)
- Line-accurate error reporting

Author: Asif Hussain
Date: December 27, 2025
"""

from pathlib import Path
from html.parser import HTMLParser
from typing import Dict, List, Tuple, Optional
import re


class HTMLValidator(HTMLParser):
    """Native Python HTML validator using html.parser"""
    
    def __init__(self, strict: bool = True):
        super().__init__()
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.tag_stack: List[Tuple[str, int]] = []
        self.line_num = 1
        self.strict = strict
        
        # HTML5 void elements (self-closing)
        self.void_elements = {
            'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
            'link', 'meta', 'param', 'source', 'track', 'wbr'
        }
        
        # Required document elements
        self.has_doctype = False
        self.has_html = False
        self.has_head = False
        self.has_title = False
        self.has_body = False
        
    def error(self, message):
        """Override default error handler"""
        self.errors.append(f"Line {self.line_num}: {message}")
    
    def handle_decl(self, decl):
        """Handle DOCTYPE declaration"""
        if decl.upper().startswith('DOCTYPE'):
            self.has_doctype = True
    
    def handle_starttag(self, tag, attrs):
        """Process opening tags"""
        tag = tag.lower()
        
        # Track required elements
        if tag == 'html':
            self.has_html = True
        elif tag == 'head':
            self.has_head = True
        elif tag == 'title':
            self.has_title = True
        elif tag == 'body':
            self.has_body = True
        
        # Void elements don't need closing tags
        if tag not in self.void_elements:
            self.tag_stack.append((tag, self.line_num))
        
        # Validate attributes
        self._validate_attributes(tag, attrs)
    
    def handle_endtag(self, tag):
        """Process closing tags and validate nesting"""
        tag = tag.lower()
        
        if not self.tag_stack:
            self.errors.append(
                f"Line {self.line_num}: Unexpected closing tag </{tag}> "
                f"with no matching opening tag"
            )
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
                        f"Line {self.line_num}: Closing tag </{tag}> doesn't match "
                        f"expected </{expected_tag}> (opened at line {open_line}). "
                        f"Improper nesting detected."
                    )
                    # Remove the found tag and all tags after it
                    self.tag_stack = self.tag_stack[:-(i+1)]
                    return
            
            # Tag not found in stack at all
            self.errors.append(
                f"Line {self.line_num}: Closing tag </{tag}> with no matching opening tag"
            )
    
    def handle_data(self, data):
        """Count lines in text content"""
        self.line_num += data.count('\n')
    
    def _validate_attributes(self, tag: str, attrs: List[Tuple[str, str]]):
        """Validate tag attributes"""
        attr_names = [name.lower() for name, _ in attrs]
        
        # Check for duplicate attributes
        if len(attr_names) != len(set(attr_names)):
            duplicates = [name for name in attr_names if attr_names.count(name) > 1]
            self.warnings.append(
                f"Line {self.line_num}: Duplicate attributes in <{tag}>: "
                f"{', '.join(set(duplicates))}"
            )
        
        # Check for required attributes
        required_attrs = {
            'img': ['src', 'alt'],
            'a': ['href'],
            'link': ['href', 'rel'],
            'meta': ['content'],
            'script': ['src']
        }
        
        if tag in required_attrs and self.strict:
            for req_attr in required_attrs[tag]:
                if req_attr not in attr_names:
                    self.warnings.append(
                        f"Line {self.line_num}: Missing required attribute '{req_attr}' "
                        f"in <{tag}>"
                    )
    
    def validate_structure(self):
        """Validate overall document structure"""
        structure_errors = []
        
        if self.strict:
            if not self.has_doctype:
                structure_errors.append("Missing DOCTYPE declaration")
            if not self.has_html:
                structure_errors.append("Missing <html> element")
            if not self.has_head:
                structure_errors.append("Missing <head> element")
            if not self.has_title:
                structure_errors.append("Missing <title> element")
            if not self.has_body:
                structure_errors.append("Missing <body> element")
        
        # Check for unclosed tags
        if self.tag_stack:
            for tag, line in self.tag_stack:
                structure_errors.append(f"Unclosed tag <{tag}> opened at line {line}")
        
        return structure_errors
    
    def get_results(self) -> Dict:
        """Get validation results"""
        structure_errors = self.validate_structure()
        
        return {
            'valid': len(self.errors) == 0 and len(structure_errors) == 0,
            'errors': self.errors + structure_errors,
            'warnings': self.warnings,
            'line_count': self.line_num,
            'unclosed_tags': len(self.tag_stack)
        }


def validate_file(file_path: Path, strict: bool = True) -> Dict:
    """
    Validate a single HTML file
    
    Args:
        file_path: Path to HTML file
        strict: Enable strict validation (DOCTYPE, required elements)
    
    Returns:
        Dict with validation results
    """
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
        
        # Pattern 3: Mismatched quotes
        if re.search(r'''<[^>]*=['"][^'"]*['"][^>]*>''', content):
            malformed_patterns.append("Potentially mismatched quotes")
        
        # Run validator
        validator = HTMLValidator(strict=strict)
        
        try:
            validator.feed(content)
        except Exception as e:
            return {
                'valid': False,
                'errors': [f"Parser exception: {str(e)}"],
                'warnings': [],
                'malformed_patterns': malformed_patterns,
                'file_path': str(file_path)
            }
        
        results = validator.get_results()
        results['malformed_patterns'] = malformed_patterns
        results['file_path'] = str(file_path)
        
        return results
        
    except Exception as e:
        return {
            'valid': False,
            'errors': [f"File read error: {str(e)}"],
            'warnings': [],
            'malformed_patterns': [],
            'file_path': str(file_path)
        }


def validate_directory(
    directory: Path,
    pattern: str = "**/*.html",
    exclude: Optional[List[str]] = None,
    strict: bool = True
) -> Dict[str, Dict]:
    """
    Validate all HTML files in a directory
    
    Args:
        directory: Directory to search
        pattern: Glob pattern for files (default: **/*.html)
        exclude: List of patterns to exclude
        strict: Enable strict validation
    
    Returns:
        Dict mapping file paths to validation results
    """
    if exclude is None:
        exclude = []
    
    results = {}
    files = list(directory.glob(pattern))
    
    for file_path in files:
        # Check exclusions
        should_exclude = False
        for exclude_pattern in exclude:
            if exclude_pattern in str(file_path):
                should_exclude = True
                break
        
        if should_exclude:
            continue
        
        result = validate_file(file_path, strict=strict)
        relative_path = file_path.relative_to(directory)
        results[str(relative_path)] = result
    
    return results


def print_validation_report(results: Dict[str, Dict]):
    """Print a formatted validation report"""
    valid_count = 0
    invalid_count = 0
    warning_count = 0
    
    print("\n" + "="*70)
    print("CORTEX HTML VALIDATION REPORT")
    print("="*70 + "\n")
    
    for file_path, result in sorted(results.items()):
        if result['valid']:
            valid_count += 1
            if result['warnings']:
                warning_count += 1
                print(f"⚠️  {file_path}")
                for warning in result['warnings']:
                    print(f"    {warning}")
        else:
            invalid_count += 1
            print(f"❌ {file_path}")
            for error in result['errors']:
                print(f"    ERROR: {error}")
            if result.get('malformed_patterns'):
                for pattern in result['malformed_patterns']:
                    print(f"    MALFORMED: {pattern}")
            print()
    
    print("="*70)
    print(f"Total Files: {len(results)}")
    print(f"✅ Valid: {valid_count}")
    print(f"⚠️  Valid with Warnings: {warning_count}")
    print(f"❌ Invalid: {invalid_count}")
    print("="*70)
    
    if invalid_count == 0:
        print("\n🎉 ALL HTML FILES ARE SYNTACTICALLY CORRECT!\n")
    else:
        print(f"\n⚠️  {invalid_count} files have syntax errors\n")
    
    return invalid_count == 0


if __name__ == "__main__":
    import sys
    
    # Example usage
    if len(sys.argv) > 1:
        path = Path(sys.argv[1])
        
        if path.is_file():
            result = validate_file(path)
            print_validation_report({path.name: result})
        elif path.is_dir():
            results = validate_directory(path)
            success = print_validation_report(results)
            sys.exit(0 if success else 1)
    else:
        print("Usage: python validator.py <file_or_directory>")
        sys.exit(1)
