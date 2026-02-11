"""Template resolver for resolving template references and inheritance."""

from typing import Any, Dict, List, Optional, Set


class TemplateResolver:
    """Resolves template references, inheritance, and composition.

    Features:
    - Register templates for reference
    - Resolve template references
    - Handle template inheritance
    - Support nested template composition
    """

    def __init__(self) -> None:
        """Initialize the template resolver."""
        self.templates: Dict[str, str] = {}
        self.inheritance_chain: Dict[str, Optional[str]] = {}

    def register_templates(self, templates: Dict[str, str]) -> None:
        """Register templates for reference resolution.

        Args:
            templates: Dictionary mapping template names to template strings
        """
        self.templates.update(templates)

    def resolve(
        self,
        template_name: str,
        **context: Any
    ) -> str:
        """Resolve a template by name with given context.

        Args:
            template_name: Name of template to resolve
            **context: Context variables for template rendering

        Returns:
            Resolved template string

        Raises:
            KeyError: If template not found
            ValueError: If resolution fails
        """
        if template_name not in self.templates:
            raise KeyError(f"Template '{template_name}' not found in registry")

        template_str = self.templates[template_name]

        # Simple resolution - substitute context variables
        result = template_str
        for key, value in context.items():
            placeholder = f"{{{{ {key} }}}}"
            result = result.replace(placeholder, str(value))

        return result

    def resolve_with_inheritance(
        self,
        child_name: str,
        parent_name: str,
        **context: Any
    ) -> str:
        """Resolve template with inheritance from parent.

        Args:
            child_name: Child template name
            parent_name: Parent template name
            **context: Context variables

        Returns:
            Resolved template with inheritance applied

        Raises:
            KeyError: If template not found
        """
        if child_name not in self.templates:
            raise KeyError(f"Template '{child_name}' not found")
        if parent_name not in self.templates:
            raise KeyError(f"Template '{parent_name}' not found")

        # Record inheritance relationship
        self.inheritance_chain[child_name] = parent_name

        # In a real implementation, this would handle Jinja2 inheritance
        # For now, return child template
        return self.resolve(child_name, **context)

    def resolve_nested(
        self,
        template_name: str,
        **context: Any
    ) -> str:
        """Resolve template with nested references.

        Args:
            template_name: Template name to resolve
            **context: Context variables

        Returns:
            Fully resolved template string

        Raises:
            KeyError: If template not found
        """
        if template_name not in self.templates:
            raise KeyError(f"Template '{template_name}' not found")

        template_str = self.templates[template_name]

        # Recursively resolve nested references
        resolved = self._resolve_recursive(template_str, context, set())

        return resolved

    def _resolve_recursive(
        self,
        template_str: str,
        context: Dict[str, Any],
        visited: Set[str]
    ) -> str:
        """Recursively resolve nested template references.

        Args:
            template_str: Template string to resolve
            context: Context variables
            visited: Set of visited template names (prevent cycles)

        Returns:
            Resolved template string

        Raises:
            ValueError: If circular reference detected
        """
        # Look for template references like {{ include 'template_name' }}
        import re

        references = re.findall(r"\{\{\s*include\s+['\"](\w+)['\"]\s*\}\}", template_str)

        for ref_name in references:
            if ref_name in visited:
                raise ValueError(f"Circular reference detected: {ref_name}")

            if ref_name not in self.templates:
                continue

            visited.add(ref_name)
            nested_str = self.templates[ref_name]
            resolved_nested = self._resolve_recursive(nested_str, context, visited)

            # Replace reference with resolved content
            template_str = template_str.replace(
                f"{{{{ include '{ref_name}' }}}}",
                resolved_nested
            )

        # Apply context substitution
        for key, value in context.items():
            placeholder = f"{{{{ {key} }}}}"
            template_str = template_str.replace(placeholder, str(value))

        return template_str

    def get_template(self, template_name: str) -> str:
        """Get raw template string without resolution.

        Args:
            template_name: Name of template

        Returns:
            Raw template string

        Raises:
            KeyError: If template not found
        """
        if template_name not in self.templates:
            raise KeyError(f"Template '{template_name}' not found")

        return self.templates[template_name]

    def list_templates(self) -> List[str]:
        """List all registered template names.

        Returns:
            List of template names
        """
        return list(self.templates.keys())

    def get_inheritance_chain(self, template_name: str) -> List[str]:
        """Get the inheritance chain for a template.

        Args:
            template_name: Template name

        Returns:
            List showing inheritance hierarchy
        """
        chain = [template_name]
        current = template_name

        while current in self.inheritance_chain and self.inheritance_chain[current]:
            parent = self.inheritance_chain[current]
            chain.append(parent)
            current = parent

        return chain
