"""
Test suite for ConversationalReflector (Phase 101 Stage 2).

AC_START: AC-CIG-S2-001
AC_START: AC-CIG-S2-002
AC_START: AC-CIG-S2-003
AC_START: AC-CIG-S2-004
AC_START: AC-CIG-S2-005

Tests:
- Natural language reflection generation (2 sentences)
- Vocabulary mirroring (user words, not jargon)
- Confidence level integration
- Token budget compliance (≤60 tokens)
- Validation data preservation
"""

import pytest
from typing import Dict, Any
from cortex.orchestrators.core.conversational_reflector import (
    ConversationalReflector,
    ConversationalReflection,
)


class TestConversationalReflector:
    """Test conversational reflection generation."""

    def test_reflect_implement_intent_natural_language(self):
        """AC-CIG-S2-01: Generate 2-sentence natural language summary."""
        reflector = ConversationalReflector()
        
        dor_data = {
            "intent_type": "IMPLEMENT",
            "confidence": 0.92,
            "canonical_keywords": ["implement", "authentication", "login", "module"],
            "scope": "module",
            "impact": "medium",
            "user_text": "implement user authentication for login module"
        }
        
        reflection = reflector.reflect(dor_data)
        
        # Should be 2 sentences
        sentences = reflection.summary.split('.')
        sentences = [s.strip() for s in sentences if s.strip()]
        assert 1 <= len(sentences) <= 2, f"Expected 1-2 sentences, got {len(sentences)}"
        
        # Should be natural language (no code/jargon)
        assert "You want to" in reflection.summary or "This involves" in reflection.context
        assert "IMPLEMENT" not in reflection.summary  # No technical constants
        assert reflection.summary[0].isupper()  # Proper capitalization
    
    def test_mirror_user_vocabulary_not_jargon(self):
        """AC-CIG-S2-02: Mirror user's vocabulary (not technical jargon)."""
        reflector = ConversationalReflector()
        
        dor_data = {
            "intent_type": "FIX",
            "confidence": 0.88,
            "canonical_keywords": ["fix", "broken", "login", "page"],
            "scope": "component",
            "impact": "high",
            "user_text": "fix the broken login page"
        }
        
        reflection = reflector.reflect(dor_data)
        
        # Should use user's words
        assert "broken" in reflection.summary or "login page" in reflection.summary
        assert "fix" in reflection.summary.lower()
        
        # Should NOT use technical jargon
        assert "IntentRouter" not in reflection.summary
        assert "TDDOrchestrator" not in reflection.summary
        assert "AC-" not in reflection.summary
    
    def test_include_confidence_level_high_medium_low(self):
        """AC-CIG-S2-03: Include confidence level (High/Medium/Low)."""
        reflector = ConversationalReflector()
        
        # Test high confidence
        dor_high = {
            "intent_type": "ANALYZE",
            "confidence": 0.95,
            "canonical_keywords": ["analyze", "performance"],
            "scope": "system",
            "impact": "low",
            "user_text": "analyze system performance"
        }
        reflection_high = reflector.reflect(dor_high)
        assert "High confidence" in reflection_high.confidence or reflection_high.confidence.startswith("High")
        assert 0.90 <= reflection_high.confidence_score <= 1.0
        
        # Test medium confidence
        dor_medium = {
            "intent_type": "REFACTOR",
            "confidence": 0.70,
            "canonical_keywords": ["refactor", "code"],
            "scope": "unclear",
            "impact": "medium",
            "user_text": "refactor code"
        }
        reflection_medium = reflector.reflect(dor_medium)
        assert "Medium confidence" in reflection_medium.confidence or reflection_medium.confidence.startswith("Medium")
        assert 0.60 <= reflection_medium.confidence_score < 0.90
        
        # Test low confidence
        dor_low = {
            "intent_type": "UNKNOWN",
            "confidence": 0.45,
            "canonical_keywords": ["check", "stuff"],
            "scope": "unclear",
            "impact": "low",
            "user_text": "check the stuff"
        }
        reflection_low = reflector.reflect(dor_low)
        assert "Low confidence" in reflection_low.confidence or reflection_low.confidence.startswith("Low")
        assert reflection_low.confidence_score < 0.60
    
    def test_output_token_budget_60_tokens_max(self):
        """AC-CIG-S2-04: Output ≤60 tokens consistently."""
        reflector = ConversationalReflector()
        
        # Test with verbose input
        dor_data = {
            "intent_type": "IMPLEMENT",
            "confidence": 0.85,
            "canonical_keywords": ["implement", "complex", "multi-layer", "authentication", "system", "microservices"],
            "scope": "system",
            "impact": "high",
            "user_text": "implement complex multi-layer authentication system for microservices architecture"
        }
        
        reflection = reflector.reflect(dor_data)
        
        # Count tokens (rough approximation: split by whitespace)
        combined_text = f"{reflection.summary} {reflection.context} {reflection.confidence}"
        token_count = len(combined_text.split())
        
        assert token_count <= 60, f"Expected ≤60 tokens, got {token_count}"
        assert token_count >= 20, f"Too short: {token_count} tokens (may be oversimplified)"
    
    def test_preserve_validation_data_background(self):
        """AC-CIG-S2-05: Preserve validation data in background."""
        reflector = ConversationalReflector()
        
        dor_data = {
            "intent_type": "FIX",
            "confidence": 0.91,
            "canonical_keywords": ["fix", "critical", "bug"],
            "scope": "component",
            "impact": "high",
            "urgency": "high",
            "user_text": "fix critical bug in payment processor",
            "additional_metadata": {"session_id": "test-123"}
        }
        
        reflection = reflector.reflect(dor_data)
        
        # Validation data should be stored (not in summary/context)
        assert reflection.validation_data is not None
        assert reflection.validation_data.get("intent_type") == "FIX"
        assert reflection.validation_data.get("confidence") == 0.91
        assert "canonical_keywords" in reflection.validation_data
        
        # User-facing text should NOT include validation data
        assert "0.91" not in reflection.summary
        assert "intent_type" not in reflection.summary.lower()
    
    def test_generate_rationale_for_implement(self):
        """Test rationale generation for IMPLEMENT intent."""
        reflector = ConversationalReflector()
        
        rationale = reflector.generate_rationale("IMPLEMENT")
        
        assert "add new functionality" in rationale.lower() or "create" in rationale.lower()
        assert len(rationale.split()) <= 15  # Keep rationale concise
    
    def test_generate_rationale_for_fix(self):
        """Test rationale generation for FIX intent."""
        reflector = ConversationalReflector()
        
        rationale = reflector.generate_rationale("FIX")
        
        assert "resolve" in rationale.lower() or "fix" in rationale.lower() or "issue" in rationale.lower()
        assert len(rationale.split()) <= 15
    
    def test_generate_rationale_for_analyze(self):
        """Test rationale generation for ANALYZE intent."""
        reflector = ConversationalReflector()
        
        rationale = reflector.generate_rationale("ANALYZE")
        
        assert "understand" in rationale.lower() or "analyze" in rationale.lower() or "state" in rationale.lower()
        assert len(rationale.split()) <= 15
    
    def test_format_confidence_high(self):
        """Test confidence formatting for high confidence."""
        reflector = ConversationalReflector()
        
        formatted = reflector.format_confidence(0.92)
        
        assert formatted.startswith("High confidence")
        assert "92%" in formatted or "9" in formatted
    
    def test_format_confidence_medium(self):
        """Test confidence formatting for medium confidence."""
        reflector = ConversationalReflector()
        
        formatted = reflector.format_confidence(0.75)
        
        assert formatted.startswith("Medium confidence")
        assert "75%" in formatted or "7" in formatted
    
    def test_format_confidence_low(self):
        """Test confidence formatting for low confidence."""
        reflector = ConversationalReflector()
        
        formatted = reflector.format_confidence(0.50)
        
        assert formatted.startswith("Low confidence")
        assert "50%" in formatted or "5" in formatted
    
    def test_dataclass_structure_complete(self):
        """Test ConversationalReflection dataclass has all fields."""
        reflector = ConversationalReflector()
        
        dor_data = {
            "intent_type": "REFACTOR",
            "confidence": 0.80,
            "canonical_keywords": ["refactor", "module"],
            "scope": "module",
            "impact": "medium",
            "user_text": "refactor the authentication module"
        }
        
        reflection = reflector.reflect(dor_data)
        
        # All fields should be present
        assert hasattr(reflection, 'summary')
        assert hasattr(reflection, 'context')
        assert hasattr(reflection, 'confidence')
        assert hasattr(reflection, 'confidence_score')
        assert hasattr(reflection, 'validation_data')
        
        # All fields should be populated
        assert reflection.summary is not None
        assert reflection.context is not None
        assert reflection.confidence is not None
        assert reflection.confidence_score is not None
        assert reflection.validation_data is not None
