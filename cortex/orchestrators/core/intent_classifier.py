"""
Three-tier Intent Classifier for IntentRouter.

AC-ID: AC-70-INTENT-CLASSIFIER-001
Phase 70 — GAP-70-A4: Replace single-strategy intent detection with a
layered pipeline:

    Tier 1 — Regex / exact-match  (deterministic, <1 ms, no I/O)
    Tier 2 — Keyword scoring       (statistical, <1 ms, no I/O)
    Tier 3 — LLM disambiguation    (semantic, ~200-500 ms, requires API key)

The classifier always returns a result: if the LLM is unavailable or
confidence is already high enough, the cheaper tiers short-circuit.

Governance:
    CORE-008: Tests written first (see tests/orchestrators/core/test_intent_classifier.py)
    CORE-011: Type hints on all functions
    CORE-012: Google-style docstrings
    CORE-013: Specific exception handling
    CORE-049: Silent degradation — LLM tier failure never raises; falls back
"""

from __future__ import annotations

import logging
import os
import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from cortex.models.canonical_enums import IntentType

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

#: Minimum confidence score from Tiers 1+2 before we skip Tier 3 LLM call.
LLM_SKIP_THRESHOLD: float = 0.72

#: Maximum tokens for the LLM intent classification prompt.
LLM_MAX_TOKENS: int = 50

#: Temperature for LLM call — near-zero for deterministic classification.
LLM_TEMPERATURE: float = 0.05

# ---------------------------------------------------------------------------
# Tier 1 — Regex / exact-match patterns
# ---------------------------------------------------------------------------

# Maps a compiled regex → (IntentType, base_confidence)
# Patterns are ordered from most-specific to least-specific so the first
# match wins.  Multi-word patterns take precedence over single-word ones.
_REGEX_PATTERNS: List[Tuple[re.Pattern[str], IntentType, float]] = [
    # Multi-word / high-specificity patterns first
    (re.compile(r"\b(investigate|root cause|trace the|debug why|find the cause)\b", re.I), IntentType.INVESTIGATE, 0.90),
    (re.compile(r"\b(digest|summarize|summarise|recap|tl;?dr)\b", re.I), IntentType.DIGEST, 0.88),
    (re.compile(r"\b(analyze|analyse|deep analysis|deep dive|inspect)\b", re.I), IntentType.ANALYZE, 0.85),
    (re.compile(r"\b(audit|production readiness|repo health|scan for issues)\b", re.I), IntentType.AUDIT, 0.88),
    (re.compile(r"\b(refactor|restructure|reorganize|simplify|modernize|rewrite|redesign)\b", re.I), IntentType.REFACTOR, 0.85),
    (re.compile(r"\b(design|architect|blueprint|system design|design pattern)\b", re.I), IntentType.DESIGN, 0.85),
    (re.compile(r"\b(plan|phase|roadmap|schedule|planning)\b", re.I), IntentType.PLAN, 0.82),
    (re.compile(r"\b(fix|bug|broken|patch|resolve|repair|crash|error|fail(?:ure|ing)?)\b", re.I), IntentType.FIX, 0.82),
    (re.compile(r"\b(implement|create|build|add|develop|construct|introduce)\b", re.I), IntentType.IMPLEMENT, 0.75),
    (re.compile(r"\b(document|docs|documentation)\b", re.I), IntentType.DOCUMENT, 0.80),
    (re.compile(r"\b(onboard|onboarding|bootstrap|initialize|register)\b", re.I), IntentType.ONBOARD, 0.85),
    (re.compile(r"\b(vacuum|cleanup|clean up|prune|purge|archive|compact)\b", re.I), IntentType.REFACTOR, 0.80),
    (re.compile(r"\b(golden test|workflow template|trace assertion|acceptance criteria)\b", re.I), IntentType.GOLDEN_TEST, 0.90),
    (re.compile(r"\b(rephrase|reword|token optim|compact this)\b", re.I), IntentType.REPHRASE, 0.88),
]

