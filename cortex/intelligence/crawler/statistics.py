# AC_START: AC-PHASE58-S3-002
# Description: Pattern Statistics & Distribution Analysis
# Authority: CORE-008 TDD, CORE-011 type hints
# Stage: S3 - GREEN phase implementation

import math
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple


@dataclass
class ArchitectureFingerprint:
    """Unique fingerprint for architecture pattern distribution."""
    patterns: Dict[str, float]
    confidence: float
    hash_value: str = ""


class PatternDistribution:
    """
    Analyze frequency and co-occurrence of patterns across repositories.
    """

    def __init__(self):
        """Initialize PatternDistribution."""
        self.pattern_counts: Dict[str, int] = defaultdict(int)
        self.repository_patterns: Dict[str, Set[str]] = defaultdict(set)
        self.pattern_co_occurrences: Dict[Tuple[str, str], int] = defaultdict(int)

    def record_pattern(self, pattern_name: str, repository: str) -> None:
        """Record pattern discovery in repository."""
        self.pattern_counts[pattern_name] += 1
        self.repository_patterns[repository].add(pattern_name)

    def record_co_occurrence(self, pattern1: str, pattern2: str) -> None:
        """Record co-occurrence of two patterns."""
        key = tuple(sorted([pattern1, pattern2]))
        self.pattern_co_occurrences[key] += 1

    def get_frequency_analysis(self) -> Dict[str, int]:
        """Get pattern frequency analysis."""
        return dict(self.pattern_counts)

    def get_patterns_for_repository(self, repository: str) -> Set[str]:
        """Get patterns found in specific repository."""
        return self.repository_patterns.get(repository, set())

    def get_statistics(self) -> Dict[str, any]:
        """Get statistical summary."""
        total_patterns = sum(self.pattern_counts.values())

        return {
            "total_patterns_recorded": total_patterns,
            "unique_patterns": len(self.pattern_counts),
            "repositories": len(self.repository_patterns),
            "frequency": dict(self.pattern_counts),
        }


class ArchitectureProfiler:
    """
    Build architecture signatures and calculate similarity between repositories.
    """

    def __init__(self):
        """Initialize ArchitectureProfiler."""
        pass

    def build_signature(self, patterns: Dict[str, int]) -> Dict[str, float]:
        """
        Build normalized architecture signature from patterns.

        Args:
            patterns: Pattern frequency dictionary

        Returns:
            Normalized signature
        """
        if not patterns:
            return {}

        total = sum(patterns.values())
        return {k: v / total for k, v in patterns.items()}

    def calculate_similarity(self, sig1: Dict[str, float], sig2: Dict[str, float]) -> float:
        """
        Calculate cosine similarity between two signatures.

        Args:
            sig1: First signature
            sig2: Second signature

        Returns:
            Similarity score (0.0-1.0)
        """
        if not sig1 or not sig2:
            return 0.0

        # Get common patterns
        common_keys = set(sig1.keys()) & set(sig2.keys())

        if not common_keys:
            return 0.0

        # Cosine similarity
        dot_product = sum(sig1[k] * sig2[k] for k in common_keys)
        mag1 = math.sqrt(sum(v ** 2 for v in sig1.values()))
        mag2 = math.sqrt(sum(v ** 2 for v in sig2.values()))

        if mag1 == 0 or mag2 == 0:
            return 0.0

        return dot_product / (mag1 * mag2)

    def find_common_patterns(self, repo_patterns: Dict[str, Dict[str, int]]) -> Dict[str, float]:
        """Find patterns common across repositories."""
        if not repo_patterns:
            return {}

        pattern_repos = defaultdict(int)

        for repo, patterns in repo_patterns.items():
            for pattern in patterns.keys():
                pattern_repos[pattern] += 1

        total_repos = len(repo_patterns)

        return {
            pattern: count / total_repos
            for pattern, count in pattern_repos.items()
        }


class LearningModel:
    """
    Build learning models from pattern observations for future predictions.
    """

    def __init__(self):
        """Initialize LearningModel."""
        self.observations: List[str] = []
        self.pattern_frequency: Dict[str, int] = defaultdict(int)
        self.co_occurrence_matrix: Dict[Tuple[str, str], int] = defaultdict(int)

    def add_observation(self, pattern: str, context: str = "") -> None:
        """Add pattern observation."""
        self.observations.append(pattern)
        self.pattern_frequency[pattern] += 1

    def get_frequency_table(self) -> Dict[str, int]:
        """Get pattern frequency table."""
        return dict(self.pattern_frequency)

    def get_conditional_probability(self, pattern_a: str, pattern_b: str) -> Optional[float]:
        """
        Calculate P(A | B) - probability of A given B.

        Args:
            pattern_a: Target pattern
            pattern_b: Condition pattern

        Returns:
            Conditional probability or None
        """
        if pattern_b not in self.pattern_frequency:
            return None

        b_count = self.pattern_frequency[pattern_b]

        if b_count == 0:
            return None

        # Simple estimate: count co-occurrences
        key = tuple(sorted([pattern_a, pattern_b]))
        co_occur = self.co_occurrence_matrix.get(key, 0)

        return co_occur / b_count if b_count > 0 else 0.0

    def generate_fingerprint(self, patterns: Dict[str, int]) -> ArchitectureFingerprint:
        """
        Generate architecture fingerprint from pattern distribution.

        Args:
            patterns: Pattern counts

        Returns:
            Architecture fingerprint
        """
        total = sum(patterns.values())
        normalized = {k: v / total for k, v in patterns.items()} if total > 0 else {}

        # Simple hash of fingerprint
        hash_str = str(sorted(normalized.items()))

        return ArchitectureFingerprint(
            patterns=normalized,
            confidence=0.85,  # Default confidence
            hash_value=hash_str,
        )

# AC_COMPLETE: AC-PHASE58-S3-002 ✅
# Implementation: PatternDistribution + ArchitectureProfiler + LearningModel
# Status: READY FOR TESTING
