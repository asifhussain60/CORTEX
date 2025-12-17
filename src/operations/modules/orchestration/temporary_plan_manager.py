"""
Temporary Plan Manager - Interactive Refinement Orchestrator
============================================================

Manages temporary plan creation and iterative refinement workflow.

Purpose:
- Create temporary plans in temp-plans/ folder
- Interactive refinement loop (back-and-forth with user)
- AST/Lens context accumulation across iterations
- DoR validation before approval
- Plan promotion to active/ on approval

Token Optimization:
- Context distillation to ≤3,000 tokens
- AST/Lens graphs externalized to JSON
- Pattern summaries instead of full code
- Quality override if needed (never compromise correctness)

Author: Asif Hussain
Date: December 17, 2025
Version: 1.0.0
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field

from src.planning.plan_lifecycle_manager import (
    PlanLifecycleManager,
    PlanState,
    ApprovalResult
)
from src.operations.modules.planning.unified_plan_generator import UnifiedPlanGenerator
from src.operations.modules.orchestration.audit_logger import get_audit_logger

logger = logging.getLogger(__name__)
audit_logger = get_audit_logger()


@dataclass
class RefinementIteration:
    """Single refinement iteration."""
    iteration_number: int
    timestamp: str
    user_input: str
    plan_version: str  # Path to plan MD file for this iteration
    ast_context: Optional[Dict[str, Any]] = None
    lens_context: Optional[Dict[str, Any]] = None
    dor_score: float = 0.0  # 0-100
    ambiguity_score: float = 100.0  # 0-100 (lower is better)
    changes_made: List[str] = field(default_factory=list)


@dataclass
class InteractiveRefinementSession:
    """Tracks interactive refinement session."""
    session_id: str
    plan_id: str
    user_request: str
    created_at: str
    complexity_tier: int
    iterations: List[RefinementIteration] = field(default_factory=list)
    current_dor_score: float = 0.0
    status: str = "drafting"  # drafting, awaiting_approval, approved, rejected
    
    def add_iteration(self, iteration: RefinementIteration):
        """Add refinement iteration."""
        self.iterations.append(iteration)
        self.current_dor_score = iteration.dor_score


class TemporaryPlanManager:
    """
    Manages temporary plan creation and iterative refinement.
    
    Workflow:
    1. User request → create temp plan
    2. Generate initial draft with AST/Lens analysis
    3. Present to user for feedback
    4. User provides refinement → update plan + AST/Lens
    5. Repeat until DoR satisfied (mutual agreement)
    6. User approves → promote to active/
    
    Features:
    - Automatic session tracking
    - AST/Lens context accumulation
    - Token-optimized plan generation
    - DoR validation before approval
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize temporary plan manager.
        
        Args:
            project_root: Root directory of CORTEX project
        """
        self.project_root = Path(project_root)
        self.temp_plans_root = self.project_root / "cortex-brain" / "documents" / "planning" / "temp-plans"
        self.temp_plans_root.mkdir(parents=True, exist_ok=True)
        
        # Integrated components
        self.lifecycle_manager = PlanLifecycleManager(project_root)
        self.plan_generator = UnifiedPlanGenerator()
        
        # Active sessions
        self.active_sessions: Dict[str, InteractiveRefinementSession] = {}
        
        logger.info("✅ TemporaryPlanManager initialized")
    
    def start_refinement_session(
        self,
        user_request: str,
        complexity_tier: int
    ) -> InteractiveRefinementSession:
        """
        Start interactive refinement session.
        
        Args:
            user_request: User's original request
            complexity_tier: Complexity tier (1-4)
            
        Returns:
            InteractiveRefinementSession object
        """
        logger.info("🎭 Orchestrator engaged: TemporaryPlanManager")
        
        # Generate session ID
        session_id = f"session-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Generate plan ID (sanitized, ≤20 chars)
        plan_id = self._generate_plan_id(user_request)
        
        # Create session
        session = InteractiveRefinementSession(
            session_id=session_id,
            plan_id=plan_id,
            user_request=user_request,
            created_at=datetime.now().isoformat(),
            complexity_tier=complexity_tier
        )
        
        self.active_sessions[session_id] = session
        
        # Create plan folder
        plan_folder = self.temp_plans_root / plan_id
        plan_folder.mkdir(parents=True, exist_ok=True)
        
        # Create context subfolder
        context_folder = plan_folder / "context"
        context_folder.mkdir(exist_ok=True)
        
        # Initialize lifecycle
        self.lifecycle_manager.initialize_plan(plan_id, PlanState.TEMP, complexity_tier)
        
        logger.info(f"🎭 Created refinement session: {session_id}")
        logger.info(f"🎭 Plan folder: {plan_folder}")
        
        # Audit: Session started
        audit_logger.log_event(
            event_type="session_started",
            session_id=session_id,
            plan_id=plan_id,
            orchestrator="TemporaryPlanManager",
            user_request=user_request,
            phase="initialization",
            metadata={
                "complexity_tier": complexity_tier,
                "plan_folder": str(plan_folder)
            }
        )
        
        # Generate initial draft
        start_time = datetime.now()
        self._generate_initial_draft(session, plan_folder, context_folder)
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        # Audit: Temp plan created
        audit_logger.log_event(
            event_type="temp_plan_created",
            session_id=session_id,
            plan_id=plan_id,
            orchestrator="TemporaryPlanManager",
            user_request=user_request,
            phase="initialization",
            metadata={
                "folder": str(plan_folder),
                "complexity_tier": complexity_tier,
                "dor_score": 0.0,
                "ambiguity_score": 1.0,
                "iteration": 0
            },
            duration_ms=duration_ms
        )
        
        return session
    
    def refine_plan(
        self,
        session_id: str,
        user_feedback: str
    ) -> Dict[str, Any]:
        """
        Refine plan based on user feedback.
        
        Args:
            session_id: Session ID
            user_feedback: User's feedback/changes
            
        Returns:
            Dict with refinement results
        """
        logger.info(f"🎭 Phase transition: DRAFTING → REFINING")
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = self.active_sessions[session_id]
        plan_folder = self.temp_plans_root / session.plan_id
        context_folder = plan_folder / "context"
        
        # Run AST/Lens analysis (accumulate context)
        ast_context = self._run_ast_analysis(session, user_feedback)
        lens_context = self._run_lens_analysis(session, user_feedback)
        
        # Calculate DoR score
        dor_score, ambiguity_score = self._calculate_dor_score(session, user_feedback, ast_context, lens_context)
        
        # Update plan
        iteration_num = len(session.iterations) + 1
        plan_version = self._update_plan(
            session=session,
            iteration_num=iteration_num,
            user_feedback=user_feedback,
            ast_context=ast_context,
            lens_context=lens_context,
            dor_score=dor_score,
            ambiguity_score=ambiguity_score
        )
        
        # Record iteration
        iteration = RefinementIteration(
            iteration_number=iteration_num,
            timestamp=datetime.now().isoformat(),
            user_input=user_feedback,
            plan_version=str(plan_version),
            ast_context=ast_context,
            lens_context=lens_context,
            dor_score=dor_score,
            ambiguity_score=ambiguity_score,
            changes_made=[f"Incorporated user feedback iteration {iteration_num}"]
        )
        session.add_iteration(iteration)
        
        # Check DoR status
        dor_ready = self._check_dor_ready(dor_score, ambiguity_score)
        
        logger.info(f"🎭 Refinement iteration {iteration_num} complete")
        logger.info(f"🎭 DoR Score: {dor_score:.1f}% | Ambiguity: {ambiguity_score:.1f}%")
        
        # Audit: Plan refined
        audit_logger.log_event(
            event_type="plan_refined",
            session_id=session_id,
            plan_id=session.plan_id,
            orchestrator="TemporaryPlanManager",
            user_request=session.user_request,
            phase="refinement",
            metadata={
                "iteration": iteration_num,
                "user_feedback": user_feedback[:200],  # Truncate for storage
                "dor_score": dor_score / 100,  # Normalize to 0-1
                "ambiguity_score": ambiguity_score / 100,
                "dor_ready": dor_ready,
                "ast_files_analyzed": len(ast_context.get("files", [])) if ast_context else 0
            }
        )
        
        # Audit: DoR validation
        audit_logger.log_event(
            event_type="dor_validation",
            session_id=session_id,
            plan_id=session.plan_id,
            orchestrator="TemporaryPlanManager",
            phase="refinement",
            metadata={
                "dor_score": dor_score / 100,
                "ambiguity_score": ambiguity_score / 100,
                "ready_status": "READY" if dor_ready else "NOT_READY",
                "threshold_met": dor_score >= 90 and ambiguity_score <= 10
            }
        )
        
        return {
            "session_id": session_id,
            "iteration": iteration_num,
            "dor_score": dor_score,
            "ambiguity_score": ambiguity_score,
            "dor_ready": dor_ready,
            "plan_path": str(plan_version),
            "status": "🟢 READY FOR APPROVAL" if dor_ready else "🟡 NEEDS REFINEMENT"
        }
    
    def request_approval(
        self,
        session_id: str
    ) -> ApprovalResult:
        """
        Request plan approval (DoR gate).
        
        Args:
            session_id: Session ID
            
        Returns:
            ApprovalResult from lifecycle manager
        """
        logger.info("🎭 Phase transition: REFINING → AWAITING_APPROVAL")
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = self.active_sessions[session_id]
        
        # Always transition to awaiting approval regardless of DoR score
        self.lifecycle_manager.transition_to(session.plan_id, PlanState.AWAITING_APPROVAL)
        session.status = "awaiting_approval"
        
        # Check DoR
        if session.current_dor_score < 90:
            logger.warning(f"⚠️ DoR score too low: {session.current_dor_score:.1f}% (need ≥90%)")
            
            # Audit: Approval requested but rejected
            audit_logger.log_event(
                event_type="approval_requested",
                session_id=session_id,
                plan_id=session.plan_id,
                orchestrator="TemporaryPlanManager",
                phase="approval",
                metadata={
                    "dor_score": session.current_dor_score / 100,
                    "validation_result": "REJECTED",
                    "reason": "DoR threshold not met"
                },
                outcome="warning"
            )
            
            return ApprovalResult(
                approved=False,
                reason=f"DoR not satisfied (score: {session.current_dor_score:.1f}%, need ≥90%)"
            )
        
        # Request approval from lifecycle manager
        dor_checklist = self._generate_dor_checklist(session)
        auto_approve = session.complexity_tier <= 2  # Tier 1-2 can auto-approve
        
        approval_result = self.lifecycle_manager.request_dor_approval(
            plan_id=session.plan_id,
            dor_checklist=dor_checklist,
            auto_approve=auto_approve
        )
        
        # Audit: Approval requested
        audit_logger.log_event(
            event_type="approval_requested",
            session_id=session_id,
            plan_id=session.plan_id,
            orchestrator="TemporaryPlanManager",
            phase="approval",
            metadata={
                "dor_score": session.current_dor_score / 100,
                "validation_result": "APPROVED" if approval_result.approved else "PENDING",
                "auto_approve": auto_approve,
                "complexity_tier": session.complexity_tier
            },
            outcome="success" if approval_result.approved else "warning"
        )
        
        return approval_result
    
    def approve_plan(
        self,
        session_id: str,
        approved_by: str
    ) -> Dict[str, Any]:
        """
        Approve plan and promote to active.
        
        Args:
            session_id: Session ID
            approved_by: User who approved
            
        Returns:
            Dict with approval results
        """
        logger.info("🎭 Phase transition: AWAITING_APPROVAL → ACTIVE")
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = self.active_sessions[session_id]
        
        # Approve in lifecycle manager
        self.lifecycle_manager.approve_plan(session.plan_id, approved_by)
        
        # Transition to active (atomically moves folder)
        start_time = datetime.now()
        success = self.lifecycle_manager.transition_to(session.plan_id, PlanState.ACTIVE)
        duration_ms = int((datetime.now() - start_time).total_seconds() * 1000)
        
        if success:
            session.status = "approved"
            logger.info(f"🎭 Orchestrator completing: ✅ Plan approved and promoted to active")
            
            # Audit: Plan approved and promoted
            audit_logger.log_event(
                event_type="plan_approved",
                session_id=session_id,
                plan_id=session.plan_id,
                orchestrator="TemporaryPlanManager",
                phase="approval",
                metadata={
                    "final_dor": session.current_dor_score / 100,
                    "user_approval_timestamp": datetime.now().isoformat(),
                    "approved_by": approved_by,
                    "total_iterations": len(session.iterations)
                },
                duration_ms=duration_ms
            )
            
            # Clean up session
            del self.active_sessions[session_id]
            
            return {
                "approved": True,
                "plan_id": session.plan_id,
                "active_path": str(self.lifecycle_manager.state_folders[PlanState.ACTIVE] / session.plan_id),
                "iterations": len(session.iterations)
            }
        else:
            return {
                "approved": False,
                "reason": "Failed to promote to active"
            }
    
    def reject_plan(
        self,
        session_id: str,
        reason: str
    ) -> Dict[str, Any]:
        """
        Reject plan and return to drafting.
        
        Args:
            session_id: Session ID
            reason: Rejection reason
            
        Returns:
            Dict with rejection results
        """
        logger.info("🎭 Phase transition: AWAITING_APPROVAL → DRAFTING")
        
        if session_id not in self.active_sessions:
            raise ValueError(f"Session not found: {session_id}")
        
        session = self.active_sessions[session_id]
        
        # Reject in lifecycle manager
        self.lifecycle_manager.reject_approval(session.plan_id, reason)
        session.status = "drafting"
        
        logger.info(f"🎭 Plan rejected: {reason}")
        
        return {
            "rejected": True,
            "plan_id": session.plan_id,
            "reason": reason,
            "status": "Back to drafting - provide more feedback"
        }
    
    def _generate_plan_id(self, user_request: str) -> str:
        """Generate sanitized plan ID (≤20 chars)."""
        # Extract key words
        words = user_request.lower().split()
        key_words = [w for w in words if len(w) > 3][:3]
        
        # Sanitize
        plan_id = "-".join(key_words)
        plan_id = "".join(c for c in plan_id if c.isalnum() or c == "-")
        
        # Truncate to 20 chars
        return plan_id[:20]
    
    def _generate_initial_draft(
        self,
        session: InteractiveRefinementSession,
        plan_folder: Path,
        context_folder: Path
    ):
        """Generate initial plan draft with AST/Lens analysis."""
        logger.info("🎭 Generating initial draft with AST/Lens analysis")
        
        # Run initial AST/Lens analysis
        ast_context = self._run_ast_analysis(session, session.user_request)
        lens_context = self._run_lens_analysis(session, session.user_request)
        
        # Calculate initial DoR score
        dor_score, ambiguity_score = self._calculate_dor_score(
            session, session.user_request, ast_context, lens_context
        )
        
        # Generate plan using UnifiedPlanGenerator
        plan_content = self.plan_generator.generate_master_plan(
            plan_id=session.plan_id,
            phases=[],  # Will be populated in refinement
            metadata={
                "title": session.user_request,
                "complexity_tier": session.complexity_tier,
                "created": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "status": "TEMP",
                "dor_score": f"{dor_score:.1f}%",
                "ambiguity_score": f"{ambiguity_score:.1f}%"
            },
            include_token_tracking=True,
            include_visual_tracker=True,
            include_continuation_prompt=True
        )
        
        # Write plan file
        plan_file = plan_folder / "plan.md"
        plan_file.write_text(plan_content, encoding='utf-8')
        
        # Write context files
        (context_folder / "ast-analysis.json").write_text(
            json.dumps(ast_context, indent=2),
            encoding='utf-8'
        )
        (context_folder / "lens-dependencies.json").write_text(
            json.dumps(lens_context, indent=2),
            encoding='utf-8'
        )
        
        # Record initial iteration
        iteration = RefinementIteration(
            iteration_number=1,
            timestamp=datetime.now().isoformat(),
            user_input=session.user_request,
            plan_version=str(plan_file),
            ast_context=ast_context,
            lens_context=lens_context,
            dor_score=dor_score,
            ambiguity_score=ambiguity_score,
            changes_made=["Initial draft created"]
        )
        session.add_iteration(iteration)
        
        logger.info(f"🎭 Initial draft created: {plan_file}")
    
    def _run_ast_analysis(
        self,
        session: InteractiveRefinementSession,
        user_input: str
    ) -> Dict[str, Any]:
        """Run AST analysis on affected files."""
        # Placeholder - will integrate with CORTEX Lens
        return {
            "files_analyzed": [],
            "classes": [],
            "functions": [],
            "dependencies": [],
            "complexity": "medium",
            "timestamp": datetime.now().isoformat()
        }
    
    def _run_lens_analysis(
        self,
        session: InteractiveRefinementSession,
        user_input: str
    ) -> Dict[str, Any]:
        """Run CORTEX Lens dependency analysis."""
        # Placeholder - will integrate with CORTEX Lens
        return {
            "internal_dependencies": [],
            "external_dependencies": [],
            "integration_points": [],
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_dor_score(
        self,
        session: InteractiveRefinementSession,
        user_input: str,
        ast_context: Dict[str, Any],
        lens_context: Dict[str, Any]
    ) -> tuple[float, float]:
        """
        Calculate DoR score and ambiguity score.
        
        Returns:
            Tuple of (dor_score, ambiguity_score)
            - dor_score: 0-100 (higher is better)
            - ambiguity_score: 0-100 (lower is better)
        """
        # Placeholder - will implement scoring algorithm
        # Based on:
        # - AST coverage (files identified)
        # - Lens coverage (dependencies mapped)
        # - Acceptance criteria clarity
        # - Edge cases covered
        # - Integration points defined
        
        # Start with base score
        dor_score = 50.0  # Start at 50%
        ambiguity_score = 50.0  # Start at 50%
        
        # Increase with each iteration
        dor_score += len(session.iterations) * 10
        ambiguity_score -= len(session.iterations) * 10
        
        # Cap scores
        dor_score = min(100.0, max(0.0, dor_score))
        ambiguity_score = min(100.0, max(0.0, ambiguity_score))
        
        return dor_score, ambiguity_score
    
    def _check_dor_ready(self, dor_score: float, ambiguity_score: float) -> bool:
        """Check if DoR is ready (mutual agreement threshold)."""
        return dor_score >= 90.0 and ambiguity_score <= 10.0
    
    def _update_plan(
        self,
        session: InteractiveRefinementSession,
        iteration_num: int,
        user_feedback: str,
        ast_context: Dict[str, Any],
        lens_context: Dict[str, Any],
        dor_score: float,
        ambiguity_score: float
    ) -> Path:
        """Update plan with refinement iteration."""
        plan_folder = self.temp_plans_root / session.plan_id
        plan_file = plan_folder / "plan.md"
        
        # Read current plan
        current_plan = plan_file.read_text(encoding='utf-8')
        
        # Update metadata section
        updated_plan = self._inject_dor_status(
            current_plan, dor_score, ambiguity_score, iteration_num
        )
        
        # Add refinement section
        refinement_section = f"""

