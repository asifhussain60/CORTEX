"""
Phase Quality Gate for Planning System 3.0

Post-execution quality gate that runs architectural review after phase completion
and blocks git checkpoints if review score falls below threshold.

Features:
- Review Orchestrator integration
- Configurable score threshold (default: 70)
- Git checkpoint blocking logic
- Review findings formatting for reports
- Optional bypass mode

Author: Asif Hussain
Version: 3.9.0
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class QualityGateResult:
    """Result of quality gate execution."""
    success: bool
    score: Optional[int]
    validation_passed: bool
    should_block_checkpoint: bool
    findings: List[Dict[str, Any]]
    bypassed: bool = False
    message: str = ""


class PhaseQualityGate:
    """
    Post-execution quality gate for planning phases.
    
    Runs Review Orchestrator after phase completion and validates
    code quality score against threshold.
    """
    
    def __init__(
        self,
        workspace_path: Path,
        threshold: int = 70,
        timeout_seconds: int = 60,
        enabled: bool = True
    ):
        """
        Initialize Phase Quality Gate.
        
        Args:
            workspace_path: Path to workspace for review
            threshold: Minimum acceptable score (default: 70)
            timeout_seconds: Maximum time for review (default: 60)
            enabled: Whether quality gate is active (default: True)
        """
        self.workspace_path = Path(workspace_path)
        self.threshold = threshold
        self.timeout_seconds = timeout_seconds
        self.enabled = enabled
        self.logger = logging.getLogger(__name__)
    
    def execute_review(self) -> Dict[str, Any]:
        """
        Execute architectural review using Review Orchestrator.
        
        Returns:
            Dictionary with success, score, and findings
        """
        if not self.enabled:
            return {
                'success': True,
                'bypassed': True,
                'score': None,
                'findings': [],
                'message': 'Quality gate disabled in configuration'
            }
        
        try:
            # Import here to avoid circular dependency
            from src.operations.modules.architectural.review_orchestrator import ReviewOrchestrator
            
            self.logger.info("🔍 Executing post-phase review...")
            
            # Create and execute review orchestrator
            reviewer = ReviewOrchestrator()
            result = reviewer.execute({'path': str(self.workspace_path)})
            
            if not result.success:
                self.logger.warning("⚠️  Review execution failed")
                return {
                    'success': False,
                    'score': None,
                    'findings': [],
                    'message': result.message or 'Review execution failed'
                }
            
            # Extract score and findings from result
            score = result.data.get('overall_score', 0)
            findings = result.data.get('findings', [])
            
            self.logger.info(f"✅ Review complete - Score: {score}/100")
            
            return {
                'success': True,
                'bypassed': False,
                'score': score,
                'findings': findings,
                'message': f'Review completed with score {score}/100'
            }
            
        except Exception as e:
            self.logger.error(f"❌ Review execution error: {e}")
            return {
                'success': False,
                'score': None,
                'findings': [],
                'message': f'Review error: {str(e)}'
            }
    
    def validate_threshold(self, score: int) -> Dict[str, Any]:
        """
        Validate score against threshold.
        
        Args:
            score: Review score (0-100)
            
        Returns:
            Dictionary with passed, score, threshold
        """
        passed = score >= self.threshold
        
        return {
            'passed': passed,
            'score': score,
            'threshold': self.threshold,
            'message': (
                f"✅ Score {score} meets threshold {self.threshold}" if passed
                else f"❌ Score {score} below threshold {self.threshold}"
            )
        }
    
    def should_block_checkpoint(self, score: int) -> bool:
        """
        Determine if git checkpoint should be blocked.
        
        Args:
            score: Review score (0-100)
            
        Returns:
            True if checkpoint should be blocked, False otherwise
        """
        return score < self.threshold
    
    def format_review_findings_for_report(self, findings: List[Dict[str, Any]]) -> str:
        """
        Format review findings for plan report.
        
        Args:
            findings: List of finding dictionaries from review
            
        Returns:
            Formatted string for report insertion
        """
        if not findings:
            return "No issues found during review."
        
        lines = ["### 🔍 Quality Gate Review Findings", ""]
        
        # Group by severity
        by_severity = {}
        for finding in findings:
            severity = finding.get('severity', 'UNKNOWN')
            if severity not in by_severity:
                by_severity[severity] = []
            by_severity[severity].append(finding)
        
        # Format by severity
        severity_order = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW']
        for severity in severity_order:
            if severity in by_severity:
                lines.append(f"#### {severity} Issues ({len(by_severity[severity])})")
                lines.append("")
                
                for finding in by_severity[severity]:
                    title = finding.get('title', 'Unknown Issue')
                    desc = finding.get('description', '')
                    location = finding.get('location', '')
                    recommendation = finding.get('recommendation', '')
                    
                    lines.append(f"**{title}**")
                    if desc:
                        lines.append(f"- {desc}")
                    if location:
                        lines.append(f"- Location: `{location}`")
                    if recommendation:
                        lines.append(f"- Recommendation: {recommendation}")
                    lines.append("")
        
        return "\n".join(lines)
    
    def execute_full_workflow(self) -> QualityGateResult:
        """
        Execute complete quality gate workflow.
        
        Steps:
        1. Execute review
        2. Validate threshold
        3. Determine checkpoint decision
        4. Return comprehensive result
        
        Returns:
            QualityGateResult with complete workflow outcome
        """
        # Step 1: Execute review
        review_result = self.execute_review()
        
        if not review_result['success']:
            return QualityGateResult(
                success=False,
                score=None,
                validation_passed=False,
                should_block_checkpoint=False,
                findings=[],
                bypassed=review_result.get('bypassed', False),
                message=review_result['message']
            )
        
        # Step 2: Validate threshold
        score = review_result['score']
        validation_result = self.validate_threshold(score)
        
        # Step 3: Determine checkpoint decision
        should_block = self.should_block_checkpoint(score)
        
        # Step 4: Comprehensive result
        return QualityGateResult(
            success=True,
            score=score,
            validation_passed=validation_result['passed'],
            should_block_checkpoint=should_block,
            findings=review_result['findings'],
            bypassed=review_result.get('bypassed', False),
            message=validation_result['message']
        )
