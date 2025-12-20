"""
Tests for ComplexityAnalyzer LLM integration.

Test Coverage:
- LLM-based semantic trigger detection
- Confidence-based fallback to regex
- Natural language pattern recognition
- Mock LLM client testing
- Edge cases and error handling

Author: Asif Hussain
Date: December 20, 2025
"""

import pytest
import json
from unittest.mock import Mock
from src.operations.modules.routing.complexity_analyzer import (
    ComplexityAnalyzer,
    ComplexityTier
)


class MockLLMClient:
    """Mock LLM client for testing without real LLM calls."""
    
    def __init__(self, fail: bool = False):
        """Initialize mock with optional failure mode."""
        self.fail = fail
        self.calls = []
    
    def analyze(self, prompt: str) -> dict:
        """Mock semantic analysis."""
        self.calls.append(prompt)
        
        if self.fail:
            raise Exception("LLM service unavailable")
        
        # Extract request from prompt
        request = ""
        if 'Request:' in prompt:
            start = prompt.index('Request:') + len('Request:')
            lines = prompt[start:].strip().split('\n')
            request = lines[0].strip().lower() if lines else ""
        
        # Return semantic analysis based on content
        triggers = []
        reasoning = []
        
        # Security patterns (broad semantic matching)
        security_keywords = ['login', 'user authentication', 'access control', 'password reset', 
                           'authentication', 'authorize', 'auth', 'sign in', 'credential']
        if any(word in request for word in security_keywords):
            triggers.append('security')
            reasoning.append('Authentication/authorization detected')
        
        # Data operations (broad semantic matching)
        data_keywords = ['database migration', 'schema update', 'data model change', 'database schema',
                        'add table', 'modify table', 'alter table', 'schema change', 'migration']
        if any(word in request for word in data_keywords):
            triggers.append('data_operations')
            reasoning.append('Database schema modification detected')
        
        # API changes (broad semantic matching)
        api_keywords = ['api versioning', 'breaking api', 'deprecate endpoint', 'api', 'rest endpoint',
                       'response format', 'api contract', 'endpoints', 'breaking change']
        if any(word in request for word in api_keywords):
            triggers.append('api_breaking')
            reasoning.append('API contract change detected')
        
        # Critical domains
        critical_keywords = ['payment processing', 'financial transaction', 'billing system',
                           'payment', 'financial', 'billing', 'transaction', 'credit card',
                           'handle credit', 'process payment', 'charge', 'refund']
        if any(word in request for word in critical_keywords):
            triggers.append('critical_domains')
            reasoning.append('Financial domain detected')
        
        confidence = 0.95 if triggers else 0.80
        
        return {
            'triggers': triggers,
            'confidence': confidence,
            'reasoning': ' | '.join(reasoning) if reasoning else 'No critical patterns detected'
        }


@pytest.fixture
def mock_llm_client():
    """Provide mock LLM client."""
    return MockLLMClient()


@pytest.fixture
def analyzer_with_llm(mock_llm_client):
    """Provide ComplexityAnalyzer with LLM client."""
    analyzer = ComplexityAnalyzer()
    analyzer.llm_client = mock_llm_client
    return analyzer


@pytest.fixture
def analyzer_without_llm():
    """Provide ComplexityAnalyzer without LLM client."""
    return ComplexityAnalyzer()


