#!/usr/bin/env python3
"""Vendor Asset Bundler for LENS Dashboard.

Downloads and bundles JavaScript/CSS dependencies for offline
operation (self-contained SPA requirement).

Assets:
    - Alpine.js 3.13.3 (15KB) - Reactive UI framework
    - D3.js 7.8.5 (250KB) - Data visualization
    - Mermaid 10.6.1 (850KB) - Diagram generation
    - Tailwind CSS 3.4.0 (CDN-compiled) - Styling

Usage:
    python -m cortex.visualization.scripts.bundle_vendor_assets
    
    Or via CLI:
    cortex lens vendor bundle
"""

import hashlib
import logging
import urllib.request
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VendorAsset(NamedTuple):
    """Definition of a vendor asset to download."""
    name: str
    url: str
    filename: str
    sha256: str  # Expected hash for integrity check
    size_kb: int  # Approximate size for progress display


# Vendor assets to download
VENDOR_ASSETS: List[VendorAsset] = [
    VendorAsset(
        name="Alpine.js",
        url="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js",
        filename="alpine-3.13.3.min.js",
        sha256="",  # Skip hash check for now
        size_kb=15,
    ),
    VendorAsset(
        name="D3.js",
        url="https://cdn.jsdelivr.net/npm/d3@7.8.5/dist/d3.min.js",
        filename="d3-7.8.5.min.js",
        sha256="",
        size_kb=250,
    ),
    VendorAsset(
        name="Mermaid",
        url="https://cdn.jsdelivr.net/npm/mermaid@10.6.1/dist/mermaid.min.js",
        filename="mermaid-10.6.1.min.js",
        sha256="",
        size_kb=850,
    ),
]


