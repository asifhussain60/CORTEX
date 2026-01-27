"""
Template Validator (AC-TT-003-01)

Validates orchestrator templates for consistency and completeness.
Provides:
- Schema validation
- Cross-reference validation
- Best practices checking
- Compliance reporting

Works with ParsedTemplate from template_parser.
"""

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Callable, Pattern, Union
import re
from datetime import datetime




@dataclass
class ValidationError:
    """A validation error or warning."""
    level: ValidationLevel
    code: str
    message: str
    location: Optional[str] = None
    suggestion: Optional[str] = None
    rule: Optional[str] = None
    
    def __str__(self) -> str:
        prefix = self.level.name
        location = f" at {self.location}" if self.location else ""
        return f"[{prefix}] {self.code}: {self.message}{location}"


@dataclass
class ValidationResult:
    """Result of template validation."""
    valid: bool = True
    errors: List[ValidationError] = field(default_factory=list)
    checked_rules: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_error(
        self,
        level: ValidationLevel,
        code: str,
        message: str,
        **kwargs,
    ) -> None:
        """Add a validation error."""
        error = ValidationError(level=level, code=code, message=message, **kwargs)
        self.errors.append(error)
        if level == ValidationLevel.ERROR:
            self.valid = False
    
    def add_rule(self, rule: str) -> None:
        """Record that a rule was checked."""
        self.checked_rules.append(rule)
    
    @property
    def error_count(self) -> int:
        """Count of errors."""
        return sum(1 for e in self.errors if e.level == ValidationLevel.ERROR)
    
    @property
    def warning_count(self) -> int:
        """Count of warnings."""
        return sum(1 for e in self.errors if e.level == ValidationLevel.WARNING)
    
    def get_by_level(self, level: ValidationLevel) -> List[ValidationError]:
        """Get errors by level."""
        return [e for e in self.errors if e.level == level]
    
    def merge(self, other: 'ValidationResult') -> None:
        """Merge another validation result."""
        self.errors.extend(other.errors)
        self.checked_rules.extend(other.checked_rules)
        if not other.valid:
            self.valid = False


@dataclass
class ComplianceReport:
    """Full compliance report for a template or set of templates."""
    template_name: str
    validation_result: ValidationResult
    coverage_score: float  # 0-100
    compliance_level: str  # 'full', 'partial', 'non-compliant'
    recommendations: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)
    
    @classmethod
    def from_validation(
        cls,
        template_name: str,
        result: ValidationResult,
    ) -> 'ComplianceReport':
        """Create report from validation result."""
        # Calculate coverage
        rules_passed = len(result.checked_rules) - result.error_count
        coverage = (rules_passed / len(result.checked_rules) * 100) if result.checked_rules else 100.0
        
        # Determine compliance level
        if result.valid and result.error_count == 0:
            if result.warning_count == 0:
                level = 'full'
            else:
                level = 'partial'
        else:
            level = 'non-compliant'
        
        # Generate recommendations
        recommendations = []
        for error in result.errors:
            if error.suggestion:
                recommendations.append(error.suggestion)
        
        return cls(
            template_name=template_name,
            validation_result=result,
            coverage_score=coverage,
            compliance_level=level,
            recommendations=recommendations,
        )


# Validation Rules

class ValidationRule:
    """Base class for validation rules."""
    
    code: str = "RULE-000"
    name: str = "Base Rule"
    description: str = "Base validation rule"
    level: ValidationLevel = ValidationLevel.ERROR
    
    def validate(self, template: Any, context: Dict[str, Any]) -> List[ValidationError]:
        """Validate the template. Override in subclass."""
        return []


class RequiredFieldsRule(ValidationRule):
    """Check for required fields."""
    
    code = "VR-001"
    name = "Required Fields"
    description = "Validates that all required fields are present"
    
    REQUIRED_FIELDS = ['name', 'domain', 'version']
    
    def validate(self, template: Any, context: Dict[str, Any]) -> List[ValidationError]:
        errors = []
        for field in self.REQUIRED_FIELDS:
            value = getattr(template, field, None) if hasattr(template, field) else template.get(field)
            if not value:
                errors.append(ValidationError(
                    level=ValidationLevel.ERROR,
                    code=f"{self.code}-MISSING",
                    message=f"Required field '{field}' is missing or empty",
                    rule=self.name,
                    suggestion=f"Add a '{field}' field to the template",
                ))
        return errors


