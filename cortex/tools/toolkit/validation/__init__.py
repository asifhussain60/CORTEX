"""
Governance Validator Module.

Consolidates governance validation from validate-production.py
and validate_governance_alignment.py scripts.

Author: CORTEX Framework
Phase: 90 (Toolkit Centralization)
"""

from .governance_validator import (
    GovernanceValidator,
    ValidationCheck,
    Severity,
    ProductionReadinessReport
)

# Import consolidated validation from Phase 90
try:
    from pathlib import Path

    # Import from sibling validation.py file
    validation_file = Path(__file__).parent.parent / "validation.py"
    if validation_file.exists():
        import importlib.util
        spec = importlib.util.spec_from_file_location("toolkit_validation", validation_file)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            ValidationManager = module.ValidationManager
            ValidationResult = module.ValidationResult
            ValidationLevel = module.ValidationLevel
    else:
        ValidationManager = None
        ValidationResult = None
        ValidationLevel = None
except Exception:
    ValidationManager = None
    ValidationResult = None
    ValidationLevel = None

__all__ = [
    "GovernanceValidator",
    "ValidationCheck",
    "Severity",
    "ProductionReadinessReport",
    "ValidationManager",
    "ValidationResult",
    "ValidationLevel",
]
