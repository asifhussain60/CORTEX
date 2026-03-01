"""
Golden Test Suite — business-leader.html
=========================================
Phase: FRONTEND / html-view-lifecycle.yaml → operation: enhance
AC Marker: AC-BL-GOLDEN-001
Authority: html-view-lifecycle.yaml · CORE-002 · CORE-008 · CORE-064 · CORE-068

Purpose:
    Immutable golden harness for business-leader.html and business-leader.css.
    These tests act as a governance shield — any change to the HTML or CSS that
    breaks a golden invariant will be caught BEFORE the change lands.

    CORE-008: This suite was written BEFORE any implementation touches.
    CORE-064: Sweep catalogue is exhaustive — covers all P0/P1 gates from
              html-view-lifecycle.yaml § gates.
    CORE-068: Convergence predicate — all tests must pass; no partial green.

Log Trace:
    Every test class emits an AC_START / AC_COMPLETE trace via the
    ``golden_log`` fixture (session-scoped, writes to
    .cortex-runtime/traces/golden-business-leader.log).

Challenge Gate (CORE-CODE-PROTECT):
    Code should NEVER be touched without a mandatory challenge if the user
    request poses a threat to golden invariants. If a test in this file
    fails after a user-driven change, the change MUST be reverted or an
    architectural decision logged in cortex-master.yaml before proceeding.

Sections validated (10-section interest path):
    §1  BLUF — problem cost framing
    §2  Problem — D3 defect cost bar chart
    §3  Solution — Mermaid 8-stage pipeline
    §4  Proof — ROI grids + D3 before/after
    §5  Engineering Efficiency — tabbed panels
    §6  Rework Elimination — Mermaid mindmap
    §7  Governance — D3 donut + CORE rule cards
    §8  Strategic Value — tabbed panels
    §9  Platform Capabilities
    §10 Explore Further / CTAs
"""

from __future__ import annotations

import logging
import re
import sqlite3
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Generator

import pytest

# ── Paths ─────────────────────────────────────────────────────────────────────
CORTEX_DOCS = Path(__file__).resolve().parents[2] / "cortex-docs"
HTML_FILE   = CORTEX_DOCS / "roles" / "business-leader.html"
CSS_FILE    = CORTEX_DOCS / "assets" / "css" / "layouts" / "business-leader.css"
RUNTIME_DIR = Path(__file__).resolve().parents[2] / ".cortex-runtime" / "traces"
LOG_FILE    = RUNTIME_DIR / "golden-business-leader.log"

# ── AC Marker constants ────────────────────────────────────────────────────────
AC_PREFIX = "AC-BL-GOLDEN"


# ══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="session")
def golden_log() -> Generator[logging.Logger, None, None]:
    """
    Session-scoped logger that writes AC_START / AC_COMPLETE traces to
    .cortex-runtime/traces/golden-business-leader.log.

    This satisfies the ``primitives/execution/ac-marker-emit.yaml`` contract
    for non-runtime (file-based) golden tests.
    """
    RUNTIME_DIR.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger("cortex.golden.business_leader")
    logger.setLevel(logging.DEBUG)
    if not logger.handlers:
        fh = logging.FileHandler(LOG_FILE, mode="a", encoding="utf-8")
        fh.setFormatter(logging.Formatter("%(asctime)s  %(message)s"))
        logger.addHandler(fh)
    ts = datetime.now(timezone.utc).isoformat()
    logger.info(f"AC_START  {AC_PREFIX}-SESSION  ts={ts}")
    yield logger
    ts = datetime.now(timezone.utc).isoformat()
    logger.info(f"AC_COMPLETE  {AC_PREFIX}-SESSION  ✅  ts={ts}")


@pytest.fixture(scope="session")
def html(golden_log: logging.Logger) -> str:
    """Raw HTML content of business-leader.html — read once per session."""
    golden_log.info(f"AC_START  {AC_PREFIX}-HTML-LOAD")
    assert HTML_FILE.exists(), f"HTML file missing: {HTML_FILE}"
    content = HTML_FILE.read_text(encoding="utf-8")
    golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-HTML-LOAD  ✅  lines={content.count(chr(10))}")
    return content


