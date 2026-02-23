"""
Tests for WorkflowTemplateRegistry — including TemplateComposer fallback integration.

AC_START: AC-PHASE55-S3-001
Phase: 55 | Stage: 3 | Priority: P1
Description: RED phase — registry/composer integration tests
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from pathlib import Path
from typing import Any, Dict


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: Core registry behaviour (baseline)
# ═══════════════════════════════════════════════════════════════════════════════


class TestWorkflowTemplateRegistryCore:
    """Baseline tests for WorkflowTemplateRegistry registration and retrieval."""

    def test_register_and_retrieve_template(self) -> None:
        """Should register and retrieve a template by ID."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()
        registry.register_template(
            {"id": "test/my-template", "name": "My Template", "steps": []}
        )

        result = registry.get_template("test/my-template")
        assert result["id"] == "test/my-template"
        assert result["name"] == "My Template"

    def test_get_unknown_template_raises_without_composer(self) -> None:
        """Should raise TemplateNotFoundError when no composer is wired and ID unknown."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
            TemplateNotFoundError,
        )

        registry = WorkflowTemplateRegistry()
        with pytest.raises(TemplateNotFoundError):
            registry.get_template("nonexistent/template-id")

    def test_list_templates_returns_registered(self) -> None:
        """list_templates should return all registered templates."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()
        registry.register_template({"id": "cat/a", "name": "A", "category": "tdd", "steps": []})
        registry.register_template({"id": "cat/b", "name": "B", "category": "api", "steps": []})

        all_templates = registry.list_templates()
        ids = [t["id"] for t in all_templates]
        assert "cat/a" in ids
        assert "cat/b" in ids

    def test_list_templates_filters_by_category(self) -> None:
        """list_templates(category=...) should return only matching templates."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()
        registry.register_template({"id": "cat/a", "name": "A", "category": "tdd", "steps": []})
        registry.register_template({"id": "cat/b", "name": "B", "category": "api", "steps": []})

        tdd_only = registry.list_templates(category="tdd")
        assert len(tdd_only) == 1
        assert tdd_only[0]["id"] == "cat/a"

    def test_register_duplicate_keeps_existing_by_default(self) -> None:
        """Re-registering the same ID without override=True should keep original."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()
        registry.register_template({"id": "t/x", "name": "Original", "steps": []})
        registry.register_template({"id": "t/x", "name": "Duplicate", "steps": []})

        result = registry.get_template("t/x")
        assert result["name"] == "Original"

    def test_register_with_override_replaces_template(self) -> None:
        """Re-registering with override=True should replace the existing template."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()
        registry.register_template({"id": "t/y", "name": "Original", "steps": []})
        registry.register_template(
            {"id": "t/y", "name": "Replacement", "steps": [], "source": "company"},
            override=True,
        )

        result = registry.get_template("t/y")
        assert result["name"] == "Replacement"

    def test_mode_detection_returns_string(self) -> None:
        """detect_mode() should return 'ARCHITECT' or 'PRODUCTION'."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()
        mode = registry.detect_mode()
        assert mode in ("ARCHITECT", "PRODUCTION")

    def test_placeholder_resolution_architect_mode(self) -> None:
        """Placeholders should resolve using ARCHITECT context when mode=ARCHITECT."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry()
        resolved = registry.resolve_placeholders(
            "Use {{test_framework}} for tests.", mode="ARCHITECT"
        )
        assert "pytest" in resolved

    def test_placeholder_resolution_raises_for_unknown_key(self) -> None:
        """Should raise PlaceholderResolutionError for unresolvable placeholder."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
            PlaceholderResolutionError,
        )

        registry = WorkflowTemplateRegistry()
        with pytest.raises(PlaceholderResolutionError):
            registry.resolve_placeholders(
                "{{totally_unknown_key}} should fail.", mode="ARCHITECT"
            )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: TemplateComposer fallback integration
# ═══════════════════════════════════════════════════════════════════════════════