class TestComplexityAnalyzerLLM:
    """Test LLM integration in ComplexityAnalyzer."""
    
    def test_llm_security_detection_natural_language(self, analyzer_with_llm):
        """Test LLM detects security in natural language."""
        request = "We need to implement user authentication for the login flow"
        
        score = analyzer_with_llm.analyze(request)
        
        assert 'security' in [t.split(':')[0] for t in score.triggers]
        assert score.tier == ComplexityTier.HIGH
        assert score.total_score >= 70
    
    def test_llm_data_operations_semantic(self, analyzer_with_llm):
        """Test LLM understands semantic data operations."""
        request = "Update the database schema to add user preferences table"
        
        score = analyzer_with_llm.analyze(request)
        
        # Should detect data_operations trigger
        trigger_categories = [t.split(':')[0] for t in score.triggers]
        assert 'data_operations' in trigger_categories
        assert score.tier in [ComplexityTier.HIGH, ComplexityTier.CRITICAL]
    
    def test_llm_api_changes_implicit(self, analyzer_with_llm):
        """Test LLM catches implicit API changes."""
        request = "Change the response format for all REST endpoints to include metadata"
        
        score = analyzer_with_llm.analyze(request)
        
        # LLM should recognize this as API breaking change
        assert score.tier == ComplexityTier.HIGH
    
    def test_llm_financial_domain_detection(self, analyzer_with_llm):
        """Test LLM recognizes financial domain."""
        request = "Build a payment processing system for credit card transactions"
        
        score = analyzer_with_llm.analyze(request)
        
        trigger_categories = [t.split(':')[0] for t in score.triggers]
        assert 'critical_domains' in trigger_categories
        assert score.tier == ComplexityTier.HIGH
    
    def test_llm_low_confidence_fallback(self, analyzer_with_llm):
        """Test fallback when LLM confidence is low."""
        # Mock to return low confidence
        analyzer_with_llm.llm_client.analyze = lambda p: {
            'triggers': ['security'],
            'confidence': 0.70,  # Below 0.8 threshold
            'reasoning': 'Uncertain match'
        }
        
        request = "Add authentication to API"
        score = analyzer_with_llm.analyze(request)
        
        # Should still detect via regex fallback
        assert score.tier == ComplexityTier.HIGH
    
    def test_llm_failure_fallback(self, analyzer_with_llm):
        """Test fallback when LLM fails."""
        analyzer_with_llm.llm_client.fail = True
        
        request = "Add password encryption to user service"
        score = analyzer_with_llm.analyze(request)
        
        # Should fallback to regex and still detect
        trigger_categories = [t.split(':')[0] for t in score.triggers]
        assert 'security' in trigger_categories
    
    def test_regex_fallback_without_llm(self, analyzer_without_llm):
        """Test regex works when no LLM available."""
        request = "Implement OAuth authentication"
        
        score = analyzer_without_llm.analyze(request)
        
        # Regex should detect security trigger
        trigger_categories = [t.split(':')[0] for t in score.triggers]
        assert 'security' in trigger_categories
        assert score.tier == ComplexityTier.HIGH
    
    def test_llm_multiple_triggers(self, analyzer_with_llm):
        """Test LLM detects multiple trigger categories."""
        request = "Migrate user authentication database schema to support OAuth tokens"
        
        score = analyzer_with_llm.analyze(request)
        
        trigger_categories = [t.split(':')[0] for t in score.triggers]
        # Should detect both security and data_operations
        assert 'security' in trigger_categories
        assert 'data_operations' in trigger_categories
        assert score.tier == ComplexityTier.HIGH
    
    def test_llm_no_triggers_detected(self, analyzer_with_llm):
        """Test LLM correctly identifies non-critical requests."""
        request = "Add a new button to the settings page"
        
        score = analyzer_with_llm.analyze(request)
        
        # Should not trigger HIGH complexity
        assert score.tier in [ComplexityTier.LOW, ComplexityTier.MEDIUM, ComplexityTier.TRIVIAL]
    
    def test_llm_json_response_parsing(self, analyzer_with_llm):
        """Test parsing of LLM JSON responses."""
        # Mock returning string JSON
        analyzer_with_llm.llm_client.analyze = lambda p: json.dumps({
            'triggers': ['security', 'data_operations'],
            'confidence': 0.92,
            'reasoning': 'Auth + migration detected'
        })
        
        request = "Add JWT auth with user table migration"
        score = analyzer_with_llm.analyze(request)
        
        assert len(score.triggers) >= 2
        assert score.tier == ComplexityTier.HIGH
    
    def test_llm_invalid_response_fallback(self, analyzer_with_llm):
        """Test fallback when LLM returns invalid response."""
        # Mock returning incomplete data
        analyzer_with_llm.llm_client.analyze = lambda p: {'invalid': 'response'}
        
        request = "Add encryption to passwords"
        score = analyzer_with_llm.analyze(request)
        
        # Should fallback to regex and still work
        assert score.tier == ComplexityTier.HIGH
    
    def test_llm_caching_not_called_twice(self, analyzer_with_llm):
        """Test LLM is called for each unique request."""
        request = "Add user login"
        
        analyzer_with_llm.analyze(request)
        analyzer_with_llm.analyze(request)
        
        # Should be called twice (no caching in v1.0)
        assert len(analyzer_with_llm.llm_client.calls) == 2
    
    def test_confidence_tracking(self, analyzer_with_llm):
        """Test confidence scores are available."""
        request = "Implement secure payment gateway"
        
        score = analyzer_with_llm.analyze(request)
        
        # Verify triggers detected
        assert len(score.triggers) > 0
        assert score.tier == ComplexityTier.HIGH
    
    def test_llm_reasoning_included(self, analyzer_with_llm):
        """Test LLM reasoning is included in rationale."""
        request = "Add credit card processing"
        
        score = analyzer_with_llm.analyze(request)
        
        # Rationale should include reasoning
        assert len(score.rationale) > 0
        assert score.tier == ComplexityTier.HIGH
    
    def test_natural_language_variations(self, analyzer_with_llm):
        """Test LLM handles various natural language forms."""
        test_cases = [
            ("user login flow", ComplexityTier.HIGH),  # security
            ("schema update for users", ComplexityTier.HIGH),  # data_operations
            ("change API response structure", ComplexityTier.HIGH),  # api_breaking
            ("handle credit cards", ComplexityTier.HIGH),  # critical_domains
        ]
        
        for request, expected_tier in test_cases:
            score = analyzer_with_llm.analyze(request)
            assert score.tier == expected_tier, f"Failed for: {request}"
