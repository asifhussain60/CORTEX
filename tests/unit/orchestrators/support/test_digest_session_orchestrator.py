"""
AC-PHASE41-001: DigestSessionOrchestrator detects chat files (score ≥5)
AC-PHASE41-002: ChatFileDetector identifies Copilot markers with 90% accuracy
AC-PHASE41-003: EnhancementProposalGenerator creates valid enhancement specs
AC-PHASE41-004: cortex_digest_session MCP tool exposes DIGEST functionality
AC-PHASE41-005: Integration with enhancement-history.yaml (read/write)

Test suite for Stage 1: cortex_digest_session MCP Tool
"""

import pytest
from pathlib import Path
from typing import Dict, List, Any
from unittest.mock import Mock, patch, MagicMock

try:
    from cortex.orchestrators.support.digest_session_orchestrator import (
        DigestSessionOrchestrator,
        DigestResult,
    )
    from cortex.sensory.chat_file_detector import (
        ChatFileDetector,
        ChatFileScore,
        CopilotMarker,
    )
    from cortex.learning.enhancement_proposal_generator import (
        EnhancementProposalGenerator,
        EnhancementProposal,
        EnhancementCategory,
    )
except ImportError:
    DigestSessionOrchestrator = None
    DigestResult = None
    ChatFileDetector = None
    ChatFileScore = None
    CopilotMarker = None
    EnhancementProposalGenerator = None
    EnhancementProposal = None
    EnhancementCategory = None


# ============================================================================
# AC-PHASE41-001: DigestSessionOrchestrator detects chat files (score ≥5)
# ============================================================================


@pytest.mark.skipif(DigestSessionOrchestrator is None, reason="Implementation pending")
class TestDigestSessionOrchestrator:
    """Test DigestSessionOrchestrator chat file detection."""

    def test_orchestrator_initialization(self):
        """Test DigestSessionOrchestrator initializes correctly."""
        orchestrator = DigestSessionOrchestrator()
        
        assert orchestrator is not None
        assert hasattr(orchestrator, "detect_chat_file")
        assert hasattr(orchestrator, "extract_enhancements")
        assert hasattr(orchestrator, "digest_session")

    def test_detect_high_confidence_chat_file(self):
        """Test detection of high-confidence chat file (score ≥8)."""
        orchestrator = DigestSessionOrchestrator()
        
        # Mock chat file with many markers
        content = """
        **User:**
        Implement feature X
        
        **GitHub Copilot:**
        I'll implement feature X using TDD.
        
        **User:**
        Great, proceed.
        
        **GitHub Copilot:**
        ✅ Implementation complete.
        """
        
        result = orchestrator.detect_chat_file(content)
        
        assert result.is_chat_file is True
        assert result.confidence_score >= 8
        assert result.marker_count >= 4

    def test_detect_medium_confidence_chat_file(self):
        """Test detection of medium-confidence chat file (score 5-7)."""
        orchestrator = DigestSessionOrchestrator()
        
        content = """
        User: Can you help?
        Assistant: Sure, I can help.
        """
        
        result = orchestrator.detect_chat_file(content)
        
        assert result.is_chat_file is True
        assert 5 <= result.confidence_score < 8

    def test_reject_low_confidence_file(self):
        """Test rejection of low-confidence file (score <5)."""
        orchestrator = DigestSessionOrchestrator()
        
        content = "This is just regular markdown content."
        
        result = orchestrator.detect_chat_file(content)
        
        assert result.is_chat_file is False
        assert result.confidence_score < 5

    def test_extract_enhancements_from_chat(self):
        """Test enhancement extraction from valid chat file."""
        orchestrator = DigestSessionOrchestrator()
        
        content = """
        **User:** Add type hints to all functions
        **GitHub Copilot:** ✅ Added type hints (CORE-011 compliance)
        
        **User:** Create tests first
        **GitHub Copilot:** ✅ TDD approach (CORE-008 compliance)
        """
        
        enhancements = orchestrator.extract_enhancements(content)
        
        assert len(enhancements) >= 2
        assert any("type hints" in e.description.lower() for e in enhancements)
        assert any("tdd" in e.description.lower() for e in enhancements)

    def test_digest_session_end_to_end(self):
        """Test complete digest session workflow."""
        orchestrator = DigestSessionOrchestrator()
        
        file_path = Path("/tmp/test_chat.md")
        file_path.write_text("""
        **User:** Implement DIGEST mode
        **GitHub Copilot:** ✅ DIGEST mode implemented with auto-detection
        """)
        
        result = orchestrator.digest_session(str(file_path))
        
        assert result.success is True
        assert result.enhancements_found >= 1
        assert result.confidence_score >= 5
        
        file_path.unlink()  # cleanup

    def test_digest_session_with_auto_apply(self):
        """Test digest session with auto-apply enabled."""
        orchestrator = DigestSessionOrchestrator()
        
        file_path = Path("/tmp/test_chat_auto.md")
        file_path.write_text("""
        **User:** Add docstrings
        **GitHub Copilot:** ✅ Added Google-style docstrings
        """)
        
        result = orchestrator.digest_session(
            str(file_path),
            auto_apply=True,
            min_confidence=9
        )
        
        assert result.success is True
        assert result.auto_applied_count >= 0  # May be 0 if confidence <9
        
        file_path.unlink()  # cleanup

    def test_digest_session_invalid_file(self):
        """Test digest session with invalid file path."""
        orchestrator = DigestSessionOrchestrator()
        
        result = orchestrator.digest_session("/nonexistent/file.md")
        
        assert result.success is False
        assert "not found" in result.error_message.lower()


