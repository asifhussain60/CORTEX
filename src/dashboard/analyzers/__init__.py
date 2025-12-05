"""
Language-specific analyzers for universal dashboard data collection.
"""

from .language_analyzer_base import LanguageAnalyzer, AnalysisResult
from .csharp_analyzer import CSharpAnalyzer
from .typescript_analyzer import TypeScriptAnalyzer
from .coldfusion_analyzer import ColdFusionAnalyzer
from .sql_analyzer import SQLAnalyzer
from .python_analyzer import PythonAnalyzer
from .language_parser_factory import (
    LanguageParserFactory,
    get_factory,
    analyze_file,
    analyze_files,
    supports_file,
    get_supported_extensions,
    detect_language
)

__all__ = [
    'LanguageAnalyzer',
    'AnalysisResult',
    'CSharpAnalyzer',
    'TypeScriptAnalyzer',
    'ColdFusionAnalyzer',
    'SQLAnalyzer',
    'PythonAnalyzer',
    'LanguageParserFactory',
    'get_factory',
    'analyze_file',
    'analyze_files',
    'supports_file',
    'get_supported_extensions',
    'detect_language'
]
