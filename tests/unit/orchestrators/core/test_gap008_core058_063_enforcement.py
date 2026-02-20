# AC_START: AC-GAP-008
"""
Tests for GAP-008: CORE-058..063 enforcement via ExtendedGovernanceAgent.

TDD Phase: RED → GREEN (CORE-008 mandate)

Test Coverage:
    - ExtendedGovernanceAgent class exists (1 test)
    - CORE-058: SQLite WAL mode check (3 tests)
    - CORE-059: MCP footprint logging check (2 tests)
    - CORE-060: SDLC brain governance check (2 tests)
    - CORE-062: Plan-first execution check (3 tests)
    - CORE-063: Challenge-first gate check (2 tests)
    - EnforcementOrchestrator includes ExtendedGovernanceAgent (2 tests)

Total: 15 tests

Authority:
    - cortex-registry/planning/cortex-refactor-master.yaml (GAP-008)
    - cortex/governance/governance_alignment_phase_2.py (CORE-058..063 definitions)

Governance:
    - CORE-008: TDD mandatory — RED first
    - CORE-011: Type hints on all functions
    - CORE-012: Docstrings on all public APIs
    - CORE-062: Plan-first execution (this file is the plan artifact)

Author: Asif Hussain
Date: 2026-02-20
"""

import pytest

from cortex.orchestrators.core.enforcement_orchestrator import (
    EnforcementOrchestrator,
    EnforcementLevel,
    EnforcementResult,
    ExtendedGovernanceAgent,
)


class TestExtendedGovernanceAgentExists:
    """CORE-058..063: ExtendedGovernanceAgent must be importable and instantiable."""

    def test_extended_governance_agent_is_importable(self) -> None:
        """ExtendedGovernanceAgent must be importable from enforcement_orchestrator."""
        agent = ExtendedGovernanceAgent()
        assert agent is not None

    def test_extended_governance_agent_has_validate_method(self) -> None:
        """ExtendedGovernanceAgent must have a validate() method."""
        agent = ExtendedGovernanceAgent()
        assert hasattr(agent, "validate")
        assert callable(agent.validate)

    def test_extended_governance_agent_covers_all_six_rules(self) -> None:
        """ExtendedGovernanceAgent.rules must include CORE-058 through CORE-063."""
        agent = ExtendedGovernanceAgent()
        required = {"CORE-058", "CORE-059", "CORE-060", "CORE-061", "CORE-062", "CORE-063"}
        assert required.issubset(set(agent.rules)), (
            f"Missing rules: {required - set(agent.rules)}"
        )


class TestCore058SqliteWalMode:
    """CORE-058: SQLite WAL mode mandatory enforcement."""

    def test_no_violation_when_wal_mode_enabled(self) -> None:
        """CORE-058: context with wal_mode_enabled=True must not produce violation."""
        agent = ExtendedGovernanceAgent()
        context = {"sqlite_db_paths": [".cortex-runtime/audit.db"], "wal_mode_enabled": True}
        result = agent.validate(context)
        core058_violations = [v for v in result.violations if "CORE-058" in v]
        assert len(core058_violations) == 0

    def test_violation_when_wal_mode_disabled(self) -> None:
        """CORE-058: context with wal_mode_enabled=False and sqlite_db_paths must produce violation."""
        agent = ExtendedGovernanceAgent()
        context = {"sqlite_db_paths": [".cortex-runtime/audit.db"], "wal_mode_enabled": False}
        result = agent.validate(context)
        core058_violations = [v for v in result.violations if "CORE-058" in v]
        assert len(core058_violations) >= 1

    def test_no_violation_when_no_sqlite_paths(self) -> None:
        """CORE-058: context without sqlite_db_paths must not produce violation."""
        agent = ExtendedGovernanceAgent()
        context = {}
        result = agent.validate(context)
        core058_violations = [v for v in result.violations if "CORE-058" in v]
        assert len(core058_violations) == 0


class TestCore059McpFootprintLogging:
    """CORE-059: MCP footprint auditing — tool invocation logging."""

    def test_no_violation_when_mcp_logging_enabled(self) -> None:
        """CORE-059: mcp_logging_enabled=True must not produce violation."""
        agent = ExtendedGovernanceAgent()
        context = {"mcp_tool_invoked": "cortex_ask", "mcp_logging_enabled": True}
        result = agent.validate(context)
        core059_violations = [v for v in result.violations if "CORE-059" in v]
        assert len(core059_violations) == 0

    def test_warning_when_mcp_tool_invoked_without_logging(self) -> None:
        """CORE-059: mcp_tool_invoked without mcp_logging_enabled must produce warning."""
        agent = ExtendedGovernanceAgent()
        context = {"mcp_tool_invoked": "cortex_ask", "mcp_logging_enabled": False}
        result = agent.validate(context)
        core059_hits = [
            item for item in (result.warnings + result.violations) if "CORE-059" in item
        ]
        assert len(core059_hits) >= 1


