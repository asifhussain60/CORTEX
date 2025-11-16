# src.cortex_agents.utils

Utility Functions for CORTEX Agents

Common helper functions used across multiple agents.

## Functions

### `extract_file_paths(text)`

Extract file paths from text.

Matches patterns like:
- /absolute/path/to/file.py
- relative/path/to/file.js
- C:\Windows\path\file.txt

Args:
    text: Text to search for file paths

Returns:
    List of extracted file paths

Example:
    >>> extract_file_paths("Edit /src/app.py and /tests/test_app.py")
    ['/src/app.py', '/tests/test_app.py']

### `extract_code_intent(text)`

Extract primary code intent from user message.

Looks for action verbs: create, edit, update, delete, fix, etc.

Args:
    text: User message text

Returns:
    Primary intent verb or None if not found

Example:
    >>> extract_code_intent("Create a new authentication module")
    'create'

### `parse_priority_keywords(text)`

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

### `normalize_intent(intent)`

Normalize intent string to standard format.

Args:
    intent: Raw intent string

Returns:
    Normalized intent (lowercase, underscores)

Example:
    >>> normalize_intent("Create File")
    'create_file'

### `validate_context(context, required_keys)`

Validate that context contains required keys.

Args:
    context: Context dictionary to validate
    required_keys: List of required key names

Returns:
    True if all required keys present, False otherwise

Example:
    >>> validate_context({"file": "test.py"}, ["file", "line"])
    False

### `truncate_message(message, max_length)`

Truncate message to maximum length with ellipsis.

Args:
    message: Message to truncate
    max_length: Maximum length (default: 200)

Returns:
    Truncated message

Example:
    >>> truncate_message("A" * 300, 100)
    'A...A (truncated)'

### `format_duration(duration_ms)`

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

### `safe_get(dictionary, *keys)`

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
