"""
Phase 124-B: Tests for atom-principle.yaml atom + comp-query.yaml injection.

RED gate: All tests fail until atom-principle.yaml is created and
          comp-query.yaml is updated with the atom-principle atom.
GREEN gate: All tests pass.

Governance: CORE-008 (TDD mandatory), CORE-002 (no .md report files).
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

ATOM_PRINCIPLE_PATH = (
    Path(__file__).parent.parent.parent
    / "cortex-registry"
    / "templates"
    / "response"
    / "atoms"
    / "atom-principle.yaml"
)

COMP_QUERY_PATH = (
    Path(__file__).parent.parent.parent
    / "cortex-registry"
    / "templates"
    / "response"
    / "compositions"
    / "comp-query.yaml"
)

REGISTRY_PATH = (
    Path(__file__).parent.parent.parent
    / "cortex-registry"
    / "templates"
    / "response"
    / "_registry.yaml"
)

REQUIRED_ATOM_FIELDS = {"id", "type", "version", "phase", "rendering_rules", "template", "theme_map"}


@pytest.fixture(scope="module")
def atom_principle() -> dict:
    assert ATOM_PRINCIPLE_PATH.exists(), (
        f"atom-principle.yaml not found at {ATOM_PRINCIPLE_PATH}"
    )
    data = yaml.safe_load(ATOM_PRINCIPLE_PATH.read_text())
    assert isinstance(data, dict)
    return data


@pytest.fixture(scope="module")
def comp_query() -> dict:
    assert COMP_QUERY_PATH.exists()
    data = yaml.safe_load(COMP_QUERY_PATH.read_text())
    assert isinstance(data, dict)
    return data


@pytest.fixture(scope="module")
def registry() -> dict:
    assert REGISTRY_PATH.exists()
    data = yaml.safe_load(REGISTRY_PATH.read_text())
    assert isinstance(data, dict)
    return data


class TestAtomPrincipleStructure:
    def test_atom_principle_file_exists(self):
        """atom-principle.yaml must exist at the canonical atom path."""
        assert ATOM_PRINCIPLE_PATH.exists(), (
            f"atom-principle.yaml not found at {ATOM_PRINCIPLE_PATH}"
        )

    def test_atom_id_is_atom_principle(self, atom_principle):
        """Atom id must be 'atom-principle'."""
        assert atom_principle.get("id") == "atom-principle"

    def test_atom_type_is_atom(self, atom_principle):
        """Type must be 'atom'."""
        assert atom_principle.get("type") == "atom"

    def test_atom_has_required_fields(self, atom_principle):
        """Atom must have all required structural fields."""
        missing = REQUIRED_ATOM_FIELDS - set(atom_principle.keys())
        assert not missing, f"atom-principle.yaml missing fields: {missing}"

    def test_atom_zone_is_3(self, atom_principle):
        """Principle atom belongs in Zone 3 (after orchestration breadcrumb)."""
        zone = atom_principle.get("rendering_rules", {}).get("zone")
        assert zone == 3, f"Expected zone=3, got zone={zone}"

    def test_atom_has_theme_map(self, atom_principle):
        """Atom must contain a theme_map with at least QUERY and DESIGN mappings."""
        theme_map = atom_principle.get("theme_map", {})
        assert "QUERY" in theme_map, "theme_map must have QUERY entry"
        assert "DESIGN" in theme_map, "theme_map must have DESIGN entry"

    def test_atom_template_has_principle_placeholders(self, atom_principle):
        """Template must contain {title} and {body} placeholders."""
        template = atom_principle.get("template", "")
        assert "{title}" in template, "Template must contain {title} placeholder"
        assert "{body}" in template, "Template must contain {body} placeholder"


class TestCompQueryPrincipleInjection:
    def test_comp_query_has_atom_principle(self, comp_query):
        """comp-query.yaml atoms list must include atom-principle."""
        atoms = comp_query.get("atoms", [])
        atom_ids = [a.get("id") for a in atoms]
        assert "atom-principle" in atom_ids, (
            f"comp-query.yaml atoms missing atom-principle; found: {atom_ids}"
        )

    def test_comp_query_atom_principle_is_zone_3(self, comp_query):
        """atom-principle entry in comp-query must be assigned to zone 3."""
        atoms = comp_query.get("atoms", [])
        principle_atoms = [a for a in atoms if a.get("id") == "atom-principle"]
        assert principle_atoms, "atom-principle not in comp-query atoms"
        assert principle_atoms[0].get("zone") == 3, (
            "atom-principle in comp-query must be zone=3"
        )

    def test_comp_query_template_has_principle_section(self, comp_query):
        """comp-query template must include a principle block marker."""
        template = comp_query.get("template", "")
        assert "{principle_title}" in template or "atom-principle" in template, (
            "comp-query template must reference principle atom"
        )


class TestRegistryHasAtomPrinciple:
    def test_registry_includes_atom_principle(self, registry):
        """_registry.yaml atoms list must contain an entry for atom-principle."""
        atoms = registry.get("atoms", [])
        atom_ids = [a.get("id") for a in atoms]
        assert "atom-principle" in atom_ids, (
            f"_registry.yaml atoms missing atom-principle; found: {atom_ids}"
        )

    def test_registry_atom_principle_status_active(self, registry):
        """atom-principle registry entry must have status ACTIVE."""
        atoms = registry.get("atoms", [])
        entry = next((a for a in atoms if a.get("id") == "atom-principle"), None)
        assert entry is not None
        assert entry.get("status") == "ACTIVE", (
            f"atom-principle registry status should be ACTIVE, got: {entry.get('status')}"
        )
