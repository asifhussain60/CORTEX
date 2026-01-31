"""Tests for LENS Dashboard vendor asset bundling.

Tests the vendor bundling script that downloads JavaScript
and CSS dependencies for offline operation.
"""

import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from cortex.visualization.scripts.bundle_vendor_assets import (
    VendorAsset,
    VENDOR_ASSETS,
    TAILWIND_CSS,
    get_vendor_dir,
    download_asset,
    bundle_vendor_assets,
    verify_vendor_assets,
)


class TestVendorAsset:
    """Tests for VendorAsset namedtuple."""
    
    def test_create_vendor_asset(self) -> None:
        """Test creating a VendorAsset."""
        asset = VendorAsset(
            name="Test.js",
            url="https://example.com/test.js",
            filename="test-1.0.0.min.js",
            sha256="abc123",
            size_kb=100,
        )
        
        assert asset.name == "Test.js"
        assert asset.filename == "test-1.0.0.min.js"
        assert asset.size_kb == 100
    
    def test_vendor_assets_list_not_empty(self) -> None:
        """Test that VENDOR_ASSETS list is populated."""
        assert len(VENDOR_ASSETS) > 0
    
    def test_vendor_assets_have_required_fields(self) -> None:
        """Test that all vendor assets have required fields."""
        for asset in VENDOR_ASSETS:
            assert asset.name
            assert asset.url.startswith("http")
            assert asset.filename.endswith(".js")
            assert asset.size_kb > 0


class TestTailwindCSS:
    """Tests for bundled Tailwind CSS."""
    
    def test_tailwind_css_not_empty(self) -> None:
        """Test that Tailwind CSS content exists."""
        assert len(TAILWIND_CSS) > 0
    
    def test_tailwind_css_has_essential_classes(self) -> None:
        """Test that Tailwind CSS has essential utility classes."""
        essential = [
            ".flex",
            ".grid",
            ".p-4",
            ".text-sm",
            ".bg-white",
            ".rounded",
            ".shadow",
        ]
        
        for cls in essential:
            assert cls in TAILWIND_CSS, f"Missing class: {cls}"
    
    def test_tailwind_css_has_glassmorphism(self) -> None:
        """Test that Tailwind CSS includes glassmorphism styles."""
        assert ".glass-panel" in TAILWIND_CSS


class TestGetVendorDir:
    """Tests for vendor directory resolution."""
    
    def test_vendor_dir_is_path(self) -> None:
        """Test that get_vendor_dir returns a Path."""
        vendor_dir = get_vendor_dir()
        assert isinstance(vendor_dir, Path)
    
    def test_vendor_dir_ends_with_vendor(self) -> None:
        """Test that vendor directory path ends with 'vendor'."""
        vendor_dir = get_vendor_dir()
        assert vendor_dir.name == "vendor"
    
    def test_vendor_dir_is_in_static(self) -> None:
        """Test that vendor directory is under static/."""
        vendor_dir = get_vendor_dir()
        assert "static" in str(vendor_dir)


class TestDownloadAsset:
    """Tests for asset downloading."""
    
    @pytest.fixture
    def temp_vendor_dir(self, tmp_path: Path) -> Path:
        """Create a temporary vendor directory."""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        return vendor_dir
    
    def test_download_skips_existing(self, temp_vendor_dir: Path) -> None:
        """Test that download skips existing files."""
        # Create existing file
        existing = temp_vendor_dir / "test.js"
        existing.write_text("existing content")
        
        asset = VendorAsset(
            name="Test",
            url="https://example.com/test.js",
            filename="test.js",
            sha256="",
            size_kb=10,
        )
        
        result = download_asset(asset, temp_vendor_dir)
        
        assert result is True
        assert existing.read_text() == "existing content"  # Not overwritten
    
    @patch("urllib.request.urlopen")
    def test_download_creates_file(
        self,
        mock_urlopen: MagicMock,
        temp_vendor_dir: Path,
    ) -> None:
        """Test that download creates new file."""
        # Mock response
        mock_response = MagicMock()
        mock_response.read.return_value = b"console.log('test');"
        mock_response.__enter__ = MagicMock(return_value=mock_response)
        mock_response.__exit__ = MagicMock(return_value=False)
        mock_urlopen.return_value = mock_response
        
        asset = VendorAsset(
            name="Test",
            url="https://example.com/new.js",
            filename="new.js",
            sha256="",
            size_kb=1,
        )
        
        result = download_asset(asset, temp_vendor_dir)
        
        assert result is True
        assert (temp_vendor_dir / "new.js").exists()
    
    @patch("urllib.request.urlopen")
    def test_download_handles_error(
        self,
        mock_urlopen: MagicMock,
        temp_vendor_dir: Path,
    ) -> None:
        """Test that download handles network errors."""
        mock_urlopen.side_effect = Exception("Network error")
        
        asset = VendorAsset(
            name="Test",
            url="https://example.com/error.js",
            filename="error.js",
            sha256="",
            size_kb=1,
        )
        
        result = download_asset(asset, temp_vendor_dir)
        
        assert result is False
        assert not (temp_vendor_dir / "error.js").exists()


