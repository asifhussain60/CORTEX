"""
Test DoR Business Principles Display

AC-ID: INTEGRATION-FIX-001
Validates that Intent Classification table displays with Business Principles
mapped to CORE governance rules (Hedgehog Concept, Flywheel Effect, etc.)

Author: Asif Hussain
Date: 2026-01-31
"""

import pytest
from cortex.orchestrators.core.dor_approval_gate import (
    DoRApprovalGate,
    # display_intent_classification,  # DEPRECATED: Function removed in refactor
    # echo_user_intent,  # DEPRECATED: Function removed in refactor
)


class TestDoRBusinessPrinciplesDisplay:
    """Test suite for DoR Business Principles display functionality."""
    
    def test_display_intent_classification_shows_business_principles(self):
        """Test that display_intent_classification shows business principles."""
        # Arrange
        gate = DoRApprovalGate()
        user_request = "implement user authentication with JWT tokens"
        
        # Act
        reflection = gate.classify_and_reflect(user_request, {})
        result = reflection.to_markdown()
        
        # Assert
        assert "### 📋 Intent Classification" in result
        assert "**Business Principles**" in result
        assert "**Quality First**" in result or "**Maintainability**" in result
        assert "CORE-" in result  # At least one CORE rule mapped
        assert "|" in result  # Table format
    
    def test_implement_intent_maps_quality_principles(self):
        """Test IMPLEMENT intent maps Quality First, Maintainability, Documentation."""
        # Arrange
        gate = DoRApprovalGate()
        
        # Act
        reflection = gate.classify_and_reflect("implement new feature", {})
        markdown = reflection.to_markdown()
        
        # Assert
        assert reflection.intent_type.lower() == "implement"
        assert len(reflection.business_principles) >= 2
        assert "Quality First" in reflection.business_principles or \
               "Maintainability" in reflection.business_principles
        assert "CORE-008" in markdown or "CORE-011" in markdown
    
    def test_fix_intent_maps_reliability_principles(self):
        """Test FIX intent maps Reliability and Root Cause Analysis."""
        # Arrange
        gate = DoRApprovalGate()
        
        # Act
        reflection = gate.classify_and_reflect("fix race condition bug", {})
        
        # Assert
        # FIX intent should map to reliability principles
        assert reflection.intent_type.lower() in ["fix", "bugfix"]
        assert len(reflection.business_principles) >= 1
    
    def test_refactor_intent_maps_code_quality_principles(self):
        """Test REFACTOR intent maps Code Quality and Maintainability."""
        # Arrange
        gate = DoRApprovalGate()
        
        # Act
        reflection = gate.classify_and_reflect("refactor orchestrator structure", {})
        
        # Assert
        assert "refactor" in reflection.intent_type.lower()
        assert len(reflection.business_principles) >= 1
    
    def test_markdown_table_has_business_principles_row(self):
        """Test markdown output contains Business Principles table row."""
        # Arrange
        gate = DoRApprovalGate()
        user_request = "implement cache invalidation"
        
        # Act
        reflection = gate.classify_and_reflect(user_request, {})
        result = reflection.to_markdown()
        
        # Assert
        # Check for table row with Business Principles
        lines = result.split("\n")
        business_principles_row = [line for line in lines if "**Business Principles**" in line]
        assert len(business_principles_row) > 0, "Business Principles row not found in table"
        
        # Check for arrow notation: **Principle** → Technical (CORE-ID)
        assert "→" in business_principles_row[0], "Arrow notation not found"
        assert "CORE-" in business_principles_row[0], "CORE rule not found"
    
    def test_dor_confidence_displayed(self):
        """Test DoR Confidence is displayed with emoji indicator."""
        # Arrange
        gate = DoRApprovalGate()
        user_request = "implement feature"
        
        # Act
        reflection = gate.classify_and_reflect(user_request, {})
        result = reflection.to_markdown()
        
        # Assert
        assert "**DoR Confidence**" in result or "**Confidence**" in result
        # Should have emoji indicator (🟢/🟡/🔴)
        assert any(emoji in result for emoji in ["🟢", "🟡", "🔴"])
    
    def test_governance_rules_mapped_to_principles(self):
        """Test governance rules are properly mapped to business principles."""
        # Arrange
        gate = DoRApprovalGate()
        
        # Act
        reflection = gate.classify_and_reflect("implement authentication", {})
        
        # Assert
        assert len(reflection.governance_rules) > 0
        assert len(reflection.business_principles) > 0
        # Each principle should reference a CORE rule
        for principle, rule in reflection.business_principles.items():
            assert "CORE-" in rule or "TDD" in rule or "Type Safety" in rule
    
    def test_echo_user_intent_alias_works(self):
        """Test classify_and_reflect is deterministic."""
        # Arrange
        gate = DoRApprovalGate()
        user_request = "test request"
        
        # Act
        reflection1 = gate.classify_and_reflect(user_request, {})
        reflection2 = gate.classify_and_reflect(user_request, {})
        result1 = reflection1.to_markdown()
        result2 = reflection2.to_markdown()
        
        # Assert
        assert result1 == result2
    
    def test_empty_context_defaults_gracefully(self):
        """Test that empty context doesn't break display."""
        # Arrange
        gate = DoRApprovalGate()
        user_request = "implement feature"
        
        # Act (use empty dict, not None)
        reflection1 = gate.classify_and_reflect(user_request, {})
        reflection2 = gate.classify_and_reflect(user_request, {})
        result1 = reflection1.to_markdown()
        result2 = reflection2.to_markdown()
        
        # Assert
        assert "**Business Principles**" in result1
        assert "**Business Principles**" in result2
        assert result1 == result2  # Should be deterministic
    
    def test_complex_request_shows_multiple_principles(self):
        """Test complex request shows multiple mapped principles."""
        # Arrange
        gate = DoRApprovalGate()
        complex_request = "implement user authentication with JWT, write comprehensive tests, and document the API"
        
        # Act
        reflection = gate.classify_and_reflect(complex_request, {})
        result = reflection.to_markdown()
        
        # Assert
        # Should have multiple principles for IMPLEMENT intent
        assert "Quality First" in result or "TDD" in result or "Maintainability" in result
        assert "|" in result  # Table format


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
