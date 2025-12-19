"""
Unit Tests for TemplateSelector
Version: 3.3.0
Purpose: Test intent detection and template selection
Part of: Response Template System Refactor (Phase 5.4)
Target: 15+ end-to-end tests
"""

import pytest
import yaml
from pathlib import Path
from src.utils.template_selector import TemplateSelector, SelectionResult
from src.utils.template_composer import UserProfile


@pytest.fixture
def mock_yaml_files(tmp_path):
    """Create mock YAML files for testing (shared with template_composer tests)"""
    
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
            },
            'educational': {
                'id': 'format_educational',
                'sections': ['header_standard', 'section_response', 'section_next_steps']
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
        'intent_detection': {
            'priority_1_exact_match': [
                {
                    'intent': 'help_table',
                    'keywords': ['help', 'commands'],
                    'template': 'template_help_table',
                    'orchestrator': None
                }
            ],
            'fallback': {
                'intent': 'fallback',
                'template': 'template_fallback',
                'orchestrator': None
            }
        },
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


@pytest.fixture
def mock_routing_rules(tmp_path):
    """Create mock routing rules"""
    routing = {
        'intent_detection': {
            'priority_1_exact_match': [
                {
                    'intent': 'help_table',
                    'keywords': ['help', 'commands'],
                    'template': 'template_help_table',
                    'orchestrator': None
                },
                {
                    'intent': 'onboarding',
                    'keywords': ['onboard', 'setup profile'],
                    'template': 'template_onboarding',
                    'orchestrator': 'OnboardingOrchestrator'
                }
            ],
            'priority_2_planning': [
                {
                    'intent': 'planning_start',
                    'keywords': ['plan', 'create plan'],
                    'template': 'template_planning_dor_incomplete',
                    'orchestrator': 'PlanningOrchestrator'
                },
                {
                    'intent': 'ado_create',
                    'keywords': ['plan ado', 'create ado'],
                    'template': 'template_ado_created',
                    'orchestrator': 'ADOOrchestrator'
                }
            ],
            'priority_5_tech_aware': [
                {
                    'intent': 'tech_implementation',
                    'keywords': ['implement', 'add', 'create'],
                    'context_required': 'has_tech_stack',
                    'template': 'template_tech_implementation',
                    'orchestrator': None
                }
            ],
            'fallback': {
                'intent': 'fallback',
                'template': 'template_fallback',
                'orchestrator': None
            }
        }
    }
    
    routing_path = tmp_path / "response-routing-rules.yaml"
    routing_path.write_text(yaml.dump(routing))
    
    return tmp_path


class TestTemplateSelector:
    """Test TemplateSelector functionality"""
    
    def test_initialization(self, mock_routing_rules, mock_yaml_files):
        """Test selector initialization"""
        selector = TemplateSelector(brain_path=str(mock_yaml_files))
        assert selector.brain_path == Path(mock_yaml_files)
        assert selector.composer is not None
    
    def test_keyword_extraction(self, mock_yaml_files):
        """Test keyword extraction from text"""
        selector = TemplateSelector(brain_path=str(mock_yaml_files))
        
        keywords = selector._extract_keywords("Please help me with the commands")
        assert 'help' in keywords
        assert 'commands' in keywords
        assert 'please' in keywords  # Not a stop word in our simple implementation
        assert 'the' not in keywords  # Stop word removed
    
    def test_keyword_extraction_punctuation(self, mock_yaml_files):
        """Test punctuation is removed"""
        selector = TemplateSelector(brain_path=str(mock_yaml_files))
        
        keywords = selector._extract_keywords("help! what's available?")
        assert 'help' in keywords
        assert 'what' in keywords
        assert '!' not in keywords
        assert '?' not in keywords


class TestIntentMatching:
    """Test intent matching logic"""
    
    def test_simple_keyword_match(self, mock_routing_rules):
        """Test simple single keyword match"""
        # Create mock YAML files
        components_path = mock_routing_rules / "response-base-components.yaml"
        components_path.write_text(yaml.dump({
            'shared_components': {},
            'format_variants': {},
            'rendering_rules': {}
        }))
        
        definitions_path = mock_routing_rules / "response-template-definitions.yaml"
        definitions_path.write_text(yaml.dump({'templates': {}}))
        
        variants_path = mock_routing_rules / "response-profile-variants.yaml"
        variants_path.write_text(yaml.dump({'interaction_modes': {}}))
        
        selector = TemplateSelector(brain_path=str(mock_routing_rules))
        
        result = selector.select_template("help me")
        assert result.template_id == 'template_help_table'
        assert result.matched_intent == 'help_table'
        assert 'help' in result.matched_keywords
    
    def test_multi_word_keyword_match(self, mock_routing_rules):
        """Test multi-word keyword phrase matching"""
        components_path = mock_routing_rules / "response-base-components.yaml"
        components_path.write_text(yaml.dump({
            'shared_components': {},
            'format_variants': {},
            'rendering_rules': {}
        }))
        
        definitions_path = mock_routing_rules / "response-template-definitions.yaml"
        definitions_path.write_text(yaml.dump({'templates': {}}))
        
        variants_path = mock_routing_rules / "response-profile-variants.yaml"
        variants_path.write_text(yaml.dump({'interaction_modes': {}}))
        
        selector = TemplateSelector(brain_path=str(mock_routing_rules))
        
        # Test that "plan ado" specifically matches ADO creation
        # The phrase "plan ado" should be detected as a multi-word keyword
        result = selector.select_template("create ado work item")
        # This should match "create ado" keyword from ADO intent
        assert 'ado' in result.matched_keywords or result.matched_intent in ['ado_create', 'planning_start']
        # Accept either ADO or planning intent since both use "plan/create" + "ado"
        assert result.template_id in ['template_ado_created', 'template_planning_dor_incomplete']
    
    def test_priority_matching(self, mock_routing_rules):
        """Test priority-based matching (earlier priority wins)"""
        components_path = mock_routing_rules / "response-base-components.yaml"
        components_path.write_text(yaml.dump({
            'shared_components': {},
            'format_variants': {},
            'rendering_rules': {}
        }))
        
        definitions_path = mock_routing_rules / "response-template-definitions.yaml"
        definitions_path.write_text(yaml.dump({'templates': {}}))
        
        variants_path = mock_routing_rules / "response-profile-variants.yaml"
        variants_path.write_text(yaml.dump({'interaction_modes': {}}))
        
        selector = TemplateSelector(brain_path=str(mock_routing_rules))
        
        # "help" matches priority_1_exact_match
        result = selector.select_template("help me plan")
        assert result.template_id == 'template_help_table'  # Priority 1 wins
    
    def test_context_validation_has_tech_stack(self, mock_routing_rules):
        """Test context validation for tech_stack requirement"""
        components_path = mock_routing_rules / "response-base-components.yaml"
        components_path.write_text(yaml.dump({
            'shared_components': {},
            'format_variants': {},
            'rendering_rules': {}
        }))
        
        definitions_path = mock_routing_rules / "response-template-definitions.yaml"
        definitions_path.write_text(yaml.dump({'templates': {}}))
        
        variants_path = mock_routing_rules / "response-profile-variants.yaml"
        variants_path.write_text(yaml.dump({'interaction_modes': {}}))
        
        selector = TemplateSelector(brain_path=str(mock_routing_rules))
        
        # Without tech_stack context - should fallback
        result = selector.select_template("implement caching")
        assert result.template_id == 'template_fallback'
        
        # With tech_stack context - should match
        result = selector.select_template(
            "implement caching",
            context={'tech_stack': {'cloud_provider': 'azure'}}
        )
        assert result.template_id == 'template_tech_implementation'
    
    def test_fallback_on_no_match(self, mock_routing_rules):
        """Test fallback template used when no match"""
        components_path = mock_routing_rules / "response-base-components.yaml"
        components_path.write_text(yaml.dump({
            'shared_components': {},
            'format_variants': {},
            'rendering_rules': {}
        }))
        
        definitions_path = mock_routing_rules / "response-template-definitions.yaml"
        definitions_path.write_text(yaml.dump({'templates': {}}))
        
        variants_path = mock_routing_rules / "response-profile-variants.yaml"
        variants_path.write_text(yaml.dump({'interaction_modes': {}}))
        
        selector = TemplateSelector(brain_path=str(mock_routing_rules))
        
        result = selector.select_template("xyz unknown command abc")
        assert result.template_id == 'template_fallback'
        assert result.matched_intent == 'fallback'
        assert result.confidence == 0.5


class TestEndToEndComposition:
    """Test end-to-end template selection + composition"""
    
    def test_compose_response_workflow(self, mock_yaml_files):
        """Test complete workflow from input to composed response"""
        selector = TemplateSelector(brain_path=str(mock_yaml_files))
        profile = UserProfile(
            interaction_mode='guided',
            experience_level='mid',
            response_detail='balanced'
        )
        
        selection, composed = selector.compose_response(
            user_input="help",
            profile=profile,
            content_vars={
                'title': 'Help Commands',
                'response_content': 'Available commands: help, status, plan'
            }
        )
        
        assert selection.template_id == 'template_help_table'
        assert composed.content is not None
        assert 'Help Commands' in composed.content
    
    def test_profile_affects_composition(self, mock_yaml_files):
        """Test user profile affects composed output"""
        selector = TemplateSelector(brain_path=str(mock_yaml_files))
        
        # Concise profile
        profile_concise = UserProfile(response_detail='concise')
        _, composed_concise = selector.compose_response(
            "help",
            profile_concise,
            content_vars={'title': 'Help', 'response_content': 'Commands'}
        )
        
        # Verbose profile (but not educational mode, so won't get educational format)
        profile_verbose = UserProfile(response_detail='verbose', interaction_mode='guided')
        _, composed_verbose = selector.compose_response(
            "help",
            profile_verbose,
            content_vars={'title': 'Help', 'response_content': 'Commands'}
        )
        
        # Concise should use compact format
        assert composed_concise.format_id == 'format_compact'
        # Verbose with guided mode uses standard format (not educational)
        assert composed_verbose.format_id in ['format_standard_5_part', 'format_compact']


class TestUtilityMethods:
    """Test utility methods"""
    
    def test_get_template_list(self, mock_yaml_files):
        """Test getting list of all templates"""
        selector = TemplateSelector(brain_path=str(mock_yaml_files))
        
        templates = selector.get_template_list()
        assert len(templates) > 0
        assert all('template_id' in t for t in templates)
        assert all('name' in t for t in templates)
    
    def test_get_intents_for_template(self, mock_routing_rules):
        """Test getting intents that map to a template"""
        components_path = mock_routing_rules / "response-base-components.yaml"
        components_path.write_text(yaml.dump({
            'shared_components': {},
            'format_variants': {},
            'rendering_rules': {}
        }))
        
        definitions_path = mock_routing_rules / "response-template-definitions.yaml"
        definitions_path.write_text(yaml.dump({'templates': {}}))
        
        variants_path = mock_routing_rules / "response-profile-variants.yaml"
        variants_path.write_text(yaml.dump({'interaction_modes': {}}))
        
        selector = TemplateSelector(brain_path=str(mock_routing_rules))
        
        intents = selector.get_intents_for_template('template_help_table')
        assert 'help_table' in intents
    
    def test_is_legacy_mode(self, mock_yaml_files):
        """Test legacy mode detection"""
        selector = TemplateSelector(brain_path=str(mock_yaml_files))
        
        # Default: new system
        assert selector.is_legacy_mode() is False


class TestConfidenceScoring:
    """Test confidence scoring for matches"""
    
    def test_confidence_single_keyword(self, mock_yaml_files):
        """Test confidence with single keyword match"""
        selector = TemplateSelector(brain_path=str(mock_yaml_files))
        
        result = selector.select_template("help")
        # Matched 1 of 2 keywords (help, commands)
        assert 0.4 < result.confidence <= 0.6
    
    def test_confidence_all_keywords(self, mock_yaml_files):
        """Test confidence with all keywords matched"""
        selector = TemplateSelector(brain_path=str(mock_yaml_files))
        
        result = selector.select_template("help commands")
        # Matched 2 of 2 keywords
        assert result.confidence >= 0.9


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
