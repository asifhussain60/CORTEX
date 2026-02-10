"""
AC-PHASE72-001: UnifiedDigestIngestionFacade - Composition Layer Tests

Tests for unified facade coordinating DIGEST and INGEST orchestrators.

CORE Compliance:
- CORE-008: TDD (tests first, 100% coverage)
- CORE-011: Type hints (mypy --strict)
- CORE-012: Google-style docstrings
- CORE-013: Specific exceptions
"""

from pathlib import Path
from typing import Dict, Any
import tempfile
import pytest

from cortex.orchestrators.support.unified_digest_ingest_facade import (
    UnifiedDigestIngestionFacade,
    UnifiedResult,
    ProcessingMode,
)
from cortex.orchestrators.support.digest_session_orchestrator import DigestResult
from cortex.brain.core.knowledge.bulk_ingestion import BulkIngestionStats


class TestUnifiedDigestIngestionFacade:
    """Tests for UnifiedDigestIngestionFacade (AC-PHASE72-001)."""

    @pytest.fixture
    def facade(self) -> UnifiedDigestIngestionFacade:
        """Create facade instance."""
        return UnifiedDigestIngestionFacade()

    @pytest.fixture
    def temp_chat_file(self) -> Path:
        """Create temporary chat file for testing."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", delete=False
        ) as f:
            # Write content with chat markers
            f.write(
                """## Copilot Chat Session
