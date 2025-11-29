"""
Feature Creation Workflow

Orchestrates complete feature creation:
- PLAN: Multi-phase breakdown via work-planner
- EXECUTE: Implement each phase with TDD
- TEST: Validate complete feature

Author: CORTEX Development Team
Version: 1.0
"""

from typing import Dict, Any, List
from src.cortex_agents.base_agent import AgentMessage
from .tdd_workflow import TDDWorkflow


class FeatureCreationWorkflow:
    """
    Feature Creation Workflow
    
    Phases:
    1. PLAN: Multi-phase breakdown (work-planner agent)
    2. EXECUTE: Implement each phase with TDD
    3. TEST: Validate complete feature
    
    Integration:
    - Uses work-planner (Phase 4: Strategic) for planning
    - Uses TDD workflow for each phase execution
    - Uses health-validator (Phase 4: Tactical) for validation
    """
    
    def __init__(self, orchestrator):
        """
        Initialize feature creation workflow
        
        Args:
            orchestrator: Agent orchestrator for message routing
        """
        self.orchestrator = orchestrator
        self.tdd_workflow = TDDWorkflow(orchestrator)
    
    def execute(self, 
                feature_description: str, 
                context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute feature creation workflow
        
        Args:
            feature_description: User's feature request
            context: Injected context (Tiers 1-3)
        
        Returns:
            {
                'status': 'success',
                'workflow': 'feature_creation',
                'plan': {
                    'feature': 'Authentication',
                    'phases': [
                        {'phase': 1, 'name': 'User model', 'tasks': [...]},
                        {'phase': 2, 'name': 'Login API', 'tasks': [...]}
                    ],
                    'estimated_hours': 8
                },
                'phases_completed': 2,
                'files_modified': ['path/to/file.py', ...],
                'tests_created': ['path/to/test.py', ...],
                'validation': {
                    'passed': True,
                    'checks': {...}
                }
            }
        """
        results = {
            'status': 'in_progress',
            'workflow': 'feature_creation',
            'phases_completed': 0,
            'files_modified': [],
            'tests_created': []
        }
        
        # PHASE 1: PLAN - Create multi-phase breakdown
        try:
            plan = self._create_plan(feature_description, context)
            results['plan'] = plan
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = f"Planning error: {str(e)}"
            return results
        
        # PHASE 2: EXECUTE - Implement each phase with TDD
        phase_results = []
        for phase in plan['phases']:
            try:
                phase_result = self._execute_phase(phase, context)
                phase_results.append(phase_result)
                results['phases_completed'] += 1
                
                # Accumulate modified files and tests
                results['files_modified'].extend(
                    phase_result.get('files_modified', [])
                )
                results['tests_created'].extend(
                    phase_result.get('tests_created', [])
                )
            except Exception as e:
                results['status'] = 'failed'
                results['error'] = f"Phase {phase['phase']} error: {str(e)}"
                results['phase_results'] = phase_results
                return results
        
        results['phase_results'] = phase_results
        
        # PHASE 3: TEST - Validate complete feature
        try:
            validation_result = self._validate_feature(plan, results)
            results['validation'] = validation_result
            
            if not validation_result['passed']:
                results['status'] = 'failed'
                results['error'] = f"Feature validation failed: {validation_result['failures']}"
                return results
        except Exception as e:
            results['status'] = 'failed'
            results['error'] = f"Validation error: {str(e)}"
            return results
        
        # Success!
        results['status'] = 'success'
        return results
    
    def _create_plan(self, 
                     feature_description: str, 
                     context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create multi-phase plan using work-planner agent
        
        Args:
            feature_description: User's feature request
            context: Injected context (Tiers 1-3)
        
        Returns:
            {
                'feature': 'Authentication',
                'phases': [
                    {
                        'phase': 1,
                        'name': 'User model',
                        'tasks': ['Create User class', 'Add validation', ...]
                    },
                    {
                        'phase': 2,
                        'name': 'Login API',
                        'tasks': ['Create login endpoint', 'Add JWT', ...]
                    }
                ],
                'estimated_hours': 8
            }
        """
        # Use work-planner agent (Phase 4: Strategic)
        message = AgentMessage(
            from_agent='feature-workflow',
            to_agent='work-planner',
            command='create_plan',
            payload={
                'feature_description': feature_description,
                'context': context
            }
        )
        
        result = self.orchestrator.route_message(message)
        
        return {
            'feature': result.get('feature_name', feature_description),
            'phases': result.get('phases', []),
            'estimated_hours': result.get('estimated_hours', 0)
        }
    
    def _execute_phase(self, 
                      phase: Dict[str, Any], 
                      context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute single phase using TDD workflow
        
        Args:
            phase: {
                'phase': 1,
                'name': 'User model',
                'tasks': ['Create User class', 'Add validation', ...]
            }
            context: Injected context
        
        Returns:
            {
                'phase': 1,
                'name': 'User model',
                'tasks_completed': 2,
                'files_modified': ['models/user.py'],
                'tests_created': ['tests/test_user.py'],
                'tdd_results': [...]
            }
        """
        phase_result = {
            'phase': phase['phase'],
            'name': phase['name'],
            'tasks_completed': 0,
            'files_modified': [],
            'tests_created': [],
            'tdd_results': []
        }
        
        # Execute each task with TDD workflow
        for task in phase['tasks']:
            tdd_result = self.tdd_workflow.execute(
                task={
                    'name': task,
                    'description': task,
                    'phase': phase['phase']
                },
                context=context
            )
            
            phase_result['tdd_results'].append(tdd_result)
            phase_result['tasks_completed'] += 1
            
            # Accumulate files and tests
            phase_result['files_modified'].extend(
                tdd_result.get('files_modified', [])
            )
            phase_result['tests_created'].extend(
                tdd_result.get('tests_created', [])
            )
        
        return phase_result
    
    def _validate_feature(self, 
                         plan: Dict[str, Any], 
                         results: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate complete feature meets DoD
        
        Args:
            plan: Original plan
            results: Execution results
        
        Returns:
            {
                'passed': True,
                'checks': {
                    'all_phases_complete': True,
                    'all_tests_passing': True,
                    'build_successful': True,
                    'zero_errors': True,
                    'zero_warnings': True
                },
                'failures': []
            }
        """
        # Use health-validator agent (Phase 4: Tactical)
        message = AgentMessage(
            from_agent='feature-workflow',
            to_agent='health-validator',
            command='validate_feature',
            payload={
                'plan': plan,
                'results': results,
                'files': results['files_modified']
            }
        )
        
        result = self.orchestrator.route_message(message)
        
        return {
            'passed': result.get('passed', False),
            'checks': result.get('checks', {}),
            'failures': result.get('failures', [])
        }
