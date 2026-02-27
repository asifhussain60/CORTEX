"""
Phase 87 — Recurrence Signature Engine
Generates canonical signatures for RCAAnalysis objects and computes
pairwise similarity to detect recurring failure patterns across sessions.

Signature format: SIG-{CATEGORY}-{HEX8}
Similarity algorithm: normalised character-level Levenshtein distance.

CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
CORE-028: snake_case filename
CORE-035: Single canonical implementation
"""

from __future__ import annotations

import hashlib
from typing import List

from cortex.intelligence.learning.rca_models import RCAAnalysis


class RecurrenceSignatureEngine:
    """Generate failure signatures and detect recurring RCA patterns.

    A signature is a stable, deterministic string derived from an RCAAnalysis
    that allows cross-session pattern matching.  Two analyses with similar
    root causes, categories, and methodologies produce high-similarity
    signatures even when their text wording differs slightly.
    """

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def generate_signature(self, rca: RCAAnalysis) -> str:
        """Generate a stable signature for an RCAAnalysis.

        The signature is deterministic: the same RCA always yields the same
        signature.  It encodes category, methodology, and a hash of the
        normalised root cause text.

        Args:
            rca: The RCAAnalysis to fingerprint.

        Returns:
            A signature string in the form 'SIG-{CATEGORY}-{HEX8}'.
        """
        normalised = self._normalise(rca.root_cause)
        payload = f"{rca.category.value}:{rca.methodology.value}:{normalised}"
        hex8 = hashlib.sha256(payload.encode()).hexdigest()[:8].upper()
        return f"SIG-{rca.category.value.upper()}-{hex8}"

    def similarity(self, sig_a: str, sig_b: str) -> float:
        """Compute normalised similarity between two signatures.

        Uses Levenshtein edit distance normalised by the length of the longer
        string to produce a value in [0.0, 1.0].

        Args:
            sig_a: First signature string.
            sig_b: Second signature string.

        Returns:
            Similarity score in [0.0, 1.0]; 1.0 means identical.
        """
        if sig_a == sig_b:
            return 1.0
        distance = self._levenshtein(sig_a, sig_b)
        max_len = max(len(sig_a), len(sig_b))
        if max_len == 0:
            return 1.0
        return 1.0 - (distance / max_len)

    def find_matches(
        self,
        signature: str,
        candidates: List[str],
        threshold: float = 0.85,
    ) -> List[str]:
        """Return all candidate signatures with similarity >= threshold.

        Args:
            signature: The query signature to match against.
            candidates: Pool of existing signatures to compare.
            threshold: Minimum similarity score to consider a match (0–1).

        Returns:
            A list of matching candidate signatures (may be empty).
        """
        return [
            c for c in candidates
            if self.similarity(signature, c) >= threshold
        ]

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _normalise(text: str) -> str:
        """Lowercase, strip punctuation, and collapse whitespace.

        Args:
            text: Raw text to normalise.

        Returns:
            Normalised string for consistent hashing.
        """
        import re
        text = text.lower()
        text = re.sub(r"[^a-z0-9\s]", " ", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _levenshtein(s: str, t: str) -> int:
        """Compute the Levenshtein edit distance between two strings.

        Args:
            s: Source string.
            t: Target string.

        Returns:
            Integer edit distance (insertions + deletions + substitutions).
        """
        m, n = len(s), len(t)
        # Use two-row DP to keep O(n) space
        prev = list(range(n + 1))
        curr = [0] * (n + 1)
        for i in range(1, m + 1):
            curr[0] = i
            for j in range(1, n + 1):
                cost = 0 if s[i - 1] == t[j - 1] else 1
                curr[j] = min(prev[j] + 1, curr[j - 1] + 1, prev[j - 1] + cost)
            prev, curr = curr, [0] * (n + 1)
        return prev[n]
