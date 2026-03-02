"""
PythonAnalyzer — Python code analysis for golden tests.

Authority: Phase 29 S2 | Production Verification
"""
import ast
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AnalysisResult:
    """Result of Python code analysis."""
    functions_found: int
    classes_found: int
    lines_of_code: int


class PythonAnalyzer:
    """
    Python code analyzer using AST.

    Example:
        analyzer = PythonAnalyzer()
        result = analyzer.analyze_file(Path("app.py"))
    """

    def analyze_file(self, file_path: Path) -> AnalysisResult:
        """
        Analyze Python file.

        Args:
            file_path: Path to Python file

        Returns:
            AnalysisResult with metrics
        """
        code = file_path.read_text()
        tree = ast.parse(code)

        functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        lines = len(code.splitlines())

        return AnalysisResult(
            functions_found=functions,
            classes_found=classes,
            lines_of_code=lines
        )