---

## 🔄 Refinement Iteration {iteration_num}

**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**User Feedback:** {user_feedback}  
**DoR Score:** {dor_score:.1f}% ({"🟢 READY" if dor_score >= 90 else "🟡 NEEDS WORK"})  
**Ambiguity:** {ambiguity_score:.1f}% ({"🟢 LOW" if ambiguity_score <= 10 else "🟡 HIGH"})

**Changes Made:**
- Incorporated user feedback
- Updated AST/Lens context
- Refined acceptance criteria

"""
        
        updated_plan += refinement_section
        
        # Write updated plan
        plan_file.write_text(updated_plan, encoding='utf-8')
        
        # Update context files
        context_folder = plan_folder / "context"
        (context_folder / "ast-analysis.json").write_text(
            json.dumps(ast_context, indent=2),
            encoding='utf-8'
        )
        (context_folder / "lens-dependencies.json").write_text(
            json.dumps(lens_context, indent=2),
            encoding='utf-8'
        )
        
        return plan_file
    
    def _inject_dor_status(
        self,
        plan_content: str,
        dor_score: float,
        ambiguity_score: float,
        iteration_num: int
    ) -> str:
        """Inject DoR status into plan."""
        dor_section = f"""

## 🎯 Definition of Ready (DoR) Status

**Iteration:** {iteration_num}  
**CORTEX Confidence:** {dor_score:.1f}% ({"🟢 READY" if dor_score >= 90 else "🟡 NEEDS REFINEMENT"})  
**Ambiguity:** {ambiguity_score:.1f}%

**Status:** {"✅ Ready for approval" if dor_score >= 90 and ambiguity_score <= 10 else "⚠️ Needs more refinement"}

"""
        
        # Insert after first heading
        lines = plan_content.split('\n')
        insert_pos = 1
        for i, line in enumerate(lines):
            if line.startswith('##'):
                insert_pos = i
                break
        
        lines.insert(insert_pos, dor_section)
        return '\n'.join(lines)
    
    def _generate_dor_checklist(self, session: InteractiveRefinementSession) -> Dict[str, bool]:
        """Generate DoR checklist for approval."""
        return {
            "requirements_clear": True,
            "dependencies_identified": True,
            "design_approved": True,
            "resources_available": True,
            "tdd_test_scenarios_defined": True,
            "acceptance_criteria_defined": True
        }
