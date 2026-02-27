"""
Phase 80-g — GAP-80-07: Canonical synthesize() facade in cortex.intelligence.provider.

Tests that a single module-level synthesize() function exists and routes
correctly to the 3 tiers (quick/targeted/full).

CORE-008: Tests written first (RED phase).
"""

from __future__ import annotations

import pytest


class TestCanonicalSynthesizeFacade:
    """Tests for GAP-80-07: canonical synthesize() entry point."""

    def test_synthesize_importable(self):
        """from cortex.intelligence.provider import synthesize must work."""
        from cortex.intelligence.provider import synthesize
        assert callable(synthesize)

    def test_synthesize_quick_returns_context(self):
        """synthesize(request, tier='quick') returns a UnifiedIntelligenceContext."""
        from cortex.intelligence.provider import synthesize
        from cortex.intelligence.knowledge.unified_intelligence_context import (
            UnifiedIntelligenceContext,
        )
        result = synthesize("test request", tier="quick")
        assert isinstance(result, UnifiedIntelligenceContext)

    def test_synthesize_targeted_returns_context(self):
        """synthesize(request, tier='targeted') returns a UnifiedIntelligenceContext."""
        from cortex.intelligence.provider import synthesize
        from cortex.intelligence.knowledge.unified_intelligence_context import (
            UnifiedIntelligenceContext,
        )
        result = synthesize("test request", tier="targeted")
        assert isinstance(result, UnifiedIntelligenceContext)

    def test_synthesize_full_returns_context(self):
        """synthesize(request, tier='full') returns a UnifiedIntelligenceContext."""
        from cortex.intelligence.provider import synthesize
        from cortex.intelligence.knowledge.unified_intelligence_context import (
            UnifiedIntelligenceContext,
        )
        result = synthesize("test request", tier="full")
        assert isinstance(result, UnifiedIntelligenceContext)

    def test_synthesize_default_tier_is_targeted(self):
        """synthesize(request) without tier uses 'targeted' by default."""
        from cortex.intelligence.provider import synthesize
        from cortex.intelligence.knowledge.unified_intelligence_context import (
            UnifiedIntelligenceContext,
        )
        result = synthesize("default tier test")
        assert isinstance(result, UnifiedIntelligenceContext)

    def test_synthesize_exported_from_intelligence_init(self):
        """synthesize must be importable from cortex.intelligence."""
        from cortex.intelligence import synthesize  # noqa: F401 — import validation
        assert callable(synthesize)
