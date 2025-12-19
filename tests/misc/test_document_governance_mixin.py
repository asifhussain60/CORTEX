"""
Tests for Document Governance Mixin.

This module validates centralized document creation with organization enforcement.
"""

import pytest
from pathlib import Path
from src.governance.mixins.document_governance_mixin import DocumentGovernanceMixin


class TestOrchestrator(DocumentGovernanceMixin):
    """Test orchestrator using the mixin."""
    
    def __init__(self, brain_path: Path):
        self.brain_path = brain_path


class TestDocumentGovernanceMixin:
    """Test document governance mixin functionality."""
    
    def test_create_document_in_valid_category(self, tmp_path):
        """Verify document creation in valid category succeeds."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        (brain_path / "documents").mkdir()
        (brain_path / "documents" / "reports").mkdir()
        
        orchestrator = TestOrchestrator(brain_path)
        
        result_path = orchestrator.create_document_safely(
            category="reports",
            filename="test-report.md",
            content="# Test Report\n\nContent here."
        )
        
        assert result_path.exists()
        assert result_path.name == "test-report.md"
        assert "reports" in str(result_path)
    
    def test_create_document_blocks_root_level(self, tmp_path):
        """Verify document creation in root is blocked."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        orchestrator = TestOrchestrator(brain_path)
        
        with pytest.raises(ValueError, match="root-level document creation blocked"):
            orchestrator.create_document_safely(
                category="",
                filename="root-doc.md",
                content="This should fail."
            )
    
    def test_create_document_validates_category(self, tmp_path):
        """Verify invalid category is rejected."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        
        orchestrator = TestOrchestrator(brain_path)
        
        with pytest.raises(ValueError, match="Invalid category"):
            orchestrator.create_document_safely(
                category="invalid_category",
                filename="doc.md",
                content="Content"
            )
    
    def test_create_document_creates_category_if_missing(self, tmp_path):
        """Verify category directory is created if it doesn't exist."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        (brain_path / "documents").mkdir()
        
        orchestrator = TestOrchestrator(brain_path)
        
        result_path = orchestrator.create_document_safely(
            category="analysis",
            filename="new-analysis.md",
            content="# Analysis\n\nData here."
        )
        
        assert (brain_path / "documents" / "analysis").exists()
        assert result_path.exists()
    
    def test_create_document_returns_absolute_path(self, tmp_path):
        """Verify returned path is absolute."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        (brain_path / "documents").mkdir()
        (brain_path / "documents" / "summaries").mkdir()
        
        orchestrator = TestOrchestrator(brain_path)
        
        result_path = orchestrator.create_document_safely(
            category="summaries",
            filename="summary.md",
            content="# Summary\n\nText."
        )
        
        assert result_path.is_absolute()
    
    def test_create_document_content_written_correctly(self, tmp_path):
        """Verify document content is written as expected."""
        brain_path = tmp_path / "cortex-brain"
        brain_path.mkdir()
        (brain_path / "documents").mkdir()
        (brain_path / "documents" / "reports").mkdir()
        
        orchestrator = TestOrchestrator(brain_path)
        expected_content = "# Test Report\n\nThis is a test."
        
        result_path = orchestrator.create_document_safely(
            category="reports",
            filename="content-test.md",
            content=expected_content
        )
        
        actual_content = result_path.read_text()
        assert actual_content == expected_content
