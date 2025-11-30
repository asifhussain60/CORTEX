"""
Multi-Language Code Analyzers

Unified interface for AST analysis across multiple programming languages.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from .base_analyzer import BaseAnalyzer, CodeSmell, SmellType
from .python_analyzer import PythonAnalyzer
from .javascript_analyzer import JavaScriptAnalyzer
from .typescript_analyzer import TypeScriptAnalyzer
from .csharp_analyzer import CSharpAnalyzer

__all__ = [
    'BaseAnalyzer',
    'CodeSmell',
    'SmellType',
    'PythonAnalyzer',
    'JavaScriptAnalyzer',
    'TypeScriptAnalyzer',
    'CSharpAnalyzer',
]
