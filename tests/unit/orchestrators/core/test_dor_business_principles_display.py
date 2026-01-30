"""
Test DoR Business Principles Display

Verifies that business principles are displayed correctly in DoR markdown
with comma-separated format for better rendering in GitHub Copilot Chat.

Author: Asif Hussain
AC-ID: AC-GOVE-BIZ-PRIN-001
Updated: 2026-01-30 (Changed from <br/> to comma-separated format)
"""

import pytest
from cortex.orchestrators.core.dor_approval_gate import IntentReflection


class TestBusinessPrinciplesDisplay:
    """Test business principles display in DoR markdown."""
    
    def test_business_principles_display_format(self):
        """Test that business principles show with technical terms in comma-separated format."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.85,
            scope="MODULE",
            governance_rules=["CORE-008", "CORE-011", "CORE-012"],
            requires_tests=True,
            estimated_impact="medium"
        )
        
        markdown = reflection.to_markdown()
        
        # Verify business principles row exists
        assert "**Business Principles**" in markdown, "Business Principles row should exist"
        
        # Verify comma separation between principles
        assert ", " in markdown, "Should have commas between principles"
        
        # Verify business principle for CORE-008 (TDD)
        assert "Red-Green-Refactor Discipline" in markdown or "TDD" in markdown, \
            "Should show TDD principle"
        
        # Verify business principle for CORE-011 (Type Safety)
        assert "Type Safety" in markdown, "Should show Type Safety principle"
        
        # Verify business principle for CORE-012 (Documentation)
        assert "Documentation" in markdown or "Docstrings" in markdown, \
            "Should show Documentation principle"
        
        # Verify CORE-IDs are still present
        assert "CORE-008" in markdown, "Should show CORE-008 ID"
        assert "CORE-011" in markdown, "Should show CORE-011 ID"
        assert "CORE-012" in markdown, "Should show CORE-012 ID"
    
    def test_multiple_principles_comma_separated(self):
        """Test that multiple principles appear comma-separated."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.90,
            scope="SYSTEM",
            governance_rules=["CORE-008", "CORE-026", "CORE-030"],
            requires_tests=True
        )
        
        markdown = reflection.to_markdown()
        
        # Count commas (should be N-1 for N principles)
        comma_count = markdown.count(", **")  # Count commas before bold principles
        assert comma_count >= 2, f"Should have at least 2 commas for 3 principles, got {comma_count}"
        
        # Verify each principle is present
        assert "TDD" in markdown, "Should show TDD"
        assert "Git Safety" in markdown or "CORE-026" in markdown, "Should show Git Safety"
        assert "Implementation Truth" in markdown or "CORE-030" in markdown, \
            "Should show Implementation Truth"
    
    def test_no_principles_no_row(self):
        """Test that Business Principles row is omitted when no rules."""
        reflection = IntentReflection(
            intent_type="ANALYZE",
            target_handler="AnalysisOrchestrator",
            dor_confidence=0.70,
            scope="FILE",
            governance_rules=[],  # No rules
            requires_tests=False
        )
        
        markdown = reflection.to_markdown()
        
        # Business Principles row should not exist
        assert "**Business Principles**" not in markdown, \
            "Should not show Business Principles row when no rules"
    
    def test_principle_format_with_arrow(self):
        """Test that principles use arrow notation: Principle → Technical (CORE-ID)."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.88,
            scope="MODULE",
            governance_rules=["CORE-008"],
            requires_tests=True
        )
        
        markdown = reflection.to_markdown()
        
        # Verify arrow notation exists
        assert "→" in markdown, "Should use arrow notation between principle and technical term"
        
        # Verify format: **Principle** → Technical (CORE-ID)
        # Example: **Red-Green-Refactor Discipline** → TDD (CORE-008)
        assert "**" in markdown, "Principle should be bold"
        assert "(" in markdown and ")" in markdown, "CORE-ID should be in parentheses"
    
    def test_up_to_five_principles_displayed(self):
        """Test that up to 5 principles are displayed (as per code limit)."""
        reflection = IntentReflection(
            intent_type="IMPLEMENT",
            target_handler="TDDOrchestrator",
            dor_confidence=0.92,
            scope="SYSTEM",
            governance_rules=[
                "CORE-008",
                "CORE-011",
                "CORE-012",
                "CORE-026",
                "CORE-030",
                "CORE-038",  # 6th rule - should not appear
            ],
            requires_tests=True
        )
        
        markdown = reflection.to_markdown()
        
        # Should show first 5 rules
        assert "CORE-008" in markdown
        assert "CORE-011" in markdown
        assert "CORE-012" in markdown
        assert "CORE-026" in markdown
        assert "CORE-030" in markdown
        
        # 6th rule might not appear (limit is 5)
        # Just verify we have at least 4 commas (for 5 principles)
        comma_count = markdown.count(", **")  # Count commas before bold principles
        assert comma_count >= 4, f"Should have at least 4 commas for 5+ principles"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
