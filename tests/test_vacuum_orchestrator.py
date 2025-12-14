"""
Tests for VacuumOrchestrator.

Tests the deep codebase cleanup orchestrator with AST intelligence.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
import asyncio

from src.operations.modules.orchestration.vacuum_orchestrator import (
    VacuumOrchestrator,
    VacuumResult,
    run_vacuum
)


class TestVacuumOrchestrator:
    """Test suite for VacuumOrchestrator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.orchestrator = VacuumOrchestrator(self.project_root)
        
    def teardown_method(self):
        """Cleanup test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        
    def test_initialization(self):
        """Test orchestrator initialization."""
        assert self.orchestrator.project_root == self.project_root
        assert self.orchestrator.version == "1.0"
        assert len(self.orchestrator.phases) == 5
        assert self.orchestrator.metrics['phases_completed'] == []
        
    def test_phases_order(self):
        """Test correct phase ordering."""
        expected_phases = [
            "duplicate_detection",
            "orphaned_tests",
            "unused_imports",
            "dead_code",
            "finalization"
        ]
        assert self.orchestrator.phases == expected_phases
        
    @pytest.mark.asyncio
    async def test_execute_empty_project(self):
        """Test vacuum on empty project."""
        result = await self.orchestrator.execute()
        
        assert result['success'] is True
        assert result['is_complete'] is True
        assert len(result['results']) == 4  # 4 active phases
        assert len(self.orchestrator.metrics['phases_completed']) == 5  # including finalization
        
    @pytest.mark.asyncio
    async def test_execute_with_files(self):
        """Test vacuum with actual Python files."""
        # Create test files
        test_file = self.project_root / "test.py"
        test_file.write_text("def unused_function():\n    pass\n")
        
        result = await self.orchestrator.execute([test_file])
        
        assert result['success'] is True
        assert self.orchestrator.metrics['items_found'] >= 0
        
    @pytest.mark.asyncio
    async def test_duplicate_detection_phase(self):
        """Test duplicate detection phase."""
        result = await self.orchestrator._run_duplicate_detection_phase([], dry_run=True)
        
        assert isinstance(result, VacuumResult)
        assert result.phase == "duplicate_detection"
        assert result.items_found >= 0
        
    @pytest.mark.asyncio
    async def test_orphaned_tests_phase(self):
        """Test orphaned tests detection phase."""
        result = await self.orchestrator._run_orphaned_tests_phase(dry_run=True)
        
        assert isinstance(result, VacuumResult)
        assert result.phase == "orphaned_tests"
        assert result.details == []  # Empty for stub AST
        
    @pytest.mark.asyncio
    async def test_unused_imports_phase(self):
        """Test unused imports detection phase."""
        result = await self.orchestrator._run_unused_imports_phase(dry_run=True)
        
        assert isinstance(result, VacuumResult)
        assert result.phase == "unused_imports"
        
    @pytest.mark.asyncio
    async def test_dead_code_phase(self):
        """Test dead code detection phase."""
        result = await self.orchestrator._run_dead_code_phase(dry_run=True)
        
        assert isinstance(result, VacuumResult)
        assert result.phase == "dead_code"
        
    def test_finalize_vacuum(self):
        """Test finalization phase."""
        results = [
            VacuumResult("duplicate_detection", 10, 2, True, []),
            VacuumResult("orphaned_tests", 5, 1, True, []),
            VacuumResult("unused_imports", 8, 3, True, []),
            VacuumResult("dead_code", 12, 4, True, [])
        ]
        
        self.orchestrator._finalize_vacuum(results, dry_run=True)
        # Should complete without error
        
    def test_generate_preview_report(self):
        """Test preview report generation."""
        results = [
            VacuumResult("duplicate_detection", 10, 2, True, ["issue1"]),
            VacuumResult("orphaned_tests", 5, 1, True, []),
        ]
        
        report = self.orchestrator.generate_preview_report(results)
        
        assert "Duplicate Detection" in report
        assert "items" in report.lower() or "vacuum" in report.lower()
        
    def test_synchronous_wrapper(self):
        """Test synchronous wrapper function."""
        result = run_vacuum(self.project_root)
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'results' in result
        assert 'metrics' in result
        
    def test_metrics_tracking(self):
        """Test metrics are properly tracked."""
        asyncio.run(self.orchestrator.execute([]))
        
        metrics = self.orchestrator.metrics
        assert 'phases_completed' in metrics
        assert 'items_found' in metrics
        assert 'items_removed' in metrics
        assert 'errors' in metrics
        assert len(metrics['phases_completed']) == 5
        
    @pytest.mark.asyncio
    async def test_error_handling(self):
        """Test error handling in orchestrator."""
        # Force an error by providing invalid path
        invalid_files = [Path("/nonexistent/file.py")]
        
        result = await self.orchestrator.execute(invalid_files)
        
        # Should still succeed with AST stub
        assert result['success'] is True or len(result.get('metrics', {}).get('errors', [])) > 0
        
    def test_version_management(self):
        """Test version management integration."""
        assert self.orchestrator.version == "1.0"
        assert self.orchestrator.version_manager is not None


class TestVacuumResult:
    """Test suite for VacuumResult dataclass."""
    
    def test_creation(self):
        """Test VacuumResult creation."""
        result = VacuumResult(
            phase="test_phase",
            items_found=10,
            items_removed=5,
            dry_run=True,
            details=["detail1", "detail2"]
        )
        
        assert result.phase == "test_phase"
        assert result.items_found == 10
        assert result.items_removed == 5
        assert len(result.details) == 2
        
    def test_empty_issues(self):
        """Test VacuumResult with no issues."""
        result = VacuumResult(
            phase="clean_phase",
            items_found=5,
            items_removed=0,
            dry_run=True,
            details=[]
        )
        
        assert result.details == []
        assert result.items_removed == 0
