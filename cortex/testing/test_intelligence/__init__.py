"""
Test Intelligence Foundation - Package initialization.

Provides unified access to test intelligence layers:
- Layer 1: Test Demand Generator
- Layer 2: Test Composer
- Layer 3: Quality Validator

Authority: WAVE-1 Stage 3, cortex-architect.prompt.md v15.3
Phase: THEME-A Intelligence Foundation
"""

from cortex.testing.test_intelligence.demand_generator import (
    TestDemand,
    TestDemandGenerator,
)
from cortex.testing.test_intelligence.test_composer import (
    ComposedTest,
    TestComposer,
)
from cortex.testing.test_intelligence.quality_validator import (
    QualityScore,
    QualityValidator,
)

__all__ = [
    "TestDemand",
    "TestDemandGenerator",
    "ComposedTest",
    "TestComposer",
    "QualityScore",
    "QualityValidator",
]
