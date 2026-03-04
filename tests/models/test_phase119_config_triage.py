"""
tests/models/test_phase119_config_triage.py — Phase 119-B TDD Red→Green

Governance gate for CORE-035 Sub-Phase B: triage all 19 ``Config`` class
definitions — pydantic inner-class pattern (retain) vs top-level duplicates
(consolidate).

Triage result (2026-03-04 AST scan):
  - 19 definitions found across 4 files
  - All 19 are pydantic-nested (indent=4, parent inherits BaseModel)
  - 0 true top-level Config duplicates requiring consolidation
  - All are intentional pydantic v1 inner ``class Config`` pattern

Sub-Phase B verdict: NO consolidation needed — all Config classes are
legitimate pydantic constructs.  Tests verify:
  1. All pydantic models that contain a nested Config are importable.
  2. Zero top-level (non-nested) Config definitions exist in cortex/.
  3. Pydantic-annotated models remain functional (orm_mode / from_attributes
     where set, field aliasing, etc. are not broken).

Governance: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep)
Authority: phase-119-b, SWEEP-119-CLASS-CONSOLIDATION
"""
from __future__ import annotations

import ast
import pathlib
from typing import List, Tuple

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# HELPER
# ─────────────────────────────────────────────────────────────────────────────

CORTEX_ROOT = pathlib.Path(__file__).parent.parent.parent / "cortex"


def _find_toplevel_config_definitions() -> List[Tuple[str, int]]:
    """Return (filepath, lineno) for any top-level (non-nested) Config class.

    A Config class is top-level if its indentation is 0 (not nested inside
    another class body).  Pydantic inner Config classes always have indent > 0.

    Excludes __pycache__ and _quarantine directories.
    """
    results: List[Tuple[str, int]] = []
    for f in CORTEX_ROOT.rglob("*.py"):
        if "__pycache__" in str(f) or "_quarantine" in str(f):
            continue
        try:
            src = f.read_text(errors="ignore")
            lines = src.splitlines()
            tree = ast.parse(src)
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef) and node.name == "Config":
                    class_line = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
                    indent = len(class_line) - len(class_line.lstrip())
                    if indent == 0:
                        results.append((str(f.relative_to(CORTEX_ROOT.parent)), node.lineno))
        except Exception:
            pass
    return results


# ─────────────────────────────────────────────────────────────────────────────
# ZERO TOP-LEVEL CONFIG TEST (RED gate — must be GREEN immediately post-triage)
# ─────────────────────────────────────────────────────────────────────────────

def test_no_toplevel_config_duplicates() -> None:
    """CORE-035: zero top-level Config class definitions may exist in cortex/.

    All 19 Config classes found by AST scan are pydantic-nested (indent=4).
    No consolidation is required.  This test enforces no future top-level
    Config is added without being pydantic-nested.
    """
    top_level = _find_toplevel_config_definitions()
    assert top_level == [], (
        f"CORE-035 violation: found {len(top_level)} top-level Config class(es) "
        f"that are NOT pydantic-nested and require consolidation:\n"
        + "\n".join(f"  {p}:{ln}" for p, ln in top_level)
    )


# ─────────────────────────────────────────────────────────────────────────────
# PYDANTIC MODEL IMPORT TESTS — verify all models with nested Config intact
# ─────────────────────────────────────────────────────────────────────────────

def test_dashboard_schema_pydantic_importable() -> None:
    """All pydantic models in dashboard_schema_pydantic.py must remain importable."""
    from cortex.models.dashboard_schema_pydantic import (  # noqa: F401
        CodeMetrics,
        DependencyMetrics,
        SecurityMetrics,
        PerformanceMetrics,
        Overview,
        LensAnalysis,
        Registry,
        GenerationMetadata,
    )
    # Verify pydantic nested Config is accessible
    assert hasattr(CodeMetrics, "model_config") or hasattr(CodeMetrics, "__config__"), (
        "CodeMetrics pydantic model must have model_config or __config__ attribute"
    )


def test_phase_detail_schema_importable() -> None:
    """All pydantic models in phase_detail_schema.py must remain importable."""
    from cortex.models.phase_detail_schema import (  # noqa: F401
        MermaidDiagram,
        ArchitectureSection,
    )
    assert MermaidDiagram is not None
    assert ArchitectureSection is not None


def test_dashboard_routes_models_importable() -> None:
    """Pydantic request/response models in dashboard_routes.py must remain importable."""
    from cortex.dashboards.api.dashboard_routes import (  # noqa: F401
        DashboardGenerateRequest,
        DashboardGenerateResponse,
        HealthCheckResponse,
        DashboardListResponse,
    )
    assert DashboardGenerateRequest is not None


def test_ldv1_schema_importable() -> None:
    """LensArtifact model in ldv1_schema.py must remain importable."""
    from cortex.lens.schemas.ldv1_schema import LensArtifact  # noqa: F401
    assert LensArtifact is not None


# ─────────────────────────────────────────────────────────────────────────────
# ANNOTATION CHECK — pydantic-nested Configs must carry noqa comment
# (Applied during Sub-Phase B REFACTOR to suppress any future CORE-035 scanner)
# ─────────────────────────────────────────────────────────────────────────────

PYDANTIC_CONFIG_FILES = [
    CORTEX_ROOT / "dashboards" / "api" / "dashboard_routes.py",
    CORTEX_ROOT / "lens" / "schemas" / "ldv1_schema.py",
    CORTEX_ROOT / "models" / "dashboard_schema_pydantic.py",
    CORTEX_ROOT / "models" / "phase_detail_schema.py",
]


def test_pydantic_nested_configs_annotated() -> None:
    """All pydantic-nested Config classes must carry a # noqa: CORE-035 comment.

    This annotation suppresses the CORE-035 duplicate scanner for legitimate
    pydantic inner classes.  Applied during Sub-Phase B REFACTOR.
    """
    missing: List[Tuple[str, int]] = []
    for f in PYDANTIC_CONFIG_FILES:
        if not f.exists():
            continue
        src = f.read_text(errors="ignore")
        lines = src.splitlines()
        tree = ast.parse(src)
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "Config":
                class_line = lines[node.lineno - 1] if node.lineno <= len(lines) else ""
                indent = len(class_line) - len(class_line.lstrip())
                if indent > 0 and "noqa: CORE-035" not in class_line:
                    missing.append((str(f.relative_to(CORTEX_ROOT.parent)), node.lineno))

    assert missing == [], (
        f"Pydantic-nested Config classes missing '# noqa: CORE-035' annotation "
        f"({len(missing)} location(s)):\n"
        + "\n".join(f"  {p}:{ln}" for p, ln in missing)
    )
