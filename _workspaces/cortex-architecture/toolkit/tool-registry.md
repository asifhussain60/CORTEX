# Tool Registry

**Purpose:** Documentation of the CORTEX tool registration system  
**Audience:** Developers, Contributors  
**Last Updated:** 2026-02-10

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

```python
class ToolRegistry:
    """Central registry for all CORTEX tools."""
    
    def __init__(self):
        self._tools: Dict[str, Tool] = {}
        self._metadata: Dict[str, ToolMetadata] = {}
        self._categories: Dict[ToolCategory, List[str]] = {}
        self._versions: Dict[str, List[str]] = {}
        self._deprecated: Set[str] = set()
    
    def register(self, tool: Tool, metadata: ToolMetadata):
        """Register a tool with metadata."""
        name = tool.name
        
        # Validate
        self._validate_tool(tool, metadata)
        
        # Store
        self._tools[name] = tool
        self._metadata[name] = metadata
        
        # Index by category
        category = metadata.category
        if category not in self._categories:
            self._categories[category] = []
        self._categories[category].append(name)
        
        # Version tracking
        if name not in self._versions:
            self._versions[name] = []
        self._versions[name].append(metadata.version)
    
    def get(self, name: str) -> Optional[Tool]:
        """Get tool by name."""
        return self._tools.get(name)
    
    def list_by_category(
        self,
        category: ToolCategory
    ) -> List[ToolMetadata]:
        """List tools in category."""
        names = self._categories.get(category, [])
        return [self._metadata[n] for n in names]
```

### Tool Metadata

```python
@dataclass
class ToolMetadata:
    """Metadata for a registered tool."""
    
    name: str
    category: ToolCategory
    description: str
    version: str
    
    # Parameters
    parameters: List[ToolParameter]
    required_parameters: List[str]
    
    # Documentation
    examples: List[ToolExample]
    related_tools: List[str]
    
    # Lifecycle
    created_at: datetime
    updated_at: datetime
    deprecated: bool = False
    replacement: Optional[str] = None
    
    # Performance
    avg_latency_ms: Optional[float] = None
    timeout_ms: int = 30000

@dataclass
class ToolParameter:
    """Parameter definition for a tool."""
    
    name: str
    type: str  # string, number, boolean, object, array
    description: str
    required: bool
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None
    pattern: Optional[str] = None
```

---

## Tool Registration

### Registration Process

```python
# Step 1: Define the tool
class LENSAnalyzeTool(Tool):
    """LENS analysis tool."""
    
    @property
    def name(self) -> str:
        return "cortex_lens_analyze"
    
    @property
    def description(self) -> str:
        return "Perform comprehensive code analysis using LENS"
    
    async def execute(
        self,
        arguments: Dict[str, Any]
    ) -> ToolResult:
        target = arguments["target"]
        analyzers = arguments.get("analyzers", ["all"])
        
        lens = LENSOrchestrator()
        result = await lens.analyze(target, analyzers)
        
        return ToolResult(
            success=True,
            data=result.to_dict()
        )

# Step 2: Create metadata
metadata = ToolMetadata(
    name="cortex_lens_analyze",
    category=ToolCategory.ANALYSIS,
    description="Perform comprehensive code analysis using LENS",
    version="1.0.0",
    parameters=[
        ToolParameter(
            name="target",
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
