"""Integration tests for CORTEX Response Template System.

Tests the complete template system working together:
- TemplateLoader + TemplateRenderer + TemplateRegistry
- ResponseFormatter integration
- End-to-end workflows
"""

import pytest
from pathlib import Path
import tempfile
import yaml
import time

from src.response_templates import TemplateLoader, TemplateRenderer, TemplateRegistry
from src.entry_point.response_formatter import ResponseFormatter
from src.cortex_agents.base_agent import AgentResponse


@pytest.fixture
def full_template_file(tmp_path):
    """Create comprehensive template file for integration testing."""
    template_data = {
        'templates': {
            'help_table': {
                'triggers': ['help', '/help'],
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
                'content': '✅ **Feature Implemented**\nFiles Modified: {{files_count}}\n{{#files}}\n• {{path}}\n{{/files}}\nNext: {{next_action}}',
                'metadata': {'category': 'agent', 'agent': 'executor'}
            },
            'operation_complete': {
                'triggers': [],
                'response_type': 'detailed',
                'context_needed': True,
                'verbosity': 'concise',
                'content': '✅ **{{operation_name}}** - Complete\nDuration: {{duration_seconds}}s\nModules: {{succeeded}}/{{total}} succeeded',
                'metadata': {'category': 'operation'}
            },
            'missing_dependency': {
                'triggers': [],
                'response_type': 'detailed',
                'context_needed': True,
                'verbosity': 'concise',
                'content': '❌ **Missing Dependency**\nPackage: {{package_name}}\nRequired by: {{required_by}}\nFix: pip install {{package_name}}',
                'metadata': {'category': 'error'}
            }
        }
    }
    
    template_file = tmp_path / "integration-templates.yaml"
    with open(template_file, 'w') as f:
        yaml.dump(template_data, f)
    
    return template_file


class TestTemplateSystemIntegration:
    """Integration tests for complete template system."""
    
    def test_loader_renderer_pipeline(self, full_template_file):
        """Test loading and rendering pipeline."""
        loader = TemplateLoader(full_template_file)
        renderer = TemplateRenderer()
        
        # Load template
        template = loader.load_template('executor_success')
        assert template is not None
        
        # Render with context
        context = {
            'files_count': 3,
            'files': [
                {'path': 'src/auth.py'},
                {'path': 'src/models.py'},
                {'path': 'tests/test_auth.py'}
            ],
            'next_action': 'Run tests'
        }
        
        result = renderer.render(template, context)
        
        assert '✅ **Feature Implemented**' in result
        assert 'Files Modified: 3' in result
        assert '• src/auth.py' in result
        assert 'Next: Run tests' in result
    
    def test_loader_registry_integration(self, full_template_file):
        """Test loader populating registry."""
        loader = TemplateLoader(full_template_file)
        registry = TemplateRegistry()
        
        # Load and register all templates
        loader.load_templates()
        for template in loader.list_templates():
            registry.register_template(template)
        
        # Verify registry contents
        assert registry.get_template_count() == 4
        assert registry.get_template('help_table') is not None
        assert registry.get_template('executor_success') is not None
        
        # Test category filtering
        system_templates = registry.list_templates(category='system')
        assert len(system_templates) == 1
        
        agent_templates = registry.list_templates(category='agent')
        assert len(agent_templates) == 1
    
    def test_trigger_to_rendered_output(self, full_template_file):
        """Test complete flow from trigger to rendered output."""
        loader = TemplateLoader(full_template_file)
        renderer = TemplateRenderer()
        
        # Find template by trigger
        template = loader.find_by_trigger('help')
        assert template is not None
        
        # Render (no context needed)
        result = renderer.render(template)
        
        assert '**CORTEX Commands**' in result
        assert '• setup' in result
        assert '• cleanup' in result
    
    def test_response_formatter_template_integration(self, full_template_file):
        """Test ResponseFormatter with template system."""
        formatter = ResponseFormatter(
            default_verbosity='concise',
            template_file=full_template_file
        )
        
        # Verify template system loaded
        assert formatter.template_loader is not None
        assert formatter.template_renderer is not None
        assert formatter.template_registry is not None
        
        # Format using template
        result = formatter.format_from_template(
            'executor_success',
            context={
                'files_count': 2,
                'files': [
                    {'path': 'src/api.py'},
                    {'path': 'tests/test_api.py'}
                ],
                'next_action': 'Review changes'
            }
        )
        
        assert '✅ **Feature Implemented**' in result
        assert 'Files Modified: 2' in result
        assert '• src/api.py' in result
        assert 'Next: Review changes' in result
    
    def test_response_formatter_trigger_lookup(self, full_template_file):
        """Test ResponseFormatter finding template by trigger."""
        formatter = ResponseFormatter(
            default_verbosity='concise',
            template_file=full_template_file
        )
        
        result = formatter.format_from_trigger('help')
        
        assert '**CORTEX Commands**' in result
    
    def test_response_formatter_fallback_when_no_templates(self):
        """Test ResponseFormatter falls back gracefully when templates unavailable."""
        formatter = ResponseFormatter(
            default_verbosity='concise',
            template_file=Path('/nonexistent/templates.yaml')
        )
        
        # Should fallback to code-based formatting
        result = formatter.format_from_template(
            'test_template',
            context={'key': 'value'}
        )
        
        assert 'Template system unavailable' in result or 'test_template' in result
    
    def test_plugin_template_registration(self, full_template_file):
        """Test registering plugin templates through ResponseFormatter."""
        from src.response_templates.template_loader import Template
        
        formatter = ResponseFormatter(
            default_verbosity='concise',
            template_file=full_template_file
        )
        
        # Create plugin templates
        plugin_templates = [
            Template(
                template_id='my_plugin_success',
                triggers=[],
                response_type='narrative',
                context_needed=True,
                content='✅ Plugin {{plugin_name}} executed successfully',
                verbosity='concise'
            )
        ]
        
        # Register plugin templates
        formatter.register_plugin_templates('my_plugin', plugin_templates)
        
        # Verify registration - check registry directly
        registered_template = formatter.template_registry.get_template('my_plugin_success')
        assert registered_template is not None
        assert registered_template.template_id == 'my_plugin_success'
    
    def test_list_available_templates(self, full_template_file):
        """Test listing all available templates."""
        formatter = ResponseFormatter(
            default_verbosity='concise',
            template_file=full_template_file
        )
        
        templates = formatter.list_available_templates()
        
        assert len(templates) == 4
        assert 'help_table' in templates
        assert 'executor_success' in templates
        assert 'operation_complete' in templates
        assert 'missing_dependency' in templates
    
    def test_list_templates_by_category(self, full_template_file):
        """Test listing templates filtered by category."""
        formatter = ResponseFormatter(
            default_verbosity='concise',
            template_file=full_template_file
        )
        
        system_templates = formatter.list_available_templates(category='system')
        
        assert len(system_templates) == 1
        assert 'help_table' in system_templates


