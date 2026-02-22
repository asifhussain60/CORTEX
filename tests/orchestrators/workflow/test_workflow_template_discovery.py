"""
Tests for WorkflowTemplateManager dynamic registry discovery — ENH-MCP-WORKFLOW-001.

Root cause: GAP-004 (PB-STS-001 Run 1) — execute_workflow only found 3 built-in
templates; security-hardening, service-decomposition-workflow, tdd-api-service,
and frontend-tdd-workflow were absent because WorkflowTemplateManager only loaded
hard-coded constants, ignoring cortex-registry/workflows/templates/**/*.yaml.

These tests verify the ENH-MCP-WORKFLOW-001 fix: dynamic YAML template discovery
on construction, with built-in templates always taking precedence.

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
AC_START: ENH-MCP-WORKFLOW-001-TESTS
"""

from __future__ import annotations

import textwrap
from pathlib import Path
from typing import Generator

import pytest
import yaml

from cortex.orchestrators.workflow.workflow_templates import WorkflowTemplateManager


# ── Helpers ───────────────────────────────────────────────────────────────────

def _write_template_yaml(path: Path, name: str, description: str = "test") -> None:
    """Write a minimal valid workflow template YAML file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        yaml.safe_dump(
            {
                "name": name,
                "description": description,
                "steps": [{"name": "step1", "action": "run"}],
            }
        ),
        encoding="utf-8",
    )


# ── Built-in templates ────────────────────────────────────────────────────────

class TestBuiltInTemplates:
    """All original built-in templates must always be present."""

    BUILT_INS = {"phase-execution", "tdd-cycle", "refactor-holistic"}

    def test_all_built_ins_present_with_empty_registry(self, tmp_path: Path) -> None:
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        for name in self.BUILT_INS:
            assert name in manager.list_templates(), f"Built-in '{name}' missing"

    def test_all_built_ins_present_with_populated_registry(self, tmp_path: Path) -> None:
        _write_template_yaml(tmp_path / "security" / "security-hardening.yaml", "security-hardening")
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        for name in self.BUILT_INS:
            assert name in manager.list_templates()

    def test_list_templates_returns_sorted_list(self, tmp_path: Path) -> None:
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        templates = manager.list_templates()
        assert templates == sorted(templates)


# ── Dynamic discovery ─────────────────────────────────────────────────────────

class TestDynamicDiscovery:
    """YAML files in the registry root must be discovered at construction time."""

    def test_discovers_single_yaml_template(self, tmp_path: Path) -> None:
        _write_template_yaml(tmp_path / "security" / "security-hardening.yaml", "security-hardening")
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        assert "security-hardening" in manager.list_templates()

    def test_discovers_multiple_templates_recursively(self, tmp_path: Path) -> None:
        templates_to_add = {
            "security/security-hardening.yaml": "security-hardening",
            "lifecycle/service-decomposition-workflow.yaml": "service-decomposition-workflow",
            "tdd/tdd-api-service.yaml": "tdd-api-service",
            "tdd/frontend-tdd-workflow.yaml": "frontend-tdd-workflow",
        }
        for rel_path, name in templates_to_add.items():
            _write_template_yaml(tmp_path / rel_path, name)

        manager = WorkflowTemplateManager(registry_root=tmp_path)
        for name in templates_to_add.values():
            assert name in manager.list_templates(), f"Expected '{name}' to be discovered"

    def test_get_template_returns_discovered_template(self, tmp_path: Path) -> None:
        _write_template_yaml(tmp_path / "tdd" / "tdd-api-service.yaml", "tdd-api-service")
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        template = manager.get_template("tdd-api-service")
        assert template["name"] == "tdd-api-service"

    def test_discovered_template_has_steps(self, tmp_path: Path) -> None:
        _write_template_yaml(tmp_path / "tdd" / "custom.yaml", "custom-workflow")
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        template = manager.get_template("custom-workflow")
        assert "steps" in template

    def test_missing_registry_root_silently_falls_back_to_built_ins(self, tmp_path: Path) -> None:
        missing_root = tmp_path / "nonexistent"
        manager = WorkflowTemplateManager(registry_root=missing_root)
        # Should not raise — just return built-ins
        assert "tdd-cycle" in manager.list_templates()

    def test_invalid_yaml_file_is_skipped(self, tmp_path: Path) -> None:
        bad_file = tmp_path / "security" / "broken.yaml"
        bad_file.parent.mkdir(parents=True)
        bad_file.write_text("{invalid yaml: [unclosed", encoding="utf-8")
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        # Built-ins still available; broken file did not raise
        assert "tdd-cycle" in manager.list_templates()

    def test_non_dict_yaml_file_is_skipped(self, tmp_path: Path) -> None:
        list_yaml = tmp_path / "tdd" / "list-only.yaml"
        list_yaml.parent.mkdir(parents=True)
        list_yaml.write_text("- item1\n- item2\n", encoding="utf-8")
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        assert "tdd-cycle" in manager.list_templates()

    def test_yaml_without_name_uses_stem_as_name(self, tmp_path: Path) -> None:
        unnamed = tmp_path / "security" / "my-security-workflow.yaml"
        unnamed.parent.mkdir(parents=True)
        unnamed.write_text(
            yaml.safe_dump({"description": "no name key", "steps": []}), encoding="utf-8"
        )
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        assert "my-security-workflow" in manager.list_templates()


# ── Built-in precedence ───────────────────────────────────────────────────────

class TestBuiltInPrecedence:
    """Built-in templates must always win over external YAML with the same name."""

    def test_builtin_content_is_unchanged_when_registry_shadows_it(self, tmp_path: Path) -> None:
        # Write a registry YAML that claims the name "tdd-cycle" with different content
        shadow = tmp_path / "tdd" / "tdd-cycle.yaml"
        shadow.parent.mkdir(parents=True)
        shadow.write_text(
            yaml.safe_dump({"name": "tdd-cycle", "description": "OVERRIDDEN", "steps": []}),
            encoding="utf-8",
        )
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        template = manager.get_template("tdd-cycle")
        # Built-in description must win — never "OVERRIDDEN"
        assert template.get("description") != "OVERRIDDEN"
        assert "RED" in template.get("description", "") or len(template.get("steps", [])) > 0

    def test_builtin_wins_for_all_three_builtins(self, tmp_path: Path) -> None:
        for name in ("phase-execution", "tdd-cycle", "refactor-holistic"):
            f = tmp_path / f"{name}.yaml"
            f.write_text(
                yaml.safe_dump({"name": name, "description": "SHADOW", "steps": []}),
                encoding="utf-8",
            )
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        for name in ("phase-execution", "tdd-cycle", "refactor-holistic"):
            template = manager.get_template(name)
            assert template.get("description") != "SHADOW"


# ── get_template / list_templates API ────────────────────────────────────────

class TestManagerPublicAPI:
    """Public API contracts remain stable after ENH-MCP-WORKFLOW-001."""

    def test_get_template_raises_key_error_for_unknown(self, tmp_path: Path) -> None:
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        with pytest.raises(KeyError, match="unknown-template-xyz"):
            manager.get_template("unknown-template-xyz")

    def test_key_error_lists_available_templates(self, tmp_path: Path) -> None:
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        with pytest.raises(KeyError) as exc_info:
            manager.get_template("no-such-template")
        assert "Available templates" in str(exc_info.value)

    def test_register_template_makes_it_retrievable(self, tmp_path: Path) -> None:
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        custom = {"name": "my-custom", "description": "runtime reg", "steps": []}
        manager.register_template("my-custom", custom)
        assert "my-custom" in manager.list_templates()
        assert manager.get_template("my-custom") == custom

    def test_list_templates_returns_list_type(self, tmp_path: Path) -> None:
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        result = manager.list_templates()
        assert isinstance(result, list)
        assert all(isinstance(n, str) for n in result)

    def test_nested_template_key_supported(self, tmp_path: Path) -> None:
        """YAML with top-level 'template:' key wrapping the template dict."""
        nested = tmp_path / "lifecycle" / "nested-format.yaml"
        nested.parent.mkdir(parents=True)
        nested.write_text(
            yaml.safe_dump({
                "template": {
                    "name": "nested-format",
                    "description": "nested YAML format",
                    "steps": [{"name": "s1", "action": "run"}],
                }
            }),
            encoding="utf-8",
        )
        manager = WorkflowTemplateManager(registry_root=tmp_path)
        assert "nested-format" in manager.list_templates()
        t = manager.get_template("nested-format")
        assert t["name"] == "nested-format"


# AC_COMPLETE: ENH-MCP-WORKFLOW-001-TESTS ✅
