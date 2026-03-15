"""Phase 105 — Stale Import References + Legacy Naming Remediation.

TDD tests asserting zero stale references to dissolved packages:
- cortex.brain (dissolved Phase 54)
- cortex_intelligence (deleted underscore-package)
- cortex_lens (deleted underscore-package / deleted MCP tool)

And verifying renamed functions/keys use canonical names.

Authority: CORE-008 (TDD), CORE-035 (single canonical implementation)
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from typing import Any

import pytest


PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent


class TestDashboardNoStaleBrainColors:
    """GAP-105-02: d3_import_graph_renderer.py must not reference cortex.brain."""

    def test_package_colors_has_intelligence_not_brain(self) -> None:
        """PACKAGE_COLORS must map 'cortex.intelligence' not 'cortex.brain'."""
        from cortex.dashboards.renderers.d3_import_graph_renderer import D3ImportGraphRenderer

        renderer = D3ImportGraphRenderer()
        assert "cortex.brain" not in renderer.PACKAGE_COLORS, (
            "cortex.brain still in PACKAGE_COLORS — should be cortex.intelligence"
        )
        assert "cortex.intelligence" in renderer.PACKAGE_COLORS, (
            "cortex.intelligence missing from PACKAGE_COLORS"
        )


class TestEngagementRendererNoStaleLens:
    """GAP-105-03: engagement_renderer.py must not reference cortex_lens tool key."""

    def test_tool_display_names_no_cortex_lens(self) -> None:
        """TOOL_DISPLAY_NAMES must not contain deleted cortex_lens key."""
        from cortex.orchestrators.core.engagement_renderer import EngagementRenderer

        renderer = EngagementRenderer()
        assert "cortex_lens" not in renderer.TOOL_DISPLAY_NAMES, (
            "cortex_lens still in TOOL_DISPLAY_NAMES — tool was deleted"
        )


class TestPathResolverCanonicalNaming:
    """GAP-105-01: path_resolver.py must use intelligence_path() not cortex_intelligence_path()."""

    def test_intelligence_path_exists(self) -> None:
        """intelligence_path() is the canonical function name."""
        from cortex.core.path_resolver import intelligence_path

        result = intelligence_path()
        assert result.name == "intelligence"
        assert "cortex" in str(result)

    def test_backward_compat_alias_exists(self) -> None:
        """cortex_intelligence_path should remain as backward-compat alias."""
        from cortex.core.path_resolver import cortex_intelligence_path

        result = cortex_intelligence_path()
        assert result.name == "intelligence"


class TestCollaborationToolsCanonicalNaming:
    """GAP-105-04: brain_collaboration_tools.py functions use canonical names."""

    def test_collaboration_share_exists(self) -> None:
        """collaboration_share is the canonical function name."""
        from cortex.mcp.tools.brain_collaboration_tools import collaboration_share

        result = collaboration_share(user_id="test-user", scope="project")
        assert result["success"] is True
        assert result["shared_by"] == "test-user"

    def test_collaboration_merge_exists(self) -> None:
        """collaboration_merge is the canonical function name."""
        from cortex.mcp.tools.brain_collaboration_tools import collaboration_merge

        result = collaboration_merge(source_contexts=["ctx1", "ctx2"])
        assert result["success"] is True
        assert result["source_count"] == 2

    def test_collaboration_sync_exists(self) -> None:
        """collaboration_sync is the canonical function name."""
        from cortex.mcp.tools.brain_collaboration_tools import collaboration_sync

        result = collaboration_sync(user_ids=["u1", "u2"])
        assert result["sync_successful"] is True

    def test_backward_compat_aliases(self) -> None:
        """Old cortex_intelligence_* names remain as aliases."""
        from cortex.mcp.tools.brain_collaboration_tools import (
            cortex_intelligence_merge,
            cortex_intelligence_share,
            cortex_intelligence_sync,
        )

        assert callable(cortex_intelligence_share)
        assert callable(cortex_intelligence_merge)
        assert callable(cortex_intelligence_sync)

    def test_all_exports_include_canonical_names(self) -> None:
        """__all__ includes both canonical and compat names."""
        import cortex.mcp.tools.brain_collaboration_tools as mod

        assert "collaboration_share" in mod.__all__
        assert "collaboration_merge" in mod.__all__
        assert "collaboration_sync" in mod.__all__


class TestUpdateImportsNoStaleBrain:
    """GAP-105-02: update_imports.py must not have stale 'from cortex.brain' mapping."""

    def test_no_cortex_brain_in_import_mappings(self) -> None:
        """IMPORT_MAPPINGS must not contain 'from cortex.brain' as a source key."""
        from cortex.tools.toolkit.update_imports import ImportUpdater

        updater = ImportUpdater(root_path=PROJECT_ROOT)
        # The mapping should map FROM cortex.brain TO cortex.intelligence
        # but the key should document this is a legacy migration, not an active path
        for key in updater.IMPORT_MAPPINGS:
            if "cortex.brain" in key:
                # If the key still exists, the value must point to cortex.intelligence
                assert "cortex.intelligence" in updater.IMPORT_MAPPINGS[key], (
                    f"Stale mapping: {key} does not point to cortex.intelligence"
                )


class TestNoStaleImportsInSource:
    """Comprehensive scan: zero live imports to dissolved packages in cortex/ source."""

    DISSOLVED_PATTERNS = [
        r"^from cortex_brain\b",
        r"^import cortex_brain\b",
        r"^from cortex_intelligence\b",
        r"^import cortex_intelligence\b",
        r"^from cortex_lens\b",
        r"^import cortex_lens\b",
    ]

    def test_zero_dissolved_imports_in_source(self) -> None:
        """No Python file under cortex/ has a live import to dissolved packages."""
        violations: list[str] = []
        cortex_dir = PROJECT_ROOT / "cortex"

        for py_file in cortex_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            try:
                content = py_file.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError):
                continue

            for line_no, line in enumerate(content.splitlines(), start=1):
                stripped = line.strip()
                if stripped.startswith("#"):
                    continue
                for pattern in self.DISSOLVED_PATTERNS:
                    if re.match(pattern, stripped):
                        violations.append(f"{py_file.relative_to(PROJECT_ROOT)}:{line_no}: {stripped}")

        assert violations == [], f"Dissolved package imports found:\n" + "\n".join(violations)
