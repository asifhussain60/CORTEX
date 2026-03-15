"""phase-m1-c gate — backward-compat shims and complexity classifiers removed.

RED phase: tests FAIL while files still exist.
GREEN phase: tests PASS after deletions.

GAP-M1-07: central_brain_orchestrator.py, brain_health_orchestrator.py (shims)
GAP-M1-08: complexity_classifier.py, complexity_assessment.py,
           complexity_triage_engine.py (3 competing classifiers → CORE-035)
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
import yaml

# ---------------------------------------------------------------------------
# Targets
# ---------------------------------------------------------------------------

SHIM_MODULES = [
    "cortex.orchestrators.core.central_brain_orchestrator",
    "cortex.orchestrators.core.brain_health_orchestrator",
]

CLASSIFIER_MODULES = [
    "cortex.orchestrators.core.complexity_classifier",
    "cortex.orchestrators.core.complexity_assessment",
    "cortex.orchestrators.core.complexity_triage_engine",
]

DEAD_MODULES = SHIM_MODULES + CLASSIFIER_MODULES

# Build patterns dynamically to avoid self-match in the filesystem scan.
_DEAD_SEGMENTS = [m.split(".")[-1] for m in DEAD_MODULES]
_PACKAGE_ROOT = "cortex.orchestrators.core"
DEAD_IMPORT_PATTERNS: list[str] = []
for _seg in _DEAD_SEGMENTS:
    _target = f"{_PACKAGE_ROOT}.{_seg}"
    DEAD_IMPORT_PATTERNS.append(f"from {_target}")
    DEAD_IMPORT_PATTERNS.append(f"import {_target}")


# ---------------------------------------------------------------------------
# Test 1 — shim modules not importable
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("module_name", SHIM_MODULES)
def test_shim_modules_not_importable(module_name: str) -> None:
    """Shim files must be deleted — importing them must raise an error."""
    sys.modules.pop(module_name, None)
    with pytest.raises((ModuleNotFoundError, ImportError)):
        importlib.import_module(module_name)


# ---------------------------------------------------------------------------
# Test 2 — classifier modules not importable
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("module_name", CLASSIFIER_MODULES)
def test_classifier_modules_not_importable(module_name: str) -> None:
    """All 3 complexity classifier files must be deleted (CORE-035)."""
    sys.modules.pop(module_name, None)
    with pytest.raises((ModuleNotFoundError, ImportError)):
        importlib.import_module(module_name)


# ---------------------------------------------------------------------------
# Test 3 — no dead import references anywhere in cortex/ or tests/
# ---------------------------------------------------------------------------


def test_no_dead_shim_or_classifier_import_references() -> None:
    """No file in cortex/ or tests/ may import the deleted modules."""
    project_root = Path(__file__).resolve().parents[2]
    search_roots = [project_root / "cortex", project_root / "tests"]
    offenders: list[str] = []
    for root in search_roots:
        for file_path in root.rglob("*.py"):
            # Skip this file itself — it contains the patterns as string literals
            if file_path.name == "test_shim_complexity_removal.py":
                continue
            text = file_path.read_text(encoding="utf-8")
            for pattern in DEAD_IMPORT_PATTERNS:
                if pattern in text:
                    offenders.append(
                        f"{file_path.relative_to(project_root)}::{pattern}"
                    )
    assert offenders == [], (
        "Found dead shim/classifier import references:\n" + "\n".join(offenders)
    )


# ---------------------------------------------------------------------------
# Test 4 — complexity heuristic entry in LLM capabilities manifest
# ---------------------------------------------------------------------------


def test_complexity_heuristic_in_llm_capabilities_manifest() -> None:
    """cortex-registry/core/llm-capabilities.yaml must have a complexity_heuristic."""
    project_root = Path(__file__).resolve().parents[2]
    manifest = project_root / "cortex-registry" / "core" / "llm-capabilities.yaml"
    assert manifest.exists(), "llm-capabilities.yaml not found"
    data = yaml.safe_load(manifest.read_text(encoding="utf-8"))
    assert "complexity_heuristic" in data, (
        "llm-capabilities.yaml must contain a 'complexity_heuristic' section "
        "(CORTEX-V2 phase-m1-c: complexity classification delegated to LLM)"
    )
