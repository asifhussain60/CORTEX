# Tool Registry

---
title: Tool Registry - Central Tool Catalog and Lifecycle Management
type: reference
audience: [Product Owners, Software Developers]
word_count: 1400
last_verified: 2026-02-15
source_of_truth: cortex/tools/registry.py + cortex-registry/
format: diátaxis-reference
voice: third-person-neutral
phase: Production (v8.1)
order: 4
---

> **Notice:** Tool registry implements hot-reload capability for dynamic tool updates without server restart. Organizations benefit from continuous tool availability during updates. Registry data persists in git-backed storage (cortex-registry/master/) requiring no runtime database.

---

**Purpose:** The connectome registry — a living map of every tool-neuron, its synaptic connections, and activation patterns within the CORTEX brain  
**Audience:** Product Owners, Software Developers  
**Last Updated:** 2026-02-15

---

## Table of Contents

- [Overview](#overview)
- [Registry Architecture](#registry-architecture)
- [Tool Registration](#tool-registration)
- [Tool Resolution](#tool-resolution)
- [Versioning](#versioning)
- [Related Documents](#related-documents)

---

## Overview

The Tool Registry is the central catalog of all CORTEX tools. It manages tool lifecycle, discovery, and invocation routing.

```
┌─────────────────────────────────────────────────────────────────┐
│                     TOOL REGISTRY                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   ToolRegistry                           │   │
│  │                                                          │   │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │   │
│  │  │   Tools     │  │  Metadata   │  │  Versions   │     │   │
│  │  │   Map       │  │   Store     │  │   Index     │     │   │
│  │  └─────────────┘  └─────────────┘  └─────────────┘     │   │
│  │                                                          │   │
│  │  ┌─────────────┐  ┌─────────────┐                       │   │
│  │  │  Category   │  │ Deprecation │                       │   │
│  │  │   Index     │  │   Tracker   │                       │   │
│  │  └─────────────┘  └─────────────┘                       │   │
│  │                                                          │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Registry Architecture

### Core Components

The Tool Registry maintains centralized registration of all CORTEX tools with comprehensive metadata tracking. The registry stores tool instances, metadata information, category indices, version histories, and deprecation status. Registration includes validation, storage, category indexing, and version tracking to ensure tools are properly catalogued and discoverable.

**Registry Capabilities:**
- Tool registration with metadata validation
- Retrieval by name or category
- Version tracking and history
- Deprecation management
- Cross-referencing of related tools

### Tool Metadata

Registered tools include comprehensive metadata covering identification (name, category, description, version), parameter specifications (type, description, required/optional status, defaults), documentation (examples, related tools), lifecycle information (creation/update timestamps, deprecation status), and performance characteristics (average latency, timeout limits).

---

## Tool Registration

### Registration Process

Tools are registered through a multi-step process:

1. **Define Tool** — Create tool class with name, description, and execute method
2. **Create Metadata** — Specify category, version, parameters, and documentation
3. **Register** — Submit tool and metadata to registry for validation and indexing

**Required Components:**
- Unique tool name (following `cortex_*` convention)
- Category assignment (ANALYSIS, DEBUG, DEPLOYMENT, etc.)
- Parameter definitions with types and validation rules
- Version number following semantic versioning
- Documentation including description and usage examples
            type="string",
            description="File or directory to analyze",
            required=True
        ),
        ToolParameter(
            name="analyzers",
            type="array",
            description="Specific analyzers to use",
            required=False,
            default=["all"]
        )
    ],
    required_parameters=["target"],
    examples=[
        ToolExample(
            description="Analyze a Python file",
            arguments={"target": "src/app.py"},
            result={"success": True}
        )
    ],
    related_tools=["cortex_ast_analyze", "cortex_git_history"]
)

# Step 3: Register
registry = ToolRegistry.instance()
registry.register(LENSAnalyzeTool(), metadata)
```

### Automatic Registration

```python
# Using decorator
@register_tool(
    category=ToolCategory.ANALYSIS,
    version="1.0.0"
)
class LENSAnalyzeTool(Tool):
    """Automatically registered on import."""
    pass

# Registration decorator implementation
def register_tool(
    category: ToolCategory,
    version: str
):
    """Decorator for automatic tool registration."""
    def decorator(cls):
        # Create instance
        tool = cls()
        
        # Extract metadata from class
        metadata = ToolMetadata(
            name=tool.name,
            category=category,
            description=tool.description,
            version=version,
            parameters=tool.get_parameters(),
            required_parameters=tool.get_required_parameters(),
            examples=getattr(tool, 'examples', []),
            related_tools=getattr(tool, 'related_tools', [])
        )
        
        # Register
        ToolRegistry.instance().register(tool, metadata)
        
        return cls
    return decorator
```

---

## Tool Resolution

### Resolution Process

```python
class ToolResolver:
    """Resolves tool invocations to handlers."""
    
    def __init__(self, registry: ToolRegistry):
        self.registry = registry
    
    def resolve(
        self,
        tool_name: str,
        version: Optional[str] = None
    ) -> Optional[Tool]:
        """
        Resolve tool name to handler.
        
        Args:
            tool_name: Name of tool to resolve
            version: Optional specific version
        
        Returns:
            Tool instance or None
        """
        # Check for exact match
        tool = self.registry.get(tool_name)
        
        if not tool:
            # Try alias resolution
            tool = self._resolve_alias(tool_name)
        
        if not tool:
            return None
        
        # Check version if specified
        if version:
            if not self._version_compatible(tool_name, version):
                return None
        
        # Check deprecation
        if self.registry.is_deprecated(tool_name):
            replacement = self.registry.get_replacement(tool_name)
            if replacement:
                logger.warning(
                    f"Tool {tool_name} is deprecated, "
                    f"use {replacement} instead"
                )
        
        return tool
```

### Alias Resolution

```python
TOOL_ALIASES = {
    "analyze": "cortex_lens_analyze",
    "lens": "cortex_lens_analyze",
    "git": "cortex_git_history",
    "ast": "cortex_ast_analyze",
    "duplicates": "cortex_detect_duplicates",
    "audit": "cortex_audit",
    "plan": "cortex_plan_resolve",
}

def _resolve_alias(self, name: str) -> Optional[Tool]:
    """Resolve tool alias to full name."""
    if name in TOOL_ALIASES:
        return self.registry.get(TOOL_ALIASES[name])
    return None
```

---

## Versioning

### Version Schema

```
{major}.{minor}.{patch}

Examples:
- 1.0.0 - Initial release
- 1.1.0 - Backward-compatible features
- 1.1.1 - Bug fixes
- 2.0.0 - Breaking changes
```

### Version Compatibility

```python
class VersionChecker:
    """Check version compatibility."""
    
    def is_compatible(
        self,
        requested: str,
        available: str
    ) -> bool:
        """
        Check if available version satisfies request.
        
        Compatibility rules:
        - Same major version
        - Available minor >= requested minor
        """
        req = self._parse(requested)
        avail = self._parse(available)
        
        # Major must match
        if req[0] != avail[0]:
            return False
        
        # Available minor must be >= requested
        if avail[1] < req[1]:
            return False
        
        return True
    
    def _parse(self, version: str) -> Tuple[int, int, int]:
        """Parse version string."""
        parts = version.split(".")
        return (
            int(parts[0]),
            int(parts[1]) if len(parts) > 1 else 0,
            int(parts[2]) if len(parts) > 2 else 0
        )
```

### Deprecation Management

```python
class DeprecationManager:
    """Manage tool deprecation lifecycle."""
    
    def deprecate(
        self,
        tool_name: str,
        replacement: Optional[str] = None,
        removal_version: Optional[str] = None
    ):
        """Mark tool as deprecated."""
        self.registry._deprecated.add(tool_name)
        
        if replacement:
            self._replacements[tool_name] = replacement
        
        if removal_version:
            self._removal_versions[tool_name] = removal_version
        
        logger.warning(
            f"Tool {tool_name} deprecated"
            + (f", use {replacement}" if replacement else "")
            + (f", removal in {removal_version}" if removal_version else "")
        )
```

---

## Related Documents

- [Toolkit Overview](overview.md) — Tool ecosystem
- [Tool Categories](tool-categories.md) — Categorization
- [Developer Guide](developer-guide.md) — Creating tools

---

*Part of CORTEX Architecture Documentation*