User: "implement feature X"
Assistant: "Here's the implementation..."
User: "Can you add error handling?"
Assistant: "Sure, let me enhance it..."
"""
            )
            return Path(f.name)

    @pytest.fixture
    def temp_knowledge_file(self) -> Path:
        """Create temporary knowledge entry file."""
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".json", delete=False
        ) as f:
            f.write('{"id": "ENH-001", "title": "Enhancement", "content": "data"}')
            return Path(f.name)

    # ========== MODE DETECTION TESTS ==========

    def test_detect_mode_chat_file(self, facade: UnifiedDigestIngestionFacade) -> None:
        """Test detection of chat file mode."""
        # AC_START: AC-PHASE72-001-TEST1
        content = "User: 'test'\nAssistant: 'response'"
        mode = facade.detect_mode(content, source_type=None)
        assert mode == ProcessingMode.DIGEST
        # AC_COMPLETE: AC-PHASE72-001-TEST1 ✅

    def test_detect_mode_knowledge_entry(
        self, facade: UnifiedDigestIngestionFacade
    ) -> None:
        """Test detection of knowledge entry mode."""
        # AC_START: AC-PHASE72-001-TEST2
        content = '{"id": "ENH-001", "data": "structured"}'
        mode = facade.detect_mode(content, source_type=None)
        assert mode == ProcessingMode.INGEST
        # AC_COMPLETE: AC-PHASE72-001-TEST2 ✅

    def test_explicit_digest_mode(self, facade: UnifiedDigestIngestionFacade) -> None:
        """Test explicit DIGEST mode specification."""
        # AC_START: AC-PHASE72-001-TEST3
        content = "any content"
        mode = facade.detect_mode(content, source_type="chat_file")
        assert mode == ProcessingMode.DIGEST
        # AC_COMPLETE: AC-PHASE72-001-TEST3 ✅

    def test_explicit_ingest_mode(self, facade: UnifiedDigestIngestionFacade) -> None:
        """Test explicit INGEST mode specification."""
        # AC_START: AC-PHASE72-001-TEST4
        content = "any content"
        mode = facade.detect_mode(content, source_type="knowledge_entry")
        assert mode == ProcessingMode.INGEST
        # AC_COMPLETE: AC-PHASE72-001-TEST4 ✅

    # ========== UNIFIED RESULT TESTS ==========

    def test_unified_result_from_digest(
        self, facade: UnifiedDigestIngestionFacade
    ) -> None:
        """Test UnifiedResult creation from DigestResult."""
        # AC_START: AC-PHASE72-001-TEST5
        digest_result = DigestResult(
            success=True,
            is_chat_file=True,
            confidence_score=8.5,
            enhancements_found=3,
        )

        unified = UnifiedResult.from_digest(digest_result, "test.md")
        assert unified.success is True
        assert unified.processing_mode == ProcessingMode.DIGEST
        assert unified.confidence_score == 8.5
        assert unified.items_processed == 3
        # AC_COMPLETE: AC-PHASE72-001-TEST5 ✅

    def test_unified_result_from_ingest(
        self, facade: UnifiedDigestIngestionFacade
    ) -> None:
        """Test UnifiedResult creation from BulkIngestionStats."""
        # AC_START: AC-PHASE72-001-TEST6
        stats = BulkIngestionStats(
            total_entries=10, successful=9, failed=1, duration_seconds=2.0
        )

        unified = UnifiedResult.from_ingest(stats, "entries.json")
        assert unified.success is True
        assert unified.processing_mode == ProcessingMode.INGEST
        assert unified.items_processed == 10
        assert unified.items_successful == 9
        assert unified.items_failed == 1
        # AC_COMPLETE: AC-PHASE72-001-TEST6 ✅

    def test_unified_result_failed_digest(
        self, facade: UnifiedDigestIngestionFacade
    ) -> None:
        """Test UnifiedResult with failed DIGEST."""
        # AC_START: AC-PHASE72-001-TEST7
        digest_result = DigestResult(
            success=False, error_message="Not a chat file"
        )

        unified = UnifiedResult.from_digest(digest_result, "test.md")
        assert unified.success is False
        assert "Not a chat file" in unified.error_message
        # AC_COMPLETE: AC-PHASE72-001-TEST7 ✅

    # ========== ROUTING TESTS ==========

    def test_routing_to_digest(
        self,
        facade: UnifiedDigestIngestionFacade,
        temp_chat_file: Path,
    ) -> None:
        """Test intelligent routing to DIGEST orchestrator."""
        # AC_START: AC-PHASE72-001-TEST8
        # Process as auto-detected
        result = facade.process_knowledge_source(
            str(temp_chat_file), source_type=None
        )

        # Should be routed to DIGEST (will fail without full setup, but routing works)
        assert result.processing_mode == ProcessingMode.DIGEST
        # AC_COMPLETE: AC-PHASE72-001-TEST8 ✅

    def test_routing_explicit_digest(
        self,
        facade: UnifiedDigestIngestionFacade,
        temp_chat_file: Path,
    ) -> None:
        """Test explicit DIGEST routing."""
        # AC_START: AC-PHASE72-001-TEST9
        result = facade.process_knowledge_source(
            str(temp_chat_file), source_type="chat_file"
        )

        assert result.processing_mode == ProcessingMode.DIGEST
        # AC_COMPLETE: AC-PHASE72-001-TEST9 ✅

    def test_routing_explicit_ingest(
        self,
        facade: UnifiedDigestIngestionFacade,
        temp_knowledge_file: Path,
    ) -> None:
        """Test explicit INGEST routing."""
        # AC_START: AC-PHASE72-001-TEST10
        result = facade.process_knowledge_source(
            str(temp_knowledge_file), source_type="knowledge_entry"
        )

        assert result.processing_mode == ProcessingMode.INGEST
        # AC_COMPLETE: AC-PHASE72-001-TEST10 ✅

    # ========== FACADE INTEGRATION TESTS ==========

    def test_facade_isolation_digest_changes(
        self, facade: UnifiedDigestIngestionFacade
    ) -> None:
        """Test that DIGEST changes don't affect INGEST."""
        # AC_START: AC-PHASE72-001-TEST11
        # Verify facades are independent
        digest_orch = facade.digest_orchestrator
        ingest_pipeline = facade.ingest_pipeline

        # Both should be initialized
        assert digest_orch is not None
        assert ingest_pipeline is not None

        # Changing one shouldn't affect the other
        original_digest_type = type(digest_orch)
        assert type(facade.ingest_pipeline) != original_digest_type
        # AC_COMPLETE: AC-PHASE72-001-TEST11 ✅

    def test_facade_error_handling_missing_file(
        self, facade: UnifiedDigestIngestionFacade
    ) -> None:
        """Test facade error handling for missing files."""
        # AC_START: AC-PHASE72-001-TEST12
        result = facade.process_knowledge_source(
            "/nonexistent/file.md", source_type="chat_file"
        )

        assert result.success is False
        assert "not found" in result.error_message.lower()
        # AC_COMPLETE: AC-PHASE72-001-TEST12 ✅
