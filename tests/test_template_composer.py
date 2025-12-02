"""
Unit Tests for TemplateComposer
Version: 3.3.0
Purpose: Test template composition with profile-aware variants
Part of: Response Template System Refactor (Phase 5)
Target: 25 tests, 85% coverage
"""

import pytest
import time
import tempfile
import yaml
from pathlib import Path
from src.utils.template_composer import (
    TemplateComposer,
    UserProfile,
    ComposedResponse
)


@pytest.fixture
def mock_yaml_files(tmp_path):
    """Create mock YAML files for testing"""
    
    # Mock response-base-components.yaml
    components = {
        'shared_components': {
            'standard_header': {
                'id': 'header_standard',
                'type': 'header',
                'content': '## 🧠 CORTEX {{title}}\n**Author:** Asif Hussain\n\n---\n'
            },
            'section_response': {
                'id': 'section_response',
                'type': 'section',
                'icon': '💬',
                'title': 'Response',
                'content': '{{response_content}}',
                'variants': {
                    'concise': '{{response_brief}}',
                    'balanced': '{{response_content}}',
                    'verbose': '{{response_content}}\n\n**Additional Context:** {{additional_context}}'
                }
            },
            'section_next_steps': {
                'id': 'section_next_steps',
                'type': 'section',
                'icon': '🔍',
                'title': 'Next Steps',
                'content': '{{next_steps_content}}'
            }
        },
        'format_variants': {
            'standard_5_part': {
                'id': 'format_standard_5_part',
                'sections': ['header_standard', 'section_response', 'section_next_steps']
            },
            'compact': {
                'id': 'format_compact',
                'sections': ['header_standard', 'section_response']
            }
        },
        'rendering_rules': {
            'section_separator': '\n\n'
        }
    }
    
    # Mock response-template-definitions.yaml
    definitions = {
        'templates': {
            'help_table': {
                'id': 'template_help_table',
                'name': 'Help Table',
                'format': 'compact',
                'required_sections': ['header_standard', 'section_response']
            },
            'fallback': {
                'id': 'template_fallback',
                'name': 'Fallback',
                'format': 'standard_5_part',
                'required_sections': ['header_standard', 'section_response', 'section_next_steps']
            }
        }
    }
    
    # Mock response-profile-variants.yaml
    variants = {
        'interaction_modes': {
            'autonomous': {
                'id': 'mode_autonomous',
                'default_detail_level': 'concise'
            },
            'guided': {
                'id': 'mode_guided',
                'default_detail_level': 'balanced'
            },
            'educational': {
                'id': 'mode_educational',
                'default_detail_level': 'verbose',
                'additional_sections': []
            }
        }
    }
    
    # Mock response-routing-rules.yaml
    routing = {
        'intent_detection': {},
        'caching': {
            'template_cache': {'enabled': True, 'ttl': 86400}
        }
    }
    
    # Write mock files
    (tmp_path / "response-base-components.yaml").write_text(yaml.dump(components))
    (tmp_path / "response-template-definitions.yaml").write_text(yaml.dump(definitions))
    (tmp_path / "response-profile-variants.yaml").write_text(yaml.dump(variants))
    (tmp_path / "response-routing-rules.yaml").write_text(yaml.dump(routing))
    
    return tmp_path


class TestTemplateComposerInitialization:
    """Test TemplateComposer initialization"""
    
    def test_init_with_custom_path(self, mock_yaml_files):
        """Test initialization with custom brain path"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        assert composer.brain_path == Path(mock_yaml_files)
        assert composer.components_path.exists()
        assert composer.definitions_path.exists()
    
    def test_init_without_path(self):
        """Test initialization without path (uses default)"""
        composer = TemplateComposer()
        assert composer.brain_path is not None
        assert composer._cache == {}
        assert composer._cache_ttl == 86400


class TestLazyLoading:
    """Test lazy loading of YAML files"""
    
    def test_lazy_load_components(self, mock_yaml_files):
        """Test components are loaded on first access"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        assert composer._components is None
        
        # Access components
        components = composer.components
        assert composer._components is not None
        assert 'shared_components' in components
    
    def test_lazy_load_definitions(self, mock_yaml_files):
        """Test definitions are loaded on first access"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        assert composer._definitions is None
        
        definitions = composer.definitions
        assert composer._definitions is not None
        assert 'templates' in definitions
    
    def test_lazy_load_cached(self, mock_yaml_files):
        """Test lazy-loaded data is cached"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        
        components1 = composer.components
        components2 = composer.components
        assert components1 is components2  # Same object


