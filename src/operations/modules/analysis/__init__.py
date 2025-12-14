"""
Analysis module for CORTEX Planning System 3.0.

Provides AST-powered code analysis capabilities including
semantic duplicate detection, architecture debt analysis,
and code smell identification.
"""

from .ast_engine import ASTEngine
from .deduplication_analyzer import DeduplicationAnalyzer, DuplicateGroup
from .architecture_debt_analyzer import ArchitectureDebtAnalyzer, ArchitectureViolation
from .code_smell_analyzer import CodeSmellAnalyzer, CodeSmell

__all__ = [
    'ASTEngine',
    'DeduplicationAnalyzer',
    'DuplicateGroup',
    'ArchitectureDebtAnalyzer',
    'ArchitectureViolation',
    'CodeSmellAnalyzer',
    'CodeSmell',
]
