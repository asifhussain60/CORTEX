"""Python structure analyzer for LENS compatibility.

Re-homed from ast_analyzer as part of M4 LENS streamlining.
Authority: SWEEP-M4-LENS-STREAMLINE
"""

import ast
import logging
import symtable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


@dataclass
class AstFunctionInfo:
    """Information about a function definition."""

    name: str
    line_number: int
    parameters: List[str] = field(default_factory=list)
    return_type: str = ""
    docstring: str = ""
    decorators: List[str] = field(default_factory=list)
    is_async: bool = False


@dataclass
class AstClassInfo:
    """Information about a class definition."""

    name: str
    line_number: int
    bases: List[str] = field(default_factory=list)
    methods: List[str] = field(default_factory=list)
    docstring: str = ""
    decorators: List[str] = field(default_factory=list)


@dataclass
class ImportInfo:
    """Information about an import statement."""

    module: str
    names: List[str]
    alias: str = ""
    line_number: int = 0


@dataclass
class ASTAnalysisResult:
    """Result of Python structure analysis."""

    success: bool
    functions: List[AstFunctionInfo] = field(default_factory=list)
    classes: List[AstClassInfo] = field(default_factory=list)
    imports: List[ImportInfo] = field(default_factory=list)
    error: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class ASTAnalyzer:
    """Analyzes Python code using AST parsing."""

    def analyze_code(self, code: str) -> ASTAnalysisResult:
        """Analyze Python code from a string."""
        try:
            tree = ast.parse(code)

            functions: List[AstFunctionInfo] = []
            classes: List[AstClassInfo] = []
            imports: List[ImportInfo] = []

            for node in ast.walk(tree):
                if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    functions.append(self._extract_function_info(node))
                elif isinstance(node, ast.ClassDef):
                    classes.append(self._extract_class_info(node))
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        imports.append(
                            ImportInfo(
                                module=alias.name,
                                names=[alias.name],
                                alias=alias.asname or "",
                                line_number=node.lineno,
                            )
                        )
                elif isinstance(node, ast.ImportFrom):
                    names = [alias.name for alias in node.names]
                    first_alias = node.names[0].asname if node.names and node.names[0].asname else ""
                    imports.append(
                        ImportInfo(
                            module=node.module or "",
                            names=names,
                            alias=first_alias,
                            line_number=node.lineno,
                        )
                    )

            scope_analysis: Dict[str, Any] = {}
            try:
                symbols = symtable.symtable(code, "<string>", "exec")
                scope_analysis = self._extract_scope_analysis(symbols)
            except Exception as exc:
                logger.debug(f"Symtable scope analysis failed: {exc}")

            return ASTAnalysisResult(
                success=True,
                functions=functions,
                classes=classes,
                imports=imports,
                metadata={
                    "line_count": len(code.splitlines()),
                    "function_count": len(functions),
                    "class_count": len(classes),
                    "import_count": len(imports),
                    "scope_analysis": scope_analysis,
                },
            )
        except SyntaxError as exc:
            return ASTAnalysisResult(success=False, error=f"Syntax error: {str(exc)}")
        except Exception as exc:
            return ASTAnalysisResult(success=False, error=f"Analysis error: {str(exc)}")

    def analyze_file(self, file_path: Path) -> ASTAnalysisResult:
        """Analyze Python code from a file."""
        try:
            if not file_path.exists():
                return ASTAnalysisResult(success=False, error=f"File not found: {file_path}")

            result = self.analyze_code(file_path.read_text(encoding="utf-8"))
            if result.success:
                result.metadata["file_path"] = str(file_path)
            return result
        except Exception as exc:
            return ASTAnalysisResult(success=False, error=f"Failed to read file: {str(exc)}")

    def _extract_function_info(self, node: ast.FunctionDef) -> AstFunctionInfo:
        """Extract information from a function definition node."""
        parameters = [arg.arg for arg in node.args.args]
        return_type = self._get_type_annotation(node.returns) if node.returns else ""
        docstring = ast.get_docstring(node) or ""
        decorators: List[str] = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(decorator.attr)

        return AstFunctionInfo(
            name=node.name,
            line_number=node.lineno,
            parameters=parameters,
            return_type=return_type,
            docstring=docstring,
            decorators=decorators,
            is_async=isinstance(node, ast.AsyncFunctionDef),
        )

    def _extract_class_info(self, node: ast.ClassDef) -> AstClassInfo:
        """Extract information from a class definition node."""
        bases: List[str] = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)

        methods = [
            item.name
            for item in node.body
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        docstring = ast.get_docstring(node) or ""
        decorators: List[str] = []
        for decorator in node.decorator_list:
            if isinstance(decorator, ast.Name):
                decorators.append(decorator.id)
            elif isinstance(decorator, ast.Attribute):
                decorators.append(decorator.attr)

        return AstClassInfo(
            name=node.name,
            line_number=node.lineno,
            bases=bases,
            methods=methods,
            docstring=docstring,
            decorators=decorators,
        )

    def _get_type_annotation(self, node: ast.AST) -> str:
        """Extract type annotation as string."""
        if isinstance(node, ast.Name):
            return node.id
        if isinstance(node, ast.Constant):
            return str(node.value)
        if isinstance(node, ast.Subscript) and isinstance(node.value, ast.Name):
            return node.value.id
        return ""

    def _extract_scope_analysis(self, symbols: symtable.SymbolTable) -> Dict[str, Any]:
        """Extract scope analysis from symtable."""
        analysis: Dict[str, Any] = {
            "scopes": [],
            "symbols_by_type": {
                "local": [],
                "global": [],
                "imported": [],
                "free": [],
                "cell": [],
            },
        }

        try:
            for symbol in symbols.get_symbols():
                sym_name = symbol.get_name()
                if symbol.is_imported():
                    analysis["symbols_by_type"]["imported"].append(sym_name)
                elif symbol.is_global():
                    analysis["symbols_by_type"]["global"].append(sym_name)
                elif symbol.is_free():
                    analysis["symbols_by_type"]["free"].append(sym_name)
                else:
                    analysis["symbols_by_type"]["local"].append(sym_name)

            for child in symbols.get_children():
                analysis["scopes"].append(
                    {
                        "type": child.get_type(),
                        "name": child.get_name(),
                        "symbols": len(child.get_symbols()),
                        "is_nested": child.is_nested(),
                    }
                )
        except Exception as exc:
            logger.debug(f"Error extracting scope analysis: {exc}")

        return analysis


FunctionInfo = AstFunctionInfo
ClassInfo = AstClassInfo
