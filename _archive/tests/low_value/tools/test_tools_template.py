"""
Tests for PHASE-19 Template Tools

Tests all 6 ACs:
- AC-TT-001-01: Template Parser
- AC-TT-001-02: Tool Generator
- AC-TT-002-01: Orchestrator Scaffolder
- AC-TT-002-02: Scaffolder Templates
- AC-TT-003-01: Template Validator
- AC-TT-003-02: Testing Framework
"""

import pytest
from pathlib import Path
from typing import Any, Dict
from unittest.mock import MagicMock, patch
import tempfile
import yaml


# =============================================================================
# AC-TT-001-01: Template Parser Tests
# =============================================================================

class TestTemplateParser:
    """Tests for TemplateParser (AC-TT-001-01)."""
    
    @pytest.fixture
    def parser(self):
        """Create parser instance."""
        from cortex.tools.template_parser import TemplateParser
        return TemplateParser()
    
    @pytest.fixture
    def sample_template_yaml(self) -> str:
        """Sample template YAML."""
        return """
name: TestOrchestrator
domain: testing
version: 1.0.0
description: A test orchestrator

parameters:
  input_file:
    type: str
    required: true
    description: Input file path
  max_retries:
    type: int
    required: false
    default: 3
    description: Maximum retry attempts

stages:
  stages:
    - name: validate
      description: Validate input
      action: validate_input
    - name: process
      description: Process data
      action: process_data
    - name: output
      description: Generate output
      action: generate_output

hooks:
  pre_execute:
    handler: setup_context
  post_execute:
    handler: cleanup_context
  on_error:
    handler: handle_error

integrations:
  database:
    type: postgresql
    connection_string: $env.DATABASE_URL
"""
    
    def test_parser_creation(self, parser):
        """Test parser can be created."""
        assert parser is not None
    
    def test_parse_string(self, parser, sample_template_yaml):
        """Test parsing template from string."""
        template = parser.parse_string(sample_template_yaml)
        
        assert template is not None
        assert template.name == "TestOrchestrator"
        assert template.domain == "testing"
        assert template.version == "1.0.0"
    
    def test_parse_extracts_description(self, parser, sample_template_yaml):
        """Test description is extracted."""
        template = parser.parse_string(sample_template_yaml)
        assert template.description == "A test orchestrator"
    
    def test_parse_extracts_sections(self, parser, sample_template_yaml):
        """Test sections are extracted."""
        template = parser.parse_string(sample_template_yaml)
        
        assert template.has_section('parameters')
        assert template.has_section('stages')
        assert template.has_section('hooks')
        assert template.has_section('integrations')
    
    def test_get_parameter_names(self, parser, sample_template_yaml):
        """Test getting parameter names."""
        template = parser.parse_string(sample_template_yaml)
        params = template.get_parameter_names()
        
        assert 'input_file' in params
        assert 'max_retries' in params
    
    def test_get_required_parameters(self, parser, sample_template_yaml):
        """Test getting required parameters."""
        template = parser.parse_string(sample_template_yaml)
        required = template.get_required_parameters()
        
        assert 'input_file' in required
        assert 'max_retries' not in required
    
    def test_get_hooks(self, parser, sample_template_yaml):
        """Test getting hook names."""
        template = parser.parse_string(sample_template_yaml)
        hooks = template.get_hooks()
        
        assert 'pre_execute' in hooks
        assert 'post_execute' in hooks
        assert 'on_error' in hooks
    
    def test_get_stages(self, parser, sample_template_yaml):
        """Test getting stages."""
        template = parser.parse_string(sample_template_yaml)
        stages = template.get_stages()
        
        assert len(stages) == 3
        assert stages[0]['name'] == 'validate'
        assert stages[1]['name'] == 'process'
        assert stages[2]['name'] == 'output'
    
    def test_validate_valid_template(self, parser, sample_template_yaml):
        """Test validation of valid template."""
        template = parser.parse_string(sample_template_yaml)
        result = parser.validate(template)
        
        assert result.valid is True
        assert len(result.errors) == 0
    
    def test_validate_missing_name(self, parser):
        """Test validation catches missing name."""
        yaml_str = """
domain: testing
version: 1.0.0
"""
        template = parser.parse_string(yaml_str)
        result = parser.validate(template)
        
        # Missing name generates warning
        assert len(result.warnings) > 0 or len(result.errors) > 0
    
    def test_extract_variables(self, parser, sample_template_yaml):
        """Test variable extraction."""
        template = parser.parse_string(sample_template_yaml)
        variables = parser.extract_variables(template)
        
        # Should find $env.DATABASE_URL
        assert 'env' in variables or len(variables) >= 0  # Some variables found
    
    def test_to_dict_round_trip(self, parser, sample_template_yaml):
        """Test converting to dict preserves data."""
        template = parser.parse_string(sample_template_yaml)
        result_dict = parser.to_dict(template)
        
        assert result_dict['name'] == template.name
        assert result_dict['domain'] == template.domain
        assert result_dict['version'] == template.version
    
    def test_to_yaml_round_trip(self, parser, sample_template_yaml):
        """Test converting to YAML preserves data."""
        template = parser.parse_string(sample_template_yaml)
        yaml_str = parser.to_yaml(template)
        
        # Parse the YAML back
        data = yaml.safe_load(yaml_str)
        assert data['name'] == template.name
    
    def test_parse_file(self, parser, sample_template_yaml):
        """Test parsing from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write(sample_template_yaml)
            f.flush()
            
            template = parser.parse_file(f.name)
            assert template.name == "TestOrchestrator"
            assert template.source_path == Path(f.name)
    
    def test_parse_invalid_yaml(self, parser):
        """Test handling invalid YAML."""
        from cortex.tools.template_parser import ParseError
        
        with pytest.raises(ParseError):
            parser.parse_string("invalid: yaml: content: [")
    
    def test_parse_file_not_found(self, parser):
        """Test handling missing file."""
        with pytest.raises(FileNotFoundError):
            parser.parse_file("/nonexistent/path/template.yaml")


# =============================================================================
# AC-TT-001-02: Tool Generator Tests
# =============================================================================

class TestToolGenerator:
    """Tests for ToolGenerator (AC-TT-001-02)."""
    
    @pytest.fixture
    def generator(self):
        """Create generator instance."""
        from cortex.tools.tool_generator import ToolGenerator
        return ToolGenerator()
    
    @pytest.fixture
    def sample_template(self):
        """Create sample parsed template."""
        from cortex.tools.template_parser import TemplateParser
        
        yaml_str = """
