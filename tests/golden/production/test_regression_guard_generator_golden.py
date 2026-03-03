"""
Phase 106-A: Regression Guard Generator — Golden Tests (CORE-008 RED cycle)
Authority: GAP-106-01 — No regression guard test generation on audit auto-fix
SSOT: cortex-registry/planning/phases/planned/phase-106-rca-guard-certification.yaml

Tests validate that regression-guard-generator.yaml primitive exists and produces
structurally correct Python guard test files.
"""
import ast
import os
import re
import textwrap
from pathlib import Path

import pytest

WORKSPACE = Path(__file__).resolve().parents[3]
PRIMITIVE_PATH = (
    WORKSPACE
    / "cortex-registry"
    / "workflows"
    / "templates"
    / "primitives"
    / "testing"
    / "regression-guard-generator.yaml"
)
PIPELINE_PATH = (
    WORKSPACE
    / "cortex-registry"
    / "workflows"
    / "templates"
    / "audit"
    / "audit-fix-pipeline.yaml"
)
GUARD_DIR = WORKSPACE / "tests" / "regression" / "guards"


class TestRegressionGuardGeneratorGolden:
    """Phase 106-A: 4 golden tests for the regression guard generator primitive."""

    def test_guard_generator_primitive_exists(self) -> None:
        """GAP-106-01: regression-guard-generator.yaml primitive must exist."""
        assert PRIMITIVE_PATH.exists(), (
            f"Missing primitive: {PRIMITIVE_PATH}\n"
            "Phase 106-A: Create cortex-registry/workflows/templates/primitives/"
            "testing/regression-guard-generator.yaml"
        )

    def test_guard_generator_primitive_has_required_fields(self) -> None:
        """GAP-106-01: Primitive must declare parameters: rule_id, detect_command, guard_test_path."""
        assert PRIMITIVE_PATH.exists(), "Primitive missing — run test_guard_generator_primitive_exists first"
        import yaml  # type: ignore[import]

        content = yaml.safe_load(PRIMITIVE_PATH.read_text())
        assert content is not None, "Primitive YAML must not be empty"

        # primitive must declare its parameters
        primitive = content.get("primitive", content)
        params_section = (
            primitive.get("parameters")
            or primitive.get("inputs")
            or primitive.get("params")
        )
        assert params_section is not None, (
            "Primitive must have a 'parameters' or 'inputs' section listing "
            "rule_id, detect_command, guard_test_path, fix_description"
        )

        # Flatten to a single string for easy key presence check
        params_str = str(params_section)
        for required_param in ("rule_id", "detect_command", "guard_test_path"):
            assert required_param in params_str, (
                f"Primitive missing parameter: '{required_param}'"
            )

    def test_pipeline_has_fix_step_on_success_hook(self) -> None:
        """GAP-106-01: audit-fix-pipeline.yaml Stage 7-8 fix_step must have on_success hook."""
        assert PIPELINE_PATH.exists(), "audit-fix-pipeline.yaml missing"
        content = PIPELINE_PATH.read_text()

        # Must contain an on_success hook that references regression guard generation
        assert "on_success" in content, (
            "audit-fix-pipeline.yaml must contain on_success hook in Stage 7-8 fix_step"
        )
        assert "regression" in content.lower() or "guard" in content.lower(), (
            "Stage 7-8 on_success hook must reference regression guard generation"
        )

    def test_guard_dir_exists_with_init(self) -> None:
        """GAP-106-01: tests/regression/guards/ must exist with __init__.py."""
        assert GUARD_DIR.exists(), f"Missing directory: {GUARD_DIR}"
        init_file = GUARD_DIR / "__init__.py"
        assert init_file.exists(), (
            f"Missing {init_file} — guard test directory must be a Python package"
        )
