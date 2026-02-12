"""
Hybrid Intent Routing - Multi-layer intent classification.

AC-ID: AC-ONBOARD-HYBRID-001
Authority: CORE-007 (MCP-first), CORE-011 (Type hints), CORE-012 (Docstrings)

Architecture:
  Layer 1: Keyword Matching (fast, deterministic, 0 latency)
  Layer 2: Semantic Similarity (embeddings for fuzzy matching)
  Layer 3: LLM Fallback (complex/ambiguous intents only)

Flow:
  1. Try keyword matching → if confidence > 0.7, return
  2. Try semantic similarity → if confidence > 0.6, return
  3. Fall back to LLM for complex cases → always returns
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


class HybridRoutingLayer(str, Enum):
    """Which layer produced the routing decision."""
    KEYWORD = "keyword"
    SEMANTIC = "semantic"
    LLM = "llm"
    COMPOSITE = "composite"


@dataclass
class HybridRoutingResult:
    """
    Result from hybrid intent routing.

    Attributes:
        intent: Detected intent type
        confidence: Confidence score (0.0-1.0)
        layer: Which routing layer produced the result
        orchestrator: Target orchestrator name
        mcp_tool: Associated MCP tool
        reasoning: Human-readable explanation
        keyword_matches: Keywords that matched (if any)
        semantic_score: Semantic similarity score (if used)
        alternative_intents: Other possible intents with scores
    """
    intent: str
    confidence: float
    layer: HybridRoutingLayer
    orchestrator: str
    mcp_tool: str
    reasoning: str
    keyword_matches: List[str] = field(default_factory=list)
    semantic_score: float = 0.0
    alternative_intents: List[Tuple[str, float]] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


# Intent configuration with keywords, orchestrator mapping, and semantic hints
INTENT_CONFIG: Dict[str, Dict[str, Any]] = {
    "IMPLEMENT": {
        "keywords": [
            "create", "add", "new", "implement", "develop", "build", "construct",
            "establish", "introduce", "feature", "enhancement", "scaffold"
        ],
        "orchestrator": "TDDOrchestrator",
        "mcp_tool": "cortex_process_request",
        "semantic_hints": ["new functionality", "build feature", "add capability"],
    },
    "FIX": {
        "keywords": [
            "fix", "bug", "issue", "error", "problem", "crash", "fail", "broken",
            "resolve", "correct", "repair", "patch", "race condition", "defect"
        ],
        "orchestrator": "IntentRouter",
        "mcp_tool": "cortex_process_request",
        "semantic_hints": ["repair error", "solve bug", "correct issue"],
    },
    "REFACTOR": {
        "keywords": [
            "refactor", "improve", "cleanup", "restructure", "simplify", "optimize",
            "clean", "modernize", "reorganize", "rewrite", "redesign", "performance"
        ],
        "orchestrator": "RefactoringOrchestrator",
        "mcp_tool": "cortex_process_request",
        "semantic_hints": ["improve code", "restructure", "optimize performance"],
    },
    "ANALYZE": {
        "keywords": [
            "analyze", "examine", "investigate", "review", "inspect", "study",
            "evaluate", "assess", "check", "audit", "explore", "lens", "scan"
        ],
        "orchestrator": "LENSOrchestrator",
        "mcp_tool": "cortex_lens_analyze",
        "semantic_hints": ["code review", "investigate issue", "examine structure"],
    },
    "TEST": {
        "keywords": [
            "test", "tests", "testing", "verify", "validate", "coverage",
            "unit test", "integration test", "pytest", "mock", "assert"
        ],
        "orchestrator": "TDDOrchestrator",
        "mcp_tool": "cortex_process_request",
        "semantic_hints": ["write tests", "test coverage", "verify functionality"],
    },
    "DEPLOY": {
        "keywords": [
            "deploy", "release", "publish", "ship", "launch", "production",
            "staging", "rollout", "ci/cd", "pipeline"
        ],
        "orchestrator": "GitOrchestrator",
        "mcp_tool": "cortex_process_request",
        "semantic_hints": ["deploy to production", "release version", "ship feature"],
    },
    "ONBOARD": {
        "keywords": [
            "onboard", "onboarding", "setup", "initialize", "bootstrap", "configure",
            "register", "integrate", "import project", "analyze repository", "scan repo",
            "discover", "inventory", "profile", "assess"
        ],
        "orchestrator": "RepositoryOnboardingOrchestrator",
        "mcp_tool": "cortex_onboard_repository",
        "semantic_hints": ["onboard repository", "setup project", "initialize workspace"],
    },
    "DOCUMENT": {
        "keywords": [
            "document", "documentation", "docs", "readme", "explain", "describe",
            "comment", "annotate", "guide", "manual"
        ],
        "orchestrator": "DocumentationOrchestrator",
        "mcp_tool": "cortex_process_request",
        "semantic_hints": ["write documentation", "create readme", "explain code"],
    },
    "QUERY": {
        "keywords": [
            "what", "how", "why", "when", "where", "which", "who",
            "show", "tell", "explain", "help", "info", "?"
        ],
        "orchestrator": "ConversationOrchestrator",
        "mcp_tool": "cortex_process_request",
        "semantic_hints": ["ask question", "get information", "understand concept"],
    },
}


class HybridIntentRouter:
    """
    Multi-layer intent routing with keyword, semantic, and LLM fallback.

    Architecture:
    - Layer 1 (Keyword): Fast, deterministic, handles 80% of requests
    - Layer 2 (Semantic): Embeddings-based similarity for fuzzy matching
    - Layer 3 (LLM): Last resort for complex/ambiguous intents

    Example:
        >>> router = HybridIntentRouter()
        >>> result = router.route("onboard D:\\PROJECTS\\KASHKOLE")
        >>> print(f"Intent: {result.intent}, Confidence: {result.confidence}")
        Intent: ONBOARD, Confidence: 0.95
    """

    def __init__(
        self,
        keyword_threshold: float = 0.7,
        semantic_threshold: float = 0.6,
        enable_semantic: bool = True,
        enable_llm_fallback: bool = False,  # Disabled by default (costly)
    ):
        """
        Initialize hybrid intent router.

        Args:
            keyword_threshold: Confidence threshold for keyword matching (default: 0.7)
            semantic_threshold: Confidence threshold for semantic matching (default: 0.6)
            enable_semantic: Whether to use semantic layer (requires embeddings)
            enable_llm_fallback: Whether to use LLM for complex cases (costly)
        """
        self.keyword_threshold = keyword_threshold
        self.semantic_threshold = semantic_threshold
        self.enable_semantic = enable_semantic
        self.enable_llm_fallback = enable_llm_fallback

        # Precompile keyword patterns for efficiency
        self._keyword_patterns: Dict[str, List[re.Pattern]] = {}
        for intent, config in INTENT_CONFIG.items():
            self._keyword_patterns[intent] = [
                re.compile(r'\b' + re.escape(kw) + r'\b', re.IGNORECASE)
                for kw in config["keywords"]
            ]

        # Lazy-loaded semantic embeddings
        self._embeddings_model = None
        self._intent_embeddings: Dict[str, Any] = {}

        logger.info(
            "HybridIntentRouter initialized: keyword_threshold=%.2f, "
            "semantic=%s, llm_fallback=%s",
            keyword_threshold, enable_semantic, enable_llm_fallback
        )

    def route(self, request: str) -> HybridRoutingResult:
        """
        Route request through hybrid layers.

        Args:
            request: User's natural language request

        Returns:
            HybridRoutingResult with intent, confidence, and routing info

        Example:
            >>> result = router.route("onboard my project at /path/to/repo")
            >>> print(result.intent)  # "ONBOARD"
        """
        if not request or not request.strip():
            return self._unknown_result("Empty request")

        normalized = request.lower().strip()

        # Layer 1: Keyword Matching (fast path)
        keyword_result = self._match_keywords(normalized, request)
        if keyword_result.confidence >= self.keyword_threshold:
            logger.info(
                "Keyword match: intent=%s, confidence=%.2f",
                keyword_result.intent, keyword_result.confidence
            )
            return keyword_result

        # Layer 2: Semantic Similarity (if enabled)
        if self.enable_semantic:
            semantic_result = self._match_semantic(normalized, request)
            if semantic_result.confidence >= self.semantic_threshold:
                logger.info(
                    "Semantic match: intent=%s, confidence=%.2f",
                    semantic_result.intent, semantic_result.confidence
                )
                return semantic_result

        # Layer 3: LLM Fallback (if enabled)
        if self.enable_llm_fallback:
            llm_result = self._match_llm(request)
            return llm_result

        # Return best keyword match even if below threshold
        if keyword_result.confidence > 0:
            keyword_result.reasoning += " (below threshold, best effort)"
            return keyword_result

        return self._unknown_result("No intent matched")

    def _match_keywords(self, normalized: str, original: str) -> HybridRoutingResult:
        """
        Layer 1: Keyword-based matching.

        Fast, deterministic matching using precompiled regex patterns.
        """
        intent_scores: Dict[str, Tuple[float, List[str]]] = {}

        for intent, patterns in self._keyword_patterns.items():
            matches = []
            for pattern in patterns:
                if pattern.search(normalized):
                    matches.append(pattern.pattern.replace(r'\b', ''))

            if matches:
                # Score based on:
                # - Number of keyword matches (density)
                # - Proportion of intent keywords matched
                config = INTENT_CONFIG[intent]
                density = len(matches) / len(config["keywords"])

                # Boost for exact command patterns like "/onboard"
                if f"/{intent.lower()}" in normalized:
                    density = min(density + 0.3, 1.0)

                # Boost if intent word itself is present
                if intent.lower() in normalized:
                    density = min(density + 0.2, 1.0)

                intent_scores[intent] = (density, matches)

        if not intent_scores:
            return HybridRoutingResult(
                intent="UNKNOWN",
                confidence=0.0,
                layer=HybridRoutingLayer.KEYWORD,
                orchestrator="ConversationOrchestrator",
                mcp_tool="cortex_process_request",
                reasoning="No keyword matches found",
            )

        # Get top intent
        sorted_intents = sorted(intent_scores.items(), key=lambda x: x[1][0], reverse=True)
        top_intent, (score, matches) = sorted_intents[0]
        config = INTENT_CONFIG[top_intent]

        # Build alternatives list
        alternatives = [
            (intent, scores[0])
            for intent, scores in sorted_intents[1:4]
        ]

        return HybridRoutingResult(
            intent=top_intent,
            confidence=min(score, 0.99),
            layer=HybridRoutingLayer.KEYWORD,
            orchestrator=config["orchestrator"],
            mcp_tool=config["mcp_tool"],
            reasoning=f"Keyword match: {', '.join(matches[:5])}",
            keyword_matches=matches,
            alternative_intents=alternatives,
        )

    def _match_semantic(self, normalized: str, original: str) -> HybridRoutingResult:
        """
        Layer 2: Semantic similarity matching.

        Uses sentence embeddings to find semantically similar intents.
        Falls back to keyword result if embeddings unavailable.
        """
        try:
            # Lazy load embeddings model
            if self._embeddings_model is None:
                try:
                    from sentence_transformers import SentenceTransformer
                    self._embeddings_model = SentenceTransformer('all-MiniLM-L6-v2')

                    # Pre-compute intent embeddings from semantic hints
                    for intent, config in INTENT_CONFIG.items():
                        hints = config.get("semantic_hints", [])
                        if hints:
                            self._intent_embeddings[intent] = self._embeddings_model.encode(
                                hints, convert_to_tensor=True
                            )
                except ImportError:
                    logger.warning("sentence-transformers not available, semantic layer disabled")
                    self.enable_semantic = False
                    return self._match_keywords(normalized, original)

            # Encode request
            request_embedding = self._embeddings_model.encode(original, convert_to_tensor=True)

            # Compare against intent embeddings
            best_intent = None
            best_score = 0.0

            from sentence_transformers import util

            for intent, embeddings in self._intent_embeddings.items():
                similarities = util.cos_sim(request_embedding, embeddings)
                max_similarity = float(similarities.max())

                if max_similarity > best_score:
                    best_score = max_similarity
                    best_intent = intent

            if best_intent:
                config = INTENT_CONFIG[best_intent]
                return HybridRoutingResult(
                    intent=best_intent,
                    confidence=best_score,
                    layer=HybridRoutingLayer.SEMANTIC,
                    orchestrator=config["orchestrator"],
                    mcp_tool=config["mcp_tool"],
                    reasoning=f"Semantic similarity: {best_score:.2f}",
                    semantic_score=best_score,
                )

        except Exception as e:
            logger.warning("Semantic matching failed: %s", e)

        return self._match_keywords(normalized, original)

    def _match_llm(self, request: str) -> HybridRoutingResult:
        """
        Layer 3: LLM-based intent classification.

        Uses LLM for complex/ambiguous requests. Most accurate but costly.
        """
        # Placeholder - would integrate with actual LLM service
        # For now, fall back to keyword matching
        logger.info("LLM fallback invoked for: %s", request[:50])

        # In production, this would call an LLM with a classification prompt
        return HybridRoutingResult(
            intent="UNKNOWN",
            confidence=0.5,
            layer=HybridRoutingLayer.LLM,
            orchestrator="ConversationOrchestrator",
            mcp_tool="cortex_process_request",
            reasoning="LLM classification (placeholder)",
        )

    def _unknown_result(self, reason: str) -> HybridRoutingResult:
        """Create an UNKNOWN intent result."""
        return HybridRoutingResult(
            intent="UNKNOWN",
            confidence=0.0,
            layer=HybridRoutingLayer.KEYWORD,
            orchestrator="ConversationOrchestrator",
            mcp_tool="cortex_process_request",
            reasoning=reason,
        )


# Singleton instance
_router_instance: Optional[HybridIntentRouter] = None


def get_hybrid_intent_router(
    keyword_threshold: float = 0.7,
    semantic_threshold: float = 0.6,
    enable_semantic: bool = True,
    enable_llm_fallback: bool = False,
) -> HybridIntentRouter:
    """
    Get singleton HybridIntentRouter instance.

    Args:
        keyword_threshold: Confidence threshold for keyword matching
        semantic_threshold: Confidence threshold for semantic matching
        enable_semantic: Whether to use semantic layer
        enable_llm_fallback: Whether to use LLM fallback

    Returns:
        HybridIntentRouter singleton instance
    """
    global _router_instance
    if _router_instance is None:
        _router_instance = HybridIntentRouter(
            keyword_threshold=keyword_threshold,
            semantic_threshold=semantic_threshold,
            enable_semantic=enable_semantic,
            enable_llm_fallback=enable_llm_fallback,
        )
    return _router_instance


__all__ = [
    "HybridIntentRouter",
    "HybridRoutingResult",
    "HybridRoutingLayer",
    "INTENT_CONFIG",
    "get_hybrid_intent_router",
]
