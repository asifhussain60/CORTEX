---
title: Developer Guide
description: Complete guide for CORTEX development
author: 
generated: true
version: ""
last_updated: 
---

# Developer Guide

**Purpose:** Complete guide for developing with and contributing to CORTEX  
**Audience:** Developers, contributors  
**Version:**   
**Last Updated:** 

---

## Getting Started

### Prerequisites

- Python 3.9.6+
- Git 2.0+
- SQLite 3.35+
- VS Code (recommended)
- GitHub Copilot (for full integration)

### Clone Repository

```bash
git clone https://github.com/asifhussain60/CORTEX.git
cd CORTEX
```

### Setup Development Environment

```bash
# Install dependencies
pip install -r requirements.txt

# Run setup
python scripts/cortex_setup.py

# Verify installation
python -m pytest tests/ -v
```

---

## Project Structure

```
CORTEX/
├── src/                    # Core source code
│   ├── tier0/             # Brain protection
│   ├── tier1/             # Working memory
│   ├── tier2/             # Knowledge graph
│   ├── tier3/             # Context intelligence
│   ├── cortex_agents/     # 10 specialist agents
│   ├── epm/               # EPM modules
│   ├── plugins/           # Plugin system
│   └── core/              # Core utilities
├── cortex-brain/          # CORTEX brain data
│   ├── tier1/             # Conversation DB
│   ├── tier2/             # Knowledge DB
│   ├── tier3/             # Context DB
│   └── templates/         # Jinja2 templates
├── tests/                 # Test suite
├── docs/                  # Documentation
└── scripts/               # Utility scripts
```

---

## Development Workflow

### 1. Create Feature Branch

```bash
git checkout -b feature/my-feature
```

### 2. Write Tests (TDD)

```python
# tests/test_my_feature.py
def test_my_feature():
    result = my_function()
    assert result == expected
```

### 3. Implement Feature

```python
# src/my_module.py
def my_function():
    return result
```

### 4. Run Tests

```bash
pytest tests/test_my_feature.py -v
```

### 5. Commit Changes

```bash
git add .
git commit -m "feat(scope): Add my feature"
```

### 6. Create Pull Request

Submit PR with description, tests, and documentation.

---

## Code Standards

### Python Style

Follow PEP 8:

```python
# Good
def calculate_total(items: List[Item]) -> float:
    """Calculate total price of items."""
    return sum(item.price for item in items)

# Bad
def calc(x):
    return sum([i.price for i in x])
```

### Type Hints

Use type hints:

```python
from typing import List, Dict, Optional

def process_data(
    data: List[Dict[str, str]],
    options: Optional[Dict] = None
) -> bool:
    pass
```

### Docstrings

Use Google-style docstrings:

```python
def my_function(param1: str, param2: int) -> bool:
    """Short description.
    
    Longer description explaining behavior.
    
    Args:
        param1: Description of param1
        param2: Description of param2
        
    Returns:
        Description of return value
        
    Raises:
        ValueError: When validation fails
    """
    pass
```

---

## Testing

### Unit Tests

```python
import pytest
from src.tier1.working_memory import WorkingMemory

def test_store_conversation():
    memory = WorkingMemory()
    conv_id = memory.store_conversation(
        user_message="Test",
        assistant_response="Response",
        intent="TEST"
    )
    assert conv_id is not None
```

### Integration Tests

```python
def test_full_workflow():
    # Test complete operation
    result = execute_operation("setup")
    assert result.success == True
```

### Run Tests

```bash
# All tests
pytest tests/ -v

# Specific module
pytest tests/tier1/ -v

# With coverage
pytest tests/ --cov=src --cov-report=html
```

---

## Agent Development

### Creating an Agent

```python
from src.cortex_agents.base_agent import BaseAgent

class MyAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="my-agent",
            hemisphere="right"
        )
    
    def execute(self, context):
        # Agent logic
        return {"success": True}
```

### Registering Agent

```python
from src.core.agent_coordinator import AgentCoordinator

coordinator = AgentCoordinator()
coordinator.register_agent(MyAgent())
```

---

## Plugin Development

### Creating a Plugin

```python
from src.plugins.base_plugin import BasePlugin

class MyPlugin(BasePlugin):
    def execute(self, context):
        # Plugin logic
        return {"success": True}
```

See: [VS Code Extension Guide](https://code.visualstudio.com/api/get-started/your-first-extension)

---

## Documentation

### Docstring Documentation

All public functions need docstrings.

### README Updates

Update relevant README files when adding features.

### MkDocs Documentation

Add pages to `docs/` directory:

```markdown
# My Feature

Description of feature...
```

---

## Performance Optimization

### Profiling

```python
import cProfile

profiler = cProfile.Profile()
profiler.enable()
# Your code
profiler.disable()
profiler.print_stats()
```

### Benchmarking

```python
import timeit

time = timeit.timeit(
    lambda: my_function(),
    number=1000
)
print(f"Average: {time/1000:.4f}s")
```

---

## Debugging

### VS Code Debugging

Configure `.vscode/launch.json`:

```json
{
  "type": "python",
  "request": "launch",
  "program": "${file}",
  "console": "integratedTerminal"
}
```

### Logging

```python
import logging

logger = logging.getLogger(__name__)
logger.debug("Debug message")
logger.info("Info message")
logger.error("Error message")
```

---

## Contributing

### Contribution Process

1. Fork repository
2. Create feature branch
3. Write tests
4. Implement feature
5. Run full test suite
6. Submit pull request

### Commit Messages

Follow semantic commits:

```
feat(scope): Add new feature
fix(scope): Fix bug
docs(scope): Update documentation
test(scope): Add tests
refactor(scope): Refactor code
```

---

## Related Documentation

- **Architecture:** [Architecture Overview](../architecture/overview.md)
- **API Reference:** [API](../reference/api-reference.md)
- **Testing:** Run `pytest tests/ -v`

---

**Copyright:** © 2024-2025 Asif Hussain. All rights reserved.  
**License:** Proprietary - See LICENSE file  
**Version:**   
**Generated:** 