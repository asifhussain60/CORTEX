"""
Tests for packager.py - Dashboard packaging and multi-format export.

Coverage target: 80%+ (12 tests for 153 LOC)
Focus areas:
- ZIP package creation
- Multi-format export
- File inclusion
- Edge cases

Author: Asif Hussain
Date: December 2025
"""

import json
import pytest
import zipfile
from pathlib import Path
from src.cortex_lens.generators.packager import Packager


# ========== Fixtures ==========

@pytest.fixture
def packager():
    """Create packager instance."""
    return Packager()


@pytest.fixture
def sample_data():
    """Sample analysis data for export."""
    return {
        'classification': {'repo_type': 'fullstack_web'},
        'health': {'total_files': 100, 'health_score': 80},
        'metadata': {'repo_name': 'TestRepo'}
    }


@pytest.fixture
def mock_dashboard(tmp_path):
    """Create mock dashboard directory with files."""
    dashboard_dir = tmp_path / "dashboard"
    dashboard_dir.mkdir()
    
    # Create mock files
    (dashboard_dir / "index.html").write_text("<html><body>Dashboard</body></html>")
    (dashboard_dir / "style.css").write_text("body { margin: 0; }")
    (dashboard_dir / "script.js").write_text("console.log('loaded');")
    
    # Create subdirectory
    assets_dir = dashboard_dir / "assets"
    assets_dir.mkdir()
    (assets_dir / "logo.png").write_bytes(b"fake_png_data")
    
    return dashboard_dir


# ========== Package Method Tests ==========

class TestPackageMethod:
    """Test package() method for ZIP creation."""
    
    def test_package_creates_zip_file(self, packager, mock_dashboard):
        """Test package creates ZIP file."""
        result = packager.package(mock_dashboard)
        
        assert result.exists()
        assert result.suffix == '.zip'
        assert result.name == 'dashboard.zip'
    
    def test_package_includes_all_files(self, packager, mock_dashboard):
        """Test ZIP package includes all dashboard files."""
        result = packager.package(mock_dashboard)
        
        with zipfile.ZipFile(result, 'r') as zf:
            names = zf.namelist()
            
            # Should include all files
            assert any('index.html' in name for name in names)
            assert any('style.css' in name for name in names)
            assert any('script.js' in name for name in names)
    
    def test_package_includes_subdirectories(self, packager, mock_dashboard):
        """Test ZIP includes subdirectory files."""
        result = packager.package(mock_dashboard)
        
        with zipfile.ZipFile(result, 'r') as zf:
            names = zf.namelist()
            
            # Should include assets subdirectory
            assert any('assets' in name and 'logo.png' in name for name in names)
    
    def test_package_uses_compression(self, packager, mock_dashboard):
        """Test ZIP uses compression."""
        result = packager.package(mock_dashboard)
        
        with zipfile.ZipFile(result, 'r') as zf:
            # Check compression type
            for info in zf.infolist():
                assert info.compress_type == zipfile.ZIP_DEFLATED


# ========== Export Method Tests ==========

class TestExportMethod:
    """Test export() method for multi-format export."""
    
    def test_export_json_format(self, packager, sample_data, tmp_path):
        """Test exporting in JSON format."""
        output_dir = tmp_path / "exports"
        
        results = packager.export(sample_data, ['json'], output_dir)
        
        assert 'json' in results
        assert results['json'].exists()
        assert results['json'].suffix == '.json'
    
    def test_export_multiple_formats(self, packager, sample_data, tmp_path):
        """Test exporting in multiple formats simultaneously."""
        output_dir = tmp_path / "exports"
        
        results = packager.export(sample_data, ['json', 'yaml'], output_dir)
        
        assert 'json' in results
        assert 'yaml' in results or 'yml' in results
    
    def test_export_all_formats(self, packager, sample_data, tmp_path):
        """Test 'all' format exports everything."""
        output_dir = tmp_path / "exports"
        
        results = packager.export(sample_data, ['all'], output_dir)
        
        # Should export multiple formats
        assert len(results) > 0
    
    def test_export_creates_directory(self, packager, sample_data, tmp_path):
        """Test export creates output directory if missing."""
        output_dir = tmp_path / "nested" / "exports"
        
        results = packager.export(sample_data, ['json'], output_dir)
        
        assert output_dir.exists()
        # Files are in data/ subdirectory
        assert 'json' in results
        assert results['json'].exists()


# ========== Edge Cases Tests ==========

class TestEdgeCases:
    """Test edge cases and error handling."""
    
    def test_generate_raises_not_implemented(self, packager, tmp_path):
        """Test generate() method raises NotImplementedError."""
        output_path = tmp_path / "output"
        
        with pytest.raises(NotImplementedError):
            packager.generate({}, output_path)
    
    def test_package_empty_dashboard(self, packager, tmp_path):
        """Test packaging empty dashboard directory."""
        empty_dir = tmp_path / "empty_dashboard"
        empty_dir.mkdir()
        
        result = packager.package(empty_dir)
        
        # Should create ZIP even if empty
        assert result.exists()
    
    def test_export_empty_data(self, packager, tmp_path):
        """Test exporting empty data."""
        output_dir = tmp_path / "exports"
        
        results = packager.export({}, ['json'], output_dir)
        
        assert 'json' in results
        assert results['json'].exists()
        
        # Should contain empty JSON object
        content = results['json'].read_text(encoding='utf-8')
        assert content.strip() in ['{}', '{ }']
    
    def test_export_unknown_format_handled(self, packager, sample_data, tmp_path):
        """Test export handles unknown format gracefully."""
        output_dir = tmp_path / "exports"
        
        # Should not crash with unknown format
        results = packager.export(sample_data, ['unknown_format'], output_dir)
        
        # May return empty dict or skip unknown format
        assert isinstance(results, dict)
