"""
Sub-Phase B — Synthesis Engine Consolidation: RED/GREEN tests.

GAP-107-03: Consolidate overlapping synthesis engines (CORE-035)
GAP-107-04: Eliminate duplicate BusinessKnowledgeRepository (CORE-035)

TDD Contract (CORE-008):
  - Tests must drive the implementation, not the reverse.
  - Run: python3 -m pytest tests/intelligence/models/test_synthesis_consolidation.py -v

Governance:
  - CORE-008: TDD mandatory
  - CORE-035: Single canonical implementation
  - CORE-064: Sweep completeness — both GAPs must close
"""
from __future__ import annotations

import ast
import pathlib
from typing import List

import pytest


CORTEX_ROOT = pathlib.Path(__file__).parents[3] / "cortex"


def _count_class_definitions(class_name: str, scan_root: pathlib.Path) -> List[str]:
    """AST-scan for all definitions of a given class name under scan_root."""
    locations: list[str] = []
    for py_file in scan_root.rglob("*.py"):
        if "__pycache__" in str(py_file):
            continue
        try:
            tree = ast.parse(py_file.read_text(encoding="utf-8"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == class_name:
                locations.append(str(py_file.relative_to(CORTEX_ROOT.parent)))
    return locations


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 1: GAP-107-03 — Synthesis engine CORE-035 compliance
# ─────────────────────────────────────────────────────────────────────────────


class TestSynthesisEngineCORE035:
    """Verify that overlapping synthesis engines are consolidated.

    After consolidation:
    - KnowledgeSynthesisEngine (knowledge/) = canonical for CORTEX+Company knowledge merge
    - SynthesisEngine (tier3/) = retained (different purpose: multi-source query synthesis)
    - KnowledgeSynthesizer (learning/) = retained (different purpose: YAML artifact generation)
    - SynthesisPhase (lens/) = retained (different purpose: LENS pipeline routing phase)
    - LENSSynthesis (domain_brain/) = retained (different purpose: conflict resolution dataclass)

    The key consolidation is that tier3.SynthesisEngine's synthesize() and
    detect_conflicts() capabilities are absorbed into KnowledgeSynthesisEngine.
    """

    def test_knowledge_synthesis_engine_has_synthesize_from_sources(self) -> None:
        """KnowledgeSynthesisEngine must expose synthesize_from_sources() method.

        This absorbs SynthesisEngine(tier3).synthesize() capability into the
        canonical engine, eliminating the need for callers to use the tier3 engine.

        RED: KnowledgeSynthesisEngine does not have synthesize_from_sources().
        GREEN: Add synthesize_from_sources() → KnowledgeSynthesisResult.
        """
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )

        engine = KnowledgeSynthesisEngine()
        assert hasattr(engine, "synthesize_from_sources"), (
            "KnowledgeSynthesisEngine must have synthesize_from_sources() — "
            "this absorbs SynthesisEngine(tier3).synthesize() capability"
        )

    def test_synthesize_from_sources_returns_correct_type(self) -> None:
        """synthesize_from_sources() must return a KnowledgeSynthesisResult.

        Uses the tier3 KnowledgeSynthesisResult dataclass (renamed in Sub-Phase A).

        RED: Method does not exist.
        GREEN: Returns KnowledgeSynthesisResult with synthesized_content.
        """
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )
        from cortex.intelligence.tier3.knowledge.synthesis_engine import (
            KnowledgeSynthesisResult,
        )

        engine = KnowledgeSynthesisEngine()
        result = engine.synthesize_from_sources(
            query="What are the best TDD practices?",
            sources=[
                {"id": "tdd-1", "content": "Write tests first"},
                {"id": "tdd-2", "content": "Use arrange-act-assert pattern"},
            ],
        )
        assert isinstance(result, KnowledgeSynthesisResult), (
            f"Expected KnowledgeSynthesisResult, got {type(result).__name__}"
        )
        assert result.query == "What are the best TDD practices?"
        assert len(result.sources) == 2
        assert result.confidence > 0.0
        assert len(result.synthesized_content) > 0

    def test_synthesize_from_sources_empty_sources(self) -> None:
        """synthesize_from_sources() with empty sources returns zero-confidence result.

        RED: Method does not exist.
        GREEN: Returns graceful empty result.
        """
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )

        engine = KnowledgeSynthesisEngine()
        result = engine.synthesize_from_sources(
            query="anything",
            sources=[],
        )
        assert result.confidence == 0.0
        assert "no sources" in result.synthesized_content.lower() or result.synthesized_content == ""

    def test_knowledge_synthesis_engine_has_detect_conflicts(self) -> None:
        """KnowledgeSynthesisEngine must expose detect_source_conflicts() method.

        This absorbs SynthesisEngine(tier3).detect_conflicts() capability.

        RED: KnowledgeSynthesisEngine does not have detect_source_conflicts().
        GREEN: Add detect_source_conflicts() → List[str].
        """
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )

        engine = KnowledgeSynthesisEngine()
        assert hasattr(engine, "detect_source_conflicts"), (
            "KnowledgeSynthesisEngine must have detect_source_conflicts() — "
            "this absorbs SynthesisEngine(tier3).detect_conflicts() capability"
        )

    def test_detect_source_conflicts_finds_conflicts(self) -> None:
        """detect_source_conflicts() must detect contradictory signals.

        RED: Method does not exist.
        GREEN: Returns list of conflict strings when negation markers are present.
        """
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )

        engine = KnowledgeSynthesisEngine()
        conflicts = engine.detect_source_conflicts(
            sources=[
                {"id": "src-1", "content": "Use TDD for all implementations"},
                {"id": "src-2", "content": "TDD is not required for simple scripts"},
            ]
        )
        assert isinstance(conflicts, list)
        assert len(conflicts) > 0, "Should detect conflict between 'use TDD' and 'not required'"

    def test_detect_source_conflicts_no_conflicts(self) -> None:
        """detect_source_conflicts() with concordant sources returns empty.

        RED: Method does not exist.
        GREEN: Returns empty list.
        """
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )

        engine = KnowledgeSynthesisEngine()
        conflicts = engine.detect_source_conflicts(sources=[
            {"id": "a", "content": "Always write clean code"},
        ])
        assert conflicts == []


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 2: GAP-107-04 — BusinessKnowledgeRepository CORE-035 compliance
# ─────────────────────────────────────────────────────────────────────────────


