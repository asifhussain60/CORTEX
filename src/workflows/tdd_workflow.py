"""
TDD Workflow Orchestrator

Orchestrates RED → GREEN → REFACTOR TDD cycle (Rule #5):
- RED: Create failing test
- GREEN: Minimum implementation to pass
- REFACTOR: Improve code while keeping tests green + CLEANUP orphaned code

Author: CORTEX Development Team
Version: 1.1 - Added orphaned code cleanup (Dec 5, 2025)
"""

from typing import Dict, Any, List
from src.cortex_agents.base_agent import AgentMessage
from src.cortex_agents.test_generator import TestGenerator
from src.cortex_agents.code_executor import CodeExecutor
from src.cortex_agents.health_validator import HealthValidator
from src.workflows.refactoring_intelligence import CodeSmellDetector, RefactoringEngine
from src.workflows.orphaned_code_cleaner import OrphanedCodeCleaner


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
        Initialize TDD workflow orchestrator
        
        Args:
            orchestrator: Parent orchestrator for agent routing
        """
        self.orchestrator = orchestrator
        self.code_smell_detector = CodeSmellDetector()
        self.refactoring_engine = RefactoringEngine()
        self.code_cleaner = OrphanedCodeCleaner(backup_enabled=True)
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
        REFACTOR phase: Improve code while keeping tests green + CLEANUP orphaned code
        
        NEW (v1.1): Automatically detects and removes:
        - Dead code (functions with zero call sites)
        - Orphaned functions (old implementations after GREEN phase)
        - Duplicate function signatures
        
        Args:
            files: Files modified in GREEN phase
            test_file: Test file to keep passing
            context: Injected context
        
        Returns:
            {
                'phase': 'REFACTOR',
                'status': 'REFACTORED',
                'files': ['path/to/impl.py', ...],
                'improvements': ['Extracted method', ...],
                'cleanup_performed': True,
                'functions_removed': ['old_login', 'authenticate_v1'],
                'lines_removed': 45
            }
        """
        improvements = []
        cleanup_results = []
        
        # STEP 1: Detect code smells (including dead code, orphans, duplicates)
        for file_path in files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    source_code = f.read()
                
                # Run code smell detection
                code_smells = self.code_smell_detector.analyze_file(file_path, source_code)
                
                # STEP 2: Auto-cleanup orphaned/dead code
                cleanup_result = self.code_cleaner.clean_file(file_path, code_smells)
                cleanup_results.append(cleanup_result)
                
                if cleanup_result.success and cleanup_result.functions_removed:
                    improvements.append(
                        f"Removed {len(cleanup_result.functions_removed)} orphaned function(s): "
                        f"{', '.join(cleanup_result.functions_removed)}"
                    )
                
                # STEP 3: Generate traditional refactoring suggestions
                remaining_smells = [
                    smell for smell in code_smells
                    if smell.smell_type.value not in ('dead_code', 'duplicate_code')
                ]
                
                if remaining_smells:
                    suggestions = self.refactoring_engine.generate_suggestions(
                        remaining_smells,
                        source_code
                    )
                    
                    for suggestion in suggestions:
                        improvements.append(suggestion.description)
            
            except Exception as e:
                improvements.append(f"Warning: Could not analyze {file_path}: {e}")
        
        # STEP 4: Use code-executor agent for remaining refactoring (optional)
        message = AgentMessage(
            from_agent='tdd-workflow',
            to_agent='code-executor',
            command='refactor',
            payload={
                'files': files,
                'test_file': test_file,
                'context': context,
                'improvements_applied': improvements
            }
        )
        
        result = self.orchestrator.route_message(message)
        
        # STEP 5: Verify tests still pass after ALL changes (cleanup + refactoring)
        if not result.get('tests_passing'):
            # ROLLBACK: Restore from backups
            for cleanup_result in cleanup_results:
                if cleanup_result.backup_path:
                    self.code_cleaner.restore_from_backup(
                        cleanup_result.backup_path,
                        cleanup_result.file_path
                    )
            
            raise ValueError(
                f"REFACTOR phase violation: Tests must remain passing after cleanup. "
                f"Test output: {result.get('test_output', '')}. "
                f"All changes have been rolled back."
            )
        
        # Calculate total cleanup metrics
        total_functions_removed = sum(
            len(r.functions_removed) for r in cleanup_results if r.success
        )
        total_lines_removed = sum(
            r.lines_removed for r in cleanup_results if r.success
        )
        
        return {
            'phase': 'REFACTOR',
            'status': 'REFACTORED',
            'files': result['files_modified'],
            'improvements': improvements + result.get('improvements', []),
            'tests_passing': True,
            'cleanup_performed': total_functions_removed > 0,
            'functions_removed': total_functions_removed,
            'lines_removed': total_lines_removed,
            'cleanup_details': [
                {
                    'file': r.file_path,
                    'functions': r.functions_removed,
                    'lines': r.lines_removed
                }
                for r in cleanup_results if r.success and r.functions_removed
            ]
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
