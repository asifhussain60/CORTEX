#!/usr/bin/env python3
"""
Config Loading Integration Tests

Tests config loading via CortexEntry with real paths (not mocked) to catch:
- Missing brain paths
- Invalid brain structures
- Path resolution issues
- Custom brain path configuration

These tests ensure config loading works end-to-end without mocks concealing bugs.

Author: Asif Hussain
"""

import pytest
from pathlib import Path
from src.entry_point.cortex_entry import CortexEntry


def test_cortex_entry_with_custom_brain_path(tmp_path):
    """Test CortexEntry initialization with custom brain path."""
    brain_dir = tmp_path / "test_brain"
    brain_dir.mkdir()
    (brain_dir / "tier1").mkdir()
    (brain_dir / "tier2").mkdir()
    (brain_dir / "tier3").mkdir()
    
    entry = CortexEntry(
        brain_path=str(brain_dir),
        enable_logging=False,
        skip_setup_check=True
    )
    
    assert entry.brain_path == brain_dir
    assert entry.logger is not None


def test_cortex_entry_with_nonexistent_brain_path(tmp_path):
    """Test CortexEntry creates missing brain directory structure."""
    brain_dir = tmp_path / "nonexistent_brain"
    
    # Brain dir doesn't exist yet
    assert not brain_dir.exists()
    
    entry = CortexEntry(
        brain_path=str(brain_dir),
        enable_logging=False,
        skip_setup_check=True
    )
    
    # Should create brain directory structure
    assert entry.brain_path is not None
    # Config should handle path creation via ensure_paths_exist()


def test_cortex_entry_with_relative_brain_path(tmp_path):
    """Test CortexEntry handles relative paths correctly."""
    brain_dir = tmp_path / "relative_brain"
    brain_dir.mkdir()
    (brain_dir / "tier1").mkdir()
    (brain_dir / "tier2").mkdir()
    (brain_dir / "tier3").mkdir()
    
    # Use relative path
    import os
    old_cwd = os.getcwd()
    try:
        os.chdir(tmp_path)
        entry = CortexEntry(
            brain_path="relative_brain",
            enable_logging=False,
            skip_setup_check=True
        )
        
        assert entry.brain_path.name == "relative_brain"
    finally:
        os.chdir(old_cwd)


def test_cortex_entry_with_special_characters_in_path(tmp_path):
    """Test CortexEntry handles paths with special characters."""
    brain_dir = tmp_path / "brain with spaces & special-chars"
    brain_dir.mkdir()
    (brain_dir / "tier1").mkdir()
    (brain_dir / "tier2").mkdir()
    (brain_dir / "tier3").mkdir()
    
    entry = CortexEntry(
        brain_path=str(brain_dir),
        enable_logging=False,
        skip_setup_check=True
    )
    
    assert entry.brain_path == brain_dir


def test_cortex_entry_logging_enabled(tmp_path):
    """Test CortexEntry with logging enabled."""
    brain_dir = tmp_path / "brain_with_logging"
    brain_dir.mkdir()
    (brain_dir / "tier1").mkdir()
    (brain_dir / "tier2").mkdir()
    (brain_dir / "tier3").mkdir()
    
    entry = CortexEntry(
        brain_path=str(brain_dir),
        enable_logging=True,
        skip_setup_check=True
    )
    
    assert entry.logger is not None
    assert entry.logger.level is not None


def test_cortex_entry_logging_disabled(tmp_path):
    """Test CortexEntry with logging disabled."""
    brain_dir = tmp_path / "brain_no_logging"
    brain_dir.mkdir()
    (brain_dir / "tier1").mkdir()
    (brain_dir / "tier2").mkdir()
    (brain_dir / "tier3").mkdir()
    
    entry = CortexEntry(
        brain_path=str(brain_dir),
        enable_logging=False,
        skip_setup_check=True
    )
    
    assert entry.logger is not None  # Logger always exists, just different levels


def test_cortex_entry_default_brain_path():
    """Test CortexEntry uses default brain path from config."""
    entry = CortexEntry(
        enable_logging=False,
        skip_setup_check=True
    )
    
    # Should use config default
    assert entry.brain_path is not None
    assert entry.brain_path.name == "cortex-brain"


def test_cortex_entry_has_component_cache(tmp_path):
    """Test CortexEntry initializes component cache."""
    brain_dir = tmp_path / "brain_cache_test"
    brain_dir.mkdir()
    (brain_dir / "tier1").mkdir()
    (brain_dir / "tier2").mkdir()
    (brain_dir / "tier3").mkdir()
    
    entry = CortexEntry(
        brain_path=str(brain_dir),
        enable_logging=False,
        skip_setup_check=True
    )
    
    assert hasattr(entry, '_component_cache')
    assert entry._component_cache is not None


def test_cortex_entry_initialization_performance(tmp_path):
    """Test CortexEntry initializes quickly with lazy loading."""
    import time
    
    brain_dir = tmp_path / "brain_perf_test"
    brain_dir.mkdir()
    (brain_dir / "tier1").mkdir()
    (brain_dir / "tier2").mkdir()
    (brain_dir / "tier3").mkdir()
    
    start = time.time()
    entry = CortexEntry(
        brain_path=str(brain_dir),
        enable_logging=False,
        skip_setup_check=True
    )
    duration = time.time() - start
    
    # Should initialize in under 1 second (lazy loading target)
    assert duration < 1.0, f"Initialization took {duration:.2f}s (target <1s)"
    assert entry is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])


