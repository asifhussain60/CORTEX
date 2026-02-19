"""
CORTEX Validation Module
Data integrity and cross-reference validation
"""
from cortex.validation.cross_reference_validator import (
    CrossReferenceValidator,
    ContradictionReport,
    ContradictionType,
    ContradictionSeverity,
)

from cortex.validation.contradiction_resolver import (
    ContradictionResolver,
    Resolution,
    ResolutionStrategy,
    ResolutionStatus,
)

__all__ = [
    'CrossReferenceValidator',
    'ContradictionReport',
    'ContradictionType',
    'ContradictionSeverity',
    'ContradictionResolver',
    'Resolution',
    'ResolutionStrategy',
    'ResolutionStatus',
]
