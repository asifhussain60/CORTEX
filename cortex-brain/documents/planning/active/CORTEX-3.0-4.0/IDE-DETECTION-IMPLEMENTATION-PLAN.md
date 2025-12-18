# IDE Detection & Configuration System - Implementation Plan

**Version:** 1.0  
**Author:** Asif Hussain  
**Created:** December 18, 2025  
**Status:** 🟢 APPROVED - Phase 1, Week 1 Work  
**Branch:** CORTEX-4.0  
**Prerequisite:** Part of Foundation Prerequisite #5 (Configuration System)

---

## 📋 Executive Summary

Implementation plan for Cross-IDE Compatibility (MASTER-PLAN Section 1.5). Enables CORTEX 4.0 to operate seamlessly in both VSCode and Visual Studio with intelligent file separation and context detection.

**Timeline:** 2-3 days (part of Phase 1, Week 1)  
**Files Created:** 5 new files (~500 lines total)  
**Files Modified:** 3 existing files (~150 lines changes)  
**Test Coverage:** 95%+ target  
**Breaking Changes:** None (additive only)

---

## 🎯 Implementation Goals

1. **Automatic IDE Detection** - Detect VSCode vs Visual Studio at runtime
2. **Configuration Inheritance** - IDE-specific → shared config cascade
3. **File Separation** - `.vscode/` vs `.vs/` with zero conflicts
4. **Shared Brain** - Single brain instance regardless of IDE
5. **Zero Lock-In** - Developers can switch IDEs without migration

---

## 🏗️ Architecture

### Component Overview

```
src/core/
├── ide_detector.py           # IDE detection (120 lines)
├── config_manager.py         # Configuration inheritance (180 lines)
└── environment_context.py    # Environment state (80 lines)

cortex-brain/config/
├── shared.config.json        # IDE-agnostic defaults (60 lines)
├── vscode.config.json        # VSCode-specific overrides (40 lines)
└── visualstudio.config.json  # Visual Studio overrides (40 lines)

tests/core/
└── test_ide_detection.py     # Comprehensive tests (250 lines)
```

---

## 📝 Detailed Implementation

### 1. IDE Detector (`src/core/ide_detector.py`)

**Purpose:** Detect active IDE and load appropriate configuration.

**Implementation:**

