"""
Dashboard Asset Manager for Universal Repository Onboarding.

Manages shared glassmorphism assets for company dashboards:
- Copy CSS, images, JS from docs/ to company/dashboards/assets/
- Verify asset integrity with hash checking
- Version tracking for cache busting

Authority: cortex-architect.prompt.md v8.0
Author: Asif Hussain
AC-ID: AC-UNIVERSAL-ONBOARD-001
"""

from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
import json
import shutil
import logging

logger = logging.getLogger(__name__)


class DashboardAssetManager:
    """
    Manages shared glassmorphism assets for onboarding dashboards.
    
    Features:
    - Single shared assets folder for all dashboards
    - Hash-based integrity verification
    - Version tracking for cache busting
    - Offline-capable (local D3.js, FontAwesome subset)
    
    Example:
        >>> manager = DashboardAssetManager()
        >>> manager.ensure_assets_exist()
        >>> manager.verify_asset_integrity()
    """
    
    # Core CSS files needed for glassmorphism dashboards
    REQUIRED_CSS = [
        "glass-design-tokens.css",
        "glass-base-patterns.css",
        "cortex-glass-system.css",
        "glass-ui-components.css",
        "glass-animations.css",
        "glass-utilities.css",
        "variables.css",
    ]
    
    # Core images for branding
    REQUIRED_IMAGES = [
        "CORTEX-logo-128.png",
        "CORTEX-logo-512.png",
        "CORTEX-logo-64.png",
    ]
    
    # JavaScript libraries (local copies for offline)
    REQUIRED_JS = [
        # D3.js will be downloaded separately
    ]
    
    def __init__(
        self,
        cortex_root: Optional[Path] = None,
        dashboards_root: Optional[Path] = None,
    ):
        """
        Initialize Dashboard Asset Manager.
        
        Args:
            cortex_root: Root path of CORTEX project
            dashboards_root: Root path for dashboards output
        """
        self.cortex_root = cortex_root or Path(__file__).parent.parent.parent.parent
        self.dashboards_root = dashboards_root or self.cortex_root / "company" / "dashboards"
        self.assets_path = self.dashboards_root / "assets"
        self.docs_assets = self.cortex_root / "docs" / "assets"
        self.manifest_path = self.dashboards_root / "asset-manifest.json"
        
    def ensure_assets_exist(self) -> Dict[str, Any]:
        """
        Ensure all required assets exist in company/dashboards/assets/.
        
        Creates directory structure and copies assets from docs/ if needed.
        
        Returns:
            Dict with status, copied_files, errors
        """
        result = {
            "success": True,
            "created_directories": [],
            "copied_files": [],
            "errors": [],
            "timestamp": datetime.now().isoformat(),
        }
        
        try:
            # Create directory structure
            directories = [
                self.dashboards_root,
                self.assets_path,
                self.assets_path / "css",
                self.assets_path / "images",
                self.assets_path / "js",
            ]
            
            for dir_path in directories:
                if not dir_path.exists():
                    dir_path.mkdir(parents=True, exist_ok=True)
                    result["created_directories"].append(str(dir_path))
                    logger.info(f"Created directory: {dir_path}")
            
            # Copy CSS files
            for css_file in self.REQUIRED_CSS:
                src = self.docs_assets / "css" / css_file
                dst = self.assets_path / "css" / css_file
                
                if src.exists() and (not dst.exists() or self._file_changed(src, dst)):
                    shutil.copy2(src, dst)
                    result["copied_files"].append(f"css/{css_file}")
                    logger.info(f"Copied: {css_file}")
                elif not src.exists():
                    result["errors"].append(f"Source CSS not found: {src}")
            
            # Copy images
            for img_file in self.REQUIRED_IMAGES:
                src = self.docs_assets / "images" / img_file
                dst = self.assets_path / "images" / img_file
                
                if src.exists() and (not dst.exists() or self._file_changed(src, dst)):
                    shutil.copy2(src, dst)
                    result["copied_files"].append(f"images/{img_file}")
                    logger.info(f"Copied: {img_file}")
                elif not src.exists():
                    result["errors"].append(f"Source image not found: {src}")
            
            # Create combined dashboard CSS
            self._create_dashboard_css()
            result["copied_files"].append("css/dashboard-combined.css")
            
            # Create landing page CSS
            self._create_landing_css()
            result["copied_files"].append("css/landing.css")
            
            # Update manifest
            self._update_manifest(result["copied_files"])
            
            if result["errors"]:
                result["success"] = False
                
        except Exception as e:
            logger.error(f"Asset setup failed: {e}", exc_info=True)
            result["success"] = False
            result["errors"].append(str(e))
        
        return result
    
    def _file_changed(self, src: Path, dst: Path) -> bool:
        """Check if source file differs from destination."""
        if not dst.exists():
            return True
        return self._hash_file(src) != self._hash_file(dst)
    
    def _hash_file(self, path: Path) -> str:
        """Calculate MD5 hash of file."""
        hasher = hashlib.md5()
        with open(path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                hasher.update(chunk)
        return hasher.hexdigest()
    
    def _create_dashboard_css(self) -> None:
        """Create combined dashboard CSS with all imports."""
        css_content = '''/**
 * CORTEX Dashboard Combined CSS
 * Auto-generated by DashboardAssetManager
 * Version: 1.0.0
 */

/* Import design tokens first */
@import url('./glass-design-tokens.css');
@import url('./variables.css');

/* Import glassmorphism patterns */
@import url('./glass-base-patterns.css');
@import url('./cortex-glass-system.css');
@import url('./glass-ui-components.css');
@import url('./glass-animations.css');
@import url('./glass-utilities.css');

/* ============================================
   DASHBOARD-SPECIFIC STYLES
   ============================================ */

:root {
    --dashboard-bg: linear-gradient(135deg, #0a0a0f 0%, #1a1a2e 100%);
    --card-radius: 16px;
    --tab-radius: 12px;
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    background: var(--dashboard-bg);
    background-attachment: fixed;
    color: var(--text-primary, #ffffff);
    min-height: 100vh;
    margin: 0;
    padding: 0;
    line-height: 1.6;
}

/* Dashboard Container */
.dashboard-container {
    max-width: 1800px;
    margin: 0 auto;
    padding: 2rem;
}

@media (max-width: 768px) {
    .dashboard-container {
        padding: 1rem;
    }
}

/* Header with Logo */
.dashboard-header {
    display: flex;
    align-items: center;
    gap: 2rem;
    padding: 2rem;
    background: rgba(26, 31, 58, 0.7);
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 24px;
    margin-bottom: 2rem;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.37);
}

.dashboard-logo {
    width: 80px;
    height: 80px;
    border-radius: 16px;
    box-shadow: 0 8px 32px rgba(59, 130, 246, 0.3);
    border: 2px solid rgba(255, 255, 255, 0.1);
    transition: transform 0.3s ease, box-shadow 0.3s ease;
}

.dashboard-logo:hover {
    transform: scale(1.05);
    box-shadow: 0 12px 48px rgba(59, 130, 246, 0.5);
}

.dashboard-title {
    font-size: 2.5rem;
    font-weight: 700;
    margin: 0;
    background: linear-gradient(135deg, #3b82f6 0%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.dashboard-subtitle {
    font-size: 1.125rem;
    color: rgba(255, 255, 255, 0.7);
    margin: 0.5rem 0 0 0;
}

/* Tabs Navigation */
.tabs-container {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
    margin-bottom: 2rem;
    padding: 1rem;
    background: rgba(26, 31, 58, 0.5);
    backdrop-filter: blur(10px);
    border-radius: 16px;
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.tab-button {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1.25rem;
    background: rgba(255, 255, 255, 0.05);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--tab-radius);
    color: rgba(255, 255, 255, 0.8);
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 0.9rem;
}

.tab-button:hover {
    background: rgba(255, 255, 255, 0.1);
    border-color: rgba(0, 212, 255, 0.3);
    color: #ffffff;
}

.tab-button.active {
    background: rgba(59, 130, 246, 0.2);
    border-color: rgba(59, 130, 246, 0.5);
    color: #ffffff;
    box-shadow: 0 0 20px rgba(59, 130, 246, 0.3);
}

.tab-button .tab-icon {
    font-size: 1.1rem;
}

/* Tab Content */
.tab-content {
    display: none;
    animation: fadeIn 0.3s ease;
}

.tab-content.active {
    display: block;
}

@keyframes fadeIn {
    from { opacity: 0; transform: translateY(10px); }
    to { opacity: 1; transform: translateY(0); }
}

/* Metric Cards */
.metrics-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 1.5rem;
    margin-bottom: 2rem;
}

.metric-card {
    background: rgba(26, 31, 58, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--card-radius);
    padding: 1.5rem;
    text-align: center;
    transition: all 0.3s ease;
}

.metric-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    border-color: rgba(0, 212, 255, 0.3);
}

.metric-value {
    font-size: 2.5rem;
    font-weight: 700;
    background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.metric-label {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 0.5rem;
}

/* Health Score Ring */
.health-ring {
    position: relative;
    width: 120px;
    height: 120px;
    margin: 0 auto 1rem;
}

.health-ring svg {
    transform: rotate(-90deg);
}

.health-ring-bg {
    fill: none;
    stroke: rgba(255, 255, 255, 0.1);
    stroke-width: 8;
}

.health-ring-progress {
    fill: none;
    stroke-width: 8;
    stroke-linecap: round;
    transition: stroke-dashoffset 1s ease;
}

.health-ring-progress.critical { stroke: #ef4444; }
.health-ring-progress.warning { stroke: #eab308; }
.health-ring-progress.good { stroke: #22c55e; }
.health-ring-progress.excellent { stroke: #00d4ff; }

.health-score-text {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
}

.health-score-value {
    font-size: 2rem;
    font-weight: 700;
    color: #ffffff;
}

.health-score-label {
    font-size: 0.75rem;
    color: rgba(255, 255, 255, 0.6);
}

/* Confidence Badge */
.confidence-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.75rem;
    border-radius: 9999px;
    font-size: 0.8rem;
    font-weight: 600;
}

.confidence-badge.high {
    background: rgba(34, 197, 94, 0.2);
    color: #22c55e;
    border: 1px solid rgba(34, 197, 94, 0.4);
}

.confidence-badge.medium {
    background: rgba(234, 179, 8, 0.2);
    color: #eab308;
    border: 1px solid rgba(234, 179, 8, 0.4);
}

.confidence-badge.low {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
    border: 1px solid rgba(239, 68, 68, 0.4);
}

/* Collapsible Sections */
.collapsible {
    margin-bottom: 1rem;
}

.collapsible-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 1rem 1.25rem;
    background: rgba(26, 31, 58, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--card-radius);
    cursor: pointer;
    transition: all 0.2s ease;
}

.collapsible-header:hover {
    background: rgba(26, 31, 58, 0.7);
    border-color: rgba(0, 212, 255, 0.3);
}

.collapsible-header.active {
    border-radius: var(--card-radius) var(--card-radius) 0 0;
    border-bottom: none;
}

.collapsible-icon {
    transition: transform 0.3s ease;
}

.collapsible-header.active .collapsible-icon {
    transform: rotate(180deg);
}

.collapsible-content {
    display: none;
    padding: 1.25rem;
    background: rgba(19, 23, 46, 0.5);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-top: none;
    border-radius: 0 0 var(--card-radius) var(--card-radius);
}

.collapsible-content.active {
    display: block;
    animation: slideDown 0.3s ease;
}

@keyframes slideDown {
    from { opacity: 0; max-height: 0; }
    to { opacity: 1; max-height: 2000px; }
}

/* File Tree */
.file-tree {
    font-family: 'SF Mono', 'Monaco', 'Consolas', monospace;
    font-size: 0.85rem;
    line-height: 1.8;
}

.file-tree-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    transition: background 0.2s ease;
}

.file-tree-item:hover {
    background: rgba(255, 255, 255, 0.05);
}

.file-tree-item a {
    color: #00d4ff;
    text-decoration: none;
}

.file-tree-item a:hover {
    text-decoration: underline;
}

/* Security Badges */
.security-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.25rem 0.5rem;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
}

.security-badge.p0 {
    background: rgba(239, 68, 68, 0.2);
    color: #ef4444;
}

.security-badge.p1 {
    background: rgba(234, 179, 8, 0.2);
    color: #eab308;
}

.security-badge.p2 {
    background: rgba(59, 130, 246, 0.2);
    color: #3b82f6;
}

/* Use Case Cards */
.use-case-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 1.5rem;
}

.use-case-card {
    background: rgba(26, 31, 58, 0.6);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: var(--card-radius);
    padding: 1.5rem;
    transition: all 0.3s ease;
}

.use-case-card:hover {
    transform: translateY(-4px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    border-color: rgba(123, 97, 255, 0.4);
}

.use-case-icon {
    font-size: 2rem;
    margin-bottom: 1rem;
}

.use-case-title {
    font-size: 1.125rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
    color: #ffffff;
}

.use-case-description {
    font-size: 0.9rem;
    color: rgba(255, 255, 255, 0.7);
    line-height: 1.6;
}

/* Print Styles */
@media print {
    body {
        background: white;
        color: black;
    }
    
    .dashboard-header,
    .tabs-container,
    .collapsible-header {
        background: #f3f4f6;
        backdrop-filter: none;
    }
}
'''
        
        css_path = self.assets_path / "css" / "dashboard-combined.css"
        css_path.write_text(css_content, encoding='utf-8')
        logger.info(f"Created dashboard-combined.css")
    
    def _create_landing_css(self) -> None:
        """Create landing page specific CSS."""
        css_content = '''/**
 * CORTEX Landing Page CSS
 * Glassmorphism hub for onboarded repositories
 * Auto-generated by DashboardAssetManager
 */

/* Hero Section */
.landing-hero {
    text-align: center;
    padding: 4rem 2rem;
    background: rgba(26, 31, 58, 0.5);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    margin-bottom: 3rem;
    border: 1px solid rgba(255, 255, 255, 0.1);
    position: relative;
    overflow: hidden;
}

.landing-hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(circle at 30% 30%, rgba(0, 212, 255, 0.1) 0%, transparent 50%);
    animation: heroGlow 8s ease-in-out infinite;
    pointer-events: none;
}

@keyframes heroGlow {
    0%, 100% { opacity: 0.5; transform: scale(1); }
    50% { opacity: 0.8; transform: scale(1.1); }
}

.landing-logo {
    width: 150px;
    height: 150px;
    margin-bottom: 2rem;
    border-radius: 24px;
    box-shadow: 0 20px 60px rgba(59, 130, 246, 0.4);
    animation: logoPulse 3s ease-in-out infinite;
    position: relative;
    z-index: 1;
}

@keyframes logoPulse {
    0%, 100% { transform: scale(1); box-shadow: 0 20px 60px rgba(59, 130, 246, 0.4); }
    50% { transform: scale(1.02); box-shadow: 0 25px 80px rgba(59, 130, 246, 0.6); }
}

.landing-title {
    font-size: 3rem;
    font-weight: 800;
    margin: 0;
    background: linear-gradient(135deg, #00d4ff 0%, #7b61ff 50%, #00d4ff 100%);
    background-size: 200% auto;
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    animation: gradientShift 4s linear infinite;
    position: relative;
    z-index: 1;
}

@keyframes gradientShift {
    0% { background-position: 0% center; }
    100% { background-position: 200% center; }
}

.landing-subtitle {
    font-size: 1.25rem;
    color: rgba(255, 255, 255, 0.7);
    margin-top: 1rem;
    position: relative;
    z-index: 1;
}

/* Repository Tiles Grid */
.repos-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 2rem;
    padding: 1rem;
}

/* Repository Tile */
.repo-tile {
    position: relative;
    display: block;
    background: rgba(26, 31, 58, 0.7);
    backdrop-filter: blur(15px);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 20px;
    padding: 2rem;
    text-decoration: none;
    color: inherit;
    transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
    overflow: hidden;
}

.repo-tile::before {
    content: '';
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(123, 97, 255, 0.1) 100%);
    opacity: 0;
    transition: opacity 0.3s ease;
    pointer-events: none;
}

.repo-tile:hover {
    transform: translateY(-8px) scale(1.02);
    box-shadow: 
        0 20px 60px rgba(0, 0, 0, 0.4),
        0 0 40px rgba(0, 212, 255, 0.2);
    border-color: rgba(0, 212, 255, 0.4);
}

.repo-tile:hover::before {
    opacity: 1;
}

.repo-tile-icon {
    font-size: 3rem;
    margin-bottom: 1rem;
    display: block;
}

.repo-tile-title {
    font-size: 1.5rem;
    font-weight: 700;
    margin: 0 0 0.5rem 0;
    color: #ffffff;
}

.repo-tile-description {
    font-size: 0.95rem;
    color: rgba(255, 255, 255, 0.7);
    margin: 0 0 1.5rem 0;
    line-height: 1.6;
}

.repo-tile-meta {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding-top: 1rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
}

.repo-tile-health {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 600;
}

.repo-tile-health.critical { color: #ef4444; }
.repo-tile-health.warning { color: #eab308; }
.repo-tile-health.good { color: #22c55e; }
.repo-tile-health.excellent { color: #00d4ff; }

.repo-tile-date {
    font-size: 0.8rem;
    color: rgba(255, 255, 255, 0.5);
}

/* Empty State */
.empty-state {
    text-align: center;
    padding: 4rem 2rem;
    background: rgba(26, 31, 58, 0.4);
    border-radius: 20px;
    border: 2px dashed rgba(255, 255, 255, 0.2);
}

.empty-state-icon {
    font-size: 4rem;
    margin-bottom: 1.5rem;
    opacity: 0.5;
}

.empty-state-title {
    font-size: 1.5rem;
    font-weight: 600;
    margin-bottom: 0.5rem;
}

.empty-state-description {
    color: rgba(255, 255, 255, 0.6);
    max-width: 400px;
    margin: 0 auto;
}

/* Footer */
.landing-footer {
    text-align: center;
    padding: 2rem;
    margin-top: 3rem;
    color: rgba(255, 255, 255, 0.5);
    font-size: 0.9rem;
}

/* Responsive */
@media (max-width: 768px) {
    .landing-hero {
        padding: 2rem 1rem;
    }
    
    .landing-logo {
        width: 100px;
        height: 100px;
    }
    
    .landing-title {
        font-size: 2rem;
    }
    
    .repos-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .repo-tile {
        padding: 1.5rem;
    }
}
'''
        
        css_path = self.assets_path / "css" / "landing.css"
        css_path.write_text(css_content, encoding='utf-8')
        logger.info(f"Created landing.css")
    
    def _update_manifest(self, copied_files: List[str]) -> None:
        """Update asset manifest with version and hash info."""
        manifest = {
            "version": "1.0.0",
            "generated": datetime.now().isoformat(),
            "generator": "DashboardAssetManager",
            "files": {},
        }
        
        # Hash all assets
        for subdir in ["css", "images", "js"]:
            subdir_path = self.assets_path / subdir
            if subdir_path.exists():
                for file_path in subdir_path.iterdir():
                    if file_path.is_file():
                        rel_path = f"{subdir}/{file_path.name}"
                        manifest["files"][rel_path] = {
                            "hash": self._hash_file(file_path),
                            "size": file_path.stat().st_size,
                            "modified": datetime.fromtimestamp(
                                file_path.stat().st_mtime
                            ).isoformat(),
                        }
        
        self.manifest_path.write_text(
            json.dumps(manifest, indent=2),
            encoding='utf-8'
        )
        logger.info(f"Updated asset manifest: {self.manifest_path}")
    
    def verify_asset_integrity(self) -> Dict[str, Any]:
        """
        Verify all assets match manifest hashes.
        
        Returns:
            Dict with verification results
        """
        result = {
            "success": True,
            "verified": [],
            "corrupted": [],
            "missing": [],
        }
        
        if not self.manifest_path.exists():
            result["success"] = False
            result["missing"].append("asset-manifest.json")
            return result
        
        manifest = json.loads(self.manifest_path.read_text(encoding='utf-8'))
        
        for rel_path, info in manifest.get("files", {}).items():
            file_path = self.assets_path / rel_path
            
            if not file_path.exists():
                result["missing"].append(rel_path)
                result["success"] = False
            elif self._hash_file(file_path) != info["hash"]:
                result["corrupted"].append(rel_path)
                result["success"] = False
            else:
                result["verified"].append(rel_path)
        
        return result
    
    def get_asset_version(self) -> str:
        """Get current asset bundle version."""
        if self.manifest_path.exists():
            manifest = json.loads(self.manifest_path.read_text(encoding='utf-8'))
            return manifest.get("version", "unknown")
        return "not-installed"


# Singleton instance
_dashboard_asset_manager = None


def get_dashboard_asset_manager() -> DashboardAssetManager:
    """Get or create singleton DashboardAssetManager."""
    global _dashboard_asset_manager
    if _dashboard_asset_manager is None:
        _dashboard_asset_manager = DashboardAssetManager()
    return _dashboard_asset_manager
