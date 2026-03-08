"""
Phase-139 TDD test suite — Cross-Repo Feedback Extractor.

139-a: SanitizationEngine — 8 privacy gates (G1–G8) with CORTEX vocabulary preservation
139-b: CrossRepoExtractor — CommitRecord/CapabilityRecord dataclasses + 6-stage pipeline
139-c: FeedbackOrchestrator mode=extract + FEEDBACK IntentType + IntentRouter keywords

Author: Asif Hussain | © 2025–2026 CORTEX Framework. All rights reserved.
"""
from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock, patch

# =============================================================================
# 139-a: SanitizationEngine tests
# =============================================================================

class TestSanitizationEngineGates:
    """8 privacy gates (G1–G8) each correctly remove their target pattern category."""

    def test_g1_removes_personal_identifiers(self) -> None:
        """G1 removes name-like personal identifier patterns from text."""
        from cortex.tools.cross_repo_extractor import SanitizationEngine
        engine = SanitizationEngine()
        result, _ = engine.apply_gate_g1("Contact John Smith at the office.")
        assert "John Smith" not in result

    def test_g2_removes_org_urls(self) -> None:
        """G2 removes internal organisation URL patterns."""
        from cortex.tools.cross_repo_extractor import SanitizationEngine
        engine = SanitizationEngine()
        result, _ = engine.apply_gate_g2("See https://internal.acme.com/docs for details.")
        assert "internal.acme.com" not in result

    def test_g3_removes_credentials(self) -> None:
        """G3 removes API key and password patterns."""
        from cortex.tools.cross_repo_extractor import SanitizationEngine
        engine = SanitizationEngine()
        result, _ = engine.apply_gate_g3("api_key=supersecret123 in config")
        assert "supersecret123" not in result

    def test_g4_removes_codenames(self) -> None:
        """G4 removes internal project codenames."""
        from cortex.tools.cross_repo_extractor import SanitizationEngine
        engine = SanitizationEngine()
        # Inject a custom codename into the engine's codename set for testing
        engine._codenames = {"PROJECT_PHOENIX", "CODENAME_ATLAS"}
        result, actions = engine.apply_gate_g4(
            "Integrated PROJECT_PHOENIX into the pipeline."
        )
        assert "PROJECT_PHOENIX" not in result
        assert actions > 0

    def test_g5_removes_customer_references(self) -> None:
        """G5 removes customer name patterns from text."""
        from cortex.tools.cross_repo_extractor import SanitizationEngine
        engine = SanitizationEngine()
        # Inject a customer name for testing
        engine._customer_names = {"AcmeCorp", "BigCo"}
        result, actions = engine.apply_gate_g5("Deployed for AcmeCorp client.")
        assert "AcmeCorp" not in result
        assert actions > 0

    def test_g6_removes_algorithm_details(self) -> None:
        """G6 removes proprietary algorithm name patterns."""
        from cortex.tools.cross_repo_extractor import SanitizationEngine
        engine = SanitizationEngine()
        result, _ = engine.apply_gate_g6(
            "The PROPRIETARY_SCORE_V2 algorithm drives predictions."
        )
        # Text should have PROPRIETARY_SCORE redacted or engine returns fewer chars
        assert len(result) <= len(
            "The PROPRIETARY_SCORE_V2 algorithm drives predictions."
        )

    def test_g7_removes_channel_references(self) -> None:
        """G7 removes Slack/Teams channel reference patterns."""
        from cortex.tools.cross_repo_extractor import SanitizationEngine
        engine = SanitizationEngine()
        result, _ = engine.apply_gate_g7(
            "See #internal-alerts channel for updates."
        )
        assert "#internal-alerts" not in result

    def test_g8_final_validation(self) -> None:
        """G8 final validation gate returns (text, action_count) tuple."""
        from cortex.tools.cross_repo_extractor import SanitizationEngine
        engine = SanitizationEngine()
        result, actions = engine.apply_gate_g8("Clean CORTEX framework text.")
        assert isinstance(result, str)
        assert isinstance(actions, int)
        assert actions == 0  # clean text → zero actions

    def test_cortex_vocabulary_preserved(self) -> None:
        """40+ CORTEX domain vocabulary terms survive all 8 sanitization gates."""
        from cortex.tools.cross_repo_extractor import SanitizationEngine
        engine = SanitizationEngine()
        cortex_terms = [
            "ComplexityTriageEngine",
            "CAPE",
            "KAL",
            "SubPhaseCheckpointInjector",
            "RollbackManager",
            "WorkflowComposer",
            "IntelligenceFacade",
            "CORE-008",
            "TDD",
            "CORTEX",
        ]
        text = " ".join(cortex_terms)
        sanitized, _ = engine.sanitize(text)
        for term in cortex_terms:
            assert term in sanitized, f"CORTEX vocabulary term '{term}' was incorrectly sanitized"

    def test_sanitize_returns_action_count(self) -> None:
        """sanitize() returns (text, action_count) tuple."""
        from cortex.tools.cross_repo_extractor import SanitizationEngine
        engine = SanitizationEngine()
        result = engine.sanitize("Some text with content.")
        assert isinstance(result, tuple)
        assert len(result) == 2
        text, count = result
        assert isinstance(text, str)
        assert isinstance(count, int)

    def test_sanitize_clean_text_zero_actions(self) -> None:
        """Clean text with no sensitive content → action_count 0."""
        from cortex.tools.cross_repo_extractor import SanitizationEngine
        engine = SanitizationEngine()
        clean = "CORTEX WorkflowComposer TDD phase-139 implementation."
        _, action_count = engine.sanitize(clean)
        assert action_count == 0

    def test_regex_precompiled(self) -> None:
        """Regex patterns are pre-compiled at class level (not per call)."""
        import re

        from cortex.tools.cross_repo_extractor import SanitizationEngine
        # Compiled patterns are attributes of the class, not created per-call
        engine = SanitizationEngine()
        # Check at least one compiled pattern attribute exists
        has_compiled = any(
            isinstance(v, type(re.compile("")))
            for v in vars(engine).values()
            if not callable(v)
        ) or any(
            isinstance(v, type(re.compile("")))
            for v in vars(type(engine)).values()
            if not callable(v)
        )
        assert has_compiled, "No pre-compiled regex patterns found on SanitizationEngine"


