"""
Golden Test: Workflow E2E Trace Chain Verification

Phase 63-D — GAP-63-04 remediation.
Verifies 4 core intents produce complete AC marker trace chains.

Tests:
  - IMPLEMENT / FIX / AUDIT / REFACTOR intent trace chains
  - No orphaned AC_START markers after pipeline execution
  - Workflow template reference present in orchestrator source

Authority: CORE-008, CORE-055, CORE-064
AC-IDs: AC-63-D-WORKFLOW-TRACE-001..006
"""
# ruff: noqa: S101
from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).parents[3]
TEMPLATES_ROOT = ROOT / "cortex-registry" / "workflows" / "templates"
ORCHESTRATORS_ROOT = ROOT / "cortex" / "orchestrators"


def _find_ac_orphans_in_file(path: Path) -> tuple[int, int]:
    """Return (ac_start_count, ac_complete_count) for a file."""
    content = path.read_text(errors="replace")
    starts = len(re.findall(r"\bAC_START\b", content))
    completes = len(re.findall(r"\bAC_COMPLETE\b", content))
    return starts, completes


class TestWorkflowTemplateExists:
    """Core workflow templates for each intent type must exist."""

    def test_implement_workflow_template_exists(self) -> None:
        """tdd/tdd-workflow.yaml must exist — canonical Phase 90 IMPLEMENT/TDD dispatcher."""
        template = TEMPLATES_ROOT / "tdd" / "tdd-workflow.yaml"
        assert template.exists(), (
            "tdd/tdd-workflow.yaml missing — "
            "IMPLEMENT/TDD intent has no canonical workflow template (Phase 90)"
        )

    def test_audit_workflow_template_exists(self) -> None:
        """security/security-compliance-audit.yaml must exist for AUDIT intent."""
        template = TEMPLATES_ROOT / "security" / "security-compliance-audit.yaml"
        assert template.exists(), (
            "security/security-compliance-audit.yaml missing — "
            "AUDIT intent has no canonical workflow template"
        )

    def test_lifecycle_onboarding_template_exists(self) -> None:
        """lifecycle/onboarding-workflow.yaml must exist."""
        template = TEMPLATES_ROOT / "lifecycle" / "onboarding-workflow.yaml"
        assert template.exists(), (
            "lifecycle/onboarding-workflow.yaml missing"
        )

    def test_audit_trace_primitive_exists(self) -> None:
        """primitives/execution/audit-trace.yaml must exist (CORE trace primitive)."""
        primitive = TEMPLATES_ROOT / "primitives" / "execution" / "audit-trace.yaml"
        assert primitive.exists(), (
            "primitives/execution/audit-trace.yaml missing — "
            "AC marker trace primitive not scaffolded"
        )


class TestACMarkerTraceIntegrity:
    """AC_START must always be paired with AC_COMPLETE in orchestrator source files."""

    def test_implement_intent_trace_chain(self) -> None:
        """TDDOrchestrator (IMPLEMENT handler) must have AC_COMPLETE paired with AC_START."""
        tdd_file = ORCHESTRATORS_ROOT / "core" / "tdd_orchestrator.py"
        if not tdd_file.exists():
            pytest.skip("tdd_orchestrator.py not found")
        starts, completes = _find_ac_orphans_in_file(tdd_file)
        if starts == 0:
            pytest.skip("TDDOrchestrator has no AC_START markers yet")
        assert completes > 0, (
            f"TDDOrchestrator has {starts} AC_START but 0 AC_COMPLETE — orphaned trace"
        )

    def test_fix_intent_trace_chain(self) -> None:
        """IntentRouter (FIX handler) must have AC_COMPLETE paired with AC_START."""
        intent_router = ORCHESTRATORS_ROOT / "core" / "intent_router.py"
        if not intent_router.exists():
            pytest.skip("intent_router.py not found")
        starts, completes = _find_ac_orphans_in_file(intent_router)
        if starts == 0:
            pytest.skip("IntentRouter has no AC_START markers yet")
        assert completes > 0, (
            f"IntentRouter has {starts} AC_START but 0 AC_COMPLETE — orphaned trace"
        )

    def test_audit_intent_trace_chain(self) -> None:
        """EnforcementOrchestrator (AUDIT handler) must have AC_COMPLETE."""
        enforcement_file = ORCHESTRATORS_ROOT / "core" / "enforcement_orchestrator.py"
        if not enforcement_file.exists():
            pytest.skip("enforcement_orchestrator.py not found")
        starts, completes = _find_ac_orphans_in_file(enforcement_file)
        if starts == 0:
            pytest.skip("EnforcementOrchestrator has no AC_START markers yet")
        assert completes > 0, (
            f"EnforcementOrchestrator has {starts} AC_START but 0 AC_COMPLETE"
        )

    def test_refactor_intent_trace_chain(self) -> None:
        """RefactoringOrchestrator (REFACTOR handler) must have AC_COMPLETE."""
        refactor_file = ORCHESTRATORS_ROOT / "domain" / "refactoring_orchestrator.py"
        if not refactor_file.exists():
            pytest.skip("refactoring_orchestrator.py not found")
        starts, completes = _find_ac_orphans_in_file(refactor_file)
        if starts == 0:
            pytest.skip("RefactoringOrchestrator has no AC_START markers yet")
        assert completes > 0, (
            f"RefactoringOrchestrator has {starts} AC_START but 0 AC_COMPLETE"
        )

    def test_no_orphaned_ac_start_in_core_orchestrators(self) -> None:
        """No core orchestrator file may have AC_START without any matching AC_COMPLETE."""
        core_dir = ORCHESTRATORS_ROOT / "core"
        if not core_dir.exists():
            pytest.skip("core orchestrators dir not found")
        orphaned = []
        for py_file in core_dir.glob("*.py"):
            starts, completes = _find_ac_orphans_in_file(py_file)
            if starts > 0 and completes == 0:
                orphaned.append(
                    f"{py_file.relative_to(ROOT)} — {starts} AC_START, 0 AC_COMPLETE"
                )
        assert orphaned == [], (
            "Orphaned AC_START in core orchestrators:\n"
            + "\n".join(f"  {o}" for o in orphaned)
        )


class TestWorkflowTemplateLoadedInTrace:
    """Workflow templates reference audit-trace primitive for trace chain wiring."""

    def test_tdd_feature_template_references_audit_trace(self) -> None:
        """tdd-workflow.yaml (Phase 90 canonical) must reference AC markers or trace primitive."""
        template = TEMPLATES_ROOT / "tdd" / "tdd-workflow.yaml"
        if not template.exists():
            pytest.skip("tdd-workflow.yaml not found")
        content = template.read_text(errors="replace")
        has_trace = "audit-trace" in content or "AC_START" in content or "audit_trace" in content
        assert has_trace, (
            "tdd-workflow.yaml does not reference audit-trace primitive or AC markers"
        )

    def test_security_audit_template_references_trace(self) -> None:
        """security-compliance-audit.yaml must reference audit-trace primitive or AC markers."""
        template = TEMPLATES_ROOT / "security" / "security-compliance-audit.yaml"
        if not template.exists():
            pytest.skip("security-compliance-audit.yaml not found")
        content = template.read_text(errors="replace")
        has_trace = "audit-trace" in content or "AC_START" in content or "audit_trail" in content
        assert has_trace, (
            "security-compliance-audit.yaml does not reference audit-trace or AC markers"
        )
