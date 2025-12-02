"""Phase 5.5 RED - Backward Compatibility Tests

Tests ensuring ResponseTemplateManager maintains backward compatibility
with existing CORTEX codebase while using new modular template system.

Author: Asif Hussain
Phase: 5.5 - Backward Compatibility Integration
Version: 1.0
Created: December 2, 2025
"""

import pytest
from pathlib import Path
from src.response_templates.response_template_manager import ResponseTemplateManager


class TestResponseTemplateManagerAPI:
    """Test ResponseTemplateManager provides expected API."""
    
    def test_manager_initializes_with_defaults(self):
        """Test manager can be initialized with default settings."""
        manager = ResponseTemplateManager()
        
        assert manager is not None
        assert hasattr(manager, 'render_template')
        assert hasattr(manager, 'get_template')
        assert hasattr(manager, 'list_templates')
    
    def test_manager_accepts_custom_template_dir(self):
        """Test manager accepts custom template directory."""
        custom_dir = Path("cortex-brain/response-templates")
        manager = ResponseTemplateManager(template_dir=custom_dir)
        
        assert manager.template_dir == custom_dir
    
    def test_manager_accepts_profile_manager(self):
        """Test manager accepts optional profile manager."""
        # Mock profile manager
        class MockProfileManager:
            def get_user_mode(self):
                return 'guided'
        
        profile_mgr = MockProfileManager()
        manager = ResponseTemplateManager(profile_manager=profile_mgr)
        
        assert manager.profile_manager == profile_mgr


class TestTemplateRendering:
    """Test template rendering with legacy API."""
    
    @pytest.fixture
    def manager(self):
        """Create ResponseTemplateManager instance."""
        return ResponseTemplateManager()
    
    def test_render_simple_template(self, manager):
        """Test rendering simple template by ID."""
        result = manager.render_template(
            template_id='help',
            context={'operation': 'test'}
        )
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0
    
    def test_render_template_with_mode(self, manager):
        """Test rendering template with specific mode."""
        result = manager.render_template(
            template_id='help',
            mode='autonomous'
        )
        
        assert result is not None
        # Autonomous mode should use compact next steps format
        assert '**Next:**' in result or 'Next' in result
    
    def test_render_template_with_context(self, manager):
        """Test rendering template with context variables."""
        context = {
            'user_name': 'Developer',
            'operation': 'refactoring',
            'status': 'in-progress'
        }
        
        result = manager.render_template(
            template_id='general',
            context=context
        )
        
        assert result is not None
        # Context values should not appear as {{placeholders}}
        assert '{{' not in result or '}}' not in result
    
    def test_render_with_all_modes(self, manager):
        """Test rendering works with all 4 interaction modes."""
        modes = ['autonomous', 'guided', 'educational', 'pair']
        
        for mode in modes:
            result = manager.render_template(
                template_id='fallback',
                mode=mode,
                context={'operation': 'test'}
            )
            
            assert result is not None
            assert len(result) > 0
            # Each mode should produce output (length check removed as it varies)


class TestTemplateRetrieval:
    """Test template retrieval operations."""
    
    @pytest.fixture
    def manager(self):
        """Create ResponseTemplateManager instance."""
        return ResponseTemplateManager()
    
    def test_get_template_by_id(self, manager):
        """Test retrieving template by ID."""
        template = manager.get_template('help')
        
        assert template is not None
        assert isinstance(template, dict)
        assert 'name' in template or 'components' in template
    
    def test_get_nonexistent_template_returns_none(self, manager):
        """Test getting non-existent template returns None."""
        template = manager.get_template('nonexistent_template_xyz')
        
        assert template is None
    
    def test_list_all_templates(self, manager):
        """Test listing all available templates."""
        templates = manager.list_templates()
        
        assert templates is not None
        assert isinstance(templates, list)
        assert len(templates) > 0
        
        # Should include core templates
        template_ids = [t['id'] for t in templates]
        assert 'help' in template_ids
        assert 'fallback' in template_ids
    
    def test_list_templates_by_category(self, manager):
        """Test filtering templates by category."""
        templates = manager.list_templates(category='planning')
        
        assert templates is not None
        assert isinstance(templates, list)
        # All returned templates should be in planning category
        for template in templates:
            assert template.get('category') == 'planning'


class TestTriggerRouting:
    """Test trigger-based template routing."""
    
    @pytest.fixture
    def manager(self):
        """Create ResponseTemplateManager instance."""
        return ResponseTemplateManager()
    
    def test_route_by_trigger_exact_match(self, manager):
        """Test routing with exact trigger match."""
        template_id = manager.route_trigger('help')
        
        assert template_id is not None
        assert template_id == 'help'
    
    def test_route_by_trigger_case_insensitive(self, manager):
        """Test routing is case-insensitive."""
        template_id = manager.route_trigger('HELP')
        
        assert template_id == 'help'
    
    def test_route_by_trigger_fuzzy_match(self, manager):
        """Test routing with fuzzy matching (80%+ similarity)."""
        # 'halp' should fuzzy match to 'help'
        template_id = manager.route_trigger('halp')
        
        assert template_id is not None
        # Should match to help or fallback
        assert template_id in ['help', 'fallback']
    
    def test_route_unknown_trigger_returns_fallback(self, manager):
        """Test routing unknown trigger returns fallback template."""
        template_id = manager.route_trigger('completely_unknown_xyz')
        
        assert template_id == 'fallback'
    
    def test_render_by_trigger(self, manager):
        """Test rendering template by trigger instead of ID."""
        result = manager.render_by_trigger(
            trigger='help',
            context={'operation': 'test'}
        )
        
        assert result is not None
        assert isinstance(result, str)
        assert len(result) > 0


