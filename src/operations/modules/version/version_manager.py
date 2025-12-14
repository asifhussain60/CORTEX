"""
Version Manager for CORTEX

Centralized version management system that:
- Reads version information from cortex.config.json
- Provides API for version queries across codebase
- Supports orchestrator-specific version tracking
- Validates version consistency

Phase 15 of CORTEX Evolution v3.9

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class VersionInfo:
    """Version information container."""
    cortex_version: str
    planning_system_version: str
    orchestrator_versions: Dict[str, str]
    config_path: Path
    last_read: datetime
    
    def __str__(self) -> str:
        return (
            f"CORTEX v{self.cortex_version} | "
            f"Planning System v{self.planning_system_version}"
        )


class VersionManager:
    """
    Centralized version management for CORTEX.
    
    Reads version from cortex.config.json and provides consistent
    version information across all orchestrators and modules.
    
    Usage:
        vm = VersionManager()
        cortex_version = vm.get_cortex_version()
        planning_version = vm.get_planning_system_version()
        orchestrator_version = vm.get_orchestrator_version("planning_orchestrator")
    """
    
    # Singleton instance
    _instance: Optional['VersionManager'] = None
    
    def __new__(cls, config_path: Optional[Path] = None):
        """Ensure singleton pattern for version manager."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize version manager.
        
        Args:
            config_path: Optional path to cortex.config.json
                        (defaults to project root)
        """
        # Only initialize once (singleton pattern)
        if self._initialized:
            return
            
        self.config_path = config_path or self._find_config_path()
        self._version_cache: Optional[VersionInfo] = None
        self._orchestrator_versions: Dict[str, str] = {}
        self._initialized = True
        
        # Load initial version data
        self._load_versions()
        
        logger.info(f"✅ VersionManager initialized: {self._version_cache}")
    
    def _find_config_path(self) -> Path:
        """
        Find cortex.config.json by walking up from current directory.
        
        Returns:
            Path to cortex.config.json
            
        Raises:
            FileNotFoundError: If config file not found
        """
        current = Path.cwd()
        
        # Walk up directory tree
        for _ in range(10):  # Limit search depth
            config_file = current / "cortex.config.json"
            if config_file.exists():
                return config_file
            current = current.parent
        
        raise FileNotFoundError(
            "cortex.config.json not found. "
            "Ensure you're running from CORTEX project directory."
        )
    
    def _load_versions(self) -> None:
        """
        Load version information from cortex.config.json.
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
            KeyError: If required version fields missing
        """
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Extract version fields
            cortex_version = config.get('version', 'unknown')
            planning_system = config.get('planningSystem', {})
            planning_version = planning_system.get('version', 'unknown')
            
            # Create version info
            self._version_cache = VersionInfo(
                cortex_version=cortex_version,
                planning_system_version=planning_version,
                orchestrator_versions=self._orchestrator_versions.copy(),
                config_path=self.config_path,
                last_read=datetime.now()
            )
            
            logger.debug(f"Loaded versions: {self._version_cache}")
            
        except FileNotFoundError:
            logger.error(f"Config file not found: {self.config_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in config file: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to load versions: {e}")
            raise
    
    def get_cortex_version(self) -> str:
        """
        Get CORTEX version.
        
        Returns:
            CORTEX version string (e.g., "3.9.0")
        """
        if self._version_cache is None:
            self._load_versions()
        return self._version_cache.cortex_version
    
    def get_planning_system_version(self) -> str:
        """
        Get Planning System version.
        
        Returns:
            Planning System version string (e.g., "3.0")
        """
        if self._version_cache is None:
            self._load_versions()
        return self._version_cache.planning_system_version
    
    def get_orchestrator_version(self, orchestrator_name: str) -> str:
        """
        Get version for specific orchestrator.
        
        Args:
            orchestrator_name: Name of orchestrator
                             (e.g., "planning_orchestrator", "ado_orchestrator")
        
        Returns:
            Orchestrator version string or "unknown" if not registered
        """
        return self._orchestrator_versions.get(orchestrator_name, "unknown")
    
    def register_orchestrator_version(
        self, 
        orchestrator_name: str, 
        version: str
    ) -> None:
        """
        Register orchestrator-specific version.
        
        Args:
            orchestrator_name: Name of orchestrator
            version: Version string (e.g., "3.0", "2.5")
        """
        self._orchestrator_versions[orchestrator_name] = version
        
        # Update cache if loaded
        if self._version_cache is not None:
            self._version_cache.orchestrator_versions = (
                self._orchestrator_versions.copy()
            )
        
        logger.debug(
            f"Registered orchestrator: {orchestrator_name} v{version}"
        )
    
    def get_version_info(self) -> VersionInfo:
        """
        Get complete version information.
        
        Returns:
            VersionInfo object with all version data
        """
        if self._version_cache is None:
            self._load_versions()
        return self._version_cache
    
    def refresh(self) -> None:
        """
        Reload version information from config file.
        
        Useful after config file updates.
        """
        logger.info("Refreshing version information...")
        self._load_versions()
    
    def validate_consistency(self) -> Dict[str, Any]:
        """
        Validate version consistency across system.
        
        Checks:
        - Config file exists and is readable
        - Required version fields present
        - Version format validity (semantic versioning)
        
        Returns:
            Dictionary with validation results:
            {
                'valid': bool,
                'errors': List[str],
                'warnings': List[str],
                'cortex_version': str,
                'planning_version': str,
                'orchestrators': Dict[str, str]
            }
        """
        errors = []
        warnings = []
        
        # Check config file
        if not self.config_path.exists():
            errors.append(f"Config file not found: {self.config_path}")
            return {
                'valid': False,
                'errors': errors,
                'warnings': warnings,
                'cortex_version': 'unknown',
                'planning_version': 'unknown',
                'orchestrators': {}
            }
        
        # Check version cache
        if self._version_cache is None:
            try:
                self._load_versions()
            except Exception as e:
                errors.append(f"Failed to load versions: {e}")
                return {
                    'valid': False,
                    'errors': errors,
                    'warnings': warnings,
                    'cortex_version': 'unknown',
                    'planning_version': 'unknown',
                    'orchestrators': {}
                }
        
        # Validate version formats
        cortex_version = self._version_cache.cortex_version
        planning_version = self._version_cache.planning_system_version
        
        if not self._is_valid_version_format(cortex_version):
            warnings.append(
                f"CORTEX version format unusual: {cortex_version}"
            )
        
        if not self._is_valid_version_format(planning_version):
            warnings.append(
                f"Planning System version format unusual: {planning_version}"
            )
        
        # Check orchestrator versions
        for name, version in self._orchestrator_versions.items():
            if not self._is_valid_version_format(version):
                warnings.append(
                    f"Orchestrator {name} version format unusual: {version}"
                )
        
        return {
            'valid': len(errors) == 0,
            'errors': errors,
            'warnings': warnings,
            'cortex_version': cortex_version,
            'planning_version': planning_version,
            'orchestrators': self._orchestrator_versions.copy()
        }
    
    def _is_valid_version_format(self, version: str) -> bool:
        """
        Check if version string follows semantic versioning.
        
        Args:
            version: Version string to validate
        
        Returns:
            True if valid format (X.Y.Z or X.Y), False otherwise
        """
        if version == 'unknown':
            return True  # Allow unknown versions
        
        parts = version.split('.')
        if len(parts) < 2 or len(parts) > 3:
            return False
        
        # Check all parts are numeric
        return all(part.isdigit() for part in parts)
    
    def get_version_string(self, include_orchestrators: bool = False) -> str:
        """
        Get formatted version string for display.
        
        Args:
            include_orchestrators: Include registered orchestrator versions
        
        Returns:
            Formatted version string
        """
        if self._version_cache is None:
            self._load_versions()
        
        base = (
            f"CORTEX v{self._version_cache.cortex_version} | "
            f"Planning System v{self._version_cache.planning_system_version}"
        )
        
        if include_orchestrators and self._orchestrator_versions:
            orch_str = ", ".join(
                f"{name} v{version}" 
                for name, version in sorted(self._orchestrator_versions.items())
            )
            return f"{base} | Orchestrators: {orch_str}"
        
        return base


# Global version manager instance
_version_manager: Optional[VersionManager] = None


def get_version_manager(config_path: Optional[Path] = None) -> VersionManager:
    """
    Get global VersionManager instance (singleton).
    
    Args:
        config_path: Optional path to cortex.config.json
    
    Returns:
        VersionManager instance
    """
    global _version_manager
    if _version_manager is None:
        _version_manager = VersionManager(config_path)
    return _version_manager


def get_cortex_version() -> str:
    """
    Convenience function to get CORTEX version.
    
    Returns:
        CORTEX version string
    """
    return get_version_manager().get_cortex_version()


def get_planning_system_version() -> str:
    """
    Convenience function to get Planning System version.
    
    Returns:
        Planning System version string
    """
    return get_version_manager().get_planning_system_version()


# Example usage in orchestrator classes:
# 
# from src.operations.modules.version.version_manager import get_version_manager
#
# class PlanningOrchestrator:
#     def __init__(self):
#         vm = get_version_manager()
#         vm.register_orchestrator_version("planning_orchestrator", "3.0")
#         self.version = vm.get_orchestrator_version("planning_orchestrator")
