"""
Scaffolder Templates (AC-TT-002-02)

Template definitions for orchestrator scaffolding.
Provides reusable templates for:
- Base orchestrator structure
- Test structure
- Configuration structure
- Integration adapters

These templates are used by OrchestratorScaffolder.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable
from datetime import datetime


class TemplateType(Enum):
    """Types of scaffolder templates."""
    BASE = auto()
    ORCHESTRATOR = auto()
    TEST = auto()
    CONFIG = auto()
    INTEGRATION = auto()
    DOCUMENTATION = auto()
    CLI = auto()


@dataclass
class TemplateVariable:
    """A variable in a template."""
    name: str
    type: str
    required: bool = True
    default: Any = None
    description: str = ""
    
    def resolve(self, context: Dict[str, Any]) -> Any:
        """Resolve variable value from context."""
        if self.name in context:
            return context[self.name]
        if not self.required:
            return self.default
        raise ValueError(f"Required variable '{self.name}' not in context")


@dataclass
class TemplateBlock:
    """A block of content in a template."""
    name: str
    content: str
    condition: Optional[str] = None  # Condition for including block
    indent: int = 0
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render block with context."""
        if self.condition:
            # Safely evaluate condition without eval()
            try:
                if not self._evaluate_condition(self.condition, context):
                    return ""
            except Exception:
                return ""
        
        content = self._interpolate(self.content, context)
        if self.indent > 0:
            lines = content.split('\n')
            indent_str = ' ' * self.indent
            content = '\n'.join(indent_str + line if line.strip() else line for line in lines)
        return content
    
    @staticmethod
    def _evaluate_condition(condition: str, context: Dict[str, Any]) -> bool:
        """Safely evaluate a condition expression without eval().
        
        Supports simple boolean logic:
        - Variable references: {key_name}
        - Comparisons: ==, !=, <, >, <=, >=
        - Boolean operators: and, or, not
        - Parentheses for grouping
        
        Args:
            condition: Condition string (e.g., "has_tests and is_core")
            context: Context dict with variable values
            
        Returns:
            Boolean result of condition evaluation
            
        Raises:
            ValueError: If condition syntax is invalid or contains disallowed operations
        """
        import re
        
        # Disallow dangerous operations
        dangerous_patterns = [
            r'__',  # Dunder attributes
            r'import',
            r'exec',
            r'eval',
            r'compile',
            r'open',
            r'file',
        ]
        for pattern in dangerous_patterns:
            if re.search(pattern, condition, re.IGNORECASE):
                raise ValueError(f"Condition contains disallowed operation: {pattern}")
        
        # Replace context variables with their values (quoted for strings)
        def replace_var(match):
            var_name = match.group(1)
            if var_name not in context:
                return "False"  # Missing var = False
            value = context[var_name]
            
            if isinstance(value, bool):
                return str(value)
            elif isinstance(value, (int, float)):
                return str(value)
            elif isinstance(value, str):
                return repr(value)
            elif value is None:
                return "None"
            elif isinstance(value, list):
                return f"len({repr(value)}) > 0"
            else:
                return "True"  # Non-falsy objects
        
        # Replace {var_name} patterns with values
        safe_condition = re.sub(r'\{\s*(\w+)\s*\}', replace_var, condition)
        
        # Only allow safe Python boolean expressions
        allowed_names = {'True', 'False', 'None', 'and', 'or', 'not', 'len'}
        # Check that only allowed names/operators are used
        identifiers = set(re.findall(r'\b([a-zA-Z_]\w*)\b', safe_condition))
        disallowed = identifiers - allowed_names - set(str(i) for i in range(10))
        if disallowed:
            raise ValueError(f"Condition contains disallowed identifiers: {disallowed}")
        
        # Safely evaluate the condition using compile + limited namespace
        try:
            code = compile(safe_condition, '<condition>', 'eval')
            result = eval(code, {'__builtins__': {}, 'len': len}, {})
            return bool(result)
        except SyntaxError as e:
            raise ValueError(f"Invalid condition syntax: {e}")
    
    def _interpolate(self, text: str, context: Dict[str, Any]) -> str:
        """Interpolate variables in text."""
        import re
        pattern = r'\{\{\s*(\w+(?:\.\w+)*)\s*\}\}'
        
        def replace(match):
            path = match.group(1).split('.')
            value = context
            for key in path:
                if isinstance(value, dict):
                    value = value.get(key, match.group(0))
                else:
                    return match.group(0)
            return str(value)
        
        return re.sub(pattern, replace, text)


