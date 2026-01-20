"""
Unit tests for HolisticContextBuilder.

Tests cover:
- All dimensions merged correctly
- YAML serialization
- Structure matches spec
- Edge cases
"""

import pytest
import yaml
from dataclasses import dataclass
from typing import Dict, Any

from src.core.orchestrator.holistic_context_builder import (
    HolisticContextBuilder,
)


@dataclass
class TestContext:
    """Test context structure."""
    intent: str
    analysis: Dict[str, Any]
    challenges: list
    recommendations: list
    git_context: Dict[str, Any]


class TestHolisticContextBuilder:
    """Test suite for HolisticContextBuilder."""
    
    def test_all_dimensions_merged_into_single_context(self):
        """Test all dimensions are merged into single context."""
        builder = HolisticContextBuilder()
        
        context_data = {
            "intent": "Add authentication feature",
            "analysis": {"complexity": "medium"},
            "challenges": [{"description": "SQL injection risk"}],
            "recommendations": [{"action": "Use ORM"}],
            "git_context": {"branch": "main"},
        }
        
        result = builder.build_holistic_context(context_data)
        
        assert "intent" in result
        assert "analysis" in result
        assert "challenges" in result
        assert "recommendations" in result
        assert "git_context" in result
    
    def test_challenges_included_in_reflection_section(self):
        """Test challenges are included in reflection section."""
        builder = HolisticContextBuilder()
        
        context_data = {
            "intent": "Test",
            "analysis": {},
            "challenges": [
                {"description": "Challenge 1", "severity": "HIGH"},
                {"description": "Challenge 2", "severity": "MEDIUM"},
            ],
            "recommendations": [],
            "git_context": {},
        }
        
        result = builder.build_holistic_context(context_data)
        
        assert "challenges" in result
        assert len(result["challenges"]) == 2
        assert result["challenges"][0]["description"] == "Challenge 1"
    
    def test_recommendations_included_in_reflection_section(self):
        """Test recommendations are included in reflection section."""
        builder = HolisticContextBuilder()
        
        context_data = {
            "intent": "Test",
            "analysis": {},
            "challenges": [],
            "recommendations": [
                {"action": "Add tests", "priority": 1},
                {"action": "Refactor", "priority": 2},
            ],
            "git_context": {},
        }
        
        result = builder.build_holistic_context(context_data)
        
        assert "recommendations" in result
        assert len(result["recommendations"]) == 2
        assert result["recommendations"][0]["action"] == "Add tests"
    
    def test_yaml_serialization_correct(self):
        """Test YAML serialization produces valid YAML."""
        builder = HolisticContextBuilder()
        
        context_data = {
            "intent": "Test",
            "analysis": {"key": "value"},
            "challenges": [{"desc": "c1"}],
            "recommendations": [{"rec": "r1"}],
            "git_context": {"branch": "main"},
        }
        
        result = builder.build_holistic_context(context_data)
        yaml_str = yaml.dump(result)
        
        # Should be parseable YAML
        parsed = yaml.safe_load(yaml_str)
        assert parsed is not None
        assert isinstance(parsed, dict)
    
    def test_empty_challenges_handled(self):
        """Test empty challenges list is handled gracefully."""
        builder = HolisticContextBuilder()
        
        context_data = {
            "intent": "Test",
            "analysis": {},
            "challenges": [],
            "recommendations": [],
            "git_context": {},
        }
        
        result = builder.build_holistic_context(context_data)
        
        assert "challenges" in result
        assert len(result["challenges"]) == 0
    
    def test_empty_recommendations_handled(self):
        """Test empty recommendations list is handled gracefully."""
        builder = HolisticContextBuilder()
        
        context_data = {
            "intent": "Test",
            "analysis": {},
            "challenges": [],
            "recommendations": [],
            "git_context": {},
        }
        
        result = builder.build_holistic_context(context_data)
        
        assert "recommendations" in result
        assert len(result["recommendations"]) == 0
    
    def test_structure_matches_cortex_prompt_format(self):
        """Test structure matches CORTEX.prompt.md holistic context format."""
        builder = HolisticContextBuilder()
        
        context_data = {
            "intent": "Add feature",
            "analysis": {"metrics": {}},
            "challenges": [{"desc": "c1"}],
            "recommendations": [{"action": "do"}],
            "git_context": {"history": []},
        }
        
        result = builder.build_holistic_context(context_data)
        
        # Should have required fields per spec
        required_fields = [
            "intent", "analysis", "challenges", 
            "recommendations", "git_context"
        ]
        for field in required_fields:
            assert field in result
    
    def test_complex_nested_analysis_preserved(self):
        """Test complex nested analysis is preserved."""
        builder = HolisticContextBuilder()
        
        complex_analysis = {
            "ast": {
                "imports": ["os", "sys"],
                "functions": {
                    "foo": {"params": ["a", "b"]},
                    "bar": {"params": ["c"]},
                },
            },
            "metrics": {
                "complexity": 5,
                "coverage": 0.85,
            },
        }
        
        context_data = {
            "intent": "Test",
            "analysis": complex_analysis,
            "challenges": [],
            "recommendations": [],
            "git_context": {},
        }
        
        result = builder.build_holistic_context(context_data)
        
        assert result["analysis"] == complex_analysis
        assert result["analysis"]["ast"]["functions"]["foo"]["params"] == ["a", "b"]
    
    def test_git_context_relationship_data_preserved(self):
        """Test git context and relationship data are preserved."""
        builder = HolisticContextBuilder()
        
        git_context = {
            "branch": "feature/auth",
            "commit_hash": "abc123",
            "relationships": {
                "depends_on": ["module_a", "module_b"],
                "used_by": ["module_c"],
            },
        }
        
        context_data = {
            "intent": "Test",
            "analysis": {},
            "challenges": [],
            "recommendations": [],
            "git_context": git_context,
        }
        
        result = builder.build_holistic_context(context_data)
        
        assert result["git_context"] == git_context
        assert result["git_context"]["relationships"]["depends_on"] == ["module_a", "module_b"]
    
    def test_intent_string_preserved(self):
        """Test intent string is preserved as-is."""
        builder = HolisticContextBuilder()
        
        intent_str = "Add authentication with OAuth2 and JWT tokens"
        
        context_data = {
            "intent": intent_str,
            "analysis": {},
            "challenges": [],
            "recommendations": [],
            "git_context": {},
        }
        
        result = builder.build_holistic_context(context_data)
        
        assert result["intent"] == intent_str
    
    def test_multiple_challenges_with_different_severities(self):
        """Test multiple challenges with different severities."""
        builder = HolisticContextBuilder()
        
        context_data = {
            "intent": "Test",
            "analysis": {},
            "challenges": [
                {"desc": "Critical issue", "severity": "CRITICAL"},
                {"desc": "High issue", "severity": "HIGH"},
                {"desc": "Medium issue", "severity": "MEDIUM"},
            ],
            "recommendations": [],
            "git_context": {},
        }
        
        result = builder.build_holistic_context(context_data)
        
        assert len(result["challenges"]) == 3
        severities = [c["severity"] for c in result["challenges"]]
        assert "CRITICAL" in severities
        assert "HIGH" in severities
        assert "MEDIUM" in severities
    
    def test_multiple_recommendations_with_priorities(self):
        """Test multiple recommendations with priorities."""
        builder = HolisticContextBuilder()
        
        context_data = {
            "intent": "Test",
            "analysis": {},
            "challenges": [],
            "recommendations": [
                {"action": "Priority 1", "priority": 1},
                {"action": "Priority 2", "priority": 2},
                {"action": "Priority 3", "priority": 3},
            ],
            "git_context": {},
        }
        
        result = builder.build_holistic_context(context_data)
        
        assert len(result["recommendations"]) == 3
        priorities = [r["priority"] for r in result["recommendations"]]
        assert priorities == [1, 2, 3]
    
    def test_empty_analysis_dict_handled(self):
        """Test empty analysis dictionary is handled."""
        builder = HolisticContextBuilder()
        
        context_data = {
            "intent": "Test",
            "analysis": {},
            "challenges": [],
            "recommendations": [],
            "git_context": {},
        }
        
        result = builder.build_holistic_context(context_data)
        
        assert result["analysis"] == {}
    
    def test_empty_git_context_dict_handled(self):
        """Test empty git context dictionary is handled."""
        builder = HolisticContextBuilder()
        
        context_data = {
            "intent": "Test",
            "analysis": {},
            "challenges": [],
            "recommendations": [],
            "git_context": {},
        }
        
        result = builder.build_holistic_context(context_data)
        
        assert result["git_context"] == {}
    
    def test_round_trip_serialization_preserves_data(self):
        """Test round-trip YAML serialization preserves data."""
        builder = HolisticContextBuilder()
        
        context_data = {
            "intent": "Add feature",
            "analysis": {"complexity": "medium"},
            "challenges": [{"desc": "c1", "severity": "HIGH"}],
            "recommendations": [{"action": "do", "priority": 1}],
            "git_context": {"branch": "main"},
        }
        
        result = builder.build_holistic_context(context_data)
        yaml_str = yaml.dump(result)
        parsed = yaml.safe_load(yaml_str)
        
        assert parsed == result
