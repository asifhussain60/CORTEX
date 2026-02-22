# AC_START: AC-MEGA-B-S2-001
"""
MCP Tool Scanner - Extract metadata from @mcp_tool decorators.

Purpose:
    Auto-generate MCP tool documentation by scanning Python source code for
    @mcp_tool decorators. Eliminates manual documentation effort and prevents
    drift between code and docs.

Features:
    - AST-based decorator extraction
    - Parameter schema parsing from type hints
    - Docstring description extraction
    - Directory recursive scanning
    - Tool filtering by pattern/auth level

Example:
    >>> scanner = MCPToolScanner()
    >>> tools = scanner.scan_directory(Path("cortex/mcp/tools"))
    >>> print(f"Found {len(tools)} tools")
    Found 78 tools

Integration Points:
    - GitAwareDeltaDetector: Incremental doc updates
    - HTMLGenerator: GitHub Pages catalog generation
    - MCP Gateway: Tool registry validation

Authority:
    - phase-22-developer-experience-tooling.yaml (Stage 2)
    - MCP specification (tool metadata requirements)

Governance:
    - CORE-011: Type hints 100%
    - CORE-012: Google-style docstrings
    - CORE-030: Implementation Truth (verify actual decorators)

Author: Asif Hussain
Date: 2026-02-16
"""

import ast
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional


@dataclass
class ToolMetadata:
    """
    Metadata extracted from @mcp_tool decorator.
    
    Attributes:
        name: Tool name (e.g., "cortex.lens")
        description: Short description from decorator
        version: Tool version (e.g., "1.0")
        auth_level: Authentication level (public/admin/internal)
        parameters: Parameter schema {name: {type, required, default, description}}
        detailed_description: Full description from docstring
        source_file: Source file path
        line_number: Decorator line number
    """
    name: str
    description: str
    version: str
    auth_level: str = "public"
    parameters: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    detailed_description: str = ""
    source_file: str = ""
    line_number: int = 0


