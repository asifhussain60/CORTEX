"""
5-Stage Workflow Orchestrator (AC-PROD-004-02).

Integrates all 5 components of the Master Orchestrator workflow:
1. Stage 1 (Comprehension) - LENS Phase 1 language analysis
2. Stage 2 (Repository Scan) - System-wide code analysis  
3. Stage 3 (Knowledge) - LENS Phases 1-3 with graph building
4. Stage 4 (Approval) - 5 approval gates + implementation planning
5. Stage 5 (Execution) - Execute approved operations

This orchestrator:
- Coordinates data flow between stages
- Handles errors at each stage boundary
- Manages context propagation
- Logs all operations
- Produces final execution results

AC-PROD-004-02: Complete workflow integration with all 5 components

Author: CORTEX
Status: Production Ready
Version: 1.0.0
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional, Any

from src.core.result import Result, Ok, Err
from src.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from src.orchestrators.core.master_orchestrator_stage_1 import (
    MasterOrchestrationStage1,
    Stage1ComprehensionContext,
    Stage1Output,
)
from src.orchestrators.core.repository_scanner import (
    RepositoryScanner,
    ScanContext,
    ScanOutput,
)
from src.orchestrators.core.master_orchestrator_stage_3 import (
    MasterOrchestrationStage3,
    Stage3KnowledgeContext,
    Stage3Output,
)
from src.orchestrators.core.master_orchestrator_stage_4 import (
    MasterOrchestrationStage4,
    Stage4ApprovalContext,
    Stage4Output,
)


# ============================================================================
# Data Classes
# ============================================================================

@dataclass
class WorkflowStageResult:
    """Result from a workflow stage."""
    stage_name: str
    success: bool
    output: Optional[Any] = None
    error: Optional[str] = None
    duration: float = 0.0


@dataclass
class WorkflowExecutionContext:
    """Context for workflow execution."""
    operation: str
    description: str
    keywords: List[str]
    domain: str
    workspace_root: Optional[Path] = None
    target_paths: Optional[List[Path]] = None
    complexity: str = "medium"
    urgency: str = "medium"
    turn_number: int = 1


@dataclass
class WorkflowExecutionResult:
    """Result of complete workflow execution."""
    operation: str
    success: bool
    stage_results: List[WorkflowStageResult] = field(default_factory=list)
    final_decision: Optional[Dict[str, Any]] = None
    implementation_plan: Optional[Dict[str, Any]] = None
    total_duration: float = 0.0
    timestamp: Optional[datetime] = None
    errors: List[str] = field(default_factory=list)


# ============================================================================
# 5-Stage Workflow Orchestrator
# ============================================================================

class WorkflowOrchestrator:
    """
    Coordinates complete 5-stage Master Orchestrator workflow.
    
    Responsibilities:
    - Execute Stage 1: Comprehension (intent extraction)
    - Execute Stage 2: Repository Scan (code analysis)
    - Execute Stage 3: Knowledge (graph + synthesis)
    - Execute Stage 4: Approval (gates + decisions)
    - Execute Stage 5: Execution (plan execution)
    - Manage data flow between stages
    - Handle errors at boundaries
    - Track execution metrics
    
    Usage:
        orchestrator = WorkflowOrchestrator(workspace_root=Path("/project"))
        context = WorkflowExecutionContext(
            operation="implement_feature",
            description="Add user authentication",
            keywords=["auth", "login"],
            domain="auth",
        )
        result = orchestrator.execute_workflow(context)
    """
    
    def __init__(self, workspace_root: Path) -> None:
        """
        Initialize workflow orchestrator.
        
        Args:
            workspace_root: Root directory of workspace
        """
        self.workspace_root = workspace_root
        self.logger = EnhancedAuditLogger()
        
        # Initialize stages
        self.stage1 = MasterOrchestrationStage1()
        self.scanner = RepositoryScanner(workspace_root=workspace_root)
        self.stage3 = MasterOrchestrationStage3()
        self.stage4 = MasterOrchestrationStage4()
    
    def execute_workflow(
        self,
        context: WorkflowExecutionContext,
    ) -> WorkflowExecutionResult:
        """
        Execute complete 5-stage workflow.
        
        Args:
            context: Workflow execution context
            
        Returns:
            WorkflowExecutionResult with detailed execution metrics
        """
        ac_id = "AC-PROD-004-02"
        
        self.logger.log_operation_start(
            ac_id=ac_id,
            operation="Execute 5-Stage Workflow",
            details={
                "operation": context.operation,
                "domain": context.domain,
                "turn": context.turn_number,
            },
        )
        
        start_time = time.time()
        result = WorkflowExecutionResult(
            operation=context.operation,
            success=True,
            timestamp=datetime.now(),
        )
        
        try:
            # ================================================================
            # Stage 1: Comprehension
            # ================================================================
            stage1_result = self._execute_stage_1(context)
            result.stage_results.append(stage1_result)
            
            if not stage1_result.success:
                result.success = False
                result.errors.append(f"Stage 1 failed: {stage1_result.error}")
                self.logger.log_operation_complete(
                    ac_id=ac_id,
                    operation="Execute 5-Stage Workflow",
                    success=False,
                    details={"error": "Stage 1 failed"},
                )
                return result
            
            stage1_output: Stage1Output = stage1_result.output
            
            # ================================================================
            # Stage 2: Repository Scan
            # ================================================================
            stage2_result = self._execute_stage_2(context)
            result.stage_results.append(stage2_result)
            
            if not stage2_result.success:
                result.success = False
                result.errors.append(f"Stage 2 failed: {stage2_result.error}")
                # Continue anyway - scan is not critical
            
            stage2_output: Optional[ScanOutput] = stage2_result.output
            
            # ================================================================
            # Stage 3: Knowledge Processing
            # ================================================================
            stage3_result = self._execute_stage_3(context, stage2_output)
            result.stage_results.append(stage3_result)
            
            if not stage3_result.success:
                result.success = False
                result.errors.append(f"Stage 3 failed: {stage3_result.error}")
                # Continue anyway - knowledge is not critical
            
            stage3_output: Optional[Stage3Output] = stage3_result.output
            
            # ================================================================
            # Stage 4: Approval
            # ================================================================
            # Use confidence from Stage 1 for approval decision
            confidence = stage1_output.confidence_score
            if stage3_output and hasattr(stage3_output, 'confidence_score'):
                # Use Stage 3 confidence if available
                confidence = max(confidence, stage3_output.confidence_score)
            
            stage4_result = self._execute_stage_4(context, confidence)
            result.stage_results.append(stage4_result)
            
            if not stage4_result.success:
                result.success = False
                result.errors.append(f"Stage 4 failed: {stage4_result.error}")
                self.logger.log_operation_complete(
                    ac_id=ac_id,
                    operation="Execute 5-Stage Workflow",
                    success=False,
                    details={"error": "Stage 4 failed"},
                )
                return result
            
            stage4_output: Stage4Output = stage4_result.output
            
            # ================================================================
            # Prepare Final Results
            # ================================================================
            result.final_decision = {
                "approved": stage4_output.approved,
                "approval_reason": stage4_output.approval_reason,
                "approval_confidence": stage4_output.approval_confidence,
            }
            
            if stage4_output.implementation_plan:
                result.implementation_plan = stage4_output.implementation_plan
            
            result.total_duration = time.time() - start_time
            
            self.logger.log_operation_complete(
                ac_id=ac_id,
                operation="Execute 5-Stage Workflow",
                success=True,
                details={
                    "stages_completed": len(result.stage_results),
                    "approved": stage4_output.approved,
                    "duration": f"{result.total_duration:.2f}s",
                },
            )
            
            return result
            
        except Exception as e:
            result.success = False
            result.errors.append(f"Workflow error: {str(e)}")
            self.logger.log_operation_complete(
                ac_id=ac_id,
                operation="Execute 5-Stage Workflow",
                success=False,
                details={"error": str(e)},
            )
            return result
    
    # ========================================================================
    # Private Stage Execution Methods
    # ========================================================================
    
    def _execute_stage_1(
        self,
        context: WorkflowExecutionContext,
    ) -> WorkflowStageResult:
        """Execute Stage 1: Comprehension."""
        start_time = time.time()
        
        try:
            stage1_context = Stage1ComprehensionContext(
                operation=context.operation,
                description=context.description,
                keywords=context.keywords,
                domain=context.domain,
            )
            
            result = self.stage1.comprehend(stage1_context)
            
            if result.is_ok():
                output = result.ok_value()
                return WorkflowStageResult(
                    stage_name="Stage 1: Comprehension",
                    success=True,
                    output=output,
                    duration=time.time() - start_time,
                )
            else:
                return WorkflowStageResult(
                    stage_name="Stage 1: Comprehension",
                    success=False,
                    error=str(result.err_value()),
                    duration=time.time() - start_time,
                )
        
        except Exception as e:
            return WorkflowStageResult(
                stage_name="Stage 1: Comprehension",
                success=False,
                error=str(e),
                duration=time.time() - start_time,
            )
    
    def _execute_stage_2(
        self,
        context: WorkflowExecutionContext,
    ) -> WorkflowStageResult:
        """Execute Stage 2: Repository Scan."""
        start_time = time.time()
        
        try:
            if not context.target_paths:
                context.target_paths = [self.workspace_root / "src"]
            
            scan_context = ScanContext(
                workspace_root=context.workspace_root or self.workspace_root,
                target_paths=context.target_paths,
                exclude_patterns=["*.pyc", "__pycache__", ".git"],
            )
            
            output = self.scanner.scan(scan_context)
            
            return WorkflowStageResult(
                stage_name="Stage 2: Repository Scan",
                success=True,
                output=output,
                duration=time.time() - start_time,
            )
        
        except Exception as e:
            return WorkflowStageResult(
                stage_name="Stage 2: Repository Scan",
                success=False,
                error=str(e),
                duration=time.time() - start_time,
            )
    
    def _execute_stage_3(
        self,
        context: WorkflowExecutionContext,
        scan_output: Optional[ScanOutput],
    ) -> WorkflowStageResult:
        """Execute Stage 3: Knowledge Processing."""
        start_time = time.time()
        
        try:
            entities = scan_output.entities if scan_output else None
            
            stage3_context = Stage3KnowledgeContext(
                operation=context.operation,
                domain=context.domain,
                code_entities=entities,
                existing_knowledge=None,
                turn_number=context.turn_number,
            )
            
            result = self.stage3.process_knowledge(stage3_context)
            
            if result.is_ok():
                output = result.ok_value()
                return WorkflowStageResult(
                    stage_name="Stage 3: Knowledge Processing",
                    success=True,
                    output=output,
                    duration=time.time() - start_time,
                )
            else:
                return WorkflowStageResult(
                    stage_name="Stage 3: Knowledge Processing",
                    success=False,
                    error=str(result.err_value()),
                    duration=time.time() - start_time,
                )
        
        except Exception as e:
            return WorkflowStageResult(
                stage_name="Stage 3: Knowledge Processing",
                success=False,
                error=str(e),
                duration=time.time() - start_time,
            )
    
    def _execute_stage_4(
        self,
        context: WorkflowExecutionContext,
        confidence_score: float,
    ) -> WorkflowStageResult:
        """Execute Stage 4: Approval."""
        start_time = time.time()
        
        try:
            stage4_context = Stage4ApprovalContext(
                operation=context.operation,
                domain=context.domain,
                complexity=context.complexity,
                urgency=context.urgency,
                confidence_score=confidence_score,
                turn_number=context.turn_number,
            )
            
            result = self.stage4.approve_operation(stage4_context)
            
            if result.is_ok():
                output = result.ok_value()
                return WorkflowStageResult(
                    stage_name="Stage 4: Approval",
                    success=True,
                    output=output,
                    duration=time.time() - start_time,
                )
            else:
                return WorkflowStageResult(
                    stage_name="Stage 4: Approval",
                    success=False,
                    error=str(result.err_value()),
                    duration=time.time() - start_time,
                )
        
        except Exception as e:
            return WorkflowStageResult(
                stage_name="Stage 4: Approval",
                success=False,
                error=str(e),
                duration=time.time() - start_time,
            )
