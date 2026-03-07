"""Preflight: cortex-registry Cohesion and Cross-Reference Integrity (phase-126-i, Check #38).

Validates the cohesion of cortex-registry/ YAML files:
  1. All YAML files in the registry parse without error
  2. No duplicate IDs across governance YAML files (id: field)
  3. Drift-lock YAML files all have required fields (id, check_number, status)
  4. All drift-lock YAML files reference test files that exist
    5. cortex-master.yaml remains ≤ 850 lines and parseableGap ref: GAP-126-09
Drift lock: cortex-registry/governance/drift-locks/check-38-registry-cohesion-lock.yaml
Tier: T0 (preflight) — YAML parse only, no server startup, < 15 s
CORE rules: CORE-008 (TDD), CORE-035 (single canonical implementation)
"""
from __future__ import annotations

import pathlib
from typing import Any, Dict, List, Tuple

import pytest
import yaml

CORTEX_ROOT = pathlib.Path(__file__).parents[2]
REGISTRY_ROOT = CORTEX_ROOT / "cortex-registry"
DRIFT_LOCKS_DIR = REGISTRY_ROOT / "governance" / "drift-locks"
MASTER_YAML = REGISTRY_ROOT / "cortex-master.yaml"

# Directories to scan for YAML parse errors
_SCAN_DIRS_FOR_PARSE = [
    REGISTRY_ROOT / "governance",
    REGISTRY_ROOT / "workflows" / "templates",
    REGISTRY_ROOT / "templates" / "response",
    REGISTRY_ROOT / "core",
]

# Max lines for cortex-master.yaml (Thin Index Contract)
_MASTER_YAML_MAX_LINES = 850


def _collect_registry_yamls() -> List[pathlib.Path]:
    """Return all .yaml files under scanned registry directories."""
    result: List[pathlib.Path] = []
    for scan_dir in _SCAN_DIRS_FOR_PARSE:
        if scan_dir.exists():
            result.extend(scan_dir.rglob("*.yaml"))
    return result


class TestRegistryCohesion:
    """cortex-registry YAML files must be parseable and internally coherent."""

    def test_all_registry_yamls_parse_without_error(self) -> None:
        """All YAML files in scanned registry directories must parse without error."""
        errors: List[str] = []
        for yaml_file in _collect_registry_yamls():
            try:
                data = yaml.safe_load(yaml_file.read_text(encoding="utf-8", errors="ignore"))
            except yaml.YAMLError as exc:
                rel = str(yaml_file.relative_to(CORTEX_ROOT))
                errors.append(f"  {rel}: {str(exc)[:120]}")
        assert not errors, (
            f"Registry YAML parse errors ({len(errors)} files):\n" + "\n".join(errors)
        )

    def test_no_duplicate_ids_in_drift_locks(self) -> None:
        """No two drift-lock YAML files may share the same id: value."""
        if not DRIFT_LOCKS_DIR.exists():
            pytest.skip("Drift locks directory not found")
        ids_seen: Dict[str, str] = {}  # id -> filename
        duplicates: List[str] = []
        for lock_file in sorted(DRIFT_LOCKS_DIR.glob("*.yaml")):
            try:
                data = yaml.safe_load(lock_file.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            lock_id = data.get("id")
            if not lock_id:
                continue
            if lock_id in ids_seen:
                duplicates.append(
                    f"  id='{lock_id}' in {lock_file.name} AND {ids_seen[lock_id]}"
                )
            else:
                ids_seen[lock_id] = lock_file.name
        assert not duplicates, (
            "Duplicate drift-lock IDs detected:\n" + "\n".join(duplicates)
        )

    def test_all_drift_lock_yamls_have_required_fields(self) -> None:
        """Every drift-lock YAML must contain: id, check_number, status."""
        if not DRIFT_LOCKS_DIR.exists():
            pytest.skip("Drift locks directory not found")
        missing_fields: List[str] = []
        required = {"id", "check_number", "status"}
        for lock_file in sorted(DRIFT_LOCKS_DIR.glob("*.yaml")):
            try:
                data = yaml.safe_load(lock_file.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                missing_fields.append(f"  {lock_file.name}: PARSE ERROR")
                continue
            absent = required - set(data.keys())
            if absent:
                missing_fields.append(
                    f"  {lock_file.name}: missing fields {sorted(absent)}"
                )
        assert not missing_fields, (
            "Drift-lock YAMLs missing required fields:\n" + "\n".join(missing_fields)
        )

    def test_drift_lock_primary_test_files_exist(self) -> None:
        """Each drift-lock YAML's primary_test_file must exist in the repo."""
        if not DRIFT_LOCKS_DIR.exists():
            pytest.skip("Drift locks directory not found")
        missing_tests: List[str] = []
        for lock_file in sorted(DRIFT_LOCKS_DIR.glob("*.yaml")):
            try:
                data = yaml.safe_load(lock_file.read_text(encoding="utf-8")) or {}
            except yaml.YAMLError:
                continue
            primary = data.get("primary_test_file")
            if primary:
                test_path = CORTEX_ROOT / primary
                if not test_path.exists():
                    missing_tests.append(
                        f"  {lock_file.name} → {primary} (NOT FOUND)"
                    )
        assert not missing_tests, (
            "Drift-lock primary_test_file references to non-existent files:\n"
            + "\n".join(missing_tests)
        )


class TestMasterYAMLCohesion:
    """cortex-master.yaml must remain within Thin Index Contract limits."""

    def test_master_yaml_is_parseable(self) -> None:
        """cortex-master.yaml must parse as valid YAML."""
        assert MASTER_YAML.exists(), "cortex-master.yaml not found."
        try:
            data = yaml.safe_load(MASTER_YAML.read_text(encoding="utf-8"))
            assert data is not None, "cortex-master.yaml parsed as None — file is empty."
        except yaml.YAMLError as exc:
            pytest.fail(f"cortex-master.yaml YAML parse error: {exc}")

    def test_master_yaml_does_not_exceed_line_limit(self) -> None:
        """cortex-master.yaml must be ≤ 850 lines (Thin Index Contract)."""
        if not MASTER_YAML.exists():
            pytest.skip("cortex-master.yaml not found")
        line_count = len(MASTER_YAML.read_text(encoding="utf-8").splitlines())
        assert line_count <= _MASTER_YAML_MAX_LINES, (
            f"cortex-master.yaml has {line_count} lines — exceeds Thin Index Contract "
            f"limit of {_MASTER_YAML_MAX_LINES}. Move detail to phase-specific YAML files."
        )


class TestRegistryCohesionDriftLock:
    """Permanent CI drift lock — Check #38 invariants."""

    def test_drift_lock_yaml_exists(self) -> None:
        lock = DRIFT_LOCKS_DIR / "check-38-registry-cohesion-lock.yaml"
        assert lock.exists(), (
            "Drift lock YAML check-38-registry-cohesion-lock.yaml not found."
        )

    def test_drift_lock_yaml_is_valid(self) -> None:
        lock = DRIFT_LOCKS_DIR / "check-38-registry-cohesion-lock.yaml"
        if not lock.exists():
            pytest.skip("Lock file missing")
        data = yaml.safe_load(lock.read_text(encoding="utf-8"))
        assert data is not None
        assert data.get("check_number") == 38
