"""
Orchestrator Scaffolder (AC-TT-002-01)

Core scaffolding functionality for generating orchestrators from templates.
Generates complete Python orchestrator implementations including:
- Main orchestrator class
- Stage handlers
- Hook implementations
- Integration adapters
- Test files
- Configuration files

This is the primary tool for creating new orchestrators.
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Union

import yaml

from cortex.tools.template_parser import ParsedTemplate, TemplateParser


class ScaffoldType(Enum):
    """Types of scaffold outputs."""
    ORCHESTRATOR = auto()
    TEST = auto()
    CONFIG = auto()
    INTEGRATION = auto()
    FULL = auto()


@dataclass
class ScaffoldConfig:
    """Configuration for scaffolding."""
    output_dir: Path = field(default_factory=lambda: Path("src/orchestrators"))
    domain: str = "general"
    tier: int = 1
    include_tests: bool = True
    include_config: bool = True
    include_integrations: bool = True
    scaffold_type: ScaffoldType = ScaffoldType.FULL

    # Code generation options
    type_hints: bool = True
    docstrings: bool = True
    async_support: bool = False

    # Naming conventions
    class_suffix: str = "Orchestrator"
    test_prefix: str = "test_"
    config_suffix: str = "_config"

    # File options
    overwrite: bool = False
    dry_run: bool = False


@dataclass
class ScaffoldedFile:
    """A scaffolded file."""
    path: Path
    content: str
    file_type: str  # 'orchestrator', 'test', 'config', etc.
    generated_at: datetime = field(default_factory=datetime.now)

    def write(self, base_dir: Optional[Path] = None) -> Path:
        """Write file to disk."""
        output_path = base_dir / self.path if base_dir else self.path
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(self.content)
        return output_path

    @property
    def line_count(self) -> int:
        """Get number of lines in file."""
        return len(self.content.splitlines())


@dataclass
class ScaffoldResult:
    """Result of scaffolding operation."""
    success: bool
    files: List[ScaffoldedFile] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def add_file(self, file: ScaffoldedFile) -> None:
        """Add a scaffolded file."""
        self.files.append(file)

    def add_error(self, message: str) -> None:
        """Add an error."""
        self.errors.append(message)
        self.success = False

    def add_warning(self, message: str) -> None:
        """Add a warning."""
        self.warnings.append(message)

    @property
    def total_lines(self) -> int:
        """Get total lines of generated code."""
        return sum(f.line_count for f in self.files)

    def write_all(self, base_dir: Optional[Path] = None) -> List[Path]:
        """Write all files to disk."""
        written = []
        for f in self.files:
            path = f.write(base_dir)
            written.append(path)
        return written


class OrchestratorScaffolder:
    """
    Scaffolder for creating orchestrator implementations.

    Generates complete Python orchestrator code from templates.

    Example:
        scaffolder = OrchestratorScaffolder()

        # From template file
        result = scaffolder.scaffold_from_file("templates/planning.yaml")

        # From parsed template
        parser = TemplateParser()
        template = parser.parse_file("templates/planning.yaml")
        result = scaffolder.scaffold(template)

        # Write files
        result.write_all(Path("output"))
    """

    def __init__(self, parser: Optional[TemplateParser] = None):
        """
        Initialize scaffolder.

        Args:
            parser: TemplateParser instance (creates one if not provided)
        """
        self.parser = parser or TemplateParser()

    def scaffold_from_file(
        self,
        template_path: Union[str, Path],
        config: Optional[ScaffoldConfig] = None,
    ) -> ScaffoldResult:
        """
        Scaffold from a template file.

        Args:
            template_path: Path to template YAML file
            config: Scaffolding configuration

        Returns:
            ScaffoldResult with generated files
        """
        config = config or ScaffoldConfig()

        try:
            template = self.parser.parse_file(template_path)
        except Exception as e:
            result = ScaffoldResult(success=False)
            result.add_error(f"Failed to parse template: {e}")
            return result

        return self.scaffold(template, config)

    def scaffold_from_dict(
        self,
        template_dict: Dict[str, Any],
        config: Optional[ScaffoldConfig] = None,
    ) -> ScaffoldResult:
        """
        Scaffold from a template dictionary.

        Args:
            template_dict: Template as dictionary
            config: Scaffolding configuration

        Returns:
            ScaffoldResult with generated files
        """
        config = config or ScaffoldConfig()

        try:
            yaml_str = yaml.dump(template_dict)
            template = self.parser.parse_string(yaml_str)
        except Exception as e:
            result = ScaffoldResult(success=False)
            result.add_error(f"Failed to parse template dict: {e}")
            return result

        return self.scaffold(template, config)

    def scaffold(
        self,
        template: ParsedTemplate,
        config: Optional[ScaffoldConfig] = None,
    ) -> ScaffoldResult:
        """
        Scaffold orchestrator from parsed template.

        Args:
            template: ParsedTemplate to scaffold from
            config: Scaffolding configuration

        Returns:
            ScaffoldResult with generated files
        """
        config = config or ScaffoldConfig()
        config.domain = template.domain or config.domain

        result = ScaffoldResult(success=True)
        result.metadata = {
            'template_name': template.name,
            'template_domain': template.domain,
            'template_version': template.version,
            'scaffold_type': config.scaffold_type.name,
            'generated_at': datetime.now().isoformat(),
        }

        # Validate template
        validation = self.parser.validate(template)
        if not validation.valid:
            for error in validation.errors:
                result.add_error(error)
            return result

        for warning in validation.warnings:
            result.add_warning(warning)

        # Generate based on scaffold type
        if config.scaffold_type in (ScaffoldType.ORCHESTRATOR, ScaffoldType.FULL):
            self._scaffold_orchestrator(template, config, result)

        if config.scaffold_type in (ScaffoldType.TEST, ScaffoldType.FULL) and config.include_tests:
            self._scaffold_tests(template, config, result)

        if config.scaffold_type in (ScaffoldType.CONFIG, ScaffoldType.FULL) and config.include_config:
            self._scaffold_config(template, config, result)

        if config.scaffold_type in (ScaffoldType.INTEGRATION, ScaffoldType.FULL) and config.include_integrations:
            self._scaffold_integrations(template, config, result)

        return result

    def _scaffold_orchestrator(
        self,
        template: ParsedTemplate,
        config: ScaffoldConfig,
        result: ScaffoldResult,
    ) -> None:
        """Generate main orchestrator file."""
        class_name = self._to_class_name(template.name) + config.class_suffix
        module_name = self._to_module_name(template.name)

        # Extract template components
        params = self._get_parameters(template)
        stages = self._get_stages(template)
        hooks = self._get_hooks(template)

        # Generate code
        code = self._render_orchestrator(
            class_name=class_name,
            template=template,
            params=params,
            stages=stages,
            hooks=hooks,
            config=config,
        )

        # Create file
        file_path = Path(f"{config.domain}/{module_name}.py")
        scaffolded = ScaffoldedFile(
            path=file_path,
            content=code,
            file_type='orchestrator',
        )
        result.add_file(scaffolded)

    def _scaffold_tests(
        self,
        template: ParsedTemplate,
        config: ScaffoldConfig,
        result: ScaffoldResult,
    ) -> None:
        """Generate test file."""
        class_name = self._to_class_name(template.name) + config.class_suffix
        test_class_name = f"Test{class_name}"
        module_name = self._to_module_name(template.name)

        params = self._get_parameters(template)
        stages = self._get_stages(template)

        code = self._render_tests(
            class_name=class_name,
            test_class_name=test_class_name,
            template=template,
            params=params,
            stages=stages,
            config=config,
        )

        file_path = Path(f"tests/{config.domain}/{config.test_prefix}{module_name}.py")
        scaffolded = ScaffoldedFile(
            path=file_path,
            content=code,
            file_type='test',
        )
        result.add_file(scaffolded)

    def _scaffold_config(
        self,
        template: ParsedTemplate,
        config: ScaffoldConfig,
        result: ScaffoldResult,
    ) -> None:
        """Generate configuration file."""
        module_name = self._to_module_name(template.name)

        config_content = self._render_config(template, config)

        file_path = Path(f"config/{config.domain}/{module_name}{config.config_suffix}.yaml")
        scaffolded = ScaffoldedFile(
            path=file_path,
            content=config_content,
            file_type='config',
        )
        result.add_file(scaffolded)

    def _scaffold_integrations(
        self,
        template: ParsedTemplate,
        config: ScaffoldConfig,
        result: ScaffoldResult,
    ) -> None:
        """Generate integration adapter if integrations defined."""
        integrations = self._get_integrations(template)
        if not integrations:
            return

        class_name = self._to_class_name(template.name) + "IntegrationAdapter"
        module_name = self._to_module_name(template.name) + "_integrations"

        code = self._render_integrations(
            class_name=class_name,
            template=template,
            integrations=integrations,
            config=config,
        )

        file_path = Path(f"{config.domain}/integrations/{module_name}.py")
        scaffolded = ScaffoldedFile(
            path=file_path,
            content=code,
            file_type='integration',
        )
        result.add_file(scaffolded)

    # Rendering methods

    def _render_orchestrator(
        self,
        class_name: str,
        template: ParsedTemplate,
        params: List[Dict[str, Any]],
        stages: List[Dict[str, Any]],
        hooks: Dict[str, Any],
        config: ScaffoldConfig,
    ) -> str:
        """Render orchestrator Python code."""
        # Generate parameter dataclass
        param_fields = []
        for param in params:
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
            param_fields.append(f"    {param['name']}: {py_type}{default_str}")

        param_fields_str = '\n'.join(param_fields) if param_fields else "    pass"

        # Generate stage methods
        stage_methods = []
        for i, stage in enumerate(stages):
            stage_name = stage.get('name', f'stage_{i}')
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', stage_name)
            stage_desc = stage.get('description', f'Execute {stage_name}')

            if config.async_support:
                stage_methods.append(f'''
    async def _execute_{safe_name}(self, context: ExecutionContext) -> StageResult:
        """
        {stage_desc}

        Args:
            context: Current execution context

        Returns:
            StageResult with stage output
        """
        self._log_stage_start('{stage_name}')

        try:
            # Stage implementation
            result = await self._process_{safe_name}(context)

            self._log_stage_complete('{stage_name}')
            return StageResult(
                stage='{stage_name}',
                status='completed',
                output=result,
            )
        except Exception as e:
            self._log_stage_error('{stage_name}', e)
            return StageResult(
                stage='{stage_name}',
                status='failed',
                error=str(e),
            )

    async def _process_{safe_name}(self, context: ExecutionContext) -> Dict[str, Any]:
        """Process {stage_name} stage logic."""
        # TODO: Implement stage logic
        return {{'processed': True}}''')
            else:
                stage_methods.append(f'''
    def _execute_{safe_name}(self, context: ExecutionContext) -> StageResult:
        """
        {stage_desc}

        Args:
            context: Current execution context

        Returns:
            StageResult with stage output
        """
        self._log_stage_start('{stage_name}')

        try:
            # Stage implementation
            result = self._process_{safe_name}(context)

            self._log_stage_complete('{stage_name}')
            return StageResult(
                stage='{stage_name}',
                status='completed',
                output=result,
            )
        except Exception as e:
            self._log_stage_error('{stage_name}', e)
            return StageResult(
                stage='{stage_name}',
                status='failed',
                error=str(e),
            )

    def _process_{safe_name}(self, context: ExecutionContext) -> Dict[str, Any]:
        """Process {stage_name} stage logic."""
        # TODO: Implement stage logic
        return {{'processed': True}}''')

        stage_methods_str = '\n'.join(stage_methods)

        # Generate hook methods
        hook_methods = []
        for hook_name, hook_config in hooks.items():
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', hook_name)
            hook_desc = hook_config.get('description', f'{hook_name} hook') if isinstance(hook_config, dict) else f'{hook_name} hook'

            hook_methods.append(f'''
    def _hook_{safe_name}(self, context: ExecutionContext, **kwargs) -> None:
        """
        {hook_desc}

        Args:
            context: Current execution context
            **kwargs: Additional hook arguments
        """
        for callback in self._hooks.get('{hook_name}', []):
            try:
                callback(context, **kwargs)
            except Exception as e:
                self._log_hook_error('{hook_name}', e)''')

        hook_methods_str = '\n'.join(hook_methods)

        # Generate stage list for pipeline
        stage_names = [stage.get('name', f'stage_{i}') for i, stage in enumerate(stages)]
        stage_list = [f"'{name}'" for name in stage_names]
        stage_list_str = ', '.join(stage_list)

        # Generate stage dispatch
        stage_dispatch = []
        for stage in stages:
            stage_name = stage.get('name', 'unknown')
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', stage_name)
            stage_dispatch.append(f"            '{stage_name}': self._execute_{safe_name},")
        stage_dispatch_str = '\n'.join(stage_dispatch)

        async_prefix = "async " if config.async_support else ""
        await_prefix = "await " if config.async_support else ""

        return f'''"""
{template.name} Orchestrator
Domain: {template.domain}
Version: {template.version}

