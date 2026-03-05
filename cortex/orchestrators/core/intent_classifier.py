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
# CORE-035 — domain-scoped; class name is contextually appropriate here

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
    # Phase-89 / Phase-90 high-specificity patterns — evaluated FIRST to prevent misclassification
    # GAP-90-08: DEBUG — must precede FIX and INVESTIGATE
    # Use (?<!\w) / (?!\w) as manual word-boundary for slash-prefixed commands
    (re.compile(r"(?<!\w)debug\b", re.I), IntentType.DEBUG, 0.95),
    (re.compile(r"(?<!\w)/debug(?:-inject|-cleanup)?", re.I), IntentType.DEBUG, 0.97),
    (re.compile(r"\b(diagnose|debugger|breakpoint|marker injection|cortex debug|injection strategy)\b", re.I), IntentType.DEBUG, 0.90),
    # "trace the" → DEBUG (not INVESTIGATE — INVESTIGATE regex below no longer contains it)
    (re.compile(r"\btrace the\b", re.I), IntentType.DEBUG, 0.90),
    # GAP-90-09: HEALTH — must precede AUDIT (health check → AUDIT clash)
    (re.compile(r"(?<!\w)/health(?:check)?", re.I), IntentType.HEALTH, 0.97),
    (re.compile(r"\bhealth(?:\s+check)?\b", re.I), IntentType.HEALTH, 0.92),
    (re.compile(r"\b(orchestrator health|orchestrator status|component health|22 orchestrators|service health|all orchestrators|endpoint health)\b", re.I), IntentType.HEALTH, 0.95),
    # GAP-90-10: SYNC
    (re.compile(r"(?<!\w)/sync\b", re.I), IntentType.SYNC, 0.97),
    (re.compile(r"\b(cross-repo sync|privacy.safe sync|sync to (?:company|work)|one-way sync|cortex sync|sync target)\b", re.I), IntentType.SYNC, 0.95),
    # GAP-90-11: TRAIN
    (re.compile(r"(?<!\w)/train\b", re.I), IntentType.TRAIN, 0.97),
    (re.compile(r"\b(gap.driven training|template evolution|pattern training|cortex train|reinforcement training|evolve templates)\b", re.I), IntentType.TRAIN, 0.95),
    (re.compile(r"\blearn from (?:repo|codebase)\b", re.I), IntentType.TRAIN, 0.92),
    # GAP-90-12: TOTALRECALL — must precede REFACTOR
    (re.compile(r"(?<!\w)/totalrecall\b", re.I), IntentType.TOTALRECALL, 0.99),
    (re.compile(r"\b(total.?recall|holistic refactor|7.phase protocol|production readiness refactor|cortex total recall|everything is broken)\b", re.I), IntentType.TOTALRECALL, 0.97),
    # GAP-90-08 (RCA): root cause analysis — must precede INVESTIGATE and FIX
    # Note: /rca has no \b anchor because / is not a word char; use (?<!\w) instead
    (re.compile(r"(?<!\w)/rca\b", re.I), IntentType.RCA, 0.99),
    (re.compile(r"\b(root cause analysis|five.?whys|5.?whys|fishbone|ishikawa|fault.?tree|causal.?chain|rca analysis|cortex rca)\b", re.I), IntentType.RCA, 0.95),
    (re.compile(r"\b(root cause|what caused|why did it fail|recurrence detection|prevention rule)\b", re.I), IntentType.RCA, 0.90),
    # GAP-90-07: VACUUM — was wrongly mapped to REFACTOR; now correctly maps to VACUUM
    (re.compile(r"(?<!\w)/vacuum\b", re.I), IntentType.VACUUM, 0.99),
    (re.compile(r"\b(cortex vacuum|markdown sprawl|root clutter|vacuum cleanup)\b", re.I), IntentType.VACUUM, 0.97),
    (re.compile(r"\bvacuum\b", re.I), IntentType.VACUUM, 0.90),
    (re.compile(r"\b(cleanup|clean up|prune|purge|archive|compact)\b", re.I), IntentType.VACUUM, 0.82),
    # Multi-word / high-specificity patterns (ordered by specificity — multi-word first)
    # INVESTIGATE: "trace the" and "debug why" removed — handled above by DEBUG patterns
    # GAP-89-COMPOSE: Workflow Composer — convergence loops + full toolchain (highest specificity, multi-word)
    (re.compile(r"\b(workflow compos(?:er|e|ition)|compose (?:workflow|template)|convergence loop|dedicated (?:workflow|template)|template compos(?:er|ition)|workflow template|workflow engine)\b", re.I), IntentType.WORKFLOW_COMPOSE, 0.92),
    (re.compile(r"\b(golden test|trace assertion|acceptance criteria)\b", re.I), IntentType.GOLDEN_TEST, 0.90),
    (re.compile(r"\b(investigate|find the cause)\b", re.I), IntentType.INVESTIGATE, 0.90),
    (re.compile(r"\b(digest|summarize|summarise|recap|tl;?dr)\b", re.I), IntentType.DIGEST, 0.88),
    (re.compile(r"\b(analyze|analyse|deep analysis|deep dive|inspect)\b", re.I), IntentType.ANALYZE, 0.85),
    (re.compile(r"\b(audit|production readiness|repo health|scan for issues)\b", re.I), IntentType.AUDIT, 0.88),
    # REFACTOR — extended with quality-cleanup aliases (tidy, consolidate, decouple, extract, rename, etc.)
    (re.compile(r"\b(refactor|restructure|reorganize|simplify|modernize|rewrite|redesign|tidy|consolidate|decouple|extract|rename|inline|deduplicate|untangle)\b", re.I), IntentType.REFACTOR, 0.85),
    (re.compile(r"\b(design|architect|blueprint|system design|design pattern)\b", re.I), IntentType.DESIGN, 0.85),
    (re.compile(r"\b(plan|phase|roadmap|schedule|planning)\b", re.I), IntentType.PLAN, 0.82),
    # FIX — extended with remediation aliases (remediate, squash, address, unblock, restore, recover)
    (re.compile(r"\b(fix|bug|broken|patch|resolve|repair|crash|error|fail(?:ure|ing)?|remediate|squash|address|unblock|restore|recover|hotfix)\b", re.I), IntentType.FIX, 0.82),
    # INTRODUCE — interactive onboarding + greeting (must precede IMPLEMENT to capture "introduce yourself" correctly)
    (re.compile(r"\b(introduce yourself|who are you|what are you|what is cortex|what'?s cortex|meet cortex|about cortex|tell me about yourself)\b", re.I), IntentType.INTRODUCE, 0.97),
    (re.compile(r"^(hello|hi|hey|howdy|greetings)\b", re.I), IntentType.INTRODUCE, 0.90),
    (re.compile(r"\b(get(?:ting)? started|new here|first time|walk me through|show me around|tour|how can you help|what can you do|how do i use)\b", re.I), IntentType.INTRODUCE, 0.92),
    # IMPLEMENT — extended with rebuild/scaffold/spin-up/generate aliases
    # Note: "introduce" removed — now routed to INTRODUCE intent; use "introduce feature" → IMPLEMENT via Tier 2 context
    (re.compile(r"\b(implement|create|build|add|develop|construct|rebuild|rework|scaffold|assemble|generate|fabricate)\b", re.I), IntentType.IMPLEMENT, 0.75),
    # IMPLEMENT — multi-word phrasal verbs (must use lookahead-friendly pattern)
    (re.compile(r"\b(spin\s+up|stand\s+up|wire\s+up)\b", re.I), IntentType.IMPLEMENT, 0.78),
    (re.compile(r"\b(document|docs|documentation)\b", re.I), IntentType.DOCUMENT, 0.80),
    (re.compile(r"\b(onboard|onboarding|bootstrap|initialize|register)\b", re.I), IntentType.ONBOARD, 0.85),
    (re.compile(r"\b(rephrase|reword|token optim|compact this)\b", re.I), IntentType.REPHRASE, 0.88),
    # VACUUM — extended with housekeeping/declutter/sweep aliases
    (re.compile(r"\b(housekeeping|declutter|sweep|spring\s+clean|tidy\s+workspace)\b", re.I), IntentType.VACUUM, 0.82),
]

