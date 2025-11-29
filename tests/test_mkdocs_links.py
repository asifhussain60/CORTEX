"""
MkDocs Link Validation Test Suite

Tests all navigation links, verifies file existence, HTTP responses,
and content quality (no stubs or incomplete documentation).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import yaml
import requests
from pathlib import Path
from typing import Dict, List, Tuple
import time
import re


# Test Configuration
MKDOCS_CONFIG = Path(__file__).parent.parent / "mkdocs.yml"
DOCS_DIR = Path(__file__).parent.parent / "docs"
MKDOCS_URL = "http://127.0.0.1:8000/CORTEX"
MKDOCS_SERVE_TIMEOUT = 5  # seconds to wait for server

# Content quality markers
STUB_MARKERS = [
    "coming soon",
    "to be implemented",
    "placeholder",
    "todo:",
    "work in progress",
    "under construction",
    "not yet available",
    "stub content",
]

INCOMPLETE_MARKERS = [
    "# Title\n\nDescription needed",
    "## Section\n\n<!-- Add content here -->",
    "TBD",
    "TODO",
    "FIXME",
]


class MkDocsNavigationParser:
    """Parse MkDocs navigation structure from mkdocs.yml"""
    
    def __init__(self, config_path: Path):
        self.config_path = config_path
        self.config = self._load_config()
        self.nav = self.config.get("nav", [])
        
    def _load_config(self) -> Dict:
        """Load mkdocs.yml configuration"""
        with open(self.config_path, 'r', encoding='utf-8') as f:
            # Use unsafe_load to handle Python tags in mkdocs.yml
            return yaml.unsafe_load(f)
    
    def extract_all_paths(self) -> List[Tuple[str, str]]:
        """
        Extract all navigation paths from mkdocs.yml
        
        Returns:
            List of (title, file_path) tuples
        """
        paths = []
        
        def traverse(items, parent_title=""):
            for item in items:
                if isinstance(item, dict):
                    for key, value in item.items():
                        if isinstance(value, str):
                            # Direct file path
                            paths.append((key, value))
                        elif isinstance(value, list):
                            # Nested navigation
                            traverse(value, key)
        
        traverse(self.nav)
        return paths


class ContentQualityValidator:
    """Validate documentation content quality"""
    
    @staticmethod
    def is_stub(content: str) -> Tuple[bool, str]:
        """
        Check if content is a stub
        
        Returns:
            (is_stub, reason)
        """
        content_lower = content.lower()
        
        for marker in STUB_MARKERS:
            if marker in content_lower:
                return True, f"Contains stub marker: '{marker}'"
        
        # Check for minimal content (less than 200 chars excluding frontmatter)
        # Remove YAML frontmatter if present
        content_no_frontmatter = re.sub(r'^---\n.*?\n---\n', '', content, flags=re.DOTALL)
        if len(content_no_frontmatter.strip()) < 200:
            return True, f"Minimal content: {len(content_no_frontmatter.strip())} characters"
        
        return False, ""
    
    @staticmethod
    def is_incomplete(content: str) -> Tuple[bool, str]:
        """
        Check if content is incomplete
        
        Returns:
            (is_incomplete, reason)
        """
        for marker in INCOMPLETE_MARKERS:
            if marker in content:
                return True, f"Contains incomplete marker: '{marker}'"
        
        # Check for empty sections (## Header\n\n## Header pattern)
        if re.search(r'##\s+[^\n]+\n\s*\n\s*##', content):
            return True, "Contains empty sections"
        
        return False, ""


@pytest.fixture(scope="module")
def navigation_parser():
    """Fixture to provide navigation parser"""
    return MkDocsNavigationParser(MKDOCS_CONFIG)


@pytest.fixture(scope="module")
def content_validator():
    """Fixture to provide content validator"""
    return ContentQualityValidator()


@pytest.fixture(scope="module", autouse=True)
def check_mkdocs_server():
    """Check if MkDocs server is running"""
    try:
        response = requests.get(MKDOCS_URL, timeout=MKDOCS_SERVE_TIMEOUT)
        if response.status_code not in [200, 301, 302, 404]:
            pytest.skip(f"MkDocs server not responding correctly (status: {response.status_code})")
    except requests.exceptions.RequestException as e:
        pytest.skip(f"MkDocs server not running at {MKDOCS_URL}. Start with: mkdocs serve")


class TestNavigationFileExistence:
    """Test that all navigation entries point to existing files"""
    
    def test_all_navigation_files_exist(self, navigation_parser):
        """Verify all files referenced in navigation exist"""
        missing_files = []
        
        for title, file_path in navigation_parser.extract_all_paths():
            full_path = DOCS_DIR / file_path
            if not full_path.exists():
                missing_files.append({
                    "title": title,
                    "path": file_path,
                    "full_path": str(full_path)
                })
        
        if missing_files:
            error_msg = "Missing files in navigation:\n"
            for item in missing_files:
                error_msg += f"  - {item['title']}: {item['path']} (expected at {item['full_path']})\n"
            pytest.fail(error_msg)


class TestHTTPResponses:
    """Test that all navigation URLs return successful HTTP responses"""
    
    def test_all_navigation_urls_return_200(self, navigation_parser):
        """Verify all navigation URLs return HTTP 200"""
        failed_urls = []
        
        for title, file_path in navigation_parser.extract_all_paths():
            # Convert file path to URL
            # Remove .md extension and handle index.md
            url_path = file_path.replace('.md', '/')
            if url_path.endswith('index/'):
                url_path = url_path.replace('index/', '')
            
            url = f"{MKDOCS_URL}/{url_path}"
            
            try:
                response = requests.get(url, timeout=MKDOCS_SERVE_TIMEOUT, allow_redirects=True)
                if response.status_code != 200:
                    failed_urls.append({
                        "title": title,
                        "url": url,
                        "status_code": response.status_code,
                        "file_path": file_path
                    })
            except requests.exceptions.RequestException as e:
                failed_urls.append({
                    "title": title,
                    "url": url,
                    "status_code": "ERROR",
                    "error": str(e),
                    "file_path": file_path
                })
            
            # Rate limiting to avoid overwhelming the server
            time.sleep(0.1)
        
        if failed_urls:
            error_msg = "Failed HTTP requests:\n"
            for item in failed_urls:
                error_msg += f"  - {item['title']} ({item['url']}): "
                if "error" in item:
                    error_msg += f"ERROR - {item['error']}\n"
                else:
                    error_msg += f"HTTP {item['status_code']}\n"
                error_msg += f"    File: {item['file_path']}\n"
            pytest.fail(error_msg)


class TestContentQuality:
    """Test that all documentation has real content (no stubs)"""
    
    def test_no_stub_content(self, navigation_parser, content_validator):
        """Verify all documentation files contain real content, not stubs"""
        stub_files = []
        
        for title, file_path in navigation_parser.extract_all_paths():
            full_path = DOCS_DIR / file_path
            
            # Skip if file doesn't exist (caught by other test)
            if not full_path.exists():
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                is_stub, reason = content_validator.is_stub(content)
                if is_stub:
                    stub_files.append({
                        "title": title,
                        "path": file_path,
                        "reason": reason
                    })
            except Exception as e:
                stub_files.append({
                    "title": title,
                    "path": file_path,
                    "reason": f"Error reading file: {e}"
                })
        
        if stub_files:
            error_msg = "Stub content detected:\n"
            for item in stub_files:
                error_msg += f"  - {item['title']} ({item['path']}): {item['reason']}\n"
            pytest.fail(error_msg)
    
    def test_no_incomplete_content(self, navigation_parser, content_validator):
        """Verify all documentation files are complete"""
        incomplete_files = []
        
        for title, file_path in navigation_parser.extract_all_paths():
            full_path = DOCS_DIR / file_path
            
            # Skip if file doesn't exist (caught by other test)
            if not full_path.exists():
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                is_incomplete, reason = content_validator.is_incomplete(content)
                if is_incomplete:
                    incomplete_files.append({
                        "title": title,
                        "path": file_path,
                        "reason": reason
                    })
            except Exception as e:
                incomplete_files.append({
                    "title": title,
                    "path": file_path,
                    "reason": f"Error reading file: {e}"
                })
        
        if incomplete_files:
            error_msg = "Incomplete content detected:\n"
            for item in incomplete_files:
                error_msg += f"  - {item['title']} ({item['path']}): {item['reason']}\n"
            pytest.fail(error_msg)


class TestInternalLinks:
    """Test that all internal links within documentation resolve correctly"""
    
    def test_internal_links_resolve(self, navigation_parser):
        """Verify all markdown internal links point to existing files"""
        broken_links = []
        
        # Pattern to match markdown links: [text](path)
        link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
        
        for title, file_path in navigation_parser.extract_all_paths():
            full_path = DOCS_DIR / file_path
            
            # Skip if file doesn't exist
            if not full_path.exists():
                continue
            
            try:
                with open(full_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Find all markdown links
                for match in link_pattern.finditer(content):
                    link_text = match.group(1)
                    link_path = match.group(2)
                    
                    # Skip external links (http://, https://, mailto:)
                    if link_path.startswith(('http://', 'https://', 'mailto:', '#')):
                        continue
                    
                    # Resolve relative path
                    # Remove anchor if present
                    clean_path = link_path.split('#')[0]
                    if not clean_path:  # Just an anchor
                        continue
                    
                    # Resolve relative to current file's directory
                    current_dir = full_path.parent
                    target_path = (current_dir / clean_path).resolve()
                    
                    # Check if target exists
                    if not target_path.exists():
                        broken_links.append({
                            "source_file": file_path,
                            "source_title": title,
                            "link_text": link_text,
                            "link_path": link_path,
                            "resolved_path": str(target_path)
                        })
            except Exception as e:
                # Log read errors but don't fail (file might be binary)
                pass
        
        if broken_links:
            error_msg = "Broken internal links detected:\n"
            for item in broken_links:
                error_msg += f"  - In {item['source_title']} ({item['source_file']}):\n"
                error_msg += f"    Link: [{item['link_text']}]({item['link_path']})\n"
                error_msg += f"    Resolved to: {item['resolved_path']}\n"
            pytest.fail(error_msg)


class TestSpecificPages:
    """Test specific pages mentioned in user request"""
    
    def test_executive_summary_exists_and_loads(self):
        """Test that EXECUTIVE-SUMMARY page exists and loads correctly"""
        # Check file exists
        file_path = DOCS_DIR / "EXECUTIVE-SUMMARY.md"
        assert file_path.exists(), f"EXECUTIVE-SUMMARY.md not found at {file_path}"
        
        # Check HTTP response
        url = f"{MKDOCS_URL}/EXECUTIVE-SUMMARY/"
        response = requests.get(url, timeout=MKDOCS_SERVE_TIMEOUT, allow_redirects=True)
        assert response.status_code == 200, f"EXECUTIVE-SUMMARY URL returned {response.status_code}: {url}"
        
        # Check content quality
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        validator = ContentQualityValidator()
        is_stub, reason = validator.is_stub(content)
        assert not is_stub, f"EXECUTIVE-SUMMARY is a stub: {reason}"
        
        is_incomplete, reason = validator.is_incomplete(content)
        assert not is_incomplete, f"EXECUTIVE-SUMMARY is incomplete: {reason}"


if __name__ == "__main__":
    # Run tests with verbose output
    pytest.main([__file__, "-v", "--tb=short"])