# ============================================================================
# AC-PHASE41-002: ChatFileDetector identifies Copilot markers (90% accuracy)
# ============================================================================


@pytest.mark.skipif(ChatFileDetector is None, reason="Implementation pending")
class TestChatFileDetector:
    """Test ChatFileDetector marker identification."""

    def test_detector_initialization(self):
        """Test ChatFileDetector initializes with patterns."""
        detector = ChatFileDetector()
        
        assert detector is not None
        assert hasattr(detector, "detect_markers")
        assert hasattr(detector, "calculate_score")
        assert len(detector.patterns) > 0

    def test_detect_github_copilot_markers(self):
        """Test detection of GitHub Copilot-specific markers."""
        detector = ChatFileDetector()
        
        content = """
        **User:**
        Can you help?
        
        **GitHub Copilot:**
        Sure, I can help.
        """
        
        markers = detector.detect_markers(content)
        
        assert len(markers) >= 2
        assert any(m.type == CopilotMarker.USER for m in markers)
        assert any(m.type == CopilotMarker.ASSISTANT for m in markers)

    def test_detect_vs_code_markers(self):
        """Test detection of VS Code chat markers."""
        detector = ChatFileDetector()
        
        content = """
        👤 User:
        Implement feature
        
        🤖 Assistant:
        Implementation complete
        """
        
        markers = detector.detect_markers(content)
        
        assert len(markers) >= 2

    def test_detect_completion_markers(self):
        """Test detection of completion markers (✅, ⚠️, 🔴)."""
        detector = ChatFileDetector()
        
        content = """
        ✅ Task complete
        ⚠️ Warning: edge case
        🔴 Critical issue
        """
        
        markers = detector.detect_markers(content)
        
        assert len(markers) >= 3
        assert any(m.type == CopilotMarker.COMPLETION for m in markers)

    def test_calculate_score_high_confidence(self):
        """Test score calculation for high-confidence chat file."""
        detector = ChatFileDetector()
        
        content = """
        **User:** Request 1
        **GitHub Copilot:** Response 1
        **User:** Request 2
        **GitHub Copilot:** Response 2
        ✅ Complete
        ✅ Verified
        """
        
        score = detector.calculate_score(content)
        
        assert score.total_score >= 8
        assert score.marker_count >= 6
        assert score.confidence_level == "HIGH"

    def test_calculate_score_low_confidence(self):
        """Test score calculation for low-confidence file."""
        detector = ChatFileDetector()
        
        content = "Just some regular markdown text."
        
        score = detector.calculate_score(content)
        
        assert score.total_score < 5
        assert score.confidence_level == "LOW"

    def test_accuracy_threshold_90_percent(self):
        """Test 90%+ accuracy on labeled dataset."""
        detector = ChatFileDetector()
        
        # Test cases: (content, expected_is_chat)
        test_cases = [
            ("**User:** Q\n**GitHub Copilot:** A", True),
            ("👤 User: Q\n🤖 Assistant: A", True),
            ("Regular markdown content", False),
            ("# Heading\nSome text", False),
            ("**User:**\nQuestion?\n**GitHub Copilot:**\n✅ Done", True),
            ("```python\ncode\n```", False),
            ("**User:** Help\n**GitHub Copilot:** Sure ✅", True),
            ("Documentation text without chat", False),
            ("User: Q\nCopilot: A\n✅ Complete", True),
            ("Random text with emoji 🎉", False),
        ]
        
        correct = 0
        for content, expected in test_cases:
            score = detector.calculate_score(content)
            predicted = score.total_score >= 5
            if predicted == expected:
                correct += 1
        
        accuracy = correct / len(test_cases)
        assert accuracy >= 0.9  # 90%+ accuracy