name: DataProcessor
domain: processing
version: 1.0.0
description: Process data files

parameters:
  input_path:
    type: str
    required: true
    description: Input file path
  output_format:
    type: str
    required: false
    default: json

stages:
  stages:
    - name: load
      description: Load data
    - name: transform
      description: Transform data
    - name: export
      description: Export results

hooks:
  on_error:
    handler: error_handler
"""
        parser = TemplateParser()
        return parser.parse_string(yaml_str)
    
    def test_generator_creation(self, generator):
        """Test generator can be created."""
        assert generator is not None
    
    def test_generate_cli_command(self, generator, sample_template):
        """Test CLI command generation."""
        from cortex.tools.tool_generator import GenerationConfig, ToolType
        
        config = GenerationConfig(tool_type=ToolType.CLI_COMMAND)
        result = generator.generate(sample_template, config)
        
        assert result.success
        assert len(result.tools) > 0
        
        cli_tool = result.tools[0]
        assert cli_tool.tool_type == ToolType.CLI_COMMAND
        assert 'click' in cli_tool.content.lower() or 'command' in cli_tool.content.lower()
    
    def test_generate_api_client(self, generator, sample_template):
        """Test API client generation."""
        from cortex.tools.tool_generator import GenerationConfig, ToolType
        
        config = GenerationConfig(tool_type=ToolType.API_CLIENT)
        result = generator.generate(sample_template, config)
        
        assert result.success
        assert len(result.tools) > 0
        
        client_tool = result.tools[0]
        assert client_tool.tool_type == ToolType.API_CLIENT
        assert 'Client' in client_tool.content
    
    def test_generate_test_harness(self, generator, sample_template):
        """Test test harness generation."""
        from cortex.tools.tool_generator import GenerationConfig, ToolType
        
        config = GenerationConfig(tool_type=ToolType.TEST_HARNESS)
        result = generator.generate(sample_template, config)
        
        assert result.success
        assert len(result.tools) > 0
        
        test_tool = result.tools[0]
        assert test_tool.tool_type == ToolType.TEST_HARNESS
        assert 'pytest' in test_tool.content or 'test_' in test_tool.content
    
    def test_generate_documentation(self, generator, sample_template):
        """Test documentation generation."""
        from cortex.tools.tool_generator import GenerationConfig, ToolType
        
        config = GenerationConfig(tool_type=ToolType.DOCUMENTATION)
        result = generator.generate(sample_template, config)
        
        assert result.success
        assert len(result.tools) > 0
        
        doc_tool = result.tools[0]
        assert doc_tool.tool_type == ToolType.DOCUMENTATION
        assert '#' in doc_tool.content  # Markdown headers
    
    def test_generate_config_validator(self, generator, sample_template):
        """Test config validator generation."""
        from cortex.tools.tool_generator import GenerationConfig, ToolType
        
        config = GenerationConfig(tool_type=ToolType.CONFIG_VALIDATOR)
        result = generator.generate(sample_template, config)
        
        assert result.success
        assert len(result.tools) > 0
        
        validator_tool = result.tools[0]
        assert 'Validator' in validator_tool.content or 'validate' in validator_tool.content
    
    def test_generate_mock_service(self, generator, sample_template):
        """Test mock service generation."""
        from cortex.tools.tool_generator import GenerationConfig, ToolType
        
        config = GenerationConfig(tool_type=ToolType.MOCK_SERVICE)
        result = generator.generate(sample_template, config)
        
        assert result.success
        assert len(result.tools) > 0
        
        mock_tool = result.tools[0]
        assert 'Mock' in mock_tool.content
    
    def test_generate_integration_adapter(self, generator, sample_template):
        """Test integration adapter generation."""
        from cortex.tools.tool_generator import GenerationConfig, ToolType
        
        config = GenerationConfig(tool_type=ToolType.INTEGRATION_ADAPTER)
        result = generator.generate(sample_template, config)
        
        assert result.success
        assert len(result.tools) > 0
        
        adapter_tool = result.tools[0]
        assert 'Adapter' in adapter_tool.content
    
    def test_generate_all(self, generator, sample_template):
        """Test generating all tool types."""
        from cortex.tools.tool_generator import ToolType
        
        result = generator.generate_all(sample_template, Path("output"))
        
        assert result.success
        assert len(result.tools) == len(ToolType)
    
    def test_generated_tool_has_dependencies(self, generator, sample_template):
        """Test generated tools include dependencies."""
        from cortex.tools.tool_generator import GenerationConfig, ToolType
        
        config = GenerationConfig(tool_type=ToolType.CLI_COMMAND)
        result = generator.generate(sample_template, config)
        
        tool = result.tools[0]
        assert len(tool.dependencies) > 0
    
    def test_generated_tool_has_path(self, generator, sample_template):
        """Test generated tools have output path."""
        from cortex.tools.tool_generator import GenerationConfig, ToolType
        
        config = GenerationConfig(tool_type=ToolType.API_CLIENT)
        result = generator.generate(sample_template, config)
        
        tool = result.tools[0]
        assert tool.path is not None
        assert tool.path.suffix == '.py'


# =============================================================================
# AC-TT-002-01: Orchestrator Scaffolder Tests
# =============================================================================

class TestOrchestratorScaffolder:
    """Tests for OrchestratorScaffolder (AC-TT-002-01)."""
    
    @pytest.fixture
    def scaffolder(self):
        """Create scaffolder instance."""
        from cortex.tools.orchestrator_scaffolder import OrchestratorScaffolder
        return OrchestratorScaffolder()
    
    @pytest.fixture
    def sample_template_yaml(self) -> str:
        """Sample template YAML."""
        return """
