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

__all__ = [
    'CrossReferenceValidator',
    'ContradictionReport',
    'ContradictionType',
    'ContradictionSeverity',
]