class ScaffolderTemplate(ABC):
    """Base class for scaffolder templates."""
    
    template_type: TemplateType = TemplateType.BASE
    
    def __init__(self):
        self._variables: Dict[str, TemplateVariable] = {}
        self._blocks: Dict[str, TemplateBlock] = {}
        self._setup()
    
    @abstractmethod
    def _setup(self) -> None:
        """Set up template variables and blocks."""
        pass
    
    @abstractmethod
    def render(self, context: Dict[str, Any]) -> str:
        """Render the template with context."""
        pass
    
    def add_variable(self, variable: TemplateVariable) -> None:
        """Add a variable to the template."""
        self._variables[variable.name] = variable
    
    def add_block(self, block: TemplateBlock) -> None:
        """Add a block to the template."""
        self._blocks[block.name] = block
    
    def get_required_variables(self) -> List[str]:
        """Get list of required variable names."""
        return [v.name for v in self._variables.values() if v.required]
    
    def validate_context(self, context: Dict[str, Any]) -> List[str]:
        """Validate that context has all required variables."""
        missing = []
        for var in self._variables.values():
            if var.required and var.name not in context:
                missing.append(var.name)
        return missing


class BaseTemplate(ScaffolderTemplate):
    """Base template with common structure."""
    
    template_type = TemplateType.BASE
    
    def _setup(self) -> None:
        """Set up base variables."""
        self.add_variable(TemplateVariable(
            name='module_name',
            type='str',
            required=True,
            description='Name of the module',
        ))
        self.add_variable(TemplateVariable(
            name='author',
            type='str',
            required=False,
            default='CORTEX Generator',
            description='Author name',
        ))
        self.add_variable(TemplateVariable(
            name='version',
            type='str',
            required=False,
            default='1.0.0',
            description='Module version',
        ))
        
        self.add_block(TemplateBlock(
            name='header',
            content='''"""
{{ module_name }}

Author: {{ author }}
Version: {{ version }}
Generated: {{ generated_at }}
"""
''',
        ))
        
        self.add_block(TemplateBlock(
            name='imports',
            content='''from typing import Any, Dict, List, Optional
''',
        ))
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render base template."""
        context.setdefault('generated_at', datetime.now().isoformat())
        
        parts = []
        for block in self._blocks.values():
            parts.append(block.render(context))
        
        return '\n'.join(parts)


class OrchestratorTemplate(ScaffolderTemplate):
    """Template for orchestrator classes."""
    
    template_type = TemplateType.ORCHESTRATOR
    
    def _setup(self) -> None:
        """Set up orchestrator template."""
        self.add_variable(TemplateVariable(
            name='class_name',
            type='str',
            required=True,
            description='Orchestrator class name',
        ))
        self.add_variable(TemplateVariable(
            name='domain',
            type='str',
            required=True,
            description='Orchestrator domain',
        ))
        self.add_variable(TemplateVariable(
            name='version',
            type='str',
            required=False,
            default='1.0.0',
            description='Orchestrator version',
        ))
        self.add_variable(TemplateVariable(
            name='description',
            type='str',
            required=False,
            default='',
            description='Orchestrator description',
        ))
        self.add_variable(TemplateVariable(
            name='stages',
            type='list',
            required=False,
            default=[],
            description='List of stage names',
        ))
        self.add_variable(TemplateVariable(
            name='parameters',
            type='list',
            required=False,
            default=[],
            description='List of parameter definitions',
        ))
        self.add_variable(TemplateVariable(
            name='hooks',
            type='list',
            required=False,
            default=[],
            description='List of hook names',
        ))
        self.add_variable(TemplateVariable(
            name='async_support',
            type='bool',
            required=False,
            default=False,
            description='Enable async support',
        ))
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render orchestrator template."""
        context.setdefault('generated_at', datetime.now().isoformat())
        context.setdefault('stages', [])
        context.setdefault('parameters', [])
        context.setdefault('hooks', [])
        context.setdefault('async_support', False)
        
        # Build components
        header = self._render_header(context)
        imports = self._render_imports(context)
        params_class = self._render_params_class(context)
        orchestrator_class = self._render_orchestrator_class(context)
        
        return f"{header}\n{imports}\n{params_class}\n{orchestrator_class}"
    
    def _render_header(self, context: Dict[str, Any]) -> str:
        """Render file header."""
        return f'''"""
{context['class_name']}
Domain: {context['domain']}
Version: {context.get('version', '1.0.0')}

{context.get('description', '')}

Generated by CORTEX Scaffolder
Generated at: {context.get('generated_at', datetime.now().isoformat())}
"""
'''
    
    def _render_imports(self, context: Dict[str, Any]) -> str:
        """Render imports section."""
        imports = [
            "from dataclasses import dataclass, field",
            "from datetime import datetime",
            "from typing import Any, Callable, Dict, List, Optional",
            "import logging",
            "",
            "from cortex.orchestrators.base import BaseOrchestrator, ExecutionContext, ExecutionResult",
            "from cortex.orchestrators.stages import StageResult",
        ]
        
        if context.get('async_support'):
            imports.insert(3, "import asyncio")
        
        return '\n'.join(imports)
    
    def _render_params_class(self, context: Dict[str, Any]) -> str:
        """Render parameters dataclass."""
        class_name = context['class_name']
        params = context.get('parameters', [])
        
        fields = []
        for param in params:
            py_type = self._yaml_type_to_python(param.get('type', 'str'))
            if not param.get('required', True):
                py_type = f"Optional[{py_type}]"
            
            default = param.get('default')
            if default is not None:
                default_str = f" = {repr(default)}"
            elif not param.get('required', True):
                default_str = " = None"
            else:
                default_str = ""
            
            fields.append(f"    {param['name']}: {py_type}{default_str}")
        
        fields_str = '\n'.join(fields) if fields else "    pass"
        
        return f'''

@dataclass
class {class_name}Params:
    """Parameters for {class_name}."""
{fields_str}
'''
    
    def _render_orchestrator_class(self, context: Dict[str, Any]) -> str:
        """Render main orchestrator class."""
        class_name = context['class_name']
        domain = context['domain']
        version = context.get('version', '1.0.0')
        stages = context.get('stages', [])
        
        stages_list = ', '.join(f"'{s}'" for s in stages)
        
        async_prefix = "async " if context.get('async_support') else ""
        await_prefix = "await " if context.get('async_support') else ""
        
        return f'''

logger = logging.getLogger(__name__)


class {class_name}(BaseOrchestrator):
    """
    {context.get('description', f'{class_name} orchestrator')}
    
    Domain: {domain}
    Version: {version}
    """
    
    DOMAIN = '{domain}'
    VERSION = '{version}'
    STAGES = [{stages_list}]
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        super().__init__(config)
        self._hooks: Dict[str, List[Callable]] = {{}}
    
    @property
    def domain(self) -> str:
        return self.DOMAIN
    
    @property
    def version(self) -> str:
        return self.VERSION
    
    def register_hook(self, hook_name: str, callback: Callable) -> None:
        if hook_name not in self._hooks:
            self._hooks[hook_name] = []
        self._hooks[hook_name].append(callback)
    
    {async_prefix}def execute(
        self,
        params: {class_name}Params | Dict[str, Any],
        context: Optional[ExecutionContext] = None,
        **kwargs,
    ) -> ExecutionResult:
        if isinstance(params, dict):
            params = {class_name}Params(**params)
        
        context = context or ExecutionContext(
            orchestrator=self.DOMAIN,
            params=params.__dict__,
            started_at=datetime.now(),
        )
        
        try:
            results = {await_prefix}self._execute_pipeline(context)
            return ExecutionResult(
                status='completed',
                output=self._aggregate_results(results),
                stages=results,
                context=context,
            )
        except Exception as e:
            logger.exception(f"Execution failed: {{e}}")
            return ExecutionResult(
                status='failed',
                error=str(e),
                context=context,
            )
    
    {async_prefix}def _execute_pipeline(self, context: ExecutionContext) -> List[StageResult]:
        results = []
        for stage_name in self.STAGES:
            result = {await_prefix}self._execute_stage(stage_name, context)
            results.append(result)
            context.stage_results[stage_name] = result
        return results
    
    {async_prefix}def _execute_stage(self, stage: str, context: ExecutionContext) -> StageResult:
        # Override in subclass
        return StageResult(stage=stage, status='completed', output={{}})
    
    def _aggregate_results(self, results: List[StageResult]) -> Dict[str, Any]:
        return {{r.stage: r.output for r in results if r.output}}
'''
    
    def _yaml_type_to_python(self, type_str: str) -> str:
        """Convert YAML type to Python type."""
        type_map = {
            'str': 'str', 'string': 'str',
            'int': 'int', 'integer': 'int',
            'float': 'float', 'number': 'float',
            'bool': 'bool', 'boolean': 'bool',
            'list': 'List[Any]', 'array': 'List[Any]',
            'dict': 'Dict[str, Any]', 'object': 'Dict[str, Any]',
        }
        return type_map.get(type_str.lower(), 'Any')


