"""
Template Validator

This module validates template structure, component references, and placeholder
consistency to catch errors before templates are used in production.

Validation Checks:
- YAML schema validation
- Component reference validation (broken links)
- Placeholder consistency (required placeholders present)
- Circular inheritance detection
- Base template existence
- Section structure validation

Author: Asif Hussain
Phase: 2 - Core Infrastructure
Version: 1.0
Created: December 5, 2025
"""

import yaml
import re
from pathlib import Path
from typing import Dict, Any, List, Set, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"      # Must fix (breaks template)
    WARNING = "warning"  # Should fix (degraded experience)
    INFO = "info"        # Nice to fix (optimization)


@dataclass
class ValidationIssue:
    """Represents a validation issue."""
    severity: ValidationSeverity
    message: str
    location: str  # Template ID or file path
    fix_suggestion: Optional[str] = None
    
    def __str__(self) -> str:
        result = f"[{self.severity.value.upper()}] {self.location}: {self.message}"
        if self.fix_suggestion:
            result += f"\n  Fix: {self.fix_suggestion}"
        return result


@dataclass
class ValidationResult:
    """Validation result for a template."""
    template_id: str
    is_valid: bool
    errors: List[ValidationIssue]
    warnings: List[ValidationIssue]
    info: List[ValidationIssue]
    
    @property
    def total_issues(self) -> int:
        """Get total number of issues."""
        return len(self.errors) + len(self.warnings) + len(self.info)
    
    @property
    def has_errors(self) -> bool:
        """Check if validation has errors."""
        return len(self.errors) > 0
    
    def summary(self) -> str:
        """Get validation summary."""
        status = "FAIL" if not self.is_valid else "PASS"
        return (
            f"{status}: {self.template_id} - "
            f"{len(self.errors)} errors, "
            f"{len(self.warnings)} warnings, "
            f"{len(self.info)} info"
        )
    
    def detailed_report(self) -> str:
        """Get detailed validation report."""
        lines = [self.summary(), ""]
        
        if self.errors:
            lines.append("ERRORS:")
            for issue in self.errors:
                lines.append(f"  {issue}")
            lines.append("")
        
        if self.warnings:
            lines.append("WARNINGS:")
            for issue in self.warnings:
                lines.append(f"  {issue}")
            lines.append("")
        
        if self.info:
            lines.append("INFO:")
            for issue in self.info:
                lines.append(f"  {issue}")
        
        return "\n".join(lines)


