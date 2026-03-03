"""
Tool Generator renderers — template rendering functions.

Phase 103-j: extracted from tool_generator.py (1,426L) god-object.
All _render_* methods live here as module-level functions.
"""
from __future__ import annotations

import re
from typing import Any, Dict, List

from cortex.tools.naming_utils import to_module_name, yaml_type_to_python


def python_type_to_click(type_str: str) -> str:
    """Convert Python type to Click type."""
    type_map = {
        "str": "str",
        "string": "str",
        "int": "int",
        "integer": "int",
        "float": "float",
        "number": "float",
        "bool": "bool",
        "boolean": "bool",
    }
    return type_map.get(type_str.lower(), "str")


def render_cli_template(
    class_name: str,
    template_name: str,
    template_domain: str,
    parameters: List[Dict[str, Any]],
    description: str,
    **_kwargs: Any,
) -> str:
    """Render CLI command template."""
    options = []
    for param in parameters:
        opt_name = param["name"].replace("_", "-")
        opt_type = python_type_to_click(param["type"])
        required = param["required"]
        default = param.get("default")
        help_text = param.get("description", "")
        if required:
            options.append(
                f"@click.option('--{opt_name}', type={opt_type}, required=True, help='{help_text}')"
            )
        else:
            default_str = f"'{default}'" if isinstance(default, str) else str(default)
            options.append(
                f"@click.option('--{opt_name}', type={opt_type}, default={default_str}, help='{help_text}')"
            )
    options_str = "\n".join(options)
    param_args = ", ".join(p["name"] for p in parameters)
    mod_name = to_module_name(template_name)
    kv = ", ".join(f"'{p['name']}': {p['name']}" for p in parameters)
    return f'''"""CLI Command for {template_name}\nDomain: {template_domain}\n\n{description}\n"""\n\nimport click\nfrom typing import Optional, Any\n\n{options_str}\n@click.command(name='{mod_name}')\ndef {mod_name}_command({param_args}):\n    """\n    {description}\n    """\n    config = {{{kv}}}\n    from cortex.orchestrators.factory import create_orchestrator\n    orchestrator = create_orchestrator('{template_domain}')\n    result = orchestrator.execute(config)\n    click.echo(f"Execution completed: {{result.status}}")\n    if result.output:\n        click.echo(result.output)\n\n\nclass {class_name}:\n    """CLI wrapper for {template_name}."""\n\n    def __init__(self):\n        self.command = {mod_name}_command\n\n    def invoke(self, **kwargs):\n        from click.testing import CliRunner\n        runner = CliRunner()\n        args = [f"--{{k.replace('_', '-')}}={{v}}" for k, v in kwargs.items()]\n        return runner.invoke(self.command, args)\n\n\nif __name__ == '__main__':\n    {mod_name}_command()\n'''


def render_api_client_template(
    class_name: str,
    template_name: str,
    template_domain: str,
    parameters: List[Dict[str, Any]],
    description: str,
    **_kwargs: Any,
) -> str:
    """Render API client template."""
    fields = []
    for param in parameters:
        py_type = yaml_type_to_python(param["type"])
        if not param["required"]:
            py_type = f"Optional[{py_type}]"
        default = param.get("default")
        if default is not None:
            ds = f" = {repr(default)}"
        elif not param["required"]:
            ds = " = None"
        else:
            ds = ""
        fields.append(f"    {param['name']}: {py_type}{ds}")
    fields_str = "\n".join(fields)
    return f'"""API Client for {template_name}\nDomain: {template_domain}\n\n{description}\n"""\nfrom dataclasses import dataclass, asdict\nfrom typing import Any, Dict, Optional\nimport httpx\n\n@dataclass\nclass {class_name}Request:\n    """Request parameters for {template_name}."""\n{fields_str}\n\n    def to_dict(self):\n        return {{k: v for k, v in asdict(self).items() if v is not None}}\n\n@dataclass\nclass {class_name}Response:\n    """Response from {template_name}."""\n    success: bool\n    status: str\n    output: Optional[Any] = None\n    error: Optional[str] = None\n\n\nclass {class_name}:\n    """{description}"""\n\n    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0, api_key: Optional[str] = None):\n        self.base_url = base_url.rstrip("/")\n        self.timeout = timeout\n        self.api_key = api_key\n        self._client = None\n\n    def execute(self, request: {class_name}Request) -> {class_name}Response:\n        """Execute {template_name}."""\n        import httpx\n        try:\n            headers = {{"Content-Type": "application/json"}}\n            if self.api_key:\n                headers["Authorization"] = f"Bearer {{self.api_key}}"\n            with httpx.Client(base_url=self.base_url, timeout=self.timeout, headers=headers) as client:\n                response = client.post("/api/v1/orchestrate/{template_domain}", json=request.to_dict())\n                response.raise_for_status()\n                data = response.json()\n                return {class_name}Response(success=True, status=data.get("status", "completed"), output=data.get("output"))\n        except Exception as e:\n            return {class_name}Response(success=False, status="error", error=str(e))\n'