class TestTemplate(ScaffolderTemplate):
    """Template for test files."""
    
    template_type = TemplateType.TEST
    
    def _setup(self) -> None:
        """Set up test template."""
        self.add_variable(TemplateVariable(
            name='class_name',
            type='str',
            required=True,
            description='Class being tested',
        ))
        self.add_variable(TemplateVariable(
            name='module_path',
            type='str',
            required=True,
            description='Import path for the module',
        ))
        self.add_variable(TemplateVariable(
            name='test_cases',
            type='list',
            required=False,
            default=[],
            description='List of test case definitions',
        ))
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render test template."""
        class_name = context['class_name']
        module_path = context['module_path']
        test_cases = context.get('test_cases', [])
        
        test_methods = []
        for tc in test_cases:
            name = tc.get('name', 'test_case')
            desc = tc.get('description', 'Test case')
            test_methods.append(f'''
    def test_{name}(self, instance):
        """Test: {desc}"""
        # TODO: Implement test
        assert instance is not None''')
        
        test_methods_str = '\n'.join(test_methods) if test_methods else '''
    def test_placeholder(self, instance):
        """Placeholder test."""
        assert instance is not None'''
        
        return f'''"""
Tests for {class_name}

Generated by CORTEX Scaffolder
"""

import pytest
from unittest.mock import MagicMock, patch

from {module_path} import {class_name}


class Test{class_name}:
    """Test suite for {class_name}."""
    
    @pytest.fixture
    def instance(self):
        """Create test instance."""
        return {class_name}()
    
    def test_creation(self, instance):
        """Test instance creation."""
        assert instance is not None
    {test_methods_str}


def test_{class_name.lower()}_basic():
    """Basic test for {class_name}."""
    instance = {class_name}()
    assert instance is not None
'''


class ConfigTemplate(ScaffolderTemplate):
    """Template for configuration files."""
    
    template_type = TemplateType.CONFIG
    
    def _setup(self) -> None:
        """Set up config template."""
        self.add_variable(TemplateVariable(
            name='name',
            type='str',
            required=True,
            description='Configuration name',
        ))
        self.add_variable(TemplateVariable(
            name='domain',
            type='str',
            required=True,
            description='Domain name',
        ))
        self.add_variable(TemplateVariable(
            name='settings',
            type='dict',
            required=False,
            default={},
            description='Configuration settings',
        ))
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render config template as YAML."""
        import yaml
        
        config = {
            'name': context['name'],
            'domain': context['domain'],
            'version': context.get('version', '1.0.0'),
            'settings': context.get('settings', {}),
            'logging': {
                'level': 'INFO',
                'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            },
            'timeouts': {
                'execution': 300,
                'stage': 60,
            },
        }
        
        return yaml.dump(config, default_flow_style=False, sort_keys=False)


class IntegrationTemplate(ScaffolderTemplate):
    """Template for integration adapters."""
    
    template_type = TemplateType.INTEGRATION
    
    def _setup(self) -> None:
        """Set up integration template."""
        self.add_variable(TemplateVariable(
            name='class_name',
            type='str',
            required=True,
            description='Adapter class name',
        ))
        self.add_variable(TemplateVariable(
            name='integrations',
            type='list',
            required=False,
            default=[],
            description='List of integration names',
        ))
    
    def render(self, context: Dict[str, Any]) -> str:
        """Render integration adapter template."""
        class_name = context['class_name']
        integrations = context.get('integrations', [])
        
        methods = []
        for integration in integrations:
            safe_name = integration.replace('-', '_').replace(' ', '_').lower()
            methods.append(f'''
    def get_{safe_name}(self) -> Any:
        """Get {integration} integration."""
        return self._connections.get('{integration}')
    
    def connect_{safe_name}(self, **kwargs) -> Any:
        """Connect to {integration}."""
        conn = self._create_connection('{integration}', kwargs)
        self._connections['{integration}'] = conn
        return conn''')
        
        methods_str = '\n'.join(methods)
        
        return f'''"""
Integration Adapter: {class_name}

Generated by CORTEX Scaffolder
"""

from typing import Any, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class {class_name}:
    """Integration adapter for external services."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self._config = config or {{}}
        self._connections: Dict[str, Any] = {{}}
    
    def _create_connection(self, name: str, config: Dict[str, Any]) -> Any:
        """Create a connection to an integration."""
        # Override for specific implementations
        return {{'name': name, 'config': config, 'connected': True}}
    
    def close_all(self) -> None:
        """Close all connections."""
        for name, conn in self._connections.items():
            if hasattr(conn, 'close'):
                try:
                    conn.close()
                except Exception as e:
                    logger.warning(f"Error closing {{name}}: {{e}}")
        self._connections.clear()
    {methods_str}
    
    def __enter__(self):
        return self
    
    def __exit__(self, *args):
        self.close_all()
'''


# Template Registry
class TemplateRegistry:
    """Registry for scaffolder templates."""
    
    _templates: Dict[TemplateType, type] = {
        TemplateType.BASE: BaseTemplate,
        TemplateType.ORCHESTRATOR: OrchestratorTemplate,
        TemplateType.TEST: TestTemplate,
        TemplateType.CONFIG: ConfigTemplate,
        TemplateType.INTEGRATION: IntegrationTemplate,
    }
    
    @classmethod
    def get(cls, template_type: TemplateType) -> ScaffolderTemplate:
        """Get a template instance by type."""
        template_class = cls._templates.get(template_type)
        if template_class:
            return template_class()
        raise ValueError(f"Unknown template type: {template_type}")
    
    @classmethod
    def register(cls, template_type: TemplateType, template_class: type) -> None:
        """Register a new template type."""
        cls._templates[template_type] = template_class
    
    @classmethod
    def available_types(cls) -> List[TemplateType]:
        """Get list of available template types."""
        return list(cls._templates.keys())
