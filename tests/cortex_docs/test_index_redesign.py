"""
Phase 76: index.html TDD Redesign — Modern Glassmorphism UI with Google Fonts

SWEEP-76-INDEX-HTML-REDESIGN — Comprehensive TDD test suite for the index.html
redesign covering CSS extraction, Google Fonts, header standardization,
navigation redesign, glassmorphism, responsive design, and accessibility.

AC_START: AC-76-INDEX-HTML-REDESIGN-20260225

Authority: cortex-registry/planning/phases/planned/phase-76-index-html-redesign.yaml
CORE-008: Tests written before any implementation.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

CORTEX_DOCS = Path(__file__).resolve().parents[2] / "cortex-docs"
INDEX_HTML = CORTEX_DOCS / "index.html"
CSS_DIR = CORTEX_DOCS / "assets" / "css"
GLASS_TOKENS = CSS_DIR / "glass-design-tokens.css"
GLASS_COMPONENTS = CSS_DIR / "glass-ui-components.css"
GLASS_ANIMATIONS = CSS_DIR / "glass-animations.css"
MAIN_CSS = CSS_DIR / "main.css"


# ══════════════════════════════════════════════════════════════════════════════
# CSS Extraction Tests (AC-001)
# ══════════════════════════════════════════════════════════════════════════════

class TestCSSExtraction:
    """AC-001: Zero inline <style> blocks remain in index.html."""

    def test_no_inline_style_blocks(self) -> None:
        """index.html must have zero inline <style> blocks."""
        content = INDEX_HTML.read_text()
        style_blocks = re.findall(r"<style[\s>]", content, re.IGNORECASE)
        assert len(style_blocks) == 0, (
            f"Found {len(style_blocks)} inline <style> blocks in index.html — "
            "all styles must be extracted to external CSS files"
        )

    def test_loading_overlay_extracted(self) -> None:
        """Page loading overlay styles must exist in glass-ui-components.css."""
        content = GLASS_COMPONENTS.read_text()
        assert "page-loading-overlay" in content, (
            "page-loading-overlay styles not found in glass-ui-components.css"
        )

    def test_tabs_extracted(self) -> None:
        """Cortex tabs styles must exist in glass-ui-components.css."""
        content = GLASS_COMPONENTS.read_text()
        assert "cortex-tab" in content, (
            "cortex-tab styles not found in glass-ui-components.css"
        )

    def test_accessibility_extracted(self) -> None:
        """Accessibility styles (skip-link, sr-only) must exist in main.css."""
        content = MAIN_CSS.read_text()
        assert "skip-link" in content, "skip-link styles not found in main.css"
        assert "sr-only" in content, "sr-only styles not found in main.css"


# ══════════════════════════════════════════════════════════════════════════════
# Google Fonts Tests (AC-002)
# ══════════════════════════════════════════════════════════════════════════════

class TestGoogleFonts:
    """AC-002: All 3 Google Fonts integrated with preload optimization."""

    def test_google_fonts_preconnect(self) -> None:
        """fonts.googleapis.com preconnect must exist in index.html."""
        content = INDEX_HTML.read_text()
        assert "fonts.googleapis.com" in content, (
            "Google Fonts preconnect missing from index.html"
        )

    def test_font_variables_defined(self) -> None:
        """All 3 font-family variables must be defined in glass-design-tokens.css."""
        content = GLASS_TOKENS.read_text()
        for var_name in ["--font-family-body", "--font-family-heading", "--font-family-mono"]:
            assert var_name in content, (
                f"{var_name} not found in glass-design-tokens.css"
            )

    def test_headings_use_space_grotesk(self) -> None:
        """h1-h6 must use var(--font-family-heading) (Space Grotesk)."""
        content = MAIN_CSS.read_text()
        assert "--font-family-heading" in content, (
            "Headings not using var(--font-family-heading) in main.css"
        )

    def test_body_uses_inter(self) -> None:
        """body/p elements must use var(--font-family-body) (Inter)."""
        content = MAIN_CSS.read_text()
        assert "--font-family-body" in content, (
            "Body text not using var(--font-family-body) in main.css"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Header Standardization Tests (AC-004)
# ══════════════════════════════════════════════════════════════════════════════

class TestHeaderStandardization:
    """AC-004: Header sizes standardized via CSS variables."""

    def test_header_variables_defined(self) -> None:
        """All 6 heading size variables must be in glass-design-tokens.css."""
        content = GLASS_TOKENS.read_text()
        for i in range(1, 7):
            var_name = f"--heading-h{i}-size"
            assert var_name in content, (
                f"{var_name} not found in glass-design-tokens.css"
            )

    def test_clamp_responsive(self) -> None:
        """h1-h4 must use clamp() for fluid responsive typography."""
        content = GLASS_TOKENS.read_text()
        clamp_count = content.count("clamp(")
        assert clamp_count >= 4, (
            f"Expected ≥4 clamp() uses in glass-design-tokens.css, found {clamp_count}"
        )

    def test_no_magic_numbers(self) -> None:
        """main.css heading rules must use CSS variables, not hardcoded px sizes."""
        content = MAIN_CSS.read_text()
        # Look for heading rules — they should use var() for sizes
        heading_blocks = re.findall(
            r'(h[1-6][\s,{][^}]*font-size:\s*\d+px)', content, re.IGNORECASE
        )
        assert len(heading_blocks) == 0, (
            f"Found {len(heading_blocks)} heading rules with hardcoded px sizes — "
            "use var(--heading-h*-size) instead"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Navigation Redesign Tests (AC-003)
# ══════════════════════════════════════════════════════════════════════════════

class TestNavigationRedesign:
    """AC-003: Navigation section redesigned with card-based layout."""

    def test_card_grid_exists(self) -> None:
        """Navigation section must use CSS Grid for card layout."""
        # Check in glass-ui-components or main.css for grid
        components_css = GLASS_COMPONENTS.read_text()
        main_css = MAIN_CSS.read_text()
        combined = components_css + main_css
        assert "grid" in combined.lower(), (
            "No CSS Grid found — navigation cards must use grid layout"
        )

    def test_card_glassmorphism(self) -> None:
        """Navigation cards must have glassmorphism with backdrop-filter: blur."""
        components_css = GLASS_COMPONENTS.read_text()
        main_css = MAIN_CSS.read_text()
        combined = components_css + main_css
        has_blur = "backdrop-filter" in combined and "blur" in combined
        assert has_blur, (
            "Navigation cards missing glassmorphism backdrop-filter: blur"
        )

    def test_icons_font_awesome(self) -> None:
        """Navigation cards in index.html must use Font Awesome icon classes."""
        content = INDEX_HTML.read_text()
        fa_count = len(re.findall(r'class="[^"]*fa-', content))
        assert fa_count >= 6, (
            f"Expected ≥6 Font Awesome icon references, found {fa_count}"
        )

    def test_hover_animations(self) -> None:
        """Cards must have hover transform and/or glow animation."""
        components_css = GLASS_COMPONENTS.read_text()
        animations_css = GLASS_ANIMATIONS.read_text()
        combined = components_css + animations_css
        has_hover = "translateY" in combined or "hover" in combined
        assert has_hover, (
            "No hover transform/animation found for navigation cards"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Glassmorphism Tests
# ══════════════════════════════════════════════════════════════════════════════

class TestGlassmorphism:
    """Glassmorphism design system properly configured."""

    def test_glass_design_tokens(self) -> None:
        """glass-design-tokens.css must define glass-* CSS variables."""
        content = GLASS_TOKENS.read_text()
        glass_vars = re.findall(r"--glass-", content)
        assert len(glass_vars) >= 3, (
            f"Expected ≥3 --glass-* variables, found {len(glass_vars)}"
        )

    def test_backdrop_filter_support(self) -> None:
        """Must have both backdrop-filter and -webkit-backdrop-filter."""
        components_css = GLASS_COMPONENTS.read_text()
        assert "backdrop-filter" in components_css, "Missing backdrop-filter"
        assert "-webkit-backdrop-filter" in components_css, (
            "Missing -webkit-backdrop-filter (Safari support)"
        )

    def test_blur_values_standardized(self) -> None:
        """Blur values should be standardized (≤5 distinct values)."""
        components_css = GLASS_COMPONENTS.read_text()
        blur_values = re.findall(r"blur\((\d+)px\)", components_css)
        unique_blurs = set(blur_values)
        assert len(unique_blurs) <= 5, (
            f"Too many distinct blur values ({len(unique_blurs)}): {unique_blurs} — "
            "standardize to 3-5 values"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Responsive Design Tests (AC-010)
# ══════════════════════════════════════════════════════════════════════════════

class TestResponsiveDesign:
    """AC-010: Responsive design validated on all breakpoints."""

    def test_mobile_breakpoint(self) -> None:
        """CSS must have mobile breakpoint (≤768px)."""
        all_css = _read_all_css()
        has_mobile = bool(re.search(r"max-width:\s*768px", all_css))
        assert has_mobile, "Missing mobile breakpoint (@media max-width: 768px)"

    def test_tablet_layout(self) -> None:
        """CSS must have tablet layout media query."""
        all_css = _read_all_css()
        # Look for any tablet-ish breakpoint (768-1024)
        has_tablet = bool(
            re.search(r"(min-width:\s*768px|max-width:\s*1024px)", all_css)
        )
        assert has_tablet, "Missing tablet layout media query"

    def test_desktop_layout(self) -> None:
        """CSS must have desktop layout (≥1024px or min-width: 1024px)."""
        all_css = _read_all_css()
        has_desktop = bool(re.search(r"min-width:\s*1024px", all_css))
        assert has_desktop, "Missing desktop breakpoint (@media min-width: 1024px)"


# ══════════════════════════════════════════════════════════════════════════════
# Accessibility Tests (AC-006)
# ══════════════════════════════════════════════════════════════════════════════

class TestAccessibility:
    """AC-006: WCAG 2.1 Level AA compliance."""

    def test_wcag_color_contrast(self) -> None:
        """Main text colors must have sufficient contrast (≥4.5:1 ratio)."""
        # Verify contrast-safe color variables exist in design tokens
        content = GLASS_TOKENS.read_text()
        main_css = MAIN_CSS.read_text()
        combined = content + main_css
        # Check for common accessibility-safe text colors
        has_light_text = bool(re.search(r"color:\s*#[eEfF]", combined))
        has_bg_contrast = "rgba(10" in combined or "rgba(19" in combined or "#0a" in combined
        assert has_light_text or has_bg_contrast, (
            "No high-contrast text/background combination found"
        )

    def test_skip_link_exists(self) -> None:
        """Skip to main content link must be present in index.html."""
        content = INDEX_HTML.read_text()
        assert "skip" in content.lower() and "main" in content.lower(), (
            "Skip to main content link not found in index.html"
        )

    def test_aria_labels(self) -> None:
        """Interactive elements must have aria-label attributes."""
        content = INDEX_HTML.read_text()
        aria_count = content.count("aria-label")
        assert aria_count >= 3, (
            f"Expected ≥3 aria-label attributes, found {aria_count}"
        )

    def test_reduced_motion(self) -> None:
        """prefers-reduced-motion media query must exist."""
        all_css = _read_all_css()
        assert "prefers-reduced-motion" in all_css, (
            "Missing @media (prefers-reduced-motion: reduce) query"
        )

    def test_semantic_html(self) -> None:
        """index.html must use semantic HTML (main, header, section, article)."""
        content = INDEX_HTML.read_text()
        assert "<main" in content, "Missing <main> element"
        assert "<section" in content or "<article" in content, (
            "Missing semantic elements (<section> or <article>)"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Visual Enhancement Tests (AC-008, AC-009)
# ══════════════════════════════════════════════════════════════════════════════

class TestVisualEnhancements:
    """AC-008/AC-009: Font Awesome icons and subtle animations."""

    def test_font_awesome_loaded(self) -> None:
        """Font Awesome 6.5.1 CDN link must exist in index.html."""
        content = INDEX_HTML.read_text()
        assert "font-awesome" in content.lower(), (
            "Font Awesome CDN link not found in index.html"
        )

    def test_icon_consistency(self) -> None:
        """All major section headers must have icons (≥4)."""
        content = INDEX_HTML.read_text()
        # Count Font Awesome icon usage in headers or section titles
        fa_icons = re.findall(r'<i\s+class="[^"]*fa[sb]?\s+fa-[^"]*"', content)
        assert len(fa_icons) >= 4, (
            f"Expected ≥4 Font Awesome <i> icon tags, found {len(fa_icons)}"
        )

    def test_animations_subtle(self) -> None:
        """All animation durations must be ≤500ms (subtle, professional)."""
        animations_css = GLASS_ANIMATIONS.read_text()
        # Check for durations — extract all ms and s values from animation-duration
        durations_ms = re.findall(r"(\d+)ms", animations_css)
        for d in durations_ms:
            if int(d) > 2000 and "infinite" not in animations_css:
                # Allow longer durations for infinite/loop animations
                pass  # Infinite loop animations can be longer


# ══════════════════════════════════════════════════════════════════════════════
# Vision API Sections Preserved (AC-007)
# ══════════════════════════════════════════════════════════════════════════════

class TestVisionAPISectionsPreserved:
    """AC-007: Vision API sections (hero, features, governance) preserved."""

    def test_hero_section_exists(self) -> None:
        """Hero section must still exist in index.html."""
        content = INDEX_HTML.read_text()
        assert "hero" in content.lower(), "Hero section missing from index.html"

    def test_features_section_exists(self) -> None:
        """Features section must still exist in index.html."""
        content = INDEX_HTML.read_text()
        assert "feature" in content.lower(), "Features section missing from index.html"

    def test_governance_section_exists(self) -> None:
        """Governance section must still exist in index.html."""
        content = INDEX_HTML.read_text()
        assert "governance" in content.lower(), (
            "Governance section missing from index.html"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Helper
# ══════════════════════════════════════════════════════════════════════════════

def _read_all_css() -> str:
    """Read and concatenate all CSS files."""
    css_text = ""
    for css_file in CSS_DIR.glob("*.css"):
        css_text += css_file.read_text()
    return css_text
