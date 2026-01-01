"""
Validation Package - Integration Depth Scoring & Validation

Validates CORTEX feature integration depth:
- Integration scorer (0-100% scoring algorithm)
- Wiring validator (entry point mapping)
- Glassmorphism validator (design standard enforcement)
- Import validator (safe import testing)
- Instantiation validator (class instantiation testing)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from src.validation.integration_scorer import IntegrationScorer
from src.validation.wiring_validator import WiringValidator

# Optional imports (may not be present in all environments)
try:
    from src.validation.glassmorphism_validator import GlassmorphismValidator
    _HAS_GLASSMORPHISM = True
except ImportError:
    _HAS_GLASSMORPHISM = False

try:
    from src.validation.glassmorphism_remediation import GlassmorphismRemediator
    _HAS_REMEDIATION = True
except ImportError:
    _HAS_REMEDIATION = False

__all__ = [
    "IntegrationScorer",
    "WiringValidator",
]

if _HAS_GLASSMORPHISM:
    __all__.append("GlassmorphismValidator")

if _HAS_REMEDIATION:
    __all__.append("GlassmorphismRemediator")

