"""
Cleanup Orchestrator v2 - Autonomous cleanup with selective modes.

Converts maintenance Phase 2 cleanup to standalone autonomous orchestrator
with BaseOrchestrator v4.1 compliance, Master Orchestrator routing, and
state persistence.

Modes:
- cache: Cache directories only (HIGH priority, safe, fast)
- logs: Log management only (MEDIUM priority, rotation/archiving)
- artifacts: Build artifacts only (MEDIUM priority, backups/reports)
- full: All cleanup categories (cache + logs + artifacts)
- git: Git optimization only (LOW priority, slow but thorough)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import time
from typing import Dict, Any, Optional, List
from pathlib import Path
from datetime import datetime

from src.orchestrators.base.base_orchestrator_v4_1 import (
    BaseOrchestratorV4_1,
    PhaseStatus,
    PhaseResult
)
from src.orchestrators.base.base_orchestrator import (
    OrchestratorResult,
    OrchestratorStatus,
    ErrorResult
)
from src.database.planning_state_db import PlanningStateDB

# Import category cleaners
from src.orchestrators.cleanup.cache_cleaner import CacheCleaner
from src.orchestrators.cleanup.log_manager import LogManager
from src.orchestrators.cleanup.artifact_remover import ArtifactRemover
from src.orchestrators.cleanup.git_optimizer import GitOptimizer


logger = logging.getLogger(__name__)


class CleanupOrchestratorV2(BaseOrchestratorV4_1):
    """
    Autonomous cleanup orchestrator v2.
    
    Features:
    - Selective cleanup modes (cache/logs/artifacts/full/git)
    - BaseOrchestrator v4.1 compliance
    - State persistence in PlanningStateDB
    - Template-driven reporting
    - Master Orchestrator routing integration
    - Backward compatible with maintenance Phase 2
    
    Modes:
        cache      - Cache directories only (~10s, 1GB freed)
        logs       - Log management (~10s, 250MB freed)
        artifacts  - Build artifacts (~60s, 2.5GB freed)
        full       - All cleanup categories (~80s, 3.75GB freed)
        git        - Git optimization (~180s, 100MB freed)
    
    Usage:
        orchestrator = CleanupOrchestratorV2(config_path, state_db)
        result = orchestrator.execute(mode="cache")
    """
    
    def __init__(
        self,
        config_path: str,
        state_db: Optional[PlanningStateDB] = None,
        plan_id: Optional[str] = None,
        workspace_root: Optional[Path] = None
    ):
        """
        Initialize Cleanup Orchestrator v2.
        
        Args:
            config_path: Path to cleanup-orchestrator-v2.yaml manifest
            state_db: PlanningStateDB instance for state persistence (creates new if None)
            plan_id: Optional existing plan ID to resume
            workspace_root: Optional workspace root (defaults to current directory)
        """
        # Initialize database if not provided
        if state_db is None:
            db_path = "cortex-brain/database/planning_state.db"
            state_db = PlanningStateDB(db_path=db_path)
        
        super().__init__(config_path, state_db, plan_id)
        
        self.workspace_root = Path(workspace_root or Path.cwd()).resolve()
        
        # Load cleanup rules
        rules_file = self.config.get('rules_file', 'cortex-brain/cleanup-rules.yaml')
        self.rules_path = self.workspace_root / rules_file
        
        # Initialize category cleaners
        self.cache_cleaner = CacheCleaner(
            workspace_root=self.workspace_root,
            rules_path=self.rules_path,
            config=self.config
        )
        
        self.log_manager = LogManager(
            workspace_root=self.workspace_root,
            rules_path=self.rules_path,
            config=self.config
        )
        
        self.artifact_remover = ArtifactRemover(
            workspace_root=self.workspace_root,
            rules_path=self.rules_path,
            config=self.config
        )
        
        self.git_optimizer = GitOptimizer(
            workspace_root=self.workspace_root,
            config=self.config
        )
        
        self.logger.info(
            f"CleanupOrchestratorV2 initialized (workspace={self.workspace_root})"
        )
    
    def execute(self, user_request: str = "", mode: str = "full", **kwargs) -> OrchestratorResult:
        """
        Execute cleanup based on mode.
        
        Args:
            user_request: User's natural language request (optional)
            mode: Cleanup mode (cache, logs, artifacts, full, git)
            **kwargs: Additional parameters
        
        Returns:
            OrchestratorResult with cleanup statistics and report
        
        Raises:
            ValueError: If mode is invalid
        """
        start_time = time.time()
        
        # Extract mode from user_request if not provided
        if not mode or mode == "full":
            mode = self._extract_mode_from_request(user_request)
        
        # Validate mode
        valid_modes = ["cache", "logs", "artifacts", "full", "git"]
        if mode not in valid_modes:
            return ErrorResult(
                orchestrator=self.name,
                error_message=f"Invalid cleanup mode: {mode}. Valid modes: {valid_modes}",
                error_type="ValueError"
            )
        
        self.logger.info(f"Starting cleanup in '{mode}' mode")
        
        # Create session in database
        session_id = self._create_session(mode)
        
        try:
            # Execute based on mode
            if mode == "cache":
                result = self._execute_cache_cleanup()
            elif mode == "logs":
                result = self._execute_log_cleanup()
            elif mode == "artifacts":
                result = self._execute_artifact_cleanup()
            elif mode == "full":
                result = self._execute_full_cleanup()
            elif mode == "git":
                result = self._execute_git_cleanup()
            
            # Add execution metadata
            result['mode'] = mode
            result['session_id'] = session_id
            result['workspace_root'] = str(self.workspace_root)
            result['duration_seconds'] = time.time() - start_time
            
            # Save result to database
            self._save_session_result(session_id, result)
            
            # Render report
            report = self._render_report(result, mode)
            
            # Complete session
            self.state_db.complete_session(session_id)
            
            return OrchestratorResult(
                orchestrator=self.name,
                status=OrchestratorStatus.SUCCESS,
                artifacts=result.get('artifacts', []),
                metadata={
                    'mode': mode,
                    'session_id': session_id,
                    'statistics': result.get('statistics', {}),
                    'report': report
                },
                execution_time=time.time() - start_time
            )
        
        except Exception as e:
            self.logger.error(f"Cleanup execution failed: {e}", exc_info=True)
            self.state_db.fail_session(session_id, str(e))
            
            return ErrorResult(
                orchestrator=self.name,
                error_message=str(e),
                error_type=type(e).__name__,
                context={'mode': mode, 'session_id': session_id}
            )
    
    def _extract_mode_from_request(self, user_request: str) -> str:
        """
        Extract cleanup mode from user's natural language request.
        
        Args:
            user_request: User's request string
        
        Returns:
            Extracted mode (default: "full")
        """
        request_lower = user_request.lower()
        
        if "cache" in request_lower:
            return "cache"
        elif "log" in request_lower:
            return "logs"
        elif "artifact" in request_lower:
            return "artifacts"
        elif "git" in request_lower:
            return "git"
        else:
            return "full"  # Default to full cleanup
    
    def _create_session(self, mode: str) -> str:
        """
        Create cleanup session in database.
        
        Args:
            mode: Cleanup mode
        
        Returns:
            Session ID
        """
        session_data = {
            'orchestrator': self.name,
            'intent': f'cleanup {mode}',
            'metadata': {
                'mode': mode,
                'workspace_root': str(self.workspace_root)
            }
        }
        
        return self.state_db.create_session(**session_data)
    
    def _save_session_result(self, session_id: str, result: Dict[str, Any]) -> None:
        """
        Save cleanup result to database.
        
        Args:
            session_id: Session ID
            result: Cleanup result dictionary
        """
        self.state_db.save_session_artifact(
            session_id=session_id,
            artifact_type='cleanup_result',
            artifact_data=result
        )
    
    def _execute_cache_cleanup(self) -> Dict[str, Any]:
        """
        Execute cache cleanup (Group 1).
        
        Returns:
            Cleanup result dictionary
        """
        self.logger.info("Executing cache cleanup")
        return self.cache_cleaner.execute()
    
    def _execute_log_cleanup(self) -> Dict[str, Any]:
        """
        Execute log management (Group 2).
        
        Returns:
            Cleanup result dictionary
        """
        self.logger.info("Executing log management")
        return self.log_manager.execute()
    
    def _execute_artifact_cleanup(self) -> Dict[str, Any]:
        """
        Execute artifact removal (Group 3).
        
        Returns:
            Cleanup result dictionary
        """
        self.logger.info("Executing artifact removal")
        return self.artifact_remover.execute()
    
    def _execute_full_cleanup(self) -> Dict[str, Any]:
        """
        Execute full cleanup (cache + logs + artifacts).
        
        Returns:
            Aggregated cleanup result dictionary
        """
        self.logger.info("Executing full cleanup (cache + logs + artifacts)")
        
        results = []
        
        # Execute in priority order
        results.append(self.cache_cleaner.execute())
        results.append(self.log_manager.execute())
        results.append(self.artifact_remover.execute())
        
        # Aggregate statistics
        return self._aggregate_results(results)
    
    def _execute_git_cleanup(self) -> Dict[str, Any]:
        """
        Execute git optimization (Group 4).
        
        Returns:
            Cleanup result dictionary
        """
        self.logger.info("Executing git optimization")
        return self.git_optimizer.execute()
    
    def _aggregate_results(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate multiple cleanup results into single result.
        
        Args:
            results: List of cleanup result dictionaries
        
        Returns:
            Aggregated result dictionary
        """
        aggregated = {
            'timestamp': datetime.now().isoformat(),
            'statistics': {
                'files_scanned': 0,
                'files_deleted': 0,
                'files_archived': 0,
                'folders_deleted': 0,
                'space_freed_bytes': 0,
                'space_freed_mb': 0.0,
                'categories_processed': 0
            },
            'categories': {},
            'errors': [],
            'warnings': [],
            'artifacts': []
        }
        
        # Sum statistics
        for result in results:
            stats = result.get('statistics', {})
            aggregated['statistics']['files_scanned'] += stats.get('files_scanned', 0)
            aggregated['statistics']['files_deleted'] += stats.get('files_deleted', 0)
            aggregated['statistics']['files_archived'] += stats.get('files_archived', 0)
            aggregated['statistics']['folders_deleted'] += stats.get('folders_deleted', 0)
            aggregated['statistics']['space_freed_bytes'] += stats.get('space_freed_bytes', 0)
            aggregated['statistics']['categories_processed'] += stats.get('categories_processed', 0)
            
            # Merge categories
            for cat_name, cat_data in result.get('categories', {}).items():
                aggregated['categories'][cat_name] = cat_data
            
            # Merge errors/warnings
            aggregated['errors'].extend(result.get('errors', []))
            aggregated['warnings'].extend(result.get('warnings', []))
            aggregated['artifacts'].extend(result.get('artifacts', []))
        
        # Calculate MB
        aggregated['statistics']['space_freed_mb'] = (
            aggregated['statistics']['space_freed_bytes'] / (1024 * 1024)
        )
        
        return aggregated
    
    def _render_report(self, result: Dict[str, Any], mode: str) -> str:
        """
        Render cleanup report using Jinja2 template.
        
        Args:
            result: Cleanup result dictionary
            mode: Cleanup mode
        
        Returns:
            Rendered report as markdown string
        """
        try:
            template = self.jinja_env.get_template('cleanup-report.jinja2')
            report = template.render(result=result, mode=mode)
            return report
        except Exception as e:
            self.logger.warning(f"Template rendering failed: {e}")
            # Fallback to simple text report
            return self._render_fallback_report(result, mode)
    
    def _render_fallback_report(self, result: Dict[str, Any], mode: str) -> str:
        """
        Render simple fallback report if template fails.
        
        Args:
            result: Cleanup result dictionary
            mode: Cleanup mode
        
        Returns:
            Simple text report
        """
        stats = result.get('statistics', {})
        
        report = f"""# 🧹 Cleanup Report - {mode.title()} Mode

**Orchestrator:** Cleanup v2  
**Mode:** {mode}  
**Timestamp:** {result.get('timestamp', 'N/A')}  
**Duration:** {result.get('duration_seconds', 0):.2f}s

---

## 📊 Statistics

| Metric | Count |
|--------|-------|
| Files Scanned | {stats.get('files_scanned', 0):,} |
| Files Deleted | {stats.get('files_deleted', 0):,} |
| Files Archived | {stats.get('files_archived', 0):,} |
| Folders Deleted | {stats.get('folders_deleted', 0):,} |
| Space Freed | {stats.get('space_freed_mb', 0):.2f} MB |

---

✅ **Cleanup complete!**
"""
        return report
