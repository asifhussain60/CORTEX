"""
Shared Validation Framework for CORTEX Orchestrators

Eliminates validation logic duplication across orchestrators.
Provides type-safe, composable, testable validation infrastructure.

Version: 1.0.0
Author: Asif Hussain
"""

from typing import Protocol, List, Dict, Any, Optional, Callable
from dataclasses import dataclass, field
from pathlib import Path
import re
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# Validation Result Models
# ============================================================================

@dataclass
class ValidationResult:
    """Standard validation result."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    checks_performed: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(self, message: str) -> None:
        """Add validation error."""
        self.errors.append(message)
        self.valid = False
    
    def add_warning(self, message: str) -> None:
        """Add validation warning."""
        self.warnings.append(message)
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result."""
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)
        self.checks_performed += other.checks_performed
        self.metadata.update(other.metadata)
        if not other.valid:
            self.valid = False
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "valid": self.valid,
            "errors": self.errors,
            "warnings": self.warnings,
            "checks_performed": self.checks_performed,
            "metadata": self.metadata
        }


# ============================================================================
# Validator Protocol
# ============================================================================

class IValidator(Protocol):
    """Base validator protocol."""
    
    def validate(self, target: Any) -> ValidationResult:
        """
        Validate target object.
        
        Args:
            target: Object to validate
            
        Returns:
            ValidationResult with errors/warnings
        """
        ...


# ============================================================================
# Plan Validators
# ============================================================================

class PlanMetadataValidator:
    """Validates plan metadata (title, description, etc.)."""
    
    def validate(self, plan_data: Dict) -> ValidationResult:
        """Validate plan metadata."""
        result = ValidationResult(valid=True, checks_performed=4)
        
        # Check required metadata
        if "metadata" not in plan_data:
            result.add_error("Missing 'metadata' section")
            return result
        
        metadata = plan_data["metadata"]
        
        # Title validation
        if "title" not in metadata or not metadata["title"].strip():
            result.add_error("Missing or empty plan title")
        
        # Description validation
        if "description" not in metadata:
            result.add_warning("Missing plan description")
        elif len(metadata["description"]) < 20:
            result.add_warning("Plan description too short (< 20 chars)")
        
        # Author validation
        if "author" not in metadata:
            result.add_warning("Missing plan author")
        
        # Priority validation
        if "priority" in metadata:
            valid_priorities = ["critical", "high", "medium", "low"]
            if metadata["priority"].lower() not in valid_priorities:
                result.add_warning(f"Invalid priority. Use: {', '.join(valid_priorities)}")
        
        return result


class PlanPhaseValidator:
    """Validates plan phase structure."""
    
    def validate(self, plan_data: Dict) -> ValidationResult:
        """Validate plan phases."""
        result = ValidationResult(valid=True, checks_performed=5)
        
        if "phases" not in plan_data:
            result.add_error("Missing 'phases' section")
            return result
        
        phases = plan_data["phases"]
        
        if not isinstance(phases, list) or len(phases) == 0:
            result.add_error("Plan must have at least one phase")
            return result
        
        for idx, phase in enumerate(phases, 1):
            phase_name = phase.get("name", f"Phase {idx}")
            
            # Phase name validation
            if "name" not in phase or not phase["name"].strip():
                result.add_error(f"Phase {idx}: Missing or empty name")
            
            # Tasks validation
            if "tasks" not in phase:
                result.add_error(f"{phase_name}: Missing 'tasks' section")
            elif not isinstance(phase["tasks"], list) or len(phase["tasks"]) == 0:
                result.add_error(f"{phase_name}: Must have at least one task")
            else:
                # Validate individual tasks
                for task_idx, task in enumerate(phase["tasks"], 1):
                    if "description" not in task or not task["description"].strip():
                        result.add_error(f"{phase_name}, Task {task_idx}: Missing description")
                    
                    if "type" in task:
                        valid_types = ["implementation", "testing", "refactoring", "documentation"]
                        if task["type"] not in valid_types:
                            result.add_warning(f"{phase_name}, Task {task_idx}: Unknown type '{task['type']}'")
        
        return result


class PlanDoRDoDValidator:
    """Validates Definition of Ready and Definition of Done."""
    
    def validate(self, plan_data: Dict) -> ValidationResult:
        """Validate DoR/DoD."""
        result = ValidationResult(valid=True, checks_performed=2)
        
        # DoR validation
        if "definition_of_ready" not in plan_data:
            result.add_warning("Missing 'definition_of_ready' section")
        else:
            dor = plan_data["definition_of_ready"]
            if not isinstance(dor, list) or len(dor) == 0:
                result.add_warning("Definition of Ready is empty")
            else:
                result.metadata["dor_items"] = len(dor)
        
        # DoD validation
        if "definition_of_done" not in plan_data:
            result.add_warning("Missing 'definition_of_done' section")
        else:
            dod = plan_data["definition_of_done"]
            if not isinstance(dod, list) or len(dod) == 0:
                result.add_warning("Definition of Done is empty")
            else:
                result.metadata["dod_items"] = len(dod)
        
        return result


