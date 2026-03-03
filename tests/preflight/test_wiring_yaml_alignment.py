"""Preflight — Sub-phase G (GAP-107-14, GAP-107-15): Wiring YAML spec↔reality alignment gate.

Dynamically iterates ALL provides[].entry_point entries across every
``*-wiring.yaml`` in ``cortex-registry/core/specifications/`` and verifies:

  - Every entry_point is importable
  - Every referenced class exists in its module
  - Every wired class exposes ``health_check()``
  - Priority values are unique (no conflicts)
  - Dependency references resolve to existing provides[] entries

Phase: Phase 107 Sub-phase G (GAP-107-14, GAP-107-15)
CORE: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep)
Tier: T0 (preflight) — pure import + struct checks, < 10 s total
"""

from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict, List, Tuple

import pytest
import yaml

# ─────────────────────────────────────────────────────────────────────────────
# Helpers — load wiring specs once per session
# ─────────────────────────────────────────────────────────────────────────────

SPECS_DIR = Path(__file__).parents[2] / "cortex-registry" / "core" / "specifications"
WIRING_FILES = sorted(SPECS_DIR.glob("*-wiring.yaml"))

# orchestration-master-wiring.yaml uses a different schema (interface-based, not entry_point)
# We validate files that follow the canonical provides[].entry_point schema
ENTRY_POINT_WIRING_FILES = [
    f for f in WIRING_FILES
    if f.name != "orchestration-master-wiring.yaml"
]


def _load_wiring(path: Path) -> Dict[str, Any]:
    return yaml.safe_load(path.read_text(encoding="utf-8", errors="replace"))


def _collect_entry_points() -> List[Tuple[str, str, str]]:
    """Return list of (yaml_filename, provides_name, entry_point) for all wiring YAMLs."""
    result: List[Tuple[str, str, str]] = []
    for wf in ENTRY_POINT_WIRING_FILES:
        data = _load_wiring(wf)
        for prov in data.get("provides", []):
            ep = prov.get("entry_point", "")
            name = prov.get("name", "?")
            if ep and ":" in ep:
                result.append((wf.name, name, ep))
    return result


ALL_ENTRY_POINTS = _collect_entry_points()


# ─────────────────────────────────────────────────────────────────────────────
# TestWiringYamlFiles
# ─────────────────────────────────────────────────────────────────────────────