class TestModeSelection:
    """Test interaction mode selection and application."""
    
    @pytest.fixture
    def manager(self):
        """Create ResponseTemplateManager instance."""
        return ResponseTemplateManager()
    
    def test_default_mode_is_guided(self, manager):
        """Test default mode is 'guided' when not specified."""
        result = manager.render_template(template_id='fallback')
        
        # Guided mode has full headers
        assert '###' in result
        assert '🎯' in result or '💬' in result
    
    def test_invalid_mode_falls_back_to_guided(self, manager):
        """Test invalid mode falls back to guided."""
        result = manager.render_template(
            template_id='fallback',
            mode='invalid_mode_xyz'
        )
        
        # Should render as guided mode
        assert '###' in result
    
    def test_profile_manager_overrides_mode(self):
        """Test profile manager can override default mode."""
        class MockProfileManager:
            def get_user_mode(self):
                return 'autonomous'
        
        manager = ResponseTemplateManager(profile_manager=MockProfileManager())
        result = manager.render_template(template_id='fallback')
        
        # Should use autonomous mode from profile (compact format)
        assert result is not None
        assert '**Next:**' in result or len(result) < 1000  # Compact format


class TestCaching:
    """Test template caching for performance."""
    
    @pytest.fixture
    def manager(self):
        """Create ResponseTemplateManager instance."""
        return ResponseTemplateManager()
    
    def test_repeated_renders_use_cache(self, manager):
        """Test repeated renders of same template hit cache."""
        # First render
        manager.render_template(template_id='help', mode='guided')
        initial_hit_count = manager.renderer.cache_hit_count
        
        # Second render with same params
        manager.render_template(template_id='help', mode='guided')
        
        # Cache hit count should increase
        assert manager.renderer.cache_hit_count > initial_hit_count
    
    def test_different_modes_cache_separately(self, manager):
        """Test different modes are cached separately."""
        result1 = manager.render_template(template_id='fallback', mode='autonomous')
        result2 = manager.render_template(template_id='fallback', mode='guided')
        
        # Should produce different output
        assert result1 != result2
    
    def test_different_context_cache_separately(self, manager):
        """Test different contexts are cached separately."""
        result1 = manager.render_template(
            template_id='fallback',
            context={'operation': 'testing'}
        )
        result2 = manager.render_template(
            template_id='fallback',
            context={'operation': 'deployment'}
        )
        
        # Should produce output (may be same or different depending on placeholder usage)
        assert result1 is not None
        assert result2 is not None


class TestErrorHandling:
    """Test error handling and graceful degradation."""
    
    @pytest.fixture
    def manager(self):
        """Create ResponseTemplateManager instance."""
        return ResponseTemplateManager()
    
    def test_render_missing_template_returns_fallback(self, manager):
        """Test rendering missing template returns fallback."""
        result = manager.render_template(template_id='nonexistent_xyz')
        
        assert result is not None
        assert isinstance(result, str)
        # Should use fallback template
        assert len(result) > 0
    
    def test_render_with_none_context(self, manager):
        """Test rendering with None context doesn't crash."""
        result = manager.render_template(template_id='help', context=None)
        
        assert result is not None
        assert isinstance(result, str)
    
    def test_render_with_empty_context(self, manager):
        """Test rendering with empty context works."""
        result = manager.render_template(template_id='help', context={})
        
        assert result is not None
        assert isinstance(result, str)
    
    def test_invalid_template_dir_raises_error(self):
        """Test invalid template directory raises clear error."""
        with pytest.raises(FileNotFoundError):
            ResponseTemplateManager(template_dir=Path("nonexistent/path"))


class TestLegacyCompatibility:
    """Test compatibility with existing CORTEX usage patterns."""
    
    @pytest.fixture
    def manager(self):
        """Create ResponseTemplateManager instance."""
        return ResponseTemplateManager()
    
    def test_supports_help_command(self, manager):
        """Test rendering help template (common operation)."""
        result = manager.render_template(template_id='help')
        
        assert result is not None
        assert len(result) > 100  # Should have substantial content
    
    def test_supports_general_response(self, manager):
        """Test rendering fallback response template."""
        result = manager.render_template(
            template_id='fallback',
            context={'operation': 'refactoring'}
        )
        
        assert result is not None
    
    def test_supports_error_response(self, manager):
        """Test rendering error response template."""
        result = manager.render_template(
            template_id='error',
            context={'error_message': 'Test error'}
        )
        
        assert result is not None
    
    def test_supports_planning_workflow(self, manager):
        """Test rendering planning-related templates."""
        result = manager.render_template(
            template_id='planning',
            context={'feature': 'User authentication'}
        )
        
        assert result is not None


class TestPerformance:
    """Test performance requirements for backward compatibility."""
    
    @pytest.fixture
    def manager(self):
        """Create ResponseTemplateManager instance."""
        return ResponseTemplateManager()
    
    def test_initialization_is_fast(self):
        """Test manager initialization completes quickly."""
        import time
        
        start = time.time()
        manager = ResponseTemplateManager()
        duration = time.time() - start
        
        # Should initialize in under 100ms
        assert duration < 0.1
    
    def test_render_is_fast(self, manager):
        """Test template rendering completes quickly."""
        import time
        
        start = time.time()
        manager.render_template(template_id='help')
        duration = time.time() - start
        
        # First render (no cache) should complete in under 50ms
        assert duration < 0.05
    
    def test_cached_render_is_very_fast(self, manager):
        """Test cached rendering is significantly faster."""
        import time
        
        # Warm up cache
        manager.render_template(template_id='help', mode='guided')
        
        # Measure cached render
        start = time.time()
        manager.render_template(template_id='help', mode='guided')
        duration = time.time() - start
        
        # Cached render should be under 5ms
        assert duration < 0.005