class MCPToolScanner:
    """
    Scan Python source code for @mcp_tool decorators and extract metadata.
    
    This scanner uses AST parsing to extract tool metadata without executing
    code, making it safe for scanning untrusted sources.
    
    Features:
        - Safe AST-based parsing (no code execution)
        - Type hint extraction for parameter schemas
        - Docstring parsing for descriptions
        - Recursive directory scanning
        - Pattern-based filtering
    
    Example:
        >>> scanner = MCPToolScanner()
        >>> 
        >>> # Scan single file
        >>> tools = scanner.scan_file(Path("cortex/mcp/tools/lens_tools.py"))
        >>> 
        >>> # Scan directory recursively
        >>> all_tools = scanner.scan_directory(Path("cortex/mcp/tools"))
        >>> 
        >>> # Filter results
        >>> public_tools = scanner.filter_tools(all_tools, auth_level="public")
    """
    
    def __init__(self) -> None:
        """Initialize the scanner."""
        self._initialized = True
    
    def scan_code(self, code: str, source_file: str = "<string>") -> List[ToolMetadata]:
        """
        Scan Python code string for @mcp_tool decorators.
        
        Args:
            code: Python source code to scan
            source_file: Source file path for error messages
        
        Returns:
            List of extracted tool metadata. Empty list if syntax errors.
        
        Example:
            >>> scanner = MCPToolScanner()
            >>> code = '''
            ... @mcp_tool("cortex_test", "Test tool", "1.0")
            ... def test_tool():
            ...     pass
            ... '''
            >>> tools = scanner.scan_code(code)
            >>> len(tools)
            1
        """
        try:
            tree = ast.parse(code, filename=source_file)
        except SyntaxError:
            # Return empty list on syntax errors
            return []
        
        tools: List[ToolMetadata] = []
        
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                tool = self._extract_tool_from_function(node, source_file)
                if tool:
                    tools.append(tool)
        
        return tools
    
    def scan_file(self, file_path: Path) -> List[ToolMetadata]:
        """
        Scan a single Python file for @mcp_tool decorators.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            List of extracted tool metadata
        
        Raises:
            FileNotFoundError: If file does not exist
        
        Example:
            >>> scanner = MCPToolScanner()
            >>> tools = scanner.scan_file(Path("cortex/mcp/tools/lens_tools.py"))
            >>> for tool in tools:
            ...     print(f"{tool.name}: {tool.description}")
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        if not file_path.is_file():
            return []
        
        code = file_path.read_text(encoding="utf-8")
        return self.scan_code(code, str(file_path))
    
    def scan_directory(self, dir_path: Path, pattern: str = "**/*.py") -> List[ToolMetadata]:
        """
        Scan directory recursively for @mcp_tool decorators.
        
        Args:
            dir_path: Directory path to scan
            pattern: Glob pattern for file matching (default: **/*.py)
        
        Returns:
            List of all extracted tool metadata from all files
        
        Example:
            >>> scanner = MCPToolScanner()
            >>> tools = scanner.scan_directory(Path("cortex/mcp/tools"))
            >>> print(f"Found {len(tools)} tools across multiple files")
        """
        if not dir_path.exists() or not dir_path.is_dir():
            return []
        
        all_tools: List[ToolMetadata] = []
        
        for file_path in dir_path.rglob("*.py"):
            if file_path.is_file():
                tools = self.scan_file(file_path)
                all_tools.extend(tools)
        
        return all_tools
    
    def filter_tools(
        self,
        tools: List[ToolMetadata],
        name_pattern: Optional[str] = None,
        auth_level: Optional[str] = None,
    ) -> List[ToolMetadata]:
        """
        Filter tools by name pattern and/or auth level.
        
        Args:
            tools: List of tool metadata to filter
            name_pattern: Glob-style pattern (e.g., "cortex_*")
            auth_level: Filter by auth level (e.g., "public")
        
        Returns:
            Filtered list of tools
        
        Example:
            >>> scanner = MCPToolScanner()
            >>> all_tools = scanner.scan_directory(Path("cortex/mcp/tools"))
            >>> public_tools = scanner.filter_tools(all_tools, auth_level="public")
            >>> cortex_tools = scanner.filter_tools(all_tools, name_pattern="cortex_*")
        """
        filtered = tools
        
        if name_pattern:
            # Convert glob pattern to regex
            regex_pattern = name_pattern.replace("*", ".*").replace("?", ".")
            regex = re.compile(f"^{regex_pattern}$")
            filtered = [t for t in filtered if regex.match(t.name)]
        
        if auth_level:
            filtered = [t for t in filtered if t.auth_level == auth_level]
        
        return filtered
    
    def get_tool_by_name(self, tools: List[ToolMetadata], name: str) -> Optional[ToolMetadata]:
        """
        Get specific tool by exact name.
        
        Args:
            tools: List of tool metadata
            name: Exact tool name to find
        
        Returns:
            Tool metadata if found, None otherwise
        
        Example:
            >>> scanner = MCPToolScanner()
            >>> tools = scanner.scan_directory(Path("cortex/mcp/tools"))
            >>> lens_tool = scanner.get_tool_by_name(tools, "cortex.lens")
        """
        for tool in tools:
            if tool.name == name:
                return tool
        return None
    
    def _extract_tool_from_function(
        self,
        func_node: ast.FunctionDef,
        source_file: str,
    ) -> Optional[ToolMetadata]:
        """
        Extract tool metadata from function with @mcp_tool decorator.
        
        Args:
            func_node: AST function definition node
            source_file: Source file path
        
        Returns:
            Tool metadata if valid decorator found, None otherwise
        """
        # Look for @mcp_tool decorator
        for decorator in func_node.decorator_list:
            if isinstance(decorator, ast.Call):
                if isinstance(decorator.func, ast.Name) and decorator.func.id == "mcp_tool":
                    return self._parse_mcp_tool_decorator(decorator, func_node, source_file)
        
        return None
    
    def _parse_mcp_tool_decorator(
        self,
        decorator: ast.Call,
        func_node: ast.FunctionDef,
        source_file: str,
    ) -> Optional[ToolMetadata]:
        """
        Parse @mcp_tool decorator arguments.
        
        Args:
            decorator: AST call node for decorator
            func_node: Function definition node
            source_file: Source file path
        
        Returns:
            Tool metadata if valid, None if missing required args
        """
        # Extract positional arguments (name, description, version)
        if len(decorator.args) < 3:
            return None  # Missing required args
        
        name = self._extract_string_value(decorator.args[0])
        description = self._extract_string_value(decorator.args[1])
        version = self._extract_string_value(decorator.args[2])
        
        if not all([name, description, version]):
            return None
        
        # Extract keyword arguments
        auth_level = "public"
        for keyword in decorator.keywords:
            if keyword.arg == "auth_level":
                auth_level = self._extract_string_value(keyword.value) or "public"
        
        # Extract detailed description from docstring
        detailed_description = ast.get_docstring(func_node) or ""
        
        # Extract parameters
        parameters = self._extract_parameters(func_node)
        
        return ToolMetadata(
            name=name,
            description=description,
            version=version,
            auth_level=auth_level,
            parameters=parameters,
            detailed_description=detailed_description,
            source_file=source_file,
            line_number=decorator.lineno,
        )
    
    def _extract_string_value(self, node: ast.expr) -> Optional[str]:
        """
        Extract string value from AST node.
        
        Args:
            node: AST expression node
        
        Returns:
            String value if node is Constant/Str, None otherwise
        """
        if isinstance(node, ast.Constant) and isinstance(node.value, str):
            return node.value
        # Handle older Python versions
        if isinstance(node, ast.Str):
            return node.s
        return None
    
    def _extract_parameters(self, func_node: ast.FunctionDef) -> Dict[str, Dict[str, Any]]:
        """
        Extract parameter schema from function signature.
        
        Args:
            func_node: Function definition node
        
        Returns:
            Parameter schema dictionary
        """
        parameters: Dict[str, Dict[str, Any]] = {}
        
        args = func_node.args
        
        # Extract parameter descriptions from docstring
        param_descriptions = self._extract_param_descriptions(func_node)
        
        # Process all arguments
        all_args = args.args + args.posonlyargs + args.kwonlyargs
        
        # Get defaults
        defaults = [None] * (len(all_args) - len(args.defaults)) + args.defaults
        
        for i, arg in enumerate(all_args):
            param_name = arg.arg
            
            # Extract type hint
            param_type = "Any"
            required = True
            
            if arg.annotation:
                param_type = self._extract_type_annotation(arg.annotation)
                # Check if Optional
                if "Optional" in param_type:
                    required = False
            
            # Get default value
            default = None
            if i < len(defaults) and defaults[i] is not None:
                default = self._extract_default_value(defaults[i])
                required = False
            
            parameters[param_name] = {
                "type": param_type,
                "required": required,
                "default": default,
                "description": param_descriptions.get(param_name, ""),
            }
        
        return parameters
    
    def _extract_type_annotation(self, annotation: ast.expr) -> str:
        """
        Extract type annotation as string.
        
        Args:
            annotation: AST annotation node
        
        Returns:
            Type annotation string
        """
        if isinstance(annotation, ast.Name):
            return annotation.id
        elif isinstance(annotation, ast.Subscript):
            # Handle List[str], Dict[str, Any], etc.
            value = self._extract_type_annotation(annotation.value)
            slice_val = self._extract_type_annotation(annotation.slice)
            return f"{value}[{slice_val}]"
        elif isinstance(annotation, ast.Tuple):
            # Handle multiple types in subscript
            types = [self._extract_type_annotation(elt) for elt in annotation.elts]
            return ", ".join(types)
        else:
            return "Any"
    
    def _extract_default_value(self, default_node: ast.expr) -> Any:
        """
        Extract default value from AST node.
        
        Args:
            default_node: AST expression node
        
        Returns:
            Default value
        """
        if isinstance(default_node, ast.Constant):
            return default_node.value
        # Handle older Python versions
        if isinstance(default_node, (ast.Str, ast.Num)):
            if isinstance(default_node, ast.Str):
                return default_node.s
            elif isinstance(default_node, ast.Num):
                return default_node.n
        if isinstance(default_node, ast.NameConstant):
            return default_node.value
        return None
    
    def _extract_param_descriptions(self, func_node: ast.FunctionDef) -> Dict[str, str]:
        """
        Extract parameter descriptions from Google-style docstring.
        
        Args:
            func_node: Function definition node
        
        Returns:
            Dictionary mapping parameter names to descriptions
        """
        docstring = ast.get_docstring(func_node)
        if not docstring:
            return {}
        
        descriptions: Dict[str, str] = {}
        
        # Find Args: section
        args_match = re.search(r"Args:\s*\n(.*?)(?:\n\s*\n|\n[A-Z]|\Z)", docstring, re.DOTALL)
        if not args_match:
            return {}
        
        args_text = args_match.group(1)
        
        # Parse parameter descriptions
        param_pattern = re.compile(r"^\s*(\w+):\s*(.+?)(?=^\s*\w+:|$)", re.MULTILINE | re.DOTALL)
        for match in param_pattern.finditer(args_text):
            param_name = match.group(1)
            description = match.group(2).strip()
            # Clean up multi-line descriptions
            description = " ".join(description.split())
            descriptions[param_name] = description
        
        return descriptions

# AC_COMPLETE: AC-MEGA-B-S2-001 ✅ MCPToolScanner implemented
