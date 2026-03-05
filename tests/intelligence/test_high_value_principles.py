"""
Phase 124-A: Tests for high-value-principles.yaml SDLC principles library.

RED gate: All tests must fail (FileNotFoundError) before the YAML is created.
GREEN gate: All tests pass once the YAML has been created with 90 principles.

Governance: CORE-008 (TDD mandatory), CORE-002 (no .md report files).
"""
from __future__ import annotations

from pathlib import Path

import pytest
import yaml

PRINCIPLES_PATH = (
    Path(__file__).parent.parent.parent
    / "cortex-registry"
    / "knowledge"
    / "sdlc"
    / "high-value-principles.yaml"
)

REQUIRED_DOMAINS = {
    "tdd",
    "refactoring",
    "architecture",
    "security",
    "api_design",
    "testing",
    "observability",
    "code_quality",
    "documentation",
    "devops",
}

REQUIRED_PRINCIPLE_FIELDS = {"id", "title", "body", "domain", "tags", "intent_types"}
REQUIRED_META_FIELDS = {"version", "description", "principles"}


@pytest.fixture(scope="module")
def principles_yaml() -> dict:
    assert PRINCIPLES_PATH.exists(), (
        f"high-value-principles.yaml not found at {PRINCIPLES_PATH}"
    )
    data = yaml.safe_load(PRINCIPLES_PATH.read_text())
    assert isinstance(data, dict), "YAML root must be a mapping"
    return data


class TestHighValuePrinciplesStructure:
    def test_file_exists(self):
        """The YAML file must exist at the canonical path."""
        assert PRINCIPLES_PATH.exists(), (
            f"high-value-principles.yaml not found at {PRINCIPLES_PATH}"
        )

    def test_root_has_required_meta_fields(self, principles_yaml):
        """Root must have version, description, and principles list."""
        for field in REQUIRED_META_FIELDS:
            assert field in principles_yaml, f"Missing root field: {field}"

    def test_principles_is_a_list(self, principles_yaml):
        """principles key must be a list."""
        assert isinstance(principles_yaml["principles"], list), (
            "principles must be a YAML list"
        )

    def test_exactly_90_principles(self, principles_yaml):
        """Catalogue must have exactly 90 principles (expanded in Phase 125)."""
        count = len(principles_yaml["principles"])
        assert count == 90, f"Expected 90 principles, got {count}"

    def test_all_principles_have_required_fields(self, principles_yaml):
        """Every principle entry must contain all required fields."""
        for i, p in enumerate(principles_yaml["principles"]):
            missing = REQUIRED_PRINCIPLE_FIELDS - set(p.keys())
            assert not missing, (
                f"Principle [{i}] id={p.get('id', '?')} missing fields: {missing}"
            )

    def test_all_principle_ids_are_unique(self, principles_yaml):
        """Principle IDs must be globally unique within the file."""
        ids = [p["id"] for p in principles_yaml["principles"]]
        assert len(ids) == len(set(ids)), "Duplicate principle IDs detected"

    def test_all_10_domains_represented(self, principles_yaml):
        """All 10 required domains must appear at least once."""
        domains_present = {p["domain"] for p in principles_yaml["principles"]}
        missing = REQUIRED_DOMAINS - domains_present
        assert not missing, f"Missing domains: {missing}"

    def test_each_principle_has_at_least_one_intent_type(self, principles_yaml):
        """Every principle must map to at least one CORTEX intent type."""
        for p in principles_yaml["principles"]:
            assert isinstance(p["intent_types"], list), (
                f"Principle {p['id']}: intent_types must be a list"
            )
            assert len(p["intent_types"]) >= 1, (
                f"Principle {p['id']}: intent_types must not be empty"
            )

    def test_each_principle_has_at_least_one_tag(self, principles_yaml):
        """Every principle must have at least one tag."""
        for p in principles_yaml["principles"]:
            assert isinstance(p["tags"], list), (
                f"Principle {p['id']}: tags must be a list"
            )
            assert len(p["tags"]) >= 1, (
                f"Principle {p['id']}: tags must not be empty"
            )

    def test_principle_body_is_non_empty_string(self, principles_yaml):
        """Every principle body must be a non-empty string (≥10 chars)."""
        for p in principles_yaml["principles"]:
            body = p.get("body", "")
            assert isinstance(body, str) and len(body) >= 10, (
                f"Principle {p['id']}: body too short or not a string"
            )