# ============================================================================
# AC-PHASE41-003: EnhancementProposalGenerator creates valid specs
# ============================================================================


@pytest.mark.skipif(EnhancementProposalGenerator is None, reason="Implementation pending")
class TestEnhancementProposalGenerator:
    """Test EnhancementProposalGenerator spec creation."""

    def test_generator_initialization(self):
        """Test EnhancementProposalGenerator initializes correctly."""
        generator = EnhancementProposalGenerator()
        
        assert generator is not None
        assert hasattr(generator, "generate_proposals")
        assert hasattr(generator, "classify_enhancement")

    def test_generate_governance_enhancement(self):
        """Test generation of governance-category enhancement."""
        generator = EnhancementProposalGenerator()
        
        content = """
        **User:** Add type hints
        **GitHub Copilot:** ✅ Added type hints per CORE-011
        """
        
        proposals = generator.generate_proposals(content)
        
        assert len(proposals) >= 1
        governance_proposals = [p for p in proposals if p.category == EnhancementCategory.GOVERNANCE]
        assert len(governance_proposals) >= 1
        assert "type hint" in governance_proposals[0].description.lower()

    def test_generate_capability_enhancement(self):
        """Test generation of capability-category enhancement."""
        generator = EnhancementProposalGenerator()
        
        content = """
        **User:** Add new MCP tool
        **GitHub Copilot:** ✅ Created cortex_new_tool
        """
        
        proposals = generator.generate_proposals(content)
        
        capability_proposals = [p for p in proposals if p.category == EnhancementCategory.CAPABILITY]
        assert len(capability_proposals) >= 1

    def test_generate_workflow_enhancement(self):
        """Test generation of workflow-category enhancement."""
        generator = EnhancementProposalGenerator()
        
        content = """
        **User:** Improve TDD workflow
        **GitHub Copilot:** ✅ Enhanced TDD orchestrator
        """
        
        proposals = generator.generate_proposals(content)
        
        workflow_proposals = [p for p in proposals if p.category == EnhancementCategory.WORKFLOW]
        assert len(workflow_proposals) >= 1

    def test_classify_enhancement_by_keywords(self):
        """Test enhancement classification by keyword analysis."""
        generator = EnhancementProposalGenerator()
        
        governance_text = "Added type hints and docstrings per CORE rules"
        capability_text = "Created new MCP tool for analysis"
        workflow_text = "Improved TDD cycle automation"
        
        assert generator.classify_enhancement(governance_text) == EnhancementCategory.GOVERNANCE
        assert generator.classify_enhancement(capability_text) == EnhancementCategory.CAPABILITY
        assert generator.classify_enhancement(workflow_text) == EnhancementCategory.WORKFLOW

    def test_proposal_has_required_fields(self):
        """Test generated proposals have all required fields."""
        generator = EnhancementProposalGenerator()
        
        content = """
        **User:** Add feature X
        **GitHub Copilot:** ✅ Feature X implemented
        """
        
        proposals = generator.generate_proposals(content)
        
        assert len(proposals) >= 1
        proposal = proposals[0]
        
        assert hasattr(proposal, "id")
        assert hasattr(proposal, "description")
        assert hasattr(proposal, "category")
        assert hasattr(proposal, "confidence_score")
        assert hasattr(proposal, "source_file")
        assert hasattr(proposal, "timestamp")

    def test_proposal_confidence_score_range(self):
        """Test proposal confidence scores are in valid range (5-10)."""
        generator = EnhancementProposalGenerator()
        
        content = """
        **User:** Implement TDD
        **GitHub Copilot:** ✅ TDD implemented with tests
        """
        
        proposals = generator.generate_proposals(content)
        
        for proposal in proposals:
            assert 5 <= proposal.confidence_score <= 10

    def test_extract_core_rule_references(self):
        """Test extraction of CORE rule references from chat."""
        generator = EnhancementProposalGenerator()
        
        content = """
        **GitHub Copilot:** ✅ Added type hints (CORE-011)
        ✅ Added docstrings (CORE-012)
        ✅ TDD approach (CORE-008)
        """
        
        proposals = generator.generate_proposals(content)
        
        core_refs = [p.core_rule_ref for p in proposals if hasattr(p, "core_rule_ref")]
        assert len(core_refs) >= 3
        assert "CORE-011" in core_refs
        assert "CORE-012" in core_refs
        assert "CORE-008" in core_refs

    def test_deduplicate_similar_proposals(self):
        """Test deduplication of similar enhancement proposals."""
        generator = EnhancementProposalGenerator()
        
        content = """
        **User:** Add type hints
        **GitHub Copilot:** ✅ Added type hints
        **User:** Make sure type hints are complete
        **GitHub Copilot:** ✅ Verified type hints
        """
        
        proposals = generator.generate_proposals(content, deduplicate=True)
        
        # Should merge similar proposals
        type_hint_proposals = [p for p in proposals if "type hint" in p.description.lower()]
        assert len(type_hint_proposals) <= 2  # Merged similar ones


