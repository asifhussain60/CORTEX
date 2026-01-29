"""
Response Header Injector

Composition layer that wraps ResponseTemplateEngine to inject
CORTEX headers into all responses. Non-invasive decorator pattern.

This module implements header/footer injection as a separate concern,
allowing ResponseTemplateEngine to remain focused on template rendering.

Classes:
    ResponseHeaderInjector: Main injector that wraps template engine
"""

from typing import Dict, Any, Optional
from datetime import datetime
from .response_header_config import HeaderConfigurationManager
from cortex.core.response_template_engine import ResponseTemplateEngine
import re
import yaml


# =============================================================================
# SANITIZATION HELPER FUNCTIONS (AC-FIX-004-01: Prompt Injection Prevention)
# =============================================================================

def escape_yaml_string(value: str) -> str:
    """
    Escape a string to be safe for YAML value contexts.
    
    Prevents prompt injection attacks by escaping YAML special characters.
    Special characters that need escaping in YAML:
    - : (colon) - indicates key/value pairs
    - - (dash) - indicates list items
    - ? (question mark) - explicit keys
    - [ ] (brackets) - flow sequences
    - { } (braces) - flow mappings
    - , (comma) - flow separators
    - & (ampersand) - anchors
    - * (asterisk) - aliases
    - # (hash) - comments
    - | (pipe) - block scalars
    - > (greater) - folded scalars
    
    Strategy: Quote the entire string if it contains any special characters.
    This ensures the entire value is treated as a literal string.
    
    Args:
        value: String value to escape
        
    Returns:
        Escaped string safe for YAML contexts
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Check if string contains any YAML special characters
    yaml_special_chars = r'[:\-\?[\]{},&*#|>\'\"@`]|^-|^---'
    
    if re.search(yaml_special_chars, value) or value.startswith(' ') or value.endswith(' '):
        # Quote the string to treat it as a literal
        # Escape any quotes within the string
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    
    return value


def validate_ac_id(ac_id: str) -> bool:
    """
    Validate AC-ID format against whitelist pattern.
    
    Valid formats:
    - AC-FIX-001-01
    - AC-DOC-007-01
    - AC-MINOR-008-01
    - CORE-001
    - FINDING-001
    
    Args:
        ac_id: AC-ID string to validate
        
    Returns:
        True if valid format, False otherwise
    """
    # Allow alphanumeric and hyphens, but nothing else
    if not isinstance(ac_id, str):
        return False
    
    # Pattern: Uppercase letters, numbers, hyphens only
    # Must start and end with alphanumeric
    pattern = r'^[A-Z][A-Z0-9]*([-][A-Z0-9]+)*$'
    return bool(re.match(pattern, ac_id))


def validate_operation_name(operation: str) -> bool:
    """
    Validate operation name against whitelist.
    
    Valid operations (from typical governance domains):
    create, read, update, delete, execute, query, backup, restore, validate, etc.
    
    Args:
        operation: Operation name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(operation, str):
        return False
    
    # Allow lowercase alphanumeric and underscores only
    pattern = r'^[a-z][a-z0-9_]{0,31}$'
    return bool(re.match(pattern, operation))


def validate_domain_name(domain: str) -> bool:
    """
    Validate domain name against whitelist.
    
    Valid domains: governance, security, compliance, operations, infrastructure
    
    Args:
        domain: Domain name to validate
        
    Returns:
        True if valid, False otherwise
    """
    if not isinstance(domain, str):
        return False
    
    # Allow lowercase alphanumeric and underscores only
    pattern = r'^[a-z][a-z0-9_]{0,31}$'
    return bool(re.match(pattern, domain))


def sanitize_context_value(var_name: str, value: Any, is_mandatory: bool = False) -> str:
    """
    Sanitize a context value before interpolation.
    
    Strategy:
    1. For known fields with whitelists (ac_id, operation_name, domain),
       validate against whitelist
    2. For all values, apply YAML-safe escaping
    3. Reject if whitelist validation fails (for mandatory fields)
    
    Args:
        var_name: Variable name to determine validation rules
        value: Value to sanitize
        is_mandatory: Whether this is a mandatory variable
        
    Returns:
        Sanitized, escaped string value
        
    Raises:
        ValueError: If whitelist validation fails for mandatory field
    """
    if value is None:
        return ""
    
    value_str = str(value)
    
    # Apply whitelist validation for known fields
    if var_name.lower() in ('ac_id', 'ac-id', 'acid'):
        if not validate_ac_id(value_str):
            msg = f"Invalid AC-ID format: {value_str}"
            if is_mandatory:
                raise ValueError(msg)
            # For optional, log warning but continue
            value_str = escape_yaml_string(value_str)
        else:
            value_str = escape_yaml_string(value_str)
    
    elif var_name.lower() in ('operation_name', 'operation', 'op_name'):
        if not validate_operation_name(value_str):
            msg = f"Invalid operation name: {value_str}"
            if is_mandatory:
                raise ValueError(msg)
            value_str = escape_yaml_string(value_str)
        else:
            value_str = escape_yaml_string(value_str)
    
    elif var_name.lower() in ('domain_name', 'domain'):
        if not validate_domain_name(value_str):
            msg = f"Invalid domain name: {value_str}"
            if is_mandatory:
                raise ValueError(msg)
            value_str = escape_yaml_string(value_str)
        else:
            value_str = escape_yaml_string(value_str)
    
    else:
        # For unknown fields, just apply escaping
        value_str = escape_yaml_string(value_str)
    
    return value_str


