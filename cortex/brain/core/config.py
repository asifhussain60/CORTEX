"""
Configuration Loader - Unified Config Management

Single implementation for loading YAML/JSON configuration files.
All configuration loading should go through this module.

Author: Asif Hussain
"""

import json
from pathlib import Path
from typing import Any, Dict, Optional

import yaml

from cortex.brain.core.result import Result, Ok, Err
from cortex.brain.core.path_resolver import resolve_path


def load_yaml(path: Path) -> Result[Dict[str, Any]]:
    """
    Load a YAML file safely.
    
    Args:
        path: Path to YAML file
    
    Returns:
        Result containing parsed YAML or error
    """
    try:
        if not path.exists():
            return Err(f"File not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if data is None:
            return Ok({})
        
        return Ok(data)
    
    except yaml.YAMLError as e:
        return Err(f"Invalid YAML in {path}: {e}")
    except Exception as e:
        return Err(f"Error loading {path}: {e}")


def load_json(path: Path) -> Result[Dict[str, Any]]:
    """
    Load a JSON file safely.
    
    Args:
        path: Path to JSON file
    
    Returns:
        Result containing parsed JSON or error
    """
    try:
        if not path.exists():
            return Err(f"File not found: {path}")
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return Ok(data)
    
    except json.JSONDecodeError as e:
        return Err(f"Invalid JSON in {path}: {e}")
    except Exception as e:
        return Err(f"Error loading {path}: {e}")


def load_config(name: str, config_dir: Optional[Path] = None) -> Result[Dict[str, Any]]:
    """
    Load a configuration file by name.
    
    Searches for config in:
    1. Provided config_dir
    2. cortex_brain/config/
    
    Supports both .yaml and .json extensions.
    
    Args:
        name: Config filename (with or without extension)
        config_dir: Optional directory to search
    
    Returns:
        Result containing config dict or error
    """
    if config_dir is None:
        config_dir = resolve_path("cortex_brain", "config")
    
    # Try with provided name first
    path = config_dir / name
    if path.exists():
        if path.suffix in ('.yaml', '.yml'):
            return load_yaml(path)
        elif path.suffix == '.json':
            return load_json(path)
    
    # Try adding extensions
    for ext in ('.yaml', '.yml', '.json'):
        path = config_dir / f"{name}{ext}"
        if path.exists():
            if ext in ('.yaml', '.yml'):
                return load_yaml(path)
            else:
                return load_json(path)
    
    return Err(f"Config not found: {name} in {config_dir}")


def save_yaml(path: Path, data: Dict[str, Any]) -> Result[None]:
    """
    Save data to a YAML file safely.
    
    Args:
        path: Path to save to
        data: Data to save
    
    Returns:
        Result indicating success or error
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)
        
        return Ok(None)
    
    except Exception as e:
        return Err(f"Error saving {path}: {e}")


def save_json(path: Path, data: Dict[str, Any]) -> Result[None]:
    """
    Save data to a JSON file safely.
    
    Args:
        path: Path to save to
        data: Data to save
    
    Returns:
        Result indicating success or error
    """
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        
        return Ok(None)
    
    except Exception as e:
        return Err(f"Error saving {path}: {e}")
