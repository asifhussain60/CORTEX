#!/usr/bin/env python3
"""
pytest configuration for Level 1 view testing

Author: Asif Hussain
Copyright: © 2026 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path


def pytest_configure(config):
    """Configure pytest markers"""
    config.addinivalue_line(
        "markers", "critical: Critical tests that must pass"
    )
    config.addinivalue_line(
        "markers", "theme: Theme consistency tests"
    )
    config.addinivalue_line(
        "markers", "content: Content quality tests"
    )
