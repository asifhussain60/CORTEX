"""
GAP-005 RED: IntentRouter must route all 10 CORTEX execution modes.
Missing: AUDIT, DESIGN, DIGEST, REPHRASE, INVESTIGATE.

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest


class TestIntentTypeHasAllModes:
    """GAP-005: IntentType enum must contain all 10 CORTEX execution modes."""

    def test_intent_type_has_audit(self) -> None:
        """IntentType must have AUDIT value."""
        from cortex.models.canonical_enums import IntentType
        assert hasattr(IntentType, "AUDIT"), "IntentType missing AUDIT mode"

    def test_intent_type_has_design(self) -> None:
        """IntentType must have DESIGN value."""
        from cortex.models.canonical_enums import IntentType
        assert hasattr(IntentType, "DESIGN"), "IntentType missing DESIGN mode"

    def test_intent_type_has_digest(self) -> None:
        """IntentType must have DIGEST value."""
        from cortex.models.canonical_enums import IntentType
        assert hasattr(IntentType, "DIGEST"), "IntentType missing DIGEST mode"

    def test_intent_type_has_rephrase(self) -> None:
        """IntentType must have REPHRASE value."""
        from cortex.models.canonical_enums import IntentType
        assert hasattr(IntentType, "REPHRASE"), "IntentType missing REPHRASE mode"

    def test_intent_type_has_investigate(self) -> None:
        """IntentType must have INVESTIGATE value."""
        from cortex.models.canonical_enums import IntentType
        assert hasattr(IntentType, "INVESTIGATE"), "IntentType missing INVESTIGATE mode"


class TestIntentRouterRoutesAllModes:
    """GAP-005: EnhancedIntentRouter must detect all CORTEX modes via _detect_intent_from_dict()."""

    def test_router_routes_audit_keywords(self) -> None:
        """EnhancedIntentRouter must classify 'audit the repo' as AUDIT intent."""
        from cortex.orchestrators.core.intent_router import IntentRouter

        router = IntentRouter()
        intent = router._detect_intent_from_dict({"description": "audit the repository for issues"})
        assert intent.value.upper() == "AUDIT", (
            f"'audit' keyword should route to AUDIT, got {intent}"
        )

    def test_router_routes_design_keywords(self) -> None:
        """EnhancedIntentRouter must classify 'design the architecture' as DESIGN intent."""
        from cortex.orchestrators.core.intent_router import IntentRouter

        router = IntentRouter()
        intent = router._detect_intent_from_dict({"description": "design the architecture for the new module"})
        assert intent.value.upper() == "DESIGN", (
            f"'design' keyword should route to DESIGN, got {intent}"
        )

    def test_router_routes_digest_keywords(self) -> None:
        """EnhancedIntentRouter must classify 'digest what happened' as DIGEST intent."""
        from cortex.orchestrators.core.intent_router import IntentRouter

        router = IntentRouter()
        intent = router._detect_intent_from_dict({"description": "digest what happened in this session"})
        assert intent.value.upper() == "DIGEST", (
            f"'digest' keyword should route to DIGEST, got {intent}"
        )

    def test_router_routes_rephrase_keywords(self) -> None:
        """EnhancedIntentRouter must classify 'rephrase this request' as REPHRASE intent."""
        from cortex.orchestrators.core.intent_router import IntentRouter

        router = IntentRouter()
        intent = router._detect_intent_from_dict({"description": "rephrase this request more efficiently"})
        assert intent.value.upper() == "REPHRASE", (
            f"'rephrase' keyword should route to REPHRASE, got {intent}"
        )

    def test_router_routes_investigate_keywords(self) -> None:
        """EnhancedIntentRouter must classify 'investigate' keyword as INVESTIGATE intent."""
        from cortex.orchestrators.core.intent_router import IntentRouter

        router = IntentRouter()
        intent = router._detect_intent_from_dict({"description": "investigate the unexpected failure in detail"})
        assert intent.value.upper() == "INVESTIGATE", (
            f"'investigate' keyword should route to INVESTIGATE, got {intent}"
        )

    def test_router_keyword_mapping_includes_all_modes(self) -> None:
        """canonical IntentType enum must contain all 5 new modes."""
        from cortex.models.canonical_enums import IntentType

        required = {"AUDIT", "DESIGN", "DIGEST", "REPHRASE", "INVESTIGATE"}
        existing = {m.name for m in IntentType}
        missing = required - existing
        assert not missing, f"canonical IntentType missing modes: {missing}"
