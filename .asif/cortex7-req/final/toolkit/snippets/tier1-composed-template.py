"""
CORTEX Toolkit - Tier1 Composed Tool Template
Purpose: Template for higher-level tools that compose tier0 primitives
Author: Asif Hussain
Date: 2026-01-14

REQUIREMENTS:
- Must use tier0 primitives only
- Must declare dependencies explicitly
- Must handle errors gracefully
- ≥95% test coverage required
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import json
from .tier0_primitives import read_file_safe, write_file_atomic


def toolkit_tool(tier: str, category: str, dependencies: List[str]):
    """Decorator for tier1+ tools with dependency tracking"""
    def decorator(func):
        func._toolkit_metadata = {
            "tier": tier,
            "category": category,
            "dependencies": dependencies,
            "capability_description": func.__doc__,
        }
        return func
    return decorator


@toolkit_tool(
    tier="tier1",
    category="config_management",
    dependencies=["tier0.file_ops.read_file_safe", "tier0.file_ops.write_file_atomic"]
)
def load_config(config_path: Path, format: str = "auto") -> Optional[Dict[str, Any]]:
    """
    Load configuration file (YAML or JSON) with validation.
    
    Args:
        config_path: Path to config file
        format: File format ("yaml", "json", "auto")
        
    Returns:
        Parsed config dict, or None if error
        
    Examples:
        >>> config = load_config(Path("settings.yaml"))
        >>> if config:
        ...     print(f"Loaded {len(config)} settings")
    """
    # Use tier0 primitive
    content = read_file_safe(config_path)
    if content is None:
        return None
    
    # Auto-detect format
    if format == "auto":
        format = "yaml" if config_path.suffix in [".yaml", ".yml"] else "json"
    
    try:
        if format == "yaml":
            return yaml.safe_load(content)
        elif format == "json":
            return json.loads(content)
        else:
            raise ValueError(f"Unsupported format: {format}")
    except Exception as e:
        logger.error(f"Error parsing {config_path}: {e}")
        return None


@toolkit_tool(
    tier="tier1",
    category="config_management",
    dependencies=["tier0.file_ops.write_file_atomic"]
)
def save_config(config_path: Path, data: Dict[str, Any], format: str = "auto") -> bool:
    """
    Save configuration to file atomically.
    
    Args:
        config_path: Destination path
        data: Configuration dictionary
        format: Output format ("yaml", "json", "auto")
        
    Returns:
        True if successful, False otherwise
    """
    # Auto-detect format
    if format == "auto":
        format = "yaml" if config_path.suffix in [".yaml", ".yml"] else "json"
    
    try:
        if format == "yaml":
            content = yaml.dump(data, default_flow_style=False, sort_keys=False)
        elif format == "json":
            content = json.dumps(data, indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        # Use tier0 primitive for atomic write
        return write_file_atomic(config_path, content)
        
    except Exception as e:
        logger.error(f"Error saving {config_path}: {e}")
        return False


# ============================================================================
# TESTS (≥95% coverage)
# ============================================================================

import pytest


@pytest.mark.unit
@pytest.mark.cross_platform
def test_load_config_yaml(tmp_path):
    """Test loading YAML config"""
    config_file = tmp_path / "config.yaml"
    config_file.write_text("key: value\nnumber: 42")
    
    config = load_config(config_file)
    assert config == {"key": "value", "number": 42}


@pytest.mark.unit
@pytest.mark.cross_platform
def test_load_config_json(tmp_path):
    """Test loading JSON config"""
    config_file = tmp_path / "config.json"
    config_file.write_text('{"key": "value", "number": 42}')
    
    config = load_config(config_file)
    assert config == {"key": "value", "number": 42}


@pytest.mark.unit
@pytest.mark.cross_platform
def test_save_config_yaml(tmp_path):
    """Test saving YAML config"""
    config_file = tmp_path / "output.yaml"
    data = {"setting": "enabled", "count": 10}
    
    success = save_config(config_file, data)
    assert success == True
    
    # Verify written content
    loaded = load_config(config_file)
    assert loaded == data
