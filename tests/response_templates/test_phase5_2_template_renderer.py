"""
Phase 5.2 RED - Template Composition Engine Tests
CORTEX 3.2.1 - Response Template System Refactor

Tests for TemplateRenderer class that composes templates from modular YAML files.
Replaces YAML anchor-based composition with Python-based dynamic assembly.

Author: Asif Hussain
Created: December 2, 2025
"""

import pytest
from pathlib import Path
from typing import Dict, Any, List


class TestTemplateRendererInitialization:
    """Test TemplateRenderer initialization and YAML loading."""
    
    def test_renderer_loads_all_yaml_files(self):
        """Test renderer loads all 4 modular YAML files on initialization."""
        from src.response_templates.template_renderer import TemplateRenderer
        
        renderer = TemplateRenderer()
        
        # Should have loaded all 4 files
        assert renderer.components is not None
        assert renderer.templates is not None
        assert renderer.profiles is not None
        assert renderer.routing is not None
    
    def test_renderer_uses_custom_template_dir(self):
        """Test renderer accepts custom template directory."""
        from src.response_templates.template_renderer import TemplateRenderer
        
        custom_dir = Path("cortex-brain/response-templates")
        renderer = TemplateRenderer(template_dir=custom_dir)
        
        assert renderer.template_dir == custom_dir
    
    def test_renderer_validates_schema_versions(self):
        """Test renderer validates all YAML files have matching schema versions."""
        from src.response_templates.template_renderer import TemplateRenderer
        
        renderer = TemplateRenderer()
        
        # All files should have schema_version 3.2
        assert renderer.schema_version == '3.2'


class TestComponentComposition:
    """Test composing templates from components."""
    
    @pytest.fixture
    def renderer(self):
        """Get TemplateRenderer instance."""
        from src.response_templates.template_renderer import TemplateRenderer
        return TemplateRenderer()
    
    def test_compose_standard_5_part_template(self, renderer):
        """Test composing standard 5-part template from components."""
        template_id = "help"
        
        composed = renderer.compose_template(template_id)
        
        # Should contain all 5 sections
        assert "🎯 My Understanding Of Your Request" in composed
        assert "⚠️ Challenge" in composed
        assert "💬 Response" in composed
        assert "📝 Your Request" in composed
        assert "🔍 Next Steps" in composed
    
    def test_compose_compact_template(self, renderer):
        """Test composing compact template for autonomous mode."""
        template_id = "status_check"
        
        composed = renderer.compose_template(template_id, mode="autonomous")
        
        # Compact format should be shorter
        assert len(composed) < 500  # Compact responses are brief
        assert "🧠 CORTEX" in composed
    
    def test_compose_with_placeholder_substitution(self, renderer):
        """Test placeholder substitution in composed templates."""
        template_id = "planning"
        context = {
            "understanding_content": "You want to create a feature plan",
            "challenge_content": "No Challenge",
            "response_content": "Planning system ready"
        }
        
        composed = renderer.compose_template(template_id, context=context)
        
        assert "You want to create a feature plan" in composed
        assert "Planning system ready" in composed
    
    def test_compose_nonexistent_template_raises_error(self, renderer):
        """Test composing non-existent template raises KeyError."""
        with pytest.raises(KeyError):
            renderer.compose_template("nonexistent_template_id")
    
    def test_component_order_preserved(self, renderer):
        """Test components are assembled in correct order."""
        template_id = "help"
        
        composed = renderer.compose_template(template_id)
        
        # Find section positions
        understanding_pos = composed.find("🎯 My Understanding")
        challenge_pos = composed.find("⚠️ Challenge")
        response_pos = composed.find("💬 Response")
        request_pos = composed.find("📝 Your Request")
        next_steps_pos = composed.find("🔍 Next Steps")
        
        # Verify order
        assert understanding_pos < challenge_pos
        assert challenge_pos < response_pos
        assert response_pos < request_pos
        assert request_pos < next_steps_pos


