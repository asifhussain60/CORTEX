# Test Fixtures

**Authority:** AC-GOLDEN-FRAMEWORK-001  
**Purpose:** Shared test data for orchestrator golden tests

## Directory Structure

```
fixtures/
├── orchestrator-configs/    # Orchestrator configuration YAMLs
├── sample-repos/           # Sample repository structures for testing
└── knowledge-bases/        # Sample knowledge base YAMLs
```

## Fixture Types

### orchestrator-configs/
Pre-configured orchestrator YAML files for testing:
- Minimal valid configuration
- Maximum complexity configuration
- Invalid configurations (for negative tests)
- Edge case configurations

### sample-repos/
Sample repository structures:
- Empty repository (0 files)
- Minimal Python project (1 file)
- Standard CORTEX project structure
- Large repository (1000+ files)
- Multi-language repository

### knowledge-bases/
Sample knowledge base YAMLs:
- Company domain knowledge
- CORTEX knowledge
- Best practices YAML
- Security policies

## Usage

```python
import pytest
from pathlib import Path

@pytest.fixture
def orchestrator_config(request):
    """Load orchestrator configuration fixture."""
    config_name = request.param
    config_path = Path("tests/fixtures/orchestrator-configs") / f"{config_name}.yaml"
    import yaml
    with open(config_path) as f:
        return yaml.safe_load(f)

@pytest.mark.parametrize("orchestrator_config", ["minimal", "maximal"], indirect=True)
def test_orchestrator_config(orchestrator_config):
    assert orchestrator_config is not None
```

## Adding New Fixtures

1. Create fixture file in appropriate directory
2. Follow kebab-case naming (CORE-028)
3. Add documentation in this README
4. Update fixture index if needed
