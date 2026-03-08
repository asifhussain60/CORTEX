"""Tests for KAL supporting triad + KnowledgeAcquisitionOrchestrator — Phase 135-b/c (KAL).

RED phase: all tests written BEFORE implementation (CORE-008 TDD mandate).
GAP-135-03: KnowledgeTemplateSynthesizer + KnowledgeSchemaValidator + KnowledgeIndexRegistrar
GAP-135-04: KnowledgeAcquisitionOrchestrator + IntelligenceFacade.acquire() + invalidate_cache()
"""
from __future__ import annotations

import tempfile
from pathlib import Path

import pytest
import yaml


# ─── KnowledgeTemplateSynthesizer tests ──────────────────────────────────────

class TestKnowledgeTemplateSynthesizer:
    """GAP-135-03: KnowledgeTemplateSynthesizer generates CORTEX-format knowledge YAMLs."""

    def test_synthesize_returns_valid_yaml(self) -> None:
        """synthesize() output is parseable YAML with required fields."""
        from cortex.intelligence.knowledge.knowledge_template_synthesizer import KnowledgeTemplateSynthesizer

        synth = KnowledgeTemplateSynthesizer()
        output = synth.synthesize(domain="testing-validation", intent="IMPLEMENT")
        assert isinstance(output, str)
        parsed = yaml.safe_load(output)
        assert parsed is not None

    def test_synthesize_5_categories(self) -> None:
        """best_practices section has Architecture/Testing/Performance/Security/Pitfalls."""
        from cortex.intelligence.knowledge.knowledge_template_synthesizer import KnowledgeTemplateSynthesizer

        synth = KnowledgeTemplateSynthesizer()
        output = synth.synthesize(domain="security", intent="AUDIT")
        parsed = yaml.safe_load(output)
        assert "best_practices" in parsed
        bp = parsed["best_practices"]
        assert isinstance(bp, list)
        assert len(bp) >= 3  # At least 3 categories (min schema requirement)

    def test_synthesize_cortex_alignment_metadata(self) -> None:
        """Output has cortex_alignment block with source/phase/intent/confidence."""
        from cortex.intelligence.knowledge.knowledge_template_synthesizer import KnowledgeTemplateSynthesizer

        synth = KnowledgeTemplateSynthesizer()
        output = synth.synthesize(domain="architecture", intent="DESIGN")
        parsed = yaml.safe_load(output)
        assert "cortex_alignment" in parsed
        ca = parsed["cortex_alignment"]
        assert "source" in ca
        assert "phase" in ca
        assert "intent" in ca
        assert "confidence" in ca

    def test_synthesize_has_title_and_domain(self) -> None:
        """Output has top-level title and domain fields."""
        from cortex.intelligence.knowledge.knowledge_template_synthesizer import KnowledgeTemplateSynthesizer

        synth = KnowledgeTemplateSynthesizer()
        output = synth.synthesize(domain="backend-python", intent="REFACTOR")
        parsed = yaml.safe_load(output)
        assert "title" in parsed
        assert "domain" in parsed
        assert parsed["domain"] == "backend-python"


# ─── KnowledgeSchemaValidator tests ──────────────────────────────────────────