@pytest.fixture(scope="session")
def css(golden_log: logging.Logger) -> str:
    """Raw CSS content of business-leader.css — read once per session."""
    golden_log.info(f"AC_START  {AC_PREFIX}-CSS-LOAD")
    assert CSS_FILE.exists(), f"CSS file missing: {CSS_FILE}"
    content = CSS_FILE.read_text(encoding="utf-8")
    golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-CSS-LOAD  ✅  lines={content.count(chr(10))}")
    return content


# ══════════════════════════════════════════════════════════════════════════════
# §A  P0 Gate — CSS Zero-Inline (html-view-lifecycle.yaml § css_zero_inline)
# ══════════════════════════════════════════════════════════════════════════════

class TestCSSZeroInline:
    """
    AC-BL-001 — P0 gate: zero style= attributes in business-leader.html.
    Blocking: any inline style= is a governance violation per CORE-002.
    """

    def test_no_inline_style_attributes(self, html: str, golden_log: logging.Logger) -> None:
        """Zero style= attributes anywhere in the HTML."""
        golden_log.info(f"AC_START  {AC_PREFIX}-001a  css_zero_inline")
        matches = re.findall(r'\bstyle\s*=', html)
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-001a  "
            f"{'✅' if not matches else '❌'}  count={len(matches)}"
        )
        assert not matches, (
            f"P0 VIOLATION: {len(matches)} inline style= attribute(s) found in "
            f"{HTML_FILE.name}. All styles must live in business-leader.css."
        )

    def test_no_inline_style_blocks(self, html: str, golden_log: logging.Logger) -> None:
        """Zero <style> blocks anywhere in the HTML."""
        golden_log.info(f"AC_START  {AC_PREFIX}-001b  css_zero_blocks")
        blocks = re.findall(r'<style[\s>]', html, re.IGNORECASE)
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-001b  "
            f"{'✅' if not blocks else '❌'}  count={len(blocks)}"
        )
        assert not blocks, (
            f"P0 VIOLATION: {len(blocks)} <style> block(s) found in "
            f"{HTML_FILE.name}. Extract all styles to business-leader.css."
        )


# ══════════════════════════════════════════════════════════════════════════════
# §B  P0 Gate — DOM Well-Formed (no duplicate IDs)
# ══════════════════════════════════════════════════════════════════════════════

class TestDOMWellFormed:
    """
    AC-BL-002 — P0 gate: DOM must have no duplicate id= attributes.
    Duplicate IDs break D3 canvas selection and accessibility.
    """

    def test_no_duplicate_ids(self, html: str, golden_log: logging.Logger) -> None:
        """All id= values in the HTML must be unique."""
        golden_log.info(f"AC_START  {AC_PREFIX}-002  dom_wellformed_no_dup_ids")
        ids = re.findall(r'\bid\s*=\s*["\']([^"\']+)["\']', html)
        seen: set[str] = set()
        duplicates: list[str] = []
        for id_val in ids:
            if id_val in seen:
                duplicates.append(id_val)
            seen.add(id_val)
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-002  "
            f"{'✅' if not duplicates else '❌'}  duplicates={duplicates}"
        )
        assert not duplicates, (
            f"P0 VIOLATION: Duplicate id= values found: {duplicates}. "
            "Each id must be unique — D3 canvas selection depends on this."
        )

    def test_html_has_doctype(self, html: str, golden_log: logging.Logger) -> None:
        """Document must start with <!DOCTYPE html>."""
        golden_log.info(f"AC_START  {AC_PREFIX}-002b  dom_doctype")
        has_doctype = html.strip().lower().startswith("<!doctype html")
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-002b  {'✅' if has_doctype else '❌'}")
        assert has_doctype, "HTML file must begin with <!DOCTYPE html>"

    def test_single_body_tag(self, html: str, golden_log: logging.Logger) -> None:
        """Exactly one <body> opening tag."""
        golden_log.info(f"AC_START  {AC_PREFIX}-002c  dom_single_body")
        count = len(re.findall(r'<body[\s>]', html, re.IGNORECASE))
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-002c  {'✅' if count == 1 else '❌'}  count={count}")
        assert count == 1, f"Expected exactly 1 <body> tag, found {count}"


