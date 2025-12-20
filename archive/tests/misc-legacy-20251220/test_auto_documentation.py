"""
Tests for Automatic Documentation Generator.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
from pathlib import Path
from datetime import datetime

from src.operations.modules.documentation.auto_documentation_generator import (
    AutoDocumentationGenerator,
    DocumentationSet
)


@pytest.fixture
def tmp_project(tmp_path):
    """Create temporary project structure."""
    learning_base = tmp_path / "cortex-brain" / "learning"
    learning_base.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def generator(tmp_project):
    """Create documentation generator."""
    return AutoDocumentationGenerator(project_root=tmp_project)


@pytest.fixture
def sample_context():
    """Sample component context."""
    return {
        'version': '1.0.0',
        'description': 'Test component for documentation generation',
        'features': [
            'Feature 1: Basic functionality',
            'Feature 2: Advanced operations',
            'Feature 3: Integration support'
        ],
        'dependencies': ['pytest', 'pathlib', 'typing'],
        'usage_example': 'generator = TestComponent()\nresult = generator.execute()',
        'problem_statement': 'Need automated documentation for learning library',
        'functional_requirements': [
            'Generate 6 document types',
            'Enforce folder structure',
            'Support templates'
        ],
        'non_functional_requirements': [
            '100% test coverage',
            'Maintainable code',
            'Clear documentation'
        ],
        'use_cases': [
            'Tier 3 operation documentation',
            'Tier 4 complex plan documentation',
            'Learning library management'
        ],
        'success_criteria': [
            'All 6 docs generated',
            'Consistent formatting',
            'Integration with Planning Orchestrator 3.0'
        ],
        'architecture_overview': 'Template-based generation with validation',
        'component_structure': 'Single generator class with 6 document methods',
        'data_flow': 'Context → Templates → Files',
        'key_interfaces': ['generate_documentation()', 'validate_structure()'],
        'integration_points': ['Planning Orchestrator', 'Learning Library'],
        'design_decisions': ['Template-based approach', 'Dataclass for output'],
        'implementation_overview': 'Template rendering with context substitution',
        'core_components': ['AutoDocumentationGenerator', 'DocumentationSet'],
        'key_algorithms': 'Template string formatting',
        'error_handling': 'Logger-based warnings and errors',
        'performance_considerations': 'File I/O is main bottleneck',
        'extension_points': ['Custom templates', 'Additional document types'],
        'test_overview': 'Comprehensive unit and integration tests',
        'test_coverage': '100% line coverage target',
        'unit_tests': ['Template rendering', 'File creation', 'Validation'],
        'integration_tests': ['End-to-end generation', 'Structure validation'],
        'test_data': 'Sample contexts and expected outputs',
        'continuous_testing': 'pytest with coverage reporting',
        'research_summary': 'Explored template engines, chose simple string formatting',
        'alternative_approaches': ['Jinja2 templates', 'Custom DSL'],
        'trade_offs': ['Simplicity vs flexibility'],
        'lessons_learned': ['Keep templates simple', 'Validate early'],
        'future_enhancements': ['Custom templates', 'Rich media support'],
        'references': ['Python docs', 'CORTEX design principles']
    }


class TestAutoDocumentationGenerator:
    """Test suite for AutoDocumentationGenerator."""
    
    def test_initialization(self, generator):
        """Test generator initialization."""
        assert generator.project_root is not None
        assert generator.learning_base.name == 'learning'
        assert len(generator.categories) == 5
        assert 'orchestration' in generator.categories
        assert len(generator.templates) == 6
        
    def test_template_initialization(self, generator):
        """Test template loading."""
        assert 'readme' in generator.templates
        assert 'context' in generator.templates
        assert 'architecture' in generator.templates
        assert 'implementation_guide' in generator.templates
        assert 'test_strategy' in generator.templates
        assert 'research_notes' in generator.templates
        
    def test_generate_documentation(self, generator, sample_context):
        """Test complete documentation generation."""
        docs = generator.generate_documentation(
            'test_component',
            'orchestration',
            sample_context
        )
        
        assert isinstance(docs, DocumentationSet)
        assert docs.readme
        assert docs.context
        assert docs.architecture
        assert docs.implementation_guide
        assert docs.test_strategy
        assert docs.research_notes
        
    def test_generate_readme(self, generator, sample_context):
        """Test README generation."""
        readme = generator._generate_readme('test_component', 'orchestration', sample_context)
        
        assert 'Test Component' in readme
        assert 'test_component' in readme
        assert '1.0.0' in readme
        assert 'orchestration' in readme
        assert sample_context['description'] in readme
        assert 'Feature 1' in readme
        
    def test_generate_context(self, generator, sample_context):
        """Test context.md generation."""
        context_doc = generator._generate_context('test_component', sample_context)
        
        assert 'Test Component' in context_doc
        assert sample_context['problem_statement'] in context_doc
        assert 'Generate 6 document types' in context_doc
        assert '100% test coverage' in context_doc
        
    def test_generate_architecture(self, generator, sample_context):
        """Test architecture.md generation."""
        arch_doc = generator._generate_architecture('test_component', sample_context)
        
        assert 'Test Component' in arch_doc
        assert sample_context['architecture_overview'] in arch_doc
        assert sample_context['component_structure'] in arch_doc
        assert sample_context['data_flow'] in arch_doc
        
    def test_generate_implementation_guide(self, generator, sample_context):
        """Test implementation-guide.md generation."""
        impl_doc = generator._generate_implementation_guide('test_component', sample_context)
        
        assert 'Test Component' in impl_doc
        assert sample_context['implementation_overview'] in impl_doc
        assert 'AutoDocumentationGenerator' in impl_doc
        
    def test_generate_test_strategy(self, generator, sample_context):
        """Test test-strategy.md generation."""
        test_doc = generator._generate_test_strategy('test_component', sample_context)
        
        assert 'Test Component' in test_doc
        assert sample_context['test_overview'] in test_doc
        assert '100% line coverage' in test_doc
        
    def test_generate_research_notes(self, generator, sample_context):
        """Test research-notes.md generation."""
        research_doc = generator._generate_research_notes('test_component', sample_context)
        
        assert 'Test Component' in research_doc
        assert sample_context['research_summary'] in research_doc
        assert 'Jinja2 templates' in research_doc
        
    def test_file_writing(self, generator, sample_context):
        """Test documentation file writing."""
        generator.generate_documentation(
            'test_component',
            'orchestration',
            sample_context
        )
        
        component_path = generator.learning_base / 'orchestration' / 'test_component'
        
        assert component_path.exists()
        assert (component_path / 'README.md').exists()
        assert (component_path / 'context.md').exists()
        assert (component_path / 'architecture.md').exists()
        assert (component_path / 'implementation-guide.md').exists()
        assert (component_path / 'test-strategy.md').exists()
        assert (component_path / 'research-notes.md').exists()
        
    def test_category_validation(self, generator, sample_context):
        """Test category validation with invalid category."""
        docs = generator.generate_documentation(
            'test_component',
            'invalid_category',
            sample_context
        )
        
        # Should default to orchestration
        assert isinstance(docs, DocumentationSet)
        component_path = generator.learning_base / 'orchestration' / 'test_component'
        assert component_path.exists()
        
    def test_validate_structure(self, generator):
        """Test learning library structure validation."""
        result = generator.validate_structure()
        
        assert result is True
        assert generator.learning_base.exists()
        
        # Check all categories exist
        for category in generator.categories:
            category_path = generator.learning_base / category
            assert category_path.exists()
            
    def test_list_documented_components(self, generator, sample_context):
        """Test listing documented components."""
        # Generate some documentation
        generator.generate_documentation('component1', 'orchestration', sample_context)
        generator.generate_documentation('component2', 'routing', sample_context)
        
        # List all components
        components = generator.list_documented_components()
        
        assert len(components) >= 2
        assert any(c['name'] == 'component1' for c in components)
        assert any(c['name'] == 'component2' for c in components)
        
    def test_list_documented_components_by_category(self, generator, sample_context):
        """Test listing components by category."""
        generator.generate_documentation('component1', 'orchestration', sample_context)
        generator.generate_documentation('component2', 'routing', sample_context)
        
        # List orchestration components only
        orchestration_comps = generator.list_documented_components('orchestration')
        
        assert len(orchestration_comps) >= 1
        assert all(c['category'] == 'orchestration' for c in orchestration_comps)
        
    def test_format_features(self, generator):
        """Test feature list formatting."""
        features = ['Feature 1', 'Feature 2', 'Feature 3']
        formatted = generator._format_features(features)
        
        assert '- Feature 1' in formatted
        assert '- Feature 2' in formatted
        assert '- Feature 3' in formatted
        
    def test_format_features_empty(self, generator):
        """Test empty feature list formatting."""
        formatted = generator._format_features([])
        
        assert 'No features specified' in formatted
        
    def test_format_dependencies(self, generator):
        """Test dependency list formatting."""
        deps = ['pytest', 'pathlib', 'typing']
        formatted = generator._format_dependencies(deps)
        
        assert '`pytest`' in formatted
        assert '`pathlib`' in formatted
        assert '`typing`' in formatted
        
    def test_format_dependencies_empty(self, generator):
        """Test empty dependency list formatting."""
        formatted = generator._format_dependencies([])
        
        assert 'No external dependencies' in formatted
        
    def test_format_list(self, generator):
        """Test generic list formatting."""
        items = ['Item 1', 'Item 2', 'Item 3']
        formatted = generator._format_list(items)
        
        assert '- Item 1' in formatted
        assert '- Item 2' in formatted
        assert '- Item 3' in formatted
        
    def test_format_list_empty(self, generator):
        """Test empty list formatting."""
        formatted = generator._format_list([])
        
        assert 'None specified' in formatted
        
    def test_generate_quickstart(self, generator):
        """Test quickstart generation."""
        context = {
            'quickstart_steps': [
                'Step 1: Install',
                'Step 2: Configure',
                'Step 3: Run'
            ]
        }
        
        quickstart = generator._generate_quickstart(context)
        
        assert '1. Step 1: Install' in quickstart
        assert '2. Step 2: Configure' in quickstart
        assert '3. Step 3: Run' in quickstart
        
    def test_generate_quickstart_default(self, generator):
        """Test quickstart generation with defaults."""
        quickstart = generator._generate_quickstart({})
        
        assert '1. Install dependencies' in quickstart
        assert '2. Import the module' in quickstart
        assert '3. Initialize the component' in quickstart
        assert '4. Execute core functionality' in quickstart
        
    def test_minimal_context(self, generator):
        """Test documentation generation with minimal context."""
        minimal_context = {
            'version': '1.0.0',
            'description': 'Minimal component'
        }
        
        docs = generator.generate_documentation(
            'minimal_component',
            'orchestration',
            minimal_context
        )
        
        assert isinstance(docs, DocumentationSet)
        assert 'Minimal component' in docs.readme
        assert 'No problem statement provided' in docs.context
        
    def test_multiple_components_same_category(self, generator, sample_context):
        """Test generating documentation for multiple components in same category."""
        generator.generate_documentation('component1', 'orchestration', sample_context)
        generator.generate_documentation('component2', 'orchestration', sample_context)
        
        components = generator.list_documented_components('orchestration')
        
        assert len(components) >= 2
        component_names = [c['name'] for c in components]
        assert 'component1' in component_names
        assert 'component2' in component_names