class TestRegistryComposerFallback:
    """Tests for TemplateComposer fallback inside WorkflowTemplateRegistry.get_template().

    Verifies the P1 integration: when get_template() cannot find a registered
    template, it should delegate to TemplateComposer, auto-register the result,
    and return it — rather than raising TemplateNotFoundError.
    """

    def _make_primitives_dir(self, tmp_path: Path) -> Path:
        """Create a minimal primitives dir with one analysis primitive."""
        prims = tmp_path / "primitives"
        prims.mkdir()
        analysis_dir = prims / "analysis"
        analysis_dir.mkdir()
        (analysis_dir / "lens-ast-scan.yaml").write_text(
            "template_id: 'primitives/analysis/lens-ast-scan'\n"
            "name: 'LENS AST Scan'\n"
            "tier: 'primitive'\n"
            "category: 'analysis'\n"
            "status: 'active'\n"
            "execution:\n"
            "  steps:\n"
            "    - step_id: 'scan'\n"
            "      name: 'Run AST analysis'\n"
            "      orchestrator: 'LENSOrchestrator'\n"
        )
        validation_dir = prims / "validation"
        validation_dir.mkdir()
        (validation_dir / "regression-test.yaml").write_text(
            "template_id: 'primitives/validation/regression-test'\n"
            "name: 'Regression Test'\n"
            "tier: 'primitive'\n"
            "category: 'validation'\n"
            "status: 'active'\n"
            "execution:\n"
            "  steps:\n"
            "    - step_id: 'test'\n"
            "      name: 'Run regression tests'\n"
            "      orchestrator: 'TDDOrchestrator'\n"
        )
        execution_dir = prims / "execution"
        execution_dir.mkdir()
        (execution_dir / "semantic-edit.yaml").write_text(
            "template_id: 'primitives/execution/semantic-edit'\n"
            "name: 'Semantic Edit'\n"
            "tier: 'primitive'\n"
            "category: 'execution'\n"
            "status: 'active'\n"
            "execution:\n"
            "  steps:\n"
            "    - step_id: 'edit'\n"
            "      name: 'Apply semantic edits'\n"
            "      orchestrator: 'RefactoringOrchestrator'\n"
        )
        return prims

    def test_get_template_falls_back_to_composer_for_unknown_id(
        self, tmp_path: Path
    ) -> None:
        """get_template() with an unknown ID should invoke composer and return result."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        prims = self._make_primitives_dir(tmp_path)
        composites = tmp_path / "composites"
        composites.mkdir()

        registry = WorkflowTemplateRegistry(
            primitives_dir=prims,
            composites_dir=composites,
        )

        # "custom/refactor-module" is not registered — should compose on-the-fly
        result = registry.get_template("custom/refactor-module")

        assert result is not None
        assert "id" in result
        assert "steps" in result
        assert len(result["steps"]) > 0

    def test_fallback_composed_template_has_convergence_gate(
        self, tmp_path: Path
    ) -> None:
        """Composed fallback template must include a convergence_gate."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        prims = self._make_primitives_dir(tmp_path)
        registry = WorkflowTemplateRegistry(primitives_dir=prims)

        result = registry.get_template("custom/fix-broken-imports")

        assert "convergence_gate" in result
        gate = result["convergence_gate"]
        assert "max_cycles" in gate
        assert "success_predicate" in gate

    def test_fallback_template_auto_registered_for_subsequent_calls(
        self, tmp_path: Path
    ) -> None:
        """After composer fallback, subsequent get_template() for same op should use cache."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        prims = self._make_primitives_dir(tmp_path)
        registry = WorkflowTemplateRegistry(primitives_dir=prims)

        result1 = registry.get_template("custom/implement-feature")
        result2 = registry.get_template("custom/implement-feature")

        # Same object / same ID returned both times
        assert result1["id"] == result2["id"]

    def test_get_template_raises_when_composer_also_fails(
        self, tmp_path: Path
    ) -> None:
        """Should raise TemplateNotFoundError when composer returns None (no primitives)."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
            TemplateNotFoundError,
        )

        # Empty primitives dir — composer will return None
        empty_prims = tmp_path / "primitives"
        empty_prims.mkdir()

        registry = WorkflowTemplateRegistry(primitives_dir=empty_prims)

        with pytest.raises(TemplateNotFoundError):
            registry.get_template("custom/unknown-operation")

    def test_no_primitives_dir_raises_as_before(self) -> None:
        """Without primitives_dir kwarg, old TemplateNotFoundError behaviour preserved."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
            TemplateNotFoundError,
        )

        registry = WorkflowTemplateRegistry()

        with pytest.raises(TemplateNotFoundError):
            registry.get_template("any/unknown-id")

    def test_fallback_extracts_operation_from_template_id(
        self, tmp_path: Path
    ) -> None:
        """Registry should parse operation type from the template ID path segment."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        prims = self._make_primitives_dir(tmp_path)
        registry = WorkflowTemplateRegistry(primitives_dir=prims)

        # ID format: "{namespace}/{operation_type}-{description}"
        result = registry.get_template("custom/refactor-legacy-auth-module")

        assert result is not None
        # Metadata should reflect the parsed operation type
        assert result.get("metadata", {}).get("operation_type") == "refactor"

    def test_fallback_persists_to_composites_when_dir_provided(
        self, tmp_path: Path
    ) -> None:
        """Composer fallback should persist the YAML to composites_dir."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        prims = self._make_primitives_dir(tmp_path)
        composites = tmp_path / "composites"
        composites.mkdir()

        registry = WorkflowTemplateRegistry(
            primitives_dir=prims,
            composites_dir=composites,
        )

        registry.get_template("custom/deploy-to-staging")

        yaml_files = list(composites.glob("*.yaml"))
        assert len(yaml_files) == 1, (
            "Expected exactly 1 YAML file in composites after fallback composition."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 3: Real-registry integration
# ═══════════════════════════════════════════════════════════════════════════════


class TestRegistryWithRealPrimitives:
    """Integration tests using the real cortex-registry primitives."""

    REAL_PRIMITIVES_DIR = (
        Path(__file__).resolve().parents[3]
        / "cortex-registry"
        / "workflows"
        / "templates"
        / "primitives"
    )

    @pytest.mark.skipif(
        not (
            Path(__file__).resolve().parents[3]
            / "cortex-registry"
            / "workflows"
            / "templates"
            / "primitives"
        ).exists(),
        reason="cortex-registry primitives directory not present",
    )
    def test_registry_composes_from_real_primitives_on_fallback(self) -> None:
        """get_template() fallback should produce non-empty steps from real registry."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry(primitives_dir=self.REAL_PRIMITIVES_DIR)
        result = registry.get_template("custom/refactor-legacy-module")

        assert result is not None
        assert len(result["steps"]) > 0

    @pytest.mark.skipif(
        not (
            Path(__file__).resolve().parents[3]
            / "cortex-registry"
            / "workflows"
            / "templates"
            / "primitives"
        ).exists(),
        reason="cortex-registry primitives directory not present",
    )
    def test_registry_fallback_category_is_composed(self) -> None:
        """Fallback composed template should have category='composed'."""
        from cortex.orchestrators.workflow.template_registry import (
            WorkflowTemplateRegistry,
        )

        registry = WorkflowTemplateRegistry(primitives_dir=self.REAL_PRIMITIVES_DIR)
        result = registry.get_template("custom/fix-database-migrations")

        assert result["category"] == "composed"


# AC_COMPLETE: AC-PHASE55-S3-001 ✅ RED phase — registry/composer integration tests