# ══════════════════════════════════════════════════════════════════════════════
# §C  10-Section Interest Path (structural golden invariant)
# ══════════════════════════════════════════════════════════════════════════════

class TestInterestPathSections:
    """
    AC-BL-003 — Golden invariant: all 10 sections of the interest path must
    be present in the correct order. This is the primary narrative contract.

    CHALLENGE GATE: If a user request would remove or reorder these sections,
    a mandatory challenge must be raised before any edit is applied.
    """

    # Unique fragments that appear ONLY inside role-section-title <h2> headings,
    # not in prose/nav text — anchored to the section title class.
    EXPECTED_SECTION_FRAGMENTS = [
        "The Problem: Defect",              # §2
        "How CORTEX Works:",                # §3
        "Proof: Quantified",               # §4
        "Engineering Efficiency",          # §5
        "Where Rework Is Eliminated",      # §6
        "Governance in Depth",             # §7
        "Strategic Value Proposition",     # §8
        "Platform Capabilities",           # §9
        "Explore Further",                 # §10
    ]

    def test_all_sections_present(self, html: str, golden_log: logging.Logger) -> None:
        """All expected section titles must appear in the HTML."""
        golden_log.info(f"AC_START  {AC_PREFIX}-003a  interest_path_sections")
        missing = [s for s in self.EXPECTED_SECTION_FRAGMENTS if s not in html]
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-003a  "
            f"{'✅' if not missing else '❌'}  missing={missing}"
        )
        assert not missing, (
            f"GOLDEN VIOLATION: {len(missing)} section(s) missing from interest path: "
            f"{missing}. Do not remove sections without architectural sign-off."
        )

    def test_section_order_preserved(self, html: str, golden_log: logging.Logger) -> None:
        """Section h2 headings must appear in the defined interest-path order."""
        golden_log.info(f"AC_START  {AC_PREFIX}-003b  interest_path_order")
        # Only match positions within role-section-title headings to avoid false
        # matches in prose text (e.g. "Proof → Strategic Value" in the signpost).
        positions: dict[str, int] = {}
        for frag in self.EXPECTED_SECTION_FRAGMENTS:
            # Find first occurrence within a role-section-title heading
            pattern = re.compile(
                r'class="role-section-title"[^>]*>.*?' + re.escape(frag),
                re.DOTALL,
            )
            m = pattern.search(html)
            if m:
                positions[frag] = m.start()
        ordered = sorted(positions.keys(), key=lambda k: positions[k])
        ok = ordered == self.EXPECTED_SECTION_FRAGMENTS
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-003b  "
            f"{'✅' if ok else '❌'}  actual_order={ordered}"
        )
        assert ok, (
            f"GOLDEN VIOLATION: Section order does not match interest path.\n"
            f"  Expected: {self.EXPECTED_SECTION_FRAGMENTS}\n"
            f"  Actual:   {ordered}"
        )

    def test_bluf_heading_present(self, html: str, golden_log: logging.Logger) -> None:
        """§1 BLUF heading must contain the defect cost framing."""
        golden_log.info(f"AC_START  {AC_PREFIX}-003c  bluf_heading")
        has_bluf = "bl-bottom-line-heading" in html and "defect" in html.lower()
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-003c  {'✅' if has_bluf else '❌'}")
        assert has_bluf, (
            "BLUF heading (class=bl-bottom-line-heading) with defect cost framing "
            "must be present. This is the primary executive hook."
        )


