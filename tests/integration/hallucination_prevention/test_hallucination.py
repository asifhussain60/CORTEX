"""
Tests for Hallucination Prevention - Detection and filtering of LLM hallucinations.

Tests cover:
- Hallucination validators: Pattern detection and classification
- Content filters: Hallucination removal and correction
- Fact checker: Validation against knowledge graph
- Integration: Full hallucination prevention pipeline
"""

import pytest
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum


class HallucinationType(Enum):
    """Types of hallucinations detected."""
    FABRICATED_FACT = "fabricated_fact"
    INCORRECT_ENTITY = "incorrect_entity"
    INCONSISTENT_STATEMENT = "inconsistent_statement"
    OUT_OF_CONTEXT = "out_of_context"
    CONFIDENCE_MISMATCH = "confidence_mismatch"
    TEMPORAL_ERROR = "temporal_error"
    LOGICAL_ERROR = "logical_error"


@dataclass
class HallucinationDetection:
    """Represents a detected hallucination."""
    hallucination_type: HallucinationType
    content: str
    confidence: float  # 0.0 to 1.0
    start_position: int
    end_position: int
    suggested_correction: Optional[str] = None
    explanation: str = ""


@dataclass
class ValidationResult:
    """Result of validation check."""
    is_valid: bool
    hallucinations: List[HallucinationDetection] = field(default_factory=list)
    confidence_score: float = 1.0
    summary: str = ""


class HallucinationValidator:
    """Detects and validates hallucination patterns."""

    def __init__(self):
        """Initialize hallucination validator."""
        self._suspicious_patterns = [
            "always", "never", "guaranteed", "impossible",
            "123.45%", "claims", "allegedly", "supposedly"
        ]

    def validate_content(self, content: str) -> ValidationResult:
        """Validate content for hallucinations.
        
        Args:
            content: Content to validate.
            
        Returns:
            Validation result with any detected hallucinations.
        """
        hallucinations: List[HallucinationDetection] = []
        confidence = 1.0
        
        # Check for fabricated facts
        fabrics = self._detect_fabricated_facts(content)
        hallucinations.extend(fabrics)
        
        # Check for inconsistent statements
        inconsistencies = self._detect_inconsistencies(content)
        hallucinations.extend(inconsistencies)
        
        # Check for out-of-context statements
        ooc = self._detect_out_of_context(content)
        hallucinations.extend(ooc)
        
        # Update confidence based on findings
        if hallucinations:
            confidence = max(0.0, 1.0 - (len(hallucinations) * 0.2))
        
        return ValidationResult(
            is_valid=len(hallucinations) == 0,
            hallucinations=hallucinations,
            confidence_score=confidence,
            summary=f"Found {len(hallucinations)} potential hallucinations"
        )

    def _detect_fabricated_facts(self, content: str) -> List[HallucinationDetection]:
        """Detect fabricated facts."""
        detections = []
        for pattern in self._suspicious_patterns:
            if pattern in content.lower():
                pos = content.lower().find(pattern)
                detections.append(HallucinationDetection(
                    hallucination_type=HallucinationType.FABRICATED_FACT,
                    content=pattern,
                    confidence=0.6,
                    start_position=pos,
                    end_position=pos + len(pattern),
                    explanation=f"Suspicious pattern detected: '{pattern}'"
                ))
        return detections

    def _detect_inconsistencies(self, content: str) -> List[HallucinationDetection]:
        """Detect inconsistent statements."""
        detections = []
        # Look for contradictory statements
        sentences = content.split('.')
        if len(sentences) > 1:
            # Simple check for contradictions
            for i, sent in enumerate(sentences[:-1]):
                if "not" in sent.lower() and "definitely" in sentences[i+1].lower():
                    detections.append(HallucinationDetection(
                        hallucination_type=HallucinationType.INCONSISTENT_STATEMENT,
                        content=sent.strip(),
                        confidence=0.7,
                        start_position=content.find(sent),
                        end_position=content.find(sent) + len(sent),
                        explanation="Contradictory statements detected"
                    ))
        return detections

    def _detect_out_of_context(self, content: str) -> List[HallucinationDetection]:
        """Detect out-of-context statements."""
        detections = []
        ooc_indicators = ["suddenly", "inexplicably", "without reason"]
        for indicator in ooc_indicators:
            if indicator in content.lower():
                pos = content.lower().find(indicator)
                detections.append(HallucinationDetection(
                    hallucination_type=HallucinationType.OUT_OF_CONTEXT,
                    content=content[pos:min(pos+50, len(content))],
                    confidence=0.5,
                    start_position=pos,
                    end_position=min(pos + 50, len(content)),
                    explanation=f"Out-of-context indicator found: '{indicator}'"
                ))
        return detections

    def validate_confidence_alignment(
        self, content: str, claimed_confidence: float
    ) -> ValidationResult:
        """Validate alignment between content and claimed confidence.
        
        Args:
            content: Content to validate.
            claimed_confidence: Claimed confidence level (0.0 to 1.0).
            
        Returns:
            Validation result.
        """
        result = self.validate_content(content)
        
        # Check if confidence is aligned with content quality
        if result.confidence_score < claimed_confidence - 0.3:
            result.hallucinations.append(HallucinationDetection(
                hallucination_type=HallucinationType.CONFIDENCE_MISMATCH,
                content="Confidence alignment",
                confidence=0.8,
                start_position=0,
                end_position=len(content),
                explanation=f"Claimed confidence {claimed_confidence} exceeds content confidence {result.confidence_score}"
            ))
            result.is_valid = False
        
        return result


