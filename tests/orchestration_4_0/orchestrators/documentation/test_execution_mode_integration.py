"""
Tests for Execution Mode Integration module

Test coverage:
- Mode selection logic
- Context-aware formatting configuration
- Section inclusion rules
- Description formatting
- User statistics tracking
- Integration with ExecutionModeManager
- Edge cases and error handling
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

from src.orchestration_4_0.orchestrators.documentation.execution_mode_integration import (
    ExecutionModeIntegration,
    OutputFormat,
    FormattingConfig
)
from src.orchestration_4_0.execution.execution_mode import ExecutionMode


# ============================================================================
# Fixtures
# ============================================================================

@pytest.fixture
def mock_logger():
    """Mock logger"""
    return Mock()


@pytest.fixture
def config():
    """Basic configuration"""
    return {}


@pytest.fixture
def mode_integration(mock_logger, config):
    """ExecutionModeIntegration instance"""
    return ExecutionModeIntegration(mock_logger, config, user_id="test_user")


@pytest.fixture
def mode_integration_override(mock_logger):
    """ExecutionModeIntegration with forced autonomous mode"""
    config = {"force_mode": "autonomous"}
    return ExecutionModeIntegration(mock_logger, config, user_id="test_user")


# ============================================================================
# Mode Selection Tests
# ============================================================================

def test_select_mode_for_operation_default(mode_integration):
    """Test mode selection with default behavior"""
    mode = mode_integration.select_mode_for_operation(
        operation_name="generate_api_docs",
        estimated_duration=120
    )
    
    # Should return one of the valid modes
    assert isinstance(mode, ExecutionMode)
    assert mode in [
        ExecutionMode.AUTONOMOUS,
        ExecutionMode.SUPERVISED,
        ExecutionMode.HUMAN_IN_LOOP
    ]


def test_select_mode_for_operation_with_override(mode_integration):
    """Test mode selection with explicit override"""
    mode = mode_integration.select_mode_for_operation(
        operation_name="generate_api_docs",
        override_mode="supervised"
    )
    
    assert mode == ExecutionMode.SUPERVISED


def test_select_mode_for_operation_invalid_override(mode_integration):
    """Test mode selection with invalid override falls back to auto-select"""
    mode = mode_integration.select_mode_for_operation(
        operation_name="generate_api_docs",
        override_mode="invalid_mode"
    )
    
    # Should fall back to valid mode
    assert isinstance(mode, ExecutionMode)


def test_select_mode_for_operation_forced_autonomous(mode_integration_override):
    """Test mode selection with config-forced autonomous"""
    mode = mode_integration_override.select_mode_for_operation(
        operation_name="generate_api_docs"
    )
    
    assert mode == ExecutionMode.AUTONOMOUS


# ============================================================================
# Formatting Configuration Tests
# ============================================================================

def test_get_formatting_config_autonomous(mode_integration):
    """Test formatting config for AUTONOMOUS mode"""
    config = mode_integration.get_formatting_config(ExecutionMode.AUTONOMOUS)
    
    assert isinstance(config, FormattingConfig)
    assert config.detail_level == OutputFormat.CONCISE
    assert config.include_examples is False
    assert config.include_warnings is False
    assert config.include_diagrams is False
    assert config.include_quick_ref is True
    assert config.max_description_length == 200
    assert config.max_examples_per_item == 1


def test_get_formatting_config_supervised(mode_integration):
    """Test formatting config for SUPERVISED mode"""
    config = mode_integration.get_formatting_config(ExecutionMode.SUPERVISED)
    
    assert isinstance(config, FormattingConfig)
    assert config.detail_level == OutputFormat.STANDARD
    assert config.include_examples is True
    assert config.include_warnings is True
    assert config.include_diagrams is True
    assert config.include_quick_ref is True
    assert config.max_description_length == 500
    assert config.max_examples_per_item == 2


def test_get_formatting_config_human_in_loop(mode_integration):
    """Test formatting config for HUMAN_IN_LOOP mode"""
    config = mode_integration.get_formatting_config(ExecutionMode.HUMAN_IN_LOOP)
    
    assert isinstance(config, FormattingConfig)
    assert config.detail_level == OutputFormat.VERBOSE
    assert config.include_examples is True
    assert config.include_warnings is True
    assert config.include_diagrams is True
    assert config.include_quick_ref is True
    assert config.max_description_length == 1000
    assert config.max_examples_per_item == 3


# ============================================================================
# Section Inclusion Tests
# ============================================================================

def test_should_include_section_essential_always(mode_integration):
    """Test that essential sections are always included"""
    essential_sections = ["description", "parameters", "returns", "class_signature"]
    
    for section in essential_sections:
        assert mode_integration.should_include_section(section, ExecutionMode.AUTONOMOUS)
        assert mode_integration.should_include_section(section, ExecutionMode.SUPERVISED)
        assert mode_integration.should_include_section(section, ExecutionMode.HUMAN_IN_LOOP)


def test_should_include_section_optional_mode_dependent(mode_integration):
    """Test that optional sections depend on mode"""
    optional_sections = ["examples", "warnings", "notes", "see_also"]
    
    for section in optional_sections:
        # Not included in autonomous
        assert not mode_integration.should_include_section(section, ExecutionMode.AUTONOMOUS)
        
        # Included in supervised and human-in-loop
        assert mode_integration.should_include_section(section, ExecutionMode.SUPERVISED)
        assert mode_integration.should_include_section(section, ExecutionMode.HUMAN_IN_LOOP)


def test_should_include_section_verbose_only(mode_integration):
    """Test that verbose-only sections only appear in HUMAN_IN_LOOP"""
    verbose_sections = ["implementation_details", "performance_notes", "history"]
    
    for section in verbose_sections:
        # Not in autonomous or supervised
        assert not mode_integration.should_include_section(section, ExecutionMode.AUTONOMOUS)
        assert not mode_integration.should_include_section(section, ExecutionMode.SUPERVISED)
        
        # Only in human-in-loop
        assert mode_integration.should_include_section(section, ExecutionMode.HUMAN_IN_LOOP)


def test_should_include_section_unknown(mode_integration):
    """Test that unknown sections are included for supervised/human-in-loop"""
    unknown_section = "custom_unknown_section"
    
    # Not in autonomous
    assert not mode_integration.should_include_section(unknown_section, ExecutionMode.AUTONOMOUS)
    
    # In supervised and human-in-loop (cautious approach)
    assert mode_integration.should_include_section(unknown_section, ExecutionMode.SUPERVISED)
    assert mode_integration.should_include_section(unknown_section, ExecutionMode.HUMAN_IN_LOOP)


# ============================================================================
# Description Formatting Tests
# ============================================================================

def test_format_description_short_text(mode_integration):
    """Test formatting of short description (under limit)"""
    text = "This is a short description."
    
    # Should return unchanged for all modes
    assert mode_integration.format_description(text, ExecutionMode.AUTONOMOUS) == text
    assert mode_integration.format_description(text, ExecutionMode.SUPERVISED) == text
    assert mode_integration.format_description(text, ExecutionMode.HUMAN_IN_LOOP) == text


def test_format_description_long_text_autonomous(mode_integration):
    """Test formatting of long description in AUTONOMOUS mode"""
    text = "A" * 300  # Exceeds 200 char limit for autonomous
    
    formatted = mode_integration.format_description(text, ExecutionMode.AUTONOMOUS)
    
    # Should be truncated with ellipsis
    assert len(formatted) < len(text)
    assert formatted.endswith("...")
    assert len(formatted) <= 203  # 200 + "..."


def test_format_description_long_text_supervised(mode_integration):
    """Test formatting of long description in SUPERVISED mode"""
    text = "A" * 600  # Exceeds 500 char limit for supervised
    
    formatted = mode_integration.format_description(text, ExecutionMode.SUPERVISED)
    
    # Should be truncated with ellipsis
    assert len(formatted) < len(text)
    assert formatted.endswith("...")


def test_format_description_long_text_human_in_loop(mode_integration):
    """Test formatting of long description in HUMAN_IN_LOOP mode"""
    text = "A" * 900  # Under 1000 char limit
    
    formatted = mode_integration.format_description(text, ExecutionMode.HUMAN_IN_LOOP)
    
    # Should return unchanged (under limit)
    assert formatted == text


# ============================================================================
# Execution Summary Tests
# ============================================================================

def test_get_execution_summary(mode_integration):
    """Test execution summary generation"""
    summary = mode_integration.get_execution_summary(ExecutionMode.SUPERVISED)
    
    assert isinstance(summary, dict)
    assert summary["mode"] == "supervised"
    assert "description" in summary
    assert "risk_tolerance" in summary
    assert "speed_multiplier" in summary
    assert summary["formatting"] == "standard"
    assert "user_action_required" in summary


def test_get_execution_summary_human_in_loop(mode_integration):
    """Test execution summary for HUMAN_IN_LOOP mode"""
    summary = mode_integration.get_execution_summary(ExecutionMode.HUMAN_IN_LOOP)
    
    assert summary["user_action_required"] is True


def test_get_execution_summary_autonomous(mode_integration):
    """Test execution summary for AUTONOMOUS mode"""
    summary = mode_integration.get_execution_summary(ExecutionMode.AUTONOMOUS)
    
    assert summary["user_action_required"] is False


# ============================================================================
# User Statistics Tests
# ============================================================================

def test_update_user_stats_success(mode_integration):
    """Test user statistics update on success"""
    initial_count = mode_integration.user_profile.get_user().completed_operations
    initial_success = mode_integration.user_profile.get_user().successful_operations
    
    mode_integration.update_user_stats("test_operation", success=True)
    
    user = mode_integration.user_profile.get_user()
    assert user.completed_operations == initial_count + 1
    assert user.successful_operations == initial_success + 1


def test_update_user_stats_failure(mode_integration):
    """Test user statistics update on failure"""
    initial_count = mode_integration.user_profile.get_user().completed_operations
    initial_success = mode_integration.user_profile.get_user().successful_operations
    
    mode_integration.update_user_stats("test_operation", success=False)
    
    user = mode_integration.user_profile.get_user()
    assert user.completed_operations == initial_count + 1
    assert user.successful_operations == initial_success  # No change


def test_update_user_stats_success_rate(mode_integration):
    """Test success rate calculation after multiple operations"""
    # Perform 2 successes and 1 failure
    mode_integration.update_user_stats("op1", success=True)
    mode_integration.update_user_stats("op2", success=True)
    mode_integration.update_user_stats("op3", success=False)
    
    user = mode_integration.user_profile.get_user()
    assert user.completed_operations >= 3
    assert user.success_rate > 0.6  # At least 66% success rate


# ============================================================================
# Integration Tests
# ============================================================================

def test_integration_full_workflow(mode_integration):
    """Test full workflow: select mode -> get config -> format"""
    # 1. Select mode
    mode = mode_integration.select_mode_for_operation(
        operation_name="generate_comprehensive_docs",
        estimated_duration=300
    )
    
    # 2. Get formatting config
    config = mode_integration.get_formatting_config(mode)
    
    # 3. Check section inclusion
    should_include_examples = mode_integration.should_include_section("examples", mode)
    
    # 4. Format description
    long_text = "A" * 1500
    formatted = mode_integration.format_description(long_text, mode)
    
    # 5. Get summary
    summary = mode_integration.get_execution_summary(mode)
    
    # 6. Update stats
    mode_integration.update_user_stats("generate_comprehensive_docs", success=True)
    
    # Verify all steps worked
    assert isinstance(mode, ExecutionMode)
    assert isinstance(config, FormattingConfig)
    assert isinstance(should_include_examples, bool)
    assert len(formatted) < len(long_text)
    assert isinstance(summary, dict)


# ============================================================================
# Edge Cases and Error Handling
# ============================================================================

def test_initialization_with_none_logger():
    """Test initialization with no logger"""
    integration = ExecutionModeIntegration(logger=None, config={})
    
    assert integration.logger is not None  # Should create default logger


def test_initialization_with_none_config():
    """Test initialization with no config"""
    integration = ExecutionModeIntegration(config=None, user_id="test")
    
    assert integration.config == {}


def test_initialization_with_none_user_id():
    """Test initialization with no user_id"""
    integration = ExecutionModeIntegration()
    
    assert integration.user_id == "default_user"


# ============================================================================
# Run Tests
# ============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
