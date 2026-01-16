# Tier 3 - Knowledge (Advisory)

## Domain Brain Query Patterns

Tier 3 provides a **Domain Brain** abstraction for querying and analyzing code domains. The Domain Brain uses specialized adapters to extract knowledge from various code sources.

### Supported Query Syntax

The Domain Brain supports structured query patterns for different types of code analysis:

#### 1. Docstring Queries
Extract documentation and function signatures from code.

**Syntax:**
- `docstring:*` - All docstrings in the domain
- `docstring:<name>` - Docstring for specific function/class

**Example:**
```python
domain_brain.query("docstring:*")  # Get all documentation
domain_brain.query("docstring:search")  # Get search() function docs
```

**Return Format:**
```python
[
    {
        "name": "function_name",
        "docstring": "Full docstring text",
        "signature": "def function(arg1, arg2) -> ReturnType"
    },
    ...
]
```

#### 2. Design Comments Queries
Extract design decisions and architecture comments from code.

**Syntax:**
- `comment:design` - Design decision comments
- `comment:architecture` - Architecture-related comments
- `comment:pattern` - Design pattern documentation

**Example:**
```python
domain_brain.query("comment:design")  # Get design decisions
```

**Return Format:**
```python
[
    {
        "type": "design_comment",
        "text": "The adapter pattern is used to...",
        "location": "adapters.py:42",
        "context": "Method or class this comment relates to"
    },
    ...
]
```

#### 3. TODO/FIXME Queries
Query technical debt and work items in the domain.

**Syntax:**
- `todo:*` - All TODO/FIXME comments

**Example:**
```python
domain_brain.query("todo:*")  # Get all TODO/FIXME items
```

**Return Format:**
```python
[
    {
        "type": "TODO",
        "text": "Implement async support",
        "file": "handlers.py",
        "line": 128,
        "priority": "high"  # Inferred from context
    },
    {
        "type": "FIXME",
        "text": "Handle edge case in validation",
        "file": "validators.py",
        "line": 245,
        "priority": "medium"
    },
    ...
]
```

### `_query_todos()` Method

The `_query_todos()` method is a specialized query handler for extracting technical debt items.

**Method Signature:**
```python
def _query_todos(self) -> List[Dict[str, Any]]:
    """Query TODO/FIXME comments.
    
    Returns:
        List of TODO/FIXME items with:
        - type: 'TODO' or 'FIXME'
        - text: Comment text
        - file: Source file path
        - line: Line number
        - priority: 'high', 'medium', or 'low'
    """
```

**Implementation Details:**
- Parses TODO and FIXME markers in code comments
- Extracts context from surrounding code
- Determines priority from keywords (urgent, important, asap vs. nice-to-have, consider)
- Returns structured list of work items

**Practical Usage:**
```python
# Get all technical debt
adapter = DomainAdapter("mymodule")
todos = adapter._query_todos()

# Filter by priority
high_priority = [t for t in todos if t['priority'] == 'high']

# Group by file
by_file = {}
for todo in todos:
    if todo['file'] not in by_file:
        by_file[todo['file']] = []
    by_file[todo['file']].append(todo)
```

### Query Method Reference

**Common Query Patterns:**

| Query Pattern | Purpose | Returns |
|---------------|---------|---------|
| `docstring:*` | All function/class documentation | List of docstrings |
| `docstring:name` | Specific function documentation | Single docstring entry |
| `comment:design` | Design decision comments | List of design notes |
| `comment:architecture` | Architecture documentation | List of architecture notes |
| `todo:*` | All technical debt items | List of TODO/FIXME entries |

### Adapter Architecture

The Domain Brain uses pluggable adapters for different code analysis tasks:

1. **CodeAdapter** - Basic code structure analysis
2. **DocstringAdapter** - Documentation extraction
3. **CommentAdapter** - Comment parsing and classification
4. **RelationshipsAdapter** - Dependency and relationship mapping

Each adapter implements the `IntegrationAdapter` interface and can be extended for domain-specific logic.

### Integration with Governance

Domain Brain queries are integrated with the governance framework:
- All queries are logged to the audit trail
- Query results are validated against AC requirements
- Results contribute to compliance metrics

### Best Practices

1. **Use Specific Queries** - `todo:*` is better than manual searching
2. **Cache Results** - Domain Brain caches analysis results for performance
3. **Combine Queries** - Use multiple query types for comprehensive analysis
4. **Monitor TODOs** - Regular review of technical debt using `_query_todos()`

### Examples

**Get all documentation for a domain:**
```python
domain_brain = DomainBrain("cortex/orchestrators")
docs = domain_brain.query("docstring:*")
for doc in docs:
    print(f"{doc['name']}: {doc['signature']}")
```

**Extract technical debt:**
```python
todos = domain_brain.query("todo:*")
print(f"Found {len(todos)} TODO items")
high_priority_items = [t for t in todos if t.get('priority') == 'high']
```

**Get design decisions:**
```python
design_notes = domain_brain.query("comment:design")
for note in design_notes:
    print(f"Design Decision: {note['text']}")
```

