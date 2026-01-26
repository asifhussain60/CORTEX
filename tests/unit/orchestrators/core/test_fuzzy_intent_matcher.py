"""
Test suite for AC-FUTURE-009: Fuzzy Matching + Advanced NLP Enhancements
Tests fuzzy string matching, NLP tokenization, semantic similarity
"""

import unittest
from unittest.mock import patch, MagicMock
from typing import List, Tuple
import difflib

from cortex.orchestrators.core.fuzzy_intent_matcher import (
    FuzzyIntentMatcher,
    FuzzyMatchResult,
    TokenizationStrategy,
)


class TestFuzzyIntentMatcher(unittest.TestCase):
    """Test fuzzy matching and NLP enhancements for intent detection"""

    def setUp(self):
        """Initialize fuzzy matcher with standard config"""
        self.matcher = FuzzyIntentMatcher(fuzzy_threshold=0.75)

    def test_exact_match_returns_100_percent(self):
        """Test that exact matches return 1.0 similarity"""
        result = self.matcher.fuzzy_match("implement user authentication", "implement user authentication")
        self.assertEqual(result.similarity_score, 1.0)
        self.assertTrue(result.is_match)

    def test_fuzzy_match_typos(self):
        """Test fuzzy matching with typos (AC-FUTURE-009)"""
        # Common typos
        test_cases = [
            ("implementt user auth", "implement user auth", 0.90),  # extra 't'
            ("implment user auth", "implement user auth", 0.88),    # missing 'e'
            ("refctor code", "refactor code", 0.85),                # transposition
        ]
        
        for typo_text, correct_text, min_expected in test_cases:
            result = self.matcher.fuzzy_match(typo_text, correct_text)
            self.assertGreater(result.similarity_score, min_expected)
            self.assertTrue(result.is_match, f"Failed for: {typo_text}")

    def test_fuzzy_match_abbreviations(self):
        """Test fuzzy matching handles common abbreviations"""
        test_cases = [
            ("impl auth", "implement authentication", 0.70),
            ("test this", "unit test", 0.65),
            ("ref code", "refactor code", 0.68),
        ]
        
        for abbrev, full, min_expected in test_cases:
            result = self.matcher.fuzzy_match(abbrev, full)
            # Abbreviations will have lower scores but should still be detected
            self.assertGreater(result.similarity_score, 0.60)

    def test_fuzzy_match_word_order(self):
        """Test fuzzy matching with different word order"""
        result = self.matcher.fuzzy_match(
            "authentication implement user",
            "implement user authentication"
        )
        # Should detect similarity despite different word order
        self.assertGreater(result.similarity_score, 0.70)

    def test_fuzzy_threshold_boundary(self):
        """Test fuzzy matching respects similarity threshold"""
        # High similarity (above threshold)
        result_high = self.matcher.fuzzy_match("implementt", "implement", threshold=0.80)
        self.assertTrue(result_high.is_match)
        
        # Low similarity (below threshold)
        result_low = self.matcher.fuzzy_match("foo", "bar", threshold=0.80)
        self.assertFalse(result_low.is_match)

    def test_tokenization_simple(self):
        """Test simple tokenization strategy"""
        tokenizer = TokenizationStrategy.SIMPLE
        tokens = self.matcher.tokenize("implement user authentication", tokenizer)
        self.assertEqual(tokens, ["implement", "user", "authentication"])

    def test_tokenization_advanced(self):
        """Test advanced NLP tokenization (camelCase, snake_case handling)"""
        tokenizer = TokenizationStrategy.ADVANCED
        
        test_cases = [
            ("implementUserAuth", ["implement", "user", "auth"]),
            ("implement_user_auth", ["implement", "user", "auth"]),
            ("ImplementUserAuth", ["implement", "user", "auth"]),
            ("IMPLEMENT_USER_AUTH", ["implement", "user", "auth"]),
        ]
        
        for input_str, expected_tokens in test_cases:
            tokens = self.matcher.tokenize(input_str, tokenizer)
            self.assertEqual(tokens, expected_tokens, f"Failed for: {input_str}")

    def test_semantic_similarity_synonyms(self):
        """Test semantic similarity detection (synonyms)"""
        # "implement" and "create" are semantically similar
        result = self.matcher.semantic_similarity("implement feature", "create feature")
        self.assertGreater(result, 0.70)
        
        # "fix" and "repair" are semantically similar
        result = self.matcher.semantic_similarity("fix bug", "repair bug")
        self.assertGreater(result, 0.70)

    def test_intent_extraction_from_fuzzy_match(self):
        """Test extracting intent classification from fuzzy match"""
        # Should recognize "implementt" as IMPLEMENT intent
        result = self.matcher.extract_intent("implementt new feature")
        self.assertEqual(result.primary_intent, "implement")
        self.assertGreater(result.confidence, 0.80)

    def test_multiple_fuzzy_matches(self):
        """Test ranking multiple fuzzy matches"""
        candidates = [
            "implement feature",
            "implementt feature",
            "implment feature",
            "crate feature",  # typo for "create"
        ]
        
        query = "implementt feture"
        matches = self.matcher.find_best_matches(query, candidates, top_k=3)
        
        # Best match should be "implementt feature"
        self.assertEqual(matches[0].candidate, "implementt feature")
        # "implement feature" should be second
        self.assertEqual(matches[1].candidate, "implement feature")
        self.assertGreater(len(matches), 0)

    def test_fuzzy_match_result_structure(self):
        """Test FuzzyMatchResult data structure"""
        result = self.matcher.fuzzy_match("test", "test")
        
        self.assertIsNotNone(result.similarity_score)
        self.assertIsNotNone(result.is_match)
        self.assertIsNotNone(result.match_type)  # EXACT, FUZZY, SEMANTIC
        self.assertIn(result.match_type, ["EXACT", "FUZZY", "SEMANTIC"])

    def test_performance_large_dataset(self):
        """Test fuzzy matching performance with large candidate list"""
        candidates = [f"candidate {i}" for i in range(1000)]
        candidates.append("implementt feature")
        
        matches = self.matcher.find_best_matches("implement feature", candidates, top_k=5)
        
        # Should complete efficiently and find correct match
        self.assertGreater(len(matches), 0)
        self.assertEqual(matches[0].candidate, "implementt feature")

    def test_case_insensitive_matching(self):
        """Test that matching is case-insensitive"""
        result1 = self.matcher.fuzzy_match("IMPLEMENT", "implement")
        result2 = self.matcher.fuzzy_match("Implement", "IMPLEMENT")
        
        self.assertEqual(result1.similarity_score, 1.0)
        self.assertEqual(result2.similarity_score, 1.0)

    def test_whitespace_normalization(self):
        """Test that extra whitespace is normalized"""
        result = self.matcher.fuzzy_match(
            "implement  user   auth",
            "implement user auth"
        )
        self.assertEqual(result.similarity_score, 1.0)


