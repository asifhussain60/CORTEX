# copilot_instructions_merger

Copilot Instructions Merger - Intelligent Markdown Section Merging

Merges CORTEX enhancements into existing copilot-instructions.md files while
preserving 100% of user customizations.

**Merge Strategy:**
- Parse both files into sections (## headers)
- Classify sections: CORTEX-managed, user-owned, hybrid
- Preserve ALL user content (user wins on conflicts)
- Inject CORTEX sections if missing
- Update CORTEX sections if stale

**Three Scenarios:**
1. **New file:** Generate CORTEX-enhanced template
2. **Generic existing:** Merge CORTEX sections + preserve user content
3. **CORTEX existing:** Update CORTEX sections + preserve user content

Part of CORTEX 3.9.0 - AST-Powered Copilot Instructions Enhancement
Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.


## Table of Contents

### Classes
- [MergeResult](#mergeresult)

### Functions
- [is_cortex_managed_section](#is_cortex_managed_section)
- [classify_section](#classify_section)
- [parse_markdown_sections](#parse_markdown_sections)
- [render_markdown](#render_markdown)
- [generate_cortex_sections](#generate_cortex_sections)
- [merge_with_existing](#merge_with_existing)
- [generate_new_instructions](#generate_new_instructions)


## Overview

- **Classes:** 1
- **Functions:** 8
- **Dependencies:** dataclasses, datetime, logging, pathlib, re, typing


## Classes

### MergeResult

```python
class MergeResult
```

**Decorators:** `dataclass`

Result of merge operation.


**Attributes:**

- `content`: str
- `action`: str
- `user_sections_preserved`: int
- `cortex_sections_updated`: int
- `patterns_injected`: int
- `warnings`: List[str]


**Methods:**

  #### `to_dict`

  ```python
  to_dict(self) -> Dict
  ```

  Convert to dictionary for reporting.

  **Parameters:**

  - `self`


  **Returns:** Dict



---

## Functions

### is_cortex_managed_section

```python
is_cortex_managed_section(header: str, content: str) -> bool
```

Check if section is CORTEX-managed (safe to update).

A section is CORTEX-managed if:
- Header starts with 🧠 or 🎯
- Content contains CORTEX-specific markers

Args:
    header: Section header (e.g., "## 🧠 CORTEX Integration")
    content: Section content

Returns:
    True if CORTEX-managed, False if user-owned

Example:
    >>> is_cortex_managed_section("## 🧠 CORTEX Integration", "Planning System 2.0...")
    True
    >>> is_cortex_managed_section("## Custom Notes", "My notes...")
    False


**Parameters:**

- `header` (str): Section header (e.g., "## 🧠 CORTEX Integration")
- `content` (str): Section content


**Returns:** bool
  True if CORTEX-managed, False if user-owned


---

### classify_section

```python
classify_section(header: str, content: str) -> str
```

Classify section ownership.

Returns:
    - "cortex_managed": CORTEX owns this section (safe to update)
    - "user_owned": User owns this section (preserve verbatim)
    - "hybrid": Shared section (inject CORTEX as subsection)

Example:
    >>> classify_section("## 🧠 CORTEX Integration", "...")
    'cortex_managed'
    >>> classify_section("## Team Guidelines", "...")
    'user_owned'
    >>> classify_section("## Development Guidelines", "...")
    'hybrid'


**Parameters:**

- `header` (str)
- `content` (str)


**Returns:** str
  - "cortex_managed": CORTEX owns this section (safe to update) - "user_owned": User owns this section (preserve verbatim) - "hybrid": Shared section (inject CORTEX as subsection)


---

### parse_markdown_sections

```python
parse_markdown_sections(content: str) -> Dict[str, str]
```

Parse markdown into sections by ## headers.

Args:
    content: Markdown content

Returns:
    Dictionary mapping header → content

Example:
    >>> content = "## Section 1\nContent 1\n## Section 2\nContent 2"
    >>> parse_markdown_sections(content)
    {'## Section 1': 'Content 1\n', '## Section 2': 'Content 2'}


**Parameters:**

- `content` (str): Markdown content


**Returns:** Dict[str, str]
  Dictionary mapping header → content


---

### render_markdown

```python
render_markdown(sections: Dict[str, str]) -> str
```

Render sections back to markdown.

Args:
    sections: Dictionary mapping header → content

Returns:
    Rendered markdown string

Example:
    >>> sections = {'## Section 1': 'Content 1', '## Section 2': 'Content 2'}
    >>> render_markdown(sections)
    '## Section 1\n\nContent 1\n\n## Section 2\n\nContent 2'


**Parameters:**

- `sections` (Dict[str, str]): Dictionary mapping header → content


**Returns:** str
  Rendered markdown string


---

### generate_cortex_sections

```python
generate_cortex_sections(project_name: str, language: str, framework: str, domain_patterns: Optional[object]) -> Dict[str, str]
```

Generate CORTEX-managed sections with detected patterns.

Args:
    project_name: Project name
    language: Primary language
    framework: Framework name
    domain_patterns: DomainPatterns from code_pattern_detector (optional)

Returns:
    Dictionary of CORTEX sections (header → content)


**Parameters:**

- `project_name` (str): Project name
- `language` (str): Primary language
- `framework` (str): Framework name
- `domain_patterns` (Optional[object]) = `None`: DomainPatterns from code_pattern_detector (optional)


**Returns:** Dict[str, str]
  Dictionary of CORTEX sections (header → content)


---

### merge_with_existing

```python
merge_with_existing(existing_path: Path, project_name: str, language: str, framework: str, domain_patterns: Optional[object]) -> MergeResult
```

Merge CORTEX enhancements with existing copilot-instructions.md.

Args:
    existing_path: Path to existing copilot-instructions.md
    project_name: Project name
    language: Primary language
    framework: Framework name
    domain_patterns: Detected patterns (optional)

Returns:
    MergeResult with merged content and metadata

Example:
    >>> result = merge_with_existing(
    ...     Path(".github/copilot-instructions.md"),
    ...     "my-project",
    ...     "Python",
    ...     "FastAPI",
    ...     patterns
    ... )
    >>> result.action
    'merged'


**Parameters:**

- `existing_path` (Path): Path to existing copilot-instructions.md
- `project_name` (str): Project name
- `language` (str): Primary language
- `framework` (str): Framework name
- `domain_patterns` (Optional[object]) = `None`: Detected patterns (optional)


**Returns:** MergeResult
  MergeResult with merged content and metadata


---

### generate_new_instructions

```python
generate_new_instructions(project_name: str, language: str, framework: str, build_system: str, test_framework: str, domain_patterns: Optional[object]) -> str
```

Generate new copilot-instructions.md from scratch.

Args:
    project_name: Project name
    language: Primary language
    framework: Framework name
    build_system: Build system
    test_framework: Test framework
    domain_patterns: Detected patterns (optional)

Returns:
    Complete markdown content


**Parameters:**

- `project_name` (str): Project name
- `language` (str): Primary language
- `framework` (str): Framework name
- `build_system` (str): Build system
- `test_framework` (str): Test framework
- `domain_patterns` (Optional[object]) = `None`: Detected patterns (optional)


**Returns:** str
  Complete markdown content


---
