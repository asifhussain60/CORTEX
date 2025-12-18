"""
Configuration Manager for CORTEX 4.0

Manages configuration with hybrid centralization:
- Shared config: ~/.cortex/shared/ (cross-workspace settings)
- Per-repo config: {workspace}/cortex-brain/config/ (workspace-specific)

Configuration Priority (highest to lowest):
1. Environment variables (CORTEX_*)
2. IDE-specific config (vscode.config.json, visualstudio.config.json)
3. Workspace config (cortex-brain/config/shared.config.json)
4. Shared global config (~/.cortex/shared/config.json)
5. Hardcoded defaults

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
Version: 4.0.0
"""

import json
import logging
import os
import platform
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field, asdict

from .ide_detector import IDEDetector, IDEType


@dataclass
class CortexConfig:
    """CORTEX configuration with IDE awareness and subscriptable access."""
    
    # Core settings (always present)
    workspace_root: Path
    brain_path: Path
    log_level: str = "INFO"
    max_conversation_history: int = 70
    
    # IDE-specific settings
    ide_type: IDEType = IDEType.UNKNOWN
    ide_config_path: Optional[Path] = None
    
    # Feature flags
    enable_telemetry: bool = True
    enable_auto_alignment: bool = True
    enable_skull_enforcement: bool = True
    
    # Performance tuning
    max_workers: int = 4
    cache_timeout_seconds: int = 300
    
    # Brain configuration
    brain_config: Dict[str, Any] = field(default_factory=dict)
    
    # Additional settings (from config files)
    custom: Dict[str, Any] = field(default_factory=dict)
    
    def __getitem__(self, key: str) -> Any:
        """Enable subscriptable access: config['key']"""
        # Check if it's a direct attribute
        if hasattr(self, key):
            value = getattr(self, key)
            # If it's a dict, return a proxy that supports chained subscripting
            if isinstance(value, dict):
                return value
            return value
        # Check in custom dict
        elif key in self.custom:
            return self.custom[key]
        # Check in brain_config
        elif key in self.brain_config:
            return self.brain_config[key]
        raise KeyError(f"Configuration key not found: {key}")
    
    def __setitem__(self, key: str, value: Any):
        """Enable subscriptable assignment: config['key'] = value"""
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            self.custom[key] = value
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get config value with default fallback."""
        try:
            return self[key]
        except KeyError:
            return default
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        config_dict = asdict(self)
        # Convert Path objects to strings
        config_dict["workspace_root"] = str(self.workspace_root)
        config_dict["brain_path"] = str(self.brain_path)
        if self.ide_config_path:
            config_dict["ide_config_path"] = str(self.ide_config_path)
        config_dict["ide_type"] = self.ide_type.value
        return config_dict


class ConfigManager:
    """
    Manage CORTEX configuration with hybrid centralization.
    
    Configuration Priority (highest to lowest):
    1. Environment variables (CORTEX_*)
    2. IDE-specific config (vscode.config.json, visualstudio.config.json)
    3. Workspace config (cortex-brain/config/shared.config.json)
    4. Global shared config (~/.cortex/shared/config.json)
    5. Hardcoded defaults (in CortexConfig dataclass)
    
    Hybrid Centralization:
    - Global: ~/.cortex/shared/config.json (machine-wide defaults)
    - Per-Repo: {workspace}/cortex-brain/config/shared.config.json (workspace overrides)
    
    Example Usage:
        config_manager = ConfigManager(workspace_root)
        config = config_manager.load()
        print(config.ide_type)  # IDEType.VSCODE
        print(config['brain_path'])  # Subscriptable access
        print(config.get('custom_key', 'default'))  # With default
    """
    
    def __init__(self, workspace_root: Path):
        """
        Initialize configuration manager.
        
        Args:
            workspace_root: Root directory of the workspace
        """
        self.workspace_root = Path(workspace_root)
        self.config_dir = self.workspace_root / "cortex-brain" / "config"
        self.global_config_dir = self._get_global_config_dir()
        self.ide_type = IDEDetector.detect(self.workspace_root)
        self.logger = logging.getLogger(__name__)
        self._cached_config: Optional[CortexConfig] = None
    
    def _get_global_config_dir(self) -> Path:
        """Get global shared configuration directory based on platform."""
        if platform.system() == "Windows":
            base = Path(os.getenv("USERPROFILE", "C:\\Users\\Default"))
        else:
            base = Path.home()
        
        return base / ".cortex" / "shared"
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value with dot notation support.
        
        Args:
            key: Configuration key (supports dot notation: 'brain.tier1.max_conversations')
            default: Default value if key not found
        
        Returns:
            Configuration value or default
        """
        if not self._cached_config:
            self._cached_config = self.load()
        
        # Support dot notation
        keys = key.split('.')
        value = self._cached_config
        
        for k in keys:
            # Try dict-like access (for CortexConfig subscriptable or dict)
            if isinstance(value, dict):
                if k in value:
                    value = value[k]
                else:
                    return default
            # Try attribute access
            elif hasattr(value, '__getitem__'):
                try:
                    value = value[k]
                except (KeyError, TypeError):
                    return default
            elif hasattr(value, k):
                value = getattr(value, k)
            else:
                return default
            
            if value is None:
                return default
        
        return value
    
    def reload(self) -> CortexConfig:
        """Clear cached configuration and force reload."""
        self._cached_config = None
        self.logger.debug("Configuration cache cleared")
        return self.load()
    
    def load(self) -> CortexConfig:
        """
        Load configuration with hybrid centralization.
        
        Priority order:
        1. Environment variables
        2. IDE-specific config (workspace)
        3. Workspace shared config
        4. Global shared config
        5. Defaults
        
        Returns:
            CortexConfig instance with merged settings
        """
        # Start with defaults
        config_dict = self._get_defaults()
        
        # Merge global shared config
        global_shared = self._load_config_file_from_dir(
            self.global_config_dir,
            "config.json"
        )
        if global_shared:
            config_dict = self._deep_merge(config_dict, global_shared)
            self.logger.debug("Merged global shared configuration")
        
        # Merge workspace shared config
        workspace_shared = self._load_config_file("shared.config.json", strict=True)
        if workspace_shared:
            config_dict = self._deep_merge(config_dict, workspace_shared)
            self.logger.debug("Merged workspace shared configuration")
        
        # Merge IDE-specific config
        if self.ide_type != IDEType.UNKNOWN:
            ide_config_file = IDEDetector.get_config_filename(self.ide_type)
            ide_config = self._load_config_file(ide_config_file)
            if ide_config:
                config_dict = self._deep_merge(config_dict, ide_config)
                self.logger.debug(f"Merged IDE-specific configuration: {ide_config_file}")
        
        # Apply environment variable overrides
        config_dict = self._apply_env_overrides(config_dict)
        
        # Convert to CortexConfig dataclass
        return self._dict_to_config(config_dict)
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get hardcoded default configuration."""
        return {
            "workspace_root": str(self.workspace_root),
            "brain_path": str(self.workspace_root / "cortex-brain"),
            "log_level": "INFO",
            "max_conversation_history": 70,
            "ide_type": self.ide_type.value,
            "enable_telemetry": True,
            "enable_auto_alignment": True,
            "enable_skull_enforcement": True,
            "max_workers": 4,
            "cache_timeout_seconds": 300,
            "brain_config": {},
            "custom": {}
        }
    
    def _load_config_file(self, filename: str, strict: bool = False) -> Optional[Dict[str, Any]]:
        """Load a configuration file from workspace config directory."""
        return self._load_config_file_from_dir(self.config_dir, filename, strict=strict)
    
    def _load_config_file_from_dir(
        self,
        directory: Path,
        filename: str,
        strict: bool = False
    ) -> Optional[Dict[str, Any]]:
        """Load a configuration file from specified directory.
        
        Args:
            directory: Directory containing config file
            filename: Name of config file
            strict: If True, raise exceptions; if False, be fault-tolerant
            
        Raises:
            FileNotFoundError: If strict=True and file not found
            json.JSONDecodeError: If strict=True and JSON invalid
        """
        config_path = directory / filename
        
        if not config_path.exists():
            if strict:
                raise FileNotFoundError(f"Config file not found: {filename}")
            self.logger.debug(f"Config file not found: {config_path}")
            return None
        
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                self.logger.debug(f"Loaded config from {filename}")
                return config
        except json.JSONDecodeError as e:
            if strict:
                raise
            self.logger.error(f"Invalid JSON in {filename}: {e}")
            return None  # Return None instead of raising to be fault-tolerant
        except Exception as e:
            if strict:
                raise
            self.logger.error(f"Error loading {filename}: {e}")
            return None
    
    def _deep_merge(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Deep merge two dictionaries.
        
        Args:
            base: Base dictionary
            override: Override dictionary (takes precedence)
            
        Returns:
            Merged dictionary
        """
        result = base.copy()
        
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                result[key] = self._deep_merge(result[key], value)
            else:
                result[key] = value
        
        return result
    
    def _apply_env_overrides(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply environment variable overrides."""
        env_mappings = {
            "CORTEX_LOG_LEVEL": ("log_level", str),
            "CORTEX_BRAIN_PATH": ("brain_path", str),
            "CORTEX_MAX_WORKERS": ("max_workers", int),
            "CORTEX_ENABLE_TELEMETRY": ("enable_telemetry", lambda x: x.lower() == "true"),
            "CORTEX_ENABLE_AUTO_ALIGNMENT": ("enable_auto_alignment", lambda x: x.lower() == "true"),
            "CORTEX_ENABLE_SKULL": ("enable_skull_enforcement", lambda x: x.lower() == "true")
        }
        
        for env_var, (config_key, converter) in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                try:
                    config[config_key] = converter(env_value)
                    self.logger.debug(f"Applied env override: {env_var} -> {config_key}")
                except Exception as e:
                    self.logger.warning(f"Failed to apply env override {env_var}: {e}")
        
        # Handle nested brain config overrides
        if "CORTEX_MAX_CONVERSATIONS" in os.environ:
            try:
                max_conv = int(os.environ["CORTEX_MAX_CONVERSATIONS"])
                if "brain" not in config:
                    config["brain"] = {}
                config["brain"]["max_conversations"] = max_conv
                self.logger.debug(f"Applied env override: CORTEX_MAX_CONVERSATIONS -> brain.max_conversations")
            except ValueError:
                pass  # Ignore invalid values
        
        if "CORTEX_TDD_ENFORCEMENT" in os.environ:
            value = os.environ["CORTEX_TDD_ENFORCEMENT"].lower()
            if value in ("true", "false"):
                if "brain" not in config:
                    config["brain"] = {}
                config["brain"]["tdd_enforcement"] = (value == "true")
                self.logger.debug(f"Applied env override: CORTEX_TDD_ENFORCEMENT -> brain.tdd_enforcement")
        
        return config
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> CortexConfig:
        """Convert dictionary to CortexConfig dataclass."""
        # Known keys that map to dataclass fields
        known_keys = {
            "workspace_root", "brain_path", "log_level", "max_conversation_history",
            "ide_type", "ide_config_path", "enable_telemetry", "enable_auto_alignment",
            "enable_skull_enforcement", "max_workers", "cache_timeout_seconds",
            "brain_config"
        }
        
        # Separate custom keys from known keys
        custom = {}
        for key, value in config_dict.items():
            if key not in known_keys and key != "custom":
                custom[key] = value
        
        # Merge with existing custom dict
        if "custom" in config_dict:
            custom.update(config_dict["custom"])
        
        return CortexConfig(
            workspace_root=Path(config_dict["workspace_root"]),
            brain_path=Path(config_dict["brain_path"]),
            log_level=config_dict["log_level"],
            max_conversation_history=config_dict["max_conversation_history"],
            ide_type=IDEType(config_dict["ide_type"]),
            ide_config_path=Path(config_dict["ide_config_path"]) if config_dict.get("ide_config_path") else None,
            enable_telemetry=config_dict["enable_telemetry"],
            enable_auto_alignment=config_dict["enable_auto_alignment"],
            enable_skull_enforcement=config_dict["enable_skull_enforcement"],
            max_workers=config_dict["max_workers"],
            cache_timeout_seconds=config_dict["cache_timeout_seconds"],
            brain_config=config_dict.get("brain_config", {}),
            custom=custom
        )
    
    def save(self, config: CortexConfig, target: str = "shared") -> bool:
        """
        Save configuration to file.
        
        Args:
            config: Configuration to save
            target: Target file ("shared", "vscode", "visualstudio")
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.config_dir.mkdir(parents=True, exist_ok=True)
            
            config_file = self.config_dir / f"{target}.config.json"
            config_dict = {
                "brain_path": str(config.brain_path),
                "log_level": config.log_level,
                "max_conversation_history": config.max_conversation_history,
                "enable_telemetry": config.enable_telemetry,
                "enable_auto_alignment": config.enable_auto_alignment,
                "enable_skull_enforcement": config.enable_skull_enforcement,
                "max_workers": config.max_workers,
                "cache_timeout_seconds": config.cache_timeout_seconds,
                "brain_config": config.brain_config,
                "custom": config.custom
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            self.logger.info(f"Configuration saved to {config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