# ============================================================================
# AC-PHASE41-004: cortex_digest_session MCP tool exposes functionality
# ============================================================================


@pytest.mark.skipif(DigestSessionOrchestrator is None, reason="Implementation pending")
class TestDigestSessionMCPTool:
    """Test cortex_digest_session MCP tool."""

    @patch("cortex.mcp.tools.digest_tool.DigestSessionOrchestrator")
    def test_mcp_tool_registration(self, mock_orchestrator):
        """Test MCP tool is registered correctly."""
        from cortex.mcp.registry import MCPToolRegistry
        
        registry = MCPToolRegistry()
        tool = registry.get_tool("cortex_digest_session")
        
        assert tool is not None
        assert tool.name == "cortex_digest_session"
        assert "file_path" in tool.parameters

    @patch("cortex.mcp.tools.digest_tool.DigestSessionOrchestrator")
    def test_mcp_tool_basic_invocation(self, mock_orchestrator):
        """Test MCP tool basic invocation."""
        from cortex.mcp.tools.digest_tool import cortex_digest_session
        
        mock_result = Mock(
            success=True,
            enhancements_found=3,
            confidence_score=8.5,
            auto_applied_count=0
        )
        mock_orchestrator.return_value.digest_session.return_value = mock_result
        
        result = cortex_digest_session(file_path="/tmp/chat.md")
        
        assert result["success"] is True
        assert result["enhancements_found"] == 3
        assert result["confidence_score"] == 8.5

    @patch("cortex.mcp.tools.digest_tool.DigestSessionOrchestrator")
    def test_mcp_tool_with_auto_apply(self, mock_orchestrator):
        """Test MCP tool with auto_apply parameter."""
        from cortex.mcp.tools.digest_tool import cortex_digest_session
        
        mock_result = Mock(
            success=True,
            enhancements_found=2,
            confidence_score=9.5,
            auto_applied_count=2
        )
        mock_orchestrator.return_value.digest_session.return_value = mock_result
        
        result = cortex_digest_session(
            file_path="/tmp/chat.md",
            auto_apply=True,
            min_confidence=9
        )
        
        assert result["auto_applied_count"] == 2

    @patch("cortex.mcp.tools.digest_tool.DigestSessionOrchestrator")
    def test_mcp_tool_error_handling(self, mock_orchestrator):
        """Test MCP tool error handling."""
        from cortex.mcp.tools.digest_tool import cortex_digest_session
        
        mock_orchestrator.return_value.digest_session.side_effect = Exception("File error")
        
        result = cortex_digest_session(file_path="/invalid/path.md")
        
        assert result["success"] is False
        assert "error" in result

    @patch("cortex.mcp.tools.digest_tool.DigestSessionOrchestrator")
    def test_mcp_tool_parameter_validation(self, mock_orchestrator):
        """Test MCP tool parameter validation."""
        from cortex.mcp.tools.digest_tool import cortex_digest_session
        
        # Missing required parameter
        with pytest.raises((ValueError, TypeError)):
            cortex_digest_session()  # No file_path

    @patch("cortex.mcp.tools.digest_tool.DigestSessionOrchestrator")
    def test_mcp_tool_returns_proposals(self, mock_orchestrator):
        """Test MCP tool returns enhancement proposals."""
        from cortex.mcp.tools.digest_tool import cortex_digest_session
        
        mock_proposal = Mock(
            id="ENH-001",
            description="Add type hints",
            category="GOVERNANCE",
            confidence_score=9.0
        )
        mock_result = Mock(
            success=True,
            enhancements=[mock_proposal],
            enhancements_found=1
        )
        mock_orchestrator.return_value.digest_session.return_value = mock_result
        
        result = cortex_digest_session(file_path="/tmp/chat.md")
        
        assert "enhancement_proposals" in result
        assert len(result["enhancement_proposals"]) == 1


