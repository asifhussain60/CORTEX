"""
Multi-Language Refactoring Orchestrator

Coordinates refactoring analysis across multiple programming languages.
Integrates with TDD Mastery workflow for performance-based refactoring.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

from pathlib import Path
from typing import List, Dict, Optional, Any
import yaml

from .parsers import ParserRegistry, LanguageDetector, Language
from .analyzers import (
    BaseAnalyzer, CodeSmell, PythonAnalyzer, 
    JavaScriptAnalyzer, TypeScriptAnalyzer, CSharpAnalyzer
)


class MultiLanguageRefactoringOrchestrator:
    """
    Orchestrates code smell detection and refactoring suggestions
    across multiple programming languages.
    """
    
    def __init__(self, rules_path: Optional[str] = None):
        """
        Initialize orchestrator
        
        Args:
            rules_path: Path to refactoring-rules.yaml (optional)
        """
        self.parser_registry = ParserRegistry()
        self.language_detector = LanguageDetector()
        
        # Initialize analyzers
        self.analyzers: Dict[Language, BaseAnalyzer] = {
            Language.PYTHON: PythonAnalyzer(),
            Language.JAVASCRIPT: JavaScriptAnalyzer(),
            Language.TYPESCRIPT: TypeScriptAnalyzer(),
            Language.CSHARP: CSharpAnalyzer(),
        }
        
        # Load refactoring rules
        self.rules = self._load_rules(rules_path)
    
    def _load_rules(self, rules_path: Optional[str] = None) -> dict:
        """Load refactoring rules from YAML"""
        if rules_path is None:
            # Default path
            cortex_root = Path(__file__).parent.parent.parent.parent
            rules_path = cortex_root / "cortex-brain" / "refactoring-rules.yaml"
        
        if Path(rules_path).exists():
            with open(rules_path, 'r') as f:
                return yaml.safe_load(f)
        
        return {}
    
    def analyze_file(self, file_path: str) -> Dict[str, Any]:
        """
        Analyze source file for code smells
        
        Args:
            file_path: Path to source file
            
        Returns:
            Analysis results dict with smells and metadata
        """
        # Detect language
        language = self.language_detector.detect_from_file(file_path)
        
        if language == Language.UNKNOWN:
            return {
                'success': False,
                'error': f"Unsupported file type: {file_path}",
                'language': None,
                'smells': []
            }
        
        # Check if parser available
        if not self.parser_registry.is_available(language):
            return {
                'success': False,
                'error': f"Parser not available for {language.value}",
                'language': language.value,
                'smells': []
            }
        
        # Read source code
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except Exception as e:
            return {
                'success': False,
                'error': f"Failed to read file: {e}",
                'language': language.value,
                'smells': []
            }
        
        # Parse code
        ast_tree = self.parser_registry.parse(code, language)
        if ast_tree is None:
            return {
                'success': False,
                'error': f"Failed to parse {language.value} code",
                'language': language.value,
                'smells': []
            }
        
        # Analyze for code smells
        analyzer = self.analyzers.get(language)
        if analyzer is None:
            return {
                'success': False,
                'error': f"Analyzer not available for {language.value}",
                'language': language.value,
                'smells': []
            }
        
        smells = analyzer.analyze(ast_tree, code)
        
        return {
            'success': True,
            'language': language.value,
            'file_path': file_path,
            'smell_count': len(smells),
            'smells': [self._smell_to_dict(smell) for smell in smells]
        }
    
    def analyze_code_string(self, code: str, language: str) -> Dict[str, Any]:
        """
        Analyze code string for code smells
        
        Args:
            code: Source code string
            language: Language name ('python', 'javascript', etc.)
            
        Returns:
            Analysis results dict
        """
        # Convert language string to enum
        lang_enum = self._string_to_language(language)
        
        if lang_enum == Language.UNKNOWN:
            return {
                'success': False,
                'error': f"Unsupported language: {language}",
                'language': language,
                'smells': []
            }
        
        # Parse code
        ast_tree = self.parser_registry.parse(code, lang_enum)
        if ast_tree is None:
            return {
                'success': False,
                'error': f"Failed to parse {language} code",
                'language': language,
                'smells': []
            }
        
        # Analyze
        analyzer = self.analyzers.get(lang_enum)
        if analyzer is None:
            return {
                'success': False,
                'error': f"Analyzer not available for {language}",
                'language': language,
                'smells': []
            }
        
        smells = analyzer.analyze(ast_tree, code)
        
        return {
            'success': True,
            'language': language,
            'smell_count': len(smells),
            'smells': [self._smell_to_dict(smell) for smell in smells]
        }
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages
        
        Returns:
            List of language names
        """
        return [lang.value for lang in self.parser_registry.get_available_languages()]
    
    def _smell_to_dict(self, smell: CodeSmell) -> dict:
        """Convert CodeSmell to dictionary"""
        return {
            'type': smell.smell_type.value,
            'function': smell.function_name,
            'line': smell.line_number,
            'confidence': smell.confidence,
            'message': smell.message,
            'suggestion': smell.suggestion,
            'metadata': smell.metadata
        }
    
    def _string_to_language(self, language_str: str) -> Language:
        """Convert language string to Language enum"""
        mapping = {
            'python': Language.PYTHON,
            'javascript': Language.JAVASCRIPT,
            'js': Language.JAVASCRIPT,
            'typescript': Language.TYPESCRIPT,
            'ts': Language.TYPESCRIPT,
            'csharp': Language.CSHARP,
            'cs': Language.CSHARP,
            'c#': Language.CSHARP,
        }
        return mapping.get(language_str.lower(), Language.UNKNOWN)


# Singleton instance
_orchestrator: Optional[MultiLanguageRefactoringOrchestrator] = None


def get_refactoring_orchestrator() -> MultiLanguageRefactoringOrchestrator:
    """
    Get singleton orchestrator instance
    
    Returns:
        MultiLanguageRefactoringOrchestrator instance
    """
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = MultiLanguageRefactoringOrchestrator()
    return _orchestrator
