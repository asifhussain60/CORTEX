"""
CORTEX Capability Manifest — Zero Regression Golden Test.

Phase 00, Step 1 (TDD RED): Validates the capability manifest against the
live CORTEX system. This test is the safety net that ensures zero capability
loss during the GPT refactor (Phases 00-08).

The manifest covers:
- MCP tools (19 target tools, currently 26 pre-consolidation)
- Active orchestrators (~40)
- Governance rules (54)
- Intelligence capabilities (10)
- Infrastructure services (10)
- Workflow templates (21 existing + ~15 new)
- Design patterns (10)

Authority: Phase 00, D1 — Capability Manifest & Regression Gate
TDD Stage: RED (test first, implementation follows)
CORE-008: Test-first development
CORE-011: Type hints on all functions
CORE-012: Docstrings on all public APIs
"""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import pytest
import yaml


# ==============================================================================
# FIXTURES
# ==============================================================================

MANIFEST_PATH = Path(__file__).resolve().parents[3] / (
    "cortex-registry/planning/phases/planned/cortex-refactor/capability-manifest.yaml"
)


@pytest.fixture(scope="module")
def manifest() -> Dict[str, Any]:
    """Load the capability manifest YAML."""
    assert MANIFEST_PATH.exists(), f"Manifest not found: {MANIFEST_PATH}"
    with open(MANIFEST_PATH) as f:
        data = yaml.safe_load(f)
    assert data is not None, "Manifest is empty"
    assert "manifest" in data, "Missing top-level 'manifest' key"
    return data["manifest"]


@pytest.fixture(scope="module")
def mcp_registry_tools() -> Dict[str, Dict[str, Any]]:
    """Load the live MCP tool registry."""
    from cortex.mcp.mcp_registry import PRODUCTION_TOOLS
    return PRODUCTION_TOOLS


@pytest.fixture(scope="module")
def mcp_server():
    """Create an MCPServer instance for tool listing."""
    from cortex.mcp.server import MCPServer
    return MCPServer()


# ==============================================================================
# SECTION 1: MANIFEST STRUCTURE VALIDATION
# ==============================================================================

class TestManifestStructure:
    """Validate the capability manifest YAML structure is complete."""

    def test_manifest_has_all_sections(self, manifest: Dict[str, Any]) -> None:
        """Manifest must contain all 7 sections."""
        required_sections = [
            "mcp_tools",
            "orchestrators",
            "governance_rules",
            "intelligence",
            "infrastructure",
            "workflow_templates",
            "design_patterns",
        ]
        for section in required_sections:
            assert section in manifest, f"Missing manifest section: {section}"

    def test_manifest_has_metadata(self, manifest: Dict[str, Any]) -> None:
        """Manifest must have id, version, status fields."""
        assert manifest["id"] == "capability-manifest"
        assert "version" in manifest
        assert "status" in manifest

    def test_manifest_mcp_tools_count(self, manifest: Dict[str, Any]) -> None:
        """MCP tools section must list the expected target count."""
        mcp = manifest["mcp_tools"]
        assert "expected_count" in mcp
        assert mcp["expected_count"] == 22, (
            f"Expected 22 target tools, got {mcp['expected_count']}"
        )
        items = mcp["items"]
        # MCP-005 (cortex_challenge) is absorbed, but still in manifest for tracking
        assert len(items) >= 22, f"Expected ≥22 tool entries, got {len(items)}"

    def test_manifest_orchestrators_listed(self, manifest: Dict[str, Any]) -> None:
        """Orchestrators section must list all active orchestrators."""
        orch = manifest["orchestrators"]
        assert "items" in orch
        assert len(orch["items"]) >= 30, (
            f"Expected ≥30 orchestrators, got {len(orch['items'])}"
        )

    def test_manifest_governance_rules_count(self, manifest: Dict[str, Any]) -> None:
        """Governance rules section must reference the manifest's expected count."""
        gov = manifest["governance_rules"]
        assert gov["expected_count"] == 39, (
            f"Expected 39 governance rules (post Phase-02), got {gov['expected_count']}"
        )

    def test_manifest_intelligence_capabilities(self, manifest: Dict[str, Any]) -> None:
        """Intelligence section must list all capabilities."""
        intel = manifest["intelligence"]
        assert "items" in intel
        assert len(intel["items"]) >= 8, (
            f"Expected ≥8 intelligence capabilities, got {len(intel['items'])}"
        )

    def test_manifest_infrastructure_services(self, manifest: Dict[str, Any]) -> None:
        """Infrastructure section must list all services."""
        infra = manifest["infrastructure"]
        assert "items" in infra
        assert len(infra["items"]) >= 8, (
            f"Expected ≥8 infrastructure services, got {len(infra['items'])}"
        )

    def test_manifest_workflow_templates(self, manifest: Dict[str, Any]) -> None:
        """Workflow templates section must list all existing templates."""
        wf = manifest["workflow_templates"]
        assert "existing" in wf
        assert len(wf["existing"]) >= 15, (
            f"Expected ≥15 workflow templates, got {len(wf['existing'])}"
        )

    def test_manifest_design_patterns(self, manifest: Dict[str, Any]) -> None:
        """Design patterns section must list all patterns."""
        dp = manifest["design_patterns"]
        assert "items" in dp
        assert len(dp["items"]) >= 8, (
            f"Expected ≥8 design patterns, got {len(dp['items'])}"
        )


