"""Phase 137 (Deep Intelligence Wiring) — IntelligenceFacade 4-Method Extension tests.

Covers:
  - GAP-137-03: IntelligenceFacade.threat_assessment(), quality_baseline(),
                guidance(), classify_archetype() extended (sub-phase 137-c)

Note: classify_archetype() already exists from Phase 131. The sub-phase 137-c
adds threat_assessment, quality_baseline, and guidance methods, plus verifies
the singleton is not broken and all expected methods are present.

TDD: RED phase — all tests must FAIL until implementation is complete.
Authority: CORE-008, CORE-011, CORE-012, CORE-035, CORE-064
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import patch

WORKSPACE_ROOT = Path(__file__).resolve().parents[2]


class TestFacadeNewMethods:
    """IntelligenceFacade must expose all 4 new GAP-137-03 methods."""

    def setup_method(self) -> None:
        """Reset singleton before each test."""
        import cortex.intelligence.facade as _f
        _f._SINGLETON_INSTANCE = None

    def test_threat_assessment_method_exists(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        assert hasattr(facade, "threat_assessment"), "facade must have threat_assessment()"

    def test_quality_baseline_method_exists(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        assert hasattr(facade, "quality_baseline"), "facade must have quality_baseline()"

    def test_guidance_method_exists(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        assert hasattr(facade, "guidance"), "facade must have guidance()"


class TestFacadeThreatAssessment:
    """IntelligenceFacade.threat_assessment() delegates and handles null fallback."""

    def setup_method(self) -> None:
        import cortex.intelligence.facade as _f
        _f._SINGLETON_INSTANCE = None

    def test_threat_assessment_returns_dict(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.threat_assessment("cortex/core/engine.py")
        assert isinstance(result, dict)

    def test_threat_assessment_null_fallback(self) -> None:
        """Missing ThreatModelEngine → null-object result, no exception raised."""
        import cortex.intelligence.facade as _f
        _f._SINGLETON_INSTANCE = None
        with patch.dict("sys.modules", {"cortex.intelligence.threat_model_engine": None}):
            from cortex.intelligence.facade import IntelligenceFacade
            facade = IntelligenceFacade()
            # Must not raise even if engine unavailable
            result = facade.threat_assessment("cortex/core/engine.py")
            assert isinstance(result, dict)


class TestFacadeQualityBaseline:
    """IntelligenceFacade.quality_baseline() delegates and handles null fallback."""

    def setup_method(self) -> None:
        import cortex.intelligence.facade as _f
        _f._SINGLETON_INSTANCE = None

    def test_quality_baseline_returns_dict(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.quality_baseline(["cortex/core/engine.py"])
        assert isinstance(result, dict)

    def test_quality_baseline_null_fallback(self) -> None:
        """Missing QualityAnalysisEngine → null-object result, no exception raised."""
        import cortex.intelligence.facade as _f
        _f._SINGLETON_INSTANCE = None
        with patch.dict("sys.modules", {"cortex.intelligence.quality_analysis_engine": None}):
            from cortex.intelligence.facade import IntelligenceFacade
            facade = IntelligenceFacade()
            result = facade.quality_baseline(["cortex/core/engine.py"])
            assert isinstance(result, dict)


class TestFacadeGuidance:
    """IntelligenceFacade.guidance() delegates and handles null fallback."""

    def setup_method(self) -> None:
        import cortex.intelligence.facade as _f
        _f._SINGLETON_INSTANCE = None

    def test_guidance_returns_dict(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        result = facade.guidance("cortex.core.engine")
        assert isinstance(result, dict)

    def test_guidance_null_fallback(self) -> None:
        """Missing KnowledgeGuidanceEngine → null-object result, no exception raised."""
        import cortex.intelligence.facade as _f
        _f._SINGLETON_INSTANCE = None
        with patch.dict("sys.modules", {"cortex.core.knowledge_guidance_engine": None}):
            from cortex.intelligence.facade import IntelligenceFacade
            facade = IntelligenceFacade()
            result = facade.guidance("cortex.core.engine")
            assert isinstance(result, dict)


class TestFacadeSingletonUnbroken:
    """IntelligenceFacade singleton must not be broken by the new methods."""

    def setup_method(self) -> None:
        import cortex.intelligence.facade as _f
        _f._SINGLETON_INSTANCE = None

    def test_facade_remains_singleton(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        a = IntelligenceFacade()
        b = IntelligenceFacade()
        assert a is b, "IntelligenceFacade must remain a singleton"

    def test_get_intelligence_facade_same_instance(self) -> None:
        from cortex.intelligence.facade import get_intelligence_facade
        a = get_intelligence_facade()
        b = get_intelligence_facade()
        assert a is b


class TestFacadeAllMethodsPresent:
    """Facade must expose all expected methods (existing + new)."""

    def setup_method(self) -> None:
        import cortex.intelligence.facade as _f
        _f._SINGLETON_INSTANCE = None

    def test_all_expected_methods_present(self) -> None:
        from cortex.intelligence.facade import IntelligenceFacade
        facade = IntelligenceFacade()
        expected = [
            "analyze",
            "synthesize",
            "query",
            "acquire",
            "invalidate_cache",
            "threat_assessment",
            "quality_baseline",
            "guidance",
            "classify_archetype",
            "load_governance",
            "load_workflows",
            "load_patterns",
        ]
        for method in expected:
            assert hasattr(facade, method), f"facade must have method: {method}"
