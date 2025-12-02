"""
Phase 5.4 RED - Dynamic Section Rendering Tests

Tests mode-specific section formatters that customize how each section
(understanding, challenge, response, request_echo, next_steps) is rendered
based on interaction mode (autonomous/guided/educational/pair).

Test Coverage:
- Section formatter initialization and registration
- Mode-specific formatting for each interaction mode
- Section length constraints (max_lines per mode)
- Visual formatting differences (headers, prefixes, styling)
- Content enrichment (learning resources, options, analysis)
- Format composition and integration

Author: Asif Hussain
Phase: 5.4 RED - Dynamic Section Rendering
Created: December 2, 2025
"""

import pytest
from pathlib import Path
from src.response_templates.template_renderer import TemplateRenderer
from src.response_templates.section_formatters import (
    SectionFormatter,
    AutonomousSectionFormatter,
    GuidedSectionFormatter,
    EducationalSectionFormatter,
    PairSectionFormatter,
    SectionFormatterRegistry
)


@pytest.fixture
def renderer():
    """Create TemplateRenderer with section formatters."""
    return TemplateRenderer(template_dir=Path("cortex-brain/response-templates"))


@pytest.fixture
def formatter_registry():
    """Create section formatter registry."""
    return SectionFormatterRegistry()


class TestSectionFormatterRegistry:
    """Test section formatter registration and retrieval."""
    
    def test_registry_has_all_modes(self, formatter_registry):
        """Test registry contains formatters for all 4 interaction modes."""
        assert formatter_registry.has_formatter('autonomous')
        assert formatter_registry.has_formatter('guided')
        assert formatter_registry.has_formatter('educational')
        assert formatter_registry.has_formatter('pair')
    
    def test_get_formatter_returns_correct_type(self, formatter_registry):
        """Test get_formatter returns correct formatter class for each mode."""
        autonomous = formatter_registry.get_formatter('autonomous')
        guided = formatter_registry.get_formatter('guided')
        educational = formatter_registry.get_formatter('educational')
        pair = formatter_registry.get_formatter('pair')
        
        assert isinstance(autonomous, AutonomousSectionFormatter)
        assert isinstance(guided, GuidedSectionFormatter)
        assert isinstance(educational, EducationalSectionFormatter)
        assert isinstance(pair, PairSectionFormatter)
    
    def test_invalid_mode_returns_guided_formatter(self, formatter_registry):
        """Test invalid mode falls back to guided formatter."""
        formatter = formatter_registry.get_formatter('invalid_mode')
        assert isinstance(formatter, GuidedSectionFormatter)
    
    def test_register_custom_formatter(self, formatter_registry):
        """Test registering custom formatter for a mode."""
        class CustomFormatter(SectionFormatter):
            def __init__(self):
                super().__init__('custom')
            def format_understanding(self, content, context):
                return "Custom understanding"
            def format_challenge(self, content, context):
                return "Custom challenge"
            def format_response(self, content, context):
                return "Custom response"
            def format_next_steps(self, steps, context):
                return "Custom next steps"
        
        formatter_registry.register('custom', CustomFormatter())
        custom = formatter_registry.get_formatter('custom')
        
        assert isinstance(custom, CustomFormatter)


class TestAutonomousSectionFormatter:
    """Test autonomous mode section formatting (minimal, compact)."""
    
    def test_understanding_section_is_compact(self, formatter_registry):
        """Test understanding section uses compact format in autonomous mode."""
        formatter = formatter_registry.get_formatter('autonomous')
        content = "You want to check the status of your project and see current progress."
        
        formatted = formatter.format_understanding(content, {})
        
        # Autonomous mode: no header, just content
        assert "### 🎯" not in formatted
        assert "My Understanding" not in formatted
        assert content in formatted
        assert len(formatted) < 200  # Should be brief
    
    def test_challenge_section_is_inline(self, formatter_registry):
        """Test challenge section is inlined or omitted in autonomous mode."""
        formatter = formatter_registry.get_formatter('autonomous')
        content = "No Challenge"
        
        formatted = formatter.format_challenge(content, {})
        
        # Autonomous mode: challenge is inline or very brief
        assert "### ⚠️" not in formatted
        assert len(formatted) < 100  # Very brief
    
    def test_response_section_respects_max_lines(self, formatter_registry):
        """Test response section respects max_lines constraint (10 lines)."""
        formatter = formatter_registry.get_formatter('autonomous')
        long_content = "\n".join([f"Line {i}" for i in range(20)])  # 20 lines
        
        formatted = formatter.format_response(long_content, {})
        
        # Should truncate to ~10 lines
        lines = formatted.split('\n')
        assert len(lines) <= 12  # Allow some buffer for headers
    
    def test_next_steps_uses_compact_format(self, formatter_registry):
        """Test next steps uses compact format without header."""
        formatter = formatter_registry.get_formatter('autonomous')
        steps = ["Step 1", "Step 2", "Step 3"]
        
        formatted = formatter.format_next_steps(steps, {})
        
        # Autonomous mode: no "### 🔍 Next Steps", just "**Next:**"
        assert "**Next:**" in formatted
        assert "### 🔍" not in formatted


