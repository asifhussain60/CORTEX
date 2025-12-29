"""
Smoke Test Configuration

Shared fixtures for smoke tests with minimal overhead.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
import tempfile


@pytest.fixture
def temp_project_root():
    """Lightweight temporary directory fixture."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def mock_brain_rules():
    """Mock SKULL rules for testing without file I/O."""
    return {
        'TDD_ENFORCEMENT': {
            'description': 'RED→GREEN→REFACTOR mandatory',
            'severity': 'critical'
        },
        'RED_PHASE_VALIDATION': {
            'description': 'Tests must fail before implementation',
            'severity': 'critical'
        },
        'HOLISTIC_CODE_DISCOVERY_ENFORCEMENT': {
            'description': 'Search before create',
            'severity': 'high'
        },
        'REFACTOR_CODE_CLEANUP_ENFORCEMENT': {
            'description': 'Remove orphaned/duplicate code',
            'severity': 'high'
        },
        'GIT_ISOLATION_ENFORCEMENT': {
            'description': 'CORTEX code never in user repos',
            'severity': 'critical'
        },
        'TEST_LOCATION_SEPARATION': {
            'description': 'App tests in user repo, CORTEX in tests/',
            'severity': 'high'
        }
    }
