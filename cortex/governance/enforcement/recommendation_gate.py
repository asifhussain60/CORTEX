"""COMPAT shim — cortex.governance.enforcement.recommendation_gate → cortex.orchestrators.core.recommendation_gate.

Phase 58-B: zero-import duplicate. Canonical implementation at cortex/orchestrators/core/recommendation_gate.py.
"""
# noqa: F401
from cortex.orchestrators.core.recommendation_gate import GateStatus, GateVerdict, GateResult, GateEvaluation, RecommendationGate

__all__ = ["GateStatus", "GateVerdict", "GateResult", "GateEvaluation", "RecommendationGate"]
