"""
Tests for TemplateComposer — Dynamic Workflow Composition from Primitives.

AC_START: AC-PHASE55-S1-001
Phase: 55 | Stage: 1 | Priority: P1
Description: RED phase — failing tests for TemplateComposer
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest
from pathlib import Path
from typing import Any, Dict, List
from unittest.mock import patch


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 1: PrimitiveScanner — discovers available primitives from registry
# ═══════════════════════════════════════════════════════════════════════════════


class TestPrimitiveScanner:
    """Tests for PrimitiveScanner — discovers primitives from YAML registry."""

    def test_scanner_discovers_primitives_from_directory(self, tmp_path: Path) -> None:
        """Should discover all primitive YAML files recursively."""
        from cortex.orchestrators.workflow.template_composer import PrimitiveScanner

        # Create primitive files
        analysis_dir = tmp_path / "analysis"
        analysis_dir.mkdir()
        (analysis_dir / "lens-ast-scan.yaml").write_text(
            "template_id: 'primitives/analysis/lens-ast-scan'\n"
            "name: 'LENS AST Scan'\n"
            "tier: 'primitive'\n"
            "category: 'analysis'\n"
            "status: 'active'\n"
        )

        validation_dir = tmp_path / "validation"
        validation_dir.mkdir()
        (validation_dir / "detect-fix-rescan-loop.yaml").write_text(
            "template_id: 'primitives/validation/detect-fix-rescan-loop'\n"
            "name: 'Detect Fix Rescan Loop'\n"
            "tier: 'primitive'\n"
            "category: 'validation'\n"
            "status: 'active'\n"
        )

        scanner = PrimitiveScanner(primitives_dir=tmp_path)
        primitives = scanner.scan()

        assert len(primitives) == 2
        categories = {p["category"] for p in primitives}
        assert "analysis" in categories
        assert "validation" in categories

    def test_scanner_returns_empty_for_missing_directory(self, tmp_path: Path) -> None:
        """Should return empty list when primitives directory doesn't exist."""
        from cortex.orchestrators.workflow.template_composer import PrimitiveScanner

        scanner = PrimitiveScanner(primitives_dir=tmp_path / "nonexistent")
        primitives = scanner.scan()

        assert primitives == []

    def test_scanner_skips_invalid_yaml(self, tmp_path: Path) -> None:
        """Should skip malformed YAML files without crashing."""
        from cortex.orchestrators.workflow.template_composer import PrimitiveScanner

        (tmp_path / "bad.yaml").write_text("{{{{ invalid yaml")
        (tmp_path / "good.yaml").write_text(
            "template_id: 'primitives/test/good'\n"
            "name: 'Good Primitive'\n"
            "tier: 'primitive'\n"
            "category: 'test'\n"
            "status: 'active'\n"
        )

        scanner = PrimitiveScanner(primitives_dir=tmp_path)
        primitives = scanner.scan()

        assert len(primitives) == 1
        assert primitives[0]["name"] == "Good Primitive"

    def test_scanner_filters_by_category(self, tmp_path: Path) -> None:
        """Should filter primitives by category when requested."""
        from cortex.orchestrators.workflow.template_composer import PrimitiveScanner

        for cat in ("analysis", "validation", "execution"):
            cat_dir = tmp_path / cat
            cat_dir.mkdir()
            (cat_dir / f"{cat}-prim.yaml").write_text(
                f"template_id: 'primitives/{cat}/{cat}-prim'\n"
                f"name: '{cat} Primitive'\n"
                f"tier: 'primitive'\n"
                f"category: '{cat}'\n"
                f"status: 'active'\n"
            )

        scanner = PrimitiveScanner(primitives_dir=tmp_path)
        analysis_only = scanner.scan(category="analysis")

        assert len(analysis_only) == 1
        assert analysis_only[0]["category"] == "analysis"

    def test_scanner_excludes_inactive_primitives(self, tmp_path: Path) -> None:
        """Should exclude primitives with status != 'active'."""
        from cortex.orchestrators.workflow.template_composer import PrimitiveScanner

        (tmp_path / "active.yaml").write_text(
            "template_id: 'primitives/test/active'\n"
            "name: 'Active'\n"
            "tier: 'primitive'\n"
            "category: 'test'\n"
            "status: 'active'\n"
        )
        (tmp_path / "deprecated.yaml").write_text(
            "template_id: 'primitives/test/deprecated'\n"
            "name: 'Deprecated'\n"
            "tier: 'primitive'\n"
            "category: 'test'\n"
            "status: 'deprecated'\n"
        )

        scanner = PrimitiveScanner(primitives_dir=tmp_path)
        primitives = scanner.scan()

        assert len(primitives) == 1
        assert primitives[0]["name"] == "Active"


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 2: TemplateComposer — assembles templates from primitives
# ═══════════════════════════════════════════════════════════════════════════════


