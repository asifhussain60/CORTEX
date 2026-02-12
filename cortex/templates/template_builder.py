"""Template builder for creating and modifying templates programmatically."""

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional


class TemplateBuilder:
    """Builds and modifies templates programmatically.

    Features:
    - Create templates with name and content
    - Add variables to templates
    - Add conditional blocks
    - Template versioning support
    """

    def __init__(self) -> None:
        """Initialize the template builder."""
        self.version_counter = 1

    def create(
        self,
        name: str,
        content: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new template.

        Args:
            name: Template name (unique identifier)
            content: Template content (Jinja2 syntax)
            description: Optional template description

        Returns:
            Template dictionary with metadata
        """
        template: Dict[str, Any] = {
            "name": name,
            "content": content,
            "description": description or "",
            "version": 1,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "variables": [],
            "dependencies": [],
            "conditionals": []
        }
        return template

    def add_variable(
        self,
        template: Dict[str, Any],
        var_name: str,
        var_type: str = "str",
        required: bool = False,
        default_value: Optional[Any] = None
    ) -> Dict[str, Any]:
        """Add a variable to template definition.

        Args:
            template: Template dictionary to modify
            var_name: Variable name
            var_type: Variable type (str, int, bool, etc.)
            required: Whether variable is required
            default_value: Default value if not provided

        Returns:
            Modified template dictionary
        """
        variable: Dict[str, Any] = {
            "name": var_name,
            "type": var_type,
            "required": required,
            "default": default_value
        }

        if "variables" not in template:
            template["variables"] = []

        template["variables"].append(variable)
        template["updated_at"] = datetime.now(timezone.utc).isoformat()

        return template

    def add_conditional(
        self,
        template: Dict[str, Any],
        condition: str,
        true_block: str,
        false_block: Optional[str] = None
    ) -> Dict[str, Any]:
        """Add a conditional block to template.

        Args:
            template: Template dictionary to modify
            condition: Condition expression
            true_block: Content if condition is true
            false_block: Optional content if condition is false

        Returns:
            Modified template dictionary
        """
        conditional_block: str = f"{{% if {condition} %}}{true_block}"
        if false_block:
            conditional_block += f"{{% else %}}{false_block}"
        conditional_block += "{% endif %}"

        # Append to template content
        template["content"] += "\n" + conditional_block

        if "conditionals" not in template:
            template["conditionals"] = []

        template["conditionals"].append({
            "condition": condition,
            "true_block": true_block,
            "false_block": false_block
        })

        template["updated_at"] = datetime.now(timezone.utc).isoformat()

        return template

    def update_version(
        self,
        template: Dict[str, Any],
        content: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update template content and increment version.

        Args:
            template: Template dictionary to update
            content: New content (optional)
            description: Updated description (optional)

        Returns:
            Modified template with incremented version
        """
        template["version"] = template.get("version", 1) + 1

        if content is not None:
            template["content"] = content

        if description is not None:
            template["description"] = description

        template["updated_at"] = datetime.now(timezone.utc).isoformat()

        return template

    def add_filter(
        self,
        template: Dict[str, Any],
        filter_name: str,
        filter_args: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add a Jinja2 filter to template.

        Args:
            template: Template dictionary to modify
            filter_name: Name of the filter (e.g., 'upper', 'lower')
            filter_args: Optional filter arguments

        Returns:
            Modified template dictionary
        """
        if "filters" not in template:
            template["filters"] = []

        template["filters"].append({
            "name": filter_name,
            "args": filter_args or []
        })

        template["updated_at"] = datetime.now(timezone.utc).isoformat()

        return template

    def add_macro(
        self,
        template: Dict[str, Any],
        macro_name: str,
        macro_body: str,
        parameters: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """Add a Jinja2 macro to template.

        Args:
            template: Template dictionary to modify
            macro_name: Macro name
            macro_body: Macro implementation
            parameters: Optional list of parameter names

        Returns:
            Modified template dictionary
        """
        params = ", ".join(parameters) if parameters else ""
        macro_def = f"{{% macro {macro_name}({params}) %}}{macro_body}{{% endmacro %}}"

        template["content"] = macro_def + "\n" + template["content"]

        if "macros" not in template:
            template["macros"] = []

        template["macros"].append({
            "name": macro_name,
            "parameters": parameters or [],
            "body": macro_body
        })

        template["updated_at"] = datetime.now(timezone.utc).isoformat()

        return template
