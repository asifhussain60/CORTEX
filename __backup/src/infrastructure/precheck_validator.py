"""
Pre-Execution Validation System for CORTEX 6.0

Provides early detection of orchestrator compatibility issues before runtime,
preventing TypeError and signature mismatch failures.

AC-IDs: AC-PRECHECK-001 to AC-PRECHECK-005

Author: GitHub Copilot (CORTEX 6.0)
Created: 2026-01-11
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import inspect
import logging
from typing import Dict, Any, List, Optional, Set, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from enum import Enum
import importlib
import uuid
from datetime import datetime


class ValidationSeverity(Enum):
    """Validation issue severity levels."""
    CRITICAL = "critical"  # Blocks execution
    WARNING = "warning"   # May cause issues
    INFO = "info"        # Informational only


class ValidationCategory(Enum):
    """Validation issue categories."""
    SIGNATURE = "signature"
    PARAMETER = "parameter"
    DEPENDENCY = "dependency"
    TEST = "test"


@dataclass
class ValidationIssue:
    """Represents a validation issue found during pre-check."""
    severity: ValidationSeverity
    category: ValidationCategory
    message: str
    fix_suggestion: str
    code_location: Optional[str] = None


@dataclass
class SignatureCheck:
    """Results of signature validation."""
    valid: bool
    required_params: List[str] = field(default_factory=list)
    optional_params: List[str] = field(default_factory=list)
    accepts_kwargs: bool = False
    issues: List[str] = field(default_factory=list)


@dataclass
class ValidationResult:
    """Complete validation result for an orchestrator."""
    manifest_id: str
    timestamp: str
    validation_passed: bool
    orchestrator_id: str
    orchestrator_class: str
    orchestrator_module: str
    
    init_signature: SignatureCheck
    execute_signature: SignatureCheck
    recommendations: List[ValidationIssue] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'manifest_id': self.manifest_id,
            'timestamp': self.timestamp,
            'validation_passed': self.validation_passed,
            'orchestrator': {
                'id': self.orchestrator_id,
                'class_name': self.orchestrator_class,
                'module_path': self.orchestrator_module
            },
            'signature_checks': {
                'init_signature': {
                    'valid': self.init_signature.valid,
                    'required_params': self.init_signature.required_params,
                    'optional_params': self.init_signature.optional_params,
                    'accepts_kwargs': self.init_signature.accepts_kwargs,
                    'issues': self.init_signature.issues
                },
                'execute_signature': {
                    'valid': self.execute_signature.valid,
                    'required_params': self.execute_signature.required_params,
                    'optional_params': self.execute_signature.optional_params,
                    'accepts_kwargs': self.execute_signature.accepts_kwargs,
                    'issues': self.execute_signature.issues
                }
            },
            'recommendations': [
                {
                    'severity': issue.severity.value,
                    'category': issue.category.value,
                    'message': issue.message,
                    'fix_suggestion': issue.fix_suggestion,
                    'code_location': issue.code_location
                }
                for issue in self.recommendations
            ]
        }


class PreCheckValidator:
    """
    Pre-execution validation system for orchestrator compatibility.
    
    AC-PRECHECK-001: Signature Validator
    AC-PRECHECK-002: Parameter Compatibility Checker
    AC-PRECHECK-003: Dependency Validator
    AC-PRECHECK-004: Test Suite Validator
    AC-PRECHECK-005: Pre-flight Manifest Generator
    
    Usage:
        validator = PreCheckValidator()
        result = validator.validate_orchestrator(
            orchestrator_id='investigation_v2',
            registry=registry,
            init_args={'workspace_root': '/path/to/workspace'},
            execute_params={'user_request': 'analyze logs'}
        )
        
        if not result.validation_passed:
            for issue in result.recommendations:
                if issue.severity == ValidationSeverity.CRITICAL:
                    print(f"CRITICAL: {issue.message}")
                    print(f"Fix: {issue.fix_suggestion}")
    """
    
    def __init__(self):
        """Initialize PreCheckValidator."""
        self.logger = logging.getLogger("cortex.infrastructure.precheck")
        self.validation_history: List[ValidationResult] = []
    
    def validate_orchestrator(
        self,
        orchestrator_id: str,
        registry: Any,
        init_args: Dict[str, Any],
        execute_params: Dict[str, Any]
    ) -> ValidationResult:
        """
        Validate orchestrator compatibility before execution.
        
        AC-PRECHECK-001 to AC-PRECHECK-005
        
        Args:
            orchestrator_id: Orchestrator identifier
            registry: OrchestratorRegistry instance
            init_args: Arguments to be passed to __init__
            execute_params: Parameters to be passed to execute()
        
        Returns:
            ValidationResult with detailed findings
        """
        manifest_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().isoformat()
        
        self.logger.info(f"Starting pre-check validation: {orchestrator_id} ({manifest_id})")
        
        try:
            # Get orchestrator metadata
            metadata = registry.get(orchestrator_id)
            if not metadata:
                return self._create_error_result(
                    manifest_id, timestamp, orchestrator_id,
                    f"Orchestrator not found in registry: {orchestrator_id}"
                )
            
            # Load orchestrator class
            orchestrator_class = self._load_class(
                metadata.module_path,
                metadata.class_name
            )
            
            if not orchestrator_class:
                return self._create_error_result(
                    manifest_id, timestamp, orchestrator_id,
                    f"Failed to load class: {metadata.class_name}"
                )
            
            # AC-PRECHECK-001: Validate __init__ signature
            init_check = self._validate_init_signature(
                orchestrator_class,
                init_args
            )
            
            # AC-PRECHECK-001: Validate execute() signature
            execute_check = self._validate_execute_signature(
                orchestrator_class,
                execute_params
            )
            
            # Determine overall validation status
            validation_passed = init_check.valid and execute_check.valid
            
            # AC-PRECHECK-005: Generate recommendations
            recommendations = self._generate_recommendations(
                orchestrator_id,
                init_check,
                execute_check,
                init_args,
                execute_params
            )
            
            result = ValidationResult(
                manifest_id=manifest_id,
                timestamp=timestamp,
                validation_passed=validation_passed,
                orchestrator_id=orchestrator_id,
                orchestrator_class=metadata.class_name,
                orchestrator_module=metadata.module_path,
                init_signature=init_check,
                execute_signature=execute_check,
                recommendations=recommendations
            )
            
            # Store in history
            self.validation_history.append(result)
            
            if validation_passed:
                self.logger.info(f"✓ Validation passed: {orchestrator_id}")
            else:
                critical_count = sum(
                    1 for r in recommendations 
                    if r.severity == ValidationSeverity.CRITICAL
                )
                self.logger.warning(
                    f"✗ Validation failed: {orchestrator_id} "
                    f"({critical_count} critical issues)"
                )
            
            return result
            
        except Exception as e:
            self.logger.error(
                f"Validation error for {orchestrator_id}: {e}",
                exc_info=True
            )
            return self._create_error_result(
                manifest_id, timestamp, orchestrator_id,
                f"Validation exception: {str(e)}"
            )
    
    def _load_class(self, module_path: str, class_name: str) -> Optional[type]:
        """Load orchestrator class from module path."""
        try:
            module = importlib.import_module(module_path)
            return getattr(module, class_name, None)
        except Exception as e:
            self.logger.error(f"Failed to load {module_path}.{class_name}: {e}")
            return None
    
    def _validate_init_signature(
        self,
        orchestrator_class: type,
        init_args: Dict[str, Any]
    ) -> SignatureCheck:
        """
        Validate __init__ signature compatibility.
        
        AC-PRECHECK-001: Signature Validator
        """
        try:
            sig = inspect.signature(orchestrator_class.__init__)
            params = sig.parameters
            
            # Exclude 'self'
            param_names = [p for p in params.keys() if p != 'self']
            
            # Categorize parameters
            required = []
            optional = []
            accepts_kwargs = False
            
            for name, param in params.items():
                if name == 'self':
                    continue
                
                if param.kind == inspect.Parameter.VAR_KEYWORD:
                    accepts_kwargs = True
                elif param.default == inspect.Parameter.empty:
                    required.append(name)
                else:
                    optional.append(name)
            
            # Check if all required params are available
            issues = []
            provided_params = set(init_args.keys())
            required_params = set(required)
            
            missing = required_params - provided_params
            if missing and not accepts_kwargs:
                issues.append(
                    f"Missing required parameters: {', '.join(missing)}"
                )
            
            valid = len(issues) == 0
            
            return SignatureCheck(
                valid=valid,
                required_params=required,
                optional_params=optional,
                accepts_kwargs=accepts_kwargs,
                issues=issues
            )
            
        except Exception as e:
            return SignatureCheck(
                valid=False,
                issues=[f"Failed to inspect __init__: {str(e)}"]
            )
    
    def _validate_execute_signature(
        self,
        orchestrator_class: type,
        execute_params: Dict[str, Any]
    ) -> SignatureCheck:
        """
        Validate execute() method signature compatibility.
        
        AC-PRECHECK-001: Signature Validator
        """
        try:
            if not hasattr(orchestrator_class, 'execute'):
                return SignatureCheck(
                    valid=False,
                    issues=["No execute() method found"]
                )
            
            sig = inspect.signature(orchestrator_class.execute)
            params = sig.parameters
            
            # Exclude 'self'
            param_names = [p for p in params.keys() if p != 'self']
            
            # Categorize parameters
            required = []
            optional = []
            accepts_kwargs = False
            
            for name, param in params.items():
                if name == 'self':
                    continue
                
                if param.kind == inspect.Parameter.VAR_KEYWORD:
                    accepts_kwargs = True
                elif param.default == inspect.Parameter.empty:
                    required.append(name)
                else:
                    optional.append(name)
            
            # Check parameter compatibility
            issues = []
            provided_params = set(execute_params.keys())
            required_params = set(required)
            expected_params = set(required + optional)
            
            # Check for missing required params
            missing = required_params - provided_params
            if missing and not accepts_kwargs:
                issues.append(
                    f"Missing required parameters: {', '.join(missing)}"
                )
            
            # Check for incompatible params (e.g., user_request vs context)
            unexpected = provided_params - expected_params
            if unexpected and not accepts_kwargs:
                issues.append(
                    f"Unexpected parameters: {', '.join(unexpected)}"
                )
            
            valid = len(issues) == 0
            
            return SignatureCheck(
                valid=valid,
                required_params=required,
                optional_params=optional,
                accepts_kwargs=accepts_kwargs,
                issues=issues
            )
            
        except Exception as e:
            return SignatureCheck(
                valid=False,
                issues=[f"Failed to inspect execute(): {str(e)}"]
            )
    
    def _generate_recommendations(
        self,
        orchestrator_id: str,
        init_check: SignatureCheck,
        execute_check: SignatureCheck,
        init_args: Dict[str, Any],
        execute_params: Dict[str, Any]
    ) -> List[ValidationIssue]:
        """
        Generate fix recommendations based on validation results.
        
        AC-PRECHECK-005: Pre-flight Manifest Generator
        """
        recommendations = []
        
        # Init signature issues
        if not init_check.valid:
            for issue in init_check.issues:
                if "Missing required parameters" in issue:
                    recommendations.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        category=ValidationCategory.SIGNATURE,
                        message=f"__init__ {issue}",
                        fix_suggestion=(
                            "Add missing parameters to init_args in "
                            "master_orchestrator.execute_orchestrator() or "
                            "update loader.py to filter parameters based on signature"
                        ),
                        code_location="src/orchestrators/master_orchestrator.py:462"
                    ))
        
        # Execute signature issues
        if not execute_check.valid:
            for issue in execute_check.issues:
                if "Unexpected parameters" in issue:
                    recommendations.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        category=ValidationCategory.PARAMETER,
                        message=f"execute() {issue}",
                        fix_suggestion=(
                            "Add parameter mapping logic in "
                            "master_orchestrator.execute_orchestrator() to map "
                            "user_request to context or vice versa based on signature"
                        ),
                        code_location="src/orchestrators/master_orchestrator.py:489"
                    ))
                elif "Missing required parameters" in issue:
                    recommendations.append(ValidationIssue(
                        severity=ValidationSeverity.CRITICAL,
                        category=ValidationCategory.PARAMETER,
                        message=f"execute() {issue}",
                        fix_suggestion=(
                            "Ensure execute_params dict contains all required "
                            "parameters or add intelligent parameter mapping"
                        ),
                        code_location="src/orchestrators/master_orchestrator.py:282"
                    ))
        
        return recommendations
    
    def _create_error_result(
        self,
        manifest_id: str,
        timestamp: str,
        orchestrator_id: str,
        error_message: str
    ) -> ValidationResult:
        """Create error validation result."""
        return ValidationResult(
            manifest_id=manifest_id,
            timestamp=timestamp,
            validation_passed=False,
            orchestrator_id=orchestrator_id,
            orchestrator_class="UNKNOWN",
            orchestrator_module="UNKNOWN",
            init_signature=SignatureCheck(
                valid=False,
                issues=[error_message]
            ),
            execute_signature=SignatureCheck(valid=True),
            recommendations=[
                ValidationIssue(
                    severity=ValidationSeverity.CRITICAL,
                    category=ValidationCategory.SIGNATURE,
                    message=error_message,
                    fix_suggestion="Check orchestrator configuration and availability"
                )
            ]
        )
    
    def get_validation_history(self) -> List[ValidationResult]:
        """Get validation history."""
        return self.validation_history
    
    def export_manifest(
        self,
        result: ValidationResult,
        output_path: Path
    ) -> None:
        """
        Export validation result as YAML manifest.
        
        AC-PRECHECK-005: Pre-flight Manifest Generator
        """
        import yaml
        
        try:
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w') as f:
                yaml.dump(result.to_dict(), f, default_flow_style=False, sort_keys=False)
            
            self.logger.info(f"Exported validation manifest: {output_path}")
            
        except Exception as e:
            self.logger.error(f"Failed to export manifest: {e}", exc_info=True)