class TestBundleVendorAssets:
    """Tests for full bundle operation."""
    
    @pytest.fixture
    def temp_vendor_dir(self, tmp_path: Path) -> Path:
        """Create a temporary vendor directory."""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        return vendor_dir
    
    def test_bundle_creates_tailwind(self, temp_vendor_dir: Path) -> None:
        """Test that bundle creates Tailwind CSS."""
        # Pre-create JS files to skip download
        for asset in VENDOR_ASSETS:
            (temp_vendor_dir / asset.filename).write_text("// mocked")
        
        results = bundle_vendor_assets(temp_vendor_dir)
        
        assert "Tailwind CSS" in results
        assert results["Tailwind CSS"] is True
        assert (temp_vendor_dir / "tailwind-3.4.0.min.css").exists()
    
    def test_bundle_returns_all_results(self, temp_vendor_dir: Path) -> None:
        """Test that bundle returns results for all assets."""
        # Pre-create JS files to skip download
        for asset in VENDOR_ASSETS:
            (temp_vendor_dir / asset.filename).write_text("// mocked")
        
        results = bundle_vendor_assets(temp_vendor_dir)
        
        expected_count = len(VENDOR_ASSETS) + 1  # +1 for Tailwind
        assert len(results) == expected_count


class TestVerifyVendorAssets:
    """Tests for asset verification."""
    
    @pytest.fixture
    def temp_vendor_dir(self, tmp_path: Path) -> Path:
        """Create a temporary vendor directory."""
        vendor_dir = tmp_path / "vendor"
        vendor_dir.mkdir()
        return vendor_dir
    
    def test_verify_empty_directory(self, temp_vendor_dir: Path) -> None:
        """Test verification of empty directory."""
        results = verify_vendor_assets(temp_vendor_dir)
        
        assert all(v is False for v in results.values())
    
    def test_verify_with_all_assets(self, temp_vendor_dir: Path) -> None:
        """Test verification with all assets present."""
        # Create all expected files
        for asset in VENDOR_ASSETS:
            (temp_vendor_dir / asset.filename).write_text("// mocked")
        (temp_vendor_dir / "tailwind-3.4.0.min.css").write_text("/* css */")
        
        results = verify_vendor_assets(temp_vendor_dir)
        
        assert all(v is True for v in results.values())
    
    def test_verify_partial_assets(self, temp_vendor_dir: Path) -> None:
        """Test verification with some assets missing."""
        # Create only Alpine.js
        (temp_vendor_dir / "alpine-3.13.3.min.js").write_text("// alpine")
        
        results = verify_vendor_assets(temp_vendor_dir)
        
        assert results.get("Alpine.js") is True
        # Other assets should be False
        assert any(v is False for v in results.values())


class TestActualVendorDirectory:
    """Integration tests for actual vendor directory."""
    
    def test_vendor_assets_are_bundled(self) -> None:
        """Test that vendor assets exist in actual location."""
        vendor_dir = get_vendor_dir()
        
        if not vendor_dir.exists():
            pytest.skip("Vendor directory not created yet")
        
        results = verify_vendor_assets(vendor_dir)
        
        # At least some assets should be present after bundling
        assert any(v is True for v in results.values())
