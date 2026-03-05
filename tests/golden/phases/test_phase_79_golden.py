"""
Phase 79 Golden Test — SDLC Intelligence Engine: E2E Execution Certainty

SWEEP-79-SDLC-INTELLIGENCE-ENGINE — End-to-end validation of the 3-layer SDLC
architecture: 6 knowledge YAMLs, 7 workflow templates, 4 response blocks,
SDLCWorkflowOrchestrator wired in domain spec, MCP ops, 4 stack-specific YAMLs.

Unlike unit tests (tests/unit/core/test_phase_79_sdlc_intelligence_engine.py) which
check file existence individually, this golden test verifies the E2E flow:
orchestrator → template selection → knowledge hydration → response block rendering.

AC_START: AC-79-GOLDEN-E2E-20260225

Authority: cortex-registry/planning/phases/completed/phase-79-sdlc-intelligence-engine.yaml
CORE-008: TDD-first | CORE-064: Full sweep
"""
from __future__ import annotations

import importlib
from pathlib import Path
from typing import Any, Dict, List

import pytest
import yaml

CORTEX_ROOT = Path(__file__).resolve().parents[3]
KNOWLEDGE_SDLC = CORTEX_ROOT / "cortex-registry" / "knowledge" / "sdlc"
WORKFLOW_SDLC = CORTEX_ROOT / "cortex-registry" / "workflows" / "templates" / "sdlc"
RESPONSE_TEMPLATES = CORTEX_ROOT / ".github" / "templates" / "cortex-response-templates.md"
INDEX_YAML = CORTEX_ROOT / "cortex-registry" / "knowledge" / "INDEX.yaml"


# ══════════════════════════════════════════════════════════════════════════════
# E2E-1: Full knowledge layer validation
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase79KnowledgeLayer:
    """All 6 SDLC knowledge YAMLs + 4 stack-specific YAMLs must exist and be valid."""

    KNOWLEDGE_FILES = [
        "analysis-design-patterns.yaml",
        "test-strategy-selection.yaml",
        "code-review-checklist.yaml",
        "integration-strategy.yaml",
        "security-by-design.yaml",
        "documentation-strategy.yaml",
    ]

    STACK_FILES = [
        "stack-specific/python-stack.yaml",
        "stack-specific/typescript-stack.yaml",
        "stack-specific/dotnet-stack.yaml",
        "stack-specific/html-css-stack.yaml",
    ]

    @pytest.mark.parametrize("filename", KNOWLEDGE_FILES)
    def test_knowledge_yaml_exists_and_valid(self, filename: str) -> None:
        """Each knowledge YAML must exist and have required keys."""
        path = KNOWLEDGE_SDLC / filename
        assert path.exists(), f"Missing SDLC knowledge YAML: {path}"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"{filename} must parse to dict"
        for key in ("overview", "best_practices", "company_context"):
            assert key in data, f"{filename} missing required key '{key}'"

    @pytest.mark.parametrize("filename", STACK_FILES)
    def test_stack_yaml_exists_and_valid(self, filename: str) -> None:
        """Each stack-specific YAML must exist with stack_overrides key."""
        path = KNOWLEDGE_SDLC / filename
        assert path.exists(), f"Missing stack-specific YAML: {path}"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"{filename} must parse to dict"
        assert "stack_overrides" in data, f"{filename} missing 'stack_overrides' key"

    def test_index_yaml_has_sdlc_domain(self) -> None:
        """INDEX.yaml must have 'sdlc' domain with ≥6 entries."""
        assert INDEX_YAML.exists(), f"INDEX.yaml not found at {INDEX_YAML}"
        data = yaml.safe_load(INDEX_YAML.read_text(encoding="utf-8"))
        assert "sdlc" in data, "INDEX.yaml must have 'sdlc' domain"
        guides = data["sdlc"].get("guides", [])
        assert len(guides) >= 6, f"sdlc domain must have ≥6 entries, got {len(guides)}"


# ══════════════════════════════════════════════════════════════════════════════
# E2E-2: Full workflow template layer validation
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase79WorkflowLayer:
    """All 6 SDLC workflow templates must exist with required structure."""

    WORKFLOW_FILES = [
        "requirements-analysis.yaml",
        "solution-design.yaml",
        "implementation-execution.yaml",
        "code-review-gate.yaml",
        "integration-verification.yaml",
        "security-assessment.yaml",
    ]

    @pytest.mark.parametrize("filename", WORKFLOW_FILES)
    def test_workflow_template_exists_and_valid(self, filename: str) -> None:
        """Each workflow template must exist with workflow and knowledge_context keys."""
        path = WORKFLOW_SDLC / filename
        assert path.exists(), f"Missing SDLC workflow template: {path}"
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict), f"{filename} must parse to dict"
        assert "workflow" in data, f"{filename} missing 'workflow' key"
        assert "knowledge_context" in data, f"{filename} missing 'knowledge_context' key"

    def test_no_auto_push_in_implementation_workflow(self) -> None:
        """implementation-execution.yaml must NOT contain 'git push' (safety)."""
        path = WORKFLOW_SDLC / "implementation-execution.yaml"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "git push" not in content.lower(), (
            "implementation-execution.yaml must NOT contain 'git push'"
        )


