"""
Tests for SPA Dependency Bundler.

Phase: 14 - LENS Dashboard
Task: 016 - SPA Dependency Bundling Script
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

import pytest

from cortex.visualization.spa.dependency_bundler import (
    DependencyBundler,
    Dependency,
    bundle_dependencies,
)


class TestDependency:
    """Test Dependency dataclass."""

    def test_dependency_creation(self) -> None:
        """Test creating dependency specification."""
        dep = Dependency(
            name="alpine",
            version="3.13.3",
            url="https://cdn.example.com/alpine.min.js",
            filename="alpine-3.13.3.min.js",
            sha256="abc123",
            size_kb=15,
        )

        assert dep.name == "alpine"
        assert dep.version == "3.13.3"
        assert dep.filename == "alpine-3.13.3.min.js"
        assert dep.size_kb == 15


class TestDependencyBundler:
    """Test DependencyBundler class."""

    def test_initialization(self, tmp_path: Path) -> None:
        """Test bundler initialization."""
        output_dir = tmp_path / "vendor"
        bundler = DependencyBundler(output_dir=output_dir)

        assert bundler.output_dir == output_dir
        assert output_dir.exists()

    def test_dependencies_defined(self) -> None:
        """Test all required dependencies are defined."""
        assert "alpine" in DependencyBundler.DEPENDENCIES
        assert "d3" in DependencyBundler.DEPENDENCIES
        assert "mermaid" in DependencyBundler.DEPENDENCIES
        assert "tailwind" in DependencyBundler.DEPENDENCIES

    def test_alpine_dependency_spec(self) -> None:
        """Test Alpine.js dependency specification."""
        alpine = DependencyBundler.DEPENDENCIES["alpine"]

        assert alpine.name == "alpine"
        assert alpine.version == "3.13.3"
        assert "alpine" in alpine.url.lower()
        assert alpine.filename == "alpine-3.13.3.min.js"

    def test_d3_dependency_spec(self) -> None:
        """Test D3.js dependency specification."""
        d3 = DependencyBundler.DEPENDENCIES["d3"]

        assert d3.name == "d3"
        assert d3.version == "7.8.5"
        assert "d3" in d3.url.lower()
        assert d3.filename == "d3-7.8.5.min.js"

    def test_mermaid_dependency_spec(self) -> None:
        """Test Mermaid.js dependency specification."""
        mermaid = DependencyBundler.DEPENDENCIES["mermaid"]

        assert mermaid.name == "mermaid"
        assert mermaid.version == "10.6.1"
        assert "mermaid" in mermaid.url.lower()
        assert mermaid.filename == "mermaid-10.6.1.min.js"

    def test_tailwind_dependency_spec(self) -> None:
        """Test Tailwind CSS dependency specification."""
        tailwind = DependencyBundler.DEPENDENCIES["tailwind"]

        assert tailwind.name == "tailwind"
        assert tailwind.version == "3.4.0"
        assert "tailwind" in tailwind.url.lower()
        assert tailwind.filename == "tailwind-3.4.0.min.css"

    @patch("urllib.request.urlretrieve")
    def test_download_dependency_success(
        self, mock_urlretrieve: Mock, tmp_path: Path
    ) -> None:
        """Test successful dependency download."""
        bundler = DependencyBundler(output_dir=tmp_path)

        dep = Dependency(
            name="test",
            version="1.0.0",
            url="https://example.com/test.js",
            filename="test-1.0.0.js",
            sha256="",  # No checksum verification
            size_kb=10,
        )

        # Mock file creation
        output_file = tmp_path / dep.filename
        output_file.write_text("console.log('test');")

        result = bundler.download_dependency(dep)

        assert result["success"] is True
        assert result["path"] == output_file
        assert result["size"] > 0
        assert "checksum" in result

    @patch("urllib.request.urlretrieve")
    def test_download_dependency_file_not_found(
        self, mock_urlretrieve: Mock, tmp_path: Path
    ) -> None:
        """Test download fails if file not created."""
        bundler = DependencyBundler(output_dir=tmp_path)

        dep = Dependency(
            name="test",
            version="1.0.0",
            url="https://example.com/test.js",
            filename="nonexistent.js",
            sha256="",
            size_kb=10,
        )

        result = bundler.download_dependency(dep)

        assert result["success"] is False
        assert "error" in result

    @patch("urllib.request.urlretrieve")
    def test_download_dependency_checksum_mismatch(
        self, mock_urlretrieve: Mock, tmp_path: Path
    ) -> None:
        """Test download fails on checksum mismatch."""
        bundler = DependencyBundler(output_dir=tmp_path)

        dep = Dependency(
            name="test",
            version="1.0.0",
            url="https://example.com/test.js",
            filename="test-1.0.0.js",
            sha256="invalid_checksum_12345",
            size_kb=10,
        )

        # Mock file creation
        output_file = tmp_path / dep.filename
        output_file.write_text("console.log('test');")

        result = bundler.download_dependency(dep)

        assert result["success"] is False
        assert "checksum mismatch" in result["error"].lower()

    @patch("urllib.request.urlretrieve")
    def test_download_dependency_network_error(
        self, mock_urlretrieve: Mock, tmp_path: Path
    ) -> None:
        """Test download handles network errors."""
        bundler = DependencyBundler(output_dir=tmp_path)

        dep = Dependency(
            name="test",
            version="1.0.0",
            url="https://example.com/test.js",
            filename="test-1.0.0.js",
            sha256="",
            size_kb=10,
        )

        # Simulate network error
        mock_urlretrieve.side_effect = Exception("Network error")

        result = bundler.download_dependency(dep)

        assert result["success"] is False
        assert "error" in result

    @patch.object(DependencyBundler, "download_dependency")
    def test_bundle_all_success(
        self, mock_download: Mock, tmp_path: Path
    ) -> None:
        """Test bundling all dependencies successfully."""
        bundler = DependencyBundler(output_dir=tmp_path)

        # Mock successful downloads
        mock_download.return_value = {
            "success": True,
            "path": tmp_path / "test.js",
            "size": 1024,
            "checksum": "abc123",
        }

        result = bundler.bundle_all()

        assert result["success"] is True
        assert result["downloaded"] == 4  # alpine, d3, mermaid, tailwind
        assert result["failed"] == 0
        assert result["total_size"] > 0

    @patch.object(DependencyBundler, "download_dependency")
    def test_bundle_all_partial_failure(
        self, mock_download: Mock, tmp_path: Path
    ) -> None:
        """Test bundling with some failures."""
        bundler = DependencyBundler(output_dir=tmp_path)

        # Mock mixed results
        call_count = 0

        def side_effect(*args, **kwargs):
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                return {"success": False, "error": "Network error"}
            return {
                "success": True,
                "path": tmp_path / "test.js",
                "size": 1024,
                "checksum": "abc123",
            }

        mock_download.side_effect = side_effect

        result = bundler.bundle_all()

        assert result["success"] is False
        assert result["downloaded"] == 3
        assert result["failed"] == 1

    def test_verify_bundle_all_present(self, tmp_path: Path) -> None:
        """Test verifying bundle when all files present."""
        bundler = DependencyBundler(output_dir=tmp_path)

        # Create mock files
        for dep in bundler.DEPENDENCIES.values():
            file_path = tmp_path / dep.filename
            file_path.write_text("mock content")

        verification = bundler.verify_bundle()

        assert all(verification.values())
        assert len(verification) == 4

    def test_verify_bundle_missing_files(self, tmp_path: Path) -> None:
        """Test verifying bundle with missing files."""
        bundler = DependencyBundler(output_dir=tmp_path)

        # Create only some files
        alpine_file = tmp_path / "alpine-3.13.3.min.js"
        alpine_file.write_text("mock content")

        verification = bundler.verify_bundle()

        assert verification["alpine"] is True
        assert verification["d3"] is False
        assert verification["mermaid"] is False
        assert verification["tailwind"] is False

    def test_clean_bundle(self, tmp_path: Path) -> None:
        """Test cleaning bundled dependencies."""
        bundler = DependencyBundler(output_dir=tmp_path)

        # Create mock files
        for dep in bundler.DEPENDENCIES.values():
            file_path = tmp_path / dep.filename
            file_path.write_text("mock content")

        # Verify files exist
        assert all(
            (tmp_path / dep.filename).exists()
            for dep in bundler.DEPENDENCIES.values()
        )

        # Clean bundle
        removed = bundler.clean_bundle()

        assert removed == 4
        assert not any(
            (tmp_path / dep.filename).exists()
            for dep in bundler.DEPENDENCIES.values()
        )

    def test_clean_bundle_no_files(self, tmp_path: Path) -> None:
        """Test cleaning when no files exist."""
        bundler = DependencyBundler(output_dir=tmp_path)

        removed = bundler.clean_bundle()

        assert removed == 0

    def test_compute_checksum(self, tmp_path: Path) -> None:
        """Test SHA-256 checksum computation."""
        bundler = DependencyBundler(output_dir=tmp_path)

        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")

        checksum = bundler._compute_checksum(test_file)

        # Verify checksum format
        assert len(checksum) == 64  # SHA-256 hex length
        assert all(c in "0123456789abcdef" for c in checksum)

    def test_compute_checksum_deterministic(self, tmp_path: Path) -> None:
        """Test checksum is deterministic."""
        bundler = DependencyBundler(output_dir=tmp_path)

        # Create test file
        test_file = tmp_path / "test.txt"
        test_file.write_text("Same content")

        checksum1 = bundler._compute_checksum(test_file)
        checksum2 = bundler._compute_checksum(test_file)

        assert checksum1 == checksum2


class TestConvenienceFunction:
    """Test convenience function."""

    @patch.object(DependencyBundler, "bundle_all")
    def test_bundle_dependencies(
        self, mock_bundle_all: Mock, tmp_path: Path
    ) -> None:
        """Test bundle_dependencies convenience function."""
        mock_bundle_all.return_value = {
            "success": True,
            "downloaded": 4,
            "failed": 0,
            "total_size": 1024 * 1024,
        }

        result = bundle_dependencies(tmp_path)

        assert result["success"] is True
        assert result["downloaded"] == 4
        mock_bundle_all.assert_called_once()
