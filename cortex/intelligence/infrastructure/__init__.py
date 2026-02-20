"""Infrastructure intelligence package for CORTEX.

Provides InfrastructureDetector for automated infrastructure detection
during repository onboarding, and topology generation utilities.
"""

from cortex.intelligence.infrastructure.detector import InfrastructureDetector

__all__ = ["InfrastructureDetector"]
