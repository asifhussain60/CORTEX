"""
Configuration Manager for CORTEX 4.0

Manages configuration inheritance:
    IDE-specific → Shared → Defaults

Example:
    vscode.config.json (overrides) → shared.config.json (base) → hardcoded defaults

Design Principles:
- Deep merging (nested dicts fully merged)
- IDE-agnostic core (shared config is default)
- Validation on load
- Type safety via dataclass
"""

import os
import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional
from dataclasses import dataclass, field

from .ide_detector import IDEDetector, IDEType


@dataclass
class CortexConfig:
    """CORTEX configuration with IDE awareness."""
    
    # Core settings (always present)
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
    
    # Additional settings (from config files)
    custom: Dict[str, Any] = field(default_factory=dict)


class ConfigManager:
    """
    Manage CORTEX configuration with IDE-specific inheritance.
    
    Configuration Priority (highest to lowest):
    1. Environment variables (CORTEX_*)
    2. IDE-specific config (vscode.config.json, visualstudio.config.json)
    3. Shared config (shared.config.json)
    4. Hardcoded defaults (in CortexConfig dataclass)
    
    Example Usage:
        config_manager = ConfigManager(workspace_root)
        config = config_manager.load()
        print(config.ide_type)  # IDEType.VSCODE
        print(config.brain_path)  # Path("cortex-brain")
    """
    
    def __init__(self, workspace_root: Path):
        """
        Initialize configuration manager.
        
        Args:
            workspace_root: Root directory of the workspace
        """
        self.workspace_root = Path(workspace_root)
        self.config_dir = self.workspace_root / "cortex-brain" / "config"
        self.ide_type = IDEDetector.detect(self.workspace_root)
        self.logger = logging.getLogger(__name__)
    
    def load(self) -> CortexConfig:
        """
        Load configuration with IDE-specific inheritance.
        
        Returns:
            CortexConfig instance with merged settings
        """
        # Start with defaults
        config_dict = self._get_defaults()
        
        # Merge shared config
        shared_config = self._load_config_file("shared.config.json")
        if shared_config:
            config_dict = self._deep_merge(config_dict, shared_config)
        
        # Merge IDE-specific config
        if self.ide_type != IDEType.UNKNOWN:
            ide_config_file = IDEDetector.get_config_filename(self.ide_type)
            ide_config = self._load_config_file(ide_config_file)
            if ide_config:
                config_dict = self._deep_merge(config_dict, ide_config)
        
        # Apply environment variable overrides
        config_dict = self._apply_env_overrides(config_dict)
        
        # Convert to CortexConfig dataclass
        return self._dict_to_config(config_dict)
    
    def _get_defaults(self) -> Dict[str, Any]:
        """Get hardcoded default configuration."""
        return {
            "brain_path": str(self.workspace_root / "cortex-brain"),
            "log_level": "INFO",
            "max_conversation_history": 70,
            "ide_type": self.ide_type.value,
            "enable_telemetry": True,
            "enable_auto_alignment": True,
            "enable_skull_enforcement": True,
            "max_workers": 4,
            "cache_timeout_seconds": 300,
            "custom": {}
        }
    
    def _load_config_file(self, filename: str) -> Optional[Dict[str, Any]]:
        """Load a configuration file."""
        config_path = self.config_dir / filename
        
        if not config_path.exists():
            self.logger.debug(f"Config file not found: {config_path}")
            return None
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON in {filename}: {e}")
            return None
        except Exception as e:
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
            "CORTEX_LOG_LEVEL": "log_level",
            "CORTEX_BRAIN_PATH": "brain_path",
            "CORTEX_MAX_WORKERS": ("max_workers", int),
            "CORTEX_ENABLE_TELEMETRY": ("enable_telemetry", lambda x: x.lower() == "true")
        }
        
        for env_var, mapping in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value:
                if isinstance(mapping, tuple):
                    config_key, converter = mapping
                    try:
                        config[config_key] = converter(env_value)
                    except (ValueError, TypeError) as e:
                        self.logger.warning(f"Invalid value for {env_var}: {e}")
                else:
                    config[mapping] = env_value
        
        return config
    
    def _dict_to_config(self, config_dict: Dict[str, Any]) -> CortexConfig:
        """Convert dictionary to CortexConfig dataclass."""
        return CortexConfig(
            brain_path=Path(config_dict["brain_path"]),
            log_level=config_dict["log_level"],
            max_conversation_history=config_dict["max_conversation_history"],
            ide_type=IDEType(config_dict["ide_type"]),
            enable_telemetry=config_dict["enable_telemetry"],
            enable_auto_alignment=config_dict["enable_auto_alignment"],
            enable_skull_enforcement=config_dict["enable_skull_enforcement"],
            max_workers=config_dict["max_workers"],
            cache_timeout_seconds=config_dict["cache_timeout_seconds"],
            custom=config_dict.get("custom", {})
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
                "custom": config.custom
            }
            
            with open(config_file, 'w') as f:
                json.dump(config_dict, f, indent=2)
            
            self.logger.info(f"Configuration saved to {config_file}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error saving configuration: {e}")
            return False