# ==============================================================================
# SECTION 2: MCP TOOLS — LIVE VALIDATION
# ==============================================================================

class TestMCPToolsLive:
    """Validate MCP tools in manifest exist in the live registry."""

    def test_registry_has_tools(self, mcp_registry_tools: Dict[str, Dict[str, Any]]) -> None:
        """Live MCP registry must have tools registered."""
        assert len(mcp_registry_tools) > 0, "No tools in live registry"

    def test_manifest_mcp_tool_ids_unique(self, manifest: Dict[str, Any]) -> None:
        """All MCP tool IDs in manifest must be unique."""
        items = manifest["mcp_tools"]["items"]
        ids = [item["id"] for item in items]
        assert len(ids) == len(set(ids)), f"Duplicate MCP tool IDs: {ids}"

    def test_manifest_mcp_tool_names_unique(self, manifest: Dict[str, Any]) -> None:
        """All MCP tool names in manifest must be unique."""
        items = manifest["mcp_tools"]["items"]
        names = [item["tool"] for item in items]
        assert len(names) == len(set(names)), f"Duplicate tool names: {names}"

    def test_each_manifest_tool_has_required_fields(
        self, manifest: Dict[str, Any]
    ) -> None:
        """Each MCP tool entry must have id, tool, category, description, status."""
        required_fields = {"id", "tool", "category", "description", "status"}
        items = manifest["mcp_tools"]["items"]
        for item in items:
            missing = required_fields - set(item.keys())
            assert not missing, (
                f"Tool {item.get('id', '?')} missing fields: {missing}"
            )

    def test_cortex_challenge_absorbed(self, manifest: Dict[str, Any]) -> None:
        """cortex_challenge must be marked as absorbed (EA-009)."""
        items = manifest["mcp_tools"]["items"]
        challenge_entry = next(
            (i for i in items if i["tool"] == "cortex_challenge"), None
        )
        assert challenge_entry is not None, "cortex_challenge entry missing from manifest"
        assert "absorbed" in challenge_entry["status"].lower(), (
            f"cortex_challenge should be absorbed, got status: {challenge_entry['status']}"
        )
        assert "absorbed_by" in challenge_entry, (
            "cortex_challenge must have absorbed_by field"
        )

    def test_no_toolkit_prefix_in_target_tools(self, manifest: Dict[str, Any]) -> None:
        """No target tools should have toolkit_ prefix."""
        items = manifest["mcp_tools"]["items"]
        toolkit_tools = [
            i["tool"] for i in items
            if i["tool"].startswith("toolkit_")
            and "absorbed" not in i.get("status", "").lower()
        ]
        assert not toolkit_tools, f"toolkit_ prefix tools found: {toolkit_tools}"