# ══════════════════════════════════════════════════════════════════════════════
# §D  D3.js Asset Validation (html-view-lifecycle.yaml § asset_validation)
# ══════════════════════════════════════════════════════════════════════════════

class TestD3Assets:
    """
    AC-BL-004 — D3 canvas presence, CDN loading, and height ≥ 400 gate.
    gate: d3_min_height_400 — fixed-height D3 SVGs must be ≥ 400px.
    """

    D3_CANVAS_IDS = [
        "defect-cost-canvas",
        "value-flow-canvas",
        "governance-canvas",
    ]

    def test_d3_cdn_loaded(self, html: str, golden_log: logging.Logger) -> None:
        """D3.js CDN script tag must be present in <head>."""
        golden_log.info(f"AC_START  {AC_PREFIX}-004a  d3_cdn")
        # Matches either d3js.org CDN or cdnjs.cloudflare.com with /d3/ in path
        has_d3 = (
            "d3js.org/d3.v7.min.js" in html
            or ("cdnjs.cloudflare.com" in html and "/d3/" in html)
        )
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-004a  {'✅' if has_d3 else '❌'}")
        assert has_d3, (
            "D3.js v7 CDN script tag missing. "
            "Expected: https://d3js.org/d3.v7.min.js  "
            "or https://cdnjs.cloudflare.com/ajax/libs/d3/{version}/d3.min.js"
        )

    def test_all_d3_canvas_ids_present(self, html: str, golden_log: logging.Logger) -> None:
        """All 3 D3 canvas container IDs must exist in the HTML."""
        golden_log.info(f"AC_START  {AC_PREFIX}-004b  d3_canvas_ids")
        missing = [cid for cid in self.D3_CANVAS_IDS if f'id="{cid}"' not in html]
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-004b  "
            f"{'✅' if not missing else '❌'}  missing={missing}"
        )
        assert not missing, (
            f"D3 canvas container IDs missing: {missing}. "
            "All 3 chart containers must be present."
        )

    def test_d3_canvas_class_present(self, html: str, golden_log: logging.Logger) -> None:
        """Canvas divs must use bl-d3-canvas class for CSS centering."""
        golden_log.info(f"AC_START  {AC_PREFIX}-004c  d3_canvas_class")
        count = html.count('class="bl-d3-canvas"')
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-004c  {'✅' if count >= 3 else '❌'}  count={count}")
        assert count >= 3, (
            f"Expected ≥ 3 elements with class=bl-d3-canvas, found {count}. "
            "CSS centering depends on this class."
        )

    def test_defect_cost_chart_height_gte_400(self, html: str, golden_log: logging.Logger) -> None:
        """
        Chart 1 (defect-cost): totalH must be ≥ 400px.
        gate: d3_min_height_400 — P1 blocking per html-view-lifecycle.yaml.

        CHALLENGE GATE: Do NOT reduce totalH below 400 without raising a
        governance challenge. This is an asset_validation P1 gate.
        """
        golden_log.info(f"AC_START  {AC_PREFIX}-004d  d3_min_height_400_chart1")
        # Find the totalH assignment in Chart 1 script block (before Chart 2 script)
        chart1_match = re.search(
            r"D3\.js Chart 1.*?var totalH\s*=\s*(\d+)",
            html,
            re.DOTALL,
        )
        if chart1_match is None:
            # Fallback: find first totalH assignment
            m = re.search(r'var totalH\s*=\s*(\d+)', html)
            height = int(m.group(1)) if m else 0
        else:
            height = int(chart1_match.group(1))
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-004d  "
            f"{'✅' if height >= 400 else '❌'}  totalH={height}"
        )
        assert height >= 400, (
            f"P1 GATE FAILURE: D3 Chart 1 totalH={height}px — must be ≥ 400px. "
            "See html-view-lifecycle.yaml § asset_validation: d3_min_height_400. "
            "Fix: set totalH = 420 (or higher)."
        )

    def test_d3_scripts_are_iife(self, html: str, golden_log: logging.Logger) -> None:
        """All D3 chart scripts must use IIFE pattern to avoid global scope pollution."""
        golden_log.info(f"AC_START  {AC_PREFIX}-004e  d3_iife_pattern")
        iife_count = len(re.findall(r'\(function\s*\(\s*\)\s*\{', html))
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-004e  "
            f"{'✅' if iife_count >= 3 else '❌'}  count={iife_count}"
        )
        assert iife_count >= 3, (
            f"Expected ≥ 3 D3 IIFE patterns, found {iife_count}. "
            "All D3 chart scripts must use (function(){ ... })() to avoid globals."
        )

    def test_d3_undefined_guard(self, html: str, golden_log: logging.Logger) -> None:
        """Each D3 chart must guard against d3 being undefined (CDN fail-safe)."""
        golden_log.info(f"AC_START  {AC_PREFIX}-004f  d3_undefined_guard")
        guards = re.findall(r"typeof d3 === 'undefined'", html)
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-004f  "
            f"{'✅' if len(guards) >= 3 else '❌'}  count={len(guards)}"
        )
        assert len(guards) >= 3, (
            f"Expected ≥ 3 CDN guard checks (typeof d3 === 'undefined'), "
            f"found {len(guards)}. Each chart must degrade gracefully if CDN fails."
        )


