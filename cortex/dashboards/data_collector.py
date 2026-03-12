"""Dashboard Data Collector — Stage 1 of the Dashboard Intelligence Pipeline.

Phase 152-a — GAP-152-01
Source: GitHub Issue #18, FB-20260312-001, AC-001-01
Author: Asif Hussain | © 2025-2026 CORTEX Framework
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict


@dataclass
class DashboardManifest:
    """Structured dashboard data extracted from an OnboardingManifest.

    Serves as the canonical data carrier for the 7-stage intelligence
    pipeline (Phase 152).

    Attributes:
        repo_name:  Human-readable repository name.
        repo_path:  Absolute path to the repository root on disk.
        tabs:       Mapping of tab_id → tab data dict.
        archetype:  Detected repository archetype (e.g. ``"python-service"``).
        metadata:   Arbitrary additional metadata from the source manifest.
    """

    repo_name: str
    repo_path: str
    tabs: Dict[str, Dict[str, Any]]
    archetype: str
    metadata: Dict[str, Any] = field(default_factory=dict)


class DashboardDataCollector:
    """Extract a :class:`DashboardManifest` from an onboarding manifest dict.

    Stage 1 of the Dashboard Intelligence Pipeline (COLLECT).

    Tolerates ``None`` or partial input — all fields fall back to safe
    defaults (graceful degradation).
    """

    # Default tab skeleton injected when the source manifest omits tabs
    _DEFAULT_TABS: Dict[str, Dict[str, Any]] = {
        "overview": {},
        "metrics": {},
        "health": {},
    }

    def collect(self, manifest: Any) -> DashboardManifest:  # noqa: ANN401
        """Extract structured dashboard data from *manifest*.

        Args:
            manifest: Source manifest — typically a dict from
                :class:`~cortex.orchestrators.support.onboarding.OnboardingManifest`
                or any dict-like object.  Accepts ``None`` gracefully.

        Returns:
            A fully populated :class:`DashboardManifest`.
        """
        if not isinstance(manifest, dict):
            manifest = {}

        repo_name: str = str(manifest.get("repo_name", ""))
        repo_path: str = str(manifest.get("repo_path", ""))
        archetype: str = str(manifest.get("archetype", ""))
        metadata: Dict[str, Any] = dict(manifest.get("metadata", {}))
        raw_tabs = manifest.get("tabs")
        tabs: Dict[str, Dict[str, Any]] = (
            dict(raw_tabs) if isinstance(raw_tabs, dict) else dict(self._DEFAULT_TABS)
        )

        return DashboardManifest(
            repo_name=repo_name,
            repo_path=repo_path,
            tabs=tabs,
            archetype=archetype,
            metadata=metadata,
        )
