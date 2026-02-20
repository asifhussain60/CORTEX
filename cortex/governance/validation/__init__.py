"""
CORTEX Validation Module
Data integrity and cross-reference validation
"""
from cortex.governance.validation.cross_reference_validator import (
    CrossReferenceValidator,
    ContradictionReport,
    ContradictionType,
    ContradictionSeverity,
)

from cortex.governance.validation.contradiction_resolver import (
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
