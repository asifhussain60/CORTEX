"""
CORTEX 4.0 Plan Validator - YAML Schema Validation

Purpose: Validate plans against YAML schema with comprehensive error reporting
Version: 4.0.0
Author: CORTEX Development Team
Migrated: 2025-12-19 (from legacy planning_orchestrator.py)

Key Features:
- YAML schema validation
- Metadata validation (plan_id, title, status, priority, etc.)
- Phase validation (sequential phase numbers, required fields)
- Task validation (unique task IDs, estimated hours)
- Risk validation (likelihood, impact, mitigation)
- DoR/DoD validation (minimum requirements)
- Integration with ValidationFramework (Week 9)

Deferred to Week 9:
- ValidationFramework integration for multi-layer validation
- Manifest compliance validation
- Advanced cross-field validation

Architecture:
- Standalone validator module
- Callable from PlanningOrchestrator
- Returns ValidationResult with errors/warnings
"""

import re
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple
import yaml

logger = logging.getLogger(__name__)


# ============================================================================
# Validation Result Models
# ============================================================================

@dataclass
class ValidationResult:
    """Result of plan validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    validation_type: str = "schema_validation"
    timestamp: datetime = field(default_factory=datetime.now)
    
    def add_error(self, error: str) -> None:
        """Add validation error."""
        self.errors.append(error)
        self.valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add validation warning."""
        self.warnings.append(warning)
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.errors) > 0
    
    @property
    def has_warnings(self) -> bool:
        """Check if validation has warnings."""
        return len(self.warnings) > 0
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result into this one."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        if not other.valid:
            self.valid = False


# ============================================================================
# Plan Validator
# ============================================================================

