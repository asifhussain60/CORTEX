"""
Tool Generator (AC-TT-001-02)

Generates tooling and utilities from orchestrator templates.
Supports:
- CLI command generation
- API client generation
- Test harness generation
- Documentation generation

Works with ParsedTemplate from template_parser.
"""

import re
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable
from datetime import datetime

from cortex.tools.template_parser import ParsedTemplate, TemplateSection


class ToolType(Enum):
    """Types of tools that can be generated."""
    CLI_COMMAND = auto()
    API_CLIENT = auto()
    TEST_HARNESS = auto()
    DOCUMENTATION = auto()
    CONFIG_VALIDATOR = auto()
    MOCK_SERVICE = auto()
    INTEGRATION_ADAPTER = auto()


@dataclass
class GenerationConfig:
    """Configuration for tool generation."""
    tool_type: ToolType
    output_dir: Path = field(default_factory=lambda: Path("generated"))
    include_tests: bool = True
    include_docs: bool = True
    python_version: str = "3.9"
    style_guide: str = "pep8"
    type_hints: bool = True
    docstrings: bool = True
    
    # Template customization
    class_prefix: str = ""
    class_suffix: str = ""
    function_prefix: str = ""
    function_suffix: str = ""
    
    # Output options
    overwrite: bool = False
    dry_run: bool = False


@dataclass
class GeneratedTool:
    """A generated tool/file."""
    name: str
    tool_type: ToolType
    content: str
    path: Path
    template_source: str
    generated_at: datetime = field(default_factory=datetime.now)
    dependencies: List[str] = field(default_factory=list)
    
    def write(self, base_dir: Optional[Path] = None) -> Path:
        """Write the generated tool to disk."""
        output_path = base_dir / self.path if base_dir else self.path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.content)
        return output_path


@dataclass
class GenerationResult:
    """Result of tool generation."""
    success: bool
    tools: List[GeneratedTool] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_tool(self, tool: GeneratedTool) -> None:
        """Add a generated tool."""
        self.tools.append(tool)
    
    def add_error(self, message: str) -> None:
        """Add an error message."""
        self.errors.append(message)
        self.success = False
    
    def add_warning(self, message: str) -> None:
        """Add a warning message."""
        self.warnings.append(message)