# ---------------------------------------------------------------------------
# Tier 2 — Keyword scoring
# ---------------------------------------------------------------------------

#: Maps IntentType → list of keywords; each match adds (1 / len(keywords)) score.
_KEYWORD_BAGS: Dict[IntentType, List[str]] = {
    IntentType.IMPLEMENT: [
        "create", "add", "new", "implement", "develop", "build", "construct",
        "establish", "feature", "enhancement",
        # Aliases: rebuild / scaffold / spin-up family
        "rebuild", "rework", "stand up", "wire up", "scaffold",
        "spin up", "generate", "produce", "assemble", "fabricate",
        "make", "port", "clone", "replicate",
    ],
    IntentType.FIX: [
        "fix", "bug", "issue", "error", "problem", "crash", "fail", "broken",
        "resolve", "correct", "repair", "patch", "race condition",
        # Aliases: remediation family
        "address", "remediate", "mitigate", "squash", "root out",
        "restore", "recover", "unblock", "hotfix", "incident",
    ],
    IntentType.REFACTOR: [
        "refactor", "improve", "restructure", "simplify", "optimize",
        "modernize", "reorganize", "rewrite", "redesign", "performance",
        # Aliases: quality-cleanup / "Fix = Refactor" family
        "tidy", "consolidate", "decouple", "extract", "rename",
        "inline", "split", "merge", "deduplicate", "untangle",
        "clean up code", "eliminate duplication",
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
        "audit", "scan repo", "production readiness", "scan for issues",
        "/audit", "repo health",
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
        "investigate", "why is", "what causes", "deep analysis", "find the cause",
    ],
    IntentType.GOLDEN_TEST: [
        "golden test", "golden tests",
        "response template", "acceptance criteria", "e2e scenario", "trace assertion",
    ],
    # GAP-89-COMPOSE: Workflow Composer — convergence loops + full CORTEX toolchain
    IntentType.WORKFLOW_COMPOSE: [
        "workflow composer", "workflow compose", "compose workflow",
        "compose template", "workflow template", "workflow templates",
        "convergence loop", "convergence gate", "condition loop",
        "template composition", "template composer", "dedicated template",
        "dedicated workflow", "dynamic workflow", "on the fly workflow",
        "workflow pipeline", "toolchain workflow", "workflow engine",
        "execute workflow", "run workflow template", "compose pipeline",
        "ast workflow", "lens workflow", "roslyn workflow",
    ],
    # GAP-90-08..12 + 90-07: Phase-89 IntentTypes now wired into Tier 2
    IntentType.DEBUG: [
        "debug", "debugger", "/debug", "/debug-inject", "/debug-cleanup",
        "diagnose", "breakpoint", "stack trace", "marker injection",
        "trace the", "debug why", "debug this", "injection strategy",
        "cortex debug", "debug mode", "step through",
    ],
    IntentType.HEALTH: [
        "health", "healthcheck", "/health", "/healthcheck",
        "orchestrator status", "orchestrator health", "component health",
        "uptime", "latency", "service health", "endpoint health",
        "all orchestrators", "22 orchestrators", "health endpoint",
    ],
    IntentType.SYNC: [
        "sync", "/sync", "sync to company", "sync to work", "cross-repo sync",
        "privacy-safe", "privacy safe", "push to work repo", "folder sync",
        "sanitize sync", "cortex sync", "sync target", "one-way sync",
    ],
    IntentType.TRAIN: [
        "train", "/train", "learn from", "learn from repo", "evolve templates",
        "gap-driven training", "template evolution", "pattern training",
        "cortex train", "train from codebase", "reinforcement training",
    ],
    IntentType.TOTALRECALL: [
        "totalrecall", "total recall", "/totalrecall", "holistic refactor",
        "production readiness refactor", "everything is broken",
        "7-phase protocol", "cortex total recall", "holistic production", "full recall",
    ],
    IntentType.RCA: [
        "rca", "/rca", "root cause analysis", "root cause", "five whys", "5 whys",
        "fishbone", "ishikawa", "fault tree", "causal chain", "causal-chain",
        "why did it fail", "recurrence detection", "prevention rule",
        "rca analysis", "cortex rca", "what caused",
    ],
    IntentType.VACUUM: [
        "vacuum", "/vacuum", "cortex vacuum", "cleanup", "clean up",
        "markdown sprawl", "root clutter", "prune", "purge", "archive",
        "compact", "vacuum cleanup",
        # Aliases: housekeeping / declutter / sweep family
        "housekeeping", "declutter", "sweep", "spring clean", "tidy workspace",
    ],
    IntentType.INTRODUCE: [
        "introduce yourself", "who are you", "what are you", "what is cortex",
        "what's cortex", "hello", "hi", "hey", "get started", "getting started",
        "help me", "how can you help", "what can you do", "capabilities",
        "how do i use", "tell me about yourself", "about cortex", "meet cortex",
        "new here", "first time", "walk me through", "show me around", "tour",
        "welcome", "onboard me",
    ],
    IntentType.DISTILL: [
        "distill", "/distill", "distill this", "distill session",
        "distill conversation", "distill chat", "compress conversation",
        "compress session", "reduce to prompt", "convert to prompt",
        "make executable prompt", "extract intent", "extract goals",
        "rebuild prompt", "reconstruct prompt", "conversation to prompt",
        "chat to prompt", "session to prompt", "entropy reduction",
        "conversation entropy", "what did we decide", "summarise to prompt",
        "summarize to prompt",
    ],
}

