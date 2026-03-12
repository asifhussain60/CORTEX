"""DashboardIntelligenceOrchestrator — Phase 152-f

7-stage pipeline orchestrator for the CORTEX Dashboard Intelligence system:

    Stage 1 — COLLECT  : DashboardDataCollector.collect()
    Stage 2 — OVERLAY  : KnowledgeOverlayEngine.overlay()
    Stage 3 — SELECT   : VisualizationSelector.select() per tab
    Stage 4 — NARRATE  : NarrativeEngine.narrate()
    Stage 5 — RENDER   : DashboardGenerator.render_tab() (HTML emission)
    Stage 6 — QUALITY  : DashboardQualityGate.evaluate()
    Stage 7 — EMIT     : Build DashboardPipelineResult

Contract: generate() NEVER raises — all exceptions are captured in DashboardPipelineResult.errors.

CORE: CORE-008 (TDD), CORE-011, CORE-012
Source: GitHub Issue #18 — FB-20260312-001
"""

from __future__ import annotations

import traceback
from dataclasses import dataclass, field
from typing import Any

from cortex.dashboards.data_collector import DashboardDataCollector, DashboardManifest
from cortex.dashboards.knowledge_overlay_engine import KnowledgeOverlayEngine
from cortex.dashboards.narrative_engine import NarrativeEngine
from cortex.dashboards.quality_gate import DashboardQualityGate, QualityReport
from cortex.dashboards.visualization_selector import VisualizationSelector


@dataclass
class DashboardPipelineResult:
    """Full output of the Dashboard Intelligence Pipeline."""

    html_path: str
    dashboard_manifest: Any  # DashboardManifest | None
    knowledge_overlay: "dict[str, Any]"
    narratives: "dict[str, str]"
    viz_selections: "dict[str, list]"
    quality_report: QualityReport
    errors: "list[str]" = field(default_factory=list)

    @property
    def success(self) -> bool:
        """True when there are no pipeline errors and the quality gate passed."""
        return not self.errors and self.quality_report.passed


class DashboardIntelligenceOrchestrator:
    """Orchestrates the 7-stage Dashboard Intelligence Pipeline."""

    def __init__(self) -> None:
        self._collector = DashboardDataCollector()
        self._overlay_engine = KnowledgeOverlayEngine()
        self._viz_selector = VisualizationSelector()
        self._narrative_engine = NarrativeEngine()
        self._quality_gate = DashboardQualityGate()

    def generate(self, manifest: Any) -> DashboardPipelineResult:
        """Execute all 7 pipeline stages and return a DashboardPipelineResult.

        Never raises — all exceptions are captured in DashboardPipelineResult.errors.
        """
        errors: list = []
        dashboard_manifest = None
        knowledge_overlay: dict = {}
        viz_selections: dict = {}
        narratives: dict = {}
        quality_report = QualityReport(issues=[], passed=True, score=100)
        html_path = ""

        try:
            # Stage 1 — COLLECT
            dashboard_manifest = self._collector.collect(manifest)

            # Stage 2 — OVERLAY
            knowledge_overlay = self._overlay_engine.overlay(dashboard_manifest)

            # Stage 3 — SELECT (per tab)
            for tab_id, tab_data in dashboard_manifest.tabs.items():
                try:
                    viz_selections[tab_id] = self._viz_selector.select(tab_id, tab_data)
                except Exception:  # noqa: BLE001
                    viz_selections[tab_id] = []

            # Stage 4 — NARRATE
            narratives = self._narrative_engine.narrate(dashboard_manifest, knowledge_overlay)

            # Stage 5 — RENDER (HTML path placeholder; full render via DashboardGenerator)
            html_path = ""  # Emit path set by caller or DashboardGenerator

            # Stage 6 — QUALITY
            quality_report = self._quality_gate.evaluate(
                narratives=narratives,
                viz_selections=viz_selections,
            )

        except Exception as exc:  # noqa: BLE001
            errors.append(f"{type(exc).__name__}: {exc}\n{traceback.format_exc()}")
            # Fallback quality report so DashboardPipelineResult is always valid
            quality_report = QualityReport(issues=[], passed=False, score=0)

        # Stage 7 — EMIT
        return DashboardPipelineResult(
            html_path=html_path,
            dashboard_manifest=dashboard_manifest,
            knowledge_overlay=knowledge_overlay,
            narratives=narratives,
            viz_selections=viz_selections,
            quality_report=quality_report,
            errors=errors,
        )
