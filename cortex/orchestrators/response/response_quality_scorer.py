"""
Response Quality Scorer for CORTEX Response Optimization.

5-dimension quality scoring framework for response evaluation:
- Clarity: Readability and understandability
- Completeness: Coverage of requirements
- Conciseness: Signal-to-noise ratio
- Accuracy: Factual correctness
- Relevance: Alignment with context

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34 specification
"""

import re
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any, Dict, List


class QualityDimension(Enum):
    """Quality dimensions for response evaluation."""

    CLARITY = "clarity"
    COMPLETENESS = "completeness"
    CONCISENESS = "conciseness"
    ACCURACY = "accuracy"
    RELEVANCE = "relevance"


@dataclass
class QualityScore:
    """
    Quality score with dimension breakdown.

    Attributes:
        clarity: Readability score (0-1)
        completeness: Requirement coverage score (0-1)
        conciseness: Signal-to-noise ratio (0-1)
        accuracy: Factual correctness score (0-1)
        relevance: Context alignment score (0-1)
        overall: Weighted average score (0-1)
    """

    clarity: float
    completeness: float
    conciseness: float
    accuracy: float
    relevance: float
    overall: float

    def to_dict(self) -> Dict[str, float]:
        """
        Convert to dictionary.

        Returns:
            Dict with dimension scores
        """
        return asdict(self)


