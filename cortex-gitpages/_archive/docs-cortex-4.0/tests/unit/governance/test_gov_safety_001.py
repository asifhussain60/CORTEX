"""
Test suite for CORE-031: Hallucination Detection & Confidence Scoring.

Validates:
- Confidence scoring with minimum 0.75 threshold
- Fact verification against knowledge base
- Hallucination detection and risk assessment
- Reasoning trace extraction
- Recommendations generation
"""

import pytest
from src.core.governance.hallucination_detector import (
    HallucinationDetector,
    ConfidenceScore,
    ConfidenceLevel,
    HallucinationDetectionResult,
    HallucinationRisk,
)


class TestConfidenceScoring:
    """Tests for confidence scoring functionality."""
    
    def test_confidence_score_creation(self):
        """Test confidence score creation with valid parameters."""
        score = ConfidenceScore(
            value=0.85,
            reasoning="Based on verified sources",
            fact_checks=["fact1", "fact2"],
            evidence_sources=["source1"]
        )
        assert score.value == 0.85
        assert score.reasoning == "Based on verified sources"
        assert len(score.fact_checks) == 2
    
    def test_confidence_level_very_low(self):
        """Test confidence level classification - very low."""
        score = ConfidenceScore(value=0.15, reasoning="Low confidence")
        assert score.get_level() == ConfidenceLevel.VERY_LOW
    
    def test_confidence_level_low(self):
        """Test confidence level classification - low."""
        score = ConfidenceScore(value=0.35, reasoning="Low confidence")
        assert score.get_level() == ConfidenceLevel.LOW
    
    def test_confidence_level_medium(self):
        """Test confidence level classification - medium."""
        score = ConfidenceScore(value=0.60, reasoning="Medium confidence")
        assert score.get_level() == ConfidenceLevel.MEDIUM
    
    def test_confidence_level_high(self):
        """Test confidence level classification - high."""
        score = ConfidenceScore(value=0.80, reasoning="High confidence")
        assert score.get_level() == ConfidenceLevel.HIGH
    
    def test_confidence_level_very_high(self):
        """Test confidence level classification - very high."""
        score = ConfidenceScore(value=0.95, reasoning="Very high confidence")
        assert score.get_level() == ConfidenceLevel.VERY_HIGH


class TestHallucinationDetector:
    """Tests for hallucination detector."""
    
    def test_detector_initialization(self):
        """Test detector initialization."""
        detector = HallucinationDetector()
        assert detector.confidence_threshold == 0.75
        assert len(detector.knowledge_base) == 0
        assert len(detector.detection_history) == 0
    
    def test_add_to_knowledge_base(self):
        """Test adding facts to knowledge base."""
        detector = HallucinationDetector()
        facts = ["Paris is the capital of France", "Earth is round"]
        detector.add_to_knowledge_base(facts)
        assert len(detector.knowledge_base) == 2
        assert "Paris is the capital of France" in detector.knowledge_base
    
    def test_score_confidence_with_valid_inputs(self):
        """Test confidence scoring with valid inputs."""
        detector = HallucinationDetector()
        score = detector.score_confidence(
            output="Test output",
            reasoning="This is a long reasoning that spans more than fifty characters total",
            fact_checks=[]
        )
        assert score.value >= 0.0
        assert score.value <= 1.0
    
    def test_score_confidence_empty_output(self):
        """Test confidence scoring with empty output."""
        detector = HallucinationDetector()
        score = detector.score_confidence(
            output="",
            reasoning="No output provided"
        )
        assert score.value == 0.0
    
    def test_score_confidence_empty_reasoning(self):
        """Test confidence scoring with empty reasoning."""
        detector = HallucinationDetector()
        score = detector.score_confidence(
            output="Some output",
            reasoning=""
        )
        assert score.value == 0.0
    
    def test_score_confidence_with_verified_facts(self):
        """Test confidence scoring with verified facts."""
        detector = HallucinationDetector()
        detector.add_to_knowledge_base([
            "Paris is the capital of France",
            "Earth is round"
        ])
        
        score = detector.score_confidence(
            output="Paris is the capital",
            reasoning="This is based on geographic knowledge that is well established",
            fact_checks=["Paris is the capital of France", "Earth is round"]
        )
        # Should have higher confidence with verified facts
        assert score.value > 0.5
    
    def test_score_confidence_with_unverified_facts(self):
        """Test confidence scoring with unverified facts."""
        detector = HallucinationDetector()
        detector.add_to_knowledge_base(["Paris is the capital of France"])
        
        score = detector.score_confidence(
            output="Unknown fact",
            reasoning="Short reasoning",
            fact_checks=["Unknown fact", "Another unknown"]
        )
        # Should have lower confidence with unverified facts
        assert score.value < 0.7


