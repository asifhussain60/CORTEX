# Update Documentation Operation - Usage Guide

**Version:** 1.0 (CORTEX 3.0 Phase 1.1 Week 2)  
**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.

---

## Overview

The **update_documentation** operation automatically generates and maintains CORTEX documentation by extracting docstrings from Python code, validating links, and updating the MkDocs navigation structure.

This is a **monolithic-then-modular** implementation following CORTEX 3.0 Phase 0 optimization principles.

---

## Features

✅ **API Reference Generation** - Extracts docstrings from Python files  
✅ **Operation Documentation** - Auto-generates docs for each operation  
✅ **Link Validation** - Checks for broken internal links  
✅ **MkDocs Integration** - Updates navigation automatically  
✅ **YAML Configuration** - Flexible, rule-based generation  
✅ **Comprehensive Testing** - 20+ test scenarios

---

## Quick Start

### Natural Language (Recommended)

```
update documentation
generate docs
refresh documentation
```

### Command Line

```bash
python3 src/operations/update_documentation.py
```

### With Custom Path

```bash
python3 src/operations/update_documentation.py --cortex-root /path/to/CORTEX
```

---

## Configuration

Configuration is stored in `cortex-brain/doc-generation-rules.yaml`:

```yaml
version: 1.0.0

sources:
  python_dirs:
    - src/
    - tests/
  
  exclude_patterns:
    - '**/__pycache__/**'
    - '**/dist/**'

output:
  api_reference: docs/api/
  operations: docs/operations/
  
link_validation:
  enabled: true
  check_external: false

mkdocs:
  auto_update_nav: true
```

### Key Configuration Options

| Option | Description | Default |
|--------|-------------|---------|
| `sources.python_dirs` | Directories to scan for Python files | `['src/', 'tests/']` |
| `sources.exclude_patterns` | Glob patterns to exclude | `['**/__pycache__/**', ...]` |
| `output.api_reference` | API reference output directory | `docs/api/` |
| `link_validation.enabled` | Enable link validation | `true` |
| `mkdocs.auto_update_nav` | Auto-update mkdocs.yml navigation | `true` |

---

## What Gets Generated

### 1. API Reference (`docs/api/reference.md`)

- Module documentation
- Class definitions with methods
- Function signatures
- Docstrings formatted as Markdown

### 2. Operation Docs (`docs/operations/*.md`)

- One file per operation
- Overview from module docstring
- Usage examples
- Method documentation

### 3. Updated Navigation

The `mkdocs.yml` file is automatically updated with:

```yaml
nav:
  - API Reference:
      - Overview: api/reference.md
      - Operations: api/operations.md
```

---

## Output Example

Given this Python code:

```python
"""
Sample Operation Module

This is a sample operation for demonstration.
"""

class SampleOperation:
    """Sample operation class."""
    
    def execute(self, param: str) -> bool:
        """
        Execute the operation.
        
        Args:
            param: Input parameter
            
        Returns:
            True if successful
        """
        return True
```

Generates this documentation:

```markdown
## src.operations.sample_operation

Sample Operation Module

This is a sample operation for demonstration.

### SampleOperation

Sample operation class.

**Methods:**

#### `execute(self, param)`

Execute the operation.

Args:
    param: Input parameter
    
Returns:
    True if successful
```

---

## Link Validation

The operation validates all markdown links and reports broken ones:

```
🔗 Validating links...
⚠️  Found 54 broken links:
   - index.md: story/the-awakening.md
   - README.md: ../reference/plugin-api.md
   ... and 49 more
```

**Note:** External links (http/https) are skipped by default for performance. Enable with:

```yaml
link_validation:
  check_external: true
```

---

## Programmatic Usage

```python
from pathlib import Path
from src.operations.update_documentation import DocumentationGenerator

# Create generator
generator = DocumentationGenerator(Path("/path/to/CORTEX"))

# Execute
result = generator.execute()

# Check results
if result.success:
    print(f"Generated {len(result.docs_generated)} files")
    print(f"Validated {result.links_validated} links")
    print(f"Found {len(result.links_broken)} broken links")
else:
    print(f"Errors: {result.errors}")
```

---

## Result Object

The `DocGenerationResult` object contains:

