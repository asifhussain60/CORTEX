"""
Test Suite for Smart Recommendations API
CORTEX 3.0 - Advanced Fusion Features

Comprehensive testing of intelligent file prediction service with pattern-based
recommendations, context analysis, and user feedback integration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Version: 3.0.0
"""

import unittest
import tempfile
import os
import sqlite3
import json
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Import the classes to test
from src.tier1.smart_recommendations import (
    SmartRecommendations, FileRecommendation, RecommendationContext, 
    RecommendationFeedback
)


class TestSmartRecommendations(unittest.TestCase):
    """Test suite for Smart Recommendations API"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.test_db = tempfile.NamedTemporaryFile(delete=False)
        self.test_db.close()
        
        # Mock pattern engine
        self.mock_pattern_engine = Mock()
        self.mock_pattern_engine.get_file_correlations.return_value = [
            {'related_file': 'test_related.py', 'confidence': 0.85},
            {'related_file': 'another_file.py', 'confidence': 0.65}
        ]
        
        self.recommendations = SmartRecommendations(
            db_path=self.test_db.name,
            pattern_engine=self.mock_pattern_engine
        )
        
        # Sample data
        self.sample_context = RecommendationContext(
            current_conversation="Let's implement user authentication with JWT tokens",
            user_intent="implementation",
            mentioned_files=["auth_service.py", "user_model.py"],
            development_phase="implementation",
            keywords=["authentication", "JWT", "user"],
            conversation_id="conv_test_123",
            timestamp=datetime.now()
        )
    
    def tearDown(self):
        """Clean up test fixtures"""
        try:
            os.unlink(self.test_db.name)
        except OSError:
            pass
    
    def test_database_initialization(self):
        """Test that database tables are created correctly"""
        with sqlite3.connect(self.test_db.name) as conn:
            cursor = conn.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            expected_tables = [
                'file_recommendations',
                'recommendation_feedback', 
                'file_access_history',
                'recommendation_patterns'
            ]
            
            for table in expected_tables:
                self.assertIn(table, tables, f"Table {table} not created")
    
    def test_file_recommendation_creation(self):
        """Test FileRecommendation dataclass creation and serialization"""
        rec = FileRecommendation(
            file_path="test_file.py",
            confidence_score=0.85,
            reasoning="Test reasoning",
            recommendation_type="pattern_match",
            supporting_evidence=["Evidence 1", "Evidence 2"]
        )
        
        self.assertEqual(rec.file_path, "test_file.py")
        self.assertEqual(rec.confidence_score, 0.85)
        self.assertEqual(rec.recommendation_type, "pattern_match")
        self.assertEqual(len(rec.supporting_evidence), 2)
        self.assertIsInstance(rec.metadata, dict)
    
    def test_recommendation_context_creation(self):
        """Test RecommendationContext dataclass creation"""
        context = RecommendationContext(
            current_conversation="Test conversation",
            user_intent="testing",
            mentioned_files=["file1.py", "file2.py"],
            development_phase="testing",
            keywords=["test", "verify"],
            conversation_id="conv_123",
            timestamp=datetime.now()
        )
        
        self.assertEqual(context.user_intent, "testing")
        self.assertEqual(len(context.mentioned_files), 2)
        self.assertIsInstance(context.session_context, dict)
    
    def test_pattern_based_recommendations(self):
        """Test pattern-based recommendation generation"""
        recommendations = self.recommendations._get_pattern_recommendations(self.sample_context)
        
        # Should have recommendations from mock pattern engine
        self.assertGreater(len(recommendations), 0)
        
        # Verify recommendations structure
        for rec in recommendations:
            self.assertIsInstance(rec, FileRecommendation)
            self.assertEqual(rec.recommendation_type, "pattern_match")
            self.assertGreater(rec.confidence_score, 0)
            self.assertIn("test_related.py", [r.file_path for r in recommendations])
    
    def test_context_similarity_recommendations(self):
        """Test context-based similarity recommendations"""
        # Add some sample file access history with multiple entries per file to meet frequency requirement
        with sqlite3.connect(self.test_db.name) as conn:
            # Add multiple entries for auth_handler.py
            conn.execute("""
                INSERT INTO file_access_history (file_path, conversation_id, access_type, context)
                VALUES (?, ?, ?, ?)
            """, ("auth_handler.py", "conv_123", "modified", "authentication implementation with JWT"))
            
            conn.execute("""
                INSERT INTO file_access_history (file_path, conversation_id, access_type, context)
                VALUES (?, ?, ?, ?)
            """, ("auth_handler.py", "conv_125", "viewed", "authentication implementation with JWT"))
            
            # Add multiple entries for user_service.py
            conn.execute("""
                INSERT INTO file_access_history (file_path, conversation_id, access_type, context)
                VALUES (?, ?, ?, ?)
            """, ("user_service.py", "conv_124", "viewed", "user management and authentication"))
            
            conn.execute("""
                INSERT INTO file_access_history (file_path, conversation_id, access_type, context)
                VALUES (?, ?, ?, ?)
            """, ("user_service.py", "conv_126", "modified", "user management and authentication"))
        
        recommendations = self.recommendations._get_context_similarity_recommendations(self.sample_context)
        
        # Should find files with similar context
        file_paths = [rec.file_path for rec in recommendations]
        self.assertIn("auth_handler.py", file_paths)
        self.assertIn("user_service.py", file_paths)
        
        # Verify recommendation properties
        for rec in recommendations:
            self.assertEqual(rec.recommendation_type, "context_similarity")
            self.assertGreater(rec.confidence_score, 0)
    
    def test_development_flow_recommendations(self):
        """Test development phase-aware recommendations"""
        # Add file access history with recent timestamps
        recent_time = (datetime.now() - timedelta(hours=2)).isoformat()
        
        with sqlite3.connect(self.test_db.name) as conn:
            conn.execute("""
                INSERT INTO file_access_history (file_path, conversation_id, access_type, context, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, ("main_service.py", "conv_123", "modified", "core implementation", recent_time))
            
            conn.execute("""
                INSERT INTO file_access_history (file_path, conversation_id, access_type, context, timestamp)  
                VALUES (?, ?, ?, ?, ?)
            """, ("test_auth.py", "conv_124", "viewed", "authentication testing", recent_time))
        
        recommendations = self.recommendations._get_development_flow_recommendations(self.sample_context)
        
        # Should recommend files appropriate for implementation phase
        self.assertGreater(len(recommendations), 0)
        
        for rec in recommendations:
            self.assertEqual(rec.recommendation_type, "development_flow")
            self.assertGreater(rec.confidence_score, 0)
    
    def test_frequency_based_recommendations(self):
        """Test frequency-based recommendations"""
        # Add multiple access records for same file
        with sqlite3.connect(self.test_db.name) as conn:
            for i in range(5):
                timestamp = (datetime.now() - timedelta(days=i)).isoformat()
                conn.execute("""
                    INSERT INTO file_access_history (file_path, conversation_id, access_type, timestamp)
                    VALUES (?, ?, ?, ?)
                """, ("frequently_used.py", f"conv_{i}", "modified", timestamp))
        
        recommendations = self.recommendations._get_frequency_recommendations(self.sample_context)
        
        # Should recommend frequently accessed file
        file_paths = [rec.file_path for rec in recommendations]
        self.assertIn("frequently_used.py", file_paths)
        
        # Find the frequent file recommendation
        freq_rec = next(rec for rec in recommendations if rec.file_path == "frequently_used.py")
        self.assertEqual(freq_rec.recommendation_type, "frequency")
        self.assertGreater(freq_rec.frequency_score, 0)
    
    def test_recency_based_recommendations(self):
        """Test recency-based recommendations"""
        # Add recent file access
        recent_time = (datetime.now() - timedelta(hours=1)).isoformat()
        
        with sqlite3.connect(self.test_db.name) as conn:
            conn.execute("""
                INSERT INTO file_access_history (file_path, conversation_id, access_type, context, timestamp)
                VALUES (?, ?, ?, ?, ?)
            """, ("recent_file.py", "conv_recent", "modified", "recent work", recent_time))
        
        recommendations = self.recommendations._get_recency_recommendations(self.sample_context)
        
        # Should recommend recently accessed file
        file_paths = [rec.file_path for rec in recommendations]
        self.assertIn("recent_file.py", file_paths)
        
        # Find the recent file recommendation
        recent_rec = next(rec for rec in recommendations if rec.file_path == "recent_file.py")
        self.assertEqual(recent_rec.recommendation_type, "recency")
        self.assertGreater(recent_rec.recency_score, 0)
    
    def test_recommendation_merging(self):
        """Test merging multiple recommendations for same file"""
        recommendations = [
            FileRecommendation(
                file_path="merge_test.py",
                confidence_score=0.6,
                reasoning="Pattern match",
                recommendation_type="pattern_match",
                supporting_evidence=["Evidence A"]
            ),
            FileRecommendation(
                file_path="merge_test.py", 
                confidence_score=0.4,
                reasoning="Context similarity",
                recommendation_type="context_similarity",
                supporting_evidence=["Evidence B"]
            )
        ]
        
        merged = self.recommendations._merge_recommendations(recommendations)
        
        # Should have one recommendation for the file
        self.assertEqual(len(merged), 1)
        merged_rec = merged[0]
        
        # Should combine confidence scores appropriately
        self.assertEqual(merged_rec.file_path, "merge_test.py")
        self.assertGreater(merged_rec.confidence_score, 0.6)  # Combined score
        self.assertIn("Evidence A", merged_rec.supporting_evidence)
        self.assertIn("Evidence B", merged_rec.supporting_evidence)
    
    def test_intent_boost_calculation(self):
        """Test intent-based confidence boosting"""
        # Test boost for testing intent with test file
        test_boost = self.recommendations._calculate_intent_boost("test_auth.py", "testing")
        self.assertGreater(test_boost, 1.0)
        
        # Test boost for implementation intent with service file
        impl_boost = self.recommendations._calculate_intent_boost("auth_service.py", "implementation")
        self.assertGreater(impl_boost, 1.0)
        
        # Test neutral case
        neutral_boost = self.recommendations._calculate_intent_boost("random.txt", "implementation")
        self.assertGreaterEqual(neutral_boost, 1.0)
    
    def test_phase_boost_calculation(self):
        """Test development phase-based confidence boosting"""
        # Test boost for testing phase with test file
        test_boost = self.recommendations._calculate_phase_boost("test_feature.py", "testing")
        self.assertGreater(test_boost, 1.0)
        
        # Test boost for implementation phase with service file
        impl_boost = self.recommendations._calculate_phase_boost("core_service.py", "implementation")
        self.assertGreater(impl_boost, 1.0)
    
    def test_keyword_extraction(self):
        """Test keyword extraction from conversation text"""
        text = "We need to implement user authentication with JWT tokens and secure the API endpoints"
        keywords = self.recommendations._extract_keywords(text)
        
        self.assertIn("implement", keywords)
        self.assertIn("authentication", keywords)  
        self.assertIn("jwt", keywords)
        self.assertIn("secure", keywords)
        self.assertIn("api", keywords)
        
        # Should exclude stop words
        self.assertNotIn("we", keywords)
        self.assertNotIn("the", keywords)
        self.assertNotIn("and", keywords)
    
    def test_context_similarity_calculation(self):
        """Test context similarity calculation"""
        keywords = ["authentication", "jwt", "user", "token"]
        context1 = "Authentication service using JWT tokens for user verification"
        context2 = "Database schema for product catalog"
        
        similarity1 = self.recommendations._calculate_context_similarity(keywords, context1)
        similarity2 = self.recommendations._calculate_context_similarity(keywords, context2)
        
        self.assertGreater(similarity1, similarity2)
        self.assertGreater(similarity1, 0.5)  # Should be high similarity
        self.assertLess(similarity2, 0.3)     # Should be low similarity
    
    def test_file_type_scoring(self):
        """Test file type appropriateness scoring"""
        implementation_types = ["implementation"]
        
        # Python file should score high for implementation
        py_score = self.recommendations._calculate_file_type_score("service.py", implementation_types)
        self.assertGreater(py_score, 0.5)
        
        # Text file should score low for implementation
        txt_score = self.recommendations._calculate_file_type_score("readme.txt", implementation_types)
        self.assertEqual(txt_score, 0.0)  # No implementation patterns match
    
    def test_get_recommendations_integration(self):
        """Test complete recommendation generation flow"""
        # Add some test data
        with sqlite3.connect(self.test_db.name) as conn:
            # Add file access history
            conn.execute("""
                INSERT INTO file_access_history (file_path, conversation_id, access_type, context)
                VALUES (?, ?, ?, ?)
            """, ("auth_service.py", "conv_123", "modified", "authentication implementation"))
            
            conn.execute("""
                INSERT INTO file_access_history (file_path, conversation_id, access_type, context)
                VALUES (?, ?, ?, ?)  
            """, ("user_model.py", "conv_124", "viewed", "user data model"))
        
        recommendations = self.recommendations.get_recommendations(self.sample_context, max_results=5)
        
        # Should return recommendations
        self.assertGreater(len(recommendations), 0)
        self.assertLessEqual(len(recommendations), 5)
        
        # Should be sorted by confidence
        for i in range(1, len(recommendations)):
            self.assertGreaterEqual(
                recommendations[i-1].confidence_score,
                recommendations[i].confidence_score
            )
        
        # Should have valid recommendation properties
        for rec in recommendations:
            self.assertIsInstance(rec, FileRecommendation)
            self.assertGreater(rec.confidence_score, 0)
            self.assertLessEqual(rec.confidence_score, 1.0)
            self.assertIsInstance(rec.supporting_evidence, list)
            self.assertIsInstance(rec.metadata, dict)
    
    def test_file_access_recording(self):
        """Test recording file access for learning"""
        self.recommendations.record_file_access(
            "test_file.py",
            "conv_123", 
            "modified",
            "testing file modification"
        )
        
        # Verify record was stored
        with sqlite3.connect(self.test_db.name) as conn:
            cursor = conn.execute("""
                SELECT file_path, access_type, context 
                FROM file_access_history 
                WHERE conversation_id = ?
            """, ("conv_123",))
            
            records = cursor.fetchall()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0][0], "test_file.py")
            self.assertEqual(records[0][1], "modified")
    
    def test_feedback_recording(self):
        """Test recording user feedback on recommendations"""
        feedback = RecommendationFeedback(
            recommendation_id="rec_123",
            file_path="feedback_test.py",
            user_action="accepted",
            timestamp=datetime.now(),
            context="User opened the recommended file",
            effectiveness_rating=4.5
        )
        
        self.recommendations.record_feedback(feedback)
        
        # Verify feedback was stored
        with sqlite3.connect(self.test_db.name) as conn:
            cursor = conn.execute("""
                SELECT user_action, effectiveness_rating, file_path
                FROM recommendation_feedback
                WHERE recommendation_id = ?
            """, ("rec_123",))
            
            records = cursor.fetchall()
            self.assertEqual(len(records), 1)
            self.assertEqual(records[0][0], "accepted")
            self.assertEqual(records[0][1], 4.5)
    
    def test_analytics_generation(self):
        """Test recommendation analytics generation"""
        # Add sample data for analytics
        with sqlite3.connect(self.test_db.name) as conn:
            # Add recommendations
            conn.execute("""
                INSERT INTO file_recommendations 
                (conversation_id, file_path, confidence_score, recommendation_type, 
                 reasoning, supporting_evidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("conv_1", "file1.py", 0.8, "pattern_match", "Test", "[]"))
            
            # Add feedback
            conn.execute("""
                INSERT INTO recommendation_feedback
                (recommendation_id, file_path, user_action, effectiveness_rating, context)
                VALUES (?, ?, ?, ?, ?)
            """, ("rec_1", "file1.py", "accepted", 4.0, "test context"))
        
        analytics = self.recommendations.get_recommendation_analytics()
        
        # Verify analytics structure
        self.assertIn('recommendation_types', analytics)
        self.assertIn('feedback', analytics)
        self.assertIn('total_feedback', analytics)
        self.assertIn('top_recommended_files', analytics)
        
        # Verify data
        self.assertEqual(analytics['total_feedback'], 1)
        self.assertIn('pattern_match', analytics['recommendation_types'])
        self.assertIn('accepted', analytics['feedback'])
    
    def test_optimization(self):
        """Test recommendation system optimization"""
        # Add some old data that should be cleaned up
        old_timestamp = (datetime.now() - timedelta(days=200)).isoformat()
        
        with sqlite3.connect(self.test_db.name) as conn:
            # Add old recommendation
            conn.execute("""
                INSERT INTO file_recommendations 
                (conversation_id, file_path, confidence_score, recommendation_type, 
                 reasoning, supporting_evidence, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("old_conv", "old_file.py", 0.5, "test", "test", "[]", old_timestamp))
            
            # Add low-confidence pattern
            conn.execute("""
                INSERT INTO recommendation_patterns
                (pattern_type, source_files, target_files, confidence, usage_count, last_used)
                VALUES (?, ?, ?, ?, ?, ?)
            """, ("test_pattern", '["source.py"]', '["target.py"]', 0.2, 1, old_timestamp))
        
        result = self.recommendations.optimize_recommendations()
        
        # Verify optimization results
        self.assertIsInstance(result, dict)
        self.assertIn('removed_patterns', result)
        self.assertIn('archived_recommendations', result)
        self.assertIn('archived_history', result)
    
    def test_cache_refresh(self):
        """Test pattern cache refresh functionality"""
        # Add a pattern to database
        with sqlite3.connect(self.test_db.name) as conn:
            conn.execute("""
                INSERT INTO recommendation_patterns
                (pattern_type, source_files, target_files, confidence, usage_count)
                VALUES (?, ?, ?, ?, ?)
            """, ("test_cache", '["source.py"]', '["target.py"]', 0.8, 5))
        
        # Refresh cache
        self.recommendations._refresh_pattern_cache()
        
        # Verify cache was updated
        self.assertGreater(len(self.recommendations.pattern_cache), 0)
    
    def test_file_types_for_phase(self):
        """Test getting appropriate file types for development phase"""
        impl_types = self.recommendations._get_file_types_for_phase("implementation", "implementation")
        self.assertIn("implementation", impl_types)
        
        test_types = self.recommendations._get_file_types_for_phase("testing", "testing")
        self.assertIn("testing", test_types)
        
        doc_types = self.recommendations._get_file_types_for_phase("documentation", "documentation")
        self.assertIn("documentation", doc_types)
    
    def test_development_flow_score(self):
        """Test development flow appropriateness scoring"""
        # High score for matching keywords
        high_score = self.recommendations._calculate_development_flow_score(
            "testing", "testing", "running unit tests and verification"
        )
        self.assertGreater(high_score, 0.5)
        
        # Lower score for mismatched keywords
        low_score = self.recommendations._calculate_development_flow_score(
            "testing", "testing", "database schema design"
        )
        self.assertLess(low_score, high_score)


if __name__ == '__main__':
    # Configure logging for tests
    import logging
    logging.basicConfig(level=logging.WARNING)
    
    # Run the test suite
    unittest.main(verbosity=2)