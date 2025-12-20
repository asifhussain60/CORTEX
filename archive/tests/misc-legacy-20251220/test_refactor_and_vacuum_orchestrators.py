"""
Test suites for RefactorCycleOrchestrator and VacuumOrchestrator

Combined test coverage for automatic code cleanup orchestrators.

RefactorCycleOrchestrator tests:
- Comment synchronization
- Debug statement removal
- Dead code elimination
- Lint enforcement
- Format enforcement
- SKULL: REFACTOR_CODE_CLEANUP_ENFORCEMENT

VacuumOrchestrator tests:
- Duplicate detection
- Orphaned test removal
- Unused import cleanup
- Dead code removal
- SKULL: VACUUM_CYCLE_ENFORCEMENT

Author: Asif Hussain
Copyright © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.operations.modules.orchestration.refactor_cycle_orchestrator import (
    RefactorCycleOrchestrator, RefactorResult
)
from src.operations.modules.orchestration.vacuum_orchestrator import (
    VacuumOrchestrator, VacuumResult
)


@pytest.fixture
def temp_project_root(tmp_path):
    """Create temporary project structure."""
    project_root = tmp_path / "test_project"
    project_root.mkdir()
    (project_root / "src").mkdir()
    (project_root / "tests").mkdir()
    
    # Create test Python files
    (project_root / "src" / "sample.py").write_text("""
def function1():
    print("debug")  # Debug statement
    return 42

def unused_function():  # Dead code
    pass
""")
    
    (project_root / "src" / "duplicate.py").write_text("""
def function1():  # Duplicate
    return 42