class CompositePlanValidator:
    """Composite validator for complete plan validation."""
    
    def __init__(self):
        self.validators = [
            PlanMetadataValidator(),
            PlanPhaseValidator(),
            PlanDoRDoDValidator()
        ]
    
    def validate(self, plan_data: Dict) -> ValidationResult:
        """Run all plan validators."""
        result = ValidationResult(valid=True)
        
        for validator in self.validators:
            validator_result = validator.validate(plan_data)
            result.merge(validator_result)
        
        return result


# ============================================================================
# Task Validators
# ============================================================================

class TaskImplementationValidator:
    """Validates task implementation requirements."""
    
    def validate(self, task: Dict) -> ValidationResult:
        """Validate task implementation."""
        result = ValidationResult(valid=True, checks_performed=6)
        
        task_desc = task.get("description", "Unknown task")
        task_type = task.get("type", "implementation")
        
        # 1. Data operations check
        data_keywords = ["database", "query", "insert", "update", "delete", "transaction", "sql"]
        has_data_ops = any(kw in task_desc.lower() for kw in data_keywords)
        if has_data_ops and "transaction" not in task_desc.lower():
            result.add_warning(f"Task involves data operations but doesn't mention transactions")
        
        # 2. Error handling check
        error_keywords = ["error", "exception", "validation", "handle"]
        if task_type == "implementation" and not any(kw in task_desc.lower() for kw in error_keywords):
            result.add_warning(f"Implementation task should mention error handling")
        
        # 3. Configuration check
        config_keywords = ["config", "setting", "environment", "connection string", "url"]
        has_config = any(kw in task_desc.lower() for kw in config_keywords)
        if has_config and "hardcoded" not in task_desc.lower():
            result.metadata["requires_configuration"] = True
        
        # 4. Security check
        security_keywords = ["auth", "password", "token", "secret", "credential", "permission"]
        has_security = any(kw in task_desc.lower() for kw in security_keywords)
        if has_security:
            result.metadata["requires_security_review"] = True
            if "encrypt" not in task_desc.lower() and "hash" not in task_desc.lower():
                result.add_warning("Security-related task should mention encryption/hashing")
        
        # 5. Testing check
        if task_type == "implementation" and "test" not in task_desc.lower():
            result.add_warning("Implementation task should include testing requirements")
        
        # 6. Domain behavior check
        if task_type == "implementation":
            # Check for anemic model indicators
            anemic_patterns = ["get", "set", "property", "field"]
            rich_patterns = ["calculate", "validate", "process", "execute", "apply"]
            has_anemic = any(p in task_desc.lower() for p in anemic_patterns)
            has_rich = any(p in task_desc.lower() for p in rich_patterns)
            
            if has_anemic and not has_rich:
                result.add_warning("Task may lead to anemic domain models (only getters/setters)")
        
        return result


# ============================================================================
# TDD Validators
# ============================================================================

class TDDPhaseValidator:
    """Validates TDD phase transitions."""
    
    VALID_PHASES = ["not_started", "red", "green", "refactor", "completed"]
    VALID_TRANSITIONS = {
        "not_started": ["red"],
        "red": ["green"],
        "green": ["refactor", "red"],  # Can go to refactor or add more tests
        "refactor": ["red", "completed"],  # Can add more features or complete
        "completed": []
    }
    
    def validate(self, current_phase: str, target_phase: str) -> ValidationResult:
        """Validate TDD phase transition."""
        result = ValidationResult(valid=True, checks_performed=2)
        
        # Validate phase names
        if current_phase not in self.VALID_PHASES:
            result.add_error(f"Invalid current phase: {current_phase}")
        
        if target_phase not in self.VALID_PHASES:
            result.add_error(f"Invalid target phase: {target_phase}")
        
        if not result.valid:
            return result
        
        # Validate transition
        valid_targets = self.VALID_TRANSITIONS.get(current_phase, [])
        if target_phase not in valid_targets:
            result.add_error(
                f"Invalid transition: {current_phase} → {target_phase}. "
                f"Valid targets: {', '.join(valid_targets) if valid_targets else 'none'}"
            )
        
        return result


class TDDTestValidator:
    """Validates TDD test requirements."""
    
    def validate(self, test_files: List[str], implementation_files: List[str]) -> ValidationResult:
        """Validate TDD test coverage."""
        result = ValidationResult(valid=True, checks_performed=3)
        
        # Check test files exist
        if not test_files:
            result.add_error("No test files provided for TDD session")
            return result
        
        # Check implementation files exist
        if not implementation_files:
            result.add_warning("No implementation files specified")
        
        # Check test/implementation ratio
        if len(test_files) < len(implementation_files):
            result.add_warning(
                f"Fewer test files ({len(test_files)}) than implementation files ({len(implementation_files)})"
            )
        
        # Check test file naming
        for test_file in test_files:
            test_path = Path(test_file)
            if not test_path.name.startswith("test_"):
                result.add_warning(f"Test file should start with 'test_': {test_path.name}")
        
        result.metadata["test_files"] = len(test_files)
        result.metadata["implementation_files"] = len(implementation_files)
        
        return result


