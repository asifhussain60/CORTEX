"""
Golden Test — PB-STS-001 v2: Workflow-Template-Based Design

Validates that the STS badmonolith playbook (pb-sts-001) has been updated to
reference the canonical SDLC workflow templates from Phase 79 for its analysis,
design, and TDD-implementation stages — replacing ad-hoc inline stage definitions
with proper template references.

SWEEP: PB-STS-001-V2-WORKFLOW-TEMPLATE-DESIGN
AC_START: AC-STS-WF-TEMPLATE-20260225

CORE-008: TDD-first (RED phase — these tests MUST fail before playbook is updated)
CORE-064: Full sweep — all 5 integration points must be validated
CORE-035: Single canonical — SDLC templates are the SSOT; no duplication in playbook

Authority:
  - cortex-registry/_cortex-master/playbooks/sharpen-the-saw/pb-sts-001-badmonolith-refactoring.yaml
  - cortex-registry/workflows/templates/sdlc/requirements-analysis.yaml
  - cortex-registry/workflows/templates/sdlc/solution-design.yaml
  - cortex-registry/workflows/templates/sdlc/implementation-execution.yaml
  - cortex-registry/workflows/templates/tdd/tdd-feature-implementation.yaml
"""
from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml

CORTEX_ROOT = Path(__file__).resolve().parents[3]

PLAYBOOK_PATH = (
    CORTEX_ROOT
    / "cortex-registry"
    / "_cortex-master"
    / "playbooks"
    / "sharpen-the-saw"
    / "pb-sts-001-badmonolith-refactoring.yaml"
)

SDLC_TEMPLATES_ROOT = (
    CORTEX_ROOT / "cortex-registry" / "workflows" / "templates" / "sdlc"
)

TDD_TEMPLATES_ROOT = (
    CORTEX_ROOT / "cortex-registry" / "workflows" / "templates" / "tdd"
)

# Canonical SDLC workflow templates that pb-sts-001 must reference
REQUIRED_SDLC_TEMPLATE_REFS = {
    "sdlc/requirements-analysis": "sdlc/requirements-analysis.yaml",
    "sdlc/solution-design": "sdlc/solution-design.yaml",
    "sdlc/implementation-execution": "sdlc/implementation-execution.yaml",
    "sdlc/security-assessment": "sdlc/security-assessment.yaml",
    "sdlc/code-review-gate": "sdlc/code-review-gate.yaml",
}

# TDD template that must be referenced for implementation stages
REQUIRED_TDD_TEMPLATE = "tdd/tdd-feature-implementation"


# ══════════════════════════════════════════════════════════════════════════════
# Fixture: load playbook
# ══════════════════════════════════════════════════════════════════════════════

@pytest.fixture(scope="module")
def playbook() -> Dict[str, Any]:
    """Load the STS pb-sts-001 playbook YAML."""
    assert PLAYBOOK_PATH.exists(), f"Playbook not found: {PLAYBOOK_PATH}"
    data = yaml.safe_load(PLAYBOOK_PATH.read_text())
    assert isinstance(data, dict), "Playbook must parse to a dict"
    return data


# ══════════════════════════════════════════════════════════════════════════════
# Suite 1: Playbook structural integrity
# ══════════════════════════════════════════════════════════════════════════════

