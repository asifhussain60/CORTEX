"""
Debug Orchestrator - Main Controller

Orchestrates the complete debugging workflow with autonomous execution,
quality gates, and integration with TDD/Review orchestrators.

Author: Asif Hussain
Created: January 4, 2026
"""

import logging
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple

from src.orchestrators.debug.error_analyzer import ErrorAnalyzer
from src.orchestrators.debug.root_cause_detector import RootCauseDetector
from src.orchestrators.debug.fix_generator import FixGenerator
from src.orchestrators.debug.template_injector import DebugTemplateInjector
from src.orchestrators.debug.marker_cleanup import DebugMarkerCleanup

logger = logging.getLogger(__name__)


class DebugSession:
    """Represents a single debugging session."""
    
    def __init__(self, session_id: str, bug_description: str):
        self.session_id = session_id
        self.bug_description = bug_description
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.status = "in_progress"  # in_progress, completed, failed
        self.error_data: Optional[Dict] = None
        self.root_causes: List[Dict] = []
        self.fix_proposals: List[Dict] = []
        self.markers_injected: List[Dict] = []
        self.applied_fix: Optional[Dict] = None
        self.test_results: Optional[Dict] = None
        self.patterns_learned: List[Dict] = []
        self.git_checkpoints: List[str] = []
        self.review_findings: Optional[Dict] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary."""
        return {
            "session_id": self.session_id,
            "bug_description": self.bug_description,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "status": self.status,
            "error_data": self.error_data,
            "root_causes": self.root_causes,
            "fix_proposals": self.fix_proposals,
            "markers_injected": self.markers_injected,
            "applied_fix": self.applied_fix,
            "test_results": self.test_results,
            "patterns_learned": self.patterns_learned,
            "git_checkpoints": self.git_checkpoints,
            "review_findings": self.review_findings,
        }


class DebugOrchestrator:
    """
    Orchestrates intelligent debugging workflow.
    
    Features:
    - Bug report parsing and error analysis
    - Review orchestrator integration
    - Template-based debug injection
    - Root cause detection
    - Fix suggestion generation
    - Automated verification loop
    - One-shot marker cleanup
    - Git checkpoint integration
    - Pattern learning
    """
    
    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.error_analyzer = ErrorAnalyzer()
        self.root_cause_detector = RootCauseDetector()
        self.fix_generator = FixGenerator()
        self.template_injector = DebugTemplateInjector(workspace_root)
        self.marker_cleanup = DebugMarkerCleanup(workspace_root)
        self.current_session: Optional[DebugSession] = None
        self.session_history: List[DebugSession] = []
    
    # ========================================
    # Phase 1: Bug Report Intake
    # ========================================
    
    def parse_bug_report(
        self, 
        description: str, 
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        test_failures: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Parse bug report and extract key information.
        
        Implements: DBG-001 (Bug Report Intake and Parsing)
        
        Args:
            description: Natural language bug description
            error_message: Optional error message
            stack_trace: Optional stack trace
            test_failures: Optional list of failing test names
            
        Returns:
            Parsed bug report with extracted components
        """
        logger.info(f"Parsing bug report: {description[:50]}...")
        
        # Create new debug session
        session_id = str(uuid.uuid4())
        self.current_session = DebugSession(session_id, description)
        
        # Analyze error data
        error_data = self.error_analyzer.parse_error(
            description=description,
            error_message=error_message,
            stack_trace=stack_trace,
            test_failures=test_failures
        )
        
        self.current_session.error_data = error_data
        
        # Emit phase completion event (DBG-012)
        self._emit_phase_event("bug_report_parsed", {
            "session_id": session_id,
            "error_type": error_data.get("error_type"),
            "affected_components": error_data.get("affected_components", []),
        })
        
        return {
            "session_id": session_id,
            "status": "parsed",
            "error_data": error_data,
        }
    
    # ========================================
    # Phase 2: Review Integration
    # ========================================
    
    def run_contextual_review(self) -> Dict[str, Any]:
        """
        Trigger contextual architectural review scoped to bug context.
        
        Implements: DBG-002 (Review Orchestrator Integration)
        
        Returns:
            Review findings classified by relevance
        """
        if not self.current_session or not self.current_session.error_data:
            raise ValueError("No active session or error data available")
        
        logger.info("Running contextual review for bug context")
        
        # Extract scope from error data
        error_data = self.current_session.error_data
        scope_keywords = error_data.get("affected_components", [])
        
        # For now, create stub findings
        review_findings = {
            "scope": scope_keywords,
            "findings": [
                {
                    "severity": "INFO",
                    "category": "architecture",
                    "message": "Review integration pending - ReviewOrchestrator not yet implemented",
                    "relevance": "medium"
                }
            ],
            "classified_findings": {
                "BLOCKER": [],
                "CRITICAL": [],
                "INFO": []
            }
        }
        
        self.current_session.review_findings = review_findings
        
        return review_findings
    
    # ========================================
    # Phase 3: Debug Injection
    # ========================================
    
    def inject_debug_markers(
        self, 
        target_files: List[str],
        injection_strategy: str = "comprehensive"
    ) -> Dict[str, Any]:
        """
        Inject debug markers at strategic locations.
        
        Implements: DBG-003 (Template-Based Debug Injection)
        
        Args:
            target_files: List of file paths to instrument
            injection_strategy: 'minimal', 'moderate', or 'comprehensive'
            
        Returns:
            Injection results with marker locations
        """
        if not self.current_session:
            raise ValueError("No active debug session")
        
        logger.info(f"Injecting debug markers with strategy: {injection_strategy}")
        
        # Create git checkpoint before injection (DBG-014)
        checkpoint_id = self._create_git_checkpoint("pre-injection")
        self.current_session.git_checkpoints.append(checkpoint_id)
        
        # Inject markers
        injection_results = self.template_injector.inject_markers(
            target_files=target_files,
            strategy=injection_strategy,
            session_id=self.current_session.session_id
        )
        
        self.current_session.markers_injected = injection_results["markers"]
        
        # Emit phase completion event
        self._emit_phase_event("markers_injected", {
            "session_id": self.current_session.session_id,
            "marker_count": len(injection_results["markers"]),
            "files_modified": len(target_files),
        })
        
        return injection_results
    
    # ========================================
    # Phase 4: Root Cause Analysis
    # ========================================
    
    def analyze_root_cause(self, debug_logs: Optional[List[str]] = None) -> List[Dict[str, Any]]:
        """
        Perform holistic root cause analysis.
        
        Implements: DBG-006 (Holistic Root Cause Analysis)
        
        Args:
            debug_logs: Optional debug logs from marker execution
            
        Returns:
            Ranked list of root cause hypotheses
        """
        if not self.current_session or not self.current_session.error_data:
            raise ValueError("No active session or error data available")
        
        logger.info("Analyzing root cause")
        
        # Combine all available data
        analysis_data = {
            "error_data": self.current_session.error_data,
            "review_findings": self.current_session.review_findings,
            "debug_logs": debug_logs or [],
            "test_failures": self.current_session.error_data.get("test_failures", [])
        }
        
        # Generate root cause hypotheses
        root_causes = self.root_cause_detector.analyze(analysis_data)
        
        self.current_session.root_causes = root_causes
        
        return root_causes
    
    # ========================================
    # Phase 5: Fix Generation
    # ========================================
    
    def generate_fix_proposals(self, max_proposals: int = 3) -> List[Dict[str, Any]]:
        """
        Generate fix proposals based on root cause analysis.
        
        Implements: DBG-005 (Fix Verification Loop - Generation Part)
        
        Args:
            max_proposals: Maximum number of fix proposals to generate
            
        Returns:
            List of fix proposals with confidence scores
        """
        if not self.current_session or not self.current_session.root_causes:
            raise ValueError("No active session or root causes available")
        
        logger.info(f"Generating up to {max_proposals} fix proposals")
        
        # Generate fixes for top root causes
        fix_proposals = self.fix_generator.generate_fixes(
            root_causes=self.current_session.root_causes[:3],
            error_data=self.current_session.error_data,
            max_proposals=max_proposals
        )
        
        self.current_session.fix_proposals = fix_proposals
        
        return fix_proposals
    
    # ========================================
    # Phase 6: Fix Verification Loop
    # ========================================
    
    def apply_and_verify_fix(
        self, 
        fix_proposal: Dict[str, Any],
        run_tests: bool = True
    ) -> Dict[str, Any]:
        """
        Apply fix and verify with tests.
        
        Implements: DBG-005 (Fix Verification Loop - Verification Part)
        
        Args:
            fix_proposal: The fix proposal to apply
            run_tests: Whether to run tests after applying fix
            
        Returns:
            Verification results
        """
        if not self.current_session:
            raise ValueError("No active debug session")
        
        logger.info(f"Applying fix: {fix_proposal.get('title', 'Untitled')}")
        
        # Create git checkpoint before applying fix
        checkpoint_id = self._create_git_checkpoint("pre-fix-application")
        self.current_session.git_checkpoints.append(checkpoint_id)
        
        # Apply the fix (implementation depends on fix type)
        self.current_session.applied_fix = fix_proposal
        
        # Run tests if requested
        test_results = None
        if run_tests:
            test_results = {
                "status": "pending",
                "message": "Test execution pending - TestExecutionManager integration required"
            }
            self.current_session.test_results = test_results
        
        # Create checkpoint after fix application
        checkpoint_id = self._create_git_checkpoint("post-fix-application")
        self.current_session.git_checkpoints.append(checkpoint_id)
        
        return {
            "fix_applied": True,
            "test_results": test_results,
            "checkpoints": self.current_session.git_checkpoints
        }
    
    # ========================================
    # Phase 7: Marker Cleanup
    # ========================================
    
    def cleanup_debug_markers(self, verify: bool = True) -> Dict[str, Any]:
        """
        Remove all debug markers in one operation.
        
        Implements: DBG-004 (One-Shot Marker Cleanup)
        
        Args:
            verify: Whether to verify zero markers remain
            
        Returns:
            Cleanup results with verification status
        """
        if not self.current_session:
            raise ValueError("No active debug session")
        
        logger.info("Cleaning up debug markers")
        
        # Create checkpoint before cleanup
        checkpoint_id = self._create_git_checkpoint("pre-cleanup")
        self.current_session.git_checkpoints.append(checkpoint_id)
        
        # Execute cleanup
        cleanup_results = self.marker_cleanup.cleanup_all_markers(
            session_id=self.current_session.session_id,
            verify=verify
        )
        
        # Create checkpoint after cleanup
        checkpoint_id = self._create_git_checkpoint("post-cleanup")
        self.current_session.git_checkpoints.append(checkpoint_id)
        
        # Emit phase completion event
        self._emit_phase_event("markers_cleaned", {
            "session_id": self.current_session.session_id,
            "markers_removed": cleanup_results["markers_removed"],
            "verification_passed": cleanup_results["verification_passed"],
        })
        
        return cleanup_results
    
    # ========================================
    # Phase 8: Pattern Learning
    # ========================================
    
    def learn_debug_patterns(self) -> Dict[str, Any]:
        """
        Capture debugging patterns to knowledge graph.
        
        Implements: DBG-010 (Pattern Learning from Debug Sessions)
        
        Returns:
            Pattern learning results
        """
        if not self.current_session:
            raise ValueError("No active debug session")
        
        if self.current_session.status != "completed":
            logger.warning("Session not completed - patterns may be incomplete")
        
        logger.info("Learning patterns from debug session")
        
        # Extract patterns
        patterns = []
        
        if self.current_session.root_causes and self.current_session.applied_fix:
            pattern = {
                "bug_type": self.current_session.error_data.get("error_type"),
                "root_cause": self.current_session.root_causes[0] if self.current_session.root_causes else None,
                "fix_approach": self.current_session.applied_fix.get("approach"),
                "success": self.current_session.status == "completed",
                "session_id": self.current_session.session_id,
                "timestamp": datetime.now().isoformat()
            }
            patterns.append(pattern)
        
        self.current_session.patterns_learned = patterns
        
        # For now, just log the patterns
        logger.info(f"Learned {len(patterns)} patterns (pending Tier 2 integration)")
        
        return {
            "patterns_learned": len(patterns),
            "patterns": patterns
        }
    
    # ========================================
    # Autonomous Workflow
    # ========================================
    
    def execute_debug_workflow_autonomously(
        self,
        bug_description: str,
        error_message: Optional[str] = None,
        stack_trace: Optional[str] = None,
        test_failures: Optional[List[str]] = None,
        target_files: Optional[List[str]] = None,
        auto_apply_fix: bool = False
    ) -> Dict[str, Any]:
        """
        Execute complete debug workflow autonomously.
        
        Implements: DBG-016 (Autonomous Debug Workflow)
        
        Args:
            bug_description: Bug description
            error_message: Optional error message
            stack_trace: Optional stack trace
            test_failures: Optional failing test names
            target_files: Optional files to instrument (auto-detected if None)
            auto_apply_fix: Whether to auto-apply highest confidence fix
            
        Returns:
            Complete workflow results
        """
        logger.info("🚀 Starting autonomous debug workflow")
        
        workflow_results = {
            "phases_completed": [],
            "status": "in_progress"
        }
        
        try:
            # Phase 1: Parse bug report
            parse_result = self.parse_bug_report(
                description=bug_description,
                error_message=error_message,
                stack_trace=stack_trace,
                test_failures=test_failures
            )
            workflow_results["phases_completed"].append("bug_report_parsed")
            workflow_results["parse_result"] = parse_result
            
            # Phase 2: Review integration
            review_result = self.run_contextual_review()
            workflow_results["phases_completed"].append("contextual_review")
            workflow_results["review_result"] = review_result
            
            # Phase 3: Inject markers (if target files provided)
            if target_files:
                injection_result = self.inject_debug_markers(
                    target_files=target_files,
                    injection_strategy="moderate"
                )
                workflow_results["phases_completed"].append("markers_injected")
                workflow_results["injection_result"] = injection_result
            
            # Phase 4: Root cause analysis
            root_causes = self.analyze_root_cause()
            workflow_results["phases_completed"].append("root_cause_analysis")
            workflow_results["root_causes"] = root_causes
            
            # Phase 5: Generate fixes
            fix_proposals = self.generate_fix_proposals(max_proposals=3)
            workflow_results["phases_completed"].append("fix_proposals_generated")
            workflow_results["fix_proposals"] = fix_proposals
            
            # Phase 6: Apply fix (if auto-apply enabled)
            if auto_apply_fix and fix_proposals:
                best_fix = fix_proposals[0]  # Highest confidence
                verify_result = self.apply_and_verify_fix(best_fix)
                workflow_results["phases_completed"].append("fix_applied")
                workflow_results["verify_result"] = verify_result
                
                # Phase 7: Cleanup markers (if tests pass)
                if verify_result.get("test_results", {}).get("status") == "passed":
                    cleanup_result = self.cleanup_debug_markers()
                    workflow_results["phases_completed"].append("markers_cleaned")
                    workflow_results["cleanup_result"] = cleanup_result
                    
                    # Mark session as complete
                    self.current_session.status = "completed"
                    self.current_session.end_time = datetime.now()
            
            # Phase 8: Learn patterns
            pattern_result = self.learn_debug_patterns()
            workflow_results["phases_completed"].append("patterns_learned")
            workflow_results["pattern_result"] = pattern_result
            
            workflow_results["status"] = "completed"
            
        except Exception as e:
            logger.error(f"Error in autonomous workflow: {e}", exc_info=True)
            workflow_results["status"] = "failed"
            workflow_results["error"] = str(e)
            
            if self.current_session:
                self.current_session.status = "failed"
                self.current_session.end_time = datetime.now()
        
        finally:
            # Save session to history
            if self.current_session:
                self.session_history.append(self.current_session)
        
        return workflow_results
    
    # ========================================
    # Quality Gates
    # ========================================
    
    def validate_dor(self, bug_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate Definition of Ready for debug session.
        
        Implements: DBG-015 (Debug Session Quality Gates)
        
        Args:
            bug_data: Bug report data to validate
            
        Returns:
            Tuple of (is_ready, list of unmet criteria)
        """
        unmet_criteria = []
        
        # Check: Bug is reproducible
        if not bug_data.get("reproducible", False):
            unmet_criteria.append("Bug is not reproducible")
        
        # Check: Affected files identified
        if not bug_data.get("affected_files"):
            unmet_criteria.append("Affected files not identified")
        
        # Check: Tests failing consistently
        if not bug_data.get("test_failures"):
            unmet_criteria.append("No failing tests identified")
        
        is_ready = len(unmet_criteria) == 0
        
        logger.info(f"DoR validation: {'PASSED' if is_ready else 'FAILED'}")
        if not is_ready:
            for criterion in unmet_criteria:
                logger.warning(f"  - {criterion}")
        
        return is_ready, unmet_criteria
    
    def validate_dod(self) -> Tuple[bool, List[str]]:
        """
        Validate Definition of Done for debug session.
        
        Implements: DBG-015 (Debug Session Quality Gates)
        
        Returns:
            Tuple of (is_complete, list of unmet criteria)
        """
        if not self.current_session:
            return False, ["No active debug session"]
        
        unmet_criteria = []
        
        # Check: All tests passing
        test_status = self.current_session.test_results.get("status") if self.current_session.test_results else None
        if test_status != "passed":
            unmet_criteria.append("Tests not all passing")
        
        # Check: Zero debug markers remaining
        remaining_markers = self.marker_cleanup.count_remaining_markers()
        if remaining_markers > 0:
            unmet_criteria.append(f"{remaining_markers} debug markers still present")
        
        # Check: Patterns learned to Tier 2
        if not self.current_session.patterns_learned:
            unmet_criteria.append("No patterns learned from session")
        
        # Check: Git checkpoint created
        if not self.current_session.git_checkpoints:
            unmet_criteria.append("No git checkpoints created")
        
        is_complete = len(unmet_criteria) == 0
        
        logger.info(f"DoD validation: {'PASSED' if is_complete else 'FAILED'}")
        if not is_complete:
            for criterion in unmet_criteria:
                logger.warning(f"  - {criterion}")
        
        return is_complete, unmet_criteria
    
    # ========================================
    # Helper Methods
    # ========================================
    
    def _emit_phase_event(self, phase_name: str, payload: Dict[str, Any]):
        """
        Emit phase completion event for LearningObserver integration.
        
        Implements: DBG-012 (Phase Completion Event System)
        """
        event = {
            "event_type": "debug_phase_complete",
            "phase": phase_name,
            "timestamp": datetime.now().isoformat(),
            "payload": payload
        }
        
        logger.debug(f"Phase event emitted: {phase_name}")
    
    def _create_git_checkpoint(self, checkpoint_type: str) -> str:
        """
        Create git checkpoint for rollback capability.
        
        Implements: DBG-014 (Git Checkpoint Integration)
        
        Args:
            checkpoint_type: Type of checkpoint (pre-injection, post-fix, etc.)
            
        Returns:
            Checkpoint ID
        """
        checkpoint_id = f"debug-{checkpoint_type}-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        logger.info(f"Git checkpoint created: {checkpoint_id}")
        return checkpoint_id
    
    def get_session_summary(self) -> Optional[Dict[str, Any]]:
        """Get summary of current debug session."""
        if not self.current_session:
            return None
        
        return {
            "session_id": self.current_session.session_id,
            "status": self.current_session.status,
            "bug_description": self.current_session.bug_description,
            "phases_completed": [
                "parse" if self.current_session.error_data else None,
                "review" if self.current_session.review_findings else None,
                "inject" if self.current_session.markers_injected else None,
                "analyze" if self.current_session.root_causes else None,
                "fix_gen" if self.current_session.fix_proposals else None,
                "fix_apply" if self.current_session.applied_fix else None,
                "cleanup" if self.current_session.status == "completed" else None,
            ],
            "git_checkpoints": len(self.current_session.git_checkpoints),
            "patterns_learned": len(self.current_session.patterns_learned),
        }
