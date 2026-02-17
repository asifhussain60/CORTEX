"""
CORTEX Governance Module

Provides governance enforcement, validation, and policy tools:
- FilenameFactory: Generate CORE-028 compliant filenames
- FilenameValidator: Validate CORE-028 filename rules
- FilePathEnforcer: Validate CORE-038 file placement policy
- GoldenHammerRules: Prevent workflow template anti-patterns (WORKFLOW-COMPLEXITY-GATE-001)
- GoldenHammerViolation: Exception for golden hammer violations
"""

try:
    from cortex.governance.filename_factory import (
        FilenameFactory,
        FilenameValidator,
        FilePathEnforcer,
        GenerationResult,
        NamingViolation,
        PathValidationResult,
        PlacementViolation,
        ValidationResult,
    )
except ImportError:
    # Graceful fallback if module not yet fully initialized
    pass

try:
    from cortex.governance.golden_hammer_rules import (
        GoldenHammerRules,
        GoldenHammerViolation,
    )
except ImportError:
    # Graceful fallback if golden hammer rules not available
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
    "GoldenHammerRules",
    "GoldenHammerViolation",
]