# =============================================================================
# HEADER INJECTOR
# =============================================================================

class ResponseHeaderInjector:
    """
    Injects CORTEX headers and footers into template responses.

    This is a composition layer that wraps ResponseTemplateEngine.
    It intercepts rendered output and adds global headers/footers.

    Architecture:
    - Wraps ResponseTemplateEngine (does not modify it)
    - Loads header config from HeaderConfigurationManager
    - Injects header BEFORE content
    - Injects copyright section AFTER header
    - Optionally injects footer AFTER content

    Non-invasive: ResponseTemplateEngine is unaware of this layer.
    """

    def __init__(
        self,
        template_engine: ResponseTemplateEngine,
        config_manager: Optional[HeaderConfigurationManager] = None
    ):
        """
        Initialize header injector.

        Args:
            template_engine: ResponseTemplateEngine instance to wrap
            config_manager: HeaderConfigurationManager (defaults to singleton)
        """
        self.engine = template_engine
        self.config_manager = config_manager or HeaderConfigurationManager.get_instance()
        self._render_cache: Dict[str, str] = {}

    def render(self, domain_id: str, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render template with injected header and footer.

        This is the main entry point. It:
        1. Renders the template using the wrapped engine
        2. Prepends CORTEX header
        3. Appends copyright section
        4. Optionally appends footer

        Args:
            domain_id: Domain identifier (e.g., "governance")
            template_name: Template name (e.g., "evaluation_result")
            context: Variable values for substitution

        Returns:
            Complete response with header, content, and optional footer
        """
        # Get rendered content from wrapped engine
        rendered_content = self.engine.render(domain_id, template_name, context)

        # Build complete response with headers
        return self._inject_headers_and_footers(rendered_content, context)

    def render_by_id(self, template_id: str, context: Dict[str, Any]) -> str:
        """
        Render template by ID with injected header and footer.

        Args:
            template_id: Fully qualified template ID
            context: Variable values for substitution

        Returns:
            Complete response with header, content, and optional footer
        """
        # Get rendered content from wrapped engine
        rendered_content = self.engine.render_by_id(template_id, context)

        # Build complete response with headers
        return self._inject_headers_and_footers(rendered_content, context)

    def _inject_headers_and_footers(self, rendered_content: str, context: Dict[str, Any]) -> str:
        """
        Inject headers and footers around rendered content.

        Assembly order:
        1. Header (if enabled)
        2. Copyright section (if enabled)
        3. Original rendered content
        4. Footer (if enabled)

        Args:
            rendered_content: Template rendering output
            context: Context variables for header substitution

        Returns:
            Complete response with all sections assembled
        """
        sections = []

        # 1. Build header section
        if self.config_manager.is_header_enabled():
            header = self._build_header_section(context)
            if header:
                sections.append(header)

        # 2. Build copyright section
        if self.config_manager.is_copyright_enabled():
            copyright_section = self._build_copyright_section(context)
            if copyright_section:
                sections.append(copyright_section)

        # 3. Add rendered content
        sections.append(rendered_content)

        # 4. Build optional footer
        if self.config_manager.is_footer_enabled():
            footer = self._build_footer_section(context)
            if footer:
                sections.append(footer)

        # Assemble with appropriate spacing
        return self._assemble_sections(sections)

    def _build_header_section(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Build header section with variable substitution.

        Args:
            context: Variables for substitution

        Returns:
            Formatted header string or None if disabled
        """
        # Check if headers are enabled
        if not self.config_manager.is_header_enabled():
            return None
        
        template = self.config_manager.get_header_template()
        if not template:
            return None

        # Substitute variables
        header_text = self._substitute_variables(template, context)

        # Apply formatting
        formatting = self.config_manager.get_header_formatting()
        if formatting.get('separator_before_header', False):
            header_text = "---\n" + header_text

        if formatting.get('separator_after_header', False):
            header_text = header_text + "\n---"

        return header_text

    def _build_copyright_section(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Build copyright section.

        Args:
            context: Variables for substitution

        Returns:
            Formatted copyright string or None if disabled
        """
        # Check if copyright section is enabled
        if not self.config_manager.is_copyright_enabled():
            return None
        
        template = self.config_manager.get_copyright_template()
        if not template:
            return None

        # Get copyright notice
        copyright_notice = self.config_manager.get_copyright_notice()

        # Build copyright text
        copyright_text = template.replace('{notice}', copyright_notice)

        # Apply formatting
        formatting = self.config_manager.get_copyright_formatting()

        if formatting.get('separator_before', False):
            copyright_text = "---\n" + copyright_text

        if formatting.get('separator_after', False):
            copyright_text = copyright_text + "\n---"

        # Apply bold if configured
        if formatting.get('bold', False) and formatting.get('emphasis') == "**":
            # Already bold in template, just ensure it's applied
            pass

        return copyright_text

    def _build_footer_section(self, context: Dict[str, Any]) -> Optional[str]:
        """
        Build footer section (if enabled).

        Args:
            context: Variables for substitution

        Returns:
            Formatted footer string or None if disabled
        """
        config = self.config_manager.get_configuration()
        if not config or not config.footer:
            return None

        template = config.footer.template
        if not template:
            return None

        # Substitute variables
        footer_text = self._substitute_variables(template, context)

        return footer_text

    def _substitute_variables(self, template: str, context: Dict[str, Any]) -> str:
        """
        Substitute template variables with context values.

        SECURITY: All values are sanitized to prevent prompt injection attacks.
        - Mandatory variables: Validated against whitelists where applicable
        - All values: YAML-safe escaped to prevent injection
        - Special characters: Quoted to treat as literal strings

        Handles both mandatory and auto-populated variables.

        Args:
            template: Template string with {variable} placeholders
            context: Variable values from caller

        Returns:
            Template with variables substituted (sanitized and escaped)
            
        Raises:
            ValueError: If mandatory field validation fails (ac_id, operation, domain)
        """
        result = template

        # Get mandatory variables from context
        for var_name in self.config_manager.get_mandatory_variables():
            placeholder = f"{{{var_name}}}"
            if var_name in context:
                value = context[var_name]
                # Sanitize and escape the value (prevents prompt injection)
                sanitized_value = sanitize_context_value(var_name, value, is_mandatory=True)
                result = result.replace(placeholder, sanitized_value)
            else:
                # Use empty string if not provided (after logging if configured)
                enforcement = self.config_manager.get_enforcement_config()
                if enforcement and enforcement.fail_on_missing_variable:
                    raise ValueError(f"Missing mandatory header variable: {var_name}")
                result = result.replace(placeholder, "")

        # Get auto-populated variables
        auto_vars = self.config_manager.get_auto_populated_variables()
        for var_name, value in auto_vars.items():
            placeholder = f"{{{var_name}}}"
            # Sanitize and escape auto-populated values too
            sanitized_value = sanitize_context_value(var_name, value, is_mandatory=False)
            result = result.replace(placeholder, sanitized_value)

        return result

    def _assemble_sections(self, sections: list) -> str:
        """
        Assemble all sections with appropriate spacing.

        Args:
            sections: List of section strings to assemble

        Returns:
            Complete response with proper spacing
        """
        # Get formatting rules
        header_formatting = self.config_manager.get_header_formatting()
        copyright_formatting = self.config_manager.get_copyright_formatting()

        assembled = []
        for i, section in enumerate(sections):
            if section:
                assembled.append(section)

        # Join sections with blank lines
        # Header + copyright need blank line between them
        if len(assembled) >= 2:
            # Between header and copyright
            if (header_formatting.get('blank_line_after_header', False) and
                copyright_formatting.get('separator_before', False)):
                return assembled[0] + "\n\n" + "\n\n".join(assembled[1:])

            # Standard spacing
            return "\n\n".join(assembled)

        return "\n\n".join(assembled) if assembled else ""

    def get_statistics(self) -> Dict[str, Any]:
        """Get injector statistics."""
        engine_stats = {}
        
        # Try to get engine statistics if available
        try:
            if self.engine and hasattr(self.engine, 'registry'):
                engine_stats = self.engine.registry.get_statistics()
        except (AttributeError, TypeError):
            # Engine or registry not available (e.g., in tests with mocks)
            pass
        
        return {
            "header_enabled": self.config_manager.is_header_enabled(),
            "copyright_enabled": self.config_manager.is_copyright_enabled(),
            "footer_enabled": self.config_manager.is_footer_enabled(),
            "author": self.config_manager.get_author_name(),
            "repository": self.config_manager.get_repository_url(),
            "engine_statistics": engine_stats
        }

    def clear_cache(self) -> None:
        """Clear render cache."""
        self._render_cache.clear()
