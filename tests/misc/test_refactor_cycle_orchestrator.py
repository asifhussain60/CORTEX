"""
Tests for RefactorCycleOrchestrator.

Tests the automatic code cleanup and quality enforcement orchestrator.

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
import asyncio

from src.operations.modules.orchestration.refactor_cycle_orchestrator import (
    RefactorCycleOrchestrator,
    RefactorResult,
    run_refactor_cycle
)


class TestRefactorCycleOrchestrator:
    """Test suite for RefactorCycleOrchestrator."""
    
    def setup_method(self):
        """Setup test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = Path(self.temp_dir)
        self.orchestrator = RefactorCycleOrchestrator(self.project_root)
        
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
            "comment_sync",
            "debug_removal",
            "dead_code",
            "lint_enforcement",
            "format_enforcement",
            "finalization"
        ]
        assert self.orchestrator.phases == expected_phases
        
    @pytest.mark.asyncio
    async def test_execute_empty_project(self):
        """Test refactor on empty project."""
        result = await self.orchestrator.execute()
        
        assert result['success'] is True
        assert result['is_complete'] is True
        assert len(self.orchestrator.metrics['phases_completed']) == 6
        
    @pytest.mark.asyncio
    async def test_execute_with_files(self):
        """Test refactor with actual Python files."""
        # Create test file with debug code
        test_file = self.project_root / "test.py"
        test_file.write_text("def func():\n    print('debug')\n    return True\n")
        
        result = await self.orchestrator.execute([test_file])
        
        assert result['success'] is True
        assert self.orchestrator.metrics['files_processed'] > 0
        
    @pytest.mark.asyncio
    async def test_comment_sync_phase(self):
        """Test comment synchronization phase."""
        test_file = self.project_root / "test.py"
        test_file.write_text("# Old comment\ndef func():\n    return True\n")
        
        result = await self.orchestrator._run_comment_sync_phase([test_file])
        
        assert isinstance(result, RefactorResult)
        assert result.phase == "comment_sync"
        
    @pytest.mark.asyncio
    async def test_debug_removal_phase(self):
        """Test debug code removal phase."""
        test_file = self.project_root / "test.py"
        test_file.write_text("def func():\n    print('debug')\n    console.log('test')\n    return True\n")
        
        result = await self.orchestrator._run_debug_removal_phase([test_file])
        
        assert isinstance(result, RefactorResult)
        assert result.phase == "debug_removal"
        assert result.files_processed > 0
        
    @pytest.mark.asyncio
    async def test_dead_code_phase(self):
        """Test dead code detection phase."""
        result = await self.orchestrator._run_dead_code_phase([])
        
        assert isinstance(result, RefactorResult)
        assert result.phase == "dead_code"
        
    @pytest.mark.asyncio
    async def test_lint_phase(self):
        """Test lint enforcement phase."""
        result = await self.orchestrator._run_lint_phase([])
        
        assert isinstance(result, RefactorResult)
        assert result.phase == "lint_enforcement"
        
    @pytest.mark.asyncio
    async def test_format_phase(self):
        """Test format enforcement phase."""
        result = await self.orchestrator._run_format_phase([])
        
        assert isinstance(result, RefactorResult)
        assert result.phase == "format_enforcement"
        
    def test_finalize_refactor(self):
        """Test finalization phase."""
        results = [
            RefactorResult("comment_sync", 10, 2, []),
            RefactorResult("debug_removal", 5, 3, []),
            RefactorResult("dead_code", 8, 1, [])
        ]
        
        self.orchestrator._finalize_refactor(results)
        # Should complete without error
        
    def test_synchronous_wrapper(self):
        """Test synchronous wrapper function."""
        result = run_refactor_cycle(self.project_root)
        
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'results' in result
        
    def test_metrics_tracking(self):
        """Test metrics are properly tracked."""
        asyncio.run(self.orchestrator.execute([]))
        
        metrics = self.orchestrator.metrics
        assert 'phases_completed' in metrics
        assert 'files_processed' in metrics
        assert 'changes_made' in metrics
        assert len(metrics['phases_completed']) == 6
        
    @pytest.mark.asyncio
    async def test_selective_phases(self):
        """Test running selective phases."""
        result = await self.orchestrator.execute(phases=["debug_removal", "lint_enforcement"])
        
        assert result['success'] is True
        assert "debug_removal" in self.orchestrator.metrics['phases_completed']
        assert "lint_enforcement" in self.orchestrator.metrics['phases_completed']
        
    def test_sync_file_comments(self):
        """Test single file comment synchronization."""
        test_file = self.project_root / "test.py"
        test_file.write_text("def func():\n    pass\n")
        
        changes = self.orchestrator._sync_file_comments(test_file)
        
        assert isinstance(changes, int)
        assert changes >= 0
        
    @pytest.mark.asyncio
    async def test_multi_threaded_execution(self):
        """Test multi-threaded file processing."""
        files = []
        for i in range(10):
            f = self.project_root / f"test_{i}.py"
            f.write_text(f"def func_{i}():\n    print('debug')\n")
            files.append(f)
            
        result = await self.orchestrator._run_comment_sync_phase(files)
        
        assert result.files_processed == 10
        
    def test_version_management(self):
        """Test version management integration."""
        assert self.orchestrator.version == "1.0"
        assert self.orchestrator.version_manager is not None


class TestRefactorResult:
    """Test suite for RefactorResult dataclass."""
    
    def test_creation(self):
        """Test RefactorResult creation."""
        result = RefactorResult(
            phase="test_phase",
            files_processed=15,
            changes_made=8,
            issues_found=["issue1"]
        )
        
        assert result.phase == "test_phase"
        assert result.files_processed == 15
        assert result.changes_made == 8
        assert len(result.issues_found) == 1
        
    def test_empty_issues(self):
        """Test RefactorResult with no issues."""
        result = RefactorResult(
            phase="clean_phase",
            files_processed=5,
            changes_made=0,
            issues_found=[]
        )
        
        assert result.issues_found == []
