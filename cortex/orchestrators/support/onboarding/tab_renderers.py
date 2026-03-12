"""Tab renderers and PersonaLayer for persona-layered dashboard output.

Phase 151-c — GAP-151-03
Governance: GV-030, GV-031, GV-032, GV-034
Author: Asif Hussain | © 2025-2026 CORTEX Framework
"""

from __future__ import annotations

import html
from typing import Any


class TabRenderer:
    """Dispatch dashboard tab rendering to per-tab methods.

    GV-034 contract:
        render_tab(tab_id: str, manifest: DashboardManifest) -> str

    Unknown ``tab_id`` values fall back to :meth:`_render_generic` (a
    ``no-data`` card).  All user-supplied values are HTML-escaped via
    :meth:`_esc` before insertion to prevent XSS (OWASP A03).
    """

    # ─── Public API ──────────────────────────────────────────────────────

    def render_tab(self, tab_id: str, manifest: Any) -> str:  # noqa: ANN401
        """Render the requested tab by dispatching to a per-tab method.

        Args:
            tab_id:   Tab identifier string (e.g. ``"01-overview"``).
            manifest: Dashboard data manifest (dict or DashboardManifest).

        Returns:
            An HTML string for the tab body.
        """
        method_name = "_render_" + tab_id.replace("-", "_")
        method = getattr(self, method_name, self._render_generic)
        return method(manifest)

    # ─── Per-tab methods ─────────────────────────────────────────────────

    def _render_01_overview(self, manifest: Any) -> str:  # noqa: ANN401
        """Overview tab — high-level summary card."""
        if isinstance(manifest, dict):
            title = self._esc(str(manifest.get("title", "Overview")))
        else:
            title = "Overview"
        return f"<section class='tab-overview'><h2>{title}</h2></section>"

    def _render_02_metrics(self, manifest: Any) -> str:  # noqa: ANN401
        """Metrics tab — numeric metrics card."""
        return "<section class='tab-metrics'><p>Metrics</p></section>"

    def _render_03_health(self, manifest: Any) -> str:  # noqa: ANN401
        """Health tab — health-check summary card."""
        return "<section class='tab-health'><p>Health</p></section>"

    def _render_04_pipeline(self, manifest: Any) -> str:  # noqa: ANN401
        """Pipeline tab — pipeline status card."""
        return "<section class='tab-pipeline'><p>Pipeline</p></section>"

    def _render_05_governance(self, manifest: Any) -> str:  # noqa: ANN401
        """Governance tab — governance compliance card."""
        return "<section class='tab-governance'><p>Governance</p></section>"

    def _render_generic(self, manifest: Any) -> str:  # noqa: ANN401
        """Fallback renderer — returns a no-data card."""
        return self._no_data_card("Tab content unavailable")

    # ─── Helpers ─────────────────────────────────────────────────────────

    def _esc(self, value: str) -> str:
        """HTML-escape *value* to prevent XSS (OWASP A03).

        Args:
            value: Raw user-supplied or data-sourced string.

        Returns:
            HTML-safe escaped string.
        """
        return html.escape(str(value))

    def _no_data_card(self, label: str) -> str:
        """Return a generic 'no data' HTML card.

        Args:
            label: Human-readable description, HTML-escaped before use.

        Returns:
            HTML div with class ``no-data``.
        """
        return f"<div class='no-data'>{self._esc(label)}</div>"


class PersonaLayer:
    """Adapt HTML fragments for engineering personas (GV-030, GV-031).

    Supported personas: ``engineer``, ``architect``, ``manager``.
    Unknown personas receive a passthrough (no transformation).

    GV-031 contract:
        ``adapt()`` **never raises** — returns the original ``html_fragment``
        on any internal error.
    """

    PERSONAS: frozenset[str] = frozenset({"engineer", "architect", "manager"})
    """Canonical set of supported persona identifiers (GV-028-equivalent)."""

    # Persona-specific CSS class injected as a wrapper
    _PERSONA_CLASS: dict[str, str] = {
        "engineer": "persona-engineer",
        "architect": "persona-architect",
        "manager": "persona-manager",
    }

    def adapt(self, html_fragment: str, persona: str) -> str:
        """Adapt *html_fragment* for the given *persona*.

        Unknown personas are returned unchanged (passthrough).
        Any internal error is suppressed and *html_fragment* is returned
        plain — GV-031 compliance.

        Args:
            html_fragment: Raw HTML string to adapt.
            persona:       Target persona identifier.

        Returns:
            Adapted HTML string (never raises).
        """
        try:
            if not html_fragment:
                return html_fragment if isinstance(html_fragment, str) else ""
            if persona not in self.PERSONAS:
                return html_fragment  # unknown persona: passthrough
            return self._adapt_for(html_fragment, persona)
        except Exception:  # noqa: BLE001  # GV-031: never raise
            return html_fragment if isinstance(html_fragment, str) else ""

    # ─── Private ─────────────────────────────────────────────────────────

    def _adapt_for(self, html_fragment: str, persona: str) -> str:
        """Apply persona-specific wrapper to *html_fragment*.

        Args:
            html_fragment: Validated non-empty HTML string.
            persona:       Known persona identifier.

        Returns:
            HTML string wrapped in a persona-class div.
        """
        css_class = self._PERSONA_CLASS.get(persona, "persona-default")
        return f"<div class='{css_class}'>{html_fragment}</div>"
