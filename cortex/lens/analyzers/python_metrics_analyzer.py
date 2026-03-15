"""Python metrics analyzer for onboarding golden workflows.

Re-homed from python_analyzer as part of M4 LENS streamlining.
Authority: SWEEP-M4-LENS-STREAMLINE
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
    """Python code analyzer using AST metrics."""

    def analyze_file(self, file_path: Path) -> AnalysisResult:
        """Analyze Python file metrics."""
        code = file_path.read_text()
        tree = ast.parse(code)

        functions = sum(1 for node in ast.walk(tree) if isinstance(node, ast.FunctionDef))
        classes = sum(1 for node in ast.walk(tree) if isinstance(node, ast.ClassDef))
        lines = len(code.splitlines())

        return AnalysisResult(
            functions_found=functions,
            classes_found=classes,
            lines_of_code=lines,
        )
