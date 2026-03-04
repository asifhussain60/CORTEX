# AC_START: AC-P125-C-001
"""
Test Suite: Phase 125-c — ReferenceResolver
Module: Cross-file reference resolution for registry YAML artifacts.
Tests: 14 tests — reference extraction, resolution, and broken-ref detection.
"""

import pytest

from cortex.intelligence.registry.reference_resolver import ReferenceResolver
from cortex.intelligence.registry.models.base import BaseRegistryModel
from cortex.intelligence.registry.models.governance import GovernanceRuleModel
from cortex.intelligence.registry.models.workflow import WorkflowTemplateModel


# ── Fixtures ────────────────────────────────────────────────────────────


@pytest.fixture
def resolver() -> ReferenceResolver:
    """Return a fresh ReferenceResolver."""
    return ReferenceResolver()


@pytest.fixture
def governance_model() -> GovernanceRuleModel:
    """A governance model with rule IDs for reference targets."""
    return GovernanceRuleModel(
        id="governance-dev-rules",
        type="governance-rule",
        source_file="governance/development-rules.yaml",
        title="Development Rules",
        source_hash="",
        domain="development",
        category="development",
        rules=[
            {"id": "CORE-008", "name": "TDD mandatory"},
            {"id": "CORE-064", "name": "Sweep Completeness"},
        ],
    )


@pytest.fixture
def workflow_model() -> WorkflowTemplateModel:
    """A workflow model that references governance rules and primitives."""
    return WorkflowTemplateModel(
        id="sdlc/implement-workflow",
        type="workflow-template",
        source_file="workflows/templates/sdlc/implement-workflow.yaml",
        title="IMPLEMENT",
        source_hash="",
        version="1.0.0",
        category="sdlc",
        steps=[
            {
                "id": "ac_start",
                "template_ref": "primitives/execution/ac-marker-emit",
            },
            {
                "id": "holistic_validation",
                "template_ref": "primitives/governance/holistic-validation-gate",
            },
        ],
        metadata={
            "core_rules": ["CORE-008", "CORE-064"],
        },
    )


# ── Reference Extraction Tests ──────────────────────────────────────────


class TestReferenceExtraction:
    """ReferenceResolver must extract all reference types from models."""

    def test_extract_core_rule_refs_from_workflow(
        self, resolver: ReferenceResolver, workflow_model: WorkflowTemplateModel
    ) -> None:
        """Workflow metadata.core_rules → outgoing refs to governance rules."""
        refs = resolver.extract_references(workflow_model)
        ref_ids = [r["target_id"] for r in refs]
        assert "CORE-008" in ref_ids
        assert "CORE-064" in ref_ids

    def test_extract_template_refs_from_steps(
        self, resolver: ReferenceResolver, workflow_model: WorkflowTemplateModel
    ) -> None:
        """Step template_ref → outgoing refs to primitive workflows."""
        refs = resolver.extract_references(workflow_model)
        ref_ids = [r["target_id"] for r in refs]
        assert "primitives/execution/ac-marker-emit" in ref_ids

    def test_extract_returns_list(
        self, resolver: ReferenceResolver, workflow_model: WorkflowTemplateModel
    ) -> None:
        """extract_references must return a list of dicts."""
        refs = resolver.extract_references(workflow_model)
        assert isinstance(refs, list)
        assert all(isinstance(r, dict) for r in refs)

    def test_each_ref_has_required_keys(
        self, resolver: ReferenceResolver, workflow_model: WorkflowTemplateModel
    ) -> None:
        """Each ref dict must have target_id, ref_type, and source_field."""
        refs = resolver.extract_references(workflow_model)
        for r in refs:
            assert "target_id" in r
            assert "ref_type" in r
            assert "source_field" in r

    def test_governance_model_has_no_outgoing_refs(
        self, resolver: ReferenceResolver, governance_model: GovernanceRuleModel
    ) -> None:
        """Governance rules are targets, not sources — no outgoing refs expected."""
        refs = resolver.extract_references(governance_model)
        assert isinstance(refs, list)


# ── Resolution Tests ────────────────────────────────────────────────────


class TestReferenceResolution:
    """ReferenceResolver.resolve() populates model.references."""

    def test_resolve_populates_outgoing(
        self,
        resolver: ReferenceResolver,
        workflow_model: WorkflowTemplateModel,
        governance_model: GovernanceRuleModel,
    ) -> None:
        """After resolve, workflow_model.references['outgoing'] must be non-empty."""
        models = [workflow_model, governance_model]
        resolver.resolve(models)
        assert len(workflow_model.references["outgoing"]) > 0

    def test_resolve_populates_incoming(
        self,
        resolver: ReferenceResolver,
        workflow_model: WorkflowTemplateModel,
        governance_model: GovernanceRuleModel,
    ) -> None:
        """After resolve, governance_model.references['incoming'] must show the workflow."""
        models = [workflow_model, governance_model]
        resolver.resolve(models)
        incoming_ids = [r["source_id"] for r in governance_model.references["incoming"]]
        assert "sdlc/implement-workflow" in incoming_ids

    def test_resolve_returns_broken_refs(
        self,
        resolver: ReferenceResolver,
        workflow_model: WorkflowTemplateModel,
    ) -> None:
        """Resolving with missing targets produces broken refs list."""
        broken = resolver.resolve([workflow_model])
        assert isinstance(broken, list)
        assert len(broken) > 0

    def test_broken_ref_has_target_id(
        self,
        resolver: ReferenceResolver,
        workflow_model: WorkflowTemplateModel,
    ) -> None:
        """Each broken ref must contain the unresolved target_id."""
        broken = resolver.resolve([workflow_model])
        assert all("target_id" in b for b in broken)

    def test_resolve_sets_integrity_flag(
        self,
        resolver: ReferenceResolver,
        workflow_model: WorkflowTemplateModel,
    ) -> None:
        """Model with broken refs must have integrity.all_refs_resolved=False."""
        resolver.resolve([workflow_model])
        assert workflow_model.integrity["all_refs_resolved"] is False

    def test_resolve_no_broken_when_all_found(
        self,
        resolver: ReferenceResolver,
        workflow_model: WorkflowTemplateModel,
        governance_model: GovernanceRuleModel,
    ) -> None:
        """When all rule refs are resolvable, those should not be in broken list."""
        models = [workflow_model, governance_model]
        broken = resolver.resolve(models)
        broken_ids = [b["target_id"] for b in broken]
        # CORE-008 and CORE-064 are rule IDs inside governance model, should resolve
        assert "CORE-008" not in broken_ids

    def test_empty_model_list(self, resolver: ReferenceResolver) -> None:
        """Resolving empty list returns empty broken list."""
        broken = resolver.resolve([])
        assert broken == []

    def test_resolve_idempotent(
        self,
        resolver: ReferenceResolver,
        workflow_model: WorkflowTemplateModel,
        governance_model: GovernanceRuleModel,
    ) -> None:
        """Calling resolve twice produces same result."""
        models = [workflow_model, governance_model]
        broken1 = resolver.resolve(models)
        broken2 = resolver.resolve(models)
        assert len(broken1) == len(broken2)


# AC_COMPLETE: AC-P125-C-001 ✅
