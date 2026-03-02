"""Preflight — Sub-phase G (GAP-107-16): MCP registry ↔ tool files alignment gate.

Validates:
  - All MCP tool files in cortex/mcp/tools/ are importable
  - Registered tool count meets minimum threshold (≥29)
  - Each registered tool has a non-empty description and operation list
  - Registry tool IDs are unique (no duplicates)

Phase: Phase 107 Sub-phase G (GAP-107-16)
CORE: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep)
Tier: T0 (preflight) — pure import + registry check, < 10 s total
"""

from __future__ import annotations

import importlib
import importlib.util
from pathlib import Path
from typing import List

import pytest

# ─────────────────────────────────────────────────────────────────────────────
# Paths
# ─────────────────────────────────────────────────────────────────────────────

TOOLS_DIR = Path(__file__).parents[2] / "cortex" / "mcp" / "tools"

# Collect all .py tool files (excluding __init__.py and __pycache__)
TOOL_FILES = sorted(
    f for f in TOOLS_DIR.glob("*.py")
    if f.name not in ("__init__.py",) and not f.name.startswith("_")
)


# ─────────────────────────────────────────────────────────────────────────────
# TestMCPToolFilesImportable
# ─────────────────────────────────────────────────────────────────────────────


class TestMCPToolFilesImportable:
    """Every .py file in cortex/mcp/tools/ must import without error (GAP-107-16)."""

    def test_tool_files_exist(self) -> None:
        """At least 20 tool files exist in cortex/mcp/tools/."""
        assert len(TOOL_FILES) >= 20, (
            f"Expected ≥20 tool files in {TOOLS_DIR}, found {len(TOOL_FILES)}"
        )

    @pytest.mark.parametrize("tool_file", TOOL_FILES, ids=lambda f: f.stem)
    def test_tool_file_importable(self, tool_file: Path) -> None:
        """Each tool .py file can be imported as a module.

        Args:
            tool_file: Absolute path to the tool file.
        """
        module_name = f"cortex.mcp.tools.{tool_file.stem}"
        try:
            importlib.import_module(module_name)
        except ImportError as e:
            pytest.fail(
                f"Tool file '{tool_file.name}' is not importable as "
                f"'{module_name}': {e}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# TestMCPRegistryAlignment
# ─────────────────────────────────────────────────────────────────────────────


class TestMCPRegistryAlignment:
    """MCP registry metadata integrity checks (GAP-107-16)."""

    @pytest.fixture(scope="class")
    def registry(self):
        """Load the MCP tool registry once per test class."""
        from cortex.mcp.mcp_registry import get_registry
        return get_registry()

    def test_registry_minimum_tool_count(self, registry) -> None:
        """Registry has at least 29 registered tools."""
        count = registry.tool_count
        assert count >= 29, (
            f"Expected ≥29 registered tools, got {count}. "
            "Check cortex/mcp/mcp_registry.py for missing registrations."
        )

    def test_registry_tool_ids_unique(self, registry) -> None:
        """All registered tool IDs are unique — no duplicate registrations."""
        all_tools = registry.list_all()
        ids = [t.id for t in all_tools]
        assert len(ids) == len(set(ids)), (
            f"Duplicate tool IDs in registry: "
            f"{[i for i in ids if ids.count(i) > 1]}"
        )

    def test_registry_all_tools_have_description(self, registry) -> None:
        """Every registered tool has a non-empty description string."""
        bad: List[str] = []
        for tool in registry.list_all():
            if not tool.description or not tool.description.strip():
                bad.append(tool.id)
        assert not bad, (
            f"Registered tools missing description: {bad}"
        )

    def test_registry_all_tools_have_operations_or_parameters(self, registry) -> None:
        """Every registered tool has at least one operation OR at least one parameter.

        Some tools are parameter-dispatched rather than operation-dispatched.
        Both forms are valid — but a tool with neither is a misconfiguration.
        """
        bad: List[str] = []
        for tool in registry.list_all():
            has_ops = bool(tool.operations)
            has_params = bool(tool.parameters)
            if not has_ops and not has_params:
                bad.append(tool.id)
        assert not bad, (
            f"Registered tools with neither operations nor parameters: {bad}"
        )

    def test_registry_all_implementations_importable(self, registry) -> None:
        """Every registered tool implementation class is importable and not None."""
        bad: List[str] = []
        for tool in registry.list_all():
            if tool.implementation is None:
                bad.append(f"{tool.id}: implementation is None")
        assert not bad, (
            f"Registered tools with missing implementations:\n"
            + "\n".join(bad)
        )

    def test_registry_list_all_count_matches_tool_count(self, registry) -> None:
        """registry.list_all() length equals registry.tool_count."""
        assert len(registry.list_all()) == registry.tool_count, (
            f"list_all() returned {len(registry.list_all())} tools "
            f"but tool_count reports {registry.tool_count}"
        )
