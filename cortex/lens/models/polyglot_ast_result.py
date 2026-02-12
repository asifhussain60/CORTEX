"""
Polyglot AST Result Models

Unified data structures for representing code analysis across multiple languages:
- Python (ast module)
- C# (tree-sitter-c-sharp)
- Java (tree-sitter-java)
- TypeScript (tree-sitter-typescript)
- JavaScript (tree-sitter-javascript)

These models provide a common interface for LENS analyzers to work with any language.

Author: Asif Hussain
Created: 2026-02-04
Authority: LENS-MULTI-LANGUAGE-ENHANCEMENT.yaml Phase 0
"""

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class LanguageType(Enum):
    """Supported programming languages for AST analysis."""

    PYTHON = "python"
    CSHARP = "csharp"
    JAVA = "java"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"

    @classmethod
    def from_extension(cls, extension: str) -> "LanguageType":
        """
        Derive language type from file extension.

        Args:
            extension: File extension (e.g., ".py", ".cs")

        Returns:
            LanguageType enum value

        Raises:
            ValueError: If extension is not supported
        """
        extension_map = {
            ".py": cls.PYTHON,
            ".cs": cls.CSHARP,
            ".java": cls.JAVA,
            ".ts": cls.TYPESCRIPT,
            ".tsx": cls.TYPESCRIPT,
            ".js": cls.JAVASCRIPT,
            ".jsx": cls.JAVASCRIPT,
        }

        if extension not in extension_map:
            raise ValueError(f"Unsupported file extension: {extension}")

        return extension_map[extension]


@dataclass
class ImportInfo:
    """
    Represents an import/using/include statement.

    Attributes:
        module: Module/package name (e.g., "os.path", "System.Collections")
        names: Specific names imported (e.g., ["join", "exists"])
        line: Line number where import appears
        alias: Optional alias (e.g., "import pandas as pd")
    """

    module: str
    names: List[str]
    line: int
    alias: Optional[str] = None


@dataclass
class FunctionInfo:
    """
    Represents a function/method extracted from AST.

    Attributes:
        name: Function name
        line_start: Starting line number
        line_end: Ending line number
        parameters: List of parameter names
        is_async: Whether function is async/await
        docstring: Documentation string (if present)
        return_type: Return type annotation (if present)
        decorators: List of decorators/attributes (e.g., @property, [HttpGet])
    """

    name: str
    line_start: int
    line_end: int
    parameters: List[str]
    is_async: bool = False
    docstring: str = ""
    return_type: Optional[str] = None
    decorators: List[str] = field(default_factory=list)


@dataclass
class ClassInfo:
    """
    Represents a class/interface/struct extracted from AST.

    Attributes:
        name: Class name
        line_start: Starting line number
        line_end: Ending line number
        methods: List of method names
        base_classes: List of parent classes/interfaces
        docstring: Documentation string (if present)
        namespace: Namespace/package (C#, Java)
        is_interface: Whether this is an interface (TypeScript, Java)
        is_abstract: Whether class is abstract
        properties: List of property names (C#, TypeScript)
        attributes: List of attributes/annotations
    """

    name: str
    line_start: int
    line_end: int
    methods: List[str]
    base_classes: List[str]
    docstring: str = ""
    namespace: Optional[str] = None
    is_interface: bool = False
    is_abstract: bool = False
    properties: List[str] = field(default_factory=list)
    attributes: List[str] = field(default_factory=list)


@dataclass
class PolyglotASTResult:
    """
    Unified AST analysis result that works across all supported languages.

    This is the primary data structure returned by language adapters.
    It provides a consistent interface for LENS orchestrators regardless
    of the underlying language being analyzed.

    Attributes:
        file_path: Path to the analyzed file
        language: Detected language type
        classes: List of classes/interfaces/structs found
        functions: List of standalone functions/methods
        imports: List of import/using statements
        raw_ast: Optional raw AST data (language-specific)
        parse_errors: List of errors encountered during parsing
        metadata: Additional language-specific metadata

    Example:
        >>> result = PolyglotASTResult(
        ...     file_path=Path("src/services/order.py"),
        ...     language=LanguageType.PYTHON,
        ...     classes=[ClassInfo(name="OrderService", ...)],
        ...     functions=[],
        ...     imports=[ImportInfo(module="typing", ...)],
        ... )
    """

    file_path: Path
    language: LanguageType
    classes: List[ClassInfo]
    functions: List[FunctionInfo]
    imports: List[ImportInfo]
    raw_ast: Optional[Any] = None
    parse_errors: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    @property
    def total_classes(self) -> int:
        """Total number of classes found."""
        return len(self.classes)

    @property
    def total_functions(self) -> int:
        """Total number of standalone functions found."""
        return len(self.functions)

    @property
    def total_methods(self) -> int:
        """Total number of methods across all classes."""
        return sum(len(cls.methods) for cls in self.classes)

    @property
    def has_errors(self) -> bool:
        """Whether any parse errors were encountered."""
        return len(self.parse_errors) > 0

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert result to dictionary (for JSON serialization).

        Returns:
            Dictionary representation of the result
        """
        return {
            "file_path": str(self.file_path),
            "language": self.language.value,
            "classes": [
                {
                    "name": cls.name,
                    "line_start": cls.line_start,
                    "line_end": cls.line_end,
                    "methods": cls.methods,
                    "base_classes": cls.base_classes,
                    "namespace": cls.namespace,
                    "is_interface": cls.is_interface,
                }
                for cls in self.classes
            ],
            "functions": [
                {
                    "name": func.name,
                    "line_start": func.line_start,
                    "line_end": func.line_end,
                    "parameters": func.parameters,
                    "is_async": func.is_async,
                }
                for func in self.functions
            ],
            "imports": [
                {
                    "module": imp.module,
                    "names": imp.names,
                    "line": imp.line,
                }
                for imp in self.imports
            ],
            "total_classes": self.total_classes,
            "total_functions": self.total_functions,
            "total_methods": self.total_methods,
            "has_errors": self.has_errors,
            "parse_errors": self.parse_errors,
            "metadata": self.metadata,
        }
