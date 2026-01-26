"""
CORTEX Governance Module

Provides governance enforcement, validation, and policy tools:
- FilenameFactory: Generate CORE-028 compliant filenames
- FilenameValidator: Validate CORE-028 filename rules
- FilePathEnforcer: Validate CORE-038 file placement policy
"""

try:
    from cortex.governance.filename_factory import (
        FilenameFactory,
        FilenameValidator,
        FilePathEnforcer,
        NamingViolation,
        PlacementViolation,
        ValidationResult,
        GenerationResult,
        PathValidationResult,
    )
except ImportError:
    # Graceful fallback if module not yet fully initialized
    pass

__all__ = [
    "FilenameFactory",
    "FilenameValidator",
    "FilePathEnforcer",
    "NamingViolation",
    "PlacementViolation",
    "ValidationResult",
    "GenerationResult",
    "PathValidationResult",
]
