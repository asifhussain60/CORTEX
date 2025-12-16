"""
Parser Registry

Centralized registry for multi-language code parsers.
Maps languages to appropriate parsing backends.

Supported Languages:
- Python: Native ast module (built-in)
- JavaScript: esprima (optional - install separately)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import ast
from typing import Any, Dict, Optional, Callable
from .language_detector import Language

try:
    import esprima
    ESPRIMA_AVAILABLE = True
except ImportError:
    ESPRIMA_AVAILABLE = False


class ParserRegistry:
    """Registry mapping languages to parsing functions"""
    
    def __init__(self):
        """Initialize parser registry"""
        self._parsers: Dict[Language, Callable] = {}
        self._initialize_parsers()
    
    def _initialize_parsers(self):
        """Register all available parsers"""
        # Python uses built-in ast module (always available)
        self._parsers[Language.PYTHON] = self._parse_python
        
        # JavaScript uses esprima (if installed)
        if ESPRIMA_AVAILABLE:
            self._parsers[Language.JAVASCRIPT] = self._parse_javascript
    
    def parse(self, code: str, language: Language) -> Optional[Any]:
        """
        Parse code using appropriate parser
        
        Args:
            code: Source code to parse
            language: Programming language
            
        Returns:
            Parsed AST or None if parsing fails
        """
        parser = self._parsers.get(language)
        if not parser:
            return None
        
        try:
            return parser(code)
        except Exception as e:
            print(f"Parser error for {language.value}: {e}")
            return None
    
    def is_available(self, language: Language) -> bool:
        """
        Check if parser is available for language
        
        Args:
            language: Programming language
            
        Returns:
            True if parser is available
        """
        return language in self._parsers
    
    def get_available_languages(self) -> list[Language]:
        """
        Get list of languages with available parsers
        
        Returns:
            List of Language enums
        """
        return list(self._parsers.keys())
    
    # Parser implementations
    
    def _parse_python(self, code: str) -> ast.AST:
        """Parse Python code using ast module"""
        return ast.parse(code)
    
    def _parse_javascript(self, code: str) -> Dict:
        """Parse JavaScript code using esprima"""
        return esprima.parseScript(code, {'loc': True, 'range': True})


# Singleton instance
_registry: Optional[ParserRegistry] = None


def get_parser_registry() -> ParserRegistry:
    """
    Get singleton parser registry instance
    
    Returns:
        ParserRegistry instance
    """
    global _registry
    if _registry is None:
        _registry = ParserRegistry()
    return _registry