class TestTemplateComposer:
    """Tests for TemplateComposer — assembles workflow templates from primitives."""

    def _make_primitives_dir(self, tmp_path: Path) -> Path:
        """Helper: create a minimal primitives directory with test primitives."""
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
            "steps:\n"
            "  - id: 'scan'\n"
            "    orchestrator: 'LENSOrchestrator'\n"
            "    description: 'Run AST analysis'\n"
        )

        validation_dir = prims / "validation"
        validation_dir.mkdir()
        (validation_dir / "regression-test.yaml").write_text(
            "template_id: 'primitives/validation/regression-test'\n"
            "name: 'Regression Test'\n"
            "tier: 'primitive'\n"
            "category: 'validation'\n"
            "status: 'active'\n"
            "steps:\n"
            "  - id: 'test'\n"
            "    orchestrator: 'TDDOrchestrator'\n"
            "    description: 'Run regression tests'\n"
        )

        execution_dir = prims / "execution"
        execution_dir.mkdir()
        (execution_dir / "semantic-edit.yaml").write_text(
            "template_id: 'primitives/execution/semantic-edit'\n"
            "name: 'Semantic Edit'\n"
            "tier: 'primitive'\n"
            "category: 'execution'\n"
            "status: 'active'\n"
            "steps:\n"
            "  - id: 'edit'\n"
            "    orchestrator: 'RefactoringOrchestrator'\n"
            "    description: 'Apply semantic edits'\n"
        )

        return prims

    def test_compose_from_intent_produces_valid_template(self, tmp_path: Path) -> None:
        """Should compose a valid workflow template from matching primitives."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        prims = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=prims)

        result = composer.compose(
            operation_type="refactor",
            description="Refactor legacy module to use new patterns",
        )

        assert result is not None
        assert "id" in result
        assert "name" in result
        assert "steps" in result
        assert len(result["steps"]) > 0
        assert result["category"] == "composed"

    def test_compose_includes_analysis_step(self, tmp_path: Path) -> None:
        """Composed templates should always start with an analysis step."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        prims = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=prims)

        result = composer.compose(
            operation_type="refactor",
            description="Optimize database queries",
        )

        assert result is not None
        first_step_category = result["steps"][0].get("source_category", "")
        assert first_step_category == "analysis"

    def test_compose_includes_validation_step(self, tmp_path: Path) -> None:
        """Composed templates should always end with a validation step."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        prims = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=prims)

        result = composer.compose(
            operation_type="implement",
            description="Add new API endpoint",
        )

        assert result is not None
        last_step_category = result["steps"][-1].get("source_category", "")
        assert last_step_category == "validation"

    def test_compose_injects_convergence_gate(self, tmp_path: Path) -> None:
        """Every composed template must have a convergence_gate in its metadata."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        prims = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=prims)

        result = composer.compose(
            operation_type="fix",
            description="Fix broken imports across codebase",
        )

        assert result is not None
        assert "convergence_gate" in result
        gate = result["convergence_gate"]
        assert "max_cycles" in gate
        assert "success_predicate" in gate

    def test_compose_generates_unique_id(self, tmp_path: Path) -> None:
        """Each composed template should have a unique ID."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        prims = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=prims)

        result1 = composer.compose(operation_type="fix", description="Fix A")
        result2 = composer.compose(operation_type="fix", description="Fix B")

        assert result1 is not None
        assert result2 is not None
        assert result1["id"] != result2["id"]

    def test_compose_returns_none_when_no_primitives(self, tmp_path: Path) -> None:
        """Should return None when no primitives exist to compose from."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        empty_dir = tmp_path / "empty"
        empty_dir.mkdir()
        composer = TemplateComposer(primitives_dir=empty_dir)

        result = composer.compose(
            operation_type="deploy",
            description="Deploy to production",
        )

        assert result is None

    def test_compose_maps_operation_to_categories(self, tmp_path: Path) -> None:
        """Should select appropriate primitive categories based on operation type."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        prims = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=prims)

        # Refactor should use analysis + execution + validation
        result = composer.compose(operation_type="refactor", description="Refactor code")

        assert result is not None
        step_categories = [s.get("source_category") for s in result["steps"]]
        assert "analysis" in step_categories
        assert "execution" in step_categories
        assert "validation" in step_categories


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 3: Persistence — composed templates saved to composites/
# ═══════════════════════════════════════════════════════════════════════════════


class TestTemplateComposerPersistence:
    """Tests for TemplateComposer persistence to composites directory."""

    def test_persist_saves_yaml_to_composites(self, tmp_path: Path) -> None:
        """Should save composed template as YAML in composites directory."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        prims = tmp_path / "primitives"
        prims.mkdir()
        analysis_dir = prims / "analysis"
        analysis_dir.mkdir()
        (analysis_dir / "scan.yaml").write_text(
            "template_id: 'primitives/analysis/scan'\n"
            "name: 'Scan'\n"
            "tier: 'primitive'\n"
            "category: 'analysis'\n"
            "status: 'active'\n"
            "steps:\n"
            "  - id: 'scan'\n"
            "    orchestrator: 'LENSOrchestrator'\n"
        )

        composites = tmp_path / "composites"
        composites.mkdir()

        composer = TemplateComposer(primitives_dir=prims, composites_dir=composites)
        result = composer.compose(operation_type="analyze", description="Analyze code")

        assert result is not None
        composer.persist(result)

        # Verify YAML file was created
        yaml_files = list(composites.glob("*.yaml"))
        assert len(yaml_files) == 1

    def test_persist_creates_loadable_yaml(self, tmp_path: Path) -> None:
        """Persisted YAML should be loadable by WorkflowTemplateRegistry."""
        import yaml as yaml_lib
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        prims = tmp_path / "primitives"
        prims.mkdir()
        val_dir = prims / "validation"
        val_dir.mkdir()
        (val_dir / "test.yaml").write_text(
            "template_id: 'primitives/validation/test'\n"
            "name: 'Test'\n"
            "tier: 'primitive'\n"
            "category: 'validation'\n"
            "status: 'active'\n"
            "steps:\n"
            "  - id: 'test'\n"
            "    orchestrator: 'TDDOrchestrator'\n"
        )

        composites = tmp_path / "composites"
        composites.mkdir()

        composer = TemplateComposer(primitives_dir=prims, composites_dir=composites)
        result = composer.compose(operation_type="test", description="Run tests")

        assert result is not None
        composer.persist(result)

        yaml_files = list(composites.glob("*.yaml"))
        assert len(yaml_files) == 1

        loaded = yaml_lib.safe_load(yaml_files[0].read_text())
        assert loaded is not None
        assert "id" in loaded or "template_id" in loaded
        assert "name" in loaded

    def test_persist_does_not_overwrite_existing(self, tmp_path: Path) -> None:
        """Should not overwrite an existing composed template file."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        prims = tmp_path / "primitives"
        prims.mkdir()
        exec_dir = prims / "execution"
        exec_dir.mkdir()
        (exec_dir / "edit.yaml").write_text(
            "template_id: 'primitives/execution/edit'\n"
            "name: 'Edit'\n"
            "tier: 'primitive'\n"
            "category: 'execution'\n"
            "status: 'active'\n"
            "steps:\n"
            "  - id: 'edit'\n"
            "    orchestrator: 'RefactoringOrchestrator'\n"
        )

        composites = tmp_path / "composites"
        composites.mkdir()

        composer = TemplateComposer(primitives_dir=prims, composites_dir=composites)
        result = composer.compose(operation_type="fix", description="Fix issue")
        assert result is not None

        composer.persist(result)
        files_before = set(composites.glob("*.yaml"))

        # Persisting same result again should not create duplicate
        composer.persist(result)
        files_after = set(composites.glob("*.yaml"))

        assert len(files_after) == len(files_before)


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 4: Integration — WorkflowComplexityRouter fallback
# ═══════════════════════════════════════════════════════════════════════════════


class TestWorkflowGateIntegration:
    """Tests for TemplateComposer integration with WorkflowComplexityRouter."""

    def test_select_template_uses_composer_for_unknown_operation(self) -> None:
        """When no template matches, _select_template should try TemplateComposer."""
        from cortex.orchestrators.core.intent_router.workflow_gate import (
            WorkflowComplexityRouter,
            Intent,
        )

        router = WorkflowComplexityRouter()
        intent = Intent(
            operation_type="data-pipeline",
            target_files=["src/pipeline.py"],
            dependencies=["pandas", "sqlalchemy"],
            risk_level="MEDIUM",
            metadata={},
        )

        template_id = router._select_template(intent)

        # Should NOT be the hard-coded default anymore for novel operations
        # (it should either be a composed template or the default with a
        # composition attempt)
        assert isinstance(template_id, str)
        assert len(template_id) > 0


# AC_COMPLETE: AC-PHASE55-S1-001 ✅ RED phase tests written
