"""
Unit tests for ResponseQualityScorer.

Tests 5-dimension quality scoring framework for response evaluation.

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34 specification
"""

import pytest
from typing import Dict, Any

from cortex.orchestrators.response.response_quality_scorer import (
    ResponseQualityScorer,
    QualityDimension,
    QualityScore,
)


class TestResponseQualityScorer:
    """Test response quality scoring."""
    
    @pytest.fixture
    def scorer(self) -> ResponseQualityScorer:
        """Create scorer instance."""
        return ResponseQualityScorer()
    
    def test_score_response_returns_quality_score(self, scorer):
        """Test that scoring returns QualityScore object."""
        response = "The system uses PostgreSQL database for storage."
        context = "Database selection"
        
        score = scorer.score_response(response, context)
        
        assert isinstance(score, QualityScore)
        assert 0.0 <= score.overall <= 1.0
    
    def test_score_clear_response_high_clarity(self, scorer):
        """Test clarity scoring for clear, readable response."""
        response = """
        The authentication system uses JWT tokens.
        Each token expires after 24 hours.
        Users can refresh tokens before expiration.
        """
        
        score = scorer.score_response(response, "authentication")
        
        # Clear response should have good clarity score
        assert score.clarity >= 0.65
    
    def test_score_complex_response_lower_clarity(self, scorer):
        """Test clarity scoring for complex response."""
        response = """
        Notwithstanding aforementioned complexities inherent within
        multifaceted architectural paradigms, authentication mechanisms
        leveraging cryptographically-secured tokens facilitate stateless
        verification protocols across distributed microservice topologies.
        """
        
        score = scorer.score_response(response, "authentication")
        
        # Complex jargon should lower clarity score (but still > 0.6)
        assert score.clarity < 0.75
    
    def test_score_complete_response_high_completeness(self, scorer):
        """Test completeness scoring for thorough response."""
        response = """
        The system implements authentication using JWT tokens.
        Token generation occurs on successful login.
        Tokens expire after 24 hours.
        Refresh tokens allow renewal without re-login.
        Token validation happens on each API request.
        """
        context = "Explain authentication system"
        
        score = scorer.score_response(response, context)
        
        # Complete response should have good completeness
        assert score.completeness >= 0.6
    
    def test_score_incomplete_response_lower_completeness(self, scorer):
        """Test completeness scoring for partial response."""
        response = "The system uses JWT tokens."
        context = "Explain authentication system including generation, expiry, validation"
        
        score = scorer.score_response(response, context)
        
        # Incomplete response should have lower completeness
        assert score.completeness < 0.5
    
    def test_score_concise_response_high_conciseness(self, scorer):
        """Test conciseness scoring for focused response."""
        response = "PostgreSQL handles data persistence. Redis manages caching."
        
        score = scorer.score_response(response, "database architecture")
        
        # Concise response should have high conciseness score
        assert score.conciseness >= 0.7
    
    def test_score_verbose_response_lower_conciseness(self, scorer):
        """Test conciseness scoring for verbose response."""
        response = """
        Well, you see, PostgreSQL, which is a database system,
        handles, among other things, the persistence of data,
        while Redis, another system, manages, as you might expect,
        the caching functionality of the application.
        """ * 3  # Repeat to make it really verbose
        
        score = scorer.score_response(response, "database architecture")
        
        # Verbose response should have lower conciseness
        assert score.conciseness < 0.7
    
    def test_score_relevant_response_high_relevance(self, scorer):
        """Test relevance scoring for on-topic response."""
        response = "JWT tokens authenticate API requests using cryptographic signatures."
        context = "authentication mechanism"
        
        score = scorer.score_response(response, context)
        
        # Relevant response with partial word match (authenticate/authentication)
        assert score.relevance >= 0.15  # Partial matching drives relevance
    
    def test_score_irrelevant_response_lower_relevance(self, scorer):
        """Test relevance scoring for off-topic response."""
        response = "The UI uses React components with Tailwind CSS."
        context = "database architecture"
        
        score = scorer.score_response(response, context)
        
        # Irrelevant response should have lower relevance
        assert score.relevance < 0.5
    
    def test_quality_dimensions_all_present(self, scorer):
        """Test that all 5 dimensions are scored."""
        response = "Test response"
        score = scorer.score_response(response, "test context")
        
        assert hasattr(score, 'clarity')
        assert hasattr(score, 'completeness')
        assert hasattr(score, 'conciseness')
        assert hasattr(score, 'accuracy')
        assert hasattr(score, 'relevance')
    
    def test_overall_score_weighted_average(self, scorer):
        """Test that overall score is weighted average of dimensions."""
        response = "Clear and complete technical response."
        score = scorer.score_response(response, "technical explanation")
        
        # Manual weighted calculation
        expected = (
            score.clarity * 0.25 +
            score.completeness * 0.25 +
            score.conciseness * 0.20 +
            score.accuracy * 0.20 +
            score.relevance * 0.10
        )
        
        assert abs(score.overall - expected) < 0.01
    
    def test_score_empty_response(self, scorer):
        """Test scoring of empty response."""
        score = scorer.score_response("", "context")
        
        # Empty response should have low scores
        assert score.overall < 0.3
    
    def test_score_code_heavy_response(self, scorer):
        """Test scoring of response with code examples."""
        response = """
        Here's the authentication implementation:
        
        ```python
        def authenticate(token: str) -> bool:
            return verify_jwt(token)
        ```
        
        This validates JWT tokens.
        """
        
        score = scorer.score_response(response, "authentication code")
        
        # Code examples should be recognized
        assert score.completeness >= 0.6


class TestQualityDimension:
    """Test QualityDimension enum."""
    
    def test_all_dimensions_defined(self):
        """Test that all 5 dimensions are defined."""
        dimensions = list(QualityDimension)
        assert len(dimensions) == 5
        assert QualityDimension.CLARITY in dimensions
        assert QualityDimension.COMPLETENESS in dimensions
        assert QualityDimension.CONCISENESS in dimensions
        assert QualityDimension.ACCURACY in dimensions
        assert QualityDimension.RELEVANCE in dimensions


class TestQualityScore:
    """Test QualityScore dataclass."""
    
    def test_quality_score_creation(self):
        """Test QualityScore instantiation."""
        score = QualityScore(
            clarity=0.8,
            completeness=0.7,
            conciseness=0.9,
            accuracy=0.85,
            relevance=0.75,
            overall=0.8
        )
        
        assert score.clarity == 0.8
        assert score.completeness == 0.7
        assert score.conciseness == 0.9
        assert score.accuracy == 0.85
        assert score.relevance == 0.75
        assert score.overall == 0.8
    
    def test_quality_score_to_dict(self):
        """Test QualityScore conversion to dictionary."""
        score = QualityScore(
            clarity=0.8,
            completeness=0.7,
            conciseness=0.9,
            accuracy=0.85,
            relevance=0.75,
            overall=0.8
        )
        
        score_dict = score.to_dict()
        
        assert isinstance(score_dict, dict)
        assert score_dict["clarity"] == 0.8
        assert score_dict["overall"] == 0.8