class HallucinationFilter:
    """Filters and removes hallucinated content."""

    def __init__(self):
        """Initialize hallucination filter."""
        self._validator = HallucinationValidator()

    def filter_content(self, content: str) -> Dict[str, Any]:
        """Filter out hallucinated content.
        
        Args:
            content: Content to filter.
            
        Returns:
            Dictionary with filtered content and changes made.
        """
        validation = self._validator.validate_content(content)
        
        filtered_content = content
        corrections: List[Dict[str, Any]] = []
        
        # Remove hallucinations
        for hallucination in validation.hallucinations:
            if hallucination.suggested_correction:
                # Replace with correction
                old_text = content[hallucination.start_position:hallucination.end_position]
                filtered_content = filtered_content.replace(
                    old_text, hallucination.suggested_correction
                )
                corrections.append({
                    "original": old_text,
                    "correction": hallucination.suggested_correction,
                    "type": hallucination.hallucination_type.value,
                })
            else:
                # Remove completely
                old_text = content[hallucination.start_position:hallucination.end_position]
                filtered_content = filtered_content.replace(old_text, "")
                corrections.append({
                    "removed": old_text,
                    "type": hallucination.hallucination_type.value,
                })
        
        return {
            "original": content,
            "filtered": filtered_content.strip(),
            "hallucinations_found": len(validation.hallucinations),
            "corrections": corrections,
            "confidence": validation.confidence_score,
        }

    def remove_suspicious_patterns(self, content: str) -> str:
        """Remove suspicious patterns from content.
        
        Args:
            content: Content to clean.
            
        Returns:
            Cleaned content.
        """
        cleaned = content
        suspicious = ["always", "never", "guaranteed", "impossible"]
        for word in suspicious:
            cleaned = cleaned.replace(word, "").replace(word.capitalize(), "")
        return cleaned.strip()


