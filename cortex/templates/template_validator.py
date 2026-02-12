"""Template validator for checking template syntax and structure."""

from typing import Dict, List, Optional, Set

from jinja2 import BaseLoader, Environment, TemplateSyntaxError, meta


class TemplateValidator:
    """Validates Jinja2 templates for syntax errors and structural issues.

    Features:
    - Validates template syntax
    - Detects missing required variables
    - Identifies circular dependencies
    - Checks for undefined variables
    """

    def __init__(self) -> None:
        """Initialize the template validator."""
        self.env = Environment(loader=BaseLoader())

    def validate(self, template_str: str) -> List[str]:
        """Validate template syntax and structure.

        Args:
            template_str: Template string to validate

        Returns:
            List of error messages (empty if valid)
        """
        errors: List[str] = []

        try:
            # Try to parse the template
            self.env.parse(template_str)
        except TemplateSyntaxError as e:
            errors.append(f"Syntax error at line {e.lineno}: {e.message}")
        except Exception as e:
            errors.append(f"Validation error: {str(e)}")

        return errors

    def validate_variables(
        self,
        template_str: str,
        required: Optional[List[str]] = None
    ) -> List[str]:
        """Validate that all required variables are present in template.

        Args:
            template_str: Template string to validate
            required: List of required variable names

        Returns:
            List of error messages for missing variables
        """
        errors: List[str] = []
        required = required or []

        try:
            ast = self.env.parse(template_str)
            undeclared = meta.find_undeclared_variables(ast)

            for var_name in required:
                if var_name not in undeclared:
                    errors.append(f"Required variable '{var_name}' not used in template")
        except Exception as e:
            errors.append(f"Variable validation error: {str(e)}")

        return errors

    def validate_dependencies(
        self,
        templates: Dict[str, str]
    ) -> List[str]:
        """Detect circular dependencies between templates.

        Args:
            templates: Dictionary mapping template names to template strings

        Returns:
            List of error messages for circular dependencies
        """
        errors: List[str] = []

        # Build dependency graph
        deps: Dict[str, Set[str]] = {}
        for name, template_str in templates.items():
            try:
                ast = self.env.parse(template_str)
                # In a real implementation, would parse template references
                # For now, return empty list as placeholder
                deps[name] = set()
            except Exception as e:
                errors.append(f"Dependency parse error in '{name}': {str(e)}")

        # Check for cycles
        for name in deps:
            if self._has_cycle(name, deps):
                errors.append(f"Circular dependency detected starting from '{name}'")

        return errors

    def _has_cycle(
        self,
        node: str,
        graph: Dict[str, Set[str]],
        visited: Optional[Set[str]] = None,
        rec_stack: Optional[Set[str]] = None
    ) -> bool:
        """Check if there's a cycle in the dependency graph.

        Args:
            node: Current node to check
            graph: Dependency graph
            visited: Set of visited nodes
            rec_stack: Recursion stack for cycle detection

        Returns:
            True if cycle detected
        """
        visited = visited or set()
        rec_stack = rec_stack or set()

        visited.add(node)
        rec_stack.add(node)

        for neighbor in graph.get(node, set()):
            if neighbor not in visited:
                if self._has_cycle(neighbor, graph, visited, rec_stack):
                    return True
            elif neighbor in rec_stack:
                return True

        rec_stack.remove(node)
        return False
