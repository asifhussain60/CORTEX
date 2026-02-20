# AC_START: AC-PHASE-06-S2-003
"""
Unit tests for DoR Display book reference integration.

Tests the integration pattern for enriching DoR (Definition of Ready) displays
with book references from BusinessWisdomFormatter. This validates the integration
contract even though full DoR system wiring is pending.

Authority:
    - phase-06-business-wisdom-display-enhancement.yaml (Stage 2)
    - business-wisdom-wiring.md

Test Coverage:
    1. DoR display integration pattern (1 test)
    2. Business wisdom section rendering (1 test)

Author: Asif Hussain
Date: 2026-02-14
"""

from unittest.mock import MagicMock, patch

import pytest

from cortex.core.interaction.business_wisdom_formatter import BusinessWisdomFormatter


class TestDoRWisdomIntegration:
    """Test DoR display integration with BusinessWisdomFormatter."""

    @patch("cortex.core.interaction.business_wisdom_formatter.GovernanceRuleLoader")
    def test_dor_display_integration_pattern(self, mock_loader_class):
        """Test integration pattern for adding Business Wisdom to DoR displays."""
        # Setup - Mock loader to avoid YAML parsing issues
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        
        # Mock get_rule_by_id to return test data
        def mock_get_rule(rule_id):
            rules_data = {
                "CORE-008": {
                    "rule_id": "CORE-008",
                    "principle": "Red-Green-Refactor Discipline",
                    "book_reference": "TDD by Kent Beck",
                    "severity": "blocked"
                },
                "CORE-011": {
                    "rule_id": "CORE-011",
                    "principle": "Type Hints Mandatory",
                    "book_reference": "Clean Code by Robert Martin",
                    "severity": "blocked"
                },
                "CORE-012": {
                    "rule_id": "CORE-012",
                    "principle": "Google Docstrings",
                    "book_reference": "Pragmatic Programmer by Hunt & Thomas",
                    "severity": "warning"
                }
            }
            return rules_data.get(rule_id)
        
        mock_loader.get_rule_by_id.side_effect = mock_get_rule
        
        formatter = BusinessWisdomFormatter(loader=mock_loader)
        
        # Mock governance rules that would come from DoR
        governance_rules = ["CORE-008", "CORE-011", "CORE-012"]
        
        # Act - Format business wisdom section
        wisdom_markdown = formatter.format_governance_with_books(
            rule_ids=governance_rules,
            max_display=5,
            include_icon=True
        )
        
        # Assert - Verify section structure
        assert "### 📚 Business Wisdom" in wisdom_markdown
        assert "CORE-008" in wisdom_markdown
        assert "→" in wisdom_markdown  # Arrow notation
        assert "TDD by Kent Beck" in wisdom_markdown
        
        # Verify max 5 principles (should only show what's available)
        lines = [line for line in wisdom_markdown.split("\n") if line.startswith("- ")]
        assert len(lines) <= 5, "Should enforce max 5 principles"
        assert len(lines) == 3, "Should show all 3 provided rules"

    @patch("cortex.core.interaction.business_wisdom_formatter.GovernanceRuleLoader")
    def test_dor_business_wisdom_section_rendering(self, mock_loader_class):
        """Test Business Wisdom section renders correctly in DoR-like context."""
        # Setup - Mock loader
        mock_loader = MagicMock()
        mock_loader_class.return_value = mock_loader
        
        # Mock get_rule_by_id for DoR context
        def mock_get_rule(rule_id):
            rules_data = {
                "CORE-008": {
                    "rule_id": "CORE-008",
                    "principle": "Red-Green-Refactor Discipline",
                    "book_reference": "TDD by Kent Beck",
                    "severity": "blocked"
                },
                "CORE-011": {
                    "rule_id": "CORE-011",
                    "principle": "Type Hints Mandatory",
                    "book_reference": "Clean Code by Robert Martin",
                    "severity": "blocked"
                }
            }
            return rules_data.get(rule_id)
        
        mock_loader.get_rule_by_id.side_effect = mock_get_rule
        
        formatter = BusinessWisdomFormatter(loader=mock_loader)
        
        # Simulate DoR context with governance rules
        dor_context = {
            "intent_type": "IMPLEMENT",
            "target_handler": "TDDOrchestrator",
            "governance_rules": ["CORE-008", "CORE-011"],
            "dor_confidence": 0.85
        }
        
        # Act - Generate wisdom section
        wisdom_section = formatter.format_governance_with_books(
            rule_ids=dor_context["governance_rules"],
            max_display=5,
            include_icon=True
        )
        
        # Assert - Verify section can be integrated into DoR markdown
        assert wisdom_section, "Should generate non-empty wisdom section"
        assert isinstance(wisdom_section, str), "Should return string for markdown integration"
        
        # Verify it follows DoR display conventions
        lines = wisdom_section.split("\n")
        assert lines[0].startswith("###"), "Should use H3 heading for DoR sections"
        
        # Verify list format compatible with DoR tables
        list_items = [line for line in lines if line.startswith("- ")]
        assert len(list_items) == 2, "Should show 2 governance rules"
        for item in list_items:
            assert "→" in item, "Each item should use arrow notation"
            assert "**" in item, "Each item should have bold principle"


# AC_COMPLETE: AC-PHASE-06-S2-003 ✅ 2/2 tests passing
