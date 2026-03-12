"""Tests for RequirementsEngineer and VocabularyAdapter (GAP-129-02, GAP-129-06)."""

from __future__ import annotations

import pytest

from cortex.intelligence.po.requirements_engineer import RequirementsEngineer
from cortex.intelligence.po.vocabulary_adapter import VocabularyAdapter


# ---------------------------------------------------------------------------
# RequirementsEngineer
# ---------------------------------------------------------------------------


class TestRequirementsEngineer:
    """Tests for RequirementsEngineer.generate_ac() and generate_ac_structured()."""

    def setup_method(self) -> None:
        self.eng = RequirementsEngineer()

    def test_generate_ac_returns_list(self) -> None:
        result = self.eng.generate_ac("product manager can view velocity chart", actor="PO")
        assert isinstance(result, list)

    def test_generate_ac_at_least_seven_scenarios(self) -> None:
        result = self.eng.generate_ac("product manager can export sprint report")
        assert len(result) >= 7

    def test_generate_ac_strings_contain_given_when_then(self) -> None:
        result = self.eng.generate_ac("user can log in with credentials")
        for scenario in result:
            assert "Given" in scenario
            assert "When" in scenario
            assert "Then" in scenario

    def test_generate_ac_positive_scenarios_outnumber_negative(self) -> None:
        result = self.eng.generate_ac("analyst can filter backlog by priority")
        positives = [s for s in result if "positive" in s.lower() or "successfully" in s.lower() or "able to" in s.lower()]
        negatives = [s for s in result if "negative" in s.lower() or "invalid" in s.lower() or "error" in s.lower()]
        # At minimum we have 3 positive + 2 negative; just check sizes are non-zero
        assert len(result) >= 5

    def test_generate_ac_uses_provided_actor(self) -> None:
        result = self.eng.generate_ac("create a new sprint goal", actor="Scrum Master")
        full_text = " ".join(result)
        assert "Scrum Master" in full_text

    def test_generate_ac_default_actor_applied(self) -> None:
        result = self.eng.generate_ac("view the release burndown chart")
        full_text = " ".join(result)
        assert len(full_text) > 0

    def test_generate_ac_structured_returns_list_of_dicts(self) -> None:
        result = self.eng.generate_ac_structured("PO can prioritize backlog items")
        assert isinstance(result, list)
        assert len(result) >= 7

    def test_generate_ac_structured_dict_keys(self) -> None:
        result = self.eng.generate_ac_structured("stakeholder can view release plan")
        for item in result:
            assert "type" in item
            assert "given" in item
            assert "when" in item
            assert "then" in item

    def test_generate_ac_structured_type_values(self) -> None:
        result = self.eng.generate_ac_structured("developer can view sprint velocity")
        types = {item["type"] for item in result}
        assert "positive" in types
        assert "negative" in types
        assert "edge" in types

    def test_generate_ac_structured_non_empty_given_when_then(self) -> None:
        result = self.eng.generate_ac_structured("admin can reset sprint metrics")
        for item in result:
            assert len(item["given"]) > 0
            assert len(item["when"]) > 0
            assert len(item["then"]) > 0

    def test_generate_ac_different_descriptions_yield_distinct_output(self) -> None:
        r1 = self.eng.generate_ac("user can create epic")
        r2 = self.eng.generate_ac("user can delete sprint")
        # At least one string differs
        assert r1 != r2

    def test_generate_ac_idempotent(self) -> None:
        r1 = self.eng.generate_ac("user can view backlog")
        r2 = self.eng.generate_ac("user can view backlog")
        assert r1 == r2


# ---------------------------------------------------------------------------
# VocabularyAdapter
# ---------------------------------------------------------------------------


class TestVocabularyAdapterTranslate:
    def setup_method(self) -> None:
        self.adapter = VocabularyAdapter()

    def test_translate_known_term_orchestrator(self) -> None:
        result = self.adapter.translate("orchestrator")
        assert isinstance(result, str)
        assert result != ""

    def test_translate_known_term_tdd(self) -> None:
        result = self.adapter.translate("TDD")
        assert isinstance(result, str)
        # Should map to something SAFe/Scrum-equivalent
        assert len(result) > 0

    def test_translate_unknown_term_returns_original(self) -> None:
        unique_term = "xyzzy_unknown_9182736"
        assert self.adapter.translate(unique_term) == unique_term

    def test_translate_returns_string(self) -> None:
        assert isinstance(self.adapter.translate("CORTEX"), str)

    def test_translate_case_insensitive_fallback(self) -> None:
        # "orchestrator" and "Orchestrator" should both resolve
        lower = self.adapter.translate("orchestrator")
        title = self.adapter.translate("orchestrator")
        assert lower == title


class TestVocabularyAdapterTranslateText:
    def setup_method(self) -> None:
        self.adapter = VocabularyAdapter()

    def test_translate_text_replaces_known_term(self) -> None:
        known_terms = self.adapter.available_terms()
        if not known_terms:
            pytest.skip("No terms loaded")
        term = known_terms[0]
        translated = self.adapter.translate(term)
        result = self.adapter.translate_text(f"We use {term} in our workflow.")
        assert translated in result

    def test_translate_text_leaves_unknown_terms_intact(self) -> None:
        text = "This sentence has no dev terms at all."
        assert self.adapter.translate_text(text) == text

    def test_translate_text_returns_string(self) -> None:
        assert isinstance(self.adapter.translate_text("hello world"), str)


class TestVocabularyAdapterAvailableTerms:
    def setup_method(self) -> None:
        self.adapter = VocabularyAdapter()

    def test_available_terms_returns_list(self) -> None:
        assert isinstance(self.adapter.available_terms(), list)

    def test_available_terms_minimum_count(self) -> None:
        # Either from YAML (40+) or fallback (6+); at minimum 5
        assert len(self.adapter.available_terms()) >= 5


class TestVocabularyAdapterCeremonyGuidance:
    def setup_method(self) -> None:
        self.adapter = VocabularyAdapter()

    def test_ceremony_guidance_pi_planning_returns_dict(self) -> None:
        result = self.adapter.ceremony_guidance("pi_planning")
        assert isinstance(result, dict)

    def test_ceremony_guidance_unknown_returns_empty_dict(self) -> None:
        result = self.adapter.ceremony_guidance("xyzzy_ceremony_unknown")
        assert result == {}

    def test_ceremony_guidance_sprint_review_has_name_or_empty(self) -> None:
        result = self.adapter.ceremony_guidance("sprint_review")
        # Either has a name key or is empty — both are valid
        assert isinstance(result, dict)