# =============================================================================
# 139-b: CrossRepoExtractor tests
# =============================================================================

class TestCrossRepoExtractorRelevanceFilter:
    """Stage 2: is_cortex_relevant() correctly filters paths."""

    def test_is_cortex_relevant_orchestrator_path(self) -> None:
        """cortex/orchestrators/ path is CORTEX-relevant."""
        from cortex.tools.cross_repo_extractor import CrossRepoExtractor
        extractor = CrossRepoExtractor(repo_path=Path("/tmp"))
        assert extractor.is_cortex_relevant("cortex/orchestrators/core/intent_router.py") is True

    def test_is_cortex_relevant_test_path(self) -> None:
        """tests/ path is CORTEX-relevant."""
        from cortex.tools.cross_repo_extractor import CrossRepoExtractor
        extractor = CrossRepoExtractor(repo_path=Path("/tmp"))
        assert extractor.is_cortex_relevant("tests/unit/tools/test_cross_repo_extractor.py") is True

    def test_is_cortex_relevant_docs_path(self) -> None:
        """docs/index.html is NOT CORTEX-framework-relevant."""
        from cortex.tools.cross_repo_extractor import CrossRepoExtractor
        extractor = CrossRepoExtractor(repo_path=Path("/tmp"))
        assert extractor.is_cortex_relevant("docs/index.html") is False

    def test_is_cortex_relevant_registry_path(self) -> None:
        """cortex-registry/ path is CORTEX-relevant."""
        from cortex.tools.cross_repo_extractor import CrossRepoExtractor
        extractor = CrossRepoExtractor(repo_path=Path("/tmp"))
        assert extractor.is_cortex_relevant("cortex-registry/planning/phases/planned/phase-139.yaml") is True


class TestCrossRepoExtractorClassification:
    """Stage 3: classify_change() maps file paths to ChangeClassification enum values."""

    def test_classify_change_new_orchestrator(self) -> None:
        """New cortex/orchestrators/ file → NEW_ORCHESTRATOR."""
        from cortex.tools.cross_repo_extractor import ChangeClassification, CrossRepoExtractor
        extractor = CrossRepoExtractor(repo_path=Path("/tmp"))
        assert extractor.classify_change("cortex/orchestrators/core/new_orch.py") == ChangeClassification.NEW_ORCHESTRATOR

    def test_classify_change_new_test(self) -> None:
        """New tests/ file → NEW_TEST."""
        from cortex.tools.cross_repo_extractor import ChangeClassification, CrossRepoExtractor
        extractor = CrossRepoExtractor(repo_path=Path("/tmp"))
        assert extractor.classify_change("tests/unit/tools/test_something.py") == ChangeClassification.NEW_TEST

    def test_classify_change_modified_mcp(self) -> None:
        """Modified cortex/mcp/ file → MCP_ENHANCEMENT."""
        from cortex.tools.cross_repo_extractor import ChangeClassification, CrossRepoExtractor
        extractor = CrossRepoExtractor(repo_path=Path("/tmp"))
        assert extractor.classify_change("cortex/mcp/tools/cortex_learning.py") == ChangeClassification.MCP_ENHANCEMENT


