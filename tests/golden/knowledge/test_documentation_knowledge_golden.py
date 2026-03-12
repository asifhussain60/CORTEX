"""
Phase 145: Documentation Intelligence Knowledge Domain — Golden Tests
RED-first: YAML files do not exist yet — all tests fail until phase-145 is implemented.

AC_START: AC-145-DOCUMENTATION-INTELLIGENCE-001
Authority: CORE-008 (TDD), CORE-064 (Sweep Completeness)
Covers: GAP-145-01, GAP-145-02, GAP-145-03
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml

PROJECT_ROOT = Path(__file__).resolve().parents[3]
REGISTRY = PROJECT_ROOT / "cortex-registry"
KNOWLEDGE_ROOT = REGISTRY / "knowledge"
DOC_YAML = KNOWLEDGE_ROOT / "best-practices" / "documentation" / "documentation-intelligence.yaml"
INDEX_YAML = KNOWLEDGE_ROOT / "INDEX.yaml"
SIGNAL_MAP_YAML = REGISTRY / "config" / "domain-signal-map.yaml"

EXPECTED_SUBDOMAINS = [
    "technical_docs",
    "api_docs",
    "adrs",
    "runbooks",
    "release_notes",
    "onboarding",
    "knowledge_management",
    "documentation_testing",
    "accessibility",
    "governance",
]

MIN_PRACTICE_COUNT = 60


# ─────────────────────────────────────────────────────────────────────────────
# Schema Compliance Tests (GAP-145-01)
# ─────────────────────────────────────────────────────────────────────────────

class TestDocumentationYAMLSchema:
    """Schema compliance: the YAML file exists and has the expected structure."""

    def test_yaml_file_exists(self) -> None:
        """GAP-145-01: documentation-intelligence.yaml must exist."""
        assert DOC_YAML.exists(), (
            f"documentation-intelligence.yaml not found at {DOC_YAML} — GAP-145-01"
        )

    def test_yaml_is_valid(self) -> None:
        """GAP-145-01: YAML must parse without errors."""
        content = DOC_YAML.read_text(encoding="utf-8")
        data = yaml.safe_load(content)
        assert isinstance(data, dict), "YAML root must be a mapping — GAP-145-01"

    def test_yaml_has_title(self) -> None:
        """GAP-145-01: YAML must have a 'title' key."""
        data = yaml.safe_load(DOC_YAML.read_text(encoding="utf-8"))
        assert "title" in data, "YAML must have a 'title' key — GAP-145-01"

    def test_yaml_has_domain(self) -> None:
        """GAP-145-01: YAML must declare its domain."""
        data = yaml.safe_load(DOC_YAML.read_text(encoding="utf-8"))
        assert "domain" in data or "category" in data, (
            "YAML must have 'domain' or 'category' key — GAP-145-01"
        )

    def test_yaml_has_practices_list(self) -> None:
        """GAP-145-01: YAML must contain a 'practices' list at the root level."""
        data = yaml.safe_load(DOC_YAML.read_text(encoding="utf-8"))
        assert "practices" in data, (
            "YAML must have a 'practices' key — GAP-145-01"
        )
        assert isinstance(data["practices"], list), (
            "'practices' must be a list — GAP-145-01"
        )

    def test_each_practice_has_required_fields(self) -> None:
        """GAP-145-01: Each practice must have id, title, and subdomain fields."""
        data = yaml.safe_load(DOC_YAML.read_text(encoding="utf-8"))
        practices: List[Dict[str, Any]] = data.get("practices", [])
        assert len(practices) > 0, "No practices found — GAP-145-01"
        for practice in practices:
            assert "id" in practice, f"Practice missing 'id': {practice} — GAP-145-01"
            assert "title" in practice, f"Practice missing 'title': {practice} — GAP-145-01"
            assert "subdomain" in practice, f"Practice missing 'subdomain': {practice} — GAP-145-01"


# ─────────────────────────────────────────────────────────────────────────────
# Practice Count Tests (GAP-145-01)
# ─────────────────────────────────────────────────────────────────────────────

class TestDocumentationPracticeCount:
    """Practice count: at least 60 practices across 10 sub-domains."""

    def test_practice_count_is_at_least_60(self) -> None:
        """GAP-145-01: At least 60 documentation practices must be defined."""
        data = yaml.safe_load(DOC_YAML.read_text(encoding="utf-8"))
        practices = data.get("practices", [])
        assert len(practices) >= MIN_PRACTICE_COUNT, (
            f"Only {len(practices)} practices found — need {MIN_PRACTICE_COUNT}+ (GAP-145-01)"
        )

    def test_all_10_subdomains_are_covered(self) -> None:
        """GAP-145-01: All 10 sub-domains must have at least one practice."""
        data = yaml.safe_load(DOC_YAML.read_text(encoding="utf-8"))
        practices = data.get("practices", [])
        covered = {p.get("subdomain") for p in practices if "subdomain" in p}
        for subdomain in EXPECTED_SUBDOMAINS:
            assert subdomain in covered, (
                f"Sub-domain '{subdomain}' has no practices — GAP-145-01"
            )

    def test_each_subdomain_has_at_least_5_practices(self) -> None:
        """GAP-145-01: Each sub-domain must have at least 5 practices (6×10=60 minimum)."""
        data = yaml.safe_load(DOC_YAML.read_text(encoding="utf-8"))
        practices = data.get("practices", [])
        counts: Dict[str, int] = {}
        for p in practices:
            sd = p.get("subdomain", "")
            counts[sd] = counts.get(sd, 0) + 1
        for subdomain in EXPECTED_SUBDOMAINS:
            count = counts.get(subdomain, 0)
            assert count >= 5, (
                f"Sub-domain '{subdomain}' has only {count} practices — need ≥5 (GAP-145-01)"
            )

    def test_practice_ids_are_unique(self) -> None:
        """GAP-145-01: No duplicate practice IDs."""
        data = yaml.safe_load(DOC_YAML.read_text(encoding="utf-8"))
        ids = [p.get("id") for p in data.get("practices", []) if "id" in p]
        assert len(ids) == len(set(ids)), (
            f"Duplicate practice IDs found: {[i for i in ids if ids.count(i) > 1]} — GAP-145-01"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Domain Registration Tests (GAP-145-02)
# ─────────────────────────────────────────────────────────────────────────────

class TestDocumentationDomainRegistration:
    """Domain registration: documentation domain must appear in INDEX.yaml."""

    def test_index_yaml_has_documentation_domain(self) -> None:
        """GAP-145-02: INDEX.yaml must contain a 'documentation' domain entry."""
        data = yaml.safe_load(INDEX_YAML.read_text(encoding="utf-8"))
        assert "documentation" in data, (
            "INDEX.yaml missing 'documentation' domain key — GAP-145-02"
        )

    def test_documentation_domain_has_guides(self) -> None:
        """GAP-145-02: The documentation domain must list at least one guide."""
        data = yaml.safe_load(INDEX_YAML.read_text(encoding="utf-8"))
        doc_domain = data.get("documentation", {})
        guides = doc_domain.get("guides", [])
        assert len(guides) >= 1, (
            "documentation domain must have at least one guide in INDEX.yaml — GAP-145-02"
        )

    def test_documentation_guide_path_is_correct(self) -> None:
        """GAP-145-02: The guide path must point to documentation-intelligence.yaml."""
        data = yaml.safe_load(INDEX_YAML.read_text(encoding="utf-8"))
        guides = data.get("documentation", {}).get("guides", [])
        paths = [g.get("path", "") for g in guides]
        assert any("documentation-intelligence" in p for p in paths), (
            f"No guide references documentation-intelligence.yaml — got {paths} (GAP-145-02)"
        )

    def test_documentation_guide_has_keywords(self) -> None:
        """GAP-145-02: The documentation guide must have at least 4 keywords."""
        data = yaml.safe_load(INDEX_YAML.read_text(encoding="utf-8"))
        guides = data.get("documentation", {}).get("guides", [])
        for guide in guides:
            if "documentation-intelligence" in guide.get("path", ""):
                keywords = guide.get("keywords", [])
                assert len(keywords) >= 4, (
                    f"documentation guide has only {len(keywords)} keywords — need ≥4 (GAP-145-02)"
                )
                return
        pytest.fail("documentation-intelligence guide not found in INDEX.yaml — GAP-145-02")


# ─────────────────────────────────────────────────────────────────────────────
# Domain Signal Map Tests (GAP-145-03)
# ─────────────────────────────────────────────────────────────────────────────

class TestDocumentationSignalMap:
    """Domain signal: documentation pattern must appear in domain-signal-map.yaml."""

    def test_signal_map_has_documentation_pattern(self) -> None:
        """GAP-145-03: domain-signal-map.yaml must have a documentation signal entry."""
        data = yaml.safe_load(SIGNAL_MAP_YAML.read_text(encoding="utf-8"))
        patterns = data.get("patterns", [])
        doc_patterns = [
            p for p in patterns
            if p.get("domain") == "documentation"
        ]
        assert len(doc_patterns) >= 1, (
            "No 'documentation' domain entry in domain-signal-map.yaml — GAP-145-03"
        )

    def test_documentation_signal_includes_key_terms(self) -> None:
        """GAP-145-03: The documentation signal pattern must cover key terms."""
        data = yaml.safe_load(SIGNAL_MAP_YAML.read_text(encoding="utf-8"))
        patterns = data.get("patterns", [])
        doc_patterns = [p for p in patterns if p.get("domain") == "documentation"]
        assert len(doc_patterns) >= 1, "No documentation pattern — GAP-145-03"
        pattern_str = doc_patterns[0].get("pattern", "")
        required_terms = ["document", "readme", "runbook"]
        for term in required_terms:
            assert term in pattern_str, (
                f"Signal pattern missing '{term}' — got: '{pattern_str}' (GAP-145-03)"
            )

    def test_documentation_signal_points_to_correct_file(self) -> None:
        """GAP-145-03: Signal entry must reference documentation-intelligence.yaml."""
        data = yaml.safe_load(SIGNAL_MAP_YAML.read_text(encoding="utf-8"))
        patterns = data.get("patterns", [])
        doc_patterns = [p for p in patterns if p.get("domain") == "documentation"]
        assert len(doc_patterns) >= 1, "No documentation pattern — GAP-145-03"
        knowledge_file = doc_patterns[0].get("knowledge_file", "")
        assert "documentation-intelligence" in knowledge_file, (
            f"Signal entry must reference documentation-intelligence.yaml — "
            f"got: '{knowledge_file}' (GAP-145-03)"
        )