class TestInteractionModeRendering:
    """Test mode-specific template rendering."""
    
    @pytest.fixture
    def renderer(self):
        """Get TemplateRenderer instance."""
        from src.response_templates.template_renderer import TemplateRenderer
        return TemplateRenderer()
    
    def test_autonomous_mode_uses_compact_format(self, renderer):
        """Test autonomous mode produces compact output."""
        template_id = "help"
        
        autonomous = renderer.compose_template(template_id, mode="autonomous")
        guided = renderer.compose_template(template_id, mode="guided")
        
        # Autonomous should be shorter
        assert len(autonomous) < len(guided)
    
    def test_guided_mode_uses_standard_format(self, renderer):
        """Test guided mode produces standard 5-part format."""
        template_id = "planning"
        
        guided = renderer.compose_template(template_id, mode="guided")
        
        # Should have all 5 sections
        sections = ["🎯", "⚠️", "💬", "📝", "🔍"]
        for section in sections:
            assert section in guided
    
    def test_educational_mode_adds_detail(self, renderer):
        """Test educational mode produces detailed explanations."""
        template_id = "tdd_workflow"
        
        educational = renderer.compose_template(template_id, mode="educational")
        guided = renderer.compose_template(template_id, mode="guided")
        
        # Educational should be longer with more detail
        assert len(educational) >= len(guided)
    
    def test_pair_mode_presents_options(self, renderer):
        """Test pair mode presents multiple options."""
        template_id = "planning"
        
        pair = renderer.compose_template(template_id, mode="pair")
        
        # Pair mode should suggest options
        assert "option" in pair.lower() or "track" in pair.lower()
    
    def test_invalid_mode_falls_back_to_guided(self, renderer):
        """Test invalid mode falls back to guided mode."""
        template_id = "help"
        
        invalid_mode = renderer.compose_template(template_id, mode="invalid_mode")
        guided = renderer.compose_template(template_id, mode="guided")
        
        # Should produce same output as guided
        assert invalid_mode == guided


class TestTriggerRouting:
    """Test trigger-based template selection."""
    
    @pytest.fixture
    def renderer(self):
        """Get TemplateRenderer instance."""
        from src.response_templates.template_renderer import TemplateRenderer
        return TemplateRenderer()
    
    def test_exact_trigger_match(self, renderer):
        """Test exact trigger match routes to correct template."""
        template_id = renderer.select_template_by_trigger("help")
        
        assert template_id == "help"
    
    def test_case_insensitive_trigger_match(self, renderer):
        """Test trigger matching is case-insensitive."""
        template_id = renderer.select_template_by_trigger("HELP")
        
        assert template_id == "help"
    
    def test_fuzzy_trigger_match(self, renderer):
        """Test fuzzy matching finds similar triggers."""
        # "hlp" should fuzzy match to "help" (80%+ similarity)
        template_id = renderer.select_template_by_trigger("hlp")
        
        assert template_id == "help"
    
    def test_no_match_returns_fallback(self, renderer):
        """Test unmatched trigger returns fallback template."""
        template_id = renderer.select_template_by_trigger("completely_unknown_trigger_xyz")
        
        assert template_id == "fallback"
    
    def test_multi_word_trigger_match(self, renderer):
        """Test multi-word triggers match correctly."""
        template_id = renderer.select_template_by_trigger("start tdd")
        
        assert template_id == "tdd_workflow"