class NamingConventionRule(ValidationRule):
    """Check naming conventions."""
    
    code = "VR-002"
    name = "Naming Conventions"
    description = "Validates that names follow conventions"
    level = ValidationLevel.WARNING
    
    NAME_PATTERN = re.compile(r'^[a-zA-Z][a-zA-Z0-9_-]*$')
    
    def validate(self, template: Any, context: Dict[str, Any]) -> List[ValidationError]:
        errors = []
        name = getattr(template, 'name', None) if hasattr(template, 'name') else template.get('name', '')
        
        if name and not self.NAME_PATTERN.match(name):
            errors.append(ValidationError(
                level=self.level,
                code=f"{self.code}-INVALID",
                message=f"Name '{name}' doesn't follow naming conventions",
                rule=self.name,
                suggestion="Use alphanumeric characters, underscores, or hyphens",
            ))
        
        return errors


class VersionFormatRule(ValidationRule):
    """Check version format."""
    
    code = "VR-003"
    name = "Version Format"
    description = "Validates semantic version format"
    level = ValidationLevel.WARNING
    
    VERSION_PATTERN = re.compile(r'^\d+\.\d+\.\d+(-[a-zA-Z0-9]+)?$')
    
    def validate(self, template: Any, context: Dict[str, Any]) -> List[ValidationError]:
        errors = []
        version = getattr(template, 'version', None) if hasattr(template, 'version') else template.get('version', '')
        
        if version and not self.VERSION_PATTERN.match(str(version)):
            errors.append(ValidationError(
                level=self.level,
                code=f"{self.code}-INVALID",
                message=f"Version '{version}' doesn't follow semantic versioning",
                rule=self.name,
                suggestion="Use format: MAJOR.MINOR.PATCH (e.g., 1.0.0)",
            ))
        
        return errors


class ParameterValidationRule(ValidationRule):
    """Validate parameter definitions."""
    
    code = "VR-004"
    name = "Parameter Validation"
    description = "Validates parameter definitions"
    
    VALID_TYPES = {'str', 'string', 'int', 'integer', 'float', 'number', 'bool', 'boolean', 'list', 'array', 'dict', 'object', 'any'}
    
    def validate(self, template: Any, context: Dict[str, Any]) -> List[ValidationError]:
        errors = []
        
        # Get parameters section
        if hasattr(template, 'get_section'):
            params_section = template.get_section('parameters')
            params = params_section.content if params_section else {}
        elif isinstance(template, dict):
            params = template.get('parameters', {})
        else:
            params = {}
        
        for name, config in params.items():
            if isinstance(config, dict):
                param_type = config.get('type', '').lower()
                if param_type and param_type not in self.VALID_TYPES:
                    errors.append(ValidationError(
                        level=ValidationLevel.WARNING,
                        code=f"{self.code}-TYPE",
                        message=f"Parameter '{name}' has unknown type: {param_type}",
                        location=f"parameters.{name}",
                        rule=self.name,
                        suggestion=f"Use one of: {', '.join(sorted(self.VALID_TYPES))}",
                    ))
                
                if 'description' not in config:
                    errors.append(ValidationError(
                        level=ValidationLevel.INFO,
                        code=f"{self.code}-DESC",
                        message=f"Parameter '{name}' has no description",
                        location=f"parameters.{name}",
                        rule=self.name,
                        suggestion="Add a description for better documentation",
                    ))
        
        return errors


class StageValidationRule(ValidationRule):
    """Validate stage definitions."""
    
    code = "VR-005"
    name = "Stage Validation"
    description = "Validates stage definitions"
    
    def validate(self, template: Any, context: Dict[str, Any]) -> List[ValidationError]:
        errors = []
        
        # Get stages section
        if hasattr(template, 'get_section'):
            stages_section = template.get_section('stages')
            stages = stages_section.content.get('stages', []) if stages_section else []
        elif isinstance(template, dict):
            stages_data = template.get('stages', {})
            stages = stages_data.get('stages', []) if isinstance(stages_data, dict) else stages_data
        else:
            stages = []
        
        seen_names = set()
        for i, stage in enumerate(stages):
            if not isinstance(stage, dict):
                errors.append(ValidationError(
                    level=ValidationLevel.ERROR,
                    code=f"{self.code}-FORMAT",
                    message=f"Stage {i} is not a valid mapping",
                    location=f"stages[{i}]",
                    rule=self.name,
                ))
                continue
            
            name = stage.get('name')
            if not name:
                errors.append(ValidationError(
                    level=ValidationLevel.ERROR,
                    code=f"{self.code}-NAME",
                    message=f"Stage {i} has no name",
                    location=f"stages[{i}]",
                    rule=self.name,
                    suggestion="Add a 'name' field to identify the stage",
                ))
            elif name in seen_names:
                errors.append(ValidationError(
                    level=ValidationLevel.ERROR,
                    code=f"{self.code}-DUPLICATE",
                    message=f"Duplicate stage name: {name}",
                    location=f"stages[{i}]",
                    rule=self.name,
                    suggestion="Use unique names for each stage",
                ))
            else:
                seen_names.add(name)
        
        return errors


