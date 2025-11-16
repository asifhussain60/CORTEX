"""
Tests for Smart Hint Generator

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
from src.operations.modules.conversations.smart_hint_generator import (
    SmartHintGenerator,
    SmartHint,
    create_hint_generator
)
from src.tier1.conversation_quality import (
    QualityScore,
    SemanticElements
)


class TestSmartHintGenerator:
    """Test suite for SmartHintGenerator."""
    
    def test_generator_initialization(self):
        """Test generator initializes with correct defaults."""
        generator = SmartHintGenerator()
        
        assert generator.quality_threshold == "GOOD"
        assert generator.enable_hints is True
    
    def test_generator_custom_config(self):
        """Test generator with custom configuration."""
        generator = SmartHintGenerator(
            quality_threshold="EXCELLENT",
            enable_hints=False
        )
        
        assert generator.quality_threshold == "EXCELLENT"
        assert generator.enable_hints is False
    
    def test_generate_hint_for_excellent_quality(self):
        """Test hint generation for EXCELLENT quality."""
        generator = SmartHintGenerator()
        
        quality = QualityScore(
            total_score=22,
            level="EXCELLENT",
            elements=SemanticElements(
                multi_phase_planning=True,
                phase_count=5,
                challenge_accept_flow=True,
                design_decisions=True,
                file_references=3,
                next_steps_provided=True
            ),
            reasoning="Multi-phase planning, challenge/accept flow",
            should_show_hint=True
        )
        
        hint = generator.generate_hint(quality)
        
        assert hint.should_display is True
        assert "💡 CORTEX Learning Opportunity" in hint.content
        assert "Multi-phase planning (5 phases)" in hint.content
        assert "/CORTEX Capture this conversation" in hint.content
        assert hint.quality_level == "EXCELLENT"
    
    def test_generate_hint_for_good_quality(self):
        """Test hint generation for GOOD quality."""
        generator = SmartHintGenerator()
        
        quality = QualityScore(
            total_score=14,
            level="GOOD",
            elements=SemanticElements(
                multi_phase_planning=True,
                phase_count=3,
                code_implementation=True,
                file_references=2
            ),
            reasoning="Multi-phase planning, code implementation",
            should_show_hint=True
        )
        
        hint = generator.generate_hint(quality)
        
        assert hint.should_display is True
        assert "strategic value" in hint.content.lower()
        assert "Multi-phase planning (3 phases)" in hint.content
        assert "Code implementation included" in hint.content
    
    def test_no_hint_for_low_quality(self):
        """Test no hint for LOW quality conversations."""
        generator = SmartHintGenerator()
        
        quality = QualityScore(
            total_score=1,
            level="LOW",
            elements=SemanticElements(),
            reasoning="Minimal strategic content",
            should_show_hint=False
        )
        
        hint = generator.generate_hint(quality)
        
        assert hint.should_display is False
        assert hint.content == ""
    
    def test_no_hint_for_fair_quality_with_good_threshold(self):
        """Test no hint for FAIR when threshold is GOOD."""
        generator = SmartHintGenerator(quality_threshold="GOOD")
        
        quality = QualityScore(
            total_score=5,
            level="FAIR",
            elements=SemanticElements(file_references=2),
            reasoning="Some file references",
            should_show_hint=False
        )
        
        hint = generator.generate_hint(quality)
        
        assert hint.should_display is False
    
    def test_hint_shown_only_once(self):
        """Test hint not shown if already shown in session."""
        generator = SmartHintGenerator()
        
        quality = QualityScore(
            total_score=14,
            level="GOOD",
            elements=SemanticElements(multi_phase_planning=True),
            reasoning="Multi-phase planning",
            should_show_hint=True
        )
        
        # First call: should show hint
        hint1 = generator.generate_hint(quality, hint_already_shown=False)
        assert hint1.should_display is True
        
        # Second call: hint already shown
        hint2 = generator.generate_hint(quality, hint_already_shown=True)
        assert hint2.should_display is False
    
    def test_hints_disabled_globally(self):
        """Test hints disabled when master switch off."""
        generator = SmartHintGenerator(enable_hints=False)
        
        quality = QualityScore(
            total_score=22,
            level="EXCELLENT",
            elements=SemanticElements(multi_phase_planning=True),
            reasoning="Excellent quality",
            should_show_hint=True
        )
        
        hint = generator.generate_hint(quality)
        
        assert hint.should_display is False
    
    def test_score_mapping_excellent(self):
        """Test internal score mapping for EXCELLENT."""
        generator = SmartHintGenerator()
        
        # Test EXCELLENT range (19+)
        assert generator._map_score_to_ten(19) == 9
        assert generator._map_score_to_ten(25) == 10
        assert generator._map_score_to_ten(30) == 10
    
    def test_score_mapping_good(self):
        """Test internal score mapping for GOOD."""
        generator = SmartHintGenerator()
        
        # Test GOOD range (10-18)
        assert generator._map_score_to_ten(10) == 7
        assert generator._map_score_to_ten(13) == 7
        assert generator._map_score_to_ten(14) == 8
        assert generator._map_score_to_ten(18) == 8
    
    def test_score_mapping_fair(self):
        """Test internal score mapping for FAIR."""
        generator = SmartHintGenerator()
        
        # Test FAIR range (2-9)
        assert generator._map_score_to_ten(2) == 4
        assert generator._map_score_to_ten(5) == 5
        assert generator._map_score_to_ten(8) == 6
        assert generator._map_score_to_ten(9) == 6
    
    def test_score_mapping_low(self):
        """Test internal score mapping for LOW."""
        generator = SmartHintGenerator()
        
        # Test LOW range (0-1)
        assert generator._map_score_to_ten(0) == 1
        assert generator._map_score_to_ten(1) == 2
    
    def test_value_items_generation(self):
        """Test strategic value items generation."""
        generator = SmartHintGenerator()
        
        elements = SemanticElements(
            multi_phase_planning=True,
            phase_count=4,
            challenge_accept_flow=True,
            design_decisions=True,
            code_implementation=True,
            architectural_discussion=True,
            file_references=2,
            next_steps_provided=True
        )
        
        quality = QualityScore(
            total_score=20,
            level="EXCELLENT",
            elements=elements,
            reasoning="All elements present",
            should_show_hint=True
        )
        
        value_items = generator._build_value_items(quality)
        
        assert "Multi-phase planning (4 phases)" in value_items
        assert "Challenge/Accept reasoning documented" in value_items
        assert "Design decisions and trade-offs discussed" in value_items
        assert "Code implementation included" in value_items
        assert "Architectural patterns discussed" in value_items
        assert "2 file reference(s)" in value_items
        assert "Clear next steps provided" in value_items
    
    def test_value_items_minimal_content(self):
        """Test value items with minimal content."""
        generator = SmartHintGenerator()
        
        elements = SemanticElements()
        
        quality = QualityScore(
            total_score=5,
            level="FAIR",
            elements=elements,
            reasoning="Minimal content",
            should_show_hint=True
        )
        
        value_items = generator._build_value_items(quality)
        
        # Should have generic message when no specific items
        assert "Strategic conversation with learning value" in value_items
    
    def test_dismissal_response(self):
        """Test dismissal response generation."""
        generator = SmartHintGenerator()
        
        response = generator.generate_dismissal_response()
        
        assert "won't suggest saving this conversation again" in response
        assert "/CORTEX Capture this conversation" in response
    
    def test_hint_format_structure(self):
        """Test hint has correct markdown structure."""
        generator = SmartHintGenerator()
        
        quality = QualityScore(
            total_score=14,
            level="GOOD",
            elements=SemanticElements(multi_phase_planning=True, phase_count=3),
            reasoning="Good quality",
            should_show_hint=True
        )
        
        hint = generator.generate_hint(quality)
        
        # Check structure
        assert hint.content.startswith("---")
        assert hint.content.endswith("---")
        assert "> ###" in hint.content  # Blockquote with heading
        assert "**Quality Score:" in hint.content
        assert "**Two-step capture:**" in hint.content
        assert "Say \"skip\"" in hint.content
    
    def test_factory_function_default(self):
        """Test factory function with defaults."""
        generator = create_hint_generator()
        
        assert generator.quality_threshold == "GOOD"
        assert generator.enable_hints is True
    
    def test_factory_function_custom_config(self):
        """Test factory function with custom config."""
        config = {
            'quality_threshold': 'EXCELLENT',
            'enable_hints': False
        }
        
        generator = create_hint_generator(config)
        
        assert generator.quality_threshold == "EXCELLENT"
        assert generator.enable_hints is False
    
    def test_hint_includes_two_step_workflow(self):
        """Test hint includes two-step capture workflow."""
        generator = SmartHintGenerator()
        
        quality = QualityScore(
            total_score=14,
            level="GOOD",
            elements=SemanticElements(),
            reasoning="Good quality",
            should_show_hint=True
        )
        
        hint = generator.generate_hint(quality)
        
        assert '1. Say "/CORTEX Capture this conversation"' in hint.content
        assert '2. Paste conversation into file and save' in hint.content
        assert '3. Say "/CORTEX Import this conversation"' in hint.content
    
    def test_excellent_threshold_filters_good(self):
        """Test EXCELLENT threshold doesn't show hints for GOOD quality."""
        generator = SmartHintGenerator(quality_threshold="EXCELLENT")
        
        quality = QualityScore(
            total_score=14,
            level="GOOD",
            elements=SemanticElements(),
            reasoning="Good but not excellent",
            should_show_hint=False  # Analyzer respects threshold
        )
        
        hint = generator.generate_hint(quality)
        
        assert hint.should_display is False
