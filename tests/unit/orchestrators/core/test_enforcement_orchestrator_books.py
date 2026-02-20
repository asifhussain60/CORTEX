# AC_START: AC-PHASE-06-S2-001
"""
Tests for EnforcementOrchestrator book reference integration.

Test Coverage:
    - Book reference formatting (3 tests)
    - Fallback behavior (2 tests)
    - Integration with BusinessWisdomFormatter (2 tests)

Total: 7 tests

Authority:
    - phase-06-business-wisdom-display-enhancement.yaml (Stage 2)
    - business-wisdom-wiring.md

Governance:
    - CORE-008: TDD
    - CORE-011: Type hints
    - CORE-012: Docstrings

Author: Asif Hussain
Date: 2026-02-13
"""

from unittest.mock import Mock, patch

import pytest

from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator


class TestBookReferenceFormatting:
    """Test book reference formatting (3 tests)."""
    
    @patch("cortex.core.interaction.business_wisdom_formatter.BusinessWisdomFormatter")
    def test_format_single_rule_with_book(self, mock_formatter_class: Mock) -> None:
        """Test formatting single rule with book reference."""
        # Arrange
        mock_formatter = Mock()
        mock_formatter.format_governance_with_books.return_value = (
            "### Business Wisdom\n"
            "- **Red-Green-Refactor Discipline** → CORE-008 (TDD by Kent Beck)"
        )
        mock_formatter_class.return_value = mock_formatter
        
        orchestrator = EnforcementOrchestrator()
        
        # Act
        result = orchestrator._format_governance_rule_with_book("CORE-008")
        
        # Assert
        assert "**Red-Green-Refactor Discipline**" in result
        assert "CORE-008" in result
        assert "TDD by Kent Beck" in result
        assert not result.startswith("- ")  # List marker stripped
    
    @patch("cortex.core.interaction.business_wisdom_formatter.BusinessWisdomFormatter")
    def test_multiple_calls_use_separate_instances(self, mock_formatter_class: Mock) -> None:
        """Test each call creates separate formatter instance."""
        # Arrange
        mock_formatter = Mock()
        mock_formatter.format_governance_with_books.return_value = (
            "### Business Wisdom\n"
            "- **Principle** → CORE-001 (Book)"
        )
        mock_formatter_class.return_value = mock_formatter
        
        orchestrator = EnforcementOrchestrator()
        
        # Act
        orchestrator._format_governance_rule_with_book("CORE-001")
        orchestrator._format_governance_rule_with_book("CORE-002")
        
        # Assert
        assert mock_formatter_class.call_count == 2  # New instance each time
    
    @patch("cortex.core.interaction.business_wisdom_formatter.BusinessWisdomFormatter")
    def test_inline_display_format(self, mock_formatter_class: Mock) -> None:
        """Test inline display format (no icon, no list marker)."""
        # Arrange
        mock_formatter = Mock()
        mock_formatter_class.return_value = mock_formatter
        
        orchestrator = EnforcementOrchestrator()
        orchestrator._format_governance_rule_with_book("CORE-008")
        
        # Assert
        mock_formatter.format_governance_with_books.assert_called_once_with(
            rule_ids=["CORE-008"],
            max_display=1,
            include_icon=False
        )


class TestFallbackBehavior:
    """Test fallback behavior (2 tests)."""
    
    @patch("cortex.core.interaction.business_wisdom_formatter.BusinessWisdomFormatter")
    def test_fallback_when_formatter_returns_empty(self, mock_formatter_class: Mock) -> None:
        """Test fallback to rule ID when formatter returns empty string."""
        # Arrange
        mock_formatter = Mock()
        mock_formatter.format_governance_with_books.return_value = ""
        mock_formatter_class.return_value = mock_formatter
        
        orchestrator = EnforcementOrchestrator()
        
        # Act
        result = orchestrator._format_governance_rule_with_book("CORE-999")
        
        # Assert
        assert result == "CORE-999"  # Fallback to rule ID
    
    @patch("cortex.core.interaction.business_wisdom_formatter.BusinessWisdomFormatter")
    def test_fallback_when_formatter_raises_exception(self, mock_formatter_class: Mock) -> None:
        """Test fallback to rule ID when formatter raises exception."""
        # Arrange
        mock_formatter_class.side_effect = Exception("Formatter error")
        
        orchestrator = EnforcementOrchestrator()
        
        # Act
        result = orchestrator._format_governance_rule_with_book("CORE-008")
        
        # Assert
        assert result == "CORE-008"  # Graceful degradation


class TestIntegration:
    """Test integration (2 tests)."""
    
    @patch("cortex.core.interaction.business_wisdom_formatter.BusinessWisdomFormatter")
    def test_strips_list_marker_correctly(self, mock_formatter_class: Mock) -> None:
        """Test list marker (- ) stripped correctly for inline display."""
        # Arrange
        mock_formatter = Mock()
        mock_formatter.format_governance_with_books.return_value = (
            "### Business Wisdom\n"
            "- **Red-Green-Refactor** → CORE-008 (Book)"
        )
        mock_formatter_class.return_value = mock_formatter
        
        orchestrator = EnforcementOrchestrator()
        
        # Act
        result = orchestrator._format_governance_rule_with_book("CORE-008")
        
        # Assert
        assert result == "**Red-Green-Refactor** → CORE-008 (Book)"
        assert not result.startswith("- ")
    
    @patch("cortex.core.interaction.business_wisdom_formatter.BusinessWisdomFormatter")
    def test_handles_multiline_markdown_gracefully(self, mock_formatter_class: Mock) -> None:
        """Test multiline markdown handled (returns first line with content)."""
        # Arrange
        mock_formatter = Mock()
        mock_formatter.format_governance_with_books.return_value = (
            "### Business Wisdom\n"
            "\n"  # Empty line
            "- **Red-Green-Refactor** → CORE-008 (Book)\n"
            "- **Another Rule** → CORE-011 (Book2)"
        )
        mock_formatter_class.return_value = mock_formatter
        
        orchestrator = EnforcementOrchestrator()
        
        # Act
        result = orchestrator._format_governance_rule_with_book("CORE-008")
        
        # Assert
        assert "**Red-Green-Refactor**" in result
        assert not result.startswith("- ")


# AC_COMPLETE: AC-PHASE-06-S2-001 ✅ 7 tests