class TestPerformance:
    """Performance tests for template system."""
    
    def test_template_load_performance(self, full_template_file):
        """Test that template loading is fast (<10ms)."""
        loader = TemplateLoader(full_template_file)
        
        start_time = time.perf_counter()
        loader.load_templates()
        elapsed = (time.perf_counter() - start_time) * 1000  # Convert to ms
        
        assert elapsed < 10, f"Template loading took {elapsed:.2f}ms (target: <10ms)"
    
    def test_template_render_performance(self, full_template_file):
        """Test that template rendering is fast (<5ms)."""
        loader = TemplateLoader(full_template_file)
        renderer = TemplateRenderer()
        
        template = loader.load_template('executor_success')
        context = {
            'files_count': 5,
            'files': [{'path': f'file{i}.py'} for i in range(5)],
            'next_action': 'Test'
        }
        
        start_time = time.perf_counter()
        result = renderer.render(template, context)
        elapsed = (time.perf_counter() - start_time) * 1000
        
        assert elapsed < 5, f"Template rendering took {elapsed:.2f}ms (target: <5ms)"
        assert result  # Ensure it actually rendered
    
    def test_trigger_lookup_performance(self, full_template_file):
        """Test that trigger lookup is fast."""
        loader = TemplateLoader(full_template_file)
        
        start_time = time.perf_counter()
        template = loader.find_by_trigger('help')
        elapsed = (time.perf_counter() - start_time) * 1000
        
        assert elapsed < 2, f"Trigger lookup took {elapsed:.2f}ms (target: <2ms)"
        assert template is not None
    
    def test_end_to_end_performance(self, full_template_file):
        """Test complete pipeline performance."""
        formatter = ResponseFormatter(
            default_verbosity='concise',
            template_file=full_template_file
        )
        
        context = {
            'operation_name': 'Setup',
            'duration_seconds': 12,
            'succeeded': 8,
            'total': 10
        }
        
        start_time = time.perf_counter()
        result = formatter.format_from_template('operation_complete', context)
        elapsed = (time.perf_counter() - start_time) * 1000
        
        assert elapsed < 15, f"End-to-end took {elapsed:.2f}ms (target: <15ms)"
        assert '✅ **Setup** - Complete' in result


class TestRealWorldScenarios:
    """Real-world usage scenario tests."""
    
    def test_help_command_workflow(self, full_template_file):
        """Test typical help command workflow."""
        formatter = ResponseFormatter(
            default_verbosity='concise',
            template_file=full_template_file
        )
        
        # User types "help"
        result = formatter.format_from_trigger('help')
        
        # Should return instant response with zero execution
        assert result
        assert '**CORTEX Commands**' in result
        assert '• setup' in result
    
    def test_agent_success_workflow(self, full_template_file):
        """Test agent success reporting workflow."""
        formatter = ResponseFormatter(
            default_verbosity='concise',
            template_file=full_template_file
        )
        
        # Agent completes task
        result = formatter.format_from_template(
            'executor_success',
            context={
                'files_count': 1,
                'files': [{'path': 'src/feature.py'}],
                'next_action': 'Write tests'
            }
        )
        
        assert '✅' in result
        assert 'src/feature.py' in result
        assert 'Write tests' in result
    
    def test_error_reporting_workflow(self, full_template_file):
        """Test error reporting workflow."""
        formatter = ResponseFormatter(
            default_verbosity='concise',
            template_file=full_template_file
        )
        
        # Error occurs
        result = formatter.format_from_template(
            'missing_dependency',
            context={
                'package_name': 'requests',
                'required_by': 'api_client.py'
            }
        )
        
        assert '❌' in result
        assert 'Missing Dependency' in result
        assert 'requests' in result
        assert 'pip install requests' in result


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
