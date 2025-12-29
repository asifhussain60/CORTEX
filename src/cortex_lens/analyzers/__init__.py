"""
AST and pattern analyzers for multiple languages.

Built-in analyzers:
- PythonAnalyzer: Native Python ast module
- CSharpAnalyzer: Regex-based C# parsing
- JavaScriptAnalyzer: Regex-based JavaScript/TypeScript parsing
- SQLAnalyzer: SQL schema and query analysis

Registry:
- AnalyzerRegistry: Plugin system for custom analyzers
"""

from .base import BaseAnalyzer
from .registry import AnalyzerRegistry

# Lazy imports for analyzers to avoid loading dependencies
def __getattr__(name):
    """Lazy import analyzers."""
    if name == 'PythonAnalyzer':
        from .python_analyzer import PythonAnalyzer
        return PythonAnalyzer
    elif name == 'CSharpAnalyzer':
        from .csharp_analyzer import CSharpAnalyzer
        return CSharpAnalyzer
    elif name == 'JavaScriptAnalyzer':
        from .javascript_analyzer import JavaScriptAnalyzer
        return JavaScriptAnalyzer
    elif name == 'SQLAnalyzer':
        from .sql_analyzer import SQLAnalyzer
        return SQLAnalyzer
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")

__all__ = [
    'BaseAnalyzer',
    'AnalyzerRegistry',
    'PythonAnalyzer',
    'CSharpAnalyzer',
    'JavaScriptAnalyzer',
    'SQLAnalyzer',
]
