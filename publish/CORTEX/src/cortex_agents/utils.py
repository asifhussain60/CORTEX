"""
Utility Functions for CORTEX Agents

Common helper functions used across multiple agents.
"""

import re
from typing import List, Dict, Any, Optional
from pathlib import Path


def extract_file_paths(text: str) -> List[str]:
    """
    Extract file paths from text.
    
    Matches patterns like:
    - /absolute/path/to/file.py
    - relative/path/to/file.js
    - C:/Windows\\path\\file.txt
    
    Args:
        text: Text to search for file paths
    
    Returns:
        List of extracted file paths
    
    Example:
        >>> extract_file_paths("Edit /src/app.py and /tests/test_app.py")
        ['/src/app.py', '/tests/test_app.py']
    """
    # Pattern for Unix/Linux paths
    unix_pattern = r'(?:/[\w\-\.]+)+\.\w+'
    # Pattern for Windows paths
    windows_pattern = r'[A-Z]:\\(?:[\w\-\.]+\\)*[\w\-\.]+\.\w+'
    # Pattern for relative paths
    relative_pattern = r'(?:[\w\-\.]+/)+[\w\-\.]+\.\w+'
    
    paths = []
    paths.extend(re.findall(unix_pattern, text))
    paths.extend(re.findall(windows_pattern, text))
    paths.extend(re.findall(relative_pattern, text))
    
    return list(set(paths))  # Remove duplicates


def extract_code_intent(text: str) -> Optional[str]:
    """
    Extract primary code intent from user message.
    
    Looks for action verbs: create, edit, update, delete, fix, etc.
    
    Args:
        text: User message text
    
    Returns:
        Primary intent verb or None if not found
    
    Example:
        >>> extract_code_intent("Create a new authentication module")
        'create'
    """
    action_verbs = [
        'create', 'make', 'add', 'build', 'implement',
        'edit', 'update', 'modify', 'change', 'refactor',
        'delete', 'remove', 'fix', 'debug', 'test'
    ]
    
    text_lower = text.lower()
    for verb in action_verbs:
        if re.search(rf'\b{verb}\b', text_lower):
            return verb
    
    return None


def parse_priority_keywords(text: str) -> int:
    """
    Parse priority level from keywords in text.
    
    Keywords:
    - urgent, critical, asap -> CRITICAL (1)
    - important, high, soon -> HIGH (2)
    - normal, standard -> NORMAL (3)
    - low, later, when possible -> LOW (4)
    
    Args:
        text: Text to analyze for priority keywords
    
    Returns:
        Priority level (1-5)
    
    Example:
        >>> parse_priority_keywords("This is URGENT!")
        1
    """
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['urgent', 'critical', 'asap', 'now']):
        return 1  # CRITICAL
    elif any(word in text_lower for word in ['important', 'high', 'soon']):
        return 2  # HIGH
    elif any(word in text_lower for word in ['low', 'later', 'when possible']):
        return 4  # LOW
    
    return 3  # NORMAL (default)


def normalize_intent(intent: str) -> str:
    """
    Normalize intent string to standard format.
    
    Args:
        intent: Raw intent string
    
    Returns:
        Normalized intent (lowercase, underscores)
    
    Example:
        >>> normalize_intent("Create File")
        'create_file'
    """
    return intent.lower().replace(' ', '_').replace('-', '_')


def validate_context(context: Dict[str, Any], required_keys: List[str]) -> bool:
    """
    Validate that context contains required keys.
    
    Args:
        context: Context dictionary to validate
        required_keys: List of required key names
    
    Returns:
        True if all required keys present, False otherwise
    
    Example:
        >>> validate_context({"file": "test.py"}, ["file", "line"])
        False
    """
    return all(key in context for key in required_keys)


def truncate_message(message: str, max_length: int = 200) -> str:
    """
    Truncate message to maximum length with ellipsis.
    
    Args:
        message: Message to truncate
        max_length: Maximum length (default: 200)
    
    Returns:
        Truncated message
    
    Example:
        >>> truncate_message("A" * 300, 100)
        'A...A (truncated)'
    """
    if len(message) <= max_length:
        return message
    
    return message[:max_length - 15] + "... (truncated)"


def format_duration(duration_ms: float) -> str:
    """
    Format duration in human-readable string.
    
    Args:
        duration_ms: Duration in milliseconds
    
    Returns:
        Formatted duration string
    
    Example:
        >>> format_duration(1234.56)
        '1.23s'
        >>> format_duration(45.2)
        '45ms'
    """
    if duration_ms < 1000:
        return f"{duration_ms:.0f}ms"
    else:
        return f"{duration_ms / 1000:.2f}s"


def safe_get(dictionary: Dict, *keys, default=None):
    """
    Safely get nested dictionary value.
    
    Args:
        dictionary: Dictionary to search
        *keys: Keys to traverse
        default: Default value if key not found
    
    Returns:
        Value at keys path or default
    
    Example:
        >>> safe_get({"a": {"b": {"c": 1}}}, "a", "b", "c")
        1
        >>> safe_get({"a": {"b": {}}}, "a", "b", "c", default=0)
        0
    """
    current = dictionary
    for key in keys:
        if not isinstance(current, dict) or key not in current:
            return default
        current = current[key]
    return current
