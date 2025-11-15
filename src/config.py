"""
CORTEX Configuration Management

Handles cross-platform path resolution and configuration loading.
Supports development on multiple machines with different paths.

Machine Detection:
- Automatically detects current machine based on hostname or path
- Falls back to environment variables if cortex.config.json not found
- Uses relative paths as final fallback

Usage:
    from src.config import config
    
    # Get brain path (automatically resolved for current machine)
    brain_path = config.brain_path
    
    # Get project root
    root = config.root_path
    
    # Check if running in development mode
    if config.is_development:
        print("Development mode active")
"""

import os
import json
import socket
from pathlib import Path
from typing import Optional, Dict, Any


class CortexConfig:
    """
    CORTEX configuration manager.
    
    Handles:
    - Multi-machine path resolution
    - Configuration file loading
    - Environment variable fallbacks
    - Relative path resolution
    """
    
    def __init__(self):
        """Initialize configuration manager."""
        self._config: Optional[Dict[str, Any]] = None
        self._root_path: Optional[Path] = None
        self._brain_path: Optional[Path] = None
        self._hostname = socket.gethostname()
        
        # Load configuration
        self._load_config()
    
    def _load_config(self) -> None:
        """Load cortex.config.json with machine-specific overrides."""
        # Find config file (search up from current file)
        config_file = self._find_config_file()
        
        if config_file and config_file.exists():
            try:
                with open(config_file, 'r', encoding='utf-8') as f:
                    self._config = json.load(f)
            except Exception as e:
                print(f"Warning: Could not load cortex.config.json: {e}")
                self._config = {}
        else:
            self._config = {}
        
        # Determine root path
        self._root_path = self._determine_root_path()
        
        # Determine brain path
        self._brain_path = self._determine_brain_path()
    
    def _find_config_file(self) -> Optional[Path]:
        """
        Find cortex.config.json by searching up directory tree.
        
        Returns:
            Path to config file or None if not found
        """
        # Start from this file's directory
        current = Path(__file__).parent
        
        # Search up to 5 levels
        for _ in range(5):
            config_path = current / "cortex.config.json"
            if config_path.exists():
                return config_path
            
            # Move up one level
            parent = current.parent
            if parent == current:
                break  # Reached root
            current = parent
        
        # Also check project root (one level up from CORTEX/)
        project_root = Path(__file__).parent.parent.parent
        config_path = project_root / "cortex.config.json"
        if config_path.exists():
            return config_path
        
        return None
    
    def _determine_root_path(self) -> Path:
        """
        Determine CORTEX root path for current machine.
        
        Priority:
        1. Environment variable CORTEX_ROOT
        2. Machine-specific path in config
        3. Default rootPath in config
        4. Relative path from this file
        
        Returns:
            Path to CORTEX root directory
        """
        # 1. Environment variable
        env_root = os.getenv("CORTEX_ROOT")
        if env_root:
            return Path(env_root)
        
        # 2. Machine-specific path in config
        if self._config:
            machine_paths = self._config.get("machines", {})
            hostname_path = machine_paths.get(self._hostname, {}).get("rootPath")
            if hostname_path:
                return Path(hostname_path)
            
            # 3. Default rootPath
            default_path = self._config.get("application", {}).get("rootPath")
            if default_path:
                path = Path(default_path)
                # Convert macOS path to Windows if needed
                if os.name == 'nt' and str(path).startswith('/Users/'):
                    # Try to find equivalent Windows path dynamically
                    # /Users/asifhussain/PROJECTS/CORTEX -> {DRIVE}\PROJECTS\CORTEX
                    parts = str(path).split('/')
                    if 'PROJECTS' in parts:
                        idx = parts.index('PROJECTS')
                        # Use the drive where this script is located
                        current_drive = Path(__file__).drive
                        if current_drive:
                            windows_path = Path(current_drive) / Path(*parts[idx:])
                            if windows_path.exists():
                                return windows_path
                        # Fallback: try available drives dynamically
                        for drive_letter in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
                            drive = f'{drive_letter}:\\'
                            if os.path.exists(drive):
                                windows_path = Path(drive) / Path(*parts[idx:])
                                if windows_path.exists():
                                    return windows_path
                
                # Use as-is if exists
                if path.exists():
                    return path
        
        # 4. Relative path fallback
        # CORTEX/src/config.py -> go up to project root
        return Path(__file__).parent.parent.parent
    
    def _determine_brain_path(self) -> Path:
        """
        Determine cortex-brain directory path.
        
        Priority:
        1. Environment variable CORTEX_BRAIN_PATH
        2. Machine-specific brain path in config
        3. {root_path}/cortex-brain
        
        Returns:
            Path to cortex-brain directory
        """
        # 1. Environment variable
        env_brain = os.getenv("CORTEX_BRAIN_PATH")
        if env_brain:
            return Path(env_brain)
        
        # 2. Machine-specific path
        if self._config:
            machine_paths = self._config.get("machines", {}).get(self._hostname, {})
            brain_path = machine_paths.get("brainPath")
            if brain_path:
                return Path(brain_path)
        
        # 3. Default: {root}/cortex-brain
        return self._root_path / "cortex-brain"
    
    @property
    def root_path(self) -> Path:
        """Get CORTEX root directory path."""
        return self._root_path
    
    @property
    def brain_path(self) -> Path:
        """Get cortex-brain directory path."""
        return self._brain_path
    
    @property
    def src_path(self) -> Path:
        """Get CORTEX/src directory path."""
        return self._root_path / "CORTEX" / "src"
    
    @property
    def tests_path(self) -> Path:
        """Get CORTEX/tests directory path."""
        return self._root_path / "CORTEX" / "tests"
    
    @property
    def hostname(self) -> str:
        """Get current machine hostname."""
        return self._hostname
    
    @property
    def tier1_db_path(self) -> Path:
        """Get Tier 1 (Working Memory) database path."""
        return self._brain_path / "tier1-working-memory.db"
    
    @property
    def tier2_db_path(self) -> Path:
        """Get Tier 2 (Knowledge Graph) database path."""
        return self._brain_path / "tier2-knowledge-graph.db"
    
    @property
    def tier3_db_path(self) -> Path:
        """Get Tier 3 (Development Context) database path."""
        return self._brain_path / "tier3-development-context.db"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return not self._config.get("portability", {}).get("setupCompleted", False)
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get configuration value using dot notation.
        
        Args:
            key_path: Dot-separated key path (e.g., "application.name")
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        
        Example:
            name = config.get("application.name")  # "CORTEX"
            threshold = config.get("governance.testQualityThreshold", 70)
        """
        if not self._config:
            return default
        
        keys = key_path.split('.')
        value = self._config
        
        for key in keys:
            if isinstance(value, dict):
                value = value.get(key)
                if value is None:
                    return default
            else:
                return default
        
        return value
    
    def ensure_paths_exist(self) -> None:
        """
        Create essential CORTEX directories if they don't exist.
        
        Creates:
        - cortex-brain/tier1
        - cortex-brain/tier2
        - cortex-brain/tier3
        - cortex-brain/corpus-callosum
        """
        dirs_to_create = [
            self.brain_path / "tier1",
            self.brain_path / "tier2",
            self.brain_path / "tier3",
            self.brain_path / "corpus-callosum",
        ]
        
        for directory in dirs_to_create:
            directory.mkdir(parents=True, exist_ok=True)
    
    def get_machine_info(self) -> Dict[str, Any]:
        """
        Get information about current machine configuration.
        
        Returns:
            Dictionary with machine info
        """
        return {
            "hostname": self._hostname,
            "platform": os.name,
            "root_path": str(self._root_path),
            "brain_path": str(self._brain_path),
            "src_path": str(self.src_path),
            "tests_path": str(self.tests_path),
            "config_loaded": self._config is not None,
            "is_development": self.is_development,
        }


# Global configuration instance
config = CortexConfig()


# Convenience function for quick access
def get_brain_path() -> Path:
    """Get cortex-brain path for current machine."""
    return config.brain_path


def get_root_path() -> Path:
    """Get CORTEX root path for current machine."""
    return config.root_path