class TestKnowledgeSchemaValidator:
    """GAP-135-03: KnowledgeSchemaValidator enforces 5-rule schema."""

    def _valid_yaml(self) -> str:
        return yaml.dump({
            "title": "Test Knowledge",
            "domain": "testing-validation",
            "best_practices": [
                {"category": "Architecture", "items": ["Use layers"]},
                {"category": "Testing", "items": ["Write tests first"]},
                {"category": "Performance", "items": ["Profile before optimizing"]},
            ],
            "cortex_alignment": {
                "source": "synthesized",
                "phase": "135",
                "intent": "IMPLEMENT",
                "confidence": 0.8,
            },
        })

    def test_validate_valid_yaml(self) -> None:
        """SchemaValidationResult.is_valid True for well-formed content."""
        from cortex.intelligence.knowledge.knowledge_schema_validator import (
            KnowledgeSchemaValidator,
            SchemaValidationResult,
        )

        validator = KnowledgeSchemaValidator()
        result = validator.validate(self._valid_yaml())
        assert isinstance(result, SchemaValidationResult)
        assert result.is_valid is True
        assert result.errors == []

    def test_validate_missing_title(self) -> None:
        """is_valid False, errors contains 'title' when title key absent."""
        from cortex.intelligence.knowledge.knowledge_schema_validator import KnowledgeSchemaValidator

        bad = yaml.dump({
            "domain": "security",
            "best_practices": [{"category": "A", "items": ["x"]}, {"category": "B", "items": ["y"]}, {"category": "C", "items": ["z"]}],
            "cortex_alignment": {"source": "s", "phase": "135", "intent": "I", "confidence": 0.5},
        })
        validator = KnowledgeSchemaValidator()
        result = validator.validate(bad)
        assert result.is_valid is False
        assert any("title" in e.lower() for e in result.errors)

    def test_validate_missing_domain(self) -> None:
        """is_valid False, errors contains 'domain' when domain key absent."""
        from cortex.intelligence.knowledge.knowledge_schema_validator import KnowledgeSchemaValidator

        bad = yaml.dump({
            "title": "Test",
            "best_practices": [{"category": "A", "items": ["x"]}, {"category": "B", "items": ["y"]}, {"category": "C", "items": ["z"]}],
            "cortex_alignment": {"source": "s", "phase": "135", "intent": "I", "confidence": 0.5},
        })
        validator = KnowledgeSchemaValidator()
        result = validator.validate(bad)
        assert result.is_valid is False
        assert any("domain" in e.lower() for e in result.errors)

    def test_validate_best_practices_not_list(self) -> None:
        """is_valid False when best_practices is not a list."""
        from cortex.intelligence.knowledge.knowledge_schema_validator import KnowledgeSchemaValidator

        bad = yaml.dump({
            "title": "Test",
            "domain": "security",
            "best_practices": "not a list",
            "cortex_alignment": {"source": "s", "phase": "135", "intent": "I", "confidence": 0.5},
        })
        validator = KnowledgeSchemaValidator()
        result = validator.validate(bad)
        assert result.is_valid is False

    def test_validate_fewer_than_3_items(self) -> None:
        """is_valid False when best_practices has fewer than 3 items."""
        from cortex.intelligence.knowledge.knowledge_schema_validator import KnowledgeSchemaValidator

        bad = yaml.dump({
            "title": "Test",
            "domain": "security",
            "best_practices": [{"category": "A", "items": ["x"]}],
            "cortex_alignment": {"source": "s", "phase": "135", "intent": "I", "confidence": 0.5},
        })
        validator = KnowledgeSchemaValidator()
        result = validator.validate(bad)
        assert result.is_valid is False
        assert any("min" in e.lower() or "3" in e or "least" in e.lower() for e in result.errors)


# ─── KnowledgeIndexRegistrar tests ───────────────────────────────────────────

class TestKnowledgeIndexRegistrar:
    """GAP-135-03: KnowledgeIndexRegistrar — idempotent INDEX.yaml registration."""

    def _make_index(self, tmp: Path) -> Path:
        index_path = tmp / "INDEX.yaml"
        index_path.write_text(yaml.dump({
            "testing-validation": {
                "guides": [{"path": "testing-validation/tdd-best-practices.yaml", "title": "TDD", "keywords": ["tdd"]}]
            }
        }))
        return index_path

    def test_register_new_domain(self, tmp_path: Path) -> None:
        """INDEX.yaml gains new domain section with guide entry."""
        from cortex.intelligence.knowledge.knowledge_index_registrar import KnowledgeIndexRegistrar

        index_path = self._make_index(tmp_path)
        registrar = KnowledgeIndexRegistrar(index_path=index_path)
        registrar.register(domain="security", path="security/new-guide.yaml", title="New Guide", keywords=["security"])
        data = yaml.safe_load(index_path.read_text())
        assert "security" in data
        assert any(g["path"] == "security/new-guide.yaml" for g in data["security"]["guides"])

    def test_register_idempotent(self, tmp_path: Path) -> None:
        """Registering the same path twice produces only one entry."""
        from cortex.intelligence.knowledge.knowledge_index_registrar import KnowledgeIndexRegistrar

        index_path = self._make_index(tmp_path)
        registrar = KnowledgeIndexRegistrar(index_path=index_path)
        registrar.register(domain="security", path="security/guide.yaml", title="G", keywords=["x"])
        registrar.register(domain="security", path="security/guide.yaml", title="G", keywords=["x"])
        data = yaml.safe_load(index_path.read_text())
        paths = [g["path"] for g in data["security"]["guides"]]
        assert paths.count("security/guide.yaml") == 1

    def test_register_sorts_alphabetically(self, tmp_path: Path) -> None:
        """Guides within domain are sorted alphabetically by path."""
        from cortex.intelligence.knowledge.knowledge_index_registrar import KnowledgeIndexRegistrar

        index_path = self._make_index(tmp_path)
        registrar = KnowledgeIndexRegistrar(index_path=index_path)
        registrar.register(domain="security", path="security/z-guide.yaml", title="Z", keywords=[])
        registrar.register(domain="security", path="security/a-guide.yaml", title="A", keywords=[])
        data = yaml.safe_load(index_path.read_text())
        paths = [g["path"] for g in data["security"]["guides"]]
        assert paths == sorted(paths)

    def test_register_creates_domain_section_if_missing(self, tmp_path: Path) -> None:
        """Missing domain key is created on first registration."""
        from cortex.intelligence.knowledge.knowledge_index_registrar import KnowledgeIndexRegistrar

        index_path = self._make_index(tmp_path)
        registrar = KnowledgeIndexRegistrar(index_path=index_path)
        registrar.register(domain="brand-new-domain", path="brand-new-domain/guide.yaml", title="BN", keywords=[])
        data = yaml.safe_load(index_path.read_text())
        assert "brand-new-domain" in data


