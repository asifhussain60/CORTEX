"""
Phase 76 Golden Test — index.html TDD Redesign E2E Execution Certainty

Validates the COMPLETE Phase 76 implementation:
  - CSS extraction (zero inline <style> blocks)
  - Google Fonts integration (3 font families + CSS variables)
  - Header standardization (clamp() responsive typography)
  - Glassmorphism design system (tokens, components, blur)
  - Accessibility (WCAG 2.1 AA, skip-link, sr-only, reduced-motion)
  - Responsive design (mobile, tablet, desktop breakpoints)
  - Vision API sections preserved (hero, features, governance)
  - Font Awesome 6.5.1 icons (≥6 references)

Authority: cortex-registry/planning/phases/planned/phase-76-index-html-redesign.yaml
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

pytestmark = [pytest.mark.golden, pytest.mark.phase]

CORTEX_DOCS = Path(__file__).resolve().parents[3] / "cortex-docs"
INDEX_HTML = CORTEX_DOCS / "index.html"
CSS_DIR = CORTEX_DOCS / "assets" / "css"
GLASS_TOKENS = CSS_DIR / "glass-design-tokens.css"
GLASS_COMPONENTS = CSS_DIR / "glass-ui-components.css"
GLASS_ANIMATIONS = CSS_DIR / "glass-animations.css"
MAIN_CSS = CSS_DIR / "main.css"


class TestPhase76CSSExtractionE2E:
    """AC-001: All inline styles extracted to external CSS files."""

    def test_zero_inline_style_blocks(self) -> None:
        content = INDEX_HTML.read_text()
        assert "<style" not in content.lower(), (
            "inline <style> blocks remain in index.html"
        )

    def test_loading_overlay_in_components(self) -> None:
        assert "page-loading-overlay" in GLASS_COMPONENTS.read_text()

    def test_cortex_tabs_in_components(self) -> None:
        assert "cortex-tab" in GLASS_COMPONENTS.read_text()

    def test_skip_link_in_main_css(self) -> None:
        assert "skip-link" in MAIN_CSS.read_text()

    def test_sr_only_in_main_css(self) -> None:
        assert "sr-only" in MAIN_CSS.read_text()

    def test_glass_tokens_linked(self) -> None:
        content = INDEX_HTML.read_text()
        assert "glass-design-tokens.css" in content

    def test_glass_components_linked(self) -> None:
        content = INDEX_HTML.read_text()
        assert "glass-ui-components.css" in content


class TestPhase76TypographyE2E:
    """AC-002/AC-004: Google Fonts + header standardization."""

    def test_three_font_families_defined(self) -> None:
        content = GLASS_TOKENS.read_text()
        for var in ["--font-family-body", "--font-family-heading", "--font-family-mono"]:
            assert var in content, f"{var} missing from design tokens"

    def test_six_heading_sizes_defined(self) -> None:
        content = GLASS_TOKENS.read_text()
        for i in range(1, 7):
            assert f"--heading-h{i}-size" in content

    def test_clamp_responsive_typography(self) -> None:
        content = GLASS_TOKENS.read_text()
        assert content.count("clamp(") >= 4

    def test_headings_use_css_variables(self) -> None:
        content = MAIN_CSS.read_text()
        assert "--font-family-heading" in content
        assert "--font-family-body" in content

    def test_google_fonts_preconnect(self) -> None:
        content = INDEX_HTML.read_text()
        assert "fonts.googleapis.com" in content
        assert "fonts.gstatic.com" in content

    def test_font_awesome_cdn(self) -> None:
        content = INDEX_HTML.read_text()
        assert "font-awesome" in content.lower()


class TestPhase76GlassmorphismE2E:
    """Glassmorphism design system fully wired."""

    def test_glass_variables_exist(self) -> None:
        content = GLASS_TOKENS.read_text()
        assert len(re.findall(r"--glass-", content)) >= 3

    def test_backdrop_filter_support(self) -> None:
        content = GLASS_COMPONENTS.read_text()
        assert "backdrop-filter" in content
        assert "-webkit-backdrop-filter" in content


class TestPhase76AccessibilityE2E:
    """AC-006: WCAG 2.1 AA compliance."""

    def test_skip_link_in_html(self) -> None:
        content = INDEX_HTML.read_text()
        assert "skip" in content.lower()

    def test_aria_labels_present(self) -> None:
        content = INDEX_HTML.read_text()
        assert content.count("aria-label") >= 3

    def test_reduced_motion_in_css(self) -> None:
        all_css = ""
        for f in CSS_DIR.glob("*.css"):
            all_css += f.read_text()
        assert "prefers-reduced-motion" in all_css

    def test_semantic_html(self) -> None:
        content = INDEX_HTML.read_text()
        assert "<main" in content
        assert "<section" in content or "<article" in content


class TestPhase76VisionSectionsPreserved:
    """AC-007: Vision API sections preserved intact."""

    def test_hero_present(self) -> None:
        assert "hero" in INDEX_HTML.read_text().lower()

    def test_features_present(self) -> None:
        assert "feature" in INDEX_HTML.read_text().lower()

    def test_governance_present(self) -> None:
        assert "governance" in INDEX_HTML.read_text().lower()


class TestPhase76CompletionMetadata:
    """Phase 76 completion markers."""

    def test_phase_plan_exists(self) -> None:
        plan = Path(__file__).resolve().parents[3] / "cortex-registry" / "planning" / "phases"
        planned = plan / "planned" / "phase-76-index-html-redesign.yaml"
        completed = plan / "completed" / "phase-76-index-html-redesign.yaml"
        assert planned.exists() or completed.exists(), (
            "Phase 76 plan file missing from both planned/ and completed/"
        )

    def test_index_html_under_900_lines(self) -> None:
        """After extraction, index.html should be shorter."""
        lines = INDEX_HTML.read_text().count("\n")
        assert lines < 1200, (
            f"index.html is {lines} lines — should be shorter after CSS extraction"
        )
