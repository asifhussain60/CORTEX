"""
Language Parser Factory for dashboard analyzers.
Provides centralized registration and retrieval of language-specific analyzers.
"""

from pathlib import Path
from typing import Dict, Optional, List, Type
from .language_analyzer_base import LanguageAnalyzer, AnalysisResult
from .csharp_analyzer import CSharpAnalyzer
from .typescript_analyzer import TypeScriptAnalyzer
from .coldfusion_analyzer import ColdFusionAnalyzer
from .sql_analyzer import SQLAnalyzer


class LanguageParserFactory:
    """
    Factory for creating and managing language-specific analyzers.
    
    Features:
    - Auto-registration of built-in analyzers
    - Extension support for custom analyzers
    - File extension to analyzer mapping
    - Batch analysis support
    """
    
    def __init__(self):
        """Initialize factory with built-in analyzers."""
        self._analyzers: Dict[str, LanguageAnalyzer] = {}
        self._extension_map: Dict[str, str] = {}
        
        # Register built-in analyzers
        self._register_builtin_analyzers()
    
    def _register_builtin_analyzers(self):
        """Register all built-in language analyzers."""
        # C# Analyzer
        csharp = CSharpAnalyzer()
        self.register_analyzer('csharp', csharp, ['.cs'])
        
        # TypeScript Analyzer
        typescript = TypeScriptAnalyzer()
        self.register_analyzer('typescript', typescript, ['.ts'])
        
        # ColdFusion Analyzer
        coldfusion = ColdFusionAnalyzer()
        self.register_analyzer('coldfusion', coldfusion, ['.cfm', '.cfc'])
        
        # SQL Analyzer
        sql = SQLAnalyzer()
        self.register_analyzer('sql', sql, ['.sql'])
        
        # Python Analyzer
        from src.dashboard.analyzers.python_analyzer import PythonAnalyzer
        python = PythonAnalyzer()
        self.register_analyzer('python', python, ['.py'])
    
    def register_analyzer(
        self,
        language: str,
        analyzer: LanguageAnalyzer,
        extensions: List[str]
    ):
        """
        Register a language analyzer.
        
        Args:
            language: Language identifier (e.g., 'csharp', 'typescript')
            analyzer: Analyzer instance
            extensions: List of file extensions (e.g., ['.cs', '.csx'])
        """
        self._analyzers[language.lower()] = analyzer
        
        # Map extensions to language
        for ext in extensions:
            ext_lower = ext.lower()
            if not ext_lower.startswith('.'):
                ext_lower = f'.{ext_lower}'
            self._extension_map[ext_lower] = language.lower()
    
    def get_analyzer(self, language: str) -> Optional[LanguageAnalyzer]:
        """
        Get analyzer by language name.
        
        Args:
            language: Language identifier
            
        Returns:
            Analyzer instance or None if not found
        """
        return self._analyzers.get(language.lower())
    
    def get_analyzer_for_file(self, file_path: Path) -> Optional[LanguageAnalyzer]:
        """
        Get appropriate analyzer for a file based on extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Analyzer instance or None if no analyzer supports this file
        """
        extension = file_path.suffix.lower()
        language = self._extension_map.get(extension)
        
        if language:
            return self._analyzers.get(language)
        
        return None
    
    def analyze_file(self, file_path: Path) -> Optional[AnalysisResult]:
        """
        Analyze a file using the appropriate analyzer.
        
        Args:
            file_path: Path to file
            
        Returns:
            AnalysisResult or None if no analyzer found
        """
        analyzer = self.get_analyzer_for_file(file_path)
        
        if analyzer:
            return analyzer.analyze(file_path)
        
        return None
    
    def analyze_files(self, file_paths: List[Path]) -> List[AnalysisResult]:
        """
        Analyze multiple files using appropriate analyzers.
        
        Args:
            file_paths: List of file paths
            
        Returns:
            List of AnalysisResults (skips unsupported files)
        """
        results = []
        
        for file_path in file_paths:
            result = self.analyze_file(file_path)
            if result:
                results.append(result)
        
        return results
    
    def supports_file(self, file_path: Path) -> bool:
        """
        Check if a file is supported by any registered analyzer.
        
        Args:
            file_path: Path to file
            
        Returns:
            True if file is supported
        """
        extension = file_path.suffix.lower()
        return extension in self._extension_map
    
    def get_supported_extensions(self) -> List[str]:
        """
        Get list of all supported file extensions.
        
        Returns:
            List of extensions (e.g., ['.cs', '.ts', '.cfm'])
        """
        return list(self._extension_map.keys())
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of all supported languages.
        
        Returns:
            List of language identifiers
        """
        return list(self._analyzers.keys())
    
    def detect_language(self, file_path: Path) -> Optional[str]:
        """
        Detect language for a file based on extension.
        
        Args:
            file_path: Path to file
            
        Returns:
            Language identifier or None
        """
        extension = file_path.suffix.lower()
        return self._extension_map.get(extension)


# Global factory instance
_factory_instance: Optional[LanguageParserFactory] = None


def get_factory() -> LanguageParserFactory:
    """
    Get the global LanguageParserFactory instance (singleton).
    
    Returns:
        LanguageParserFactory instance
    """
    global _factory_instance
    
    if _factory_instance is None:
        _factory_instance = LanguageParserFactory()
    
    return _factory_instance


def analyze_file(file_path: Path) -> Optional[AnalysisResult]:
    """
    Convenience function to analyze a file using the global factory.
    
    Args:
        file_path: Path to file
        
    Returns:
        AnalysisResult or None
    """
    factory = get_factory()
    return factory.analyze_file(file_path)


def analyze_files(file_paths: List[Path]) -> List[AnalysisResult]:
    """
    Convenience function to analyze multiple files using the global factory.
    
    Args:
        file_paths: List of file paths
        
    Returns:
        List of AnalysisResults
    """
    factory = get_factory()
    return factory.analyze_files(file_paths)


def supports_file(file_path: Path) -> bool:
    """
    Convenience function to check if a file is supported.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if supported
    """
    factory = get_factory()
    return factory.supports_file(file_path)


def get_supported_extensions() -> List[str]:
    """
    Convenience function to get supported extensions.
    
    Returns:
        List of extensions
    """
    factory = get_factory()
    return factory.get_supported_extensions()


def detect_language(file_path: Path) -> Optional[str]:
    """
    Convenience function to detect file language.
    
    Args:
        file_path: Path to file
        
    Returns:
        Language identifier or None
    """
    factory = get_factory()
    return factory.detect_language(file_path)