# ---------------------------------------------------------------------------
# Tier 2 — Keyword scoring
# ---------------------------------------------------------------------------

#: Maps IntentType → list of keywords; each match adds (1 / len(keywords)) score.
_KEYWORD_BAGS: Dict[IntentType, List[str]] = {
    IntentType.IMPLEMENT: [
        "create", "add", "new", "implement", "develop", "build", "construct",
        "establish", "introduce", "feature", "enhancement",
    ],
    IntentType.FIX: [
        "fix", "bug", "issue", "error", "problem", "crash", "fail", "broken",
        "resolve", "correct", "repair", "patch", "race condition",
    ],
    IntentType.REFACTOR: [
        "refactor", "improve", "cleanup", "restructure", "simplify", "optimize",
        "clean", "modernize", "reorganize", "rewrite", "redesign", "performance",
    ],
    IntentType.DOCUMENT: [
        "document", "docs", "documentation", "write", "report", "generate", "export",
    ],
    IntentType.ANALYZE: [
        "analyze", "analyse", "investigate", "inspect", "examine", "scan",
        "deep dive", "detect", "discover", "explore", "review", "check",
    ],
    IntentType.ONBOARD: [
        "onboard", "onboarding", "setup", "initialize", "bootstrap", "configure",
        "register", "integrate", "discover", "inventory",
    ],
    IntentType.PLAN: [
        "plan", "phase", "enhance cortex", "add to cortex", "modify cortex",
        "roadmap", "schedule", "cortex change", "cortex enhancement",
    ],
    IntentType.AUDIT: [
        "audit", "scan repo", "production readiness", "health check", "check repo",
        "/audit", "scan for issues", "repo health",
    ],
    IntentType.DESIGN: [
        "design", "architect", "architecture", "structure", "pattern", "blueprint",
        "system design", "design pattern",
    ],
    IntentType.DIGEST: [
        "digest", "summarize", "summarise", "summary", "recap", "synthesize",
        "tldr", "tl;dr", "what happened",
    ],
    IntentType.REPHRASE: [
        "rephrase", "reword", "token optimize", "optimize this prompt",
        "rewrite request", "make this concise", "compact this",
    ],
    IntentType.INVESTIGATE: [
        "investigate", "root cause", "why is", "what causes", "deep analysis",
        "trace the", "debug why", "find the cause",
    ],
    IntentType.GOLDEN_TEST: [
        "golden test", "golden tests", "workflow template", "workflow templates",
        "response template", "acceptance criteria", "e2e scenario", "trace assertion",
    ],
}

# ---------------------------------------------------------------------------
# LLM classification prompt
# ---------------------------------------------------------------------------

_LLM_SYSTEM_PROMPT = """\
You are an intent classifier for a software engineering AI assistant.
Classify the user request into exactly ONE of these intent labels:
IMPLEMENT, FIX, REFACTOR, DOCUMENT, ANALYZE, ONBOARD, PLAN, AUDIT, DESIGN, DIGEST, REPHRASE, INVESTIGATE, GOLDEN_TEST

Reply with ONLY the label — no punctuation, no explanation.\
"""

_LLM_USER_TEMPLATE = "Request: {request}"

# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class IntentClassificationResult:
    """Result from the three-tier intent classifier.

    Attributes:
        intent_type:   The winning IntentType.
        confidence:    Overall confidence [0.0, 1.0].
        tier_used:     Which tier produced the winning result (1, 2, or 3).
        tier1_match:   Regex match result if tier 1 fired (None otherwise).
        tier2_scores:  Per-intent keyword scores from tier 2.
        llm_raw:       Raw LLM response text if tier 3 was called.
        reasoning:     Human-readable explanation.
    """

    intent_type: IntentType
    confidence: float
    tier_used: int
    tier1_match: Optional[str] = None
    tier2_scores: Dict[str, float] = field(default_factory=dict)
    llm_raw: Optional[str] = None
    reasoning: str = ""