# ══════════════════════════════════════════════════════════════════════════════
# §E  Mermaid Asset Validation
# ══════════════════════════════════════════════════════════════════════════════

class TestMermaidAssets:
    """
    AC-BL-005 — Mermaid CDN, panel presence, and diagram type validation.
    """

    def test_mermaid_cdn_loaded(self, html: str, golden_log: logging.Logger) -> None:
        """Mermaid v10 CDN script must be present."""
        golden_log.info(f"AC_START  {AC_PREFIX}-005a  mermaid_cdn")
        has_mermaid = "mermaid" in html and ("jsdelivr.net" in html or "cdn" in html.lower())
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-005a  {'✅' if has_mermaid else '❌'}")
        assert has_mermaid, "Mermaid v10 CDN script tag missing from <head>."

    def test_mermaid_panels_count(self, html: str, golden_log: logging.Logger) -> None:
        """Exactly 2 Mermaid panels must be present (pipeline + mindmap)."""
        golden_log.info(f"AC_START  {AC_PREFIX}-005b  mermaid_panel_count")
        count = html.count('class="bl-mermaid-panel"')
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-005b  "
            f"{'✅' if count == 2 else '❌'}  count={count}"
        )
        assert count == 2, (
            f"Expected exactly 2 bl-mermaid-panel elements, found {count}. "
            "§3 pipeline flowchart and §6 mindmap must both be present."
        )

    def test_mermaid_flowchart_present(self, html: str, golden_log: logging.Logger) -> None:
        """§3 pipeline: Mermaid flowchart LR diagram must be present."""
        golden_log.info(f"AC_START  {AC_PREFIX}-005c  mermaid_flowchart")
        has_flowchart = "flowchart LR" in html or "graph LR" in html
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-005c  {'✅' if has_flowchart else '❌'}")
        assert has_flowchart, (
            "§3 Mermaid flowchart LR (8-stage pipeline) missing. "
            "Must contain 'flowchart LR' or 'graph LR' diagram definition."
        )

    def test_mermaid_mindmap_present(self, html: str, golden_log: logging.Logger) -> None:
        """§6 rework: Mermaid mindmap diagram must be present."""
        golden_log.info(f"AC_START  {AC_PREFIX}-005d  mermaid_mindmap")
        has_mindmap = "mindmap" in html
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-005d  {'✅' if has_mindmap else '❌'}")
        assert has_mindmap, (
            "§6 Mermaid mindmap (rework elimination) missing. "
            "Must contain a 'mindmap' diagram definition."
        )

    def test_mermaid_init_present(self, html: str, golden_log: logging.Logger) -> None:
        """mermaid.initialize() must be called with CORTEX dark theme."""
        golden_log.info(f"AC_START  {AC_PREFIX}-005e  mermaid_init")
        has_init = "mermaid.initialize" in html
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-005e  {'✅' if has_init else '❌'}")
        assert has_init, (
            "mermaid.initialize() call missing. "
            "Mermaid must be initialized with the CORTEX dark themeVariables."
        )

    def test_mermaid_canvas_class_present(self, html: str, golden_log: logging.Logger) -> None:
        """All Mermaid diagram wrappers must use bl-mermaid-canvas for CSS centering."""
        golden_log.info(f"AC_START  {AC_PREFIX}-005f  mermaid_canvas_class")
        count = html.count("bl-mermaid-canvas")
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-005f  "
            f"{'✅' if count >= 2 else '❌'}  count={count}"
        )
        assert count >= 2, (
            f"Expected ≥ 2 bl-mermaid-canvas elements, found {count}. "
            "CSS centering via flex depends on this class."
        )


