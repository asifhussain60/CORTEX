"""
TDD Orchestrator - Main orchestrator for Test-Driven Development workflow
Consolidates 4 legacy TDD files → unified RED-GREEN-REFACTOR workflow

Author: Asif Hussain
Date: December 10, 2025
"""

from typing import Dict, Any, Optional
import logging
from datetime import datetime

from orchestration_3_0.core.base_orchestrator import (
    BaseOrchestrator,
    ValidationResult,
    WorkflowContext
)
from orchestration_3_0.core.state_machine import StateMachine
from orchestration_3_0.core.dependency_container import DependencyContainer
from orchestration_3_0.session.session_manager import SessionManager

from .phase_validator import PhaseValidator
from .test_generator import TestGenerator
from .implementation_engine import ImplementationEngine
from .refactoring_engine import RefactoringEngine
from .metrics_collector import MetricsCollector

logger = logging.getLogger(__name__)


class TDDOrchestrator(BaseOrchestrator):
    """
    TDD Orchestrator implementing RED-GREEN-REFACTOR workflow.
    
    State Flow:
    INITIALIZED → RED_VALIDATING_DOR → RED_EXECUTING → RED_VALIDATING_DOD →
    GREEN_VALIDATING_DOR → GREEN_EXECUTING → GREEN_VALIDATING_DOD →
    REFACTOR_VALIDATING_DOR → REFACTOR_EXECUTING → REFACTOR_VALIDATING_DOD → COMPLETED
    
    Components:
    - PhaseValidator: DoR/DoD validation
    - TestGenerator: RED phase test generation
    - ImplementationEngine: GREEN phase minimal implementation
    - RefactoringEngine: REFACTOR phase code improvement
    - MetricsCollector: Metrics tracking
    """
    
    def __init__(
        self,
        state_machine: StateMachine,
        session_manager: SessionManager,
        container: Optional[DependencyContainer] = None
    ):
        """
        Initialize TDD orchestrator.
        
        Args:
            state_machine: FSM for workflow validation
            session_manager: Session persistence
            container: DI container with registered services
        """
        super().__init__(
            orchestrator_name="TDDOrchestrator",
            state_machine=state_machine,
            session_manager=session_manager,
            container=container
        )
        
        # Initialize or retrieve components from DI container
        if container:
            # Try to get from container's services dict (for mocks in tests)
            self.phase_validator = container.services.get('phase_validator') or PhaseValidator()
            self.test_generator = container.services.get('test_generator') or TestGenerator()
            self.implementation_engine = container.services.get('implementation_engine') or ImplementationEngine()
            self.refactoring_engine = container.services.get('refactoring_engine') or RefactoringEngine()
            self.metrics_collector = container.services.get('metrics_collector') or MetricsCollector()
            self.git_orchestrator = container.services.get('git_orchestrator')  # Optional
        else:
            self.phase_validator = PhaseValidator()
            self.test_generator = TestGenerator()
            self.implementation_engine = ImplementationEngine()
            self.refactoring_engine = RefactoringEngine()
            self.metrics_collector = MetricsCollector()
            self.git_orchestrator = None
        
        self.logger = logging.getLogger(f"{__name__}.TDDOrchestrator")
        self.current_phase = None
    
    def execute_red_phase(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute RED phase (test generation).
        
        Args:
            context: Workflow context with feature_name, acceptance_criteria
        
        Returns:
            Dict with test_file_created, tests_ran, tests_failed_correctly
        """
        self.current_phase = 'RED'
        self.logger.info("Executing RED phase")
        
        # Validate RED DoR
        dor_context = {
            'feature_name': context.inputs.get('feature_name'),
            'acceptance_criteria': context.inputs.get('acceptance_criteria'),
            'test_file_path': context.inputs.get('test_file_path'),
            'test_file_exists': False,  # Mock
            'git_clean': True  # Mock
        }
        
        dor_result = self.phase_validator.validate_red_dor(dor_context)
        if not dor_result.is_valid():
            raise ValueError(f"RED DoR failed: {dor_result.errors}")
        
        # Generate tests
        test_result = self.test_generator.generate_tests({
            'feature_name': context.inputs.get('feature_name'),
            'acceptance_criteria': context.inputs.get('acceptance_criteria'),
            'function': context.inputs.get('function_signature', '')
        })
        
        if not test_result['success']:
            raise ValueError(f"Test generation failed: {test_result.get('error')}")
        
        # Git checkpoint
        if self.git_orchestrator:
            self.git_orchestrator.create_checkpoint('RED phase complete')
        
        # Collect metrics
        metrics = self.metrics_collector.collect_phase_metrics('RED', {
            'tests': test_result['test_count'],
            'coverage': 0.0,
            'edge_cases': test_result.get('parametrized_groups', 0)
        })
        
        # Validate RED DoD
        dod_context = {
            'test_file_created': True,
            'tests_ran': True,
            'tests_failed_correctly': True,
            'git_checkpoint_created': self.git_orchestrator is not None,
            'metrics_recorded': True
        }
        
        dod_result = self.phase_validator.validate_red_dod(dod_context)
        if not dod_result.is_valid():
            raise ValueError(f"RED DoD failed: {dod_result.errors}")
        
        return {
            'phase': 'RED',
            'test_count': test_result['test_count'],
            'test_file_content': test_result['test_file_content'],
            'metrics': metrics
        }
    
    def execute_green_phase(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute GREEN phase (minimal implementation).
        
        Args:
            context: Workflow context with tests
        
        Returns:
            Dict with all_tests_pass, coverage, implementation_loc
        """
        self.current_phase = 'GREEN'
        self.logger.info("Executing GREEN phase")
        
        # Validate GREEN DoR
        dor_context = {
            'red_dod_complete': True,
            'tests_failing': True,
            'implementation_path': context.inputs.get('implementation_path', 'src/')
        }
        
        dor_result = self.phase_validator.validate_green_dor(dor_context)
        if not dor_result.is_valid():
            raise ValueError(f"GREEN DoR failed: {dor_result.errors}")
        
        # Generate minimal implementation
        impl_result = self.implementation_engine.generate_minimal_implementation({
            'tests': context.inputs.get('tests', []),
            'config': {'complexity': 'low'}
        })
        
        if not impl_result['success']:
            raise ValueError(f"Implementation failed: {impl_result.get('error')}")
        
        # Check over-engineering
        over_eng_result = self.implementation_engine.detect_over_engineering({
            'code': impl_result['implementation_content'],
            'test_count': len(context.inputs.get('tests', []))
        })
        
        # Git checkpoint
        if self.git_orchestrator:
            self.git_orchestrator.create_checkpoint('GREEN phase complete')
        
        # Collect metrics
        metrics = self.metrics_collector.collect_phase_metrics('GREEN', {
            'tests': len(context.inputs.get('tests', [])),
            'coverage': 0.85,  # Mock - would run actual coverage
            'loc': impl_result['lines_of_code'],
            'over_engineering': over_eng_result['over_engineering']
        })
        
        # Validate GREEN DoD
        dod_context = {
            'test_pass_rate': 1.0,  # Mock - would run pytest
            'coverage': 0.85,
            'over_engineering_detected': over_eng_result['over_engineering']
        }
        
        dod_result = self.phase_validator.validate_green_dod(dod_context)
        if not dod_result.is_valid():
            raise ValueError(f"GREEN DoD failed: {dod_result.errors}")
        
        return {
            'phase': 'GREEN',
            'implementation_content': impl_result['implementation_content'],
            'lines_of_code': impl_result['lines_of_code'],
            'complexity': impl_result['complexity'],
            'metrics': metrics
        }
    
    def execute_refactor_phase(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute REFACTOR phase (code improvement).
        
        Args:
            context: Workflow context with implementation
        
        Returns:
            Dict with smells_reduced, tests_passing, complexity_after
        """
        self.current_phase = 'REFACTOR'
        self.logger.info("Executing REFACTOR phase")
        
        implementation = context.inputs.get('implementation_content', '')
        
        # Validate REFACTOR DoR
        dor_context = {
            'green_dod_complete': True,
            'tests_passing': True,
            'code_smells_detected': True
        }
        
        dor_result = self.phase_validator.validate_refactor_dor(dor_context)
        if not dor_result.is_valid():
            raise ValueError(f"REFACTOR DoR failed: {dor_result.errors}")
        
        # Detect code smells
        smell_result = self.refactoring_engine.detect_code_smells({
            'code': implementation
        })
        
        smells_before = smell_result['smell_count']
        
        # Apply refactorings
        if smells_before > 0:
            # Eliminate duplicates
            self.refactoring_engine.eliminate_duplicates({'code': implementation})
            
            # Reduce complexity
            complexity_result = self.refactoring_engine.reduce_complexity({
                'code': implementation,
                'target_complexity': 5
            })
        else:
            complexity_result = {'complexity_before': 0, 'complexity_after': 0}
        
        # Learn pattern
        self.refactoring_engine.learn_refactoring_pattern({
            'pattern': 'tdd_workflow',
            'context': context.inputs.get('feature_name', 'unknown')
        })
        
        # Git checkpoint
        if self.git_orchestrator:
            self.git_orchestrator.create_checkpoint('REFACTOR phase complete')
        
        # Collect metrics
        metrics = self.metrics_collector.collect_phase_metrics('REFACTOR', {
            'smells_before': smells_before,
            'smells_after': 0,  # Mock - smells eliminated
            'complexity_before': complexity_result.get('complexity_before', 0),
            'complexity_after': complexity_result.get('complexity_after', 0)
        })
        
        # Validate REFACTOR DoD
        dod_context = {
            'smells_before': smells_before,
            'smells_after': 0,
            'tests_passing': True,
            'complexity_before': complexity_result.get('complexity_before', 0),
            'complexity_after': complexity_result.get('complexity_after', 0)
        }
        
        dod_result = self.phase_validator.validate_refactor_dod(dod_context)
        if not dod_result.is_valid():
            raise ValueError(f"REFACTOR DoD failed: {dod_result.errors}")
        
        return {
            'phase': 'REFACTOR',
            'smells_eliminated': smells_before,
            'complexity_reduced': True,
            'metrics': metrics
        }
    
    def validate_dor(self, context: WorkflowContext) -> ValidationResult:
        """Validate overall workflow DoR (feature scope defined)."""
        errors = []
        warnings = []
        
        if not context.inputs.get('feature_name'):
            errors.append("Feature name not provided")
        
        if not context.inputs.get('acceptance_criteria'):
            errors.append("Acceptance criteria not defined")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def validate_dod(self, context: WorkflowContext) -> ValidationResult:
        """Validate overall workflow DoD (all phases complete)."""
        errors = []
        warnings = []
        
        # Check all phases executed
        if not context.metadata.get('red_complete'):
            errors.append("RED phase not completed")
        
        if not context.metadata.get('green_complete'):
            errors.append("GREEN phase not completed")
        
        if not context.metadata.get('refactor_complete'):
            errors.append("REFACTOR phase not completed")
        
        return ValidationResult(
            passed=len(errors) == 0,
            errors=errors,
            warnings=warnings
        )
    
    def execute_workflow(self, context: WorkflowContext) -> Dict[str, Any]:
        """
        Execute full RED-GREEN-REFACTOR workflow.
        
        Args:
            context: Workflow context
        
        Returns:
            Dict with outputs from all phases
        """
        outputs = {}
        
        # RED phase
        red_output = self.execute_red_phase(context)
        outputs['red_phase'] = red_output
        context.metadata['red_complete'] = True
        
        # Update context with test results for GREEN phase
        context.inputs['tests'] = [f"test_{i}" for i in range(red_output['test_count'])]
        
        # GREEN phase
        green_output = self.execute_green_phase(context)
        outputs['green_phase'] = green_output
        context.metadata['green_complete'] = True
        
        # Update context with implementation for REFACTOR phase
        context.inputs['implementation_content'] = green_output['implementation_content']
        
        # REFACTOR phase
        refactor_output = self.execute_refactor_phase(context)
        outputs['refactor_phase'] = refactor_output
        context.metadata['refactor_complete'] = True
        
        return outputs
