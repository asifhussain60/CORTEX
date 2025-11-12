"""
Brain Tests Setup Module

Validates brain initialization with quick tests.

SOLID Principles:
- Single Responsibility: Only handles brain validation tests
- Open/Closed: Extends BaseOperationModule without modifying it
- Dependency Inversion: Depends on BaseOperationModule abstraction

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, Tuple, List
from datetime import datetime

from src.operations.base_operation_module import (
    BaseOperationModule,
    OperationModuleMetadata,
    OperationResult,
    OperationStatus,
    OperationPhase
)


class BrainTestsModule(BaseOperationModule):
    """
    Setup module for brain validation tests.
    
    Responsibilities:
    1. Verify Tier 0 (brain protection rules loaded)
    2. Verify Tier 1 (conversation history database)
    3. Verify Tier 2 (knowledge graph)
    4. Run quick validation queries
    5. Report brain health status
    """
    
    def get_metadata(self) -> OperationModuleMetadata:
        """Return module metadata."""
        return OperationModuleMetadata(
            module_id="brain_tests",
            name="Brain Validation Tests",
            description="Validate brain initialization with quick tests",
            phase=OperationPhase.VALIDATION,
            priority=10,
            dependencies=["brain_initialization"],
            optional=True,  # Optional validation step
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate prerequisites for brain tests.
        
        Checks:
        1. Brain initialized
        2. Brain path exists
        """
        issues = []
        
        # Check brain initialization
        brain_initialized = context.get('brain_initialized', False)
        if not brain_initialized:
            issues.append("Brain must be initialized before running tests")
            return False, issues
        
        # Check brain path
        cortex_brain_path = context.get('cortex_brain_path')
        if not cortex_brain_path or not Path(cortex_brain_path).exists():
            issues.append("Brain path not found or does not exist")
            return False, issues
        
        return True, []
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """
        Execute brain validation tests.
        
        Steps:
        1. Test Tier 0 (brain protection rules)
        2. Test Tier 1 (conversation history)
        3. Test Tier 2 (knowledge graph)
        4. Generate test summary
        """
        start_time = datetime.now()
        brain_path = Path(context['cortex_brain_path'])
        
        try:
            test_results = {
                'tier0_test': None,
                'tier1_test': None,
                'tier2_test': None,
                'overall_status': 'pending'
            }
            
            # Test Tier 0 - Brain Protection Rules
            tier0_result = self._test_tier0(brain_path)
            test_results['tier0_test'] = tier0_result
            self.log_info(f"Tier 0 test: {tier0_result['status']}")
            
            # Test Tier 1 - Conversation History
            tier1_result = self._test_tier1(brain_path)
            test_results['tier1_test'] = tier1_result
            self.log_info(f"Tier 1 test: {tier1_result['status']}")
            
            # Test Tier 2 - Knowledge Graph
            tier2_result = self._test_tier2(brain_path)
            test_results['tier2_test'] = tier2_result
            self.log_info(f"Tier 2 test: {tier2_result['status']}")
            
            # Determine overall status
            all_passed = all(
                result['status'] == 'pass' 
                for result in [tier0_result, tier1_result, tier2_result]
            )
            
            any_failed = any(
                result['status'] == 'fail' 
                for result in [tier0_result, tier1_result, tier2_result]
            )
            
            if all_passed:
                test_results['overall_status'] = 'pass'
                status = OperationStatus.SUCCESS
                message = "All brain tests passed"
            elif any_failed:
                test_results['overall_status'] = 'fail'
                status = OperationStatus.WARNING
                message = "Some brain tests failed"
            else:
                test_results['overall_status'] = 'partial'
                status = OperationStatus.WARNING
                message = "Brain tests completed with warnings"
            
            context['brain_tests_passed'] = all_passed
            context['brain_test_results'] = test_results
            
            duration_seconds = (datetime.now() - start_time).total_seconds()
            
            return OperationResult(
                success=True,
                status=status,
                message=message,
                data=test_results,
                warnings=None if all_passed else ["Some brain validation tests did not pass completely"],
                duration_seconds=duration_seconds
            )
            
        except Exception as e:
            self.log_error(f"Brain tests failed: {e}")
            return OperationResult(
                success=False,
                status=OperationStatus.FAILED,
                message=f"Brain tests failed: {str(e)}",
                errors=[str(e)],
                duration_seconds=(datetime.now() - start_time).total_seconds()
            )
    
    def _test_tier0(self, brain_path: Path) -> Dict[str, Any]:
        """Test Tier 0 - Brain Protection Rules."""
        try:
            rules_file = brain_path / "brain-protection-rules.yaml"
            if not rules_file.exists():
                return {
                    'status': 'skip',
                    'message': 'Brain protection rules file not found',
                    'file': str(rules_file)
                }
            
            # Try to load and parse YAML
            import yaml
            with open(rules_file, 'r') as f:
                rules = yaml.safe_load(f)
            
            if not rules or 'brain_protection' not in rules:
                return {
                    'status': 'fail',
                    'message': 'Invalid brain protection rules format',
                    'file': str(rules_file)
                }
            
            return {
                'status': 'pass',
                'message': 'Brain protection rules loaded successfully',
                'file': str(rules_file),
                'rule_count': len(rules.get('brain_protection', {}).get('layers', []))
            }
            
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Tier 0 test failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_tier1(self, brain_path: Path) -> Dict[str, Any]:
        """Test Tier 1 - Conversation History."""
        try:
            # Check for conversation history file
            history_file = brain_path / "conversation-history.jsonl"
            if not history_file.exists():
                return {
                    'status': 'skip',
                    'message': 'Conversation history file not found (will be created on first use)',
                    'file': str(history_file)
                }
            
            # File exists - basic validation passed
            file_size = history_file.stat().st_size
            
            return {
                'status': 'pass',
                'message': 'Conversation history file exists',
                'file': str(history_file),
                'size_bytes': file_size
            }
            
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Tier 1 test failed: {str(e)}',
                'error': str(e)
            }
    
    def _test_tier2(self, brain_path: Path) -> Dict[str, Any]:
        """Test Tier 2 - Knowledge Graph."""
        try:
            kg_file = brain_path / "knowledge-graph.yaml"
            if not kg_file.exists():
                return {
                    'status': 'skip',
                    'message': 'Knowledge graph file not found (will be created on first use)',
                    'file': str(kg_file)
                }
            
            # Try to load and parse YAML
            import yaml
            with open(kg_file, 'r') as f:
                kg = yaml.safe_load(f)
            
            if not kg:
                return {
                    'status': 'pass',
                    'message': 'Knowledge graph file exists (empty)',
                    'file': str(kg_file)
                }
            
            return {
                'status': 'pass',
                'message': 'Knowledge graph loaded successfully',
                'file': str(kg_file),
                'pattern_count': len(kg.get('patterns', []))
            }
            
        except Exception as e:
            return {
                'status': 'fail',
                'message': f'Tier 2 test failed: {str(e)}',
                'error': str(e)
            }
