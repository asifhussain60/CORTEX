# documentation_orchestrator

Documentation Orchestrator - Auto-generate comprehensive technical documentation

Phase-based documentation generation workflow:
1. ANALYZE: Scan target modules and extract metadata
2. EXTRACT: Parse code structure and type information
3. GENERATE_DOCS: Create API documentation
4. GENERATE_DIAGRAMS: Create D3.js visualizations
5. VALIDATE: Verify documentation completeness
6. EXPORT: Save all documentation files


## Table of Contents

### Classes
- [DocumentationConfig](#documentationconfig)
- [DocumentationResult](#documentationresult)
- [DocumentationOrchestrator](#documentationorchestrator)


## Overview

- **Classes:** 3
- **Functions:** 0
- **Dependencies:** base, dataclasses, extractors, generators, logging, pathlib, typing


## Classes

### DocumentationConfig

```python
class DocumentationConfig
```

**Decorators:** `dataclass`

Configuration for documentation generation


**Attributes:**

- `source_paths`: List[Path]
- `output_dir`: Path
- `include_private`: bool
- `generate_diagrams`: bool
- `generate_quick_ref`: bool
- `diagram_types`: List[str]



---

### DocumentationResult

```python
class DocumentationResult
```

**Decorators:** `dataclass`

Results from documentation generation


**Attributes:**

- `modules_analyzed`: int
- `classes_documented`: int
- `functions_documented`: int
- `diagrams_generated`: int
- `output_files`: List[Path]
- `errors`: List[str]
- `warnings`: List[str]



---

### DocumentationOrchestrator

```python
class DocumentationOrchestrator(BaseOrchestrator)
```

Orchestrates comprehensive technical documentation generation

Features:
- AST-based code analysis
- Type hint extraction
- API documentation generation
- Interactive D3.js diagrams
- Phase flow visualization
- Class hierarchy diagrams

Example:
    orchestrator = DocumentationOrchestrator(logger, config)
    
    context = {
        'config': DocumentationConfig(
            source_paths=[Path("src/orchestration_4_0")],
            output_dir=Path("docs/orchestration")
        )
    }
    
    result = orchestrator.execute(context)
    print(f"Documented {result['modules_analyzed']} modules")


**Methods:**


---
