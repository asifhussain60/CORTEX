"""
Intelligence Module

Multi-language code analysis and refactoring intelligence.
Provides unified interface for AST parsing and code smell detection
across Python, JavaScript, TypeScript, and C#.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from .multi_language_refactoring import (
    MultiLanguageRefactoringOrchestrator,
    get_refactoring_orchestrator
)
from .parsers import ParserRegistry, Language, LanguageDetector
from .analyzers import BaseAnalyzer, CodeSmell, SmellType

__all__ = [
    'MultiLanguageRefactoringOrchestrator',
    'get_refactoring_orchestrator',
    'ParserRegistry',
    'Language',
    'LanguageDetector',
    'BaseAnalyzer',
    'CodeSmell',
    'SmellType',
]
