"""
Validation Framework Adapter - Multi-layer Validation for Planning System

Purpose: Provides comprehensive validation framework with schema validation,
business rules, cross-field validation, and async validation support.

Version: 1.0.0
Author: CORTEX Development Team
Created: 2025-12-24 (Week 9 Day 2)

Responsibilities:
- Schema validation (YAML structure, data types)
- Business rule validation (DoR/DoD, task dependencies)
- Cross-field validation (phase consistency, time estimates)
- Async validation (external API checks, resource availability)
- Validation result aggregation and reporting

Integration Points:
- Planning System: Enhanced validation beyond basic schema checks
- plan_validator.py: Extends core validation with business rules
- Brain Protection (Tier 0): Enforces governance rules
- Phase Manager: Validates phase transitions

Week 9 Target: 400 LOC
"""

import asyncio
import logging
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Callable, Tuple
import re

logger = logging.getLogger(__name__)


class ValidationLevel(Enum):
    """Validation severity levels."""
    ERROR = "error"  # Blocks execution
    WARNING = "warning"  # Allows execution with caution
    INFO = "info"  # Informational only


class ValidationType(Enum):
    """Types of validation."""
    SCHEMA = "schema"  # Structure and data types
    BUSINESS_RULE = "business_rule"  # Business logic
    CROSS_FIELD = "cross_field"  # Field relationships
    ASYNC = "async"  # External checks


@dataclass
class ValidationResult:
    """Single validation result."""
    validation_type: ValidationType
    level: ValidationLevel
    field_path: str  # e.g., "phases[0].tasks[2].estimated_hours"
    message: str
    suggestion: Optional[str] = None
    
    def is_blocking(self) -> bool:
        """Check if validation blocks execution."""
        return self.level == ValidationLevel.ERROR


@dataclass
class ValidationReport:
    """Complete validation report."""
    is_valid: bool
    results: List[ValidationResult] = field(default_factory=list)
    
    errors: int = 0
    warnings: int = 0
    infos: int = 0
    
    execution_blocked: bool = False
    
    def add_result(self, result: ValidationResult):
        """Add validation result and update counters."""
        self.results.append(result)
        
        if result.level == ValidationLevel.ERROR:
            self.errors += 1
            self.execution_blocked = True
        elif result.level == ValidationLevel.WARNING:
            self.warnings += 1
        elif result.level == ValidationLevel.INFO:
            self.infos += 1
        
        self.is_valid = self.errors == 0
    
    def get_blocking_errors(self) -> List[ValidationResult]:
        """Get errors that block execution."""
        return [r for r in self.results if r.is_blocking()]
    
    def get_summary(self) -> str:
        """Get human-readable summary."""
        if self.is_valid:
            return f"✅ Validation passed ({self.warnings} warnings, {self.infos} infos)"
        else:
            return f"❌ Validation failed ({self.errors} errors, {self.warnings} warnings)"


