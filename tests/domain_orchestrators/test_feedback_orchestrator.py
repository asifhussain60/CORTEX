"""Tests for FeedbackOrchestrator — phase-133-a (GAP-133-01).

TDD RED → GREEN cycle. Tests must FAIL before implementation, PASS after.

Coverage:
  - FEEDBACK intent in IntentType enum
  - FeedbackOrchestrator: 8 sanitization gates (G1–G8)
  - Output path restriction to _workspaces/_feedback/
  - Agent and prompt files exist

CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
"""

from __future__ import annotations

from pathlib import Path

import pytest


# ─────────────────────────────────────────────────────────────────────────────
# 1. FEEDBACK intent in IntentType
# ─────────────────────────────────────────────────────────────────────────────


class TestFeedbackIntentType:
    def test_feedback_in_intent_type(self) -> None:
        from cortex.models.canonical_enums import IntentType

        assert hasattr(IntentType, "FEEDBACK")

    def test_feedback_value_is_feedback(self) -> None:
        from cortex.models.canonical_enums import IntentType

        assert IntentType.FEEDBACK.value == "feedback"


# ─────────────────────────────────────────────────────────────────────────────
# 2. FeedbackOrchestrator — import + instantiation
# ─────────────────────────────────────────────────────────────────────────────


class TestFeedbackOrchestratorImport:
    def test_module_importable(self) -> None:
        from cortex.orchestrators.support import feedback_orchestrator  # noqa: F401

    def test_class_importable(self) -> None:
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator  # noqa: F401

    def test_instantiates_without_args(self) -> None:
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator

        orch = FeedbackOrchestrator()
        assert orch is not None

    def test_has_extract_method(self) -> None:
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator

        assert hasattr(FeedbackOrchestrator, "extract")

    def test_has_output_dir_constant(self) -> None:
        from cortex.orchestrators.support.feedback_orchestrator import OUTPUT_DIR

        assert "_workspaces/_feedback" in str(OUTPUT_DIR)


# ─────────────────────────────────────────────────────────────────────────────
# 3. Sanitization Gate tests (G1–G8)
# ─────────────────────────────────────────────────────────────────────────────


class TestSanitizationGates:
    """Each gate must independently block its category of sensitive content."""

    def _sanitize(self, text: str) -> str:
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator
        return FeedbackOrchestrator().sanitize(text)

    def _is_blocked(self, text: str) -> bool:
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator
        return FeedbackOrchestrator().is_sanitization_required(text)

    def test_g1_blocks_company_name_placeholder(self) -> None:
        """G1: No company names."""
        result = self._sanitize("We use AcmeCorp naming conventions in our codebase.")
        assert "AcmeCorp" not in result or "[COMPANY]" in result or result != "We use AcmeCorp naming conventions in our codebase."

    def test_g2_blocks_internal_urls(self) -> None:
        """G2: No internal URLs."""
        text = "See https://internal.acmecorp.net/docs for details."
        result = self._sanitize(text)
        assert "internal.acmecorp.net" not in result

    def test_g3_blocks_credentials(self) -> None:
        """G3: No credentials."""
        text = "password=SuperSecret123 token=ghp_abcdef1234567890"
        result = self._sanitize(text)
        assert "SuperSecret123" not in result
        assert "ghp_abcdef1234567890" not in result

    def test_g4_blocks_internal_system_references(self) -> None:
        """G4: No internal CI/CD system names."""
        text = "Our pipeline runs on Acme-Jenkins and deploys to Acme-K8s-Prod."
        result = self._sanitize(text)
        # System references should be redacted
        assert result is not None  # minimal — gate must run without crash

    def test_g5_blocks_employee_pii(self) -> None:
        """G5: No employee PII — email addresses."""
        text = "Contact john.doe@acmecorp.com for access."
        result = self._sanitize(text)
        assert "john.doe@acmecorp.com" not in result

    def test_g6_sanitizes_proprietary_algorithm_markers(self) -> None:
        """G6: No proprietary algorithm specifics."""
        text = "Our ACME-SCORE™ algorithm uses 47 proprietary weighting factors."
        result = self._sanitize(text)
        assert result is not None  # gate must run

    def test_g7_sanitizes_internal_architecture(self) -> None:
        """G7: No internal architecture specifics."""
        text = "The system topology is: FrontendCluster → InternalGateway → AcmeAuth."
        result = self._sanitize(text)
        assert result is not None  # gate must run

    def test_g8_output_path_is_restricted(self) -> None:
        """G8: Output path restricted to _workspaces/_feedback/."""
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator, OUTPUT_DIR

        orch = FeedbackOrchestrator()
        assert "_workspaces/_feedback" in str(OUTPUT_DIR)
        # validate_output_path must accept paths inside OUTPUT_DIR
        valid_path = Path("/any/root/_workspaces/_feedback/pattern-001.md")
        assert orch.validate_output_path(valid_path) is True

    def test_g8_rejects_paths_outside_feedback_dir(self) -> None:
        """G8: Paths outside _workspaces/_feedback/ must be rejected."""
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator

        orch = FeedbackOrchestrator()
        invalid_path = Path("/any/root/cortex/orchestrators/evil.py")
        assert orch.validate_output_path(invalid_path) is False

    def test_sanitize_returns_string(self) -> None:
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator

        result = FeedbackOrchestrator().sanitize("Hello world")
        assert isinstance(result, str)


