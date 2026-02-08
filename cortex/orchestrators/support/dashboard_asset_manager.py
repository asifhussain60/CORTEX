"""
Dashboard Asset Manager

Ensures shared dashboard assets (CSS, JS, images, vendor libs) exist
before dashboard generation. Copies assets from CORTEX to target locations.

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
AC-ID: AC-DASHBOARD-ASSET-MGR-001
Phase: 28 (Repository Onboarding)
"""

import logging
import shutil
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


class DashboardAssetManager:
    """
    Manages shared dashboard assets for repository onboarding.
    
    Ensures CSS, JS, images, and vendor libraries are available
    at expected locations before dashboard generation.
    """
    
    def __init__(self, cortex_root: Optional[Path] = None):
        """
        Initialize asset manager.
        
        Args:
            cortex_root: CORTEX root directory (auto-detected if None)
        """
        if cortex_root is None:
            cortex_root = self._find_cortex_root()
        
        self.cortex_root = cortex_root
        self.assets_src = cortex_root / "docs" / "assets"
        self.company_assets_dest = cortex_root / "company" / "dashboards" / "assets"
        
        logger.debug(f"DashboardAssetManager initialized: {cortex_root}")
    
    def _find_cortex_root(self) -> Path:
        """Find CORTEX root directory by searching upward for marker files."""
        current = Path(__file__).resolve()
        
        # Search upward for CORTEX root indicators
        for parent in [current] + list(current.parents):
            if (parent / "cortex" / "__init__.py").exists() and \
               (parent / "README.md").exists():
                return parent
        
        # Fallback: assume we're in cortex/orchestrators/support
        return current.parent.parent.parent
    
    def ensure_assets_exist(self) -> bool:
        """
        Ensure all required dashboard assets exist at target locations.
        
        Copies CSS, JS, images, and vendor libraries from source to destination
        if they don't already exist or are outdated.
        
        Returns:
            True if assets verified/copied successfully, False on error
        """
        try:
            # Create destination directories
            (self.company_assets_dest / "css").mkdir(parents=True, exist_ok=True)
            (self.company_assets_dest / "js").mkdir(parents=True, exist_ok=True)
            (self.company_assets_dest / "images").mkdir(parents=True, exist_ok=True)
            (self.company_assets_dest / "vendor").mkdir(parents=True, exist_ok=True)
            
            # Copy CSS files
            self._copy_directory_contents(
                self.assets_src / "css",
                self.company_assets_dest / "css",
                pattern="*.css"
            )
            
            # Copy JS files
            self._copy_directory_contents(
                self.assets_src / "js",
                self.company_assets_dest / "js",
                pattern="*.js"
            )
            
            # Copy images
            self._copy_directory_contents(
                self.assets_src / "images",
                self.company_assets_dest / "images",
                pattern="*.*"
            )
            
            # Copy vendor libraries (if they exist)
            vendor_src = self.cortex_root / "docs" / "assets" / "vendor"
            if vendor_src.exists():
                self._copy_directory_contents(
                    vendor_src,
                    self.company_assets_dest / "vendor",
                    pattern="*.*"
                )
            
            logger.info("✅ Dashboard assets verified/copied successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to ensure dashboard assets: {e}", exc_info=True)
            return False
    
    def _copy_directory_contents(
        self,
        src: Path,
        dest: Path,
        pattern: str = "*",
        force: bool = False
    ) -> int:
        """
        Copy files matching pattern from src to dest.
        
        Args:
            src: Source directory
            dest: Destination directory
            pattern: Glob pattern for files to copy
            force: Force overwrite existing files
            
        Returns:
            Number of files copied
        """
        if not src.exists():
            logger.debug(f"Source directory does not exist: {src}")
            return 0
        
        dest.mkdir(parents=True, exist_ok=True)
        
        copied = 0
        for src_file in src.glob(pattern):
            if src_file.is_file():
                dest_file = dest / src_file.name
                
                # Skip if destination exists and not forcing
                if dest_file.exists() and not force:
                    # Check if source is newer
                    if src_file.stat().st_mtime <= dest_file.stat().st_mtime:
                        continue
                
                shutil.copy2(src_file, dest_file)
                copied += 1
                logger.debug(f"Copied asset: {src_file.name} -> {dest}")
        
        if copied > 0:
            logger.debug(f"Copied {copied} files from {src.name} to {dest}")
        
        return copied
    
    def verify_assets(self) -> dict[str, bool]:
        """
        Verify all required assets exist.
        
        Returns:
            Dict mapping asset categories to existence status
        """
        required_css = [
            "main.css",
            "glass-design-tokens.css",
            "glass-base-patterns.css",
            "glass-ui-components.css",
        ]
        
        required_images = [
            "CORTEX-logo-200.png",
            "CORTEX-logo-64.png",
        ]
        
        status = {
            "css": all((self.company_assets_dest / "css" / css).exists() for css in required_css),
            "images": all((self.company_assets_dest / "images" / img).exists() for img in required_images),
            "js": (self.company_assets_dest / "js").exists(),
            "vendor": (self.company_assets_dest / "vendor").exists(),
        }
        
        return status


# Global singleton instance
_asset_manager: Optional[DashboardAssetManager] = None


def get_dashboard_asset_manager(cortex_root: Optional[Path] = None) -> DashboardAssetManager:
    """
    Get or create the global DashboardAssetManager instance.
    
    Args:
        cortex_root: CORTEX root directory (auto-detected if None)
        
    Returns:
        DashboardAssetManager instance
    """
    global _asset_manager
    
    if _asset_manager is None:
        _asset_manager = DashboardAssetManager(cortex_root=cortex_root)
    
    return _asset_manager
