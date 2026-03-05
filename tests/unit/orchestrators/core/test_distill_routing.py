"""
Sub-phase 129-d RED tests — DISTILL routing wiring.

Verifies that:
1. CortexDistill is registered in mcp_registry PRODUCTION_TOOLS
2. CortexDistill is in ALL_TOOLS
3. IntentType.DISTILL is wired in the intent classifier keyword dict
4. keyword_registry.DISTILL_KEYWORDS is defined
5. The classifier can route 'distill' → IntentType.DISTILL

TDD contract (CORE-008): tests MUST fail before wiring is complete.
"""
from __future__ import annotations

import pytest


class TestDistillMcpRegistration:
    """cortex_distill must appear in PRODUCTION_TOOLS."""

    def test_cortex_distill_in_production_tools(self):
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS
        assert "cortex_distill" in PRODUCTION_TOOLS, (
            "cortex_distill missing from PRODUCTION_TOOLS — add to mcp_registry.py"
        )

    def test_cortex_distill_has_conversation_parameter(self):
        from cortex.mcp.mcp_registry import PRODUCTION_TOOLS
        spec = PRODUCTION_TOOLS.get("cortex_distill", {})
        param_names = [p["name"] for p in spec.get("parameters", [])]
        assert "conversation" in param_names


class TestDistillAllToolsRegistration:
    """CortexDistill must be in ALL_TOOLS."""

    def test_cortex_distill_class_in_all_tools(self):
        from cortex.mcp.tools import ALL_TOOLS
        from cortex.mcp.tools.cortex_distill_tool import CortexDistill
        tool_classes = [type(t) if not isinstance(t, type) else t for t in ALL_TOOLS]
        assert CortexDistill in tool_classes, (
            "CortexDistill missing from ALL_TOOLS in cortex/mcp/tools/__init__.py"
        )


class TestDistillKeywordRegistry:
    """keyword_registry must have DISTILL_KEYWORDS defined."""

    def test_distill_keywords_defined(self):
        from cortex.orchestrators.core.intent_router.keyword_registry import IntentKeywordRegistry
        assert hasattr(IntentKeywordRegistry, "DISTILL_KEYWORDS"), (
            "DISTILL_KEYWORDS not defined in IntentKeywordRegistry"
        )

    def test_distill_keywords_is_list(self):
        from cortex.orchestrators.core.intent_router.keyword_registry import IntentKeywordRegistry
        assert isinstance(IntentKeywordRegistry.DISTILL_KEYWORDS, list)

    def test_distill_keywords_contains_distill(self):
        from cortex.orchestrators.core.intent_router.keyword_registry import IntentKeywordRegistry
        assert "distill" in IntentKeywordRegistry.DISTILL_KEYWORDS

    def test_distill_in_operation_type_mappings(self):
        from cortex.orchestrators.core.intent_router_impl import IntentRouter
        from cortex.models.canonical_enums import IntentType
        router = IntentRouter()
        assert IntentType.DISTILL in router.operation_type_mappings


class TestDistillClassifierRouting:
    """IntentClassifier must route 'distill' keywords to DISTILL."""

    def test_classifier_keyword_map_has_distill(self):
        from cortex.orchestrators.core.intent_classifier import _KEYWORD_BAGS
        from cortex.models.canonical_enums import IntentType
        assert IntentType.DISTILL in _KEYWORD_BAGS, (
            "IntentType.DISTILL missing from _KEYWORD_BAGS in intent_classifier.py"
        )

    def test_classifier_exact_match_distill(self):
        from cortex.orchestrators.core.intent_classifier import IntentClassifier
        from cortex.models.canonical_enums import IntentType
        clf = IntentClassifier()
        result = clf._exact_operation_match("distill")
        assert result == IntentType.DISTILL, (
            f"_exact_operation_match('distill') returned {result!r}, expected IntentType.DISTILL"
        )