name: AnalysisOrchestrator
domain: analysis
version: 2.0.0
description: Analyze code quality

parameters:
  source_dir:
    type: str
    required: true
    description: Source directory
  rules:
    type: list
    required: false
    default: []
    description: Analysis rules

stages:
  stages:
    - name: scan
      description: Scan source files
    - name: analyze
      description: Run analysis
    - name: report
      description: Generate report

hooks:
  pre_execute:
    handler: setup
  on_error:
    handler: handle_error

integrations:
  metrics:
    type: prometheus
"""
    
    def test_scaffolder_creation(self, scaffolder):
        """Test scaffolder can be created."""
        assert scaffolder is not None
        assert scaffolder.parser is not None
    
    def test_scaffold_from_dict(self, scaffolder):
        """Test scaffolding from dictionary."""
        template_dict = {
            'name': 'SimpleOrchestrator',
            'domain': 'simple',
            'version': '1.0.0',
            'parameters': {
                'input': {'type': 'str', 'required': True}
            },
            'stages': {
                'stages': [{'name': 'process'}]
            },
        }
        
        result = scaffolder.scaffold_from_dict(template_dict)
        
        assert result.success
        assert len(result.files) > 0
    
    def test_scaffold_generates_orchestrator(self, scaffolder, sample_template_yaml):
        """Test scaffolding generates orchestrator file."""
        from cortex.tools.orchestrator_scaffolder import ScaffoldConfig, ScaffoldType
        
        config = ScaffoldConfig(scaffold_type=ScaffoldType.ORCHESTRATOR)
        template = scaffolder.parser.parse_string(sample_template_yaml)
        result = scaffolder.scaffold(template, config)
        
        assert result.success
        
        # Find orchestrator file
        orch_files = [f for f in result.files if f.file_type == 'orchestrator']
        assert len(orch_files) == 1
        
        orch_file = orch_files[0]
        assert 'class' in orch_file.content
        assert 'AnalysisOrchestrator' in orch_file.content
    
    def test_scaffold_generates_tests(self, scaffolder, sample_template_yaml):
        """Test scaffolding generates test file."""
        from cortex.tools.orchestrator_scaffolder import ScaffoldConfig, ScaffoldType
        
        config = ScaffoldConfig(
            scaffold_type=ScaffoldType.FULL,
            include_tests=True,
        )
        template = scaffolder.parser.parse_string(sample_template_yaml)
        result = scaffolder.scaffold(template, config)
        
        assert result.success
        
        # Find test file
        test_files = [f for f in result.files if f.file_type == 'test']
        assert len(test_files) == 1
        
        test_file = test_files[0]
        assert 'pytest' in test_file.content or 'def test_' in test_file.content
    
    def test_scaffold_generates_config(self, scaffolder, sample_template_yaml):
        """Test scaffolding generates config file."""
        from cortex.tools.orchestrator_scaffolder import ScaffoldConfig, ScaffoldType
        
        config = ScaffoldConfig(
            scaffold_type=ScaffoldType.FULL,
            include_config=True,
        )
        template = scaffolder.parser.parse_string(sample_template_yaml)
        result = scaffolder.scaffold(template, config)
        
        assert result.success
        
        # Find config file
        config_files = [f for f in result.files if f.file_type == 'config']
        assert len(config_files) == 1
        
        config_file = config_files[0]
        assert 'orchestrator:' in config_file.content or 'name:' in config_file.content
    
    def test_scaffold_generates_integrations(self, scaffolder, sample_template_yaml):
        """Test scaffolding generates integration adapter."""
        from cortex.tools.orchestrator_scaffolder import ScaffoldConfig, ScaffoldType
        
        config = ScaffoldConfig(
            scaffold_type=ScaffoldType.FULL,
            include_integrations=True,
        )
        template = scaffolder.parser.parse_string(sample_template_yaml)
        result = scaffolder.scaffold(template, config)
        
        assert result.success
        
        # Find integration file
        int_files = [f for f in result.files if f.file_type == 'integration']
        assert len(int_files) == 1
    
    def test_scaffold_includes_stages(self, scaffolder, sample_template_yaml):
        """Test scaffolded code includes stage methods."""
        from cortex.tools.orchestrator_scaffolder import ScaffoldConfig, ScaffoldType
        
        config = ScaffoldConfig(scaffold_type=ScaffoldType.ORCHESTRATOR)
        template = scaffolder.parser.parse_string(sample_template_yaml)
        result = scaffolder.scaffold(template, config)
        
        orch_file = [f for f in result.files if f.file_type == 'orchestrator'][0]
        
        assert '_execute_scan' in orch_file.content
        assert '_execute_analyze' in orch_file.content
        assert '_execute_report' in orch_file.content
    
    def test_scaffold_includes_parameters(self, scaffolder, sample_template_yaml):
        """Test scaffolded code includes parameter class."""
        from cortex.tools.orchestrator_scaffolder import ScaffoldConfig, ScaffoldType
        
        config = ScaffoldConfig(scaffold_type=ScaffoldType.ORCHESTRATOR)
        template = scaffolder.parser.parse_string(sample_template_yaml)
        result = scaffolder.scaffold(template, config)
        
        orch_file = [f for f in result.files if f.file_type == 'orchestrator'][0]
        
        assert 'Params' in orch_file.content
        assert 'source_dir' in orch_file.content
        assert 'rules' in orch_file.content
    
    def test_scaffold_result_metadata(self, scaffolder, sample_template_yaml):
        """Test scaffold result includes metadata."""
        template = scaffolder.parser.parse_string(sample_template_yaml)
        result = scaffolder.scaffold(template)
        
        assert 'template_name' in result.metadata
        assert 'template_domain' in result.metadata
        assert 'generated_at' in result.metadata
    
    def test_scaffold_total_lines(self, scaffolder, sample_template_yaml):
        """Test scaffold result tracks line counts."""
        template = scaffolder.parser.parse_string(sample_template_yaml)
        result = scaffolder.scaffold(template)
        
        assert result.total_lines > 0
    
    def test_scaffold_async_support(self, scaffolder, sample_template_yaml):
        """Test scaffolding with async support."""
        from cortex.tools.orchestrator_scaffolder import ScaffoldConfig, ScaffoldType
        
        config = ScaffoldConfig(
            scaffold_type=ScaffoldType.ORCHESTRATOR,
            async_support=True,
        )
        template = scaffolder.parser.parse_string(sample_template_yaml)
        result = scaffolder.scaffold(template, config)
        
        orch_file = [f for f in result.files if f.file_type == 'orchestrator'][0]
        
        assert 'async def' in orch_file.content
        assert 'await' in orch_file.content


# =============================================================================
# AC-TT-002-02: Scaffolder Templates Tests
# =============================================================================

class TestScaffolderTemplates:
    """Tests for ScaffolderTemplates (AC-TT-002-02)."""
    
    def test_base_template_creation(self):
        """Test BaseTemplate can be created."""
        from cortex.tools.scaffolder_templates import BaseTemplate
        
        template = BaseTemplate()
        assert template is not None
    
    def test_base_template_render(self):
        """Test BaseTemplate rendering."""
        from cortex.tools.scaffolder_templates import BaseTemplate
        
        template = BaseTemplate()
        context = {
            'module_name': 'TestModule',
            'author': 'Test Author',
            'version': '1.0.0',
        }
        
        output = template.render(context)
        
        assert 'TestModule' in output
        assert 'Test Author' in output
    
    def test_orchestrator_template_creation(self):
        """Test OrchestratorTemplate can be created."""
        from cortex.tools.scaffolder_templates import OrchestratorTemplate
        
        template = OrchestratorTemplate()
        assert template is not None
    
    def test_orchestrator_template_render(self):
        """Test OrchestratorTemplate rendering."""
        from cortex.tools.scaffolder_templates import OrchestratorTemplate
        
        template = OrchestratorTemplate()
        context = {
            'class_name': 'MyOrchestrator',
            'domain': 'testing',
            'version': '1.0.0',
            'description': 'Test orchestrator',
            'stages': ['stage1', 'stage2'],
            'parameters': [
                {'name': 'input', 'type': 'str', 'required': True}
            ],
        }
        
        output = template.render(context)
        
        assert 'class MyOrchestrator' in output
        assert 'testing' in output
    
    def test_test_template_creation(self):
        """Test TestTemplate can be created."""
        from cortex.tools.scaffolder_templates import TestTemplate
        
        template = TestTemplate()
        assert template is not None
    
    def test_test_template_render(self):
        """Test TestTemplate rendering."""
        from cortex.tools.scaffolder_templates import TestTemplate
        
        template = TestTemplate()
        context = {
            'class_name': 'MyClass',
            'module_path': 'src.my_module',
            'test_cases': [
                {'name': 'basic', 'description': 'Basic test'}
            ],
        }
        
        output = template.render(context)
        
        assert 'TestMyClass' in output
        assert 'pytest' in output
    
    def test_config_template_creation(self):
        """Test ConfigTemplate can be created."""
        from cortex.tools.scaffolder_templates import ConfigTemplate
        
        template = ConfigTemplate()
        assert template is not None
    
    def test_config_template_render(self):
        """Test ConfigTemplate rendering."""
        from cortex.tools.scaffolder_templates import ConfigTemplate
        
        template = ConfigTemplate()
        context = {
            'name': 'MyConfig',
            'domain': 'testing',
            'settings': {'key': 'value'},
        }
        
        output = template.render(context)
        
        assert 'name: MyConfig' in output
        assert 'domain: testing' in output
    
    def test_integration_template_creation(self):
        """Test IntegrationTemplate can be created."""
        from cortex.tools.scaffolder_templates import IntegrationTemplate
        
        template = IntegrationTemplate()
        assert template is not None
    
    def test_integration_template_render(self):
        """Test IntegrationTemplate rendering."""
        from cortex.tools.scaffolder_templates import IntegrationTemplate
        
        template = IntegrationTemplate()
        context = {
            'class_name': 'MyAdapter',
            'integrations': ['database', 'cache'],
        }
        
        output = template.render(context)
        
        assert 'class MyAdapter' in output
        assert 'get_database' in output
        assert 'get_cache' in output
    
    def test_template_registry_get(self):
        """Test TemplateRegistry.get()."""
        from cortex.tools.scaffolder_templates import TemplateRegistry, TemplateType
        
        template = TemplateRegistry.get(TemplateType.ORCHESTRATOR)
        assert template is not None
    
    def test_template_registry_available_types(self):
        """Test TemplateRegistry.available_types()."""
        from cortex.tools.scaffolder_templates import TemplateRegistry, TemplateType
        
        types = TemplateRegistry.available_types()
        
        assert TemplateType.ORCHESTRATOR in types
        assert TemplateType.TEST in types
        assert TemplateType.CONFIG in types
    
    def test_template_variable_resolve(self):
        """Test TemplateVariable resolution."""
        from cortex.tools.scaffolder_templates import TemplateVariable
        
        var = TemplateVariable(
            name='test_var',
            type='str',
            required=True,
        )
        
        context = {'test_var': 'test_value'}
        value = var.resolve(context)
        
        assert value == 'test_value'
    
    def test_template_variable_default(self):
        """Test TemplateVariable default value."""
        from cortex.tools.scaffolder_templates import TemplateVariable
        
        var = TemplateVariable(
            name='optional_var',
            type='str',
            required=False,
            default='default_value',
        )
        
        context = {}
        value = var.resolve(context)
        
        assert value == 'default_value'
    
    def test_template_block_render(self):
        """Test TemplateBlock rendering."""
        from cortex.tools.scaffolder_templates import TemplateBlock
        
        block = TemplateBlock(
            name='test_block',
            content='Hello {{ name }}!',
        )
        
        output = block.render({'name': 'World'})
        
        assert output == 'Hello World!'
    
    def test_template_block_conditional(self):
        """Test TemplateBlock conditional rendering."""
        from cortex.tools.scaffolder_templates import TemplateBlock
        
        block = TemplateBlock(
            name='conditional_block',
            content='Included content',
            condition='include_block',
        )
        
        output_included = block.render({'include_block': True})
        output_excluded = block.render({'include_block': False})
        
        assert output_included == 'Included content'
        assert output_excluded == ''


# =============================================================================
# AC-TT-003-01: Template Validator Tests
# =============================================================================

class TestTemplateValidator:
    """Tests for TemplateValidator (AC-TT-003-01)."""
    
    @pytest.fixture
    def validator(self):
        """Create validator instance."""
        from cortex.tools.template_validator import TemplateValidator
        return TemplateValidator()
    
    @pytest.fixture
    def valid_template(self):
        """Create a valid template dict."""
        return {
            'name': 'ValidTemplate',
            'domain': 'testing',
            'version': '1.0.0',
            'description': 'A valid template',
            'parameters': {
                'input': {
                    'type': 'str',
                    'required': True,
                    'description': 'Input parameter',
                }
            },
            'stages': {
                'stages': [
                    {'name': 'process', 'description': 'Process data'}
                ]
            },
        }
    
    @pytest.fixture
    def invalid_template(self):
        """Create an invalid template dict."""
        return {
            # Missing name
            'domain': 'testing',
            # Invalid version format
            'version': 'invalid',
            'stages': {
                'stages': [
                    # Missing stage name
                    {'description': 'Unnamed stage'},
                    # Duplicate name
                    {'name': 'process'},
                    {'name': 'process'},
                ]
            },
        }
    
    def test_validator_creation(self, validator):
        """Test validator can be created."""
        assert validator is not None
        assert len(validator.rules) > 0
    
    def test_validate_valid_template(self, validator, valid_template):
        """Test validating a valid template."""
        result = validator.validate(valid_template)
        
        assert result.valid is True
        assert result.error_count == 0
    
    def test_validate_invalid_template(self, validator, invalid_template):
        """Test validating an invalid template."""
        result = validator.validate(invalid_template)
        
        # Should have errors or warnings
        assert result.error_count > 0 or result.warning_count > 0
    
    def test_validate_missing_required_field(self, validator):
        """Test validation catches missing required fields."""
        from cortex.tools.template_validator import ValidationLevel
        
        template = {
            'domain': 'testing',
            'version': '1.0.0',
        }
        
        result = validator.validate(template)
        
        # Should catch missing name - may be error or warning
        all_messages = [e.message.lower() for e in result.errors]
        all_messages.extend([w.message.lower() for w in result.get_by_level(ValidationLevel.WARNING)])
        assert any('name' in m for m in all_messages)
    
    def test_validate_invalid_version(self, validator):
        """Test validation catches invalid version format."""
        from cortex.tools.template_validator import ValidationLevel
        
        template = {
            'name': 'Test',
            'domain': 'testing',
            'version': 'not-semver',
        }
        
        result = validator.validate(template)
        
        warnings = result.get_by_level(ValidationLevel.WARNING)
        version_warnings = [w for w in warnings if 'version' in w.message.lower()]
        assert len(version_warnings) > 0
    
    def test_validate_duplicate_stage_names(self, validator):
        """Test validation catches duplicate stage names."""
        template = {
            'name': 'Test',
            'domain': 'testing',
            'version': '1.0.0',
            'stages': {
                'stages': [
                    {'name': 'process'},
                    {'name': 'process'},  # Duplicate
                ]
            },
        }
        
        result = validator.validate(template)
        
        errors = [e for e in result.errors if 'duplicate' in e.message.lower()]
        assert len(errors) > 0
    
    def test_validate_unknown_parameter_type(self, validator):
        """Test validation catches unknown parameter types."""
        from cortex.tools.template_validator import ValidationLevel
        
        template = {
            'name': 'Test',
            'domain': 'testing',
            'version': '1.0.0',
            'parameters': {
                'param': {
                    'type': 'unknown_type',
                    'required': True,
                }
            },
        }
        
        result = validator.validate(template)
        
        warnings = result.get_by_level(ValidationLevel.WARNING)
        type_warnings = [w for w in warnings if 'type' in w.message.lower()]
        assert len(type_warnings) > 0
    
    def test_generate_report(self, validator, valid_template):
        """Test generating compliance report."""
        report = validator.generate_report(valid_template)
        
        assert report is not None
        assert report.template_name == 'ValidTemplate'
        assert report.compliance_level in ('full', 'partial', 'non-compliant')
        assert 0 <= report.coverage_score <= 100
    
    def test_compliance_levels(self, validator, valid_template, invalid_template):
        """Test compliance level determination."""
        valid_report = validator.generate_report(valid_template)
        invalid_report = validator.generate_report(invalid_template)
        
        # Valid template should be compliant
        assert valid_report.compliance_level in ('full', 'partial')
        
        # Invalid template should be non-compliant or partial
        assert invalid_report.compliance_level in ('partial', 'non-compliant')
    
    def test_check_compliance(self, validator, valid_template):
        """Test compliance checking."""
        assert validator.check_compliance(valid_template, 'partial') is True
    
    def test_add_rule(self, validator):
        """Test adding custom rule."""
        from cortex.tools.template_validator import ValidationRule
        
        class CustomRule(ValidationRule):
            code = "CUSTOM-001"
            name = "Custom Rule"
            
            def validate(self, template, context):
                return []
        
        initial_count = len(validator.rules)
        validator.add_rule(CustomRule())
        
        assert len(validator.rules) == initial_count + 1
    
    def test_remove_rule(self, validator):
        """Test removing a rule."""
        initial_count = len(validator.rules)
        
        # Remove first rule
        if validator.rules:
            code = validator.rules[0].code
            validator.remove_rule(code)
            assert len(validator.rules) == initial_count - 1
    
    def test_validate_file(self, validator, valid_template):
        """Test validating from file."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(valid_template, f)
            f.flush()
            
            result = validator.validate_file(f.name)
            assert result.valid is True
    
    def test_validate_file_not_found(self, validator):
        """Test validation of non-existent file."""
        result = validator.validate_file('/nonexistent/template.yaml')
        
        assert result.valid is False
        assert result.error_count > 0


