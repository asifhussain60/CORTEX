"""Phase M3-b V2 tests for IntelligenceFacade simplification and subsystem preservation."""

from __future__ import annotations

from pathlib import Path


def test_facade_core_methods() -> None:
    """IntelligenceFacade core methods stay callable with structured responses."""
    from cortex.intelligence.facade import IntelligenceFacade

    facade = IntelligenceFacade()

    analyze_result = facade.analyze(
        file_path="cortex/intelligence/facade.py",
        intent="INVESTIGATE",
    )
    assert analyze_result.get("status") == "ok"
    assert analyze_result.get("delegation") == "llm-native"

    classify_result = facade.classify_archetype(Path("."))
    assert isinstance(classify_result, dict)
    assert "archetype" in classify_result

    context_result = facade.framework_context()
    assert isinstance(context_result, dict)


def test_facade_governance_methods() -> None:
    """Governance-centric facade methods remain available and typed."""
    from cortex.intelligence.facade import IntelligenceFacade

    facade = IntelligenceFacade()

    governance = facade.load_governance()
    assert isinstance(governance, list)

    patterns = facade.load_patterns()
    assert isinstance(patterns, list)

    plans = facade.load_plans()
    assert hasattr(plans, "phases")

    workflows = facade.load_workflows()
    assert isinstance(workflows, list)


def test_rca_engine_preserved() -> None:
    """RCA engine remains importable with methodology-specific entry points."""
    from cortex.intelligence.learning.rca_engine import RCAEngine

    engine = RCAEngine()
    assert hasattr(engine, "analyze")
    assert hasattr(engine, "analyze_five_whys")
    assert hasattr(engine, "analyze_fishbone")


def test_urs_learning_preserved() -> None:
    """URS operations remain exposed through the learning MCP tool contract."""
    from cortex.mcp.tools.learning_tool import CortexLearning

    ops = next(p for p in CortexLearning().definition.parameters if p.name == "op").enum
    assert ops is not None
    required_ops = {"emit", "history", "decay", "promote", "quarantine", "metrics"}
    assert required_ops.issubset(set(ops))


def test_domain_brain_accessible() -> None:
    """Domain brain API remains importable after intelligence reductions."""
    from cortex.intelligence.domain_brain import DomainBrainAPI

    api = DomainBrainAPI()
    assert api is not None