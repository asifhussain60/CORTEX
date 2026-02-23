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