# ============================================================================
# Code Quality Validators
# ============================================================================

class ConfigurationValidator:
    """Validates configuration management."""
    
    SUSPICIOUS_PATTERNS = [
        (r'https?://[a-zA-Z0-9.-]+', "Hard-coded URL"),
        (r'Server=[^;]+;Database=', "Hard-coded connection string"),
        (r'password\s*=\s*["\'][^"\']+["\']', "Hard-coded password"),
        (r'api[_-]?key\s*=\s*["\'][^"\']+["\']', "Hard-coded API key"),
    ]
    
    def validate(self, code_content: str) -> ValidationResult:
        """Validate configuration usage."""
        result = ValidationResult(valid=True, checks_performed=len(self.SUSPICIOUS_PATTERNS))
        
        for pattern, issue in self.SUSPICIOUS_PATTERNS:
            matches = re.findall(pattern, code_content, re.IGNORECASE)
            if matches:
                result.add_warning(f"{issue} detected: {len(matches)} occurrence(s)")
                result.metadata[f"config_issue_{issue.lower().replace(' ', '_')}"] = len(matches)
        
        return result


class TransactionValidator:
    """Validates transaction usage."""
    
    DB_OPERATIONS = ["INSERT", "UPDATE", "DELETE", "ExecuteNonQuery", "SaveChanges"]
    TRANSACTION_KEYWORDS = ["transaction", "BeginTransaction", "TransactionScope", "commit", "rollback"]
    
    def validate(self, code_content: str) -> ValidationResult:
        """Validate transaction usage."""
        result = ValidationResult(valid=True, checks_performed=2)
        
        # Count DB operations
        db_op_count = sum(code_content.count(op) for op in self.DB_OPERATIONS)
        
        # Check for transaction keywords
        has_transaction = any(kw in code_content for kw in self.TRANSACTION_KEYWORDS)
        
        if db_op_count >= 2 and not has_transaction:
            result.add_warning(
                f"Multiple database operations ({db_op_count}) without explicit transaction"
            )
            result.metadata["db_operations"] = db_op_count
            result.metadata["has_transaction"] = False
        
        return result


# ============================================================================
# Composite Validators
# ============================================================================

class CompositeValidator:
    """Runs multiple validators and aggregates results."""
    
    def __init__(self, validators: List[IValidator]):
        self.validators = validators
    
    def validate(self, target: Any) -> ValidationResult:
        """Run all validators."""
        result = ValidationResult(valid=True)
        
        for validator in self.validators:
            try:
                validator_result = validator.validate(target)
                result.merge(validator_result)
            except Exception as e:
                logger.error(f"Validator {validator.__class__.__name__} failed: {e}")
                result.add_error(f"Validator error: {e}")
        
        return result


# ============================================================================
# Validation Utilities
# ============================================================================

def validate_plan(plan_data: Dict) -> ValidationResult:
    """
    Convenience function for plan validation.
    
    Args:
        plan_data: Plan dictionary
        
    Returns:
        ValidationResult
    """
    validator = CompositePlanValidator()
    return validator.validate(plan_data)


def validate_task(task: Dict) -> ValidationResult:
    """
    Convenience function for task validation.
    
    Args:
        task: Task dictionary
        
    Returns:
        ValidationResult
    """
    validator = TaskImplementationValidator()
    return validator.validate(task)


def validate_tdd_transition(current_phase: str, target_phase: str) -> ValidationResult:
    """
    Convenience function for TDD phase validation.
    
    Args:
        current_phase: Current TDD phase
        target_phase: Target TDD phase
        
    Returns:
        ValidationResult
    """
    validator = TDDPhaseValidator()
    return validator.validate(current_phase, target_phase)


def validate_code_quality(code_content: str) -> ValidationResult:
    """
    Convenience function for code quality validation.
    
    Args:
        code_content: Source code content
        
    Returns:
        ValidationResult with config/transaction warnings
    """
    validators = [
        ConfigurationValidator(),
        TransactionValidator()
    ]
    composite = CompositeValidator(validators)
    return composite.validate(code_content)


# ============================================================================
# Export Public API
# ============================================================================

__all__ = [
    # Models
    "ValidationResult",
    "IValidator",
    
    # Plan validators
    "PlanMetadataValidator",
    "PlanPhaseValidator",
    "PlanDoRDoDValidator",
    "CompositePlanValidator",
    
    # Task validators
    "TaskImplementationValidator",
    
    # TDD validators
    "TDDPhaseValidator",
    "TDDTestValidator",
    
    # Code quality validators
    "ConfigurationValidator",
    "TransactionValidator",
    
    # Composite
    "CompositeValidator",
    
    # Convenience functions
    "validate_plan",
    "validate_task",
    "validate_tdd_transition",
    "validate_code_quality",
]
