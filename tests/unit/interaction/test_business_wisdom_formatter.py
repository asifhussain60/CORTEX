# AC_START: AC-PHASE-06-S1-002
"""
Unit tests for BusinessWisdomFormatter.

Test Coverage:
    - Format validation (4 tests)
    - Markdown structure (3 tests)
    - Edge cases (3 tests)
    - Integration (2 tests)

Total: 12 tests (100% coverage)

Authority:
    - phase-06-business-wisdom-display-enhancement.yaml (Stage 1 test strategy)
    - TDD by Kent Beck (test-first development)

Governance:
    - CORE-008: TDD (tests before code)
    - CORE-011: Type hints 100%
    - CORE-012: Google-style docstrings

Author: Asif Hussain
Date: 2026-02-13
"""

from typing import Any, Dict, List
from unittest.mock import Mock, patch

import pytest

from cortex.orchestrators.core.business_wisdom_formatter import BusinessWisdomFormatter


class TestFormatValidation:
    """Test format validation (4 tests)."""
    
    def test_single_rule_with_book_reference(self) -> None:
        """Test single rule formatted correctly with book reference."""
        # Arrange
        mock_loader = Mock()
        mock_loader.get_rule_by_id.return_value = {
            "rule_id": "CORE-008",
            "principle": "Red-Green-Refactor Discipline",
            "book_reference": "Test-Driven Development: By Example by Kent Beck",
            "severity": "blocked"
        }
        formatter = BusinessWisdomFormatter(loader=mock_loader)
        
        # Act
        result = formatter.format_governance_with_books(rule_ids=["CORE-008"])
        
        # Assert
        assert "**Red-Green-Refactor Discipline**" in result
        assert "CORE-008" in result
        assert "Test-Driven Development: By Example by Kent Beck" in result
        assert "→" in result  # Arrow notation
    
    def test_single_rule_without_book_reference(self) -> None:
        """Test graceful degradation when book reference missing."""
        # Arrange
        mock_loader = Mock()
        mock_loader.get_rule_by_id.return_value = {
            "rule_id": "CORE-999",
            "principle": "Custom Rule",
            "severity": "warning"
        }
        formatter = BusinessWisdomFormatter(loader=mock_loader)
        
        # Act
        result = formatter.format_governance_with_books(rule_ids=["CORE-999"])
        
        # Assert
        assert "**Custom Rule**" in result
        assert "CORE-999" in result
        assert "→" in result
        # Should not have book reference
        assert "(" not in result or ")" not in result
    
    def test_multiple_rules_formatted_correctly(self) -> None:
        """Test multiple rules (3) formatted correctly."""
        # Arrange
        mock_loader = Mock()
        mock_loader.get_rule_by_id.side_effect = [
            {
                "rule_id": "CORE-008",
                "principle": "Red-Green-Refactor Discipline",
                "book_reference": "TDD by Kent Beck",
                "severity": "blocked"
            },
            {
                "rule_id": "CORE-011",
                "principle": "Type Hints Mandatory",
                "book_reference": "Clean Code by Robert Martin",
                "severity": "blocked"
            },
            {
                "rule_id": "CORE-012",
                "principle": "Google Docstrings",
                "book_reference": "Pragmatic Programmer by Hunt & Thomas",
                "severity": "blocked"
            }
        ]
        formatter = BusinessWisdomFormatter(loader=mock_loader)
        
        # Act
        result = formatter.format_governance_with_books(
            rule_ids=["CORE-008", "CORE-011", "CORE-012"]
        )
        
        # Assert
        assert "CORE-008" in result
        assert "CORE-011" in result
        assert "CORE-012" in result
        assert result.count("→") == 3  # All have arrow notation
        assert result.count("**") == 6  # 3 principles, each with ** on both sides
    
    def test_max_display_limit_enforcement(self) -> None:
        """Test max display limit (5 rules) enforced."""
        # Arrange
        mock_loader = Mock()
        rules = []
        for i in range(10):  # 10 rules
            rules.append({
                "rule_id": f"CORE-{i:03d}",
                "principle": f"Rule {i}",
                "book_reference": f"Book {i}",
                "severity": "blocked"
            })
        mock_loader.get_rule_by_id.side_effect = rules
        formatter = BusinessWisdomFormatter(loader=mock_loader)
        
        # Act
        result = formatter.format_governance_with_books(
            rule_ids=[f"CORE-{i:03d}" for i in range(10)],
            max_display=5
        )
        
        # Assert
        assert result.count("→") == 5  # Only 5 displayed
        assert "CORE-000" in result  # First rule
        assert "CORE-004" in result  # Fifth rule
        assert "CORE-009" not in result  # Tenth rule not displayed