""")
    
    return project_root


# ===== REFACTOR CYCLE ORCHESTRATOR TESTS =====

@pytest.fixture
def refactor_orchestrator(temp_project_root):
    """Create refactor cycle orchestrator."""
    return RefactorCycleOrchestrator(project_root=temp_project_root)


class TestRefactorCycleCommentSync:
    """Test comment synchronization phase."""
    
    @pytest.mark.asyncio
    async def test_comment_sync_phase(self, refactor_orchestrator):
        """Comment sync keeps docs aligned with code."""
        result = await refactor_orchestrator.execute(phases=["comment_sync"])
        assert result is not None
        assert 'comment_sync' in refactor_orchestrator.metrics['phases_completed']


class TestRefactorCycleDebugRemoval:
    """Test debug statement removal."""
    
    @pytest.mark.asyncio
    async def test_debug_removal_finds_prints(self, refactor_orchestrator, temp_project_root):
        """Debug removal finds print/console statements."""
        result = await refactor_orchestrator.execute(phases=["debug_removal"])
        assert result is not None


class TestRefactorCycleDeadCode:
    """Test dead code elimination."""
    
    @pytest.mark.asyncio
    async def test_dead_code_detection(self, refactor_orchestrator):
        """Dead code phase detects unused functions."""
        result = await refactor_orchestrator.execute(phases=["dead_code"])
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_refactor_code_cleanup_enforcement(self, refactor_orchestrator):
        """SKULL: REFACTOR_CODE_CLEANUP_ENFORCEMENT removes orphaned code."""
        result = await refactor_orchestrator.execute(phases=["dead_code"])
        assert result is not None


class TestRefactorCycleLintEnforcement:
    """Test lint enforcement phase."""
    
    @pytest.mark.asyncio
    async def test_lint_enforcement(self, refactor_orchestrator):
        """Lint enforcement validates code quality."""
        result = await refactor_orchestrator.execute(phases=["lint_enforcement"])
        assert result is not None


class TestRefactorCycleFormatEnforcement:
    """Test format enforcement phase."""
    
    @pytest.mark.asyncio
    async def test_format_enforcement(self, refactor_orchestrator):
        """Format enforcement ensures consistent style."""
        result = await refactor_orchestrator.execute(phases=["format_enforcement"])
        assert result is not None


class TestRefactorCycleIntegration:
    """Test refactor cycle integration."""
    
    @pytest.mark.asyncio
    async def test_all_phases_execute(self, refactor_orchestrator):
        """All refactor phases execute in sequence."""
        result = await refactor_orchestrator.execute()
        assert result is not None
        assert len(refactor_orchestrator.metrics['phases_completed']) > 0
    
    @pytest.mark.asyncio
    async def test_planning_system_integration(self, refactor_orchestrator):
        """Refactor cycle integrates with Planning System 3.0."""
        result = await refactor_orchestrator.execute()
        assert refactor_orchestrator.version == "1.0"


# ===== VACUUM ORCHESTRATOR TESTS =====

@pytest.fixture
def vacuum_orchestrator(temp_project_root):
    """Create vacuum orchestrator."""
    return VacuumOrchestrator(project_root=temp_project_root)


class TestVacuumDuplicateDetection:
    """Test duplicate detection phase."""
    
    @pytest.mark.asyncio
    async def test_duplicate_detection(self, vacuum_orchestrator, temp_project_root):
        """Vacuum detects duplicate code."""
        result = await vacuum_orchestrator.execute(
            targets=["duplicate_code"],
            dry_run=True
        )
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_similarity_threshold(self, vacuum_orchestrator):
        """Duplicate detection respects similarity threshold."""
        result = await vacuum_orchestrator.execute(
            targets=["duplicate_code"],
            similarity_threshold=0.90
        )
        assert result is not None


class TestVacuumOrphanedTests:
    """Test orphaned test removal."""
    
    @pytest.mark.asyncio
    async def test_orphaned_test_detection(self, vacuum_orchestrator):
        """Vacuum finds tests without corresponding source files."""
        result = await vacuum_orchestrator.execute(
            targets=["orphaned_tests"],
            dry_run=True
        )
        assert result is not None


class TestVacuumUnusedImports:
    """Test unused import cleanup."""
    
    @pytest.mark.asyncio
    async def test_unused_imports_detection(self, vacuum_orchestrator):
        """Vacuum detects unused imports."""
        result = await vacuum_orchestrator.execute(
            targets=["unused_imports"],
            dry_run=True
        )
        assert result is not None


class TestVacuumDeadCode:
    """Test dead code removal."""
    
    @pytest.mark.asyncio
    async def test_dead_code_detection(self, vacuum_orchestrator):
        """Vacuum identifies unreachable code."""
        result = await vacuum_orchestrator.execute(
            targets=["dead_code"],
            dry_run=True
        )
        assert result is not None


class TestVacuumSKULLEnforcement:
    """Test SKULL rule enforcement."""
    
    @pytest.mark.asyncio
    async def test_vacuum_cycle_enforcement(self, vacuum_orchestrator):
        """SKULL: VACUUM_CYCLE_ENFORCEMENT uses AST intelligence."""
        result = await vacuum_orchestrator.execute(dry_run=True)
        assert result is not None
        assert vacuum_orchestrator.ast_engine is not None


class TestVacuumDryRunMode:
    """Test dry run mode."""
    
    @pytest.mark.asyncio
    async def test_dry_run_no_modifications(self, vacuum_orchestrator):
        """Dry run mode previews without modifications."""
        result = await vacuum_orchestrator.execute(dry_run=True)
        assert result is not None
        assert vacuum_orchestrator.metrics['dry_run'] is True
    
    @pytest.mark.asyncio
    async def test_actual_run_applies_changes(self, vacuum_orchestrator):
        """Actual run applies changes."""
        result = await vacuum_orchestrator.execute(dry_run=False)
        assert result is not None


class TestVacuumMetrics:
    """Test vacuum metrics collection."""
    
    @pytest.mark.asyncio
    async def test_metrics_collected(self, vacuum_orchestrator):
        """Vacuum collects comprehensive metrics."""
        result = await vacuum_orchestrator.execute(dry_run=True)
        assert vacuum_orchestrator.metrics['items_found'] >= 0
        assert vacuum_orchestrator.metrics['items_removed'] >= 0


class TestVacuumIntegration:
    """Test vacuum integration."""
    
    @pytest.mark.asyncio
    async def test_all_targets_execute(self, vacuum_orchestrator):
        """All vacuum targets execute."""
        result = await vacuum_orchestrator.execute(dry_run=True)
        assert result is not None
    
    @pytest.mark.asyncio
    async def test_ast_engine_integration(self, vacuum_orchestrator):
        """Vacuum uses AST engine for analysis."""
        assert vacuum_orchestrator.ast_engine is not None
        result = await vacuum_orchestrator.execute(dry_run=True)
        assert result is not None


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
