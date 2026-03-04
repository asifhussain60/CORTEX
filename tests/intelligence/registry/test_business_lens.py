# AC_START: AC-P125-H-001
"""
Test Suite: Phase 125-h — BusinessLensWriter
Module: LLM-synthesized executive summaries per artifact.
Tests: 12 tests — summary generation, template rendering, batch processing.
"""

import json
from typing import Any, Dict, List

import pytest

from cortex.intelligence.registry.business_lens_writer import BusinessLensWriter
from cortex.intelligence.registry.models.governance import GovernanceRuleModel
from cortex.intelligence.registry.models.workflow import WorkflowTemplateModel
from cortex.intelligence.registry.models.pattern import PatternModel
from cortex.intelligence.registry.models.generic import GenericModel


# ═══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ═══════════════════════════════════════════════════════════════════════════════


@pytest.fixture
def writer() -> BusinessLensWriter:
    return BusinessLensWriter()


@pytest.fixture
def gov_model() -> GovernanceRuleModel:
    return GovernanceRuleModel(
        id="core-dev",
        type="governance-rule",
        source_file="core/dev-standards.yaml",
        title="Development Standards",
        source_hash="",
        domain="engineering",
        category="quality",
        severity="P1",
        rules=[
            {"id": "CORE-008", "description": "TDD mandatory"},
            {"id": "CORE-011", "description": "Type hints required"},
        ],
    )


@pytest.fixture
def wf_model() -> WorkflowTemplateModel:
    return WorkflowTemplateModel(
        id="implement-workflow",
        type="workflow-template",
        source_file="workflows/sdlc/implement-workflow.yaml",
        title="Implementation Workflow",
        source_hash="",
        version="2.0",
        category="sdlc",
        steps=[
            {"name": "validate", "action": "holistic gate"},
            {"name": "implement", "action": "code changes"},
            {"name": "test", "action": "convergence loop"},
        ],
    )


@pytest.fixture
def pattern_model() -> PatternModel:
    return PatternModel(
        id="strategy-pattern",
        type="pattern",
        source_file="patterns/strategy.yaml",
        title="Strategy Pattern",
        source_hash="",
        pattern_name="Strategy",
        pattern_type="behavioral",
        description="Encapsulate a family of algorithms",
    )


# ═══════════════════════════════════════════════════════════════════════════════
# BusinessLensWriter Tests
# ═══════════════════════════════════════════════════════════════════════════════


class TestBusinessLensSummary:
    """generate_summary() must produce a business-language description."""

    def test_returns_string(self, writer: BusinessLensWriter, gov_model: GovernanceRuleModel) -> None:
        summary = writer.generate_summary(gov_model)
        assert isinstance(summary, str)

    def test_non_empty(self, writer: BusinessLensWriter, gov_model: GovernanceRuleModel) -> None:
        summary = writer.generate_summary(gov_model)
        assert len(summary) > 10

    def test_includes_title(self, writer: BusinessLensWriter, gov_model: GovernanceRuleModel) -> None:
        summary = writer.generate_summary(gov_model)
        assert "Development Standards" in summary

    def test_governance_mentions_rules(self, writer: BusinessLensWriter, gov_model: GovernanceRuleModel) -> None:
        summary = writer.generate_summary(gov_model)
        assert "rule" in summary.lower() or "2" in summary

    def test_workflow_mentions_steps(self, writer: BusinessLensWriter, wf_model: WorkflowTemplateModel) -> None:
        summary = writer.generate_summary(wf_model)
        assert "step" in summary.lower() or "3" in summary

    def test_pattern_mentions_type(self, writer: BusinessLensWriter, pattern_model: PatternModel) -> None:
        summary = writer.generate_summary(pattern_model)
        assert "behavioral" in summary.lower() or "strategy" in summary.lower()


class TestBusinessLensBatch:
    """generate_all() must process a list of models."""

    def test_batch_returns_list(
        self, writer: BusinessLensWriter, gov_model: GovernanceRuleModel, wf_model: WorkflowTemplateModel
    ) -> None:
        results = writer.generate_all([gov_model, wf_model])
        assert isinstance(results, list)
        assert len(results) == 2

    def test_batch_item_has_id_and_summary(
        self, writer: BusinessLensWriter, gov_model: GovernanceRuleModel
    ) -> None:
        results = writer.generate_all([gov_model])
        assert results[0]["id"] == "core-dev"
        assert "summary" in results[0]

    def test_empty_list(self, writer: BusinessLensWriter) -> None:
        results = writer.generate_all([])
        assert results == []


class TestBusinessLensGenericFallback:
    """Generic models should get a basic summary too."""

    def test_generic_model_summary(self, writer: BusinessLensWriter) -> None:
        model = GenericModel(
            id="misc-config",
            type="generic",
            source_file="misc/config.yaml",
            title="Misc Config",
            source_hash="",
            raw_data={"key": "value"},
        )
        summary = writer.generate_summary(model)
        assert isinstance(summary, str)
        assert len(summary) > 0

    def test_to_json(
        self, writer: BusinessLensWriter, gov_model: GovernanceRuleModel
    ) -> None:
        results = writer.generate_all([gov_model])
        json_str = writer.to_json(results)
        parsed = json.loads(json_str)
        assert len(parsed) == 1


# AC_COMPLETE: AC-P125-H-001 ✅