class TestBusinessKnowledgeRepoCORE035:
    """Verify that duplicate BusinessKnowledgeRepository is consolidated.

    Canonical: cortex/intelligence/knowledge/business_knowledge_repository.py
    Duplicate: cortex/intelligence/domain_brain/business_knowledge_repository.py

    After consolidation, domain_brain version must re-export from knowledge/.
    """

    def test_single_business_knowledge_repository_definition(self) -> None:
        """Exactly 1 BusinessKnowledgeRepository class definition within intelligence/.

        RED: 2 definitions — knowledge/ and domain_brain/.
        GREEN: domain_brain/ re-exports from knowledge/ (compat shim).
        """
        intelligence_root = CORTEX_ROOT / "intelligence"
        locations = _count_class_definitions("BusinessKnowledgeRepository", intelligence_root)

        assert len(locations) == 1, (
            f"CORE-035 violation: {len(locations)} BusinessKnowledgeRepository definitions:\n"
            f"  {locations}\n"
            "Expected exactly 1 in cortex/intelligence/knowledge/business_knowledge_repository.py\n"
            "Fix: domain_brain version → compat shim re-exporting from knowledge/"
        )

    def test_domain_brain_shim_exports_canonical(self) -> None:
        """domain_brain.BusinessKnowledgeRepository IS knowledge.BusinessKnowledgeRepository.

        RED: domain_brain defines its own class (not a shim).
        GREEN: domain_brain re-exports via `from cortex.intelligence.knowledge... import`.
        """
        from cortex.intelligence.domain_brain.business_knowledge_repository import (
            BusinessKnowledgeRepository as ViaDomainBrain,
        )
        from cortex.intelligence.knowledge.business_knowledge_repository import (
            BusinessKnowledgeRepository as ViaKnowledge,
        )

        assert ViaDomainBrain is ViaKnowledge, (
            "domain_brain.BusinessKnowledgeRepository must be the SAME class object "
            "as knowledge.BusinessKnowledgeRepository (compat re-export, not a copy)"
        )

    def test_domain_brain_shim_exports_entry_dataclass(self) -> None:
        """domain_brain.BusinessKnowledgeEntry must still be importable.

        The domain_brain version defines BusinessKnowledgeEntry which has
        no equivalent in knowledge/. It should be moved to knowledge/ or
        kept in domain_brain as a standalone dataclass.

        RED/GREEN: This test verifies the entry dataclass is still importable
        from domain_brain after consolidation.
        """
        from cortex.intelligence.domain_brain.business_knowledge_repository import (
            BusinessKnowledgeEntry,
        )

        assert BusinessKnowledgeEntry is not None
        assert BusinessKnowledgeEntry.__name__ == "BusinessKnowledgeEntry"


# ─────────────────────────────────────────────────────────────────────────────
# GROUP 3: Cross-engine consolidation integrity
# ─────────────────────────────────────────────────────────────────────────────


class TestCrossEngineIntegrity:
    """Verify that the consolidated engine doesn't break existing callers."""

    def test_tier3_synthesis_engine_still_importable(self) -> None:
        """SynthesisEngine from tier3 must still be importable (compat).

        Even after absorbing its capabilities, the class remains importable
        for existing callers (backward compatibility).
        """
        from cortex.intelligence.tier3.knowledge.synthesis_engine import SynthesisEngine

        engine = SynthesisEngine()
        result = engine.synthesize(
            query="test",
            sources=[{"content": "hello"}],
        )
        assert result.synthesized_content  # Still functional

    def test_knowledge_synthesis_engine_synthesize_unified_context_unchanged(self) -> None:
        """synthesize_unified_context() must continue to work as before.

        This is the primary caller path — must not regress.
        """
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import (
            KnowledgeSynthesisEngine,
        )

        engine = KnowledgeSynthesisEngine()
        ctx = engine.synthesize_unified_context(
            intent_type="IMPLEMENT",
            file_path="/test.py",
        )
        assert ctx is not None
        assert ctx.intent_type == "IMPLEMENT"
        assert ctx.file_path == "/test.py"

    def test_knowledge_synthesizer_unchanged(self) -> None:
        """KnowledgeSynthesizer (learning/) must be unaffected by consolidation.

        This engine generates YAML artifacts — completely different purpose.
        """
        from cortex.intelligence.learning.knowledge_synthesizer import (
            KnowledgeSynthesizer,
        )

        synthesizer = KnowledgeSynthesizer.__new__(KnowledgeSynthesizer)
        assert hasattr(synthesizer, "generate_pattern_template")
