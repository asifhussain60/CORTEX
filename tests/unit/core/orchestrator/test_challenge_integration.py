"""
Comprehensive unit tests for ChallengeIntegrationOrchestrator.

Tests cover:
- Confidence threshold filtering
- Severity-based sorting  
- Edge cases (empty, all low-confidence, mixed)
- Integration with ChallengeGenerator
"""

import pytest
from typing import List
from dataclasses import dataclass
from enum import Enum

from src.core.orchestrator.challenge_integration import (
    ChallengeIntegrationOrchestrator,
    Challenge,
    ChallengeSeverity,
)


class MockChallengeGenerator:
    """Mock challenge generator for testing."""
    
    def __init__(self, challenges: List[Challenge]):
        self.challenges = challenges
    
    def generate_challenges(self, context: dict) -> List[Challenge]:
        """Generate challenges from context."""
        return self.challenges


class TestChallengeIntegrationOrchestrator:
    """Test suite for ChallengeIntegrationOrchestrator."""
    
    def test_confidence_threshold_filtering_excludes_low_confidence(self):
        """Test that challenges < 0.3 confidence are excluded."""
        challenges = [
            Challenge("low", ChallengeSeverity.CRITICAL, 0.25),
            Challenge("high", ChallengeSeverity.HIGH, 0.75),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(
            generator, confidence_threshold=0.30
        )
        
        result = orchestrator.process_challenges({"dummy": "context"})
        assert len(result) == 1
        assert result[0].description == "high"
        assert result[0].confidence == 0.75
    
    def test_confidence_threshold_filtering_includes_threshold_equal(self):
        """Test that challenges = 0.3 confidence are included."""
        challenges = [
            Challenge("edge", ChallengeSeverity.HIGH, 0.30),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(
            generator, confidence_threshold=0.30
        )
        
        result = orchestrator.process_challenges({"dummy": "context"})
        assert len(result) == 1
        assert result[0].confidence == 0.30
    
    def test_severity_sorting_critical_first(self):
        """Test severity sorting: CRITICAL → HIGH → MEDIUM → LOW."""
        challenges = [
            Challenge("low", ChallengeSeverity.LOW, 0.5),
            Challenge("critical", ChallengeSeverity.CRITICAL, 0.5),
            Challenge("medium", ChallengeSeverity.MEDIUM, 0.5),
            Challenge("high", ChallengeSeverity.HIGH, 0.5),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(generator)
        
        result = orchestrator.process_challenges({"dummy": "context"})
        
        assert result[0].description == "critical"
        assert result[1].description == "high"
        assert result[2].description == "medium"
        assert result[3].description == "low"
    
    def test_empty_challenges_returns_empty_list(self):
        """Test empty challenge list is handled gracefully."""
        generator = MockChallengeGenerator([])
        orchestrator = ChallengeIntegrationOrchestrator(generator)
        
        result = orchestrator.process_challenges({"dummy": "context"})
        
        assert result == []
        assert len(result) == 0
    
    def test_mixed_severity_challenges_sorted_correctly(self):
        """Test mixed severity challenges are sorted correctly."""
        challenges = [
            Challenge("m2", ChallengeSeverity.MEDIUM, 0.6),
            Challenge("c1", ChallengeSeverity.CRITICAL, 0.5),
            Challenge("h1", ChallengeSeverity.HIGH, 0.7),
            Challenge("l1", ChallengeSeverity.LOW, 0.4),
            Challenge("c2", ChallengeSeverity.CRITICAL, 0.8),
            Challenge("m1", ChallengeSeverity.MEDIUM, 0.5),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(generator)
        
        result = orchestrator.process_challenges({"dummy": "context"})
        
        # Should be sorted: CRITICAL (both) → HIGH → MEDIUM (both) → LOW
        assert result[0].severity == ChallengeSeverity.CRITICAL
        assert result[1].severity == ChallengeSeverity.CRITICAL
        assert result[2].severity == ChallengeSeverity.HIGH
        assert result[3].severity == ChallengeSeverity.MEDIUM
        assert result[4].severity == ChallengeSeverity.MEDIUM
        assert result[5].severity == ChallengeSeverity.LOW
    
    def test_all_low_confidence_challenges_filtered(self):
        """Test all low-confidence challenges are filtered."""
        challenges = [
            Challenge("low1", ChallengeSeverity.CRITICAL, 0.15),
            Challenge("low2", ChallengeSeverity.HIGH, 0.25),
            Challenge("low3", ChallengeSeverity.MEDIUM, 0.20),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(
            generator, confidence_threshold=0.30
        )
        
        result = orchestrator.process_challenges({"dummy": "context"})
        
        assert len(result) == 0
    
    def test_high_confidence_challenges_all_included(self):
        """Test all high-confidence challenges are included."""
        challenges = [
            Challenge("c1", ChallengeSeverity.CRITICAL, 0.95),
            Challenge("h1", ChallengeSeverity.HIGH, 0.85),
            Challenge("m1", ChallengeSeverity.MEDIUM, 0.75),
            Challenge("l1", ChallengeSeverity.LOW, 0.65),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(
            generator, confidence_threshold=0.30
        )
        
        result = orchestrator.process_challenges({"dummy": "context"})
        
        assert len(result) == 4
    
    def test_integration_with_challenge_generator(self):
        """Test orchestrator correctly calls generator."""
        challenges = [
            Challenge("generated", ChallengeSeverity.HIGH, 0.5),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(generator)
        
        context = {"key": "value"}
        result = orchestrator.process_challenges(context)
        
        assert len(result) == 1
        assert result[0].description == "generated"
    
    def test_confidence_filtering_with_mixed_threshold(self):
        """Test confidence filtering with 0.5 threshold."""
        challenges = [
            Challenge("c1", ChallengeSeverity.CRITICAL, 0.49),
            Challenge("c2", ChallengeSeverity.CRITICAL, 0.50),
            Challenge("c3", ChallengeSeverity.CRITICAL, 0.51),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(
            generator, confidence_threshold=0.50
        )
        
        result = orchestrator.process_challenges({"dummy": "context"})
        
        # Should include 0.50 and 0.51, exclude 0.49
        assert len(result) == 2
        assert all(c.confidence >= 0.50 for c in result)
    
    def test_single_challenge_returned_unchanged(self):
        """Test single challenge is returned unchanged."""
        challenges = [Challenge("single", ChallengeSeverity.HIGH, 0.6)]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(generator)
        
        result = orchestrator.process_challenges({"dummy": "context"})
        
        assert len(result) == 1
        assert result[0].description == "single"
    
    def test_challenges_with_empty_mitigation(self):
        """Test challenges with empty mitigation strings."""
        challenges = [
            Challenge("no_mitigation", ChallengeSeverity.HIGH, 0.6, mitigation=""),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(generator)
        
        result = orchestrator.process_challenges({"dummy": "context"})
        
        assert len(result) == 1
        assert result[0].mitigation == ""
    
    def test_challenges_with_code_context(self):
        """Test challenges preserve code context."""
        code_ctx = "def foo(): pass"
        challenges = [
            Challenge("with_context", ChallengeSeverity.HIGH, 0.6, 
                     code_context=code_ctx),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(generator)
        
        result = orchestrator.process_challenges({"dummy": "context"})
        
        assert len(result) == 1
        assert result[0].code_context == code_ctx
    
    def test_sort_stability_within_same_severity(self):
        """Test sort stability: same severity maintains order."""
        challenges = [
            Challenge("high1", ChallengeSeverity.HIGH, 0.5),
            Challenge("high2", ChallengeSeverity.HIGH, 0.6),
            Challenge("high3", ChallengeSeverity.HIGH, 0.4),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(generator)
        
        result = orchestrator.process_challenges({"dummy": "context"})
        
        # All HIGH severity, should maintain insertion order
        assert len(result) == 3
        assert result[0].description == "high1"
        assert result[1].description == "high2"
        assert result[2].description == "high3"
    
    def test_default_confidence_threshold_0_30(self):
        """Test default confidence threshold is 0.30."""
        challenges = [
            Challenge("low", ChallengeSeverity.HIGH, 0.29),
            Challenge("high", ChallengeSeverity.HIGH, 0.31),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(generator)
        
        result = orchestrator.process_challenges({"dummy": "context"})
        
        assert len(result) == 1
        assert result[0].description == "high"
    
    def test_custom_confidence_threshold_respected(self):
        """Test custom confidence threshold is respected."""
        challenges = [
            Challenge("low", ChallengeSeverity.HIGH, 0.49),
            Challenge("high", ChallengeSeverity.HIGH, 0.51),
        ]
        generator = MockChallengeGenerator(challenges)
        orchestrator = ChallengeIntegrationOrchestrator(
            generator, confidence_threshold=0.50
        )
        
        result = orchestrator.process_challenges({"dummy": "context"})
        
        assert len(result) == 1
        assert result[0].confidence == 0.51
