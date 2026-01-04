"""
Refinement Orchestrator

Main orchestrator class implementing 7-phase code quality improvement workflow.

Author: Asif Hussain
Created: January 3, 2026
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from .phases.quality_assessment import QualityAssessmentPhase
from .phases.duplicate_detection import DuplicateDetectionPhase
from .phases.performance_analysis import PerformanceAnalysisPhase
from .phases.security_audit import SecurityAuditPhase
from .phases.refactoring_plan import RefactoringPlanPhase
from .phases.apply_refactorings import ApplyRefactoringsPhase
from .phases.validation_metrics import ValidationMetricsPhase
from .utils.metrics_reporter import MetricsReporter

logger = logging.getLogger(__name__)


class RefinementOrchestrator:
    """
    7-phase code quality improvement orchestrator.
    
    Phases:
        1. Code Quality Assessment
        2. Duplicate Detection
        3. Performance Analysis
        4. Security Audit
        5. Refactoring Plan
        6. Apply Refactorings
        7. Validation & Metrics
    """
    
    def __init__(self, target_path: Path, output_dir: Optional[Path] = None):
        """
        Initialize refinement orchestrator.
        
        Args:
            target_path: File or directory to refine
            output_dir: Directory for reports and artifacts
        """
        self.target_path = Path(target_path)
        self.output_dir = Path(output_dir) if output_dir else Path.cwd() / "refinement-output"
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.state: Dict[str, Any] = {
            "session_id": self.session_id,
            "target_path": str(self.target_path),
            "start_time": None,
            "end_time": None,
            "phases_completed": [],
            "current_phase": None,
            "results": {}
        }
        
        # Initialize phases
        self.phases = [
            QualityAssessmentPhase(self),
            DuplicateDetectionPhase(self),
            PerformanceAnalysisPhase(self),
            SecurityAuditPhase(self),
            RefactoringPlanPhase(self),
            ApplyRefactoringsPhase(self),
            ValidationMetricsPhase(self)
        ]
        
        self.reporter = MetricsReporter(self.output_dir)
        
        logger.info(f"Initialized RefinementOrchestrator for {self.target_path}")
    
    def execute(self, phases: Optional[List[int]] = None, auto_apply: bool = False) -> Dict[str, Any]:
        """
        Execute refinement workflow.
        
        Args:
            phases: Specific phases to run (1-7). If None, runs all phases.
            auto_apply: If True, automatically applies refactorings in Phase 6
            
        Returns:
            Dictionary containing all phase results and final metrics
        """
        self.state["start_time"] = datetime.now().isoformat()
        
        logger.info(f"Starting refinement workflow (Session: {self.session_id})")
        
        # Determine which phases to execute
        phases_to_run = phases if phases else list(range(1, 8))
        
        try:
            for phase_num in phases_to_run:
                phase = self.phases[phase_num - 1]
                self._execute_phase(phase, auto_apply=(phase_num == 6 and auto_apply))
            
            # Generate final report
            self._generate_final_report()
            
            self.state["end_time"] = datetime.now().isoformat()
            self.state["status"] = "completed"
            
            logger.info(f"Refinement workflow completed (Session: {self.session_id})")
            
        except Exception as e:
            self.state["status"] = "failed"
            self.state["error"] = str(e)
            logger.error(f"Refinement workflow failed: {e}", exc_info=True)
            raise
        
        return self.state
    
    def _execute_phase(self, phase: Any, auto_apply: bool = False) -> None:
        """Execute a single phase."""
        phase_name = phase.__class__.__name__.replace("Phase", "")
        self.state["current_phase"] = phase_name
        
        logger.info(f"Executing Phase: {phase_name}")
        
        try:
            # Pass auto_apply for Phase 6
            if hasattr(phase, 'execute'):
                if phase_name == "ApplyRefactorings":
                    result = phase.execute(auto_apply=auto_apply)
                else:
                    result = phase.execute()
            else:
                result = {"status": "skipped", "reason": "not implemented"}
            
            self.state["results"][phase_name] = result
            self.state["phases_completed"].append(phase_name)
            
            logger.info(f"Phase {phase_name} completed")
            
        except Exception as e:
            logger.error(f"Phase {phase_name} failed: {e}", exc_info=True)
            self.state["results"][phase_name] = {"status": "failed", "error": str(e)}
            raise
    
    def _generate_final_report(self) -> None:
        """Generate comprehensive final report."""
        logger.info("Generating final refinement report")
        
        report = self.reporter.generate_comprehensive_report(
            session_id=self.session_id,
            results=self.state["results"],
            target_path=self.target_path
        )
        
        self.state["report_path"] = str(report)
        logger.info(f"Final report saved: {report}")
    
    def get_summary(self) -> Dict[str, Any]:
        """Get summary of refinement results."""
        return {
            "session_id": self.session_id,
            "target": str(self.target_path),
            "phases_completed": len(self.state["phases_completed"]),
            "status": self.state.get("status", "in_progress"),
            "report": self.state.get("report_path"),
            "improvements": self._calculate_improvements()
        }
    
    def _calculate_improvements(self) -> Dict[str, Any]:
        """Calculate overall improvement metrics."""
        results = self.state["results"]
        
        # Extract before/after metrics from validation phase
        validation = results.get("ValidationMetrics", {})
        
        return {
            "quality_score_improvement": validation.get("quality_score_delta", 0),
            "issues_fixed": validation.get("issues_fixed", 0),
            "complexity_reduction": validation.get("complexity_reduction", 0),
            "duplicates_removed": results.get("DuplicateDetection", {}).get("duplicates_found", 0)
        }
