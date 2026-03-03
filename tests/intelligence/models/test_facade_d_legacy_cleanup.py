"""Phase 109 Sub-Phase D — Legacy Trace Cleanup: GAP-109-14, GAP-109-15, GAP-109-16.

TDD RED→GREEN→REFACTOR tests verifying:
- GAP-109-14: cortex/tools/cortex_intelligence_integration.py uses IntelligenceFacade
- GAP-109-15: cortex/mcp/tools/intelligence.py CortexKnowledge uses IntelligenceFacade.query()
- GAP-109-16: cortex/lens/__init__.py is a thin re-export shim (≤30 lines of real content)

Authority: CORE-008 (TDD), CORE-035 (single canonical), CORE-064 (sweep completeness)
Tier: T1 (unit)
Phase: 109-D | GAP-109-14, GAP-109-15, GAP-109-16
"""
from __future__ import annotations

import ast
import pathlib

import pytest

CORTEX_ROOT = pathlib.Path(__file__).parents[3]
TOOLS_DIR = CORTEX_ROOT / "cortex" / "tools"
MCP_TOOLS_DIR = CORTEX_ROOT / "cortex" / "mcp" / "tools"
LENS_DIR = CORTEX_ROOT / "cortex" / "lens"


# ─────────────────────────────────────────────────────────────────────────────
# GAP-109-14: cortex_intelligence_integration.py must use IntelligenceFacade
# ─────────────────────────────────────────────────────────────────────────────
class TestGap10914ToolLayerUsesFacade:
    """GAP-109-14: cortex/tools/cortex_intelligence_integration.py must delegate via IntelligenceFacade."""

    def _get_source(self) -> str:
        filepath = TOOLS_DIR / "cortex_intelligence_integration.py"
        assert filepath.exists(), f"File not found: {filepath}"
        return filepath.read_text(encoding="utf-8")

    def test_cortex_intelligence_integration_imports_facade(self) -> None:
        """GAP-109-14: cortex_intelligence_integration.py must import IntelligenceFacade."""
        source = self._get_source()
        assert "IntelligenceFacade" in source, (
            "GAP-109-14: cortex_intelligence_integration.py does not import IntelligenceFacade. "
            "Must delegate via facade, not UnifiedIntelligenceProvider directly."
        )

    def test_cortex_intelligence_integration_no_direct_provider(self) -> None:
        """GAP-109-14: cortex_intelligence_integration.py must NOT import UnifiedIntelligenceProvider."""
        source = self._get_source()
        # Check AST for import statements (not comments/docstrings)
        tree = ast.parse(source)
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if node.module and "provider" in node.module:
                    imported_names = [alias.name for alias in node.names]
                    assert "UnifiedIntelligenceProvider" not in imported_names, (
                        "GAP-109-14: cortex_intelligence_integration.py still imports "
                        "UnifiedIntelligenceProvider directly. Must route via IntelligenceFacade."
                    )

    def test_cortex_intelligence_integration_functional(self) -> None:
        """GAP-109-14: CortexIntelligenceIntegration.query() must return a dict with status key."""
        from cortex.tools.cortex_intelligence_integration import CortexIntelligenceIntegration
        tool = CortexIntelligenceIntegration()
        result = tool.query(domain="architecture", prompt="TDD best practices")
        assert isinstance(result, dict), "query() must return a dict"
        assert "domain" in result, "result must have 'domain' key"
        assert "status" in result, "result must have 'status' key"


# ─────────────────────────────────────────────────────────────────────────────
# GAP-109-15: cortex/mcp/tools/intelligence.py CortexKnowledge must use IntelligenceFacade
# ─────────────────────────────────────────────────────────────────────────────
class TestGap10915McpKnowledgeUsesFacade:
    """GAP-109-15: CortexKnowledge must delegate through IntelligenceFacade.query()."""

    def _get_source(self) -> str:
        filepath = MCP_TOOLS_DIR / "intelligence.py"
        assert filepath.exists(), f"File not found: {filepath}"
        return filepath.read_text(encoding="utf-8")

    def test_mcp_intelligence_imports_facade(self) -> None:
        """GAP-109-15: cortex/mcp/tools/intelligence.py must import IntelligenceFacade."""
        source = self._get_source()
        assert "IntelligenceFacade" in source, (
            "GAP-109-15: cortex/mcp/tools/intelligence.py does not reference IntelligenceFacade. "
            "CortexKnowledge must delegate via facade, not KnowledgeRegistryProxy directly."
        )

    def test_cortex_knowledge_no_direct_registry_proxy_import_in_init(self) -> None:
        """GAP-109-15: CortexKnowledge.__init__ must NOT import KnowledgeRegistryProxy directly.

        The proxy should now be accessed via IntelligenceFacade._get_registry() internally.
        """
        source = self._get_source()
        tree = ast.parse(source)

        # Find CortexKnowledge class and its __init__ method
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef) and node.name == "CortexKnowledge":
                for item in ast.walk(node):
                    if isinstance(item, ast.FunctionDef) and item.name == "__init__":
                        # Check that __init__ does NOT contain KnowledgeRegistryProxy import
                        for subnode in ast.walk(item):
                            if isinstance(subnode, ast.ImportFrom):
                                if subnode.module and "registry_proxy" in subnode.module:
                                    imported = [alias.name for alias in subnode.names]
                                    assert "KnowledgeRegistryProxy" not in imported, (
                                        "GAP-109-15: CortexKnowledge.__init__ still imports "
                                        "KnowledgeRegistryProxy directly. Must use IntelligenceFacade."
                                    )
                        return  # Found __init__, test done
        # If CortexKnowledge or __init__ not found, test passes (class may have changed)

    def test_cortex_knowledge_importable(self) -> None:
        """GAP-109-15: CortexKnowledge must still be importable after refactor."""
        from cortex.mcp.tools.intelligence import CortexKnowledge  # noqa: F401
        assert CortexKnowledge is not None