```python
"""
IDE Detection Module for CORTEX 4.0

Detects the active IDE (VSCode, Visual Studio, or Unknown) based on:
1. Environment variables (VSCODE_*, VS_*)
2. Directory markers (.vscode/, .vs/)
3. Process inspection (parent process name)
4. Configuration hints (cortex-brain/ide-context.json)

Design Principles:
- Fast detection (<10ms)
- Cached results (avoid re-detection)
- Graceful degradation (defaults to shared config if unknown)
- No external dependencies
"""

import os
import json
import logging
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any
import psutil  # Will need to add to requirements.txt


class IDEType(Enum):
    """Supported IDE types."""
    VSCODE = "vscode"
    VISUAL_STUDIO = "visualstudio"
    UNKNOWN = "unknown"


class IDEDetector:
    """
    Detect active IDE and manage IDE context.
    
    Detection Strategy (in order of precedence):
    1. Explicit environment variable (CORTEX_IDE=vscode|visualstudio)
    2. IDE-specific environment variables (VSCODE_*, VS_*)
    3. Parent process name (Code.exe, devenv.exe)
    4. Directory markers (.vscode/settings.json, .vs/)
    5. Cached context (cortex-brain/ide-context.json)
    6. Default to UNKNOWN (use shared config)
    """
    
    _cached_ide: Optional[IDEType] = None
    _context_file = "cortex-brain/ide-context.json"
    
    @classmethod
    def detect(cls, workspace_root: Path) -> IDEType:
        """
        Detect the active IDE.
        
        Args:
            workspace_root: Root directory of the workspace
            
        Returns:
            IDEType enum value
        """
        if cls._cached_ide:
            return cls._cached_ide
            
        # Strategy 1: Explicit override
        explicit_ide = os.getenv("CORTEX_IDE")
        if explicit_ide:
            try:
                cls._cached_ide = IDEType(explicit_ide.lower())
                cls._save_context(workspace_root, cls._cached_ide)
                return cls._cached_ide
            except ValueError:
                logging.warning(f"Invalid CORTEX_IDE value: {explicit_ide}")
        
        # Strategy 2: IDE-specific environment variables
        if os.getenv("VSCODE_PID") or os.getenv("VSCODE_IPC_HOOK"):
            cls._cached_ide = IDEType.VSCODE
            cls._save_context(workspace_root, cls._cached_ide)
            return cls._cached_ide
            
        if os.getenv("VisualStudioVersion") or os.getenv("VSINSTALLDIR"):
            cls._cached_ide = IDEType.VISUAL_STUDIO
            cls._save_context(workspace_root, cls._cached_ide)
            return cls._cached_ide
        
        # Strategy 3: Parent process detection
        try:
            parent = psutil.Process(os.getppid())
            parent_name = parent.name().lower()
            
            if "code" in parent_name:  # Code.exe, code.exe, VSCode
                cls._cached_ide = IDEType.VSCODE
                cls._save_context(workspace_root, cls._cached_ide)
                return cls._cached_ide
                
            if "devenv" in parent_name or "visualstudio" in parent_name:
                cls._cached_ide = IDEType.VISUAL_STUDIO
                cls._save_context(workspace_root, cls._cached_ide)
                return cls._cached_ide
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            logging.debug("Could not inspect parent process for IDE detection")
        
        # Strategy 4: Directory markers
        vscode_dir = workspace_root / ".vscode"
        vs_dir = workspace_root / ".vs"
        
        # Prefer most recently modified
        vscode_time = vscode_dir.stat().st_mtime if vscode_dir.exists() else 0
        vs_time = vs_dir.stat().st_mtime if vs_dir.exists() else 0
        
        if vscode_time > vs_time and vscode_time > 0:
            cls._cached_ide = IDEType.VSCODE
            cls._save_context(workspace_root, cls._cached_ide)
            return cls._cached_ide
        elif vs_time > 0:
            cls._cached_ide = IDEType.VISUAL_STUDIO
            cls._save_context(workspace_root, cls._cached_ide)
            return cls._cached_ide
        
        # Strategy 5: Cached context
        cached = cls._load_context(workspace_root)
        if cached:
            cls._cached_ide = cached
            return cls._cached_ide
        
        # Strategy 6: Default to unknown
        cls._cached_ide = IDEType.UNKNOWN
        logging.info("Could not detect IDE, using shared configuration")
        return cls._cached_ide
    
    @classmethod
    def _save_context(cls, workspace_root: Path, ide_type: IDEType) -> None:
        """Save detected IDE context for future sessions."""
        context_path = workspace_root / cls._context_file
        context_path.parent.mkdir(parents=True, exist_ok=True)
        
        context = {
            "detected_ide": ide_type.value,
            "detection_time": os.times().elapsed,
            "environment": {
                "os": os.name,
                "platform": os.sys.platform
            }
        }
        
        with open(context_path, 'w') as f:
            json.dump(context, f, indent=2)
    
    @classmethod
    def _load_context(cls, workspace_root: Path) -> Optional[IDEType]:
        """Load previously saved IDE context."""
        context_path = workspace_root / cls._context_file
        
        if not context_path.exists():
            return None
            
        try:
            with open(context_path, 'r') as f:
                context = json.load(f)
                return IDEType(context.get("detected_ide", "unknown"))
        except (json.JSONDecodeError, ValueError, FileNotFoundError):
            return None
    
    @classmethod
    def reset_cache(cls) -> None:
        """Reset cached IDE detection (for testing)."""
        cls._cached_ide = None
    
    @classmethod
    def get_config_filename(cls, ide_type: IDEType) -> str:
        """Get configuration filename for IDE type."""
        return f"{ide_type.value}.config.json"
    
    @classmethod
    def get_ide_directory(cls, ide_type: IDEType) -> str:
        """Get IDE-specific directory name."""
        if ide_type == IDEType.VSCODE:
            return ".vscode"
        elif ide_type == IDEType.VISUAL_STUDIO:
            return ".vs"
        else:
            return ".cortex"  # Fallback for unknown IDEs
```

**Key Features:**
- ✅ Multi-strategy detection (6 levels)
- ✅ Context caching (<10ms after first detection)
- ✅ Explicit override support (`CORTEX_IDE` env var)
- ✅ Graceful degradation
- ✅ No breaking changes

---

