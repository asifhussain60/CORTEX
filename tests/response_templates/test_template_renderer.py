"""Tests for TemplateRenderer.

Tests template rendering with placeholder substitution, verbosity control,
conditionals, loops, and format conversion.
"""

import pytest
from src.response_templates.template_loader import Template
from src.response_templates.template_renderer import TemplateRenderer


@pytest.fixture
def renderer():
    """Create template renderer instance."""
    return TemplateRenderer()


@pytest.fixture
def simple_template():
    """Create a simple template with placeholders."""
    return Template(
        template_id='simple',
        triggers=[],
        response_type='narrative',
        context_needed=True,
        content='Hello {{name}}, you have {{count}} messages.',
        verbosity='concise'
    )


@pytest.fixture
def verbosity_template():
    """Create template with verbosity sections."""
    return Template(
        template_id='verbosity',
        triggers=[],
        response_type='detailed',
        context_needed=False,
        content='''
✅ Success

[concise]
Quick summary
[/concise]

[detailed]
Detailed information
[/detailed]

[expert]
Expert-level details
[/expert]
        '''.strip(),
        verbosity='concise'
    )


@pytest.fixture
def conditional_template():
    """Create template with conditionals."""
    return Template(
        template_id='conditional',
        triggers=[],
        response_type='narrative',
        context_needed=True,
        content='''
Result: Success
{{#if warnings}}
⚠️ Warnings: {{warnings}}
{{/if}}
        '''.strip(),
        verbosity='concise'
    )


@pytest.fixture
def loop_template():
    """Create template with loops."""
    return Template(
        template_id='loop',
        triggers=[],
        response_type='detailed',
        context_needed=True,
        content='''
Files Modified:
{{#files}}
• {{path}}
{{/files}}
        '''.strip(),
        verbosity='concise'
    )