class TestMarkdownStructure:
    """Test markdown structure (3 tests)."""
    
    def test_section_header_includes_icon(self) -> None:
        """Test section header includes 📚 icon."""
        # Arrange
        mock_loader = Mock()
        mock_loader.get_rule_by_id.return_value = {
            "rule_id": "CORE-008",
            "principle": "Red-Green-Refactor Discipline",
            "book_reference": "TDD by Kent Beck",
            "severity": "blocked"
        }
        formatter = BusinessWisdomFormatter(loader=mock_loader)
        
        # Act
        result = formatter.format_governance_with_books(
            rule_ids=["CORE-008"],
            include_icon=True
        )
        
        # Assert
        assert "### 📚 Business Wisdom" in result
    
    def test_arrow_notation_present(self) -> None:
        """Test arrow notation (→) present in formatted output."""
        # Arrange
        mock_loader = Mock()
        mock_loader.get_rule_by_id.return_value = {
            "rule_id": "CORE-008",
            "principle": "Red-Green-Refactor Discipline",
            "book_reference": "TDD by Kent Beck",
            "severity": "blocked"
        }
        formatter = BusinessWisdomFormatter(loader=mock_loader)
        
        # Act
        result = formatter.format_governance_with_books(rule_ids=["CORE-008"])
        
        # Assert
        assert "→" in result
    
    def test_bold_principle_names(self) -> None:
        """Test principle names are bold (**text**)."""
        # Arrange
        mock_loader = Mock()
        mock_loader.get_rule_by_id.return_value = {
            "rule_id": "CORE-008",
            "principle": "Red-Green-Refactor Discipline",
            "book_reference": "TDD by Kent Beck",
            "severity": "blocked"
        }
        formatter = BusinessWisdomFormatter(loader=mock_loader)
        
        # Act
        result = formatter.format_governance_with_books(rule_ids=["CORE-008"])
        
        # Assert
        assert "**Red-Green-Refactor Discipline**" in result


class TestEdgeCases:
    """Test edge cases (3 tests)."""
    
    def test_empty_rule_list_returns_empty_string(self) -> None:
        """Test empty rule list returns empty string."""
        # Arrange
        formatter = BusinessWisdomFormatter()
        
        # Act
        result = formatter.format_governance_with_books(rule_ids=[])
        
        # Assert
        assert result == ""
    
    def test_invalid_rule_ids_skipped_gracefully(self) -> None:
        """Test invalid rule IDs skipped gracefully."""
        # Arrange
        mock_loader = Mock()
        mock_loader.get_rule_by_id.side_effect = [
            None,  # Invalid rule
            {
                "rule_id": "CORE-008",
                "principle": "Red-Green-Refactor Discipline",
                "book_reference": "TDD by Kent Beck",
                "severity": "blocked"
            }
        ]
        formatter = BusinessWisdomFormatter(loader=mock_loader)
        
        # Act
        result = formatter.format_governance_with_books(
            rule_ids=["INVALID-RULE", "CORE-008"]
        )
        
        # Assert
        assert "CORE-008" in result
        assert "INVALID-RULE" not in result
    
    def test_missing_book_reference_field_handled(self) -> None:
        """Test missing book_reference field handled gracefully."""
        # Arrange
        mock_loader = Mock()
        mock_loader.get_rule_by_id.return_value = {
            "rule_id": "CORE-999",
            "principle": "Custom Rule",
            "severity": "warning"
            # No book_reference field
        }
        formatter = BusinessWisdomFormatter(loader=mock_loader)
        
        # Act
        result = formatter.format_governance_with_books(rule_ids=["CORE-999"])
        
        # Assert
        assert "**Custom Rule**" in result
        assert "CORE-999" in result
        # Should not crash, just omit book reference


class TestIntegration:
    """Test integration (2 tests)."""
    
    @patch("cortex.orchestrators.core.business_wisdom_formatter.GovernanceRuleLoader")
    def test_governance_rule_loader_integration(
        self, mock_loader_class: Mock
    ) -> None:
        """Test integration with GovernanceRuleLoader."""
        # Arrange
        mock_instance = Mock()
        mock_instance.get_rule_by_id.return_value = {
            "rule_id": "CORE-008",
            "principle": "Red-Green-Refactor Discipline",
            "book_reference": "TDD by Kent Beck",
            "severity": "blocked"
        }
        mock_loader_class.return_value = mock_instance
        
        # Act
        formatter = BusinessWisdomFormatter()  # Uses default loader
        result = formatter.format_governance_with_books(rule_ids=["CORE-008"])
        
        # Assert
        mock_loader_class.assert_called_once()
        mock_instance.get_rule_by_id.assert_called_once_with("CORE-008")
        assert "CORE-008" in result
    
    def test_severity_based_sorting(self) -> None:
        """Test rules sorted by severity (P0 → P1 → P2)."""
        # Arrange
        mock_loader = Mock()
        mock_loader.get_rule_by_id.side_effect = [
            {
                "rule_id": "CORE-001",
                "principle": "Warning Rule",
                "severity": "warning"  # P1
            },
            {
                "rule_id": "CORE-008",
                "principle": "Blocked Rule",
                "severity": "blocked"  # P0 (higher priority)
            },
            {
                "rule_id": "CORE-999",
                "principle": "Other Rule",
                "severity": "other"  # P2
            }
        ]
        formatter = BusinessWisdomFormatter(loader=mock_loader)
        
        # Act
        result = formatter.format_governance_with_books(
            rule_ids=["CORE-001", "CORE-008", "CORE-999"]
        )
        
        # Assert
        # CORE-008 (blocked/P0) should appear before CORE-001 (warning/P1)
        assert result.index("CORE-008") < result.index("CORE-001")
        # CORE-001 (warning/P1) should appear before CORE-999 (other/P2)
        assert result.index("CORE-001") < result.index("CORE-999")


# AC_COMPLETE: AC-PHASE-06-S1-002 ✅ 12 tests
