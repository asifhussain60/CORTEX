"""
AC-PERMANENT-FIX-010: Execution Specification Framework

Provides YAML-based specification registry for spec-driven execution,
enforcing CORE-040 (Execution Specification Mandate).

Modules:
    spec_models: Data classes for specification structures
    spec_registry: Registry to load and cache specifications
    spec_validator: Validation layer for specification compliance

CORE Rules Applied:
    - CORE-008: TDD (tests before implementation)
    - CORE-011: Type hints mandatory
    - CORE-012: Google-style docstrings
    - CORE-040: Execution Specification Mandate
"""

__version__ = "1.0.0"
__all__ = [
    "SpecRegistry",
    "SpecValidator",
    "SpecModels",
]
