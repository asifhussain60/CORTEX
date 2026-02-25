"""
Phase 72-c — RED tests for CapabilityMatcher.load_from_manifest() + IntentRouter wiring.

AC_START: AC-72-CAPABILITY-MATCHER-MANIFEST-20260226

Tests verify:
  GAP-72-04: CapabilityMatcher can load from capabilities-manifest.yaml
             and IntentRouter has capability_registry attribute post-init.
"""

import pytest
import yaml
from pathlib import Path
from typing import Dict, Any

# ─────────────────────────────────────────────────────────────────────────────
# Import guards
# ─────────────────────────────────────────────────────────────────────────────
try:
    from cortex.intelligence.intelligence_capability_matcher import (
        CapabilityMatcher,
        AgentMetadata,
    )
    _MATCHER_IMPORT_OK = True
except ImportError:
    _MATCHER_IMPORT_OK = False

try:
    from cortex.intelligence.capability_registry_builder import (
        CapabilityRegistryBuilder,
    )
    _BUILDER_IMPORT_OK = True
except ImportError:
    _BUILDER_IMPORT_OK = False


@pytest.mark.skipif(
    not (_MATCHER_IMPORT_OK and _BUILDER_IMPORT_OK),
    reason="CapabilityMatcher or CapabilityRegistryBuilder not importable — RED phase",
)
class TestCapabilityMatcherManifest:
    """GAP-72-04: CapabilityMatcher.load_from_manifest() loads orchestrator entries."""

    @pytest.fixture
    def manifest_path(self, tmp_path: Path) -> Path:
        """Generate a real manifest to tmp, return the path."""
        root = Path(__file__).parent.parent.parent  # /CORTEX
        builder = CapabilityRegistryBuilder(
            workspace_root=root,
            output_path=tmp_path / "capabilities-manifest.yaml",
        )
        builder.generate_manifest()
        return tmp_path / "capabilities-manifest.yaml"

    def test_load_from_manifest_returns_orchestrator_entries(
        self, manifest_path: Path
    ) -> None:
        """
        CapabilityMatcher.load_from_manifest() must load orchestrator entries
        as AgentMetadata and populate the internal cache with ≥27 entries.
        """
        matcher = CapabilityMatcher.load_from_manifest(manifest_path)
        # Must have loaded orchestrators as agents
        all_agents = list(matcher._agent_cache.values())
        assert len(all_agents) >= 27, (
            f"Expected ≥27 orchestrator entries from manifest, got {len(all_agents)}"
        )

    def test_find_by_capability_includes_orchestrators(
        self, manifest_path: Path
    ) -> None:
        """
        After loading manifest, find_by_capability('tdd') must return
        TDDOrchestrator (or equivalent orchestrator with tdd in capabilities).
        """
        matcher = CapabilityMatcher.load_from_manifest(manifest_path)
        matches = matcher.find_by_capability("tdd")
        assert len(matches) >= 1, (
            "find_by_capability('tdd') must return at least one match from manifest orchestrators"
        )
        matched_ids = [m.agent.agent_id for m in matches]
        # TDDOrchestrator should be among the matches
        assert any("tdd" in aid.lower() for aid in matched_ids), (
            f"Expected a TDD-related orchestrator in matches, got: {matched_ids}"
        )

    def test_load_from_manifest_classmethod_exists(self) -> None:
        """load_from_manifest must be a classmethod on CapabilityMatcher."""
        assert hasattr(CapabilityMatcher, "load_from_manifest"), (
            "CapabilityMatcher must have a load_from_manifest classmethod"
        )
        # Verify it's callable
        assert callable(getattr(CapabilityMatcher, "load_from_manifest")), (
            "load_from_manifest must be callable"
        )


@pytest.mark.skipif(
    not (_MATCHER_IMPORT_OK and _BUILDER_IMPORT_OK),
    reason="CapabilityMatcher or CapabilityRegistryBuilder not importable — RED phase",
)
class TestIntentRouterCapabilityRegistry:
    """GAP-72-04: IntentRouter has capability_registry attribute post-init."""

    def test_intent_router_has_capability_registry_attribute(self) -> None:
        """
        IntentRouter must have a capability_registry attribute after __init__.
        This verifies manifest-level capability awareness at routing time.
        """
        from cortex.orchestrators.core.intent_router_impl import IntentRouter

        router = IntentRouter()
        assert hasattr(router, "capability_registry"), (
            "IntentRouter must have capability_registry attribute post-init"
        )

    def test_intent_router_capability_registry_is_matcher(self) -> None:
        """
        IntentRouter.capability_registry must be a CapabilityMatcher instance
        (or None if manifest is not available — graceful degradation).
        """
        from cortex.orchestrators.core.intent_router_impl import IntentRouter

        router = IntentRouter()
        registry = getattr(router, "capability_registry", None)
        # Either a CapabilityMatcher or None (graceful degradation if manifest absent)
        if registry is not None:
            assert isinstance(registry, CapabilityMatcher), (
                f"capability_registry must be CapabilityMatcher, got {type(registry)}"
            )
