"""
Polyglot Analyzer - Multi-Language AST Analysis.

Routes files to appropriate language adapters based on file extension.
Converts language-specific AST results to unified format for LENSOrchestrator.

Supports:
- Python (.py) - via ASTAnalyzer
- C# (.cs, .csx) - via CSharpAdapter
- Java (.java) - TODO Phase 2
- TypeScript (.ts, .tsx) - TODO Phase 2
- JavaScript (.js, .jsx) - TODO Phase 2

Authority: ENH-017 Phase 2 (Multi-Language AST Parsing)
"""

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from cortex.lens.adapters.csharp_adapter import CSharpAdapter
from cortex.lens.adapters.java_adapter import JavaAdapter
from cortex.lens.adapters.javascript_adapter import JavaScriptAdapter
from cortex.lens.adapters.typescript_adapter import TypeScriptAdapter
from cortex.lens.analyzers.ast_analyzer import (
    ASTAnalysisResult,
    ASTAnalyzer,
    ClassInfo,
    FunctionInfo,
)
from cortex.lens.models.polyglot_ast_result import LanguageType, PolyglotASTResult

logger = logging.getLogger(__name__)


@dataclass
class PolyglotAnalysisResult:
    """
    Unified result format for multi-language AST analysis.

    Compatible with LENSOrchestrator's expected format.

    Attributes:
        success: Whether analysis succeeded
        language: Detected language
        functions: List of functions found (unified format)
        classes: List of classes found (unified format)
        imports: List of imports found
        error: Error message if analysis failed
        metadata: Additional metadata
    """
    success: bool
    language: str = "unknown"
    functions: List[Dict[str, Any]] = field(default_factory=list)
    classes: List[Dict[str, Any]] = field(default_factory=list)
    imports: List[Dict[str, Any]] = field(default_factory=list)
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class PolyglotAnalyzer:
    """
    Multi-language AST analyzer that routes to appropriate language adapter.

    Detects language from file extension and delegates to:
    - ASTAnalyzer for Python files
    - CSharpAdapter for C# files
    - More adapters in future phases

    Converts language-specific results to unified format compatible with
    LENSOrchestrator's existing interface.

    Example:
        ```python
        analyzer = PolyglotAnalyzer()

        # Analyze Python file
        py_result = analyzer.analyze_file(Path("module.py"))
        print(f"Functions: {len(py_result.functions)}")

        # Analyze C# file
        cs_result = analyzer.analyze_file(Path("UserService.cs"))
        print(f"Classes: {len(cs_result.classes)}")
        ```
    """

    def __init__(self):
        """Initialize polyglot analyzer with all language adapters."""
        self.python_analyzer = ASTAnalyzer()

        # Initialize language adapters with graceful degradation (Phase 65)
        try:
            self.csharp_adapter = CSharpAdapter()
        except Exception as e:
            logger.warning(f"CSharpAdapter unavailable: {e}")
            self.csharp_adapter = None

        try:
            self.java_adapter = JavaAdapter()
        except Exception as e:
            logger.warning(f"JavaAdapter unavailable: {e}")
            self.java_adapter = None

        try:
            self.typescript_adapter = TypeScriptAdapter()
        except Exception as e:
            logger.warning(f"TypeScriptAdapter unavailable: {e}")
            self.typescript_adapter = None

        try:
            self.javascript_adapter = JavaScriptAdapter()
        except Exception as e:
            logger.warning(f"JavaScriptAdapter unavailable: {e}")
            self.javascript_adapter = None

        # Language detection map
        self.language_map = {
            ".py": "python",
            ".cs": "csharp",
            ".csx": "csharp",
            ".java": "java",
            ".ts": "typescript",
            ".tsx": "typescript",
            ".js": "javascript",
            ".jsx": "javascript",
        }

    def analyze_file(self, file_path: Path) -> PolyglotAnalysisResult:
        """
        Analyze file with appropriate language adapter.

        Detects language from extension, routes to adapter, and converts
        result to unified format compatible with LENSOrchestrator.

        Args:
            file_path: Path to source file

        Returns:
            PolyglotAnalysisResult with unified format
        """
        # Detect language
        language = self._detect_language(file_path)

        if language == "python":
            return self._analyze_python(file_path)
        elif language == "csharp":
            return self._analyze_csharp(file_path)
        elif language == "java":
            return self._analyze_java(file_path)
        elif language == "typescript":
            return self._analyze_typescript(file_path)
        elif language == "javascript":
            return self._analyze_javascript(file_path)
        else:
            return PolyglotAnalysisResult(
                success=False,
                language=language,
                error=f"Unsupported language: {file_path.suffix}",
                metadata={"file_path": str(file_path)},
            )

    def _detect_language(self, file_path: Path) -> str:
        """
        Detect programming language from file extension.

        Args:
            file_path: Path to file

        Returns:
            Language identifier (python, csharp, etc.) or "unknown"
        """
        suffix = file_path.suffix.lower()
        return self.language_map.get(suffix, "unknown")

    def _analyze_python(self, file_path: Path) -> PolyglotAnalysisResult:
        """
        Analyze Python file using ASTAnalyzer.

        Converts ASTAnalysisResult to PolyglotAnalysisResult format.

        Args:
            file_path: Path to Python file

        Returns:
            PolyglotAnalysisResult
        """
        result = self.python_analyzer.analyze_file(file_path)

        # Convert to unified format
        functions = [
            {
                "name": func.name,
                "line_number": func.line_number,
                "parameters": func.parameters,
                "is_async": func.is_async,
                "return_type": func.return_type,
                "docstring": func.docstring,
            }
            for func in result.functions
        ]

        classes = [
            {
                "name": cls.name,
                "line_number": cls.line_number,
                "methods": cls.methods,
                "bases": cls.bases,
                "docstring": cls.docstring,
            }
            for cls in result.classes
        ]

        imports = [
            {
                "module": imp.module,
                "names": imp.names,
                "alias": imp.alias,
                "line_number": imp.line_number,
            }
            for imp in result.imports
        ]

        return PolyglotAnalysisResult(
            success=result.success,
            language="Python",
            functions=functions,
            classes=classes,
            imports=imports,
            error=result.error,
            metadata={
                **result.metadata,
                "analyzer": "ASTAnalyzer",
            },
        )

    def _analyze_csharp(self, file_path: Path) -> PolyglotAnalysisResult:
        """
        Analyze C# file using CSharpAdapter.

        Converts PolyglotASTResult to PolyglotAnalysisResult format.

        Args:
            file_path: Path to C# file

        Returns:
            PolyglotAnalysisResult
        """
        try:
            # Graceful degradation if adapter not available (Phase 65)
            if self.csharp_adapter is None:
                return PolyglotAnalysisResult(
                    success=False,
                    language="csharp",
                    functions=[],
                    classes=[],
                    imports=[],
                    error="CSharpAdapter not available (tree-sitter-c-sharp not installed)"
                )

            result = self.csharp_adapter.parse_file(file_path)

            # Convert to unified format
            functions = [
                {
                    "name": func.name,
                    "line_number": func.line_start,
                    "parameters": func.parameters,
                    "is_async": func.is_async,
                    "return_type": func.return_type or "",
                    "docstring": func.docstring or "",
                }
                for func in result.functions
            ]

            classes = [
                {
                    "name": cls.name,
                    "line_number": cls.line_start,
                    "methods": [m.name for m in cls.methods],  # Convert FunctionInfo to names
                    "bases": cls.base_classes,
                    "docstring": cls.docstring or "",
                    "namespace": cls.namespace or "",
                    "is_interface": cls.is_interface,
                    "is_abstract": cls.is_abstract,
                    "properties": cls.properties,  # List of dicts with {"name": ..., "type": ...}
                }
                for cls in result.classes
            ]

            imports = [
                {
                    "module": imp.module,
                    "names": imp.names,
                    "alias": imp.alias or "",
                    "line_number": imp.line,
                }
                for imp in result.imports
            ]

            return PolyglotAnalysisResult(
                success=True,
                language="C#",
                functions=functions,
                classes=classes,
                imports=imports,
                error="",
                metadata={
                    **result.metadata,
                    "analyzer": "CSharpAdapter",
                    "parse_errors": result.parse_errors,
                },
            )

        except Exception as e:
            return PolyglotAnalysisResult(
                success=False,
                language="C#",
                error=str(e),
                metadata={"file_path": str(file_path)},
            )

    def _analyze_java(self, file_path: Path) -> PolyglotAnalysisResult:
        """
        Analyze Java file using JavaAdapter.

        Converts PolyglotASTResult to PolyglotAnalysisResult format.

        Args:
            file_path: Path to Java file

        Returns:
            PolyglotAnalysisResult
        """
        try:
            # Graceful degradation if adapter not available (Phase 65)
            if self.java_adapter is None:
                return PolyglotAnalysisResult(
                    success=False,
                    language="java",
                    functions=[],
                    classes=[],
                    imports=[],
                    error="JavaAdapter not available (tree-sitter-java not installed)"
                )

            result = self.java_adapter.parse_file(file_path)

            # Convert to unified format
            functions = [
                {
                    "name": func.name,
                    "line_number": func.line_start,
                    "parameters": func.parameters,
                    "is_async": func.is_async,
                    "return_type": func.return_type or "",
                    "docstring": func.docstring or "",
                }
                for func in result.functions
            ]

            classes = [
                {
                    "name": cls.name,
                    "line_number": cls.line_start,
                    "methods": [m.name for m in cls.methods],
                    "bases": cls.base_classes,
                    "docstring": cls.docstring or "",
                    "namespace": cls.namespace or "",
                    "is_interface": cls.is_interface,
                    "is_abstract": cls.is_abstract,
                    "properties": cls.properties,
                }
                for cls in result.classes
            ]

            imports = [
                {
                    "module": imp.module,
                    "names": imp.names,
                    "alias": imp.alias or "",
                    "line_number": imp.line,
                }
                for imp in result.imports
            ]

            return PolyglotAnalysisResult(
                success=True,
                language="Java",
                functions=functions,
                classes=classes,
                imports=imports,
                error="",
                metadata={
                    **result.metadata,
                    "analyzer": "JavaAdapter",
                    "parse_errors": result.parse_errors,
                },
            )

        except Exception as e:
            return PolyglotAnalysisResult(
                success=False,
                language="Java",
                error=str(e),
                metadata={"file_path": str(file_path)},
            )

    def _analyze_typescript(self, file_path: Path) -> PolyglotAnalysisResult:
        """
        Analyze TypeScript file using TypeScriptAdapter.

        Converts PolyglotASTResult to PolyglotAnalysisResult format.

        Args:
            file_path: Path to TypeScript file

        Returns:
            PolyglotAnalysisResult
        """
        try:
            # Graceful degradation if adapter not available (Phase 65)
            if self.typescript_adapter is None:
                return PolyglotAnalysisResult(
                    success=False,
                    language="typescript",
                    functions=[],
                    classes=[],
                    imports=[],
                    error="TypeScriptAdapter not available (tree-sitter-typescript installed but init failed)"
                )

            result = self.typescript_adapter.parse_file(file_path)

            # Convert to unified format
            functions = [
                {
                    "name": func.name,
                    "line_number": func.line_start,
                    "parameters": func.parameters,
                    "is_async": func.is_async,
                    "return_type": func.return_type or "",
                    "docstring": func.docstring or "",
                }
                for func in result.functions
            ]

            classes = [
                {
                    "name": cls.name,
                    "line_number": cls.line_start,
                    "methods": [m.name for m in cls.methods],
                    "bases": cls.base_classes,
                    "docstring": cls.docstring or "",
                    "namespace": cls.namespace or "",
                    "is_interface": cls.is_interface,
                    "is_abstract": cls.is_abstract,
                    "properties": cls.properties,
                }
                for cls in result.classes
            ]

            imports = [
                {
                    "module": imp.module,
                    "names": imp.names,
                    "alias": imp.alias or "",
                    "line_number": imp.line,
                }
                for imp in result.imports
            ]

            return PolyglotAnalysisResult(
                success=True,
                language="TypeScript",
                functions=functions,
                classes=classes,
                imports=imports,
                error="",
                metadata={
                    **result.metadata,
                    "analyzer": "TypeScriptAdapter",
                    "parse_errors": result.parse_errors,
                },
            )

        except Exception as e:
            return PolyglotAnalysisResult(
                success=False,
                language="TypeScript",
                error=str(e),
                metadata={"file_path": str(file_path)},
            )

    def _analyze_javascript(self, file_path: Path) -> PolyglotAnalysisResult:
        """
        Analyze JavaScript file using JavaScriptAdapter.

        Converts PolyglotASTResult to PolyglotAnalysisResult format.

        Args:
            file_path: Path to JavaScript file

        Returns:
            PolyglotAnalysisResult
        """
        try:
            # Graceful degradation if adapter not available (Phase 65)
            if self.javascript_adapter is None:
                return PolyglotAnalysisResult(
                    success=False,
                    language="javascript",
                    functions=[],
                    classes=[],
                    imports=[],
                    error="JavaScriptAdapter not available (tree-sitter-javascript installed but init failed)"
                )

            result = self.javascript_adapter.parse_file(file_path)

            # Convert to unified format
            functions = [
                {
                    "name": func.name,
                    "line_number": func.line_start,
                    "parameters": func.parameters,
                    "is_async": func.is_async,
                    "return_type": func.return_type or "",
                    "docstring": func.docstring or "",
                }
                for func in result.functions
            ]

            classes = [
                {
                    "name": cls.name,
                    "line_number": cls.line_start,
                    "methods": [m.name for m in cls.methods],
                    "bases": cls.base_classes,
                    "docstring": cls.docstring or "",
                    "namespace": cls.namespace or "",
                    "is_interface": cls.is_interface,
                    "is_abstract": cls.is_abstract,
                    "properties": cls.properties,
                }
                for cls in result.classes
            ]

            imports = [
                {
                    "module": imp.module,
                    "names": imp.names,
                    "alias": imp.alias or "",
                    "line_number": imp.line,
                }
                for imp in result.imports
            ]

            return PolyglotAnalysisResult(
                success=True,
                language="JavaScript",
                functions=functions,
                classes=classes,
                imports=imports,
                error="",
                metadata={
                    **result.metadata,
                    "analyzer": "JavaScriptAdapter",
                    "parse_errors": result.parse_errors,
                },
            )

        except Exception as e:
            return PolyglotAnalysisResult(
                success=False,
                language="JavaScript",
                error=str(e),
                metadata={"file_path": str(file_path)},
            )

    def get_supported_extensions(self) -> List[str]:
        """
        Get list of supported file extensions.

        Returns:
            List of extensions (e.g., [".py", ".cs", ".java"])
        """
        return list(self.language_map.keys())

    def is_supported(self, file_path: Path) -> bool:
        """
        Check if file is supported for analysis.

        Args:
            file_path: Path to file

        Returns:
            True if file extension is supported
        """
        return file_path.suffix.lower() in self.language_map