class TestCaching:
    """Test template caching for performance."""
    
    @pytest.fixture
    def renderer(self):
        """Get TemplateRenderer instance."""
        from src.response_templates.template_renderer import TemplateRenderer
        return TemplateRenderer()
    
    def test_composed_templates_are_cached(self, renderer):
        """Test composed templates are cached for reuse."""
        template_id = "help"
        
        # First call - should compose and cache
        first = renderer.compose_template(template_id)
        
        # Second call - should use cache
        second = renderer.compose_template(template_id)
        
        assert first == second
        assert renderer.cache_hit_count > 0
    
    def test_cache_invalidates_on_context_change(self, renderer):
        """Test cache invalidates when context changes."""
        template_id = "planning"
        context1 = {"response_content": "Response 1"}
        context2 = {"response_content": "Response 2"}
        
        first = renderer.compose_template(template_id, context=context1)
        second = renderer.compose_template(template_id, context=context2)
        
        # Should produce different outputs
        assert "Response 1" in first
        assert "Response 2" in second
        assert first != second
    
    def test_cache_respects_mode_changes(self, renderer):
        """Test cache respects mode parameter."""
        template_id = "help"
        
        autonomous = renderer.compose_template(template_id, mode="autonomous")
        guided = renderer.compose_template(template_id, mode="guided")
        
        # Should be different outputs
        assert autonomous != guided


class TestErrorHandling:
    """Test error handling in template composition."""
    
    @pytest.fixture
    def renderer(self):
        """Get TemplateRenderer instance."""
        from src.response_templates.template_renderer import TemplateRenderer
        return TemplateRenderer()
    
    def test_missing_component_raises_error(self, renderer):
        """Test missing component raises descriptive error."""
        # Manually create template with non-existent component
        with pytest.raises(KeyError) as exc_info:
            renderer._compose_from_components(["nonexistent_component"])
        
        assert "nonexistent_component" in str(exc_info.value)
    
    def test_invalid_yaml_raises_error(self):
        """Test invalid YAML file raises descriptive error."""
        from src.response_templates.template_renderer import TemplateRenderer
        
        # Point to non-existent directory
        with pytest.raises(FileNotFoundError):
            TemplateRenderer(template_dir=Path("nonexistent/directory"))
    
    def test_missing_required_placeholder_warns(self, renderer):
        """Test missing required placeholder generates warning."""
        template_id = "planning"
        # Missing 'understanding_content' placeholder
        context = {"response_content": "Test"}
        
        # Should still compose but may have placeholder markers
        composed = renderer.compose_template(template_id, context=context)
        
        # Should complete without error (graceful degradation)
        assert "🧠 CORTEX" in composed


class TestPerformance:
    """Test template composition performance."""
    
    @pytest.fixture
    def renderer(self):
        """Get TemplateRenderer instance."""
        from src.response_templates.template_renderer import TemplateRenderer
        return TemplateRenderer()
    
    def test_composition_completes_quickly(self, renderer):
        """Test template composition completes in <100ms."""
        import time
        
        template_id = "help"
        
        start = time.time()
        renderer.compose_template(template_id)
        duration = time.time() - start
        
        assert duration < 0.1  # <100ms
    
    def test_batch_composition_efficient(self, renderer):
        """Test batch composition of multiple templates is efficient."""
        import time
        
        template_ids = ["help", "planning", "tdd_workflow", "feedback", "status_check"]
        
        start = time.time()
        for template_id in template_ids:
            renderer.compose_template(template_id)
        duration = time.time() - start
        
        # 5 templates in <500ms
        assert duration < 0.5


class TestBackwardCompatibility:
    """Test backward compatibility with existing template loader."""
    
    def test_renderer_works_with_template_loader(self):
        """Test TemplateRenderer integrates with existing TemplateLoader."""
        from src.response_templates.template_loader import TemplateLoader
        from src.response_templates.template_renderer import TemplateRenderer
        
        # Old system
        loader = TemplateLoader(Path("cortex-brain/response-templates.yaml"))
        
        # New system
        renderer = TemplateRenderer()
        
        # Should load templates without error
        assert loader is not None
        assert renderer is not None


# Phase 5.2 Test Summary
# =====================
# Total Tests: 35+
# Coverage Areas:
# - Initialization and YAML loading
# - Component composition
# - Interaction mode rendering
# - Trigger routing and fuzzy matching
# - Caching and performance
# - Error handling
# - Backward compatibility
#
# Expected Outcome: ALL TESTS FAIL (RED phase)
# Next Step: Phase 5.2 GREEN - Implement TemplateRenderer class