def render_test_harness_template(
    class_name: str,
    template_name: str,
    template_domain: str,
    parameters: List[Dict[str, Any]],
    stages: List[Dict[str, Any]],
    hooks: Dict[str, Any],
    description: str,
    **_kwargs: Any,
) -> str:
    """Render test harness template."""
    fixtures = []
    for param in parameters:
        value = param.get("default")
        if value is None:
            t = param["type"]
            if t == "str":
                value = "'test_value'"
            elif t in ("int", "integer"):
                value = "1"
            elif t in ("float", "number"):
                value = "1.0"
            elif t in ("bool", "boolean"):
                value = "True"
            else:
                value = "'test'"
        else:
            value = repr(value)
        fixtures.append(f"        '{param['name']}': {value},")
    fixtures_str = "\n".join(fixtures)
    mod_name = to_module_name(template_name)
    return f'"""Test Harness for {template_name}\nDomain: {template_domain}\n\n{description}\n"""\nimport pytest\nfrom unittest.mock import MagicMock\nfrom typing import Any, Dict\n\nclass {class_name}:\n    """Test harness for {template_name}."""\n\n    @pytest.fixture\n    def orchestrator(self):\n        from cortex.orchestrators.factory import create_orchestrator\n        return create_orchestrator("{template_domain}")\n\n    @pytest.fixture\n    def sample_input(self) -> Dict[str, Any]:\n        return {{\n{fixtures_str}\n        }}\n\n    def test_orchestrator_creation(self, orchestrator):\n        assert orchestrator is not None\n\n    def test_basic_execution(self, orchestrator, sample_input):\n        result = orchestrator.execute(sample_input)\n        assert result is not None\n\ndef test_{mod_name}_creation():\n    from cortex.orchestrators.factory import create_orchestrator\n    orch = create_orchestrator("{template_domain}")\n    assert orch is not None\n'


def render_documentation_template(
    template_name: str,
    template_domain: str,
    parameters: List[Dict[str, Any]],
    stages: List[Dict[str, Any]],
    hooks: Dict[str, Any],
    description: str,
    version: str,
    **_kwargs: Any,
) -> str:
    """Render documentation template."""
    rows = []
    for p in parameters:
        req = "Yes" if p["required"] else "No"
        rows.append(f"| `{p['name']}` | {p['type']} | {req} | {p.get('default', '-')} | {p.get('description', '-')} |")
    table = "| Parameter | Type | Required | Default | Description |\n|-----------|------|----------|---------|-------------|\n" + "\n".join(rows)
    stages_list = "\n".join(f"{i+1}. **{s.get('name', f'Stage {i+1}')}**: {s.get('description', '')}" for i, s in enumerate(stages)) or "No stages defined."
    return f"# {template_name}\n\nDomain: {template_domain} | Version: {version}\n\n{description}\n\n## Parameters\n\n{table}\n\n## Stages\n\n{stages_list}\n"


def render_config_validator_template(
    class_name: str,
    template_name: str,
    parameters: List[Dict[str, Any]],
    **_kwargs: Any,
) -> str:
    """Render configuration validator template."""
    fields = []
    for param in parameters:
        py_type = yaml_type_to_python(param["type"])
        if not param["required"]:
            py_type = f"Optional[{py_type}]"
        default = param.get("default")
        ds = f" = {repr(default)}" if default is not None else (" = None" if not param["required"] else " = ...")
        fields.append(f"    {param['name']}: {py_type}{ds}")
    fields_str = "\n".join(fields)
    return f'"""Config Validator for {template_name}"""\nfrom typing import Any, Dict, Optional\n\nclass {class_name}:\n    """Config validator for {template_name}."""\n{fields_str}\n\n    def validate(self) -> bool:\n        return True\n'


def render_mock_service_template(
    class_name: str,
    template_name: str,
    stages: List[Dict[str, Any]],
    **_kwargs: Any,
) -> str:
    """Render mock service template."""
    stage_mocks = []
    for i, stage in enumerate(stages):
        sn = stage.get("name", f"stage_{i}")
        safe = re.sub(r"[^a-zA-Z0-9_]", "_", sn)
        stage_mocks.append(
            f"    def mock_{safe}(self, *args, **kwargs):\n        self._call_log.append(('{sn}', args, kwargs))\n        return self._stage_responses.get('{sn}', {{'status': 'mocked'}})"
        )
    methods = "\n\n".join(stage_mocks)
    return f'"""Mock Service for {template_name}"""\nfrom typing import Any, Dict, List, Tuple\n\nclass {class_name}:\n    def __init__(self):\n        self._call_log: List[Tuple] = []\n        self._stage_responses: Dict[str, Any] = {{}}\n\n    def execute(self, input_data: Dict[str, Any]) -> Dict[str, Any]:\n        self._call_log.append(("execute", (input_data,), {{}}))\n        return {{"status": "completed", "output": {{"mocked": True}}}}\n\n{methods}\n'


def render_integration_adapter_template(
    class_name: str,
    template_name: str,
    integrations: Dict[str, Any],
    **_kwargs: Any,
) -> str:
    """Render integration adapter template."""
    methods = []
    for name in integrations:
        safe = re.sub(r"[^a-zA-Z0-9_]", "_", name)
        methods.append(
            f"    def connect_{safe}(self, **kwargs):\n        return self.connect('{name}', **kwargs)"
        )
    methods_str = "\n\n".join(methods)
    return f'"""Integration Adapter for {template_name}"""\nfrom typing import Any, Dict, Optional\n\nclass {class_name}:\n    def __init__(self):\n        self._connections: Dict[str, Any] = {{}}\n\n    def connect(self, name: str, **kwargs) -> Any:\n        self._connections[name] = kwargs\n        return kwargs\n\n    def disconnect(self, name: str) -> None:\n        self._connections.pop(name, None)\n\n    def is_connected(self, name: str) -> bool:\n        return name in self._connections\n\n{methods_str}\n'
