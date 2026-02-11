"""
Similarity Checker for Enhancement Deduplication.

Phase 41 Stage 5 (ENH-054):
Semantic similarity checking using sentence-transformers.

Detects duplicate/similar enhancements via:
- Sentence embeddings (sentence-transformers)
- Cosine similarity calculation
- Threshold-based deduplication
- Historical enhancement checking

Author: Asif Hussain
Date: 2026-02-07
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)
import numpy as np


class SimilarityChecker:
    """
    Check semantic similarity between enhancement descriptions.

    Uses sentence-transformers for semantic embeddings and
    cosine similarity for comparison.

    Usage:
        checker = SimilarityChecker()
        similarity = checker.calculate_similarity(desc1, desc2)
        is_dup = checker.is_duplicate(new_desc, existing_descs, threshold=0.7)
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize SimilarityChecker.

        Args:
            model_name: Sentence-transformers model name
        """
        self.model_name = model_name
        self._model: Optional[Any] = None  # Lazy initialization
        self.use_embeddings = False  # Will be True if model loads

    def _load_model(self) -> bool:
        """Lazy-load sentence-transformers model. Returns True if successful."""
        if self._model is not None:
            return True

        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name)
            self.use_embeddings = True
            return True
        except Exception as e:
            logger.warning(f"Failed to load sentence-transformers model: {e}")
            self.use_embeddings = False
            return False

    def calculate_similarity(self, desc1: str, desc2: str) -> float:
        """
        Calculate semantic similarity between two descriptions.

        Args:
            desc1: First description
            desc2: Second description

        Returns:
            Similarity score (0-1, where 1 = identical)
        """
        # Try to load model if not already loaded
        if self._load_model() and self._model is not None:
            # Use sentence embeddings
            embeddings = self._model.encode([desc1, desc2])
            similarity = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            return float(similarity)
        else:
            # Fallback: simple word overlap
            words1 = set(desc1.lower().split())
            words2 = set(desc2.lower().split())

            if not words1 or not words2:
                return 0.0

            intersection = words1.intersection(words2)
            union = words1.union(words2)

            return len(intersection) / len(union)

    def is_duplicate(
        self,
        new_description: str,
        existing_descriptions: List[str],
        threshold: float = 0.7
    ) -> bool:
        """
        Check if new description is duplicate of existing ones.

        Args:
            new_description: New enhancement description
            existing_descriptions: List of existing descriptions
            threshold: Similarity threshold (0-1)

        Returns:
            True if duplicate (similarity >= threshold)
        """
        for existing in existing_descriptions:
            similarity = self.calculate_similarity(new_description, existing)
            if similarity >= threshold:
                return True

        return False

    def check_history(
        self,
        new_description: str,
        history_file: Path,
        threshold: float = 0.7
    ) -> bool:
        """
        Check if description duplicates entry in enhancement-history.yaml.

        Args:
            new_description: New enhancement description
            history_file: Path to enhancement-history.yaml
            threshold: Similarity threshold

        Returns:
            True if duplicate found in history
        """
        if not history_file.exists():
            return False

        with open(history_file) as f:
            history = yaml.safe_load(f) or {}

        enhancements = history.get("enhancements", [])
        existing_descriptions = [e.get("description", "") for e in enhancements]

        return self.is_duplicate(new_description, existing_descriptions, threshold)

    def check_rejected(
        self,
        new_description: str,
        history_file: Path,
        threshold: float = 0.6
    ) -> bool:
        """
        Check if description matches rejected recommendation.

        Args:
            new_description: New enhancement description
            history_file: Path to enhancement-history.yaml
            threshold: Similarity threshold (lower for rejected)

        Returns:
            True if matches rejected recommendation
        """
        if not history_file.exists():
            return False

        with open(history_file) as f:
            history = yaml.safe_load(f) or {}

        rejected = history.get("rejected_recommendations", [])
        rejected_descriptions = [r.get("description", "") for r in rejected]

        return self.is_duplicate(new_description, rejected_descriptions, threshold)

    def check_with_scores(
        self,
        new_description: str,
        existing_descriptions: List[str],
        threshold: float = 0.7
    ) -> Dict[str, Any]:
        """
        Check for duplicates and return similarity scores.

        Args:
            new_description: New enhancement description
            existing_descriptions: List of existing descriptions
            threshold: Similarity threshold

        Returns:
            Dict with is_duplicate, max_similarity, similar_to
        """
        if not existing_descriptions:
            return {
                "is_duplicate": False,
                "max_similarity": 0.0,
                "similar_to": None
            }

        scores = []
        for existing in existing_descriptions:
            similarity = self.calculate_similarity(new_description, existing)
            scores.append((similarity, existing))

        max_similarity, most_similar = max(scores, key=lambda x: x[0])

        return {
            "is_duplicate": max_similarity >= threshold,
            "max_similarity": max_similarity,
            "similar_to": most_similar if max_similarity >= threshold else None
        }

    def deduplicate_batch(
        self,
        descriptions: List[str],
        threshold: float = 0.7
    ) -> List[str]:
        """
        Deduplicate a batch of descriptions.

        Args:
            descriptions: List of descriptions
            threshold: Similarity threshold

        Returns:
            List of unique descriptions
        """
        if not descriptions:
            return []

        unique = [descriptions[0]]

        for desc in descriptions[1:]:
            if not self.is_duplicate(desc, unique, threshold):
                unique.append(desc)

        return unique
