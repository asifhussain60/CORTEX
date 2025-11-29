"""
Multi-Language Parser Registry

Provides unified interface for parsing code across multiple programming languages.
Supports Python, JavaScript, TypeScript, and C#.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from .parser_registry import ParserRegistry, Language
from .language_detector import LanguageDetector

__all__ = ['ParserRegistry', 'Language', 'LanguageDetector']
