# CORTEX API Documentation

**Version:** 2.0  
**Last Updated:** 2025-11-10  
**Status:** Auto-generated from source code docstrings

---

## Overview

This directory contains comprehensive API documentation for the CORTEX cognitive framework. Documentation is automatically generated from Python docstrings using the `scan_docstrings_module` and `generate_api_docs_module`.

---

## Documentation Structure

```
docs/api/
├── README.md (this file)
├── operations/
│   ├── overview.md
│   ├── environment_setup.md
│   ├── story_refresh.md
│   ├── workspace_cleanup.md
│   ├── documentation_update.md
│   ├── brain_protection.md
│   └── test_execution.md
├── modules/
│   ├── base_operation_module.md
│   └── [43 individual module docs]
├── tier0/
│   ├── brain_protector.md
│   └── protection_rules.md
├── tier1/
│   ├── conversation_tracker.md
│   └── working_memory.md
├── tier2/
│   ├── knowledge_graph.md
│   └── pattern_matcher.md
├── tier3/
│   ├── context_intelligence.md
│   └── development_metrics.md
└── agents/
    ├── intent_detector.md
    ├── work_planner.md
    ├── executor.md
    ├── tester.md
    └── [10 agent docs]
```

---

## Quick Links

### Core Systems

- [Universal Operations System](./operations/overview.md) - Modular operation architecture
- [Brain Protection (Tier 0)](./tier0/brain_protector.md) - Governance layer
- [Working Memory (Tier 1)](./tier1/working_memory.md) - Conversation tracking
- [Knowledge Graph (Tier 2)](./tier2/knowledge_graph.md) - Pattern learning
- [Context Intelligence (Tier 3)](./tier3/context_intelligence.md) - Dev metrics

### Operations

- [Environment Setup](./operations/environment_setup.md) - Platform configuration
- [Story Refresh](./operations/story_refresh.md) - Documentation maintenance
- [Workspace Cleanup](./operations/workspace_cleanup.md) - File cleanup
- [Documentation Update](./operations/documentation_update.md) - Doc generation
- [Brain Protection Check](./operations/brain_protection.md) - Integrity validation
- [Test Execution](./operations/test_execution.md) - Test runner

### Agents

- [Intent Detector](./agents/intent_detector.md) - Request routing
- [Work Planner](./agents/work_planner.md) - Task breakdown
- [Executor](./agents/executor.md) - Implementation
- [Tester](./agents/tester.md) - Test generation
- [Validator](./agents/validator.md) - Quality assurance

---

## Usage Examples

### Importing Modules

```python
# Import specific module
from src.operations.modules import LoadStoryTemplateModule

# Import operation execution function
from src.operations import execute_operation

# Import base classes
from src.operations.base_operation_module import (
    BaseOperationModule,
    ModuleMetadata,
    ExecutionPhase,
    OperationResult
)
```

### Executing Operations

```python
# Execute with default profile
report = execute_operation('refresh cortex story')

# Execute with specific profile
report = execute_operation('setup environment', profile='full')

# Check results
if report.success:
    print(f"✅ Operation succeeded in {report.duration}s")
    print(f"Modules: {report.modules_succeeded}/{report.total_modules}")
else:
    print(f"❌ Operation failed: {report.error}")
```

### Creating Custom Modules

```python
from src.operations.base_operation_module import (
    BaseOperationModule,
    ModuleMetadata,
    ExecutionPhase,
    OperationResult
)
from typing import Dict, Any

class MyCustomModule(BaseOperationModule):
    """Custom module for specific functionality."""
    
    def get_metadata(self) -> ModuleMetadata:
        """Return module metadata."""
        return ModuleMetadata(
            module_id="my_custom_module",
            name="My Custom Module",
            phase=ExecutionPhase.PROCESSING,
            description="Does custom processing",
            dependencies=[]
        )
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Execute module logic."""
        try:
            # Your custom logic here
            result_data = {"processed": True}
            
            return OperationResult.success(
                message="Custom processing complete",
                data=result_data
            )
        except Exception as e:
            return OperationResult.failure(
                message=f"Custom processing failed: {e}",
                error=str(e)
            )
```

---

## API Conventions

### Naming Conventions

