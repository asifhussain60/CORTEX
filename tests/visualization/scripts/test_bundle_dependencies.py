"""
Tests for Dependency Bundling Script.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-007
Task: 018 - Dependency Bundling Tests
"""

import json
import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from cortex.visualization.scripts.bundle_dependencies import (
    DependencyAsset,
    DependencyBundler,
    bundle_dependencies,
    verify_bundle,
    DEPENDENCIES,
)


class TestDependencyAsset:
    """Test DependencyAsset dataclass."""
    
    def test_create_dependency_asset(self):
        """Test creating a dependency asset."""
        asset = DependencyAsset(
            name="Alpine.js",
            version="3.13.3",
            url="https://example.com/alpine.min.js",
            filename="alpine-3.13.3.min.js",
            expected_checksum="abc123",
            size_kb=15,
        )
        
        assert asset.name == "Alpine.js"
        assert asset.version == "3.13.3"
        assert asset.filename == "alpine-3.13.3.min.js"
        assert asset.size_kb == 15


class TestDependencyBundler:
    """Test DependencyBundler class."""
    
    @pytest.fixture
    def temp_vendor_dir(self, tmp_path):
        """Create temporary vendor directory."""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        return vendor_dir
    
    @pytest.fixture
    def bundler(self, temp_vendor_dir):
        """Create DependencyBundler instance with temp directory."""
        return DependencyBundler(vendor_dir=temp_vendor_dir)
    
    def test_init_creates_vendor_dir_path(self, temp_vendor_dir):
        """Test bundler initialization with custom vendor directory."""
        bundler = DependencyBundler(vendor_dir=temp_vendor_dir)
        assert bundler.vendor_dir == temp_vendor_dir
        assert bundler.checksums_file == temp_vendor_dir / ".checksums.json"
    
    def test_init_with_default_path(self):
        """Test bundler initialization with default vendor directory."""
        bundler = DependencyBundler()
        assert bundler.vendor_dir.name == "vendor"
        assert "static" in str(bundler.vendor_dir)
    
    def test_compute_checksum(self, bundler):
        """Test SHA-256 checksum computation."""
        content = b"Hello, CORTEX!"
        checksum = bundler._compute_checksum(content)
        
        # Verify it's a valid SHA-256 hex string
        assert len(checksum) == 64
        assert all(c in "0123456789abcdef" for c in checksum)
        
        # Verify consistency
        checksum2 = bundler._compute_checksum(content)
        assert checksum == checksum2
    
    def test_compute_checksum_different_content(self, bundler):
        """Test different content produces different checksums."""
        content1 = b"Content 1"
        content2 = b"Content 2"
        
        checksum1 = bundler._compute_checksum(content1)
        checksum2 = bundler._compute_checksum(content2)
        
        assert checksum1 != checksum2
    
    @patch("urllib.request.urlopen")
    def test_download_asset_success(self, mock_urlopen, bundler):
        """Test successful asset download."""
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.read.return_value = b"/* Alpine.js */"
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        asset = DependencyAsset(
            name="Test",
            version="1.0.0",
            url="https://example.com/test.js",
            filename="test.js",
            expected_checksum="",
            size_kb=1,
        )
        
        content = bundler._download_asset(asset)
        assert content == b"/* Alpine.js */"
        mock_urlopen.assert_called_once()
    
    @patch("urllib.request.urlopen")
    def test_download_asset_retry_on_failure(self, mock_urlopen, bundler):
        """Test retry logic on download failure."""
        from urllib.error import URLError
        
        # Fail twice, succeed on third attempt
        mock_response = MagicMock()
        mock_response.read.return_value = b"Success!"
        mock_response.__enter__ = Mock(return_value=mock_response)
        mock_response.__exit__ = Mock(return_value=False)
        
        mock_urlopen.side_effect = [
            URLError("Network error"),
            URLError("Network error"),
            mock_response,
        ]
        
        asset = DependencyAsset(
            name="Test",
            version="1.0.0",
            url="https://example.com/test.js",
            filename="test.js",
            expected_checksum="",
            size_kb=1,
        )
        
        content = bundler._download_asset(asset, retries=3)
        assert content == b"Success!"
        assert mock_urlopen.call_count == 3
    
    @patch("urllib.request.urlopen")
    def test_download_asset_exhausted_retries(self, mock_urlopen, bundler):
        """Test failure after exhausting retries."""
        from urllib.error import URLError
        
        mock_urlopen.side_effect = URLError("Persistent network error")
        
        asset = DependencyAsset(
            name="Test",
            version="1.0.0",
            url="https://example.com/test.js",
            filename="test.js",
            expected_checksum="",
            size_kb=1,
        )
        
        with pytest.raises(URLError):
            bundler._download_asset(asset, retries=3)
    
    def test_save_checksums_manifest(self, bundler, temp_vendor_dir):
        """Test saving checksums manifest."""
        # Create mock files matching DEPENDENCIES
        from cortex.visualization.scripts.bundle_dependencies import DEPENDENCIES
        
        for dep in DEPENDENCIES[:2]:  # Create first 2 dependencies
            (temp_vendor_dir / dep.filename).write_bytes(b"/* Mock Content */")
        
        bundler._save_checksums_manifest()
        
        assert bundler.checksums_file.exists()
        manifest = json.loads(bundler.checksums_file.read_text())
        
        # Verify manifest has entries
        assert len(manifest) >= 2
    
    def test_verify_bundle_integrity_no_manifest(self, bundler, capsys):
        """Test verification fails when no manifest exists."""
        result = bundler.verify_bundle_integrity()
        
        assert result is False
        captured = capsys.readouterr()
        assert "No checksums manifest found" in captured.out
    
    def test_verify_bundle_integrity_valid(self, bundler, temp_vendor_dir):
        """Test verification succeeds for valid bundle."""
        # Create files
        alpine_content = b"/* Alpine.js */"
        d3_content = b"/* D3.js */"
        
        (temp_vendor_dir / "alpine.min.js").write_bytes(alpine_content)
        (temp_vendor_dir / "d3.min.js").write_bytes(d3_content)
        
        # Create manifest
        manifest = {
            "alpine.min.js": {
                "name": "Alpine.js",
                "version": "3.13.3",
                "checksum": bundler._compute_checksum(alpine_content),
                "size_bytes": len(alpine_content),
            },
            "d3.min.js": {
                "name": "D3.js",
                "version": "7.8.5",
                "checksum": bundler._compute_checksum(d3_content),
                "size_bytes": len(d3_content),
            },
        }
        bundler.checksums_file.write_text(json.dumps(manifest))
        
        result = bundler.verify_bundle_integrity()
        assert result is True
    
    def test_verify_bundle_integrity_corrupted(self, bundler, temp_vendor_dir):
        """Test verification fails for corrupted files."""
        # Create file
        (temp_vendor_dir / "alpine.min.js").write_bytes(b"/* Alpine.js */")
        
        # Create manifest with wrong checksum
        manifest = {
            "alpine.min.js": {
                "name": "Alpine.js",
                "version": "3.13.3",
                "checksum": "wrong_checksum_here",
                "size_bytes": 15,
            },
        }
        bundler.checksums_file.write_text(json.dumps(manifest))
        
        result = bundler.verify_bundle_integrity()
        assert result is False
    
    def test_verify_bundle_integrity_missing_file(self, bundler, temp_vendor_dir):
        """Test verification fails for missing files."""
        # Create manifest for non-existent file
        manifest = {
            "missing.js": {
                "name": "Missing",
                "version": "1.0.0",
                "checksum": "abc123",
                "size_bytes": 100,
            },
        }
        bundler.checksums_file.write_text(json.dumps(manifest))
        
        result = bundler.verify_bundle_integrity()
        assert result is False
    
    def test_list_bundled_dependencies_empty(self, bundler):
        """Test listing dependencies when no manifest exists."""
        deps = bundler.list_bundled_dependencies()
        assert deps == []
    
    def test_list_bundled_dependencies(self, bundler, temp_vendor_dir):
        """Test listing bundled dependencies."""
        manifest = {
            "alpine.min.js": {
                "name": "Alpine.js",
                "version": "3.13.3",
                "checksum": "a" * 64,
                "size_bytes": 15000,
            },
        }
        bundler.checksums_file.write_text(json.dumps(manifest))
        
        deps = bundler.list_bundled_dependencies()
        
        assert len(deps) == 1
        assert deps[0]["name"] == "Alpine.js"
        assert deps[0]["version"] == "3.13.3"
        assert "14.6" in deps[0]["size_kb"]  # ~15000/1024