{template.description}

Generated by CORTEX OrchestratorScaffolder
Generated at: {datetime.now().isoformat()}
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Callable, Dict, List, Optional, Set
import logging

from cortex.orchestrators.base import BaseOrchestrator, ExecutionContext, ExecutionResult
from cortex.orchestrators.stages import StageResult


# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class {class_name}Params:
    """Parameters for {template.name} orchestrator."""
{param_fields_str}


class {class_name}(BaseOrchestrator):
    """
    {template.description}

    Domain: {template.domain}
    Version: {template.version}
    Tier: {config.tier}

    Stages:
        {', '.join(stage_names) if stage_names else 'No stages defined'}

    Example:
        orchestrator = {class_name}()
        params = {class_name}Params(...)
        result = orchestrator.execute(params)
    """

    DOMAIN = '{template.domain}'
    VERSION = '{template.version}'
    STAGES = [{stage_list_str}]

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize orchestrator.

        Args:
            config: Optional configuration overrides
        """
        super().__init__(config)
        self._hooks: Dict[str, List[Callable]] = {{}}
        self._stage_handlers: Dict[str, Callable] = {{
{stage_dispatch_str}
        }}

    @property
    def domain(self) -> str:
        """Get orchestrator domain."""
        return self.DOMAIN

    @property
    def version(self) -> str:
        """Get orchestrator version."""
        return self.VERSION

    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """
        Register a hook callback.

        Args:
            hook_name: Name of hook to register for
            callback: Callback function
        """
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)

    def unregister_hook(self, hook_name: str, callback: Callable) -> None:
        """
        Unregister a hook callback.

        Args:
            hook_name: Name of hook
            callback: Callback to remove
        """
        if hook_name in self._hooks and callback in self._hooks[hook_name]:
            self._hooks[hook_name].remove(callback)

    {async_prefix}def execute(
        self,
        params: {class_name}Params | Dict[str, Any],
        context: Optional[ExecutionContext] = None,
        **kwargs,
    ) -> ExecutionResult:
        """
        Execute the orchestrator.

        Args:
            params: Execution parameters
            context: Optional execution context
            **kwargs: Additional execution options

        Returns:
            ExecutionResult with execution outcome
        """
        # Convert dict to params if needed
        if isinstance(params, dict):
            params = {class_name}Params(**params)

        # Create context
        context = context or ExecutionContext(
            orchestrator=self.DOMAIN,
            params=params.__dict__,
            started_at=datetime.now(),
        )

        # Execute pre hooks
        self._hook_pre_execute(context)

        try:
            # Execute pipeline
            results = {await_prefix}self._execute_pipeline(context)

            # Build result
            execution_result = ExecutionResult(
                status='completed',
                output=self._aggregate_results(results),
                stages=results,
                context=context,
            )

            # Execute success hooks
            self._hook_on_success(context, result=execution_result)

        except Exception as e:
            logger.exception(f"Execution failed: {{e}}")
            execution_result = ExecutionResult(
                status='failed',
                error=str(e),
                context=context,
            )

            # Execute error hooks
            self._hook_on_error(context, error=e)

        # Execute post hooks
        self._hook_post_execute(context, result=execution_result)

        return execution_result

    {async_prefix}def _execute_pipeline(self, context: ExecutionContext) -> List[StageResult]:
        """Execute the stage pipeline."""
        results = []

        for stage_name in self.STAGES:
            handler = self._stage_handlers.get(stage_name)
            if handler:
                result = {await_prefix}handler(context)
                results.append(result)

                # Update context with stage result
                context.stage_results[stage_name] = result

                # Stop on failure unless configured otherwise
                if result.status == 'failed' and not self._config.get('continue_on_error'):
                    break

        return results

    def _aggregate_results(self, results: List[StageResult]) -> Dict[str, Any]:
        """Aggregate stage results into final output."""
        output = {{}}
        for result in results:
            if result.output:
                output[result.stage] = result.output
        return output

    # Logging helpers

    def _log_stage_start(self, stage: str) -> None:
        """Log stage start."""
        logger.info(f"Starting stage: {{stage}}")

    def _log_stage_complete(self, stage: str) -> None:
        """Log stage completion."""
        logger.info(f"Completed stage: {{stage}}")

    def _log_stage_error(self, stage: str, error: Exception) -> None:
        """Log stage error."""
        logger.error(f"Stage {{stage}} failed: {{error}}")

    def _log_hook_error(self, hook: str, error: Exception) -> None:
        """Log hook error."""
        logger.warning(f"Hook {{hook}} error: {{error}}")

    # Stage implementations
    {stage_methods_str}

    # Hook implementations
    {hook_methods_str}

    def _hook_pre_execute(self, context: ExecutionContext) -> None:
        """Pre-execution hook."""
        for callback in self._hooks.get('pre_execute', []):
            try:
                callback(context)
            except Exception as e:
                self._log_hook_error('pre_execute', e)

    def _hook_post_execute(self, context: ExecutionContext, **kwargs) -> None:
        """Post-execution hook."""
        for callback in self._hooks.get('post_execute', []):
            try:
                callback(context, **kwargs)
            except Exception as e:
                self._log_hook_error('post_execute', e)

    def _hook_on_success(self, context: ExecutionContext, **kwargs) -> None:
        """Success hook."""
        for callback in self._hooks.get('on_success', []):
            try:
                callback(context, **kwargs)
            except Exception as e:
                self._log_hook_error('on_success', e)

    def _hook_on_error(self, context: ExecutionContext, **kwargs) -> None:
        """Error hook."""
        for callback in self._hooks.get('on_error', []):
            try:
                callback(context, **kwargs)
            except Exception as e:
                self._log_hook_error('on_error', e)


# Factory registration
def register_orchestrator():
    """Register this orchestrator with the factory."""
    from cortex.orchestrators.factory import OrchestratorRegistry
    OrchestratorRegistry.register('{template.domain}', {class_name})


# Auto-register on import
try:
    register_orchestrator()
except ImportError:
    pass  # Factory not available
'''

    def _render_tests(
        self,
        class_name: str,
        test_class_name: str,
        template: ParsedTemplate,
        params: List[Dict[str, Any]],
        stages: List[Dict[str, Any]],
        config: ScaffoldConfig,
    ) -> str:
        """Render test file."""
        module_name = self._to_module_name(template.name)

        # Generate sample params
        sample_params = []
        for param in params:
            value = param.get('default')
            if value is None:
                if param['type'] in ('str', 'string'):
                    value = "'test_value'"
                elif param['type'] in ('int', 'integer'):
                    value = "1"
                elif param['type'] in ('float', 'number'):
                    value = "1.0"
                elif param['type'] in ('bool', 'boolean'):
                    value = "True"
                else:
                    value = "None"
            else:
                value = repr(value)
            sample_params.append(f"        {param['name']}={value},")

        sample_params_str = '\n'.join(sample_params) if sample_params else "        # No parameters"

        # Generate stage tests
        stage_tests = []
        for i, stage in enumerate(stages):
            stage_name = stage.get('name', f'stage_{i}')
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', stage_name)
            stage_tests.append(f'''
    def test_stage_{safe_name}(self, orchestrator, sample_params):
        """Test {stage_name} stage."""
        from cortex.orchestrators.base import ExecutionContext

        context = ExecutionContext(
            orchestrator=orchestrator.domain,
            params=sample_params.__dict__,
        )

        result = orchestrator._execute_{safe_name}(context)

        assert result is not None
        assert result.stage == '{stage_name}'
        assert result.status in ('completed', 'success', 'failed')''')

        stage_tests_str = '\n'.join(stage_tests) if stage_tests else '''
    def test_stages_placeholder(self, orchestrator):
        """Placeholder for when no stages defined."""
        pass'''

        return f'''"""