class HookValidationRule(ValidationRule):
    """Validate hook definitions."""
    
    code = "VR-006"
    name = "Hook Validation"
    description = "Validates hook definitions"
    level = ValidationLevel.INFO
    
    STANDARD_HOOKS = {'pre_execute', 'post_execute', 'on_success', 'on_error', 'on_failure'}
    
    def validate(self, template: Any, context: Dict[str, Any]) -> List[ValidationError]:
        errors = []
        
        # Get hooks section
        if hasattr(template, 'get_section'):
            hooks_section = template.get_section('hooks')
            hooks = hooks_section.content if hooks_section else {}
        elif isinstance(template, dict):
            hooks = template.get('hooks', {})
        else:
            hooks = {}
        
        for hook_name in hooks.keys():
            if hook_name not in self.STANDARD_HOOKS:
                errors.append(ValidationError(
                    level=self.level,
                    code=f"{self.code}-CUSTOM",
                    message=f"Custom hook defined: {hook_name}",
                    location=f"hooks.{hook_name}",
                    rule=self.name,
                    suggestion=f"Standard hooks are: {', '.join(sorted(self.STANDARD_HOOKS))}",
                ))
        
        return errors


class DependencyValidationRule(ValidationRule):
    """Validate dependencies between sections."""
    
    code = "VR-007"
    name = "Dependency Validation"
    description = "Validates cross-references between sections"
    level = ValidationLevel.WARNING
    
    def validate(self, template: Any, context: Dict[str, Any]) -> List[ValidationError]:
        errors = []
        
        # Get sections
        if hasattr(template, 'get_section'):
            params_section = template.get_section('parameters')
            stages_section = template.get_section('stages')
            param_names = set(params_section.content.keys()) if params_section else set()
            stages = stages_section.content.get('stages', []) if stages_section else []
        elif isinstance(template, dict):
            param_names = set(template.get('parameters', {}).keys())
            stages_data = template.get('stages', {})
            stages = stages_data.get('stages', []) if isinstance(stages_data, dict) else stages_data
        else:
            return errors
        
        # Check stage references to parameters
        for i, stage in enumerate(stages):
            if not isinstance(stage, dict):
                continue
            
            self._check_references(stage, param_names, f"stages[{i}]", errors)
        
        return errors
    
    def _check_references(
        self,
        obj: Any,
        valid_params: Set[str],
        location: str,
        errors: List[ValidationError],
    ) -> None:
        """Recursively check for parameter references."""
        if isinstance(obj, str):
            # Check for $params.xxx references
            matches = re.findall(r'\$(?:params?|parameters?)\.(\w+)', obj)
            for param_ref in matches:
                if param_ref not in valid_params:
                    errors.append(ValidationError(
                        level=self.level,
                        code=f"{self.code}-REF",
                        message=f"Reference to undefined parameter: {param_ref}",
                        location=location,
                        rule=self.name,
                        suggestion=f"Define parameter '{param_ref}' or fix the reference",
                    ))
        elif isinstance(obj, dict):
            for key, value in obj.items():
                self._check_references(value, valid_params, f"{location}.{key}", errors)
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                self._check_references(item, valid_params, f"{location}[{i}]", errors)


