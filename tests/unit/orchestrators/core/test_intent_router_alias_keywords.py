"""
TDD: Intent Router Alias Keyword Expansion

Verifies that user-facing synonyms and natural-language aliases correctly
route to the expected IntentType via both Tier-1 (regex) and Tier-2/3
(keyword bag / full detect_intent) classifiers.

New aliases added:
  IMPLEMENT triggers: rebuild, rework, stand up, wire up, scaffold,
                      write, make, generate, produce, spin up, bootstrap,
                      port, clone, replicate, assemble, fabricate
  REFACTOR triggers: fix (when used as cleanup/quality), clean up code,
                     tidy, consolidate, decouple, extract, rename,
                     inline, move, split, merge, eliminate duplication
  FIX triggers:      address, remediate, mitigate, root out, squash,
                     debug (bug context), restore, recover, unblock
  VACUUM triggers:   spring clean, declutter, housekeeping, sweep

Authority: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import pytest

from cortex.models.canonical_enums import IntentType


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _classify(text: str) -> IntentType:
    """Run the full three-tier IntentClassifier and return the detected type."""
    from cortex.orchestrators.core.intent_classifier import IntentClassifier
    clf = IntentClassifier()
    result = clf.classify(text)
    return result.intent_type


def _keyword_bags() -> dict:
    """Return the Tier-2 keyword bags from IntentClassifier."""
    from cortex.orchestrators.core.intent_classifier import _KEYWORD_BAGS
    return _KEYWORD_BAGS


def _router_keywords(intent: IntentType) -> list:
    """Return the SSOT keyword list from IntentRouter for an intent."""
    from cortex.orchestrators.core.intent_router_impl import IntentRouter
    router = IntentRouter()
    return router.operation_type_mappings.get(intent, [])


# ---------------------------------------------------------------------------
# Phase 1 — IMPLEMENT aliases
# ---------------------------------------------------------------------------

class TestImplementAliases:
    """New alias triggers that must route to IMPLEMENT."""

    def test_rebuild_routes_to_implement(self) -> None:
        """'rebuild' must route to IMPLEMENT (via Workflow Composer path)."""
        intent = _classify("rebuild the authentication module from scratch")
        assert intent == IntentType.IMPLEMENT, f"Expected IMPLEMENT, got {intent}"

    def test_rework_routes_to_implement(self) -> None:
        """'rework' must route to IMPLEMENT."""
        intent = _classify("rework the notification service")
        assert intent == IntentType.IMPLEMENT, f"Expected IMPLEMENT, got {intent}"

    def test_stand_up_routes_to_implement(self) -> None:
        """'stand up' must route to IMPLEMENT."""
        intent = _classify("stand up a new API gateway")
        assert intent == IntentType.IMPLEMENT, f"Expected IMPLEMENT, got {intent}"

    def test_wire_up_routes_to_implement(self) -> None:
        """'wire up' must route to IMPLEMENT."""
        intent = _classify("wire up the event bus to the orchestrator")
        assert intent == IntentType.IMPLEMENT, f"Expected IMPLEMENT, got {intent}"

    def test_scaffold_routes_to_implement(self) -> None:
        """'scaffold' must route to IMPLEMENT."""
        intent = _classify("scaffold a new MCP tool for the registry")
        assert intent == IntentType.IMPLEMENT, f"Expected IMPLEMENT, got {intent}"

    def test_spin_up_routes_to_implement(self) -> None:
        """'spin up' must route to IMPLEMENT."""
        intent = _classify("spin up a new microservice")
        assert intent == IntentType.IMPLEMENT, f"Expected IMPLEMENT, got {intent}"

    def test_generate_routes_to_implement(self) -> None:
        """'generate' must route to IMPLEMENT."""
        intent = _classify("generate a dashboard component for the registry")
        assert intent == IntentType.IMPLEMENT, f"Expected IMPLEMENT, got {intent}"

    def test_assemble_routes_to_implement(self) -> None:
        """'assemble' must route to IMPLEMENT."""
        intent = _classify("assemble the pipeline from existing primitives")
        assert intent == IntentType.IMPLEMENT, f"Expected IMPLEMENT, got {intent}"

    def test_rebuild_in_implement_keyword_list(self) -> None:
        """'rebuild' must be present in IntentRouterImpl IMPLEMENT_KEYWORDS."""
        keywords = _router_keywords(IntentType.IMPLEMENT)
        assert "rebuild" in keywords, f"'rebuild' missing from IMPLEMENT_KEYWORDS: {keywords}"

    def test_scaffold_in_implement_keyword_list(self) -> None:
        """'scaffold' must be present in IntentRouterImpl IMPLEMENT_KEYWORDS."""
        keywords = _router_keywords(IntentType.IMPLEMENT)
        assert "scaffold" in keywords, f"'scaffold' missing from IMPLEMENT_KEYWORDS: {keywords}"

    def test_rebuild_in_keyword_bag(self) -> None:
        """'rebuild' must be in the Tier-2 IMPLEMENT keyword bag."""
        bags = _keyword_bags()
        assert "rebuild" in bags[IntentType.IMPLEMENT], (
            f"'rebuild' missing from Tier-2 IMPLEMENT bag"
        )


# ---------------------------------------------------------------------------
# Phase 2 — REFACTOR aliases (Fix = Refactor rule)
# ---------------------------------------------------------------------------

class TestRefactorAliases:
    """
    New alias triggers that must route to REFACTOR.

    The user explicitly requested: "Fix = Refactor" — meaning quality-oriented
    fix requests ("clean up", "tidy", "extract", "decouple") should route to
    REFACTOR rather than FIX.  High-priority REFACTOR regex patterns enforce this.
    """

    def test_tidy_routes_to_refactor(self) -> None:
        """'tidy' must route to REFACTOR."""
        intent = _classify("tidy up the orchestrator registration code")
        assert intent == IntentType.REFACTOR, f"Expected REFACTOR, got {intent}"

    def test_consolidate_routes_to_refactor(self) -> None:
        """'consolidate' must route to REFACTOR."""
        intent = _classify("consolidate the duplicate YAML loaders")
        assert intent == IntentType.REFACTOR, f"Expected REFACTOR, got {intent}"

    def test_decouple_routes_to_refactor(self) -> None:
        """'decouple' must route to REFACTOR."""
        intent = _classify("decouple the database layer from the orchestrator")
        assert intent == IntentType.REFACTOR, f"Expected REFACTOR, got {intent}"

    def test_extract_routes_to_refactor(self) -> None:
        """'extract' must route to REFACTOR."""
        intent = _classify("extract the validation logic into its own module")
        assert intent == IntentType.REFACTOR, f"Expected REFACTOR, got {intent}"

    def test_rename_routes_to_refactor(self) -> None:
        """'rename' must route to REFACTOR."""
        intent = _classify("rename the cortex_brain module to cortex_intelligence")
        assert intent == IntentType.REFACTOR, f"Expected REFACTOR, got {intent}"

    def test_split_routes_to_refactor(self) -> None:
        """'split' must route to REFACTOR."""
        intent = _classify("split the master orchestrator into smaller components")
        assert intent == IntentType.REFACTOR, f"Expected REFACTOR, got {intent}"

    def test_inline_routes_to_refactor(self) -> None:
        """'inline' must route to REFACTOR."""
        intent = _classify("inline the one-liner helper into the caller")
        assert intent == IntentType.REFACTOR, f"Expected REFACTOR, got {intent}"

    def test_decouple_in_refactor_keyword_list(self) -> None:
        """'decouple' must be present in IntentRouterImpl REFACTOR_KEYWORDS."""
        keywords = _router_keywords(IntentType.REFACTOR)
        assert "decouple" in keywords, f"'decouple' missing from REFACTOR_KEYWORDS"

    def test_consolidate_in_keyword_bag(self) -> None:
        """'consolidate' must be in the Tier-2 REFACTOR keyword bag."""
        bags = _keyword_bags()
        assert "consolidate" in bags[IntentType.REFACTOR], (
            f"'consolidate' missing from Tier-2 REFACTOR bag"
        )


# ---------------------------------------------------------------------------
# Phase 3 — FIX aliases
# ---------------------------------------------------------------------------

class TestFixAliases:
    """New alias triggers that must route to FIX."""

    def test_address_routes_to_fix(self) -> None:
        """'address' must route to FIX."""
        intent = _classify("address the null pointer exception in the loader")
        assert intent == IntentType.FIX, f"Expected FIX, got {intent}"

    def test_remediate_routes_to_fix(self) -> None:
        """'remediate' must route to FIX."""
        intent = _classify("remediate the security vulnerability in the API")
        assert intent == IntentType.FIX, f"Expected FIX, got {intent}"

    def test_squash_routes_to_fix(self) -> None:
        """'squash' must route to FIX."""
        intent = _classify("squash the regression introduced in the last commit")
        assert intent == IntentType.FIX, f"Expected FIX, got {intent}"

    def test_restore_routes_to_fix(self) -> None:
        """'restore' must route to FIX."""
        intent = _classify("restore the broken pipeline to working state")
        assert intent == IntentType.FIX, f"Expected FIX, got {intent}"

    def test_unblock_routes_to_fix(self) -> None:
        """'unblock' must route to FIX."""
        intent = _classify("unblock the CI pipeline that is stuck on import errors")
        assert intent == IntentType.FIX, f"Expected FIX, got {intent}"

    def test_remediate_in_fix_keyword_list(self) -> None:
        """'remediate' must be present in IntentRouterImpl FIX_KEYWORDS."""
        keywords = _router_keywords(IntentType.FIX)
        assert "remediate" in keywords, f"'remediate' missing from FIX_KEYWORDS"

    def test_squash_in_keyword_bag(self) -> None:
        """'squash' must be in the Tier-2 FIX keyword bag."""
        bags = _keyword_bags()
        assert "squash" in bags[IntentType.FIX], (
            f"'squash' missing from Tier-2 FIX bag"
        )


# ---------------------------------------------------------------------------
# Phase 4 — VACUUM aliases
# ---------------------------------------------------------------------------

class TestVacuumAliases:
    """New alias triggers that must route to VACUUM."""

    def test_housekeeping_routes_to_vacuum(self) -> None:
        """'housekeeping' must route to VACUUM."""
        intent = _classify("run housekeeping on the cortex workspace")
        assert intent == IntentType.VACUUM, f"Expected VACUUM, got {intent}"

    def test_declutter_routes_to_vacuum(self) -> None:
        """'declutter' must route to VACUUM."""
        intent = _classify("declutter the reports directory")
        assert intent == IntentType.VACUUM, f"Expected VACUUM, got {intent}"

    def test_sweep_routes_to_vacuum(self) -> None:
        """'sweep' must route to VACUUM."""
        intent = _classify("sweep and remove all stale markdown files")
        assert intent == IntentType.VACUUM, f"Expected VACUUM, got {intent}"

    def test_housekeeping_in_vacuum_keyword_list(self) -> None:
        """'housekeeping' must be in IntentRouterImpl VACUUM_KEYWORDS."""
        keywords = _router_keywords(IntentType.VACUUM)
        assert "housekeeping" in keywords, f"'housekeeping' missing from VACUUM_KEYWORDS"


# ---------------------------------------------------------------------------
# Phase 5 — IMPLEMENT via Workflow Composer (rebuild special case)
# ---------------------------------------------------------------------------

class TestRebuildRoutesViaWorkflowComposer:
    """
    'rebuild' should prefer IMPLEMENT (not REFACTOR/TOTALRECALL).

    When 'rebuild' appears alongside 'workflow composer' context,
    WORKFLOW_COMPOSE should take priority — test the disambiguation.
    """

    def test_rebuild_alone_is_implement(self) -> None:
        """'rebuild X' with no workflow context → IMPLEMENT."""
        intent = _classify("rebuild the caching layer")
        assert intent == IntentType.IMPLEMENT, f"Expected IMPLEMENT, got {intent}"

    def test_rebuild_with_workflow_composer_is_workflow_compose(self) -> None:
        """'rebuild using workflow composer' → WORKFLOW_COMPOSE takes priority."""
        intent = _classify("rebuild the pipeline using the workflow composer template")
        assert intent == IntentType.WORKFLOW_COMPOSE, (
            f"Expected WORKFLOW_COMPOSE when 'workflow composer' is explicit, got {intent}"
        )