class TestHallucinationDetection:
    """Tests for hallucination detection."""
    
    def test_detect_hallucinations_safe_output(self):
        """Test detection with safe output."""
        detector = HallucinationDetector()
        detector.add_to_knowledge_base(["Paris is the capital of France"])
        
        result = detector.detect_hallucinations(
            output="Paris is the capital",
            reasoning="Based on geographic knowledge that is well-established and verified",
            fact_checks=["Paris is the capital of France"]
        )
        
        assert result.success
        assert result.value.is_safe
        assert result.value.hallucination_risk == HallucinationRisk.SAFE or result.value.hallucination_risk == HallucinationRisk.LOW
    
    def test_detect_hallucinations_empty_output(self):
        """Test detection with empty output."""
        detector = HallucinationDetector()
        result = detector.detect_hallucinations(
            output="",
            reasoning="No output"
        )
        assert not result.success
        assert result.error == "Output cannot be empty"
    
    def test_detect_hallucinations_with_unverified_facts(self):
        """Test detection with unverified facts."""
        detector = HallucinationDetector()
        detector.add_to_knowledge_base(["Fact A is true"])
        
        result = detector.detect_hallucinations(
            output="Unknown fact",
            reasoning="Based on something",
            fact_checks=["Fact B is true", "Fact C is true"]
        )
        
        assert result.success
        assert len(result.value.detected_hallucinations) > 0
    
    def test_detection_history_tracking(self):
        """Test that detection history is tracked."""
        detector = HallucinationDetector()
        
        result1 = detector.detect_hallucinations(
            output="Output 1",
            reasoning="Reasoning 1"
        )
        result2 = detector.detect_hallucinations(
            output="Output 2",
            reasoning="Reasoning 2"
        )
        
        assert len(detector.detection_history) == 2


class TestRiskAssessment:
    """Tests for hallucination risk assessment."""
    
    def test_risk_safe(self):
        """Test SAFE risk classification."""
        detector = HallucinationDetector()
        risk = detector._assess_risk(confidence=0.95, hallucinations=[])
        assert risk == HallucinationRisk.SAFE
    
    def test_risk_low(self):
        """Test LOW risk classification."""
        detector = HallucinationDetector()
        risk = detector._assess_risk(confidence=0.80, hallucinations=[])
        assert risk == HallucinationRisk.LOW
    
    def test_risk_medium(self):
        """Test MEDIUM risk classification."""
        detector = HallucinationDetector()
        risk = detector._assess_risk(confidence=0.65, hallucinations=["halluc1"])
        assert risk == HallucinationRisk.MEDIUM
    
    def test_risk_high(self):
        """Test HIGH risk classification."""
        detector = HallucinationDetector()
        risk = detector._assess_risk(confidence=0.45, hallucinations=["halluc1", "halluc2"])
        assert risk == HallucinationRisk.HIGH
    
    def test_risk_critical(self):
        """Test CRITICAL risk classification."""
        detector = HallucinationDetector()
        risk = detector._assess_risk(confidence=0.20, hallucinations=["halluc1", "halluc2"])
        assert risk == HallucinationRisk.CRITICAL


class TestReasoningTraces:
    """Tests for reasoning trace extraction."""
    
    def test_extract_reasoning_steps(self):
        """Test extraction of reasoning steps."""
        detector = HallucinationDetector()
        reasoning = "First step. Second step. Third step."
        steps = detector._extract_reasoning_steps(reasoning)
        assert len(steps) == 3
        assert "First step" in steps
    
    def test_extract_reasoning_empty(self):
        """Test extraction with empty reasoning."""
        detector = HallucinationDetector()
        steps = detector._extract_reasoning_steps("")
        assert len(steps) == 0
    
    def test_extract_sources_from_reasoning(self):
        """Test extraction of evidence sources."""
        detector = HallucinationDetector()
        reasoning = "Based on verified sources from the knowledge base"
        sources = detector._extract_sources(reasoning)
        assert len(sources) > 0