### 2. Configuration Manager (`src/core/config_manager.py`)

**Purpose:** Manage IDE-specific and shared configuration with inheritance.

**Implementation:**

```python
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
- Type safety
"""

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
        self.workspace_root = workspace_root
        self.config_dir = workspace_root / "cortex-brain" / "config"
        self.ide_type = IDEDetector.detect(workspace_root)
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
                    config[config_key] = converter(env_value)
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
```

---

### 3. Configuration Files

**`cortex-brain/config/shared.config.json`** (IDE-agnostic defaults):

```json
{
  "brain_path": "cortex-brain",
  "log_level": "INFO",
  "max_conversation_history": 70,
  "enable_telemetry": true,
  "enable_auto_alignment": true,
  "enable_skull_enforcement": true,
  "max_workers": 4,
  "cache_timeout_seconds": 300,
  "orchestrators": {
    "planning": {
      "auto_tdd": true,
      "complexity_detection": true
    },
    "tdd": {
      "enforce_red_phase": true,
      "coverage_threshold": 80
    },
    "maintenance": {
      "auto_cleanup": true,
      "aggressive_mode": false
    }
  },
  "brain": {
    "tier1_max_conversations": 70,
    "tier2_pattern_threshold": 3,
    "tier3_metrics_enabled": true
  }
}
```

**`cortex-brain/config/vscode.config.json`** (VSCode-specific overrides):

```json
{
  "custom": {
    "editor": {
      "integration_mode": "copilot_chat",
      "file_watching": true,
      "problem_matcher": "$tsc"
    },
    "ui": {
      "progress_location": "notification",
      "output_channel": "CORTEX"
    }
  }
}
```

**`cortex-brain/config/visualstudio.config.json`** (Visual Studio overrides):

```json
{
  "custom": {
    "editor": {
      "integration_mode": "extension",
      "solution_aware": true,
      "msbuild_integration": true
    },
    "ui": {
      "progress_location": "status_bar",
      "output_pane": "CORTEX"
    }
  }
}
```

---

### 4. Test Suite (`tests/core/test_ide_detection.py`)

**Coverage Target:** 95%+

