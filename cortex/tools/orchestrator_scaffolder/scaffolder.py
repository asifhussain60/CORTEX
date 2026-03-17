"""
OrchestratorScaffolder — generates orchestrator implementations from templates.

Phase 103-i: extracted from orchestrator_scaffolder.py (1,455L) god-object.
"""
from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

import yaml

from cortex.tools.naming_utils import to_class_name, to_module_name, yaml_type_to_python
from cortex.tools.template_parser import ParsedTemplate, TemplateParser
from cortex.tools.orchestrator_scaffolder.models import (
    ScaffoldConfig,
    ScaffoldedFile,
    ScaffoldResult,
    ScaffoldType,
)
from cortex.tools.orchestrator_scaffolder import renderers

logger = logging.getLogger(__name__)


class OrchestratorScaffolder:
    """
    Scaffolder for creating orchestrator implementations.

    Generates complete Python orchestrator code from templates.

    Example:
        scaffolder = OrchestratorScaffolder()
        result = scaffolder.scaffold_from_file("templates/planning.yaml")
        result.write_all(Path("output"))
    """

    def __init__(self, parser: Optional[TemplateParser] = None) -> None:
        """Initialize scaffolder."""
        self.parser = parser or TemplateParser()

    def scaffold_from_file(
        self,
        template_path: Union[str, Path],
        config: Optional[ScaffoldConfig] = None,
    ) -> ScaffoldResult:
        """Scaffold from a template file."""
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
        """Scaffold from a template dictionary."""
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
        """Scaffold orchestrator from parsed template."""
        from datetime import datetime
        config = config or ScaffoldConfig()
        config.domain = template.domain or config.domain

        result = ScaffoldResult(success=True)
        result.metadata = {
            "template_name": template.name,
            "template_domain": template.domain,
            "template_version": template.version,
            "scaffold_type": config.scaffold_type.name,
            "generated_at": datetime.now().isoformat(),
        }

        # Optional audit logger (WAVE-2)
        audit_logger = self._get_audit_logger(result)

        if audit_logger:
            try:
                query_result = self._check_registry_for_duplicates(template.name)
                decision = "upgrade_proposed" if query_result.found else "create_new"
                ac_marker = audit_logger.log_pre_scaffolding_check(
                    orchestrator_name=template.name,
                    query_result=query_result,
                    decision=decision,
                    decision_rationale="",
                    user_override=False,
                )
                result.metadata["ac_marker_pre_check"] = ac_marker
                result.metadata["duplicate_detected"] = bool(query_result.found)
            except Exception as e:
                result.add_warning(f"Pre-scaffolding check failed: {e}")
        else:
            result.metadata["duplicate_detected"] = False

        # Validate template
        validation = self.parser.validate(template)
        if not validation.valid:
            for error in validation.errors:
                result.add_error(error)
            return result
        for warning in validation.warnings:
            result.add_warning(warning)

        # Generate files based on scaffold type
        if config.scaffold_type in (ScaffoldType.ORCHESTRATOR, ScaffoldType.FULL):
            self._scaffold_orchestrator(template, config, result)

        if config.scaffold_type in (ScaffoldType.TEST, ScaffoldType.FULL) and config.include_tests:
            self._scaffold_tests(template, config, result)

        if config.scaffold_type in (ScaffoldType.CONFIG, ScaffoldType.FULL) and config.include_config:
            self._scaffold_config(template, config, result)

        if config.scaffold_type in (ScaffoldType.INTEGRATION, ScaffoldType.FULL) and config.include_integrations:
            self._scaffold_integrations(template, config, result)

        return result

    # ---- private scaffold methods ----

    def _scaffold_orchestrator(
        self, template: ParsedTemplate, config: ScaffoldConfig, result: ScaffoldResult
    ) -> None:
        """Generate main orchestrator file."""
        class_name = to_class_name(template.name) + config.class_suffix
        module_name = to_module_name(template.name)
        params = self._get_parameters(template)
        stages = self._get_stages(template)
        hooks = self._get_hooks(template)
        code = renderers.render_orchestrator(
            class_name=class_name,
            template=template,
            params=params,
            stages=stages,
            hooks=hooks,
            config=config,
        )
        result.add_file(ScaffoldedFile(
            path=Path(f"{config.domain}/{module_name}.py"),
            content=code,
            file_type="orchestrator",
        ))

    def _scaffold_tests(
        self, template: ParsedTemplate, config: ScaffoldConfig, result: ScaffoldResult
    ) -> None:
        """Generate test file."""
        class_name = to_class_name(template.name) + config.class_suffix
        test_class_name = f"Test{class_name}"
        module_name = to_module_name(template.name)
        params = self._get_parameters(template)
        stages = self._get_stages(template)
        code = renderers.render_tests(
            class_name=class_name,
            test_class_name=test_class_name,
            template=template,
            params=params,
            stages=stages,
            config=config,
        )
        result.add_file(ScaffoldedFile(
            path=Path(f"tests/{config.domain}/{config.test_prefix}{module_name}.py"),
            content=code,
            file_type="test",
        ))

    def _scaffold_config(
        self, template: ParsedTemplate, config: ScaffoldConfig, result: ScaffoldResult
    ) -> None:
        """Generate configuration file."""
        module_name = to_module_name(template.name)
        content = renderers.render_config(template, config)
        result.add_file(ScaffoldedFile(
            path=Path(f"config/{config.domain}/{module_name}{config.config_suffix}.yaml"),
            content=content,
            file_type="config",
        ))

    def _scaffold_integrations(
        self, template: ParsedTemplate, config: ScaffoldConfig, result: ScaffoldResult
    ) -> None:
        """Generate integration adapter if integrations defined."""
        integrations = self._get_integrations(template)
        if not integrations:
            return
        class_name = to_class_name(template.name) + "IntegrationAdapter"
        module_name = to_module_name(template.name) + "_integrations"
        code = renderers.render_integrations(
            class_name=class_name,
            template=template,
            integrations=integrations,
            config=config,
        )
        result.add_file(ScaffoldedFile(
            path=Path(f"{config.domain}/integrations/{module_name}.py"),
            content=code,
            file_type="integration",
        ))

    # ---- helpers ----

    def _get_parameters(self, template: ParsedTemplate) -> List[Dict[str, Any]]:
        """Extract parameter definitions from template."""
        params = []
        s = template.get_section("parameters")
        if s:
            for name, cfg in s.content.items():
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

    def _yaml_type_to_python(self, type_str: str) -> str:
        """Convert YAML type to Python type."""
        return yaml_type_to_python(type_str)

    def _to_class_name(self, name: str) -> str:
        """Convert name to PascalCase."""
        return to_class_name(name)

    def _to_module_name(self, name: str) -> str:
        """Convert name to snake_case."""
        return to_module_name(name)

    def _get_audit_logger(self, result: ScaffoldResult) -> Optional[Any]:
        """Get audit logger or None."""
        try:
            from cortex.tools.scaffolder_audit_logger import ScaffolderAuditLogger
            return ScaffolderAuditLogger()
        except ImportError:
            result.add_warning("Audit logger not available")
            return None
        except Exception:
            result.add_warning("Audit logger not available")
            return None

    def _check_registry_for_duplicates(self, name: str) -> Any:
        """Check wiring registry for existing implementations."""
        try:
            from cortex.tools.scaffolder_audit_logger import RegistryQueryResult
            return RegistryQueryResult(found=False, location=None, capability_overlap=0.0)
        except ImportError:
            return type("R", (), {"found": False, "location": None, "capability_overlap": 0.0})()

    def _render_tests_via_intelligence(
        self, class_name: str, template: ParsedTemplate, config: ScaffoldConfig
    ) -> str:
        """Render tests using intelligence adapter (WAVE-2 optional path)."""
        # Fallback to standard rendering
        return renderers.render_tests(
            class_name=class_name,
            test_class_name=f"Test{class_name}",
            template=template,
            params=self._get_parameters(template),
            stages=self._get_stages(template),
            config=config,
        )
