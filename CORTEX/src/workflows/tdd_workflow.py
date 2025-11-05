"""
TDD Workflow Orchestrator

Orchestrates RED → GREEN → REFACTOR TDD cycle (Rule #5):
- RED: Create failing test
- GREEN: Minimum implementation to pass
- REFACTOR: Improve code while keeping tests green

Author: CORTEX Development Team
Version: 1.0
"""

from typing import Dict, Any, List
from cortex_agents.base_agent import AgentMessage
from cortex_agents.tactical.test_generator import TestGenerator
from cortex_agents.tactical.code_executor import CodeExecutor
from cortex_agents.tactical.health_validator import HealthValidator


class TDDWorkflow:
    """
    TDD Workflow Orchestrator (Rule #5)
    
    Orchestrates RED → GREEN → REFACTOR cycle
    
    Phases:
    1. RED: Create failing test
    2. GREEN: Minimum implementation to pass
    3. REFACTOR: Improve code while keeping tests green
    
    Rule #5 Compliance:
    - Tests MUST be written first (no implementation without tests)
    - Tests MUST fail initially (RED phase validation)
    - Implementation MUST make tests pass (GREEN phase validation)
    - Refactoring MUST keep tests passing (REFACTOR phase validation)
    - DoD MUST be validated (Rule #21)
    """
    
    def __init__(self, orchestrator):
        """
        Initialize TDD workflow
        
        Args:
            orchestrator: Agent orchestrator for message routing
        """
        self.orchestrator = orchestrator
        self.test_gen = TestGenerator()
        self.code_exec = CodeExecutor()
        self.validator = HealthValidator()
    
    def execute(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute TDD cycle for a task
        
        Args:
            task: {
                'name': 'feature_name',
                'description': 'feature description',
                'files': ['path/to/file.py', ...] (optional)
            }
            context: Injected context from router (Tiers 1-3)
        
        Returns:
            {
                'status': 'success',
                'cycle': 'RED → GREEN → REFACTOR',
                'phases': [
                    {'phase': 'RED', 'status': 'RED', ...},
                    {'phase': 'GREEN', 'status': 'GREEN', ...},
                    {'phase': 'REFACTOR', 'status': 'REFACTORED', ...}
                ],
                'files_modified': [...],
                'tests_created': [...],
                'tests_passing': True,
                'dod_validated': True
            }
        """
        results = {
            'status': 'in_progress',
            'cycle': 'RED → GREEN → REFACTOR',
            'phases': []
        }
        
        # PHASE 1: RED - Create failing test
        try:
            red_result = self._red_phase(task, context)
            results['phases'].append(red_result)
            
            if red_result['status'] != 'RED':
                raise ValueError(
                    f"RED phase failed: Test must fail initially. "
                    f"Status: {red_result['status']}"
                )
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = f"RED phase error: {str(e)}"
            return results
        
        # PHASE 2: GREEN - Minimum implementation
        try:
            green_result = self._green_phase(task, red_result['test_file'], context)
            results['phases'].append(green_result)
            
            if green_result['status'] != 'GREEN':
                raise ValueError(
                    f"GREEN phase failed: Tests not passing. "
                    f"Status: {green_result['status']}"
                )
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = f"GREEN phase error: {str(e)}"
            return results
        
        # PHASE 3: REFACTOR - Improve code while keeping tests green
        try:
            refactor_result = self._refactor_phase(
                green_result['files'], 
                red_result['test_file'],
                context
            )
            results['phases'].append(refactor_result)
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = f"REFACTOR phase error: {str(e)}"
            return results
        
        # Validate Definition of Done (Rule #21)
        try:
            dod_result = self._validate_dod(refactor_result['files'])
            results['dod_validated'] = dod_result['passed']
            
            if not dod_result['passed']:
                results['status'] = 'failed'
                results['error'] = f"DoD validation failed: {dod_result['failures']}"
                return results
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = f"DoD validation error: {str(e)}"
            return results
        
        # Success!
        results['status'] = 'success'
        results['files_modified'] = refactor_result['files']
        results['tests_created'] = [red_result['test_file']]
        results['tests_passing'] = True
        
        return results
    
    def _red_phase(self, task: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """
        RED phase: Create failing test
        
        Args:
            task: Task description
            context: Injected context
        
        Returns:
            {
                'phase': 'RED',
                'status': 'RED',
                'test_file': 'path/to/test.py',
                'test_name': 'test_feature'
            }
        """
        # Use test-generator agent (Phase 4: Tactical)
        message = AgentMessage(
            from_agent='tdd-workflow',
            to_agent='test-generator',
            command='create_test',
            payload={
                'task': task,
                'context': context,
                'expect_failure': True  # RED phase requirement
            }
        )
        
        result = self.orchestrator.route_message(message)
        
        # Verify test fails (Rule #5 requirement)
        if result.get('test_status') != 'FAILED':
            raise ValueError(
                f"RED phase violation: Test must fail initially. "
                f"Status: {result.get('test_status')}"
            )
        
        return {
            'phase': 'RED',
            'status': 'RED',
            'test_file': result['test_file'],
            'test_name': result['test_name'],
            'test_output': result.get('test_output', '')
        }
    
    def _green_phase(self, 
                     task: Dict[str, Any], 
                     test_file: str,
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        GREEN phase: Minimum implementation to pass test
        
        Args:
            task: Task description
            test_file: Path to test file created in RED phase
            context: Injected context
        
        Returns:
            {
                'phase': 'GREEN',
                'status': 'GREEN',
                'files': ['path/to/impl.py', ...],
                'tests_passing': True
            }
        """
        # Use code-executor agent (Phase 4: Tactical)
        message = AgentMessage(
            from_agent='tdd-workflow',
            to_agent='code-executor',
            command='execute_task',
            payload={
                'task': task,
                'test_file': test_file,
                'context': context,
                'mode': 'minimum_implementation'  # GREEN phase: minimum code
            }
        )
        
        result = self.orchestrator.route_message(message)
        
        # Verify tests pass (Rule #5 requirement)
        if not result.get('tests_passing'):
            raise ValueError(
                f"GREEN phase violation: Tests must pass. "
                f"Test output: {result.get('test_output', '')}"
            )
        
        return {
            'phase': 'GREEN',
            'status': 'GREEN',
            'files': result['files_modified'],
            'tests_passing': True,
            'test_output': result.get('test_output', '')
        }
    
    def _refactor_phase(self, 
                       files: List[str], 
                       test_file: str,
                       context: Dict[str, Any]) -> Dict[str, Any]:
        """
        REFACTOR phase: Improve code while keeping tests green
        
        Args:
            files: Files modified in GREEN phase
            test_file: Test file to keep passing
            context: Injected context
        
        Returns:
            {
                'phase': 'REFACTOR',
                'status': 'REFACTORED',
                'files': ['path/to/impl.py', ...],
                'improvements': ['Extracted method', ...]
            }
        """
        # Use code-executor agent in refactor mode
        message = AgentMessage(
            from_agent='tdd-workflow',
            to_agent='code-executor',
            command='refactor',
            payload={
                'files': files,
                'test_file': test_file,
                'context': context
            }
        )
        
        result = self.orchestrator.route_message(message)
        
        # Verify tests still pass after refactor (Rule #5 requirement)
        if not result.get('tests_passing'):
            raise ValueError(
                f"REFACTOR phase violation: Tests must remain passing. "
                f"Test output: {result.get('test_output', '')}"
            )
        
        return {
            'phase': 'REFACTOR',
            'status': 'REFACTORED',
            'files': result['files_modified'],
            'improvements': result.get('improvements', []),
            'tests_passing': True
        }
    
    def _validate_dod(self, files: List[str]) -> Dict[str, Any]:
        """
        Validate Definition of Done (Rule #21)
        
        Args:
            files: Files to validate
        
        Returns:
            {
                'passed': True,
                'checks': {
                    'build': True,
                    'tests': True,
                    'errors': 0,
                    'warnings': 0
                },
                'failures': []
            }
        """
        # Use health-validator agent (Phase 4: Tactical)
        message = AgentMessage(
            from_agent='tdd-workflow',
            to_agent='health-validator',
            command='validate_dod',
            payload={'files': files}
        )
        
        result = self.orchestrator.route_message(message)
        
        return {
            'passed': result.get('passed', False),
            'checks': result.get('checks', {}),
            'failures': result.get('failures', [])
        }
