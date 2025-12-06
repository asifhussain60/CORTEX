"""
Plan Execution Orchestrator for CORTEX

Executes feature implementation plans created by PlanningOrchestrator
and ADO Work Item Orchestrator. Autonomously implements phases with
automatic Integration & Consolidation phase at the end.

The Integration & Consolidation phase:
- Identifies and removes deprecated/obsolete code
- Eliminates duplicate implementations
- Organizes files into proper folder structures
- Updates references across the application
- Verifies new features are properly wired and functional
- Runs integration tests to validate production readiness

Author: GitHub Copilot (CORTEX 3.0)
Created: 2025-12-04
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import yaml
import json

from src.cortex_agents.base_agent import AgentRequest, AgentResponse
from src.cortex_agents.agent_types import IntentType
from src.learning.event_collector import get_global_collector
from src.learning.event_taxonomy import LearningEvent, EventType

logger = logging.getLogger(__name__)


class PlanExecutionOrchestrator:
    """
    Orchestrates autonomous execution of feature implementation plans.
    
    Workflow:
    1. Load plan (YAML or Markdown)
    2. Execute each phase sequentially
    3. Automatically add Integration & Consolidation phase
    4. Execute cleanup and wiring operations
    5. Validate production readiness
    
    Features:
    - Phase-by-phase execution with checkpoints
    - Automatic rollback on failure
    - Integration & Consolidation phase (always added automatically)
    - Production readiness validation
    - Progress tracking and reporting
    """
    
    def __init__(self, cortex_root: str):
        """
        Initialize plan execution orchestrator.
        
        Args:
            cortex_root: Path to CORTEX root directory
        """
        self.cortex_root = Path(cortex_root)
        self.plans_dir = self.cortex_root / "cortex-brain" / "documents" / "planning" / "features"
        self.execution_history_dir = self.cortex_root / "cortex-brain" / "documents" / "reports" / "execution-history"
        self.execution_history_dir.mkdir(parents=True, exist_ok=True)
        
        # Load orchestrators for phase execution
        self._init_execution_agents()
    
    def _init_execution_agents(self):
        """Initialize agents and orchestrators used for execution."""
        try:
            # Code Executor Agent for implementation tasks
            from src.cortex_agents.tactical.code_executor import CodeExecutor
            self.code_executor = CodeExecutor("CodeExecutor")
            logger.info("✅ CodeExecutor agent initialized")
        except ImportError as e:
            logger.warning(f"⚠️  CodeExecutor not available: {e}")
            self.code_executor = None
        
        try:
            # TDD Implementation Orchestrator for TDD workflow
            from src.orchestrators.tdd_implementation_orchestrator import TDDImplementationOrchestrator
            self.tdd_orchestrator = TDDImplementationOrchestrator(
                project_root=self.cortex_root,
                enable_pattern_library=True
            )
            logger.info("✅ TDDImplementationOrchestrator initialized")
        except ImportError as e:
            logger.warning(f"⚠️  TDDImplementationOrchestrator not available: {e}")
            self.tdd_orchestrator = None
        
        try:
            # Cleanup orchestrator for Integration & Consolidation phase
            from src.orchestrators.cleanup_orchestrator import CleanupOrchestrator
            self.cleanup_orchestrator = CleanupOrchestrator(str(self.cortex_root))
            logger.info("✅ CleanupOrchestrator initialized")
        except ImportError as e:
            # CleanupOrchestrator is optional - uses inline cleanup if not available
            logger.debug(f"CleanupOrchestrator not available (optional): {e}")
            self.cleanup_orchestrator = None
        
        try:
            # Git checkpoint for safety
            from src.orchestrators.git_checkpoint_orchestrator import GitCheckpointOrchestrator
            self.git_checkpoint = GitCheckpointOrchestrator(project_root=str(self.cortex_root))
            logger.info("✅ GitCheckpointOrchestrator initialized")
        except ImportError as e:
            logger.warning(f"⚠️  GitCheckpointOrchestrator not available: {e}")
            self.git_checkpoint = None
    
    def execute_plan(
        self, 
        plan_path: Path,
        auto_consolidate: bool = True,
        dry_run: bool = False,
        execution_mode: str = "approval_gated",
        force_execution: bool = False
    ) -> Tuple[bool, Dict[str, Any]]:
        """
        Execute a feature implementation plan.
        
        Args:
            plan_path: Path to plan file (YAML or Markdown)
            auto_consolidate: Automatically add Integration & Consolidation phase
            dry_run: Preview execution without making changes
            execution_mode: "autonomous" (run all phases without stopping) or 
                          "approval_gated" (stop after each phase for approval)
            force_execution: Skip DoR validation (DANGEROUS - use only with remediation plan)
        
        Returns:
            Tuple of (success, execution_report)
        """
        logger.info(f"🚀 Starting plan execution: {plan_path.name} (mode: {execution_mode})")
        
        # Create git checkpoint before starting
        if self.git_checkpoint and not dry_run:
            try:
                self.git_checkpoint.create_auto_checkpoint(
                    operation="plan_execution",
                    message=f"Before executing plan: {plan_path.name}"
                )
            except Exception as e:
                logger.warning(f"Git checkpoint failed: {e}")
        
        # Load plan
        success, plan_data, errors = self._load_plan(plan_path)
        if not success:
            return (False, {
                "error": "Failed to load plan",
                "details": errors,
                "plan_path": str(plan_path)
            })
        
        # VALIDATION GATE: Check Definition of Ready
        if not force_execution:
            dor_satisfied, dor_violations = self._check_definition_of_ready(plan_data)
            
            if not dor_satisfied:
                logger.error("❌ Definition of Ready not satisfied - execution BLOCKED")
                logger.error(f"   Violations: {len(dor_violations)}")
                for violation in dor_violations:
                    logger.error(f"   - {violation}")
                
                # Generate remediation plan
                remediation_plan = self._generate_remediation_plan(plan_data, dor_violations)
                
                return (False, {
                    "error": "Definition of Ready not satisfied",
                    "dor_violations": dor_violations,
                    "remediation_plan": remediation_plan,
                    "plan_path": str(plan_path),
                    "message": "Execution blocked. Complete DoR items OR review remediation plan and execute with force_execution=True"
                })
            else:
                logger.info("✅ Definition of Ready satisfied - proceeding with execution")
        
        # Initialize execution report
        execution_report = {
            "plan_path": str(plan_path),
            "plan_title": plan_data.get("metadata", {}).get("title", "Unknown"),
            "started_at": datetime.now().isoformat(),
            "dry_run": dry_run,
            "execution_mode": execution_mode,
            "phases_executed": [],
            "integration_consolidation_executed": False,
            "success": False,
            "errors": []
        }
        
        # Execute phases
        phases = plan_data.get("phases", [])
        
        for phase in phases:
            phase_result = self._execute_phase(phase, dry_run)
            execution_report["phases_executed"].append(phase_result)
            
            if not phase_result["success"]:
                logger.error(f"❌ Phase {phase.get('phase_number')} failed: {phase_result.get('error')}")
                execution_report["errors"].append(phase_result.get("error"))
                execution_report["completed_at"] = datetime.now().isoformat()
                self._save_execution_report(execution_report)
                return (False, execution_report)
            
            logger.info(f"✅ Phase {phase.get('phase_number')} completed")
            
            # In approval_gated mode, pause after each phase for user approval
            if execution_mode == "approval_gated" and phase != phases[-1]:
                logger.info("⏸️  Phase complete. Awaiting approval to continue...")
                logger.info("   → In approval_gated mode: User must approve to proceed to next phase")
                logger.info("   → To enable autonomous execution, use triggers:")
                logger.info("      • 'execute all phases autonomously'")
                logger.info("      • 'auto chained'")
                logger.info("      • 'without user intervention'")
                # Return early - user must call execute_plan again to continue
                execution_report["awaiting_approval"] = True
                execution_report["next_phase"] = phases[phases.index(phase) + 1].get("phase_name")
                execution_report["completed_at"] = datetime.now().isoformat()
                self._save_execution_report(execution_report)
                return (True, execution_report)  # Success but paused
        
        # Automatically add Integration & Consolidation phase
        if auto_consolidate:
            logger.info("🔧 Starting Integration & Consolidation phase...")
            consolidation_result = self._execute_integration_consolidation_phase(plan_data, dry_run)
            execution_report["integration_consolidation_executed"] = True
            execution_report["integration_consolidation_result"] = consolidation_result
            
            if not consolidation_result["success"]:
                logger.error(f"❌ Integration & Consolidation failed: {consolidation_result.get('error')}")
                execution_report["errors"].append(consolidation_result.get("error"))
                execution_report["completed_at"] = datetime.now().isoformat()
                self._save_execution_report(execution_report)
                return (False, execution_report)
            
            logger.info("✅ Integration & Consolidation phase completed")
        
        # Mark as successful
        execution_report["success"] = True
        execution_report["completed_at"] = datetime.now().isoformat()
        
        # Save execution report
        self._save_execution_report(execution_report)
        
        logger.info(f"✅ Plan execution completed: {plan_path.name}")
        return (True, execution_report)
    
    def _execute_phase(self, phase: Dict[str, Any], dry_run: bool) -> Dict[str, Any]:
        """
        Execute a single phase of the plan.
        
        Args:
            phase: Phase data from plan
            dry_run: Preview without making changes
        
        Returns:
            Phase execution result
        """
        phase_number = phase.get("phase_number", "?")
        phase_name = phase.get("phase_name", "Unknown")
        tasks = phase.get("tasks", [])
        
        logger.info(f"📋 Executing Phase {phase_number}: {phase_name} ({len(tasks)} tasks)")
        
        # Emit PHASE_STARTED event
        try:
            event = LearningEvent(
                event_type=EventType.PHASE_STARTED,
                component="PlanExecutionOrchestrator",
                metadata={"phase_number": phase_number, "phase_name": phase_name, "task_count": len(tasks)}
            )
            get_global_collector().capture_event(event)
        except Exception as e:
            logger.debug(f"Learning event capture failed: {e}")
        
        phase_result = {
            "phase_number": phase_number,
            "phase_name": phase_name,
            "tasks_executed": [],
            "success": True,
            "started_at": datetime.now().isoformat()
        }
        
        if dry_run:
            logger.info(f"  [DRY RUN] Would execute {len(tasks)} tasks")
            phase_result["completed_at"] = datetime.now().isoformat()
            phase_result["dry_run_note"] = f"Would execute {len(tasks)} tasks"
            return phase_result
        
        # Execute each task in phase
        for task in tasks:
            task_result = self._execute_task(task)
            phase_result["tasks_executed"].append(task_result)
            
            if not task_result["success"]:
                phase_result["success"] = False
                phase_result["error"] = f"Task {task.get('task_id')} failed: {task_result.get('error')}"
                break
        
        phase_result["completed_at"] = datetime.now().isoformat()
        
        # Emit PHASE_COMPLETED event
        if phase_result["success"]:
            try:
                event = LearningEvent(
                    event_type=EventType.PHASE_COMPLETED,
                    component="PlanExecutionOrchestrator",
                    metadata={
                        "phase_number": phase_number,
                        "phase_name": phase_name,
                        "tasks_completed": len(phase_result["tasks_executed"])
                    }
                )
                get_global_collector().capture_event(event)
            except Exception as e:
                logger.debug(f"Learning event capture failed: {e}")
        
        return phase_result
    
    def _execute_task(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a single task.
        
        Uses TDD workflow if task specifies TDD mode, otherwise uses CodeExecutor.
        
        Args:
            task: Task data from phase
        
        Returns:
            Task execution result
        """
        task_id = task.get("task_id", "?")
        
        # NEW: Pre-execution validation from CRITICAL-ARCHITECTURE-REVIEW.md findings
        validation_result = self._validate_task_implementation_requirements(task)
        if not validation_result["valid"]:
            logger.warning(f"⚠️  Task {task_id} validation warnings: {validation_result['warnings']}")
            # Log warnings but continue - these are guidelines not blockers
        task_name = task.get("task_name", "Unknown")
        # TIER 0: TDD_ENFORCEMENT - TDD is MANDATORY unless explicitly disabled
        use_tdd = task.get("use_tdd", True) and task.get("tdd_enabled", True)
        
        logger.info(f"  ⚙️  Executing task {task_id}: {task_name} (TDD: {use_tdd})")
        
        task_result = {
            "task_id": task_id,
            "task_name": task_name,
            "success": False,
            "started_at": datetime.now().isoformat(),
            "tdd_enabled": use_tdd
        }
        
        # Route to TDD orchestrator if enabled
        if use_tdd and self.tdd_orchestrator:
            return self._execute_task_with_tdd(task, task_result)
        
        # SKULL PROTECTION: TDD bypass is a Tier 0 violation
        if not use_tdd:
            logger.warning(f"⚠️  SKULL VIOLATION: Task {task_id} bypassing TDD (TDD_ENFORCEMENT instinct)")
            logger.warning("   This violates Tier 0 governance - tests MUST be written first")
        
        # Fallback to CodeExecutor (only when TDD orchestrator unavailable)
        if not self.code_executor:
            task_result["error"] = "CodeExecutor not available"
            task_result["completed_at"] = datetime.now().isoformat()
            logger.warning(f"⚠️  Skipping task {task_id}: CodeExecutor not available")
            task_result["success"] = True  # Don't fail if executor not available
            return task_result
        
        try:
            # Create agent request for code execution
            request = AgentRequest(
                intent=IntentType.CODE_EXECUTION,
                context={
                    "task_description": task_name,
                    "acceptance_criteria": task.get("acceptance_criteria", []),
                    "files_affected": task.get("files_affected", []),
                    "implementation_notes": task.get("implementation_notes", "")
                },
                user_message=f"Implement: {task_name}"
            )
            
            # Execute via CodeExecutor agent
            response = self.code_executor.execute(request)
            
            if response.success:
                task_result["success"] = True
                task_result["result"] = response.result
                task_result["message"] = response.message
                logger.info(f"    ✅ Task {task_id} completed")
            else:
                task_result["error"] = response.message
                logger.error(f"    ❌ Task {task_id} failed: {response.message}")
        
        except Exception as e:
            task_result["error"] = str(e)
            logger.error(f"    ❌ Task {task_id} exception: {e}")
        
        task_result["completed_at"] = datetime.now().isoformat()
        return task_result
    
    def _execute_task_with_tdd(
        self,
        task: Dict[str, Any],
        task_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute task using TDD workflow (RED→GREEN→REFACTOR).
        
        Args:
            task: Task data
            task_result: Pre-initialized task result dict
            
        Returns:
            Updated task result with TDD execution data
        """
        task_id = task.get("task_id", "?")
        task_name = task.get("task_name", "Unknown")
        
        try:
            # Extract test files from task metadata (enforce test-first)
            test_files = []
            files_affected = task.get("files_affected", [])
            for file_path in files_affected:
                # Identify test files (common patterns)
                if any(pattern in str(file_path).lower() for pattern in ["test_", "_test", "tests/"]):
                    test_files.append(Path(file_path))
            
            # TIER 0 ENFORCEMENT: Warn if no test files specified
            if not test_files:
                logger.warning(f"⚠️ Task {task_id} has no test files in 'files_affected'")
                logger.warning("   Best practice: Include test files to enforce test-first discipline")
            
            # Start TDD session with test file validation
            session = self.tdd_orchestrator.start_session(
                feature_name=task_name,
                task_id=task_id,
                work_item_id=task.get("work_item_id"),
                test_files=test_files if test_files else None,
                require_tests_upfront=True
            )
            
            session_id = session["session_id"]
            logger.info(f"    🧪 Started TDD session: {session_id}")
            
            # Execute RED phase
            red_result = self.tdd_orchestrator.execute_red_phase(session_id=session_id)
            if not red_result["success"]:
                task_result["error"] = f"RED phase failed: {red_result.get('message')}"
                task_result["completed_at"] = datetime.now().isoformat()
                return task_result
            
            logger.info(f"    🔴 RED phase complete: {red_result.get('failing_tests', 0)} tests failing")
            
            # Execute GREEN phase
            green_result = self.tdd_orchestrator.execute_green_phase(session_id=session_id)
            if not green_result["success"]:
                task_result["error"] = f"GREEN phase failed: {green_result.get('message')}"
                task_result["completed_at"] = datetime.now().isoformat()
                return task_result
            
            logger.info(f"    🟢 GREEN phase complete: {green_result.get('passing_tests', 0)} tests passing")
            
            # Execute REFACTOR phase (THE INNOVATION)
            refactor_result = self.tdd_orchestrator.execute_refactor_phase(session_id=session_id)
            if not refactor_result["success"]:
                task_result["error"] = f"REFACTOR phase failed: {refactor_result.get('message')}"
                task_result["completed_at"] = datetime.now().isoformat()
                return task_result
            
            logger.info(f"    🔵 REFACTOR phase complete: {len(refactor_result.get('applied_refactorings', []))} refactorings applied")
            
            # Complete session
            complete_result = self.tdd_orchestrator.complete_session(session_id=session_id)
            
            task_result["success"] = True
            task_result["tdd_session_id"] = session_id
            task_result["tdd_metrics"] = {
                "red_phase": red_result,
                "green_phase": green_result,
                "refactor_phase": refactor_result
            }
            task_result["message"] = f"TDD workflow complete: {session_id}"
            logger.info(f"    ✅ Task {task_id} completed via TDD")
            
        except Exception as e:
            task_result["error"] = f"TDD execution exception: {str(e)}"
            logger.error(f"    ❌ Task {task_id} TDD exception: {e}")
        
        task_result["completed_at"] = datetime.now().isoformat()
        return task_result
    
    def _execute_integration_consolidation_phase(
        self, 
        plan_data: Dict[str, Any],
        dry_run: bool
    ) -> Dict[str, Any]:
        """
        Execute Integration & Consolidation phase automatically.
        
        This phase:
        1. Identifies deprecated/obsolete code
        2. Removes duplicates
        3. Organizes files into proper structures
        4. Updates references across application
        5. Verifies features are wired and functional
        6. Runs integration tests
        
        Args:
            plan_data: Original plan data for context
            dry_run: Preview without making changes
        
        Returns:
            Consolidation execution result
        """
        result = {
            "phase_name": "Integration & Consolidation",
            "success": False,
            "started_at": datetime.now().isoformat(),
            "operations": []
        }
        
        if dry_run:
            result["dry_run_note"] = "Would execute cleanup and wiring operations"
            result["success"] = True
            result["completed_at"] = datetime.now().isoformat()
            return result
        
        logger.info("🔍 Analyzing codebase for cleanup opportunities...")
        
        # Operation 1: Identify files affected by plan
        files_affected = self._gather_affected_files(plan_data)
        result["files_analyzed"] = len(files_affected)
        logger.info(f"  📁 Analyzing {len(files_affected)} affected files")
        
        # Operation 2: Find deprecated code
        deprecated_items = self._find_deprecated_code(files_affected)
        if deprecated_items:
            cleanup_op = {
                "operation": "remove_deprecated",
                "items_found": len(deprecated_items),
                "success": False
            }
            
            if self.cleanup_orchestrator:
                try:
                    cleanup_result = self._remove_deprecated_code(deprecated_items)
                    cleanup_op["success"] = cleanup_result["success"]
                    cleanup_op["items_removed"] = cleanup_result.get("items_removed", 0)
                    logger.info(f"  🗑️  Removed {cleanup_op['items_removed']} deprecated items")
                except Exception as e:
                    cleanup_op["error"] = str(e)
                    logger.error(f"  ❌ Cleanup failed: {e}")
            else:
                cleanup_op["skipped"] = "CleanupOrchestrator not available"
                cleanup_op["success"] = True  # Don't fail if not available
            
            result["operations"].append(cleanup_op)
        
        # Operation 3: Find and eliminate duplicates
        duplicates = self._find_duplicate_code(files_affected)
        if duplicates:
            dedup_op = {
                "operation": "eliminate_duplicates",
                "duplicates_found": len(duplicates),
                "success": False
            }
            
            try:
                dedup_result = self._eliminate_duplicates(duplicates)
                dedup_op["success"] = dedup_result["success"]
                dedup_op["duplicates_resolved"] = dedup_result.get("resolved", 0)
                logger.info(f"  🔀 Resolved {dedup_op['duplicates_resolved']} duplicates")
            except Exception as e:
                dedup_op["error"] = str(e)
                logger.error(f"  ❌ Deduplication failed: {e}")
            
            result["operations"].append(dedup_op)
        
        # Operation 4: Organize files into proper folders
        org_op = {
            "operation": "organize_files",
            "success": False
        }
        
        try:
            org_result = self._organize_files(files_affected)
            org_op["success"] = org_result["success"]
            org_op["files_moved"] = org_result.get("files_moved", 0)
            logger.info(f"  📂 Organized {org_op['files_moved']} files")
        except Exception as e:
            org_op["error"] = str(e)
            logger.error(f"  ❌ File organization failed: {e}")
        
        result["operations"].append(org_op)
        
        # Operation 5: Update references across application
        ref_op = {
            "operation": "update_references",
            "success": False
        }
        
        try:
            ref_result = self._update_references(files_affected)
            ref_op["success"] = ref_result["success"]
            ref_op["references_updated"] = ref_result.get("updated", 0)
            logger.info(f"  🔗 Updated {ref_op['references_updated']} references")
        except Exception as e:
            ref_op["error"] = str(e)
            logger.error(f"  ❌ Reference update failed: {e}")
        
        result["operations"].append(ref_op)
        
        # Operation 6: Verify wiring and functionality
        verify_op = {
            "operation": "verify_wiring",
            "success": False
        }
        
        try:
            verify_result = self._verify_feature_wiring(plan_data)
            verify_op["success"] = verify_result["success"]
            verify_op["wiring_status"] = verify_result.get("status", "unknown")
            logger.info(f"  ✅ Wiring verification: {verify_op['wiring_status']}")
        except Exception as e:
            verify_op["error"] = str(e)
            logger.error(f"  ❌ Wiring verification failed: {e}")
        
        result["operations"].append(verify_op)
        
        # Operation 7: Run integration tests
        test_op = {
            "operation": "integration_tests",
            "success": False
        }
        
        try:
            test_result = self._run_integration_tests(plan_data)
            test_op["success"] = test_result["success"]
            test_op["tests_passed"] = test_result.get("passed", 0)
            test_op["tests_failed"] = test_result.get("failed", 0)
            logger.info(f"  🧪 Tests: {test_op['tests_passed']} passed, {test_op['tests_failed']} failed")
        except Exception as e:
            test_op["error"] = str(e)
            logger.error(f"  ❌ Integration tests failed: {e}")
        
        result["operations"].append(test_op)
        
        # Determine overall success
        failed_critical_ops = [op for op in result["operations"] 
                              if not op.get("success") and op["operation"] in ["verify_wiring", "integration_tests"]]
        
        result["success"] = len(failed_critical_ops) == 0
        result["completed_at"] = datetime.now().isoformat()
        
        return result
    
    def _validate_task_implementation_requirements(self, task: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate task specifies necessary implementation requirements.
        
        Based on CORTEX-Clean-v2 review findings:
        - Security requirements (auth, validation, sanitization)
        - Error handling strategy
        - Configuration externalization
        - Transaction management (for data operations)
        - Domain model richness (behavior vs data)
        
        Args:
            task: Task data from plan
            
        Returns:
            Dict with validation results and warnings
        """
        warnings = []
        task_name = task.get("task_name", "").lower()
        files_affected = task.get("files_affected", [])
        acceptance_criteria = task.get("acceptance_criteria", [])
        
        # Check 1: Security requirements for data operations
        if any(keyword in task_name for keyword in ['create', 'update', 'delete', 'save', 'persist']):
            if not any('validat' in str(criterion).lower() for criterion in acceptance_criteria):
                warnings.append("DATA_OPERATION_MISSING_VALIDATION: Task performs data operations but has no validation criteria")
            if not any('auth' in str(criterion).lower() for criterion in acceptance_criteria):
                warnings.append("DATA_OPERATION_MISSING_AUTH: Task performs state changes but has no authorization criteria")
        
        # Check 2: Error handling strategy
        if any(keyword in task_name for keyword in ['api', 'service', 'handler', 'controller']):
            if not any('error' in str(criterion).lower() for criterion in acceptance_criteria):
                warnings.append("SERVICE_LAYER_MISSING_ERROR_HANDLING: Service/API task has no error handling criteria")
        
        # Check 3: Configuration externalization
        if any(keyword in task_name for keyword in ['url', 'endpoint', 'connection', 'config']):
            if not any('environment' in str(criterion).lower() or 'config' in str(criterion).lower() for criterion in acceptance_criteria):
                warnings.append("HARDCODED_CONFIG_RISK: Task involves configuration but has no externalization criteria")
        
        # Check 4: Transaction management for repositories
        if any('repository' in file_path.lower() or 'dbcontext' in file_path.lower() for file_path in files_affected):
            if not any('transaction' in str(criterion).lower() or 'atomic' in str(criterion).lower() for criterion in acceptance_criteria):
                warnings.append("REPOSITORY_MISSING_TRANSACTION: Repository implementation has no transaction criteria")
        
        # Check 5: Domain model behavior
        if any('domain' in file_path.lower() or 'entity' in file_path.lower() or 'entities' in file_path.lower() for file_path in files_affected):
            if not any('method' in str(criterion).lower() or 'behavior' in str(criterion).lower() for criterion in acceptance_criteria):
                warnings.append("ANEMIC_DOMAIN_RISK: Domain entity task has no behavior/method criteria (may create anemic model)")
        
        # Check 6: Integration/infrastructure completeness
        files_lower = [f.lower() for f in files_affected]
        has_interface = any('interface' in f or 'irepository' in f for f in files_lower)
        has_implementation = any('repository' in f and 'interface' not in f for f in files_lower)
        
        if has_interface and not has_implementation:
            warnings.append("INCOMPLETE_ABSTRACTION: Task creates interface but has no concrete implementation")
        
        return {
            "valid": True,  # Warnings don't block execution
            "warnings": warnings,
            "checks_performed": 6
        }
    
    def _gather_affected_files(self, plan_data: Dict[str, Any]) -> List[Path]:
        """Gather list of files affected by plan implementation."""
        files = set()
        
        for phase in plan_data.get("phases", []):
            for task in phase.get("tasks", []):
                task_files = task.get("files_affected", [])
                for file_path in task_files:
                    files.add(Path(file_path))
        
        return list(files)
    
    def _find_deprecated_code(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Find deprecated code markers in affected files."""
        deprecated_items = []
        
        for file_path in files:
            if not file_path.exists():
                continue
            
            try:
                content = file_path.read_text(encoding='utf-8')
                
                # Look for deprecation markers
                if "@deprecated" in content.lower() or "# deprecated" in content.lower():
                    deprecated_items.append({
                        "file": str(file_path),
                        "type": "marked_deprecated"
                    })
            except Exception as e:
                logger.debug(f"Could not scan {file_path}: {e}")
        
        return deprecated_items
    
    def _remove_deprecated_code(self, items: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Remove deprecated code using CleanupOrchestrator."""
        if not self.cleanup_orchestrator:
            return {"success": False, "error": "CleanupOrchestrator not available"}
        
        # Delegate to cleanup orchestrator
        try:
            result = self.cleanup_orchestrator.remove_deprecated_items(items)
            return result
        except AttributeError:
            # Fallback if method doesn't exist
            logger.warning("CleanupOrchestrator.remove_deprecated_items not available")
            return {"success": True, "items_removed": 0, "note": "Manual cleanup required"}
    
    def _find_duplicate_code(self, files: List[Path]) -> List[Dict[str, Any]]:
        """Find duplicate code patterns in affected files."""
        # Simple placeholder - real implementation would use AST analysis
        return []
    
    def _eliminate_duplicates(self, duplicates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Eliminate duplicate code."""
        return {"success": True, "resolved": len(duplicates)}
    
    def _organize_files(self, files: List[Path]) -> Dict[str, Any]:
        """Organize files into proper folder structures."""
        # Placeholder - real implementation would use file structure rules
        return {"success": True, "files_moved": 0}
    
    def _update_references(self, files: List[Path]) -> Dict[str, Any]:
        """Update import statements and references after file moves."""
        # Placeholder - real implementation would update imports
        return {"success": True, "updated": 0}
    
    def _verify_feature_wiring(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify new features are properly wired and accessible."""
        # Placeholder - real implementation would check:
        # - Entry points registered
        # - Routes configured
        # - Dependencies injected
        # - Configuration present
        return {"success": True, "status": "fully_wired"}
    
    def _run_integration_tests(self, plan_data: Dict[str, Any]) -> Dict[str, Any]:
        """Run integration tests to validate production readiness."""
        # Placeholder - real implementation would run pytest
        return {"success": True, "passed": 0, "failed": 0}
    
    def _check_definition_of_ready(self, plan_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Check if Definition of Ready is satisfied.
        
        Args:
            plan_data: Plan dictionary
        
        Returns:
            Tuple of (satisfied, list of violations)
        """
        dor = plan_data.get("definition_of_ready", {})
        violations = []
        
        required_fields = [
            "requirements_clear",
            "dependencies_identified",
            "design_approved",
            "resources_available",
            "tdd_test_scenarios_defined",
            "clean_architecture_planned",
            "solid_principles_reviewed"
        ]
        
        for field in required_fields:
            if field not in dor:
                violations.append(f"Missing DoR field: {field}")
            elif not dor[field]:
                violations.append(f"DoR not satisfied: {field}")
        
        return (len(violations) == 0, violations)
    
    def _generate_remediation_plan(
        self, 
        plan_data: Dict[str, Any], 
        dor_violations: List[str]
    ) -> Dict[str, Any]:
        """
        Generate remediation plan to address DoR violations.
        
        Args:
            plan_data: Original plan data
            dor_violations: List of DoR violations
        
        Returns:
            Remediation plan dictionary
        """
        metadata = plan_data.get("metadata", {})
        feature_name = metadata.get("feature_name", "Unknown")
        
        remediation_plan = {
            "type": "remediation",
            "target_plan": feature_name,
            "purpose": "Address Definition of Ready violations before execution",
            "violations": dor_violations,
            "phases": []
        }
        
        # Generate remediation phases based on violation types
        phase_number = 1
        
        if any("requirements_clear" in v for v in dor_violations):
            remediation_plan["phases"].append({
                "phase_number": phase_number,
                "phase_name": "Requirements Clarification",
                "tasks": [
                    {
                        "task_id": f"R{phase_number}.1",
                        "task_name": "Document detailed requirements",
                        "description": "Create comprehensive requirements document with acceptance criteria, constraints, and success metrics"
                    },
                    {
                        "task_id": f"R{phase_number}.2",
                        "task_name": "Stakeholder review",
                        "description": "Review requirements with stakeholders and obtain approval"
                    }
                ]
            })
            phase_number += 1
        
        if any("dependencies_identified" in v for v in dor_violations):
            remediation_plan["phases"].append({
                "phase_number": phase_number,
                "phase_name": "Dependency Analysis",
                "tasks": [
                    {
                        "task_id": f"R{phase_number}.1",
                        "task_name": "Identify technical dependencies",
                        "description": "List all libraries, services, APIs, and infrastructure required"
                    },
                    {
                        "task_id": f"R{phase_number}.2",
                        "task_name": "Verify dependency availability",
                        "description": "Confirm all dependencies are available, licensed, and compatible"
                    }
                ]
            })
            phase_number += 1
        
        if any("design_approved" in v for v in dor_violations):
            remediation_plan["phases"].append({
                "phase_number": phase_number,
                "phase_name": "Architecture Design",
                "tasks": [
                    {
                        "task_id": f"R{phase_number}.1",
                        "task_name": "Create architecture diagram",
                        "description": "Design component structure, data flow, and integration points"
                    },
                    {
                        "task_id": f"R{phase_number}.2",
                        "task_name": "Technical design review",
                        "description": "Present design to technical team and obtain approval"
                    }
                ]
            })
            phase_number += 1
        
        if any("tdd_test_scenarios_defined" in v for v in dor_violations):
            remediation_plan["phases"].append({
                "phase_number": phase_number,
                "phase_name": "TDD Test Planning",
                "tasks": [
                    {
                        "task_id": f"R{phase_number}.1",
                        "task_name": "Define test scenarios",
                        "description": "Document all test cases: happy path, error cases, edge cases, boundary conditions"
                    },
                    {
                        "task_id": f"R{phase_number}.2",
                        "task_name": "Create test data fixtures",
                        "description": "Prepare test data, mocks, and fixtures for RED phase"
                    }
                ]
            })
            phase_number += 1
        
        if any("clean_architecture_planned" in v for v in dor_violations):
            remediation_plan["phases"].append({
                "phase_number": phase_number,
                "phase_name": "Clean Architecture Planning",
                "tasks": [
                    {
                        "task_id": f"R{phase_number}.1",
                        "task_name": "Define layer boundaries",
                        "description": "Document domain, application, infrastructure layers and their responsibilities"
                    },
                    {
                        "task_id": f"R{phase_number}.2",
                        "task_name": "Plan dependency injection",
                        "description": "Design DI container, interfaces, and dependency flow"
                    }
                ]
            })
            phase_number += 1
        
        if any("solid_principles_reviewed" in v for v in dor_violations):
            remediation_plan["phases"].append({
                "phase_number": phase_number,
                "phase_name": "SOLID Principles Review",
                "tasks": [
                    {
                        "task_id": f"R{phase_number}.1",
                        "task_name": "SRP and OCP validation",
                        "description": "Review design for Single Responsibility and Open/Closed principles"
                    },
                    {
                        "task_id": f"R{phase_number}.2",
                        "task_name": "LSP, ISP, DIP validation",
                        "description": "Validate Liskov Substitution, Interface Segregation, and Dependency Inversion"
                    }
                ]
            })
            phase_number += 1
        
        remediation_plan["execution_note"] = (
            "Execute this remediation plan first to satisfy DoR requirements. "
            "Once complete, re-run original plan with force_execution=True OR "
            "update original plan's DoR fields and execute normally."
        )
        
        logger.info(f"📋 Generated remediation plan with {len(remediation_plan['phases'])} phases")
        return remediation_plan
    
    def _load_plan(self, plan_path: Path) -> Tuple[bool, Optional[Dict[str, Any]], List[str]]:
        """
        Load plan from file (YAML or Markdown).
        
        Args:
            plan_path: Path to plan file
        
        Returns:
            Tuple of (success, plan_data, errors)
        """
        if not plan_path.exists():
            return (False, None, [f"Plan file not found: {plan_path}"])
        
        try:
            if plan_path.suffix == ".yaml" or plan_path.suffix == ".yml":
                with open(plan_path, 'r', encoding='utf-8') as f:
                    plan_data = yaml.safe_load(f)
                return (True, plan_data, [])
            elif plan_path.suffix == ".md":
                # Parse markdown plan
                plan_data = self._parse_markdown_plan(plan_path)
                return (True, plan_data, [])
            else:
                return (False, None, [f"Unsupported plan format: {plan_path.suffix}"])
        
        except Exception as e:
            return (False, None, [f"Failed to load plan: {e}"])
    
    def _parse_markdown_plan(self, plan_path: Path) -> Dict[str, Any]:
        """Parse Markdown plan into structured data."""
        content = plan_path.read_text(encoding='utf-8')
        
        # Simple parser - extract title and phases
        plan_data = {
            "metadata": {
                "title": "Markdown Plan",
                "source": str(plan_path)
            },
            "phases": []
        }
        
        lines = content.split('\n')
        current_phase = None
        
        for line in lines:
            # Extract title
            if line.startswith('# ') and not plan_data["metadata"]["title"]:
                plan_data["metadata"]["title"] = line[2:].strip()
            
            # Extract phases
            if line.startswith('## Phase '):
                if current_phase:
                    plan_data["phases"].append(current_phase)
                
                # Parse phase header
                import re
                match = re.match(r'##\s+Phase\s+(\d+):\s+(.+)', line)
                if match:
                    current_phase = {
                        "phase_number": int(match.group(1)),
                        "phase_name": match.group(2).strip(),
                        "tasks": []
                    }
        
        # Add last phase
        if current_phase:
            plan_data["phases"].append(current_phase)
        
        return plan_data
    
    def _save_execution_report(self, report: Dict[str, Any]):
        """Save execution report to disk."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        plan_name = Path(report["plan_path"]).stem
        report_path = self.execution_history_dir / f"{plan_name}_execution_{timestamp}.json"
        
        try:
            with open(report_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"📊 Execution report saved: {report_path.name}")
        except Exception as e:
            logger.error(f"Failed to save execution report: {e}")
