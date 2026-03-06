"""
ContentLibraryFacade — Unified selection facade for all three content libraries.

Phase 129 — Content Library Facade + AI Spark Pool + Epoch Shuffle Algorithm.
SSOT: cortex-registry/planning/phases/planned/phase-129-content-library-facade.yaml

Architecture:
  Three pools behind a single facade:
    - 'quotes'     → atom-quote.yaml (300+ literary quotes)        label: "Insight"
    - 'principles' → high-value-principles.yaml (200+ SDLC)        label: "Principle"
    - 'ai_spark'   → ai-adoption-sparks.yaml (150+ AI adoption)    label: "AI Spark"

  EpochShuffler guarantees full-corpus traversal before any item repeats:
    - Fisher-Yates shuffle into an epoch deque on first load or on exhaustion
    - O(1) pop from front — no per-call filtering, no filesystem I/O post-load
    - Weight bias: high-relevance_weight items front-loaded in first 30% of epoch
    - Cross-library ring buffer (deque maxlen=5) prevents same library 3+ consecutive

  Backward compatibility:
    - PrincipleSelector is NOT broken — it continues to work unchanged
    - ContentLibraryFacade is an additive layer; it does NOT replace PrincipleSelector

Performance:
  - p95 target: ≤ 5ms per select() call (any pool, 650+ total items)
  - Lazy singleton loading — filesystem I/O only on first access per pool
  - EpochShuffler.next() is O(1) pop

Rendering:
  Every result dict includes:
    - library_label: "Insight" | "Principle" | "AI Spark"
    - render_header: "> 💡 **{label}:** {body/text}" — paste-ready blockquote line

Governance: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings), CORE-035 (single impl)
Author: Asif Hussain | © 2025-2026 CORTEX Framework
"""
from __future__ import annotations

import random
from collections import deque
from pathlib import Path
from typing import Any

import yaml

# ─── Constants ────────────────────────────────────────────────────────────────

VALID_POOLS: frozenset[str] = frozenset({"quotes", "principles", "ai_spark"})

LIBRARY_LABELS: dict[str, str] = {
    "quotes": "Insight",
    "principles": "Principle",
    "ai_spark": "AI Spark",
}

# Complexity gate: intents that always warrant principle injection
_ALWAYS_COMPLEX_INTENTS: frozenset[str] = frozenset({
    "DESIGN", "PLAN", "INVESTIGATE", "ANALYZE", "ONBOARD",
})

# ─── YAML paths ───────────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).parent.parent.parent.parent

_QUOTE_PATH = (
    _REPO_ROOT / "cortex-registry" / "templates" / "response" / "atoms" / "atom-quote.yaml"
)
_PRINCIPLES_PATH = (
    _REPO_ROOT / "cortex-registry" / "knowledge" / "sdlc" / "high-value-principles.yaml"
)
_AI_SPARK_PATH = (
    _REPO_ROOT / "cortex-registry" / "knowledge" / "ai" / "ai-adoption-sparks.yaml"
)

# ─── Module-level cache singletons (lazy, loaded once) ────────────────────────

_quotes_items: list[dict[str, Any]] | None = None
_principles_items: list[dict[str, Any]] | None = None
_ai_spark_items: list[dict[str, Any]] | None = None

# Cross-library ring buffer — prevents same library 3+ consecutive
_library_ring: deque[str] = deque(maxlen=5)


# ─── YAML Loaders (lazy singletons) ───────────────────────────────────────────

def _load_quotes() -> list[dict[str, Any]]:
    """Load and cache quote items from atom-quote.yaml."""
    global _quotes_items
    if _quotes_items is None:
        with _QUOTE_PATH.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        _quotes_items = data["quotes"]
    return _quotes_items


def _load_principles() -> list[dict[str, Any]]:
    """Load and cache principle items from high-value-principles.yaml."""
    global _principles_items
    if _principles_items is None:
        with _PRINCIPLES_PATH.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        _principles_items = data["principles"]
    return _principles_items


def _load_ai_sparks() -> list[dict[str, Any]]:
    """Load and cache AI Spark items from ai-adoption-sparks.yaml."""
    global _ai_spark_items
    if _ai_spark_items is None:
        with _AI_SPARK_PATH.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        _ai_spark_items = data["sparks"]
    return _ai_spark_items


# ─── EpochShuffler ────────────────────────────────────────────────────────────

