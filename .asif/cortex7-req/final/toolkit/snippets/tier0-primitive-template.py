"""
CORTEX Toolkit - Tier0 Primitive Template
Purpose: Template for creating atomic, zero-dependency tools
Author: Asif Hussain
Date: 2026-01-14

REQUIREMENTS:
- CORE-005: Use pathlib.Path for all file operations
- CORE-008: Created via TDD (RED → GREEN → REFACTOR)
- CORE-024: Use @toolkit_tool decorator
- Cross-platform (MAC/WIN/LINUX)
- 100% test coverage required
"""

from pathlib import Path
from typing import Any, Optional
from functools import wraps
import logging
import time

logger = logging.getLogger(__name__)


def toolkit_tool(tier: str, category: str):
    """
    Decorator for toolkit tools. Auto-registers in tool_registry.yaml
    
    Args:
        tier: Tool tier (tier0, tier1, tier2, tier3)
        category: Tool category (file_ops, process_ops, etc.)
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Log tool invocation to usage_analytics.db
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                execution_time = (time.time() - start_time) * 1000
                _log_tool_usage(func.__name__, tier, execution_time, True, None)
                return result
            except Exception as e:
                execution_time = (time.time() - start_time) * 1000
                _log_tool_usage(func.__name__, tier, execution_time, False, str(e))
                raise
        
        # Store metadata for registry
        wrapper._toolkit_metadata = {
            "tier": tier,
            "category": category,
            "capability_description": func.__doc__,
        }
        return wrapper
    return decorator


@toolkit_tool(tier="tier0", category="file_ops")
def read_file_safe(file_path: Path, encoding: str = "utf-8") -> Optional[str]:
    """
    Read file contents safely with error handling.
    
    Args:
        file_path: Path to file (pathlib.Path, CORE-005 compliant)
        encoding: File encoding (default: utf-8)
        
    Returns:
        File contents as string, or None if error
        
    Raises:
        TypeError: If file_path is not Path object
        
    Complexity: O(n) where n = file size
    
    Examples:
        >>> from pathlib import Path
        >>> content = read_file_safe(Path("config.yaml"))
        >>> if content:
        ...     print(f"Read {len(content)} characters")
    """
    # CORE-005: Enforce pathlib.Path
    if not isinstance(file_path, Path):
        raise TypeError(f"file_path must be Path, got {type(file_path)}")
    
    try:
        # Cross-platform file reading
        return file_path.read_text(encoding=encoding)
    except FileNotFoundError:
        logger.warning(f"File not found: {file_path}")
        return None
    except PermissionError:
        logger.error(f"Permission denied: {file_path}")
        return None
    except Exception as e:
        logger.error(f"Error reading {file_path}: {e}")
        return None


@toolkit_tool(tier="tier0", category="file_ops")
def write_file_atomic(file_path: Path, content: str, encoding: str = "utf-8") -> bool:
    """
    Write file atomically using temp file + rename pattern.
    
    Args:
        file_path: Destination path (pathlib.Path)
        content: Content to write
        encoding: File encoding
        
    Returns:
        True if successful, False otherwise
        
    Complexity: O(n) where n = content size
    
    Examples:
        >>> success = write_file_atomic(Path("output.txt"), "Hello World")
        >>> assert success == True
    """
    if not isinstance(file_path, Path):
        raise TypeError(f"file_path must be Path, got {type(file_path)}")
    
    try:
        # Create parent directories if needed
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to temp file first (atomic)
        temp_path = file_path.with_suffix(f"{file_path.suffix}.tmp")
        temp_path.write_text(content, encoding=encoding)
        
        # Atomic rename (POSIX guarantees atomicity)
        temp_path.replace(file_path)
        return True
        
    except Exception as e:
        logger.error(f"Error writing {file_path}: {e}")
        return False


def _log_tool_usage(tool_name: str, tier: str, execution_time_ms: float, 
                   success: bool, error_message: Optional[str]):
    """Log tool usage to usage_analytics.db"""
    # Implementation: Write to SQLite
    pass


# ============================================================================
# TESTS (TDD - CORE-008)
# ============================================================================

import pytest
from pathlib import Path


@pytest.mark.unit
@pytest.mark.cross_platform
def test_read_file_safe_success(tmp_path):
    """Test reading existing file"""
    test_file = tmp_path / "test.txt"
    test_file.write_text("Hello World")
    
    content = read_file_safe(test_file)
    assert content == "Hello World"


@pytest.mark.unit
@pytest.mark.cross_platform
def test_read_file_safe_not_found(tmp_path):
    """Test reading non-existent file"""
    content = read_file_safe(tmp_path / "missing.txt")
    assert content is None


@pytest.mark.unit
def test_read_file_safe_type_error():
    """Test TypeError when not using Path"""
    with pytest.raises(TypeError):
        read_file_safe("/some/string/path")


@pytest.mark.unit
@pytest.mark.cross_platform
def test_write_file_atomic_success(tmp_path):
    """Test atomic file write"""
    test_file = tmp_path / "output.txt"
    success = write_file_atomic(test_file, "Test Content")
    
    assert success == True
    assert test_file.read_text() == "Test Content"


@pytest.mark.unit
@pytest.mark.cross_platform
def test_write_file_atomic_creates_parents(tmp_path):
    """Test that parent directories are created"""
    test_file = tmp_path / "nested" / "dirs" / "file.txt"
    success = write_file_atomic(test_file, "Content")
    
    assert success == True
    assert test_file.exists()