class ToolGenerator:
    """
    Generator for orchestrator tooling.
    
    Takes ParsedTemplate objects and generates various tools:
    - CLI commands for orchestrator invocation
    - API clients for programmatic access
    - Test harnesses for validation
    - Documentation for users
    
    Example:
        generator = ToolGenerator()
        config = GenerationConfig(tool_type=ToolType.CLI_COMMAND)
        result = generator.generate(template, config)
        for tool in result.tools:
            tool.write(Path("output"))
    """
    
    def __init__(self):
        """Initialize the generator."""
        self._generators: Dict[ToolType, Callable] = {
            ToolType.CLI_COMMAND: self._generate_cli,
            ToolType.API_CLIENT: self._generate_api_client,
            ToolType.TEST_HARNESS: self._generate_test_harness,
            ToolType.DOCUMENTATION: self._generate_documentation,
            ToolType.CONFIG_VALIDATOR: self._generate_config_validator,
            ToolType.MOCK_SERVICE: self._generate_mock_service,
            ToolType.INTEGRATION_ADAPTER: self._generate_integration_adapter,
        }
    
    def generate(self, template: ParsedTemplate, config: GenerationConfig) -> GenerationResult:
        """
        Generate tools from a template.
        
        Args:
            template: ParsedTemplate to generate from
            config: Generation configuration
            
        Returns:
            GenerationResult with generated tools
        """
        result = GenerationResult(success=True)
        
        generator = self._generators.get(config.tool_type)
        if not generator:
            result.add_error(f"Unknown tool type: {config.tool_type}")
            return result
        
        try:
            tools = generator(template, config)
            for tool in tools:
                result.add_tool(tool)
        except Exception as e:
            result.add_error(f"Generation failed: {str(e)}")
        
        return result
    
    def generate_all(self, template: ParsedTemplate, output_dir: Path) -> GenerationResult:
        """
        Generate all available tools from a template.
        
        Args:
            template: ParsedTemplate to generate from
            output_dir: Directory for output files
            
        Returns:
            GenerationResult with all generated tools
        """
        result = GenerationResult(success=True)
        
        for tool_type in ToolType:
            config = GenerationConfig(
                tool_type=tool_type,
                output_dir=output_dir,
            )
            sub_result = self.generate(template, config)
            result.tools.extend(sub_result.tools)
            result.errors.extend(sub_result.errors)
            result.warnings.extend(sub_result.warnings)
            if not sub_result.success:
                result.success = False
        
        return result
    
    def _generate_cli(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        """Generate CLI command for orchestrator."""
        tools = []
        
        class_name = self._to_class_name(template.name) + "CLI"
        module_name = self._to_module_name(template.name) + "_cli"
        
        # Get parameters for CLI arguments
        params = self._get_parameters(template)
        
        # Generate CLI code
        cli_code = self._render_cli_template(
            class_name=class_name,
            template_name=template.name,
            template_domain=template.domain,
            parameters=params,
            description=template.description,
            config=config,
        )
        
        tool = GeneratedTool(
            name=class_name,
            tool_type=ToolType.CLI_COMMAND,
            content=cli_code,
            path=Path(f"cli/{module_name}.py"),
            template_source=template.name,
            dependencies=['click', 'typing'],
        )
        tools.append(tool)
        
        return tools
    
    def _generate_api_client(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        """Generate API client for orchestrator."""
        tools = []
        
        class_name = self._to_class_name(template.name) + "Client"
        module_name = self._to_module_name(template.name) + "_client"
        
        params = self._get_parameters(template)
        
        client_code = self._render_api_client_template(
            class_name=class_name,
            template_name=template.name,
            template_domain=template.domain,
            parameters=params,
            description=template.description,
            config=config,
        )
        
        tool = GeneratedTool(
            name=class_name,
            tool_type=ToolType.API_CLIENT,
            content=client_code,
            path=Path(f"clients/{module_name}.py"),
            template_source=template.name,
            dependencies=['httpx', 'typing', 'dataclasses'],
        )
        tools.append(tool)
        
        return tools
    
    def _generate_test_harness(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        """Generate test harness for orchestrator."""
        tools = []
        
        class_name = f"Test{self._to_class_name(template.name)}"
        module_name = f"test_{self._to_module_name(template.name)}"
        
        params = self._get_parameters(template)
        stages = self._get_stages(template)
        hooks = self._get_hooks(template)
        
        test_code = self._render_test_harness_template(
            class_name=class_name,
            template_name=template.name,
            template_domain=template.domain,
            parameters=params,
            stages=stages,
            hooks=hooks,
            description=template.description,
            config=config,
        )
        
        tool = GeneratedTool(
            name=class_name,
            tool_type=ToolType.TEST_HARNESS,
            content=test_code,
            path=Path(f"tests/{module_name}.py"),
            template_source=template.name,
            dependencies=['pytest', 'unittest.mock'],
        )
        tools.append(tool)
        
        return tools
    
    def _generate_documentation(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        """Generate documentation for orchestrator."""
        tools = []
        
        doc_name = self._to_module_name(template.name)
        
        params = self._get_parameters(template)
        stages = self._get_stages(template)
        hooks = self._get_hooks(template)
        
        doc_content = self._render_documentation_template(
            template_name=template.name,
            template_domain=template.domain,
            parameters=params,
            stages=stages,
            hooks=hooks,
            description=template.description,
            version=template.version,
        )
        
        # CORE-002 COMPLIANCE: No docs/ markdown generation
        # Documentation generated inline only
        tool = GeneratedTool(
            name=f"{template.name} Documentation",
            tool_type=ToolType.DOCUMENTATION,
            content=doc_content,
            path=None,  # No file path - inline only
            template_source=template.name,
            dependencies=[],
        )
        tools.append(tool)
        
        return tools
    
    def _generate_config_validator(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        """Generate configuration validator."""
        tools = []
        
        class_name = self._to_class_name(template.name) + "ConfigValidator"
        module_name = self._to_module_name(template.name) + "_validator"
        
        params = self._get_parameters(template)
        
        validator_code = self._render_config_validator_template(
            class_name=class_name,
            template_name=template.name,
            parameters=params,
            config=config,
        )
        
        tool = GeneratedTool(
            name=class_name,
            tool_type=ToolType.CONFIG_VALIDATOR,
            content=validator_code,
            path=Path(f"validators/{module_name}.py"),
            template_source=template.name,
            dependencies=['pydantic', 'typing'],
        )
        tools.append(tool)
        
        return tools
    
    def _generate_mock_service(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        """Generate mock service for testing."""
        tools = []
        
        class_name = f"Mock{self._to_class_name(template.name)}Service"
        module_name = f"mock_{self._to_module_name(template.name)}"
        
        stages = self._get_stages(template)
        
        mock_code = self._render_mock_service_template(
            class_name=class_name,
            template_name=template.name,
            stages=stages,
            config=config,
        )
        
        tool = GeneratedTool(
            name=class_name,
            tool_type=ToolType.MOCK_SERVICE,
            content=mock_code,
            path=Path(f"mocks/{module_name}.py"),
            template_source=template.name,
            dependencies=['unittest.mock', 'typing'],
        )
        tools.append(tool)
        
        return tools
    
    def _generate_integration_adapter(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        """Generate integration adapter."""
        tools = []
        
        class_name = self._to_class_name(template.name) + "Adapter"
        module_name = self._to_module_name(template.name) + "_adapter"
        
        integrations = self._get_integrations(template)
        
        adapter_code = self._render_integration_adapter_template(
            class_name=class_name,
            template_name=template.name,
            integrations=integrations,
            config=config,
        )
        
        tool = GeneratedTool(
            name=class_name,
            tool_type=ToolType.INTEGRATION_ADAPTER,
            content=adapter_code,
            path=Path(f"adapters/{module_name}.py"),
            template_source=template.name,
            dependencies=['typing', 'abc'],
        )
        tools.append(tool)
        
        return tools
    
    # Helper methods
    
    def _to_class_name(self, name: str) -> str:
        """Convert name to PascalCase class name."""
        # Remove special characters and split on separators
        parts = re.split(r'[-_\s]+', name)
        return ''.join(part.capitalize() for part in parts)
    
    def _to_module_name(self, name: str) -> str:
        """Convert name to snake_case module name."""
        # Convert to lowercase and replace separators
        name = re.sub(r'[-\s]+', '_', name.lower())
        # Handle camelCase
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name).lower()
        return name
    
    def _get_parameters(self, template: ParsedTemplate) -> List[Dict[str, Any]]:
        """Extract parameter definitions from template."""
        params = []
        params_section = template.get_section('parameters')
        if params_section:
            for name, config in params_section.content.items():
                if isinstance(config, dict):
                    params.append({
                        'name': name,
                        'type': config.get('type', 'str'),
                        'required': config.get('required', False),
                        'default': config.get('default'),
                        'description': config.get('description', ''),
                    })
                else:
                    params.append({
                        'name': name,
                        'type': 'str',
                        'required': False,
                        'default': config,
                        'description': '',
                    })
        return params
    
    def _get_stages(self, template: ParsedTemplate) -> List[Dict[str, Any]]:
        """Extract stage definitions from template."""
        stages_section = template.get_section('stages')
        if stages_section:
            return stages_section.content.get('stages', [])
        return []
    
    def _get_hooks(self, template: ParsedTemplate) -> Dict[str, Any]:
        """Extract hook definitions from template."""
        hooks_section = template.get_section('hooks')
        if hooks_section:
            return hooks_section.content
        return {}
    
    def _get_integrations(self, template: ParsedTemplate) -> Dict[str, Any]:
        """Extract integration definitions from template."""
        integrations_section = template.get_section('integrations')
        if integrations_section:
            return integrations_section.content
        return {}
    
    # Template rendering methods
    
    def _render_cli_template(
        self,
        class_name: str,
        template_name: str,
        template_domain: str,
        parameters: List[Dict[str, Any]],
        description: str,
        config: GenerationConfig,
    ) -> str:
        """Render CLI command template."""
        # Generate click options for parameters
        options = []
        for param in parameters:
            opt_name = param['name'].replace('_', '-')
            opt_type = self._python_type_to_click(param['type'])
            required = param['required']
            default = param.get('default')
            help_text = param.get('description', '')
            
            if required:
                options.append(f"@click.option('--{opt_name}', type={opt_type}, required=True, help='{help_text}')")
            else:
                default_str = f"'{default}'" if isinstance(default, str) else str(default)
                options.append(f"@click.option('--{opt_name}', type={opt_type}, default={default_str}, help='{help_text}')")
        
        options_str = '\n'.join(options)
        param_args = ', '.join(param['name'] for param in parameters)
        
        return f'''"""
CLI Command for {template_name}
Generated from template: {template_name}
Domain: {template_domain}

{description}
"""

import click
from typing import Optional, Any

{options_str}
@click.command(name='{self._to_module_name(template_name)}')
def {self._to_module_name(template_name)}_command({param_args}):
    """
    {description}
    """
    # Build configuration from parameters
    config = {{
        {', '.join(f"'{p['name']}': {p['name']}" for p in parameters)}
    }}
    
    # Execute orchestrator
    from cortex.orchestrators.factory import create_orchestrator
    
    orchestrator = create_orchestrator('{template_domain}')
    result = orchestrator.execute(config)
    
    # Output result
    click.echo(f"Execution completed: {{result.status}}")
    if result.output:
        click.echo(result.output)


class {class_name}:
    """CLI wrapper for {template_name}."""
    
    def __init__(self):
        self.command = {self._to_module_name(template_name)}_command
    
    def invoke(self, **kwargs) -> Any:
        """Invoke the CLI command programmatically."""
        from click.testing import CliRunner
        runner = CliRunner()
        args = [f"--{{k.replace('_', '-')}}={{v}}" for k, v in kwargs.items()]
        return runner.invoke(self.command, args)


if __name__ == '__main__':
    {self._to_module_name(template_name)}_command()
'''
    
    def _render_api_client_template(
        self,
        class_name: str,
        template_name: str,
        template_domain: str,
        parameters: List[Dict[str, Any]],
        description: str,
        config: GenerationConfig,
    ) -> str:
        """Render API client template."""
        # Generate dataclass fields for parameters
        fields = []
        for param in parameters:
            py_type = self._yaml_type_to_python(param['type'])
            if not param['required']:
                py_type = f"Optional[{py_type}]"
            default = param.get('default')
            if default is not None:
                default_str = f" = {repr(default)}"
            elif not param['required']:
                default_str = " = None"
            else:
                default_str = ""
            fields.append(f"    {param['name']}: {py_type}{default_str}")
        
        fields_str = '\n'.join(fields)
        
        return f'''"""
API Client for {template_name}
Generated from template: {template_name}
Domain: {template_domain}

{description}
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, Optional
import httpx


@dataclass
class {class_name}Request:
    """Request parameters for {template_name}."""
{fields_str}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary, excluding None values."""
        return {{k: v for k, v in asdict(self).items() if v is not None}}


@dataclass
class {class_name}Response:
    """Response from {template_name} execution."""
    success: bool
    status: str
    output: Optional[Any] = None
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


class {class_name}:
    """
    API Client for {template_name}.
    
    {description}
    
    Example:
        client = {class_name}(base_url="http://localhost:8000")
        request = {class_name}Request(...)
        response = client.execute(request)
    """
    
    def __init__(
        self,
        base_url: str = "http://localhost:8000",
        timeout: float = 30.0,
        api_key: Optional[str] = None,
    ):
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.api_key = api_key
        self._client: Optional[httpx.Client] = None
    
    @property
    def client(self) -> httpx.Client:
        """Get or create HTTP client."""
        if self._client is None:
            headers = {{"Content-Type": "application/json"}}
            if self.api_key:
                headers["Authorization"] = f"Bearer {{self.api_key}}"
            self._client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
                headers=headers,
            )
        return self._client
    
    def execute(self, request: {class_name}Request) -> {class_name}Response:
        """
        Execute the {template_name} orchestrator.
        
        Args:
            request: Request parameters
            
        Returns:
            {class_name}Response with execution results
        """
        try:
            response = self.client.post(
                "/api/v1/orchestrate/{template_domain}",
                json=request.to_dict(),
            )
            response.raise_for_status()
            data = response.json()
            return {class_name}Response(
                success=True,
                status=data.get("status", "completed"),
                output=data.get("output"),
                metadata=data.get("metadata"),
            )
        except httpx.HTTPError as e:
            return {class_name}Response(
                success=False,
                status="error",
                error=str(e),
            )
    
    async def execute_async(self, request: {class_name}Request) -> {class_name}Response:
        """Execute asynchronously."""
        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=self.timeout,
        ) as client:
            try:
                response = await client.post(
                    "/api/v1/orchestrate/{template_domain}",
                    json=request.to_dict(),
                )
                response.raise_for_status()
                data = response.json()
                return {class_name}Response(
                    success=True,
                    status=data.get("status", "completed"),
                    output=data.get("output"),
                    metadata=data.get("metadata"),
                )
            except httpx.HTTPError as e:
                return {class_name}Response(
                    success=False,
                    status="error",
                    error=str(e),
                )
    
    def close(self) -> None:
        """Close the client connection."""
        if self._client:
            self._client.close()
            self._client = None
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close()
'''
    
    def _render_test_harness_template(
        self,
        class_name: str,
        template_name: str,
        template_domain: str,
        parameters: List[Dict[str, Any]],
        stages: List[Dict[str, Any]],
        hooks: Dict[str, Any],
        description: str,
        config: GenerationConfig,
    ) -> str:
        """Render test harness template."""
        # Generate parameter fixtures
        fixtures = []
        for param in parameters:
            value = param.get('default')
            if value is None:
                if param['type'] == 'str':
                    value = "'test_value'"
                elif param['type'] in ('int', 'integer'):
                    value = "1"
                elif param['type'] in ('float', 'number'):
                    value = "1.0"
                elif param['type'] in ('bool', 'boolean'):
                    value = "True"
                else:
                    value = "'test'"
            else:
                value = repr(value)
            fixtures.append(f"    '{param['name']}': {value},")
        
        fixtures_str = '\n'.join(fixtures)
        
        # Generate stage tests
        stage_tests = []
        for i, stage in enumerate(stages):
            stage_name = stage.get('name', f'stage_{i}')
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', stage_name)
            stage_tests.append(f'''
    def test_stage_{safe_name}(self, orchestrator, sample_input):
        """Test {stage_name} stage execution."""
        # Execute up to this stage
        result = orchestrator.execute_stage('{stage_name}', sample_input)
        assert result is not None
        assert result.status in ['completed', 'success']''')
        
        stage_tests_str = '\n'.join(stage_tests) if stage_tests else '''
    def test_stages_placeholder(self, orchestrator, sample_input):
        """Placeholder for stage tests when no stages defined."""
        pass'''
        
        # Generate hook tests
        hook_tests = []
        for hook_name in hooks.keys():
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', hook_name)
            hook_tests.append(f'''
    def test_hook_{safe_name}(self, orchestrator, sample_input):
        """Test {hook_name} hook execution."""
        from unittest.mock import MagicMock
        hook_mock = MagicMock()
        orchestrator.register_hook('{hook_name}', hook_mock)
        orchestrator.execute(sample_input)
        hook_mock.assert_called()''')
        
        hook_tests_str = '\n'.join(hook_tests) if hook_tests else ''
        
        return f'''"""
Test Harness for {template_name}
Generated from template: {template_name}
Domain: {template_domain}

{description}
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Any, Dict


class {class_name}:
    """Test harness for {template_name} orchestrator."""
    
    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance for testing."""
        from cortex.orchestrators.factory import create_orchestrator
        return create_orchestrator('{template_domain}')
    
    @pytest.fixture
    def sample_input(self) -> Dict[str, Any]:
        """Sample input parameters for testing."""
        return {{
{fixtures_str}
        }}
    
    @pytest.fixture
    def mock_context(self):
        """Mock execution context."""
        return MagicMock()
    
    # Basic Tests
    
    def test_orchestrator_creation(self, orchestrator):
        """Test orchestrator can be created."""
        assert orchestrator is not None
        assert orchestrator.domain == '{template_domain}'
    
    def test_basic_execution(self, orchestrator, sample_input):
        """Test basic orchestrator execution."""
        result = orchestrator.execute(sample_input)
        assert result is not None
        assert hasattr(result, 'status')
    
    def test_with_missing_required_params(self, orchestrator):
        """Test execution with missing required parameters."""
        with pytest.raises((ValueError, TypeError)):
            orchestrator.execute({{}})
    
    def test_with_invalid_params(self, orchestrator):
        """Test execution with invalid parameters."""
        invalid_input = {{'invalid_param': 'invalid_value'}}
        # Should either raise or handle gracefully
        try:
            result = orchestrator.execute(invalid_input)
            assert result.status in ['error', 'failed', 'invalid']
        except (ValueError, TypeError):
            pass  # Expected behavior
    
    # Stage Tests
    {stage_tests_str}
    
    # Hook Tests
    {hook_tests_str}
    
    # Integration Tests
    
    def test_end_to_end_execution(self, orchestrator, sample_input):
        """Test complete end-to-end execution."""
        result = orchestrator.execute(sample_input)
        assert result is not None
        assert result.status in ['completed', 'success']
    
    def test_execution_with_context(self, orchestrator, sample_input, mock_context):
        """Test execution with custom context."""
        result = orchestrator.execute(sample_input, context=mock_context)
        assert result is not None
    
    # Error Handling Tests
    
    def test_error_recovery(self, orchestrator, sample_input):
        """Test error recovery mechanisms."""
        with patch.object(orchestrator, '_execute_stage', side_effect=Exception("Test error")):
            try:
                result = orchestrator.execute(sample_input)
                assert result.status in ['error', 'failed', 'recovered']
            except Exception:
                pass  # Error propagation is also valid
    
    def test_timeout_handling(self, orchestrator, sample_input):
        """Test timeout handling."""
        import time
        
        def slow_stage(*args, **kwargs):
            time.sleep(0.1)
            return {{'status': 'completed'}}
        
        with patch.object(orchestrator, '_execute_stage', side_effect=slow_stage):
            # Should complete or timeout gracefully
            try:
                result = orchestrator.execute(sample_input, timeout=0.01)
            except TimeoutError:
                pass  # Expected behavior


# Standalone test functions for pytest discovery

def test_{self._to_module_name(template_name)}_creation():
    """Test {template_name} orchestrator creation."""
    from cortex.orchestrators.factory import create_orchestrator
    orchestrator = create_orchestrator('{template_domain}')
    assert orchestrator is not None


def test_{self._to_module_name(template_name)}_basic():
    """Test {template_name} basic execution."""
    from cortex.orchestrators.factory import create_orchestrator
    orchestrator = create_orchestrator('{template_domain}')
    sample_input = {{
{fixtures_str}
    }}
    result = orchestrator.execute(sample_input)
    assert result is not None
'''
    
    def _render_documentation_template(
        self,
        template_name: str,
        template_domain: str,
        parameters: List[Dict[str, Any]],
        stages: List[Dict[str, Any]],
        hooks: Dict[str, Any],
        description: str,
        version: str,
    ) -> str:
        """Render documentation template."""
        # Generate parameters table
        params_table = "| Parameter | Type | Required | Default | Description |\n"
        params_table += "|-----------|------|----------|---------|-------------|\n"
        for param in parameters:
            required = "Yes" if param['required'] else "No"
            default = param.get('default', '-')
            desc = param.get('description', '-')
            params_table += f"| `{param['name']}` | {param['type']} | {required} | {default} | {desc} |\n"
        
        # Generate stages list
        stages_list = ""
        for i, stage in enumerate(stages, 1):
            stage_name = stage.get('name', f'Stage {i}')
            stage_desc = stage.get('description', 'No description')
            stages_list += f"{i}. **{stage_name}**: {stage_desc}\n"
        
        if not stages_list:
            stages_list = "No stages defined in template.\n"
        
        # Generate hooks list
        hooks_list = ""
        for hook_name, hook_config in hooks.items():
            hook_desc = hook_config.get('description', 'No description') if isinstance(hook_config, dict) else 'No description'
            hooks_list += f"- `{hook_name}`: {hook_desc}\n"
        
        if not hooks_list:
            hooks_list = "No hooks defined in template.\n"
        
        return f'''# {template_name}

> Domain: {template_domain} | Version: {version}

{description}

## Overview

This orchestrator is part of the **{template_domain}** domain and provides
automated workflow execution for related tasks.

## Installation

```bash
pip install cortex-orchestrators
```

## Quick Start

```python
from cortex.orchestrators.factory import create_orchestrator

# Create orchestrator
orchestrator = create_orchestrator('{template_domain}')

# Execute with parameters
result = orchestrator.execute({{
    # Add your parameters here
}})

print(result.status)
print(result.output)
```

## Parameters

{params_table}

## Execution Stages

{stages_list}

## Lifecycle Hooks

{hooks_list}

## CLI Usage

```bash
python -m cortex.cli {template_domain} \\
    --param1 value1 \\
    --param2 value2
```

## API Usage

```python
from cortex.tools import get_tool_generator
from cortex.tools.tool_generator import ToolType, GenerationConfig

# Generate API client
generator = get_tool_generator()()
config = GenerationConfig(tool_type=ToolType.API_CLIENT)
result = generator.generate(template, config)
```

## Error Handling

The orchestrator handles errors through the following mechanisms:

1. **Input Validation**: Parameters are validated before execution
2. **Stage Errors**: Individual stage failures are captured and reported
3. **Recovery Hooks**: Custom recovery logic can be registered

```python
orchestrator.register_hook('on_error', my_error_handler)
```

## Configuration

Configure the orchestrator through environment variables or config file:

```yaml
# config.yaml
orchestrator:
  domain: {template_domain}
  timeout: 30
  retry_count: 3
```

## See Also

- [CORTEX Orchestrator Overview](../README.md)
- [Domain Templates](../templates/{template_domain}.md)
- [API Reference](../api/orchestrators.md)

---

*Generated from template: {template_name} v{version}*
'''
    
    def _render_config_validator_template(
        self,
        class_name: str,
        template_name: str,
        parameters: List[Dict[str, Any]],
        config: GenerationConfig,
    ) -> str:
        """Render configuration validator template."""
        # Generate Pydantic fields
        fields = []
        for param in parameters:
            py_type = self._yaml_type_to_python(param['type'])
            if not param['required']:
                py_type = f"Optional[{py_type}]"
            default = param.get('default')
            if default is not None:
                default_str = f" = {repr(default)}"
            elif not param['required']:
                default_str = " = None"
            else:
                default_str = " = ..."
            
            desc = param.get('description', '')
            if desc:
                fields.append(f"    {param['name']}: {py_type}{default_str}  # {desc}")
            else:
                fields.append(f"    {param['name']}: {py_type}{default_str}")
        
        fields_str = '\n'.join(fields)
        
        return f'''"""
Configuration Validator for {template_name}
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, validator, root_validator


class {class_name}(BaseModel):
    """
    Configuration validator for {template_name}.
    
    Validates input parameters against the template schema.
    """
    
{fields_str}
    
    class Config:
        """Pydantic configuration."""
        extra = 'forbid'  # Reject unknown fields
        validate_assignment = True
    
    @root_validator
    def validate_all(cls, values: Dict[str, Any]) -> Dict[str, Any]:
        """Validate all values together."""
        # Add cross-field validation logic here
        return values
    
    def to_execution_config(self) -> Dict[str, Any]:
        """Convert to execution configuration dict."""
        return self.dict(exclude_none=True)


def validate_config(config: Dict[str, Any]) -> {class_name}:
    """
    Validate a configuration dictionary.
    
    Args:
        config: Configuration to validate
        
    Returns:
        Validated {class_name} instance
        
    Raises:
        ValidationError: If validation fails
    """
    return {class_name}(**config)


def is_valid_config(config: Dict[str, Any]) -> bool:
    """
    Check if configuration is valid without raising.
    
    Args:
        config: Configuration to check
        
    Returns:
        True if valid, False otherwise
    """
    try:
        {class_name}(**config)
        return True
    except Exception:
        return False


def get_validation_errors(config: Dict[str, Any]) -> List[str]:
    """
    Get validation errors for a configuration.
    
    Args:
        config: Configuration to validate
        
    Returns:
        List of error messages
    """
    try:
        {class_name}(**config)
        return []
    except Exception as e:
        if hasattr(e, 'errors'):
            return [err['msg'] for err in e.errors()]
        return [str(e)]
'''
    
    def _render_mock_service_template(
        self,
        class_name: str,
        template_name: str,
        stages: List[Dict[str, Any]],
        config: GenerationConfig,
    ) -> str:
        """Render mock service template."""
        # Generate stage mock methods
        stage_mocks = []
        for i, stage in enumerate(stages):
            stage_name = stage.get('name', f'stage_{i}')
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', stage_name)
            stage_mocks.append(f'''
    def mock_{safe_name}(self, *args, **kwargs) -> Dict[str, Any]:
        """Mock implementation of {stage_name} stage."""
        self._call_log.append(('{stage_name}', args, kwargs))
        return self._stage_responses.get('{stage_name}', {{'status': 'mocked'}})''')
        
        stage_mocks_str = '\n'.join(stage_mocks)
        
        return f'''"""
Mock Service for {template_name}
"""

from typing import Any, Callable, Dict, List, Optional, Tuple
from unittest.mock import MagicMock


class {class_name}:
    """
    Mock service for {template_name} testing.
    
    Provides configurable mock responses and call logging.
    
    Example:
        mock = {class_name}()
        mock.set_response('stage_1', {{'result': 'test'}})
        result = mock.execute({{'input': 'test'}})
    """
    
    def __init__(self):
        self._call_log: List[Tuple[str, tuple, dict]] = []
        self._stage_responses: Dict[str, Any] = {{}}
        self._error_stages: set = set()
        self._side_effects: Dict[str, Callable] = {{}}
    
    @property
    def call_log(self) -> List[Tuple[str, tuple, dict]]:
        """Get log of all calls made."""
        return self._call_log.copy()
    
    @property
    def call_count(self) -> int:
        """Get total number of calls."""
        return len(self._call_log)
    
    def set_response(self, stage: str, response: Any) -> None:
        """Set mock response for a stage."""
        self._stage_responses[stage] = response
    
    def set_error(self, stage: str, error: Optional[Exception] = None) -> None:
        """Configure a stage to raise an error."""
        self._error_stages.add(stage)
        if error:
            self._side_effects[stage] = lambda: (_ for _ in ()).throw(error)
    
    def set_side_effect(self, stage: str, effect: Callable) -> None:
        """Set a side effect function for a stage."""
        self._side_effects[stage] = effect
    
    def reset(self) -> None:
        """Reset all mock state."""
        self._call_log.clear()
        self._stage_responses.clear()
        self._error_stages.clear()
        self._side_effects.clear()
    
    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute mock orchestration."""
        self._call_log.append(('execute', (input_data,), {{}}))
        
        if 'execute' in self._error_stages:
            raise RuntimeError("Mock execution error")
        
        return {{
            'status': 'completed',
            'output': self._stage_responses.get('execute', {{'mocked': True}}),
            'stages_executed': list(self._stage_responses.keys()),
        }}
    
    def get_calls_for_stage(self, stage: str) -> List[Tuple[tuple, dict]]:
        """Get all calls for a specific stage."""
        return [(args, kwargs) for name, args, kwargs in self._call_log if name == stage]
    
    def assert_stage_called(self, stage: str, times: Optional[int] = None) -> None:
        """Assert a stage was called."""
        calls = self.get_calls_for_stage(stage)
        if times is not None:
            assert len(calls) == times, f"Stage '{{stage}}' called {{len(calls)}} times, expected {{times}}"
        else:
            assert len(calls) > 0, f"Stage '{{stage}}' was not called"
    
    def assert_stage_called_with(self, stage: str, **kwargs) -> None:
        """Assert a stage was called with specific kwargs."""
        calls = self.get_calls_for_stage(stage)
        for _, call_kwargs in calls:
            if all(call_kwargs.get(k) == v for k, v in kwargs.items()):
                return
        raise AssertionError(f"Stage '{{stage}}' not called with {{kwargs}}")
    {stage_mocks_str}
    
    def create_mock_orchestrator(self) -> MagicMock:
        """Create a MagicMock configured as an orchestrator."""
        mock = MagicMock()
        mock.execute = self.execute
        mock.domain = '{template_name}'
        return mock
'''
    
    def _render_integration_adapter_template(
        self,
        class_name: str,
        template_name: str,
        integrations: Dict[str, Any],
        config: GenerationConfig,
    ) -> str:
        """Render integration adapter template."""
        # Generate adapter methods
        adapter_methods = []
        for name, integration in integrations.items():
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
            adapter_methods.append(f'''
    def connect_{safe_name}(self, **kwargs) -> Any:
        """Connect to {name} integration."""
        config = self._integrations.get('{name}', {{}})
        config.update(kwargs)
        # Implementation depends on integration type
        return self._create_connection('{name}', config)
    
    def disconnect_{safe_name}(self) -> None:
        """Disconnect from {name} integration."""
        if '{name}' in self._connections:
            conn = self._connections.pop('{name}')
            if hasattr(conn, 'close'):
                conn.close()''')
        
        adapter_methods_str = '\n'.join(adapter_methods)
        
        return f'''"""
Integration Adapter for {template_name}
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class IntegrationAdapterBase(ABC):
    """Base class for integration adapters."""
    
    @abstractmethod
    def connect(self, name: str, **kwargs) -> Any:
        """Connect to an integration."""
        pass
    
    @abstractmethod
    def disconnect(self, name: str) -> None:
        """Disconnect from an integration."""
        pass
    
    @abstractmethod
    def is_connected(self, name: str) -> bool:
        """Check if connected to an integration."""
        pass


class {class_name}(IntegrationAdapterBase):
    """
    Integration adapter for {template_name}.
    
    Manages connections to external services and tools.
    
    Example:
        adapter = {class_name}()
        adapter.connect('database', host='localhost')
        result = adapter.query('database', 'SELECT * FROM table')
        adapter.disconnect('database')
    """
    
    def __init__(self, integrations: Optional[Dict[str, Any]] = None):
        self._integrations = integrations or {{}}
        self._connections: Dict[str, Any] = {{}}
    
    def connect(self, name: str, **kwargs) -> Any:
        """
        Connect to an integration.
        
        Args:
            name: Integration name
            **kwargs: Connection parameters
            
        Returns:
            Connection object
        """
        if name in self._connections:
            return self._connections[name]
        
        config = self._integrations.get(name, {{}})
        config.update(kwargs)
        
        conn = self._create_connection(name, config)
        self._connections[name] = conn
        return conn
    
    def disconnect(self, name: str) -> None:
        """
        Disconnect from an integration.
        
        Args:
            name: Integration name
        """
        if name in self._connections:
            conn = self._connections.pop(name)
            if hasattr(conn, 'close'):
                conn.close()
    
    def is_connected(self, name: str) -> bool:
        """
        Check if connected to an integration.
        
        Args:
            name: Integration name
            
        Returns:
            True if connected
        """
        return name in self._connections
    
    def get_connection(self, name: str) -> Optional[Any]:
        """Get an existing connection."""
        return self._connections.get(name)
    
    def _create_connection(self, name: str, config: Dict[str, Any]) -> Any:
        """Create a connection based on configuration."""
        # Override in subclass for specific connection logic
        return {{'name': name, 'config': config, 'connected': True}}
    
    def disconnect_all(self) -> None:
        """Disconnect from all integrations."""
        for name in list(self._connections.keys()):
            self.disconnect(name)
    {adapter_methods_str}
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.disconnect_all()
'''
    
    def _python_type_to_click(self, type_str: str) -> str:
        """Convert Python type to Click type."""
        type_map = {
            'str': 'str',
            'string': 'str',
            'int': 'int',
            'integer': 'int',
            'float': 'float',
            'number': 'float',
            'bool': 'bool',
            'boolean': 'bool',
        }
        return type_map.get(type_str.lower(), 'str')
    
    def _yaml_type_to_python(self, type_str: str) -> str:
        """Convert YAML type to Python type."""
        type_map = {
            'str': 'str',
            'string': 'str',
            'int': 'int',
            'integer': 'int',
            'float': 'float',
            'number': 'float',
            'bool': 'bool',
            'boolean': 'bool',
            'list': 'List[Any]',
            'array': 'List[Any]',
            'dict': 'Dict[str, Any]',
            'object': 'Dict[str, Any]',
        }
        return type_map.get(type_str.lower(), 'Any')
