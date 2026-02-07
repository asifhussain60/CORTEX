"""
Test BrainFlushOrchestrator and Flush System.

AC_START: AC-PHASE38-012, AC-PHASE38-013, AC-PHASE38-014

Test coverage:
- AC-PHASE38-012: BrainFlushOrchestrator with unified cleanup (12 tests)
- AC-PHASE38-013: Scheduled flush daemon (8 tests)
- AC-PHASE38-014: /flush command for on-demand cleanup (5 tests)

Total: 25 tests
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from typing import Dict, Any, List

try:
    from cortex.orchestrators.support.brain_flush_orchestrator import (
        BrainFlushOrchestrator,
        FlushTarget,
        FlushResult,
        FlushScheduler
    )
except ImportError:
    BrainFlushOrchestrator = None
    FlushTarget = None
    FlushResult = None
    FlushScheduler = None


@pytest.mark.skipif(BrainFlushOrchestrator is None, reason="Implementation pending")
class TestBrainFlushOrchestrator:
    """Test BrainFlushOrchestrator (AC-PHASE38-012)."""
    
    def test_orchestrator_initialization(self):
        """Test orchestrator initializes with flush targets."""
        orchestrator = BrainFlushOrchestrator()
        
        assert orchestrator is not None
        assert hasattr(orchestrator, 'flush_all')
        assert hasattr(orchestrator, 'flush_target')
    
    def test_flush_context_cache_ttl_based(self):
        """Test flushing context cache based on TTL."""
        orchestrator = BrainFlushOrchestrator()
        
        result = orchestrator.flush_target('context_cache', strategy='ttl', ttl_hours=24)
        
        assert isinstance(result, FlushResult)
        assert result.target == 'context_cache'
        assert result.items_removed >= 0
        assert result.bytes_freed >= 0
    
    def test_flush_embedding_cache_lru(self):
        """Test flushing embedding cache with LRU strategy."""
        orchestrator = BrainFlushOrchestrator()
        
        result = orchestrator.flush_target('embedding_cache', strategy='lru', keep_count=100)
        
        assert isinstance(result, FlushResult)
        assert result.target == 'embedding_cache'
        assert result.strategy == 'lru'
    
    def test_flush_governance_db_wal(self):
        """Test rotating governance.db WAL file."""
        orchestrator = BrainFlushOrchestrator()
        
        result = orchestrator.flush_target('governance_db_wal', strategy='rotation')
        
        assert isinstance(result, FlushResult)
        assert result.target == 'governance_db_wal'
    
    def test_flush_stale_sessions(self):
        """Test removing stale sessions based on age."""
        orchestrator = BrainFlushOrchestrator()
        
        result = orchestrator.flush_target('stale_sessions', strategy='age', max_age_days=7)
        
        assert isinstance(result, FlushResult)
        assert result.target == 'stale_sessions'
    
    def test_flush_orphan_checkpoints(self):
        """Test removing orphan checkpoints without references."""
        orchestrator = BrainFlushOrchestrator()
        
        result = orchestrator.flush_target('orphan_checkpoints', strategy='reference')
        
        assert isinstance(result, FlushResult)
        assert result.target == 'orphan_checkpoints'
    
    def test_flush_all_targets(self):
        """Test flushing all targets at once."""
        orchestrator = BrainFlushOrchestrator()
        
        results = orchestrator.flush_all()
        
        assert isinstance(results, list)
        assert len(results) == 5  # 5 flush targets
        assert all(isinstance(r, FlushResult) for r in results)
    
    def test_flush_dry_run_mode(self):
        """Test dry run mode (no actual deletion)."""
        orchestrator = BrainFlushOrchestrator()
        
        result = orchestrator.flush_target('context_cache', dry_run=True)
        
        assert result.dry_run is True
        assert result.items_removed == 0  # Dry run doesn't remove
        assert result.would_remove >= 0  # Reports what would be removed
    
    def test_flush_statistics_tracking(self):
        """Test tracking flush statistics over time."""
        orchestrator = BrainFlushOrchestrator()
        
        orchestrator.flush_target('context_cache')
        
        stats = orchestrator.get_flush_statistics()
        
        assert 'total_flushes' in stats
        assert 'total_items_removed' in stats
        assert 'total_bytes_freed' in stats
    
    def test_flush_priority_ordering(self):
        """Test flush operations respect priority."""
        orchestrator = BrainFlushOrchestrator()
        
        # High priority targets should flush first
        results = orchestrator.flush_all(respect_priority=True)
        
        # Verify high priority targets processed first
        assert results[0].target in ['governance_db_wal', 'orphan_checkpoints']
    
    def test_flush_error_handling(self):
        """Test error handling during flush operations."""
        orchestrator = BrainFlushOrchestrator()
        
        # Simulate error scenario
        with patch.object(orchestrator, '_flush_context_cache', side_effect=Exception("Test error")):
            result = orchestrator.flush_target('context_cache')
        
        assert result.success is False
        assert 'error' in result.message.lower()
    
    def test_flush_selective_targets(self):
        """Test flushing only selected targets."""
        orchestrator = BrainFlushOrchestrator()
        
        results = orchestrator.flush_selective(['context_cache', 'embedding_cache'])
        
        assert len(results) == 2
        assert all(r.target in ['context_cache', 'embedding_cache'] for r in results)


@pytest.mark.skipif(FlushScheduler is None, reason="Implementation pending")
class TestFlushScheduler:
    """Test FlushScheduler (AC-PHASE38-013)."""
    
    def test_scheduler_initialization(self):
        """Test scheduler initializes with default schedule."""
        scheduler = FlushScheduler()
        
        assert scheduler is not None
        assert hasattr(scheduler, 'start')
        assert hasattr(scheduler, 'stop')
    
    def test_schedule_daily_flush(self):
        """Test scheduling daily flush operation."""
        scheduler = FlushScheduler()
        
        scheduler.schedule_flush(interval='daily', time='03:00')
        
        schedule = scheduler.get_schedule()
        assert len(schedule) > 0
        assert schedule[0]['interval'] == 'daily'
    
    def test_schedule_hourly_flush(self):
        """Test scheduling hourly flush operation."""
        scheduler = FlushScheduler()
        
        scheduler.schedule_flush(interval='hourly', targets=['context_cache'])
        
        schedule = scheduler.get_schedule()
        assert any(s['interval'] == 'hourly' for s in schedule)
    
    def test_scheduler_start_stop(self):
        """Test starting and stopping scheduler daemon."""
        scheduler = FlushScheduler()
        
        scheduler.start()
        assert scheduler.is_running() is True
        
        scheduler.stop()
        assert scheduler.is_running() is False
    
    def test_scheduler_execution_logging(self):
        """Test scheduler logs execution history."""
        scheduler = FlushScheduler()
        
        scheduler.start()
        
        # Simulate execution
        scheduler._execute_flush(['context_cache'])
        
        history = scheduler.get_execution_history()
        assert len(history) > 0
        assert 'timestamp' in history[0]
    
    def test_scheduler_error_recovery(self):
        """Test scheduler recovers from flush errors."""
        scheduler = FlushScheduler()
        
        with patch('cortex.orchestrators.support.brain_flush_orchestrator.BrainFlushOrchestrator.flush_target', side_effect=Exception("Test error")):
            scheduler.start()
            scheduler._execute_flush(['context_cache'])
        
        # Scheduler should still be running
        assert scheduler.is_running() is True
    
    def test_scheduler_custom_intervals(self):
        """Test custom flush intervals."""
        scheduler = FlushScheduler()
        
        scheduler.schedule_flush(interval='custom', minutes=15)
        
        schedule = scheduler.get_schedule()
        assert any(s.get('minutes') == 15 for s in schedule)
    
    def test_scheduler_conditional_flush(self):
        """Test conditional flush based on thresholds."""
        scheduler = FlushScheduler()
        
        scheduler.schedule_flush(
            interval='conditional',
            condition='cache_size > 1GB'
        )
        
        schedule = scheduler.get_schedule()
        assert any('condition' in s for s in schedule)


@pytest.mark.skipif(BrainFlushOrchestrator is None, reason="Implementation pending")
class TestFlushCommand:
    """Test /flush command integration (AC-PHASE38-014)."""
    
    def test_flush_command_all_targets(self):
        """Test /flush command with all targets."""
        orchestrator = BrainFlushOrchestrator()
        
        result = orchestrator.handle_flush_command(command='/flush')
        
        assert result['success'] is True
        assert 'results' in result
        assert len(result['results']) == 5
    
    def test_flush_command_specific_target(self):
        """Test /flush command with specific target."""
        orchestrator = BrainFlushOrchestrator()
        
        result = orchestrator.handle_flush_command(command='/flush context_cache')
        
        assert result['success'] is True
        assert len(result['results']) == 1
        assert result['results'][0].target == 'context_cache'
    
    def test_flush_command_dry_run(self):
        """Test /flush command with --dry-run flag."""
        orchestrator = BrainFlushOrchestrator()
        
        result = orchestrator.handle_flush_command(command='/flush --dry-run')
        
        assert result['success'] is True
        assert all(r.dry_run for r in result['results'])
    
    def test_flush_command_verbose_output(self):
        """Test /flush command with --verbose flag."""
        orchestrator = BrainFlushOrchestrator()
        
        result = orchestrator.handle_flush_command(command='/flush --verbose')
        
        assert result['success'] is True
        assert result.get('verbose') is True
    
    def test_flush_command_help(self):
        """Test /flush command with --help flag."""
        orchestrator = BrainFlushOrchestrator()
        
        result = orchestrator.handle_flush_command(command='/flush --help')
        
        assert result['success'] is True
        assert 'help' in result
        assert 'usage' in result['help'].lower()


# AC-PHASE38-012 ✅ 12 tests implemented
# AC-PHASE38-013 ✅ 8 tests implemented  
# AC-PHASE38-014 ✅ 5 tests implemented
# Total: 25 tests (matches stage_5 target)
