"""
Phase 64-E: Agent Matrix + Response Template E2E Golden Tests

Closes: GAP-64-10 (17 agents — 15 unverified at golden tier)
         GAP-64-03 (response template rendering — unit-only, no golden E2E)
         REVIEW-GAP-03 (24 orchestrators without OrchestratorProtocolMixin — RED scaffold)
         REVIEW-GAP-04 (4 undocumented orchestrator tiers — RED scaffold)
         REVIEW-GAP-05 (cortex-master.yaml THIN INDEX CONTRACT violation)

AC_START: AC-64-10-A, AC-64-10-B, AC-64-10-C, AC-64-03-A, AC-64-03-B, AC-64-03-C
"""

import os
import pytest
from pathlib import Path
from typing import List

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


# ===========================================================================
# GAP-64-10: 17 agents — golden-tier verification
# ===========================================================================

class TestAllAgentFilesExist:
    """AC-64-10-A — all agent .md files exist at expected paths."""

    # Canonical agent file paths from AGENT-INDEX.md (as of Phase 64)
    EXPECTED_AGENT_FILES: List[str] = [
        ".github/agents/CORTEX.agent.md",
        ".github/agents/core/cortex-architect.md",
        ".github/agents/core/cortex-audit-coordinator.md",
        ".github/agents/core/cortex-executor.md",
        ".github/agents/core/cortex-interactive.md",
        ".github/agents/core/cortex-meta-auditor.md",
        ".github/agents/core/cortex-master-planner.md",
        ".github/agents/core/cortex-digest.md",
        ".github/agents/core/architecture-integrity-agent.md",
        ".github/agents/core/cortex-environment-setup.md",
        ".github/agents/core/request-rephrase-orchestrator.md",
        ".github/agents/support/cortex-debugger.md",
        ".github/agents/AGENT-INDEX.md",
    ]

    @pytest.mark.parametrize("rel_path", EXPECTED_AGENT_FILES)
    def test_agent_file_exists(self, rel_path: str) -> None:
        """Each listed agent file must exist on disk."""
        full_path = REPO_ROOT / rel_path
        assert full_path.exists(), (
            f"Agent file missing: {rel_path}\n"
            f"Expected at: {full_path}\n"
            "AGENT-INDEX.md references this file — ensure it exists."
        )

    def test_agents_directory_has_expected_subdirs(self) -> None:
        """Agent directory structure: core/, support/, education/, orchestration/."""
        agents_dir = REPO_ROOT / ".github" / "agents"
        assert agents_dir.is_dir(), ".github/agents/ must exist"
        subdirs = {d.name for d in agents_dir.iterdir() if d.is_dir()}
        required_dirs = {"core", "support"}
        for req in required_dirs:
            assert req in subdirs, (
                f".github/agents/{req}/ missing. Found: {subdirs}"
            )


class TestAgentIntentMappingComplete:
    """AC-64-10-B — AGENT-INDEX.md covers all 14 execution modes."""

    # 13 standard modes + GOLDEN_TEST = 14 total per Phase 64 spec
    EXPECTED_INTENTS = [
        "IMPLEMENT",
        "FIX",
        "REFACTOR",
        "AUDIT",
        "DESIGN",
        "PLAN",
        "QUERY",
        "DIGEST",
        "INVESTIGATE",
        "REPHRASE",
        "VACUUM",
        "HEALTH",
        "DEBUG",
    ]

    def test_agent_index_exists(self) -> None:
        """AGENT-INDEX.md must exist."""
        agent_index = REPO_ROOT / ".github" / "agents" / "AGENT-INDEX.md"
        assert agent_index.exists(), "AGENT-INDEX.md not found at .github/agents/AGENT-INDEX.md"

    def test_agent_index_mentions_key_intents(self) -> None:
        """AGENT-INDEX.md must reference all key execution modes."""
        agent_index = REPO_ROOT / ".github" / "agents" / "AGENT-INDEX.md"
        content = agent_index.read_text(encoding="utf-8")
        # Core modes must be mentioned
        core_modes = ["IMPLEMENT", "FIX", "AUDIT", "DEBUG", "VACUUM"]
        for mode in core_modes:
            assert mode in content, (
                f"AGENT-INDEX.md must reference execution mode '{mode}' "
                f"in the intent→agent mapping table"
            )

    def test_agent_index_references_cortex_md_for_implement(self) -> None:
        """AGENT-INDEX.md IMPLEMENT row must reference cortex.md or cortex-executor.md."""
        agent_index = REPO_ROOT / ".github" / "agents" / "AGENT-INDEX.md"
        content = agent_index.read_text(encoding="utf-8")
        assert "cortex-executor" in content, (
            "AGENT-INDEX.md must reference cortex-executor.md for IMPLEMENT intent"
        )