- **Modules:** `module_name_module.py` (e.g., `load_story_template_module.py`)
- **Classes:** `ModuleNameModule` (e.g., `LoadStoryTemplateModule`)
- **Functions:** `snake_case` (e.g., `execute`, `should_run`, `rollback`)
- **Constants:** `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`)

### Module Structure

All modules follow this structure:

```python
class ModuleNameModule(BaseOperationModule):
    """Module description.
    
    Detailed explanation of what the module does,
    its purpose, and when to use it.
    """
    
    def get_metadata(self) -> ModuleMetadata:
        """Return module metadata.
        
        Returns:
            ModuleMetadata: Module configuration
        """
        pass
    
    def should_run(self, context: Dict[str, Any]) -> bool:
        """Check if module should execute.
        
        Args:
            context: Shared execution context
            
        Returns:
            bool: True if module should run
        """
        return True
    
    def execute(self, context: Dict[str, Any]) -> OperationResult:
        """Execute module logic.
        
        Args:
            context: Shared execution context
            
        Returns:
            OperationResult: Execution result
        """
        pass
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """Rollback changes if operation fails.
        
        Args:
            context: Shared execution context
            
        Returns:
            bool: True if rollback successful
        """
        return True
```

### Return Values

All modules return `OperationResult`:

```python
# Success
OperationResult.success(
    message="Operation succeeded",
    data={"key": "value"}
)

# Failure
OperationResult.failure(
    message="Operation failed",
    error="Error details"
)

# Warning
OperationResult.warning(
    message="Operation succeeded with warnings",
    data={"warnings": ["warning1", "warning2"]}
)
```

### Context Dictionary

Modules communicate via shared context:

```python
context = {
    # Standard keys (always present)
    'project_root': Path('/path/to/cortex'),
    'profile': 'standard',  # minimal, standard, full
    'platform': 'windows',  # windows, darwin, linux
    
    # Module-specific keys (added during execution)
    'story_content': "# Story title...",
    'transformed_story': "# Transformed...",
    'validation_warnings': [],
    'story_file_path': Path('...'),
}
```

---

## Documentation Generation

### Auto-Generation Command

```bash
# Scan docstrings and generate docs
python -m src.operations.modules.scan_docstrings_module
python -m src.operations.modules.generate_api_docs_module

# Or use the operation
/CORTEX update documentation
```

### Manual Updates

If you need to update documentation manually:

1. Edit the source Python file
2. Update the docstring
3. Run the documentation generation command
4. Verify the generated Markdown

### Docstring Format

Use Google-style docstrings:

```python
def function_name(arg1: str, arg2: int) -> bool:
    """Short description.
    
    Longer description with more details about
    what the function does and how to use it.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        bool: Description of return value
        
    Raises:
        ValueError: When arg1 is invalid
        IOError: When file operation fails
        
    Examples:
        >>> result = function_name("test", 42)
        >>> print(result)
        True
    """
    pass
```

---

## Version History

### Version 2.0 (2025-11-10)

- ✅ Universal Operations architecture
- ✅ 43 modules across 7 operations
- ✅ Auto-generated API documentation
- ✅ Comprehensive docstrings
- ✅ Google-style docstring format

### Version 1.0 (2025-11-01)

- Initial CORTEX framework
- Basic agent system
- Tier 0-3 architecture
- Manual documentation

---

## Contributing

### Adding New API Documentation

1. Create/update Python file with comprehensive docstrings
2. Run documentation generation:
   ```bash
   python scripts/generate_api_docs.py
   ```
3. Verify generated Markdown in `docs/api/`
4. Commit both source and generated docs

### Documentation Standards

- **Coverage:** Every public class/function must have docstring
- **Format:** Use Google-style docstrings
- **Examples:** Include usage examples where helpful
- **Types:** Use type hints (Args, Returns)
- **Raises:** Document all exceptions

---

## Support

### Getting Help

- **Documentation Issues:** Open GitHub issue with `docs` label
- **API Questions:** Ask in GitHub Discussions
- **Bug Reports:** Use issue template

### Useful Links

- [Main README](../../README.md)
- [Architecture Guide](../architecture/)
- [Module Integration Report](../../cortex-brain/MODULE-INTEGRATION-REPORT.md)
- [Operations Config](../../cortex-brain/operations-config.yaml)

---

*This documentation is auto-generated from source code. Last updated: 2025-11-10*
