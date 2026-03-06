"""
Phase 129-B: AI Spark Library Schema Validation Tests
Tests for cortex-registry/knowledge/ai/ai-adoption-sparks.yaml

GAP: GAP-129-02 — ai_spark library created with schema compliance
CORE-008: TDD — these tests were written before the library was finalized.
"""

import pathlib
from collections import Counter

import pytest
import yaml

# ─── Constants ────────────────────────────────────────────────────────────────

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
_AI_SPARK_PATH = _REPO_ROOT / "cortex-registry" / "knowledge" / "ai" / "ai-adoption-sparks.yaml"

REQUIRED_FIELDS = {
    "id", "title", "body", "author", "source",
    "category", "tags", "audience", "dedup_key",
}
VALID_CATEGORIES = {
    "productivity", "creativity", "collaboration", "adoption",
    "evolution", "ethics", "craftsmanship", "leadership",
}
MINIMUM_SPARKS = 150
BODY_MAX_CHARS = 200


# ─── Fixtures ─────────────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def sparks() -> list[dict]:
    """Load the ai-adoption-sparks.yaml and return the sparks list."""
    assert _AI_SPARK_PATH.exists(), (
        f"ai-adoption-sparks.yaml not found at {_AI_SPARK_PATH}. "
        "Create it as part of Phase 129-B."
    )
    data = yaml.safe_load(_AI_SPARK_PATH.read_text())
    assert "sparks" in data, "Top-level key must be 'sparks:'"
    return data["sparks"]


# ─── Test: File existence and structure ──────────────────────────────────────

class TestAiSparkLibraryExists:
    def test_file_exists(self) -> None:
        assert _AI_SPARK_PATH.exists(), f"Missing: {_AI_SPARK_PATH}"

    def test_yaml_parseable(self) -> None:
        data = yaml.safe_load(_AI_SPARK_PATH.read_text())
        assert isinstance(data, dict)

    def test_top_level_key_is_sparks(self) -> None:
        data = yaml.safe_load(_AI_SPARK_PATH.read_text())
        assert "sparks" in data, "Top-level key must be 'sparks:' — not 'items:' or 'quotes:'"

    def test_sparks_is_list(self, sparks: list[dict]) -> None:
        assert isinstance(sparks, list)


# ─── Test: Minimum count ─────────────────────────────────────────────────────

class TestAiSparkLibraryCount:
    def test_minimum_spark_count(self, sparks: list[dict]) -> None:
        assert len(sparks) >= MINIMUM_SPARKS, (
            f"Expected ≥{MINIMUM_SPARKS} sparks, got {len(sparks)}"
        )

    def test_validation_block_minimum(self) -> None:
        data = yaml.safe_load(_AI_SPARK_PATH.read_text())
        val = data.get("validation", {})
        assert val.get("minimum_sparks", 0) >= MINIMUM_SPARKS


# ─── Test: Required fields ───────────────────────────────────────────────────

class TestAiSparkRequiredFields:
    def test_all_sparks_have_required_fields(self, sparks: list[dict]) -> None:
        violations = []
        for spark in sparks:
            missing = REQUIRED_FIELDS - spark.keys()
            if missing:
                violations.append((spark.get("id", "unknown"), missing))
        assert not violations, f"Missing fields: {violations}"

    def test_all_sparks_have_id(self, sparks: list[dict]) -> None:
        ids = [s.get("id") for s in sparks]
        missing = [i for i, v in enumerate(ids) if not v]
        assert not missing, f"Sparks at indices {missing} have no id"

    def test_all_sparks_have_non_empty_body(self, sparks: list[dict]) -> None:
        violations = [s["id"] for s in sparks if not s.get("body", "").strip()]
        assert not violations, f"Empty body on sparks: {violations}"

    def test_all_sparks_have_non_empty_author(self, sparks: list[dict]) -> None:
        violations = [s["id"] for s in sparks if not s.get("author", "").strip()]
        assert not violations, f"Empty author on sparks: {violations}"

    def test_all_sparks_have_non_empty_source(self, sparks: list[dict]) -> None:
        violations = [s["id"] for s in sparks if not s.get("source", "").strip()]
        assert not violations, f"Empty source on sparks: {violations}"

    def test_all_sparks_have_tags_list(self, sparks: list[dict]) -> None:
        violations = [s["id"] for s in sparks if not isinstance(s.get("tags"), list)]
        assert not violations, f"Non-list tags on sparks: {violations}"

    def test_all_sparks_have_non_empty_tags(self, sparks: list[dict]) -> None:
        violations = [s["id"] for s in sparks if not s.get("tags")]
        assert not violations, f"Empty tags on sparks: {violations}"

    def test_all_sparks_have_dedup_key(self, sparks: list[dict]) -> None:
        violations = [s["id"] for s in sparks if not s.get("dedup_key", "").strip()]
        assert not violations, f"Missing dedup_key on sparks: {violations}"

    def test_relevance_weight_present(self, sparks: list[dict]) -> None:
        """relevance_weight is optional but recommended — warn if absent."""
        missing = [s["id"] for s in sparks if "relevance_weight" not in s]
        # Not a hard failure — but surface the info
        if missing:
            pytest.warns(UserWarning, match="relevance_weight") if False else None
            # Soft assertion: allow missing but print
            print(f"\nINFO: {len(missing)} sparks missing relevance_weight: {missing[:5]}...")


