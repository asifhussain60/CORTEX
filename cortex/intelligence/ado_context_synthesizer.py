"""ADOContextSynthesizer — Token-budget-enforced Azure DevOps context summariser.

Produces a token-optimised summary of an ADO work item, extracting:
  - Title and ID
  - Acceptance criteria scenarios (all, truncated to budget)
  - Top 5 comment themes (truncated)
  - Child task hierarchy (≤ 2 levels, capped at 10 tasks per level)
  - Classification tags

The output is a plain-text string that MUST fit within MAX_CHARS = 8000
characters, guaranteeing it does not exhaust GitHub Copilot Chat context budget.

Phase: 131 (GAP-131-03 — Intelligence Layer Backport)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-035 (single canonical implementation)
"""

from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class ADOContextSynthesizer:
    """Token-budget-enforced Azure DevOps work item summariser.

    Synthesizes ADO work item dicts (as returned by the ADO REST API or
    a fetching orchestrator) into compact plain-text summaries that fit
    within the :attr:`MAX_CHARS` budget.

    Args:
        max_chars: Output character budget override.  Defaults to 8000.

    Example::

        synth = ADOContextSynthesizer()
        summary = synth.synthesize(work_item_dict)
        assert len(summary) <= 8000

    Phase: 131 — GAP-131-03
    """

    MAX_CHARS: int = 8000
    _MAX_COMMENT_THEMES: int = 5
    _MAX_CHILD_TASKS_PER_LEVEL: int = 10
    _MAX_CHILD_LEVELS: int = 2
    _DESCRIPTION_MAX_CHARS: int = 800
    _AC_MAX_CHARS: int = 1200

    def __init__(self, max_chars: Optional[int] = None) -> None:
        """Initialise with optional budget override."""
        self._budget = max_chars if max_chars is not None else self.MAX_CHARS

    # ── Public API ────────────────────────────────────────────────────────────

    def synthesize(self, work_item: Dict[str, Any]) -> str:
        """Synthesize an ADO work item dict into a token-budget-safe summary.

        Args:
            work_item: ADO work item dict.  Expected keys (all optional):
                ``id``, ``title``, ``description``, ``acceptance_criteria``,
                ``state``, ``assigned_to``, ``tags``, ``comments``,
                ``child_tasks``.

        Returns:
            Plain-text summary string — guaranteed ``len(result) ≤ MAX_CHARS``.
        """
        if not work_item:
            return "(empty work item)"[:self._budget]

        parts: List[str] = []

        # ── Header ──
        item_id = work_item.get("id", "?")
        title = str(work_item.get("title", "(no title)"))
        state = work_item.get("state", "")
        assigned = work_item.get("assigned_to", "")

        header = f"# ADO #{item_id}: {title}"
        if state:
            header += f"  [{state}]"
        if assigned:
            header += f"  → {assigned}"
        parts.append(header)

        # ── Tags ──
        tags = work_item.get("tags", [])
        if tags:
            parts.append(f"Tags: {', '.join(str(t) for t in tags[:10])}")

        # ── Description (truncated) ──
        description = str(work_item.get("description", ""))
        if description:
            parts.append("\n## Description")
            parts.append(self._truncate(description, self._DESCRIPTION_MAX_CHARS))

        # ── Acceptance Criteria ──
        ac = str(work_item.get("acceptance_criteria", ""))
        if ac:
            parts.append("\n## Acceptance Criteria")
            parts.append(self._truncate(ac, self._AC_MAX_CHARS))

        # ── Top 5 comment themes ──
        comments: List[Dict[str, Any]] = work_item.get("comments", [])
        if comments:
            parts.append("\n## Top Comment Themes")
            for i, comment in enumerate(comments[: self._MAX_COMMENT_THEMES]):
                author = comment.get("author", "?")
                text = self._truncate(str(comment.get("text", "")), 200)
                parts.append(f"  {i + 1}. [{author}] {text}")

        # ── Child tasks (≤ 2 levels) ──
        child_tasks: List[Dict[str, Any]] = work_item.get("child_tasks", [])
        if child_tasks:
            parts.append("\n## Child Tasks")
            for task in child_tasks[: self._MAX_CHILD_TASKS_PER_LEVEL]:
                tid = task.get("id", "?")
                ttitle = self._truncate(str(task.get("title", "")), 100)
                tstate = task.get("state", "")
                line = f"  - #{tid}: {ttitle}"
                if tstate:
                    line += f" [{tstate}]"
                parts.append(line)
            if len(child_tasks) > self._MAX_CHILD_TASKS_PER_LEVEL:
                remaining = len(child_tasks) - self._MAX_CHILD_TASKS_PER_LEVEL
                parts.append(f"  … and {remaining} more tasks")

        result = "\n".join(parts)
        return self._enforce_budget(result)

    # ── Private helpers ───────────────────────────────────────────────────────

    @staticmethod
    def _truncate(text: str, max_len: int) -> str:
        """Truncate *text* to *max_len* characters at a word boundary.

        Appends ``…`` if truncation occurs.

        Args:
            text: Input string.
            max_len: Maximum allowed length.

        Returns:
            Truncated string, possibly ending with ``…``.
        """
        if len(text) <= max_len:
            return text
        truncated = text[: max_len - 1].rsplit(" ", 1)[0]
        return truncated + "…"

    def _enforce_budget(self, text: str) -> str:
        """Enforce the overall character budget.

        If *text* exceeds the budget, truncate at the last newline before
        the budget limit and append a budget-exceeded notice.

        Args:
            text: Assembled summary text.

        Returns:
            Text guaranteed to be ≤ ``_budget`` characters.
        """
        if len(text) <= self._budget:
            return text
        # Leave room for the notice
        notice = "\n… [truncated to fit 8000-char context budget]"
        cut_at = self._budget - len(notice)
        # Truncate at a safe point
        truncated = text[:cut_at]
        # Try to cut at last newline for cleanliness
        last_nl = truncated.rfind("\n")
        if last_nl > cut_at // 2:
            truncated = truncated[:last_nl]
        return truncated + notice
