"""COMPAT shim — cortex.core.audit_required_validator → cortex.core.core.audit_required_validator.

Phase 58: Canonical implementation lives in cortex/core/core/audit_required_validator.py.
This stub is kept for import-path compatibility.
"""
# noqa: F401
from cortex.core.core.audit_required_validator import AuditOperationType, AuditValidationResult, ACCompletionStatus, AuditOperationsTracker, ACCompletionAuditValidator, AuditRequiredValidator

__all__ = ["AuditOperationType", "AuditValidationResult", "ACCompletionStatus", "AuditOperationsTracker", "ACCompletionAuditValidator", "AuditRequiredValidator"]