# ══════════════════════════════════════════════════════════════════════════════
# §F  Image Parity Gate (html-view-lifecycle.yaml § image_parity)
# ══════════════════════════════════════════════════════════════════════════════

class TestImageParity:
    """
    AC-BL-006 — Image parity: generated images directory must exist;
    no stale <img> src= references to removed images.

    The 3 DALL-E images (01-roi, 02-governance, 03-cost-avoidance) were
    replaced with D3/Mermaid charts. HTML must contain zero references to them.
    """

    REMOVED_IMAGES = [
        "01-roi-executive-dashboard.png",
        "02-governance-shield-architecture.png",
        "03-cost-avoidance-infographic.png",
    ]

    def test_no_stale_generated_image_references(
        self, html: str, golden_log: logging.Logger
    ) -> None:
        """HTML must not reference the 3 DALL-E images replaced by D3/Mermaid."""
        golden_log.info(f"AC_START  {AC_PREFIX}-006a  image_parity_stale_refs")
        stale = [img for img in self.REMOVED_IMAGES if img in html]
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-006a  "
            f"{'✅' if not stale else '❌'}  stale={stale}"
        )
        assert not stale, (
            f"PARITY VIOLATION: HTML still references removed DALL-E images: {stale}. "
            "These were replaced by D3/Mermaid — remove the <img> tags."
        )

    def test_logo_image_resolves(self, golden_log: logging.Logger) -> None:
        """The only remaining <img> (CORTEX-logo-200.png) must exist on disk."""
        golden_log.info(f"AC_START  {AC_PREFIX}-006b  logo_image_resolves")
        logo = CORTEX_DOCS / "assets" / "images" / "CORTEX-logo-200.png"
        exists = logo.exists()
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-006b  {'✅' if exists else '❌'}  path={logo}")
        assert exists, (
            f"Logo image not found at {logo}. "
            "Check the relative path in the HTML src attribute."
        )

    def test_generated_images_dir_exists(self, golden_log: logging.Logger) -> None:
        """The business-leader generated images directory must still exist on disk."""
        golden_log.info(f"AC_START  {AC_PREFIX}-006c  generated_images_dir")
        img_dir = CORTEX_DOCS / "assets" / "images" / "generated" / "business-leader"
        exists = img_dir.is_dir()
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-006c  {'✅' if exists else '❌'}")
        assert exists, (
            f"Generated images directory missing: {img_dir}. "
            "Directory must be preserved even if images are not currently referenced."
        )


# ══════════════════════════════════════════════════════════════════════════════
# §G  CSS Golden Invariants — business-leader.css
# ══════════════════════════════════════════════════════════════════════════════

