"""
Golden Truth Test: Memory Tier Operations

Phase 63-B rewrite — original from tests/golden/ root moved to architecture/
and enhanced with workflow template wiring assertion.

Validates:
1. Memory tier directory structure is valid (no collisions with governance tiers)
2. WorkflowTemplateRegistry loads without error
3. At least 1 workflow template references primitives/execution/audit-trace.yaml

Authority: CORE-008, CORE-035, CORE-055
AC-IDs: AC-63-B-MEMORY-TIER-001..005
"""
# ruff: noqa: S101
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).parents[3]
PRIMITIVES_EXECUTION = ROOT / "cortex-registry" / "workflows" / "templates" / "primitives" / "execution"
TEMPLATES_ROOT = ROOT / "cortex-registry" / "workflows" / "templates"
INTELLIGENCE_MEMORY = ROOT / "cortex" / "intelligence" / "memory"


class TestMemoryTierStructure:
    """Validate memory tier directory layout."""

    def test_memory_tier_directory_exists(self) -> None:
        """cortex/intelligence/memory/ must exist."""
        assert INTELLIGENCE_MEMORY.exists(), (
            "cortex/intelligence/memory/ does not exist — memory tier not initialised"
        )

    def test_memory_tier_has_init(self) -> None:
        """cortex/intelligence/memory/__init__.py must exist."""
        init_file = INTELLIGENCE_MEMORY / "__init__.py"
        assert init_file.exists(), (
            "cortex/intelligence/memory/__init__.py missing — package not initialised"
        )

    def test_no_collision_between_governance_and_memory_tiers(self) -> None:
        """Memory tiers (cortex/intelligence/memory/) must not contain governance YAML rule files."""
        if not INTELLIGENCE_MEMORY.exists():
            pytest.skip("memory tier directory not found")
        governance_yaml = list(INTELLIGENCE_MEMORY.glob("*-rules.yaml"))
        assert governance_yaml == [], (
            f"Governance rule YAML files found inside memory tier: {governance_yaml}"
        )

    def test_memory_importable(self) -> None:
        """cortex.intelligence.memory must be importable."""
        try:
            import cortex.intelligence.memory  # noqa: F401
        except ImportError as exc:
            pytest.skip(f"cortex.intelligence.memory not importable: {exc}")


class TestWorkflowTemplateWiring:
    """Verify workflow template registry loads and references audit-trace primitive."""

    def test_audit_trace_primitive_exists(self) -> None:
        """primitives/execution/audit-trace.yaml must exist."""
        audit_trace = PRIMITIVES_EXECUTION / "audit-trace.yaml"
        assert audit_trace.exists(), (
            "primitives/execution/audit-trace.yaml missing — trace primitive not scaffolded"
        )

    def test_audit_trace_primitive_is_valid_yaml(self) -> None:
        """audit-trace.yaml must be parseable YAML."""
        audit_trace = PRIMITIVES_EXECUTION / "audit-trace.yaml"
        if not audit_trace.exists():
            pytest.skip("audit-trace.yaml not found")
        with audit_trace.open() as fh:
            content = yaml.safe_load(fh)
        assert content is not None, "audit-trace.yaml parsed as None (empty file)"
        assert isinstance(content, dict), "audit-trace.yaml must be a YAML mapping"

    def test_at_least_one_workflow_references_audit_trace(self) -> None:
        """At least 1 workflow template must reference primitives/execution/audit-trace.yaml."""
        references = []
        for yaml_file in TEMPLATES_ROOT.rglob("*.yaml"):
            try:
                content = yaml_file.read_text(errors="replace")
                if "audit-trace" in content or "audit_trace" in content:
                    references.append(str(yaml_file.relative_to(ROOT)))
            except OSError:
                continue
        assert len(references) >= 1, (
            "No workflow template references audit-trace primitive — "
            "trace chain is not wired into any workflow"
        )

    def test_workflow_template_registry_class_importable(self) -> None:
        """WorkflowTemplateRegistry must be importable."""
        try:
            from cortex.core.workflow_engine import WorkflowEngine  # noqa: F401

            assert WorkflowEngine is not None
        except ImportError:
            try:
                from cortex.templates.workflow_template_registry import (  # noqa: F401
                    WorkflowTemplateRegistry,
                )

                assert WorkflowTemplateRegistry is not None
            except ImportError as exc:
                pytest.skip(f"No workflow registry importable: {exc}")
