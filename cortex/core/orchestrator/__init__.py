"""COMPAT shim — cortex.core.orchestrator moved to cortex.orchestrators.core (Phase 60).

Phase 114-b: Wildcard re-exports moved under lazy __getattr__ to break L1→L3 DAG violation.
"""
from __future__ import annotations


def __getattr__(name: str) -> object:
    """Lazy re-export: resolves the import only when the symbol is actually accessed."""
    import importlib
    _modules = [
        "cortex.orchestrators.core.approval_gate",
        "cortex.orchestrators.core.challenge_integration",
        "cortex.orchestrators.core.context_aggregator",
        "cortex.orchestrators.core.continuation_decision",
        "cortex.orchestrators.core.conversation_metrics",
        "cortex.orchestrators.core.conversation_protocol",
        "cortex.orchestrators.core.conversation_state",
        "cortex.orchestrators.core.holistic_context_builder",
        "cortex.orchestrators.core.pattern_enforcer",
        "cortex.orchestrators.core.phase_events",
        "cortex.orchestrators.core.stage_2_5_gate",
        "cortex.orchestrators.core.terminal_events",
        "cortex.orchestrators.core.turn_response_generator",
        "cortex.orchestrators.core.turn_response_with_challenges",
        "cortex.orchestrators.core.turn_timeout",
    ]
    for mod_name in _modules:
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, name):
                return getattr(mod, name)
        except ImportError:
            pass
    raise AttributeError(f"module 'cortex.core.orchestrator' has no attribute {name!r}")
