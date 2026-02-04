"""
Unit tests for KnowledgeLevelDetector.

Tests the intelligent knowledge level classification system that detects
user expertise from queries and conversation history.

Authority: AC-EDUCATIONAL-INTERACTION-001, PHASE-22-ASK-MODE-SYSTEM.yaml
Rules: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
"""

import unittest
from typing import List

from cortex.brain.education.knowledge_level_detector import (
    KnowledgeLevelDetector,
    KnowledgeLevel,
    DetectionSignals,
)


class TestKnowledgeLevelDetector(unittest.TestCase):
    """Test suite for KnowledgeLevelDetector."""

    def setUp(self):
        """Set up test fixtures."""
        self.detector = KnowledgeLevelDetector()

    def test_initialization_succeeds(self):
        """Test KnowledgeLevelDetector initializes correctly."""
        self.assertIsNotNone(self.detector)
        self.assertIsInstance(self.detector, KnowledgeLevelDetector)

    def test_detects_beginner_from_general_question(self):
        """Test detection of beginner level from general questions."""
        level = self.detector.detect_level(
            query="What is CORTEX?",
            conversation_history=[]
        )
        self.assertEqual(level, KnowledgeLevel.BEGINNER)

    def test_detects_beginner_from_what_is_question(self):
        """Test 'what is' questions indicate beginner level."""
        level = self.detector.detect_level(
            query="What is an orchestrator?",
            conversation_history=[]
        )
        self.assertEqual(level, KnowledgeLevel.BEGINNER)

    def test_detects_intermediate_from_implementation_question(self):
        """Test questions about implementation indicate intermediate level."""
        level = self.detector.detect_level(
            query="How does the IntentRouter classify intents?",
            conversation_history=[]
        )
        self.assertEqual(level, KnowledgeLevel.INTERMEDIATE)

    def test_detects_intermediate_from_integration_question(self):
        """Test questions about integration indicate intermediate level."""
        level = self.detector.detect_level(
            query="How do I integrate my orchestrator with the wiring system?",
            conversation_history=[]
        )
        self.assertEqual(level, KnowledgeLevel.INTERMEDIATE)

    def test_detects_advanced_from_architecture_question(self):
        """Test architectural questions indicate advanced level."""
        level = self.detector.detect_level(
            query="What design patterns are used in the EnforcementOrchestrator?",
            conversation_history=[]
        )
        self.assertEqual(level, KnowledgeLevel.ADVANCED)

    def test_detects_advanced_from_extension_question(self):
        """Test questions about extending indicate advanced level."""
        level = self.detector.detect_level(
            query="Can I extend the IOrchestrator interface to add custom hooks?",
            conversation_history=[]
        )
        self.assertEqual(level, KnowledgeLevel.ADVANCED)

    def test_detects_advanced_from_optimization_question(self):
        """Test optimization questions indicate advanced level."""
        level = self.detector.detect_level(
            query="How can I optimize the AST analyzer for large codebases?",
            conversation_history=[]
        )
        self.assertEqual(level, KnowledgeLevel.ADVANCED)

    def test_considers_conversation_history(self):
        """Test that conversation history influences detection."""
        history = [
            "What is an orchestrator?",
            "How many orchestrators are there?",
            "What does MasterOrchestrator do?"
        ]
        
        # Even with beginner query, extensive history suggests higher level
        level = self.detector.detect_level(
            query="Tell me more about orchestrators",
            conversation_history=history
        )
        
        # Should be at least intermediate due to history
        self.assertIn(level, [KnowledgeLevel.INTERMEDIATE, KnowledgeLevel.ADVANCED])

    def test_detects_technical_terminology_usage(self):
        """Test that technical terms indicate higher knowledge level."""
        level = self.detector.detect_level(
            query="Does the AST analyzer use visitor pattern for traversal?",
            conversation_history=[]
        )
        self.assertIn(level, [KnowledgeLevel.INTERMEDIATE, KnowledgeLevel.ADVANCED])

    def test_empty_conversation_history_handled(self):
        """Test that empty history is handled gracefully."""
        level = self.detector.detect_level(
            query="How does CORTEX work?",
            conversation_history=[]
        )
        self.assertIsInstance(level, KnowledgeLevel)

    def test_detects_specific_component_questions(self):
        """Test specific component questions indicate at least intermediate."""
        level = self.detector.detect_level(
            query="How does LENSOrchestrator integrate with MasterOrchestrator?",
            conversation_history=[]
        )
        self.assertIn(level, [KnowledgeLevel.INTERMEDIATE, KnowledgeLevel.ADVANCED])

    def test_detects_implementation_details_interest(self):
        """Test interest in implementation details."""
        level = self.detector.detect_level(
            query="Show me the code for TDDOrchestrator's execute method",
            conversation_history=[]
        )
        self.assertIn(level, [KnowledgeLevel.INTERMEDIATE, KnowledgeLevel.ADVANCED])

    def test_detects_why_questions_as_deeper(self):
        """Test 'why' questions indicate deeper understanding."""
        level = self.detector.detect_level(
            query="Why does CORTEX use TDD enforcement at the orchestrator level?",
            conversation_history=[]
        )
        self.assertIn(level, [KnowledgeLevel.INTERMEDIATE, KnowledgeLevel.ADVANCED])

    def test_provides_detection_signals(self):
        """Test that detection signals are provided."""
        signals = self.detector.get_detection_signals(
            query="What is MasterOrchestrator?",
            conversation_history=[]
        )
        
        self.assertIsInstance(signals, DetectionSignals)
        self.assertIsNotNone(signals.query_complexity)
        self.assertIsNotNone(signals.technical_depth)

    def test_detects_troubleshooting_questions(self):
        """Test troubleshooting questions indicate intermediate level."""
        level = self.detector.detect_level(
            query="Why is my orchestrator not being registered in wiring.yaml?",
            conversation_history=[]
        )
        self.assertEqual(level, KnowledgeLevel.INTERMEDIATE)

    def test_detects_comparison_questions(self):
        """Test comparison questions indicate intermediate+ level."""
        level = self.detector.detect_level(
            query="What's the difference between IntentRouter and LENSOrchestrator?",
            conversation_history=[]
        )
        self.assertIn(level, [KnowledgeLevel.INTERMEDIATE, KnowledgeLevel.ADVANCED])

    def test_detects_best_practices_questions(self):
        """Test best practices questions indicate advanced level."""
        level = self.detector.detect_level(
            query="What are the best practices for creating custom orchestrators?",
            conversation_history=[]
        )
        self.assertEqual(level, KnowledgeLevel.ADVANCED)

    def test_confidence_score_provided(self):
        """Test that confidence score is provided."""
        signals = self.detector.get_detection_signals(
            query="What is CORTEX?",
            conversation_history=[]
        )
        
        self.assertIsNotNone(signals.confidence)
        self.assertGreaterEqual(signals.confidence, 0.0)
        self.assertLessEqual(signals.confidence, 1.0)


if __name__ == "__main__":
    unittest.main()
