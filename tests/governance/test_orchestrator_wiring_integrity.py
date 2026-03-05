"""Phase 128-d: Orchestrator Wiring Integrity Tests.

Authority: GAP-128-D-01 (wiring YAML entry_points resolving to importable symbols)
Governance: CORE-008 (TDD mandatory), CORE-064 (Sweep Completeness)
SSOT: cortex-registry/planning/phases/planned/phase-128-conflict-drift-eradication.yaml

Verifies that:
  1. All wiring YAML entry_points resolve to actual Python modules + classes
  2. All wired orchestrators implement IOrchestrator or OrchestratorProtocolMixin
  3. No wiring entry_points are duplicated across wiring files
  4. All wiring YAML files are parseable and have required fields
  5. Named orchestrators in wiring have AC_START markers in their source files
"""
from __future__ import annotations

import importlib
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

PROJECT_ROOT = Path(__file__).parent.parent.parent
SPECS_DIR = PROJECT_ROOT / "cortex-registry" / "core" / "specifications"

WIRING_FILES = [
    "core-orchestrator-wiring.yaml",
    "domain-orchestrator-wiring.yaml",
    "support-orchestrator-wiring.yaml",
]

ORCHESTRATORS_DIR = PROJECT_ROOT / "cortex" / "orchestrators"


def load_wiring_entries(section: str = "provides") -> list[dict[str, Any]]:
    """Load all wiring entries from all wiring YAML files."""
    entries = []
    for fname in WIRING_FILES:
        fpath = SPECS_DIR / fname
        if not fpath.exists():
            continue
        content = yaml.safe_load(fpath.read_text(encoding="utf-8"))
        for entry in content.get(section, []):
            entry["_source_file"] = fname
            entries.append(entry)
    return entries


def parse_entry_point(entry_point: str) -> tuple[str, str] | None:
    """Parse 'module.path:ClassName' into (module_path, class_name).
    
    Returns None if format is invalid.
    """
    if not entry_point or ":" not in entry_point:
        return None
    parts = entry_point.rsplit(":", 1)
    if len(parts) != 2:
        return None
    return parts[0], parts[1]