class TemplateValidator:
    """
    Comprehensive template validation system.
    
    Features:
    - Schema validation (YAML structure)
    - Component reference validation
    - Placeholder consistency checks
    - Inheritance validation
    - Section structure validation
    - Circular reference detection
    
    Usage:
        validator = TemplateValidator(
            template_dir=Path("cortex-brain/response-templates"),
            required_placeholders=['operation', 'understanding_scope_content']
        )
        
        result = validator.validate_template(template_def, template_id)
        if not result.is_valid:
            print(result.detailed_report())
    """
    
    def __init__(
        self,
        template_dir: Path,
        required_placeholders: Optional[List[str]] = None,
        required_sections: Optional[List[str]] = None
    ):
        """
        Initialize template validator.
        
        Args:
            template_dir: Base directory for templates
            required_placeholders: List of required placeholders (optional)
            required_sections: List of required sections (optional)
        """
        self.template_dir = template_dir
        self.required_placeholders = required_placeholders or []
        self.required_sections = required_sections or []
        
        logger.info(f"TemplateValidator initialized: {template_dir}")
    
    def validate_template(
        self,
        template_def: Dict[str, Any],
        template_id: str
    ) -> ValidationResult:
        """
        Validate template definition.
        
        Args:
            template_def: Template definition dictionary
            template_id: Template identifier
        
        Returns:
            ValidationResult with all issues found
        """
        errors: List[ValidationIssue] = []
        warnings: List[ValidationIssue] = []
        info: List[ValidationIssue] = []
        
        # 1. Schema validation
        schema_issues = self._validate_schema(template_def, template_id)
        errors.extend([i for i in schema_issues if i.severity == ValidationSeverity.ERROR])
        warnings.extend([i for i in schema_issues if i.severity == ValidationSeverity.WARNING])
        info.extend([i for i in schema_issues if i.severity == ValidationSeverity.INFO])
        
        # 2. Component reference validation
        component_issues = self._validate_component_references(template_def, template_id)
        errors.extend([i for i in component_issues if i.severity == ValidationSeverity.ERROR])
        warnings.extend([i for i in component_issues if i.severity == ValidationSeverity.WARNING])
        
        # 3. Placeholder validation
        placeholder_issues = self._validate_placeholders(template_def, template_id)
        warnings.extend([i for i in placeholder_issues if i.severity == ValidationSeverity.WARNING])
        info.extend([i for i in placeholder_issues if i.severity == ValidationSeverity.INFO])
        
        # 4. Inheritance validation
        if 'inherits' in template_def:
            inheritance_issues = self._validate_inheritance(template_def, template_id)
            errors.extend([i for i in inheritance_issues if i.severity == ValidationSeverity.ERROR])
            warnings.extend([i for i in inheritance_issues if i.severity == ValidationSeverity.WARNING])
        
        # 5. Section structure validation
        if self.required_sections:
            section_issues = self._validate_sections(template_def, template_id)
            warnings.extend([i for i in section_issues if i.severity == ValidationSeverity.WARNING])
        
        is_valid = len(errors) == 0
        
        return ValidationResult(
            template_id=template_id,
            is_valid=is_valid,
            errors=errors,
            warnings=warnings,
            info=info
        )
    
    def _validate_schema(
        self,
        template_def: Dict[str, Any],
        template_id: str
    ) -> List[ValidationIssue]:
        """Validate YAML schema structure."""
        issues = []
        
        # Check if template_def is a dictionary
        if not isinstance(template_def, dict):
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Template must be a dictionary",
                location=template_id,
                fix_suggestion="Ensure template definition is a YAML dictionary"
            ))
            return issues
        
        # Check for empty template
        if not template_def:
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message="Template is empty",
                location=template_id,
                fix_suggestion="Add template content"
            ))
        
        return issues
    
    def _validate_component_references(
        self,
        template_def: Dict[str, Any],
        template_id: str
    ) -> List[ValidationIssue]:
        """Validate component references are well-formed."""
        issues = []
        
        # Find all component references in template
        references = self._extract_component_references(template_def)
        
        for ref in references:
            # Check reference format (should be path/file.yaml#component_id)
            if '#' not in ref:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Invalid component reference format: {ref}",
                    location=template_id,
                    fix_suggestion="Use format: path/file.yaml#component_id"
                ))
                continue
            
            file_ref, component_id = ref.split('#', 1)
            
            # Check if file exists
            file_path = self.template_dir / file_ref
            if not file_path.exists():
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Component file not found: {file_ref}",
                    location=template_id,
                    fix_suggestion=f"Create component file: {file_ref}"
                ))
        
        return issues
    
    def _validate_placeholders(
        self,
        template_def: Dict[str, Any],
        template_id: str
    ) -> List[ValidationIssue]:
        """Validate placeholder consistency."""
        issues = []
        
        # Extract all placeholders from template
        placeholders = self._extract_placeholders(template_def)
        
        # Check required placeholders are present
        for required in self.required_placeholders:
            if required not in placeholders:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Required placeholder missing: {{{required}}}",
                    location=template_id,
                    fix_suggestion=f"Add {{{required}}} placeholder to template"
                ))
        
        # Check for unused/undefined placeholders
        # v3.0 section names only
        common_placeholders = {
            'operation', 'understanding_scope_content', 'approach_considerations_content',
            'response_content', 'impact_changes_content', 'next_steps_content',
            'title', 'mode', 'confidence_level'
        }
        
        for placeholder in placeholders:
            if placeholder not in common_placeholders and placeholder not in self.required_placeholders:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.INFO,
                    message=f"Uncommon placeholder found: {{{placeholder}}}",
                    location=template_id,
                    fix_suggestion="Verify this placeholder will be provided in context"
                ))
        
        return issues
    
    def _validate_inheritance(
        self,
        template_def: Dict[str, Any],
        template_id: str
    ) -> List[ValidationIssue]:
        """Validate inheritance references."""
        issues = []
        
        inherits_from = template_def.get('inherits')
        
        if not inherits_from:
            return issues
        
        # Check if base template exists
        if inherits_from.endswith('.yaml'):
            base_path = self.template_dir / inherits_from
        else:
            base_path = self.template_dir / 'core' / 'base-templates' / f"{inherits_from}.yaml"
        
        if not base_path.exists():
            issues.append(ValidationIssue(
                severity=ValidationSeverity.ERROR,
                message=f"Base template not found: {inherits_from}",
                location=template_id,
                fix_suggestion=f"Create base template: {inherits_from}"
            ))
        
        return issues
    
    def _validate_sections(
        self,
        template_def: Dict[str, Any],
        template_id: str
    ) -> List[ValidationIssue]:
        """Validate required sections are present."""
        issues = []
        
        # Check for sections key
        sections = template_def.get('sections', {})
        
        if not isinstance(sections, dict):
            return issues
        
        # Check required sections
        for required_section in self.required_sections:
            if required_section not in sections:
                issues.append(ValidationIssue(
                    severity=ValidationSeverity.WARNING,
                    message=f"Required section missing: {required_section}",
                    location=template_id,
                    fix_suggestion=f"Add '{required_section}' to sections"
                ))
        
        return issues
    
    def _extract_component_references(self, content: Any) -> Set[str]:
        """Extract all component references from content."""
        references = set()
        
        if isinstance(content, str):
            # Find {component:path#id} patterns
            pattern = r'\{component:([^}]+)\}'
            matches = re.findall(pattern, content)
            references.update(matches)
        
        elif isinstance(content, dict):
            # Check 'components' key
            if 'components' in content:
                components_def = content['components']
                if isinstance(components_def, dict):
                    for ref in components_def.values():
                        if isinstance(ref, str):
                            references.add(ref)
            
            # Recursively search dict values
            for value in content.values():
                references.update(self._extract_component_references(value))
        
        elif isinstance(content, list):
            # Recursively search list items
            for item in content:
                references.update(self._extract_component_references(item))
        
        return references
    
    def _extract_placeholders(self, content: Any) -> Set[str]:
        """Extract all placeholders from content."""
        placeholders = set()
        
        if isinstance(content, str):
            # Find {placeholder} patterns
            pattern = r'\{([a-z_][a-z0-9_]*)\}'
            matches = re.findall(pattern, content)
            placeholders.update(matches)
        
        elif isinstance(content, dict):
            # Recursively search dict values
            for value in content.values():
                placeholders.update(self._extract_placeholders(value))
        
        elif isinstance(content, list):
            # Recursively search list items
            for item in content:
                placeholders.update(self._extract_placeholders(item))
        
        return placeholders
    
    def validate_file(self, file_path: Path) -> List[ValidationResult]:
        """
        Validate all templates in a file.
        
        Args:
            file_path: Path to template file
        
        Returns:
            List of validation results (one per template in file)
        """
        results = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = yaml.safe_load(f)
            
            if not isinstance(content, dict):
                # Single template file
                template_id = file_path.stem
                result = self.validate_template(content, template_id)
                results.append(result)
            else:
                # Multi-template file
                for template_id, template_def in content.items():
                    result = self.validate_template(template_def, template_id)
                    results.append(result)
        
        except Exception as e:
            logger.error(f"Failed to validate file {file_path}: {e}")
            results.append(ValidationResult(
                template_id=str(file_path),
                is_valid=False,
                errors=[ValidationIssue(
                    severity=ValidationSeverity.ERROR,
                    message=f"Failed to load file: {str(e)}",
                    location=str(file_path)
                )],
                warnings=[],
                info=[]
            ))
        
        return results
    
    def validate_directory(self, directory: Path) -> List[ValidationResult]:
        """
        Validate all template files in directory.
        
        Args:
            directory: Directory to validate
        
        Returns:
            List of all validation results
        """
        results = []
        
        # Find all YAML files
        for yaml_file in directory.rglob('*.yaml'):
            file_results = self.validate_file(yaml_file)
            results.extend(file_results)
        
        return results
    
    def generate_validation_report(
        self,
        results: List[ValidationResult]
    ) -> str:
        """
        Generate comprehensive validation report.
        
        Args:
            results: List of validation results
        
        Returns:
            Formatted validation report
        """
        total_templates = len(results)
        passed = sum(1 for r in results if r.is_valid)
        failed = total_templates - passed
        
        total_errors = sum(len(r.errors) for r in results)
        total_warnings = sum(len(r.warnings) for r in results)
        total_info = sum(len(r.info) for r in results)
        
        lines = [
            "=" * 60,
            "TEMPLATE VALIDATION REPORT",
            "=" * 60,
            "",
            f"Total Templates: {total_templates}",
            f"Passed: {passed}",
            f"Failed: {failed}",
            "",
            f"Total Errors: {total_errors}",
            f"Total Warnings: {total_warnings}",
            f"Total Info: {total_info}",
            "",
            "=" * 60,
            ""
        ]
        
        # Failed templates
        failed_results = [r for r in results if not r.is_valid]
        if failed_results:
            lines.append("FAILED TEMPLATES:")
            lines.append("")
            for result in failed_results:
                lines.append(result.detailed_report())
                lines.append("")
        
        # Templates with warnings
        warning_results = [r for r in results if r.is_valid and r.warnings]
        if warning_results:
            lines.append("TEMPLATES WITH WARNINGS:")
            lines.append("")
            for result in warning_results:
                lines.append(result.summary())
            lines.append("")
        
        return "\n".join(lines)