# Tailwind CSS (standalone compiled version for offline use)
TAILWIND_CSS = """/* Tailwind CSS - Minimal subset for LENS Dashboard */
/* Generated for offline use - includes only required utilities */

*, ::before, ::after {
  box-sizing: border-box;
  border-width: 0;
  border-style: solid;
  border-color: #e5e7eb;
}

html {
  line-height: 1.5;
  -webkit-text-size-adjust: 100%;
  font-family: ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
}

body {
  margin: 0;
  line-height: inherit;
}

/* Layout */
.container { width: 100%; margin-right: auto; margin-left: auto; padding-right: 1rem; padding-left: 1rem; }
.flex { display: flex; }
.flex-col { flex-direction: column; }
.flex-wrap { flex-wrap: wrap; }
.items-center { align-items: center; }
.justify-center { justify-content: center; }
.justify-between { justify-content: space-between; }
.gap-2 { gap: 0.5rem; }
.gap-4 { gap: 1rem; }
.gap-6 { gap: 1.5rem; }

/* Grid */
.grid { display: grid; }
.grid-cols-1 { grid-template-columns: repeat(1, minmax(0, 1fr)); }
.grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
.grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
.grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }

/* Spacing */
.p-2 { padding: 0.5rem; }
.p-4 { padding: 1rem; }
.p-6 { padding: 1.5rem; }
.px-4 { padding-left: 1rem; padding-right: 1rem; }
.py-2 { padding-top: 0.5rem; padding-bottom: 0.5rem; }
.py-4 { padding-top: 1rem; padding-bottom: 1rem; }
.m-0 { margin: 0; }
.m-2 { margin: 0.5rem; }
.m-4 { margin: 1rem; }
.mt-2 { margin-top: 0.5rem; }
.mt-4 { margin-top: 1rem; }
.mb-2 { margin-bottom: 0.5rem; }
.mb-4 { margin-bottom: 1rem; }
.ml-2 { margin-left: 0.5rem; }
.mr-2 { margin-right: 0.5rem; }

/* Sizing */
.w-full { width: 100%; }
.h-full { height: 100%; }
.min-h-screen { min-height: 100vh; }
.max-w-7xl { max-width: 80rem; }

/* Typography */
.text-xs { font-size: 0.75rem; line-height: 1rem; }
.text-sm { font-size: 0.875rem; line-height: 1.25rem; }
.text-base { font-size: 1rem; line-height: 1.5rem; }
.text-lg { font-size: 1.125rem; line-height: 1.75rem; }
.text-xl { font-size: 1.25rem; line-height: 1.75rem; }
.text-2xl { font-size: 1.5rem; line-height: 2rem; }
.text-3xl { font-size: 1.875rem; line-height: 2.25rem; }
.font-medium { font-weight: 500; }
.font-semibold { font-weight: 600; }
.font-bold { font-weight: 700; }
.text-center { text-align: center; }
.text-left { text-align: left; }
.text-right { text-align: right; }

/* Colors */
.text-white { color: #ffffff; }
.text-gray-400 { color: #9ca3af; }
.text-gray-500 { color: #6b7280; }
.text-gray-600 { color: #4b5563; }
.text-gray-700 { color: #374151; }
.text-gray-800 { color: #1f2937; }
.text-gray-900 { color: #111827; }
.text-blue-500 { color: #3b82f6; }
.text-blue-600 { color: #2563eb; }
.text-green-500 { color: #22c55e; }
.text-green-600 { color: #16a34a; }
.text-red-500 { color: #ef4444; }
.text-red-600 { color: #dc2626; }
.text-yellow-500 { color: #eab308; }

.bg-white { background-color: #ffffff; }
.bg-gray-50 { background-color: #f9fafb; }
.bg-gray-100 { background-color: #f3f4f6; }
.bg-gray-200 { background-color: #e5e7eb; }
.bg-gray-800 { background-color: #1f2937; }
.bg-gray-900 { background-color: #111827; }
.bg-blue-500 { background-color: #3b82f6; }
.bg-blue-600 { background-color: #2563eb; }
.bg-green-500 { background-color: #22c55e; }
.bg-red-500 { background-color: #ef4444; }

/* Borders */
.border { border-width: 1px; }
.border-2 { border-width: 2px; }
.border-gray-200 { border-color: #e5e7eb; }
.border-gray-300 { border-color: #d1d5db; }
.rounded { border-radius: 0.25rem; }
.rounded-md { border-radius: 0.375rem; }
.rounded-lg { border-radius: 0.5rem; }
.rounded-xl { border-radius: 0.75rem; }
.rounded-full { border-radius: 9999px; }

/* Shadows */
.shadow { box-shadow: 0 1px 3px 0 rgb(0 0 0 / 0.1), 0 1px 2px -1px rgb(0 0 0 / 0.1); }
.shadow-md { box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1), 0 2px 4px -2px rgb(0 0 0 / 0.1); }
.shadow-lg { box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1); }
.shadow-xl { box-shadow: 0 20px 25px -5px rgb(0 0 0 / 0.1), 0 8px 10px -6px rgb(0 0 0 / 0.1); }

/* Effects */
.opacity-0 { opacity: 0; }
.opacity-50 { opacity: 0.5; }
.opacity-75 { opacity: 0.75; }
.opacity-100 { opacity: 1; }
.transition { transition-property: all; transition-timing-function: cubic-bezier(0.4, 0, 0.2, 1); transition-duration: 150ms; }
.duration-200 { transition-duration: 200ms; }
.duration-300 { transition-duration: 300ms; }

/* Interactivity */
.cursor-pointer { cursor: pointer; }
.select-none { user-select: none; }
.hover\\:bg-gray-100:hover { background-color: #f3f4f6; }
.hover\\:bg-blue-600:hover { background-color: #2563eb; }
.hover\\:text-blue-600:hover { color: #2563eb; }
.hover\\:shadow-lg:hover { box-shadow: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1); }
.focus\\:outline-none:focus { outline: 2px solid transparent; outline-offset: 2px; }
.focus\\:ring-2:focus { box-shadow: 0 0 0 2px #3b82f6; }

/* Display */
.hidden { display: none; }
.block { display: block; }
.inline { display: inline; }
.inline-block { display: inline-block; }
.overflow-hidden { overflow: hidden; }
.overflow-auto { overflow: auto; }

/* Position */
.relative { position: relative; }
.absolute { position: absolute; }
.fixed { position: fixed; }
.sticky { position: sticky; }
.top-0 { top: 0; }
.right-0 { right: 0; }
.bottom-0 { bottom: 0; }
.left-0 { left: 0; }
.z-10 { z-index: 10; }
.z-50 { z-index: 50; }

/* Glassmorphism */
.glass-panel {
  background: rgba(255, 255, 255, 0.7);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.75rem;
  box-shadow: 0 4px 6px -1px rgb(0 0 0 / 0.1);
}

.glass-panel-dark {
  background: rgba(31, 41, 55, 0.8);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 0.75rem;
}

/* Responsive */
@media (min-width: 640px) {
  .sm\\:grid-cols-2 { grid-template-columns: repeat(2, minmax(0, 1fr)); }
  .sm\\:px-6 { padding-left: 1.5rem; padding-right: 1.5rem; }
}

@media (min-width: 768px) {
  .md\\:grid-cols-3 { grid-template-columns: repeat(3, minmax(0, 1fr)); }
  .md\\:flex-row { flex-direction: row; }
}

@media (min-width: 1024px) {
  .lg\\:grid-cols-4 { grid-template-columns: repeat(4, minmax(0, 1fr)); }
  .lg\\:px-8 { padding-left: 2rem; padding-right: 2rem; }
}
"""


