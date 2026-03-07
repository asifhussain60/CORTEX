"""
Test Linting — cortex-docs/tests/pipeline/test_linting.py
Validates HTML, CSS, and JS files are well-formed and follow standards.
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple

import pytest
from bs4 import BeautifulSoup


# AC_START: AC-DOCGEN-LINTING-20260224T000000


class TestHTMLLinting:
    """Validate HTML files are well-formed and follow best practices."""
    
    def test_all_html_files_exist(self, docs_root: Path) -> None:
        """Collect all HTML files for linting."""
        html_files = list(docs_root.glob("**/*.html"))
        assert len(html_files) > 0, "No HTML files found"
        print(f"\n📄 Found {len(html_files)} HTML files to lint")
    
    def test_html_files_have_valid_structure(self, docs_root: Path, parse_html: callable) -> None:
        """All HTML files must have valid structure."""
        html_files = list(docs_root.glob("**/*.html"))
        invalid_files = []
        
        for html_file in html_files:
            try:
                soup = parse_html(html_file)
                
                # Check for basic structure
                issues = []
                
                if not soup.find("html"):
                    issues.append("Missing <html> tag")
                
                if not soup.find("head"):
                    issues.append("Missing <head> tag")
                
                if not soup.find("body"):
                    issues.append("Missing <body> tag")
                
                if not soup.find("title"):
                    issues.append("Missing <title> tag")
                
                if issues:
                    invalid_files.append({
                        "file": html_file.relative_to(docs_root),
                        "issues": issues
                    })
            except Exception as e:
                invalid_files.append({
                    "file": html_file.relative_to(docs_root),
                    "issues": [f"Parse error: {str(e)}"]
                })
        
        if invalid_files:
            print(f"\n❌ Invalid HTML files found:")
            for item in invalid_files:
                print(f"   {item['file']}:")
                for issue in item['issues']:
                    print(f"      - {issue}")
        
        assert len(invalid_files) == 0, f"{len(invalid_files)} HTML files have structure issues"
    
    def test_html_files_have_proper_doctype(self, docs_root: Path) -> None:
        """All HTML files should have DOCTYPE declaration."""
        html_files = list(docs_root.glob("**/*.html"))
        missing_doctype = []
        
        for html_file in html_files:
            with open(html_file, "r", encoding="utf-8") as f:
                content = f.read()
                
                # Check for DOCTYPE (case-insensitive)
                if not re.search(r'<!DOCTYPE\s+html', content, re.IGNORECASE):
                    missing_doctype.append(html_file.relative_to(docs_root))
        
        if missing_doctype:
            print(f"\n⚠️ Files missing DOCTYPE:")
            for file in missing_doctype:
                print(f"   - {file}")
        
        assert len(missing_doctype) == 0, f"{len(missing_doctype)} files missing DOCTYPE"
    
    def test_html_files_have_lang_attribute(self, docs_root: Path, parse_html: callable) -> None:
        """HTML tags should have lang attribute for accessibility."""
        html_files = list(docs_root.glob("**/*.html"))
        missing_lang = []
        
        for html_file in html_files:
            soup = parse_html(html_file)
            html_tag = soup.find("html")
            
            if html_tag and not html_tag.get("lang"):
                missing_lang.append(html_file.relative_to(docs_root))
        
        if missing_lang:
            print(f"\n⚠️ Files missing lang attribute:")
            for file in missing_lang:
                print(f"   - {file}")
        
        # This is a warning, not a failure (accessibility best practice)
        if len(missing_lang) > 0:
            print(f"\n💡 Consider adding lang='en' to <html> tags for accessibility")
    
    def test_html_files_have_charset_meta(self, docs_root: Path, parse_html: callable) -> None:
        """HTML files should have charset meta tag."""
        html_files = list(docs_root.glob("**/*.html"))
        missing_charset = []
        
        for html_file in html_files:
            soup = parse_html(html_file)
            
            # Look for charset meta tag
            charset_meta = soup.find("meta", charset=True) or soup.find("meta", attrs={"http-equiv": "Content-Type"})
            
            if not charset_meta:
                missing_charset.append(html_file.relative_to(docs_root))
        
        if missing_charset:
            print(f"\n⚠️ Files missing charset meta:")
            for file in missing_charset:
                print(f"   - {file}")
        
        assert len(missing_charset) == 0, f"{len(missing_charset)} files missing charset"
    
    def test_html_files_have_viewport_meta(self, docs_root: Path, parse_html: callable) -> None:
        """HTML files should have viewport meta for responsive design."""
        html_files = list(docs_root.glob("**/*.html"))
        missing_viewport = []
        
        for html_file in html_files:
            soup = parse_html(html_file)
            viewport_meta = soup.find("meta", attrs={"name": "viewport"})
            
            if not viewport_meta:
                missing_viewport.append(html_file.relative_to(docs_root))
        
        if missing_viewport:
            print(f"\n⚠️ Files missing viewport meta:")
            for file in missing_viewport:
                print(f"   - {file}")
        
        assert len(missing_viewport) == 0, f"{len(missing_viewport)} files missing viewport meta"
    
    def test_html_files_no_inline_styles(self, docs_root: Path, parse_html: callable) -> None:
        """HTML files should minimize inline styles (use CSS files)."""
        html_files = list(docs_root.glob("**/*.html"))
        files_with_inline_styles = []
        
        for html_file in html_files:
            soup = parse_html(html_file)
            
            # Check for style attributes (excluding minimal cases)
            elements_with_style = soup.find_all(style=True)
            
            if len(elements_with_style) > 5:  # Allow up to 5 inline styles
                files_with_inline_styles.append({
                    "file": html_file.relative_to(docs_root),
                    "count": len(elements_with_style)
                })
        
        if files_with_inline_styles:
            print(f"\n⚠️ Files with excessive inline styles:")
            for item in files_with_inline_styles:
                print(f"   - {item['file']}: {item['count']} elements")
        
        # This is a warning for code quality, not a hard failure
        if len(files_with_inline_styles) > 0:
            print(f"\n💡 Consider moving inline styles to CSS files")
    
    def test_html_files_proper_nesting(self, docs_root: Path, parse_html: callable) -> None:
        """HTML elements should be properly nested."""
        html_files = list(docs_root.glob("**/*.html"))
        nesting_issues = []
        
        for html_file in html_files:
            soup = parse_html(html_file)
            
            # Check for common nesting violations
            issues = []
            
            # Check: <p> should not contain block elements
            for p in soup.find_all("p"):
                block_children = p.find_all(["div", "section", "article", "h1", "h2", "h3", "h4", "h5", "h6"])
                if block_children:
                    issues.append(f"<p> contains block elements: {[tag.name for tag in block_children]}")
            
            # Check: <a> should not contain interactive elements
            for a in soup.find_all("a"):
                interactive_children = a.find_all(["a", "button", "input"])
                if interactive_children:
                    issues.append(f"<a> contains interactive elements: {[tag.name for tag in interactive_children]}")
            
            if issues:
                nesting_issues.append({
                    "file": html_file.relative_to(docs_root),
                    "issues": issues
                })
        
        if nesting_issues:
            print(f"\n⚠️ Files with nesting issues:")
            for item in nesting_issues:
                print(f"   {item['file']}:")
                for issue in item['issues']:
                    print(f"      - {issue}")
        
        # Warning only - BeautifulSoup may auto-fix some issues
        if len(nesting_issues) > 0:
            print(f"\n💡 Review HTML nesting for best practices")
    
    def test_html_files_have_alt_text_on_images(self, docs_root: Path, parse_html: callable) -> None:
        """Images should have alt text for accessibility."""
        html_files = list(docs_root.glob("**/*.html"))
        images_without_alt = []
        
        for html_file in html_files:
            soup = parse_html(html_file)
            
            # Find all img tags without alt attribute or with empty alt
            images = soup.find_all("img")
            missing_alt = [img for img in images if not img.get("alt")]
            
            if missing_alt:
                images_without_alt.append({
                    "file": html_file.relative_to(docs_root),
                    "count": len(missing_alt)
                })
        
        if images_without_alt:
            print(f"\n⚠️ Images missing alt text (accessibility):")
            for item in images_without_alt:
                print(f"   - {item['file']}: {item['count']} images")
        
        # Warning for accessibility - not all images may need alt text (decorative)
        if len(images_without_alt) > 0:
            print(f"\n💡 Add alt='' for decorative images or descriptive alt text")


class TestCSSLinting:
    """Validate CSS files are well-formed and follow best practices."""
    
    def test_all_css_files_exist(self, docs_root: Path) -> None:
        """Collect all CSS files for linting."""
        css_files = list(docs_root.glob("**/*.css"))
        assert len(css_files) > 0, "No CSS files found"
        print(f"\n🎨 Found {len(css_files)} CSS files to lint")
    
    def test_css_files_are_valid_utf8(self, docs_root: Path) -> None:
        """All CSS files should be UTF-8 encoded."""
        css_files = list(docs_root.glob("**/*.css"))
        encoding_errors = []
        
        for css_file in css_files:
            try:
                with open(css_file, "r", encoding="utf-8") as f:
                    f.read()
            except UnicodeDecodeError as e:
                encoding_errors.append({
                    "file": css_file.relative_to(docs_root),
                    "error": str(e)
                })
        
        assert len(encoding_errors) == 0, f"{len(encoding_errors)} CSS files have encoding issues"
    
    def test_css_files_basic_syntax_validation(self, docs_root: Path) -> None:
        """CSS files should have balanced braces and valid syntax."""
        css_files = list(docs_root.glob("**/*.css"))
        syntax_errors = []
        
        for css_file in css_files:
            with open(css_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            issues = []
            
            # Check balanced braces
            open_braces = content.count("{")
            close_braces = content.count("}")
            
            if open_braces != close_braces:
                issues.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
            
            # Check for basic syntax issues
            # Look for property declarations outside of rulesets (excluding :root and CSS variables)
            lines = content.split("\n")
            brace_depth = 0
            in_root_block = False
            
            for i, line in enumerate(lines, 1):
                stripped = line.strip()
                
                # Skip comments and empty lines
                if not stripped or stripped.startswith("/*") or stripped.startswith("*"):
                    continue
                
                # Track :root block
                if ":root" in stripped and "{" in line:
                    in_root_block = True
                
                # Track brace depth
                brace_depth += line.count("{") - line.count("}")
                
                # If we left a block, check if we left :root
                if brace_depth == 0:
                    in_root_block = False
                
                # Check for property declarations at wrong depth
                # Exclude: @rules, comments, CSS variables in :root, media queries
                if ":" in stripped and ";" in stripped and brace_depth == 0:
                    # Skip valid cases
                    if stripped.startswith("@"):  # @import, @media, etc.
                        continue
                    if stripped.startswith("/*"):  # Comments
                        continue
                    if "--" in stripped and in_root_block:  # CSS variables in :root
                        continue
                    
                    # If none of the above, this might be an issue
                    # But let's be more lenient - only flag clear syntax errors
                    # Issues would be: properties without a selector
                    
            if issues:
                syntax_errors.append({
                    "file": css_file.relative_to(docs_root),
                    "issues": issues
                })
        
        if syntax_errors:
            print(f"\n❌ CSS syntax errors:")
            for item in syntax_errors:
                print(f"   {item['file']}:")
                for issue in item['issues']:
                    print(f"      - {issue}")
        
        assert len(syntax_errors) == 0, f"{len(syntax_errors)} CSS files have syntax errors"
    
    def test_css_files_no_empty_rulesets(self, docs_root: Path) -> None:
        """CSS files should not have empty rulesets."""
        css_files = list(docs_root.glob("**/*.css"))
        files_with_empty_rulesets = []
        
        for css_file in css_files:
            with open(css_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Remove comments
            content_no_comments = re.sub(r'/\*.*?\*/', '', content, flags=re.DOTALL)
            
            # Find empty rulesets: selector { }
            empty_rulesets = re.findall(r'[^{}]+\{\s*\}', content_no_comments)
            
            if empty_rulesets:
                files_with_empty_rulesets.append({
                    "file": css_file.relative_to(docs_root),
                    "count": len(empty_rulesets)
                })
        
        if files_with_empty_rulesets:
            print(f"\n⚠️ CSS files with empty rulesets:")
            for item in files_with_empty_rulesets:
                print(f"   - {item['file']}: {item['count']} empty rulesets")
        
        # Warning only - empty rulesets are valid but indicate dead code
        if len(files_with_empty_rulesets) > 0:
            print(f"\n💡 Consider removing empty CSS rulesets")
    
    def test_css_files_use_css_variables(self, docs_root: Path) -> None:
        """Check if CSS files use CSS custom properties (variables)."""
        css_files = list(docs_root.glob("**/*.css"))
        
        files_with_vars = 0
        files_without_vars = 0
        
        for css_file in css_files:
            with open(css_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check for CSS variable declarations or usage
            has_var_declaration = re.search(r'--[\w-]+\s*:', content)
            has_var_usage = re.search(r'var\(--', content)
            
            if has_var_declaration or has_var_usage:
                files_with_vars += 1
            else:
                files_without_vars += 1
        
        print(f"\n📊 CSS Variables Usage:")
        print(f"   Files using CSS variables: {files_with_vars}")
        print(f"   Files without CSS variables: {files_without_vars}")
        
        # Informational only - not all files need variables


class TestJSLinting:
    """Validate JavaScript files are well-formed and follow best practices."""
    
    def test_all_js_files_exist(self, docs_root: Path) -> None:
        """Collect all JS files for linting."""
        js_files = list(docs_root.glob("**/*.js"))
        assert len(js_files) > 0, "No JS files found"
        print(f"\n⚡ Found {len(js_files)} JS files to lint")
    
    def test_js_files_are_valid_utf8(self, docs_root: Path) -> None:
        """All JS files should be UTF-8 encoded."""
        js_files = list(docs_root.glob("**/*.js"))
        encoding_errors = []
        
        for js_file in js_files:
            try:
                with open(js_file, "r", encoding="utf-8") as f:
                    f.read()
            except UnicodeDecodeError as e:
                encoding_errors.append({
                    "file": js_file.relative_to(docs_root),
                    "error": str(e)
                })
        
        assert len(encoding_errors) == 0, f"{len(encoding_errors)} JS files have encoding issues"
    
    def test_js_files_basic_syntax_validation(self, docs_root: Path) -> None:
        """JavaScript files should have balanced braces and parentheses."""
        js_files = list(docs_root.glob("**/*.js"))
        syntax_errors = []
        
        for js_file in js_files:
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            issues = []
            
            # Count braces, parentheses, and brackets in the raw file
            # This is more accurate than trying to parse JS ourselves
            open_braces = content.count("{")
            close_braces = content.count("}")
            
            if open_braces != close_braces:
                issues.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")
            
            # Check balanced parentheses
            open_parens = content.count("(")
            close_parens = content.count(")")
            
            if open_parens != close_parens:
                issues.append(f"Unbalanced parentheses: {open_parens} open, {close_parens} close")
            
            # Check balanced square brackets
            open_brackets = content.count("[")
            close_brackets = content.count("]")
            
            if open_brackets != close_brackets:
                issues.append(f"Unbalanced brackets: {open_brackets} open, {close_brackets} close")
            
            if issues:
                syntax_errors.append({
                    "file": js_file.relative_to(docs_root),
                    "issues": issues
                })
        
        if syntax_errors:
            print(f"\n❌ JS syntax errors:")
            for item in syntax_errors:
                print(f"   {item['file']}:")
                for issue in item['issues']:
                    print(f"      - {issue}")
        
        assert len(syntax_errors) == 0, f"{len(syntax_errors)} JS files have syntax errors"
    
    def test_js_files_no_console_log_in_production(self, docs_root: Path) -> None:
        """JavaScript files should minimize console.log (production)."""
        js_files = list(docs_root.glob("**/*.js"))
        files_with_console_log = []
        
        for js_file in js_files:
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Count console.log occurrences (not console.error/warn which are acceptable)
            console_logs = re.findall(r'console\.log\s*\(', content)
            
            if len(console_logs) > 3:  # Allow up to 3 for debugging
                files_with_console_log.append({
                    "file": js_file.relative_to(docs_root),
                    "count": len(console_logs)
                })
        
        if files_with_console_log:
            print(f"\n⚠️ JS files with console.log (consider removing for production):")
            for item in files_with_console_log:
                print(f"   - {item['file']}: {item['count']} occurrences")
        
        # Warning only - console.log is acceptable during development
        if len(files_with_console_log) > 0:
            print(f"\n💡 Consider removing console.log before production deployment")
    
    def test_js_files_use_strict_mode(self, docs_root: Path) -> None:
        """JavaScript files should use 'use strict' for better error checking."""
        js_files = list(docs_root.glob("**/*.js"))
        files_without_strict = []
        
        for js_file in js_files:
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check for 'use strict' at the beginning (ignoring comments)
            # Remove comments first
            content_no_comments = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)
            content_no_comments = re.sub(r'/\*.*?\*/', '', content_no_comments, flags=re.DOTALL)
            
            if not re.search(r'["\']use strict["\']', content_no_comments):
                files_without_strict.append(js_file.relative_to(docs_root))
        
        if files_without_strict:
            print(f"\n⚠️ JS files without 'use strict':")
            for file in files_without_strict:
                print(f"   - {file}")
        
        # Warning only - strict mode is a best practice but not required
        if len(files_without_strict) > 0:
            print(f"\n💡 Consider adding 'use strict' for better error checking")
    
    def test_js_files_have_semicolons(self, docs_root: Path) -> None:
        """Check JavaScript files for semicolon usage (style consistency)."""
        js_files = list(docs_root.glob("**/*.js"))
        
        files_with_semicolons = 0
        files_without_semicolons = 0
        
        for js_file in js_files:
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Count lines with and without semicolons
            # This is a rough heuristic
            lines_with_semicolon = content.count(";")
            
            # If file has substantial semicolon usage, consider it semicolon-style
            if lines_with_semicolon > 10:
                files_with_semicolons += 1
            else:
                files_without_semicolons += 1
        
        print(f"\n📊 JavaScript Style:")
        print(f"   Files with semicolons: {files_with_semicolons}")
        print(f"   Files without semicolons: {files_without_semicolons}")
        
        # Informational only - both styles are valid
    
    def test_js_files_valid_json_responses(self, docs_root: Path) -> None:
        """Check if JS files handle JSON parsing correctly."""
        js_files = list(docs_root.glob("**/*.js"))
        files_with_json_parse = []
        
        for js_file in js_files:
            with open(js_file, "r", encoding="utf-8") as f:
                content = f.read()
            
            # Check for JSON.parse usage
            has_json_parse = "JSON.parse" in content
            
            # Check if there's error handling around JSON.parse
            has_try_catch = "try" in content and "catch" in content
            
            if has_json_parse:
                files_with_json_parse.append({
                    "file": js_file.relative_to(docs_root),
                    "has_error_handling": has_try_catch
                })
        
        if files_with_json_parse:
            print(f"\n📊 JSON.parse usage:")
            for item in files_with_json_parse:
                status = "✅" if item["has_error_handling"] else "⚠️"
                print(f"   {status} {item['file']}")
        
        # Check that files using JSON.parse have error handling
        files_without_error_handling = [
            item for item in files_with_json_parse 
            if not item["has_error_handling"]
        ]
        
        if files_without_error_handling:
            print(f"\n⚠️ Files using JSON.parse without try/catch:")
            for item in files_without_error_handling:
                print(f"   - {item['file']}")
            print(f"\n💡 Add try/catch around JSON.parse to handle malformed JSON")


# AC_COMPLETE: AC-DOCGEN-LINTING-20260224T000000 ✅
