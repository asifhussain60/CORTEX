"""COMPAT shim — cortex.core.resumption_handler → cortex.core.core.resumption_handler.

Phase 58: Canonical implementation lives in cortex/core/core/resumption_handler.py.
This stub is kept for import-path compatibility.
"""
# noqa: F401
from cortex.core.core.resumption_handler import RecoveryStrategy, ResumptionStatus, ResumptionRecord, RecoveryContext, ResumptionHandler

__all__ = ["RecoveryStrategy", "ResumptionStatus", "ResumptionRecord", "RecoveryContext", "ResumptionHandler"]
