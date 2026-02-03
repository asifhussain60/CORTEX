"""
Unit tests for NextStepGenerator.

Tests the intelligent next-step suggestion system that generates
3-5 numbered options based on user context and knowledge level.

Authority: AC-EDUCATIONAL-INTERACTION-001, PHASE-22-ASK-MODE-SYSTEM.yaml
Rules: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import unittest
from typing import List
from dataclasses import dataclass

from cortex.brain.education.next_step_generator import (
    NextStepGenerator,
    NextStepOption,
    NextStepContext,
    KnowledgeLevel,
    StepType,
)


class TestNextStepGenerator(unittest.TestCase):
    """Test suite for NextStepGenerator."""

    def setUp(self):
        """Set up test fixtures."""
        self.generator = NextStepGenerator()

    def test_initialization_succeeds(self):
        """Test NextStepGenerator initializes correctly."""
        self.assertIsNotNone(self.generator)
        self.assertIsInstance(self.generator, NextStepGenerator)

    def test_generates_minimum_three_options(self):
        """Test that at least 3 options are always generated."""
        context = NextStepContext(
            current_topic="MasterOrchestrator",
            knowledge_level=KnowledgeLevel.BEGINNER,
            user_query="What is MasterOrchestrator?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        self.assertGreaterEqual(len(options), 3)
        self.assertLessEqual(len(options), 5)

    def test_generates_maximum_five_options(self):
        """Test that no more than 5 options are generated."""
        context = NextStepContext(
            current_topic="CORTEX Architecture",
            knowledge_level=KnowledgeLevel.ADVANCED,
            user_query="Explain the orchestrator hierarchy",
            conversation_history=["previous question"]
        )
        
        options = self.generator.generate_next_steps(context)
        
        self.assertLessEqual(len(options), 5)

    def test_first_option_is_always_deeper_dive(self):
        """Test that option #1 is always a deeper dive on current topic."""
        context = NextStepContext(
            current_topic="TDDOrchestrator",
            knowledge_level=KnowledgeLevel.INTERMEDIATE,
            user_query="How does TDD work?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        self.assertEqual(options[0].step_type, StepType.DEEPER_DIVE)
        self.assertIn("TDDOrchestrator", options[0].title)

    def test_includes_related_concepts(self):
        """Test that related concepts are suggested."""
        context = NextStepContext(
            current_topic="IntentRouter",
            knowledge_level=KnowledgeLevel.BEGINNER,
            user_query="What is IntentRouter?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        # Should have at least one RELATED_CONCEPT option
        related_options = [opt for opt in options if opt.step_type == StepType.RELATED_CONCEPT]
        self.assertGreater(len(related_options), 0)

    def test_includes_practical_example(self):
        """Test that a practical example is offered."""
        context = NextStepContext(
            current_topic="MCP Tools",
            knowledge_level=KnowledgeLevel.INTERMEDIATE,
            user_query="How do MCP tools work?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        # Should have at least one PRACTICAL_EXAMPLE option
        example_options = [opt for opt in options if opt.step_type == StepType.PRACTICAL_EXAMPLE]
        self.assertGreater(len(example_options), 0)

    def test_adapts_to_beginner_level(self):
        """Test that suggestions adapt to beginner knowledge level."""
        context = NextStepContext(
            current_topic="Orchestrators",
            knowledge_level=KnowledgeLevel.BEGINNER,
            user_query="What are orchestrators?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        # Beginner options should avoid advanced concepts
        for option in options:
            self.assertNotIn("architecture pattern", option.title.lower())
            self.assertNotIn("design pattern", option.title.lower())

    def test_adapts_to_intermediate_level(self):
        """Test that suggestions adapt to intermediate knowledge level."""
        context = NextStepContext(
            current_topic="LENSOrchestrator",
            knowledge_level=KnowledgeLevel.INTERMEDIATE,
            user_query="How does LENS work with orchestrators?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        # Intermediate should have integration/architecture options
        titles = " ".join([opt.title for opt in options])
        self.assertTrue(
            any(keyword in titles.lower() for keyword in ["integration", "architecture", "workflow"])
        )

    def test_adapts_to_advanced_level(self):
        """Test that suggestions adapt to advanced knowledge level."""
        context = NextStepContext(
            current_topic="EnforcementOrchestrator",
            knowledge_level=KnowledgeLevel.ADVANCED,
            user_query="How does governance enforcement work?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        # Advanced should offer extension/customization options
        has_advanced_option = any(
            opt.step_type in [StepType.ADVANCED_EXTENSION, StepType.CUSTOMIZATION]
            for opt in options
        )
        self.assertTrue(has_advanced_option)

    def test_generates_unique_options(self):
        """Test that all generated options are unique."""
        context = NextStepContext(
            current_topic="MasterOrchestrator",
            knowledge_level=KnowledgeLevel.BEGINNER,
            user_query="What is MasterOrchestrator?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        titles = [opt.title for opt in options]
        self.assertEqual(len(titles), len(set(titles)))  # No duplicates

    def test_options_have_descriptions(self):
        """Test that all options have non-empty descriptions."""
        context = NextStepContext(
            current_topic="ChallengeEngine",
            knowledge_level=KnowledgeLevel.INTERMEDIATE,
            user_query="How does challenge generation work?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        for option in options:
            self.assertIsNotNone(option.description)
            self.assertGreater(len(option.description), 20)

    def test_numbered_options_display_correctly(self):
        """Test that options are numbered 1-5."""
        context = NextStepContext(
            current_topic="Wiring",
            knowledge_level=KnowledgeLevel.BEGINNER,
            user_query="What is wiring?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        for i, option in enumerate(options, start=1):
            self.assertEqual(option.number, i)

    def test_context_aware_suggestions(self):
        """Test that suggestions consider conversation history."""
        context = NextStepContext(
            current_topic="MCP Tools",
            knowledge_level=KnowledgeLevel.BEGINNER,
            user_query="How do I use cortex_ask?",
            conversation_history=[
                "What are MCP tools?",
                "Show me available tools"
            ]
        )
        
        options = self.generator.generate_next_steps(context)
        
        # Should not repeat topics already covered
        for option in options:
            self.assertNotIn("What are MCP tools", option.title)

    def test_handles_orchestrator_topic(self):
        """Test handling of orchestrator-specific topics."""
        context = NextStepContext(
            current_topic="TDDOrchestrator",
            knowledge_level=KnowledgeLevel.INTERMEDIATE,
            user_query="How does TDD enforcement work?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        # Should include related orchestrators
        titles = " ".join([opt.title for opt in options])
        self.assertTrue(
            any(keyword in titles for keyword in ["Orchestrator", "Enforcement", "Wiring"])
        )

    def test_handles_mcp_tool_topic(self):
        """Test handling of MCP tool-specific topics."""
        context = NextStepContext(
            current_topic="cortex_ask",
            knowledge_level=KnowledgeLevel.BEGINNER,
            user_query="What does cortex_ask do?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        # Should include other MCP tools or usage examples
        has_related_tools = any(
            "tool" in opt.title.lower() or "cortex_" in opt.title.lower()
            for opt in options
        )
        self.assertTrue(has_related_tools)

    def test_handles_general_architecture_topic(self):
        """Test handling of general architecture topics."""
        context = NextStepContext(
            current_topic="CORTEX Architecture",
            knowledge_level=KnowledgeLevel.BEGINNER,
            user_query="How is CORTEX structured?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        # Should break down into components
        has_component_suggestion = any(
            "orchestrator" in opt.title.lower() or "brain" in opt.title.lower()
            for opt in options
        )
        self.assertTrue(has_component_suggestion)

    def test_provides_faq_option_for_common_topics(self):
        """Test that FAQ option is provided for common topics."""
        context = NextStepContext(
            current_topic="Getting Started",
            knowledge_level=KnowledgeLevel.BEGINNER,
            user_query="How do I start using CORTEX?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        # Should have FAQ or common questions option
        has_faq = any(
            opt.step_type == StepType.FAQ or "common" in opt.title.lower()
            for opt in options
        )
        self.assertTrue(has_faq)

    def test_formats_output_correctly(self):
        """Test that output formatting is correct for display."""
        context = NextStepContext(
            current_topic="Test Topic",
            knowledge_level=KnowledgeLevel.BEGINNER,
            user_query="Test query",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        formatted = self.generator.format_options(options)
        
        # Should have numbered list format
        self.assertIn("1.", formatted)
        self.assertIn("2.", formatted)
        self.assertIn("3.", formatted)

    def test_empty_conversation_history_handled(self):
        """Test that empty conversation history is handled gracefully."""
        context = NextStepContext(
            current_topic="MasterOrchestrator",
            knowledge_level=KnowledgeLevel.BEGINNER,
            user_query="What is this?",
            conversation_history=[]
        )
        
        options = self.generator.generate_next_steps(context)
        
        self.assertGreaterEqual(len(options), 3)


if __name__ == "__main__":
    unittest.main()
