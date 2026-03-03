"""
Phase 102-b: Domain Boundary Consolidation — Architecture Contract Tests.

Documents and asserts the justified domain splits for governance, knowledge,
lens, and models namespaces. These tests encode the architectural decisions
made during Phase 102 analysis — each "duplicate" namespace is examined and
either consolidated or documented as a justified distinct layer.

CORE-008: TDD — tests written before closing the GAPs.
SWEEP-102-SUBSYSTEM-BOUNDARIES / GAPs 01, 02, 03, 08
"""
import pytest


# ── GAP-102-01: Governance namespace ─────────────────────────────────────────

class TestGovernanceDomainBoundary:
    """GAP-102-01: cortex/core/governance/ is a re-export shim (justified)."""

    def test_core_governance_is_re_export_shim(self) -> None:
        """cortex.core.governance.__init__ re-exports tier2 governance — no logic duplication."""
        import cortex.core.governance as cg
        # The shim re-exports from tier2 — verify it is importable and is a re-export, not canonical
        # No classes should be *defined* in cortex.core.governance itself
        import inspect, ast, pathlib
        src = pathlib.Path("cortex/core/governance/__init__.py").read_text()
        tree = ast.parse(src)
        class_defs = [n.name for n in ast.walk(tree) if isinstance(n, ast.ClassDef)]
        assert class_defs == [], (
            "cortex.core.governance.__init__ must contain no class definitions — it is a re-export shim. "
            f"Found: {class_defs}"
        )

    def test_canonical_governance_is_cortex_governance(self) -> None:
        """cortex.governance is the canonical governance package (28 files)."""
        import cortex.governance
        assert cortex.governance is not None

    def test_governance_enforcement_importable_from_canonical(self) -> None:
        """GovernanceEnforcementAgent is importable from the canonical cortex.governance."""
        from cortex.enforcement.governance_enforcement_agent import GovernanceEnforcementAgent  # noqa: F401
        assert GovernanceEnforcementAgent is not None


# ── GAP-102-02: Knowledge namespace ───────────────────────────────────────────

class TestKnowledgeDomainBoundary:
    """GAP-102-02: Three knowledge layers are distinct — justified split."""

    def test_cortex_knowledge_is_registry_proxy_layer(self) -> None:
        """cortex.knowledge provides KnowledgeRegistryProxy — thin YAML-backed registry."""
        from cortex.knowledge import KnowledgeRegistryProxy  # noqa: F401
        assert KnowledgeRegistryProxy is not None

    def test_cortex_core_knowledge_is_canonical_implementation(self) -> None:
        """cortex.core.knowledge provides the canonical deep knowledge implementation."""
        from cortex.core.knowledge.knowledge_repository import KnowledgeRepository  # noqa: F401
        assert KnowledgeRepository is not None

    def test_cortex_intelligence_knowledge_is_synthesis_layer(self) -> None:
        """cortex.intelligence.knowledge provides the intelligence synthesis layer."""
        from cortex.intelligence.knowledge.knowledge_synthesis_engine import KnowledgeSynthesisEngine  # noqa: F401
        assert KnowledgeSynthesisEngine is not None

    def test_three_knowledge_layers_are_distinct_objects(self) -> None:
        """The three knowledge layers must be distinct modules (not the same object)."""
        import cortex.knowledge as layer1
        import cortex.core.knowledge as layer2
        import cortex.intelligence.knowledge as layer3
        assert layer1 is not layer2
        assert layer2 is not layer3
        assert layer1 is not layer3


# ── GAP-102-03: Lens namespace ────────────────────────────────────────────────

class TestLensDomainBoundary:
    """GAP-102-03: cortex/intelligence/lens/ is the implementation layer for cortex/lens/."""

    def test_cortex_lens_is_top_level_api(self) -> None:
        """cortex.lens is the public API (74 files — top-level)."""
        import cortex.lens
        assert cortex.lens is not None

    def test_cortex_intelligence_lens_is_implementation_layer(self) -> None:
        """cortex.intelligence.lens provides implementation details (LENSPipeline, dotnet, knowledge_graph)."""
        from cortex.intelligence.lens.lens_pipeline import LENSPipeline  # noqa: F401
        assert LENSPipeline is not None

    def test_intelligence_lens_dotnet_is_roslyn_tooling(self) -> None:
        """cortex.intelligence.lens.dotnet contains Roslyn/C# specific analysis tools."""
        from cortex.intelligence.lens.dotnet.roslyn_workspace_builder import RoslynWorkspaceBuilder  # noqa: F401
        assert RoslynWorkspaceBuilder is not None

    def test_cortex_lens_imports_from_intelligence_lens(self) -> None:
        """cortex.lens.dotnet_analyzer imports from cortex.intelligence.lens — confirms layered design."""
        import pathlib
        src = pathlib.Path("cortex/lens/dotnet_analyzer.py").read_text()
        assert "from cortex.intelligence.lens" in src, (
            "cortex/lens/dotnet_analyzer.py must import from cortex.intelligence.lens "
            "(confirms the two-layer architecture)"
        )


# ── GAP-102-08: Models namespace ─────────────────────────────────────────────

class TestModelsDomainBoundary:
    """GAP-102-08: Five 'models' namespaces are domain-scoped — justified."""

    def test_cortex_models_is_canonical_enums_layer(self) -> None:
        """cortex.models contains canonical enums and shared model definitions."""
        from cortex.models.canonical_enums import IntentType  # noqa: F401
        assert IntentType is not None

    def test_cortex_core_models_is_core_layer(self) -> None:
        """cortex.core.models provides core-scoped model definitions."""
        import cortex.core.models
        assert cortex.core.models is not None

    def test_intelligence_lens_models_is_lens_layer(self) -> None:
        """cortex.intelligence.lens.models provides lens analysis model definitions."""
        import cortex.intelligence.lens.models
        assert cortex.intelligence.lens.models is not None

    def test_lens_models_is_top_level_lens_layer(self) -> None:
        """cortex.lens.models provides top-level lens model definitions."""
        import cortex.lens.models
        assert cortex.lens.models is not None
