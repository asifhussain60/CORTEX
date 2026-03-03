"""
ToolGenerator — generates CLI, API clients, test harnesses, and more from templates.

Phase 103-j: extracted from tool_generator.py (1,426L) god-object.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict, List

from cortex.tools.naming_utils import to_class_name, to_module_name
from cortex.tools.template_parser import ParsedTemplate
from cortex.tools.tool_generator.models import (
    GeneratedTool,
    GenerationConfig,
    GenerationResult,
    ToolType,
)
from cortex.tools.tool_generator import renderers


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

    def __init__(self) -> None:
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
        """Generate tools from a template."""
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
        """Generate all available tools from a template."""
        result = GenerationResult(success=True)
        for tool_type in ToolType:
            config = GenerationConfig(tool_type=tool_type, output_dir=output_dir)
            sub = self.generate(template, config)
            result.tools.extend(sub.tools)
            result.errors.extend(sub.errors)
            result.warnings.extend(sub.warnings)
            if not sub.success:
                result.success = False
        return result

    # ---- private generators ----

    def _generate_cli(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        class_name = to_class_name(template.name) + "CLI"
        module_name = to_module_name(template.name) + "_cli"
        params = self._get_parameters(template)
        content = renderers.render_cli_template(
            class_name=class_name,
            template_name=template.name,
            template_domain=template.domain,
            parameters=params,
            description=template.description,
            config=config,
        )
        return [GeneratedTool(name=class_name, tool_type=ToolType.CLI_COMMAND, content=content,
                              path=Path(f"cli/{module_name}.py"), template_source=template.name,
                              dependencies=["click"])]

    def _generate_api_client(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        class_name = to_class_name(template.name) + "Client"
        module_name = to_module_name(template.name) + "_client"
        params = self._get_parameters(template)
        content = renderers.render_api_client_template(
            class_name=class_name,
            template_name=template.name,
            template_domain=template.domain,
            parameters=params,
            description=template.description,
            config=config,
        )
        return [GeneratedTool(name=class_name, tool_type=ToolType.API_CLIENT, content=content,
                              path=Path(f"clients/{module_name}.py"), template_source=template.name,
                              dependencies=["httpx"])]

    def _generate_test_harness(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        class_name = f"Test{to_class_name(template.name)}"
        module_name = f"test_{to_module_name(template.name)}"
        params = self._get_parameters(template)
        stages = self._get_stages(template)
        hooks = self._get_hooks(template)
        content = renderers.render_test_harness_template(
            class_name=class_name,
            template_name=template.name,
            template_domain=template.domain,
            parameters=params,
            stages=stages,
            hooks=hooks,
            description=template.description,
            config=config,
        )
        return [GeneratedTool(name=class_name, tool_type=ToolType.TEST_HARNESS, content=content,
                              path=Path(f"tests/{module_name}.py"), template_source=template.name,
                              dependencies=["pytest"])]

    def _generate_documentation(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        params = self._get_parameters(template)
        stages = self._get_stages(template)
        hooks = self._get_hooks(template)
        content = renderers.render_documentation_template(
            template_name=template.name,
            template_domain=template.domain,
            parameters=params,
            stages=stages,
            hooks=hooks,
            description=template.description,
            version=template.version,
        )
        return [GeneratedTool(name=f"{template.name} Documentation", tool_type=ToolType.DOCUMENTATION,
                              content=content, path=None, template_source=template.name, dependencies=[])]

    def _generate_config_validator(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        class_name = to_class_name(template.name) + "ConfigValidator"
        module_name = to_module_name(template.name) + "_validator"
        params = self._get_parameters(template)
        content = renderers.render_config_validator_template(
            class_name=class_name,
            template_name=template.name,
            parameters=params,
            config=config,
        )
        return [GeneratedTool(name=class_name, tool_type=ToolType.CONFIG_VALIDATOR, content=content,
                              path=Path(f"validators/{module_name}.py"), template_source=template.name,
                              dependencies=[])]

    def _generate_mock_service(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        class_name = f"Mock{to_class_name(template.name)}Service"
        module_name = f"mock_{to_module_name(template.name)}"
        stages = self._get_stages(template)
        content = renderers.render_mock_service_template(
            class_name=class_name,
            template_name=template.name,
            stages=stages,
            config=config,
        )
        return [GeneratedTool(name=class_name, tool_type=ToolType.MOCK_SERVICE, content=content,
                              path=Path(f"mocks/{module_name}.py"), template_source=template.name,
                              dependencies=[])]

    def _generate_integration_adapter(self, template: ParsedTemplate, config: GenerationConfig) -> List[GeneratedTool]:
        class_name = to_class_name(template.name) + "Adapter"
        module_name = to_module_name(template.name) + "_adapter"
        integrations = self._get_integrations(template)
        content = renderers.render_integration_adapter_template(
            class_name=class_name,
            template_name=template.name,
            integrations=integrations,
            config=config,
        )
        return [GeneratedTool(name=class_name, tool_type=ToolType.INTEGRATION_ADAPTER, content=content,
                              path=Path(f"adapters/{module_name}.py"), template_source=template.name,
                              dependencies=[])]

    # ---- helpers ----

    def _get_parameters(self, template: ParsedTemplate) -> List[Dict[str, Any]]:
        """Extract parameter definitions from template."""
        params = []
        params_section = template.get_section("parameters")
        if params_section:
            for name, cfg in params_section.content.items():
                if isinstance(cfg, dict):
                    params.append({
                        "name": name,
                        "type": cfg.get("type", "str"),
                        "required": cfg.get("required", False),
                        "default": cfg.get("default"),
                        "description": cfg.get("description", ""),
                    })
                else:
                    params.append({"name": name, "type": "str", "required": False,
                                   "default": cfg, "description": ""})
        return params

    def _get_stages(self, template: ParsedTemplate) -> List[Dict[str, Any]]:
        """Extract stage definitions from template."""
        s = template.get_section("stages")
        return s.content.get("stages", []) if s else []

    def _get_hooks(self, template: ParsedTemplate) -> Dict[str, Any]:
        """Extract hook definitions from template."""
        s = template.get_section("hooks")
        return s.content if s else {}

    def _get_integrations(self, template: ParsedTemplate) -> Dict[str, Any]:
        """Extract integration definitions from template."""
        s = template.get_section("integrations")
        return s.content if s else {}
