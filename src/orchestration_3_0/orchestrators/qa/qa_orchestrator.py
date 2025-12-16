"""
QA Orchestrator - CORTEX 4.0

Unified quality assurance with code reviews, security scanning, performance analysis, and architecture review.

Consolidates:
- code_review_orchestrator.py (257 LOC)
- review.py (292 LOC)

Total: 549 LOC → 800 LOC (46% expansion with new features)

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

from ...core.base_orchestrator import (
    BaseOrchestrator,
    ValidationResult,
    WorkflowContext,
    OrchestratorResult
)
from ...core.state_machine import StateMachine, OrchestratorStates
from ...core.dependency_container import DependencyContainer
from ...session.session_manager import SessionManager

from .code_review_engine import CodeReviewEngine, ReviewDepth
from .security_scanner import SecurityScanner
from .performance_analyzer import PerformanceAnalyzer
from .architecture_reviewer import ArchitectureReviewer

# Import batch path hardening
import sys
from pathlib import Path
from src.utils.resource_resolver import get_root_path
scripts_path = get_root_path() / "scripts"
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

from batch_path_hardening import PathHardeningOrchestrator, BatchResult

logger = logging.getLogger(__name__)


class QAOrchestrator(BaseOrchestrator):
    """
    Unified QA orchestrator for CORTEX 4.0.
    
    Provides comprehensive quality assurance:
    - Code review (QUICK/STANDARD/DEEP)
    - Security scanning (OWASP Top 10)
    - Performance analysis (bottleneck detection)
    - Architecture review (SOLID principles)
    
    State Machine Flow:
    INITIALIZED → CODE_REVIEW → SECURITY_SCAN → PERFORMANCE_ANALYSIS → ARCHITECTURE_REVIEW → COMPLETED
    """
    
    def __init__(
        self,
        state_machine: StateMachine,
        session_manager: SessionManager,
        container: Optional[DependencyContainer] = None
    ):
        """
        Initialize QA orchestrator.
        
        Args:
            state_machine: FSM for workflow validation
            session_manager: Session persistence manager
            container: Optional DI container
        """
        super().__init__(
            orchestrator_name="QAOrchestrator",
            state_machine=state_machine,
            session_manager=session_manager,
            container=container
        )
        
        # Initialize components
        self.code_review_engine = CodeReviewEngine()
        self.security_scanner = SecurityScanner()
        self.performance_analyzer = PerformanceAnalyzer()
        self.architecture_reviewer = ArchitectureReviewer()
        self.path_hardening_orchestrator = PathHardeningOrchestrator()
        
        logger.info("QAOrchestrator initialized with 5 components (includes path hardening)")
    
    def validate_dor(self, context: WorkflowContext) -> ValidationResult:
        """
        Validate Definition of Ready (DoR).
        
        Prerequisites:
        - Files to review specified
        - Analysis depth selected (QUICK/STANDARD/DEEP)
        - Project path exists
        
        Args:
            context: Workflow context
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check files specified
        files = context.inputs.get('files', [])
        if not files:
            errors.append("No files specified for review")
        
        # Check depth
        depth = context.inputs.get('depth', 'STANDARD')
        if depth not in ['QUICK', 'STANDARD', 'DEEP']:
            errors.append(f"Invalid depth: {depth} (must be QUICK/STANDARD/DEEP)")
        
        # Check project path
        project_path = context.inputs.get('project_path', '.')
        from pathlib import Path
        if not Path(project_path).exists():
            errors.append(f"Project path not found: {project_path}")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_dod(self, context: WorkflowContext) -> ValidationResult:
        """
        Validate Definition of Done (DoD).
        
        Success criteria:
        - Code review complete
        - Security scan complete
        - Performance analysis complete
        - Architecture review complete
        - No CRITICAL issues (unless approved)
        
        Args:
            context: Workflow context
            
        Returns:
            ValidationResult
        """
        errors = []
        warnings = []
        
        # Check review complete
        if not context.metadata.get('review_complete'):
            errors.append("Code review not complete")
        
        # Check security scan
        if not context.metadata.get('security_scan_complete'):
            errors.append("Security scan not complete")
        
        # Check performance analysis
        if not context.metadata.get('performance_analysis_complete'):
            errors.append("Performance analysis not complete")
        
        # Check architecture review
        if not context.metadata.get('architecture_review_complete'):
            errors.append("Architecture review not complete")
        
        # Check for CRITICAL issues
        critical_issues = context.metadata.get('critical_issues', 0)
        if critical_issues > 0:
            errors.append(f"{critical_issues} CRITICAL issues found - must be resolved")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def execute_workflow(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute QA workflow.
        
        Phases:
        1. Code Review (QUICK/STANDARD/DEEP)
        2. Security Scan (OWASP Top 10)
        3. Performance Analysis (bottleneck detection)
        4. Architecture Review (SOLID principles)
        
        Args:
            context: Workflow context
            
        Returns:
            Execution outputs
        """
        files = context.inputs.get('files', [])
        depth = context.inputs.get('depth', 'STANDARD')
        project_path = context.inputs.get('project_path', '.')
        
        results = {}
        
        # Phase 1: Code Review
        logger.info(f"Starting code review ({depth})")
        review_result = self.code_review_engine.analyze_files(
            files=files,
            depth=ReviewDepth[depth],
            project_path=project_path
        )
        results['code_review'] = review_result
        context.metadata['review_complete'] = True
        
        # Phase 2: Security Scan
        logger.info("Starting security scan")
        security_result = self.security_scanner.scan_for_vulnerabilities(
            files=files,
            project_path=project_path
        )
        results['security_scan'] = security_result
        context.metadata['security_scan_complete'] = True
        
        # Phase 3: Performance Analysis
        logger.info("Starting performance analysis")
        performance_result = self.performance_analyzer.analyze_performance(
            files=files,
            project_path=project_path
        )
        results['performance_analysis'] = performance_result
        context.metadata['performance_analysis_complete'] = True
        
        # Phase 4: Architecture Review
        logger.info("Starting architecture review")
        architecture_result = self.architecture_reviewer.review_architecture(
            files=files,
            project_path=project_path
        )
        results['architecture_review'] = architecture_result
        context.metadata['architecture_review_complete'] = True
        
        # Count critical issues across all phases
        critical_issues = 0
        critical_issues += len([i for i in review_result.get('issues', []) if i.get('severity') == 'CRITICAL'])
        critical_issues += len([i for i in security_result.get('issues', []) if i.get('severity') == 'CRITICAL'])
        critical_issues += len([i for i in performance_result.get('issues', []) if i.get('severity') == 'CRITICAL'])
        critical_issues += len([i for i in architecture_result.get('issues', []) if i.get('severity') == 'CRITICAL'])
        
        context.metadata['critical_issues'] = critical_issues
        
        # Generate summary
        total_issues = sum([
            len(review_result.get('issues', [])),
            len(security_result.get('issues', [])),
            len(performance_result.get('issues', [])),
            len(architecture_result.get('issues', []))
        ])
        
        results['summary'] = {
            'total_issues': total_issues,
            'critical_issues': critical_issues,
            'files_analyzed': len(files),
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"QA complete: {total_issues} issues ({critical_issues} CRITICAL)")
        
        return results
    
    def execute_path_hardening(
        self,
        module: Optional[str] = None,
        dry_run: bool = True
    ) -> BatchResult:
        """
        Execute batch path hardening to fix hardcoded paths.
        
        This can be invoked as part of code refinement workflow or standalone.
        
        Args:
            module: Specific module to process (e.g., 'tier1', 'operations')
                   If None, processes all of src/
            dry_run: If True, only previews changes without applying
        
        Returns:
            BatchResult with operation summary
        """
        logger.info(f"🔧 Starting path hardening{' (dry run)' if dry_run else ''}...")
        
        result = self.path_hardening_orchestrator.execute(
            module=module,
            dry_run=dry_run
        )
        
        # Log summary
        logger.info(
            f"Path hardening complete: {result.replacements_made} replacements "
            f"in {result.files_processed} files"
        )
        
        if result.errors:
            logger.warning(f"{len(result.errors)} errors encountered")
            for error in result.errors:
                logger.error(f"  - {error}")
        
        return result
    
    def generate_path_hardening_report(self, result: BatchResult) -> str:
        """
        Generate detailed report for path hardening operation.
        
        Args:
            result: BatchResult from path hardening
        
        Returns:
            Formatted markdown report
        """
        return self.path_hardening_orchestrator.generate_report(result)


def create_qa_orchestrator(
    state_machine: Optional[StateMachine] = None,
    session_manager: Optional[SessionManager] = None,
    container: Optional[DependencyContainer] = None
) -> QAOrchestrator:
    """
    Factory function to create QA orchestrator.
    
    Args:
        state_machine: Optional FSM (creates default if not provided)
        session_manager: Optional session manager (creates default if not provided)
        container: Optional DI container
        
    Returns:
        QAOrchestrator instance
    """
    from ...core.state_machine import create_basic_orchestrator_fsm
    from ...session.session_manager import get_session_manager
    
    if state_machine is None:
        state_machine = create_basic_orchestrator_fsm("QAOrchestrator")
    
    if session_manager is None:
        session_manager = get_session_manager()
    
    return QAOrchestrator(
        state_machine=state_machine,
        session_manager=session_manager,
        container=container
    )
