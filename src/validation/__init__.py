"""
Validation Package - Integration Depth Scoring & Validation

Validates CORTEX feature integration depth:
- Integration scorer (0-100% scoring algorithm)
- Wiring validator (entry point mapping)
- Test coverage validator (pytest integration)
- Import validator (safe import testing)
- Instantiation validator (class instantiation testing)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from src.validation.integration_scorer import IntegrationScorer
from src.validation.wiring_validator import WiringValidator
from src.validation.test_coverage_validator import TestCoverageValidator

__all__ = [
    "IntegrationScorer",
    "WiringValidator",
    "TestCoverageValidator",
]