class TestRecommendations:
    """Tests for recommendation generation."""
    
    def test_recommendations_safe_output(self):
        """Test recommendations for safe output."""
        detector = HallucinationDetector()
        recommendations = detector._generate_recommendations(
            is_safe=True,
            risk_level=HallucinationRisk.SAFE
        )
        assert len(recommendations) == 0
    
    def test_recommendations_critical_risk(self):
        """Test recommendations for critical risk."""
        detector = HallucinationDetector()
        recommendations = detector._generate_recommendations(
            is_safe=False,
            risk_level=HallucinationRisk.CRITICAL
        )
        assert len(recommendations) > 0
        assert any("retry" in rec.lower() for rec in recommendations)
    
    def test_recommendations_high_risk(self):
        """Test recommendations for high risk."""
        detector = HallucinationDetector()
        recommendations = detector._generate_recommendations(
            is_safe=False,
            risk_level=HallucinationRisk.HIGH
        )
        assert len(recommendations) > 0
        assert any("review" in rec.lower() for rec in recommendations)
    
    def test_recommendations_medium_risk(self):
        """Test recommendations for medium risk."""
        detector = HallucinationDetector()
        recommendations = detector._generate_recommendations(
            is_safe=False,
            risk_level=HallucinationRisk.MEDIUM
        )
        assert len(recommendations) > 0
        assert any("validate" in rec.lower() for rec in recommendations)


class TestDetectionSummary:
    """Tests for detection summary."""
    
    def test_summary_empty_history(self):
        """Test summary with empty detection history."""
        detector = HallucinationDetector()
        summary = detector.get_detection_summary()
        assert summary["total_detections"] == 0
        assert summary["safe_outputs"] == 0
        assert summary["average_confidence"] == 0.0
    
    def test_summary_with_detections(self):
        """Test summary with detection history."""
        detector = HallucinationDetector()
        detector.add_to_knowledge_base(["Fact 1"])
        
        detector.detect_hallucinations(
            output="Output 1",
            reasoning="Reasoning 1",
            fact_checks=["Fact 1"]
        )
        detector.detect_hallucinations(
            output="Output 2",
            reasoning="Reasoning 2"
        )
        
        summary = detector.get_detection_summary()
        assert summary["total_detections"] == 2
        assert "average_confidence" in summary


class TestConfidenceThreshold:
    """Tests for confidence threshold validation."""
    
    def test_confidence_threshold_meets_minimum(self):
        """Test that output meets confidence threshold."""
        detector = HallucinationDetector()
        detector.add_to_knowledge_base(["Known fact"])
        
        result = detector.detect_hallucinations(
            output="Output",
            reasoning="Long reasoning with substantial length and detail to increase confidence score significantly",
            fact_checks=["Known fact"]
        )
        
        assert result.success
        assert result.value.confidence_score.value >= detector.confidence_threshold or result.value.hallucination_risk in [HallucinationRisk.SAFE, HallucinationRisk.LOW]
    
    def test_confidence_threshold_not_met(self):
        """Test that unsafe output is flagged."""
        detector = HallucinationDetector()
        
        result = detector.detect_hallucinations(
            output="Output",
            reasoning="X",
            fact_checks=["Unknown fact 1", "Unknown fact 2"]
        )
        
        assert result.success
        # With unverified facts and short reasoning, should flag as unsafe
        assert result.value.hallucination_risk in [HallucinationRisk.HIGH, HallucinationRisk.CRITICAL] or result.value.confidence_score.value < detector.confidence_threshold


class TestIntegration:
    """Integration tests for hallucination detection."""
    
    def test_end_to_end_safe_output(self):
        """Test end-to-end detection of safe output."""
        detector = HallucinationDetector()
        detector.add_to_knowledge_base([
            "Paris is the capital of France",
            "France is in Europe",
            "Europe is a continent"
        ])
        
        result = detector.detect_hallucinations(
            output="Paris is in Europe",
            reasoning="Paris is the capital of France. France is located in Europe. Therefore Paris is in Europe.",
            fact_checks=[
                "Paris is the capital of France",
                "France is in Europe"
            ]
        )
        
        assert result.success
        assert result.value.is_safe or result.value.confidence_score.value >= 0.75
    
    def test_end_to_end_unsafe_output(self):
        """Test end-to-end detection of unsafe output."""
        detector = HallucinationDetector()
        detector.add_to_knowledge_base(["Paris is the capital of France"])
        
        result = detector.detect_hallucinations(
            output="Mars is the capital of France",
            reasoning="Short",
            fact_checks=["Mars is a planet", "Mars is the capital of something"]
        )
        
        assert result.success
        # Output has unverified facts and low confidence
        assert not result.value.is_safe or result.value.hallucination_risk in [HallucinationRisk.HIGH, HallucinationRisk.CRITICAL]