# ---------------------------------------------------------------------------
# LLM classification prompt
# ---------------------------------------------------------------------------

_LLM_SYSTEM_PROMPT = """\
You are an intent classifier for a software engineering AI assistant.
Classify the user request into exactly ONE of these intent labels:
IMPLEMENT, FIX, REFACTOR, DOCUMENT, ANALYZE, ONBOARD, PLAN, AUDIT, DESIGN, DIGEST, REPHRASE, INVESTIGATE, GOLDEN_TEST, WORKFLOW_COMPOSE, DEBUG, HEALTH, SYNC, TRAIN, TOTALRECALL, RCA, VACUUM, INTRODUCE, DISTILL

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
            # GAP-90-08..12 + 90-07: Phase-89 IntentTypes
            "debug": IntentType.DEBUG,
            "health": IntentType.HEALTH,
            "healthcheck": IntentType.HEALTH,
            "health_check": IntentType.HEALTH,
            "sync": IntentType.SYNC,
            "train": IntentType.TRAIN,
            "totalrecall": IntentType.TOTALRECALL,
            "total_recall": IntentType.TOTALRECALL,
            "rca": IntentType.RCA,
            "vacuum": IntentType.VACUUM,
            # INTRODUCE: interactive onboarding
            "introduce": IntentType.INTRODUCE,
            # DISTILL: conversational entropy reduction
            "distill": IntentType.DISTILL,
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
            # GAP-89-COMPOSE: Workflow Composer intent
            "WORKFLOW_COMPOSE": IntentType.WORKFLOW_COMPOSE,
            "WORKFLOW COMPOSE": IntentType.WORKFLOW_COMPOSE,
            "COMPOSE": IntentType.WORKFLOW_COMPOSE,
            # GAP-90-08..12 + 90-07: Phase-89 IntentTypes
            "DEBUG": IntentType.DEBUG,
            "HEALTH": IntentType.HEALTH,
            "SYNC": IntentType.SYNC,
            "TRAIN": IntentType.TRAIN,
            "TOTALRECALL": IntentType.TOTALRECALL,
            "TOTAL_RECALL": IntentType.TOTALRECALL,
            "RCA": IntentType.RCA,
            "VACUUM": IntentType.VACUUM,
        }
        return _MAP.get(label.upper())
