"""
Dependency Bundling Script for Self-Contained LENS Dashboard.

Downloads and bundles all external dependencies locally for offline operation:
- Alpine.js 3.13.3 (15KB reactive framework)
- D3.js 7.8.5 (250KB visualization library)
- Mermaid 10.6.1 (850KB diagram library)
- Tailwind CSS 3.4.0 (standalone CSS framework)

All assets stored in cortex/visualization/static/vendor/ with SHA-256 checksums.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-007
Task: 018 - Dependency Bundling
"""

import hashlib
import json
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Dict, List, Optional
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError


@dataclass
class DependencyAsset:
    """
    Represents a single downloadable asset.
    
    Attributes:
        name: Human-readable name (e.g., "Alpine.js")
        version: Semantic version (e.g., "3.13.3")
        url: Download URL
        filename: Local filename to save as
        expected_checksum: SHA-256 checksum for verification
        size_kb: Expected file size in KB
    """
    name: str
    version: str
    url: str
    filename: str
    expected_checksum: str
    size_kb: int


# Dependency catalog with CDN URLs and checksums
DEPENDENCIES: List[DependencyAsset] = [
    DependencyAsset(
        name="Alpine.js",
        version="3.13.3",
        url="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js",
        filename="alpine-3.13.3.min.js",
        expected_checksum="",  # Will be computed on first download
        size_kb=15,
    ),
    DependencyAsset(
        name="D3.js",
        version="7.8.5",
        url="https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js",
        filename="d3-7.8.5.min.js",
        expected_checksum="",
        size_kb=250,
    ),
    DependencyAsset(
        name="Mermaid",
        version="10.6.1",
        url="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js",
        filename="mermaid-10.6.1.min.js",
        expected_checksum="",
        size_kb=850,
    ),
    DependencyAsset(
        name="Tailwind CSS",
        version="3.4.0",
        url="https://cdn.jsdelivr.net/npm/tailwindcss@3.4.0/dist/tailwind.min.css",
        filename="tailwind-3.4.0.min.css",
        expected_checksum="",
        size_kb=80,
    ),
]