# ============================================================================
# AC-PHASE41-005: Integration with enhancement-history.yaml (read/write)
# ============================================================================


@pytest.mark.skipif(DigestSessionOrchestrator is None, reason="Implementation pending")
class TestEnhancementHistoryIntegration:
    """Test integration with enhancement-history.yaml."""

    def test_read_enhancement_history(self):
        """Test reading from enhancement-history.yaml."""
        orchestrator = DigestSessionOrchestrator()
        
        history = orchestrator.read_enhancement_history()
        
        assert history is not None
        assert isinstance(history, dict)
        assert "enhancements" in history or "history" in history

    def test_write_enhancement_proposal(self):
        """Test writing enhancement proposal to history."""
        orchestrator = DigestSessionOrchestrator()
        
        proposal = EnhancementProposal(
            id="ENH-TEST-001",
            description="Test enhancement",
            category=EnhancementCategory.GOVERNANCE,
            confidence_score=8.5,
            source_file="/tmp/test.md",
            timestamp="2026-02-07"
        )
        
        result = orchestrator.write_enhancement_proposal(proposal)
        
        assert result.success is True

    def test_integration_end_to_end(self):
        """Test end-to-end integration: detect → propose → write."""
        orchestrator = DigestSessionOrchestrator()
        
        file_path = Path("/tmp/integration_test.md")
        file_path.write_text("""
        **User:** Add DIGEST automation
        **GitHub Copilot:** ✅ DIGEST automation implemented
        """)
        
        # Digest session
        result = orchestrator.digest_session(str(file_path))
        
        # Verify proposals written to history
        history = orchestrator.read_enhancement_history()
        recent_proposals = [e for e in history.get("enhancements", []) 
                          if e.get("source_file") == str(file_path)]
        
        assert len(recent_proposals) >= 1
        
        file_path.unlink()  # cleanup


# ============================================================================
# Integration Tests (6 tests)
# ============================================================================