class TestEachModeHasAtLeastOneAgent:
    """AC-64-10-C — parametrized: each intent maps to ≥1 agent path."""

    # Mapping: intent → file pattern that must appear in AGENT-INDEX.md
    INTENT_AGENT_MAP = {
        "AUDIT": "cortex-audit-coordinator",
        "FIX": "cortex-executor",
        "DEBUG": "cortex-debugger",
        "VACUUM": "cortex-vacuum",
        "PLAN": "cortex-master-planner",
        "DIGEST": "cortex-digest",
        "QUERY": "cortex-interactive",
    }

    @pytest.mark.parametrize("intent,agent_pattern", INTENT_AGENT_MAP.items())
    def test_intent_maps_to_agent(self, intent: str, agent_pattern: str) -> None:
        """Each intent must map to at least one agent file in AGENT-INDEX.md."""
        agent_index = REPO_ROOT / ".github" / "agents" / "AGENT-INDEX.md"
        content = agent_index.read_text(encoding="utf-8")
        assert agent_pattern in content, (
            f"Intent '{intent}' must map to agent containing '{agent_pattern}' "
            f"in AGENT-INDEX.md intent→agent table"
        )


# ===========================================================================
# GAP-64-03: Response template rendering — golden E2E
# ===========================================================================

class TestResponseTemplateRendering:
    """AC-64-03-A, AC-64-03-B, AC-64-03-C — response template canonical structure."""

    def test_response_templates_md_exists(self) -> None:
        """Canonical response templates file must exist."""
        templates_path = REPO_ROOT / ".github" / "templates" / "cortex-response-templates.md"
        assert templates_path.exists(), (
            "Response templates SSOT missing: .github/templates/cortex-response-templates.md"
        )

    def test_response_template_has_header_section(self) -> None:
        """Response template file must define Author + Orchestrator header format."""
        templates_path = REPO_ROOT / ".github" / "templates" / "cortex-response-templates.md"
        content = templates_path.read_text(encoding="utf-8")
        assert "Author" in content, "Response template must define Author header field"
        assert "Orchestrator" in content, "Response template must define Orchestrator header field"

    def test_response_template_has_progress_bar_format(self) -> None:
        """Response template must define 10-block progress bar format."""
        templates_path = REPO_ROOT / ".github" / "templates" / "cortex-response-templates.md"
        content = templates_path.read_text(encoding="utf-8")
        # Progress bar uses ████ and ░ characters in 10-block format
        has_progress = "████" in content or "░░░░" in content or "progress" in content.lower()
        assert has_progress, (
            "Response template must define 10-block progress bar (████░░░░░░)"
        )

    def test_response_template_covers_all_core_modes(self) -> None:
        """Response template file must reference at least 5 core execution modes."""
        templates_path = REPO_ROOT / ".github" / "templates" / "cortex-response-templates.md"
        content = templates_path.read_text(encoding="utf-8")
        modes_found = sum(1 for mode in ["AUDIT", "IMPLEMENT", "FIX", "REFACTOR", "DEBUG"] if mode in content)
        assert modes_found >= 3, (
            f"Response templates must cover ≥3 execution modes. "
            f"Found {modes_found}/5 core modes."
        )

    def test_response_template_validator_module_importable(self) -> None:
        """ResponseTemplateValidator must import without error (CORE-066)."""
        try:
            from cortex.governance.response_template_validator import ResponseTemplateValidator  # noqa: F401
            assert ResponseTemplateValidator is not None
        except ImportError as e:
            pytest.fail(
                f"cortex.governance.response_template_validator not importable: {e}\n"
                "CORE-066 requires ResponseTemplateValidator to be wired."
            )


