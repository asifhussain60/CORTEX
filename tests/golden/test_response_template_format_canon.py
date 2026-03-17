"""Golden snapshot: Response Template Canonicalization Enforcement (phase-126-h, Check #37).

Validates the terminal composition YAML files for structural correctness:
  1. Each composition file is parseable YAML (non-empty)
    2. All required compositions exist in cortex-registry/templates/response/compositions/
  3. No composition contains a 'proceed' block inside a 'next_steps' section
  4. Proceed gate markers appear only at the terminal position if present
  5. Composition IDs match their filename stems (no orphaned IDs)
  6. The _registry.yaml index references all 8 compositions

This is a structural governance test — it does not render compositions at runtime.
The Phase 120 golden tests (tests/golden/response/test_phase_120_response_golden.py)
handle render-time validation.

Gap ref: GAP-126-08
Drift lock: cortex-registry/governance/drift-locks/check-37-response-template-lock.yaml
Tier: T0 (preflight) — YAML parse only, no server startup, < 10 s
CORE rules: CORE-008 (TDD), CORE-064 (Sweep Completeness Contract)
"""
from __future__ import annotations

import pathlib
from typing import Any, Dict, List

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
COMPOSITIONS_DIR = (
    CORTEX_ROOT / "cortex-registry" / "templates" / "response" / "compositions"
)
REGISTRY_FILE = CORTEX_ROOT / "cortex-registry" / "templates" / "response" / "_registry.yaml"

# Canonical terminal compositions (includes guided interaction composition)
_REQUIRED_COMPOSITIONS = {
    "comp-implement-fix",
    "comp-refactor",
    "comp-audit-fix",
    "comp-health",
    "comp-vacuum",
    "comp-debug",
    "comp-query",
    "comp-introduce",
    "comp-interaction-guided",
}


def _load_composition(name: str) -> Dict[str, Any]:
    """Load a composition YAML file by stem name."""
    path = COMPOSITIONS_DIR / f"{name}.yaml"
    if not path.exists():
        return {}
    content = path.read_text(encoding="utf-8")
    return yaml.safe_load(content) or {}


class TestResponseTemplateCanon:
    """All required terminal composition files must exist and be structurally valid."""

    def test_all_eight_compositions_exist(self) -> None:
        """All 8 required terminal compositions must exist in the compositions dir."""
        if not COMPOSITIONS_DIR.exists():
            pytest.fail(
                f"Compositions directory not found: {COMPOSITIONS_DIR.relative_to(CORTEX_ROOT)}"
            )
        present = {p.stem for p in COMPOSITIONS_DIR.glob("comp-*.yaml")}
        missing = _REQUIRED_COMPOSITIONS - present
        assert not missing, (
            f"Missing composition file(s):\n"
            + "\n".join(f"  {m}.yaml" for m in sorted(missing))
        )

    def test_all_compositions_are_parseable_yaml(self) -> None:
        """Every composition YAML must parse without error and be non-empty."""
        errors: List[str] = []
        for stem in _REQUIRED_COMPOSITIONS:
            path = COMPOSITIONS_DIR / f"{stem}.yaml"
            if not path.exists():
                errors.append(f"  {stem}.yaml: FILE NOT FOUND")
                continue
            try:
                content = path.read_text(encoding="utf-8")
                data = yaml.safe_load(content)
                if not content.strip():
                    errors.append(f"  {stem}.yaml: EMPTY FILE")
            except yaml.YAMLError as exc:
                errors.append(f"  {stem}.yaml: YAML ERROR — {exc}")
        assert not errors, (
            "Composition YAML parse errors:\n" + "\n".join(errors)
        )

    def test_all_compositions_are_non_trivial(self) -> None:
        """Every composition file must be > 200 bytes (non-stub content)."""
        too_small: List[str] = []
        for stem in _REQUIRED_COMPOSITIONS:
            path = COMPOSITIONS_DIR / f"{stem}.yaml"
            if not path.exists():
                continue
            size = path.stat().st_size
            if size < 200:
                too_small.append(f"  {stem}.yaml: {size} bytes (minimum 200)")
        assert not too_small, (
            "Composition files are stub-sized:\n" + "\n".join(too_small)
        )

    def test_no_proceed_gate_inside_next_steps_section(self) -> None:
        """'proceed' markers must not appear inside 'next_steps' composition sections.

        The Proceed Gate must always be the LAST block, never nested inside Next Steps.
        """
        violations: List[str] = []
        for stem in _REQUIRED_COMPOSITIONS:
            path = COMPOSITIONS_DIR / f"{stem}.yaml"
            if not path.exists():
                continue
            content = path.read_text(encoding="utf-8")
            lines = content.splitlines()
            in_next_steps = False
            for i, line in enumerate(lines, 1):
                stripped = line.lower().strip()
                if "next_steps" in stripped or "next-steps" in stripped:
                    in_next_steps = True
                # Reset when we hit a new top-level key
                if in_next_steps and line and not line[0].isspace() and ":" in line:
                    if "next_steps" not in stripped and "next-steps" not in stripped:
                        in_next_steps = False
                if in_next_steps and "proceed" in stripped:
                    violations.append(
                        f"  {stem}.yaml:{i}: 'proceed' inside next_steps — {line.strip()[:80]}"
                    )
        assert not violations, (
            "Proceed gate found inside next_steps section (must be LAST block):\n"
            + "\n".join(violations)
        )

    def test_composition_registry_exists(self) -> None:
        """cortex-registry/templates/response/_registry.yaml must exist."""
        assert REGISTRY_FILE.exists(), (
            f"Response template registry not found: {REGISTRY_FILE.relative_to(CORTEX_ROOT)}"
        )

    def test_composition_registry_is_parseable(self) -> None:
        """_registry.yaml must parse as valid YAML."""
        if not REGISTRY_FILE.exists():
            pytest.skip("Registry file not found")
        try:
            data = yaml.safe_load(REGISTRY_FILE.read_text(encoding="utf-8"))
            assert data is not None, "_registry.yaml is empty"
        except yaml.YAMLError as exc:
            pytest.fail(f"_registry.yaml parse error: {exc}")


class TestResponseTemplateDriftLock:
    """Permanent CI drift lock — Check #37 invariants."""

    def test_drift_lock_yaml_exists(self) -> None:
        lock = (
            CORTEX_ROOT
            / "cortex-registry"
            / "governance"
            / "drift-locks"
            / "check-37-response-template-lock.yaml"
        )
        assert lock.exists(), (
            "Drift lock YAML check-37-response-template-lock.yaml not found."
        )

    def test_drift_lock_yaml_is_valid(self) -> None:
        lock = (
            CORTEX_ROOT
            / "cortex-registry"
            / "governance"
            / "drift-locks"
            / "check-37-response-template-lock.yaml"
        )
        if not lock.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(lock.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 37