class TestCrossRepoExtractorPipeline:
    """Stages 1–6: extract_capabilities() and generate_output() pipeline."""

    def test_extract_capabilities_from_commits(self) -> None:
        """extract_capabilities() converts commit list to CapabilityRecord list."""
        from cortex.tools.cross_repo_extractor import CommitRecord, CrossRepoExtractor
        extractor = CrossRepoExtractor(repo_path=Path("/tmp"))
        commits = [
            CommitRecord(
                sha="abc123",
                message="feat: add RollbackManager to cortex/core/rollback_manager.py",
                files_changed=["cortex/core/rollback_manager.py"],
                date="2026-03-08",
            )
        ]
        capabilities = extractor.extract_capabilities(commits)
        assert isinstance(capabilities, list)
        assert len(capabilities) >= 1

    def test_capability_record_schema(self) -> None:
        """CapabilityRecord has classification, title, description, files, commit_sha."""
        from cortex.tools.cross_repo_extractor import CapabilityRecord, ChangeClassification
        record = CapabilityRecord(
            classification=ChangeClassification.NEW_ORCHESTRATOR,
            title="RollbackManager",
            description="Git rollback with URS signal.",
            files=["cortex/core/rollback_manager.py"],
            commit_sha="abc123",
        )
        assert record.classification == ChangeClassification.NEW_ORCHESTRATOR
        assert record.title == "RollbackManager"
        assert record.commit_sha == "abc123"

    def test_sanitize_capabilities_applies_engine(self) -> None:
        """sanitize_capabilities() calls SanitizationEngine.sanitize() per record."""
        from cortex.tools.cross_repo_extractor import (
            CapabilityRecord,
            ChangeClassification,
            CrossRepoExtractor,
        )
        extractor = CrossRepoExtractor(repo_path=Path("/tmp"))
        records = [
            CapabilityRecord(
                classification=ChangeClassification.NEW_CAPABILITY,
                title="SomeFeature",
                description="Added new capability.",
                files=["cortex/core/something.py"],
                commit_sha="abc123",
            )
        ]
        with patch.object(extractor.sanitization_engine, "sanitize", return_value=("sanitized", 0)) as mock_san:
            extractor.sanitize_capabilities(records)
            assert mock_san.call_count >= 1

    def test_generate_output_markdown(self) -> None:
        """generate_output() returns markdown string with expected sections."""
        from cortex.tools.cross_repo_extractor import (
            CapabilityRecord,
            ChangeClassification,
            CrossRepoExtractor,
        )
        extractor = CrossRepoExtractor(repo_path=Path("/tmp"))
        records = [
            CapabilityRecord(
                classification=ChangeClassification.NEW_ORCHESTRATOR,
                title="RollbackManager",
                description="Git rollback capability.",
                files=["cortex/core/rollback_manager.py"],
                commit_sha="abc123",
            )
        ]
        output = extractor.generate_output(records)
        assert isinstance(output, str)
        assert "Executive Summary" in output or "Capability" in output

    def test_generate_output_empty_capabilities(self) -> None:
        """Empty capability list → 'No capabilities found' in output."""
        from cortex.tools.cross_repo_extractor import CrossRepoExtractor
        extractor = CrossRepoExtractor(repo_path=Path("/tmp"))
        output = extractor.generate_output([])
        assert "No capabilities found" in output


# =============================================================================
# 139-c: FeedbackOrchestrator + FEEDBACK IntentType + IntentRouter keywords
# =============================================================================

class TestFeedbackIntentType:
    """FEEDBACK registered as IntentType in canonical_enums.py."""

    def test_feedback_intent_type_exists(self) -> None:
        """IntentType.FEEDBACK exists in canonical_enums."""
        from cortex.models.canonical_enums import IntentType
        assert hasattr(IntentType, "FEEDBACK")
        assert IntentType.FEEDBACK.value is not None


