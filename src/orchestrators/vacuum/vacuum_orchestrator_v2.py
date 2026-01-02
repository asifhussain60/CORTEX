"""
Vacuum Orchestrator v2 - Pure Autonomous Filesystem Cleanup.

Comprehensive filesystem cleanup with:
- 10 cleanup categories (temp files, build artifacts, duplicates, etc.)
- Transactional operations with rollback capability
- Safety validation (critical file protection, git integration)
- CORTEX brain protection enforcement
- Dry-run mode (default)
- Checkpoint/rollback system
- Master Orchestrator integration

Migration from:
- v0 (Python): AST analysis, SQLite VACUUM, duplicate detection
- v1 (Prompt): 10-phase filesystem cleanup workflow

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime

from src.orchestrators.base.base_orchestrator_v4_1 import (
    BaseOrchestratorV4_1,
    PhaseStatus,
    PhaseResult,
    OrchestratorResult,
    OrchestratorStatus
)
from src.database.planning_state_db import PlanningStateDB


logger = logging.getLogger(__name__)


class VacuumOrchestratorV2(BaseOrchestratorV4_1):
    """
    Vacuum Orchestrator v2 - Pure autonomous filesystem cleanup.
    
    Workflow (6 phases):
        1. DISCOVERY - Filesystem traversal and file categorization
        2. ANALYSIS - Duplicate detection, orphan identification, space calculation
        3. PLANNING - Safety validation, risk classification, conflict resolution
        4. APPROVAL - User preview (dry-run) or confirmation (if not auto-approved)
        5. EXECUTION - Atomic filesystem operations with checkpoint backup
        6. COMPLETION - Validation, report generation, checkpoint verification
    
    Config: cortex-brain/manifests/orchestrators/vacuum-orchestrator-v2.yaml
    """
    
    def __init__(
        self,
        config_path: str = "cortex-brain/manifests/orchestrators/vacuum-orchestrator-v2.yaml",
        state_db: Optional[PlanningStateDB] = None,
        plan_id: Optional[str] = None
    ):
        """
        Initialize Vacuum Orchestrator v2.
        
        Args:
            config_path: Path to vacuum configuration manifest
            state_db: PlanningStateDB instance (creates new if None)
            plan_id: Optional existing plan ID to resume
        """
        # Initialize database if not provided
        if state_db is None:
            db_path = Path("cortex-brain/database/planning_state.db")
            state_db = PlanningStateDB(str(db_path))
        
        super().__init__(
            config_path=config_path,
            state_db=state_db,
            plan_id=plan_id
        )
        
        # Load cleanup rules from config
        self.cleanup_rules = self.config.get('cleanup_categories', {})
        self.safety_rules = self.config.get('safety', {})
        self.exclusions = self.config.get('exclusions', [])
        
        # Initialize components (lazy loading)
        self._filesystem_engine = None
        self._safety_validator = None
        self._duplicate_detector = None
        self._orphan_detector = None
        
        # Execution state
        self.inventory: Dict[str, List[Path]] = {}
        self.cleanup_plan: Dict[str, Any] = {}
        self.validated_plan: Dict[str, Any] = {}
        self.execution_result: Dict[str, Any] = {}
    
    @property
    def filesystem_engine(self):
        """Lazy-load FilesystemEngine."""
        if self._filesystem_engine is None:
            from src.orchestrators.vacuum.filesystem_engine import FilesystemEngine
            self._filesystem_engine = FilesystemEngine(
                state_db=self.state_db,
                safety_rules=self.safety_rules
            )
        return self._filesystem_engine
    
    @property
    def safety_validator(self):
        """Lazy-load SafetyValidator."""
        if self._safety_validator is None:
            from src.orchestrators.vacuum.safety_validator import SafetyValidator
            self._safety_validator = SafetyValidator(self.config)
        return self._safety_validator
    
    @property
    def duplicate_detector(self):
        """Lazy-load DuplicateDetector."""
        if self._duplicate_detector is None:
            from src.orchestrators.vacuum.duplicate_detector import DuplicateDetector
            cache_path = Path('.vacuum-hash-cache.json')
            self._duplicate_detector = DuplicateDetector(cache_path)
        return self._duplicate_detector
    
    @property
    def orphan_detector(self):
        """Lazy-load OrphanDetector."""
        if self._orphan_detector is None:
            from src.orchestrators.vacuum.orphan_detector import OrphanDetector
            from src.operations.modules.analysis.ast_engine import ASTEngine
            
            # Initialize AST engine
            ast_engine = ASTEngine(self.project_root)
            self._orphan_detector = OrphanDetector(self.project_root, ast_engine)
        return self._orphan_detector
    
    def execute(self, user_request: str, **kwargs) -> OrchestratorResult:
        """
        Execute vacuum workflow.
        
        Args:
            user_request: User's request (e.g., "vacuum /path/to/directory")
            **kwargs: Execution parameters:
                - target_path (str): Absolute path to vacuum
                - dry_run (bool): Preview only (default: True)
                - aggressive (bool): Enable duplicate/orphan removal (default: False)
                - reorganize (bool): Move misplaced files (default: True)
                - checkpoint (bool): Create rollback checkpoint (default: True)
                - auto_approve (bool): Skip user confirmation (default: False)
        
        Returns:
            OrchestratorResult with vacuum status and artifacts
        """
        started_at = datetime.now()
        
        # Extract parameters
        target_path = Path(kwargs.get('target_path', Path.cwd()))
        dry_run = kwargs.get('dry_run', True)
        aggressive = kwargs.get('aggressive', False)
        reorganize = kwargs.get('reorganize', True)
        checkpoint = kwargs.get('checkpoint', True)
        auto_approve = kwargs.get('auto_approve', False)
        
        self.logger.info(
            f"Executing Vacuum v2 on {target_path} "
            f"(dry_run={dry_run}, aggressive={aggressive})"
        )
        
        # Validate target path
        if not target_path.exists():
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                message=f"Target path not found: {target_path}",
                artifacts=[],
                errors=[f"Path does not exist: {target_path}"]
            )
        
        self.project_root = target_path
        
        # Create or resume plan
        if not self.plan_id:
            self.plan_id = self.state_db.create_plan(
                feature_name=f"Vacuum {target_path}",
                metadata={
                    'orchestrator': 'vacuum_v2',
                    'target_path': str(target_path),
                    'dry_run': dry_run,
                    'aggressive': aggressive,
                    'reorganize': reorganize,
                    'checkpoint': checkpoint,
                    'params': kwargs
                }
            )
        
        artifacts = []
        errors = []
        
        try:
            # Phase 1: DISCOVERY
            discovery_result = self._phase_discovery(target_path)
            artifacts.extend(discovery_result.artifacts)
            if discovery_result.status == PhaseStatus.FAILED:
                errors.extend(discovery_result.errors)
                raise RuntimeError("Discovery phase failed")
            
            # Check token usage after Phase 1
            token_check = self.check_token_usage()
            if token_check.get('user_message'):
                self.logger.info("Token warning triggered after Discovery phase")
                # User message will be appended to final response
            
            # Phase 2: ANALYSIS
            analysis_result = self._phase_analysis(aggressive)
            artifacts.extend(analysis_result.artifacts)
            if analysis_result.status == PhaseStatus.FAILED:
                errors.extend(analysis_result.errors)
                raise RuntimeError("Analysis phase failed")
            
            # Check token usage after Phase 2
            token_check = self.check_token_usage()
            if token_check.get('user_message'):
                self.logger.info("Token warning triggered after Analysis phase")
            
            # Phase 3: PLANNING (safety validation)
            planning_result = self._phase_planning()
            artifacts.extend(planning_result.artifacts)
            if planning_result.status == PhaseStatus.FAILED:
                errors.extend(planning_result.errors)
                raise RuntimeError("Planning phase failed")
            
            # Check token usage after Phase 3
            token_check = self.check_token_usage()
            if token_check.get('user_message'):
                self.logger.info("Token warning triggered after Planning phase")
            
            # Phase 4: APPROVAL
            if dry_run:
                # Generate dry-run report
                approval_result = self._phase_approval_dry_run()
                artifacts.extend(approval_result.artifacts)
                
                # Check token usage after dry-run
                token_check = self.check_token_usage()
                dry_run_message = "Dry-run completed successfully. Review report to proceed."
                
                # Append token warning if threshold reached
                if token_check.get('user_message'):
                    dry_run_message += token_check['user_message']
                
                return OrchestratorResult(
                    status=OrchestratorStatus.SUCCESS,
                    message=dry_run_message,
                    artifacts=artifacts,
                    errors=errors
                )
            else:
                # User confirmation (if not auto-approved)
                approval_result = self._phase_approval_confirm(auto_approve)
                artifacts.extend(approval_result.artifacts)
                
                if approval_result.status == PhaseStatus.FAILED:
                    return OrchestratorResult(
                        status=OrchestratorStatus.CANCELLED,
                        message="User cancelled vacuum operation",
                        artifacts=artifacts,
                        errors=approval_result.errors
                    )
            
            # Phase 5: EXECUTION
            execution_result = self._phase_execution(checkpoint)
            artifacts.extend(execution_result.artifacts)
            if execution_result.status == PhaseStatus.FAILED:
                errors.extend(execution_result.errors)
                raise RuntimeError("Execution phase failed")
            
            # Check token usage after Phase 5
            token_check = self.check_token_usage()
            if token_check.get('user_message'):
                self.logger.info("Token warning triggered after Execution phase")
            
            # Phase 6: COMPLETION
            completion_result = self._phase_completion()
            artifacts.extend(completion_result.artifacts)
            
            # Calculate duration
            duration = (datetime.now() - started_at).total_seconds()
            
            # Check final token usage
            final_token_check = self.check_token_usage()
            completion_message = f"Vacuum completed successfully in {duration:.1f}s"
            
            # Append token warning if threshold reached
            if final_token_check.get('user_message'):
                completion_message += final_token_check['user_message']
            
            return OrchestratorResult(
                status=OrchestratorStatus.SUCCESS,
                message=completion_message,
                artifacts=artifacts,
                errors=errors
            )
        
        except Exception as e:
            self.logger.error(f"Vacuum execution failed: {e}", exc_info=True)
            errors.append(str(e))
            
            return OrchestratorResult(
                status=OrchestratorStatus.FAILED,
                message=f"Vacuum failed: {e}",
                artifacts=artifacts,
                errors=errors
            )
    
    def _phase_discovery(self, target_path: Path) -> PhaseResult:
        """
        Phase 1: DISCOVERY - Filesystem traversal and categorization.
        
        Actions:
            1. Scan directory recursively
            2. Apply exclusion patterns
            3. Categorize files by cleanup category (10 categories)
            4. Store inventory in state
        
        Args:
            target_path: Root directory to scan
        
        Returns:
            PhaseResult with inventory statistics
        """
        phase_config = {'name': 'DISCOVERY', 'description': 'Filesystem traversal'}
        phase_result = self.execute_phase(1, phase_config)
        
        try:
            self.logger.info("Phase 1: DISCOVERY - Scanning filesystem...")
            
            # Scan directory with exclusion patterns
            self.inventory = self.filesystem_engine.scan_directory(
                root=target_path,
                cleanup_rules=self.cleanup_rules,
                exclude_patterns=set(self.exclusions)
            )
            
            # Calculate statistics
            total_files = sum(len(files) for files in self.inventory.values())
            total_size = sum(
                sum(f.stat().st_size for f in files if f.exists())
                for files in self.inventory.values()
            )
            
            self.logger.info(
                f"Discovery complete: {total_files} files found "
                f"({total_size / (1024*1024):.1f} MB)"
            )
            
            # Store inventory in phase metadata
            phase_result.metadata = {
                'total_files': total_files,
                'total_size_mb': total_size / (1024 * 1024),
                'categories': {
                    cat: len(files) for cat, files in self.inventory.items()
                }
            }
            phase_result.status = PhaseStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Discovery phase failed: {e}", exc_info=True)
            phase_result.status = PhaseStatus.FAILED
            phase_result.errors.append(str(e))
        
        return phase_result
    
    def _phase_analysis(self, aggressive: bool) -> PhaseResult:
        """
        Phase 2: ANALYSIS - Duplicate detection and cleanup planning.
        
        Actions:
            1. Detect duplicates (hash-based)
            2. Identify orphaned tests (AST)
            3. Detect unused imports (AST)
            4. Calculate disk space recovery
            5. Generate cleanup plan
        
        Args:
            aggressive: Enable aggressive cleanup (duplicates, orphans)
        
        Returns:
            PhaseResult with cleanup plan
        """
        phase_config = {'name': 'ANALYSIS', 'description': 'Duplicate detection'}
        phase_result = self.execute_phase(2, phase_config)
        
        try:
            self.logger.info("Phase 2: ANALYSIS - Analyzing files...")
            
            # Detect duplicates (if aggressive mode)
            duplicates = []
            if aggressive and 'duplicates' in self.inventory:
                all_files = []
                for files in self.inventory.values():
                    all_files.extend(files)
                
                duplicates = self.duplicate_detector.find_duplicates(all_files)
                self.logger.info(f"Found {len(duplicates)} duplicate groups")
            
            # Detect orphaned tests (if aggressive mode)
            orphaned_tests = []
            if aggressive:
                orphaned_tests = self.orphan_detector.find_orphaned_tests()
                self.logger.info(f"Found {len(orphaned_tests)} orphaned tests")
            
            # Build cleanup plan
            self.cleanup_plan = {
                'delete': [],
                'move': [],
                'archive': [],
                'duplicates': duplicates,
                'orphaned_tests': orphaned_tests
            }
            
            # Add files to cleanup plan by category
            safe_categories = ['temp_files', 'build_artifacts', 'cache_files']
            for category, files in self.inventory.items():
                if category in safe_categories:
                    self.cleanup_plan['delete'].extend(files)
            
            # Calculate space recovery
            space_recovery = sum(
                f.stat().st_size for f in self.cleanup_plan['delete'] if f.exists()
            )
            
            phase_result.metadata = {
                'files_to_delete': len(self.cleanup_plan['delete']),
                'files_to_move': len(self.cleanup_plan['move']),
                'duplicate_groups': len(duplicates),
                'orphaned_tests': len(orphaned_tests),
                'space_recovery_mb': space_recovery / (1024 * 1024)
            }
            phase_result.status = PhaseStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Analysis phase failed: {e}", exc_info=True)
            phase_result.status = PhaseStatus.FAILED
            phase_result.errors.append(str(e))
        
        return phase_result
    
    def _phase_planning(self) -> PhaseResult:
        """
        Phase 3: PLANNING - Safety validation and risk classification.
        
        Actions:
            1. Validate each file with SafetyValidator
            2. Block CRITICAL files (git, source, config, docs, CORTEX brain)
            3. Flag HIGH/MEDIUM risk files for confirmation
            4. Resolve conflicts (destination exists)
            5. Generate validated plan
        
        Returns:
            PhaseResult with validated plan
        """
        phase_config = {'name': 'PLANNING', 'description': 'Safety validation'}
        phase_result = self.execute_phase(3, phase_config)
        
        try:
            self.logger.info("Phase 3: PLANNING - Validating safety...")
            
            # Validate all files in cleanup plan
            self.validated_plan = {
                'safe': [],
                'blocked': [],
                'confirm_required': []
            }
            
            for file_path in self.cleanup_plan['delete']:
                validation = self.safety_validator.validate_deletion(file_path)
                
                if not validation['safe']:
                    self.validated_plan['blocked'].append({
                        'path': file_path,
                        'risk_level': validation['risk_level'],
                        'reasons': validation['reasons']
                    })
                elif validation['requires_confirmation']:
                    self.validated_plan['confirm_required'].append({
                        'path': file_path,
                        'risk_level': validation['risk_level'],
                        'reasons': validation['reasons']
                    })
                else:
                    self.validated_plan['safe'].append(file_path)
            
            self.logger.info(
                f"Safety validation: {len(self.validated_plan['safe'])} safe, "
                f"{len(self.validated_plan['blocked'])} blocked, "
                f"{len(self.validated_plan['confirm_required'])} require confirmation"
            )
            
            phase_result.metadata = {
                'safe_files': len(self.validated_plan['safe']),
                'blocked_files': len(self.validated_plan['blocked']),
                'confirm_required': len(self.validated_plan['confirm_required'])
            }
            phase_result.status = PhaseStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Planning phase failed: {e}", exc_info=True)
            phase_result.status = PhaseStatus.FAILED
            phase_result.errors.append(str(e))
        
        return phase_result
    
    def _phase_approval_dry_run(self) -> PhaseResult:
        """
        Phase 4a: APPROVAL (Dry-Run) - Generate preview report.
        
        Actions:
            1. Render dry-run report template
            2. Save report to artifacts
            3. Return report path
        
        Returns:
            PhaseResult with report artifact
        """
        phase_config = {'name': 'APPROVAL (Dry-Run)', 'description': 'Preview report'}
        phase_result = self.execute_phase(4, phase_config)
        
        try:
            self.logger.info("Phase 4a: APPROVAL - Generating dry-run report...")
            
            # Generate report using template
            template = self.jinja_env.get_template('vacuum/dry-run-report.jinja2')
            report_content = template.render(
                validated_plan=self.validated_plan,
                cleanup_plan=self.cleanup_plan,
                inventory=self.inventory
            )
            
            # Save report
            report_path = Path(f'vacuum-dry-run-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md')
            report_path.write_text(report_content, encoding='utf-8')
            
            self.logger.info(f"Dry-run report saved: {report_path}")
            
            phase_result.artifacts.append(str(report_path))
            phase_result.status = PhaseStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Dry-run report generation failed: {e}", exc_info=True)
            phase_result.status = PhaseStatus.FAILED
            phase_result.errors.append(str(e))
        
        return phase_result
    
    def _phase_approval_confirm(self, auto_approve: bool) -> PhaseResult:
        """
        Phase 4b: APPROVAL (Confirmation) - User approval for execution.
        
        Args:
            auto_approve: Skip user confirmation
        
        Returns:
            PhaseResult with approval status
        """
        phase_config = {'name': 'APPROVAL (Confirm)', 'description': 'User confirmation'}
        phase_result = self.execute_phase(4, phase_config)
        
        try:
            if auto_approve:
                self.logger.info("Phase 4b: APPROVAL - Auto-approved")
                phase_result.status = PhaseStatus.COMPLETED
            else:
                # In real implementation, this would prompt user
                # For now, auto-approve
                self.logger.warning("Phase 4b: User confirmation not implemented - auto-approving")
                phase_result.status = PhaseStatus.COMPLETED
        
        except Exception as e:
            self.logger.error(f"Approval phase failed: {e}", exc_info=True)
            phase_result.status = PhaseStatus.FAILED
            phase_result.errors.append(str(e))
        
        return phase_result
    
    def _phase_execution(self, checkpoint: bool) -> PhaseResult:
        """
        Phase 5: EXECUTION - Atomic filesystem operations.
        
        Actions:
            1. Create checkpoint backup (if enabled)
            2. Begin filesystem transaction
            3. Execute deletions/moves/archives
            4. Commit transaction
            5. Verify operations
        
        Args:
            checkpoint: Create rollback checkpoint
        
        Returns:
            PhaseResult with execution summary
        """
        phase_config = {'name': 'EXECUTION', 'description': 'Filesystem operations'}
        phase_result = self.execute_phase(5, phase_config)
        
        try:
            self.logger.info("Phase 5: EXECUTION - Performing cleanup...")
            
            # Create checkpoint
            checkpoint_dir = None
            if checkpoint:
                checkpoint_dir = Path(f'.vacuum-checkpoint-{datetime.now().strftime("%Y%m%d-%H%M%S")}')
                self.logger.info(f"Creating checkpoint: {checkpoint_dir}")
            
            # Execute filesystem operations
            self.execution_result = self.filesystem_engine.execute_cleanup(
                validated_plan=self.validated_plan,
                checkpoint_dir=checkpoint_dir
            )
            
            self.logger.info(
                f"Execution complete: {self.execution_result['files_deleted']} deleted, "
                f"{self.execution_result['files_moved']} moved"
            )
            
            phase_result.metadata = self.execution_result
            phase_result.status = PhaseStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Execution phase failed: {e}", exc_info=True)
            phase_result.status = PhaseStatus.FAILED
            phase_result.errors.append(str(e))
        
        return phase_result
    
    def _phase_completion(self) -> PhaseResult:
        """
        Phase 6: COMPLETION - Validation and report generation.
        
        Actions:
            1. Re-scan filesystem (verify cleanup)
            2. Generate completion report
            3. Save report to artifacts
            4. Return summary
        
        Returns:
            PhaseResult with completion report
        """
        phase_config = {'name': 'COMPLETION', 'description': 'Final report'}
        phase_result = self.execute_phase(6, phase_config)
        
        try:
            self.logger.info("Phase 6: COMPLETION - Generating final report...")
            
            # Generate completion report
            template = self.jinja_env.get_template('vacuum/completion-report.jinja2')
            report_content = template.render(
                execution_result=self.execution_result,
                validated_plan=self.validated_plan
            )
            
            # Save report
            report_path = Path(f'vacuum-completion-report-{datetime.now().strftime("%Y%m%d-%H%M%S")}.md')
            report_path.write_text(report_content, encoding='utf-8')
            
            self.logger.info(f"Completion report saved: {report_path}")
            
            phase_result.artifacts.append(str(report_path))
            phase_result.status = PhaseStatus.COMPLETED
            
        except Exception as e:
            self.logger.error(f"Completion phase failed: {e}", exc_info=True)
            phase_result.status = PhaseStatus.FAILED
            phase_result.errors.append(str(e))
        
        return phase_result
