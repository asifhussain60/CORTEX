"""
Multilingual Template Loader (Task 3.2)
Loads and manages language-specific template variants
"""
from typing import Optional, Dict, List, Any
from pathlib import Path
import yaml


class MultilingualTemplateLoader:
    """
    Loader for multilingual template variants.
    
    Features:
    - Load templates by language and verbosity
    - Fallback to English for unsupported languages
    - Fallback to balanced verbosity when requested level unavailable
    - Template caching for performance
    - Structure validation
    - Metadata retrieval
    
    Usage:
        loader = MultilingualTemplateLoader()
        template = loader.get_template("help", language="es", verbosity="concise")
    """
    
    DEFAULT_TEMPLATE_PATH = "/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/multilingual-templates.yaml"
    
    def __init__(self, template_path: Optional[str] = None):
        """
        Initialize multilingual template loader.
        
        Args:
            template_path: Path to multilingual templates YAML file
        """
        self.template_path = Path(template_path or self.DEFAULT_TEMPLATE_PATH)
        self._templates: Dict[str, Any] = {}
        self._supported_languages: List[str] = []
        self._cache: Dict[str, str] = {}
        self.cache_hits = 0
        
        # Load templates
        self._load_templates()
    
    def _load_templates(self):
        """Load templates from YAML file"""
        if not self.template_path.exists():
            raise FileNotFoundError(f"Template file not found: {self.template_path}")
        
        with open(self.template_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        self._templates = data.get('templates', {})
        self._supported_languages = data.get('supported_languages', ['en'])
        
        # Clear cache on reload
        self._cache.clear()
        self.cache_hits = 0
    
    @property
    def template_count(self) -> int:
        """Get total number of base templates"""
        return len(self._templates)
    
    def get_template(
        self,
        template_name: str,
        language: str = "en",
        verbosity: str = "balanced"
    ) -> Optional[str]:
        """
        Get template by name, language, and verbosity.
        
        Fallback logic:
        1. Requested language + verbosity
        2. Requested language + balanced verbosity
        3. English + requested verbosity
        4. English + balanced verbosity
        
        Args:
            template_name: Template identifier (e.g., "help", "onboarding")
            language: Language code (e.g., "en", "es", "fr")
            verbosity: Verbosity level (concise/balanced/verbose)
        
        Returns:
            Template content string or None if not found
        """
        # Check cache first
        cache_key = f"{template_name}:{language}:{verbosity}"
        if cache_key in self._cache:
            self.cache_hits += 1
            return self._cache[cache_key]
        
        # Template doesn't exist
        if template_name not in self._templates:
            return None
        
        template_data = self._templates[template_name]
        
        # Try requested language
        if language in template_data:
            lang_data = template_data[language]
            
            # Try requested verbosity
            if verbosity in lang_data:
                content = lang_data[verbosity].get('content', '')
                self._cache[cache_key] = content
                return content
            
            # Fallback to balanced verbosity
            if 'balanced' in lang_data:
                content = lang_data['balanced'].get('content', '')
                self._cache[cache_key] = content
                return content
        
        # Fallback to English
        if 'en' in template_data:
            lang_data = template_data['en']
            
            # Try requested verbosity in English
            if verbosity in lang_data:
                content = lang_data[verbosity].get('content', '')
                self._cache[cache_key] = content
                return content
            
            # Fallback to balanced English
            if 'balanced' in lang_data:
                content = lang_data['balanced'].get('content', '')
                self._cache[cache_key] = content
                return content
        
        return None
    
    def get_supported_languages(self) -> List[str]:
        """
        Get list of supported languages.
        
        Returns:
            List of language codes
        """
        return list(self._supported_languages)
    
    def template_exists(self, template_name: str, language: str, verbosity: str) -> bool:
        """
        Check if specific template variant exists.
        
        Args:
            template_name: Template identifier
            language: Language code
            verbosity: Verbosity level
        
        Returns:
            True if template exists, False otherwise
        """
        if template_name not in self._templates:
            return False
        
        template_data = self._templates[template_name]
        
        if language not in template_data:
            return False
        
        lang_data = template_data[language]
        
        return verbosity in lang_data
    
    def get_available_verbosity_levels(self, template_name: str, language: str) -> List[str]:
        """
        Get available verbosity levels for template and language.
        
        Args:
            template_name: Template identifier
            language: Language code
        
        Returns:
            List of verbosity levels (concise, balanced, verbose)
        """
        if template_name not in self._templates:
            return []
        
        template_data = self._templates[template_name]
        
        if language not in template_data:
            return []
        
        lang_data = template_data[language]
        
        return list(lang_data.keys())
    
    def validate_template_structure(self) -> bool:
        """
        Validate that all templates follow expected structure.
        
        Returns:
            True if structure is valid, False otherwise
        """
        try:
            # Check that we have templates
            if not self._templates:
                return False
            
            # Check that we have supported languages
            if not self._supported_languages:
                return False
            
            # Basic structure validation
            for template_name, template_data in self._templates.items():
                if not isinstance(template_data, dict):
                    return False
                
                # Check at least English exists
                if 'en' not in template_data:
                    return False
            
            return True
        except Exception:
            return False
    
    def get_template_metadata(self, template_name: str) -> Optional[Dict[str, Any]]:
        """
        Get metadata for template (available languages and verbosity levels).
        
        Args:
            template_name: Template identifier
        
        Returns:
            Dictionary with 'languages' and 'verbosity_levels' or None
        """
        if template_name not in self._templates:
            return None
        
        template_data = self._templates[template_name]
        
        languages = list(template_data.keys())
        
        # Get verbosity levels from English (should be consistent across languages)
        verbosity_levels = []
        if 'en' in template_data:
            verbosity_levels = list(template_data['en'].keys())
        
        return {
            'languages': languages,
            'verbosity_levels': verbosity_levels
        }
    
    def reload(self):
        """Reload templates from file"""
        self._load_templates()
