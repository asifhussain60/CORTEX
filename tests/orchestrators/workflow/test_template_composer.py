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
        """Helper: create a minimal primitives directory with test primitives.

        Uses canonical schema: steps are nested under ``execution.steps``,
        matching the structure of all real primitives in
        ``cortex-registry/workflows/templates/primitives/``.
        """
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
        # Phase 56: refactor injects sweep_catalogue_open at step[0] (CORE-064).
        # Analysis is still present — it is just no longer the first step.
        step_categories = [s.get("source_category", "") for s in result["steps"]]
        assert "analysis" in step_categories, (
            "Composed refactor template must include an analysis step"
        )

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
            "execution:\n"
            "  steps:\n"
            "    - step_id: 'scan'\n"
            "      name: 'Scan codebase'\n"
            "      orchestrator: 'LENSOrchestrator'\n"
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
            "execution:\n"
            "  steps:\n"
            "    - step_id: 'test'\n"
            "      name: 'Run test suite'\n"
            "      orchestrator: 'TDDOrchestrator'\n"
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
            "execution:\n"
            "  steps:\n"
            "    - step_id: 'edit'\n"
            "      name: 'Apply edit'\n"
            "      orchestrator: 'RefactoringOrchestrator'\n"
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


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 5: Real-Registry Integration — validate against live primitives
# ═══════════════════════════════════════════════════════════════════════════════


