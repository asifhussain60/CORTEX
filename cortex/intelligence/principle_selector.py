"""Compat shim: PrincipleSelector moved to analysis sub-package (Phase 117)."""
# ruff: noqa: F401
import cortex.intelligence.analysis.principle_selector as _ps_analysis  # noqa: F401

# Explicit re-exports for static analysis / direct imports
from cortex.intelligence.analysis.principle_selector import (  # noqa: F401
    PrincipleSelector,
    _VALID_POOLS,
    _load_principles_yaml,
    is_complex_request,
    _load_atom_quote_yaml,
)

# NOTE: _principles_cache, _ring_buffer, _quotes_cache are NOT imported here.
# They are mutable module-level singletons in the analysis module. Importing them
# would create frozen local bindings. Instead, __getattr__ below delegates to the
# live analysis module, so tests that mutate ps_mod._principles_cache etc. affect
# the canonical module-level state.


def __getattr__(name):  # noqa: N807 — module-level __getattr__ for transparent delegation
    """Delegate any missing attribute to the canonical analysis module."""
    return getattr(_ps_analysis, name)