class TestPlaybookStructure:
    """PB-STS-001 playbook must have workflow-template design keys (no version field)."""

    def test_playbook_has_no_version(self, playbook: Dict[str, Any]) -> None:
        """Playbook must NOT declare a version field (version language eliminated)."""
        pb = playbook.get("playbook", playbook)
        assert "version" not in pb, "Playbook must not have a 'version' field"

    def test_playbook_version_is_absent(self, playbook: Dict[str, Any]) -> None:
        """Playbook version field must be absent (production-readiness hardening)."""
        pb = playbook.get("playbook", playbook)
        assert "version" not in pb, (
            f"Playbook must not contain version field, found: '{pb.get('version')}'"
        )

    def test_playbook_has_sdlc_template_section(self, playbook: Dict[str, Any]) -> None:
        """Playbook must have 'sdlc_workflow_templates' section listing canonical refs."""
        pb = playbook.get("playbook", playbook)
        assert "sdlc_workflow_templates" in pb, (
            "Playbook must have 'sdlc_workflow_templates' section mapping stages to "
            "canonical SDLC workflow template IDs"
        )

    def test_playbook_has_workflow_design_flag(self, playbook: Dict[str, Any]) -> None:
        """Playbook must have workflow_template_design: true flag."""
        pb = playbook.get("playbook", playbook)
        assert pb.get("workflow_template_design") is True, (
            "Playbook must have 'workflow_template_design: true' to signal v2 design"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Suite 2: SDLC template references in stages
# ══════════════════════════════════════════════════════════════════════════════

class TestSDLCTemplateReferences:
    """Each key STS stage must reference the canonical SDLC workflow template."""

    def _collect_template_refs(self, playbook: Dict[str, Any]) -> List[str]:
        """Extract all template_ref values from stages."""
        pb = playbook.get("playbook", playbook)
        stages = pb.get("stages", [])
        refs: List[str] = []
        for stage in stages:
            ref = stage.get("template_ref", "")
            if ref:
                refs.append(ref)
            # also check nested mcp_tools template_name fields
            for tool_call in stage.get("mcp_tools", []):
                call_str = tool_call.get("call", "")
                if "template_name=" in call_str:
                    # extract e.g. template_name='sdlc/requirements-analysis'
                    start = call_str.find("template_name='") + len("template_name='")
                    end = call_str.find("'", start)
                    if start > 0 and end > start:
                        refs.append(call_str[start:end])
        # also check sdlc_workflow_templates section
        sdlc_section = pb.get("sdlc_workflow_templates", {})
        refs.extend(sdlc_section.values())
        return refs

    def test_requirements_analysis_template_referenced(
        self, playbook: Dict[str, Any]
    ) -> None:
        """Stage 1 (LENS Baseline / Analysis) must reference sdlc/requirements-analysis."""
        refs = self._collect_template_refs(playbook)
        assert any("requirements-analysis" in r for r in refs), (
            "No stage references 'sdlc/requirements-analysis' template. "
            "Stage 1 (LENS Baseline) must use the canonical requirements-analysis SDLC template."
        )

    def test_solution_design_template_referenced(
        self, playbook: Dict[str, Any]
    ) -> None:
        """Stage 4 (Architecture Decomposition) must reference sdlc/solution-design."""
        refs = self._collect_template_refs(playbook)
        assert any("solution-design" in r for r in refs), (
            "No stage references 'sdlc/solution-design' template. "
            "Stage 4 (Architecture Decomposition) must use the canonical solution-design SDLC template."
        )

    def test_implementation_execution_template_referenced(
        self, playbook: Dict[str, Any]
    ) -> None:
        """Stage 5 (TDD Coverage) must reference sdlc/implementation-execution."""
        refs = self._collect_template_refs(playbook)
        assert any("implementation-execution" in r for r in refs), (
            "No stage references 'sdlc/implementation-execution' template. "
            "Stage 5 (TDD Coverage) must use the canonical implementation-execution SDLC template."
        )

    def test_security_assessment_template_referenced(
        self, playbook: Dict[str, Any]
    ) -> None:
        """Stage 3 (Security Gate) must reference sdlc/security-assessment."""
        refs = self._collect_template_refs(playbook)
        assert any("security-assessment" in r for r in refs), (
            "No stage references 'sdlc/security-assessment' template. "
            "Stage 3 (Security Gate) must use the canonical security-assessment SDLC template."
        )

    def test_tdd_feature_implementation_template_referenced(
        self, playbook: Dict[str, Any]
    ) -> None:
        """TDD stage must reference tdd/tdd-feature-implementation template."""
        refs = self._collect_template_refs(playbook)
        assert any("tdd-feature-implementation" in r or "tdd/feature-implementation" in r for r in refs), (
            "No stage references 'tdd/tdd-feature-implementation' template. "
            "TDD Coverage stage must use the canonical tdd-feature-implementation template."
        )


# ══════════════════════════════════════════════════════════════════════════════
# Suite 3: SDLC templates actually exist on disk
# ══════════════════════════════════════════════════════════════════════════════

class TestSDLCTemplatesExist:
    """All SDLC templates referenced by the playbook must exist on disk."""

    @pytest.mark.parametrize(
        "template_id,filename",
        list(REQUIRED_SDLC_TEMPLATE_REFS.items()),
    )
    def test_sdlc_template_file_exists(self, template_id: str, filename: str) -> None:
        """Canonical SDLC template file must exist at expected path."""
        path = CORTEX_ROOT / "cortex-registry" / "workflows" / "templates" / filename
        assert path.exists(), (
            f"SDLC template '{template_id}' not found at: {path}"
        )

    def test_tdd_feature_implementation_exists(self) -> None:
        """tdd-feature-implementation.yaml must exist."""
        path = TDD_TEMPLATES_ROOT / "tdd-feature-implementation.yaml"
        assert path.exists(), f"tdd-feature-implementation.yaml not found at: {path}"

    @pytest.mark.parametrize(
        "template_id,filename",
        list(REQUIRED_SDLC_TEMPLATE_REFS.items()),
    )
    def test_sdlc_template_valid_yaml(self, template_id: str, filename: str) -> None:
        """Each SDLC template must be valid YAML with workflow and knowledge_context keys."""
        path = CORTEX_ROOT / "cortex-registry" / "workflows" / "templates" / filename
        if not path.exists():
            pytest.skip(f"File not yet created: {filename}")
        data = yaml.safe_load(path.read_text())
        assert isinstance(data, dict), f"{filename} must parse to a dict"
        assert "workflow" in data, f"{filename} missing required 'workflow' key"
        assert "knowledge_context" in data, (
            f"{filename} missing required 'knowledge_context' key"
        )


# ══════════════════════════════════════════════════════════════════════════════
# Suite 4: Badmonolith onboarding data feeds Stage 1
# ══════════════════════════════════════════════════════════════════════════════

class TestBadmonolithOnboardingIntegration:
    """Badmonolith onboarding artifacts must feed the requirements-analysis stage."""

    ONBOARDING_ROOT = (
        CORTEX_ROOT / "cortex-registry" / "company" / "repos" / "badmonolith"
    )

    def test_onboarding_summary_exists(self) -> None:
        """onboarding-summary.json must exist (produced by cortex_onboard_repository)."""
        path = self.ONBOARDING_ROOT / "onboarding-summary.json"
        assert path.exists(), (
            f"Badmonolith onboarding summary not found at: {path}\n"
            "Run: cortex_onboard_repository(repository_path='cortex-sts/CortexLabs/BadMonolith')"
        )

    def test_onboarding_has_governance_tab(self) -> None:
        """Onboarding must include 03_governance tab (feeds requirements-analysis LENS scan)."""
        import json
        summary_path = self.ONBOARDING_ROOT / "onboarding-summary.json"
        if not summary_path.exists():
            pytest.skip("Onboarding summary not yet generated")
        data = json.loads(summary_path.read_text())
        tab_ids = [t["id"] for t in data.get("tabs", [])]
        assert "03_governance" in tab_ids, (
            "Onboarding summary must have '03_governance' tab to feed requirements-analysis"
        )

    def test_onboarding_has_security_tab(self) -> None:
        """Onboarding must include 06_security tab (feeds security-assessment template)."""
        import json
        summary_path = self.ONBOARDING_ROOT / "onboarding-summary.json"
        if not summary_path.exists():
            pytest.skip("Onboarding summary not yet generated")
        data = json.loads(summary_path.read_text())
        tab_ids = [t["id"] for t in data.get("tabs", [])]
        assert "06_security" in tab_ids, (
            "Onboarding summary must have '06_security' tab to feed security-assessment"
        )

    def test_playbook_references_onboarding_artifacts(
        self, playbook: Dict[str, Any]
    ) -> None:
        """Playbook Stage 1 must reference the badmonolith onboarding artifacts path."""
        pb = playbook.get("playbook", playbook)
        # Look in target config or stage 1 inputs
        content = yaml.dump(pb)
        assert "company/repos/badmonolith" in content or "onboarding-summary" in content, (
            "Playbook must reference badmonolith onboarding artifacts "
            "('cortex-registry/company/repos/badmonolith') as inputs to Stage 1 analysis."
        )


# ══════════════════════════════════════════════════════════════════════════════
# Suite 5: No-auto-push and git checkpoint compliance
# ══════════════════════════════════════════════════════════════════════════════

class TestGitPolicyCompliance:
    """Playbook must inherit git checkpoint policy from implementation-execution template."""

    def test_playbook_has_no_auto_push(self, playbook: Dict[str, Any]) -> None:
        """Playbook YAML must not contain 'git push' (auto-push forbidden per SDLC template)."""
        raw = PLAYBOOK_PATH.read_text()
        assert "git push" not in raw.lower(), (
            "pb-sts-001 must NOT contain 'git push'. "
            "The implementation-execution.yaml template enforces no-auto-push policy."
        )

    def test_playbook_has_git_checkpoint_reference(
        self, playbook: Dict[str, Any]
    ) -> None:
        """Playbook must reference git checkpoint before implementation stages."""
        raw = PLAYBOOK_PATH.read_text()
        assert "git_checkpoint" in raw or "baseline_sha" in raw or "git checkpoint" in raw.lower(), (
            "Playbook must reference 'git_checkpoint' (inherited from implementation-execution.yaml). "
            "A baseline SHA must be recorded before any code changes."
        )


# ══════════════════════════════════════════════════════════════════════════════
# Suite 6: run_history captures workflow template run
# ══════════════════════════════════════════════════════════════════════════════

class TestRunHistoryWFTemplateRun:
    """run_history must include an entry for the workflow-template-based run."""

    def test_run_history_has_wf_template_run(self, playbook: Dict[str, Any]) -> None:
        """run_history must have ≥1 entry with workflow_template_design: true."""
        pb = playbook.get("playbook", playbook)
        run_history = pb.get("run_history", [])
        wf_runs = [r for r in run_history if r.get("workflow_template_design") is True]
        assert len(wf_runs) >= 1, (
            "run_history must include at least one entry with "
            "'workflow_template_design: true' to record the first workflow-template run."
        )

    def test_wf_template_run_references_sdlc_templates(
        self, playbook: Dict[str, Any]
    ) -> None:
        """The workflow-template run entry must list which SDLC templates were exercised."""
        pb = playbook.get("playbook", playbook)
        run_history = pb.get("run_history", [])
        wf_runs = [r for r in run_history if r.get("workflow_template_design") is True]
        if not wf_runs:
            pytest.skip("No workflow-template run entry yet (expected after playbook update)")
        run = wf_runs[-1]
        templates_used = run.get("sdlc_templates_used", [])
        assert len(templates_used) >= 3, (
            f"Workflow-template run must list ≥3 SDLC templates used, got {len(templates_used)}. "
            "Expected: requirements-analysis, solution-design, implementation-execution at minimum."
        )