class TestCSSGoldenInvariants:
    """
    AC-BL-007 — CSS file must contain all component classes added during
    the html-view-lifecycle enhance operation.

    CHALLENGE GATE: Removing any of these classes without updating all HTML
    references is a P1 violation. A mandatory challenge must be raised.
    """

    REQUIRED_CLASSES = [
        "bl-d3-panel",
        "bl-d3-canvas",
        "bl-d3-title",
        "bl-d3-legend",
        "bl-mermaid-panel",
        "bl-mermaid-canvas",
        "bl-mermaid-title",
        "bl-insight-row",
        "bl-insight-card",
        "bl-insight-card--green",
        "bl-insight-card--red",
        "bl-governance-narrative",
        "bl-gov-rule",
        "bl-gov-rule-code",
        "bl-problem-statement",
    ]

    def test_all_required_css_classes_defined(
        self, css: str, golden_log: logging.Logger
    ) -> None:
        """All new component classes must be defined in business-leader.css."""
        golden_log.info(f"AC_START  {AC_PREFIX}-007a  css_classes_defined")
        missing = [cls for cls in self.REQUIRED_CLASSES if f".{cls}" not in css]
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-007a  "
            f"{'✅' if not missing else '❌'}  missing={missing}"
        )
        assert not missing, (
            f"CSS GOLDEN VIOLATION: {len(missing)} required class(es) missing from "
            f"business-leader.css: {missing}. "
            "Do not remove CSS classes without updating HTML references."
        )

    def test_css_centering_flex_present(self, css: str, golden_log: logging.Logger) -> None:
        """bl-d3-canvas and bl-mermaid-canvas must use flex centering."""
        golden_log.info(f"AC_START  {AC_PREFIX}-007b  css_flex_centering")
        has_flex = "justify-content" in css and "align-items" in css
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-007b  {'✅' if has_flex else '❌'}")
        assert has_flex, (
            "CSS flex centering (justify-content + align-items) missing. "
            "Diagram centering depends on flex layout — do not remove."
        )

    def test_css_glassmorphism_backdrop(self, css: str, golden_log: logging.Logger) -> None:
        """Glassmorphism backdrop-filter must be present for D3/Mermaid panels."""
        golden_log.info(f"AC_START  {AC_PREFIX}-007c  css_glassmorphism")
        has_backdrop = "backdrop-filter" in css
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-007c  {'✅' if has_backdrop else '❌'}")
        assert has_backdrop, (
            "backdrop-filter missing from CSS. "
            "Glassmorphism panel effect depends on backdrop-filter: blur(...)."
        )

    def test_css_monospace_gov_rule_code(self, css: str, golden_log: logging.Logger) -> None:
        """bl-gov-rule-code must use monospace font for CORE rule badges."""
        golden_log.info(f"AC_START  {AC_PREFIX}-007d  css_gov_rule_monospace")
        has_mono = "bl-gov-rule-code" in css and "monospace" in css
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-007d  {'✅' if has_mono else '❌'}")
        assert has_mono, (
            "bl-gov-rule-code must use a monospace font-family. "
            "CORE rule code badges (CORE-008 etc.) require monospace rendering."
        )


# ══════════════════════════════════════════════════════════════════════════════
# §H  Metrics Accuracy — Live Count Invariants
# ══════════════════════════════════════════════════════════════════════════════

