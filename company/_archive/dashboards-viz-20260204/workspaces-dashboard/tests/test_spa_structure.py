"""
Test Suite: SPA Structure & File Path Validation
Author: CORTEX Architect
Version: 1.0.0
Date: 2026-02-04

Tests verify:
1. All HTML files exist and are valid
2. All referenced JS/CSS files exist
3. File paths in HTML are correct
4. No 404 errors in asset loading
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Base paths
DASHBOARD_ROOT = Path(__file__).parent.parent
FRONTEND_ROOT = DASHBOARD_ROOT / "frontend"
PUBLIC_DIR = FRONTEND_ROOT / "public"
SRC_DIR = FRONTEND_ROOT / "src"


class TestSPAStructure:
    """Test the SPA folder structure and file references."""

    def test_directory_structure(self):
        """Verify all required directories exist."""
        required_dirs = [
            FRONTEND_ROOT / "public",
            FRONTEND_ROOT / "src",
            FRONTEND_ROOT / "src" / "js",
            FRONTEND_ROOT / "src" / "js" / "components",
            FRONTEND_ROOT / "src" / "css",
            DASHBOARD_ROOT / "backend",
            DASHBOARD_ROOT / "ARCHIVE",
        ]
        
        for directory in required_dirs:
            assert directory.exists(), f"Directory missing: {directory}"
            assert directory.is_dir(), f"Not a directory: {directory}"
        
        print("✅ All required directories exist")

    def test_html_files_exist(self):
        """Verify all HTML files are in the correct location."""
        required_html_files = [
            PUBLIC_DIR / "index.html",
            PUBLIC_DIR / "lens-dashboard.html",
            PUBLIC_DIR / "compliance.html",
        ]
        
        for html_file in required_html_files:
            assert html_file.exists(), f"HTML file missing: {html_file}"
            assert html_file.suffix == ".html", f"Invalid file type: {html_file}"
        
        print(f"✅ All {len(required_html_files)} HTML files exist")

    def test_js_files_exist(self):
        """Verify all JavaScript files are in the correct location."""
        required_js_files = [
            SRC_DIR / "js" / "cortex-unified.js",
            SRC_DIR / "js" / "components" / "cortex-components.js",
            SRC_DIR / "js" / "components" / "chart-builder.js",
            SRC_DIR / "js" / "components" / "d3-force-graph.js",
            SRC_DIR / "js" / "components" / "data-renderer.js",
        ]
        
        for js_file in required_js_files:
            assert js_file.exists(), f"JS file missing: {js_file}"
            assert js_file.suffix == ".js", f"Invalid file type: {js_file}"
        
        print(f"✅ All {len(required_js_files)} JavaScript files exist")

    def test_css_files_exist(self):
        """Verify CSS files are in the correct location."""
        css_files = list((SRC_DIR / "css").glob("*.css"))
        assert len(css_files) > 0, "No CSS files found"
        
        # Check main unified CSS
        main_css = SRC_DIR / "css" / "cortex-unified.css"
        assert main_css.exists(), f"Main CSS file missing: {main_css}"
        
        print(f"✅ All {len(css_files)} CSS files exist")

    def test_html_file_paths(self):
        """Verify all file path references in HTML are correct."""
        html_files = [
            PUBLIC_DIR / "index.html",
            PUBLIC_DIR / "lens-dashboard.html",
        ]
        
        errors = []
        
        for html_file in html_files:
            with open(html_file, 'r') as f:
                content = f.read()
            
            # Extract all src and href attributes
            script_pattern = r'<script\s+src="([^"]+)"'
            link_pattern = r'<link\s+[^>]*href="([^"]+)"'
            
            scripts = re.findall(script_pattern, content)
            links = re.findall(link_pattern, content)
            
            # Check each reference
            for src in scripts:
                # Skip CDN URLs
                if src.startswith("http"):
                    continue
                
                # Remove query strings for checking file existence
                src_without_query = src.split("?")[0]
                
                # Resolve the path relative to the HTML file
                resolved_path = (html_file.parent / src_without_query).resolve()
                
                # Check if file exists
                if not resolved_path.exists():
                    errors.append(f"In {html_file.name}: Script file not found: {src} (resolved to {resolved_path})")
            
            for href in links:
                # Skip external URLs
                if href.startswith("http"):
                    continue
                
                # Remove query strings for checking file existence
                href_without_query = href.split("?")[0]
                
                # Resolve the path
                resolved_path = (html_file.parent / href_without_query).resolve()
                
                # Check if file exists
                if not resolved_path.exists():
                    errors.append(f"In {html_file.name}: Link file not found: {href} (resolved to {resolved_path})")
        
        if errors:
            print("❌ File path errors found:")
            for error in errors:
                print(f"  - {error}")
            raise AssertionError(f"Found {len(errors)} file path errors")
        
        print(f"✅ All file paths in HTML files are correct")

    def test_no_orphaned_files(self):
        """Verify no orphaned enhancement files in root."""
        root_files = list(DASHBOARD_ROOT.glob("enhancements_*"))
        
        assert len(root_files) == 0, f"Orphaned enhancement files found in root: {root_files}"
        
        print("✅ No orphaned enhancement files in root")

    def test_backend_files_moved(self):
        """Verify backend files are in backend directory."""
        backend_dir = DASHBOARD_ROOT / "backend"
        
        # Check for at least some Python files
        py_files = list(backend_dir.glob("*.py"))
        assert len(py_files) > 0, "No Python files in backend directory"
        
        print(f"✅ Backend directory contains {len(py_files)} Python files")

    def test_archive_directory(self):
        """Verify ARCHIVE directory exists with old files."""
        archive_dir = DASHBOARD_ROOT / "ARCHIVE"
        assert archive_dir.exists(), "ARCHIVE directory missing"
        
        archived_files = list(archive_dir.glob("*"))
        assert len(archived_files) > 0, "ARCHIVE directory is empty"
        
        print(f"✅ ARCHIVE directory contains {len(archived_files)} files")

    def test_no_duplicate_assets(self):
        """Verify no duplicate asset files across directories."""
        # Get all JS files
        js_files = {}
        
        for js_file in SRC_DIR.rglob("*.js"):
            filename = js_file.name
            if filename in js_files:
                raise AssertionError(f"Duplicate JS file found: {filename}")
            js_files[filename] = str(js_file)
        
        # Get all CSS files
        css_files = {}
        
        for css_file in SRC_DIR.rglob("*.css"):
            filename = css_file.name
            if filename in css_files:
                raise AssertionError(f"Duplicate CSS file found: {filename}")
            css_files[filename] = str(css_file)
        
        print(f"✅ No duplicate assets found ({len(js_files)} JS, {len(css_files)} CSS)")

    def test_file_permissions(self):
        """Verify all files have proper read permissions."""
        for file_path in [SRC_DIR / "js", SRC_DIR / "css", PUBLIC_DIR]:
            for file in file_path.rglob("*"):
                if file.is_file():
                    assert os.access(file, os.R_OK), f"File not readable: {file}"
        
        print("✅ All files have proper read permissions")

    def test_html_validity(self):
        """Basic HTML validity check (well-formed XML/HTML)."""
        import re
        
        for html_file in PUBLIC_DIR.glob("*.html"):
            with open(html_file, 'r') as f:
                content = f.read()
            
            # Check for basic HTML structure
            assert content.strip().startswith("<!DOCTYPE"), f"Missing DOCTYPE in {html_file.name}"
            assert "<html" in content, f"Missing <html> tag in {html_file.name}"
            assert "</html>" in content, f"Missing </html> tag in {html_file.name}"
            
            # Check for unmatched tags (basic check)
            opening_script = len(re.findall(r"<script", content))
            closing_script = len(re.findall(r"</script>", content))
            assert opening_script == closing_script, f"Unmatched <script> tags in {html_file.name}"
        
        print("✅ HTML files are well-formed")


def run_all_tests():
    """Run all test methods."""
    test_suite = TestSPAStructure()
    
    test_methods = [
        test_suite.test_directory_structure,
        test_suite.test_html_files_exist,
        test_suite.test_js_files_exist,
        test_suite.test_css_files_exist,
        test_suite.test_html_file_paths,
        test_suite.test_no_orphaned_files,
        test_suite.test_backend_files_moved,
        test_suite.test_archive_directory,
        test_suite.test_no_duplicate_assets,
        test_suite.test_file_permissions,
        test_suite.test_html_validity,
    ]
    
    print("\n" + "="*60)
    print("SPA STRUCTURE & FILE PATH VALIDATION TEST SUITE")
    print("="*60 + "\n")
    
    passed = 0
    failed = 0
    
    for test_method in test_methods:
        test_name = test_method.__name__
        try:
            test_method()
            passed += 1
        except AssertionError as e:
            print(f"❌ {test_name}: {e}")
            failed += 1
        except Exception as e:
            print(f"❌ {test_name}: Unexpected error: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print(f"RESULTS: {passed} passed, {failed} failed")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
