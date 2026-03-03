"""COMPAT shim — cortex.core.interaction moved to cortex.orchestrators.core (Phase 60).

Phase 114-b: Wildcard re-exports moved under lazy access to break L1→L3 DAG violation.
No callers outside tests use this package directly — compat maintained for safety.
"""
from __future__ import annotations


def __getattr__(name: str) -> object:
    """Lazy re-export: only resolves the import when the symbol is actually accessed."""
    import importlib
    _modules = [
        "cortex.orchestrators.core.autonomous_plan_executor",
        "cortex.orchestrators.core.bluf_system",
        "cortex.orchestrators.core.business_wisdom_formatter",
        "cortex.orchestrators.core.command_handlers",
        "cortex.orchestrators.core.context_cache_layer",
        "cortex.orchestrators.core.context_metrics_collector",
        "cortex.orchestrators.core.context_synthesis_gateway",
        "cortex.orchestrators.core.conversational_reflector",
        "cortex.orchestrators.core.persona_command_handlers",
        "cortex.orchestrators.core.persona_store",
        "cortex.orchestrators.core.request_transformer",
        "cortex.orchestrators.core.tooling_suggestions",
    ]
    for mod_name in _modules:
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, name):
                return getattr(mod, name)
        except ImportError:
            pass
    raise AttributeError(f"module 'cortex.core.interaction' has no attribute {name!r}")
