# Documentation Generation Orchestrator Guide

## Overview
Auto-generate API documentation and usage guides from Python source code using AST parsing.

## Key Features
- **Docstring Extraction**: Parse Python code to extract docstrings
- **API Reference Generation**: Create formatted API documentation
- **Usage Guide Creation**: Generate guides with code examples

## Usage

### Extract Docstrings
```python
from src.operations.utilities import DocumentationGenerationOrchestrator

orchestrator = DocumentationGenerationOrchestrator()

source_code = '''
def add(x, y):
    """Add two numbers."""
    return x + y
'''

docstrings = orchestrator.extract_docstrings(source_code)
```

### Generate API Reference
```python
api_ref = orchestrator.generate_api_reference(docstrings, module_name="mymodule")
print(api_ref.markdown)
```

### Create Usage Guide
```python
examples = [
    {"title": "Basic Usage", "code": "result = add(1, 2)"}
]
guide = orchestrator.create_usage_guide("mymodule", examples)
print(guide.markdown)
```

## API Reference
- `extract_docstrings(source_code)` - Extract all docstrings from code
- `generate_api_reference(docstrings, module_name)` - Generate API docs
- `create_usage_guide(module_name, examples, description)` - Create usage guide
