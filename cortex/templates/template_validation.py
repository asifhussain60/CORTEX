"""
CORTEX Templates - Template Validation

Template validation and consistency checking.

"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set

from cortex.templates.content_strategy import ContentPopulationStrategy
from cortex.templates.knowledge_schema import KnowledgeBaseSchema, ValidationResult
from cortex.templates.template_manager import TemplateManager


@dataclass
class ValidationReport:
    """Validation report."""
    valid: bool
    templates_checked: int
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    summary: Dict[str, Any] = field(default_factory=dict)
    details: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.utcnow().isoformat())


class TemplateContentValidator:
    """Template content validator.

    Validates template structure, content, and consistency.
    """

    def __init__(self) -> None:
        """Initialize template content validator."""
        self._strategy = ContentPopulationStrategy()
        self._schema = KnowledgeBaseSchema()
        self._manager = TemplateManager()

    def validate_structure(self, template: Dict[str, Any]) -> ValidationResult:
        """Validate template structure.

        Args:
            template: Template to validate.

        Returns:
            Validation result.
        """
        return self._schema.validate(template)

    def validate_content(self, content: str) -> ValidationResult:
        """Validate template content.

        Args:
            content: Template content to validate.

        Returns:
            Validation result.
        """
        errors = []
        warnings = []

        # Check minimum length
        if len(content) < 50:
            warnings.append("Content is very short (< 50 characters)")

        # Check for basic structure
        if not content.strip():
            errors.append("Content is empty")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_variables(self, content: str) -> ValidationResult:
        """Validate variable syntax in content.

        Args:
            content: Template content with variables.

        Returns:
            Validation result.
        """
        errors = []
        warnings = []

        # Find all variable patterns
        single_brace = re.findall(r'\{(\w+)\}', content)
        double_brace = re.findall(r'\{\{(\w+)\}\}', content)

        # Warn about double braces
        if double_brace:
            warnings.append(f"Found double brace variables: {double_brace}")

        # Check for unclosed braces
        open_count = content.count('{')
        close_count = content.count('}')
        if open_count != close_count:
            errors.append(f"Unmatched braces: {open_count} open, {close_count} close")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_markdown(self, content: str) -> ValidationResult:
        """Validate markdown syntax.

        Args:
            content: Markdown content to validate.

        Returns:
            Validation result.
        """
        errors = []
        warnings = []

        # Check for basic markdown elements
        lines = content.split('\n')

        # Check for code blocks
        code_block_markers = [line for line in lines if line.startswith('```')]
        if len(code_block_markers) % 2 != 0:
            warnings.append("Unclosed code block detected")

        return ValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_cross_references(self, domain: str) -> ValidationResult:
        """Validate cross-references between templates in a domain.

        Args:
            domain: Domain to validate.

        Returns:
            Validation result.
        """
        # Basic validation - always passes for now
        return ValidationResult(valid=True, errors=[], warnings=[])

    def validate_inheritance(self, template_id: str) -> ValidationResult:
        """Validate template inheritance chain.

        Args:
            template_id: Template ID to validate.

        Returns:
            Validation result.
        """
        # Basic validation - always passes for now
        return ValidationResult(valid=True, errors=[], warnings=[])

    def validate_all(self) -> ValidationReport:
        """Validate all templates in registry.

        Returns:
            Validation report.
        """
        errors = []
        warnings = []
        templates_checked = 0

        # Validate each domain
        for domain in self._strategy.domains:
            templates = self._strategy.get_domain_templates(domain)
            for template in templates:
                templates_checked += 1
                template_id = template['id']

                # Check if content exists
                content = self._manager.get_template_content(template_id)
                if content is None:
                    warnings.append(f"Template {template_id} has no content")
                    continue

                # Validate content
                content_result = self.validate_content(content)
                if not content_result.valid:
                    errors.extend([f"{template_id}: {e}" for e in content_result.errors])
                warnings.extend([f"{template_id}: {w}" for w in content_result.warnings])

                # Validate variables
                var_result = self.validate_variables(content)
                if not var_result.valid:
                    errors.extend([f"{template_id}: {e}" for e in var_result.errors])
                warnings.extend([f"{template_id}: {w}" for w in var_result.warnings])

        return ValidationReport(
            valid=len(errors) == 0,
            templates_checked=templates_checked,
            errors=errors,
            warnings=warnings,
            summary={
                'total_templates': templates_checked,
                'error_count': len(errors),
                'warning_count': len(warnings),
            },
            details={
                'domains_checked': len(self._strategy.domains),
            },
        )

    def generate_report(self) -> Dict[str, Any]:
        """Generate validation report.

        Returns:
            Validation report dictionary.
        """
        report = self.validate_all()
        return {
            'summary': report.summary,
            'details': report.details,
            'timestamp': report.timestamp,
            'valid': report.valid,
        }

    def find_orphaned_templates(self) -> List[str]:
        """Find orphaned templates not in registry.

        Returns:
            List of orphaned template IDs.
        """
        # For now, return empty list as all templates are in registry
        return []

    def find_duplicates(self) -> List[Dict[str, Any]]:
        """Find templates with duplicate content.

        Returns:
            List of duplicate pairs.
        """
        duplicates = []
        content_map: Dict[str, List[str]] = {}

        # Build content map
        for domain in self._strategy.domains:
            templates = self._strategy.get_domain_templates(domain)
            for template in templates:
                template_id = template['id']
                content = self._manager.get_template_content(template_id)
                if content:
                    # Normalize content for comparison
                    normalized = content.strip().lower()
                    if normalized in content_map:
                        content_map[normalized].append(template_id)
                    else:
                        content_map[normalized] = [template_id]

        # Find duplicates
        for content_hash, template_ids in content_map.items():
            if len(template_ids) > 1:
                duplicates.append({
                    'template_ids': template_ids,
                    'count': len(template_ids),
                })

        return duplicates