class TestConvenienceFunctions:
    """Test module-level convenience functions."""
    
    @patch.object(DependencyBundler, "download_all_dependencies")
    def test_bundle_dependencies_success(self, mock_download):
        """Test bundle_dependencies convenience function success."""
        mock_download.return_value = {
            "Alpine.js": True,
            "D3.js": True,
        }
        
        result = bundle_dependencies()
        
        assert result is True
        mock_download.assert_called_once_with(force=False)
    
    @patch.object(DependencyBundler, "download_all_dependencies")
    def test_bundle_dependencies_partial_failure(self, mock_download):
        """Test bundle_dependencies with partial failures."""
        mock_download.return_value = {
            "Alpine.js": True,
            "D3.js": False,
        }
        
        result = bundle_dependencies()
        
        assert result is False
    
    @patch.object(DependencyBundler, "verify_bundle_integrity")
    def test_verify_bundle_convenience(self, mock_verify):
        """Test verify_bundle convenience function."""
        mock_verify.return_value = True
        
        result = verify_bundle()
        
        assert result is True
        mock_verify.assert_called_once()


class TestDependenciesCatalog:
    """Test DEPENDENCIES catalog configuration."""
    
    def test_dependencies_catalog_exists(self):
        """Test DEPENDENCIES catalog is defined."""
        assert len(DEPENDENCIES) > 0
    
    def test_all_dependencies_have_required_fields(self):
        """Test all dependencies have required fields."""
        for asset in DEPENDENCIES:
            assert asset.name
            assert asset.version
            assert asset.url
            assert asset.filename
            assert asset.size_kb > 0
    
    def test_dependencies_have_unique_filenames(self):
        """Test all dependencies have unique filenames."""
        filenames = [asset.filename for asset in DEPENDENCIES]
        assert len(filenames) == len(set(filenames))
    
    def test_alpine_js_in_dependencies(self):
        """Test Alpine.js is in dependencies catalog."""
        alpine = next((d for d in DEPENDENCIES if d.name == "Alpine.js"), None)
        assert alpine is not None
        assert "3.13" in alpine.version
    
    def test_d3_js_in_dependencies(self):
        """Test D3.js is in dependencies catalog."""
        d3 = next((d for d in DEPENDENCIES if d.name == "D3.js"), None)
        assert d3 is not None
        assert "7." in d3.version
    
    def test_mermaid_in_dependencies(self):
        """Test Mermaid is in dependencies catalog."""
        mermaid = next((d for d in DEPENDENCIES if d.name == "Mermaid"), None)
        assert mermaid is not None
        assert "10." in mermaid.version
    
    def test_tailwind_in_dependencies(self):
        """Test Tailwind CSS is in dependencies catalog."""
        tailwind = next((d for d in DEPENDENCIES if d.name == "Tailwind CSS"), None)
        assert tailwind is not None
        assert "3." in tailwind.version
