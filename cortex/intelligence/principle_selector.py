"""
PrincipleSelector — Weighted Random Selection with Anti-Repetition Ring Buffer.

Phase 123 — Principle of the Moment (quotes pool).
Phase 124 — Principle Block Library (principles pool extension).
SSOT: cortex-registry/planning/phases/completed/phase-123-principle-of-the-moment.yaml
      cortex-registry/planning/phases/planned/phase-124-principle-block-library.yaml

Architecture:
  - pool='quotes' (default): loads atom-quote.yaml — 32 literary quotes
  - pool='principles': loads high-value-principles.yaml — 30 SDLC principles
  - Both pools use a shared ring buffer (deque maxlen=10) for anti-repetition
  - Theme/domain mapping per intent_type for contextual selection
  - Weighted random selection via relevance_weight field
  - Falls back to full pool when theme-filtered candidates are exhausted

Performance:
  - p95 target: ≤ 3ms (quotes), ≤ 5ms (principles)
  - No filesystem I/O at select() time after initial YAML load
"""

from __future__ import annotations

from collections import deque
from pathlib import Path
import random
import time
from typing import Any

import yaml

# ── Module-level singleton state (shared across all PrincipleSelector instances) ──
_quotes_cache: list[dict[str, Any]] | None = None
_principles_cache: list[dict[str, Any]] | None = None
_ring_buffer: deque[str] = deque(maxlen=10)

_VALID_POOLS = frozenset({"quotes", "principles"})

# Canonical paths — resolved once at module load
_ATOM_QUOTE_PATH = (
    Path(__file__).parent.parent.parent
    / "cortex-registry"
    / "templates"
    / "response"
    / "atoms"
    / "atom-quote.yaml"
)

_PRINCIPLES_PATH = (
    Path(__file__).parent.parent.parent
    / "cortex-registry"
    / "knowledge"
    / "sdlc"
    / "high-value-principles.yaml"
)

