"""
Tests for DocumentHygieneOrchestrator.

Tests the automatic Markdown maintenance and organization orchestrator.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
import asyncio
from datetime import datetime, timedelta

from src.operations.modules.orchestration.document_hygiene_orchestrator import (
    DocumentHygieneOrchestrator,
    HygieneResult,
    run_document_hygiene
)


class TestDocumentHygieneOrchestrator:
    """Test suite for DocumentHygieneOrchestrator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.docs_brain = self.project_root / "cortex-brain" / "documents"
        self.docs_brain.mkdir(parents=True, exist_ok=True)
        self.orchestrator = DocumentHygieneOrchestrator(self.project_root)
        
    def teardown_method(self):
        """Cleanup test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_initialization(self):
        """Test orchestrator initialization."""
        assert self.orchestrator.project_root == self.project_root
        assert self.orchestrator.version == "1.0"
        assert len(self.orchestrator.phases) == 6
        assert self.orchestrator.max_workers == 4
        
    def test_phases_order(self):
        """Test correct phase ordering."""
        expected_phases = [
            "consolidation",
            "archiving",
            "filename_optimization",
            "reference_updating",
            "reorganization",
            "finalization"
        ]
        assert self.orchestrator.phases == expected_phases
        
    @pytest.mark.asyncio
    async def test_execute_empty_docs(self):
        """Test hygiene on empty documentation."""
        result = await self.orchestrator.execute()
        
        assert result['success'] is True
        assert result['is_complete'] is True
        assert len(self.orchestrator.metrics['phases_completed']) == 6
        
    @pytest.mark.asyncio
    async def test_execute_with_docs(self):
        """Test hygiene with actual markdown files."""
        # Create test documents
        test_doc = self.docs_brain / "test.md"
        test_doc.write_text("# Test Document\n\nContent here.")
        
        result = await self.orchestrator.execute([self.docs_brain])
        
        assert result['success'] is True
        assert self.orchestrator.metrics['files_processed'] > 0
        
    @pytest.mark.asyncio
    async def test_consolidation_phase(self):
        """Test document consolidation phase."""
        # Create similar documents
        doc1 = self.docs_brain / "doc1.md"
        doc1.write_text("# Document 1\n\nSimilar content.")
        doc2 = self.docs_brain / "doc2.md"
        doc2.write_text("# Document 2\n\nSimilar content.")
        
        result = await self.orchestrator._run_consolidation_phase([self.docs_brain])
        
        assert isinstance(result, HygieneResult)
        assert result.phase == "consolidation"
        assert result.files_processed >= 2
        
    @pytest.mark.asyncio
    async def test_archiving_phase(self):
        """Test outdated document archiving phase."""
        # Create planning directory
        planning_dir = self.docs_brain / "planning"
        planning_dir.mkdir(exist_ok=True)
        
        # Create old document
        old_doc = planning_dir / "old_plan.md"
        old_doc.write_text("# Old Plan\n\nOutdated content.")
        
        result = await self.orchestrator._run_archiving_phase([self.docs_brain])
        
        assert isinstance(result, HygieneResult)
        assert result.phase == "archiving"
        
    @pytest.mark.asyncio
    async def test_filename_optimization_phase(self):
        """Test filename optimization phase."""
        # Create document with long filename
        long_name = self.docs_brain / ("x" * 60 + ".md")
        long_name.write_text("# Long Name\n\nContent.")
        
        result = await self.orchestrator._run_filename_optimization_phase([self.docs_brain])
        
        assert isinstance(result, HygieneResult)
        assert result.phase == "filename_optimization"
        
    @pytest.mark.asyncio
    async def test_reference_updating_phase(self):
        """Test reference updating phase."""
        result = await self.orchestrator._run_reference_updating_phase()
        
        assert isinstance(result, HygieneResult)
        assert result.phase == "reference_updating"
        
    @pytest.mark.asyncio
    async def test_reorganization_phase(self):
        """Test reorganization recommendations phase."""
        result = await self.orchestrator._run_reorganization_phase([self.docs_brain])
        
        assert isinstance(result, HygieneResult)
        assert result.phase == "reorganization"
        assert len(result.recommendations) > 0
        
    def test_finalize_hygiene(self):
        """Test finalization phase."""
        results = [
            HygieneResult("consolidation", 10, 2, []),
            HygieneResult("archiving", 5, 3, ["rec1"]),
            HygieneResult("filename_optimization", 8, 1, [])
        ]
        
        self.orchestrator._finalize_hygiene(results)
        # Should complete without error
        
    def test_find_similar_documents(self):
        """Test finding similar documents."""
        doc1 = self.docs_brain / "similar1.md"
        doc1.write_text("# Similar Doc 1")
        doc2 = self.docs_brain / "similar2.md"
        doc2.write_text("# Similar Doc 2")
        
        similar_groups = self.orchestrator._find_similar_documents([doc1, doc2])
        
        assert isinstance(similar_groups, list)
        
    def test_is_active_plan(self):
        """Test active plan detection."""
        test_doc = self.docs_brain / "plan.md"
        test_doc.write_text("# Active Plan\n\nSTATUS: active")
        
        is_active = self.orchestrator._is_active_plan(test_doc)
        
        assert isinstance(is_active, bool)
        
    def test_synchronous_wrapper(self):
        """Test synchronous wrapper function."""
        result = run_document_hygiene(self.project_root)
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'results' in result
        
    def test_metrics_tracking(self):
        """Test metrics are properly tracked."""
        asyncio.run(self.orchestrator.execute([]))
        
        metrics = self.orchestrator.metrics
        assert 'phases_completed' in metrics
        assert 'files_processed' in metrics
        assert 'actions_taken' in metrics
        assert 'recommendations' in metrics
        assert len(metrics['phases_completed']) == 6
        
    @pytest.mark.asyncio
    async def test_selective_phases(self):
        """Test running selective phases."""
        result = await self.orchestrator.execute(
            phases=["consolidation", "archiving"]
        )
        
        assert result['success'] is True
        assert "consolidation" in self.orchestrator.metrics['phases_completed']
        assert "archiving" in self.orchestrator.metrics['phases_completed']
        
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in orchestrator."""
        # Force error with nonexistent directory
        result = await self.orchestrator.execute([Path("/nonexistent/docs")])
        
        # Should still complete successfully (handles missing dirs)
        assert result['success'] is True
        
    def test_version_management(self):
        """Test version management integration."""
        assert self.orchestrator.version == "1.0"
        assert self.orchestrator.version_manager is not None


class TestHygieneResult:
    """Test suite for HygieneResult dataclass."""
    
    def test_creation(self):
        """Test HygieneResult creation."""
        result = HygieneResult(
            phase="test_phase",
            files_processed=20,
            actions_taken=5,
            recommendations=["rec1", "rec2"]
        )
        
        assert result.phase == "test_phase"
        assert result.files_processed == 20
        assert result.actions_taken == 5
        assert len(result.recommendations) == 2
        
    def test_empty_recommendations(self):
        """Test HygieneResult with no recommendations."""
        result = HygieneResult(
            phase="clean_phase",
            files_processed=10,
            actions_taken=0,
            recommendations=[]
        )
        
        assert result.recommendations == []
        assert result.actions_taken == 0
