"""
Tests for DocumentOrganizer

Validates document organization functionality including:
- Category detection from filenames and content
- Document moving and organization
- Directory scanning and batch organization
- Index generation
- Statistics reporting
- Edge cases and error handling

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime

from src.workflows.document_organizer import (
    DocumentOrganizer,
    DocumentCategory,
    organize_brain_documents
)


@pytest.fixture
def temp_brain():
    """Create temporary brain directory structure."""
    temp_dir = tempfile.mkdtemp()
    brain_path = Path(temp_dir) / "cortex-brain"
    brain_path.mkdir()
    
    # Create documents directory
    docs_path = brain_path / "documents"
    docs_path.mkdir()
    
    yield brain_path
    
    # Cleanup
    shutil.rmtree(temp_dir)


@pytest.fixture
def organizer(temp_brain):
    """Create DocumentOrganizer instance."""
    return DocumentOrganizer(temp_brain)


@pytest.fixture
def sample_documents(temp_brain):
    """Create sample documents for testing."""
    docs_path = temp_brain / "documents"
    
    samples = {
        "SESSION-REPORT.md": "# TDD Session Report\n\nTest results...",
        "architecture-analysis.md": "# Architecture Analysis\n\nDesign patterns...",
        "project-summary.md": "# Project Summary\n\nProgress overview...",
        "bug-investigation.md": "# Bug Investigation\n\nIssue #123...",
        "PLAN-feature.md": "# Feature Plan\n\nDefinition of Ready...",
        "capture_conversation.md": "# Conversation Capture\n\nUser: ...",
        "setup-guide.md": "# Setup Guide\n\nHow to install..."
    }
    
    paths = {}
    for filename, content in samples.items():
        file_path = docs_path / filename
        file_path.write_text(content, encoding='utf-8')
        paths[filename] = file_path
    
    return paths


class TestDocumentCategory:
    """Test DocumentCategory class."""
    
    def test_all_categories_returns_seven_categories(self):
        """Verify all 7 categories are defined."""
        categories = DocumentCategory.all_categories()
        assert len(categories) == 7
        assert DocumentCategory.REPORTS in categories
        assert DocumentCategory.ANALYSIS in categories
        assert DocumentCategory.SUMMARIES in categories
        assert DocumentCategory.INVESTIGATIONS in categories
        assert DocumentCategory.PLANNING in categories
        assert DocumentCategory.CONVERSATION_CAPTURES in categories
        assert DocumentCategory.IMPLEMENTATION_GUIDES in categories
    
    def test_get_patterns_returns_dict_with_all_categories(self):
        """Verify patterns exist for all categories."""
        patterns = DocumentCategory.get_patterns()
        assert len(patterns) == 7
        for category in DocumentCategory.all_categories():
            assert category in patterns
            assert isinstance(patterns[category], list)
            assert len(patterns[category]) > 0


class TestDocumentOrganizer:
    """Test DocumentOrganizer class."""
    
    def test_initialization_creates_category_directories(self, organizer, temp_brain):
        """Verify all category directories are created on init."""
        docs_path = temp_brain / "documents"
        
        for category in DocumentCategory.all_categories():
            category_path = docs_path / category
            assert category_path.exists()
            assert category_path.is_dir()
    
    def test_detect_category_from_session_report_filename(self, organizer):
        """Test detection of session report category."""
        category = organizer.detect_category("SESSION-EPM-SPRINT1.md")
        assert category == DocumentCategory.REPORTS
    
    def test_detect_category_from_tdd_session_filename(self, organizer):
        """Test detection of TDD session report."""
        category = organizer.detect_category("TDD-SESSION-2025-11-26.md")
        assert category == DocumentCategory.REPORTS
    
    def test_detect_category_from_analysis_filename(self, organizer):
        """Test detection of analysis document."""
        category = organizer.detect_category("architecture-analysis.md")
        assert category == DocumentCategory.ANALYSIS
    
    def test_detect_category_from_summary_filename(self, organizer):
        """Test detection of summary document."""
        category = organizer.detect_category("project-summary.md")
        assert category == DocumentCategory.SUMMARIES
    
    def test_detect_category_from_investigation_filename(self, organizer):
        """Test detection of investigation document."""
        category = organizer.detect_category("bug-investigation.md")
        assert category == DocumentCategory.INVESTIGATIONS
    
    def test_detect_category_from_plan_filename(self, organizer):
        """Test detection of planning document."""
        category = organizer.detect_category("PLAN-authentication.md")
        assert category == DocumentCategory.PLANNING
    
    def test_detect_category_from_ado_filename(self, organizer):
        """Test detection of ADO work item."""
        category = organizer.detect_category("ADO-12345-feature.md")
        assert category == DocumentCategory.PLANNING
    
    def test_detect_category_from_capture_filename(self, organizer):
        """Test detection of conversation capture."""
        category = organizer.detect_category("capture_20251126_143025.md")
        assert category == DocumentCategory.CONVERSATION_CAPTURES
    
    def test_detect_category_from_guide_filename(self, organizer):
        """Test detection of implementation guide."""
        category = organizer.detect_category("setup-guide.md")
        assert category == DocumentCategory.IMPLEMENTATION_GUIDES
    
    def test_detect_category_from_content_with_tdd_keywords(self, organizer):
        """Test content-based detection for TDD sessions."""
        content = "# TDD Session\n\nThis is a test-driven development session report."
        category = organizer.detect_category("document.md", content)
        assert category == DocumentCategory.REPORTS
    
    def test_detect_category_from_content_with_dor_keywords(self, organizer):
        """Test content-based detection for planning docs."""
        content = "# Feature Plan\n\nDefinition of Ready:\n- Requirements documented"
        category = organizer.detect_category("feature.md", content)
        assert category == DocumentCategory.PLANNING
    
    def test_detect_category_returns_none_for_unknown_pattern(self, organizer):
        """Test unknown filename returns None."""
        category = organizer.detect_category("random-file.md")
        assert category is None
    
    def test_organize_document_moves_file_to_correct_category(self, organizer, sample_documents, temp_brain):
        """Test organizing a document moves it to correct category."""
        source_path = sample_documents["SESSION-REPORT.md"]
        
        new_path, message = organizer.organize_document(source_path)
        
        assert new_path is not None
        assert new_path.exists()
        assert new_path.parent.name == DocumentCategory.REPORTS
        assert not source_path.exists()  # Original file moved
        assert "Organized" in message
    
    def test_organize_document_with_explicit_category(self, organizer, sample_documents):
        """Test organizing with explicitly specified category."""
        source_path = sample_documents["project-summary.md"]
        
        new_path, message = organizer.organize_document(
            source_path, 
            category=DocumentCategory.SUMMARIES
        )
        
        assert new_path is not None
        assert new_path.parent.name == DocumentCategory.SUMMARIES
    
    def test_organize_document_handles_collision_with_timestamp(self, organizer, temp_brain):
        """Test collision handling adds timestamp suffix."""
        docs_path = temp_brain / "documents"
        
        # Create first file
        file1 = docs_path / "test-report.md"
        file1.write_text("Report 1", encoding='utf-8')
        
        # Organize first file
        new_path1, _ = organizer.organize_document(file1)
        
        # Create second file with same name
        file2 = docs_path / "test-report.md"
        file2.write_text("Report 2", encoding='utf-8')
        
        # Organize second file (should add timestamp)
        new_path2, _ = organizer.organize_document(file2)
        
        assert new_path1 != new_path2
        assert new_path1.exists()
        assert new_path2.exists()
        assert "-202" in new_path2.stem  # Timestamp pattern
    
    def test_organize_document_dry_run_does_not_move_file(self, organizer, sample_documents):
        """Test dry run mode returns path without moving file."""
        source_path = sample_documents["SESSION-REPORT.md"]
        
        new_path, message = organizer.organize_document(source_path, dry_run=True)
        
        assert new_path is not None
        assert source_path.exists()  # Original still exists
        assert "Would move" in message
    
    def test_organize_document_returns_error_for_nonexistent_file(self, organizer, temp_brain):
        """Test error handling for missing source file."""
        fake_path = temp_brain / "documents" / "nonexistent.md"
        
        new_path, message = organizer.organize_document(fake_path)
        
        assert new_path is None
        assert "not found" in message.lower()
    
    def test_organize_document_returns_error_for_invalid_category(self, organizer, sample_documents):
        """Test error handling for invalid category."""
        source_path = sample_documents["SESSION-REPORT.md"]
        
        new_path, message = organizer.organize_document(
            source_path, 
            category="invalid-category"
        )
        
        assert new_path is None
        assert "Invalid category" in message
    
    def test_organize_document_skips_if_already_organized(self, organizer, temp_brain):
        """Test organizing already-organized file."""
        # Create file directly in reports directory
        reports_path = temp_brain / "documents" / DocumentCategory.REPORTS
        file_path = reports_path / "test-report.md"
        file_path.write_text("Report", encoding='utf-8')
        
        new_path, message = organizer.organize_document(file_path)
        
        assert new_path == file_path
        assert "Already organized" in message
    
    def test_organize_directory_processes_all_markdown_files(self, organizer, sample_documents, temp_brain):
        """Test batch organization of directory."""
        docs_path = temp_brain / "documents"
        
        results = organizer.organize_directory(docs_path, dry_run=False)
        
        assert len(results["success"]) == 7  # All 7 sample files
        assert len(results["failed"]) == 0
    
    def test_organize_directory_skips_readme_files(self, organizer, temp_brain):
        """Test README files are skipped."""
        docs_path = temp_brain / "documents"
        readme = docs_path / "README.md"
        readme.write_text("# README", encoding='utf-8')
        
        results = organizer.organize_directory(docs_path)
        
        # Check README was skipped
        skipped_messages = results.get("skipped", [])
        assert any("README" in msg for msg in skipped_messages)
    
    def test_organize_directory_dry_run_does_not_move_files(self, organizer, sample_documents, temp_brain):
        """Test dry run mode for directory organization."""
        docs_path = temp_brain / "documents"
        
        results = organizer.organize_directory(docs_path, dry_run=True)
        
        assert len(results["success"]) > 0
        # Verify original files still exist
        for file_path in sample_documents.values():
            assert file_path.exists()
    
    def test_generate_category_index_creates_markdown_index(self, organizer, temp_brain):
        """Test index generation for a category."""
        # Add some files to reports category
        reports_path = temp_brain / "documents" / DocumentCategory.REPORTS
        for i in range(3):
            (reports_path / f"report-{i}.md").write_text(f"Report {i}", encoding='utf-8')
        
        index = organizer.generate_category_index(DocumentCategory.REPORTS)
        
        assert "# Reports Index" in index
        assert "**Total Documents:** 3" in index  # Fixed: Match actual output format
        assert "report-0.md" in index
        assert "report-1.md" in index
        assert "report-2.md" in index
    
    def test_generate_category_index_groups_by_date(self, organizer, temp_brain):
        """Test index groups documents by date."""
        reports_path = temp_brain / "documents" / DocumentCategory.REPORTS
        
        # Create files with dates
        (reports_path / "SESSION-2025-11-26-report.md").write_text("Report 1", encoding='utf-8')
        (reports_path / "SESSION-2025-11-27-report.md").write_text("Report 2", encoding='utf-8')
        
        index = organizer.generate_category_index(DocumentCategory.REPORTS)
        
        assert "## 2025-11-26" in index
        assert "## 2025-11-27" in index
    
    def test_generate_category_index_handles_empty_category(self, organizer):
        """Test index generation for empty category."""
        index = organizer.generate_category_index(DocumentCategory.REPORTS)
        
        assert "No documents in this category" in index
    
    def test_update_all_indexes_creates_index_files(self, organizer, temp_brain):
        """Test updating indexes for all categories."""
        results = organizer.update_all_indexes()
        
        assert len(results) == 7
        for category in DocumentCategory.all_categories():
            assert category in results
            # Verify index file exists
            index_path = temp_brain / "documents" / category / "INDEX.md"
            assert index_path.exists()
    
    def test_get_statistics_returns_document_counts(self, organizer, sample_documents, temp_brain):
        """Test statistics reporting."""
        # Organize all sample documents first
        docs_path = temp_brain / "documents"
        organizer.organize_directory(docs_path)
        
        stats = organizer.get_statistics()
        
        assert "categories" in stats
        assert "total_documents" in stats
        assert stats["total_documents"] == 7
        assert stats["categories"][DocumentCategory.REPORTS] >= 1
        assert stats["categories"][DocumentCategory.ANALYSIS] >= 1


class TestConvenienceFunction:
    """Test organize_brain_documents convenience function."""
    
    def test_organize_brain_documents_organizes_all_and_updates_indexes(self, temp_brain, sample_documents):
        """Test full organization with index updates."""
        result = organize_brain_documents(temp_brain, dry_run=False)
        
        assert "results" in result
        assert "statistics" in result
        assert result["results"]["success"]
        assert result["statistics"]["total_documents"] == 7
        
        # Verify indexes created
        for category in DocumentCategory.all_categories():
            index_path = temp_brain / "documents" / category / "INDEX.md"
            assert index_path.exists()
    
    def test_organize_brain_documents_dry_run_preview(self, temp_brain, sample_documents):
        """Test dry run mode for full organization."""
        result = organize_brain_documents(temp_brain, dry_run=True)
        
        assert result["results"]["success"]
        # Verify files not moved
        for file_path in sample_documents.values():
            assert file_path.exists()


class TestEdgeCases:
    """Test edge cases and error scenarios."""
    
    def test_organize_very_large_file_skips_content_detection(self, organizer, temp_brain):
        """Test large files use filename-only detection."""
        docs_path = temp_brain / "documents"
        large_file = docs_path / "large-report.md"
        
        # Create file > 1MB (content detection threshold)
        large_file.write_text("x" * 1_100_000, encoding='utf-8')
        
        # Should still detect from filename
        new_path, message = organizer.organize_document(large_file)
        
        assert new_path is not None
        assert new_path.parent.name == DocumentCategory.REPORTS
    
    def test_organize_unicode_filenames(self, organizer, temp_brain):
        """Test handling of unicode characters in filenames."""
        docs_path = temp_brain / "documents"
        # Use a filename that matches report pattern (repört contains "report")
        unicode_file = docs_path / "SESSION-repört-français-日本語.md"
        unicode_file.write_text("# Test Report", encoding='utf-8')
        
        new_path, message = organizer.organize_document(unicode_file)
        
        assert new_path is not None
        assert new_path.exists()
        assert "reports" in str(new_path)  # Should be organized into reports/
    
    def test_organize_file_with_spaces_in_name(self, organizer, temp_brain):
        """Test handling of spaces in filenames."""
        docs_path = temp_brain / "documents"
        spaced_file = docs_path / "test report with spaces.md"
        spaced_file.write_text("# Test", encoding='utf-8')
        
        new_path, message = organizer.organize_document(spaced_file)
        
        assert new_path is not None
        assert new_path.exists()
