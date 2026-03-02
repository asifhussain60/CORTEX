"""
Naming utility functions for tool and orchestrator generation.

"""
import re

def to_class_name(name: str) -> str:
    """
    Convert name to PascalCase class name.

    Args:
        name: Input name (can be kebab-case, snake_case, or mixed)

    Returns:
        PascalCase class name

    Examples:
        >>> to_class_name("my-tool")
        'MyTool'
        >>> to_class_name("lens_analyzer")
        'LensAnalyzer'
        >>> to_class_name("TDD Orchestrator")
        'TddOrchestrator'
    """
    parts = re.split(r'[-_\s]+', name)
    return ''.join(part.capitalize() for part in parts)

def to_module_name(name: str) -> str:
    """
    Convert name to snake_case module name.

    Args:
        name: Input name (can be kebab-case, PascalCase, or mixed)

    Returns:
        snake_case module name

    Examples:
        >>> to_module_name("MyTool")
        'my_tool'
        >>> to_module_name("lens-analyzer")
        'lens_analyzer'
        >>> to_module_name("TDD Orchestrator")
        'tdd_orchestrator'
    """
    # Handle camelCase/PascalCase FIRST (before lowercasing)
    name = re.sub(r'([a-z])([A-Z])', r'\1_\2', name)
    # Convert to lowercase and replace separators
    name = re.sub(r'[-\s]+', '_', name.lower())
    return name

def yaml_type_to_python(type_str: str) -> str:
    """
    Convert YAML type specification to Python type.

    Args:
        type_str: YAML type string (e.g., 'string', 'int', 'array')

    Returns:
        Python type string (e.g., 'str', 'int', 'List[Any]')

    Examples:
        >>> yaml_type_to_python("string")
        'str'
        >>> yaml_type_to_python("array")
        'List[Any]'
        >>> yaml_type_to_python("object")
        'Dict[str, Any]'
    """
    type_map = {
        'str': 'str',
        'string': 'str',
        'int': 'int',
        'integer': 'int',
        'float': 'float',
        'number': 'float',
        'bool': 'bool',
        'boolean': 'bool',
        'list': 'List[Any]',
        'array': 'List[Any]',
        'dict': 'Dict[str, Any]',
        'object': 'Dict[str, Any]',
    }
    return type_map.get(type_str.lower(), 'Any')

# AC_COMPLETE: AC-AUDIT-2026-02-12-002 ✅
