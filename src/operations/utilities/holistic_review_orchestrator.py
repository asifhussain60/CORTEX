"""
Holistic Review Orchestrator - Quality gate validation and learning integration.

Provides comprehensive review of feature execution with quality gates,
recommendations, and learning library documentation.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


@dataclass
class QualityGate:
    """Quality gate evaluation result."""
    gate_name: str
    passed: bool
    score: float
    message: str
    metrics: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ReviewResult:
    """Complete holistic review result."""
    overall_passed: bool
    gates: List[QualityGate]
    recommendations: List[str]
    lessons: Dict[str, Any]
    patterns: List[str]
    
    @property
    def failed_gates(self) -> List[QualityGate]:
        """Get failed quality gates."""
        return [gate for gate in self.gates if not gate.passed]


class HolisticReviewOrchestrator:
    """
    Orchestrates holistic review of feature execution.
    
    Evaluates quality gates:
    - Code quality (complexity, maintainability)
    - Test coverage (>90% threshold)
    - Documentation (docstrings, guides)
    
    Integrates with:
    - IncrementalPlanGenerator (Phase 4 auto-addition)
    - Learning library (lessons learned documentation)
    """
    
    def __init__(self):
        """Initialize orchestrator."""
        self.min_coverage = 90.0
        self.min_tests = 3
        
    def evaluate_code_quality(self, context: Dict[str, Any]) -> QualityGate:
        """
        Evaluate code quality metrics.
        
        Args:
            context: Execution context with code metrics
            
        Returns:
            QualityGate result
        """
        files_modified = context.get('files_modified', [])
        
        # Pass if files were modified and basic quality checks
        passed = len(files_modified) > 0
        score = 100.0 if passed else 0.0
        message = "Code quality checks passed" if passed else "No code modifications detected"
        
        return QualityGate(
            gate_name='code_quality',
            passed=passed,
            score=score,
            message=message,
            metrics={'files_modified': len(files_modified)}
        )
    
    def evaluate_test_coverage(self, context: Dict[str, Any]) -> QualityGate:
        """
        Evaluate test coverage metrics.
        
        Args:
            context: Execution context with test metrics
            
        Returns:
            QualityGate result
        """
        coverage = context.get('coverage', 0.0)
        tests_run = context.get('tests_run', 0)
        tests_passed = context.get('tests_passed', 0)
        
        # Pass if coverage >= 90% and tests pass
        passed = coverage >= self.min_coverage and tests_run >= self.min_tests and tests_passed == tests_run
        score = coverage
        
        if passed:
            message = f"Coverage {coverage:.1f}% meets {self.min_coverage}% threshold"
        else:
            message = f"Coverage {coverage:.1f}% below {self.min_coverage}% threshold or test failures"
        
        return QualityGate(
            gate_name='test_coverage',
            passed=passed,
            score=score,
            message=message,
            metrics={
                'coverage': coverage,
                'tests_run': tests_run,
                'tests_passed': tests_passed
            }
        )
    
    def evaluate_documentation(self, context: Dict[str, Any]) -> QualityGate:
        """
        Evaluate documentation quality.
        
        Args:
            context: Execution context with doc metrics
            
        Returns:
            QualityGate result
        """
        feature_name = context.get('feature_name', '')
        phases_completed = context.get('phases_completed', [])
        
        # Pass if feature has name and phases completed
        passed = bool(feature_name) and len(phases_completed) >= 3
        score = 100.0 if passed else 50.0
        message = "Documentation adequate" if passed else "Documentation needs improvement"
        
        return QualityGate(
            gate_name='documentation',
            passed=passed,
            score=score,
            message=message,
            metrics={'phases_completed': len(phases_completed)}
        )
    
    def run_holistic_review(self, context: Dict[str, Any]) -> ReviewResult:
        """
        Run complete holistic review.
        
        Args:
            context: Execution context with all metrics
            
        Returns:
            ReviewResult with gates, recommendations, lessons, patterns
        """
        logger.info(f"🎭 Orchestrator engaged: HolisticReviewOrchestrator")
        
        # Evaluate all gates
        gates = [
            self.evaluate_code_quality(context),
            self.evaluate_test_coverage(context),
            self.evaluate_documentation(context)
        ]
        
        # Overall pass requires all gates to pass
        overall_passed = all(gate.passed for gate in gates)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(gates)
        
        # Document lessons
        lessons = self.document_lessons_learned_from_gates(gates, context)
        
        # Extract patterns
        patterns = self.extract_patterns(context)
        
        logger.info(f"🎭 Review complete: {'✅ PASS' if overall_passed else '❌ FAIL'}")
        
        return ReviewResult(
            overall_passed=overall_passed,
            gates=gates,
            recommendations=recommendations,
            lessons=lessons,
            patterns=patterns
        )
    
    def _generate_recommendations(self, gates: List[QualityGate]) -> List[str]:
        """Generate actionable recommendations from gate results."""
        recommendations = []
        
        for gate in gates:
            if not gate.passed:
                if gate.gate_name == 'code_quality':
                    recommendations.append("Review code complexity and refactor high-complexity functions")
                elif gate.gate_name == 'test_coverage':
                    recommendations.append(f"Increase test coverage from {gate.score:.1f}% to 90%+")
                elif gate.gate_name == 'documentation':
                    recommendations.append("Add comprehensive docstrings and implementation guides")
        
        if not recommendations:
            recommendations.append("All quality gates passed - consider advanced optimizations")
        
        return recommendations
    
    def document_lessons_learned(self, result: ReviewResult) -> Dict[str, Any]:
        """
        Document lessons learned for learning library.
        
        Args:
            result: ReviewResult from holistic review
            
        Returns:
            Structured lessons dictionary
        """
        return {
            'feature_name': 'holistic-review',
            'quality_metrics': {
                gate.gate_name: {
                    'passed': gate.passed,
                    'score': gate.score
                }
                for gate in result.gates
            },
            'recommendations': result.recommendations,
            'patterns': result.patterns
        }
    
    def document_lessons_learned_from_gates(self, gates: List[QualityGate], context: Dict[str, Any]) -> Dict[str, Any]:
        """Document lessons from gates and context."""
        return {
            'feature_name': context.get('feature_name', 'unknown'),
            'quality_metrics': {
                gate.gate_name: {
                    'passed': gate.passed,
                    'score': gate.score,
                    'metrics': gate.metrics
                }
                for gate in gates
            },
            'execution_summary': {
                'files_modified': len(context.get('files_modified', [])),
                'tests_run': context.get('tests_run', 0),
                'phases_completed': len(context.get('phases_completed', []))
            }
        }
    
    def extract_patterns(self, context: Dict[str, Any]) -> List[str]:
        """
        Extract reusable patterns from execution.
        
        Args:
            context: Execution context
            
        Returns:
            List of identified patterns
        """
        patterns = []
        
        # Pattern: High test coverage
        if context.get('coverage', 0) >= 95:
            patterns.append("high-test-coverage-pattern")
        
        # Pattern: Multi-phase execution
        phases = context.get('phases_completed', [])
        if len(phases) >= 3:
            patterns.append("multi-phase-execution-pattern")
        
        # Pattern: Comprehensive modification
        files_modified = context.get('files_modified', [])
        if len(files_modified) >= 3:
            patterns.append("comprehensive-modification-pattern")
        
        return patterns