```python
"""
Comprehensive tests for IDE detection and configuration management.

Test Coverage:
- IDE detection (all 6 strategies)
- Configuration inheritance
- Environment variable overrides
- File I/O and error handling
- Cache behavior
- Edge cases and fallbacks
"""

import pytest
import json
import os
from pathlib import Path
from unittest.mock import patch, MagicMock

from src.core.ide_detector import IDEDetector, IDEType
from src.core.config_manager import ConfigManager, CortexConfig


@pytest.fixture
def mock_workspace(tmp_path):
    """Create a temporary workspace structure."""
    workspace = tmp_path / "test-workspace"
    workspace.mkdir()
    
    # Create cortex-brain structure
    brain_dir = workspace / "cortex-brain"
    brain_dir.mkdir()
    
    config_dir = brain_dir / "config"
    config_dir.mkdir()
    
    return workspace


@pytest.fixture(autouse=True)
def reset_detector():
    """Reset IDE detector cache before each test."""
    IDEDetector.reset_cache()
    yield
    IDEDetector.reset_cache()


class TestIDEDetector:
    """Test suite for IDEDetector class."""
    
    def test_explicit_override_vscode(self, mock_workspace):
        """Test explicit CORTEX_IDE=vscode override."""
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}):
            result = IDEDetector.detect(mock_workspace)
            assert result == IDEType.VSCODE
    
    def test_explicit_override_visualstudio(self, mock_workspace):
        """Test explicit CORTEX_IDE=visualstudio override."""
        with patch.dict(os.environ, {"CORTEX_IDE": "visualstudio"}):
            result = IDEDetector.detect(mock_workspace)
            assert result == IDEType.VISUAL_STUDIO
    
    def test_vscode_environment_variables(self, mock_workspace):
        """Test detection via VSCode environment variables."""
        with patch.dict(os.environ, {"VSCODE_PID": "12345"}):
            result = IDEDetector.detect(mock_workspace)
            assert result == IDEType.VSCODE
    
    def test_visual_studio_environment_variables(self, mock_workspace):
        """Test detection via Visual Studio environment variables."""
        with patch.dict(os.environ, {"VisualStudioVersion": "17.0"}):
            result = IDEDetector.detect(mock_workspace)
            assert result == IDEType.VISUAL_STUDIO
    
    @patch('psutil.Process')
    def test_parent_process_vscode(self, mock_process, mock_workspace):
        """Test detection via parent process (VSCode)."""
        mock_parent = MagicMock()
        mock_parent.name.return_value = "Code.exe"
        mock_process.return_value = mock_parent
        
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.VSCODE
    
    @patch('psutil.Process')
    def test_parent_process_visualstudio(self, mock_process, mock_workspace):
        """Test detection via parent process (Visual Studio)."""
        mock_parent = MagicMock()
        mock_parent.name.return_value = "devenv.exe"
        mock_process.return_value = mock_parent
        
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.VISUAL_STUDIO
    
    def test_directory_marker_vscode(self, mock_workspace):
        """Test detection via .vscode/ directory."""
        vscode_dir = mock_workspace / ".vscode"
        vscode_dir.mkdir()
        
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.VSCODE
    
    def test_directory_marker_visualstudio(self, mock_workspace):
        """Test detection via .vs/ directory."""
        vs_dir = mock_workspace / ".vs"
        vs_dir.mkdir()
        
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.VISUAL_STUDIO
    
    def test_directory_marker_most_recent(self, mock_workspace):
        """Test detection prefers most recently modified directory."""
        import time
        
        vscode_dir = mock_workspace / ".vscode"
        vscode_dir.mkdir()
        
        time.sleep(0.1)  # Ensure different timestamps
        
        vs_dir = mock_workspace / ".vs"
        vs_dir.mkdir()
        
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.VISUAL_STUDIO  # .vs/ is newer
    
    def test_cached_context_loading(self, mock_workspace):
        """Test loading cached IDE context."""
        context_file = mock_workspace / "cortex-brain" / "ide-context.json"
        context_file.parent.mkdir(parents=True, exist_ok=True)
        
        context = {
            "detected_ide": "vscode",
            "detection_time": 123456,
            "environment": {"os": "nt", "platform": "win32"}
        }
        
        with open(context_file, 'w') as f:
            json.dump(context, f)
        
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.VSCODE
    
    def test_unknown_fallback(self, mock_workspace):
        """Test fallback to UNKNOWN when no detection method succeeds."""
        result = IDEDetector.detect(mock_workspace)
        assert result == IDEType.UNKNOWN
    
    def test_cache_behavior(self, mock_workspace):
        """Test that detection is cached after first call."""
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}):
            result1 = IDEDetector.detect(mock_workspace)
            assert result1 == IDEType.VSCODE
        
        # Remove env var, should still return cached value
        result2 = IDEDetector.detect(mock_workspace)
        assert result2 == IDEType.VSCODE
    
    def test_get_config_filename(self):
        """Test config filename generation."""
        assert IDEDetector.get_config_filename(IDEType.VSCODE) == "vscode.config.json"
        assert IDEDetector.get_config_filename(IDEType.VISUAL_STUDIO) == "visualstudio.config.json"
        assert IDEDetector.get_config_filename(IDEType.UNKNOWN) == "unknown.config.json"
    
    def test_get_ide_directory(self):
        """Test IDE directory name generation."""
        assert IDEDetector.get_ide_directory(IDEType.VSCODE) == ".vscode"
        assert IDEDetector.get_ide_directory(IDEType.VISUAL_STUDIO) == ".vs"
        assert IDEDetector.get_ide_directory(IDEType.UNKNOWN) == ".cortex"


class TestConfigManager:
    """Test suite for ConfigManager class."""
    
    def test_load_defaults_only(self, mock_workspace):
        """Test loading with no config files (defaults only)."""
        manager = ConfigManager(mock_workspace)
        config = manager.load()
        
        assert isinstance(config, CortexConfig)
        assert config.log_level == "INFO"
        assert config.max_conversation_history == 70
        assert config.enable_skull_enforcement is True
    
    def test_load_shared_config(self, mock_workspace):
        """Test loading shared configuration."""
        config_dir = mock_workspace / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "log_level": "DEBUG",
            "max_workers": 8
        }
        
        with open(config_dir / "shared.config.json", 'w') as f:
            json.dump(shared_config, f)
        
        manager = ConfigManager(mock_workspace)
        config = manager.load()
        
        assert config.log_level == "DEBUG"
        assert config.max_workers == 8
    
    def test_load_ide_specific_config(self, mock_workspace):
        """Test IDE-specific configuration overrides."""
        config_dir = mock_workspace / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"log_level": "INFO", "max_workers": 4}
        with open(config_dir / "shared.config.json", 'w') as f:
            json.dump(shared_config, f)
        
        vscode_config = {"log_level": "DEBUG"}
        with open(config_dir / "vscode.config.json", 'w') as f:
            json.dump(vscode_config, f)
        
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}):
            manager = ConfigManager(mock_workspace)
            config = manager.load()
            
            assert config.log_level == "DEBUG"  # Overridden
            assert config.max_workers == 4  # Inherited from shared
    
    def test_deep_merge(self, mock_workspace):
        """Test deep merging of nested dictionaries."""
        config_dir = mock_workspace / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {
            "custom": {
                "feature_a": {"enabled": True, "value": 100},
                "feature_b": {"enabled": False}
            }
        }
        
        ide_config = {
            "custom": {
                "feature_a": {"value": 200},
                "feature_c": {"enabled": True}
            }
        }
        
        with open(config_dir / "shared.config.json", 'w') as f:
            json.dump(shared_config, f)
        
        with open(config_dir / "vscode.config.json", 'w') as f:
            json.dump(ide_config, f)
        
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}):
            manager = ConfigManager(mock_workspace)
            config = manager.load()
            
            # feature_a: deep merged
            assert config.custom["feature_a"]["enabled"] is True  # From shared
            assert config.custom["feature_a"]["value"] == 200  # Overridden
            
            # feature_b: inherited
            assert config.custom["feature_b"]["enabled"] is False
            
            # feature_c: new from IDE config
            assert config.custom["feature_c"]["enabled"] is True
    
    def test_environment_variable_overrides(self, mock_workspace):
        """Test environment variable overrides."""
        with patch.dict(os.environ, {
            "CORTEX_LOG_LEVEL": "WARNING",
            "CORTEX_MAX_WORKERS": "16",
            "CORTEX_ENABLE_TELEMETRY": "false"
        }):
            manager = ConfigManager(mock_workspace)
            config = manager.load()
            
            assert config.log_level == "WARNING"
            assert config.max_workers == 16
            assert config.enable_telemetry is False
    
    def test_save_configuration(self, mock_workspace):
        """Test saving configuration to file."""
        manager = ConfigManager(mock_workspace)
        config = manager.load()
        config.log_level = "DEBUG"
        config.max_workers = 16
        
        success = manager.save(config, target="shared")
        assert success is True
        
        # Verify file was created
        config_file = mock_workspace / "cortex-brain" / "config" / "shared.config.json"
        assert config_file.exists()
        
        # Verify content
        with open(config_file, 'r') as f:
            saved = json.load(f)
            assert saved["log_level"] == "DEBUG"
            assert saved["max_workers"] == 16
    
    def test_invalid_json_handling(self, mock_workspace):
        """Test handling of invalid JSON in config files."""
        config_dir = mock_workspace / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        # Create invalid JSON file
        with open(config_dir / "shared.config.json", 'w') as f:
            f.write("{invalid json content")
        
        manager = ConfigManager(mock_workspace)
        config = manager.load()  # Should not crash
        
        assert config.log_level == "INFO"  # Falls back to defaults


class TestIntegration:
    """Integration tests for IDE detection + configuration."""
    
    def test_end_to_end_vscode(self, mock_workspace):
        """Test complete flow for VSCode."""
        # Setup environment
        vscode_dir = mock_workspace / ".vscode"
        vscode_dir.mkdir()
        
        config_dir = mock_workspace / "cortex-brain" / "config"
        config_dir.mkdir(parents=True)
        
        shared_config = {"log_level": "INFO"}
        with open(config_dir / "shared.config.json", 'w') as f:
            json.dump(shared_config, f)
        
        vscode_config = {"log_level": "DEBUG"}
        with open(config_dir / "vscode.config.json", 'w') as f:
            json.dump(vscode_config, f)
        
        # Execute
        manager = ConfigManager(mock_workspace)
        config = manager.load()
        
        # Verify
        assert config.ide_type == IDEType.VSCODE
        assert config.log_level == "DEBUG"
    
    def test_end_to_end_visual_studio(self, mock_workspace):
        """Test complete flow for Visual Studio."""
        # Setup environment
        with patch.dict(os.environ, {"VisualStudioVersion": "17.0"}):
            config_dir = mock_workspace / "cortex-brain" / "config"
            config_dir.mkdir(parents=True)
            
            shared_config = {"max_workers": 4}
            with open(config_dir / "shared.config.json", 'w') as f:
                json.dump(shared_config, f)
            
            vs_config = {"max_workers": 8}
            with open(config_dir / "visualstudio.config.json", 'w') as f:
                json.dump(vs_config, f)
            
            # Execute
            manager = ConfigManager(mock_workspace)
            config = manager.load()
            
            # Verify
            assert config.ide_type == IDEType.VISUAL_STUDIO
            assert config.max_workers == 8
    
    def test_switch_ides_preserves_brain(self, mock_workspace):
        """Test switching IDEs preserves brain state."""
        brain_dir = mock_workspace / "cortex-brain"
        tier1_dir = brain_dir / "tier1"
        tier1_dir.mkdir(parents=True)
        
        # Create mock brain data
        conversation_file = tier1_dir / "conversations.db"
        conversation_file.write_text("mock brain data")
        
        # Load as VSCode
        with patch.dict(os.environ, {"CORTEX_IDE": "vscode"}):
            manager1 = ConfigManager(mock_workspace)
            config1 = manager1.load()
            assert config1.ide_type == IDEType.VSCODE
        
        # Reset cache and load as Visual Studio
        IDEDetector.reset_cache()
        
        with patch.dict(os.environ, {"CORTEX_IDE": "visualstudio"}):
            manager2 = ConfigManager(mock_workspace)
            config2 = manager2.load()
            assert config2.ide_type == IDEType.VISUAL_STUDIO
        
        # Verify brain data unchanged
        assert conversation_file.read_text() == "mock brain data"
```