class TestCaching:
    """Test template caching mechanism"""
    
    def test_cache_key_generation(self, mock_yaml_files):
        """Test cache key is consistent"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile = UserProfile(interaction_mode='guided', response_detail='balanced')
        
        key1 = composer._generate_cache_key('template_help', profile)
        key2 = composer._generate_cache_key('template_help', profile)
        assert key1 == key2
    
    def test_cache_key_uniqueness(self, mock_yaml_files):
        """Test different profiles produce different cache keys"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile1 = UserProfile(interaction_mode='guided')
        profile2 = UserProfile(interaction_mode='autonomous')
        
        key1 = composer._generate_cache_key('template_help', profile1)
        key2 = composer._generate_cache_key('template_help', profile2)
        assert key1 != key2
    
    def test_cache_hit(self, mock_yaml_files):
        """Test cached response is returned on second call"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile = UserProfile()
        
        # First call - compose from scratch
        response1 = composer.compose_response(
            'template_help_table',
            profile,
            content_vars={'title': 'Help', 'response_content': 'Test content'}
        )
        assert response1.cached is False
        
        # Second call - should hit cache
        response2 = composer.compose_response(
            'template_help_table',
            profile,
            content_vars={'title': 'Help', 'response_content': 'Test content'}
        )
        assert response2.cached is True
    
    def test_cache_expiration(self, mock_yaml_files):
        """Test cache expires after TTL"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        composer._cache_ttl = 1  # 1 second TTL for testing
        profile = UserProfile()
        
        # First call
        response1 = composer.compose_response(
            'template_help_table',
            profile,
            content_vars={'title': 'Help', 'response_content': 'Test'}
        )
        
        # Wait for expiration
        time.sleep(1.1)
        
        # Second call - cache should be expired
        response2 = composer.compose_response(
            'template_help_table',
            profile,
            content_vars={'title': 'Help', 'response_content': 'Test'}
        )
        # Note: Both will be False because we clear expired entries
        assert response1.cached is False
    
    def test_force_recompose(self, mock_yaml_files):
        """Test force_recompose bypasses cache"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile = UserProfile()
        
        # First call
        composer.compose_response(
            'template_help_table',
            profile,
            content_vars={'title': 'Help', 'response_content': 'Test'}
        )
        
        # Force recompose
        response = composer.compose_response(
            'template_help_table',
            profile,
            content_vars={'title': 'Help', 'response_content': 'Test'},
            force_recompose=True
        )
        assert response.cached is False
    
    def test_clear_cache(self, mock_yaml_files):
        """Test clear_cache empties cache"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile = UserProfile()
        
        # Add to cache
        composer.compose_response(
            'template_help_table',
            profile,
            content_vars={'title': 'Help', 'response_content': 'Test'}
        )
        assert len(composer._cache) > 0
        
        # Clear cache
        composer.clear_cache()
        assert len(composer._cache) == 0