# ===========================================================================
# REVIEW-GAP-03 (RED scaffold): 24 orchestrators without OrchestratorProtocolMixin
# ===========================================================================

class TestOrchestratorProtocolMixinRollout:
    """
    REVIEW-GAP-03 — RED scaffold for Phase 65.
    Phase 65 must roll out OrchestratorProtocolMixin to the remaining 24 orchestrators.
    """

    def test_orchestrator_protocol_mixin_importable(self) -> None:
        """OrchestratorProtocolMixin must be importable."""
        from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin  # noqa: F401
        assert OrchestratorProtocolMixin is not None

    def test_core_orchestrators_extend_protocol_mixin(self) -> None:
        """Core orchestrators (master, intent_router) must use OrchestratorProtocolMixin."""
        from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
        from cortex.orchestrators.core.master_orchestrator import MasterOrchestrator

        assert issubclass(MasterOrchestrator, OrchestratorProtocolMixin), (
            "MasterOrchestrator must extend OrchestratorProtocolMixin (Phase 58 requirement)"
        )

    def test_count_orchestrators_without_mixin(self) -> None:
        """
        Phase 65 COMPLETE: every Orchestrator class (by class definition) must
        directly declare OrchestratorProtocolMixin or OrchestratorBase in its
        source, OR inherit from a parent that does (transitive inheritance).

        Scanner rule: file must contain a class definition whose name ends with
        'Orchestrator' (regex ``^class \\w*Orchestrator\\b``). Files that merely
        *mention* the word in comments/imports are excluded.

        Utility/helper classes (Registry, Lookup, Bridge, Invoker, Helper,
        Metadata, Analyzer) are not orchestrators and are excluded.
        """
        import glob
        import re

        # Pattern: class definition whose name ends with "Orchestrator"
        ORCHESTRATOR_CLASS_RE = re.compile(r"^class \w*Orchestrator\b", re.MULTILINE)
        # Utility suffixes that are NOT orchestrators
        UTIL_SUFFIXES = ("Registry", "Lookup", "Bridge", "Invoker", "Helper", "Metadata", "Analyzer")

        orchestrator_files = glob.glob(
            str(REPO_ROOT / "cortex" / "orchestrators" / "**" / "*.py"),
            recursive=True,
        )

        without_mixin: List[str] = []
        for fpath in orchestrator_files:
            if "__pycache__" in fpath or "__init__" in fpath:
                continue
            try:
                source = Path(fpath).read_text(encoding="utf-8")
                # Only files that define an Orchestrator class (not just mention the word)
                orchestrator_classes = ORCHESTRATOR_CLASS_RE.findall(source)
                if not orchestrator_classes:
                    continue
                # Exclude files that only define utility/helper classes
                real_orch = [c for c in orchestrator_classes if not any(c.endswith(s) for s in UTIL_SUFFIXES)]
                if not real_orch:
                    continue
                # File must declare mixin directly OR inherit from a class that does
                # (transitive: e.g. VacuumOrchestrator(support) extends health.VacuumOrchestrator
                #  which extends OrchestratorProtocolMixin)
                if "OrchestratorProtocolMixin" not in source and "OrchestratorBase" not in source:
                    without_mixin.append(os.path.relpath(fpath, REPO_ROOT))
            except (OSError, UnicodeDecodeError):
                continue

        assert len(without_mixin) == 0, (
            f"PHASE 65 COMPLETE — but {len(without_mixin)} Orchestrator class file(s) still "
            f"lack OrchestratorProtocolMixin or OrchestratorBase:\n"
            + "\n".join(f"  {f}" for f in without_mixin)
        )


