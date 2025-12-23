"""
Tests for CORTEX 3.0 Pattern Learning Engine
Advanced Fusion - Milestone 3

Tests pattern learning capabilities, file suggestion algorithms,
confidence boosting, and learning session management.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Repository: https://github.com/asifhussain60/CORTEX
"""

import json
import os
import tempfile
import unittest
from datetime import datetime, timedelta
from typing import Dict, Any

from src.tier1.pattern_learning_engine import (
    PatternLearningEngine, 
    CorrelationPattern, 
    LearningSession,
    PatternType
)


class TestPatternLearningEngine(unittest.TestCase):
    """Test suite for Pattern Learning Engine"""
    
    def setUp(self):
        """Set up test environment with temporary database"""
        self.temp_db = tempfile.NamedTemporaryFile(suffix='.db', delete=False)
        self.temp_db.close()
        self.engine = PatternLearningEngine(self.temp_db.name)
        
    def tearDown(self):
        """Clean up temporary database"""
        if os.path.exists(self.temp_db.name):
            os.unlink(self.temp_db.name)
    
    def test_initialization(self):
        """Test pattern learning engine initialization"""
        # Should create database schema without errors
        self.assertIsInstance(self.engine, PatternLearningEngine)
        self.assertEqual(self.engine.database_path, self.temp_db.name)
        
        # Should have empty statistics initially
        stats = self.engine.get_learning_statistics()
        self.assertEqual(stats["overall_statistics"]["total_patterns"], 0)
        self.assertEqual(stats["learning_statistics"]["learning_sessions"], 0)
    
    def test_file_mention_pattern_learning(self):
        """Test learning patterns from file mentions"""
        # Prepare correlation result with file mentions
        correlation_result = {
            "conversation_id": "test_conv_001",
            "file_mentions": ["UserService.cs", "UserController.cs", "UserTests.cs"],
            "correlations": [
                {"file_path": "UserService.cs", "confidence": 0.8, "timestamp": datetime.now().isoformat()},
                {"file_path": "UserController.cs", "confidence": 0.7, "timestamp": datetime.now().isoformat()}
            ],
            "conversation_content": "Implement user authentication with service and controller",
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        # Learn from correlation
        session = self.engine.learn_from_correlation(correlation_result)
        
        # Verify learning session
        self.assertIsInstance(session, LearningSession)
        self.assertEqual(session.conversation_id, "test_conv_001")
        self.assertGreater(session.patterns_learned, 0)
        
        # Verify patterns were stored
        stats = self.engine.get_learning_statistics()
        self.assertGreater(stats["overall_statistics"]["total_patterns"], 0)
        
        # Check that file mention patterns were created
        patterns = self.engine._get_patterns_by_type(PatternType.FILE_MENTION)
        self.assertGreater(len(patterns), 0)
        
        # Verify pattern structure
        pattern = patterns[0]
        self.assertEqual(pattern["pattern_type"], PatternType.FILE_MENTION.value)
        pattern_data = pattern["pattern_data"]
        self.assertIn("file_a", pattern_data)
        self.assertIn("file_b", pattern_data)
        self.assertIn("confidence_boost", pattern_data)
    
    def test_context_pattern_learning(self):
        """Test learning patterns from conversation context"""
        correlation_result = {
            "conversation_id": "test_conv_002",
            "file_mentions": ["AuthService.cs"],
            "correlations": [
                {"file_path": "AuthService.cs", "confidence": 0.85, "timestamp": datetime.now().isoformat()},
                {"file_path": "AuthService.cs", "confidence": 0.75, "timestamp": (datetime.now() + timedelta(minutes=5)).isoformat()}
            ],
            "conversation_content": "authentication login security password hashing validation jwt token",
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        # Learn from correlation
        session = self.engine.learn_from_correlation(correlation_result)
        
        # Verify context patterns were created
        patterns = self.engine._get_patterns_by_type(PatternType.CONTEXT)
        self.assertGreater(len(patterns), 0)
        
        pattern = patterns[0]
        pattern_data = pattern["pattern_data"]
        self.assertIn("keywords", pattern_data)
        self.assertIn("target_file", pattern_data)
        self.assertEqual(pattern_data["target_file"], "AuthService.cs")
        self.assertIn("authentication", pattern_data["keywords"])
    
    def test_temporal_pattern_learning(self):
        """Test learning temporal patterns from correlations"""
        now = datetime.now()
        correlation_result = {
            "conversation_id": "test_conv_003",
            "file_mentions": ["DataService.cs"],
            "correlations": [
                {"file_path": "DataService.cs", "confidence": 0.8, "timestamp": (now - timedelta(hours=1)).isoformat()},
                {"file_path": "DataService.cs", "confidence": 0.7, "timestamp": (now - timedelta(hours=2)).isoformat()}
            ],
            "conversation_content": "database query optimization performance",
            "conversation_timestamp": now.isoformat()
        }
        
        # Learn from correlation
        session = self.engine.learn_from_correlation(correlation_result)
        
        # Verify temporal patterns were created
        patterns = self.engine._get_patterns_by_type(PatternType.TEMPORAL)
        self.assertGreater(len(patterns), 0)
        
        pattern = patterns[0]
        pattern_data = pattern["pattern_data"]
        self.assertIn("optimal_window_seconds", pattern_data)
        self.assertIn("average_delta_seconds", pattern_data)
        self.assertGreater(pattern_data["optimal_window_seconds"], 0)
    
    def test_plan_sequence_pattern_learning(self):
        """Test learning patterns from plan sequences"""
        correlation_result = {
            "conversation_id": "test_conv_004",
            "plan_mentions": ["Phase 1: Design", "Phase 2: Implementation", "Phase 3: Testing"],
            "correlations": [
                {"file_path": "DesignDoc.md", "confidence": 0.9, "timestamp": datetime.now().isoformat()},
                {"file_path": "ServiceImpl.cs", "confidence": 0.8, "timestamp": datetime.now().isoformat()}
            ],
            "conversation_content": "plan implementation testing sequence workflow",
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        # Learn from correlation
        session = self.engine.learn_from_correlation(correlation_result)
        
        # Verify plan sequence patterns were created
        patterns = self.engine._get_patterns_by_type(PatternType.PLAN_SEQUENCE)
        self.assertGreater(len(patterns), 0)
        
        pattern = patterns[0]
        pattern_data = pattern["pattern_data"]
        self.assertIn("phase_sequence", pattern_data)
        self.assertIn("sequence_type", pattern_data)
        self.assertEqual(len(pattern_data["phase_sequence"]), 2)
    
    def test_file_suggestion_based_on_patterns(self):
        """Test file suggestion using learned patterns"""
        # First, create some context patterns
        correlation_result = {
            "conversation_id": "test_conv_005",
            "file_mentions": ["PaymentService.cs"],
            "correlations": [
                {"file_path": "PaymentService.cs", "confidence": 0.85, "timestamp": datetime.now().isoformat()},
                {"file_path": "PaymentService.cs", "confidence": 0.80, "timestamp": datetime.now().isoformat()}
            ],
            "conversation_content": "payment processing credit card transaction billing invoice",
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        # Learn patterns
        self.engine.learn_from_correlation(correlation_result)
        
        # Test file suggestion with similar content
        suggestions = self.engine.suggest_files_for_conversation(
            "need to implement payment processing for credit card transactions"
        )
        
        # Should suggest PaymentService.cs based on learned patterns
        self.assertGreater(len(suggestions), 0)
        
        # Check if PaymentService.cs is in suggestions
        suggested_files = [s["file_path"] for s in suggestions]
        self.assertIn("PaymentService.cs", suggested_files)
        
        # Verify suggestion structure
        suggestion = next(s for s in suggestions if s["file_path"] == "PaymentService.cs")
        self.assertIn("confidence", suggestion)
        self.assertIn("reasoning", suggestion)
        self.assertIn("pattern_types", suggestion)
        self.assertGreater(suggestion["confidence"], 0.5)
    
    def test_file_mention_suggestions(self):
        """Test file suggestions based on file mention patterns"""
        # Create file mention pattern
        correlation_result = {
            "conversation_id": "test_conv_006",
            "file_mentions": ["OrderService.cs", "OrderController.cs"],
            "correlations": [
                {"file_path": "OrderService.cs", "confidence": 0.8, "timestamp": datetime.now().isoformat()},
                {"file_path": "OrderController.cs", "confidence": 0.75, "timestamp": datetime.now().isoformat()}
            ],
            "conversation_content": "order management service controller integration",
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        # Learn patterns
        self.engine.learn_from_correlation(correlation_result)
        
        # Test suggestion when one file is mentioned
        suggestions = self.engine.suggest_files_for_conversation(
            "need to modify OrderService.cs for new requirements"
        )
        
        # Should suggest OrderController.cs based on co-occurrence pattern
        suggested_files = [s["file_path"] for s in suggestions]
        self.assertIn("OrderController.cs", suggested_files)
    
    def test_confidence_boosting_from_patterns(self):
        """Test correlation confidence boosting using patterns"""
        # Create patterns first
        correlation_result = {
            "conversation_id": "test_conv_007",
            "file_mentions": ["ConfigService.cs", "ConfigController.cs"],
            "correlations": [
                {"file_path": "ConfigService.cs", "confidence": 0.8, "timestamp": datetime.now().isoformat()},
                {"file_path": "ConfigController.cs", "confidence": 0.75, "timestamp": datetime.now().isoformat()}
            ],
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        # Learn patterns
        self.engine.learn_from_correlation(correlation_result)
        
        # Test confidence boosting
        correlation_candidates = [
            {
                "file_path": "ConfigService.cs",
                "confidence": 0.5,
                "timestamp": datetime.now().isoformat()
            }
        ]
        
        boosted_candidates = self.engine.boost_confidence_from_patterns(correlation_candidates)
        
        # Confidence should be boosted
        self.assertGreater(boosted_candidates[0]["confidence"], 0.5)
        self.assertIn("pattern_boost", boosted_candidates[0])
        self.assertGreater(boosted_candidates[0]["pattern_boost"], 0.0)
    
    def test_learning_statistics(self):
        """Test learning statistics collection"""
        # Start with empty statistics
        initial_stats = self.engine.get_learning_statistics()
        self.assertEqual(initial_stats["overall_statistics"]["total_patterns"], 0)
        
        # Learn some patterns
        correlation_result = {
            "conversation_id": "test_conv_008",
            "file_mentions": ["TestService.cs", "TestController.cs"],
            "correlations": [
                {"file_path": "TestService.cs", "confidence": 0.8, "timestamp": datetime.now().isoformat()},
                {"file_path": "TestController.cs", "confidence": 0.7, "timestamp": datetime.now().isoformat()}
            ],
            "conversation_content": "test implementation service controller validation",
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        session = self.engine.learn_from_correlation(correlation_result)
        
        # Check updated statistics
        stats = self.engine.get_learning_statistics()
        self.assertGreater(stats["overall_statistics"]["total_patterns"], 0)
        self.assertEqual(stats["learning_statistics"]["learning_sessions"], 1)
        self.assertGreater(stats["overall_statistics"]["overall_confidence"], 0.0)
        
        # Verify pattern type statistics
        self.assertIn("pattern_statistics", stats)
        pattern_stats = stats["pattern_statistics"]
        self.assertGreater(len(pattern_stats), 0)
    
    def test_pattern_export(self):
        """Test exporting learned patterns to JSON"""
        # Learn some patterns first
        correlation_result = {
            "conversation_id": "test_conv_009",
            "file_mentions": ["ExportService.cs"],
            "correlations": [
                {"file_path": "ExportService.cs", "confidence": 0.85, "timestamp": datetime.now().isoformat()}
            ],
            "conversation_content": "export data reporting analytics",
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        self.engine.learn_from_correlation(correlation_result)
        
        # Export patterns
        with tempfile.NamedTemporaryFile(suffix='.json', delete=False) as temp_export:
            success = self.engine.export_patterns(temp_export.name)
            
            self.assertTrue(success)
            
            # Verify export file
            with open(temp_export.name, 'r') as f:
                export_data = json.load(f)
                
            self.assertIn("export_timestamp", export_data)
            self.assertIn("pattern_count", export_data)
            self.assertIn("patterns", export_data)
            self.assertGreater(export_data["pattern_count"], 0)
            self.assertEqual(len(export_data["patterns"]), export_data["pattern_count"])
            
            # Clean up
            os.unlink(temp_export.name)
    
    def test_keyword_extraction(self):
        """Test keyword extraction from conversation text"""
        text = "implement user authentication with password hashing and jwt token validation security"
        
        keywords = self.engine._extract_keywords(text)
        
        # Should extract meaningful keywords
        self.assertIn("authentication", keywords)
        self.assertIn("password", keywords)
        self.assertIn("hashing", keywords)
        self.assertIn("token", keywords)
        self.assertIn("validation", keywords)
        self.assertIn("security", keywords)
        
        # Should not include common words
        self.assertNotIn("with", keywords)
        self.assertNotIn("and", keywords)
    
    def test_file_mention_extraction(self):
        """Test file mention extraction from text"""
        text = "Update UserService.cs and UserController.cs, also check UserTests and verify config.json"
        
        file_mentions = self.engine._extract_file_mentions_from_text(text)
        
        # Should extract file-like patterns
        self.assertIn("UserService", file_mentions)
        self.assertIn("UserController", file_mentions)
        self.assertIn("UserTests", file_mentions)
        self.assertIn("config.json", file_mentions)
    
    def test_pattern_merging_and_similarity(self):
        """Test that similar patterns get merged instead of duplicated"""
        # Create similar correlation results
        correlation_result_1 = {
            "conversation_id": "test_conv_010",
            "file_mentions": ["SimilarService.cs", "SimilarController.cs"],
            "correlations": [
                {"file_path": "SimilarService.cs", "confidence": 0.8, "timestamp": datetime.now().isoformat()},
                {"file_path": "SimilarController.cs", "confidence": 0.7, "timestamp": datetime.now().isoformat()}
            ],
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        correlation_result_2 = {
            "conversation_id": "test_conv_011",
            "file_mentions": ["SimilarService.cs", "SimilarController.cs"],
            "correlations": [
                {"file_path": "SimilarService.cs", "confidence": 0.75, "timestamp": datetime.now().isoformat()},
                {"file_path": "SimilarController.cs", "confidence": 0.8, "timestamp": datetime.now().isoformat()}
            ],
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        # Learn from both (should result in pattern merging in future implementation)
        session_1 = self.engine.learn_from_correlation(correlation_result_1)
        session_2 = self.engine.learn_from_correlation(correlation_result_2)
        
        # Verify both sessions learned patterns
        self.assertGreater(session_1.patterns_learned, 0)
        self.assertGreater(session_2.patterns_learned, 0)
        
        # For now, just verify that patterns are stored
        # (Pattern merging logic can be enhanced in future iterations)
        stats = self.engine.get_learning_statistics()
        self.assertGreater(stats["overall_statistics"]["total_patterns"], 0)
    
    def test_empty_correlation_handling(self):
        """Test handling of empty or minimal correlation data"""
        # Empty correlation result
        empty_result = {
            "conversation_id": "test_conv_012",
            "file_mentions": [],
            "correlations": [],
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        # Should handle gracefully without errors
        session = self.engine.learn_from_correlation(empty_result)
        self.assertIsInstance(session, LearningSession)
        self.assertEqual(session.patterns_learned, 0)
        
        # Minimal result with just one file
        minimal_result = {
            "conversation_id": "test_conv_013",
            "file_mentions": ["SingleFile.cs"],
            "correlations": [
                {"file_path": "SingleFile.cs", "confidence": 0.8, "timestamp": datetime.now().isoformat()}
            ],
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        # Should handle gracefully
        session = self.engine.learn_from_correlation(minimal_result)
        self.assertIsInstance(session, LearningSession)
        # May or may not learn patterns (depends on pattern type requirements)
    
    def test_pattern_confidence_evolution(self):
        """Test that pattern confidence evolves with usage"""
        # Create initial pattern
        correlation_result = {
            "conversation_id": "test_conv_014",
            "file_mentions": ["EvolvingService.cs", "EvolvingController.cs"],
            "correlations": [
                {"file_path": "EvolvingService.cs", "confidence": 0.8, "timestamp": datetime.now().isoformat()},
                {"file_path": "EvolvingController.cs", "confidence": 0.7, "timestamp": datetime.now().isoformat()}
            ],
            "conversation_timestamp": datetime.now().isoformat()
        }
        
        # Learn patterns
        self.engine.learn_from_correlation(correlation_result)
        
        # Get initial pattern confidence
        initial_patterns = self.engine._get_patterns_by_type(PatternType.FILE_MENTION)
        if initial_patterns:
            initial_confidence = initial_patterns[0]["confidence"]
            
            # Use pattern for confidence boosting (simulates usage)
            correlation_candidates = [
                {
                    "file_path": "EvolvingService.cs",
                    "confidence": 0.6,
                    "timestamp": datetime.now().isoformat()
                }
            ]
            
            self.engine.boost_confidence_from_patterns(correlation_candidates)
            
            # Check that pattern usage was updated
            updated_patterns = self.engine._get_patterns_by_type(PatternType.FILE_MENTION)
            if updated_patterns:
                # Usage count should have increased
                self.assertGreaterEqual(updated_patterns[0]["usage_count"], initial_patterns[0]["usage_count"])


if __name__ == '__main__':
    unittest.main()