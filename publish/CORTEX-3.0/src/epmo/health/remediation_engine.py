"""
CORTEX 3.0 - Remediation Engine
===============================

Guided remediation system for EPMO health issues.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass

from .validation_suite import ValidationResult, ValidationSeverity, HealthDimension
from .auto_fix import AutoFixEngine


@dataclass
class RemediationAction:
    """Represents a remediation action for a health issue."""
    action_type: str
    description: str
    auto_fixable: bool
    estimated_effort_minutes: int
    priority: int  # 1 = high, 2 = medium, 3 = low
    metadata: Dict[str, Any]


class RemediationEngine:
    """Guided remediation system for EPMO health issues."""
    
    def __init__(self):
        self.auto_fix_engine = AutoFixEngine()
        
        # Remediation templates by dimension
        self.remediation_templates = {
            HealthDimension.CODE_QUALITY: {
                'high_complexity': RemediationAction(
                    'refactor_complex_function',
                    'Refactor overly complex function to improve readability',
                    False,
                    60,
                    1,
                    {'technique': 'extract_method', 'target_complexity': 10}
                ),
                'large_file': RemediationAction(
                    'split_large_file',
                    'Split large file into smaller, focused modules',
                    False,
                    120,
                    2,
                    {'technique': 'module_extraction', 'target_size_lines': 300}
                ),
                'poor_naming': RemediationAction(
                    'improve_naming',
                    'Improve variable and function naming for clarity',
                    True,
                    30,
                    2,
                    {'auto_fix_type': 'standardize_naming'}
                )
            },
            HealthDimension.DOCUMENTATION: {
                'missing_docstrings': RemediationAction(
                    'add_documentation',
                    'Add comprehensive docstrings to functions and classes',
                    True,
                    45,
                    2,
                    {'auto_fix_type': 'add_missing_docstrings'}
                ),
                'outdated_docs': RemediationAction(
                    'update_documentation',
                    'Update documentation to match current implementation',
                    False,
                    90,
                    1,
                    {'technique': 'manual_review'}
                )
            },
            HealthDimension.TEST_COVERAGE: {
                'low_coverage': RemediationAction(
                    'add_tests',
                    'Add comprehensive test coverage for uncovered code',
                    True,
                    180,
                    1,
                    {'auto_fix_type': 'generate_missing_tests', 'target_coverage': 80}
                ),
                'missing_edge_cases': RemediationAction(
                    'add_edge_case_tests',
                    'Add tests for edge cases and error conditions',
                    False,
                    120,
                    2,
                    {'technique': 'boundary_testing'}
                )
            },
            HealthDimension.PERFORMANCE: {
                'large_files': RemediationAction(
                    'optimize_file_size',
                    'Optimize large files for better performance',
                    False,
                    90,
                    2,
                    {'technique': 'code_optimization'}
                ),
                'inefficient_algorithms': RemediationAction(
                    'optimize_algorithms',
                    'Optimize algorithms for better time complexity',
                    False,
                    240,
                    1,
                    {'technique': 'algorithm_analysis'}
                )
            },
            HealthDimension.ARCHITECTURE: {
                'srp_violation': RemediationAction(
                    'apply_srp',
                    'Apply Single Responsibility Principle to classes',
                    False,
                    180,
                    1,
                    {'technique': 'class_extraction'}
                ),
                'poor_separation': RemediationAction(
                    'improve_separation',
                    'Improve separation of concerns in module structure',
                    False,
                    300,
                    1,
                    {'technique': 'architectural_refactoring'}
                )
            },
            HealthDimension.MAINTAINABILITY: {
                'code_duplication': RemediationAction(
                    'remove_duplication',
                    'Extract common code to reduce duplication',
                    False,
                    120,
                    2,
                    {'technique': 'extract_common_code'}
                ),
                'inconsistent_error_handling': RemediationAction(
                    'standardize_error_handling',
                    'Standardize error handling patterns across codebase',
                    True,
                    90,
                    1,
                    {'auto_fix_type': 'add_error_handling'}
                )
            }
        }
    
    def generate_remediation_plan(self, validation_results: List[ValidationResult]) -> List[RemediationAction]:
        """Generate a comprehensive remediation plan from validation results."""
        actions = []
        
        for result in validation_results:
            if result.severity in [ValidationSeverity.MEDIUM, ValidationSeverity.HIGH]:
                action = self._create_remediation_action(result)
                if action:
                    actions.append(action)
        
        # Sort by priority (high priority first) and estimated effort
        actions.sort(key=lambda a: (a.priority, a.estimated_effort_minutes))
        
        return actions
    
    def execute_remediation(self, action: RemediationAction, file_path: Path) -> Tuple[bool, str]:
        """Execute a remediation action."""
        if action.auto_fixable:
            # Try auto-fix first
            result = self._try_auto_fix(action, file_path)
            if result:
                return True, f"Auto-fix applied successfully: {action.description}"
            else:
                return False, f"Auto-fix failed for: {action.description}"
        else:
            # Provide manual guidance
            guidance = self._get_manual_guidance(action)
            return True, f"Manual remediation guidance: {guidance}"
    
    def estimate_total_effort(self, actions: List[RemediationAction]) -> Dict[str, Any]:
        """Estimate total effort required for remediation plan."""
        total_minutes = sum(action.estimated_effort_minutes for action in actions)
        auto_fixable_count = sum(1 for action in actions if action.auto_fixable)
        
        return {
            'total_minutes': total_minutes,
            'total_hours': total_minutes / 60,
            'total_actions': len(actions),
            'auto_fixable_actions': auto_fixable_count,
            'manual_actions': len(actions) - auto_fixable_count,
            'estimated_completion': self._estimate_completion_time(total_minutes)
        }
    
    def _create_remediation_action(self, result: ValidationResult) -> Optional[RemediationAction]:
        """Create a remediation action from a validation result."""
        dimension = result.metadata.get('dimension')
        
        if not dimension or dimension not in self.remediation_templates:
            return None
        
        # Map result check_id to remediation template
        template_key = self._map_result_to_template(result)
        template = self.remediation_templates[dimension].get(template_key)
        
        if not template:
            return self._create_generic_action(result)
        
        # Customize template with specific result data
        action = RemediationAction(
            action_type=template.action_type,
            description=f"{template.description} - {result.message}",
            auto_fixable=template.auto_fixable,
            estimated_effort_minutes=template.estimated_effort_minutes,
            priority=template.priority,
            metadata={**template.metadata, **result.metadata}
        )
        
        return action
    
    def _map_result_to_template(self, result: ValidationResult) -> str:
        """Map validation result to remediation template key."""
        check_id = result.check_id
        
        # Map common check IDs to template keys
        mapping = {
            'high_complexity_functions': 'high_complexity',
            'large_files': 'large_file',
            'poor_naming_convention': 'poor_naming',
            'missing_docstrings': 'missing_docstrings',
            'low_test_coverage': 'low_coverage',
            'single_responsibility': 'srp_violation',
            'code_duplication': 'code_duplication'
        }
        
        return mapping.get(check_id, 'generic')
    
    def _create_generic_action(self, result: ValidationResult) -> RemediationAction:
        """Create a generic remediation action for unmapped results."""
        return RemediationAction(
            action_type='generic_improvement',
            description=f"Address validation issue: {result.message}",
            auto_fixable=False,
            estimated_effort_minutes=60,
            priority=2,
            metadata=result.metadata
        )
    
    def _try_auto_fix(self, action: RemediationAction, file_path: Path) -> bool:
        """Attempt to apply auto-fix for an action."""
        # Create a mock validation result for auto-fix engine
        mock_result = ValidationResult(
            check_id=action.action_type,
            score=0.5,
            message=action.description,
            severity=ValidationSeverity.MEDIUM,
            metadata=action.metadata
        )
        
        return self.auto_fix_engine.apply_auto_fix(mock_result, file_path)
    
    def _get_manual_guidance(self, action: RemediationAction) -> str:
        """Get manual guidance for non-auto-fixable actions."""
        technique = action.metadata.get('technique', 'manual_review')
        
        guidance_map = {
            'extract_method': "Extract complex logic into smaller, focused methods",
            'module_extraction': "Split large modules by grouping related functionality",
            'manual_review': "Manually review and update the affected code",
            'boundary_testing': "Add tests for edge cases, null values, and error conditions",
            'code_optimization': "Optimize code for better performance and memory usage",
            'algorithm_analysis': "Analyze and optimize algorithm time/space complexity",
            'class_extraction': "Extract separate classes for distinct responsibilities",
            'architectural_refactoring': "Refactor to improve module boundaries and dependencies"
        }
        
        return guidance_map.get(technique, "Review and improve the code manually")
    
    def _estimate_completion_time(self, total_minutes: int) -> str:
        """Estimate human-readable completion time."""
        if total_minutes < 60:
            return f"{total_minutes} minutes"
        elif total_minutes < 480:  # 8 hours
            hours = total_minutes / 60
            return f"{hours:.1f} hours"
        else:
            days = total_minutes / (8 * 60)  # 8-hour work days
            return f"{days:.1f} days"