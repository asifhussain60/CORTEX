"""Tests for PO Dashboard Tab 11 in docs/index.html (Phase 129-g)."""

from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

DOCS_DIR = Path(__file__).resolve().parents[2] / "docs"
INDEX_HTML = DOCS_DIR / "index.html"
PO_METRICS_SCHEMA = DOCS_DIR / "data" / "po-metrics-schema.json"


# ---------------------------------------------------------------------------
# Tab 11 Navigation Item
# ---------------------------------------------------------------------------


class TestPODashboardTabNav:
    """Tab 11 nav item must exist in docs/index.html."""

    def setup_method(self) -> None:
        self.content = INDEX_HTML.read_text()

    def test_index_html_exists(self) -> None:
        assert INDEX_HTML.exists(), "docs/index.html must exist"

    def test_po_dashboard_tab_id_present(self) -> None:
        assert 'id="po-dashboard-tab"' in self.content, (
            "PO Dashboard section with id='po-dashboard-tab' not found in docs/index.html"
        )

    def test_po_dashboard_nav_item_present(self) -> None:
        assert 'id="po-dashboard-nav"' in self.content, (
            "Tab 11 nav item with id='po-dashboard-nav' not found in docs/index.html"
        )

    def test_po_dashboard_tab_index_is_11(self) -> None:
        assert 'data-tab-index="11"' in self.content, (
            "Tab nav item must have data-tab-index='11' for Tab 11"
        )

    def test_po_dashboard_heading_present(self) -> None:
        assert "PO Dashboard" in self.content, (
            "PO Dashboard heading text not found in docs/index.html"
        )

    def test_po_dashboard_section_has_aria_label(self) -> None:
        assert 'aria-labelledby="po-dashboard-heading"' in self.content


# ---------------------------------------------------------------------------
# D3 Velocity Chart Div
# ---------------------------------------------------------------------------


class TestPODashboardVelocityChart:
    """D3 velocity chart div must exist with correct attributes."""

    def setup_method(self) -> None:
        self.content = INDEX_HTML.read_text()

    def test_po_velocity_chart_div_exists(self) -> None:
        assert 'id="po-velocity-chart"' in self.content, (
            "D3 velocity chart div with id='po-velocity-chart' not found in docs/index.html"
        )

    def test_velocity_chart_references_schema(self) -> None:
        assert "po-metrics-schema.json" in self.content, (
            "po-metrics-schema.json must be referenced in docs/index.html for D3 data binding"
        )

    def test_velocity_chart_has_aria_label(self) -> None:
        assert 'aria-label="Sprint velocity trend chart' in self.content

    def test_velocity_chart_has_role_img(self) -> None:
        assert 'role="img"' in self.content


# ---------------------------------------------------------------------------
# po-metrics-schema.json
# ---------------------------------------------------------------------------


class TestPOMetricsSchema:
    """po-metrics-schema.json must exist and be valid JSON with required keys."""

    def test_schema_file_exists(self) -> None:
        assert PO_METRICS_SCHEMA.exists(), "docs/data/po-metrics-schema.json must exist"

    def test_schema_is_valid_json(self) -> None:
        data = json.loads(PO_METRICS_SCHEMA.read_text())
        assert isinstance(data, dict)

    def test_schema_has_velocity_trend_key(self) -> None:
        data = json.loads(PO_METRICS_SCHEMA.read_text())
        assert "velocity_trend" in data

    def test_schema_has_cycle_time_distribution_key(self) -> None:
        data = json.loads(PO_METRICS_SCHEMA.read_text())
        assert "cycle_time_distribution" in data

    def test_schema_has_predictability_score_key(self) -> None:
        data = json.loads(PO_METRICS_SCHEMA.read_text())
        assert "predictability_score" in data

    def test_schema_has_blocked_themes_key(self) -> None:
        data = json.loads(PO_METRICS_SCHEMA.read_text())
        assert "blocked_themes" in data

    def test_schema_version_present(self) -> None:
        data = json.loads(PO_METRICS_SCHEMA.read_text())
        assert "version" in data