class TestWiringYamlStructure:
    """Verify wiring YAML files have correct structure."""

    def test_all_wiring_files_exist(self) -> None:
        """All wiring YAML files must exist in specs directory."""
        missing = []
        for fname in WIRING_FILES:
            fpath = SPECS_DIR / fname
            if not fpath.exists():
                missing.append(str(fpath.relative_to(PROJECT_ROOT)))

        assert not missing, (
            f"Missing wiring YAML files:\n"
            + "\n".join(f"  - {m}" for m in missing)
        )

    def test_all_wiring_files_parseable(self) -> None:
        """All wiring YAML files must be parseable."""
        errors = []
        for fname in WIRING_FILES:
            fpath = SPECS_DIR / fname
            if not fpath.exists():
                continue
            try:
                yaml.safe_load(fpath.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                errors.append(f"{fname}: {e}")

        assert not errors, (
            f"Wiring YAML parse errors:\n"
            + "\n".join(f"  - {e}" for e in errors)
        )

    def test_all_wiring_entries_have_entry_point(self) -> None:
        """Every 'provides' entry must have an entry_point field."""
        entries = load_wiring_entries("provides")
        missing_ep = [
            f"{e.get('name')} in {e['_source_file']}"
            for e in entries
            if not e.get("entry_point")
        ]

        assert not missing_ep, (
            f"Found {len(missing_ep)} wiring entries without entry_point:\n"
            + "\n".join(f"  - {m}" for m in missing_ep)
        )

    def test_no_duplicate_entry_points(self) -> None:
        """Entry points must be unique across all wiring files."""
        entries = load_wiring_entries("provides")
        eps = [e.get("entry_point", "") for e in entries if e.get("entry_point")]
        duplicates = [ep for ep in eps if eps.count(ep) > 1]
        unique_dups = list(set(duplicates))

        assert not unique_dups, (
            f"Found {len(unique_dups)} duplicate entry_points:\n"
            + "\n".join(f"  - {d}" for d in unique_dups)
        )

    def test_entry_point_format_is_valid(self) -> None:
        """Entry points must follow 'module.path:ClassName' format."""
        entries = load_wiring_entries("provides")
        invalid = []
        for e in entries:
            ep = e.get("entry_point", "")
            if not ep:
                continue
            parsed = parse_entry_point(ep)
            if parsed is None:
                invalid.append(f"{e.get('name')}: '{ep}'")

        assert not invalid, (
            f"Found {len(invalid)} malformed entry_points:\n"
            + "\n".join(f"  - {i}" for i in invalid)
        )


class TestWiringEntryPointsImportable:
    """Verify wiring entry_points resolve to importable modules and classes."""

    @pytest.mark.parametrize("entry", load_wiring_entries("provides"), ids=lambda e: f"{e['_source_file']}-{e.get('name', '?')}-{e.get('entry_point', '?')}")
    def test_entry_point_module_importable(self, entry: dict) -> None:
        """Each wiring entry_point module must be importable.
        
        GAP-128-D-01: wiring YAML entry_points that don't resolve to real modules.
        """
        ep = entry.get("entry_point", "")
        if not ep:
            pytest.skip(f"No entry_point for {entry.get('name')}")

        parsed = parse_entry_point(ep)
        if parsed is None:
            pytest.skip(f"Malformed entry_point: {ep}")

        module_path, class_name = parsed

        try:
            mod = importlib.import_module(module_path)
        except ImportError as e:
            pytest.fail(
                f"Cannot import module '{module_path}' "
                f"for {entry.get('name')} ({entry['_source_file']}): {e}"
            )

        assert hasattr(mod, class_name), (
            f"Module '{module_path}' has no class '{class_name}' "
            f"(wiring: {entry.get('name')} in {entry['_source_file']})"
        )


class TestWiredOrchestratorProtocolCompliance:
    """Verify wired orchestrators implement the required protocol."""

    def test_wired_orchestrators_implement_protocol(self) -> None:
        """All wired *Orchestrator classes must use IOrchestrator or OrchestratorProtocolMixin.
        
        GAP-128-D-01: protocol compliance for all wired orchestrators.
        Scans both single-file and sub-package layouts; follows shim imports.
        """
        entries = load_wiring_entries("provides")
        violations: list[str] = []

        def scan_for_protocol(module_path: str) -> bool:
            """Scan module (or its package) for protocol. Returns True if found."""
            rel_path = module_path.replace(".", "/") + ".py"
            src_file = PROJECT_ROOT / rel_path

            src_to_scan: list[Path] = []
            if src_file.exists():
                src_to_scan = [src_file]
            else:
                # Try as a sub-package directory
                pkg_dir = PROJECT_ROOT / module_path.replace(".", "/")
                if pkg_dir.is_dir():
                    src_to_scan = list(pkg_dir.rglob("*.py"))

            if not src_to_scan:
                return False

            combined_src = "\n".join(
                p.read_text(encoding="utf-8", errors="ignore") for p in src_to_scan
            )

            # Direct protocol usage
            if "IOrchestrator" in combined_src or "OrchestratorProtocolMixin" in combined_src:
                return True

            # Shim pattern: re-exports from another module — follow the import
            import re
            shim_imports = re.findall(
                r"from\s+(cortex\.\S+)\s+import", combined_src
            )
            for imp_module in shim_imports:
                if imp_module == module_path:
                    continue  # avoid infinite recursion
                imp_path = imp_module.replace(".", "/") + ".py"
                imp_file = PROJECT_ROOT / imp_path
                if imp_file.exists():
                    imp_src = imp_file.read_text(encoding="utf-8", errors="ignore")
                    if "IOrchestrator" in imp_src or "OrchestratorProtocolMixin" in imp_src:
                        return True

            return False

        for entry in entries:
            ep = entry.get("entry_point", "")
            name = entry.get("name", "")
            if not ep or "Orchestrator" not in name:
                continue

            parsed = parse_entry_point(ep)
            if parsed is None:
                continue

            module_path, class_name = parsed
            if not scan_for_protocol(module_path):
                rel = module_path.replace(".", "/") + ".py"
                violations.append(
                    f"{class_name} ({rel}): no IOrchestrator or OrchestratorProtocolMixin"
                )

        assert not violations, (
            f"Found {len(violations)} wired orchestrators without protocol:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )

    def test_wired_orchestrators_have_ac_markers(self) -> None:
        """Wired orchestrators should have AC_START markers.
        
        Note: This is a coverage check, not a hard failure — some orchestrators
        delegate AC emission to their mixins.
        """
        entries = load_wiring_entries("provides")
        without_ac: list[str] = []
        checked = 0

        for entry in entries:
            ep = entry.get("entry_point", "")
            name = entry.get("name", "")
            if not ep or "Orchestrator" not in name:
                continue

            parsed = parse_entry_point(ep)
            if parsed is None:
                continue

            module_path, class_name = parsed
            rel_path = module_path.replace(".", "/") + ".py"
            src_file = PROJECT_ROOT / rel_path

            if not src_file.exists():
                continue

            checked += 1
            src = src_file.read_text(encoding="utf-8", errors="ignore")
            if "AC_START" not in src and "AC_COMPLETE" not in src:
                without_ac.append(f"{class_name} ({rel_path})")

        # Threshold: at least 50% of checked orchestrators must have AC markers
        # (others may delegate to mixins)
        if checked > 0:
            coverage_pct = (checked - len(without_ac)) / checked * 100
            assert coverage_pct >= 50, (
                f"AC marker coverage is {coverage_pct:.0f}% (need ≥50%). "
                f"{len(without_ac)}/{checked} orchestrators lack AC markers:\n"
                + "\n".join(f"  - {w}" for w in without_ac)
            )