class PlanValidator:
    """
    CORTEX 4.0 Plan Validator.
    
    Validates plan data against YAML schema with comprehensive error reporting.
    
    Validation Layers:
    1. Schema validation (required fields, types)
    2. Metadata validation (plan_id, title, status, priority, dates)
    3. Phase validation (sequential numbering, required fields)
    4. Task validation (unique IDs, estimated hours)
    5. Risk validation (likelihood, impact, mitigation)
    6. DoR/DoD validation (minimum requirements)
    
    Week 9: Will integrate with ValidationFramework for multi-layer validation
    """
    
    # Valid enum values for validation
    VALID_STATUSES = ["proposed", "approved", "in-progress", "blocked", "completed", "cancelled"]
    VALID_PRIORITIES = ["critical", "high", "medium", "low"]
    VALID_LIKELIHOOD = ["low", "medium", "high"]
    VALID_IMPACT = ["low", "medium", "high", "critical"]
    
    def __init__(self, schema_path: Optional[Path] = None):
        """
        Initialize plan validator.
        
        Args:
            schema_path: Optional path to plan schema YAML file
        """
        self.schema_path = schema_path
        self.schema = self._load_schema() if schema_path else self._get_default_schema()
        
        logger.info(f"✅ Plan Validator initialized (schema={'loaded' if self.schema else 'default'})")
    
    def _load_schema(self) -> Optional[Dict[str, Any]]:
        """
        Load plan schema from YAML file.
        
        Returns:
            Schema dictionary or None if not found
        """
        try:
            if not self.schema_path or not self.schema_path.exists():
                logger.warning(f"Schema not found at {self.schema_path}, using defaults")
                return self._get_default_schema()
            
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                schema = yaml.safe_load(f)
                logger.info(f"✅ Schema loaded: {self.schema_path.name}")
                return schema
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            return self._get_default_schema()
    
    def _get_default_schema(self) -> Dict[str, Any]:
        """
        Get default schema if file not found.
        
        Returns:
            Default schema dictionary
        """
        return {
            "schema": {
                "version": "1.0.0",
                "required_fields": ["metadata", "phases", "definition_of_ready", "definition_of_done"]
            }
        }
    
    def validate(self, plan_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate complete plan against schema.
        
        Args:
            plan_data: Plan data dictionary to validate
        
        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult(valid=True, validation_type="complete_plan_validation")
        
        # Layer 1: Schema validation (required fields)
        schema_result = self._validate_schema(plan_data)
        result.merge(schema_result)
        
        # Layer 2: Metadata validation
        if "metadata" in plan_data:
            metadata_result = self._validate_metadata(plan_data["metadata"])
            result.merge(metadata_result)
        
        # Layer 3: Phase validation
        if "phases" in plan_data:
            phases_result = self._validate_phases(plan_data["phases"])
            result.merge(phases_result)
        
        # Layer 4: DoR/DoD validation
        dor_result = self._validate_dor(plan_data.get("definition_of_ready", []))
        result.merge(dor_result)
        
        dod_result = self._validate_dod(plan_data.get("definition_of_done", []))
        result.merge(dod_result)
        
        # Layer 5: Risk validation (optional)
        if "risks" in plan_data:
            risks_result = self._validate_risks(plan_data["risks"])
            result.merge(risks_result)
        
        # Week 9: Will add ValidationFramework integration here
        
        return result
    
    def _validate_schema(self, plan_data: Dict[str, Any]) -> ValidationResult:
        """
        Validate required fields against schema.
        
        Args:
            plan_data: Plan data dictionary
        
        Returns:
            ValidationResult for schema validation
        """
        result = ValidationResult(valid=True, validation_type="schema_validation")
        
        required_fields = self.schema.get("schema", {}).get("required_fields", [])
        for field in required_fields:
            if field not in plan_data:
                result.add_error(f"Missing required field: {field}")
        
        # Type validation
        if "metadata" in plan_data and not isinstance(plan_data["metadata"], dict):
            result.add_error("metadata must be a dictionary")
        
        if "phases" in plan_data and not isinstance(plan_data["phases"], list):
            result.add_error("phases must be a list")
        
        if "definition_of_ready" in plan_data and not isinstance(plan_data["definition_of_ready"], list):
            result.add_error("definition_of_ready must be a list")
        
        if "definition_of_done" in plan_data and not isinstance(plan_data["definition_of_done"], list):
            result.add_error("definition_of_done must be a list")
        
        return result
    
    def _validate_metadata(self, metadata: Dict[str, Any]) -> ValidationResult:
        """
        Validate metadata section.
        
        Args:
            metadata: Metadata dictionary
        
        Returns:
            ValidationResult for metadata validation
        """
        result = ValidationResult(valid=True, validation_type="metadata_validation")
        
        # Required metadata fields
        required = ["plan_id", "title", "created_date", "created_by", "status", "priority", "estimated_hours"]
        for field in required:
            if field not in metadata:
                result.add_error(f"metadata: Missing required field '{field}'")
        
        # Validate plan_id format (uppercase alphanumeric with hyphens)
        if "plan_id" in metadata:
            if not re.match(r'^[A-Z0-9-]+$', metadata["plan_id"]):
                result.add_error(f"metadata.plan_id: Must match pattern ^[A-Z0-9-]+$ (got: {metadata['plan_id']})")
        
        # Validate status enum
        if "status" in metadata:
            if metadata["status"] not in self.VALID_STATUSES:
                result.add_error(f"metadata.status: Must be one of {self.VALID_STATUSES} (got: {metadata['status']})")
        
        # Validate priority enum
        if "priority" in metadata:
            if metadata["priority"] not in self.VALID_PRIORITIES:
                result.add_error(f"metadata.priority: Must be one of {self.VALID_PRIORITIES} (got: {metadata['priority']})")
        
        # Validate estimated_hours
        if "estimated_hours" in metadata:
            if not isinstance(metadata["estimated_hours"], (int, float)) or metadata["estimated_hours"] < 0:
                result.add_error(f"metadata.estimated_hours: Must be a positive number (got: {metadata['estimated_hours']})")
        
        # Validate created_date format (ISO 8601)
        if "created_date" in metadata:
            if not self._is_valid_iso8601(metadata["created_date"]):
                result.add_error(f"metadata.created_date: Must be ISO 8601 format (got: {metadata['created_date']})")
        
        return result
    
    def _validate_phases(self, phases: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validate phases section.
        
        Args:
            phases: List of phase dictionaries
        
        Returns:
            ValidationResult for phases validation
        """
        result = ValidationResult(valid=True, validation_type="phases_validation")
        
        if not isinstance(phases, list):
            result.add_error("phases: Must be a list")
            return result
        
        if len(phases) == 0:
            result.add_error("phases: Must have at least 1 phase")
            return result
        
        task_ids: Set[str] = set()
        phase_numbers: List[int] = []
        
        for idx, phase in enumerate(phases):
            phase_label = f"phases[{idx}]"
            
            # Required phase fields
            required = ["phase_number", "phase_name", "estimated_hours", "tasks"]
            for field in required:
                if field not in phase:
                    result.add_error(f"{phase_label}: Missing required field '{field}'")
            
            # Validate phase_number
            if "phase_number" in phase:
                if not isinstance(phase["phase_number"], int) or phase["phase_number"] < 1:
                    result.add_error(f"{phase_label}.phase_number: Must be integer >= 1")
                else:
                    phase_numbers.append(phase["phase_number"])
            
            # Validate tasks
            if "tasks" in phase:
                tasks_result = self._validate_tasks(phase["tasks"], task_ids, phase_label)
                result.merge(tasks_result)
        
        # Validate phase numbers are sequential
        if phase_numbers:
            phase_numbers.sort()
            expected = list(range(1, len(phase_numbers) + 1))
            if phase_numbers != expected:
                result.add_error(f"phases: Phase numbers must be sequential starting from 1 (got: {phase_numbers})")
        
        return result
    
    def _validate_tasks(
        self,
        tasks: List[Dict[str, Any]],
        task_ids: Set[str],
        phase_label: str
    ) -> ValidationResult:
        """
        Validate tasks within a phase.
        
        Args:
            tasks: List of task dictionaries
            task_ids: Set of seen task IDs for uniqueness validation
            phase_label: Label for phase (for error messages)
        
        Returns:
            ValidationResult for tasks validation
        """
        result = ValidationResult(valid=True, validation_type="tasks_validation")
        
        if not isinstance(tasks, list):
            result.add_error(f"{phase_label}.tasks: Must be a list")
            return result
        
        if len(tasks) == 0:
            result.add_error(f"{phase_label}.tasks: Must have at least 1 task")
            return result
        
        for idx, task in enumerate(tasks):
            task_label = f"{phase_label}.tasks[{idx}]"
            
            # Required task fields
            required = ["task_id", "task_name", "estimated_hours"]
            for field in required:
                if field not in task:
                    result.add_error(f"{task_label}: Missing required field '{field}'")
            
            # Validate task_id format (e.g., "1.1", "2.3")
            if "task_id" in task:
                if not re.match(r'^\d+\.\d+$', task["task_id"]):
                    result.add_error(f"{task_label}.task_id: Must match pattern \\d+\\.\\d+ (got: {task['task_id']})")
                elif task["task_id"] in task_ids:
                    result.add_error(f"{task_label}.task_id: Duplicate task ID '{task['task_id']}'")
                else:
                    task_ids.add(task["task_id"])
            
            # Validate estimated_hours (minimum 0.25 hours = 15 minutes)
            if "estimated_hours" in task:
                if not isinstance(task["estimated_hours"], (int, float)) or task["estimated_hours"] < 0.25:
                    result.add_error(f"{task_label}.estimated_hours: Must be >= 0.25 (got: {task['estimated_hours']})")
        
        return result
    
    def _validate_risks(self, risks: List[Dict[str, Any]]) -> ValidationResult:
        """
        Validate risks section.
        
        Args:
            risks: List of risk dictionaries
        
        Returns:
            ValidationResult for risks validation
        """
        result = ValidationResult(valid=True, validation_type="risks_validation")
        
        if not isinstance(risks, list):
            result.add_error("risks: Must be a list")
            return result
        
        for idx, risk in enumerate(risks):
            risk_label = f"risks[{idx}]"
            
            # Required risk fields
            required = ["risk_id", "description", "likelihood", "impact", "mitigation"]
            for field in required:
                if field not in risk:
                    result.add_error(f"{risk_label}: Missing required field '{field}'")
            
            # Validate likelihood enum
            if "likelihood" in risk:
                if risk["likelihood"] not in self.VALID_LIKELIHOOD:
                    result.add_error(f"{risk_label}.likelihood: Must be one of {self.VALID_LIKELIHOOD}")
            
            # Validate impact enum
            if "impact" in risk:
                if risk["impact"] not in self.VALID_IMPACT:
                    result.add_error(f"{risk_label}.impact: Must be one of {self.VALID_IMPACT}")
        
        return result
    
    def _validate_dor(self, dor: List[str]) -> ValidationResult:
        """
        Validate Definition of Ready.
        
        Args:
            dor: List of DoR items
        
        Returns:
            ValidationResult for DoR validation
        """
        result = ValidationResult(valid=True, validation_type="dor_validation")
        
        if not isinstance(dor, list):
            result.add_error("definition_of_ready: Must be a list")
            return result
        
        if len(dor) == 0:
            result.add_error("definition_of_ready: Must have at least 1 item")
        
        return result
    
    def _validate_dod(self, dod: List[str]) -> ValidationResult:
        """
        Validate Definition of Done.
        
        Args:
            dod: List of DoD items
        
        Returns:
            ValidationResult for DoD validation
        """
        result = ValidationResult(valid=True, validation_type="dod_validation")
        
        if not isinstance(dod, list):
            result.add_error("definition_of_done: Must be a list")
            return result
        
        if len(dod) == 0:
            result.add_error("definition_of_done: Must have at least 1 item")
        
        return result
    
    def _is_valid_iso8601(self, date_string: str) -> bool:
        """
        Check if string is valid ISO 8601 format.
        
        Args:
            date_string: Date string to validate
        
        Returns:
            True if valid ISO 8601 format
        """
        try:
            datetime.fromisoformat(date_string.replace('Z', '+00:00'))
            return True
        except (ValueError, AttributeError, TypeError):
            return False
    
    def validate_tdd_requirements(
        self,
        plan_data: Dict[str, Any],
        dor_requirements: List[str],
        dod_requirements: List[str]
    ) -> ValidationResult:
        """
        Validate TDD requirements in plan.
        
        Week 9: Will integrate with TDDIntelligence for deeper validation.
        
        Args:
            plan_data: Plan data dictionary
            dor_requirements: Required DoR items for TDD
            dod_requirements: Required DoD items for TDD
        
        Returns:
            ValidationResult for TDD validation
        """
        result = ValidationResult(valid=True, validation_type="tdd_validation")
        
        # Check if plan has TDD requirements
        if "tdd_requirements" not in plan_data:
            result.add_warning("Plan missing 'tdd_requirements' section")
            return result
        
        tdd_req = plan_data["tdd_requirements"]
        
        # Validate DoR requirements
        if "dor" in tdd_req:
            plan_dor = tdd_req["dor"]
            for req in dor_requirements:
                if req not in plan_dor:
                    result.add_warning(f"TDD DoR missing requirement: {req}")
        else:
            result.add_error("TDD requirements missing 'dor' section")
        
        # Validate DoD requirements
        if "dod" in tdd_req:
            plan_dod = tdd_req["dod"]
            for req in dod_requirements:
                if req not in plan_dod:
                    result.add_warning(f"TDD DoD missing requirement: {req}")
        else:
            result.add_error("TDD requirements missing 'dod' section")
        
        return result


# ============================================================================
# Convenience Functions
# ============================================================================

def validate_plan(plan_data: Dict[str, Any], schema_path: Optional[Path] = None) -> ValidationResult:
    """
    Convenience function to validate a plan.
    
    Args:
        plan_data: Plan data dictionary to validate
        schema_path: Optional path to schema YAML file
    
    Returns:
        ValidationResult with validation status
    """
    validator = PlanValidator(schema_path=schema_path)
    return validator.validate(plan_data)


def validate_plan_file(plan_path: Path, schema_path: Optional[Path] = None) -> ValidationResult:
    """
    Convenience function to validate a plan YAML file.
    
    Args:
        plan_path: Path to plan YAML file
        schema_path: Optional path to schema YAML file
    
    Returns:
        ValidationResult with validation status
    """
    try:
        with open(plan_path, 'r', encoding='utf-8') as f:
            plan_data = yaml.safe_load(f)
        
        return validate_plan(plan_data, schema_path)
    
    except Exception as e:
        result = ValidationResult(valid=False, validation_type="file_validation")
        result.add_error(f"Failed to load plan file: {e}")
        return result
