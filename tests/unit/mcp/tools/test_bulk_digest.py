"""
Tests for Bulk Digest Tool - AC-BULK-DIGEST-001

Test suite for cortex_bulk_digest_files MCP tool.
Validates bulk markdown ingestion with intelligent routing and cleanup.
"""

import pytest
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock


class TestBulkDigestTool:
    """Test cortex_bulk_digest_files MCP tool."""
    
    def test_tool_exists(self) -> None:
        """Test bulk digest tool is importable."""
        from cortex.mcp.tools.bulk_digest import cortex_bulk_digest_files
        assert callable(cortex_bulk_digest_files)
    
    def test_bulk_digest_empty_directory(self) -> None:
        """Test handling of directory with no markdown files."""
        from cortex.mcp.tools.bulk_digest import cortex_bulk_digest_files
        
        with patch('pathlib.Path.glob') as mock_glob:
            mock_glob.return_value = []
            
            result = cortex_bulk_digest_files(
                directory=".",
                pattern="*.md",
                auto_delete=False
            )
            
            assert result["success"] is True
            assert result["files_found"] == 0
            assert result["files_processed"] == 0
    
    def test_bulk_digest_excludes_docs_directory(self) -> None:
        """Test exclusion of docs/ directory files."""
        from cortex.mcp.tools.bulk_digest import cortex_bulk_digest_files
        
        result = cortex_bulk_digest_files(
            directory=".",
            pattern="*.md",
            exclude_patterns=["docs/**", "README.md"],
            auto_delete=False
        )
        
        assert result["success"] is True
        assert "files_excluded" in result
    
    def test_bulk_digest_dry_run_mode(self) -> None:
        """Test dry run mode does not delete files."""
        from cortex.mcp.tools.bulk_digest import cortex_bulk_digest_files
        
        with patch('cortex.orchestrators.support.digest_session_orchestrator.DigestSessionOrchestrator') as MockOrch:
            mock_instance = MockOrch.return_value
            mock_instance.digest_session.return_value = Mock(
                success=True,
                is_chat_file=True,
                confidence_score=8.0,
                enhancements_found=3,
                to_dict=lambda: {"success": True}
            )
            
            with patch('pathlib.Path.glob') as mock_glob:
                mock_file = Mock()
                mock_file.name = "test.md"
                mock_file.is_file.return_value = True
                mock_file.exists.return_value = True
                mock_glob.return_value = [mock_file]
                
                with patch('pathlib.Path.unlink') as mock_unlink:
                    result = cortex_bulk_digest_files(
                        directory=".",
                        pattern="*.md",
                        dry_run=True,
                        auto_delete=True
                    )
                    
                    assert result["dry_run"] is True
                    # File should NOT be deleted in dry run
                    mock_unlink.assert_not_called()
    
    def test_bulk_digest_deletes_after_successful_ingestion(self) -> None:
        """Test file deletion after successful ingestion."""
        from cortex.mcp.tools.bulk_digest import cortex_bulk_digest_files
        
        with patch('cortex.orchestrators.support.digest_session_orchestrator.DigestSessionOrchestrator') as MockOrch:
            mock_instance = MockOrch.return_value
            mock_instance.digest_session.return_value = Mock(
                success=True,
                is_chat_file=True,
                confidence_score=8.0,
                enhancements_found=3,
                to_dict=lambda: {"success": True, "enhancements_found": 3}
            )
            
            with patch('pathlib.Path.glob') as mock_glob:
                mock_file = MagicMock(spec=Path)
                mock_file.name = "test-completion.md"
                mock_file.is_file.return_value = True
                mock_file.exists.return_value = True
                mock_file.__str__.return_value = "/fake/test-completion.md"
                mock_glob.return_value = [mock_file]
                
                result = cortex_bulk_digest_files(
                    directory=".",
                    pattern="*.md",
                    auto_delete=True,
                    dry_run=False
                )
                
                # Should have attempted deletion
                mock_file.unlink.assert_called_once()
                assert result["files_deleted"] > 0
    
    def test_bulk_digest_preserves_on_failure(self) -> None:
        """Test file preservation when ingestion fails."""
        from cortex.mcp.tools.bulk_digest import cortex_bulk_digest_files
        
        with patch('cortex.orchestrators.support.digest_session_orchestrator.DigestSessionOrchestrator') as MockOrch:
            mock_instance = MockOrch.return_value
            mock_instance.digest_session.return_value = Mock(
                success=False,
                error_message="Processing failed",
                to_dict=lambda: {"success": False, "error_message": "Processing failed"}
            )
            
            with patch('pathlib.Path.glob') as mock_glob:
                mock_file = MagicMock(spec=Path)
                mock_file.name = "test.md"
                mock_file.is_file.return_value = True
                mock_file.exists.return_value = True
                mock_file.__str__.return_value = "/fake/test.md"
                mock_glob.return_value = [mock_file]
                
                result = cortex_bulk_digest_files(
                    directory=".",
                    pattern="*.md",
                    auto_delete=True,
                    dry_run=False
                )
                
                # Should NOT delete on failure
                mock_file.unlink.assert_not_called()
                assert result["files_deleted"] == 0
                assert result["files_failed"] > 0
    
    def test_bulk_digest_applies_min_confidence_filter(self) -> None:
        """Test minimum confidence filtering."""
        from cortex.mcp.tools.bulk_digest import cortex_bulk_digest_files
        
        with patch('cortex.orchestrators.support.digest_session_orchestrator.DigestSessionOrchestrator') as MockOrch:
            mock_instance = MockOrch.return_value
            # Low confidence file
            mock_instance.digest_session.return_value = Mock(
                success=True,
                is_chat_file=False,
                confidence_score=3.0,  # Below threshold
                enhancements_found=0,
                to_dict=lambda: {"success": True, "confidence_score": 3.0, "is_chat_file": False}
            )
            
            with patch('pathlib.Path.glob') as mock_glob:
                mock_file = MagicMock(spec=Path)
                mock_file.name = "low-confidence.md"
                mock_file.is_file.return_value = True
                mock_file.exists.return_value = True
                mock_file.__str__.return_value = "/fake/low-confidence.md"
                mock_glob.return_value = [mock_file]
                
                result = cortex_bulk_digest_files(
                    directory=".",
                    pattern="*.md",
                    min_confidence=5.0,
                    auto_delete=True
                )
                
                # Should skip low confidence files
                assert result["files_skipped"] > 0
                mock_file.unlink.assert_not_called()
    
    def test_bulk_digest_parallel_processing(self) -> None:
        """Test parallel processing option."""
        from cortex.mcp.tools.bulk_digest import cortex_bulk_digest_files
        
        result = cortex_bulk_digest_files(
            directory=".",
            pattern="*.md",
            parallel=True,
            max_workers=4
        )
        
        assert "parallel" in result
        assert result["parallel"] is True
    
    def test_bulk_digest_returns_detailed_stats(self) -> None:
        """Test detailed statistics in return value."""
        from cortex.mcp.tools.bulk_digest import cortex_bulk_digest_files
        
        result = cortex_bulk_digest_files(
            directory=".",
            pattern="*.md",
            dry_run=True
        )
        
        # Required fields
        assert "success" in result
        assert "files_found" in result
        assert "files_processed" in result
        assert "files_skipped" in result
        assert "files_deleted" in result
        assert "files_failed" in result
        assert "total_enhancements" in result
        assert "processing_time_seconds" in result
    
    def test_bulk_digest_excludes_readme(self) -> None:
        """Test README.md is always excluded."""
        from cortex.mcp.tools.bulk_digest import cortex_bulk_digest_files
        
        with patch('pathlib.Path.glob') as mock_glob:
            readme = MagicMock(spec=Path)
            readme.name = "README.md"
            readme.is_file.return_value = True
            
            other = MagicMock(spec=Path)
            other.name = "PHASE-1.md"
            other.is_file.return_value = True
            
            mock_glob.return_value = [readme, other]
            
            result = cortex_bulk_digest_files(
                directory=".",
                pattern="*.md",
                dry_run=True
            )
            
            # README should be excluded automatically
            assert result["files_excluded"] >= 1