class TemplateValidator:
    """
    Validator for orchestrator templates.
    
    Runs validation rules against templates and produces reports.
    
    Example:
        validator = TemplateValidator()
        result = validator.validate(template)
        
        if not result.valid:
            for error in result.errors:
                print(error)
        
        report = validator.generate_report(template)
    """
    
    DEFAULT_RULES = [
        RequiredFieldsRule(),
        NamingConventionRule(),
        VersionFormatRule(),
        ParameterValidationRule(),
        StageValidationRule(),
        HookValidationRule(),
        DependencyValidationRule(),
    ]
    
    def __init__(self, rules: Optional[List[ValidationRule]] = None):
        """
        Initialize validator.
        
        Args:
            rules: Custom validation rules (uses defaults if not provided)
        """
        self.rules = rules or self.DEFAULT_RULES.copy()
        self._context: Dict[str, Any] = {}
    
    def add_rule(self, rule: ValidationRule) -> None:
        """Add a validation rule."""
        self.rules.append(rule)
    
    def remove_rule(self, code: str) -> bool:
        """Remove a rule by code."""
        for i, rule in enumerate(self.rules):
            if rule.code == code:
                self.rules.pop(i)
                return True
        return False
    
    def set_context(self, key: str, value: Any) -> None:
        """Set context value for validation."""
        self._context[key] = value
    
    def validate(
        self,
        template: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Validate a template.
        
        Args:
            template: Template to validate (ParsedTemplate or dict)
            context: Additional validation context
            
        Returns:
            ValidationResult with errors and warnings
        """
        result = ValidationResult()
        ctx = {**self._context, **(context or {})}
        
        for rule in self.rules:
            result.add_rule(rule.name)
            try:
                errors = rule.validate(template, ctx)
                for error in errors:
                    result.errors.append(error)
                    if error.level == ValidationLevel.ERROR:
                        result.valid = False
            except Exception as e:
                result.add_error(
                    ValidationLevel.ERROR,
                    f"{rule.code}-EXCEPTION",
                    f"Rule '{rule.name}' raised exception: {e}",
                    rule=rule.name,
                )
        
        return result
    
    def validate_file(
        self,
        path: Union[Path, str],
        context: Optional[Dict[str, Any]] = None,
    ) -> ValidationResult:
        """
        Validate a template file.
        
        Args:
            path: Path to template file
            context: Additional validation context
            
        Returns:
            ValidationResult
        """
        import yaml
from cortex.models.canonical_enums import ValidationLevel
        
        path = Path(path)
        result = ValidationResult()
        
        if not path.exists():
            result.add_error(
                ValidationLevel.ERROR,
                "FILE-001",
                f"Template file not found: {path}",
            )
            return result
        
        try:
            content = path.read_text()
            template = yaml.safe_load(content)
        except yaml.YAMLError as e:
            result.add_error(
                ValidationLevel.ERROR,
                "FILE-002",
                f"YAML parsing error: {e}",
            )
            return result
        except Exception as e:
            result.add_error(
                ValidationLevel.ERROR,
                "FILE-003",
                f"Error reading file: {e}",
            )
            return result
        
        return self.validate(template, context)
    
    def validate_multiple(
        self,
        templates: List[Any],
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, ValidationResult]:
        """
        Validate multiple templates.
        
        Args:
            templates: List of templates to validate
            context: Additional validation context
            
        Returns:
            Dict mapping template names to results
        """
        results = {}
        for template in templates:
            name = getattr(template, 'name', None) or template.get('name', 'unnamed')
            results[name] = self.validate(template, context)
        return results
    
    def generate_report(
        self,
        template: Any,
        context: Optional[Dict[str, Any]] = None,
    ) -> ComplianceReport:
        """
        Generate a compliance report for a template.
        
        Args:
            template: Template to validate
            context: Additional validation context
            
        Returns:
            ComplianceReport
        """
        result = self.validate(template, context)
        name = getattr(template, 'name', None) or template.get('name', 'unnamed')
        return ComplianceReport.from_validation(name, result)
    
    def check_compliance(
        self,
        template: Any,
        required_level: str = 'partial',
    ) -> bool:
        """
        Check if template meets compliance level.
        
        Args:
            template: Template to check
            required_level: Required compliance level ('full', 'partial')
            
        Returns:
            True if compliant
        """
        report = self.generate_report(template)
        
        if required_level == 'full':
            return report.compliance_level == 'full'
        elif required_level == 'partial':
            return report.compliance_level in ('full', 'partial')
        else:
            return report.compliance_level != 'non-compliant'


# Convenience functions

def validate_template(template: Any) -> ValidationResult:
    """Quick validation of a template."""
    validator = TemplateValidator()
    return validator.validate(template)


def validate_template_file(path: Union[Path, str]) -> ValidationResult:
    """Quick validation of a template file."""
    validator = TemplateValidator()
    return validator.validate_file(path)


def is_valid_template(template: Any) -> bool:
    """Check if template is valid."""
    result = validate_template(template)
    return result.valid
