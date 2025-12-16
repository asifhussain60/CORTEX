"""
CORTEX Resource Path Resolver

Provides production-safe path resolution for installed packages.
Replaces hardcoded `Path(__file__).parent.parent.parent` patterns.

Usage:
    from src.utils.resource_resolver import ResourceResolver
    
    resolver = ResourceResolver()
    
    # Get cortex-brain directory
    brain_path = resolver.get_brain_path()
    
    # Get specific brain file
    rules_path = resolver.get_brain_file("brain-protection-rules.yaml")
    
    # Get templates directory
    templates_path = resolver.get_templates_path()
    
    # Get project root
    root = resolver.get_root_path()

Production Package Support:
- Works in both development (source tree) and production (pip install)
- Falls back to config.py for machine-specific paths
- Uses importlib.resources for package-aware resolution
- Supports environment variable overrides

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import os
import sys
from pathlib import Path
from typing import Optional
try:
    import importlib.resources as pkg_resources
    HAS_PKG_RESOURCES = True
except ImportError:
    # Python < 3.7
    HAS_PKG_RESOURCES = False


class ResourceResolver:
    """
    Production-safe resource path resolver.
    
    Handles both development and production package installations.
    """
    
    def __init__(self):
        """Initialize resource resolver."""
        self._root_path: Optional[Path] = None
        self._brain_path: Optional[Path] = None
        self._is_installed: Optional[bool] = None
    
    @property
    def is_installed_package(self) -> bool:
        """
        Check if running from installed package or development source.
        
        Returns:
            True if installed via pip, False if running from source
        """
        if self._is_installed is not None:
            return self._is_installed
        
        # Check if cortex-brain exists as sibling to src
        try:
            root = self.get_root_path()
            brain_dir = root / "cortex-brain"
            self._is_installed = not brain_dir.exists()
        except Exception:
            self._is_installed = True  # Assume installed if can't determine
        
        return self._is_installed
    
    def get_root_path(self) -> Path:
        """
        Get CORTEX project root directory.
        
        Strategy:
        1. Check CORTEX_ROOT environment variable
        2. Load from config.py (multi-machine support)
        3. Use package resources (if installed)
        4. Fall back to relative path from this file
        
        Returns:
            Absolute path to project root
        """
        if self._root_path is not None:
            return self._root_path
        
        # 1. Environment variable override
        env_root = os.environ.get("CORTEX_ROOT")
        if env_root:
            self._root_path = Path(env_root).resolve()
            return self._root_path
        
        # 2. Try config.py (best option for development)
        try:
            from src.config import config
            self._root_path = config.root_path
            return self._root_path
        except Exception:
            pass
        
        # 3. Package resources (for installed packages)
        if HAS_PKG_RESOURCES:
            try:
                # Get package location
                import src
                pkg_path = Path(src.__file__).parent.parent
                self._root_path = pkg_path
                return self._root_path
            except Exception:
                pass
        
        # 4. Relative path fallback (development)
        # This file is at: CORTEX/src/utils/resource_resolver.py
        # Project root is 2 levels up from src/
        self._root_path = Path(__file__).parent.parent.resolve()
        return self._root_path
    
    def get_brain_path(self) -> Path:
        """
        Get cortex-brain directory path.
        
        Returns:
            Absolute path to cortex-brain directory
        
        Raises:
            FileNotFoundError: If brain directory doesn't exist
        """
        if self._brain_path is not None:
            return self._brain_path
        
        # 1. Environment variable override
        env_brain = os.environ.get("CORTEX_BRAIN_PATH")
        if env_brain:
            brain_path = Path(env_brain).resolve()
            if brain_path.exists():
                self._brain_path = brain_path
                return self._brain_path
        
        # 2. Try config.py
        try:
            from src.config import config
            self._brain_path = config.brain_path
            return self._brain_path
        except Exception:
            pass
        
        # 3. Standard location (development)
        root = self.get_root_path()
        brain_path = root / "cortex-brain"
        
        if brain_path.exists():
            self._brain_path = brain_path
            return self._brain_path
        
        # 4. Package data location (installed)
        if HAS_PKG_RESOURCES:
            try:
                import cortex_brain
                brain_path = Path(cortex_brain.__file__).parent
                if brain_path.exists():
                    self._brain_path = brain_path
                    return self._brain_path
            except Exception:
                pass
        
        raise FileNotFoundError(
            f"cortex-brain directory not found. Checked:\n"
            f"  - Environment: CORTEX_BRAIN_PATH\n"
            f"  - Config: src.config\n"
            f"  - Standard: {root / 'cortex-brain'}\n"
            f"  - Package: cortex_brain module"
        )
    
    def get_brain_file(self, relative_path: str) -> Path:
        """
        Get path to file within cortex-brain directory.
        
        Args:
            relative_path: Path relative to cortex-brain (e.g., "tier0/rules.yaml")
        
        Returns:
            Absolute path to brain file
        
        Raises:
            FileNotFoundError: If file doesn't exist
        """
        brain_path = self.get_brain_path()
        file_path = brain_path / relative_path
        
        if not file_path.exists():
            raise FileNotFoundError(
                f"Brain file not found: {relative_path}\n"
                f"Expected at: {file_path}"
            )
        
        return file_path
    
    def get_templates_path(self) -> Path:
        """
        Get cortex-brain/templates directory path.
        
        Returns:
            Absolute path to templates directory
        """
        brain_path = self.get_brain_path()
        templates_path = brain_path / "templates"
        templates_path.mkdir(exist_ok=True)
        return templates_path
    
    def get_src_path(self) -> Path:
        """
        Get src directory path.
        
        Returns:
            Absolute path to src directory
        """
        # This file is in src/utils/
        return Path(__file__).parent.parent.resolve()


# Global resolver instance
_resolver = ResourceResolver()


# Convenience functions
def get_root_path() -> Path:
    """Get CORTEX project root."""
    return _resolver.get_root_path()


def get_brain_path() -> Path:
    """Get cortex-brain directory."""
    return _resolver.get_brain_path()


def get_brain_file(relative_path: str) -> Path:
    """Get file within cortex-brain directory."""
    return _resolver.get_brain_file(relative_path)


def get_templates_path() -> Path:
    """Get templates directory."""
    return _resolver.get_templates_path()


def is_installed_package() -> bool:
    """Check if running from installed package."""
    return _resolver.is_installed_package
