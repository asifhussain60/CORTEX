"""
Workflow Templates — Phase 45 Stage 3.

Pre-defined workflow templates for common CORTEX operations.

AC_START: AC-PHASE45-S3-003
Phase: 45 | Stage: 3 | Priority: P0
Description: GREEN phase implementation for workflow templates
Requirements: CORE-008 (TDD), CORE-011 (type hints), CORE-012 (docstrings)
"""

import logging
from typing import Dict, List, Any


logger = logging.getLogger(__name__)


# =============================================================================
# TEMPLATE: Phase Execution
# =============================================================================
PHASE_EXECUTION_TEMPLATE = {
    "name": "phase-execution",
    "description": "Execute a CORTEX phase with TDD methodology",
    "variables": {
        "phase_number": "Phase number to execute",
        "phase_name": "Phase name",
        "stage_count": "Number of stages in phase",
    },
    "steps": [
        {
            "name": "Load Phase Specification",
            "action": "read_phase_spec",
            "params": {
                "phase_number": "{{phase_number}}",
            },
        },
        {
            "name": "Initialize Phase Context",
            "action": "init_context",
            "params": {
                "phase_name": "{{phase_name}}",
                "stage_count": "{{stage_count}}",
            },
        },
        {
            "name": "Execute All Stages",
            "action": "execute_stages",
            "params": {
                "stages": "{{stage_count}}",
            },
        },
        {
            "name": "Validate Phase Completion",
            "action": "validate_completion",
            "params": {
                "phase_number": "{{phase_number}}",
            },
        },
        {
            "name": "Update Registry",
            "action": "update_registry",
            "params": {
                "phase_number": "{{phase_number}}",
                "status": "completed",
            },
        },
    ],
}


# =============================================================================
# TEMPLATE: TDD Cycle
# =============================================================================
TDD_CYCLE_TEMPLATE = {
    "name": "tdd-cycle",
    "description": "Execute TDD cycle: RED → GREEN → REFACTOR",
    "variables": {
        "module_name": "Module being developed",
        "test_file": "Test file path",
        "impl_file": "Implementation file path",
    },
    "steps": [
        {
            "name": "RED: Write Failing Tests",
            "action": "write_tests",
            "params": {
                "test_file": "{{test_file}}",
                "module_name": "{{module_name}}",
            },
        },
        {
            "name": "RED: Run Tests (Expect Failures)",
            "action": "run_tests",
            "params": {
                "test_file": "{{test_file}}",
                "expect_failures": True,
            },
        },
        {
            "name": "GREEN: Implement Minimal Solution",
            "action": "implement_solution",
            "params": {
                "impl_file": "{{impl_file}}",
                "module_name": "{{module_name}}",
            },
        },
        {
            "name": "GREEN: Run Tests (Expect Success)",
            "action": "run_tests",
            "params": {
                "test_file": "{{test_file}}",
                "expect_failures": False,
            },
        },
        {
            "name": "REFACTOR: Optimize Implementation",
            "action": "refactor_code",
            "params": {
                "impl_file": "{{impl_file}}",
            },
        },
        {
            "name": "REFACTOR: Verify Tests Still Pass",
            "action": "run_tests",
            "params": {
                "test_file": "{{test_file}}",
                "expect_failures": False,
            },
        },
    ],
}


# =============================================================================
# TEMPLATE: Holistic Refactoring
# =============================================================================
REFACTOR_HOLISTIC_TEMPLATE = {
    "name": "refactor-holistic",
    "description": "Holistic refactoring with semantic analysis",
    "variables": {
        "target_files": "Files to refactor",
        "refactor_operation": "Refactoring operation (extract, rename, etc.)",
    },
    "steps": [
        {
            "name": "Analyze Code Structure",
            "action": "semantic_analyze",
            "params": {
                "target_files": "{{target_files}}",
            },
        },
        {
            "name": "Generate Refactoring Plan",
            "action": "generate_refactor_plan",
            "params": {
                "operation": "{{refactor_operation}}",
                "files": "{{target_files}}",
            },
        },
        {
            "name": "Execute Refactoring",
            "action": "execute_refactor",
            "params": {
                "plan": "{{refactor_plan}}",
            },
        },
        {
            "name": "Run Tests",
            "action": "run_tests",
            "params": {
                "all_tests": True,
            },
        },
        {
            "name": "Validate Semantics Preserved",
            "action": "validate_semantics",
            "params": {
                "original_files": "{{target_files}}",
            },
        },
    ],
}


# =============================================================================
# TEMPLATE MANAGER
# =============================================================================
class WorkflowTemplateManager:
    """Manages workflow templates.
    
    Provides access to pre-defined workflow templates for common operations.
    
    Example:
        >>> manager = WorkflowTemplateManager()
        >>> template = manager.get_template("tdd-cycle")
        >>> print(template["name"])
        tdd-cycle
    """
    
    def __init__(self):
        """Initialize template manager."""
        self._templates: Dict[str, Dict[str, Any]] = {
            "phase-execution": PHASE_EXECUTION_TEMPLATE,
            "tdd-cycle": TDD_CYCLE_TEMPLATE,
            "refactor-holistic": REFACTOR_HOLISTIC_TEMPLATE,
        }
    
    def get_template(self, name: str) -> Dict[str, Any]:
        """Get workflow template by name.
        
        Args:
            name: Template name.
        
        Returns:
            Template dictionary.
        
        Raises:
            KeyError: If template does not exist.
        """
        if name not in self._templates:
            raise KeyError(f"Template not found: {name}")
        
        logger.debug(f"Retrieved template: {name}")
        return self._templates[name]
    
    def list_templates(self) -> List[str]:
        """List all available template names.
        
        Returns:
            List of template names.
        """
        return list(self._templates.keys())
    
    def register_template(self, name: str, template: Dict[str, Any]) -> None:
        """Register custom workflow template.
        
        Args:
            name: Template name.
            template: Template dictionary.
        """
        self._templates[name] = template
        logger.info(f"Registered custom template: {name}")


# =============================================================================
# AC_COMPLETE: AC-PHASE45-S3-003 (GREEN phase implementation)
# =============================================================================