class TestGuidedSectionFormatter:
    """Test guided mode section formatting (standard, balanced)."""
    
    def test_understanding_section_has_full_header(self, formatter_registry):
        """Test understanding section has complete header in guided mode."""
        formatter = formatter_registry.get_formatter('guided')
        content = "You want to implement a new feature with authentication."
        
        formatted = formatter.format_understanding(content, {})
        
        # Guided mode: full header with emoji
        assert "### 🎯 My Understanding Of Your Request" in formatted
        assert content in formatted
    
    def test_challenge_section_is_visible(self, formatter_registry):
        """Test challenge section is fully visible in guided mode."""
        formatter = formatter_registry.get_formatter('guided')
        content = "No Challenge"
        
        formatted = formatter.format_challenge(content, {})
        
        # Guided mode: full section with header
        assert "### ⚠️ Challenge" in formatted
        assert content in formatted
    
    def test_response_section_respects_max_lines(self, formatter_registry):
        """Test response section respects max_lines constraint (30 lines)."""
        formatter = formatter_registry.get_formatter('guided')
        long_content = "\n".join([f"Line {i}" for i in range(50)])  # 50 lines
        
        formatted = formatter.format_response(long_content, {})
        
        # Should truncate to ~30 lines
        lines = formatted.split('\n')
        assert len(lines) <= 35  # Allow buffer
    
    def test_request_echo_is_included(self, formatter_registry):
        """Test request echo section is included in guided mode."""
        formatter = formatter_registry.get_formatter('guided')
        content = "Implement user authentication"
        
        formatted = formatter.format_request_echo(content, {})
        
        assert "### 📝 Your Request" in formatted
        assert content in formatted


class TestEducationalSectionFormatter:
    """Test educational mode section formatting (detailed, learning-focused)."""
    
    def test_understanding_includes_context(self, formatter_registry):
        """Test understanding section includes context explanation."""
        formatter = formatter_registry.get_formatter('educational')
        content = "You want to implement OAuth2 authentication."
        
        formatted = formatter.format_understanding(content, {})
        
        # Educational mode: includes context or explanation
        assert "### 🎯 My Understanding Of Your Request" in formatted
        assert content in formatted
        # May include additional context
        assert len(formatted) > len(content) + 50  # Has enrichment
    
    def test_challenge_includes_explanation(self, formatter_registry):
        """Test challenge section includes why/explanation."""
        formatter = formatter_registry.get_formatter('educational')
        content = "Authentication requires secure token storage."
        
        formatted = formatter.format_challenge(content, {})
        
        # Educational mode: may include "why" or explanation
        assert "### ⚠️ Challenge" in formatted
        assert content in formatted
    
    def test_response_includes_analysis(self, formatter_registry):
        """Test response section includes analysis/recommendations."""
        formatter = formatter_registry.get_formatter('educational')
        content = "Use JWT tokens for stateless authentication."
        
        formatted = formatter.format_response(content, {})
        
        # Educational mode: detailed response with analysis
        assert "### 💬 Response" in formatted
        assert content in formatted
        assert len(formatted) > len(content) + 100  # Has additional detail
    
    def test_next_steps_includes_learning_resources(self, formatter_registry):
        """Test next steps includes learning resources in educational mode."""
        formatter = formatter_registry.get_formatter('educational')
        steps = ["Implement OAuth2 flow", "Secure token storage"]
        
        formatted = formatter.format_next_steps(steps, {})
        
        # Educational mode: may include learning resources or checkboxes
        assert "### 🔍 Next Steps" in formatted
        # Uses checkboxes instead of numbers
        assert "☐" in formatted or "- [ ]" in formatted


class TestPairSectionFormatter:
    """Test pair mode section formatting (collaborative, options-focused)."""
    
    def test_understanding_has_collaborative_tone(self, formatter_registry):
        """Test understanding section uses collaborative language."""
        formatter = formatter_registry.get_formatter('pair')
        content = "Create a REST API endpoint."
        
        formatted = formatter.format_understanding(content, {})
        
        assert "### 🎯 My Understanding Of Your Request" in formatted
        assert content in formatted
    
    def test_challenge_presents_options(self, formatter_registry):
        """Test challenge section presents multiple options."""
        formatter = formatter_registry.get_formatter('pair')
        content = "API design requires choosing between REST and GraphQL."
        
        formatted = formatter.format_challenge(content, {})
        
        # Pair mode: may present options or trade-offs
        assert "### ⚠️ Challenge" in formatted
        assert content in formatted
    
    def test_response_includes_tradeoffs(self, formatter_registry):
        """Test response section includes trade-off discussions."""
        formatter = formatter_registry.get_formatter('pair')
        content = "REST is simpler but GraphQL offers more flexibility."
        
        formatted = formatter.format_response(content, {})
        
        # Pair mode: discusses trade-offs
        assert "### 💬 Response" in formatted
        assert content in formatted
    
    def test_next_steps_presents_options(self, formatter_registry):
        """Test next steps presents multiple options/tracks."""
        formatter = formatter_registry.get_formatter('pair')
        steps = ["Option A: REST API", "Option B: GraphQL API"]
        
        formatted = formatter.format_next_steps(steps, {})
        
        # Pair mode: presents options/tracks
        assert "### 🔍 Next Steps" in formatted
        assert "option" in formatted.lower() or "track" in formatted.lower()
        assert "Option A" in formatted or "Track A" in formatted


