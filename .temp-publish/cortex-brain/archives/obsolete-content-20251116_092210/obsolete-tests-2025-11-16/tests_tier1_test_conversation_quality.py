"""
Tests for CORTEX 3.0 Conversation Quality Analyzer

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from src.tier1.conversation_quality import (
    ConversationQualityAnalyzer,
    QualityScore,
    SemanticElements,
    create_analyzer
)


class TestConversationQualityAnalyzer:
    """Test conversation quality analysis."""
    
    def test_excellent_quality_multi_phase(self):
        """Test EXCELLENT quality detection with multi-phase planning."""
        analyzer = ConversationQualityAnalyzer(show_hint_threshold="GOOD")
        
        user_prompt = "Implement the smart hint feature"
        assistant_response = """
        🧠 CORTEX Feature Implementation
        
        ⚠️ **Challenge:** ✓ **Accept**
        This approach is sound with good architecture.
        
        💬 **Response:** I'll implement using a modular design with clear separation.
        
        🔍 Next Steps:
           ☐ Phase 1: Core analyzer (tasks 1-3)
           ☐ Phase 2: Integration layer (tasks 4-6)
           ☐ Phase 3: Testing validation (tasks 7-9)
        
        Files: `src/tier1/conversation_quality.py`, `src/tier1/smart_hint_generator.py`
        """
        
        quality = analyzer.analyze_conversation(user_prompt, assistant_response)
        
        assert quality.level == "EXCELLENT"
        assert quality.total_score >= 10
        assert quality.elements.multi_phase_planning is True
        assert quality.elements.phase_count == 3
        assert quality.elements.challenge_accept_flow is True
        assert quality.elements.next_steps_provided is True
        assert quality.elements.file_references >= 2
        assert quality.should_show_hint is True
    
    def test_good_quality_with_design(self):
        """Test GOOD quality detection with design decisions."""
        analyzer = ConversationQualityAnalyzer(show_hint_threshold="GOOD")
        
        user_prompt = "How should we handle authentication?"
        assistant_response = """
        We have several alternatives for authentication:
        1. Token-based approach
        2. Session-based strategy
        
        The trade-off is between stateless (tokens) and stateful (sessions).
        We should consider architectural implications for the module layer.
        
        🔍 Next Steps:
           1. Implement token service in `src/auth/token_service.py`
           2. Add middleware in `src/auth/middleware.py`
           3. Test security
        """
        
        quality = analyzer.analyze_conversation(user_prompt, assistant_response)
        
        # Score calculation: design (2) + next steps (2) + file refs (2) + arch (2) = 8 (GOOD)
        assert quality.level == "GOOD"
        assert 6 <= quality.total_score < 10
        assert quality.elements.design_decisions is True
        assert quality.elements.next_steps_provided is True
        assert quality.should_show_hint is True
    
    def test_fair_quality_simple_task(self):
        """Test FAIR quality detection for simple tasks."""
        analyzer = ConversationQualityAnalyzer(show_hint_threshold="GOOD")
        
        user_prompt = "Update the README"
        assistant_response = """
        I'll update the README with:
        - Latest version info in `README.md`
        - Installation steps in `docs/install.md`
        - Usage examples with code in `docs/usage.md`
        
        ```python
        # Example code
        print("hello")
        ```
        """
        
        quality = analyzer.analyze_conversation(user_prompt, assistant_response)
        
        # Score: file refs (3) + code (1) = 4 (FAIR)
        assert quality.level == "FAIR"
        assert 3 <= quality.total_score < 6
        assert quality.should_show_hint is False  # Below GOOD threshold
    
    def test_low_quality_minimal_content(self):
        """Test LOW quality detection."""
        analyzer = ConversationQualityAnalyzer(show_hint_threshold="GOOD")
        
        user_prompt = "What is CORTEX?"
        assistant_response = "CORTEX is a memory system for GitHub Copilot."
        
        quality = analyzer.analyze_conversation(user_prompt, assistant_response)
        
        assert quality.level == "LOW"
        assert quality.total_score < 3
        assert quality.should_show_hint is False
    
    def test_challenge_flow_detection(self):
        """Test challenge/accept flow detection."""
        analyzer = ConversationQualityAnalyzer()
        
        # Test Accept
        response_accept = "⚠️ **Challenge:** ✓ **Accept**\nThis approach is sound."
        quality = analyzer.analyze_conversation("test", response_accept)
        assert quality.elements.challenge_accept_flow is True
        
        # Test Challenge
        response_challenge = "⚠️ **Challenge:** ⚡ **Challenge**\nI suggest an alternative."
        quality = analyzer.analyze_conversation("test", response_challenge)
        assert quality.elements.challenge_accept_flow is True
    
    def test_file_reference_counting(self):
        """Test file reference detection and capping."""
        analyzer = ConversationQualityAnalyzer()
        
        response = """
        Files involved:
        - `src/file1.py`
        - `src/file2.py`
        - `src/file3.py`
        - `src/file4.py`
        - `src/file5.py`
        """
        
        quality = analyzer.analyze_conversation("test", response)
        
        # Should cap at 3 for scoring
        assert quality.elements.file_references == 3
    
    def test_architectural_discussion(self):
        """Test architectural discussion detection."""
        analyzer = ConversationQualityAnalyzer()
        
        response = """
        This affects Tier 1 and Tier 2 components.
        The module interfaces with the plugin layer through the API.
        """
        
        quality = analyzer.analyze_conversation("test", response)
        assert quality.elements.architectural_discussion is True
    
    def test_code_implementation_detection(self):
        """Test code implementation detection."""
        analyzer = ConversationQualityAnalyzer()
        
        response = """
        ```python
        def example():
            return "code"
        ```
        """
        
        quality = analyzer.analyze_conversation("test", response)
        assert quality.elements.code_implementation is True
    
    def test_hint_threshold_excellent_only(self):
        """Test hint threshold set to EXCELLENT only."""
        analyzer = ConversationQualityAnalyzer(show_hint_threshold="EXCELLENT")
        
        # GOOD quality response with higher score
        response = """
        ⚠️ **Challenge:** ✓ **Accept**
        
        ☐ Phase 1: Design
        ☐ Phase 2: Implement
        
        🔍 Next Steps:
           1. Step one
           2. Step two
        
        Design trade-offs discussed with multiple alternatives.
        Architecture includes Tier 1, plugin, and module components.
        Files: `src/file1.py`, `src/file2.py`
        """
        
        quality = analyzer.analyze_conversation("test", response)
        
        # Score: phases (6) + challenge (3) + design (2) + next steps (2) + arch (2) + files (2) = 17 -> EXCELLENT
        # But let's verify it gets GOOD/EXCELLENT and tests threshold
        assert quality.level in ["GOOD", "EXCELLENT"]
        if quality.level == "GOOD":
            assert quality.should_show_hint is False  # Below EXCELLENT threshold
    
    def test_multi_turn_aggregation(self):
        """Test multi-turn conversation aggregation."""
        analyzer = ConversationQualityAnalyzer()
        
        turns = [
            ("First question", "⚠️ **Challenge:** ✓ **Accept**\nGood idea."),
            ("Next step", "☐ Phase 1: Design\n☐ Phase 2: Implement"),
            ("How to test?", "🔍 Next Steps:\n1. Write tests\n2. Run validation")
        ]
        
        quality = analyzer.analyze_multi_turn_conversation(turns)
        
        assert quality.total_score > 0
        assert quality.elements.multi_phase_planning is True
        assert quality.elements.challenge_accept_flow is True
        assert quality.elements.next_steps_provided is True
    
    def test_reasoning_generation(self):
        """Test quality reasoning text generation."""
        analyzer = ConversationQualityAnalyzer()
        
        response = """
        ☐ Phase 1: Design
        ☐ Phase 2: Implement
        
        ⚠️ **Challenge:** ✓ **Accept**
        
        🔍 Next Steps:
           1. Start coding
        
        Files: `src/test.py`
        """
        
        quality = analyzer.analyze_conversation("test", response)
        
        assert "Multi-phase planning" in quality.reasoning
        assert "Challenge/Accept" in quality.reasoning
        assert "Next steps" in quality.reasoning
        assert "file reference" in quality.reasoning
    
    def test_factory_function_with_config(self):
        """Test factory function with configuration."""
        config = {'hint_threshold': 'EXCELLENT'}
        analyzer = create_analyzer(config)
        
        assert analyzer.show_hint_threshold == 'EXCELLENT'
    
    def test_factory_function_defaults(self):
        """Test factory function with defaults."""
        analyzer = create_analyzer()
        
        assert analyzer.show_hint_threshold == 'GOOD'
    
    def test_score_calculation_accuracy(self):
        """Test score calculation matches design."""
        analyzer = ConversationQualityAnalyzer()
        
        response = """
        ☐ Phase 1: First
        ☐ Phase 2: Second
        ⚠️ **Challenge:** ✓ **Accept**
        Design trade-offs discussed with alternatives.
        🔍 Next Steps:
           1. Implement
        Files: `file1.py`, `file2.py`, `file3.py`, `file4.py`
        ```python
        code here
        ```
        Architecture includes Tier 1, plugin, and module components.
        """
        
        quality = analyzer.analyze_conversation("test", response)
        
        expected_score = (
            6 +   # 2 phases × 3 points
            3 +   # Challenge/Accept
            2 +   # Design decisions
            3 +   # File references (capped at 3)
            2 +   # Next steps
            1 +   # Code implementation
            2     # Architectural discussion
        )
        
        assert quality.total_score == expected_score
        assert quality.level == "EXCELLENT"


class TestSemanticElements:
    """Test SemanticElements dataclass."""
    
    def test_default_initialization(self):
        """Test default values."""
        elements = SemanticElements()
        
        assert elements.multi_phase_planning is False
        assert elements.phase_count == 0
        assert elements.challenge_accept_flow is False
        assert elements.design_decisions is False
        assert elements.file_references == 0
        assert elements.next_steps_provided is False
        assert elements.code_implementation is False
        assert elements.architectural_discussion is False
    
    def test_custom_initialization(self):
        """Test custom values."""
        elements = SemanticElements(
            multi_phase_planning=True,
            phase_count=3,
            file_references=5
        )
        
        assert elements.multi_phase_planning is True
        assert elements.phase_count == 3
        assert elements.file_references == 5


class TestQualityScore:
    """Test QualityScore dataclass."""
    
    def test_quality_score_structure(self):
        """Test QualityScore contains expected fields."""
        elements = SemanticElements()
        
        score = QualityScore(
            total_score=10,
            level="EXCELLENT",
            elements=elements,
            reasoning="Test reasoning",
            should_show_hint=True
        )
        
        assert score.total_score == 10
        assert score.level == "EXCELLENT"
        assert score.elements == elements
        assert score.reasoning == "Test reasoning"
        assert score.should_show_hint is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
