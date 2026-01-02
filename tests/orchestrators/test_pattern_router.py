"""
Tests for Pattern Router.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import yaml
from pathlib import Path

from src.orchestrators.pattern_router import (
    PatternRouter,
    RoutingRule,
    OrchestratorMatch,
    MatchType
)


@pytest.fixture
def temp_config():
    """Create temporary routing config."""
    config = {
        'routing_rules': [
            {
                'pattern': '^(plan|create a plan)$',
                'orchestrator': 'planning_v5',
                'confidence': 1.0,
                'match_type': 'exact',
                'priority': 10
            },
            {
                'pattern': '^(tdd|start tdd).*$',
                'orchestrator': 'tdd_orchestrator',
                'confidence': 1.0,
                'match_type': 'regex',
                'priority': 20
            },
            {
                'pattern': '^(ado|ado story).*$',
                'orchestrator': 'ado_orchestrator',
                'confidence': 0.95,
                'match_type': 'regex',
                'priority': 30
            }
        ],
        'fallback': {
            'enabled': true,
            'confidence_threshold': 0.7
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
        yaml.dump(config, f)
        yield f.name
    
    Path(f.name).unlink(missing_ok=True)


@pytest.fixture
def router(temp_config):
    """Create PatternRouter instance."""
    return PatternRouter(temp_config)


class TestPatternRouterInitialization:
    """Test router initialization."""
    
    def test_init_valid_config(self, router):
        """Test initialization with valid config."""
        assert len(router.rules) == 3
        assert router.fallback_config['enabled'] is True
    
    def test_init_missing_config(self):
        """Test initialization with missing config."""
        with pytest.raises(FileNotFoundError):
            PatternRouter('nonexistent.yaml')
    
    def test_init_invalid_yaml(self):
        """Test initialization with invalid YAML."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content:")
            config_path = f.name
        
        try:
            with pytest.raises(yaml.YAMLError):
                PatternRouter(config_path)
        finally:
            Path(config_path).unlink(missing_ok=True)
    
    def test_rules_sorted_by_priority(self, router):
        """Test that rules are sorted by priority."""
        priorities = [rule.priority for rule in router.rules]
        assert priorities == sorted(priorities)


class TestRoutingRule:
    """Test RoutingRule dataclass."""
    
    def test_create_valid_rule(self):
        """Test creating valid routing rule."""
        rule = RoutingRule(
            pattern="^test$",
            orchestrator_id="test_orch",
            confidence=0.9,
            match_type=MatchType.EXACT,
            priority=100
        )
        
        assert rule.pattern == "^test$"
        assert rule.confidence == 0.9
    
    def test_invalid_confidence(self):
        """Test rule with invalid confidence."""
        with pytest.raises(ValueError, match="Confidence must be 0-1"):
            RoutingRule(
                pattern="test",
                orchestrator_id="test",
                confidence=1.5,
                match_type=MatchType.EXACT
            )
    
    def test_invalid_regex_pattern(self):
        """Test rule with invalid regex."""
        with pytest.raises(ValueError, match="Invalid regex pattern"):
            RoutingRule(
                pattern="[invalid(regex",
                orchestrator_id="test",
                confidence=1.0,
                match_type=MatchType.REGEX
            )


class TestPatternMatching:
    """Test pattern matching functionality."""
    
    def test_exact_match(self, router):
        """Test exact pattern matching."""
        match = router.match_intent("plan")
        
        assert match.is_matched
        assert match.orchestrator_id == "planning_v5"
        assert match.match_type == MatchType.EXACT
        assert match.confidence == 1.0
    
    def test_exact_match_case_insensitive(self, router):
        """Test exact match is case-insensitive."""
        match = router.match_intent("PLAN")
        
        assert match.is_matched
        assert match.orchestrator_id == "planning_v5"
    
    def test_regex_match(self, router):
        """Test regex pattern matching."""
        match = router.match_intent("tdd for user authentication")
        
        assert match.is_matched
        assert match.orchestrator_id == "tdd_orchestrator"
        assert match.match_type == MatchType.REGEX
    
    def test_regex_match_prefix(self, router):
        """Test regex matches at start."""
        match = router.match_intent("ado story for feature X")
        
        assert match.is_matched
        assert match.orchestrator_id == "ado_orchestrator"
    
    def test_no_match(self, router):
        """Test input with no matching pattern."""
        match = router.match_intent("completely unrelated request")
        
        assert not match.is_matched
        assert match.orchestrator_id is None
        assert match.confidence == 0.0
    
    def test_empty_input(self, router):
        """Test empty input."""
        match = router.match_intent("")
        
        assert not match.is_matched
    
    def test_whitespace_only_input(self, router):
        """Test whitespace-only input."""
        match = router.match_intent("   ")
        
        assert not match.is_matched
    
    def test_priority_ordering(self, router):
        """Test that higher priority rules match first."""
        # If both patterns could match, higher priority (lower number) wins
        match = router.match_intent("plan")
        
        # planning_v5 has priority 10, should match before others
        assert match.orchestrator_id == "planning_v5"