class TestBulkDigestOrchestrator:
    """Test BulkDigestOrchestrator class."""
    
    def test_orchestrator_initialization(self) -> None:
        """Test orchestrator initializes correctly."""
        from cortex.orchestrators.support.bulk_digest_orchestrator import BulkDigestOrchestrator
        
        orchestrator = BulkDigestOrchestrator()
        assert orchestrator is not None
        assert hasattr(orchestrator, "process_directory")
    
    def test_orchestrator_file_filtering(self) -> None:
        """Test file filtering logic."""
        from cortex.orchestrators.support.bulk_digest_orchestrator import BulkDigestOrchestrator
        
        orchestrator = BulkDigestOrchestrator()
        
        # Should exclude docs/ files
        assert not orchestrator._should_process("docs/guide.md", exclude_patterns=["docs/**"])
        
        # Should exclude README.md
        assert not orchestrator._should_process("README.md", exclude_patterns=["README.md"])
        
        # Should process root-level phase files
        assert orchestrator._should_process("PHASE-64-SUMMARY.md", exclude_patterns=["docs/**"])
    
    def test_orchestrator_batch_processing(self) -> None:
        """Test batch processing functionality."""
        from cortex.orchestrators.support.bulk_digest_orchestrator import BulkDigestOrchestrator
        
        orchestrator = BulkDigestOrchestrator()
        
        files = [f"file{i}.md" for i in range(50)]
        batches = orchestrator._create_batches(files, batch_size=10)
        
        assert len(batches) == 5
        assert all(len(batch) == 10 for batch in batches)
    
    def test_orchestrator_progress_reporting(self) -> None:
        """Test progress reporting during processing."""
        from cortex.orchestrators.support.bulk_digest_orchestrator import BulkDigestOrchestrator
        
        orchestrator = BulkDigestOrchestrator()
        
        # Should track progress
        assert hasattr(orchestrator, "_update_progress")
        
    def test_orchestrator_error_handling(self) -> None:
        """Test graceful error handling."""
        from cortex.orchestrators.support.bulk_digest_orchestrator import BulkDigestOrchestrator
        
        orchestrator = BulkDigestOrchestrator()
        
        with patch.object(orchestrator, "_process_single_file") as mock_process:
            mock_process.side_effect = Exception("Processing error")
            
            # Should not crash on single file error
            result = orchestrator.process_directory(
                directory=".",
                pattern="*.md",
                continue_on_error=True
            )
            
            assert result["success"] is True  # Overall success despite errors
            assert result["files_failed"] > 0