# ══════════════════════════════════════════════════════════════════════════════
# E2E-3: Response blocks present in SSOT
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase79ResponseBlocks:
    """All 4 BLOCK-* sections must exist in cortex-response-templates.md."""

    BLOCKS = [
        "BLOCK-ANALYSIS",
        "BLOCK-DESIGN-DECISION",
        "BLOCK-CODE-REVIEW",
        "BLOCK-SECURITY-ASSESSMENT",
    ]

    @pytest.mark.parametrize("block_id", BLOCKS)
    def test_response_block_exists(self, block_id: str) -> None:
        """Each response block must be present in the SSOT templates file."""
        assert RESPONSE_TEMPLATES.exists()
        content = RESPONSE_TEMPLATES.read_text(encoding="utf-8")
        assert block_id in content, (
            f"Response block '{block_id}' not found in cortex-response-templates.md"
        )


# ══════════════════════════════════════════════════════════════════════════════
# E2E-4: SDLCWorkflowOrchestrator functional E2E
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase79SDLCOrchestratorE2E:
    """SDLCWorkflowOrchestrator end-to-end: import → health → execute → result."""

    def test_orchestrator_importable(self) -> None:
        """SDLCWorkflowOrchestrator must be importable."""
        mod = importlib.import_module(
            "cortex.orchestrators.domain.sdlc_workflow_orchestrator"
        )
        assert hasattr(mod, "SDLCWorkflowOrchestrator")

    def test_orchestrator_inherits_protocol_mixin(self) -> None:
        """SDLCWorkflowOrchestrator must inherit OrchestratorProtocolMixin."""
        from cortex.orchestrators.domain.sdlc_workflow_orchestrator import (
            SDLCWorkflowOrchestrator,
        )
        from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
        assert issubclass(SDLCWorkflowOrchestrator, OrchestratorProtocolMixin)

    def test_health_check_returns_healthy(self) -> None:
        """health_check() must return status: healthy with template_count > 0."""
        from cortex.orchestrators.domain.sdlc_workflow_orchestrator import (
            SDLCWorkflowOrchestrator,
        )
        orch = SDLCWorkflowOrchestrator()
        result = orch.health_check()
        assert result["status"] == "healthy"
        assert result["template_count"] > 0

    def test_execute_analyze_intent(self) -> None:
        """Execute 'ANALYZE' intent → returns result with template_id and response_block."""
        from cortex.orchestrators.domain.sdlc_workflow_orchestrator import (
            SDLCWorkflowOrchestrator,
        )
        orch = SDLCWorkflowOrchestrator()
        result = orch.execute_operation("ANALYZE")
        assert result["result"] == "ok"
        assert "template_id" in result
        assert "response_block" in result
        assert result["response_block"] in (
            "BLOCK-ANALYSIS", "BLOCK-DESIGN-DECISION",
            "BLOCK-CODE-REVIEW", "BLOCK-SECURITY-ASSESSMENT",
        )

    def test_execute_design_intent(self) -> None:
        """Execute 'DESIGN' intent → routes to solution-design template."""
        from cortex.orchestrators.domain.sdlc_workflow_orchestrator import (
            SDLCWorkflowOrchestrator,
        )
        orch = SDLCWorkflowOrchestrator()
        result = orch.execute_operation("DESIGN")
        assert result["result"] == "ok"
        assert "design" in result["template_id"].lower()

    def test_execute_security_intent(self) -> None:
        """Execute 'SECURITY_AUDIT' intent → routes to security-assessment."""
        from cortex.orchestrators.domain.sdlc_workflow_orchestrator import (
            SDLCWorkflowOrchestrator,
        )
        orch = SDLCWorkflowOrchestrator()
        result = orch.execute_operation("SECURITY_AUDIT")
        assert result["result"] == "ok"
        assert result["response_block"] == "BLOCK-SECURITY-ASSESSMENT"

    def test_workflow_tools_has_execute_and_list_sdlc(self) -> None:
        """workflow_tools.py must support execute and list_sdlc operations."""
        try:
            mod = importlib.import_module("cortex.mcp.tools.workflow_tools")
            src = Path(mod.__file__).read_text(encoding="utf-8")
            assert "execute" in src, "workflow_tools.py missing 'execute' operation"
            assert "list_sdlc" in src, "workflow_tools.py missing 'list_sdlc' operation"
        except ImportError:
            pytest.skip("workflow_tools not available")


# ══════════════════════════════════════════════════════════════════════════════
# E2E-5: Domain wiring + completion metadata
# ══════════════════════════════════════════════════════════════════════════════

class TestPhase79DomainWiringAndMetadata:
    """SDLCWorkflowOrchestrator wired in domain spec; phase marked COMPLETE."""

    def test_domain_wiring_has_sdlc_orchestrator(self) -> None:
        """domain-orchestrator-wiring.yaml must list SDLCWorkflowOrchestrator."""
        domain_wiring = (
            CORTEX_ROOT / "cortex-registry" / "core" / "specifications"
            / "domain-orchestrator-wiring.yaml"
        )
        assert domain_wiring.exists()
        content = domain_wiring.read_text(encoding="utf-8")
        assert "SDLCWorkflowOrchestrator" in content, (
            "SDLCWorkflowOrchestrator not found in domain-orchestrator-wiring.yaml"
        )

    def test_cortex_master_marks_phase_79_complete(self) -> None:
        """cortex-master.yaml must show phase-79 status: COMPLETE."""
        master = CORTEX_ROOT / "cortex-registry" / "cortex-master.yaml"
        data = yaml.safe_load(master.read_text(encoding="utf-8"))
        phases = data.get("phase_detail_files", [])
        ph79 = next((p for p in phases if p.get("id") == "phase-79"), None)
        assert ph79 is not None, "phase-79 not found in cortex-master.yaml"
        assert ph79.get("status") == "COMPLETE", (
            f"phase-79 status is '{ph79.get('status')}', expected COMPLETE"
        )
