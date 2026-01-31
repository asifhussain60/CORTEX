"""
Conftest for support orchestrator tests
"""

import pytest

# Disable pytest-asyncio for these tests
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest"""
    config.option.asyncio_mode = "auto"