# ─── Test: Body length ───────────────────────────────────────────────────────

class TestAiSparkBodyLength:
    def test_all_bodies_within_200_chars(self, sparks: list[dict]) -> None:
        violations = [
            (s["id"], len(s["body"].strip()))
            for s in sparks
            if len(s["body"].strip()) > BODY_MAX_CHARS
        ]
        assert not violations, (
            f"{len(violations)} bodies exceed {BODY_MAX_CHARS} chars:\n"
            + "\n".join(f"  {sid}: {length}" for sid, length in violations)
        )

    def test_no_empty_bodies(self, sparks: list[dict]) -> None:
        violations = [s["id"] for s in sparks if not s.get("body", "").strip()]
        assert not violations, f"Empty bodies: {violations}"

    def test_bodies_have_meaningful_content(self, sparks: list[dict]) -> None:
        violations = [s["id"] for s in sparks if len(s.get("body", "").strip()) < 20]
        assert not violations, f"Bodies too short (<20 chars): {violations}"


# ─── Test: Dedup key uniqueness ──────────────────────────────────────────────

class TestAiSparkDedupKeys:
    def test_dedup_keys_are_unique(self, sparks: list[dict]) -> None:
        keys = [s["dedup_key"] for s in sparks if s.get("dedup_key")]
        counter = Counter(keys)
        dupes = {k: v for k, v in counter.items() if v > 1}
        assert not dupes, f"Duplicate dedup_keys found: {dupes}"

    def test_id_values_are_unique(self, sparks: list[dict]) -> None:
        ids = [s["id"] for s in sparks if s.get("id")]
        counter = Counter(ids)
        dupes = {k: v for k, v in counter.items() if v > 1}
        assert not dupes, f"Duplicate ids found: {dupes}"


# ─── Test: Category coverage ─────────────────────────────────────────────────

class TestAiSparkCategories:
    def test_all_sparks_have_valid_category(self, sparks: list[dict]) -> None:
        violations = [
            (s["id"], s.get("category"))
            for s in sparks
            if s.get("category") not in VALID_CATEGORIES
        ]
        assert not violations, (
            f"Invalid categories: {violations}\nValid: {VALID_CATEGORIES}"
        )

    def test_all_required_categories_present(self, sparks: list[dict]) -> None:
        present = {s["category"] for s in sparks}
        missing = VALID_CATEGORIES - present
        assert not missing, f"Required categories missing from library: {missing}"

    def test_each_category_has_minimum_5_sparks(self, sparks: list[dict]) -> None:
        cats = Counter(s["category"] for s in sparks)
        low = {cat: count for cat, count in cats.items() if count < 5}
        assert not low, f"Categories with <5 sparks: {low}"


# ─── Test: Audience ──────────────────────────────────────────────────────────

class TestAiSparkAudience:
    def test_all_sparks_have_universal_audience(self, sparks: list[dict]) -> None:
        violations = [
            (s["id"], s.get("audience"))
            for s in sparks
            if s.get("audience") != "universal"
        ]
        assert not violations, (
            f"Non-universal audience detected (all sparks must be 'universal'): {violations}"
        )


# ─── Test: Relevance weight range ────────────────────────────────────────────

class TestAiSparkRelevanceWeight:
    def test_relevance_weight_in_range(self, sparks: list[dict]) -> None:
        violations = [
            (s["id"], s["relevance_weight"])
            for s in sparks
            if "relevance_weight" in s
            and not (0.0 <= s["relevance_weight"] <= 1.0)
        ]
        assert not violations, f"Out-of-range relevance_weight: {violations}"

    def test_no_zero_weight_sparks(self, sparks: list[dict]) -> None:
        violations = [
            s["id"] for s in sparks
            if s.get("relevance_weight", 1.0) == 0.0
        ]
        assert not violations, f"Zero-weight sparks (will never be selected): {violations}"


# ─── Test: Validation block ──────────────────────────────────────────────────

class TestAiSparkValidationBlock:
    def test_validation_block_exists(self) -> None:
        data = yaml.safe_load(_AI_SPARK_PATH.read_text())
        assert "validation" in data, "YAML must have a 'validation:' block"

    def test_validation_has_required_fields_spec(self) -> None:
        data = yaml.safe_load(_AI_SPARK_PATH.read_text())
        val = data.get("validation", {})
        assert "required_fields_per_spark" in val

    def test_validation_has_required_categories(self) -> None:
        data = yaml.safe_load(_AI_SPARK_PATH.read_text())
        val = data.get("validation", {})
        assert "required_categories" in val

    def test_validation_body_max_chars(self) -> None:
        data = yaml.safe_load(_AI_SPARK_PATH.read_text())
        val = data.get("validation", {})
        assert val.get("body_max_chars", 0) == BODY_MAX_CHARS

    def test_validation_no_fabricated_quotes(self) -> None:
        data = yaml.safe_load(_AI_SPARK_PATH.read_text())
        val = data.get("validation", {})
        assert val.get("no_fabricated_quotes") is True
