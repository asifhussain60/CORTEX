"""
Test configuration and fixtures for CORTEX 4.0 orchestration tests
"""

import pytest
import logging


@pytest.fixture
def logger():
    """Provide a test logger"""
    return logging.getLogger("cortex.test")


@pytest.fixture
def simple_config():
    """Simple orchestrator configuration"""
    return {
        "max_retries": 3,
        "timeout": 30
    }


@pytest.fixture
def complex_config():
    """Complex orchestrator configuration with all options"""
    return {
        "max_retries": 5,
        "timeout": 60,
        "enable_validation": True,
        "enable_rollback": True,
        "log_level": "DEBUG"
    }
