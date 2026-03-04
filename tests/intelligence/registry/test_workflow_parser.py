# AC_START: AC-P125-S2-002
"""
Test Suite: Phase 125 Stage 2 — WorkflowTemplateParser
Module: Typed parser for workflow-template schema YAML files.
Tests: 15 tests — field extraction, registry integration, fallback override.
"""

import pytest

from cortex.intelligence.registry.parsers import (
    PARSER_REGISTRY,
    get_parser_for_type,
)
from cortex.intelligence.registry.parsers.workflow_parser import WorkflowTemplateParser
from cortex.intelligence.registry.models.workflow import WorkflowTemplateModel
from cortex.intelligence.registry.models.base import BaseRegistryModel


# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def parser() -> WorkflowTemplateParser:
    """Return a fresh WorkflowTemplateParser instance."""
    return WorkflowTemplateParser()


@pytest.fixture
def workflow_data() -> dict:
    """Workflow YAML with top-level ``workflow`` block and steps."""
    return {
        "workflow": {
            "id": "sdlc/implement-workflow",
            "name": "IMPLEMENT — TDD-First Development",
            "version": "1.0.0",
            "category": "sdlc",
            "status": "active",
            "metadata": {
                "author": "CORTEX Architecture",
                "created": "2026-02-28",
                "modes_served": ["IMPLEMENT"],
                "trigger_keywords": ["build", "create", "add", "implement"],
                "orchestrators_used": [
                    "TDDOrchestrator",
                    "EnforcementOrchestrator",
                ],
                "core_rules": ["CORE-008", "CORE-048", "CORE-064"],
            },
            "convergence_gate": {
                "primitive_ref": "primitives/validation/detect-fix-rescan-loop",
                "max_cycles": 3,
                "success_predicate": "test_pass_count >= baseline",
            },
            "steps": [
                {
                    "id": "ac_start",
                    "name": "Emit AC_START marker",
                    "template_ref": "primitives/execution/ac-marker-emit",
                },
                {
                    "id": "tdd_red",
                    "name": "RED — Write failing tests",
                    "depends_on": ["ac_start"],
                    "orchestrator": "TDDOrchestrator",
                },
                {
                    "id": "tdd_green",
                    "name": "GREEN — Minimum implementation",
                    "depends_on": ["tdd_red"],
                    "orchestrator": "TDDOrchestrator",
                },
            ],
        },
    }


@pytest.fixture
def workflow_data_minimal() -> dict:
    """Minimal workflow YAML — only id and name."""
    return {
        "workflow": {
            "id": "minimal/workflow",
            "name": "Minimal",
        },
    }


# ── Registration Tests ──────────────────────────────────────────────────


class TestWorkflowParserRegistration:
    """WorkflowTemplateParser must register via @register_parser."""

    def test_workflow_template_registered_in_parser_registry(self) -> None:
        """'workflow-template' key must exist in PARSER_REGISTRY."""
        assert "workflow-template" in PARSER_REGISTRY

    def test_registered_class_is_workflow_template_parser(self) -> None:
        """PARSER_REGISTRY['workflow-template'] must be WorkflowTemplateParser."""
        assert PARSER_REGISTRY["workflow-template"] is WorkflowTemplateParser

    def test_get_parser_for_type_returns_workflow_parser(self) -> None:
        """get_parser_for_type('workflow-template') must return WorkflowTemplateParser."""
        cls = get_parser_for_type("workflow-template")
        assert cls is WorkflowTemplateParser

    def test_overrides_generic_fallback(self) -> None:
        """workflow-template must NOT fall back to GenericParser."""
        from cortex.intelligence.registry.parsers.generic_parser import GenericParser

        cls = get_parser_for_type("workflow-template")
        assert cls is not GenericParser


# ── Parse Output Tests ──────────────────────────────────────────────────


class TestWorkflowParserParse:
    """WorkflowTemplateParser.parse() must produce WorkflowTemplateModel."""

    def test_parse_returns_workflow_template_model(
        self, parser: WorkflowTemplateParser, workflow_data: dict
    ) -> None:
        """parse() must return a WorkflowTemplateModel instance."""
        result = parser.parse(data=workflow_data, source_file="implement.yaml")
        assert isinstance(result, WorkflowTemplateModel)

    def test_model_is_base_registry_subclass(
        self, parser: WorkflowTemplateParser, workflow_data: dict
    ) -> None:
        """WorkflowTemplateModel must be a BaseRegistryModel subclass."""
        result = parser.parse(data=workflow_data, source_file="implement.yaml")
        assert isinstance(result, BaseRegistryModel)

    def test_type_field_is_workflow_template(
        self, parser: WorkflowTemplateParser, workflow_data: dict
    ) -> None:
        """Model.type must be 'workflow-template'."""
        result = parser.parse(data=workflow_data, source_file="implement.yaml")
        assert result.type == "workflow-template"

    def test_workflow_id_extracted(
        self, parser: WorkflowTemplateParser, workflow_data: dict
    ) -> None:
        """WorkflowTemplateModel.id must equal the workflow.id value."""
        result = parser.parse(data=workflow_data, source_file="implement.yaml")
        assert result.id == "sdlc/implement-workflow"

    def test_version_extracted(
        self, parser: WorkflowTemplateParser, workflow_data: dict
    ) -> None:
        """WorkflowTemplateModel.version must equal '1.0.0'."""
        result = parser.parse(data=workflow_data, source_file="implement.yaml")
        assert result.version == "1.0.0"

    def test_category_extracted(
        self, parser: WorkflowTemplateParser, workflow_data: dict
    ) -> None:
        """WorkflowTemplateModel.category must equal 'sdlc'."""
        result = parser.parse(data=workflow_data, source_file="implement.yaml")
        assert result.category == "sdlc"

    def test_steps_extracted_as_list(
        self, parser: WorkflowTemplateParser, workflow_data: dict
    ) -> None:
        """WorkflowTemplateModel.steps must be a list."""
        result = parser.parse(data=workflow_data, source_file="implement.yaml")
        assert isinstance(result.steps, list)
        assert len(result.steps) == 3

    def test_step_ids_preserved(
        self, parser: WorkflowTemplateParser, workflow_data: dict
    ) -> None:
        """Each step dict must preserve its 'id' field."""
        result = parser.parse(data=workflow_data, source_file="implement.yaml")
        ids = [s["id"] for s in result.steps]
        assert "ac_start" in ids
        assert "tdd_red" in ids

    def test_trigger_keywords_extracted(
        self, parser: WorkflowTemplateParser, workflow_data: dict
    ) -> None:
        """WorkflowTemplateModel.trigger_keywords from metadata."""
        result = parser.parse(data=workflow_data, source_file="implement.yaml")
        assert isinstance(result.trigger_keywords, list)
        assert "build" in result.trigger_keywords

    def test_convergence_gate_extracted(
        self, parser: WorkflowTemplateParser, workflow_data: dict
    ) -> None:
        """WorkflowTemplateModel.convergence_gate must be a dict."""
        result = parser.parse(data=workflow_data, source_file="implement.yaml")
        assert isinstance(result.convergence_gate, dict)
        assert result.convergence_gate.get("max_cycles") == 3

    def test_to_dict_includes_typed_fields(
        self, parser: WorkflowTemplateParser, workflow_data: dict
    ) -> None:
        """to_dict() must include steps, version, category."""
        result = parser.parse(data=workflow_data, source_file="implement.yaml")
        d = result.to_dict()
        assert "steps" in d
        assert "version" in d
        assert "category" in d


# AC_COMPLETE: AC-P125-S2-002 ✅