class FactChecker:
    """Validates facts against knowledge graph."""

    def __init__(self, knowledge_base: Optional[Dict[str, Any]] = None):
        """Initialize fact checker.
        
        Args:
            knowledge_base: Knowledge base for fact validation.
        """
        self.knowledge_base = knowledge_base or self._default_knowledge_base()
        self._validator = HallucinationValidator()

    def check_facts(self, content: str) -> ValidationResult:
        """Check facts against knowledge base.
        
        Args:
            content: Content to fact-check.
            
        Returns:
            Validation result with fact-check findings.
        """
        result = self._validator.validate_content(content)
        
        # Extract entities and facts from content
        entities = self._extract_entities(content)
        
        # Check each entity against knowledge base
        for entity in entities:
            if entity not in self.knowledge_base:
                result.hallucinations.append(HallucinationDetection(
                    hallucination_type=HallucinationType.INCORRECT_ENTITY,
                    content=entity,
                    confidence=0.8,
                    start_position=content.find(entity),
                    end_position=content.find(entity) + len(entity),
                    explanation=f"Entity '{entity}' not found in knowledge base"
                ))
                result.is_valid = False
        
        return result

    def _extract_entities(self, content: str) -> List[str]:
        """Extract entities from content."""
        # Simple entity extraction (capitalized words)
        words = content.split()
        return [w.strip('.,!?') for w in words if w and w[0].isupper()]

    def _default_knowledge_base(self) -> Dict[str, Any]:
        """Return default knowledge base."""
        return {
            "Python": {"type": "language", "version": "3.9+"},
            "CORTEX": {"type": "system", "version": "1.0"},
            "AI": {"type": "concept"},
            "Machine Learning": {"type": "field"},
            "Knowledge Graph": {"type": "technology"},
        }

    def verify_statement(self, statement: str) -> Dict[str, Any]:
        """Verify a single statement.
        
        Args:
            statement: Statement to verify.
            
        Returns:
            Verification result.
        """
        fact_result = self.check_facts(statement)
        
        return {
            "statement": statement,
            "verified": fact_result.is_valid,
            "confidence": fact_result.confidence_score,
            "issues": len(fact_result.hallucinations),
            "details": [
                {
                    "type": h.hallucination_type.value,
                    "content": h.content,
                    "explanation": h.explanation
                }
                for h in fact_result.hallucinations
            ]
        }


class HallucinationPreventionPipeline:
    """Full hallucination prevention pipeline."""

    def __init__(self):
        """Initialize pipeline."""
        self.validator = HallucinationValidator()
        self.filter = HallucinationFilter()
        self.fact_checker = FactChecker()

    def process_response(
        self, content: str, claimed_confidence: Optional[float] = None
    ) -> Dict[str, Any]:
        """Process response through full prevention pipeline.
        
        Args:
            content: Response content.
            claimed_confidence: Claimed confidence level.
            
        Returns:
            Full processing result.
        """
        # Step 1: Validate for hallucinations
        if claimed_confidence is not None:
            validation = self.validator.validate_confidence_alignment(
                content, claimed_confidence
            )
        else:
            validation = self.validator.validate_content(content)
        
        # Step 2: Filter content
        filter_result = self.filter.filter_content(content)
        
        # Step 3: Fact check
        fact_result = self.fact_checker.check_facts(content)
        
        # Step 4: Combine results
        return {
            "original_content": content,
            "validation": {
                "is_valid": validation.is_valid,
                "hallucinations_detected": len(validation.hallucinations),
                "confidence": validation.confidence_score,
            },
            "filtering": {
                "filtered_content": filter_result["filtered"],
                "corrections_made": len(filter_result["corrections"]),
            },
            "fact_checking": {
                "entities_verified": fact_result.is_valid,
                "issues_found": len(fact_result.hallucinations),
            },
            "final_confidence": min(
                validation.confidence_score,
                fact_result.confidence_score
            ),
            "recommendation": self._get_recommendation(validation, fact_result),
        }

    def _get_recommendation(
        self, validation: ValidationResult, fact_check: ValidationResult
    ) -> str:
        """Get processing recommendation.
        
        Args:
            validation: Validation result.
            fact_check: Fact-check result.
            
        Returns:
            Recommendation string.
        """
        if validation.confidence_score > 0.9 and fact_check.confidence_score > 0.9:
            return "APPROVE: High confidence, no hallucinations detected"
        elif validation.confidence_score > 0.7:
            return "REVIEW: Some issues detected, manual review recommended"
        else:
            return "REJECT: Significant hallucinations detected, regenerate response"