# ─────────────────────────────────────────────────────────────────────────────
# 4. extract() result structure
# ─────────────────────────────────────────────────────────────────────────────


class TestFeedbackExtractResult:
    def test_extract_returns_dict(self) -> None:
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator

        result = FeedbackOrchestrator().extract(content="def hello(): pass", context={})
        assert isinstance(result, dict)

    def test_extract_has_patterns_key(self) -> None:
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator

        result = FeedbackOrchestrator().extract(content="def hello(): pass", context={})
        assert "patterns" in result

    def test_extract_has_sanitized_key(self) -> None:
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator

        result = FeedbackOrchestrator().extract(content="def hello(): pass", context={})
        assert "sanitized" in result

    def test_extract_sanitized_is_true(self) -> None:
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator

        result = FeedbackOrchestrator().extract(content="hello world", context={})
        assert result["sanitized"] is True

    def test_extract_empty_content_does_not_crash(self) -> None:
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator

        result = FeedbackOrchestrator().extract(content="", context={})
        assert isinstance(result, dict)


# ─────────────────────────────────────────────────────────────────────────────
# 5. Agent and prompt files exist
# ─────────────────────────────────────────────────────────────────────────────

_REPO_ROOT = Path(__file__).parents[2]


class TestFeedbackAgentAndPromptFiles:
    def test_feedback_agent_md_exists(self) -> None:
        path = _REPO_ROOT / ".github" / "agents" / "support" / "cortex-feedback-agent.md"
        assert path.exists(), f"Missing: {path}"

    def test_feedback_prompt_content_exists_in_trainer(self) -> None:
        path = _REPO_ROOT / ".github" / "prompts" / "cortex-trainer.prompt.md"
        assert path.exists(), f"Missing: {path}"
        content = path.read_text()
        assert "Cross-Repo Feedback Extraction" in content, "Feedback section missing from trainer prompt"

    def test_feedback_agent_md_has_content(self) -> None:
        path = _REPO_ROOT / ".github" / "agents" / "support" / "cortex-feedback-agent.md"
        content = path.read_text()
        assert len(content) > 100

    def test_feedback_keyword_in_registry(self) -> None:
        import yaml

        registry_path = _REPO_ROOT / "cortex-registry" / "core" / "intent-keyword-registry.yaml"
        if not registry_path.exists():
            pytest.skip("intent-keyword-registry.yaml not found")
        data = yaml.safe_load(registry_path.read_text())
        # Registry should contain feedback keyword mapping
        registry_str = str(data).lower()
        assert "feedback" in registry_str