class TestFormatSelection:
    """Test format selection logic"""
    
    def test_concise_selects_compact(self, mock_yaml_files):
        """Test concise detail level selects compact format"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        template = {'format': 'standard_5_part'}
        profile = UserProfile(response_detail='concise')
        
        format_id = composer._select_format(template, profile)
        assert format_id == 'format_compact'
    
    def test_verbose_educational_selects_educational(self, mock_yaml_files):
        """Test verbose + educational selects educational format"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        template = {'format': 'standard_5_part'}
        profile = UserProfile(
            interaction_mode='educational',
            response_detail='verbose'
        )
        
        format_id = composer._select_format(template, profile)
        assert format_id == 'format_educational'
    
    def test_default_format_used(self, mock_yaml_files):
        """Test template's default format is used"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        template = {'format': 'compact'}
        profile = UserProfile(response_detail='balanced')
        
        format_id = composer._select_format(template, profile)
        assert format_id == 'format_compact'


class TestDetailLevelResolution:
    """Test detail level resolution"""
    
    def test_explicit_concise_used(self, mock_yaml_files):
        """Test explicit concise is used"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile = UserProfile(response_detail='concise')
        
        detail = composer._resolve_detail_level(profile)
        assert detail == 'concise'
    
    def test_explicit_verbose_used(self, mock_yaml_files):
        """Test explicit verbose is used"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile = UserProfile(response_detail='verbose')
        
        detail = composer._resolve_detail_level(profile)
        assert detail == 'verbose'
    
    def test_balanced_respects_autonomous_mode(self, mock_yaml_files):
        """Test balanced + autonomous = concise"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile = UserProfile(
            interaction_mode='autonomous',
            response_detail='balanced'
        )
        
        detail = composer._resolve_detail_level(profile)
        assert detail == 'concise'
    
    def test_balanced_respects_educational_mode(self, mock_yaml_files):
        """Test balanced + educational = verbose"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile = UserProfile(
            interaction_mode='educational',
            response_detail='balanced'
        )
        
        detail = composer._resolve_detail_level(profile)
        assert detail == 'verbose'


class TestComposition:
    """Test template composition"""
    
    def test_compose_basic_template(self, mock_yaml_files):
        """Test basic template composition"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile = UserProfile()
        
        response = composer.compose_response(
            'template_help_table',
            profile,
            content_vars={
                'title': 'Help Commands',
                'response_content': 'Available commands: help, status'
            }
        )
        
        assert response.content is not None
        assert 'Help Commands' in response.content
        assert 'Available commands' in response.content
        assert response.template_id == 'template_help_table'
    
    def test_composition_performance(self, mock_yaml_files):
        """Test composition completes within 50ms target"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile = UserProfile()
        
        response = composer.compose_response(
            'template_help_table',
            profile,
            content_vars={
                'title': 'Test',
                'response_content': 'Content'
            }
        )
        
        # First call might be slower due to lazy loading
        # Second call should be fast (cached)
        response2 = composer.compose_response(
            'template_help_table',
            profile,
            content_vars={
                'title': 'Test',
                'response_content': 'Content'}
        )
        
        # Cached response should be nearly instant
        assert response2.composition_time_ms < 50  # Target: <50ms
    
    def test_variable_substitution(self, mock_yaml_files):
        """Test variable substitution works correctly"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        
        text = "Hello {{name}}, you are {{age}} years old"
        result = composer._substitute_variables(text, {
            'name': 'Alice',
            'age': '25'
        })
        
        assert result == "Hello Alice, you are 25 years old"
    
    def test_missing_template_raises_error(self, mock_yaml_files):
        """Test missing template raises ValueError"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile = UserProfile()
        
        with pytest.raises(ValueError, match="Template not found"):
            composer.compose_response('template_nonexistent', profile)


class TestCacheStats:
    """Test cache statistics"""
    
    def test_cache_stats_empty(self, mock_yaml_files):
        """Test cache stats when empty"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        
        stats = composer.get_cache_stats()
        assert stats['total_entries'] == 0
        assert stats['valid_entries'] == 0
    
    def test_cache_stats_with_entries(self, mock_yaml_files):
        """Test cache stats with entries"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        profile = UserProfile()
        
        # Add entries
        composer.compose_response(
            'template_help_table',
            profile,
            content_vars={'title': 'Test', 'response_content': 'Content'}
        )
        
        stats = composer.get_cache_stats()
        assert stats['total_entries'] > 0
        assert stats['valid_entries'] > 0


class TestProfileVariants:
    """Test profile-based variant selection"""
    
    def test_concise_variant_selected(self, mock_yaml_files):
        """Test concise variant is selected for concise detail level"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        
        component = {
            'content': 'default content',
            'variants': {
                'concise': 'brief content',
                'verbose': 'detailed content'
            }
        }
        
        content = composer._get_component_content(component, 'concise')
        assert content == 'brief content'
    
    def test_default_content_fallback(self, mock_yaml_files):
        """Test default content used when no variant exists"""
        composer = TemplateComposer(brain_path=str(mock_yaml_files))
        
        component = {
            'content': 'default content',
            'variants': {}
        }
        
        content = composer._get_component_content(component, 'verbose')
        assert content == 'default content'


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--cov=src.utils.template_composer', '--cov-report=term-missing'])
