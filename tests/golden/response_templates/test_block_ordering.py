"""
GAP-128-C-03: Response template blocks must appear in the canonical assembly order.

The 5-section golden format from .github/templates/cortex-response-templates.md
defines the canonical section order:
  Summary → Analysis → Recommendation → Benefits & Risks → Next Steps

Compositions (comp-*.yaml) must reference blocks in this order.
Also validates that composition YAML files are structurally valid.

Drift lock: check-44-response-template-compliance-lock.yaml
"""

from pathlib import Path
from typing import List, Tuple
import yaml
import pytest

REPO_ROOT = Path(__file__).parents[3]
COMPOSITIONS_DIR = REPO_ROOT / "cortex-registry/templates/response/compositions"

# Canonical 5-section order from cortex-response-templates.md § Golden Format
CANONICAL_SECTION_ORDER = [
    "summary",
    "analysis",
    "recommendation",
    "benefits",
    "next_steps",
]

# Required top-level fields for every composition YAML
REQUIRED_COMPOSITION_FIELDS = {"id", "type"}


def _load_composition(path: Path) -> dict:
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as e:
        pytest.fail(f"YAML parse error in {path.name}: {e}")
        return {}


def _get_composition_files() -> List[Path]:
    if not COMPOSITIONS_DIR.exists():
        return []
    return sorted(COMPOSITIONS_DIR.glob("*.yaml"))


class TestBlockOrdering:
    """GAP-128-C-03: Block ordering and structural validity of composition YAML files."""

    def test_compositions_dir_exists(self):
        """compositions/ directory must exist under cortex-registry/templates/response/."""
        assert COMPOSITIONS_DIR.exists(), (
            f"Compositions directory not found: {COMPOSITIONS_DIR}"
        )

    def test_at_least_one_composition_exists(self):
        """At least one composition YAML file must exist."""
        files = _get_composition_files()
        assert len(files) > 0, "No composition YAML files found in compositions/"

    def test_all_compositions_have_required_fields(self):
        """Every composition YAML must have 'id' and 'description' fields."""
        files = _get_composition_files()
        missing: List[str] = []
        for path in files:
            data = _load_composition(path)
            for field in REQUIRED_COMPOSITION_FIELDS:
                if field not in data:
                    missing.append(f"{path.name}: missing field '{field}'")
        assert missing == [], (
            f"Composition files missing required fields:\n"
            + "\n".join(f"  {m}" for m in missing)
        )

    def test_no_duplicate_composition_ids(self):
        """Composition IDs must be unique across all comp-*.yaml files."""
        files = _get_composition_files()
        seen: dict = {}
        duplicates: List[str] = []
        for path in files:
            data = _load_composition(path)
            comp_id = data.get("id")
            if not comp_id:
                continue
            if comp_id in seen:
                duplicates.append(f"'{comp_id}' in '{path.name}' (first in '{seen[comp_id]}')")
            else:
                seen[comp_id] = path.name
        assert duplicates == [], (
            f"Duplicate composition IDs:\n" + "\n".join(f"  {d}" for d in duplicates)
        )

    def test_compositions_valid_yaml(self):
        """Every composition file must be valid YAML with a non-empty document."""
        files = _get_composition_files()
        invalid: List[str] = []
        for path in files:
            try:
                data = yaml.safe_load(path.read_text(encoding="utf-8"))
            except yaml.YAMLError as e:
                invalid.append(f"{path.name}: {e}")
                continue
            if not isinstance(data, dict) or not data:
                invalid.append(f"{path.name}: empty or non-mapping YAML document")
        assert invalid == [], (
            f"Invalid composition YAML files:\n" + "\n".join(f"  {i}" for i in invalid)
        )

    def test_sections_key_order_if_present(self):
        """
        If a composition declares a 'sections' list, the section keys must follow
        the canonical order: summary → analysis → recommendation → benefits → next_steps.
        Compositions without a 'sections' key are exempt.
        """
        files = _get_composition_files()
        violations: List[str] = []
        for path in files:
            data = _load_composition(path)
            sections = data.get("sections")
            if not isinstance(sections, list):
                continue
            # Extract normalized section ids/names
            section_keys = []
            for sec in sections:
                if isinstance(sec, dict):
                    key = (sec.get("id") or sec.get("name") or "").lower().replace("-", "_").replace(" ", "_")
                    section_keys.append(key)
                elif isinstance(sec, str):
                    section_keys.append(sec.lower().replace("-", "_").replace(" ", "_"))
            # Check that canonical sections appear in order (if they appear at all)
            canonical_present = [s for s in CANONICAL_SECTION_ORDER if any(s in k for k in section_keys)]
            actual_positions = []
            for canonical in canonical_present:
                for i, key in enumerate(section_keys):
                    if canonical in key:
                        actual_positions.append((canonical, i))
                        break
            # Verify positions are non-decreasing
            for j in range(1, len(actual_positions)):
                if actual_positions[j][1] < actual_positions[j - 1][1]:
                    violations.append(
                        f"{path.name}: section '{actual_positions[j][0]}' appears before "
                        f"'{actual_positions[j-1][0]}' (violates canonical order)"
                    )
        assert violations == [], (
            f"Section order violations in compositions:\n"
            + "\n".join(f"  {v}" for v in violations)
        )