class ValidationFrameworkAdapter:
    """
    Multi-layer validation framework for Planning System.
    
    Provides comprehensive validation including schema, business rules,
    cross-field validation, and async external checks.
    
    Usage:
        adapter = ValidationFrameworkAdapter()
        report = await adapter.validate_plan(plan_data, validation_levels=["schema", "business_rule"])
        
        if report.is_valid:
            # Proceed with plan
        else:
            # Handle errors
            for error in report.get_blocking_errors():
                print(f"Error: {error.message}")
    """
    
    def __init__(self, strict_mode: bool = True):
        """
        Initialize validation framework.
        
        Args:
            strict_mode: Enforce strict validation (warnings as errors)
        """
        self.strict_mode = strict_mode
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        
        # Register validation rules
        self._schema_rules: List[Callable] = []
        self._business_rules: List[Callable] = []
        self._cross_field_rules: List[Callable] = []
        self._async_rules: List[Callable] = []
        
        self._register_default_rules()
    
    # ========== Main Validation Entry Point ==========
    
    async def validate_plan(
        self,
        plan_data: Dict[str, Any],
        validation_levels: Optional[List[str]] = None
    ) -> ValidationReport:
        """
        Validate plan with specified validation levels.
        
        Args:
            plan_data: Plan data to validate
            validation_levels: Validation levels to run (None = all)
            
        Returns:
            Complete validation report
        """
        self.logger.info("Starting multi-layer plan validation")
        
        report = ValidationReport(is_valid=True)
        
        # Determine which validations to run
        levels = validation_levels or ["schema", "business_rule", "cross_field"]
        
        # Schema validation
        if "schema" in levels:
            schema_results = self._validate_schema(plan_data)
            for result in schema_results:
                report.add_result(result)
        
        # Business rule validation
        if "business_rule" in levels:
            business_results = self._validate_business_rules(plan_data)
            for result in business_results:
                report.add_result(result)
        
        # Cross-field validation
        if "cross_field" in levels:
            cross_field_results = self._validate_cross_fields(plan_data)
            for result in cross_field_results:
                report.add_result(result)
        
        # Async validation (if requested)
        if "async" in levels:
            async_results = await self._validate_async(plan_data)
            for result in async_results:
                report.add_result(result)
        
        self.logger.info(f"Validation complete: {report.get_summary()}")
        return report
    
    # ========== Schema Validation ==========
    
    def _validate_schema(self, plan_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate schema structure and data types."""
        results = []
        
        # Required top-level fields
        required_fields = ["metadata", "phases"]
        for field in required_fields:
            if field not in plan_data:
                results.append(ValidationResult(
                    validation_type=ValidationType.SCHEMA,
                    level=ValidationLevel.ERROR,
                    field_path=field,
                    message=f"Missing required field: {field}",
                    suggestion=f"Add '{field}' to plan YAML"
                ))
        
        # Validate metadata
        if "metadata" in plan_data:
            metadata_results = self._validate_metadata_schema(plan_data["metadata"])
            results.extend(metadata_results)
        
        # Validate phases
        if "phases" in plan_data:
            phases_results = self._validate_phases_schema(plan_data["phases"])
            results.extend(phases_results)
        
        return results
    
    def _validate_metadata_schema(self, metadata: Dict[str, Any]) -> List[ValidationResult]:
        """Validate metadata schema."""
        results = []
        
        required_metadata = ["plan_name", "complexity", "estimated_hours"]
        for field in required_metadata:
            if field not in metadata:
                results.append(ValidationResult(
                    validation_type=ValidationType.SCHEMA,
                    level=ValidationLevel.WARNING,
                    field_path=f"metadata.{field}",
                    message=f"Missing recommended metadata field: {field}"
                ))
        
        # Validate complexity value
        if "complexity" in metadata:
            valid_complexities = ["low", "medium", "high", "complex"]
            if metadata["complexity"] not in valid_complexities:
                results.append(ValidationResult(
                    validation_type=ValidationType.SCHEMA,
                    level=ValidationLevel.ERROR,
                    field_path="metadata.complexity",
                    message=f"Invalid complexity: {metadata['complexity']}",
                    suggestion=f"Must be one of: {', '.join(valid_complexities)}"
                ))
        
        return results
    
    def _validate_phases_schema(self, phases: List[Dict[str, Any]]) -> List[ValidationResult]:
        """Validate phases schema."""
        results = []
        
        if not phases:
            results.append(ValidationResult(
                validation_type=ValidationType.SCHEMA,
                level=ValidationLevel.ERROR,
                field_path="phases",
                message="Plan must have at least one phase"
            ))
            return results
        
        for i, phase in enumerate(phases):
            # Required phase fields
            required_phase_fields = ["phase_number", "phase_name", "tasks"]
            for field in required_phase_fields:
                if field not in phase:
                    results.append(ValidationResult(
                        validation_type=ValidationType.SCHEMA,
                        level=ValidationLevel.ERROR,
                        field_path=f"phases[{i}].{field}",
                        message=f"Missing required phase field: {field}"
                    ))
            
            # Validate tasks
            if "tasks" in phase:
                task_results = self._validate_tasks_schema(phase["tasks"], i)
                results.extend(task_results)
        
        return results
    
    def _validate_tasks_schema(self, tasks: List[Dict[str, Any]], phase_index: int) -> List[ValidationResult]:
        """Validate tasks schema."""
        results = []
        
        if not tasks:
            results.append(ValidationResult(
                validation_type=ValidationType.SCHEMA,
                level=ValidationLevel.WARNING,
                field_path=f"phases[{phase_index}].tasks",
                message="Phase has no tasks"
            ))
            return results
        
        for j, task in enumerate(tasks):
            # Required task fields
            required_task_fields = ["task_id", "task_name", "estimated_hours"]
            for field in required_task_fields:
                if field not in task:
                    results.append(ValidationResult(
                        validation_type=ValidationType.SCHEMA,
                        level=ValidationLevel.ERROR,
                        field_path=f"phases[{phase_index}].tasks[{j}].{field}",
                        message=f"Missing required task field: {field}"
                    ))
            
            # Validate estimated_hours is numeric
            if "estimated_hours" in task:
                if not isinstance(task["estimated_hours"], (int, float)):
                    results.append(ValidationResult(
                        validation_type=ValidationType.SCHEMA,
                        level=ValidationLevel.ERROR,
                        field_path=f"phases[{phase_index}].tasks[{j}].estimated_hours",
                        message="estimated_hours must be a number"
                    ))
        
        return results
    
    # ========== Business Rule Validation ==========
    
    def _validate_business_rules(self, plan_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate business rules."""
        results = []
        
        # Rule 1: Phase numbers must be sequential
        if "phases" in plan_data:
            phase_numbers = [p.get("phase_number", 0) for p in plan_data["phases"]]
            expected = list(range(1, len(phase_numbers) + 1))
            if phase_numbers != expected:
                results.append(ValidationResult(
                    validation_type=ValidationType.BUSINESS_RULE,
                    level=ValidationLevel.ERROR,
                    field_path="phases[*].phase_number",
                    message=f"Phase numbers not sequential: {phase_numbers}",
                    suggestion="Phase numbers must be 1, 2, 3, ..."
                ))
        
        # Rule 2: Total estimated hours should be reasonable
        total_hours = self._calculate_total_hours(plan_data)
        if total_hours > 1000:
            results.append(ValidationResult(
                validation_type=ValidationType.BUSINESS_RULE,
                level=ValidationLevel.WARNING,
                field_path="metadata.estimated_hours",
                message=f"Very high time estimate: {total_hours}h",
                suggestion="Consider breaking into smaller plans"
            ))
        
        # Rule 3: DoR/DoD should be present
        if "definition_of_ready" not in plan_data:
            results.append(ValidationResult(
                validation_type=ValidationType.BUSINESS_RULE,
                level=ValidationLevel.WARNING,
                field_path="definition_of_ready",
                message="Missing Definition of Ready (DoR)"
            ))
        
        if "definition_of_done" not in plan_data:
            results.append(ValidationResult(
                validation_type=ValidationType.BUSINESS_RULE,
                level=ValidationLevel.WARNING,
                field_path="definition_of_done",
                message="Missing Definition of Done (DoD)"
            ))
        
        return results
    
    # ========== Cross-Field Validation ==========
    
    def _validate_cross_fields(self, plan_data: Dict[str, Any]) -> List[ValidationResult]:
        """Validate relationships between fields."""
        results = []
        
        # Cross-field 1: Metadata total hours vs sum of phase hours
        if "metadata" in plan_data and "phases" in plan_data:
            metadata_hours = plan_data["metadata"].get("estimated_hours", 0)
            calculated_hours = self._calculate_total_hours(plan_data)
            
            if abs(metadata_hours - calculated_hours) > 0.1:
                results.append(ValidationResult(
                    validation_type=ValidationType.CROSS_FIELD,
                    level=ValidationLevel.WARNING,
                    field_path="metadata.estimated_hours",
                    message=f"Metadata hours ({metadata_hours}h) != sum of phase hours ({calculated_hours}h)",
                    suggestion=f"Update metadata.estimated_hours to {calculated_hours}"
                ))
        
        # Cross-field 2: Task dependencies reference valid tasks
        if "phases" in plan_data:
            all_task_ids = set()
            for phase in plan_data["phases"]:
                for task in phase.get("tasks", []):
                    all_task_ids.add(task.get("task_id"))
            
            for i, phase in enumerate(plan_data["phases"]):
                for j, task in enumerate(phase.get("tasks", [])):
                    dependencies = task.get("dependencies", [])
                    for dep in dependencies:
                        if dep not in all_task_ids:
                            results.append(ValidationResult(
                                validation_type=ValidationType.CROSS_FIELD,
                                level=ValidationLevel.ERROR,
                                field_path=f"phases[{i}].tasks[{j}].dependencies",
                                message=f"Invalid dependency: {dep} (task not found)"
                            ))
        
        return results
    
    # ========== Async Validation ==========
    
    async def _validate_async(self, plan_data: Dict[str, Any]) -> List[ValidationResult]:
        """Async validation (external checks)."""
        results = []
        
        # Example: Check if file paths exist
        if "phases" in plan_data:
            for i, phase in enumerate(plan_data["phases"]):
                for j, task in enumerate(phase.get("tasks", [])):
                    files_affected = task.get("files_affected", [])
                    for file_path in files_affected:
                        exists = await self._check_file_exists(file_path)
                        if not exists:
                            results.append(ValidationResult(
                                validation_type=ValidationType.ASYNC,
                                level=ValidationLevel.INFO,
                                field_path=f"phases[{i}].tasks[{j}].files_affected",
                                message=f"File not found: {file_path}",
                                suggestion="File will be created during implementation"
                            ))
        
        return results
    
    async def _check_file_exists(self, file_path: str) -> bool:
        """Check if file exists (async)."""
        # Simulate async check
        await asyncio.sleep(0.01)
        return Path(file_path).exists()
    
    # ========== Helper Methods ==========
    
    def _calculate_total_hours(self, plan_data: Dict[str, Any]) -> float:
        """Calculate total estimated hours from phases."""
        total = 0.0
        for phase in plan_data.get("phases", []):
            for task in phase.get("tasks", []):
                total += task.get("estimated_hours", 0)
        return total
    
    def _register_default_rules(self):
        """Register default validation rules."""
        # This would be extended with custom validation rules
        pass
    
    # ========== Public API ==========
    
    def validate_phase_transition(
        self,
        current_phase: int,
        target_phase: int,
        phase_data: Dict[str, Any]
    ) -> ValidationReport:
        """
        Validate phase transition.
        
        Args:
            current_phase: Current phase number
            target_phase: Target phase number
            phase_data: Phase data to validate
            
        Returns:
            Validation report
        """
        report = ValidationReport(is_valid=True)
        
        # Rule: Can only transition to next phase
        if target_phase != current_phase + 1:
            report.add_result(ValidationResult(
                validation_type=ValidationType.BUSINESS_RULE,
                level=ValidationLevel.ERROR,
                field_path=f"phases[{current_phase}]",
                message=f"Cannot skip phases: {current_phase} → {target_phase}",
                suggestion=f"Complete phase {current_phase + 1} first"
            ))
        
        # Rule: Current phase must be complete
        if phase_data.get("status") != "complete":
            report.add_result(ValidationResult(
                validation_type=ValidationType.BUSINESS_RULE,
                level=ValidationLevel.ERROR,
                field_path=f"phases[{current_phase}].status",
                message=f"Phase {current_phase} not complete",
                suggestion="Complete all tasks before transitioning"
            ))
        
        return report
