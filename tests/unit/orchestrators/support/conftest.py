"""
Conftest for support orchestrator tests
"""

import pytest


def pytest_configure(config):
    """Configure pytest - asyncio mode inherited from root conftest"""
    config.option.asyncio_mode = "auto"
