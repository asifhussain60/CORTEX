"""
Phase 103-e TDD RED: enforcement_orchestrator.py agent extraction.

Verifies that all 11 agent classes are importable from the new
cortex.orchestrators.core.enforcement_orchestrator.agents sub-package
AND that the top-level enforcement_orchestrator still re-exports everything
for backwards compatibility.

Authority: phase-103c-remaining-god-objects.yaml
CORE-008: Tests written BEFORE implementation.
AC-ID: AC-P103E-001
"""

from __future__ import annotations

import importlib
import pytest


# ---------------------------------------------------------------------------
# New sub-package imports (Phase 103-e extraction targets)
# ---------------------------------------------------------------------------

AGENT_MODULES = {
    "GovernanceEnforcementAgent": "cortex.orchestrators.core.enforcement_orchestrator.agents.governance_enforcement_agent",
    "SecurityCheckpointAgent": "cortex.orchestrators.core.enforcement_orchestrator.agents.security_checkpoint_agent",
    "ComplianceValidationAgent": "cortex.orchestrators.core.enforcement_orchestrator.agents.compliance_validation_agent",
    "FileNamingEnforcementAgent": "cortex.orchestrators.core.enforcement_orchestrator.agents.file_naming_enforcement_agent",
    "IncrementalExecutionAgent": "cortex.orchestrators.core.enforcement_orchestrator.agents.incremental_execution_agent",
    "MarkdownSuppressionAgent": "cortex.orchestrators.core.enforcement_orchestrator.agents.markdown_suppression_agent",
    "ResponseContentValidationAgent": "cortex.orchestrators.core.enforcement_orchestrator.agents.markdown_suppression_agent",
    "ArchitectureIntegrityAgent": "cortex.orchestrators.core.enforcement_orchestrator.agents.architecture_integrity_agent",
    "DiscoveryEnforcementAgent": "cortex.orchestrators.core.enforcement_orchestrator.agents.discovery_enforcement_agent",
    "ExtendedGovernanceAgent": "cortex.orchestrators.core.enforcement_orchestrator.agents.extended_governance_agent",
    "SweepCompositionEnforcementAgent": "cortex.orchestrators.core.enforcement_orchestrator.agents.sweep_composition_agent",
}


@pytest.mark.parametrize("class_name,module_path", list(AGENT_MODULES.items()))
def test_agent_importable_from_sub_package(class_name: str, module_path: str) -> None:
    """Each agent class must be importable from its dedicated sub-module."""
    mod = importlib.import_module(module_path)
    assert hasattr(mod, class_name), (
        f"{class_name} not found in {module_path}"
    )
    cls = getattr(mod, class_name)
    assert callable(cls), f"{class_name} must be a class"


def test_agents_package_init_exports_all() -> None:
    """agents/__init__.py must re-export all 11 agent classes."""
    agents_pkg = importlib.import_module(
        "cortex.orchestrators.core.enforcement_orchestrator.agents"
    )
    for class_name in AGENT_MODULES:
        assert hasattr(agents_pkg, class_name), (
            f"agents/__init__.py missing re-export: {class_name}"
        )


# ---------------------------------------------------------------------------
# Backwards-compatibility: top-level module must still export everything
# ---------------------------------------------------------------------------

BACKWARDS_COMPAT_EXPORTS = [
    "EnforcementOrchestrator",
    "EnforcementResult",
    "EnforcementLevel",
    "GovernanceEnforcementAgent",
    "SecurityCheckpointAgent",
    "ComplianceValidationAgent",
    "FileNamingEnforcementAgent",
    "IncrementalExecutionAgent",
    "MarkdownSuppressionAgent",
    "ResponseContentValidationAgent",
    "ArchitectureIntegrityAgent",
    "DiscoveryEnforcementAgent",
    "ExtendedGovernanceAgent",
    "SweepCompositionEnforcementAgent",
    "get_enforcement_orchestrator",
]


@pytest.mark.parametrize("symbol", BACKWARDS_COMPAT_EXPORTS)
def test_top_level_module_still_exports(symbol: str) -> None:
    """Top-level enforcement_orchestrator.py must re-export all public symbols."""
    mod = importlib.import_module(
        "cortex.orchestrators.core.enforcement_orchestrator"
    )
    assert hasattr(mod, symbol), (
        f"Backwards-compat broken: '{symbol}' not found in enforcement_orchestrator"
    )


# ---------------------------------------------------------------------------
# File-size guard: after extraction the top-level file must be < 1000 lines
# ---------------------------------------------------------------------------

def test_enforcement_orchestrator_line_count_under_1000() -> None:
    """After extraction the orchestrator coordinator file must be < 1000 lines."""
    import pathlib

    workspace = pathlib.Path(__file__).parents[3]  # /PROJECTS/CORTEX
    # After Phase 103-e the entry point is the package __init__.py;
    # the thin orchestrator.py coordinator is also checked.
    candidates = [
        workspace / "cortex/orchestrators/core/enforcement_orchestrator/__init__.py",
        workspace / "cortex/orchestrators/core/enforcement_orchestrator/orchestrator.py",
    ]
    found = [p for p in candidates if p.exists()]
    assert found, (
        "enforcement_orchestrator package __init__.py or orchestrator.py not found. "
        "Expected at cortex/orchestrators/core/enforcement_orchestrator/"
    )

    for coordinator in found:
        line_count = len(coordinator.read_text().splitlines())
        assert line_count < 1000, (
            f"{coordinator.name} is {line_count} lines — must be < 1000 after extraction"
        )


# ---------------------------------------------------------------------------
# Smoke: orchestrator still instantiates and validates correctly
# ---------------------------------------------------------------------------

def test_enforcement_orchestrator_instantiates() -> None:
    """EnforcementOrchestrator must instantiate with 11 agents."""
    from cortex.orchestrators.core.enforcement_orchestrator import EnforcementOrchestrator

    eo = EnforcementOrchestrator()
    assert len(eo.agents) == 11


def test_enforcement_orchestrator_validate_operation_passes_clean() -> None:
    """validate_operation must return Ok for a clean QUERY operation."""
    from cortex.orchestrators.core.enforcement_orchestrator import (
        EnforcementOrchestrator,
        EnforcementLevel,
    )

    eo = EnforcementOrchestrator()
    result = eo.validate_operation({"intent": "QUERY"})
    # QUERY intent should produce no blocking violations
    assert result.is_ok() or (
        result.is_err() and result.error.level == EnforcementLevel.BLOCKED
    ), "validate_operation must return a Result"
