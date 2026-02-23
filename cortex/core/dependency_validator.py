"""COMPAT shim — cortex.core.dependency_validator → cortex.core.core.dependency_validator.

Phase 58: Canonical implementation lives in cortex/core/core/dependency_validator.py.
This stub is kept for import-path compatibility.
"""
# noqa: F401
from cortex.core.core.dependency_validator import DependencyValidationResult, DependencyPath, DependencyValidationStatus, PhaseDependencyAnalyzer, DependencyModificationValidator, HolisticDependencyValidator

__all__ = ["DependencyValidationResult", "DependencyPath", "DependencyValidationStatus", "PhaseDependencyAnalyzer", "DependencyModificationValidator", "HolisticDependencyValidator"]
