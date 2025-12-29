"""
CORTEX Toolkit - Shared Configuration Module

Handles hierarchical configuration loading:
Environment > User > Repository > Global
"""
from pathlib import Path
import yaml
import os
from typing import Dict, Any, Optional
import json


class ToolkitConfig:
    """Hierarchical configuration manager for CORTEX Toolkit."""
    
    def __init__(self, toolkit_root: Optional[Path] = None):
        """
        Initialize configuration manager.
        
        Args:
            toolkit_root: Path to toolkit root. Auto-discovers if None.
        """
        self.toolkit_root = toolkit_root or self._discover_toolkit_root()
        self._config = self._load_hierarchical_config()
    
    def _discover_toolkit_root(self) -> Path:
        """Discover toolkit root directory."""
        if env_root := os.getenv("CORTEX_TOOLKIT_ROOT"):
            return Path(env_root)
        
        # Relative to this file
        return Path(__file__).parent.parent
    
    def _load_hierarchical_config(self) -> Dict[str, Any]:
        """
        Load configuration from all sources with priority:
        Environment > User > Repository > Global
        """
        config = {}
        
        # 1. Global workspace config (lowest priority)
        global_config_path = self._find_global_config()
        if global_config_path and global_config_path.exists():
            try:
                config.update(yaml.safe_load(global_config_path.read_text(encoding='utf-8')))
            except Exception:
                pass
        
        # 2. Repository config
        repo_config_path = self._find_repo_config()
        if repo_config_path and repo_config_path.exists():
            try:
                config.update(json.loads(repo_config_path.read_text(encoding='utf-8')))
            except Exception:
                pass
        
        # 3. User config
        user_config_path = Path.home() / ".cortex" / "config.yaml"
        if user_config_path.exists():
            try:
                config.update(yaml.safe_load(user_config_path.read_text(encoding='utf-8')))
            except Exception:
                pass
        
        # 4. Environment variables (highest priority)
        env_config = self._load_env_config()
        config.update(env_config)
        
        return config
    
    def _find_global_config(self) -> Optional[Path]:
        """Find global workspace config."""
        search_paths = [
            Path.cwd(),
            Path.cwd().parent,
            Path.cwd().parent.parent,
            self.toolkit_root.parent.parent
        ]
        
        for path in search_paths:
            global_config = path / "global-workspace-config.yaml"
            if global_config.exists():
                return global_config
        
        return None
    
    def _find_repo_config(self) -> Optional[Path]:
        """Find repository-specific config."""
        search_paths = [
            Path.cwd(),
            Path.cwd().parent,
            self.toolkit_root.parent
        ]
        
        for path in search_paths:
            repo_config = path / "cortex.config.json"
            if repo_config.exists():
                return repo_config
        
        return None
    
    def _load_env_config(self) -> Dict[str, Any]:
        """Load configuration from environment variables."""
        env_config = {}
        
        # CORTEX-specific environment variables
        if toolkit_root := os.getenv("CORTEX_TOOLKIT_ROOT"):
            env_config["cortex_toolkit_root"] = toolkit_root
        
        if cortex_root := os.getenv("CORTEX_ROOT"):
            env_config["cortex_root"] = cortex_root
        
        if python_path := os.getenv("CORTEX_PYTHON_PATH"):
            env_config["python_path"] = python_path
        
        return env_config
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value.
        
        Args:
            key: Configuration key.
            default: Default value if key not found.
            
        Returns:
            Configuration value or default.
        """
        return self._config.get(key, default)
    
    def get_toolkit_root(self) -> Path:
        """Get toolkit root path."""
        if root := self.get("cortex_toolkit_root"):
            return Path(root)
        return self.toolkit_root
    
    def get_workspace_roots(self) -> list[Path]:
        """Get all workspace root directories."""
        roots = self.get("workspace_roots", [])
        return [Path(r) for r in roots]
    
    def get_path_alias(self, alias: str) -> Optional[Path]:
        """
        Resolve path alias.
        
        Args:
            alias: Alias name (e.g., 'cortex', 'ksessions').
            
        Returns:
            Resolved path or None if alias not found.
        """
        aliases = self.get("path_aliases", [])
        for item in aliases:
            if item.get("alias") == alias:
                return Path(item["path"])
        return None
    
    def all(self) -> Dict[str, Any]:
        """Get all configuration."""
        return self._config.copy()


# Singleton instance
_config_instance: Optional[ToolkitConfig] = None


def get_config() -> ToolkitConfig:
    """Get singleton configuration instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = ToolkitConfig()
    return _config_instance


def reload_config():
    """Reload configuration from all sources."""
    global _config_instance
    _config_instance = None
    return get_config()
