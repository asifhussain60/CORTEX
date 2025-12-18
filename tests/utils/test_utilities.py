"""
Test Utilities for CORTEX 4.0

Provides helper functions and mock factories for testing.

Features:
- Mock object factories
- Test data generators
- Assertion helpers
- Test isolation utilities

Copyright © 2024-2025 Asif Hussain. All rights reserved.
"""

import json
import tempfile
from pathlib import Path
from typing import Any, Dict, List, Optional
from datetime import datetime
from unittest.mock import Mock, MagicMock

from src.core.config_manager import CortexConfig
from src.core.ide_detector import IDEType
from src.orchestrators.base.base_orchestrator import OrchestratorStatus, OrchestratorResult


class MockFactory:
    """Factory for creating mock objects for testing"""
    
    @staticmethod
    def create_cortex_config(
        workspace_root: Path,
        **overrides
    ) -> CortexConfig:
        """Create a CortexConfig with test defaults"""
        defaults = {
            "workspace_root": workspace_root,
            "brain_path": workspace_root / "cortex-brain",
            "log_level": "DEBUG",
            "max_conversation_history": 70,
            "ide_type": IDEType.UNKNOWN,
            "enable_telemetry": False,
            "enable_auto_alignment": True,
            "enable_skull_enforcement": True,
            "max_workers": 2,
            "cache_timeout_seconds": 60,
            "brain_config": {},
            "custom": {}
        }
        defaults.update(overrides)
        return CortexConfig(**defaults)
    
    @staticmethod
    def create_orchestrator_result(
        status: OrchestratorStatus = OrchestratorStatus.COMPLETED,
        success: bool = True,
        message: str = "Test execution successful",
        **kwargs
    ) -> OrchestratorResult:
        """Create an orchestrator result for testing"""
        defaults = {
            "data": {},
            "errors": [],
            "warnings": [],
            "execution_time_seconds": 0.5
        }
        defaults.update(kwargs)
        
        return OrchestratorResult(
            status=status,
            success=success,
            message=message,
            **defaults
        )
    
    @staticmethod
    def create_config_dict(
        workspace_root: Path,
        **overrides
    ) -> Dict[str, Any]:
        """Create a configuration dictionary for JSON files"""
        config = {
            "brain": {
                "max_conversations": 70,
                "tdd_enforcement": True,
                "timeout": 30,
                "tier0": {
                    "enforcement": "strict"
                },
                "tier1": {
                    "max_conversations": 70,
                    "fifo_enabled": False
                }
            },
            "orchestrator": {
                "auto_cleanup": True,
                "phase_validation": "strict",
                "max_retries": 3
            },
            "ide": {
                "integration_mode": "copilot_chat"
            }
        }
        
        # Deep merge overrides
        def deep_merge(base: Dict, override: Dict) -> Dict:
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = deep_merge(result[key], value)
                else:
                    result[key] = value
            return result
        
        return deep_merge(config, overrides)


class TempWorkspaceManager:
    """Manager for creating and cleaning up temporary workspaces"""
    
    def __init__(self, base_name: str = "cortex-test"):
        self.base_name = base_name
        self.temp_dir = None
        self.workspace = None
    
    def __enter__(self) -> Path:
        """Create temporary workspace"""
        self.temp_dir = tempfile.TemporaryDirectory(prefix=f"{self.base_name}-")
        self.workspace = Path(self.temp_dir.name)
        
        # Create standard CORTEX structure
        self._create_brain_structure()
        return self.workspace
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Cleanup temporary workspace"""
        if self.temp_dir:
            self.temp_dir.cleanup()
    
    def _create_brain_structure(self):
        """Create standard brain directory structure"""
        brain = self.workspace / "cortex-brain"
        brain.mkdir()
        
        # Tiers
        for tier in ["tier0", "tier1", "tier2", "tier3"]:
            (brain / tier).mkdir()
        
        # Config
        (brain / "config").mkdir()
        
        # Documents
        docs = brain / "documents"
        for category in ["reports", "analysis", "summaries", "investigations", "planning", "implementation-guides"]:
            (docs / category).mkdir(parents=True)
        
        # Templates
        (brain / "response-templates").mkdir()


class ConfigFileBuilder:
    """Builder for creating configuration files in test workspaces"""
    
    def __init__(self, config_dir: Path):
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def add_shared_config(self, config: Dict[str, Any]) -> 'ConfigFileBuilder':
        """Add shared.config.json"""
        config_file = self.config_dir / "shared.config.json"
        config_file.write_text(json.dumps(config, indent=2))
        return self
    
    def add_vscode_config(self, config: Dict[str, Any]) -> 'ConfigFileBuilder':
        """Add vscode.config.json"""
        config_file = self.config_dir / "vscode.config.json"
        config_file.write_text(json.dumps(config, indent=2))
        return self
    
    def add_visualstudio_config(self, config: Dict[str, Any]) -> 'ConfigFileBuilder':
        """Add visualstudio.config.json"""
        config_file = self.config_dir / "visualstudio.config.json"
        config_file.write_text(json.dumps(config, indent=2))
        return self
    
    def add_corrupted_config(self, filename: str) -> 'ConfigFileBuilder':
        """Add corrupted JSON file for error testing"""
        config_file = self.config_dir / filename
        config_file.write_text("INVALID JSON{{{")
        return self


class AssertionHelpers:
    """Helper methods for common test assertions"""
    
    @staticmethod
    def assert_config_has_keys(config: Dict[str, Any], *keys: str):
        """Assert that config dict has all specified keys"""
        for key in keys:
            assert key in config, f"Config missing key: {key}"
    
    @staticmethod
    def assert_path_exists(path: Path, message: str = ""):
        """Assert that path exists"""
        assert path.exists(), message or f"Path does not exist: {path}"
    
    @staticmethod
    def assert_file_contains(file_path: Path, content: str):
        """Assert that file contains specific content"""
        assert file_path.exists(), f"File does not exist: {file_path}"
        file_content = file_path.read_text()
        assert content in file_content, f"File does not contain: {content}"
    
    @staticmethod
    def assert_orchestrator_success(result: OrchestratorResult):
        """Assert that orchestrator completed successfully"""
        assert result.success, f"Orchestrator failed: {result.message}"
        assert result.status == OrchestratorStatus.COMPLETED, \
            f"Orchestrator status is {result.status}, expected COMPLETED"
    
    @staticmethod
    def assert_no_errors(result: OrchestratorResult):
        """Assert that orchestrator result has no errors"""
        assert len(result.errors) == 0, \
            f"Orchestrator has errors: {result.errors}"


class TestIsolation:
    """Utilities for test isolation and cleanup"""
    
    @staticmethod
    def clear_environment_vars(*var_names: str):
        """Clear specified environment variables"""
        import os
        for var_name in var_names:
            if var_name in os.environ:
                del os.environ[var_name]
    
    @staticmethod
    def reset_module_caches(*module_names: str):
        """Reset module-level caches"""
        import sys
        for module_name in module_names:
            if module_name in sys.modules:
                module = sys.modules[module_name]
                if hasattr(module, 'reset_cache'):
                    module.reset_cache()
    
    @staticmethod
    def cleanup_temp_files(*file_paths: Path):
        """Clean up temporary files"""
        for file_path in file_paths:
            if file_path.exists():
                if file_path.is_dir():
                    import shutil
                    shutil.rmtree(file_path)
                else:
                    file_path.unlink()


# Convenience exports
create_cortex_config = MockFactory.create_cortex_config
create_orchestrator_result = MockFactory.create_orchestrator_result
create_config_dict = MockFactory.create_config_dict
