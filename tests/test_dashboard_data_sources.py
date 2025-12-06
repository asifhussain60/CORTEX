"""
Test Dashboard Data Source Registration

Validates that data sources are properly registered and accessible.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
import pytest
from pathlib import Path
import re


class TestDashboardDataSources:
    """Test suite for dashboard data source registration"""
    
    @pytest.fixture
    def cortex_root(self):
        """Get CORTEX root directory"""
        return Path(__file__).parent.parent
    
    @pytest.fixture
    def dashboards_dir(self, cortex_root):
        """Get dashboards directory"""
        return cortex_root / "cortex-brain" / "dashboards"
    
    @pytest.fixture
    def ui_dir(self, dashboards_dir):
        """Get UI directory"""
        return dashboards_dir / "ui"
    
    @pytest.fixture
    def data_loader_js(self, ui_dir):
        """Get data-loader.js file"""
        return ui_dir / "data-loader.js"
    
    @pytest.fixture
    def index_html(self, ui_dir):
        """Get index.html file"""
        return ui_dir / "index.html"
    
    def test_dashboards_directory_exists(self, dashboards_dir):
        """Test that dashboards directory exists"""
        assert dashboards_dir.exists(), f"Dashboards directory not found: {dashboards_dir}"
        assert dashboards_dir.is_dir(), f"Dashboards path is not a directory: {dashboards_dir}"
    
    def test_ui_directory_exists(self, ui_dir):
        """Test that UI directory exists"""
        assert ui_dir.exists(), f"UI directory not found: {ui_dir}"
        assert ui_dir.is_dir(), f"UI path is not a directory: {ui_dir}"
    
    def test_data_loader_js_exists(self, data_loader_js):
        """Test that data-loader.js exists"""
        assert data_loader_js.exists(), f"data-loader.js not found: {data_loader_js}"
        assert data_loader_js.is_file(), f"data-loader.js is not a file: {data_loader_js}"
    
    def test_index_html_exists(self, index_html):
        """Test that index.html exists"""
        assert index_html.exists(), f"index.html not found: {index_html}"
        assert index_html.is_file(), f"index.html is not a file: {index_html}"
    
    def test_luum_fresh_data_directory_exists(self, dashboards_dir):
        """Test that luum-fresh data directory exists"""
        luum_fresh_dir = dashboards_dir / "luum-fresh"
        assert luum_fresh_dir.exists(), f"luum-fresh directory not found: {luum_fresh_dir}"
        assert luum_fresh_dir.is_dir(), f"luum-fresh is not a directory: {luum_fresh_dir}"
    
    def test_luum_fresh_has_required_json_files(self, dashboards_dir):
        """Test that luum-fresh has all required JSON files"""
        luum_fresh_dir = dashboards_dir / "luum-fresh"
        required_files = [
            "metadata.json",
            "architecture.json",
            "tech-stack.json",
            "code-organization.json",
            "security.json",
            "team-metrics.json",
            "health-data.json",
            "vendors.json"
        ]
        
        for filename in required_files:
            file_path = luum_fresh_dir / filename
            assert file_path.exists(), f"Required file not found: {file_path}"
            
            # Validate JSON is parseable
            with open(file_path) as f:
                try:
                    json.load(f)
                except json.JSONDecodeError as e:
                    pytest.fail(f"Invalid JSON in {filename}: {e}")
    
    def test_data_loader_js_has_data_sources_object(self, data_loader_js):
        """Test that data-loader.js contains DATA_SOURCES object"""
        content = data_loader_js.read_text(encoding='utf-8')
        
        assert "const DATA_SOURCES" in content, "DATA_SOURCES constant not found in data-loader.js"
        assert "DATA_SOURCES = {" in content, "DATA_SOURCES object declaration not found"
    
    def test_data_loader_js_includes_luum_fresh(self, data_loader_js):
        """Test that data-loader.js includes luum-fresh in DATA_SOURCES"""
        content = data_loader_js.read_text(encoding='utf-8')
        
        # Extract DATA_SOURCES object
        pattern = r'const DATA_SOURCES = \{([^}]+)\};'
        match = re.search(pattern, content, re.DOTALL)
        
        assert match, "Could not extract DATA_SOURCES object from data-loader.js"
        
        data_sources_content = match.group(1)
        
        # Check for luum-fresh entry
        assert "'luum-fresh'" in data_sources_content, \
            "luum-fresh not found in DATA_SOURCES. Content:\n" + data_sources_content
        assert "'/luum-fresh/'" in data_sources_content, \
            "luum-fresh path not found in DATA_SOURCES"
    
    def test_index_html_has_source_selector(self, index_html):
        """Test that index.html contains source selector dropdown"""
        content = index_html.read_text(encoding='utf-8')
        
        assert '<select id="sourceSelect"' in content, \
            "Source selector dropdown not found in index.html"
    
    def test_index_html_includes_luum_fresh_option(self, index_html):
        """Test that index.html includes luum-fresh option in dropdown"""
        content = index_html.read_text(encoding='utf-8')
        
        # Check for luum-fresh option
        assert 'value="luum-fresh"' in content, \
            "luum-fresh option not found in dropdown. Check index.html source selector."
        
        # Verify option has label
        assert 'Luum Fresh' in content or 'luum-fresh' in content.lower(), \
            "luum-fresh label not found in dropdown options"
    
    def test_all_data_directories_registered_in_data_loader(self, dashboards_dir, data_loader_js):
        """Test that all valid data directories are registered in data-loader.js"""
        content = data_loader_js.read_text(encoding='utf-8')
        
        # Find all directories with JSON files
        data_dirs = []
        for item in dashboards_dir.iterdir():
            if item.is_dir() and item.name not in ['ui', 'schema', '__pycache__']:
                # Check if has metadata or architecture JSON
                if (item / "metadata.json").exists() or (item / "architecture.json").exists():
                    data_dirs.append(item.name)
        
        # Extract registered sources from DATA_SOURCES
        pattern = r"'([^']+)':\s*'/[^/]+/'"
        registered_sources = re.findall(pattern, content)
        
        # Verify all data directories are registered
        for dir_name in data_dirs:
            assert dir_name in registered_sources, \
                f"Data directory '{dir_name}' exists but not registered in DATA_SOURCES"
    
    def test_all_registered_sources_have_data_directories(self, dashboards_dir, data_loader_js):
        """Test that all registered sources have corresponding data directories"""
        content = data_loader_js.read_text(encoding='utf-8')
        
        # Extract registered sources
        pattern = r"'([^']+)':\s*'/([^/]+)/'"
        matches = re.findall(pattern, content)
        
        for source_id, source_path in matches:
            data_dir = dashboards_dir / source_path
            assert data_dir.exists(), \
                f"Source '{source_id}' registered but directory '{source_path}' not found"
    
    def test_data_loader_version_is_set(self, data_loader_js):
        """Test that DATA_LOADER_VERSION is set for cache busting"""
        content = data_loader_js.read_text(encoding='utf-8')
        
        assert "DATA_LOADER_VERSION" in content, \
            "DATA_LOADER_VERSION not found in data-loader.js"
        
        # Extract version
        pattern = r"const DATA_LOADER_VERSION = '([^']+)'"
        match = re.search(pattern, content)
        
        assert match, "Could not extract DATA_LOADER_VERSION value"
        
        version = match.group(1)
        assert version, "DATA_LOADER_VERSION is empty"
        
        # Verify version format (e.g., 2.0.2)
        assert re.match(r'\d+\.\d+\.\d+', version), \
            f"Invalid version format: {version}. Expected X.Y.Z"
    
    def test_cache_busting_in_load_function(self, data_loader_js):
        """Test that cache-busting parameters are added to fetch calls"""
        content = data_loader_js.read_text(encoding='utf-8')
        
        # Look for cache-busting in loadJsonFile function
        assert "cacheBuster" in content or "cache: 'no-cache'" in content, \
            "Cache-busting mechanism not found in data-loader.js"
    
    def test_index_html_has_cache_control_meta_tags(self, index_html):
        """Test that index.html has cache control meta tags"""
        content = index_html.read_text(encoding='utf-8')
        
        assert 'http-equiv="Cache-Control"' in content, \
            "Cache-Control meta tag not found in index.html"
        assert 'no-cache' in content, \
            "no-cache directive not found in meta tags"
    
    def test_index_html_script_tags_have_version_parameters(self, index_html):
        """Test that script tags include version parameters for cache-busting"""
        content = index_html.read_text(encoding='utf-8')
        
        # Check that data-loader.js has version parameter
        assert 'data-loader.js?v=' in content, \
            "data-loader.js script tag missing version parameter"
        
        # Verify version format
        pattern = r'data-loader\.js\?v=(\d+\.\d+\.\d+)'
        match = re.search(pattern, content)
        
        assert match, "Version parameter format invalid in script tag"
        
        version = match.group(1)
        assert version, "Version parameter is empty"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