Tests for {class_name}
Domain: {template.domain}

Generated by CORTEX OrchestratorScaffolder
"""

import pytest
from unittest.mock import MagicMock, patch
from typing import Any, Dict

from cortex.orchestrators.{config.domain}.{module_name} import {class_name}, {class_name}Params


class {test_class_name}:
    """Test suite for {class_name}."""

    @pytest.fixture
    def orchestrator(self):
        """Create orchestrator instance."""
        return {class_name}()

    @pytest.fixture
    def sample_params(self) -> {class_name}Params:
        """Sample parameters for testing."""
        return {class_name}Params(
{sample_params_str}
        )

    @pytest.fixture
    def mock_context(self):
        """Mock execution context."""
        return MagicMock()

    # Creation Tests

    def test_creation(self, orchestrator):
        """Test orchestrator can be created."""
        assert orchestrator is not None
        assert orchestrator.domain == '{template.domain}'
        assert orchestrator.version == '{template.version}'

    def test_stages_defined(self, orchestrator):
        """Test stages are defined."""
        assert hasattr(orchestrator, 'STAGES')
        assert isinstance(orchestrator.STAGES, (list, tuple))

    # Execution Tests

    def test_basic_execution(self, orchestrator, sample_params):
        """Test basic execution."""
        result = orchestrator.execute(sample_params)

        assert result is not None
        assert hasattr(result, 'status')
        assert result.status in ('completed', 'success', 'failed')

    def test_execution_with_dict(self, orchestrator, sample_params):
        """Test execution with dict params."""
        params_dict = sample_params.__dict__
        result = orchestrator.execute(params_dict)

        assert result is not None

    def test_execution_with_context(self, orchestrator, sample_params, mock_context):
        """Test execution with custom context."""
        result = orchestrator.execute(sample_params, context=mock_context)

        assert result is not None

    # Stage Tests
    {stage_tests_str}

    # Hook Tests

    def test_register_hook(self, orchestrator):
        """Test hook registration."""
        callback = MagicMock()
        orchestrator.register_hook('pre_execute', callback)

        assert 'pre_execute' in orchestrator._hooks
        assert callback in orchestrator._hooks['pre_execute']

    def test_unregister_hook(self, orchestrator):
        """Test hook unregistration."""
        callback = MagicMock()
        orchestrator.register_hook('pre_execute', callback)
        orchestrator.unregister_hook('pre_execute', callback)

        assert callback not in orchestrator._hooks.get('pre_execute', [])

    def test_pre_execute_hook_called(self, orchestrator, sample_params):
        """Test pre_execute hook is called."""
        callback = MagicMock()
        orchestrator.register_hook('pre_execute', callback)

        orchestrator.execute(sample_params)

        callback.assert_called()

    def test_post_execute_hook_called(self, orchestrator, sample_params):
        """Test post_execute hook is called."""
        callback = MagicMock()
        orchestrator.register_hook('post_execute', callback)

        orchestrator.execute(sample_params)

        callback.assert_called()

    # Error Handling Tests

    def test_error_handling(self, orchestrator, sample_params):
        """Test error handling."""
        with patch.object(orchestrator, '_execute_pipeline', side_effect=Exception("Test error")):
            result = orchestrator.execute(sample_params)

            assert result.status == 'failed'
            assert 'Test error' in str(result.error)

    def test_on_error_hook_called(self, orchestrator, sample_params):
        """Test on_error hook is called on failure."""
        callback = MagicMock()
        orchestrator.register_hook('on_error', callback)

        with patch.object(orchestrator, '_execute_pipeline', side_effect=Exception("Test error")):
            orchestrator.execute(sample_params)

        callback.assert_called()


# Standalone tests for pytest discovery

def test_{module_name}_creation():
    """Test {class_name} creation."""
    orchestrator = {class_name}()
    assert orchestrator is not None
    assert orchestrator.domain == '{template.domain}'


def test_{module_name}_params():
    """Test {class_name}Params creation."""
    params = {class_name}Params(
{sample_params_str}
    )
    assert params is not None
'''

    def _render_config(self, template: ParsedTemplate, config: ScaffoldConfig) -> str:
        """Render configuration YAML."""
        params = self._get_parameters(template)
        stages = self._get_stages(template)

        # Build config structure
        config_dict = {
            'orchestrator': {
                'name': template.name,
                'domain': template.domain,
                'version': template.version,
                'tier': config.tier,
            },
            'parameters': {},
            'stages': {
                'enabled': [s.get('name', f'stage_{i}') for i, s in enumerate(stages)],
                'parallel': False,
                'continue_on_error': False,
            },
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
            'timeouts': {
                'execution': 300,
                'stage': 60,
            },
        }

        # Add parameter defaults
        for param in params:
            if param.get('default') is not None:
                config_dict['parameters'][param['name']] = param['default']

        return yaml.dump(config_dict, default_flow_style=False, sort_keys=False)

    def _render_integrations(
        self,
        class_name: str,
        template: ParsedTemplate,
        integrations: Dict[str, Any],
        config: ScaffoldConfig,
    ) -> str:
        """Render integrations adapter."""
        module_name = self._to_module_name(template.name)

        # Generate adapter methods
        adapter_methods = []
        for name, integration_config in integrations.items():
            safe_name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
            adapter_methods.append(f'''
    def get_{safe_name}(self) -> Any:
        """Get {name} integration."""
        return self._get_or_create('{name}')''')

        adapter_methods_str = '\n'.join(adapter_methods)

        return f'''"""