def get_vendor_dir() -> Path:
    """Get the vendor assets directory path."""
    # Relative to this script's location
    script_dir = Path(__file__).parent.parent
    return script_dir / "static" / "vendor"


def download_asset(asset: VendorAsset, vendor_dir: Path) -> bool:
    """Download a single vendor asset.
    
    Args:
        asset: Asset definition to download
        vendor_dir: Directory to save the asset
        
    Returns:
        True if download successful
    """
    output_path = vendor_dir / asset.filename
    
    # Check if already exists
    if output_path.exists():
        logger.info(f"  ✓ {asset.name} already exists")
        return True
    
    logger.info(f"  ↓ Downloading {asset.name} (~{asset.size_kb}KB)...")
    
    try:
        # Download with timeout
        req = urllib.request.Request(
            asset.url,
            headers={"User-Agent": "CORTEX-LENS-Dashboard/1.0"},
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read()
        
        # Verify hash if provided
        if asset.sha256:
            actual_hash = hashlib.sha256(content).hexdigest()
            if actual_hash != asset.sha256:
                logger.error(f"  ✗ {asset.name} hash mismatch!")
                return False
        
        # Save to file
        output_path.write_bytes(content)
        actual_size = len(content) // 1024
        logger.info(f"  ✓ {asset.name} downloaded ({actual_size}KB)")
        return True
        
    except Exception as e:
        logger.error(f"  ✗ {asset.name} download failed: {e}")
        return False


def bundle_vendor_assets(vendor_dir: Optional[Path] = None) -> Dict[str, bool]:
    """Download all vendor assets for offline operation.
    
    Args:
        vendor_dir: Optional override for vendor directory
        
    Returns:
        Dictionary mapping asset names to success status
    """
    if vendor_dir is None:
        vendor_dir = get_vendor_dir()
    
    # Ensure vendor directory exists
    vendor_dir.mkdir(parents=True, exist_ok=True)
    
    logger.info(f"Bundling vendor assets to {vendor_dir}")
    logger.info("=" * 50)
    
    results: Dict[str, bool] = {}
    
    # Download JavaScript assets
    for asset in VENDOR_ASSETS:
        results[asset.name] = download_asset(asset, vendor_dir)
    
    # Write Tailwind CSS
    tailwind_path = vendor_dir / "tailwind-3.4.0.min.css"
    if not tailwind_path.exists():
        logger.info("  → Writing Tailwind CSS subset...")
        tailwind_path.write_text(TAILWIND_CSS)
        logger.info(f"  ✓ Tailwind CSS written ({len(TAILWIND_CSS) // 1024}KB)")
    else:
        logger.info("  ✓ Tailwind CSS already exists")
    results["Tailwind CSS"] = True
    
    # Summary
    logger.info("=" * 50)
    success_count = sum(1 for v in results.values() if v)
    total_count = len(results)
    
    if success_count == total_count:
        logger.info(f"✅ All {total_count} assets bundled successfully!")
    else:
        failed = [k for k, v in results.items() if not v]
        logger.warning(f"⚠️  {success_count}/{total_count} assets bundled. Failed: {failed}")
    
    return results


def verify_vendor_assets(vendor_dir: Optional[Path] = None) -> Dict[str, bool]:
    """Verify all vendor assets are present.
    
    Args:
        vendor_dir: Optional override for vendor directory
        
    Returns:
        Dictionary mapping asset names to existence status
    """
    if vendor_dir is None:
        vendor_dir = get_vendor_dir()
    
    results: Dict[str, bool] = {}
    
    for asset in VENDOR_ASSETS:
        path = vendor_dir / asset.filename
        results[asset.name] = path.exists()
    
    # Check Tailwind
    tailwind_path = vendor_dir / "tailwind-3.4.0.min.css"
    results["Tailwind CSS"] = tailwind_path.exists()
    
    return results


def main() -> None:
    """CLI entry point for vendor bundling."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "verify":
        results = verify_vendor_assets()
        all_present = all(results.values())
        
        print("\nVendor Asset Status:")
        for name, present in results.items():
            status = "✓" if present else "✗"
            print(f"  {status} {name}")
        
        sys.exit(0 if all_present else 1)
    else:
        results = bundle_vendor_assets()
        all_success = all(results.values())
        sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