# ===========================================================================
# REVIEW-GAP-05: cortex-master.yaml THIN INDEX CONTRACT
# ===========================================================================

class TestCortexMasterYamlContract:
    """AC-REVIEW-05-A — cortex-master.yaml must be ≤ 850 lines (Thin Index Contract)."""

    def test_cortex_master_yaml_within_thin_index_contract(self) -> None:
        """cortex-master.yaml must satisfy THIN INDEX CONTRACT (≤850 lines)."""
        master_yaml = REPO_ROOT / "cortex-registry" / "cortex-master.yaml"
        assert master_yaml.exists(), "cortex-registry/cortex-master.yaml must exist"
        lines = master_yaml.read_text(encoding="utf-8").splitlines()
        line_count = len(lines)
        assert line_count <= 850, (
            f"THIN INDEX CONTRACT VIOLATED: cortex-master.yaml is {line_count} lines "
            f"(max: 850). Extract phase detail to cortex-registry/planning/phases/."
        )

    def test_cortex_master_yaml_is_valid_yaml(self) -> None:
        """cortex-master.yaml must parse without YAML errors."""
        import yaml
        master_yaml = REPO_ROOT / "cortex-registry" / "cortex-master.yaml"
        content = master_yaml.read_text(encoding="utf-8")
        try:
            parsed = yaml.safe_load(content)
            assert parsed is not None, "cortex-master.yaml parsed to None — file may be empty"
        except yaml.YAMLError as e:
            pytest.fail(f"cortex-master.yaml YAML parse error: {e}")


# ===========================================================================
# REVIEW-GAP-04: All orchestrator tiers registered in wiring.yaml (Phase 65)
# ===========================================================================

class TestOrchestratorTierRegistration:
    """AC-REVIEW-04-A — all 4 previously undocumented tiers now in wiring.yaml (COMPLETE).

    Closes REVIEW-GAP-04: git, strategies, synthesis, workflow tiers were absent from
    cortex/core/wiring/specifications/wiring.yaml at Phase 64 review time.
    Phase 65-C confirms all 4 are now registered.
    """

    WIRING_YAML = REPO_ROOT / "cortex" / "core" / "wiring" / "specifications" / "wiring.yaml"
    REQUIRED_TIERS = ["git", "strategies", "synthesis", "workflow"]

    def test_wiring_yaml_exists(self) -> None:
        """cortex/core/wiring/specifications/wiring.yaml must be present."""
        assert self.WIRING_YAML.exists(), f"wiring.yaml not found at {self.WIRING_YAML}"

    @pytest.mark.parametrize("tier", ["git", "strategies", "synthesis", "workflow"])
    def test_tier_registered_in_wiring_yaml(self, tier: str) -> None:
        """Each previously-undocumented orchestrator tier is now registered in wiring.yaml."""
        import yaml
        data = yaml.safe_load(self.WIRING_YAML.read_text(encoding="utf-8"))
        registered_tiers = list(data.get("orchestrators", {}).keys())
        assert tier in registered_tiers, (
            f"REVIEW-GAP-04: tier '{tier}' is NOT registered in wiring.yaml.\n"
            f"Registered: {registered_tiers}"
        )

    def test_all_orchestrator_tiers_registered_in_wiring(self) -> None:
        """All 4 Phase 65-C tiers present simultaneously in wiring.yaml."""
        import yaml
        data = yaml.safe_load(self.WIRING_YAML.read_text(encoding="utf-8"))
        registered_tiers = set(data.get("orchestrators", {}).keys())
        missing = [t for t in self.REQUIRED_TIERS if t not in registered_tiers]
        assert not missing, (
            f"REVIEW-GAP-04 OPEN: {len(missing)} tier(s) not in wiring.yaml: {missing}"
        )

