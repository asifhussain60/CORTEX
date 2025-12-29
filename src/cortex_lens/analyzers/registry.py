"""
Registry for language analyzers with plugin support.

The AnalyzerRegistry manages analyzer lifecycle and provides
dynamic loading capabilities.
"""

from typing import Dict, List, Optional, Type
from pathlib import Path
import logging

from .base import BaseAnalyzer

logger = logging.getLogger(__name__)


class AnalyzerRegistry:
    """
    Central registry for language analyzers.
    
    Provides plugin system for registering custom analyzers
    and selecting appropriate analyzer for file types.
    
    Example:
        >>> registry = AnalyzerRegistry()
        >>> registry.register('python', PythonAnalyzer())
        >>> analyzer = registry.get_analyzer(Path('app.py'))
    """
    
    def __init__(self):
        """Initialize empty registry."""
        self._analyzers: Dict[str, BaseAnalyzer] = {}
        self._extension_map: Dict[str, str] = {}
        logger.info("🎭 AnalyzerRegistry initialized")
    
    def register(self, language: str, analyzer: BaseAnalyzer) -> None:
        """
        Register an analyzer for a language.
        
        Args:
            language: Language identifier (e.g., 'python')
            analyzer: Analyzer instance implementing BaseAnalyzer protocol
            
        Raises:
            ValueError: If language already registered
        """
        if language in self._analyzers:
            raise ValueError(f"Analyzer for '{language}' already registered")
        
        self._analyzers[language] = analyzer
        
        # Build extension mapping
        for ext in analyzer.file_extensions:
            self._extension_map[ext.lower()] = language
        
        logger.info(f"📝 Registered analyzer: {language} ({len(analyzer.file_extensions)} extensions)")
    
    def get_analyzer(self, file_path: Path) -> Optional[BaseAnalyzer]:
        """
        Get analyzer for a file based on extension.
        
        Args:
            file_path: Path to source file
            
        Returns:
            Analyzer instance or None if no match
        """
        ext = file_path.suffix.lower()
        language = self._extension_map.get(ext)
        
        if language:
            return self._analyzers[language]
        
        logger.debug(f"No analyzer found for extension: {ext}")
        return None
    
    def get_by_language(self, language: str) -> Optional[BaseAnalyzer]:
        """
        Get analyzer by language name.
        
        Args:
            language: Language identifier
            
        Returns:
            Analyzer instance or None
        """
        return self._analyzers.get(language)
    
    def list_languages(self) -> List[str]:
        """
        List all registered languages.
        
        Returns:
            List of language identifiers
        """
        return list(self._analyzers.keys())
    
    def list_extensions(self) -> List[str]:
        """
        List all supported file extensions.
        
        Returns:
            List of file extensions (e.g., ['.py', '.cs'])
        """
        return list(self._extension_map.keys())
    
    def unregister(self, language: str) -> bool:
        """
        Unregister an analyzer.
        
        Args:
            language: Language identifier
            
        Returns:
            True if unregistered, False if not found
        """
        if language not in self._analyzers:
            return False
        
        analyzer = self._analyzers[language]
        
        # Remove extension mappings
        for ext in analyzer.file_extensions:
            self._extension_map.pop(ext.lower(), None)
        
        del self._analyzers[language]
        logger.info(f"🗑️ Unregistered analyzer: {language}")
        return True
    
    def clear(self) -> None:
        """Clear all registered analyzers."""
        count = len(self._analyzers)
        self._analyzers.clear()
        self._extension_map.clear()
        logger.info(f"🧹 Cleared {count} analyzers")


# Global singleton instance
_default_registry: Optional[AnalyzerRegistry] = None


def get_default_registry() -> AnalyzerRegistry:
    """
    Get the default global registry instance.
    
    Returns:
        Global AnalyzerRegistry singleton
    """
    global _default_registry
    if _default_registry is None:
        _default_registry = AnalyzerRegistry()
    return _default_registry