class TestOrchestratorMatch:
    """Test OrchestratorMatch dataclass."""
    
    def test_is_matched_true(self):
        """Test is_matched property when matched."""
        match = OrchestratorMatch(
            orchestrator_id="test_orch",
            confidence=0.9,
            match_type=MatchType.EXACT
        )
        
        assert match.is_matched
    
    def test_is_matched_false(self):
        """Test is_matched property when not matched."""
        match = OrchestratorMatch(
            orchestrator_id=None,
            confidence=0.0,
            match_type=MatchType.NONE
        )
        
        assert not match.is_matched
    
    def test_is_high_confidence(self):
        """Test is_high_confidence property."""
        high_match = OrchestratorMatch(
            orchestrator_id="test",
            confidence=0.95,
            match_type=MatchType.EXACT
        )
        
        low_match = OrchestratorMatch(
            orchestrator_id="test",
            confidence=0.7,
            match_type=MatchType.REGEX
        )
        
        assert high_match.is_high_confidence
        assert not low_match.is_high_confidence


class TestRouterQueries:
    """Test router query methods."""
    
    def test_get_orchestrator_patterns(self, router):
        """Test getting patterns for specific orchestrator."""
        patterns = router.get_orchestrator_patterns("tdd_orchestrator")
        
        assert len(patterns) == 1
        assert patterns[0].orchestrator_id == "tdd_orchestrator"
    
    def test_get_orchestrator_patterns_none(self, router):
        """Test getting patterns for non-existent orchestrator."""
        patterns = router.get_orchestrator_patterns("nonexistent")
        
        assert len(patterns) == 0
    
    def test_get_stats(self, router):
        """Test router statistics."""
        stats = router.get_stats()
        
        assert stats['total_rules'] == 3
        assert stats['exact_patterns'] == 1
        assert stats['regex_patterns'] == 2
        assert 'planning_v5' in stats['orchestrators']
        assert 'tdd_orchestrator' in stats['orchestrators']


class TestValidation:
    """Test pattern validation."""
    
    def test_validate_patterns_valid(self, router):
        """Test validation with valid patterns."""
        errors = router.validate_patterns()
        
        assert len(errors) == 0
    
    def test_validate_patterns_duplicate(self):
        """Test validation detects duplicate patterns."""
        config = {
            'routing_rules': [
                {
                    'pattern': '^test$',
                    'orchestrator': 'orch1',
                    'confidence': 1.0,
                    'match_type': 'exact'
                },
                {
                    'pattern': '^test$',  # Duplicate
                    'orchestrator': 'orch2',
                    'confidence': 1.0,
                    'match_type': 'exact'
                }
            ]
        }
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(config, f)
            config_path = f.name
        
        try:
            router = PatternRouter(config_path)
            errors = router.validate_patterns()
            
            assert len(errors) > 0
            assert any('Duplicate' in err for err in errors)
        finally:
            Path(config_path).unlink(missing_ok=True)


class TestConfigReload:
    """Test configuration reloading."""
    
    def test_reload_config(self, temp_config, router):
        """Test reloading configuration."""
        initial_count = len(router.rules)
        
        # Modify config file
        config = {
            'routing_rules': [
                {
                    'pattern': '^new_pattern$',
                    'orchestrator': 'new_orch',
                    'confidence': 1.0,
                    'match_type': 'exact'
                }
            ],
            'fallback': {'enabled': False}
        }
        
        with open(temp_config, 'w') as f:
            yaml.dump(config, f)
        
        # Reload
        router.reload_config()
        
        assert len(router.rules) != initial_count
        assert len(router.rules) == 1
        assert router.rules[0].orchestrator_id == 'new_orch'


class TestEdgeCases:
    """Test edge cases and error conditions."""
    
    def test_pattern_with_special_characters(self, router):
        """Test pattern matching with special regex characters."""
        # Patterns should be properly escaped or handled
        match = router.match_intent("test (with) special [chars]")
        
        # Should not crash, may or may not match
        assert match is not None
    
    def test_very_long_input(self, router):
        """Test pattern matching with very long input."""
        long_input = "plan " + ("test " * 1000)
        
        match = router.match_intent(long_input)
        
        # Should not crash
        assert match is not None
    
    def test_unicode_input(self, router):
        """Test pattern matching with unicode characters."""
        match = router.match_intent("plan with 中文 characters")
        
        # Should not crash
        assert match is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