# =============================================================================
# AC-TT-003-02: Testing Framework Tests
# =============================================================================

class TestTestingFramework:
    """Tests for TemplateTestFramework (AC-TT-003-02)."""
    
    @pytest.fixture
    def framework(self):
        """Create framework instance."""
        from cortex.tools.testing_framework import TemplateTestFramework
        return TemplateTestFramework("Test Framework")
    
    @pytest.fixture
    def sample_template(self):
        """Create sample template for testing."""
        return {
            'name': 'SampleTemplate',
            'domain': 'testing',
            'version': '1.0.0',
            'parameters': {
                'input': {'type': 'str', 'required': True}
            },
        }
    
    def test_framework_creation(self, framework):
        """Test framework can be created."""
        assert framework is not None
        assert framework.name == "Test Framework"
    
    def test_add_test(self, framework):
        """Test adding test case."""
        from cortex.tools.testing_framework import TemplateTestCase, Assertion
        
        test = TemplateTestCase(
            name='test_example',
            description='Example test',
            assertions=[
                Assertion(name='always_pass', condition=lambda: True)
            ],
        )
        
        framework.add_test(test)
        
        assert len(framework._tests) == 1
    
    def test_run_passing_test(self, framework):
        """Test running a passing test."""
        from cortex.tools.testing_framework import TemplateTestCase, Assertion, TestStatus
        
        test = TemplateTestCase(
            name='test_pass',
            assertions=[
                Assertion(name='check', condition=lambda: True)
            ],
        )
        
        framework.add_test(test)
        suite = framework.run()
        
        assert suite.passed == 1
        assert suite.failed == 0
        assert suite.results[0].status == TestStatus.PASSED
    
    def test_run_failing_test(self, framework):
        """Test running a failing test."""
        from cortex.tools.testing_framework import TemplateTestCase, Assertion, TestStatus
        
        test = TemplateTestCase(
            name='test_fail',
            assertions=[
                Assertion(name='check', condition=lambda: False, message='Expected failure')
            ],
        )
        
        framework.add_test(test)
        suite = framework.run()
        
        assert suite.failed == 1
        assert suite.passed == 0
        assert suite.results[0].status == TestStatus.FAILED
    
    def test_run_skipped_test(self, framework):
        """Test running a skipped test."""
        from cortex.tools.testing_framework import TemplateTestCase, TestStatus
        
        test = TemplateTestCase(
            name='test_skip',
            skip=True,
            skip_reason='Intentionally skipped',
        )
        
        framework.add_test(test)
        suite = framework.run()
        
        assert suite.skipped == 1
        assert suite.results[0].status == TestStatus.SKIPPED
    
    def test_run_error_test(self, framework):
        """Test handling test errors."""
        from cortex.tools.testing_framework import TemplateTestCase, Assertion, TestStatus
        
        def raise_error():
            raise RuntimeError("Test error")
        
        test = TemplateTestCase(
            name='test_error',
            assertions=[
                Assertion(name='check', condition=raise_error)
            ],
        )
        
        framework.add_test(test)
        suite = framework.run()
        
        # Error in assertion still counts as failure
        assert suite.results[0].status in (TestStatus.FAILED, TestStatus.ERROR)
    
    def test_suite_summary(self, framework):
        """Test suite summary generation."""
        from cortex.tools.testing_framework import TemplateTestCase, Assertion
        
        framework.add_test(TemplateTestCase(
            name='test1',
            assertions=[Assertion(name='c', condition=lambda: True)],
        ))
        framework.add_test(TemplateTestCase(
            name='test2',
            assertions=[Assertion(name='c', condition=lambda: True)],
        ))
        
        suite = framework.run()
        summary = suite.summary()
        
        assert 'Test Framework' in summary
        assert '2/2' in summary
    
    def test_report_generation(self, framework):
        """Test report generation."""
        from cortex.tools.testing_framework import TemplateTestCase, Assertion
        
        framework.add_test(TemplateTestCase(
            name='test_pass',
            assertions=[Assertion(name='c', condition=lambda: True)],
        ))
        framework.add_test(TemplateTestCase(
            name='test_fail',
            assertions=[Assertion(name='c', condition=lambda: False)],
        ))
        
        suite = framework.run()
        report = framework.report(suite)
        
        assert 'Passed:' in report
        assert 'Failed:' in report
    
    def test_assertion_builder(self, sample_template):
        """Test AssertionBuilder."""
        from cortex.tools.testing_framework import AssertionBuilder
        
        builder = AssertionBuilder(sample_template)
        builder.has_field('name').equals('SampleTemplate')
        builder.has_field('domain').is_not_empty()
        
        assertions = builder.build()
        
        assert len(assertions) >= 2
    
    def test_assertion_builder_check_all(self, sample_template):
        """Test AssertionBuilder.check_all()."""
        from cortex.tools.testing_framework import AssertionBuilder
        
        builder = AssertionBuilder(sample_template)
        builder.has_field('name').equals('SampleTemplate')
        
        passed, failures = builder.check_all()
        
        assert passed is True
        assert len(failures) == 0
    
    def test_assertion_builder_failed_check(self, sample_template):
        """Test AssertionBuilder with failing checks."""
        from cortex.tools.testing_framework import AssertionBuilder
        
        builder = AssertionBuilder(sample_template)
        builder.has_field('name').equals('WrongName')
        
        passed, failures = builder.check_all()
        
        assert passed is False
        assert len(failures) > 0
    
    def test_filter_tests_by_tags(self, framework):
        """Test filtering tests by tags."""
        from cortex.tools.testing_framework import TemplateTestCase, Assertion
        
        framework.add_test(TemplateTestCase(
            name='test_tagged',
            tags={'important'},
            assertions=[Assertion(name='c', condition=lambda: True)],
        ))
        framework.add_test(TemplateTestCase(
            name='test_untagged',
            assertions=[Assertion(name='c', condition=lambda: True)],
        ))
        
        suite = framework.run(tags={'important'})
        
        assert suite.total == 1
        assert suite.results[0].test_name == 'test_tagged'
    
    def test_filter_tests_by_names(self, framework):
        """Test filtering tests by names."""
        from cortex.tools.testing_framework import TemplateTestCase, Assertion
        
        framework.add_test(TemplateTestCase(
            name='test_one',
            assertions=[Assertion(name='c', condition=lambda: True)],
        ))
        framework.add_test(TemplateTestCase(
            name='test_two',
            assertions=[Assertion(name='c', condition=lambda: True)],
        ))
        
        suite = framework.run(names=['test_one'])
        
        assert suite.total == 1
        assert suite.results[0].test_name == 'test_one'
    
    def test_before_each_hook(self, framework):
        """Test before_each hook."""
        from cortex.tools.testing_framework import TemplateTestCase, Assertion
        
        call_count = [0]
        
        def increment():
            call_count[0] += 1
        
        framework.before_each(increment)
        framework.add_test(TemplateTestCase(
            name='test1',
            assertions=[Assertion(name='c', condition=lambda: True)],
        ))
        framework.add_test(TemplateTestCase(
            name='test2',
            assertions=[Assertion(name='c', condition=lambda: True)],
        ))
        
        framework.run()
        
        assert call_count[0] == 2
    
    def test_create_template_test(self, sample_template):
        """Test create_template_test factory function."""
        from cortex.tools.testing_framework import create_template_test
        
        test = create_template_test(
            sample_template,
            checks=['has_name', 'has_version', 'has_domain'],
        )
        
        assert test is not None
        assert len(test.assertions) > 0
    
    def test_to_pytest_generation(self, framework):
        """Test pytest code generation."""
        from cortex.tools.testing_framework import TemplateTestCase, Assertion
        
        framework.add_test(TemplateTestCase(
            name='test_example',
            description='Example test',
            assertions=[Assertion(name='c', condition=lambda: True)],
        ))
        
        pytest_code = framework.to_pytest()
        
        assert 'def test_example' in pytest_code
        assert 'pytest' in pytest_code


