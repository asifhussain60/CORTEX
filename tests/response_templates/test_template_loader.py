"""Tests for TemplateLoader.

Tests template loading from YAML, trigger matching, and template search.
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from src.response_templates.template_loader import TemplateLoader, Template


@pytest.fixture
def sample_template_file(tmp_path):
    """Create a sample template file for testing."""
    template_data = {
        'templates': {
            'help_table': {
                'triggers': ['help', '/help', 'show commands'],
                'response_type': 'table',
                'context_needed': False,
                'verbosity': 'concise',
                'content': '**CORTEX Commands**\n• setup\n• cleanup',
                'metadata': {'category': 'system'}
            },
            'executor_success': {
                'triggers': [],
                'response_type': 'detailed',
                'context_needed': True,
                'verbosity': 'concise',
                'content': '✅ **Feature Implemented**\nFiles: {{files_count}}',
                'metadata': {'category': 'agent', 'agent': 'executor'}
            },
            'status_check': {
                'triggers': ['status', '/status', 'implementation status'],
                'response_type': 'table',
                'context_needed': False,
                'verbosity': 'concise',
                'content': '📊 **CORTEX Status**',
                'metadata': {'category': 'system'}
            }
        }
    }
    
    template_file = tmp_path / "test-templates.yaml"
    with open(template_file, 'w') as f:
        yaml.dump(template_data, f)
    
    return template_file


class TestTemplateLoader:
    """Tests for TemplateLoader class."""
    
    def test_init(self, sample_template_file):
        """Test loader initialization."""
        loader = TemplateLoader(sample_template_file)
        assert loader.template_file == sample_template_file
        assert not loader._loaded
        assert loader._templates == {}
    
    def test_load_templates(self, sample_template_file):
        """Test loading templates from YAML."""
        loader = TemplateLoader(sample_template_file)
        loader.load_templates()
        
        assert loader._loaded
        assert len(loader._templates) == 3
        assert 'help_table' in loader._templates
        assert 'executor_success' in loader._templates
        assert 'status_check' in loader._templates
    
    def test_load_template_by_id(self, sample_template_file):
        """Test loading specific template by ID."""
        loader = TemplateLoader(sample_template_file)
        
        template = loader.load_template('help_table')
        
        assert template is not None
        assert template.template_id == 'help_table'
        assert 'help' in template.triggers
        assert template.response_type == 'table'
        assert not template.context_needed
        assert template.verbosity == 'concise'
        assert '**CORTEX Commands**' in template.content
    
    def test_load_nonexistent_template(self, sample_template_file):
        """Test loading template that doesn't exist."""
        loader = TemplateLoader(sample_template_file)
        
        template = loader.load_template('nonexistent')
        
        assert template is None
    
    def test_find_by_trigger_exact_match(self, sample_template_file):
        """Test finding template by exact trigger match."""
        loader = TemplateLoader(sample_template_file)
        
        template = loader.find_by_trigger('help')
        
        assert template is not None
        assert template.template_id == 'help_table'
    
    def test_find_by_trigger_case_insensitive(self, sample_template_file):
        """Test trigger matching is case-insensitive."""
        loader = TemplateLoader(sample_template_file)
        
        template = loader.find_by_trigger('HELP')
        
        assert template is not None
        assert template.template_id == 'help_table'
    
    def test_find_by_trigger_fuzzy_match(self, sample_template_file):
        """Test fuzzy trigger matching."""
        loader = TemplateLoader(sample_template_file)
        
        template = loader.find_by_trigger('help me')
        
        # Fuzzy matching looks for 'help' keyword
        assert template is not None
        assert template.template_id == 'help_table'
    
    def test_find_by_trigger_no_match(self, sample_template_file):
        """Test finding template with no matching trigger."""
        loader = TemplateLoader(sample_template_file)
        
        template = loader.find_by_trigger('nonexistent trigger')
        
        assert template is None
    
    def test_list_templates_all(self, sample_template_file):
        """Test listing all templates."""
        loader = TemplateLoader(sample_template_file)
        
        templates = loader.list_templates()
        
        assert len(templates) == 3
        template_ids = [t.template_id for t in templates]
        assert 'help_table' in template_ids
        assert 'executor_success' in template_ids
        assert 'status_check' in template_ids
    
    def test_list_templates_by_category(self, sample_template_file):
        """Test listing templates filtered by category."""
        loader = TemplateLoader(sample_template_file)
        
        templates = loader.list_templates(category='system')
        
        assert len(templates) == 2
        template_ids = [t.template_id for t in templates]
        assert 'help_table' in template_ids
        assert 'status_check' in template_ids
        assert 'executor_success' not in template_ids
    
    def test_get_template_ids(self, sample_template_file):
        """Test getting all template IDs."""
        loader = TemplateLoader(sample_template_file)
        
        ids = loader.get_template_ids()
        
        assert len(ids) == 3
        assert 'help_table' in ids
        assert 'executor_success' in ids
        assert 'status_check' in ids
    
    def test_get_triggers(self, sample_template_file):
        """Test getting all registered triggers."""
        loader = TemplateLoader(sample_template_file)
        
        triggers = loader.get_triggers()
        
        assert len(triggers) >= 5
        assert 'help' in triggers
        assert '/help' in triggers
        assert 'status' in triggers
    
    def test_load_templates_idempotent(self, sample_template_file):
        """Test that calling load_templates multiple times is safe."""
        loader = TemplateLoader(sample_template_file)
        
        loader.load_templates()
        count1 = len(loader._templates)
        
        loader.load_templates()
        count2 = len(loader._templates)
        
        assert count1 == count2
        assert loader._loaded
    
    def test_file_not_found_error(self, tmp_path):
        """Test error handling for missing template file."""
        nonexistent_file = tmp_path / "nonexistent.yaml"
        loader = TemplateLoader(nonexistent_file)
        
        with pytest.raises(FileNotFoundError):
            loader.load_templates()
    
    def test_invalid_yaml_structure(self, tmp_path):
        """Test error handling for invalid YAML structure."""
        invalid_file = tmp_path / "invalid.yaml"
        with open(invalid_file, 'w') as f:
            yaml.dump({'invalid': 'structure'}, f)
        
        loader = TemplateLoader(invalid_file)
        
        with pytest.raises(ValueError, match="missing 'templates' section"):
            loader.load_templates()
    
    def test_template_metadata_preservation(self, sample_template_file):
        """Test that template metadata is preserved."""
        loader = TemplateLoader(sample_template_file)
        
        template = loader.load_template('executor_success')
        
        assert template.metadata is not None
        assert template.metadata['category'] == 'agent'
        assert template.metadata['agent'] == 'executor'
    
    def test_empty_triggers_handled(self, sample_template_file):
        """Test templates with empty triggers list."""
        loader = TemplateLoader(sample_template_file)
        
        template = loader.load_template('executor_success')
        
        assert template.triggers == []


class TestTemplateDataClass:
    """Tests for Template data class."""
    
    def test_template_creation(self):
        """Test creating a Template instance."""
        template = Template(
            template_id='test_template',
            triggers=['test', 'testing'],
            response_type='narrative',
            context_needed=True,
            content='Test content',
            verbosity='detailed',
            metadata={'key': 'value'}
        )
        
        assert template.template_id == 'test_template'
        assert template.triggers == ['test', 'testing']
        assert template.response_type == 'narrative'
        assert template.context_needed
        assert template.content == 'Test content'
        assert template.verbosity == 'detailed'
        assert template.metadata['key'] == 'value'
    
    def test_template_defaults(self):
        """Test Template default values."""
        template = Template(
            template_id='minimal',
            triggers=[],
            response_type='text',
            context_needed=False,
            content='Minimal content'
        )
        
        assert template.verbosity == 'concise'
        assert template.metadata is None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