class EpochShuffler:
    """Full-corpus traversal guarantee via Fisher-Yates epoch shuffle.

    Algorithm:
      1. On first access (or epoch exhaustion): shuffle items using Fisher-Yates
         with weight bias — high relevance_weight items are front-loaded into
         the first 30% of the epoch queue.
      2. next() pops from the front of the epoch deque — O(1), zero repeats
         within an epoch.
      3. When epoch is exhausted, automatically reshuffles into a new epoch.

    This guarantees every item is served exactly once per epoch. Users see the
    full library before any item repeats, regardless of corpus size.

    Args:
        items: The full list of content items. Must be non-empty.
        weight_field: The field name holding relevance weight. Default 'relevance_weight'.
    """

    def __init__(
        self,
        items: list[dict[str, Any]],
        weight_field: str = "relevance_weight",
    ) -> None:
        """Initialise with the full item list and build the first epoch."""
        if not items:
            raise ValueError("EpochShuffler requires a non-empty item list")
        self._items = items
        self._weight_field = weight_field
        self._epoch: deque[dict[str, Any]] = deque()
        self._epoch_count: int = 0
        self._build_epoch()

    def next(self) -> dict[str, Any]:
        """Return the next item from the current epoch, reshuffling if exhausted.

        Returns:
            One item dict — guaranteed non-repeating within an epoch.
        """
        if not self._epoch:
            self._build_epoch()
        return self._epoch.popleft()

    @property
    def epoch_count(self) -> int:
        """Number of epochs completed (reshuffles triggered)."""
        return self._epoch_count

    @property
    def remaining(self) -> int:
        """Items remaining in the current epoch."""
        return len(self._epoch)

    def _build_epoch(self) -> None:
        """Build a new epoch using weight-biased Fisher-Yates shuffle.

        Strategy:
          1. Partition items into HIGH (weight ≥ 0.85) and NORMAL buckets.
          2. Fisher-Yates shuffle each bucket independently.
          3. Front-load: interleave HIGH items into the first 30% of positions.
          4. Fill remaining positions with NORMAL items (also shuffled).

        Result: high-relevance items appear proportionally more in the first
        third of the epoch — they are not excluded, just biased forward.
        """
        wf = self._weight_field
        high = [it for it in self._items if float(it.get(wf, 0.5)) >= 0.85]
        normal = [it for it in self._items if float(it.get(wf, 0.5)) < 0.85]

        random.shuffle(high)
        random.shuffle(normal)

        n = len(self._items)
        front_slots = max(1, n * 30 // 100)  # 30% front zone

        # Distribute high-weight items across front slots
        # Any overflow goes into the back half (still served, just not front-biased)
        front: list[dict[str, Any]] = []
        back: list[dict[str, Any]] = []

        for i, item in enumerate(high):
            if i < front_slots:
                front.append(item)
            else:
                back.append(item)

        # Fill remaining front slots with normal items
        normal_iter = iter(normal)
        while len(front) < front_slots and (item := next(normal_iter, None)):
            front.append(item)

        # All remaining normal items go to back
        back.extend(normal_iter)

        # Shuffle the back section independently
        random.shuffle(back)

        self._epoch = deque(front + back)
        self._epoch_count += 1


# ─── Intent → theme/domain mappings ──────────────────────────────────────────

_QUOTE_THEME_MAP: dict[str, str] = {
    "IMPLEMENT": "quality",
    "FIX": "systems-thinking",
    "REFACTOR": "improvement",
    "AUDIT": "discipline",
    "DEBUG": "systems-thinking",
    "DESIGN": "architecture",
    "PLAN": "strategy",
    "HEALTH": "discipline",
    "VACUUM": "discipline",
    "TOTALRECALL": "strategy",
    "QUERY": "universal",
    "INTRODUCE": "universal",
    "SECURITY_AUDIT": "security",
    "DIGEST": "learning",
    "ONBOARD": "learning",
    "SYNC": "flow",
    "TRAIN": "learning",
    "META_AUDIT": "discipline",
    "DEFAULT": "universal",
}

_PRINCIPLE_DOMAIN_MAP: dict[str, str] = {
    "QUERY": "universal",
    "DESIGN": "architecture",
    "PLAN": "devops",
    "AUDIT": "code_quality",
    "REFACTOR": "refactoring",
    "TDD": "tdd",
    "IMPLEMENT": "tdd",
    "FIX": "code_quality",
    "ONBOARD": "documentation",
    "INTRODUCE": "documentation",
    "DEFAULT": "universal",
}

_AI_SPARK_CATEGORY_MAP: dict[str, str] = {
    "INTRODUCE": "adoption",
    "QUERY": "productivity",
    "DESIGN": "creativity",
    "ONBOARD": "collaboration",
    "PLAN": "leadership",
    "IMPLEMENT": "productivity",
    "FIX": "productivity",
    "REFACTOR": "craftsmanship",
    "DEFAULT": "adoption",
}

# ─── Module-level EpochShuffler singletons (one per pool) ─────────────────────
# Initialised lazily on first select() call for that pool.

_quote_shuffler: EpochShuffler | None = None
_principle_shuffler: EpochShuffler | None = None
_ai_spark_shuffler: EpochShuffler | None = None


def _get_quote_shuffler() -> EpochShuffler:
    """Return (or create) the module-level quote EpochShuffler."""
    global _quote_shuffler
    if _quote_shuffler is None:
        _quote_shuffler = EpochShuffler(_load_quotes())
    return _quote_shuffler


def _get_principle_shuffler() -> EpochShuffler:
    """Return (or create) the module-level principle EpochShuffler."""
    global _principle_shuffler
    if _principle_shuffler is None:
        _principle_shuffler = EpochShuffler(_load_principles())
    return _principle_shuffler


def _get_ai_spark_shuffler() -> EpochShuffler:
    """Return (or create) the module-level AI Spark EpochShuffler."""
    global _ai_spark_shuffler
    if _ai_spark_shuffler is None:
        _ai_spark_shuffler = EpochShuffler(_load_ai_sparks())
    return _ai_spark_shuffler


# ─── Complexity gate (mirrors principle_selector.py) ──────────────────────────

def _is_complex(intent_type: str, context_hints: dict[str, Any] | None = None) -> bool:
    """Return True if the request warrants principle injection."""
    intent = intent_type.upper()
    if intent in _ALWAYS_COMPLEX_INTENTS:
        return True
    if context_hints and context_hints.get("is_complex") is True:
        return True
    return False


# ─── Rendering helper ─────────────────────────────────────────────────────────

def _build_render_header(label: str, body: str) -> str:
    """Build the paste-ready blockquote header line for VS Code Copilot Chat rendering."""
    return f"> 💡 **{label}:** {body}"


def _truncate(text: str, max_chars: int = 200) -> str:
    """Truncate text to max_chars at word boundary, appending ellipsis if needed."""
    if len(text) <= max_chars:
        return text
    truncated = text[: max_chars - 1].rsplit(" ", 1)[0]
    return truncated + "…"


# ─── ContentLibraryFacade ─────────────────────────────────────────────────────

class ContentLibraryFacade:
    """Unified selection facade for all three CORTEX content libraries.

    Provides a single, consistent API to select from:
      - 'quotes'     → Insight label (literary wisdom, 300+ items)
      - 'principles' → Principle label (SDLC engineering, 200+ items)
      - 'ai_spark'   → AI Spark label (AI adoption encouragement, 150+ items)

    Each result dict includes a ``library_label`` and ``render_header`` field
    for direct paste into VS Code Copilot Chat blockquote blocks.

    The facade is stateless — all epoch state lives in module-level shuffler
    singletons so it is shared across instances (consistent anti-repetition).

    Usage::

        facade = ContentLibraryFacade()

        # Single pool
        quote = facade.select("IMPLEMENT", pool="quotes")
        spark = facade.select("INTRODUCE", pool="ai_spark")

        # Cross-library rotation (any eligible pool)
        item = facade.select_across("QUERY")
        print(item["render_header"])  # paste-ready blockquote
    """

    def select(
        self,
        intent_type: str,
        pool: str = "quotes",
        request_text: str = "",
        context_hints: dict[str, Any] | None = None,
    ) -> dict[str, Any] | None:
        """Select one non-repeating item from the specified pool.

        For pool='principles': applies the complexity gate. Returns None when
        the request is not complex enough to warrant principle injection.
        For pool='quotes' and pool='ai_spark': always returns an item.

        Args:
            intent_type: CORTEX intent string (e.g. "IMPLEMENT", "QUERY").
            pool: Content pool — 'quotes', 'principles', or 'ai_spark'.
            request_text: Raw user request text (used by complexity gate).
            context_hints: Optional signals dict. Key 'is_complex' (bool) overrides gate.

        Returns:
            Dict with content fields + library_label + render_header, or None
            if complexity gate suppresses a principle.

        Raises:
            ValueError: If pool is not in VALID_POOLS.
        """
        if pool not in VALID_POOLS:
            raise ValueError(
                f"Invalid pool '{pool}'. Valid pools: {sorted(VALID_POOLS)}"
            )

        intent = intent_type.upper()

        if pool == "quotes":
            return self._select_quote(intent)
        if pool == "principles":
            return self._select_principle(intent, request_text, context_hints)
        if pool == "ai_spark":
            return self._select_ai_spark(intent)

        return None  # unreachable — kept for type checker

    def select_across(
        self,
        intent_type: str,
        request_text: str = "",
        context_hints: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Select one item from any eligible pool, rotating across libraries fairly.

        Cross-library selection rules:
          1. The cross-library ring buffer (_library_ring) prevents the same
             library from appearing 3+ consecutive times.
          2. The quotes and ai_spark pools always yield an item.
          3. The principles pool is only included for complex requests.
          4. Falls back to quotes if no eligible pool remains.

        Args:
            intent_type: CORTEX intent string.
            request_text: Raw user request text (complexity gate for principles).
            context_hints: Optional signals dict.

        Returns:
            A content dict with library_label + render_header — never None.
        """
        intent = intent_type.upper()
        complex_request = _is_complex(intent, context_hints)

        # Build list of eligible pools, excluding those that appeared last 2 times
        recent_two = list(_library_ring)[-2:] if len(_library_ring) >= 2 else []

        candidates: list[str] = []
        for pool_name in ["quotes", "ai_spark", "principles"]:
            if pool_name == "principles" and not complex_request:
                continue
            # Suppress pool if it was the last 2 selections (prevent 3+ consecutive)
            if recent_two.count(pool_name) >= 2:
                continue
            candidates.append(pool_name)

        if not candidates:
            candidates = ["quotes"]  # guaranteed fallback

        chosen_pool = random.choice(candidates)
        _library_ring.append(chosen_pool)

        result = self.select(
            intent_type=intent,
            pool=chosen_pool,
            request_text=request_text,
            context_hints=context_hints,
        )

        # Principles can return None for simple requests — fall back to quotes
        if result is None:
            result = self._select_quote(intent)

        return result

    # ─── Pool-specific selection ───────────────────────────────────────────────

    def _select_quote(self, intent: str) -> dict[str, Any]:
        """Select one quote from the quotes pool via EpochShuffler."""
        theme = _QUOTE_THEME_MAP.get(intent, "universal")
        shuffler = _get_quote_shuffler()

        # Try up to 10 pops to find a theme-matched item
        # (EpochShuffler guarantees no full-epoch repeats; theme-match is a soft filter)
        found: dict[str, Any] | None = None
        attempts: list[dict[str, Any]] = []
        for _ in range(min(10, shuffler.remaining + 1)):
            if shuffler.remaining == 0:
                break
            item = shuffler.next()
            if theme in item.get("themes", []) or theme == "universal":
                found = item
                break
            attempts.append(item)

        if found is None:
            # Theme not matched in first 10 pops — use last attempt or reshuffle
            found = attempts[-1] if attempts else shuffler.next()

        label = LIBRARY_LABELS["quotes"]
        body = _truncate(found.get("text", ""), 200)
        return {
            **found,
            "library_label": label,
            "render_header": _build_render_header(label, body),
            "_pool": "quotes",
        }

    def _select_principle(
        self,
        intent: str,
        request_text: str,
        context_hints: dict[str, Any] | None,
    ) -> dict[str, Any] | None:
        """Select one principle via EpochShuffler, or None if not complex."""
        if not _is_complex(intent, context_hints):
            # Secondary check: word count
            word_count = (
                context_hints.get("word_count")
                if context_hints and "word_count" in context_hints
                else len(request_text.strip().split()) if request_text.strip() else 0
            )
            if word_count < 8:
                return None

        shuffler = _get_principle_shuffler()
        preferred_domain = _PRINCIPLE_DOMAIN_MAP.get(intent, "universal")

        found: dict[str, Any] | None = None
        attempts: list[dict[str, Any]] = []
        for _ in range(min(10, shuffler.remaining + 1)):
            if shuffler.remaining == 0:
                break
            item = shuffler.next()
            if (
                preferred_domain == "universal"
                or item.get("domain") == preferred_domain
                or intent in item.get("intent_types", [])
            ):
                found = item
                break
            attempts.append(item)

        if found is None:
            found = attempts[-1] if attempts else shuffler.next()

        label = LIBRARY_LABELS["principles"]
        body = _truncate(found.get("body", ""), 200)
        return {
            **found,
            "body": body,
            "library_label": label,
            "render_header": _build_render_header(label, body),
            "_pool": "principles",
        }

    def _select_ai_spark(self, intent: str) -> dict[str, Any]:
        """Select one AI Spark item via EpochShuffler."""
        preferred_category = _AI_SPARK_CATEGORY_MAP.get(intent, "adoption")
        shuffler = _get_ai_spark_shuffler()

        found: dict[str, Any] | None = None
        attempts: list[dict[str, Any]] = []
        for _ in range(min(10, shuffler.remaining + 1)):
            if shuffler.remaining == 0:
                break
            item = shuffler.next()
            if item.get("category") == preferred_category or preferred_category == "adoption":
                found = item
                break
            attempts.append(item)

        if found is None:
            found = attempts[-1] if attempts else shuffler.next()

        label = LIBRARY_LABELS["ai_spark"]
        body = _truncate(found.get("body", ""), 200)
        return {
            **found,
            "body": body,
            "library_label": label,
            "render_header": _build_render_header(label, body),
            "_pool": "ai_spark",
        }
