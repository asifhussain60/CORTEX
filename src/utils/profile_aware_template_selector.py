"""
Profile-Aware Template Selector (Task 3.1)
Extends template selection with user profile integration for personalized responses
"""
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
from pathlib import Path

from src.utils.template_selector import TemplateSelector, SelectionResult as BaseSelectionResult
from src.setup.models.user_profile import UserProfile, SUPPORTED_LANGUAGES
from src.setup.modules.user_profile_storage import UserProfileStorage


@dataclass
class ProfileAwareSelectionResult:
    """Extended selection result with profile-aware metadata"""
    template_id: str
    language: str
    verbosity: str
    role: str
    confidence: float
    matched_intent: str
    matched_keywords: List[str]
    orchestrator: Optional[str] = None


class ProfileAwareTemplateSelector:
    """
    Template selector with user profile awareness.
    
    Features:
    - Language-based template selection (12 languages)
    - Verbosity filtering (concise/balanced/verbose)
    - Role-aware template selection (beginner/intermediate/expert)
    - Automatic profile loading from storage
    - Fallback to English for unsupported languages
    - Context override support
    
    Usage:
        # With profile
        profile = UserProfile(name="User", language="es", preference="concise", ...)
        selector = ProfileAwareTemplateSelector(profile=profile)
        result = selector.select_template("help")
        
        # Auto-load from storage
        selector = ProfileAwareTemplateSelector()
        result = selector.select_template("help")
    """
    
    # Available template languages (subset of supported languages with templates)
    TEMPLATE_LANGUAGES = ["en", "es"]  # Start with English and Spanish
    
    # Verbosity levels
    VERBOSITY_LEVELS = ["concise", "balanced", "verbose"]
    
    def __init__(self, profile: Optional[UserProfile] = None, brain_path: Optional[str] = None):
        """
        Initialize profile-aware template selector.
        
        Args:
            profile: User profile (optional, will load from storage if None)
            brain_path: Path to cortex-brain directory
        """
        # Load profile from storage if not provided
        if profile is None:
            storage = UserProfileStorage()
            profile = storage.load_profile()
        
        self.profile = profile
        
        # Base template selector
        self.base_selector = TemplateSelector(brain_path=brain_path)
        
        # Cache for template selection results
        self._cache: Dict[str, ProfileAwareSelectionResult] = {}
    
    def select_template(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ProfileAwareSelectionResult:
        """
        Select template based on user input and profile preferences.
        
        Args:
            user_input: User's natural language input
            context: Additional context (can override profile preferences)
        
        Returns:
            ProfileAwareSelectionResult with template selection metadata
        """
        context = context or {}
        
        # Check cache
        cache_key = f"{user_input}:{context.get('force_language', '')}:{context.get('force_verbosity', '')}"
        if cache_key in self._cache:
            return self._cache[cache_key]
        
        # Get base template selection
        base_result = self.base_selector.select_template(user_input, context)
        
        # Determine language, verbosity, and role from profile/context
        language = self._get_language(context)
        verbosity = self._get_verbosity(context)
        role = self._get_role()
        
        # Construct profile-aware template ID
        # Format: {base_template_id}_{language}_{verbosity}
        template_id = self._construct_template_id(
            base_result.template_id,
            language,
            verbosity
        )
        
        result = ProfileAwareSelectionResult(
            template_id=template_id,
            language=language,
            verbosity=verbosity,
            role=role,
            confidence=base_result.confidence,
            matched_intent=base_result.matched_intent,
            matched_keywords=base_result.matched_keywords,
            orchestrator=base_result.orchestrator
        )
        
        # Cache result
        self._cache[cache_key] = result
        
        return result
    
    def _get_language(self, context: Dict[str, Any]) -> str:
        """
        Determine language from context or profile.
        
        Priority: context override > profile > default (en)
        Fallback to English if language not supported in templates.
        
        Args:
            context: Request context with optional 'force_language'
        
        Returns:
            Language code (guaranteed to be in TEMPLATE_LANGUAGES)
        """
        language = context.get('force_language')
        if not language and self.profile:
            language = self.profile.language
        if not language:
            language = "en"
        
        # Fallback to English if language not supported in templates
        if language not in self.TEMPLATE_LANGUAGES:
            language = "en"
        
        return language
    
    def _get_verbosity(self, context: Dict[str, Any]) -> str:
        """
        Determine verbosity from context or profile.
        
        Priority: context override > profile > default (verbose)
        
        Args:
            context: Request context with optional 'force_verbosity'
        
        Returns:
            Verbosity level (concise/balanced/verbose)
        """
        verbosity = context.get('force_verbosity')
        if not verbosity and self.profile:
            verbosity = self.profile.preference
        if not verbosity:
            verbosity = "verbose"
        
        return verbosity
    
    def _get_role(self) -> str:
        """
        Determine user role from profile.
        
        Returns:
            Role level (beginner/intermediate/expert)
        """
        return self.profile.role if self.profile else "intermediate"
    
    def _construct_template_id(self, base_id: str, language: str, verbosity: str) -> str:
        """
        Construct profile-aware template ID.
        
        Args:
            base_id: Base template ID from selector
            language: Language code (en, es, etc.)
            verbosity: Verbosity level (concise, balanced, verbose)
        
        Returns:
            Full template ID with language and verbosity suffixes
        """
        # Format: base_id_lang_verbosity
        # Example: help_en_concise, onboarding_es_verbose
        return f"{base_id}_{language}_{verbosity}"
    
    def get_available_languages(self) -> List[str]:
        """
        Get list of available template languages.
        
        Returns:
            List of language codes
        """
        return list(self.TEMPLATE_LANGUAGES)
    
    def get_template_variants(self, template_id: str) -> Dict[str, List[str]]:
        """
        Get available variants for a template.
        
        Args:
            template_id: Base template ID
        
        Returns:
            Dict with 'languages' and 'verbosity_levels' lists
        """
        return {
            "languages": self.TEMPLATE_LANGUAGES,
            "verbosity_levels": self.VERBOSITY_LEVELS
        }
