"""
Tests for LintValidationOrchestrator

Minimal test coverage for system alignment validation.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from src.orchestrators.lint_validation_orchestrator import LintValidationOrchestrator, ViolationSeverity


@pytest.fixture
def orchestrator():
    """Create orchestrator instance."""
    return LintValidationOrchestrator()


def test_initialization(orchestrator):
    """Test orchestrator can be instantiated."""
    assert orchestrator is not None
    assert orchestrator.config is not None


def test_config_loaded(orchestrator):
    """Test configuration is loaded."""
    assert isinstance(orchestrator.config, dict)
    assert "dotnet" in orchestrator.config or "python" in orchestrator.config


def test_should_block_phase_no_violations(orchestrator):
    """Test phase blocking with no violations."""
    results = {
        "total_violations": 0,
        "critical": 0,
        "warnings": 0,
        "info": 0,
        "passed": True
    }
    should_block = orchestrator.should_block_phase(results)
    assert should_block is False


def test_should_block_phase_with_critical(orchestrator):
    """Test phase blocking with critical violations."""
    results = {
        "total_violations": 5,
        "critical": 2,
        "warnings": 3,
        "info": 0,
        "passed": False
    }
    should_block = orchestrator.should_block_phase(results)
    assert should_block is True