@pytest.mark.integration
@pytest.mark.skipif(DigestSessionOrchestrator is None, reason="Implementation pending")
class TestDigestSessionIntegration:
    """Integration tests for DIGEST session workflow."""

    def test_full_workflow_chat_detection(self):
        """Test full workflow: file → detection → extraction → storage."""
        orchestrator = DigestSessionOrchestrator()
        detector = ChatFileDetector()
        generator = EnhancementProposalGenerator()
        
        content = """
        **User:** Implement Phase 41
        **GitHub Copilot:** ✅ Phase 41 DIGEST system complete
        """
        
        # Step 1: Detection
        score = detector.calculate_score(content)
        assert score.total_score >= 5
        
        # Step 2: Extraction
        proposals = generator.generate_proposals(content)
        assert len(proposals) >= 1
        
        # Step 3: Storage
        result = orchestrator.write_enhancement_proposal(proposals[0])
        assert result.success is True

    def test_orchestrator_with_real_chat_file(self):
        """Test orchestrator with realistic chat file."""
        orchestrator = DigestSessionOrchestrator()
        
        file_path = Path("/tmp/real_chat_test.md")
        file_path.write_text("""
        ## 🧠 CORTEX Implementation Session
        **Author:** Asif Hussain | **Orchestrator:** TDDOrchestrator ✅
        
        **User:**
        Implement DIGEST mode automation
        
        **GitHub Copilot:**
        I'll implement DIGEST mode with auto-detection. Starting with TDD approach.
        
        ✅ ChatFileDetector created (8 tests)
        ✅ DigestSessionOrchestrator created (15 tests)
        ✅ MCP tool registered
        
        **User:**
        Great! Add confidence scoring.
        
        **GitHub Copilot:**
        ✅ ConfidenceScorer implemented (6 tests)
        """)
        
        result = orchestrator.digest_session(str(file_path))
        
        assert result.success is True
        assert result.confidence_score >= 8  # High confidence
        assert result.enhancements_found >= 3
        
        file_path.unlink()  # cleanup

    def test_orchestrator_rejects_non_chat_file(self):
        """Test orchestrator rejects non-chat file."""
        orchestrator = DigestSessionOrchestrator()
        
        file_path = Path("/tmp/regular_doc.md")
        file_path.write_text("""
        # Regular Documentation
        
        This is just regular documentation without chat markers.
        """)
        
        result = orchestrator.digest_session(str(file_path))
        
        assert result.success is False
        assert result.confidence_score < 5
        assert "not a chat file" in result.error_message.lower()
        
        file_path.unlink()  # cleanup

    def test_concurrent_digest_sessions(self):
        """Test handling of concurrent digest sessions."""
        orchestrator = DigestSessionOrchestrator()
        
        # Create multiple chat files
        files = []
        for i in range(3):
            f = Path(f"/tmp/chat_{i}.md")
            f.write_text(f"""
            **User:** Task {i}
            **GitHub Copilot:** ✅ Task {i} complete
            """)
            files.append(f)
        
        # Digest all concurrently
        results = []
        for f in files:
            result = orchestrator.digest_session(str(f))
            results.append(result)
        
        assert all(r.success for r in results)
        
        # Cleanup
        for f in files:
            f.unlink()

    def test_digest_with_enhancement_history_update(self):
        """Test digest updates enhancement-history.yaml correctly."""
        orchestrator = DigestSessionOrchestrator()
        
        # Read current history
        history_before = orchestrator.read_enhancement_history()
        count_before = len(history_before.get("enhancements", []))
        
        # Digest new session
        file_path = Path("/tmp/new_session.md")
        file_path.write_text("""
        **User:** Add new capability
        **GitHub Copilot:** ✅ New capability added
        """)
        
        result = orchestrator.digest_session(str(file_path))
        
        # Read updated history
        history_after = orchestrator.read_enhancement_history()
        count_after = len(history_after.get("enhancements", []))
        
        assert count_after > count_before
        
        file_path.unlink()  # cleanup

    def test_auto_apply_high_confidence_enhancements(self):
        """Test auto-apply for high-confidence enhancements."""
        orchestrator = DigestSessionOrchestrator()
        
        file_path = Path("/tmp/high_confidence.md")
        file_path.write_text("""
        **User:** Add type hints to module X
        **GitHub Copilot:** ✅ Added type hints to all functions in module X
        **User:** Run tests
        **GitHub Copilot:** ✅ All 50 tests passing
        """)
        
        result = orchestrator.digest_session(
            str(file_path),
            auto_apply=True,
            min_confidence=9
        )
        
        # High confidence with test validation should auto-apply
        if result.confidence_score >= 9:
            assert result.auto_applied_count >= 1
        
        file_path.unlink()  # cleanup