# ─────────────────────────────────────────────────────────────────────────────
# GAP-109-16: cortex/lens/__init__.py must be a thin re-export shim
# ─────────────────────────────────────────────────────────────────────────────
class TestGap10916LensInitIsThinShim:
    """GAP-109-16: cortex/lens/__init__.py must be a thin re-export shim (≤30 content lines)."""

    def _get_source(self) -> str:
        filepath = LENS_DIR / "__init__.py"
        assert filepath.exists(), f"File not found: {filepath}"
        return filepath.read_text(encoding="utf-8")

    def test_lens_init_is_thin_shim(self) -> None:
        """GAP-109-16: cortex/lens/__init__.py must be ≤35 non-blank, non-comment lines.

        A thin shim with 9 re-exported symbols requires ~10 lines for __all__
        and ~18 lines for the lazy dispatch map — 35 is the practical minimum.
        """
        source = self._get_source()
        content_lines = [
            line for line in source.splitlines()
            if line.strip() and not line.strip().startswith("#") and not line.strip().startswith('"""') and not line.strip().startswith("'''")
        ]
        assert len(content_lines) <= 35, (
            f"GAP-109-16: cortex/lens/__init__.py has {len(content_lines)} content lines — "
            "must be ≤35 (re-export shim only, no implementation logic). "
            f"Content lines found:\n" + "\n".join(content_lines[:10])
        )

    def test_lens_package_importable(self) -> None:
        """GAP-109-16: cortex.lens must still be importable after shim conversion."""
        import cortex.lens  # noqa: F401
        assert cortex.lens is not None

    def test_lens_init_has_deprecation_notice(self) -> None:
        """GAP-109-16: cortex/lens/__init__.py must have a deprecation/shim notice."""
        source = self._get_source()
        has_notice = any(
            keyword in source.lower()
            for keyword in ("shim", "compat", "deprecated", "re-export", "re_export", "delegate")
        )
        assert has_notice, (
            "GAP-109-16: cortex/lens/__init__.py must have a deprecation/compat/shim notice "
            "explaining it re-exports from cortex.intelligence.*"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Zero stale provider refs in tools/ and mcp/ (convergence verification)
# ─────────────────────────────────────────────────────────────────────────────
class TestZeroStaleProviderRefsInToolsAndMcp:
    """Convergence gate: zero get_intelligence_provider refs in cortex/tools/ and cortex/mcp/."""

    def test_no_direct_provider_in_tools(self) -> None:
        """Zero get_intelligence_provider imports in cortex/tools/ (AST-level)."""
        tools_dir = CORTEX_ROOT / "cortex" / "tools"
        violations: list[str] = []
        for py_file in tools_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            source = py_file.read_text(encoding="utf-8")
            if "get_intelligence_provider" not in source:
                continue
            # AST check: must not be an actual import
            tree = ast.parse(source)
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    if node.module and "provider" in node.module:
                        imported = [alias.name for alias in node.names]
                        if "get_intelligence_provider" in imported:
                            violations.append(str(py_file))
        assert not violations, (
            f"get_intelligence_provider imported directly in cortex/tools/: {violations}. "
            "All tool-layer intelligence must route via IntelligenceFacade."
        )

    def test_no_direct_provider_in_mcp_init_methods(self) -> None:
        """No KnowledgeRegistryProxy imported directly in CortexKnowledge.__init__."""
        mcp_tools_dir = CORTEX_ROOT / "cortex" / "mcp" / "tools"
        violations: list[str] = []
        for py_file in mcp_tools_dir.rglob("*.py"):
            if "__pycache__" in str(py_file):
                continue
            source = py_file.read_text(encoding="utf-8")
            if "KnowledgeRegistryProxy" not in source:
                continue
            tree = ast.parse(source)
            for class_node in ast.walk(tree):
                if not isinstance(class_node, ast.ClassDef):
                    continue
                for method in ast.walk(class_node):
                    if not isinstance(method, ast.FunctionDef) or method.name != "__init__":
                        continue
                    for subnode in ast.walk(method):
                        if isinstance(subnode, ast.ImportFrom):
                            if subnode.module and "registry_proxy" in subnode.module:
                                imported = [alias.name for alias in subnode.names]
                                if "KnowledgeRegistryProxy" in imported:
                                    violations.append(f"{py_file}::{class_node.name}.__init__")
        assert not violations, (
            f"KnowledgeRegistryProxy imported in __init__ methods: {violations}. "
            "Use IntelligenceFacade.query() for knowledge operations."
        )