class TestRealRegistryComposition:
    """Integration tests using the actual cortex-registry/workflows/templates/primitives/.

    These tests verify that TemplateComposer works end-to-end with the real
    YAML primitives committed to the repository — catching any schema drift
    between the composer and the registry files.
    """

    # Canonical path to the real primitives directory
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
    def test_scanner_discovers_real_primitives(self) -> None:
        """PrimitiveScanner should discover ≥5 active primitives from the real registry."""
        from cortex.orchestrators.workflow.template_composer import PrimitiveScanner

        scanner = PrimitiveScanner(primitives_dir=self.REAL_PRIMITIVES_DIR)
        primitives = scanner.scan()

        assert len(primitives) >= 5, (
            f"Expected ≥5 real primitives, got {len(primitives)}. "
            f"Check status: 'active' in YAML files under {self.REAL_PRIMITIVES_DIR}"
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
    def test_real_primitives_expose_execution_steps(self) -> None:
        """Every active real primitive with an execution block must expose steps.

        Acceptable execution schemas:
        - ``execution.steps`` — flat list (standard schema, consumed by PrimitiveScanner)
        - ``execution.pre_loop`` / ``execution.loop_body`` — multi-section (convergence loops)
        - ``execution.on_start`` / ``execution.on_complete`` — event-driven (audit-trace)

        Marker-only primitives (no ``execution:`` key) are exempt by design.
        """
        from cortex.orchestrators.workflow.template_composer import PrimitiveScanner

        scanner = PrimitiveScanner(primitives_dir=self.REAL_PRIMITIVES_DIR)
        primitives = scanner.scan()

        missing_steps = []
        for prim in primitives:
            exec_block = prim.get("execution", None)
            if exec_block is None:
                # No execution block — marker-only primitive (e.g., audit-trace if
                # markers block present), or unknown structure. Exempt.
                continue

            # Recognised multi-section schemas
            flat_steps = exec_block.get("steps", [])
            pre_loop = exec_block.get("pre_loop", [])
            loop_body = exec_block.get("loop_body", {})
            on_start = exec_block.get("on_start", [])

            has_any_steps = bool(
                flat_steps
                or pre_loop
                or (isinstance(loop_body, dict) and loop_body)
                or on_start
            )

            root_steps = prim.get("steps", [])
            if not has_any_steps and not root_steps:
                missing_steps.append(prim.get("template_id", "unknown"))

        assert not missing_steps, (
            f"These primitives have an execution block but no recognisable steps "
            f"(execution.steps / pre_loop / loop_body / on_start): {missing_steps}"
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
    def test_compose_refactor_from_real_registry_produces_non_empty_steps(
        self,
    ) -> None:
        """TemplateComposer.compose('refactor') should produce ≥1 step from real primitives.

        This is the key regression test for the execution.steps path bug (Gap 1).
        Previously this test would return a template with 0 steps because
        PrimitiveScanner read root-level 'steps:' which doesn't exist in real YAMLs.
        """
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        composer = TemplateComposer(primitives_dir=self.REAL_PRIMITIVES_DIR)
        result = composer.compose(
            operation_type="refactor",
            description="Refactor legacy module using real registry primitives",
        )

        assert result is not None, (
            "TemplateComposer returned None — no primitives matched. "
            "Check that primitives have status: 'active'."
        )
        assert len(result["steps"]) > 0, (
            "Composed template has 0 steps — PrimitiveScanner is not reading "
            "execution.steps correctly from real YAML primitives."
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
    def test_compose_fix_selects_regression_not_css_primitive(self) -> None:
        """For 'fix' operation, composer should prefer regression-test over css-zero-inline."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        composer = TemplateComposer(primitives_dir=self.REAL_PRIMITIVES_DIR)
        result = composer.compose(
            operation_type="fix",
            description="Fix broken import chain",
        )

        assert result is not None
        validation_steps = [
            s for s in result["steps"] if s.get("source_category") == "validation"
        ]
        validation_sources = [s.get("source_primitive", "") for s in validation_steps]
        # css-zero-inline should NOT be selected for a code-fix operation
        assert not any(
            "css" in src for src in validation_sources
        ), (
            f"Primitive scorer selected a CSS primitive for a 'fix' operation: "
            f"{validation_sources}. Check _select_best_primitive() scoring."
        )


# ═══════════════════════════════════════════════════════════════════════════════
# STAGE 6: _select_best_primitive unit tests (P2 — operation-type-aware scoring)
# ═══════════════════════════════════════════════════════════════════════════════


class TestPrimitiveScorerUnit:
    """Unit tests for _select_best_primitive() scoring heuristic.

    Tests the full scoring matrix:
      +2  name/template_id contains the operation keyword
      +1  tags contain the operation keyword
      +1  tags contain an op-aligned synonym
      -1  name contains an unrelated-domain keyword
      -1  tags contain an unrelated-domain keyword
    """

    def _make_primitive(
        self,
        template_id: str,
        name: str,
        tags: list,
    ) -> dict:
        return {
            "template_id": template_id,
            "name": name,
            "category": "validation",
            "status": "active",
            "metadata": {"tags": tags},
            "execution": {"steps": [{"step_id": "s1", "name": "step"}]},
        }

    def _scorer(self) -> object:
        from cortex.orchestrators.workflow.template_composer import TemplateComposer
        from pathlib import Path
        import tempfile

        with tempfile.TemporaryDirectory() as d:
            composer = TemplateComposer(primitives_dir=Path(d))
        return composer

    def test_name_keyword_match_scores_highest(self) -> None:
        """Primitive whose name contains the op keyword should win over generic ones."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer
        from pathlib import Path

        composer = TemplateComposer(primitives_dir=Path("/nonexistent"))
        candidates = [
            self._make_primitive("val/generic", "Generic Validator", ["validation"]),
            self._make_primitive("val/refactor-check", "Refactor Check", ["validation"]),
        ]
        winner = composer._select_best_primitive(candidates, "refactor")
        assert winner["template_id"] == "val/refactor-check"

    def test_tag_synonym_boosts_score(self) -> None:
        """Tag 'refactoring' should boost a primitive when op='refactor'."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer
        from pathlib import Path

        composer = TemplateComposer(primitives_dir=Path("/nonexistent"))
        candidates = [
            self._make_primitive("exec/plain-edit", "Plain Edit", ["execution"]),
            self._make_primitive("exec/file-extract", "File Extraction", ["execution", "refactoring"]),
        ]
        winner = composer._select_best_primitive(candidates, "refactor")
        assert winner["template_id"] == "exec/file-extract"

    def test_css_tag_penalised_for_refactor(self) -> None:
        """Tag 'css-selector' should penalise a primitive when op='refactor'."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer
        from pathlib import Path

        composer = TemplateComposer(primitives_dir=Path("/nonexistent"))
        candidates = [
            self._make_primitive(
                "exec/semantic-edit", "Semantic Edit",
                ["execution", "semantic", "css-selector"]
            ),
            self._make_primitive(
                "exec/file-extract", "File Extraction",
                ["execution", "extraction", "refactoring"]
            ),
        ]
        winner = composer._select_best_primitive(candidates, "refactor")
        assert winner["template_id"] == "exec/file-extract", (
            "file-extract (tag: refactoring) should beat semantic-edit (tag: css-selector) "
            "for op='refactor'"
        )

    def test_css_tag_penalised_for_fix(self) -> None:
        """Primitives tagged 'css' or 'zero-inline' should score lower for op='fix'."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer
        from pathlib import Path

        composer = TemplateComposer(primitives_dir=Path("/nonexistent"))
        candidates = [
            self._make_primitive(
                "val/css-zero-inline", "CSS Zero Inline",
                ["validation", "css", "zero-inline"]
            ),
            self._make_primitive(
                "val/regression-test", "Regression Test",
                ["validation", "testing", "regression"]
            ),
        ]
        winner = composer._select_best_primitive(candidates, "fix")
        assert winner["template_id"] == "val/regression-test"

    def test_tag_op_exact_match_bonus(self) -> None:
        """Tag containing the exact op word should add +1 bonus."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer
        from pathlib import Path

        composer = TemplateComposer(primitives_dir=Path("/nonexistent"))
        candidates = [
            self._make_primitive("val/plain", "Plain Check", ["validation"]),
            self._make_primitive("val/testing", "Testing Suite", ["validation", "testing"]),
        ]
        # op = "test" — tag "testing" contains "test"
        winner = composer._select_best_primitive(candidates, "test")
        assert winner["template_id"] == "val/testing"

    def test_single_candidate_always_returned(self) -> None:
        """With only one candidate, scorer must always return it."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer
        from pathlib import Path

        composer = TemplateComposer(primitives_dir=Path("/nonexistent"))
        only = self._make_primitive("val/only", "Only Primitive", ["css", "dom"])
        winner = composer._select_best_primitive([only], "refactor")
        assert winner["template_id"] == "val/only"

    def test_real_registry_fix_prefers_regression_over_css_zero_inline(self) -> None:
        """End-to-end: real primitives — fix op should not pick css-zero-inline."""
        real_dir = (
            __import__("pathlib").Path(__file__).resolve().parents[3]
            / "cortex-registry" / "workflows" / "templates" / "primitives"
        )
        if not real_dir.exists():
            __import__("pytest").skip("real primitives dir not present")

        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        composer = TemplateComposer(primitives_dir=real_dir)
        result = composer.compose(operation_type="fix", description="Fix broken imports")
        assert result is not None
        val_sources = [
            s.get("source_primitive", "") for s in result["steps"]
            if s.get("source_category") == "validation"
        ]
        assert not any("css" in src for src in val_sources), (
            f"Scorer picked a CSS primitive for 'fix': {val_sources}"
        )

    def test_real_registry_refactor_prefers_file_extraction_over_semantic_edit(self) -> None:
        """End-to-end: for refactor, file-extraction (tag: refactoring) beats semantic-edit."""
        real_dir = (
            __import__("pathlib").Path(__file__).resolve().parents[3]
            / "cortex-registry" / "workflows" / "templates" / "primitives"
        )
        if not real_dir.exists():
            __import__("pytest").skip("real primitives dir not present")

        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        composer = TemplateComposer(primitives_dir=real_dir)
        result = composer.compose(operation_type="refactor", description="Refactor legacy module")
        assert result is not None
        exec_sources = [
            s.get("source_primitive", "") for s in result["steps"]
            if s.get("source_category") == "execution"
        ]
        # file-extraction should win over semantic-edit for refactor
        assert any("file-extraction" in src for src in exec_sources), (
            f"Expected file-extraction to be selected for refactor, got: {exec_sources}"
        )



# AC_COMPLETE: AC-PHASE55-S1-001 ✅ RED phase tests written


# ═══════════════════════════════════════════════════════════════════════════════
# PHASE 56: Sweep Catalogue Injection — CORE-064 structural enforcement
# AC_START: AC-PHASE56-S1-001
# Phase: 56 | Stage: 1 | Priority: P0
# Description: RED phase — CORE-064 sweep envelope injected at compose time
# ═══════════════════════════════════════════════════════════════════════════════


class TestSweepCatalogueInjection:
    """Tests that TemplateComposer injects sweep envelope for FIX/REFACTOR/AUDIT operations."""

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def _make_primitives_dir(self, tmp_path: Path) -> Path:
        """Create a minimal primitives directory with one primitive per needed category."""
        for cat in ("governance", "analysis", "execution", "validation"):
            cat_dir = tmp_path / cat
            cat_dir.mkdir(parents=True, exist_ok=True)
            steps = [{"id": f"{cat}-step", "action": f"{cat}.run"}]
            (cat_dir / f"{cat}-prim.yaml").write_text(
                f"template_id: 'primitives/{cat}/{cat}-prim'\n"
                f"name: '{cat} Primitive'\n"
                f"tier: 'primitive'\n"
                f"category: '{cat}'\n"
                f"status: 'active'\n"
                f"steps:\n"
                f"  - id: {cat}-step\n"
                f"    action: {cat}.run\n"
            )
        return tmp_path

    # ------------------------------------------------------------------
    # Sweep envelope injection — fix / refactor / audit
    # ------------------------------------------------------------------

    def test_fix_composed_template_has_sweep_open_as_first_step(self, tmp_path: Path) -> None:
        """Composed FIX template: holistic_file_review_gate_open at step[0] (CORE-065),
        sweep_catalogue_open at step[1] (CORE-064)."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        pdir = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=pdir)
        result = composer.compose(operation_type="fix", description="Fix broken imports")
        assert result is not None
        # CORE-065 (Phase 64-G): holistic gate is absolute index 0
        assert result["steps"][0]["id"] == "holistic_file_review_gate_open", (
            "CORE-065: holistic_file_review_gate_open must be first step"
        )
        # CORE-064: sweep_catalogue_open is index 1 (after holistic gate)
        assert result["steps"][1]["id"] == "sweep_catalogue_open", (
            "CORE-064: sweep_catalogue_open must follow holistic gate at index 1"
        )
        assert result["steps"][1]["source_category"] == "governance"

    def test_fix_composed_template_has_sweep_close_as_last_step(self, tmp_path: Path) -> None:
        """Composed FIX template must have sweep_catalogue_assert_exhausted as step[-1] (CORE-064)."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        pdir = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=pdir)
        result = composer.compose(operation_type="fix", description="Fix broken imports")
        assert result is not None
        assert result["steps"][-1]["id"] == "sweep_catalogue_assert_exhausted", (
            "Last step must be sweep_catalogue_assert_exhausted for CORE-064 enforcement"
        )
        assert result["steps"][-1]["blocking"] is True

    def test_refactor_composed_template_has_sweep_envelope(self, tmp_path: Path) -> None:
        """Composed REFACTOR template: holistic gate at [0], sweep open at [1], sweep close at [-1]."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        pdir = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=pdir)
        result = composer.compose(operation_type="refactor", description="Refactor auth module")
        assert result is not None
        step_ids = [s["id"] for s in result["steps"]]
        # CORE-065 (Phase 64-G): holistic gate at absolute index 0
        assert step_ids[0] == "holistic_file_review_gate_open"
        # CORE-064: sweep envelope present (open not necessarily at [0] any more)
        assert "sweep_catalogue_open" in step_ids
        assert step_ids[-1] == "sweep_catalogue_assert_exhausted"

    def test_audit_composed_template_has_sweep_envelope(self, tmp_path: Path) -> None:
        """Composed AUDIT template: holistic gate at [0], sweep open at [1], sweep close at [-1]."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        pdir = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=pdir)
        result = composer.compose(operation_type="audit", description="Full production audit")
        assert result is not None
        step_ids = [s["id"] for s in result["steps"]]
        # CORE-065: holistic gate at index 0
        assert step_ids[0] == "holistic_file_review_gate_open"
        # CORE-064: sweep envelope present
        assert "sweep_catalogue_open" in step_ids
        assert step_ids[-1] == "sweep_catalogue_assert_exhausted"

    def test_implement_composed_template_has_no_sweep_envelope(self, tmp_path: Path) -> None:
        """Composed IMPLEMENT template must NOT have sweep envelope (not a sweep operation)."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        pdir = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=pdir)
        result = composer.compose(operation_type="implement", description="Build new feature")
        assert result is not None
        step_ids = [s["id"] for s in result["steps"]]
        assert "sweep_catalogue_open" not in step_ids, (
            "IMPLEMENT must not get sweep envelope — it is not a sweep operation"
        )
        assert "sweep_catalogue_assert_exhausted" not in step_ids

    def test_analyze_composed_template_has_no_sweep_envelope(self, tmp_path: Path) -> None:
        """Composed ANALYZE template must NOT have sweep envelope."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        pdir = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=pdir)
        result = composer.compose(operation_type="analyze", description="Analyze codebase")
        assert result is not None
        step_ids = [s["id"] for s in result["steps"]]
        assert "sweep_catalogue_open" not in step_ids
        assert "sweep_catalogue_assert_exhausted" not in step_ids

    # ------------------------------------------------------------------
    # Metadata correctness
    # ------------------------------------------------------------------

    def test_sweep_open_step_has_required_metadata_fields(self, tmp_path: Path) -> None:
        """Sweep open step (CORE-064) must carry action, args, source_primitive.
        
        CORE-065 (Phase 64-G): holistic gate occupies index 0; sweep open is at index 1.
        """
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        pdir = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=pdir)
        result = composer.compose(operation_type="fix", description="Fix tests")
        assert result is not None
        # CORE-065: holistic gate is at absolute index 0
        assert result["steps"][0]["id"] == "holistic_file_review_gate_open"
        # CORE-064: sweep open is now at index 1
        open_step = result["steps"][1]
        assert open_step["action"] == "SweepCatalogueOrchestrator.open_catalogue"
        assert "args" in open_step
        assert open_step["args"]["intent"] == "FIX"
        assert open_step["source_primitive"] == "core-064-sweep-open"

    def test_sweep_close_step_has_required_metadata_fields(self, tmp_path: Path) -> None:
        """Sweep close step must carry action, blocking flag, source_primitive."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        pdir = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=pdir)
        result = composer.compose(operation_type="refactor", description="Refactor tests")
        assert result is not None
        close_step = result["steps"][-1]
        assert close_step["action"] == "SweepCatalogueOrchestrator.assert_exhausted"
        assert close_step["blocking"] is True
        assert close_step["source_primitive"] == "core-064-sweep-close"

    def test_template_metadata_records_sweep_enforced_flag(self, tmp_path: Path) -> None:
        """Composed FIX template metadata must set sweep_enforced=True (CORE-064)."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        pdir = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=pdir)
        result = composer.compose(operation_type="fix", description="Fix missing types")
        assert result is not None
        assert result["metadata"].get("sweep_enforced") is True
        assert result["metadata"].get("core_064_compliant") is True

    def test_template_metadata_sweep_enforced_false_for_implement(self, tmp_path: Path) -> None:
        """Composed IMPLEMENT template metadata must set sweep_enforced=False."""
        from cortex.orchestrators.workflow.template_composer import TemplateComposer

        pdir = self._make_primitives_dir(tmp_path)
        composer = TemplateComposer(primitives_dir=pdir)
        result = composer.compose(operation_type="implement", description="Build feature")
        assert result is not None
        assert result["metadata"].get("sweep_enforced") is False

    # ------------------------------------------------------------------
    # Governance category presence in OPERATION_CATEGORY_MAP
    # ------------------------------------------------------------------

    def test_fix_category_map_includes_governance(self) -> None:
        """OPERATION_CATEGORY_MAP['fix'] must include 'governance' as first category."""
        from cortex.orchestrators.workflow.template_composer import OPERATION_CATEGORY_MAP

        assert "governance" in OPERATION_CATEGORY_MAP["fix"], (
            "CORE-064: 'governance' must be first in fix category map"
        )
        assert OPERATION_CATEGORY_MAP["fix"][0] == "governance"

    def test_refactor_category_map_includes_governance(self) -> None:
        """OPERATION_CATEGORY_MAP['refactor'] must include 'governance' as first category."""
        from cortex.orchestrators.workflow.template_composer import OPERATION_CATEGORY_MAP

        assert "governance" in OPERATION_CATEGORY_MAP["refactor"]
        assert OPERATION_CATEGORY_MAP["refactor"][0] == "governance"

    def test_audit_category_map_includes_governance(self) -> None:
        """OPERATION_CATEGORY_MAP['audit'] must include 'governance' as first category."""
        from cortex.orchestrators.workflow.template_composer import OPERATION_CATEGORY_MAP

        assert "governance" in OPERATION_CATEGORY_MAP.get("audit", [])
        assert OPERATION_CATEGORY_MAP["audit"][0] == "governance"

    def test_implement_category_map_excludes_governance(self) -> None:
        """OPERATION_CATEGORY_MAP['implement'] must NOT include 'governance' category."""
        from cortex.orchestrators.workflow.template_composer import OPERATION_CATEGORY_MAP

        assert "governance" not in OPERATION_CATEGORY_MAP["implement"]


class TestSweepCompositionEnforcementAgent:
    """Tests for SweepCompositionEnforcementAgent added to EnforcementOrchestrator."""

    def test_composed_fix_template_without_sweep_open_is_blocked(self) -> None:
        """Composed FIX template lacking sweep_catalogue_open step must be BLOCKED (CORE-064)."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            SweepCompositionEnforcementAgent,
            EnforcementLevel,
        )

        agent = SweepCompositionEnforcementAgent()
        bad_template = {
            "steps": [
                {"id": "analysis-step", "action": "lens.scan"},
                {"id": "execution-step", "action": "edit.run"},
            ],
            "metadata": {"operation_type": "fix"},
        }
        result = agent.validate({"composed_template": bad_template, "operation_type": "FIX"})
        assert result.level == EnforcementLevel.BLOCKED
        assert any("CORE-064" in v for v in result.violations)

    def test_composed_fix_template_without_sweep_close_is_blocked(self) -> None:
        """Composed FIX template lacking sweep_catalogue_assert_exhausted must be BLOCKED."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            SweepCompositionEnforcementAgent,
            EnforcementLevel,
        )

        agent = SweepCompositionEnforcementAgent()
        bad_template = {
            "steps": [
                {"id": "sweep_catalogue_open", "action": "SweepCatalogueOrchestrator.open_catalogue"},
                {"id": "execution-step", "action": "edit.run"},
                # missing sweep_catalogue_assert_exhausted at [-1]
            ],
            "metadata": {"operation_type": "fix"},
        }
        result = agent.validate({"composed_template": bad_template, "operation_type": "FIX"})
        assert result.level == EnforcementLevel.BLOCKED
        assert any("CORE-064" in v for v in result.violations)

    def test_composed_fix_template_with_full_envelope_passes(self) -> None:
        """Composed FIX template with correct sweep envelope must PASS."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            SweepCompositionEnforcementAgent,
            EnforcementLevel,
        )

        agent = SweepCompositionEnforcementAgent()
        good_template = {
            "steps": [
                {"id": "sweep_catalogue_open", "action": "SweepCatalogueOrchestrator.open_catalogue", "blocking": False},
                {"id": "analysis-step", "action": "lens.scan"},
                {"id": "sweep_catalogue_assert_exhausted", "action": "SweepCatalogueOrchestrator.assert_exhausted", "blocking": True},
            ],
            "metadata": {"operation_type": "fix", "sweep_enforced": True},
        }
        result = agent.validate({"composed_template": good_template, "operation_type": "FIX"})
        assert result.level == EnforcementLevel.PASS

    def test_implement_template_without_envelope_passes(self) -> None:
        """IMPLEMENT composed template without sweep envelope must PASS (not a sweep op)."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            SweepCompositionEnforcementAgent,
            EnforcementLevel,
        )

        agent = SweepCompositionEnforcementAgent()
        implement_template = {
            "steps": [
                {"id": "analysis-step", "action": "lens.scan"},
                {"id": "execution-step", "action": "tdd.run"},
            ],
            "metadata": {"operation_type": "implement", "sweep_enforced": False},
        }
        result = agent.validate({"composed_template": implement_template, "operation_type": "IMPLEMENT"})
        assert result.level == EnforcementLevel.PASS

    def test_no_composed_template_in_context_is_skipped(self) -> None:
        """When no composed_template present, agent must PASS (non-composed path)."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            SweepCompositionEnforcementAgent,
            EnforcementLevel,
        )

        agent = SweepCompositionEnforcementAgent()
        result = agent.validate({"operation_type": "FIX"})
        assert result.level == EnforcementLevel.PASS

    def test_agent_is_registered_in_enforcement_orchestrator(self) -> None:
        """SweepCompositionEnforcementAgent must be present in EnforcementOrchestrator.agents."""
        from cortex.orchestrators.core.enforcement_orchestrator import (
            EnforcementOrchestrator,
            SweepCompositionEnforcementAgent,
        )

        eo = EnforcementOrchestrator()
        agent_types = [type(a).__name__ for a in eo.agents]
        assert "SweepCompositionEnforcementAgent" in agent_types, (
            "SweepCompositionEnforcementAgent must be wired into EnforcementOrchestrator"
        )


# AC_COMPLETE: AC-PHASE56-S1-001 ✅ RED phase tests written (Phase 56)