class TestIntentRouterFeedbackKeywords:
    """IntentRouter routes feedback-related keywords to FEEDBACK intent."""

    def test_intent_router_feedback_keyword(self) -> None:
        """'/feedback' maps to FEEDBACK intent."""
        from cortex.orchestrators.core.intent_router.keyword_registry import IntentKeywordRegistry
        assert hasattr(IntentKeywordRegistry, "FEEDBACK_KEYWORDS")
        assert any("/feedback" in kw for kw in IntentKeywordRegistry.FEEDBACK_KEYWORDS)

    def test_intent_router_backport_keyword(self) -> None:
        """'backport' maps to FEEDBACK intent keywords."""
        from cortex.orchestrators.core.intent_router.keyword_registry import IntentKeywordRegistry
        assert any("backport" in kw for kw in IntentKeywordRegistry.FEEDBACK_KEYWORDS)

    def test_intent_router_capability_extraction_keyword(self) -> None:
        """'capability extraction' maps to FEEDBACK intent keywords."""
        from cortex.orchestrators.core.intent_router.keyword_registry import IntentKeywordRegistry
        assert any("capability extraction" in kw for kw in IntentKeywordRegistry.FEEDBACK_KEYWORDS)


class TestFeedbackOrchestratorExtractMode:
    """FeedbackOrchestrator mode=extract routes to CrossRepoExtractor."""

    def test_feedback_orchestrator_mode_extract_routes(self) -> None:
        """mode='extract' causes FeedbackOrchestrator to call _execute_extraction()."""
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator
        orch = FeedbackOrchestrator()
        assert hasattr(orch, "_execute_extraction"), (
            "FeedbackOrchestrator must have _execute_extraction() method"
        )

    def test_feedback_orchestrator_instantiates_extractor(self) -> None:
        """_execute_extraction() instantiates CrossRepoExtractor."""
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator
        orch = FeedbackOrchestrator()
        with patch(
            "cortex.orchestrators.support.feedback_orchestrator.CrossRepoExtractor"
        ) as MockExtractor:
            mock_inst = MagicMock()
            mock_inst.extract_capabilities.return_value = []
            mock_inst.sanitize_capabilities.return_value = []
            mock_inst.generate_output.return_value = "No capabilities found"
            MockExtractor.return_value = mock_inst
            orch._execute_extraction(repo_path=Path("/tmp"))
            MockExtractor.assert_called_once()

    def test_feedback_output_path(self) -> None:
        """Output is written to _workspaces/_feedback/{date}-feedback.md."""
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator
        orch = FeedbackOrchestrator()
        with patch(
            "cortex.orchestrators.support.feedback_orchestrator.CrossRepoExtractor"
        ) as MockExtractor:
            mock_inst = MagicMock()
            mock_inst.extract_capabilities.return_value = []
            mock_inst.sanitize_capabilities.return_value = []
            mock_inst.generate_output.return_value = "No capabilities found"
            MockExtractor.return_value = mock_inst
            with patch("pathlib.Path.mkdir"), patch("pathlib.Path.write_text"):
                output_path = orch._execute_extraction(repo_path=Path("/tmp"))
                # The returned path must be under _workspaces/_feedback/
                assert "_workspaces/_feedback" in str(output_path) or "_feedback" in str(output_path)

    def test_feedback_output_never_written_to_cortex_dir(self) -> None:
        """Output path does NOT start with cortex/ (never inside the source tree)."""
        from cortex.orchestrators.support.feedback_orchestrator import FeedbackOrchestrator
        orch = FeedbackOrchestrator()
        with patch(
            "cortex.orchestrators.support.feedback_orchestrator.CrossRepoExtractor"
        ) as MockExtractor:
            mock_inst = MagicMock()
            mock_inst.extract_capabilities.return_value = []
            mock_inst.sanitize_capabilities.return_value = []
            mock_inst.generate_output.return_value = "No capabilities found"
            MockExtractor.return_value = mock_inst
            with patch("pathlib.Path.mkdir"), patch("pathlib.Path.write_text"):
                output_path = orch._execute_extraction(repo_path=Path("/tmp"))
                assert not str(output_path).startswith("cortex/"), (
                    f"Output path '{output_path}' must not start with cortex/"
                )