# ---------------------------------------------------------------------------
# Core classifier
# ---------------------------------------------------------------------------


class IntentClassifier:
    """Three-tier intent classifier combining regex, keyword scoring, and LLM.

    Usage::

        clf = IntentClassifier()
        result = clf.classify("fix the broken authentication handler")
        print(result.intent_type)   # IntentType.FIX
        print(result.confidence)    # 0.95
        print(result.tier_used)     # 1 (regex matched immediately)

    Tiers:
        1. Regex exact-match — fast, deterministic, highest priority.
        2. Keyword bag-of-words scoring — scores all intents, picks winner.
        3. LLM disambiguation — called only when Tiers 1+2 disagree or
           confidence < LLM_SKIP_THRESHOLD.  Requires an API key in the
           environment (OPENAI_API_KEY or ANTHROPIC_API_KEY).  Failure is
           silent — falls back to Tier 2 result (CORE-049).

    Governance:
        CORE-008 — tests in tests/orchestrators/core/test_intent_classifier.py
        CORE-011 — full type hints
        CORE-012 — Google docstrings
        CORE-013 — no bare except
        CORE-049 — silent degradation on LLM failure
    """

    def __init__(
        self,
        llm_skip_threshold: float = LLM_SKIP_THRESHOLD,
        enable_llm: bool = True,
        llm_provider: Optional[str] = None,
    ) -> None:
        """Initialise the classifier.

        Args:
            llm_skip_threshold: Confidence floor above which LLM tier is skipped.
            enable_llm: If False, Tier 3 is never called (useful in tests/CI).
            llm_provider: Force a provider name ("openai" / "anthropic").
                          When None, auto-detected from environment.
        """
        self.llm_skip_threshold = llm_skip_threshold
        self.enable_llm = enable_llm
        self._llm_provider_name = llm_provider
        self._llm: Optional[Any] = None  # lazy-loaded

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def classify(
        self,
        text: str,
        operation: str = "",
        extra_context: Optional[Dict[str, Any]] = None,
    ) -> IntentClassificationResult:
        """Classify a free-text request into an IntentType.

        Args:
            text:          Combined description + user_request text.
            operation:     Explicit operation field (e.g. "fix", "audit").
                           When non-empty and an exact enum match exists,
                           this short-circuits all tiers.
            extra_context: Optional additional context dict (unused by tiers
                           1/2, forwarded to LLM prompt as JSON if present).

        Returns:
            IntentClassificationResult with winning intent and metadata.
        """
        # ---- Explicit operation fast-path --------------------------------
        exact = self._exact_operation_match(operation)
        if exact is not None:
            return IntentClassificationResult(
                intent_type=exact,
                confidence=1.0,
                tier_used=0,
                reasoning=f"Exact operation match: '{operation}'",
            )

        combined = f"{operation} {text}".strip().lower()

        # ---- Tier 1: Regex ---------------------------------------------------
        t1_result = self._tier1_regex(combined)

        # ---- Tier 2: Keyword scoring ----------------------------------------
        t2_result, t2_scores = self._tier2_keywords(combined)

        # Decide whether tiers agree and whether confidence is high enough
        t1_confidence = t1_result[1] if t1_result else 0.0
        t2_confidence = t2_scores.get(t2_result.value, 0.0) if t2_result else 0.0

        tiers_agree = (t1_result is not None) and (t1_result[0] == t2_result)

        if tiers_agree:
            # Boost confidence when both tiers agree
            combined_confidence = min(1.0, t1_confidence * 0.6 + t2_confidence * 0.4 + 0.15)
            return IntentClassificationResult(
                intent_type=t1_result[0],
                confidence=combined_confidence,
                tier_used=1,
                tier1_match=t1_result[2],
                tier2_scores={k.value: v for k, v in t2_scores.items()},
                reasoning=(
                    f"Tier 1 regex matched '{t1_result[2]}' → {t1_result[0].value}; "
                    f"Tier 2 keyword scoring confirms (score={t2_confidence:.2f})"
                ),
            )

        # If tier 1 matched with high confidence, trust it even without tier 2 agreement
        if t1_result is not None and t1_confidence >= self.llm_skip_threshold:
            return IntentClassificationResult(
                intent_type=t1_result[0],
                confidence=t1_confidence,
                tier_used=1,
                tier1_match=t1_result[2],
                tier2_scores={k.value: v for k, v in t2_scores.items()},
                reasoning=(
                    f"Tier 1 regex matched '{t1_result[2]}' → {t1_result[0].value} "
                    f"with high confidence ({t1_confidence:.2f}); tier 2 skipped"
                ),
            )

        # Tier 2 best guess
        best_intent = t2_result or IntentType.IMPLEMENT
        best_confidence = t2_confidence if t2_result else 0.0

        # ---- Tier 3: LLM disambiguation ------------------------------------
        if self.enable_llm and best_confidence < self.llm_skip_threshold:
            llm_intent, llm_raw = self._tier3_llm(text, operation)
            if llm_intent is not None:
                # Blend LLM result with tier 2
                llm_confidence = min(1.0, best_confidence + 0.25)
                return IntentClassificationResult(
                    intent_type=llm_intent,
                    confidence=llm_confidence,
                    tier_used=3,
                    tier2_scores={k.value: v for k, v in t2_scores.items()},
                    llm_raw=llm_raw,
                    reasoning=(
                        f"LLM classified as {llm_intent.value} "
                        f"(tier 2 best was {best_intent.value} @ {best_confidence:.2f})"
                    ),
                )

        # Fallback: tier 2 winner (or IMPLEMENT)
        return IntentClassificationResult(
            intent_type=best_intent,
            confidence=best_confidence,
            tier_used=2,
            tier2_scores={k.value: v for k, v in t2_scores.items()},
            reasoning=f"Tier 2 keyword winner: {best_intent.value} (score={best_confidence:.2f})",
        )

    # ------------------------------------------------------------------
    # Tier implementations
    # ------------------------------------------------------------------

    def _exact_operation_match(self, operation: str) -> Optional[IntentType]:
        """Match explicit operation string to IntentType.

        Args:
            operation: Lowercase operation name from context dict.

        Returns:
            IntentType if exact match found, else None.
        """
        _EXACT: Dict[str, IntentType] = {
            "fix": IntentType.FIX,
            "audit": IntentType.AUDIT,
            "refactor": IntentType.REFACTOR,
            "design": IntentType.DESIGN,
            "plan": IntentType.PLAN,
            "investigate": IntentType.INVESTIGATE,
            "analyze": IntentType.ANALYZE,
            "analyse": IntentType.ANALYZE,
            "digest": IntentType.DIGEST,
            "implement": IntentType.IMPLEMENT,
            "create": IntentType.IMPLEMENT,
            "test": IntentType.IMPLEMENT,
            "migrate": IntentType.IMPLEMENT,
            "security": IntentType.AUDIT,
            "document": IntentType.DOCUMENT,
            "onboard": IntentType.ONBOARD,
            "rephrase": IntentType.REPHRASE,
        }
        return _EXACT.get(operation.strip().lower())

    def _tier1_regex(
        self, combined: str
    ) -> Optional[Tuple[IntentType, float, str]]:
        """Apply regex patterns in priority order.

        Args:
            combined: Lowercased combined text.

        Returns:
            (IntentType, confidence, matched_pattern_string) or None.
        """
        for pattern, intent, confidence in _REGEX_PATTERNS:
            m = pattern.search(combined)
            if m:
                return (intent, confidence, m.group(0))
        return None

    def _tier2_keywords(
        self, combined: str
    ) -> Tuple[Optional[IntentType], Dict[IntentType, float]]:
        """Score all intents via keyword bag-of-words.

        Args:
            combined: Lowercased combined text.

        Returns:
            (best_intent_or_None, scores_dict)
        """
        scores: Dict[IntentType, float] = {}
        for intent, keywords in _KEYWORD_BAGS.items():
            hits = sum(1 for kw in keywords if kw in combined)
            scores[intent] = hits / len(keywords) if keywords else 0.0

        if not scores or max(scores.values()) == 0.0:
            return None, scores

        best = max(scores, key=scores.__getitem__)
        return best, scores

    def _tier3_llm(
        self, text: str, operation: str
    ) -> Tuple[Optional[IntentType], Optional[str]]:
        """Call LLM to classify intent when tiers 1+2 are inconclusive.

        Fails silently (CORE-049) — returns (None, None) on any error.

        Args:
            text:      Raw user text.
            operation: Explicit operation hint (included in prompt if non-empty).

        Returns:
            (IntentType_or_None, raw_llm_response_or_None)
        """
        try:
            llm = self._get_llm()
            if llm is None:
                return None, None

            request_text = text.strip()
            if operation:
                request_text = f"[operation={operation}] {request_text}"

            prompt = (
                f"{_LLM_SYSTEM_PROMPT}\n\n"
                f"{_LLM_USER_TEMPLATE.format(request=request_text)}"
            )

            response = llm.generate(
                prompt=prompt,
                max_tokens=LLM_MAX_TOKENS,
                temperature=LLM_TEMPERATURE,
                timeout=5,  # strict 5 s timeout — routing must be fast
            )

            raw = response.content.strip().upper()
            # Extract first word only (model sometimes adds punctuation)
            label = re.split(r"[\s.,;:!?]", raw)[0]
            intent = self._label_to_intent(label)
            return intent, raw

        except Exception as exc:  # noqa: BLE001
            logger.debug("IntentClassifier Tier 3 LLM call failed (degraded): %s", exc)
            return None, None

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _get_llm(self) -> Optional[Any]:
        """Lazy-load the LLM provider (cached after first call).

        Returns:
            ILLMProvider instance or None if unavailable.
        """
        if self._llm is not None:
            return self._llm

        try:
            from cortex.intelligence.llm.llm_factory import LLMFactory  # noqa: PLC0415

            provider_name = self._llm_provider_name
            if provider_name is None:
                # Auto-detect from environment
                if os.environ.get("ANTHROPIC_API_KEY"):
                    provider_name = "anthropic"
                elif os.environ.get("OPENAI_API_KEY"):
                    provider_name = "openai"
                else:
                    logger.debug(
                        "IntentClassifier: no LLM API key found — Tier 3 disabled"
                    )
                    return None

            self._llm = LLMFactory.create_provider(provider_name)
            return self._llm

        except Exception as exc:  # noqa: BLE001
            logger.debug("IntentClassifier: LLM factory init failed: %s", exc)
            return None

    @staticmethod
    def _label_to_intent(label: str) -> Optional[IntentType]:
        """Convert a string label to IntentType.

        Args:
            label: Uppercase label string from LLM.

        Returns:
            Matching IntentType or None if not recognised.
        """
        _MAP: Dict[str, IntentType] = {
            "IMPLEMENT": IntentType.IMPLEMENT,
            "FIX": IntentType.FIX,
            "REFACTOR": IntentType.REFACTOR,
            "DOCUMENT": IntentType.DOCUMENT,
            "ANALYZE": IntentType.ANALYZE,
            "ANALYSE": IntentType.ANALYZE,
            "ONBOARD": IntentType.ONBOARD,
            "PLAN": IntentType.PLAN,
            "AUDIT": IntentType.AUDIT,
            "DESIGN": IntentType.DESIGN,
            "DIGEST": IntentType.DIGEST,
            "REPHRASE": IntentType.REPHRASE,
            "INVESTIGATE": IntentType.INVESTIGATE,
            "GOLDEN_TEST": IntentType.GOLDEN_TEST,
        }
        return _MAP.get(label.upper())
