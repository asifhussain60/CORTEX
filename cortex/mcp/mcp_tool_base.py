"""
MCP Tool Base Classes and Data Models.

Provides the foundation for all MCP tools with:
- Type-safe parameter definitions
- Consistent execution interface
- Structured result formatting
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import json


class ToolCategory(Enum):  # CORE-035-scoped — domain-specific tool taxonomy
    """
    Tool categories for organization and discovery.

    Each tool belongs to exactly one category based on its
    primary business capability.
    """
    CORE = "core"               # Request processing, challenge
    INTELLIGENCE = "intelligence"  # LENS, knowledge, AST
    GOVERNANCE = "governance"   # Validation, compliance, rules
    OPERATIONS = "operations"   # Debug, refactor, plan
    UTILITIES = "utilities"     # Verify, vacuum, catalog


@dataclass
class ToolParameter:
    """
    MCP Tool Parameter Definition (MCP v2024-11-05 compliant).

    Attributes:
        name: Parameter name (snake_case)
        type: JSON Schema type (string, number, boolean, array, object)
        required: Whether parameter is required
        description: Human-readable description
        default: Default value if optional
        enum: Allowed values (for validation)
    """
    name: str
    type: str
    required: bool = True
    description: str = ""
    default: Optional[Any] = None
    enum: Optional[List[Any]] = None

    def to_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format."""
        schema: Dict[str, Any] = {
            "type": self.type,
            "description": self.description,
        }
        if self.default is not None:
            schema["default"] = self.default
        if self.enum:
            schema["enum"] = self.enum
        return schema


@dataclass
class ToolDefinition:
    """
    Complete MCP Tool Definition.

    Attributes:
        name: Unique tool identifier (cortex_*)
        description: What the tool does
        category: Business capability category
        parameters: Input parameters
        operations: Sub-operations (for consolidated tools)
        version: Tool version
    """
    name: str
    description: str
    category: ToolCategory
    parameters: List[ToolParameter] = field(default_factory=list)
    operations: List[str] = field(default_factory=list)
    version: str = "1.0"

    def to_mcp_schema(self) -> Dict[str, Any]:
        """
        Convert to MCP protocol schema format.

        Returns:
            MCP-compliant tool definition
        """
        properties: Dict[str, Any] = {}
        required: List[str] = []

        for param in self.parameters:
            properties[param.name] = param.to_schema()
            if param.required:
                required.append(param.name)

        return {
            "name": self.name,
            "description": self.description,
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
        }


@dataclass
class ToolResult:
    """
    Standardized tool execution result.

    All tools return this structure for consistency.
    """
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        result = {
            "success": self.success,
            "timestamp": datetime.utcnow().isoformat(),
        }
        if self.data is not None:
            result["data"] = self.data
        if self.error:
            result["error"] = self.error
        if self.metadata:
            result["metadata"] = self.metadata
        return result

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps(self.to_dict(), default=str)


class Tool(ABC):
    """
    Abstract base class for all MCP tools.

    Every tool must:
    1. Define its metadata via `definition` property
    2. Implement `execute()` method
    3. Return ToolResult from execute()

    Example:
        class MyTool(Tool):
            @property
            def definition(self) -> ToolDefinition:
                return ToolDefinition(
                    name="cortex_my_tool",
                    description="Does something useful",
                    category=ToolCategory.UTILITIES,
                )

            def execute(self, **kwargs) -> ToolResult:
                return ToolResult(success=True, data={"result": "done"})
    """

    @property
    @abstractmethod
    def definition(self) -> ToolDefinition:
        """Get tool definition (name, description, parameters)."""
        pass

    @abstractmethod
    def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute tool with given parameters.

        Args:
            **kwargs: Tool-specific parameters

        Returns:
            ToolResult with success status and data/error
        """
        pass

    def validate_params(self, **kwargs: Any) -> Optional[str]:
        """
        Validate parameters against definition.

        Args:
            **kwargs: Parameters to validate

        Returns:
            Error message if validation fails, None if valid
        """
        definition = self.definition

        # Check required parameters
        for param in definition.parameters:
            if param.required and param.name not in kwargs:
                return f"Missing required parameter: {param.name}"

            # Validate enum values
            if param.name in kwargs and param.enum:
                if kwargs[param.name] not in param.enum:
                    return f"Invalid value for {param.name}: must be one of {param.enum}"

        return None


class ConsolidatedTool(Tool):
    """
    Base class for consolidated tools with multiple operations.

    Consolidated tools use an `operation` parameter to route
    to different sub-functions, reducing tool count while
    maintaining functionality.

    Subclasses must implement:
    - name: Tool name property
    - description: Tool description property
    - category: Tool category property
    - parameters: List of ToolParameter
    - supported_operations: List of operation strings
    - execute(**params): Async execution method

    Example:
        cortex_debug(operation="inject", ...) → handles inject
        cortex_debug(operation="capture", ...) → handles capture
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name (e.g., 'cortex_debug')."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Tool description."""
        pass

    @property
    @abstractmethod
    def category(self) -> ToolCategory:
        """Tool category."""
        pass

    @property
    @abstractmethod
    def parameters(self) -> List[ToolParameter]:
        """Tool parameters."""
        pass

    @property
    @abstractmethod
    def supported_operations(self) -> List[str]:
        """List of supported operation names."""
        pass

    @property
    def definition(self) -> ToolDefinition:
        """Generate ToolDefinition from properties."""
        return ToolDefinition(
            name=self.name,
            description=self.description,
            category=self.category,
            parameters=self.parameters,
        )

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        """
        Execute a specific operation.

        Args:
            **kwargs: Operation-specific parameters (including 'operation')

        Returns:
            ToolResult from the operation
        """
        pass

    def format_response(self, result: "ToolResult") -> "ToolResult":
        """Apply post-processing formatting to a ToolResult.

        Marks the result as formatted by setting ``metadata['formatted'] = True``
        and normalising the data payload for consistent downstream rendering.

        This hook is called on every MCP tool output to ensure a uniform
        response contract (GAP-66-004 — Phase 66-A).

        Args:
            result: Raw :class:`ToolResult` from ``execute()``.

        Returns:
            A new :class:`ToolResult` with ``metadata['formatted']`` set to
            ``True``.
        """
        metadata = dict(result.metadata) if result.metadata else {}
        metadata["formatted"] = True
        return ToolResult(
            success=result.success,
            data=result.data,
            error=result.error,
            metadata=metadata,
        )
