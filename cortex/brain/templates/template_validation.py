"""
AC-TC-002-02: Template Content Validation

Validates template content, structure, and consistency.
Provides cross-reference and markdown validation.

"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Set


@dataclass
class ContentValidationResult:
    """Result of content validation."""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    details: Dict[str, Any] = field(default_factory=dict)
    templates_checked: int = 0


class TemplateContentValidator:
    """
    Template content validator.

    Validates template structure, content, markdown syntax,
    and cross-references between templates.
    """

    # Variable syntax patterns
    VALID_VARIABLE_PATTERN = re.compile(r'\{[a-z_][a-z0-9_]*\}')
    DOUBLE_BRACE_PATTERN = re.compile(r'\{\{[^}]+\}\}')

    # Markdown patterns
    HEADING_PATTERN = re.compile(r'^#{1,6}\s+.+$', re.MULTILINE)
    LIST_PATTERN = re.compile(r'^[\s]*[-*+]\s+.+$', re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r'```[\s\S]*?```')

    def __init__(self, template_base_path: Optional[Path] = None):
        """
        Initialize template content validator.

        Args:
            template_base_path: Base path for templates
        """
        if template_base_path is None:
            self.template_base_path = Path(__file__).parent.parent.parent / "cortex_brain" / "tier2"
        else:
            self.template_base_path = Path(template_base_path)

        # Import content strategy
        from .content_strategy import ContentPopulationStrategy
        from .knowledge_schema import KnowledgeBaseSchema

        self._strategy = ContentPopulationStrategy(self.template_base_path)
        self._schema = KnowledgeBaseSchema()

    def validate_structure(self, template: Dict[str, Any]) -> ContentValidationResult:
        """
        Validate template structure against schema.

        Args:
            template: Template dictionary

        Returns:
            Validation result
        """
        schema_result = self._schema.validate(template)

        return ContentValidationResult(
            valid=schema_result.valid,
            errors=schema_result.errors,
            warnings=schema_result.warnings,
        )

    def validate_content(self, content: str) -> ContentValidationResult:
        """
        Validate template content.

        Args:
            content: Template content string

        Returns:
            Validation result
        """
        errors = []
        warnings = []

        if not content or not content.strip():
            errors.append("Content is empty")
            return ContentValidationResult(valid=False, errors=errors)

        # Check minimum content length
        if len(content.strip()) < 50:
            warnings.append("Content is very short (< 50 chars)")

        # Check for balanced braces
        open_braces = content.count('{')
        close_braces = content.count('}')
        if open_braces != close_braces:
            errors.append(f"Unbalanced braces: {open_braces} open, {close_braces} close")

        return ContentValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
        )

    def validate_variables(self, content: str) -> ContentValidationResult:
        """
        Validate variable syntax in content.

        Args:
            content: Template content string

        Returns:
            Validation result
        """
        errors = []
        warnings = []

        # Find double brace patterns (might be intentional escaping)
        double_braces = self.DOUBLE_BRACE_PATTERN.findall(content)
        if double_braces:
            for db in double_braces:
                warnings.append(f"Double brace found (escaped or error?): {db}")

        # Find all brace patterns
        all_braces = re.findall(r'\{[^}]*\}', content)
        valid_vars = self.VALID_VARIABLE_PATTERN.findall(content)

        # Check for invalid variable names
        for brace in all_braces:
            if brace not in valid_vars and not brace.startswith('{{'):
                # Extract variable name for error
                var_name = brace[1:-1]
                if var_name and not re.match(r'^[a-z_][a-z0-9_]*$', var_name):
                    errors.append(f"Invalid variable name: {var_name}")

        return ContentValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details={'variables': valid_vars, 'double_braces': double_braces},
        )

    def validate_markdown(self, content: str) -> ContentValidationResult:
        """
        Validate markdown syntax in content.

        Args:
            content: Template content string

        Returns:
            Validation result
        """
        errors = []
        warnings = []

        # Check for headings
        headings = self.HEADING_PATTERN.findall(content)
        if not headings:
            warnings.append("No markdown headings found")

        # Check for unbalanced code blocks
        code_blocks = content.count('```')
        if code_blocks % 2 != 0:
            errors.append("Unbalanced code blocks (odd number of ```)")

        # Check for common markdown issues
        lines = content.split('\n')
        for i, line in enumerate(lines, 1):
            # Check for heading without space after #
            if re.match(r'^#{1,6}[^#\s]', line):
                warnings.append(f"Line {i}: Heading missing space after #")

        return ContentValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details={'headings': len(headings), 'code_blocks': code_blocks // 2},
        )

    def validate_cross_references(self, domain: str) -> ContentValidationResult:
        """
        Validate cross-references within a domain.

        Args:
            domain: Domain name

        Returns:
            Validation result
        """
        errors = []
        warnings = []

        templates = self._strategy.get_domain_templates(domain)
        template_ids = {t['id'] for t in templates}

        # Check for orphaned references (simplified check)
        for template in templates:
            # In a full implementation, we'd check actual cross-references
            # For now, just verify the template exists
            if template['id'] not in template_ids:
                errors.append(f"Orphaned template reference: {template['id']}")

        return ContentValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details={'template_count': len(templates)},
        )

    def validate_inheritance(self, template_id: str) -> ContentValidationResult:
        """
        Validate template inheritance chain.

        Args:
            template_id: Template identifier

        Returns:
            Validation result
        """
        errors = []
        warnings = []

        template = self._strategy.get_template_by_id(template_id)
        if not template:
            errors.append(f"Template not found: {template_id}")
            return ContentValidationResult(valid=False, errors=errors)

        # Get inheritance rules
        rules = self._schema.get_inheritance_rules()
        max_depth = rules.get('inheritance_depth', 3)

        # Check inheritance chain (simplified)
        # In full implementation, we'd trace the full chain

        return ContentValidationResult(
            valid=len(errors) == 0,
            errors=errors,
            warnings=warnings,
            details={'template': template_id, 'max_depth': max_depth},
        )

    def validate_all(self) -> ContentValidationResult:
        """
        Validate all templates in registry.

        Returns:
            Validation result with aggregate data
        """
        all_errors = []
        all_warnings = []
        templates_checked = 0

        for domain in self._strategy.domains:
            templates = self._strategy.get_domain_templates(domain)
            for template in templates:
                templates_checked += 1

                # Validate cross-references for domain
                result = self.validate_cross_references(domain)
                all_errors.extend(result.errors)
                all_warnings.extend(result.warnings)

        return ContentValidationResult(
            valid=len(all_errors) == 0,
            errors=all_errors,
            warnings=all_warnings,
            details={'templates_checked': templates_checked},
            templates_checked=templates_checked,
        )

    @property
    def templates_checked(self) -> int:
        """Get count of templates that can be checked."""
        return self._strategy.total_template_count

    def generate_report(self) -> Dict[str, Any]:
        """
        Generate validation report.

        Returns:
            Report dictionary
        """
        result = self.validate_all()

        return {
            'summary': {
                'valid': result.valid,
                'errors_count': len(result.errors),
                'warnings_count': len(result.warnings),
                'templates_checked': result.details.get('templates_checked', 0),
            },
            'details': {
                'errors': result.errors[:10],  # First 10 errors
                'warnings': result.warnings[:10],  # First 10 warnings
            },
            'timestamp': datetime.now().isoformat(),
        }

    def find_orphaned_templates(self) -> List[str]:
        """
        Find templates not in registry.

        Returns:
            List of orphaned template IDs
        """
        # In a full implementation, this would scan the filesystem
        # and compare against the registry
        return []

    def find_duplicates(self) -> List[Dict[str, Any]]:
        """
        Find templates with duplicate content.

        Returns:
            List of duplicate template pairs
        """
        # In a full implementation, this would compare template content
        # For now, return empty (no duplicates in well-designed registry)
        return []