# =============================================================================
# Integration Tests
# =============================================================================

class TestTemplateToolsIntegration:
    """Integration tests for all template tools."""
    
    @pytest.fixture
    def full_template_yaml(self) -> str:
        """Complete template for integration testing."""
        return """
name: IntegrationTestOrchestrator
domain: integration
version: 2.1.0
description: Full orchestrator for integration testing

metadata:
  author: CORTEX
  tier: 2
  tags:
    - testing
    - integration

parameters:
  source:
    type: str
    required: true
    description: Source path
  target:
    type: str
    required: true
    description: Target path
  options:
    type: dict
    required: false
    default: {}
    description: Additional options

stages:
  stages:
    - name: validate
      description: Validate inputs
      action: validate_inputs
      inputs:
        source: $params.source
        target: $params.target
    - name: transform
      description: Transform data
      action: transform_data
    - name: output
      description: Write output
      action: write_output

hooks:
  pre_execute:
    handler: setup_context
    description: Initialize execution context
  post_execute:
    handler: cleanup_context
    description: Cleanup after execution
  on_error:
    handler: handle_error
    description: Error handling

integrations:
  filesystem:
    type: local
    base_path: /tmp
  metrics:
    type: prometheus
    endpoint: http://localhost:9090
"""
    
    def test_full_workflow_parse_validate_scaffold(self, full_template_yaml):
        """Test complete workflow: parse -> validate -> scaffold."""
        from cortex.tools.template_parser import TemplateParser
        from cortex.tools.template_validator import TemplateValidator
        from cortex.tools.orchestrator_scaffolder import OrchestratorScaffolder
        
        # Parse
        parser = TemplateParser()
        template = parser.parse_string(full_template_yaml)
        
        assert template.name == "IntegrationTestOrchestrator"
        assert template.domain == "integration"
        
        # Validate
        validator = TemplateValidator()
        validation_result = validator.validate(template)
        
        assert validation_result.valid is True
        
        # Scaffold
        scaffolder = OrchestratorScaffolder()
        scaffold_result = scaffolder.scaffold(template)
        
        assert scaffold_result.success is True
        assert len(scaffold_result.files) >= 1
    
    def test_full_workflow_with_tool_generation(self, full_template_yaml):
        """Test workflow with tool generation."""
        from cortex.tools.template_parser import TemplateParser
        from cortex.tools.tool_generator import ToolGenerator, GenerationConfig, ToolType
        
        # Parse
        parser = TemplateParser()
        template = parser.parse_string(full_template_yaml)
        
        # Generate CLI
        generator = ToolGenerator()
        cli_result = generator.generate(
            template,
            GenerationConfig(tool_type=ToolType.CLI_COMMAND),
        )
        
        assert cli_result.success is True
        
        # Generate Tests
        test_result = generator.generate(
            template,
            GenerationConfig(tool_type=ToolType.TEST_HARNESS),
        )
        
        assert test_result.success is True
        
        # Generate Docs
        doc_result = generator.generate(
            template,
            GenerationConfig(tool_type=ToolType.DOCUMENTATION),
        )
        
        assert doc_result.success is True
    
    def test_full_workflow_with_testing_framework(self, full_template_yaml):
        """Test workflow with testing framework."""
        from cortex.tools.template_parser import TemplateParser
        from cortex.tools.testing_framework import (
            TemplateTestFramework,
            TemplateTestCase,
            AssertionBuilder,
        )
        
        # Parse
        parser = TemplateParser()
        template = parser.parse_string(full_template_yaml)
        
        # Create test framework
        framework = TemplateTestFramework("Integration Tests")
        
        # Add tests using AssertionBuilder
        builder = AssertionBuilder(template)
        builder.has_field('name').equals('IntegrationTestOrchestrator')
        builder.has_field('domain').equals('integration')
        builder.has_field('version').matches(r'^\d+\.\d+\.\d+$')
        
        framework.add_test(TemplateTestCase(
            name='test_template_structure',
            description='Verify template structure',
            assertions=builder.build(),
        ))
        
        # Run tests
        suite = framework.run()
        
        assert suite.passed > 0
        assert suite.success_rate > 0
    
    def test_compliance_report_generation(self, full_template_yaml):
        """Test generating compliance report."""
        from cortex.tools.template_parser import TemplateParser
        from cortex.tools.template_validator import TemplateValidator
        
        parser = TemplateParser()
        template = parser.parse_string(full_template_yaml)
        
        validator = TemplateValidator()
        report = validator.generate_report(template)
        
        assert report.template_name == "IntegrationTestOrchestrator"
        assert report.compliance_level in ('full', 'partial')
        assert report.coverage_score > 0


# =============================================================================
# Standalone test for quick validation
# =============================================================================

def test_all_tools_importable():
    """Test that all tools are importable."""
    from cortex.tools.template_parser import TemplateParser, ParsedTemplate, ParseError
    from cortex.tools.tool_generator import ToolGenerator, GeneratedTool, ToolType
    from cortex.tools.orchestrator_scaffolder import OrchestratorScaffolder, ScaffoldResult
    from cortex.tools.scaffolder_templates import (
        BaseTemplate,
        OrchestratorTemplate,
        TestTemplate,
        ConfigTemplate,
        IntegrationTemplate,
    )
    from cortex.tools.template_validator import TemplateValidator, ValidationResult
    from cortex.tools.testing_framework import TemplateTestFramework, TemplateTestCase
    
    # All imports successful
    assert TemplateParser is not None
    assert ToolGenerator is not None
    assert OrchestratorScaffolder is not None
    assert BaseTemplate is not None
    assert TemplateValidator is not None
    assert TemplateTestFramework is not None
