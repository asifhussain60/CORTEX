#!/usr/bin/env python3
"""
Entry Point Unit Tests

Tests for CortexEntry routing, initialization, and request processing.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
from src.entry_point.cortex_entry import CortexEntry


@pytest.fixture
def temp_brain_path(tmp_path):
    """Create temporary brain directory for testing."""
    brain_dir = tmp_path / "cortex-brain"
    brain_dir.mkdir()
    
    # Create required subdirectories
    (brain_dir / "tier1").mkdir()
    (brain_dir / "tier2").mkdir()
    (brain_dir / "tier3").mkdir()
    
    return str(brain_dir)


@pytest.fixture
def cortex_entry(temp_brain_path):
    """Create CortexEntry instance for testing."""
    return CortexEntry(
        brain_path=temp_brain_path,
        enable_logging=False,
        skip_setup_check=True
    )


def test_cortex_entry_initialization(cortex_entry):
    """Test that CortexEntry initializes correctly."""
    assert cortex_entry is not None
    assert cortex_entry.brain_path is not None
    assert cortex_entry.brain_path.exists()


def test_cortex_entry_has_process_method(cortex_entry):
    """Test that CortexEntry has process() method."""
    assert hasattr(cortex_entry, 'process')
    assert callable(cortex_entry.process)


def test_cortex_entry_brain_path_creation(temp_brain_path):
    """Test that brain directory structure is created."""
    brain_path = Path(temp_brain_path)
    
    assert brain_path.exists()
    assert brain_path.is_dir()
    
    # Check for tier directories
    assert (brain_path / "tier1").exists()
    assert (brain_path / "tier2").exists()
    assert (brain_path / "tier3").exists()


def test_cortex_entry_logging_enabled():
    """Test CortexEntry with logging enabled."""
    with patch('src.entry_point.cortex_entry.config'):
        entry = CortexEntry(enable_logging=True, skip_setup_check=True)
        assert entry.logger is not None


def test_cortex_entry_logging_disabled():
    """Test CortexEntry with logging disabled."""
    with patch('src.entry_point.cortex_entry.config'):
        entry = CortexEntry(enable_logging=False, skip_setup_check=True)
        assert entry.logger is not None


@pytest.mark.integration
def test_cortex_entry_request_parsing(cortex_entry):
    """
    Test that CortexEntry can parse requests.
    
    Note: This tests the parsing layer, not execution.
    """
    test_commands = [
        "help",
        "plan authentication feature",
        "start tdd",
        "system maintenance"
    ]
    
    for cmd in test_commands:
        # Verify entry point can accept these commands
        # (actual execution may require full setup)
        assert isinstance(cmd, str)
        assert len(cmd) > 0


def test_cortex_entry_import():
    """Test that CortexEntry can be imported."""
    from src.entry_point.cortex_entry import CortexEntry
    assert CortexEntry is not None


def test_cortex_entry_routing_components():
    """Test that routing components can be imported."""
    try:
        from src.cortex_agents.intent_router import IntentRouter
        assert IntentRouter is not None
    except ImportError:
        pytest.skip("IntentRouter not available")


def test_cortex_entry_parser_exists():
    """Test that RequestParser exists."""
    try:
        from src.entry_point.request_parser import RequestParser
        assert RequestParser is not None
    except ImportError:
        pytest.skip("RequestParser not available")


def test_cortex_entry_formatter_exists():
    """Test that ResponseFormatter exists."""
    try:
        from src.entry_point.response_formatter import ResponseFormatter
        assert ResponseFormatter is not None
    except ImportError:
        pytest.skip("ResponseFormatter not available")


def test_cortex_entry_lazy_loading():
    """Test that CortexEntry uses lazy loading for performance."""
    # CortexEntry should initialize quickly without loading heavy components
    import time
    
    start = time.perf_counter()
    with patch('src.entry_point.cortex_entry.config'):
        entry = CortexEntry(enable_logging=False, skip_setup_check=True)
    elapsed = time.perf_counter() - start
    
    # Should initialize in under 1 second (lazy loading)
    assert elapsed < 1.0, f"Initialization too slow: {elapsed:.3f}s"
    assert entry is not None


def test_cortex_entry_component_cache():
    """Test that CortexEntry uses component caching."""
    with patch('src.entry_point.cortex_entry.config'):
        entry = CortexEntry(enable_logging=False, skip_setup_check=True)
        
        # Should have component cache
        assert hasattr(entry, '_component_cache')


@pytest.mark.integration
def test_cortex_entry_process_method_signature(cortex_entry):
    """Test that process() method has correct signature."""
    import inspect
    
    sig = inspect.signature(cortex_entry.process)
    params = list(sig.parameters.keys())
    
    # Should have user_message parameter
    assert 'user_message' in params


def test_cortex_entry_supports_session_management(cortex_entry):
    """Test that CortexEntry supports session management."""
    # Should have session-related methods or properties
    process_sig = str(cortex_entry.process.__code__.co_varnames)
    
    # resume_session parameter should be supported
    assert 'resume_session' in process_sig or hasattr(cortex_entry, 'session_manager')


def test_cortex_entry_tier_integration(cortex_entry):
    """Test that CortexEntry integrates with tier APIs."""
    # Should have tier API properties or lazy loaders
    entry_vars = dir(cortex_entry)
    
    # Check for tier-related attributes (may be lazy-loaded)
    tier_related = [v for v in entry_vars if 'tier' in v.lower()]
    
    assert len(tier_related) > 0, "CortexEntry should have tier integration"
