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
    import logging as _logging; _logging.getLogger(__name__).warning("Optional cortex dependency unavailable: cortex.governance.filename_factory — feature degraded")

try:
    from cortex.governance.golden_hammer_rules import (
        GoldenHammerRules,
        GoldenHammerViolation,
    )
except ImportError:
    import logging as _logging; _logging.getLogger(__name__).warning("Optional cortex dependency unavailable: cortex.governance.golden_hammer_rules — feature degraded")

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
