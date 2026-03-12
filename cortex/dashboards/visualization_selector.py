"""Visualization Selector — Stage 3 of the Dashboard Intelligence Pipeline.

Phase 152-c — GAP-152-03
Source: GitHub Issue #18, FB-20260312-001
Author: Asif Hussain | © 2025-2026 CORTEX Framework
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List


class DataShape(str, Enum):
    """Classification of the underlying data structure for a visualization."""

    RELATIONAL = "relational"
    TEMPORAL = "temporal"
    PROPORTIONAL = "proportional"
    CATEGORICAL = "categorical"
    SCALAR = "scalar"


class ChartType(str, Enum):
    """Supported chart / visualization types."""

    BAR = "bar"
    LINE = "line"
    PIE = "pie"
    TABLE = "table"
    METRIC_CARD = "metric_card"
    HEATMAP = "heatmap"
    SCATTER = "scatter"
    SANKEY = "sankey"


@dataclass
class VisualizationChoice:
    """A ranked visualization recommendation for a single dashboard tab.

    Attributes:
        tab_id:              Tab this choice is for.
        chart_type:          Recommended chart type.
        data_shape:          Underlying data shape.
        five_second_primary: True when the primary metric is scannable in ≤5 s.
        f_pattern_position:  Layout position (``"top-left"``, ``"body-full"``, …).
    """

    tab_id: str
    chart_type: ChartType
    data_shape: DataShape
    five_second_primary: bool
    f_pattern_position: str


# ─── Per-tab heuristic definitions ───────────────────────────────────────────

_TAB_HEURISTICS: Dict[str, List[VisualizationChoice]] = {
    "overview": [
        VisualizationChoice("overview", ChartType.METRIC_CARD, DataShape.SCALAR, True, "top-left"),
        VisualizationChoice("overview", ChartType.TABLE, DataShape.RELATIONAL, False, "body-full"),
    ],
    "metrics": [
        VisualizationChoice("metrics", ChartType.METRIC_CARD, DataShape.SCALAR, True, "top-left"),
        VisualizationChoice("metrics", ChartType.LINE, DataShape.TEMPORAL, False, "body-full"),
        VisualizationChoice("metrics", ChartType.BAR, DataShape.CATEGORICAL, False, "body-full"),
    ],
    "health": [
        VisualizationChoice("health", ChartType.METRIC_CARD, DataShape.SCALAR, True, "top-left"),
        VisualizationChoice("health", ChartType.TABLE, DataShape.CATEGORICAL, False, "body-full"),
    ],
    "pipeline": [
        VisualizationChoice("pipeline", ChartType.SANKEY, DataShape.RELATIONAL, True, "top-left"),
        VisualizationChoice("pipeline", ChartType.TABLE, DataShape.TEMPORAL, False, "body-full"),
    ],
    "security": [
        VisualizationChoice("security", ChartType.METRIC_CARD, DataShape.SCALAR, True, "top-left"),
        VisualizationChoice("security", ChartType.HEATMAP, DataShape.CATEGORICAL, False, "body-full"),
    ],
    "governance": [
        VisualizationChoice("governance", ChartType.METRIC_CARD, DataShape.SCALAR, True, "top-left"),
        VisualizationChoice("governance", ChartType.PIE, DataShape.PROPORTIONAL, False, "top-right"),
    ],
}

_DEFAULT_CHOICE_TEMPLATE = lambda tab_id: VisualizationChoice(  # noqa: E731
    tab_id=tab_id,
    chart_type=ChartType.METRIC_CARD,
    data_shape=DataShape.SCALAR,
    five_second_primary=True,
    f_pattern_position="top-left",
)


class VisualizationSelector:
    """Select ranked visualization choices for a dashboard tab.

    Stage 3 of the Dashboard Intelligence Pipeline (SELECT).

    Applies 5-Second Rule and F-Pattern heuristics:
    - **5-Second Rule**: the primary metric must be scannable within 5 seconds
      → always leads with a ``METRIC_CARD`` (``five_second_primary=True``).
    - **F-Pattern**: most important information in ``"top-left"`` area.

    Graceful degradation: returns a single default METRIC_CARD for unknown tabs.
    """

    def select(self, tab_id: str, tab_data: Dict[str, Any]) -> List[VisualizationChoice]:  # noqa: ARG002
        """Return ranked visualization choices for *tab_id*.

        Args:
            tab_id:   Tab identifier.
            tab_data: Per-tab data dict (used in future extensions).

        Returns:
            Non-empty list of :class:`VisualizationChoice` objects.
        """
        return list(_TAB_HEURISTICS.get(tab_id, [_DEFAULT_CHOICE_TEMPLATE(tab_id)]))
