"""
SPA Dependency Bundler for LENS Dashboard.

Downloads and bundles frontend dependencies locally to create a self-contained
Single Page Application with zero external CDN dependencies.

Dependencies:
- Alpine.js 3.13.3 (15KB)
- D3.js v7.8.5 (250KB)
- Mermaid.js v10.6.1 (850KB)
- Tailwind CSS 3.4.0 (~100KB)

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
Task: 016 - SPA Dependency Bundling Script
AC-ID: LENS-DASH-016
"""

import hashlib
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Optional


@dataclass
class Dependency:
    """
    Frontend dependency specification.

    Attributes:
        name: Dependency name (e.g., "alpine", "d3")
        version: Version string (e.g., "3.13.3")
        url: CDN URL to download from
        filename: Local filename to save as
        sha256: Expected SHA-256 checksum for integrity verification
        size_kb: Approximate size in kilobytes
    """

    name: str
    version: str
    url: str
    filename: str
    sha256: str
    size_kb: int


class DependencyBundler:
    """
    Downloads and bundles frontend dependencies locally.

    Ensures dashboard works offline without external CDN calls.

    Example:
        ```python
        bundler = DependencyBundler(output_dir=Path("static/vendor"))
        result = bundler.bundle_all()
        print(f"Downloaded {result['downloaded']} dependencies")
        ```
    """

    # Dependency specifications with CDN URLs and checksums
    DEPENDENCIES: Dict[str, Dependency] = {
        "alpine": Dependency(
            name="alpine",
            version="3.13.3",
            url="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js",
            filename="alpine-3.13.3.min.js",
            sha256="",  # To be filled with actual checksum
            size_kb=15,
        ),
        "d3": Dependency(
            name="d3",
            version="7.8.5",
            url="https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js",
            filename="d3-7.8.5.min.js",
            sha256="",  # To be filled with actual checksum
            size_kb=250,
        ),
        "mermaid": Dependency(
            name="mermaid",
            version="10.6.1",
            url="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js",
            filename="mermaid-10.6.1.min.js",
            sha256="",  # To be filled with actual checksum
            size_kb=850,
        ),
        "tailwind": Dependency(
            name="tailwind",
            version="3.4.0",
            url="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.0/dist/tailwind.min.css",
            filename="tailwind-3.4.0.min.css",
            sha256="",  # To be filled with actual checksum
            size_kb=100,
        ),
    }

    def __init__(self, output_dir: Path) -> None:
        """
        Initialize bundler.

        Args:
            output_dir: Directory to save bundled dependencies
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def download_dependency(self, dep: Dependency) -> Dict[str, any]:
        """
        Download a single dependency from CDN.

        Args:
            dep: Dependency specification

        Returns:
            Dictionary with download results:
                - success: bool
                - path: Path to downloaded file
                - size: File size in bytes
                - checksum: Computed SHA-256 checksum
                - error: Optional error message

        Example:
            ```python
            bundler = DependencyBundler(Path("static/vendor"))
            result = bundler.download_dependency(bundler.DEPENDENCIES["alpine"])
            if result["success"]:
                print(f"Downloaded to {result['path']}")
            ```
        """
        output_path = self.output_dir / dep.filename

        try:
            # Download file
            urllib.request.urlretrieve(dep.url, output_path)

            # Verify file exists and get size
            if not output_path.exists():
                return {
                    "success": False,
                    "error": f"File not found after download: {output_path}",
                }

            file_size = output_path.stat().st_size

            # Compute checksum
            checksum = self._compute_checksum(output_path)

            # Verify checksum if provided
            if dep.sha256 and checksum != dep.sha256:
                output_path.unlink()  # Delete corrupted file
                return {
                    "success": False,
                    "error": f"Checksum mismatch: expected {dep.sha256}, got {checksum}",
                }

            return {
                "success": True,
                "path": output_path,
                "size": file_size,
                "checksum": checksum,
            }

        except Exception as e:
            return {"success": False, "error": str(e)}

    def bundle_all(self) -> Dict[str, any]:
        """
        Download and bundle all frontend dependencies.

        Returns:
            Dictionary with bundling results:
                - success: bool
                - downloaded: Number of successfully downloaded dependencies
                - failed: Number of failed downloads
                - total_size: Total size in bytes
                - dependencies: Dict mapping dependency name to download result

        Example:
            ```python
            bundler = DependencyBundler(Path("static/vendor"))
            result = bundler.bundle_all()

            if result["success"]:
                print(f"Bundle complete: {result['downloaded']} files")
                print(f"Total size: {result['total_size'] / 1024:.1f} KB")
            else:
                print(f"Bundle failed: {result['failed']} errors")
            ```
        """
        results = {}
        downloaded = 0
        failed = 0
        total_size = 0

        for name, dep in self.DEPENDENCIES.items():
            result = self.download_dependency(dep)
            results[name] = result

            if result["success"]:
                downloaded += 1
                total_size += result["size"]
            else:
                failed += 1

        return {
            "success": failed == 0,
            "downloaded": downloaded,
            "failed": failed,
            "total_size": total_size,
            "dependencies": results,
        }

    def verify_bundle(self) -> Dict[str, bool]:
        """
        Verify all bundled dependencies exist and have correct checksums.

        Returns:
            Dictionary mapping dependency name to verification status

        Example:
            ```python
            bundler = DependencyBundler(Path("static/vendor"))
            verification = bundler.verify_bundle()

            for name, valid in verification.items():
                status = "✓" if valid else "✗"
                print(f"{status} {name}")
            ```
        """
        verification = {}

        for name, dep in self.DEPENDENCIES.items():
            file_path = self.output_dir / dep.filename

            if not file_path.exists():
                verification[name] = False
                continue

            # Verify checksum if provided
            if dep.sha256:
                checksum = self._compute_checksum(file_path)
                verification[name] = checksum == dep.sha256
            else:
                # No checksum provided, just verify file exists
                verification[name] = True

        return verification

    def clean_bundle(self) -> int:
        """
        Remove all bundled dependencies.

        Returns:
            Number of files removed

        Example:
            ```python
            bundler = DependencyBundler(Path("static/vendor"))
            removed = bundler.clean_bundle()
            print(f"Removed {removed} files")
            ```
        """
        removed = 0

        for dep in self.DEPENDENCIES.values():
            file_path = self.output_dir / dep.filename
            if file_path.exists():
                file_path.unlink()
                removed += 1

        return removed

    def _compute_checksum(self, file_path: Path) -> str:
        """
        Compute SHA-256 checksum of file.

        Args:
            file_path: Path to file

        Returns:
            Hex-encoded SHA-256 checksum
        """
        sha256 = hashlib.sha256()

        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256.update(chunk)

        return sha256.hexdigest()


def bundle_dependencies(output_dir: Path) -> Dict[str, any]:
    """
    Convenience function to bundle all dependencies.

    Args:
        output_dir: Directory to save bundled dependencies

    Returns:
        Bundling result dictionary

    Example:
        ```python
        from pathlib import Path
        from cortex.visualization.spa.dependency_bundler import bundle_dependencies

        result = bundle_dependencies(Path("cortex/visualization/static/vendor"))
        print(f"Downloaded {result['downloaded']} dependencies")
        ```
    """
    bundler = DependencyBundler(output_dir)
    return bundler.bundle_all()