class DependencyBundler:
    """
    Downloads and bundles external dependencies for offline dashboard operation.
    
    Features:
    - Downloads from CDN with retry logic
    - Verifies SHA-256 checksums
    - Saves checksums manifest for future verification
    - Detects already-downloaded assets
    - Provides progress feedback
    
    Example:
        ```python
        bundler = DependencyBundler()
        bundler.download_all_dependencies()
        
        # Verify existing bundle
        is_valid = bundler.verify_bundle_integrity()
        ```
    """
    
    def __init__(self, vendor_dir: Optional[Path] = None):
        """
        Initialize dependency bundler.
        
        Args:
            vendor_dir: Path to vendor directory (default: cortex/visualization/static/vendor/)
        """
        if vendor_dir is None:
            # Default to cortex/visualization/static/vendor/
            script_dir = Path(__file__).parent
            vendor_dir = script_dir.parent / "static" / "vendor"
        
        self.vendor_dir = vendor_dir
        self.checksums_file = vendor_dir / ".checksums.json"
        self.user_agent = "CORTEX-LENS-Dashboard/1.0"
    
    def download_all_dependencies(self, force: bool = False) -> Dict[str, bool]:
        """
        Download all dependencies from CDN.
        
        Args:
            force: If True, re-download even if files exist
        
        Returns:
            Dict mapping asset name to success status
        """
        self.vendor_dir.mkdir(parents=True, exist_ok=True)
        
        results = {}
        for asset in DEPENDENCIES:
            print(f"📦 Downloading {asset.name} v{asset.version}...")
            
            file_path = self.vendor_dir / asset.filename
            
            # Skip if already exists and not forcing
            if file_path.exists() and not force:
                print(f"   ✅ Already exists: {asset.filename}")
                results[asset.name] = True
                continue
            
            try:
                content = self._download_asset(asset)
                checksum = self._compute_checksum(content)
                
                # Write to file
                file_path.write_bytes(content)
                
                # Verify checksum if expected is set
                if asset.expected_checksum:
                    if checksum != asset.expected_checksum:
                        raise ValueError(
                            f"Checksum mismatch for {asset.name}!\n"
                            f"Expected: {asset.expected_checksum}\n"
                            f"Got: {checksum}"
                        )
                
                size_kb = len(content) / 1024
                print(f"   ✅ Downloaded: {asset.filename} ({size_kb:.1f} KB)")
                print(f"   🔐 SHA-256: {checksum[:16]}...")
                
                results[asset.name] = True
                
            except Exception as e:
                print(f"   ❌ Failed: {e}")
                results[asset.name] = False
        
        # Save checksums manifest
        self._save_checksums_manifest()
        
        return results
    
    def _download_asset(self, asset: DependencyAsset, retries: int = 3) -> bytes:
        """
        Download asset from URL with retry logic.
        
        Args:
            asset: Asset to download
            retries: Number of retry attempts
        
        Returns:
            Downloaded content as bytes
        
        Raises:
            URLError: If download fails after retries
        """
        for attempt in range(retries):
            try:
                request = Request(asset.url, headers={"User-Agent": self.user_agent})
                with urlopen(request, timeout=30) as response:
                    return response.read()
            
            except (URLError, HTTPError) as e:
                if attempt == retries - 1:
                    raise URLError(f"Failed to download after {retries} attempts: {e}")
                print(f"   ⚠️  Retry {attempt + 1}/{retries}...")
        
        raise URLError("Download failed (should not reach here)")
    
    def _compute_checksum(self, content: bytes) -> str:
        """
        Compute SHA-256 checksum of content.
        
        Args:
            content: Bytes to checksum
        
        Returns:
            Hex-encoded SHA-256 checksum
        """
        return hashlib.sha256(content).hexdigest()
    
    def _save_checksums_manifest(self) -> None:
        """Save checksums manifest for all downloaded assets."""
        manifest = {}
        
        for asset in DEPENDENCIES:
            file_path = self.vendor_dir / asset.filename
            if file_path.exists():
                content = file_path.read_bytes()
                checksum = self._compute_checksum(content)
                manifest[asset.filename] = {
                    "name": asset.name,
                    "version": asset.version,
                    "checksum": checksum,
                    "size_bytes": len(content),
                }
        
        self.checksums_file.write_text(json.dumps(manifest, indent=2))
        print(f"\n💾 Checksums saved to: {self.checksums_file}")
    
    def verify_bundle_integrity(self) -> bool:
        """
        Verify integrity of existing bundle against checksums manifest.
        
        Returns:
            True if all files match checksums, False otherwise
        """
        if not self.checksums_file.exists():
            print("❌ No checksums manifest found. Run download first.")
            return False
        
        manifest = json.loads(self.checksums_file.read_text())
        all_valid = True
        
        print("🔍 Verifying bundle integrity...")
        
        for filename, info in manifest.items():
            file_path = self.vendor_dir / filename
            
            if not file_path.exists():
                print(f"   ❌ Missing: {filename}")
                all_valid = False
                continue
            
            content = file_path.read_bytes()
            checksum = self._compute_checksum(content)
            
            if checksum == info["checksum"]:
                print(f"   ✅ Valid: {filename}")
            else:
                print(f"   ❌ Corrupted: {filename}")
                all_valid = False
        
        return all_valid
    
    def list_bundled_dependencies(self) -> List[Dict[str, str]]:
        """
        List all bundled dependencies with metadata.
        
        Returns:
            List of dependency info dicts
        """
        if not self.checksums_file.exists():
            return []
        
        manifest = json.loads(self.checksums_file.read_text())
        return [
            {
                "filename": filename,
                "name": info["name"],
                "version": info["version"],
                "size_kb": f"{info['size_bytes'] / 1024:.1f}",
                "checksum": info["checksum"][:16] + "...",
            }
            for filename, info in manifest.items()
        ]


def bundle_dependencies(force: bool = False) -> bool:
    """
    Convenience function to download all dependencies.
    
    Args:
        force: If True, re-download even if files exist
    
    Returns:
        True if all downloads succeeded, False otherwise
    """
    bundler = DependencyBundler()
    results = bundler.download_all_dependencies(force=force)
    success_count = sum(results.values())
    total_count = len(results)
    
    print(f"\n📊 Summary: {success_count}/{total_count} dependencies downloaded")
    
    return all(results.values())


def verify_bundle() -> bool:
    """
    Convenience function to verify bundle integrity.
    
    Returns:
        True if bundle is valid, False otherwise
    """
    bundler = DependencyBundler()
    return bundler.verify_bundle_integrity()


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        # Verify existing bundle
        is_valid = verify_bundle()
        sys.exit(0 if is_valid else 1)
    else:
        # Download dependencies
        force = "--force" in sys.argv
        success = bundle_dependencies(force=force)
        sys.exit(0 if success else 1)
