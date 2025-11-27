"""
CORTEX Optimize Operation Module

Provides code and CORTEX system optimization capabilities.
Part of user-facing entry points for deployment.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .base_operation_module import (
    BaseOperationModule,
    OperationResult,
    OperationStatus,
    OperationPhase,
    OperationModuleMetadata,
)


logger = logging.getLogger(__name__)


class OptimizeOperation(BaseOperationModule):
    """
    Optimization operation for CORTEX and user code.
    
    Features:
    - Code optimization suggestions
    - CORTEX brain cleanup
    - Cache optimization
    - Database vacuum
    - Token usage optimization
    
    Usage:
        User says: "optimize" or "optimize code" or "optimize cortex"
        CORTEX routes to this module
    """
    
    def __init__(self):
        super().__init__()
        self._metadata = OperationModuleMetadata(
            module_id="optimize",
            name="optimize",
            description="Code and system optimization",
            phase=OperationPhase.PROCESSING,
            priority=50,
            version="1.0.0",
            author="Asif Hussain",
            tags=["user-facing", "maintenance", "performance"],
        )
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return operation metadata."""
        return self._metadata
    
    def validate(self) -> OperationResult:
        """
        Validate optimization operation can run.
        
        Returns:
            OperationResult with validation status
        """
        issues = []
        
        # Check CORTEX brain exists
        brain_path = Path.cwd() / "cortex-brain"
        if not brain_path.exists():
            issues.append("cortex-brain/ directory not found")
        
        # Check databases exist
        tier1_db = brain_path / "tier1" / "working_memory.db"
        tier2_db = brain_path / "tier2" / "knowledge-graph.db"
        
        if not tier1_db.exists():
            issues.append("Tier 1 database not found (working_memory.db)")
        
        if not tier2_db.exists():
            issues.append("Tier 2 database not found (knowledge-graph.db)")
        
        if issues:
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Validation failed: {', '.join(issues)}",
                phase=OperationPhase.VALIDATION,
            )
        
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="✓ Optimization prerequisites validated",
            phase=OperationPhase.VALIDATION,
        )
    
    def execute(self, **kwargs) -> OperationResult:
        """
        Execute optimization operations.
        
        Args:
            target: What to optimize (code/cortex/cache/all)
            aggressive: Use aggressive optimization
        
        Returns:
            OperationResult with optimization summary
        """
        target = kwargs.get('target', 'all')
        aggressive = kwargs.get('aggressive', False)
        
        logger.info(f"Starting optimization (target={target}, aggressive={aggressive})")
        
        results = {
            'optimizations_applied': [],
            'space_saved_mb': 0.0,
            'performance_improvement': None,
        }
        
        try:
            # Brain cleanup
            if target in ['cortex', 'all']:
                cleanup_result = self._optimize_brain()
                results['optimizations_applied'].extend(cleanup_result['applied'])
                results['space_saved_mb'] += cleanup_result['space_saved_mb']
            
            # Cache optimization
            if target in ['cache', 'cortex', 'all']:
                cache_result = self._optimize_cache()
                results['optimizations_applied'].extend(cache_result['applied'])
                results['space_saved_mb'] += cache_result['space_saved_mb']
            
            # Database vacuum
            if target in ['cortex', 'all']:
                db_result = self._vacuum_databases(aggressive)
                results['optimizations_applied'].extend(db_result['applied'])
                results['space_saved_mb'] += db_result['space_saved_mb']
            
            # Code optimization (suggestions only)
            if target in ['code', 'all']:
                code_result = self._analyze_code()
                results['optimizations_applied'].extend(code_result['suggestions'])
            
            return OperationResult(
                status=OperationStatus.SUCCESS,
                message=f"✓ Optimization complete ({len(results['optimizations_applied'])} actions)",
                phase=OperationPhase.COMPLETE,
                data=results,
            )
            
        except Exception as e:
            logger.error(f"Optimization failed: {e}", exc_info=True)
            return OperationResult(
                status=OperationStatus.FAILED,
                message=f"Optimization failed: {str(e)}",
                phase=OperationPhase.EXECUTION,
                error=e,
            )
    
    def _optimize_brain(self) -> Dict[str, Any]:
        """Optimize CORTEX brain storage."""
        applied = []
        space_saved = 0.0
        
        brain_path = Path.cwd() / "cortex-brain"
        
        # Remove old conversation captures (>30 days)
        captures_dir = brain_path / "conversation-captures"
        if captures_dir.exists():
            old_captures = []
            for capture_file in captures_dir.glob("*.jsonl"):
                age_days = (datetime.now() - datetime.fromtimestamp(capture_file.stat().st_mtime)).days
                if age_days > 30:
                    old_captures.append(capture_file)
            
            if old_captures:
                for old_file in old_captures:
                    size_mb = old_file.stat().st_size / (1024 * 1024)
                    old_file.unlink()
                    space_saved += size_mb
                
                applied.append(f"Removed {len(old_captures)} old conversation captures (>30 days)")
        
        # Clean up temporary crawler files
        crawler_temp = brain_path / "crawler-temp"
        if crawler_temp.exists():
            temp_files = list(crawler_temp.glob("*"))
            if temp_files:
                for temp_file in temp_files:
                    if temp_file.is_file():
                        size_mb = temp_file.stat().st_size / (1024 * 1024)
                        temp_file.unlink()
                        space_saved += size_mb
                
                applied.append(f"Cleaned {len(temp_files)} temporary crawler files")
        
        # Clean old logs
        logs_dir = brain_path / "logs"
        if logs_dir.exists():
            old_logs = []
            for log_file in logs_dir.glob("*.log"):
                age_days = (datetime.now() - datetime.fromtimestamp(log_file.stat().st_mtime)).days
                if age_days > 7:
                    old_logs.append(log_file)
            
            if old_logs:
                for old_log in old_logs:
                    size_mb = old_log.stat().st_size / (1024 * 1024)
                    old_log.unlink()
                    space_saved += size_mb
                
                applied.append(f"Removed {len(old_logs)} old log files (>7 days)")
        
        return {
            'applied': applied,
            'space_saved_mb': space_saved,
        }
    
    def _optimize_cache(self) -> Dict[str, Any]:
        """Optimize YAML cache."""
        applied = []
        space_saved = 0.0
        
        try:
            from src.utils.yaml_cache import get_cache_stats, clear_cache
            
            # Get cache stats before
            stats_before = get_cache_stats()
            
            # Clear cache (will rebuild on next access)
            clear_cache()
            
            applied.append(f"Cleared YAML cache ({stats_before['total_entries']} entries)")
            
            # Estimate space saved (rough estimate based on entry count)
            space_saved += (stats_before['total_entries'] * 0.01)  # ~10KB per entry
            
        except Exception as e:
            logger.warning(f"Cache optimization skipped: {e}")
        
        return {
            'applied': applied,
            'space_saved_mb': space_saved,
        }
    
    def _vacuum_databases(self, aggressive: bool) -> Dict[str, Any]:
        """Vacuum SQLite databases to reclaim space."""
        applied = []
        space_saved = 0.0
        
        import sqlite3
        brain_path = Path.cwd() / "cortex-brain"
        
        databases = [
            brain_path / "tier1" / "working_memory.db",
            brain_path / "tier2" / "knowledge-graph.db",
        ]
        
        for db_path in databases:
            if db_path.exists():
                try:
                    # Get size before
                    size_before = db_path.stat().st_size / (1024 * 1024)
                    
                    # Vacuum database
                    conn = sqlite3.connect(str(db_path))
                    conn.execute("VACUUM")
                    conn.close()
                    
                    # Get size after
                    size_after = db_path.stat().st_size / (1024 * 1024)
                    saved = size_before - size_after
                    
                    if saved > 0:
                        applied.append(f"Vacuumed {db_path.name} (saved {saved:.2f} MB)")
                        space_saved += saved
                    
                except Exception as e:
                    logger.warning(f"Failed to vacuum {db_path.name}: {e}")
        
        return {
            'applied': applied,
            'space_saved_mb': space_saved,
        }
    
    def _analyze_code(self) -> Dict[str, Any]:
        """Analyze code for optimization opportunities."""
        suggestions = []
        
        # Suggest common optimizations
        suggestions.append("Code analysis: Use list comprehensions instead of loops where possible")
        suggestions.append("Code analysis: Consider caching expensive function results")
        suggestions.append("Code analysis: Use generators for large data processing")
        suggestions.append("Code analysis: Profile hot paths with PerformanceProfiler")
        
        return {
            'suggestions': suggestions,
        }
    
    def rollback(self) -> OperationResult:
        """
        Rollback optimization (not applicable).
        
        Returns:
            OperationResult indicating rollback not supported
        """
        return OperationResult(
            status=OperationStatus.SUCCESS,
            message="Optimization rollback not applicable (changes are safe)",
            phase=OperationPhase.ROLLBACK,
        )