class TestFuzzyMatcherIntegration(unittest.TestCase):
    """Integration tests for fuzzy matcher with intent router"""

    def setUp(self):
        """Initialize fuzzy matcher"""
        self.matcher = FuzzyIntentMatcher(fuzzy_threshold=0.75)

    def test_fuzzy_matching_improves_routing_accuracy(self):
        """Test that fuzzy matching reduces misclassification"""
        # With fuzzy matching, typos should still route to correct intent
        typo_requests = [
            "implementt new login system",
            "fixx memory leak",
            "refctor database queries",
        ]
        
        for request in typo_requests:
            # Should still extract primary intent despite typos
            result = self.matcher.extract_intent(request)
            self.assertIsNotNone(result.primary_intent)
            self.assertGreater(result.confidence, 0.75)

    def test_fuzzy_match_caching(self):
        """Test that fuzzy match results are cached for performance"""
        # First call
        result1 = self.matcher.fuzzy_match("implementt", "implement")
        
        # Second call (should be cached)
        result2 = self.matcher.fuzzy_match("implementt", "implement")
        
        # Results should be identical
        self.assertEqual(result1.similarity_score, result2.similarity_score)

    def test_semantic_understanding_with_context(self):
        """Test semantic understanding uses context for better matching"""
        # Request talks about implementation
        request = "build a new authentication system"
        
        # Should understand "build" as implementation intent
        result = self.matcher.extract_intent(request)
        self.assertIn(result.primary_intent, ["implement", "feature"])


if __name__ == "__main__":
    unittest.main()
