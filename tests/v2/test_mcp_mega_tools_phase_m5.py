"""Phase M5 tests for MCP mega-tool introduction and legacy alias routing."""

from __future__ import annotations

import asyncio

from cortex.mcp.mcp_registry import (
    LEGACY_MEGATOOL_ALIASES,
    PRODUCTION_TOOLS,
    resolve_legacy_tool_alias,
)
from cortex.mcp.tools.cortex_analyze import CortexAnalyze
from cortex.mcp.tools.cortex_code import CortexCode
from cortex.mcp.tools.cortex_govern import CortexGovern
from cortex.mcp.tools.cortex_learn import CortexLearn
from cortex.mcp.tools.cortex_ops import CortexOps
from cortex.mcp.tools.cortex_plan import CortexPlanMega


def test_m5_mega_tools_registered_in_metadata() -> None:
    """Mega-tool metadata entries exist in registry definitions."""
    expected = {
        "cortex_code",
        "cortex_govern",
        "cortex_analyze",
        "cortex_plan",
        "cortex_learn",
        "cortex_ops",
    }
    assert expected.issubset(set(PRODUCTION_TOOLS.keys()))


def test_cortex_code_allowlist_and_boundary() -> None:
    """cortex_code enforces op allowlist and publishes trust boundary metadata."""
    tool = CortexCode()

    ok = asyncio.run(tool.execute(op="implement", target="cortex/"))
    assert ok.success
    assert ok.data["route"] == "TDDOrchestrator.implement"
    assert ok.metadata["trust_boundary"] == "code-only"

    bad = asyncio.run(tool.execute(op="forbidden"))
    assert not bad.success
    assert "Unsupported op" in (bad.error or "")


def test_cortex_govern_health_route() -> None:
    """cortex_govern routes health operation correctly."""
    result = asyncio.run(CortexGovern().execute(op="health", target="."))
    assert result.success
    assert result.data["route"] == "HealthOrchestrator.health_check"


def test_analyze_plan_learn_ops_execute_known_routes() -> None:
    """Remaining mega-tools return deterministic route mapping for valid operations."""
    analyze = asyncio.run(CortexAnalyze().execute(op="lens", target="."))
    assert analyze.success
    assert analyze.data["route"] == "LensOrchestrator.analyze"

    plan = asyncio.run(CortexPlanMega().execute(op="phase", phase_id="phase-m5"))
    assert plan.success
    assert plan.data["route"] == "PlanningOrchestrator.phase"

    learn = asyncio.run(CortexLearn().execute(op="rca", target="failure-001"))
    assert learn.success
    assert learn.data["route"] == "LearningOrchestrator.rca"

    ops = asyncio.run(CortexOps().execute(op="status", target="workspace"))
    assert ops.success
    assert ops.data["route"] == "OperationsOrchestrator.status"


def test_legacy_alias_resolution_to_mega_tools() -> None:
    """Legacy aliases resolve to target mega-tool and inject default op."""
    tool, params = resolve_legacy_tool_alias("cortex_implement", {})
    assert tool == "cortex_code"
    assert params["op"] == "implement"

    same_tool, same_params = resolve_legacy_tool_alias("cortex_unknown", {"x": 1})
    assert same_tool == "cortex_unknown"
    assert same_params == {"x": 1}


def test_legacy_aliases_collapse_to_six_v2_mega_tools() -> None:
    """All retained legacy aliases point at the canonical six M5 mega-tools."""
    expected_targets = {
        "cortex_analyze",
        "cortex_code",
        "cortex_govern",
        "cortex_learn",
        "cortex_ops",
        "cortex_plan",
    }

    alias_targets = {alias["tool"] for alias in LEGACY_MEGATOOL_ALIASES.values()}

    assert alias_targets == expected_targets


def test_legacy_alias_examples_cover_current_registry_routes() -> None:
    """Former consolidated-tool coverage now lives against mcp_registry alias routing."""
    expectations = {
        "cortex_audit": ("cortex_govern", "audit"),
        "cortex_phase": ("cortex_plan", "phase"),
        "cortex_feedback": ("cortex_learn", "feedback"),
        "cortex_status": ("cortex_ops", "status"),
    }

    for legacy_name, (tool_name, op_name) in expectations.items():
        resolved_tool, resolved_params = resolve_legacy_tool_alias(legacy_name, {})
        assert resolved_tool == tool_name
        assert resolved_params["op"] == op_name
