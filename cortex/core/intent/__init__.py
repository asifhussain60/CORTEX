"""COMPAT shim — cortex.core.intent moved to cortex.orchestrators.core.intent_router (Phase 60).

Phase 114-b: Wildcard re-exports moved under lazy __getattr__ to break L1→L3 DAG violation.
"""
from __future__ import annotations


def __getattr__(name: str) -> object:
    """Lazy re-export: resolves the import only when the symbol is actually accessed."""
    import importlib
    _modules = [
        "cortex.orchestrators.core.intent_router.challenge_generator",
        "cortex.orchestrators.core.intent_router.comprehension_loop",
        "cortex.orchestrators.core.intent_router.comprehension_yaml",
        "cortex.orchestrators.core.intent_router.intent_canonicalizer",
        "cortex.orchestrators.core.intent_router.intent_reflection_protocol",
        "cortex.orchestrators.core.intent_router.lens_context_builder",
        "cortex.orchestrators.core.intent_router.lens_response_formatter",
        "cortex.orchestrators.core.intent_router.recommendation_engine",
    ]
    for mod_name in _modules:
        try:
            mod = importlib.import_module(mod_name)
            if hasattr(mod, name):
                return getattr(mod, name)
        except ImportError:
            pass
    raise AttributeError(f"module 'cortex.core.intent' has no attribute {name!r}")