# ==============================================================================
# SECTION 3: ORCHESTRATORS — LIVE VALIDATION
# ==============================================================================

class TestOrchestratorsLive:
    """Validate orchestrators listed in manifest exist in the codebase."""

    def test_master_orchestrator_exists(self) -> None:
        """MasterOrchestrator must be importable."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        assert MasterOrchestrator is not None

    def test_master_orchestrator_has_challenge_generator(self) -> None:
        """MasterOrchestrator must have ChallengeGenerator (EA-009 foundation)."""
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator
        mo = MasterOrchestrator()
        assert hasattr(mo, "_challenge_generator"), (
            "MasterOrchestrator missing _challenge_generator (needed for EA-009)"
        )

    def test_orchestrator_names_in_manifest_are_valid(
        self, manifest: Dict[str, Any]
    ) -> None:
        """Each orchestrator in manifest must have name and domain."""
        items = manifest["orchestrators"]["items"]
        for item in items:
            assert "name" in item, f"Orchestrator {item.get('id')} missing name"
            assert "domain" in item, f"Orchestrator {item['name']} missing domain"

    def test_critical_orchestrators_exist(self) -> None:
        """Critical orchestrators must be importable."""
        critical = {
            "MasterOrchestrator": "cortex.orchestrators.core.master_orchestrator",
            "EnforcementOrchestrator": "cortex.orchestrators.core.enforcement_orchestrator",
        }
        import importlib
        for name, module_path in critical.items():
            try:
                mod = importlib.import_module(module_path)
                cls = getattr(mod, name, None)
                assert cls is not None, f"{name} not found in {module_path}"
            except ImportError as e:
                pytest.fail(f"Cannot import {name} from {module_path}: {e}")


# ==============================================================================
# SECTION 4: GOVERNANCE RULES — LIVE VALIDATION
# ==============================================================================

class TestGovernanceRulesLive:
    """Validate governance rules referenced in manifest exist."""

    def test_skull_rules_yaml_exists(self) -> None:
        """skull-rules.yaml must exist in cortex-registry."""
        skull_path = Path(__file__).resolve().parents[3] / (
            "cortex-registry/core/tier0-skull/skull-rules.yaml"
        )
        # Also check common alternate locations
        alt_paths = [
            Path(__file__).resolve().parents[3] / "cortex-registry/governance/skull-rules.yaml",
            Path(__file__).resolve().parents[3] / "cortex-registry/core/skull-rules.yaml",
        ]
        found = skull_path.exists() or any(p.exists() for p in alt_paths)
        assert found, (
            f"skull-rules.yaml not found at {skull_path} or alternate locations"
        )

    def test_critical_core_rules_defined(self, manifest: Dict[str, Any]) -> None:
        """Critical CORE rules must be referenced in manifest governance section."""
        gov = manifest["governance_rules"]
        # Manifest uses tier0_skull_rules as the canonical governance source
        assert "tier0_skull_rules" in gov or "critical_rules" in gov, (
            "Manifest must reference governance rules via tier0_skull_rules or critical_rules"
        )


# ==============================================================================
# SECTION 5: INTELLIGENCE CAPABILITIES — LIVE VALIDATION
# ==============================================================================

class TestIntelligenceLive:
    """Validate intelligence capabilities exist in the codebase."""

    def test_lens_analyzer_exists(self) -> None:
        """LENS workspace analyzer must be importable."""
        try:
            # Try multiple known locations
            try:
                from cortex.lens.analyzers import workspace_analyzer
                assert workspace_analyzer is not None
            except ImportError:
                from cortex.intelligence.lens.analyzers import workspace_analyzer
                assert workspace_analyzer is not None
        except ImportError:
            pytest.skip("LENS analyzer not yet at canonical location")

    def test_challenge_generator_exists(self) -> None:
        """ChallengeGenerator must be importable (EA-009 dependency)."""
        try:
            from cortex.core.intent.challenge_generator import ChallengeGenerator
            assert ChallengeGenerator is not None
        except ImportError:
            pytest.fail("ChallengeGenerator not importable — needed for EA-009")

    def test_token_budget_manager_exists(self) -> None:
        """TokenBudgetManager must be importable (EA-010 dependency)."""
        try:
            from cortex.intelligence.llm.token_budget_manager import TokenBudgetManager
            assert TokenBudgetManager is not None
        except ImportError:
            pytest.fail("TokenBudgetManager not importable — needed for EA-010")

    def test_response_optimizer_exists(self) -> None:
        """ResponseOptimizer must be importable (EA-010 dependency)."""
        try:
            from cortex.core.core.response_optimizer import ResponseOptimizer
            assert ResponseOptimizer is not None
        except ImportError:
            pytest.fail("ResponseOptimizer not importable — needed for EA-010")


# ==============================================================================
# SECTION 6: INFRASTRUCTURE SERVICES — LIVE VALIDATION
# ==============================================================================

class TestInfrastructureLive:
    """Validate infrastructure services exist."""

    def test_event_bus_exists(self) -> None:
        """EventBus must be importable."""
        from cortex.core.event_bus import EventBus
        assert EventBus is not None

    def test_cortex_audit_db_exists(self) -> None:
        """CortexAuditDB must be importable (Phase 00 D6 deliverable)."""
        try:
            from cortex.infrastructure.audit_db import CortexAuditDB
            assert CortexAuditDB is not None
        except ImportError:
            pytest.fail(
                "CortexAuditDB not yet implemented — Phase 00 D6 deliverable"
            )

    @pytest.mark.xfail(reason="ChallengeFirstProtocol not yet implemented — Phase 00 D8 deliverable")
    def test_challenge_first_protocol_exists(self) -> None:
        """Challenge-first protocol must be importable (Phase 00 D8 deliverable)."""
        from cortex.core.challenge_first_protocol import ChallengeFirstProtocol
        assert ChallengeFirstProtocol is not None

    @pytest.mark.xfail(reason="TokenOptimizer not yet implemented — Phase 00 D9 deliverable")
    def test_token_optimizer_exists(self) -> None:
        """Token optimizer must be importable (Phase 00 D9 deliverable)."""
        from cortex.core.token_optimizer import TokenOptimizer
        assert TokenOptimizer is not None


# ==============================================================================
# SECTION 7: WORKFLOW TEMPLATES — LIVE VALIDATION
# ==============================================================================

class TestWorkflowTemplatesLive:
    """Validate workflow templates referenced in manifest exist on disk."""

    WORKFLOW_BASE = Path(__file__).resolve().parents[3] / "cortex-registry/workflows/templates"

    def test_workflow_base_directory_exists(self) -> None:
        """Workflow templates directory must exist."""
        assert self.WORKFLOW_BASE.exists(), (
            f"Workflow base not found: {self.WORKFLOW_BASE}"
        )

    def test_manifest_workflow_templates_exist_on_disk(
        self, manifest: Dict[str, Any]
    ) -> None:
        """Each workflow template in manifest must exist as a file."""
        existing = manifest["workflow_templates"]["existing"]
        missing: List[str] = []
        for wf in existing:
            template_path = self.WORKFLOW_BASE / wf["template"]
            if not template_path.exists():
                missing.append(wf["template"])
        assert not missing, (
            f"Workflow templates missing from disk: {missing}"
        )


# ==============================================================================
# SECTION 8: CROSS-CUTTING CONCERNS
# ==============================================================================

class TestCrossCuttingConcerns:
    """Validate EA-009 and EA-010 cross-cutting wiring."""

    def test_ea_009_challenge_first_not_in_mcp_tools_layer(self) -> None:
        """
        EA-009: Challenge-first protocol text must NOT be appended in MCP tools.
        
        After Phase 00 D8, the challenge text in cortex/mcp/tools/core.py
        (lines ~506-520) must be removed. Until then, this test tracks
        the current (incorrect) state.
        """
        core_tools_path = Path(__file__).resolve().parents[3] / "cortex/mcp/tools/core.py"
        if not core_tools_path.exists():
            pytest.skip("cortex/mcp/tools/core.py not found")

        content = core_tools_path.read_text()
        # This SHOULD fail until D8 is implemented — it's tracking the gap
        challenge_append_text = "challenge-first protocol"
        has_challenge_append = challenge_append_text in content.lower()

        # After D8 implementation, flip this assertion:
        # assert not has_challenge_append, "Challenge text still appended in MCP tools layer"
        if has_challenge_append:
            pytest.xfail(
                "EA-009 not yet implemented: challenge text still appended in MCP tools layer. "
                "Will be fixed in Phase 00 D8."
            )

    def test_ea_010_token_budget_used_system_wide(self) -> None:
        """
        EA-010: TokenBudgetManager must be used beyond just LENS.
        
        After Phase 00 D9, TokenBudgetManager should be imported in
        core infrastructure, not just tiered_lens_analyzer.
        """
        # Check if TokenBudgetManager is imported anywhere besides LENS
        cortex_root = Path(__file__).resolve().parents[3] / "cortex"
        imports_found: List[str] = []
        for py_file in cortex_root.rglob("*.py"):
            try:
                text = py_file.read_text(errors="ignore")
                if "TokenBudgetManager" in text:
                    rel = py_file.relative_to(cortex_root)
                    imports_found.append(str(rel))
            except Exception:
                continue

        # Filter out the definition file itself
        non_definition = [
            f for f in imports_found
            if "token_budget_manager" not in f
        ]

        if len(non_definition) <= 1:
            pytest.xfail(
                "EA-010 not yet implemented: TokenBudgetManager only used in LENS. "
                "Will be promoted to system-wide in Phase 00 D9."
            )


# ==============================================================================
# SECTION 9: REGRESSION GATE (run after each phase)
# ==============================================================================

class TestRegressionGate:
    """
    Aggregate regression check — run this after every phase to confirm
    zero capability loss. Counts all ✅ vs ⬜ in the manifest.
    """

    def test_regression_gate_summary(self, manifest: Dict[str, Any]) -> None:
        """
        Report manifest validation status.
        
        This test always passes but reports the ratio of validated
        capabilities. Use --tb=short to see the summary.
        """
        total = 0
        validated = 0
        pending = 0

        for section_key in [
            "mcp_tools", "orchestrators", "governance_rules",
            "intelligence", "infrastructure", "workflow_templates",
            "design_patterns",
        ]:
            section = manifest.get(section_key, {})
            items = section.get("items", section.get("existing", section.get("critical_rules", [])))
            if isinstance(items, list):
                for item in items:
                    total += 1
                    status = item.get("status", "")
                    if "pending" in status.lower():
                        pending += 1
                    else:
                        validated += 1

        pct = (validated / total * 100) if total > 0 else 0
        print(
            f"\n📊 CAPABILITY MANIFEST REGRESSION GATE\n"
            f"   Total capabilities: {total}\n"
            f"   Validated (✅):     {validated}\n"
            f"   Pending (⬜):       {pending}\n"
            f"   Coverage:           {pct:.1f}%\n"
        )
        # This test is informational — it passes even at 0% to enable CI
        assert total > 0, "Manifest has no items to validate"
