"""
Track B Validation Framework

Comprehensive testing and validation system for CORTEX 3.0 Track B components.
Provides macOS-specific testing infrastructure, component validators, and integration testing.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

from .test_framework import MacOSTestFramework
from .component_validator import ComponentValidator
from .integration_tester import IntegrationTester
from .merge_validator import MergeValidator

__all__ = [
    'MacOSTestFramework',
    'ComponentValidator', 
    'IntegrationTester',
    'MergeValidator'
]

__version__ = "3.0.0"
__author__ = "Asif Hussain"