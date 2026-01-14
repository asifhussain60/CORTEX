"""
AC-CRAWLER-002: Language-Specific AST Analyzers
Base analyzer class and language detection
"""
import ast
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Dict, Set, Any, Optional
import logging

logger = logging.getLogger(__name__)


@dataclass
class Symbol:
    """Code symbol extracted from analysis"""
    name: str
    type: str  # class, function, import, variable
    line: int
    column: int
    docstring: Optional[str] = None
    parameters: List[str] = field(default_factory=list)
    returns: Optional[str] = None
    complexity: int = 1


@dataclass
class AnalysisResult:
    """Result of code analysis"""
    file_path: str
    language: str
    symbols: List[Symbol] = field(default_factory=list)
    imports: List[str] = field(default_factory=list)
    exports: List[str] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)
    metrics: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)


class BaseAnalyzer(ABC):
    """Base class for language-specific analyzers"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.content = self._read_file()

    def _read_file(self) -> str:
        """Read file content"""
        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            logger.error(f"Failed to read {self.file_path}: {e}")
            return ""

    @abstractmethod
    def analyze(self) -> AnalysisResult:
        """Analyze file and return result"""
        pass


class PythonAnalyzer(BaseAnalyzer):
    """Python AST analyzer - AC-CRAWLER-002"""

    def analyze(self) -> AnalysisResult:
        """Analyze Python file"""
        result = AnalysisResult(
            file_path=self.file_path, language="python"
        )

        if not self.content:
            return result

        try:
            tree = ast.parse(self.content)
        except SyntaxError as e:
            result.errors.append(f"Syntax error: {e}")
            return result

        # Extract symbols
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                result.symbols.append(
                    Symbol(
                        name=node.name,
                        type="class",
                        line=node.lineno,
                        column=node.col_offset,
                        docstring=ast.get_docstring(node),
                    )
                )
            elif isinstance(node, ast.FunctionDef):
                args = [
                    arg.arg for arg in node.args.args
                ]
                result.symbols.append(
                    Symbol(
                        name=node.name,
                        type="function",
                        line=node.lineno,
                        column=node.col_offset,
                        docstring=ast.get_docstring(node),
                        parameters=args,
                    )
                )
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    result.imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    result.imports.append(node.module)
                for alias in node.names:
                    result.exports.append(alias.name)

        # Analyze complexity (simplified)
        result.metrics["lines"] = len(self.content.split("\n"))
        result.metrics["functions"] = len(
            [s for s in result.symbols if s.type == "function"]
        )
        result.metrics["classes"] = len(
            [s for s in result.symbols if s.type == "class"]
        )

        return result


class JavaScriptAnalyzer(BaseAnalyzer):
    """JavaScript/TypeScript analyzer"""

    def analyze(self) -> AnalysisResult:
        """Analyze JavaScript/TypeScript file (regex-based)"""
        result = AnalysisResult(
            file_path=self.file_path, language="javascript"
        )

        # Simple pattern matching for JS/TS
        import re

        # Extract classes
        class_pattern = r"class\s+(\w+)"
        for match in re.finditer(class_pattern, self.content):
            result.symbols.append(
                Symbol(
                    name=match.group(1),
                    type="class",
                    line=self.content[:match.start()].count("\n") + 1,
                    column=0,
                )
            )

        # Extract functions
        func_pattern = r"(?:function|const|let|var)\s+(\w+)\s*(?:=|:)"
        for match in re.finditer(func_pattern, self.content):
            result.symbols.append(
                Symbol(
                    name=match.group(1),
                    type="function",
                    line=self.content[:match.start()].count("\n") + 1,
                    column=0,
                )
            )

        # Extract imports
        import_pattern = r"import\s+.*?from\s+['\"]([^'\"]+)['\"]"
        for match in re.finditer(import_pattern, self.content):
            result.imports.append(match.group(1))

        result.metrics["lines"] = len(self.content.split("\n"))

        return result


class CSharpAnalyzer(BaseAnalyzer):
    """C# analyzer (regex-based)"""

    def analyze(self) -> AnalysisResult:
        """Analyze C# file"""
        result = AnalysisResult(
            file_path=self.file_path, language="csharp"
        )

        import re

        # Extract classes
        class_pattern = r"(public\s+)?class\s+(\w+)"
        for match in re.finditer(class_pattern, self.content):
            result.symbols.append(
                Symbol(
                    name=match.group(2),
                    type="class",
                    line=self.content[:match.start()].count("\n") + 1,
                    column=0,
                )
            )

        # Extract methods
        method_pattern = (
            r"(public|private|protected)?\s+\w+\s+(\w+)\s*\("
        )
        for match in re.finditer(method_pattern, self.content):
            result.symbols.append(
                Symbol(
                    name=match.group(2),
                    type="function",
                    line=self.content[:match.start()].count("\n") + 1,
                    column=0,
                )
            )

        # Extract using statements
        using_pattern = r"using\s+([^;]+);"
        for match in re.finditer(using_pattern, self.content):
            result.imports.append(match.group(1).strip())

        result.metrics["lines"] = len(self.content.split("\n"))

        return result


class GenericAnalyzer(BaseAnalyzer):
    """Fallback generic analyzer for unsupported languages"""

    def analyze(self) -> AnalysisResult:
        """Analyze using generic patterns"""
        result = AnalysisResult(
            file_path=self.file_path, language="generic"
        )

        import re

        # Generic patterns
        func_pattern = r"(?:def|function|func|fn|sub)\s+(\w+)\s*\("
        for match in re.finditer(func_pattern, self.content):
            result.symbols.append(
                Symbol(
                    name=match.group(1),
                    type="function",
                    line=self.content[:match.start()].count("\n") + 1,
                    column=0,
                )
            )

        result.metrics["lines"] = len(self.content.split("\n"))

        return result


class AnalyzerFactory:
    """Factory for creating appropriate analyzer"""

    ANALYZERS = {
        ".py": PythonAnalyzer,
        ".js": JavaScriptAnalyzer,
        ".ts": JavaScriptAnalyzer,
        ".tsx": JavaScriptAnalyzer,
        ".jsx": JavaScriptAnalyzer,
        ".cs": CSharpAnalyzer,
    }

    @classmethod
    def get_analyzer(cls, file_path: str) -> BaseAnalyzer:
        """Get appropriate analyzer for file"""
        ext = Path(file_path).suffix.lower()
        analyzer_class = cls.ANALYZERS.get(ext, GenericAnalyzer)
        return analyzer_class(file_path)