Integration Adapter for {template.name}
Domain: {template.domain}

Generated by CORTEX OrchestratorScaffolder
"""

from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class {class_name}:
    """
    Integration adapter for {template.name}.

    Manages external service connections.
    """

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config or {{}}
        self._connections: Dict[str, Any] = {{}}

    def _get_or_create(self, name: str) -> Any:
        """Get or create a connection."""
        if name not in self._connections:
            self._connections[name] = self._create_connection(name)
        return self._connections[name]

    def _create_connection(self, name: str) -> Any:
        """Create a new connection."""
        # Override in subclass for specific implementations
        integration_config = self._config.get(name, {{}})
        return {{'name': name, 'config': integration_config}}

    def close_all(self) -> None:
        """Close all connections."""
        for name, conn in self._connections.items():
            try:
                if hasattr(conn, 'close'):
                    conn.close()
            except Exception as e:
                logger.warning(f"Error closing {{name}}: {{e}}")
        self._connections.clear()
    {adapter_methods_str}

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close_all()
'''

    # Helper methods

    def _to_class_name(self, name: str) -> str:
        """Convert name to PascalCase class name."""
        parts = re.split(r'[-_\s]+', name)
        return ''.join(part.capitalize() for part in parts)

    def _to_module_name(self, name: str) -> str:
        """Convert name to snake_case module name."""
        name = re.sub(r'[-\s]+', '_', name.lower())
        name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name).lower()
        return name

    def _get_parameters(self, template: ParsedTemplate) -> List[Dict[str, Any]]:
        """Extract parameters from template."""
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
        """Extract stages from template."""
        stages_section = template.get_section('stages')
        if stages_section:
            return stages_section.content.get('stages', [])
        return []

    def _get_hooks(self, template: ParsedTemplate) -> Dict[str, Any]:
        """Extract hooks from template."""
        hooks_section = template.get_section('hooks')
        if hooks_section:
            return hooks_section.content
        return {}

    def _get_integrations(self, template: ParsedTemplate) -> Dict[str, Any]:
        """Extract integrations from template."""
        integrations_section = template.get_section('integrations')
        if integrations_section:
            return integrations_section.content
        return {}

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
