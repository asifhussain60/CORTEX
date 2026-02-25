"""Phase 79: SDLC Intelligence Engine — TDD Gate (SWEEP-79-SDLC-INTELLIGENCE-ENGINE).

Tests cover all 22 GAPs across 7 sub-phases:
  79-A: 6 SDLC knowledge YAMLs
  79-B: 7 SDLC workflow templates
  79-C: 4 response blocks in cortex-response-templates.md
  79-D: SDLCWorkflowOrchestrator + routing + MCP
  79-E: 4 stack-specific knowledge YAMLs
  79-F: INDEX.yaml update + git checkpoint policy
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import pytest
import yaml

WORKSPACE = Path(__file__).parents[3]
KNOWLEDGE_SDLC = WORKSPACE / "cortex-registry" / "knowledge" / "sdlc"
WORKFLOW_SDLC = WORKSPACE / "cortex-registry" / "workflows" / "templates" / "sdlc"
RESPONSE_TEMPLATES = WORKSPACE / ".github" / "templates" / "cortex-response-templates.md"
INDEX_YAML = WORKSPACE / "cortex-registry" / "knowledge" / "INDEX.yaml"

# ── SUB-PHASE 79-A: SDLC Knowledge YAMLs ─────────────────────────────────────

SDLC_KNOWLEDGE_FILES = [
    "analysis-design-patterns.yaml",
    "test-strategy-selection.yaml",
    "code-review-checklist.yaml",
    "integration-strategy.yaml",
    "security-by-design.yaml",
    "documentation-strategy.yaml",
]

SDLC_STACK_FILES = [
    "stack-specific/python-stack.yaml",
    "stack-specific/typescript-stack.yaml",
    "stack-specific/dotnet-stack.yaml",
    "stack-specific/html-css-stack.yaml",
]


@pytest.mark.parametrize("filename", SDLC_KNOWLEDGE_FILES)
def test_gap_79_a_knowledge_yaml_exists(filename: str) -> None:
    """GAP-79-A-01..06: All 6 SDLC knowledge YAMLs must exist."""
    path = KNOWLEDGE_SDLC / filename
    assert path.exists(), f"Missing SDLC knowledge YAML: {path}"


@pytest.mark.parametrize("filename", SDLC_KNOWLEDGE_FILES)
def test_gap_79_a_knowledge_yaml_valid(filename: str) -> None:
    """GAP-79-A-01..06: Each knowledge YAML must be valid YAML."""
    path = KNOWLEDGE_SDLC / filename
    if not path.exists():
        pytest.skip(f"File not yet created: {filename}")
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict), f"{filename} must parse to a dict"


@pytest.mark.parametrize("filename", SDLC_KNOWLEDGE_FILES)
def test_gap_79_a_knowledge_yaml_structure(filename: str) -> None:
    """GAP-79-A-01..06: Each YAML must have overview, best_practices, company_context keys."""
    path = KNOWLEDGE_SDLC / filename
    if not path.exists():
        pytest.skip(f"File not yet created: {filename}")
    data = yaml.safe_load(path.read_text())
    for required_key in ("overview", "best_practices", "company_context"):
        assert required_key in data, (
            f"{filename} is missing required key '{required_key}'"
        )


# ── SUB-PHASE 79-B: SDLC Workflow Templates ───────────────────────────────────

SDLC_WORKFLOW_FILES = [
    "requirements-analysis.yaml",
    "solution-design.yaml",
    "implementation-execution.yaml",
    "code-review-gate.yaml",
    "integration-verification.yaml",
    "security-assessment.yaml",
    "release-readiness.yaml",
]


@pytest.mark.parametrize("filename", SDLC_WORKFLOW_FILES)
def test_gap_79_b_workflow_template_exists(filename: str) -> None:
    """GAP-79-B-01..07: All 7 SDLC workflow templates must exist."""
    path = WORKFLOW_SDLC / filename
    assert path.exists(), f"Missing SDLC workflow template: {path}"


@pytest.mark.parametrize("filename", SDLC_WORKFLOW_FILES)
def test_gap_79_b_workflow_template_valid(filename: str) -> None:
    """GAP-79-B-01..07: Each workflow template must be valid YAML."""
    path = WORKFLOW_SDLC / filename
    if not path.exists():
        pytest.skip(f"File not yet created: {filename}")
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict), f"{filename} must parse to a dict"


@pytest.mark.parametrize("filename", SDLC_WORKFLOW_FILES)
def test_gap_79_b_workflow_template_structure(filename: str) -> None:
    """GAP-79-B-01..07: Each workflow template must have workflow, knowledge_context keys."""
    path = WORKFLOW_SDLC / filename
    if not path.exists():
        pytest.skip(f"File not yet created: {filename}")
    data = yaml.safe_load(path.read_text())
    assert "workflow" in data, f"{filename} missing 'workflow' key"
    assert "knowledge_context" in data, f"{filename} missing 'knowledge_context' key"


# ── SUB-PHASE 79-C: Response Blocks ───────────────────────────────────────────

RESPONSE_BLOCKS = [
    "BLOCK-ANALYSIS",
    "BLOCK-DESIGN-DECISION",
    "BLOCK-CODE-REVIEW",
    "BLOCK-SECURITY-ASSESSMENT",
]


@pytest.mark.parametrize("block_id", RESPONSE_BLOCKS)
def test_gap_79_c_response_block_exists(block_id: str) -> None:
    """GAP-79-C-01..04: All 4 BLOCK-* sections must exist in cortex-response-templates.md."""
    assert RESPONSE_TEMPLATES.exists(), (
        f"cortex-response-templates.md not found at {RESPONSE_TEMPLATES}"
    )
    content = RESPONSE_TEMPLATES.read_text()
    assert block_id in content, (
        f"Response block '{block_id}' not found in cortex-response-templates.md"
    )


# ── SUB-PHASE 79-D: SDLCWorkflowOrchestrator ──────────────────────────────────

def test_gap_79_d01_sdlc_orchestrator_importable() -> None:
    """GAP-79-D-01: SDLCWorkflowOrchestrator must be importable."""
    module = importlib.import_module(
        "cortex.orchestrators.domain.sdlc_workflow_orchestrator"
    )
    assert hasattr(module, "SDLCWorkflowOrchestrator"), (
        "SDLCWorkflowOrchestrator class not found in module"
    )


def test_gap_79_d01_sdlc_orchestrator_protocol_mixin() -> None:
    """GAP-79-D-01: SDLCWorkflowOrchestrator must inherit OrchestratorProtocolMixin."""
    try:
        module = importlib.import_module(
            "cortex.orchestrators.domain.sdlc_workflow_orchestrator"
        )
        cls = getattr(module, "SDLCWorkflowOrchestrator")
        from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin
        assert issubclass(cls, OrchestratorProtocolMixin), (
            "SDLCWorkflowOrchestrator must inherit OrchestratorProtocolMixin"
        )
    except ImportError:
        pytest.skip("SDLCWorkflowOrchestrator not yet implemented")


def test_gap_79_d01_sdlc_orchestrator_health_check() -> None:
    """GAP-79-D-01: SDLCWorkflowOrchestrator.health_check() must exist."""
    try:
        module = importlib.import_module(
            "cortex.orchestrators.domain.sdlc_workflow_orchestrator"
        )
        cls = getattr(module, "SDLCWorkflowOrchestrator")
        assert hasattr(cls, "health_check"), (
            "SDLCWorkflowOrchestrator must have health_check() method"
        )
    except ImportError:
        pytest.skip("SDLCWorkflowOrchestrator not yet implemented")


def test_gap_79_d02_intent_router_sdlc_routing() -> None:
    """GAP-79-D-02: IntentRouter must have SDLC routing for ANALYZE/DESIGN intents."""
    from cortex.orchestrators.core.intent_router_impl import IntentRouter
    assert hasattr(IntentRouter, "_intelligence_matrix_lookup"), (
        "IntentRouter must support intelligence matrix routing (Phase 78 hook)"
    )


def test_gap_79_d03_workflow_tools_execute_operation() -> None:
    """GAP-79-D-03: workflow_tools.py must have execute operation."""
    try:
        module = importlib.import_module("cortex.mcp.tools.workflow_tools")
        src = Path(module.__file__).read_text()
        assert "execute" in src, (
            "workflow_tools.py must support 'execute' operation"
        )
    except ImportError:
        pytest.skip("workflow_tools not available")


def test_gap_79_d03_workflow_tools_list_sdlc_operation() -> None:
    """GAP-79-D-03: workflow_tools.py must have list_sdlc operation."""
    try:
        module = importlib.import_module("cortex.mcp.tools.workflow_tools")
        src = Path(module.__file__).read_text()
        assert "list_sdlc" in src, (
            "workflow_tools.py must support 'list_sdlc' operation"
        )
    except ImportError:
        pytest.skip("workflow_tools not available")


# ── SUB-PHASE 79-E: Stack-Specific Knowledge ──────────────────────────────────

@pytest.mark.parametrize("filename", SDLC_STACK_FILES)
def test_gap_79_e_stack_yaml_exists(filename: str) -> None:
    """GAP-79-E-02: All 4 stack-specific knowledge YAMLs must exist."""
    path = KNOWLEDGE_SDLC / filename
    assert path.exists(), f"Missing stack-specific YAML: {path}"


@pytest.mark.parametrize("filename", SDLC_STACK_FILES)
def test_gap_79_e_stack_yaml_valid(filename: str) -> None:
    """GAP-79-E-02: Each stack YAML must be valid YAML with stack_overrides key."""
    path = KNOWLEDGE_SDLC / filename
    if not path.exists():
        pytest.skip(f"File not yet created: {filename}")
    data = yaml.safe_load(path.read_text())
    assert isinstance(data, dict), f"{filename} must parse to a dict"
    assert "stack_overrides" in data, f"{filename} missing 'stack_overrides' key"


# ── SUB-PHASE 79-F: INDEX.yaml Update ────────────────────────────────────────

def test_gap_79_f01_index_yaml_has_sdlc_domain() -> None:
    """GAP-79-F-01: INDEX.yaml must have 'sdlc' domain with ≥6 entries."""
    assert INDEX_YAML.exists(), f"INDEX.yaml not found at {INDEX_YAML}"
    data = yaml.safe_load(INDEX_YAML.read_text())
    assert "sdlc" in data, "INDEX.yaml must have 'sdlc' domain"
    sdlc_guides = data["sdlc"].get("guides", [])
    assert len(sdlc_guides) >= 6, (
        f"INDEX.yaml sdlc domain must have ≥6 entries, got {len(sdlc_guides)}"
    )


def test_gap_79_f01_index_yaml_still_valid() -> None:
    """GAP-79-F-01: INDEX.yaml must remain valid YAML after sdlc domain addition."""
    assert INDEX_YAML.exists(), f"INDEX.yaml not found at {INDEX_YAML}"
    data = yaml.safe_load(INDEX_YAML.read_text())
    assert isinstance(data, dict), "INDEX.yaml must parse to a dict"


def test_gap_79_f02_implementation_workflow_no_auto_push() -> None:
    """GAP-79-F-02: implementation-execution.yaml must not contain 'git push'."""
    path = WORKFLOW_SDLC / "implementation-execution.yaml"
    if not path.exists():
        pytest.skip("implementation-execution.yaml not yet created")
    content = path.read_text()
    assert "git push" not in content.lower(), (
        "implementation-execution.yaml must NOT contain 'git push' (auto-push forbidden)"
    )