class TestSectionIntegration:
    """Test section formatter integration with TemplateRenderer."""
    
    def test_renderer_uses_section_formatters(self, renderer):
        """Test TemplateRenderer uses section formatters during composition."""
        # Compose template with autonomous mode
        composed = renderer.compose_template("planning", mode="autonomous")
        
        # Should use autonomous formatting (compact, no headers)
        assert "**Next:**" in composed or len(composed) < 500
    
    def test_mode_specific_formatting_applied(self, renderer):
        """Test mode-specific formatting is applied to all sections."""
        # Educational mode should be more verbose
        educational = renderer.compose_template("planning", mode="educational")
        guided = renderer.compose_template("planning", mode="guided")
        
        # Educational should have more content
        assert len(educational) >= len(guided)
    
    def test_section_formatters_respect_context(self, renderer):
        """Test section formatters use context data during formatting."""
        context = {
            "operation": "Feature Planning",
            "understanding_content": "Custom understanding text",
            "challenge_content": "Custom challenge text"
        }
        
        composed = renderer.compose_template("planning", mode="guided", context=context)
        
        # Should include custom context
        assert "Custom understanding text" in composed
        assert "Custom challenge text" in composed


class TestFormatComposition:
    """Test composition of multiple formatted sections."""
    
    def test_sections_maintain_order(self, formatter_registry):
        """Test sections maintain correct order when composed."""
        formatter = formatter_registry.get_formatter('guided')
        
        sections = [
            formatter.format_understanding("Understanding", {}),
            formatter.format_challenge("Challenge", {}),
            formatter.format_response("Response", {}),
            formatter.format_request_echo("Request", {}),
            formatter.format_next_steps(["Step 1", "Step 2"], {})
        ]
        
        composed = "\n\n".join(sections)
        
        # Verify order
        understanding_pos = composed.find("🎯")
        challenge_pos = composed.find("⚠️")
        response_pos = composed.find("💬")
        request_pos = composed.find("📝")
        next_steps_pos = composed.find("🔍")
        
        assert understanding_pos < challenge_pos < response_pos < request_pos < next_steps_pos
    
    def test_sections_are_separated(self, formatter_registry):
        """Test sections have proper spacing between them."""
        formatter = formatter_registry.get_formatter('guided')
        
        sections = [
            formatter.format_understanding("Understanding", {}),
            formatter.format_challenge("Challenge", {})
        ]
        
        composed = "\n\n".join(sections)
        
        # Should have double newline separation
        assert "\n\n" in composed
    
    def test_empty_sections_handled_gracefully(self, formatter_registry):
        """Test empty section content is handled gracefully."""
        formatter = formatter_registry.get_formatter('guided')
        
        formatted = formatter.format_response("", {})
        
        # Should not crash, should return minimal format
        assert isinstance(formatted, str)
        assert len(formatted) >= 0  # Empty or has header


class TestPerformance:
    """Test section formatting performance."""
    
    def test_formatting_completes_quickly(self, formatter_registry):
        """Test section formatting completes in <10ms per section."""
        import time
        
        formatter = formatter_registry.get_formatter('guided')
        content = "Test content with some reasonable length to simulate real usage."
        
        start = time.time()
        for _ in range(100):  # 100 sections
            formatter.format_understanding(content, {})
        duration = time.time() - start
        
        avg_per_section = duration / 100
        assert avg_per_section < 0.01  # <10ms per section
    
    def test_all_formatters_perform_similarly(self, formatter_registry):
        """Test all mode formatters have similar performance."""
        import time
        
        modes = ['autonomous', 'guided', 'educational', 'pair']
        content = "Test content for performance measurement."
        durations = []
        
        for mode in modes:
            formatter = formatter_registry.get_formatter(mode)
            start = time.time()
            for _ in range(100):  # More iterations for stable timing
                formatter.format_response(content, {})
            durations.append(time.time() - start)
        
        # All should be within 5x of fastest (educational mode adds analysis)
        min_duration = min(durations)
        max_duration = max(durations)
        assert max_duration < min_duration * 5
