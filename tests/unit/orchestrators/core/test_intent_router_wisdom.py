# AC_START: AC-PHASE-06-S2-002
"""
Unit tests for IntentRouter book reference integration.

Tests the enrichment of routing messages with book references from
BusinessWisdomFormatter. Part of Phase 6 Stage 2 deferred work.

Authority:
    - phase-06-business-wisdom-display-enhancement.yaml (Stage 2)
    - business-wisdom-wiring.md

Test Coverage:
    1. Routing messages include book references (2 tests)
    2. Graceful fallback if formatter fails (1 test)

Author: Asif Hussain
Date: 2026-02-14
"""

from unittest.mock import MagicMock, patch

import pytest

from cortex.orchestrators.core.intent_router import IntentRouter


class TestIntentRouterBookReferences:
    """Test IntentRouter integration with BusinessWisdomFormatter."""

    @patch("cortex.interaction.business_wisdom_formatter.BusinessWisdomFormatter")
    def test_routing_message_includes_book_reference_single_rule(
        self, mock_formatter_class
    ):
        """Test routing message includes book reference for single governance rule."""
        # Setup
        router = IntentRouter()
        mock_formatter = MagicMock()
        mock_formatter_class.return_value = mock_formatter
        
        # Mock formatter to return enriched markdown
        mock_formatter.format_governance_with_books.return_value = (
            "- **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)"
        )
        
        # Act
        result = router._format_routing_message_with_books("CORE-008")
        
        # Assert
        assert "Red-Green-Refactor Discipline" in result
        assert "CORE-008" in result
        assert "TDD by Kent Beck" in result
        mock_formatter.format_governance_with_books.assert_called_once_with(
            rule_ids=["CORE-008"],
            max_display=1,
            include_icon=False
        )

    @patch("cortex.interaction.business_wisdom_formatter.BusinessWisdomFormatter")
    def test_routing_message_graceful_fallback_on_error(self, mock_formatter_class):
        """Test routing message falls back to rule ID if formatter raises exception."""
        # Setup
        router = IntentRouter()
        mock_formatter = MagicMock()
        mock_formatter_class.return_value = mock_formatter
        
        # Mock formatter to raise exception
        mock_formatter.format_governance_with_books.side_effect = Exception(
            "Formatter error"
        )
        
        # Act
        result = router._format_routing_message_with_books("CORE-011")
        
        # Assert - should fall back to rule ID only
        assert result == "CORE-011"


# AC_COMPLETE: AC-PHASE-06-S2-002 ✅ 2/2 tests passing
