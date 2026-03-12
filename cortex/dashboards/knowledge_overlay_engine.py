"""Knowledge Overlay Engine — Stage 2 of the Dashboard Intelligence Pipeline.

Phase 152-b — GAP-152-02
Source: GitHub Issue #18, FB-20260312-001
Author: Asif Hussain | © 2025-2026 CORTEX Framework
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List

from cortex.dashboards.data_collector import DashboardManifest

# ─── Tab → domain mapping ────────────────────────────────────────────────────

TAB_DOMAIN_MAP: Dict[str, str] = {
    "overview": "cortex-frame-context",
    "architecture": "sdlc-patterns",
    "quality": "quality",
    "security": "security",
    "observability": "observability",
    "metrics": "performance-optimization",
    "health": "governance",
    "pipeline": "sdlc-patterns",
    "governance": "governance",
    "testing": "testing-validation",
}
"""Canonical mapping of dashboard tab_id → knowledge domain.

Used by :class:`KnowledgeOverlayEngine` to resolve which registry YAML
domain to search for knowledge enrichment entries.
"""


@dataclass
class KnowledgeOverlay:
    """Knowledge enrichment data for a single dashboard tab.

    Attributes:
        tab_id:            The tab this overlay is for.
        domain:            Registry domain resolved for this tab.
        knowledge_entries: List of knowledge entry dicts from the registry.
        source_yaml:       Path hint for the primary source YAML (may be empty).
    """

    tab_id: str
    domain: str
    knowledge_entries: List[Dict[str, Any]] = field(default_factory=list)
    source_yaml: str = ""


class KnowledgeOverlayEngine:
    """Enrich a :class:`DashboardManifest` with registry knowledge overlays.

    Stage 2 of the Dashboard Intelligence Pipeline (OVERLAY).

    Uses :func:`cortex.intelligence.facade.IntelligenceFacade.registry_index`
    to fetch domain knowledge entries.  Graceful degradation: unknown tabs or
    registry errors return an empty :class:`KnowledgeOverlay` (never raises).
    """

    def overlay(self, manifest: DashboardManifest) -> Dict[str, KnowledgeOverlay]:
        """Return a mapping of tab_id → :class:`KnowledgeOverlay` for all tabs.

        Args:
            manifest: The :class:`DashboardManifest` from Stage 1 COLLECT.

        Returns:
            Dict mapping each tab_id to a :class:`KnowledgeOverlay`.
        """
        result: Dict[str, KnowledgeOverlay] = {}
        for tab_id in manifest.tabs:
            result[tab_id] = self._overlay_tab(tab_id)
        return result

    # ─── Private ─────────────────────────────────────────────────────────

    def _overlay_tab(self, tab_id: str) -> KnowledgeOverlay:
        """Produce a :class:`KnowledgeOverlay` for a single tab.

        Falls back to an empty overlay on any error.

        Args:
            tab_id: The tab identifier.

        Returns:
            A :class:`KnowledgeOverlay` (never raises).
        """
        domain = TAB_DOMAIN_MAP.get(tab_id, "")
        try:
            entries = self._fetch_entries(domain) if domain else []
        except Exception:  # noqa: BLE001
            entries = []
        return KnowledgeOverlay(
            tab_id=tab_id,
            domain=domain,
            knowledge_entries=entries,
            source_yaml=domain,
        )

    @staticmethod
    def _fetch_entries(domain: str) -> List[Dict[str, Any]]:
        """Fetch knowledge entries for *domain* via IntelligenceFacade.

        Args:
            domain: Registry domain name.

        Returns:
            List of entry dicts (may be empty if domain has no entries).
        """
        try:
            from cortex.intelligence.facade import IntelligenceFacade  # local import

            facade = IntelligenceFacade()
            all_entries = facade.registry_index(domain)
            return [e.__dict__ if hasattr(e, "__dict__") else dict(e) for e in all_entries]
        except Exception:  # noqa: BLE001
            return []