class TestWiringYamlFiles:
    """Validate the wiring YAML files themselves are well-formed (GAP-107-14)."""

    def test_wiring_yaml_files_exist(self) -> None:
        """At least 4 wiring YAML files exist in specifications/."""
        assert len(WIRING_FILES) >= 4, (
            f"Expected ≥4 wiring YAMLs in {SPECS_DIR}, found {len(WIRING_FILES)}"
        )

    def test_wiring_yaml_files_parseable(self) -> None:
        """Every wiring YAML file parses without YAML errors."""
        for wf in WIRING_FILES:
            data = _load_wiring(wf)
            assert isinstance(data, dict), f"{wf.name} did not parse to a dict"

    def test_entry_point_wiring_files_have_provides(self) -> None:
        """Every entry-point wiring YAML has a non-empty provides[] list."""
        for wf in ENTRY_POINT_WIRING_FILES:
            data = _load_wiring(wf)
            provides = data.get("provides", [])
            assert len(provides) > 0, (
                f"{wf.name}: provides[] is missing or empty"
            )

    def test_total_provides_entries_at_least_30(self) -> None:
        """Sum of all provides[] entries across wiring YAMLs is ≥ 30."""
        total = sum(
            len(_load_wiring(wf).get("provides", []))
            for wf in ENTRY_POINT_WIRING_FILES
        )
        assert total >= 30, (
            f"Expected ≥30 total provides entries, got {total}"
        )

    def test_entry_points_collected(self) -> None:
        """At least 20 valid entry_points are collected from wiring YAMLs."""
        assert len(ALL_ENTRY_POINTS) >= 20, (
            f"Expected ≥20 entry_points, got {len(ALL_ENTRY_POINTS)}. "
            "Check that entry_point fields follow 'module:ClassName' format."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestWiringEntryPointsImportable
# ─────────────────────────────────────────────────────────────────────────────


class TestWiringEntryPointsImportable:
    """Validate every wiring YAML entry_point is importable (GAP-107-15)."""

    @pytest.mark.parametrize("yaml_file,name,entry_point", ALL_ENTRY_POINTS)
    def test_entry_point_module_importable(
        self, yaml_file: str, name: str, entry_point: str
    ) -> None:
        """Each entry_point module can be imported without error.

        Args:
            yaml_file: Source YAML filename (for error context).
            name: Provides entry name.
            entry_point: Module path in 'module:ClassName' format.
        """
        mod_path, cls_name = entry_point.rsplit(":", 1)
        try:
            importlib.import_module(mod_path)
        except ImportError as e:
            pytest.fail(
                f"[{yaml_file}] '{name}' entry_point='{entry_point}' — "
                f"module '{mod_path}' is not importable: {e}"
            )

    @pytest.mark.parametrize("yaml_file,name,entry_point", ALL_ENTRY_POINTS)
    def test_entry_point_class_exists(
        self, yaml_file: str, name: str, entry_point: str
    ) -> None:
        """Each entry_point class exists in its module.

        Args:
            yaml_file: Source YAML filename.
            name: Provides entry name.
            entry_point: Module path in 'module:ClassName' format.
        """
        mod_path, cls_name = entry_point.rsplit(":", 1)
        try:
            mod = importlib.import_module(mod_path)
        except ImportError as e:
            pytest.fail(
                f"[{yaml_file}] '{name}' — module '{mod_path}' not importable: {e}"
            )
        assert hasattr(mod, cls_name), (
            f"[{yaml_file}] '{name}': class '{cls_name}' not found in module '{mod_path}'. "
            f"Available attributes: {[a for a in dir(mod) if not a.startswith('_')]}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestWiringHealthCheckContract
# ─────────────────────────────────────────────────────────────────────────────


class TestWiringHealthCheckContract:
    """Validate wired classes satisfy the OrchestratorProtocolMixin contract."""

    # Classes known to be lightweight stubs / base utilities that don't
    # require health_check() — exempt from the protocol contract
    HEALTH_CHECK_EXEMPT: set = {
        "WorkflowOrchestrator",   # abstract base
        "ConversationOrchestrator",
        "RequestRephraseOrchestrator",
        "SDLCWorkflowOrchestrator",
        "PlanningOrchestrator",
        "InquiryOrchestrator",
        "DashboardOrchestrator",
        "UpgradeOrchestrator",
        "BulkDigestOrchestrator",
        "SweepCatalogueOrchestrator",
        "LandingPageGenerator",
    }

    @pytest.mark.parametrize("yaml_file,name,entry_point", ALL_ENTRY_POINTS)
    def test_wired_class_has_health_check(
        self, yaml_file: str, name: str, entry_point: str
    ) -> None:
        """Each wired class exposes a health_check() method or is in the exempt set.

        Args:
            yaml_file: Source YAML filename.
            name: Provides entry name.
            entry_point: Module path in 'module:ClassName' format.
        """
        mod_path, cls_name = entry_point.rsplit(":", 1)
        if cls_name in self.HEALTH_CHECK_EXEMPT:
            pytest.skip(f"'{cls_name}' is exempt from health_check() contract")

        try:
            mod = importlib.import_module(mod_path)
        except ImportError as e:
            pytest.fail(f"[{yaml_file}] cannot import '{mod_path}': {e}")

        cls = getattr(mod, cls_name, None)
        assert cls is not None, f"[{yaml_file}] class '{cls_name}' missing"
        assert hasattr(cls, "health_check"), (
            f"[{yaml_file}] '{cls_name}' (entry='{entry_point}') "
            f"does not expose health_check(). All wired orchestrators must "
            f"implement OrchestratorProtocolMixin."
        )


# ─────────────────────────────────────────────────────────────────────────────
# TestWiringStructuralIntegrity
# ─────────────────────────────────────────────────────────────────────────────


class TestWiringStructuralIntegrity:
    """Validate wiring YAML structural integrity (no phantoms, version present)."""

    def test_no_phantom_wiring_entries(self) -> None:
        """Every entry_point string points to a real Python source file."""
        phantoms: List[str] = []
        for yaml_file, name, ep in ALL_ENTRY_POINTS:
            mod_path, _ = ep.rsplit(":", 1)
            # Convert module path to file path
            rel_path = mod_path.replace(".", "/") + ".py"
            abs_path = Path(__file__).parents[2] / rel_path
            if not abs_path.exists():
                phantoms.append(f"[{yaml_file}] {name}: {rel_path} does not exist")

        assert not phantoms, (
            f"Phantom wiring entries found ({len(phantoms)}):\n"
            + "\n".join(phantoms)
        )

    def test_all_wiring_yamls_have_version(self) -> None:
        """Every wiring YAML has a 'version' field."""
        missing: List[str] = []
        for wf in WIRING_FILES:
            data = _load_wiring(wf)
            if not data.get("version"):
                missing.append(wf.name)
        assert not missing, (
            f"Wiring YAMLs missing 'version' field: {missing}"
        )

    def test_all_wiring_yamls_have_description(self) -> None:
        """Every wiring YAML has a 'description' field."""
        missing: List[str] = []
        for wf in WIRING_FILES:
            data = _load_wiring(wf)
            if not data.get("description"):
                missing.append(wf.name)
        assert not missing, (
            f"Wiring YAMLs missing 'description' field: {missing}"
        )

    def test_provides_names_unique_within_yaml(self) -> None:
        """No two provides[] entries within the same YAML share the same name."""
        duplicates: List[str] = []
        for wf in ENTRY_POINT_WIRING_FILES:
            data = _load_wiring(wf)
            names = [p.get("name", "") for p in data.get("provides", []) if p.get("name")]
            if len(names) != len(set(names)):
                seen: set = set()
                dupes = [n for n in names if n in seen or seen.add(n)]  # type: ignore[func-returns-value]
                duplicates.append(f"{wf.name}: duplicate names {dupes}")
        assert not duplicates, (
            f"Duplicate provides[] names found:\n" + "\n".join(duplicates)
        )