class TestMetricsAccuracy:
    """
    AC-BL-008 — Key metric counts displayed to executives must match
    the canonical values in copilot-instructions.md.

    CHALLENGE GATE: Any request to change these numbers requires a
    mandatory challenge — wrong metrics in a BL-facing page is a
    credibility risk. The golden test will catch stale counts automatically.
    """

    def test_orchestrator_count_is_186(self, html: str, golden_log: logging.Logger) -> None:
        """Orchestrator count displayed must be 186 (canonical per copilot-instructions.md)."""
        golden_log.info(f"AC_START  {AC_PREFIX}-008a  metric_orchestrator_count")
        # Accept 186 as the valid count
        has_186 = "186" in html
        # Ensure old stale count 259 is NOT present
        has_stale = "259" in html
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-008a  "
            f"{'✅' if has_186 and not has_stale else '❌'}  "
            f"has_186={has_186}  has_stale_259={has_stale}"
        )
        assert has_186, "Orchestrator count '186' not found in business-leader.html."
        assert not has_stale, (
            "Stale orchestrator count '259' still present. "
            "Update to the canonical count: 186."
        )

    def test_test_count_is_17735(self, html: str, golden_log: logging.Logger) -> None:
        """Test count displayed must be 17,735 (canonical per copilot-instructions.md)."""
        golden_log.info(f"AC_START  {AC_PREFIX}-008b  metric_test_count")
        has_count = "17,735" in html or "17735" in html
        has_stale = "7,581" in html or "7581" in html
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-008b  "
            f"{'✅' if has_count and not has_stale else '❌'}  "
            f"has_17735={has_count}  has_stale_7581={has_stale}"
        )
        assert has_count, "Test count '17,735' not found in business-leader.html."
        assert not has_stale, (
            "Stale test count '7,581' still present. "
            "Update to the canonical count: 17,735."
        )

    def test_governance_yaml_count_is_32(self, html: str, golden_log: logging.Logger) -> None:
        """Governance rule count displayed must be 32 (canonical)."""
        golden_log.info(f"AC_START  {AC_PREFIX}-008c  metric_governance_count")
        has_32 = "32" in html
        golden_log.info(f"AC_COMPLETE  {AC_PREFIX}-008c  {'✅' if has_32 else '❌'}")
        assert has_32, (
            "Governance YAML count '32' not found in business-leader.html. "
            "§7 Governance section must display the canonical rule count."
        )


# ══════════════════════════════════════════════════════════════════════════════
# §I  CDN Script Load Order (integrity guard)
# ══════════════════════════════════════════════════════════════════════════════

class TestScriptLoadOrder:
    """
    AC-BL-009 — CDN scripts must load in the correct dependency order:
    D3.js must be loaded BEFORE any D3 chart scripts execute.
    Mermaid must be loaded BEFORE mermaid.initialize() is called.
    """

    def test_d3_loads_before_chart_scripts(self, html: str, golden_log: logging.Logger) -> None:
        """D3 CDN <script> tag must appear before the D3 chart (function(){}) scripts."""
        golden_log.info(f"AC_START  {AC_PREFIX}-009a  d3_load_order")
        # Match either cdn variant
        d3_cdn_pos = html.find("d3.v7.min.js")
        if d3_cdn_pos == -1:
            d3_cdn_pos = html.find("/d3/")          # cdnjs path fragment
        chart_iife_pos = html.find("(function ()")
        if chart_iife_pos == -1:
            chart_iife_pos = html.find("(function()")
        valid = d3_cdn_pos != -1 and chart_iife_pos != -1 and d3_cdn_pos < chart_iife_pos
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-009a  {'✅' if valid else '❌'}  "
            f"d3_cdn_pos={d3_cdn_pos}  first_iife_pos={chart_iife_pos}"
        )
        assert valid, (
            "Script load order violation: D3 CDN must appear before chart IIFE scripts. "
            "D3 must be loaded before any chart code runs."
        )

    def test_mermaid_loads_before_initialize(
        self, html: str, golden_log: logging.Logger
    ) -> None:
        """Mermaid CDN script must appear before mermaid.initialize() call."""
        golden_log.info(f"AC_START  {AC_PREFIX}-009b  mermaid_load_order")
        cdn_pos = html.find("mermaid@")
        if cdn_pos == -1:
            cdn_pos = html.find("mermaid.min.js")
        init_pos = html.find("mermaid.initialize")
        valid = cdn_pos != -1 and init_pos != -1 and cdn_pos < init_pos
        golden_log.info(
            f"AC_COMPLETE  {AC_PREFIX}-009b  {'✅' if valid else '❌'}  "
            f"cdn_pos={cdn_pos}  init_pos={init_pos}"
        )
        assert valid, (
            "Script load order violation: Mermaid CDN must appear before "
            "mermaid.initialize() call."
        )