class TestTemplateRenderer:
    """Tests for TemplateRenderer class."""
    
    def test_render_simple_template(self, renderer, simple_template):
        """Test rendering template with basic placeholders."""
        context = {'name': 'Alice', 'count': 5}
        
        result = renderer.render(simple_template, context)
        
        assert 'Hello Alice' in result
        assert '5 messages' in result
    
    def test_render_missing_placeholder(self, renderer, simple_template):
        """Test handling missing placeholder values."""
        context = {'name': 'Bob'}  # Missing 'count'
        
        result = renderer.render(simple_template, context)
        
        assert 'Hello Bob' in result
        assert '{{MISSING: count}}' in result
    
    def test_render_with_none_context(self, renderer, simple_template):
        """Test rendering with None context."""
        result = renderer.render(simple_template, None)
        
        assert '{{MISSING: name}}' in result
        assert '{{MISSING: count}}' in result
    
    def test_render_with_empty_context(self, renderer, simple_template):
        """Test rendering with empty context."""
        result = renderer.render(simple_template, {})
        
        assert '{{MISSING: name}}' in result
        assert '{{MISSING: count}}' in result
    
    def test_render_with_kwargs(self, renderer, simple_template):
        """Test rendering using keyword arguments."""
        result = renderer.render_with_placeholders(
            simple_template,
            name='Charlie',
            count=10
        )
        
        assert 'Hello Charlie' in result
        assert '10 messages' in result
    
    def test_verbosity_concise(self, renderer, verbosity_template):
        """Test concise verbosity filtering."""
        result = renderer.render(verbosity_template, verbosity='concise')
        
        assert 'Quick summary' in result
        assert 'Detailed information' not in result
        assert 'Expert-level details' not in result
    
    def test_verbosity_detailed(self, renderer, verbosity_template):
        """Test detailed verbosity filtering."""
        result = renderer.render(verbosity_template, verbosity='detailed')
        
        assert 'Quick summary' not in result
        assert 'Detailed information' in result
        assert 'Expert-level details' not in result
    
    def test_verbosity_expert(self, renderer, verbosity_template):
        """Test expert verbosity filtering."""
        result = renderer.render(verbosity_template, verbosity='expert')
        
        assert 'Quick summary' not in result
        assert 'Detailed information' not in result
        assert 'Expert-level details' in result
    
    def test_verbosity_invalid_defaults_to_concise(self, renderer, verbosity_template):
        """Test invalid verbosity defaults to concise."""
        result = renderer.render(verbosity_template, verbosity='invalid')
        
        assert 'Quick summary' in result
    
    def test_conditional_with_true_condition(self, renderer, conditional_template):
        """Test conditional rendering when condition is true."""
        context = {'warnings': 'Some warnings occurred'}
        
        result = renderer.render(conditional_template, context)
        
        assert '⚠️ Warnings: Some warnings occurred' in result
    
    def test_conditional_with_false_condition(self, renderer, conditional_template):
        """Test conditional rendering when condition is false."""
        context = {}  # No warnings
        
        result = renderer.render(conditional_template, context)
        
        assert '⚠️ Warnings' not in result
    
    def test_conditional_with_false_value(self, renderer, conditional_template):
        """Test conditional with explicitly false value."""
        context = {'warnings': False}
        
        result = renderer.render(conditional_template, context)
        
        assert '⚠️ Warnings' not in result
    
    def test_loop_rendering(self, renderer, loop_template):
        """Test loop rendering with list of dicts."""
        context = {
            'files': [
                {'path': 'src/auth.py'},
                {'path': 'src/models.py'},
                {'path': 'tests/test_auth.py'}
            ]
        }
        
        result = renderer.render(loop_template, context)
        
        assert '• src/auth.py' in result
        assert '• src/models.py' in result
        assert '• tests/test_auth.py' in result
    
    def test_loop_with_empty_list(self, renderer, loop_template):
        """Test loop rendering with empty list."""
        context = {'files': []}
        
        result = renderer.render(loop_template, context)
        
        assert 'Files Modified:' in result
        # Loop should produce no output
    
    def test_loop_with_missing_list(self, renderer, loop_template):
        """Test loop rendering with missing list."""
        context = {}
        
        result = renderer.render(loop_template, context)
        
        assert 'Files Modified:' in result
        # Loop should produce no output
    
    def test_convert_format_json(self, renderer):
        """Test converting content to JSON format."""
        content = "Test message"
        
        result = renderer.convert_format(content, 'json')
        
        assert '{"response":' in result
        assert 'Test message' in result
    
    def test_convert_format_text(self, renderer):
        """Test converting markdown to plain text."""
        content = "**Bold** and *italic* and `code`"
        
        result = renderer.convert_format(content, 'text')
        
        assert '**' not in result
        assert '*' not in result
        assert '`' not in result
        assert 'Bold' in result
        assert 'italic' in result
        assert 'code' in result
    
    def test_convert_format_markdown(self, renderer):
        """Test markdown format (default, no conversion)."""
        content = "**Bold** text"
        
        result = renderer.convert_format(content, 'markdown')
        
        assert result == content
    
    def test_complex_template_with_all_features(self, renderer):
        """Test template with placeholders, conditionals, loops, and verbosity."""
        template = Template(
            template_id='complex',
            triggers=[],
            response_type='detailed',
            context_needed=True,
            content='''
✅ **{{operation_name}}** Complete

[concise]
Quick: {{summary}}
[/concise]

[detailed]
Files Modified: {{files_count}}
{{#files}}
• {{name}}: {{changes}} changes
{{/files}}

{{#if warnings}}
⚠️ Warnings: {{warnings}}
{{/if}}
[/detailed]
            '''.strip(),
            verbosity='detailed'
        )
        
        context = {
            'operation_name': 'Setup',
            'summary': 'Environment configured',
            'files_count': 2,
            'files': [
                {'name': 'config.py', 'changes': 3},
                {'name': 'setup.py', 'changes': 5}
            ],
            'warnings': 'Deprecated packages detected'
        }
        
        result = renderer.render(template, context, verbosity='detailed')
        
        assert '✅ **Setup** Complete' in result
        assert 'Quick:' not in result  # Should be filtered by verbosity
        assert 'Files Modified: 2' in result
        assert '• config.py: 3 changes' in result
        assert '• setup.py: 5 changes' in result
        assert '⚠️ Warnings: Deprecated packages detected' in result
    
    def test_apply_verbosity_removes_other_sections(self, renderer):
        """Test that verbosity filtering removes other verbosity sections."""
        content = '''
        [concise]Section A[/concise]
        [detailed]Section B[/detailed]
        [expert]Section C[/expert]
        '''
        
        result = renderer.apply_verbosity(content, 'detailed')
        
        assert 'Section A' not in result
        assert 'Section B' in result
        assert 'Section C' not in result
        assert '[detailed]' not in result
        assert '[/detailed]' not in result
    
    def test_placeholder_substitution_with_nested_dict(self, renderer, simple_template):
        """Test placeholder substitution with nested dictionary values."""
        context = {
            'name': 'Dave',
            'count': 3,
            'extra': {'key': 'value'}
        }
        
        result = renderer.render(simple_template, context)
        
        assert 'Hello Dave' in result
        assert '3 messages' in result
    
    def test_render_strips_whitespace(self, renderer, simple_template):
        """Test that rendered output is stripped of leading/trailing whitespace."""
        context = {'name': 'Eve', 'count': 1}
        
        result = renderer.render(simple_template, context)
        
        assert not result.startswith(' ')
        assert not result.startswith('\n')
        assert not result.endswith(' ')
        assert not result.endswith('\n')


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
