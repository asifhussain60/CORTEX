"""
PersonalityLayer — Phase 150-c.

Provides voiced, empathetic formatting for CORTEX orchestrator output.
The layer wraps plain-text summaries, DoD items, and context headers in a
configured persona tone without changing their semantic content.

All public methods are fail-safe (CORE-049): any exception returns the
original plain-text input unchanged so orchestrators never crash on
presentation formatting.

Phase: 150-c (GAP-150-03)
CORE: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings),
      CORE-049 (silent autonomous — NEVER raises)
"""
from __future__ import annotations

import logging
from typing import List, Optional

logger = logging.getLogger(__name__)

# Persona → prefix fragments (for voiced_context_header)
_PERSONA_HEADERS: dict[str, str] = {
    "architect": "🏗️ Architecture lens active.",
    "mentor": "📚 Here's what I understand.",
    "coach": "🎯 Let's make this clear.",
    "default": "🧠 CORTEX is ready.",
}

# Persona → DoD item prefix
_PERSONA_DOD_PREFIX: dict[str, str] = {
    "architect": "Design goal:",
    "mentor": "We'll ensure:",
    "coach": "Checkpoint:",
    "default": "✅",
}


class PersonalityLayer:
    """
    Voiced presentation layer for CORTEX orchestrator responses.

    Wraps plain-text summaries, DoD items, and context headers in the
    configured persona tone.  All methods are fail-safe — they NEVER raise;
    any internal error returns the plain-text input unchanged.

    Personas available: ``"architect"``, ``"mentor"``, ``"coach"``,
    ``"default"`` (fallback for any unknown name).

    Usage::

        layer = PersonalityLayer(persona="mentor")
        print(layer.voiced_summary("Run the TDD suite before merging."))
        print(layer.voiced_context_header())
        print(layer.voiced_dod_items(["All tests green", "No lint errors"]))

    Phase: 150-c (GAP-150-03)
    """

    def __init__(self, persona: str = "default") -> None:
        """Initialise with a named persona.

        Args:
            persona: Persona name — one of ``"architect"``, ``"mentor"``,
                ``"coach"``, ``"default"``.  Unknown names fall back to
                ``"default"``.
        """
        self._persona = persona if persona in _PERSONA_HEADERS else "default"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    @property
    def persona(self) -> str:
        """Active persona name."""
        return self._persona

    def voiced_summary(self, summary: str) -> str:
        """Return a voiced, empathetic version of a plain-text summary.

        Args:
            summary: Plain-text summary from an orchestrator.

        Returns:
            Voiced summary.  Falls back to *summary* on error.
        """
        try:
            if not summary or not summary.strip():
                return summary
            header = _PERSONA_HEADERS.get(self._persona, _PERSONA_HEADERS["default"])
            return f"{header} {summary.strip()}"
        except Exception as exc:  # pragma: no cover
            logger.debug("PersonalityLayer.voiced_summary failed: %s", exc)
            return summary

    def voiced_dod_items(self, items: List[str]) -> List[str]:
        """Return DoD items wrapped with a persona-specific prefix.

        Args:
            items: List of plain-text DoD strings.

        Returns:
            List of voiced DoD strings.  Falls back to *items* on error.
        """
        try:
            if not items:
                return items
            prefix = _PERSONA_DOD_PREFIX.get(
                self._persona, _PERSONA_DOD_PREFIX["default"]
            )
            return [f"{prefix} {item.strip()}" for item in items if item]
        except Exception as exc:  # pragma: no cover
            logger.debug("PersonalityLayer.voiced_dod_items failed: %s", exc)
            return items

    def voiced_context_header(
        self, extra: Optional[str] = None
    ) -> str:
        """Return a voiced context header for the current persona.

        Args:
            extra: Optional extra context to append after the header.

        Returns:
            Voiced context header string.  Falls back to empty string on error.
        """
        try:
            header = _PERSONA_HEADERS.get(self._persona, _PERSONA_HEADERS["default"])
            if extra and extra.strip():
                return f"{header} {extra.strip()}"
            return header
        except Exception as exc:  # pragma: no cover
            logger.debug("PersonalityLayer.voiced_context_header failed: %s", exc)
            return extra or ""