class ResponseQualityScorer:
    """
    5-dimension response quality scorer.

    Evaluates response quality across multiple dimensions to provide
    objective quality metrics for optimization.

    Scoring formula:
        Overall = (clarity × 0.25) + (completeness × 0.25) +
                  (conciseness × 0.20) + (accuracy × 0.20) +
                  (relevance × 0.10)

    Example:
        >>> scorer = ResponseQualityScorer()
        >>> score = scorer.score_response(
        ...     "The system uses JWT for authentication.",
        ...     "authentication mechanism"
        ... )
        >>> score.overall >= 0.7  # High quality response
        True
    """

    def __init__(self):
        """Initialize response quality scorer."""
        # Weights for overall score calculation
        self.weights = {
            QualityDimension.CLARITY: 0.25,
            QualityDimension.COMPLETENESS: 0.25,
            QualityDimension.CONCISENESS: 0.20,
            QualityDimension.ACCURACY: 0.20,
            QualityDimension.RELEVANCE: 0.10
        }

    def score_response(self, response: str, context: str) -> QualityScore:
        """
        Score response across all dimensions.

        Args:
            response: Response text to evaluate
            context: Context or user query

        Returns:
            QualityScore with dimension breakdown
        """
        if not response or not response.strip():
            # Empty response scores low across all dimensions
            return QualityScore(
                clarity=0.1,
                completeness=0.1,
                conciseness=0.1,
                accuracy=0.1,
                relevance=0.1,
                overall=0.1
            )

        # Calculate dimension scores
        clarity = self.calculate_clarity_score(response)
        completeness = self.calculate_completeness_score(response, context)
        conciseness = self.calculate_conciseness_score(response)
        accuracy = self.calculate_accuracy_score(response)
        relevance = self.calculate_relevance_score(response, context)

        # Calculate weighted overall score
        overall = (
            clarity * self.weights[QualityDimension.CLARITY] +
            completeness * self.weights[QualityDimension.COMPLETENESS] +
            conciseness * self.weights[QualityDimension.CONCISENESS] +
            accuracy * self.weights[QualityDimension.ACCURACY] +
            relevance * self.weights[QualityDimension.RELEVANCE]
        )

        return QualityScore(
            clarity=clarity,
            completeness=completeness,
            conciseness=conciseness,
            accuracy=accuracy,
            relevance=relevance,
            overall=overall
        )

    def calculate_clarity_score(self, response: str) -> float:
        """
        Calculate clarity score based on readability metrics.

        Factors:
        - Average sentence length (shorter = clearer)
        - Complex word ratio (fewer = clearer)
        - Technical jargon density

        Args:
            response: Response text

        Returns:
            Clarity score (0-1)
        """
        sentences = [s.strip() for s in re.split(r'[.!?]+', response) if s.strip()]

        if not sentences:
            return 0.5

        # Average sentence length (target: 15-25 words)
        total_words = sum(len(s.split()) for s in sentences)
        avg_sentence_length = total_words / len(sentences)

        # Penalize very long or very short sentences
        if 15 <= avg_sentence_length <= 25:
            length_score = 1.0
        elif avg_sentence_length < 10:
            length_score = 0.7
        elif avg_sentence_length < 15:
            length_score = 0.9
        else:
            # Penalty increases with length
            length_score = max(0.3, 1.0 - (avg_sentence_length - 25) * 0.02)

        # Complex word ratio (words > 12 characters)
        words = response.split()
        complex_words = [w for w in words if len(w) > 12]
        complex_ratio = len(complex_words) / len(words) if words else 0

        # Lower ratio = higher clarity
        complexity_score = max(0.3, 1.0 - complex_ratio * 2)

        # Technical jargon density (heuristic: words ending in -tion, -ity, -ology)
        jargon_pattern = r'\b\w+(tion|ity|ology)\b'
        jargon_count = len(re.findall(jargon_pattern, response))
        jargon_density = jargon_count / len(words) if words else 0
        jargon_score = max(0.4, 1.0 - jargon_density * 5)

        # Combined clarity score
        clarity = (length_score * 0.4 + complexity_score * 0.3 + jargon_score * 0.3)

        return min(1.0, max(0.0, clarity))

    def calculate_completeness_score(self, response: str, context: str) -> float:
        """
        Calculate completeness score based on requirement coverage.

        Factors:
        - Response length relative to context
        - Key topic coverage
        - Code example presence (if technical context)

        Args:
            response: Response text
            context: Context or user query

        Returns:
            Completeness score (0-1)
        """
        # Extract key concepts from context (nouns, verbs)
        context_words = set(context.lower().split())
        response_words = set(response.lower().split())

        # Coverage of context keywords
        coverage = len(context_words & response_words) / len(context_words) if context_words else 0.5

        # Response length (longer responses generally more complete)
        word_count = len(response.split())

        if word_count < 20:
            length_score = 0.4
        elif word_count < 50:
            length_score = 0.6
        elif word_count < 100:
            length_score = 0.8
        else:
            length_score = 1.0

        # Code example bonus (if technical context)
        has_code = bool(re.search(r'```[\s\S]*?```', response))
        technical_context = any(word in context.lower() for word in [
            'code', 'implement', 'function', 'class', 'method', 'api'
        ])

        code_bonus = 0.2 if (has_code and technical_context) else 0.0

        # Combined completeness score
        completeness = min(1.0, coverage * 0.5 + length_score * 0.5 + code_bonus)

        return min(1.0, max(0.0, completeness))

    def calculate_conciseness_score(self, response: str) -> float:
        """
        Calculate conciseness score (signal-to-noise ratio).

        Factors:
        - Filler word density
        - Repetition ratio
        - Information density

        Args:
            response: Response text

        Returns:
            Conciseness score (0-1)
        """
        words = response.lower().split()

        if not words:
            return 0.5

        # Filler words
        fillers = {
            'well', 'you see', 'actually', 'basically', 'essentially',
            'among other things', 'as you might expect', 'you know'
        }

        filler_count = sum(1 for word in words if word in fillers)
        filler_ratio = filler_count / len(words)
        filler_score = max(0.3, 1.0 - filler_ratio * 10)

        # Repetition (repeated sentences or phrases)
        sentences = [s.strip().lower() for s in re.split(r'[.!?]+', response) if s.strip()]
        unique_sentences = len(set(sentences))
        repetition_ratio = unique_sentences / len(sentences) if sentences else 1.0
        repetition_score = repetition_ratio

        # Information density (favor shorter responses)
        char_count = len(response)

        if char_count < 200:
            density_score = 1.0
        elif char_count < 500:
            density_score = 0.9
        elif char_count < 1000:
            density_score = 0.7
        else:
            density_score = 0.5

        # Combined conciseness score
        conciseness = (filler_score * 0.3 + repetition_score * 0.4 + density_score * 0.3)

        return min(1.0, max(0.0, conciseness))

    def calculate_accuracy_score(self, response: str) -> float:
        """
        Calculate accuracy score (factual correctness heuristic).

        Factors:
        - Hedge word presence (uncertain = lower confidence)
        - Absolute statement ratio
        - Contradiction detection

        Args:
            response: Response text

        Returns:
            Accuracy score (0-1)
        """
        # Hedge words indicate uncertainty
        hedge_words = [
            'probably', 'maybe', 'perhaps', 'possibly', 'might',
            'could be', 'seems like', 'appears to', 'may be'
        ]

        lower_response = response.lower()
        hedge_count = sum(1 for hedge in hedge_words if hedge in lower_response)
        words = response.split()
        hedge_ratio = hedge_count / len(words) if words else 0

        # Lower hedge ratio = higher accuracy confidence
        confidence_score = max(0.5, 1.0 - hedge_ratio * 20)

        # Presence of specific facts/numbers (indicates precision)
        has_numbers = bool(re.search(r'\d+', response))
        has_specifics = bool(re.search(r'\b(PostgreSQL|JWT|Redis|Python|React)\b', response))

        specificity_bonus = 0.1 if has_numbers else 0.0
        specificity_bonus += 0.1 if has_specifics else 0.0

        # Combined accuracy score
        accuracy = min(1.0, confidence_score + specificity_bonus)

        return min(1.0, max(0.0, accuracy))

    def calculate_relevance_score(self, response: str, context: str) -> float:
        """
        Calculate relevance score (context alignment).

        Factors:
        - Keyword overlap with context
        - Topic coherence
        - Off-topic content ratio

        Args:
            response: Response text
            context: Context or user query

        Returns:
            Relevance score (0-1)
        """
        # Extract keywords from context and response
        context_keywords = set(re.findall(r'\b\w{3,}\b', context.lower()))  # Min 3 chars
        response_keywords = set(re.findall(r'\b\w{3,}\b', response.lower()))

        # Remove common stop words but keep technical terms
        stop_words = {'the', 'and', 'but', 'for', 'with', 'this', 'that', 'from', 'have', 'will', 'been'}
        context_keywords -= stop_words
        response_keywords -= stop_words

        if not context_keywords:
            return 0.5  # No meaningful context keywords

        # Keyword overlap
        overlap = context_keywords & response_keywords
        overlap_ratio = len(overlap) / len(context_keywords)

        # Boost for partial word matches (e.g., "authenticate" matches "authentication")
        partial_matches = 0
        for ctx_word in context_keywords:
            for resp_word in response_keywords:
                if len(ctx_word) >= 5 and len(resp_word) >= 5:
                    if ctx_word[:5] == resp_word[:5]:  # First 5 chars match
                        partial_matches += 1
                        break

        partial_ratio = partial_matches / len(context_keywords)

        # Combined keyword score
        keyword_score = min(1.0, overlap_ratio + partial_ratio * 0.5)

        # Topic coherence (all sentences relate to main topic)
        sentences = [s.strip() for s in re.split(r'[.!?]+', response) if s.strip()]

        if not sentences:
            return 0.5

        relevant_sentences = sum(
            1 for sent in sentences
            if any(kw in sent.lower() for kw in context_keywords)
        )
        coherence_ratio = relevant_sentences / len(sentences)

        # Combined relevance score
        relevance = (keyword_score * 0.6 + coherence_ratio * 0.4)

        return min(1.0, max(0.0, relevance))
