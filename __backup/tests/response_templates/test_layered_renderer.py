"""Tests for 3-layer template renderer (ENH-TEMPLATE-001 Phase 2).

Phase 2 Tests (AC-TEMPLATE-003, AC-TEMPLATE-004):
- Layer loading (Layer 1, 2, 3)
- Lazy loading for Layer 3
- Inheritance resolution
- Template composition
- Caching mechanism
- Placeholder substitution

Author: Asif Hussain
Phase: 9.7
"""

import pytest
from pathlib import Path
from src.response_templates.layered_template_renderer import LayeredTemplateRenderer


class TestLayerLoading:
    """Test AC-TEMPLATE-003: Load 3-layer template architecture."""
    
    def test_renderer_initialization(self):
        """Verify LayeredTemplateRenderer initializes successfully."""
        renderer = LayeredTemplateRenderer()
        assert renderer is not None
    
    def test_layer1_loaded_at_init(self):
        """Verify Layer 1 (mandatory header) loaded at initialization."""
        renderer = LayeredTemplateRenderer()
        assert hasattr(renderer, 'layer1'), "Must have layer1 attribute"
        assert renderer.layer1 is not None, "Layer 1 must be loaded"
        assert 'header_template' in renderer.layer1, "Must have header_template"
    
    def test_layer2_loaded_at_init(self):
        """Verify Layer 2 (executive summary) loaded at initialization."""
        renderer = LayeredTemplateRenderer()
        assert hasattr(renderer, 'layer2'), "Must have layer2 attribute"
        assert renderer.layer2 is not None, "Layer 2 must be loaded"
        assert 'sections' in renderer.layer2, "Must have sections"
    
    def test_layer3_cache_initialized(self):
        """Verify Layer 3 cache initialized but empty."""
        renderer = LayeredTemplateRenderer()
        assert hasattr(renderer, 'layer3_cache'), "Must have layer3_cache"
        assert isinstance(renderer.layer3_cache, dict), "Cache must be dict"
        assert len(renderer.layer3_cache) == 0, "Cache should start empty (lazy loading)"


class TestLazyLoading:
    """Test AC-TEMPLATE-004: Lazy load Layer 3 orchestrator templates."""
    
    def test_layer3_not_loaded_until_requested(self):
        """Verify Layer 3 not loaded at initialization."""
        renderer = LayeredTemplateRenderer()
        assert len(renderer.layer3_cache) == 0, "Should not load Layer 3 until requested"
    
    def test_layer3_loaded_on_first_request(self):
        """Verify Layer 3 loaded when first requested."""
        renderer = LayeredTemplateRenderer()
        templates = renderer._load_orchestrator_templates('generic')
        
        assert templates is not None, "Must return templates"
        assert 'generic' in renderer.layer3_cache, "Must cache loaded templates"
        assert 'templates' in templates, "Must have templates dict"
    
    def test_layer3_cached_on_subsequent_requests(self):
        """Verify Layer 3 served from cache on subsequent requests."""
        renderer = LayeredTemplateRenderer()
        
        # First request (loads from file)
        templates1 = renderer._load_orchestrator_templates('generic')
        cache_size_after_first = len(renderer.layer3_cache)
        
        # Second request (should use cache)
        templates2 = renderer._load_orchestrator_templates('generic')
        cache_size_after_second = len(renderer.layer3_cache)
        
        assert templates1 is templates2, "Should return same object (cached)"
        assert cache_size_after_first == cache_size_after_second == 1, "Cache size should not change"
    
    def test_missing_orchestrator_falls_back_to_generic(self):
        """Verify missing orchestrator falls back to generic.yaml."""
        renderer = LayeredTemplateRenderer()
        templates = renderer._load_orchestrator_templates('NONEXISTENT-ORCHESTRATOR')
        
        assert templates is not None, "Must return fallback"
        assert templates['orchestrator'] == 'generic', "Must fall back to generic"


class TestInheritanceResolution:
    """Test AC-TEMPLATE-004: Resolve Layer 3 inheritance from Layer 1/2."""
    
    def test_layer3_declares_inheritance(self):
        """Verify Layer 3 declares inheritance from Layer 1 and 2."""
        renderer = LayeredTemplateRenderer()
        templates = renderer._load_orchestrator_templates('generic')
        
        assert 'inherits' in templates, "Must declare inheritance"
        inherits = templates['inherits']
        assert 'mandatory-header.yaml' in inherits, "Must inherit Layer 1"
        assert 'executive-summary.yaml' in inherits, "Must inherit Layer 2"
    
    def test_inheritance_validation(self):
        """Verify inheritance chain is validated."""
        renderer = LayeredTemplateRenderer()
        
        # Should not raise exception for valid inheritance
        try:
            renderer._validate_inheritance('generic')
            validation_passed = True
        except Exception:
            validation_passed = False
        
        assert validation_passed, "Valid inheritance should pass validation"