# ─── KnowledgeAcquisitionOrchestrator tests ──────────────────────────────────

class TestKnowledgeAcquisitionOrchestrator:
    """GAP-135-04: KnowledgeAcquisitionOrchestrator — 6-step pipeline."""

    def test_acquire_above_threshold_skips(self) -> None:
        """score >= 0.80 → returns early, no synthesis performed."""
        from cortex.intelligence.knowledge.knowledge_acquisition_orchestrator import (
            KnowledgeAcquisitionOrchestrator,
            AcquisitionResult,
        )

        orch = KnowledgeAcquisitionOrchestrator()
        result = orch.acquire(signals=["testing-validation"], coverage_score=1.0)
        assert isinstance(result, AcquisitionResult)
        assert result.skipped is True
        assert len(result.acquired_domains) == 0

    def test_acquire_result_contains_acquired_domains(self) -> None:
        """AcquisitionResult.acquired_domains is a list."""
        from cortex.intelligence.knowledge.knowledge_acquisition_orchestrator import (
            KnowledgeAcquisitionOrchestrator,
        )

        orch = KnowledgeAcquisitionOrchestrator()
        result = orch.acquire(signals=["testing-validation"], coverage_score=1.0)
        assert isinstance(result.acquired_domains, list)

    def test_acquisition_result_dataclass_fields(self) -> None:
        """AcquisitionResult has skipped, acquired_domains, errors, cycles fields."""
        from cortex.intelligence.knowledge.knowledge_acquisition_orchestrator import AcquisitionResult

        r = AcquisitionResult(
            skipped=False,
            acquired_domains=["security"],
            errors=[],
            cycles=1,
        )
        assert r.skipped is False
        assert r.acquired_domains == ["security"]
        assert r.errors == []
        assert r.cycles == 1

    def test_acquire_below_threshold_runs_pipeline(self, tmp_path: Path) -> None:
        """score < 0.80 → pipeline executes and returns AcquisitionResult with skipped=False."""
        from cortex.intelligence.knowledge.knowledge_acquisition_orchestrator import (
            KnowledgeAcquisitionOrchestrator,
        )
        # Use a temp INDEX.yaml so we don't pollute the real one
        index_path = tmp_path / "INDEX.yaml"
        index_path.write_text(yaml.dump({}))

        orch = KnowledgeAcquisitionOrchestrator(index_path=index_path)
        result = orch.acquire(signals=["completely-unknown-domain-xyz"], coverage_score=0.0)
        assert result.skipped is False


# ─── IntelligenceFacade extension tests ──────────────────────────────────────

class TestIntelligenceFacadeKAL:
    """GAP-135-04: IntelligenceFacade.acquire() + invalidate_cache() extension."""

    def test_facade_acquire_returns_dict(self) -> None:
        """IntelligenceFacade.acquire() returns a dict with status key."""
        from cortex.intelligence.facade import IntelligenceFacade

        facade = IntelligenceFacade()
        result = facade.acquire(signals=[])
        assert isinstance(result, dict)
        assert "status" in result

    def test_facade_invalidate_cache_does_not_raise(self) -> None:
        """IntelligenceFacade.invalidate_cache() clears caches without raising."""
        from cortex.intelligence.facade import IntelligenceFacade

        facade = IntelligenceFacade()
        # Should not raise
        facade.invalidate_cache()

    def test_facade_invalidate_cache_clears_registry_index(self) -> None:
        """invalidate_cache() sets _registry_index_cache to None."""
        from cortex.intelligence.facade import IntelligenceFacade

        facade = IntelligenceFacade()
        # Prime the cache
        facade._registry_index_cache = ["something"]
        facade.invalidate_cache()
        assert facade._registry_index_cache is None

    def test_null_coverage_assessor_returns_full_coverage(self) -> None:
        """_NullCoverageAssessor.assess() → CoverageResult with score=1.0."""
        from cortex.intelligence.facade import _NullCoverageAssessor

        assessor = _NullCoverageAssessor()
        result = assessor.assess(["anything"])
        assert result.score == pytest.approx(1.0)
        assert result.acquisition_needed is False

    def test_null_acquisition_orchestrator_returns_empty(self) -> None:
        """_NullAcquisitionOrchestrator.acquire() → AcquisitionResult with skipped=True."""
        from cortex.intelligence.facade import _NullAcquisitionOrchestrator

        orch = _NullAcquisitionOrchestrator()
        result = orch.acquire(signals=[], coverage_score=1.0)
        assert result.skipped is True
        assert result.acquired_domains == []