---

## 📊 Implementation Checklist

### Day 1: Core Implementation
- ☐ Create `src/core/ide_detector.py` (120 lines)
- ☐ Create `src/core/config_manager.py` (180 lines)
- ☐ Add `psutil` to `requirements.txt`
- ☐ Create config directory structure
- ☐ Create 3 config JSON files (shared, vscode, visualstudio)

### Day 2: Testing
- ☐ Create `tests/core/test_ide_detection.py` (250 lines)
- ☐ Write unit tests for IDEDetector (20+ tests)
- ☐ Write unit tests for ConfigManager (15+ tests)
- ☐ Write integration tests (5+ tests)
- ☐ Achieve 95%+ code coverage

### Day 3: Integration & Documentation
- ☐ Update `src/orchestrators/base/base_orchestrator.py` to use ConfigManager
- ☐ Add IDE context to Brain Tier 3 (metadata only)
- ☐ Create `.gitignore` templates for user repos
- ☐ Update MASTER-PLAN.md checklist (mark Phase 1, Week 1 IDE work complete)
- ☐ Test in both VSCode and Visual Studio (if available)

---

## ✅ Success Criteria

1. **Automatic Detection** - IDE detected in <10ms with 95%+ accuracy
2. **Zero Conflicts** - `.vscode/` and `.vs/` coexist without issues
3. **Configuration Inheritance** - 3-tier cascade works correctly
4. **Test Coverage** - 95%+ coverage on all new code
5. **No Breaking Changes** - Existing CORTEX 4.0 code unaffected
6. **Documentation Complete** - All public APIs documented

---

## 🚀 Next Steps (After IDE Detection)

Once IDE detection is complete, continue with remaining Phase 1 prerequisites:

- **Prerequisite #3:** Brain Tiers (Week 1-2)
- **Prerequisite #4:** Response Template System v4.0 (Week 2)
- **Prerequisite #6:** Testing Infrastructure (Week 2)
- **Prerequisite #7:** Dependency Injection (Week 3)
- **Prerequisite #8:** Logging & Monitoring (Week 3)
- **Prerequisite #9:** MCP Gateway Stub (Week 3)
- **Prerequisite #10:** Validation Script (Week 3)

**Timeline:** IDE detection complete by end of Day 3, Phase 1 Week 1. On track for Phase 3 orchestrator migration by Week 7.

---

**Status:** Ready for implementation on CORTEX-4.0 branch.