# Intent → theme mapping for the quotes pool (mirrors atom-quote.yaml theme_map)
_THEME_MAP: dict[str, str] = {
    "IMPLEMENT": "quality",
    "FIX": "systems_thinking",
    "REFACTOR": "improvement",
    "AUDIT": "discipline",
    "DEBUG": "systems_thinking",
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

# Intent → preferred domain for the principles pool (mirrors atom-principle.yaml theme_map)
_PRINCIPLES_DOMAIN_MAP: dict[str, str] = {
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


def _load_atom_quote_yaml() -> list[dict[str, Any]]:
    """Load and return the quotes list from atom-quote.yaml (lazy singleton).

    Returns:
        List of quote dicts. Each dict has: text, author, book, themes, dedup_key.

    Raises:
        FileNotFoundError: If atom-quote.yaml cannot be located.
        KeyError: If the YAML structure does not contain a 'quotes' key.
    """
    global _quotes_cache
    if _quotes_cache is None:
        with _ATOM_QUOTE_PATH.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        _quotes_cache = data["quotes"]
    return _quotes_cache


def _load_principles_yaml() -> list[dict[str, Any]]:
    """Load and return the principles list from high-value-principles.yaml (lazy singleton).

    Returns:
        List of principle dicts. Each dict has: id, title, body, domain, tags, intent_types.

    Raises:
        FileNotFoundError: If high-value-principles.yaml cannot be located.
        KeyError: If the YAML structure does not contain a 'principles' key.
    """
    global _principles_cache
    if _principles_cache is None:
        with _PRINCIPLES_PATH.open(encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        _principles_cache = data["principles"]
    return _principles_cache


class PrincipleSelector:
    """Select a thematically appropriate, non-repeating quote or principle.

    Supports two pools via the ``pool`` parameter:
    - ``'quotes'`` (default): 32 literary quotes from atom-quote.yaml
    - ``'principles'``: 30 SDLC engineering principles from high-value-principles.yaml

    Both pools use the same shared ring buffer (deque maxlen=10) for anti-repetition.
    Each pool applies its own intent→theme/domain mapping for contextual selection.

    Usage::

        ps = PrincipleSelector("QUERY", pool="principles")
        principle = ps.select()
        print(principle["title"])

        ps = PrincipleSelector("IMPLEMENT")
        quote = ps.select()
        print(quote["text"])

    Args:
        intent_type: The CORTEX intent enum value (e.g. "IMPLEMENT", "DESIGN").
        metrics_enabled: When True, emit telemetry. Default False.
        pool: Selection pool — 'quotes' (default) or 'principles'.

    Raises:
        ValueError: If pool is not one of the supported values.
    """

    def __init__(
        self,
        intent_type: str,
        metrics_enabled: bool = False,
        pool: str = "quotes",
    ) -> None:
        """Initialise the selector for the given intent type and pool.

        Args:
            intent_type: CORTEX intent string. Unknown values fall back to theme/domain default.
            metrics_enabled: Opt-in telemetry flag. Default False.
            pool: 'quotes' or 'principles'. Raises ValueError for unknown pools.
        """
        if pool not in _VALID_POOLS:
            raise ValueError(
                f"Unsupported pool '{pool}'. Valid pools: {sorted(_VALID_POOLS)}"
            )
        self._intent_type = intent_type.upper()
        self._metrics_enabled = metrics_enabled
        self._pool = pool
        # Ring buffer is a module-level singleton — shared across all instances
        self._ring_buffer = _ring_buffer

    # ── Public API ─────────────────────────────────────────────────────────────

    def select(self) -> dict[str, Any]:
        """Select one non-repeating item from the configured pool.

        Returns:
            For pool='quotes': dict with keys text, author, book, themes, dedup_key.
            For pool='principles': dict with keys id, title, body, domain, tags, intent_types.
            Never returns None — falls back to full pool if theme/domain filter is exhausted.
        """
        if self._pool == "principles":
            return self._select_principle()
        return self._select_quote()

    # ── Quote selection (pool='quotes') ────────────────────────────────────────

    def _select_quote(self) -> dict[str, Any]:
        """Select one non-repeating quote from atom-quote.yaml."""
        t_start = time.perf_counter_ns()
        repeat_avoided = 0

        theme = _THEME_MAP.get(self._intent_type, "universal")
        quotes = self._load_quotes()

        # Step 1: filter by theme
        candidates = [q for q in quotes if theme in q.get("themes", [])]

        # Step 2: filter by ring buffer (dedup)
        available = [q for q in candidates if q.get("dedup_key", "") not in self._ring_buffer]
        repeat_avoided = len(candidates) - len(available)

        # Step 3: ring buffer exhaustion fallback — evict oldest 5 and retry
        if not available:
            for _ in range(min(5, len(self._ring_buffer))):
                if self._ring_buffer:
                    self._ring_buffer.popleft()
            available = [q for q in candidates if q.get("dedup_key", "") not in self._ring_buffer]

        # Step 4: universal fallback if theme pool itself is empty
        if not available:
            available = [q for q in quotes if "universal" in q.get("themes", [])]

        # Step 5: weighted random selection
        selected = self._weighted_random(available)

        # Step 6: push selected key into ring buffer
        dedup_key = selected.get("dedup_key", "")
        if dedup_key:
            self._ring_buffer.append(dedup_key)

        # Step 7: optional telemetry
        if self._metrics_enabled:
            latency_ms = (time.perf_counter_ns() - t_start) / 1_000_000
            self._emit_metrics(latency_ms, repeat_avoided)

        return selected

    # ── Principle selection (pool='principles') ─────────────────────────────────

    def _select_principle(self) -> dict[str, Any]:
        """Select one non-repeating SDLC principle from high-value-principles.yaml."""
        t_start = time.perf_counter_ns()
        repeat_avoided = 0

        preferred_domain = _PRINCIPLES_DOMAIN_MAP.get(self._intent_type, "universal")
        principles = _load_principles_yaml()

        # Step 1: filter by intent_types field (principles declare compatible intents)
        # "universal" domain (QUERY, DEFAULT) = no intent filter — all principles eligible
        if preferred_domain == "universal":
            candidates = principles
        else:
            intent_matched = [
                p for p in principles
                if self._intent_type in p.get("intent_types", [])
            ]
            # If no intent match, use all principles (universal fallback)
            candidates = intent_matched if intent_matched else principles

        # Step 2: filter by ring buffer (dedup on principle id)
        available = [p for p in candidates if p.get("id", "") not in self._ring_buffer]
        repeat_avoided = len(candidates) - len(available)

        # Step 3: ring buffer exhaustion fallback
        if not available:
            for _ in range(min(5, len(self._ring_buffer))):
                if self._ring_buffer:
                    self._ring_buffer.popleft()
            available = [p for p in candidates if p.get("id", "") not in self._ring_buffer]

        # Step 4: full pool fallback
        if not available:
            available = principles

        # Step 5: prefer preferred_domain candidates (soft preference, not hard filter)
        if preferred_domain != "universal":
            domain_preferred = [p for p in available if p.get("domain") == preferred_domain]
            if domain_preferred:
                available = domain_preferred

        # Step 6: weighted random selection
        selected = self._weighted_random(available)

        # Step 7: push principle id into ring buffer
        principle_id = selected.get("id", "")
        if principle_id:
            self._ring_buffer.append(principle_id)

        # Step 7b: enforce brevity limit — ≤200 chars on body (governance: atom-principle.yaml body_max_chars)
        _BODY_MAX_CHARS = 200
        if "body" in selected:
            body = selected["body"]
            if len(body) > _BODY_MAX_CHARS:
                # Truncate at last word boundary before limit, append ellipsis (ellipsis = 1 char)
                truncated = body[:_BODY_MAX_CHARS - 1].rsplit(" ", 1)[0]
                selected = {**selected, "body": truncated + "…"}

        # Step 8: optional telemetry
        if self._metrics_enabled:
            latency_ms = (time.perf_counter_ns() - t_start) / 1_000_000
            self._emit_metrics(latency_ms, repeat_avoided)

        return selected

    def _load_quotes(self) -> list[dict[str, Any]]:
        """Return the quotes pool from atom-quote.yaml (lazy singleton)."""
        return _load_atom_quote_yaml()

    # ── Private helpers ────────────────────────────────────────────────────────

    @staticmethod
    def _weighted_random(candidates: list[dict[str, Any]]) -> dict[str, Any]:
        """Select one candidate using relevance_weight as probability weight.

        Falls back to uniform random when weights are absent or all zero.

        Args:
            candidates: Non-empty list of dicts (quotes or principles).

        Returns:
            One selected dict.
        """
        if not candidates:
            return {}

        weights = [float(c.get("relevance_weight", 1.0)) for c in candidates]
        total = sum(weights)
        if total <= 0:
            return random.choice(candidates)

        return random.choices(candidates, weights=weights, k=1)[0]

    def _emit_metrics(self, latency_ms: float, repeat_avoided: int) -> None:
        """Emit selection telemetry via cortex_capture_metrics (fire-and-forget).

        A failed emit MUST NOT raise or affect select() return value.

        Args:
            latency_ms: Wall-clock time for the select() call in milliseconds.
            repeat_avoided: Number of candidates skipped due to ring buffer dedup.
        """
        try:
            from cortex.mcp.tools.cortex_capture_metrics import emit_metric  # type: ignore[import]
            emit_metric("principle_selection_latency_ms", latency_ms)
            if repeat_avoided > 0:
                emit_metric("principle_repeat_avoided_count", repeat_avoided)
        except Exception:  # noqa: BLE001
            pass
