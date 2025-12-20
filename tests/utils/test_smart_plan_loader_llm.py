"""
Tests for SmartPlanLoader LLM Integration (v2.0)

Tests LLM-based intent classification with fallback to regex.

Author: Asif Hussain
Date: December 20, 2025
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.utils.smart_plan_loader import SmartPlanLoader


class MockLLMClient:
    """Mock LLM client for testing."""
    
    def __init__(self, responses: dict = None, fail: bool = False):
        """
        Initialize mock client.
        
        Args:
            responses: Dict mapping queries to responses
            fail: If True, raise exceptions
        """
        self.responses = responses or {}
        self.fail = fail
        self.calls = []
    
    def classify(self, prompt: str) -> dict:
        """Mock classification."""
        self.calls.append(prompt)
        
        if self.fail:
            raise Exception("LLM service unavailable")
        
        # Extract query from prompt
        query_match = 'Query: "' in prompt
        if query_match:
            start = prompt.index('Query: "') + len('Query: "')
            end = prompt.index('"', start)
            query = prompt[start:end].lower()
            
            # Return mock response based on query content
            # Natural language variations for status
            if any(word in query for word in ['status', 'progress', 'going', 'update', 'where are we']):
                return {
                    'type': 'status_only',
                    'confidence': 0.95,
                    'reasoning': 'Status query detected (natural language)',
                    'estimated_tokens': 400
                }
            elif 'architecture' in query or 'design' in query:
                return {
                    'type': 'architecture',
                    'confidence': 0.92,
                    'reasoning': 'Architecture query detected',
                    'estimated_tokens': 1200
                }
            elif 'phase' in query:
                return {
                    'type': 'phase_specific',
                    'confidence': 0.97,
                    'reasoning': 'Phase-specific query detected',
                    'phase_id': '6',
                    'estimated_tokens': 2500
                }
            elif 'week' in query:
                return {
                    'type': 'week_specific',
                    'confidence': 0.93,
                    'reasoning': 'Week-specific query detected',
                    'week_number': '9',
                    'phase_id': '6',
                    'estimated_tokens': 1000
                }
        
        # Default response
        return {
            'type': 'default',
            'confidence': 0.75,
            'reasoning': 'No specific intent detected',
            'estimated_tokens': 1200
        }


@pytest.fixture
def mock_llm_client():
    """Provide mock LLM client."""
    return MockLLMClient()


@pytest.fixture
def cortex_root(tmp_path):
    """Create temporary CORTEX structure."""
    plan_base = tmp_path / "cortex-brain" / "documents" / "planning" / "active" / "CORTEX-3.0-4.0"
    plan_base.mkdir(parents=True)
    
    # Create status file
    status_file = plan_base / "CORTEX4-STATUS.md"
    status_file.write_text("# Status\nProgress: 80%")
    
    # Create master plan
    master_file = plan_base / "00-MASTER-PLAN.md"
    master_file.write_text("# Master Plan\nPhases: 10")
    
    # Create metadata
    metadata_dir = plan_base / "metadata"
    metadata_dir.mkdir()
    metadata_file = metadata_dir / "plan-metadata.yaml"
    metadata_file.write_text("version: 1.0\ncurrent_phase: 6")
    
    return tmp_path


class TestSmartPlanLoaderLLM:
    """Test LLM integration in SmartPlanLoader."""
    
    def test_initialization_with_llm(self, cortex_root, mock_llm_client):
        """Test loader initializes with LLM client."""
        loader = SmartPlanLoader(cortex_root, llm_client=mock_llm_client)
        
        assert loader.llm_client is not None
        assert loader.llm_client == mock_llm_client
    
    def test_initialization_without_llm(self, cortex_root):
        """Test loader initializes without LLM (fallback mode)."""
        loader = SmartPlanLoader(cortex_root)
        
        assert loader.llm_client is None
    
    def test_llm_classification_status_query(self, cortex_root, mock_llm_client):
        """Test LLM correctly classifies status queries."""
        loader = SmartPlanLoader(cortex_root, llm_client=mock_llm_client)
        
        result = loader._classify_query_intent("What's the current status?")
        
        assert result['type'] == 'status_only'
        assert result['confidence'] >= 0.8
        assert result['estimated_tokens'] == 400
        assert len(mock_llm_client.calls) == 1
    
    def test_llm_classification_architecture_query(self, cortex_root, mock_llm_client):
        """Test LLM correctly classifies architecture queries."""
        loader = SmartPlanLoader(cortex_root, llm_client=mock_llm_client)
        
        result = loader._classify_query_intent("Explain the architecture")
        
        assert result['type'] == 'architecture'
        assert result['confidence'] >= 0.8
        assert result['estimated_tokens'] == 1200
    
    def test_llm_classification_phase_query(self, cortex_root, mock_llm_client):
        """Test LLM correctly classifies phase-specific queries."""
        loader = SmartPlanLoader(cortex_root, llm_client=mock_llm_client)
        
        result = loader._classify_query_intent("Tell me about Phase 6")
        
        assert result['type'] == 'phase_specific'
        assert result['phase_id'] == '6'
        assert result['confidence'] >= 0.8
    
    def test_llm_classification_week_query(self, cortex_root, mock_llm_client):
        """Test LLM correctly classifies week-specific queries."""
        loader = SmartPlanLoader(cortex_root, llm_client=mock_llm_client)
        
        result = loader._classify_query_intent("What's happening in Week 9?")
        
        assert result['type'] == 'week_specific'
        assert result['week_number'] == '9'
        assert result['confidence'] >= 0.8
    
    def test_llm_classification_natural_language_status(self, cortex_root, mock_llm_client):
        """Test LLM handles natural language status queries."""
        loader = SmartPlanLoader(cortex_root, llm_client=mock_llm_client)
        
        # Natural variations
        queries = [
            "how's it going?",
            "give me a progress update",
            "where are we at?"
        ]
        
        for query in queries:
            result = loader._classify_query_intent(query)
            assert result['type'] == 'status_only', f"Failed for: {query}"
            assert result['confidence'] >= 0.8
    
    def test_llm_low_confidence_fallback(self, cortex_root):
        """Test fallback to regex when LLM confidence is low."""
        # Mock LLM with low confidence
        mock_client = Mock()
        mock_client.classify.return_value = {
            'type': 'default',
            'confidence': 0.5,  # Below 0.8 threshold
            'estimated_tokens': 1200
        }
        
        loader = SmartPlanLoader(cortex_root, llm_client=mock_client)
        
        # Should fallback to regex for clear status query
        result = loader._classify_query_intent("status")
        
        assert result['type'] == 'status_only'
        assert result['confidence'] == 0.85  # Regex confidence
    
    def test_llm_failure_fallback(self, cortex_root):
        """Test fallback to regex when LLM fails."""
        mock_client = MockLLMClient(fail=True)
        
        loader = SmartPlanLoader(cortex_root, llm_client=mock_client)
        
        # Should fallback to regex
        result = loader._classify_query_intent("What's the status?")
        
        assert result['type'] == 'status_only'
        assert result['confidence'] == 0.85  # Regex confidence
    
    def test_regex_fallback_without_llm(self, cortex_root):
        """Test regex classification works without LLM."""
        loader = SmartPlanLoader(cortex_root)  # No LLM
        
        test_cases = [
            ("status", "status_only"),
            ("architecture", "architecture"),
            ("Phase 6", "phase_specific"),
            ("Week 9", "week_specific")
        ]
        
        for query, expected_type in test_cases:
            result = loader._classify_query_intent(query)
            assert result['type'] == expected_type, f"Failed for: {query}"
            assert 'confidence' in result
    
    def test_llm_json_parsing(self, cortex_root):
        """Test LLM response JSON parsing."""
        # Mock LLM returning string JSON (like real LLM would)
        mock_client = Mock()
        mock_client.classify.return_value = json.dumps({
            'type': 'status_only',
            'confidence': 0.95,
            'reasoning': 'Status query detected',
            'estimated_tokens': 400
        })
        
        loader = SmartPlanLoader(cortex_root, llm_client=mock_client)
        result = loader._classify_query_intent("status check")
        
        # Verify LLM path was used (not regex fallback)
        assert result['type'] == 'status_only'
        assert result['confidence'] >= 0.8  # Accept any confidence >= threshold
        assert mock_client.classify.called  # Verify LLM was actually called
    
    def test_llm_invalid_response_fallback(self, cortex_root):
        """Test fallback when LLM returns invalid response."""
        # Mock LLM returning incomplete data
        mock_client = Mock()
        mock_client.classify.return_value = {'invalid': 'response'}
        
        loader = SmartPlanLoader(cortex_root, llm_client=mock_client)
        
        # Should fallback to regex
        result = loader._classify_query_intent("What's the status?")
        
        assert result['type'] == 'status_only'
        assert result['confidence'] == 0.85  # Regex confidence
    
    def test_end_to_end_with_llm(self, cortex_root, mock_llm_client):
        """Test full load_plan_context flow with LLM."""
        loader = SmartPlanLoader(cortex_root, llm_client=mock_llm_client)
        
        # Should load status only
        context = loader.load_plan_context("What's the status?")
        
        assert "Progress: 80%" in context
        assert len(mock_llm_client.calls) == 1
    
    def test_llm_caching_not_called_twice(self, cortex_root, mock_llm_client):
        """Test LLM is called for each unique query (no caching yet)."""
        loader = SmartPlanLoader(cortex_root, llm_client=mock_llm_client)
        
        loader._classify_query_intent("status")
        loader._classify_query_intent("status")
        
        # Should be called twice (no caching in v2.0)
        assert len(mock_llm_client.calls) == 2
    
    def test_confidence_tracking(self, cortex_root, mock_llm_client):
        """Test confidence scores are tracked correctly."""
        loader = SmartPlanLoader(cortex_root, llm_client=mock_llm_client)
        
        result = loader._classify_query_intent("What's the current progress?")
        
        assert 'confidence' in result
        assert 0.0 <= result['confidence'] <= 1.0
        assert result['confidence'] >= 0.8  # LLM should be confident


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
