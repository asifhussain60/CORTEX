"""
ConversationProtocol data models.

Phase 103-h: extracted from conversation_protocol.py (1,539L) god-object.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict


class RequestComplexityClassifier:
    """
    Classifies request complexity to determine adaptive turn limits.

    AC-FUTURE-004: Adaptive turn limit based on task complexity

    Complexity levels:
    - SIMPLE  (2-3 turns): Single file edit, quick fix
    - MEDIUM  (5-8 turns): Multi-file changes, some refactoring
    - COMPLEX (10-15 turns): Major feature, heavy architecture changes
    - CRITICAL (20-25 turns): System-wide changes, multiple components
    """

    SIMPLE_KEYWORDS = ["fix", "typo", "bug", "edit", "single file", "one file"]
    MEDIUM_KEYWORDS = ["refactor", "improve", "implement feature", "modify", "update"]
    COMPLEX_KEYWORDS = ["architecture", "redesign", "rebuild", "multiple", "system", "orchestrator"]
    CRITICAL_KEYWORDS = ["rewrite", "migration", "consolidation", "governance", "complete system"]

    SIMPLE_MAX_WORDS = 20
    MEDIUM_MAX_WORDS = 50
    COMPLEX_MAX_WORDS = 100

    @staticmethod
    def classify(request: str) -> tuple[str, int]:
        """
        Classify request complexity and return (level, recommended_max_turns).

        AC-FUTURE-004: Adaptive turn limits
        """
        request_lower = request.lower().strip()
        word_count = len(request.split())
        kc = {"simple": 0, "medium": 0, "complex": 0, "critical": 0}

        for kw in RequestComplexityClassifier.SIMPLE_KEYWORDS:
            if kw in request_lower:
                kc["simple"] += 1
        for kw in RequestComplexityClassifier.MEDIUM_KEYWORDS:
            if kw in request_lower:
                kc["medium"] += 1
        for kw in RequestComplexityClassifier.COMPLEX_KEYWORDS:
            if kw in request_lower:
                kc["complex"] += 1
        for kw in RequestComplexityClassifier.CRITICAL_KEYWORDS:
            if kw in request_lower:
                kc["critical"] += 1

        if kc["critical"] > 0 or word_count > RequestComplexityClassifier.COMPLEX_MAX_WORDS:
            return "CRITICAL", 25
        elif kc["complex"] > 0 or word_count > RequestComplexityClassifier.MEDIUM_MAX_WORDS:
            return "COMPLEX", 15
        elif kc["medium"] > 0 or word_count > RequestComplexityClassifier.SIMPLE_MAX_WORDS:
            return "MEDIUM", 8
        else:
            return "SIMPLE", 3


@dataclass
class RoundContext:
    """Context for a single round of execution."""

    round_number: int
    user_input: str
    previous_context: Dict[str, Any]
    orchestrator_name: str
    timestamp: datetime = field(default_factory=datetime.now)
