"""
Planning Orchestrator v5.1 - Production TaskListOrchestrator Integration.

Extends Planning v5 with TaskListOrchestrator for robust state management,
sub-millisecond recovery, and task-level progress tracking.

This is the PRODUCTION version (not pilot). Fully integrated with Planning v5
config, templates, governance, and knowledge graph.

Key Features:
- Task-based execution replacing phase loop
- Strategic checkpointing (2 of 6 tasks)
- Sub-millisecond recovery from any interruption
- Backward compatible with Planning v5
- Real-time progress tracking

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from typing import Dict, Any, Optional
from pathlib import Path

from src.orchestrators.task_list_orchestrator import TaskListOrchestrator
from src.orchestrators.planning.planning_orchestrator_v5 import PlanningOrchestratorV5
from src.database.planning_state_db import PlanningStateDB


class PlanningOrchestratorV5_1(PlanningOrchestratorV5):
    """
    Planning Orchestrator v5.1 - Production TaskListOrchestrator Integration.
    
    Replaces Planning v5's phase loop with TaskListOrchestrator for:
    - Sub-millisecond recovery from interruptions
    - Strategic checkpointing at slow operations
    - Task-level progress visibility
    - Automatic state management
    
    Backward Compatible: All Planning v5 config, templates, and governance
    rules continue to work. Existing plans can be resumed.
    
    Usage:
        # Standard execution (same as v5)
        orch = PlanningOrchestratorV5_1()
        result = orch.execute("plan user authentication")
        
        # Recovery from interruption (NEW in v5.1)
        orch = PlanningOrchestratorV5_1(resume=True, plan_id="plan-abc123")
        result = orch.execute("plan user authentication")
    """
    
    VERSION = "5.1.0"
    
    def __init__(
        self,
        config_path: Optional[str] = None,
        state_db: Optional[PlanningStateDB] = None,
        plan_id: Optional[str] = None,
        template_dir: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        plan_type: str = "feature",
        resume: bool = False
    ):
        """
        Initialize Planning Orchestrator v5.1.
        
        Args:
            config_path: Path to configuration YAML (default: planning-v5-default.yaml)
            state_db: Planning state database instance
            plan_id: Existing plan ID to resume
            template_dir: Custom template directory
            context: Additional context from Master Orchestrator
            plan_type: Type of plan - 'feature' | 'epic' | 'phase' | 'sub-plan'
            resume: If True, attempt to recover from last checkpoint
        """
        # Initialize parent (Planning v5)
        super().__init__(
            config_path=config_path,
            state_db=state_db,
            plan_id=plan_id,
            template_dir=template_dir,
            context=context,
            plan_type=plan_type
        )
        
        self.resume = resume
        self.task_orchestrator: Optional[TaskListOrchestrator] = None
        
        # Override logger for v5.1
        self.logger = logging.getLogger("cortex.orchestrators.planning_v5_1")
        self.logger.info(f"Planning Orchestrator v{self.VERSION} initialized (TaskListOrchestrator)")
    
    def execute(self, user_request: str, **kwargs) -> Dict[str, Any]:
        """
        Execute planning using TaskListOrchestrator (replaces phase loop).
        
        This method overrides Planning v5's execute() to use task-based execution
        instead of phase-based loops.
        
        Args:
            user_request: User's planning request
            **kwargs: Additional execution parameters
        
        Returns:
            Execution result dict with task progress and outputs
        """
        self.logger.info(f"🚀 Planning v{self.VERSION} - Task-based execution starting")
        
        # Initialize task orchestrator
        try:
            self._initialize_task_orchestrator(user_request)
        except Exception as e:
            self.logger.error(f"❌ Task orchestrator initialization failed: {e}")
            return self._build_error_result(f"Initialization failed: {e}")
        
        # Check if resuming from checkpoint
        if self.resume:
            try:
                self.task_orchestrator.recover()
                self.logger.info("✅ Recovered from checkpoint - resuming planning")
            except ValueError:
                self.logger.warning("⚠️ No checkpoint found - starting from beginning")
                self.resume = False
        
        # Define planning tasks (if not resuming with existing tasks)
        if not self.resume or not self.task_orchestrator.tasks:
            try:
                self._define_planning_tasks(user_request, **kwargs)
            except Exception as e:
                self.logger.error(f"❌ Task definition failed: {e}")
                return self._build_error_result(f"Task definition failed: {e}")
        else:
            # Re-register executors after recovery
            self._register_task_executors()
        
        # Execute all tasks
        try:
            while self.task_orchestrator.has_pending_tasks():
                result = self.task_orchestrator.execute_next()
                
                # Log progress
                progress = self.task_orchestrator.get_progress()
                self.logger.info(
                    f"📊 Progress: {progress['completed']}/{progress['total_tasks']} "
                    f"({progress['progress_percent']:.1f}%)"
                )
            
            # Build success result
            return self._build_task_result(success=True)
        
        except Exception as e:
            self.logger.error(f"❌ Planning execution failed: {e}")
            return self._build_task_result(success=False, error=str(e))
    
    def _initialize_task_orchestrator(self, user_request: str) -> None:
        """
        Initialize TaskListOrchestrator with database-backed persistence.
        
        Creates plan entry in database if needed for snapshot foreign key.
        """
        # Create unique orchestrator ID
        orchestrator_id = f"planning-v5.1-{self.plan_id or 'new'}"
        
        # Ensure plan exists in database for snapshot foreign key
        # (TaskListOrchestrator uses orchestrator_id as plan_id for snapshots)
        try:
            existing_plan = self.state_db.get_plan(orchestrator_id)
            if not existing_plan:
                # Create plan entry for orchestrator
                self.state_db.create_plan(
                    feature_name=f"Planning v5.1 Execution - {user_request[:50]}"
                )
                # Override plan_id to use orchestrator_id
                cursor = self.state_db._conn.execute(
                    "UPDATE plans SET plan_id = ? WHERE plan_id = (SELECT plan_id FROM plans ORDER BY created_at DESC LIMIT 1)",
                    (orchestrator_id,)
                )
                self.state_db._conn.commit()
                self.logger.debug(f"Created plan entry for orchestrator: {orchestrator_id}")
        except Exception as e:
            self.logger.warning(f"Could not ensure orchestrator plan exists: {e}")
        
        # Create task orchestrator
        self.task_orchestrator = TaskListOrchestrator(
            orchestrator_id=orchestrator_id,
            state_db=self.state_db
        )
        
        self.logger.debug(f"TaskListOrchestrator initialized: {orchestrator_id}")
    
    def _define_planning_tasks(self, user_request: str, **kwargs) -> None:
        """
        Define planning tasks for TaskListOrchestrator.
        
        Maps Planning v5 phases to individual tasks with dependencies and
        strategic checkpointing.
        
        Planning v5 Phases → v5.1 Tasks:
        - Phase 0: Parse request → Task 1: parse_request
        - Phase 1: Context discovery → Task 2: discover_context (CHECKPOINT)
        - Phase 2: Architecture analysis → Task 3: analyze_architecture
        - Phase 3: Plan generation → Task 4: generate_plan (CHECKPOINT)
        - Phase 4a: Folder creation → Task 5: create_folders
        - Phase 4b: Validation → Task 6: validate_plan
        """
        # Store request in orchestrator for task access
        self.user_request = user_request
        self.execution_kwargs = kwargs
        
        # Task 1: Parse request and create plan
        self.task_orchestrator.add_task(
            task_id="parse_request",
            description="Parse user request and create plan in database",
            executor=self._task_parse_request,
            parameters={"user_request": user_request},
            checkpoint_before=False  # Fast operation (<1s)
        )
        
        # Task 2: Context discovery (with checkpoint - slow search)
        self.task_orchestrator.add_task(
            task_id="discover_context",
            description="Search workspace for relevant context (semantic + grep)",
            executor=self._task_discover_context,
            parameters={},
            checkpoint_before=True,  # ✅ Strategic checkpoint (10+ seconds)
            depends_on=["parse_request"]
        )
        
        # Task 3: Architecture analysis
        self.task_orchestrator.add_task(
            task_id="analyze_architecture",
            description="AST scanning and architecture analysis",
            executor=self._task_analyze_architecture,
            parameters={},
            checkpoint_before=False,  # Medium speed (3-5s)
            depends_on=["discover_context"]
        )
        
        # Task 4: Plan generation (with checkpoint - complex rendering)
        self.task_orchestrator.add_task(
            task_id="generate_plan",
            description="Generate plan from Jinja2 templates",
            executor=self._task_generate_plan,
            parameters={},
            checkpoint_before=True,  # ✅ Strategic checkpoint (5+ seconds)
            depends_on=["analyze_architecture"]
        )
        
        # Task 5: Folder creation
        self.task_orchestrator.add_task(
            task_id="create_folders",
            description="Create 5-folder plan structure",
            executor=self._task_create_folders,
            parameters={},
            checkpoint_before=False,  # Fast (<1s)
            depends_on=["generate_plan"]
        )
        
        # Task 6: Validation
        self.task_orchestrator.add_task(
            task_id="validate_plan",
            description="Run validation checks",
            executor=self._task_validate,
            parameters={},
            checkpoint_before=False,  # Fast (<1s)
            depends_on=["create_folders"]
        )
        
        self.logger.info("✅ Defined 6 planning tasks with 2 strategic checkpoints")
    
    def _register_task_executors(self) -> None:
        """
        Re-register task executors after recovery.
        
        Task executors (functions) are not serialized during checkpoint,
        so they must be re-bound after recovery.
        """
        self.task_orchestrator.register_executor("parse_request", self._task_parse_request)
        self.task_orchestrator.register_executor("discover_context", self._task_discover_context)
        self.task_orchestrator.register_executor("analyze_architecture", self._task_analyze_architecture)
        self.task_orchestrator.register_executor("generate_plan", self._task_generate_plan)
        self.task_orchestrator.register_executor("create_folders", self._task_create_folders)
        self.task_orchestrator.register_executor("validate_plan", self._task_validate)
        
        self.logger.info("✅ Re-registered 6 task executors after recovery")
    
    # =========================================================================
    # Task Executors (Wrapping Planning v5 phase methods)
    # =========================================================================
    
    def _task_parse_request(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Parse user request and create plan in database.
        
        Wraps Planning v5 Phase 0.
        """
        user_request = params["user_request"]
        
        # Call parent's parse logic
        try:
            # Parse user request (extract feature name, complexity, etc.)
            parsed = self._parse_user_request(user_request)
            
            # Create plan in database if not exists
            if not self.plan_id:
                self.plan_id = self.state_db.create_plan(
                    feature_name=parsed.get("feature_name", user_request[:50]),
                    complexity_tier=parsed.get("complexity_tier", 3)
                )
            
            self.logger.info(f"✅ Task: parse_request - Plan ID: {self.plan_id}")
            
            return {
                "plan_id": self.plan_id,
                "feature_name": parsed.get("feature_name"),
                "complexity_tier": parsed.get("complexity_tier"),
                "status": "completed"
            }
        except Exception as e:
            self.logger.error(f"❌ parse_request failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _task_discover_context(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Discover context from workspace.
        
        Wraps Planning v5 Phase 1 (Context Discovery).
        """
        try:
            # Call parent's context discovery
            context_results = self._discover_context(self.user_request)
            
            self.logger.info(f"✅ Task: discover_context - Found {len(context_results.get('files', []))} relevant files")
            
            return {
                "discovered_files": len(context_results.get("files", [])),
                "semantic_results": context_results.get("semantic_matches", []),
                "grep_results": context_results.get("grep_matches", []),
                "status": "completed"
            }
        except Exception as e:
            self.logger.error(f"❌ discover_context failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _task_analyze_architecture(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Analyze architecture via AST scanning.
        
        Wraps Planning v5 Phase 2 (Architecture Analysis).
        """
        try:
            # Call parent's architecture analysis
            analysis_results = self._analyze_architecture()
            
            self.logger.info(f"✅ Task: analyze_architecture - Scanned {analysis_results.get('files_scanned', 0)} files")
            
            return {
                "files_scanned": analysis_results.get("files_scanned", 0),
                "functions_found": analysis_results.get("functions", 0),
                "classes_found": analysis_results.get("classes", 0),
                "status": "completed"
            }
        except Exception as e:
            self.logger.error(f"❌ analyze_architecture failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _task_generate_plan(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Generate plan from templates.
        
        Wraps Planning v5 Phase 3 (Plan Generation).
        """
        try:
            # Call parent's plan generation
            plan_results = self._generate_plan_from_templates()
            
            self.logger.info(f"✅ Task: generate_plan - Generated {plan_results.get('phases', 0)} phases, {plan_results.get('tasks', 0)} tasks")
            
            return {
                "phases": plan_results.get("phases", 0),
                "tasks": plan_results.get("tasks", 0),
                "plan_path": plan_results.get("plan_path"),
                "status": "completed"
            }
        except Exception as e:
            self.logger.error(f"❌ generate_plan failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _task_create_folders(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Create plan folder structure.
        
        Wraps Planning v5 Phase 4 (Folder Creation).
        """
        try:
            # Call parent's folder creation
            folder_results = self._create_plan_folders()
            
            self.logger.info(f"✅ Task: create_folders - Created {len(folder_results.get('folders', []))} subfolders")
            
            return {
                "folders_created": len(folder_results.get("folders", [])),
                "base_path": folder_results.get("base_path"),
                "status": "completed"
            }
        except Exception as e:
            self.logger.error(f"❌ create_folders failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    def _task_validate(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Task: Run validation checks.
        
        Wraps Planning v5 Phase 4 (Validation).
        """
        try:
            # Call parent's validation
            validation_results = self._validate_plan()
            
            passed = validation_results.get("passed", 0)
            failed = validation_results.get("failed", 0)
            
            self.logger.info(f"✅ Task: validate_plan - {passed} passed, {failed} failed")
            
            return {
                "validation_checks": passed + failed,
                "passed": passed,
                "failed": failed,
                "status": "completed" if failed == 0 else "completed_with_warnings"
            }
        except Exception as e:
            self.logger.error(f"❌ validate_plan failed: {e}")
            return {
                "status": "failed",
                "error": str(e)
            }
    
    # =========================================================================
    # Helper Methods
    # =========================================================================
    
    def _build_task_result(
        self,
        success: bool,
        error: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build execution result from task orchestrator state."""
        if not self.task_orchestrator:
            return {"success": False, "error": "Task orchestrator not initialized"}
        
        progress = self.task_orchestrator.get_progress()
        completed_tasks = self.task_orchestrator.get_completed_tasks()
        failed_tasks = self.task_orchestrator.get_failed_tasks()
        
        return {
            "success": success,
            "error": error,
            "plan_id": self.plan_id,
            "version": self.VERSION,
            "progress": progress,
            "completed_tasks": len(completed_tasks),
            "failed_tasks": len(failed_tasks),
            "task_results": {
                task.task_id: task.result
                for task in completed_tasks
            }
        }
    
    def _build_error_result(self, error_message: str) -> Dict[str, Any]:
        """Build error result dict."""
        return {
            "success": False,
            "error": error_message,
            "plan_id": self.plan_id,
            "version": self.VERSION
        }
    
    def recover_and_continue(self) -> Dict[str, Any]:
        """
        Recover from last checkpoint and continue execution.
        
        Convenience method for recovery workflow.
        
        Returns:
            Execution result dict
        """
        if not self.user_request:
            raise ValueError("Cannot recover without user_request - must be set")
        
        self.resume = True
        return self.execute(self.user_request)
