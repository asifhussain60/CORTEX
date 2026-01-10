"""
CORTEX 6.0 - Version-Agnostic Import Manager

Provides dynamic import system with fallbacks and version compatibility checks.
Supports Python 3.9, 3.10, 3.11, 3.12+ with graceful degradation.

Key Features:
- Dynamic imports with fallback chains
- Version compatibility matrix validation
- Optional feature detection (AI, Vision API, etc.)
- Graceful degradation for missing packages
- Performance optimized (<100ms lazy loading)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import importlib
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple, Union
import logging


logger = logging.getLogger(__name__)


class ImportManager:
    """
    Version-agnostic import manager with fallbacks and compatibility checks.
    
    Ensures CORTEX works across Python 3.9+ without version-specific code.
    """
    
    # Singleton instance
    _instance: Optional['ImportManager'] = None
    
    # Compatibility matrix
    COMPATIBILITY_MATRIX = {
        'python_versions': {
            'minimum': (3, 9),
            'supported': ['3.9', '3.10', '3.11', '3.12'],
            'tested': ['3.9', '3.10', '3.11', '3.12']
        },
        'package_compatibility': {
            'pytest': {'min_version': '8.4.0', 'required': True},
            'PyYAML': {'min_version': '6.0.2', 'required': True},
            'pyyaml': {'min_version': '6.0.2', 'required': True},  # Alias
            'pydantic': {'min_version': '2.0.0', 'required': True},
            'openai': {'min_version': '1.0.0', 'required': False, 'feature': 'ai_integration'},
            'anthropic': {'min_version': '0.18.0', 'required': False, 'feature': 'ai_integration'},
            'opencv-python': {'min_version': '4.8.0', 'required': False, 'feature': 'vision_api'},
            'parso': {'min_version': '0.8.5', 'required': False, 'feature': 'advanced_parsing', 'fallback': 'ast'},
        }
    }
    
    def __new__(cls):
        """Singleton pattern for consistent state."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize import manager (only once due to singleton)."""
        if self._initialized:
            return
        
        self._imported_modules: Dict[str, Any] = {}
        self._failed_imports: Dict[str, str] = {}
        self._optional_features_enabled = True
        self._degraded_features: List[str] = []
        self._initialized = True
        
        # Check environment compatibility on init
        self._check_initial_compatibility()
    
    def get_python_version(self) -> Tuple[int, int, int]:
        """
        Get current Python version as tuple.
        
        Returns:
            Tuple of (major, minor, micro) version numbers
        """
        return sys.version_info[:3]
    
    def get_compatibility_matrix(self) -> Dict[str, Any]:
        """
        Get version compatibility matrix.
        
        Returns:
            Dictionary with Python versions and package compatibility info
        """
        return self.COMPATIBILITY_MATRIX.copy()
    
    def check_environment_compatibility(self) -> bool:
        """
        Check if current Python environment meets minimum requirements.
        
        Returns:
            True if compatible, False otherwise
        """
        major, minor, _ = self.get_python_version()
        min_major, min_minor = self.COMPATIBILITY_MATRIX['python_versions']['minimum']
        
        if major < min_major:
            return False
        if major == min_major and minor < min_minor:
            return False
        
        return True
    
    def import_with_fallback(
        self,
        module_name: str,
        fallback: Optional[str] = None,
        optional: bool = False
    ) -> Optional[Any]:
        """
        Import module with fallback support.
        
        Args:
            module_name: Primary module to import
            fallback: Alternative module if primary fails
            optional: If True, returns None on failure without logging error
        
        Returns:
            Imported module or None if all attempts fail
        """
        # Check cache first
        if module_name in self._imported_modules:
            return self._imported_modules[module_name]
        
        # Skip optional imports if disabled
        if optional and not self._optional_features_enabled:
            return None
        
        # Try primary import
        try:
            module = importlib.import_module(module_name)
            self._imported_modules[module_name] = module
            return module
        except ImportError as e:
            self._failed_imports[module_name] = str(e)
            
            if not optional:
                logger.debug(f"Failed to import {module_name}: {e}")
            
            # Try fallback if provided
            if fallback:
                try:
                    fallback_module = importlib.import_module(fallback)
                    self._imported_modules[module_name] = fallback_module
                    logger.info(f"Using fallback {fallback} for {module_name}")
                    return fallback_module
                except ImportError as fallback_error:
                    logger.debug(f"Fallback {fallback} also failed: {fallback_error}")
            
            # Track degraded features
            if optional and module_name in self.COMPATIBILITY_MATRIX['package_compatibility']:
                pkg_info = self.COMPATIBILITY_MATRIX['package_compatibility'][module_name]
                if 'feature' in pkg_info:
                    feature = pkg_info['feature']
                    if feature not in self._degraded_features:
                        self._degraded_features.append(feature)
            
            return None
    
    def bulk_import(self, packages: Dict[str, Optional[str]]) -> Dict[str, Any]:
        """
        Import multiple packages with fallbacks.
        
        Args:
            packages: Dictionary of {module_name: fallback_name}
        
        Returns:
            Dictionary of {module_name: imported_module}
        """
        results = {}
        
        for module_name, fallback in packages.items():
            results[module_name] = self.import_with_fallback(module_name, fallback)
        
        return results
    
    def get_available_features(self) -> Dict[str, bool]:
        """
        Get availability status of optional features.
        
        Returns:
            Dictionary of {feature_name: is_available}
        """
        features = {
            'ai_integration': False,
            'vision_api': False,
            'advanced_parsing': False,
        }
        
        # Check AI integration
        openai_available = self.import_with_fallback('openai', optional=True) is not None
        anthropic_available = self.import_with_fallback('anthropic', optional=True) is not None
        features['ai_integration'] = openai_available or anthropic_available
        
        # Check Vision API
        cv2_available = self.import_with_fallback('cv2', optional=True) is not None
        features['vision_api'] = cv2_available
        
        # Check advanced parsing
        parso_available = self.import_with_fallback('parso', optional=True) is not None
        features['advanced_parsing'] = parso_available
        
        return features
    
    def get_degraded_features(self) -> List[str]:
        """
        Get list of features operating in degraded mode.
        
        Returns:
            List of feature names that are degraded due to missing packages
        """
        return self._degraded_features.copy()
    
    def enable_optional_features(self, enabled: bool = True) -> None:
        """
        Enable or disable optional feature imports.
        
        Args:
            enabled: True to enable optional imports, False to disable
        """
        self._optional_features_enabled = enabled
    
    def get_active_workarounds(self) -> List[str]:
        """
        Get list of active version-specific workarounds.
        
        Returns:
            List of workaround descriptions for current Python version
        """
        workarounds = []
        major, minor, _ = self.get_python_version()
        
        # Python 3.9 workarounds
        if major == 3 and minor == 9:
            # 3.9 doesn't support PEP 604 union syntax (X | Y)
            workarounds.append("Using typing.Union instead of | union syntax")
            
            # 3.9 requires __future__ annotations for forward references
            workarounds.append("Using from __future__ import annotations for self-references")
        
        # Python 3.10 workarounds
        if major == 3 and minor == 10:
            # 3.10 has some minor typing improvements but mostly compatible
            pass
        
        return workarounds
    
    def _check_initial_compatibility(self) -> None:
        """Check environment compatibility on initialization."""
        if not self.check_environment_compatibility():
            major, minor, micro = self.get_python_version()
            min_major, min_minor = self.COMPATIBILITY_MATRIX['python_versions']['minimum']
            logger.warning(
                f"Python {major}.{minor}.{micro} may not be fully supported. "
                f"Minimum recommended: {min_major}.{min_minor}"
            )
    
    def get_import_summary(self) -> Dict[str, Any]:
        """
        Get summary of import status.
        
        Returns:
            Dictionary with import statistics and status
        """
        return {
            'python_version': f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            'is_compatible': self.check_environment_compatibility(),
            'imported_modules': len(self._imported_modules),
            'failed_imports': len(self._failed_imports),
            'degraded_features': self._degraded_features.copy(),
            'available_features': self.get_available_features(),
        }


# ==============================================================================
# Convenience Functions
# ==============================================================================

def safe_import(module_name: str, fallback: Optional[str] = None) -> Optional[Any]:
    """
    Convenience function for safe module import with fallback.
    
    Args:
        module_name: Module to import
        fallback: Optional fallback module
    
    Returns:
        Imported module or None
    """
    manager = ImportManager()
    return manager.import_with_fallback(module_name, fallback)


def check_feature_available(feature_name: str) -> bool:
    """
    Check if optional feature is available.
    
    Args:
        feature_name: Feature to check (ai_integration, vision_api, etc.)
    
    Returns:
        True if feature available, False otherwise
    """
    manager = ImportManager()
    features = manager.get_available_features()
    return features.get(feature_name, False)


def get_version_info() -> Dict[str, Any]:
    """
    Get comprehensive version and compatibility information.
    
    Returns:
        Dictionary with version details
    """
    manager = ImportManager()
    return manager.get_import_summary()