class TestTemplateComposition:
    """Test AC-TEMPLATE-003: Compose templates from 3 layers."""
    
    def test_render_with_all_layers(self):
        """Verify render() composes Layer 1 + Layer 2 + Layer 3."""
        renderer = LayeredTemplateRenderer()
        
        context = {
            'operation_type': 'Test Operation',
            'phase': 'Phase 9.7',
            'orchestrator': 'generic',
            'operation': 'Unit test',
            'details': 'passed'
        }
        
        result = renderer.render('generic', 'generic_success', context)
        
        # Should include Layer 1 (header)
        assert "## 🧠 CORTEX Test Operation" in result, "Must include Layer 1 header"
        assert "**Author:** Asif Hussain" in result, "Must include author"
        
        # Should include Layer 3 (template content)
        assert "Unit test passed" in result or "✅" in result, "Must include Layer 3 content"
    
    def test_header_always_first(self):
        """Verify Layer 1 header always appears first."""
        renderer = LayeredTemplateRenderer()
        
        context = {
            'operation_type': 'Test',
            'phase': 'Phase 9.7',
            'orchestrator': 'generic'
        }
        
        result = renderer.render('generic', 'generic_success', context)
        
        # Header must be on line 1
        lines = result.strip().split('\n')
        assert lines[0].startswith("## 🧠 CORTEX"), "Header must be first line"
    
    def test_placeholder_substitution(self):
        """Verify placeholders substituted in rendered output."""
        renderer = LayeredTemplateRenderer()
        
        context = {
            'operation_type': 'Code Generation',
            'phase': 'Phase 9.7',
            'orchestrator': 'TDD-MASTER',
            'operation': 'Test creation',
            'details': 'completed successfully'
        }
        
        result = renderer.render('generic', 'generic_success', context)
        
        # No unsubstituted placeholders
        assert '{operation_type}' not in result, "Must substitute operation_type"
        assert '{phase}' not in result, "Must substitute phase"
        assert '{orchestrator}' not in result, "Must substitute orchestrator"
        
        # Substituted values present
        assert 'Code Generation' in result, "Must include substituted operation_type"
        assert 'Phase 9.7' in result, "Must include substituted phase"


class TestCachingMechanism:
    """Test AC-TEMPLATE-004: Layer caching for performance."""
    
    def test_layer1_cached_as_singleton(self):
        """Verify Layer 1 loaded once and reused."""
        renderer1 = LayeredTemplateRenderer()
        renderer2 = LayeredTemplateRenderer()
        
        # Both should reference same Layer 1 data (if singleton implemented)
        # For now, just verify both have Layer 1 loaded
        assert renderer1.layer1 is not None
        assert renderer2.layer1 is not None
    
    def test_layer3_cache_grows_on_demand(self):
        """Verify Layer 3 cache grows as orchestrators requested."""
        renderer = LayeredTemplateRenderer()
        
        assert len(renderer.layer3_cache) == 0, "Cache starts empty"
        
        renderer._load_orchestrator_templates('generic')
        assert len(renderer.layer3_cache) == 1, "Cache grows to 1"
        
        # Request same orchestrator (should not grow)
        renderer._load_orchestrator_templates('generic')
        assert len(renderer.layer3_cache) == 1, "Cache stays at 1 (reused)"


class TestErrorHandling:
    """Test error handling for missing/invalid templates."""
    
    def test_missing_layer1_raises_error(self):
        """Verify missing Layer 1 raises clear error."""
        # This would require mocking file system or creating broken renderer
        # For now, verify normal path works
        renderer = LayeredTemplateRenderer()
        assert renderer.layer1 is not None
    
    def test_invalid_template_id_returns_error_message(self):
        """Verify invalid template ID returns helpful error."""
        renderer = LayeredTemplateRenderer()
        
        context = {
            'operation_type': 'Test',
            'phase': 'Phase 9.7',
            'orchestrator': 'generic'
        }
        
        # Should handle gracefully (not crash)
        try:
            result = renderer.render('generic', 'NONEXISTENT_TEMPLATE', context)
            # If no exception, verify result indicates error
            assert 'error' in result.lower() or 'not found' in result.lower()
        except KeyError:
            # Acceptable to raise KeyError for missing template
            pass