```python
@dataclass
class DocGenerationResult:
    success: bool
    docs_generated: List[str]       # Files created
    docs_updated: List[str]         # Files updated
    links_validated: int            # Total links checked
    links_broken: List[str]         # Broken link paths
    warnings: List[str]             # Non-fatal issues
    errors: List[str]               # Fatal errors
    duration_seconds: float         # Execution time
    timestamp: datetime             # When executed
```

---

## Common Use Cases

### 1. After Adding New Operation

```python
# Create new operation file
touch src/operations/my_operation.py

# Generate docs
python3 src/operations/update_documentation.py

# Result: docs/operations/my-operation.md created
```

### 2. Before Release

```bash
# Generate all docs
python3 src/operations/update_documentation.py

# Build MkDocs site
mkdocs build

# Preview
mkdocs serve
```

### 3. CI/CD Integration

```yaml
# .github/workflows/docs.yml
- name: Generate Documentation
  run: python3 src/operations/update_documentation.py
  
- name: Check for Broken Links
  run: |
    # Fail if broken links found
    python3 -c "
    from src.operations.update_documentation import DocumentationGenerator
    result = DocumentationGenerator().execute()
    exit(1 if result.links_broken else 0)
    "
```

---

## Testing

Run the comprehensive test suite:

```bash
# All tests
pytest tests/operations/test_update_documentation.py -v

# Specific test class
pytest tests/operations/test_update_documentation.py::TestDocumentationGenerator -v

# Integration test with real CORTEX files
pytest tests/operations/test_update_documentation.py::TestIntegration -v
```

**Test Coverage:**

- ✅ Configuration loading and defaults
- ✅ File discovery with exclusions
- ✅ Docstring extraction (Google format)
- ✅ API reference generation
- ✅ Operation docs generation
- ✅ Link validation (internal/external/anchors)
- ✅ MkDocs navigation updates
- ✅ Edge cases (empty files, malformed code, no links)
- ✅ Error handling

---

## Troubleshooting

### Issue: "Config file not found"

**Solution:** The operation creates a default config on first run. Check `cortex-brain/doc-generation-rules.yaml`.

### Issue: "MkDocs navigation update failed"

**Solution:** 
- Check `mkdocs.yml` is valid YAML
- Disable auto-update: `mkdocs.auto_update_nav: false`
- Update navigation manually

### Issue: "Too many broken links"

**Solution:**
- Review `exclude_patterns` in config
- Check if paths are relative to correct directory
- Disable validation temporarily: `link_validation.enabled: false`

### Issue: "Private methods appearing in docs"

**Solution:** Private methods (starting with `_`) are filtered during API generation. If they appear, check the generation logic in `generate_api_reference()`.

---

## Performance

**Typical Performance (CORTEX Repository):**

| Metric | Value |
|--------|-------|
| Python files scanned | 425 |
| Docstrings extracted | 425 |
| Docs generated | 14 |
| Links validated | 415 |
| Execution time | ~2-3 seconds |

---

## Future Enhancements (CORTEX 3.1+)

- 🔄 Incremental updates (only changed files)
- 📊 Code complexity metrics
- 🎨 Diagram generation from code structure
- 🔍 Full-text search index
- 🌐 Multi-language support (Sphinx, NumPy formats)

---

## Related Operations

- **refresh_cortex_story** - Updates narrative documentation
- **comprehensive_self_review** - Full health check including docs
- **workspace_cleanup** - Removes generated doc artifacts

---

## Technical Details

### Architecture

```
DocumentationGenerator
├── load_config()           # YAML config loading
├── discover_files()        # File system scan
├── extract_python_docstrings()
├── generate_api_reference()
├── generate_operations_docs()
├── validate_links()
└── update_mkdocs_nav()
```

### Design Principles

1. **Monolithic-first** - Single file until >500 lines
2. **Pragmatic defaults** - Works out-of-box
3. **YAML-driven** - Configuration over hardcoding
4. **Fail gracefully** - Warnings vs errors
5. **Test-driven** - 20+ test scenarios

### Dependencies

```python
import ast          # Python AST parsing
import yaml         # Config and mkdocs.yml
import re           # Link validation
from pathlib import Path
```

---

## Copyright & License

**Author:** Asif Hussain  
**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file for terms  
**Repository:** https://github.com/asifhussain60/CORTEX

---

*Generated: 2025-11-14 | CORTEX 3.0 Phase 1.1 Week 2*