class TestCore060SdlcBrainGovernance:
    """CORE-060: SDLC Brain governance — decisions must flow through SDLC Brain."""

    def test_no_violation_when_sdlc_approved(self) -> None:
        """CORE-060: sdlc_approved=True must not produce violation."""
        agent = ExtendedGovernanceAgent()
        context = {"sdlc_action": "deploy", "sdlc_approved": True}
        result = agent.validate(context)
        core060_hits = [
            item for item in (result.warnings + result.violations) if "CORE-060" in item
        ]
        assert len(core060_hits) == 0

    def test_warning_when_sdlc_action_without_approval(self) -> None:
        """CORE-060: sdlc_action without sdlc_approved must produce warning."""
        agent = ExtendedGovernanceAgent()
        context = {"sdlc_action": "deploy"}
        result = agent.validate(context)
        core060_hits = [
            item for item in (result.warnings + result.violations) if "CORE-060" in item
        ]
        assert len(core060_hits) >= 1


class TestCore062PlanFirstExecution:
    """CORE-062: Plan-first execution — all execution must follow approved plan."""

    def test_no_violation_when_plan_document_provided(self) -> None:
        """CORE-062: plan_document key must suppress violation."""
        agent = ExtendedGovernanceAgent()
        context = {
            "operation_type": "IMPLEMENT",
            "plan_document": "cortex-registry/planning/cortex-refactor-master.yaml",
        }
        result = agent.validate(context)
        core062_violations = [v for v in result.violations if "CORE-062" in v]
        assert len(core062_violations) == 0

    def test_violation_when_implement_without_plan(self) -> None:
        """CORE-062: IMPLEMENT operation without plan_document must produce BLOCKED violation."""
        agent = ExtendedGovernanceAgent()
        context = {"operation_type": "IMPLEMENT"}
        result = agent.validate(context)
        core062_violations = [v for v in result.violations if "CORE-062" in v]
        assert len(core062_violations) >= 1
        assert result.level == EnforcementLevel.BLOCKED

    def test_no_violation_for_read_operations_without_plan(self) -> None:
        """CORE-062: READ/QUERY operations do not require a plan document."""
        agent = ExtendedGovernanceAgent()
        context = {"operation_type": "READ"}
        result = agent.validate(context)
        core062_violations = [v for v in result.violations if "CORE-062" in v]
        assert len(core062_violations) == 0


class TestCore063ChallengeFirstGate:
    """CORE-063: Challenge-first governance gate — major operations require challenge."""

    def test_no_violation_when_challenge_issued(self) -> None:
        """CORE-063: challenge_issued=True must not produce violation."""
        agent = ExtendedGovernanceAgent()
        context = {
            "operation_scope": "SYSTEM",
            "challenge_issued": True,
        }
        result = agent.validate(context)
        core063_violations = [v for v in result.violations if "CORE-063" in v]
        assert len(core063_violations) == 0

    def test_violation_for_system_scope_without_challenge(self) -> None:
        """CORE-063: SYSTEM scope operation without challenge_issued must be BLOCKED."""
        agent = ExtendedGovernanceAgent()
        context = {"operation_scope": "SYSTEM"}
        result = agent.validate(context)
        core063_violations = [v for v in result.violations if "CORE-063" in v]
        assert len(core063_violations) >= 1
        assert result.level == EnforcementLevel.BLOCKED


class TestEnforcementOrchestratorIncludesExtendedAgent:
    """EnforcementOrchestrator must include ExtendedGovernanceAgent in its agent list."""

    def test_enforcement_orchestrator_has_extended_governance_agent(self) -> None:
        """EnforcementOrchestrator.agents must include an ExtendedGovernanceAgent."""
        orchestrator = EnforcementOrchestrator()
        agent_types = [type(a).__name__ for a in orchestrator.agents]
        assert "ExtendedGovernanceAgent" in agent_types, (
            f"Expected ExtendedGovernanceAgent in agents, got: {agent_types}"
        )

    def test_enforcement_orchestrator_covers_core_058_in_validate_operation(self) -> None:
        """validate_operation must evaluate CORE-058 when sqlite_db_paths and wal_mode_enabled=False."""
        orchestrator = EnforcementOrchestrator()
        operation = {
            "sqlite_db_paths": [".cortex-runtime/audit.db"],
            "wal_mode_enabled": False,
            "operation_type": "READ",
        }
        result = orchestrator.validate_operation(operation)
        # Must be Err (BLOCKED) or Ok with CORE-058 in violations/warnings
        if result.is_err():
            all_msgs = result.error.violations + result.error.warnings
        else:
            all_msgs = result.value.violations + result.value.warnings
        core058_hits = [m for m in all_msgs if "CORE-058" in m]
        assert len(core058_hits) >= 1, "CORE-058 must be enforced by validate_operation"