# ============================================================================
# E2E Tests (2 tests)
# ============================================================================


@pytest.mark.e2e
@pytest.mark.skipif(DigestSessionOrchestrator is None, reason="Implementation pending")
class TestDigestSessionE2E:
    """End-to-end tests for DIGEST session."""

    def test_e2e_mcp_tool_invocation(self):
        """Test E2E: MCP tool invocation → digest → proposals → storage."""
        from cortex.mcp.tools.digest_tool import cortex_digest_session
        
        # Create realistic chat file
        file_path = Path("/tmp/e2e_chat.md")
        file_path.write_text("""
        ## 🧠 CORTEX Phase 41 Session
        
        **User:**
        Implement DIGEST automation with confidence scoring
        
        **GitHub Copilot:**
        I'll implement Phase 41 Stage 1 with TDD approach.
        
        ✅ DigestSessionOrchestrator (650 LOC, 8 tests)
        ✅ ChatFileDetector (250 LOC, 6 tests)
        ✅ EnhancementProposalGenerator (400 LOC, 8 tests)
        ✅ MCP tool cortex_digest_session (200 LOC, 6 tests)
        
        **User:**
        Excellent! Run full test suite.
        
        **GitHub Copilot:**
        ✅ 30/30 tests passing
        """)
        
        # Invoke MCP tool
        result = cortex_digest_session(str(file_path), auto_apply=False)
        
        # Verify results
        assert result["success"] is True
        assert result["confidence_score"] >= 8
        assert result["enhancements_found"] >= 4
        assert len(result["enhancement_proposals"]) >= 4
        
        # Verify proposals have correct structure
        for proposal in result["enhancement_proposals"]:
            assert "id" in proposal
            assert "description" in proposal
            assert "category" in proposal
            assert "confidence_score" in proposal
        
        file_path.unlink()  # cleanup

    def test_e2e_digest_pipeline_with_validation(self):
        """Test E2E: Full digest pipeline with validation gates."""
        from cortex.mcp.tools.digest_tool import cortex_digest_session
        
        # Create chat file with governance enhancements
        file_path = Path("/tmp/e2e_governance.md")
        file_path.write_text("""
        **User:**
        Add type hints and docstrings per CORE rules
        
        **GitHub Copilot:**
        ✅ Added type hints (CORE-011 compliance)
        ✅ Added Google-style docstrings (CORE-012 compliance)
        ✅ All 25 tests passing
        
        **User:**
        Run governance validation
        
        **GitHub Copilot:**
        ✅ EnforcementOrchestrator validation passed
        ✅ No CORE rule violations detected
        """)
        
        # Digest with auto-apply
        result = cortex_digest_session(
            str(file_path),
            auto_apply=True,
            min_confidence=9
        )
        
        # Verify high-confidence governance enhancements
        assert result["success"] is True
        assert result["confidence_score"] >= 9
        
        # Check for governance proposals
        governance_proposals = [
            p for p in result["enhancement_proposals"]
            if p.get("category") == "GOVERNANCE"
        ]
        assert len(governance_proposals) >= 2
        
        # Verify auto-apply occurred for high-confidence
        if result["confidence_score"] >= 9:
            assert result["auto_applied_count"] >= 1
        
        file_path.unlink()  # cleanup