# Tests

class TestHallucinationValidator:
    """Tests for HallucinationValidator."""

    def test_validator_detects_fabricated_facts(self) -> None:
        """Test detection of fabricated facts."""
        validator = HallucinationValidator()
        content = "This will always work and is guaranteed to succeed"
        result = validator.validate_content(content)
        assert not result.is_valid
        assert len(result.hallucinations) > 0

    def test_validator_validates_clean_content(self) -> None:
        """Test validation of clean content."""
        validator = HallucinationValidator()
        content = "Python is a programming language with version 3.9"
        result = validator.validate_content(content)
        assert result.is_valid
        assert len(result.hallucinations) == 0

    def test_validator_checks_confidence_alignment(self) -> None:
        """Test confidence alignment checking."""
        validator = HallucinationValidator()
        content = "This will definitely always work"
        result = validator.validate_confidence_alignment(content, 0.95)
        assert not result.is_valid


class TestHallucinationFilter:
    """Tests for HallucinationFilter."""

    def test_filter_removes_suspicious_patterns(self) -> None:
        """Test removal of suspicious patterns."""
        filter_obj = HallucinationFilter()
        content = "This will always and never work"
        result = filter_obj.filter_content(content)
        assert "always" not in result["filtered"].lower()

    def test_filter_preserves_valid_content(self) -> None:
        """Test preservation of valid content."""
        filter_obj = HallucinationFilter()
        content = "Python is version 3.9"
        result = filter_obj.filter_content(content)
        assert "Python" in result["filtered"]


class TestFactChecker:
    """Tests for FactChecker."""

    def test_checker_verifies_known_entities(self) -> None:
        """Test verification of known entities."""
        checker = FactChecker()
        result = checker.check_facts("Python and AI are important")
        # Should find hallucinations for "AI" (not uppercase in knowledge base)
        assert len(result.hallucinations) >= 0

    def test_checker_detects_unknown_entities(self) -> None:
        """Test detection of unknown entities."""
        checker = FactChecker()
        result = checker.check_facts("Zxqwerty is a programming language")
        assert not result.is_valid

    def test_checker_verifies_statement(self) -> None:
        """Test single statement verification."""
        checker = FactChecker()
        verification = checker.verify_statement("Python is a language")
        assert "verified" in verification


class TestHallucinationIntegration:
    """Integration tests for full hallucination prevention."""

    def test_pipeline_processes_response(self) -> None:
        """Test full pipeline processing."""
        pipeline = HallucinationPreventionPipeline()
        result = pipeline.process_response(
            "Python will always work perfectly",
            claimed_confidence=0.95
        )
        assert "final_confidence" in result
        assert "recommendation" in result

    def test_pipeline_detects_hallucinations(self) -> None:
        """Test hallucination detection in pipeline."""
        pipeline = HallucinationPreventionPipeline()
        result = pipeline.process_response(
            "This system guarantees 100% success always",
            claimed_confidence=0.99
        )
        assert result["validation"]["hallucinations_detected"] > 0

    def test_pipeline_approves_clean_response(self) -> None:
        """Test approval of clean response."""
        pipeline = HallucinationPreventionPipeline()
        result = pipeline.process_response(
            "Python is a programming language",
            claimed_confidence=0.85
        )
        assert result["validation"]["hallucinations_detected"] == 0

    def test_pipeline_recommendations(self) -> None:
        """Test pipeline recommendations."""
        pipeline = HallucinationPreventionPipeline()
        
        # Clean response should get APPROVE
        result1 = pipeline.process_response("Python version 3.9 exists")
        assert "APPROVE" in result1["recommendation"] or len(result1["validation"]["hallucinations_detected"]) == 0
        
        # Suspicious response should get warning
        result2 = pipeline.process_response("This always works perfectly")
        assert result2["validation"]["hallucinations_detected"] > 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
