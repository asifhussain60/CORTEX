"""
PersonaLoader agent for cached persona configuration access.

Provides singleton access to persona configurations with LRU caching.

AC_START: AC-PHASE37.2-006
"""

from typing import Dict, List, Optional
from functools import lru_cache

from cortex.brain.core.yaml_loaders import load_personas
from cortex.brain.core.models.persona_models import Persona, DepthLevel, PersonasYAML


class PersonaLoader:
    """Cached access to persona configurations (singleton)."""
    
    _instance: Optional['PersonaLoader'] = None
    
    # Persona ID aliases
    ALIASES = {
        "pm": "product_owner",
        "po": "product_owner",
        "sm": "scrum_master",
        "tl": "tech_lead",
        "eng": "engineer",
        "dev": "engineer",
        "business": "business_leader",
        "exec": "business_leader"
    }
    
    def __new__(cls):
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize loader (only once due to singleton)."""
        if self._initialized:
            return
        
        self._personas_yaml: Optional[PersonasYAML] = None
        self._initialized = True
    
    def _load_config(self) -> PersonasYAML:
        """Load personas configuration (lazy loading)."""
        if self._personas_yaml is None:
            self._personas_yaml = load_personas()
        return self._personas_yaml
    
    @lru_cache(maxsize=16)
    def get_persona(self, persona_id: str) -> Optional[Persona]:
        """Get persona configuration by ID (with caching).
        
        Args:
            persona_id: Persona ID or alias
        
        Returns:
            Persona model or None if not found
        """
        # Resolve alias
        resolved_id = self.ALIASES.get(persona_id, persona_id)
        
        config = self._load_config()
        return config.get_persona(resolved_id)
    
    def get_all_personas(self) -> Dict[str, Persona]:
        """Get all persona configurations.
        
        Returns:
            Dictionary of persona_id → Persona
        """
        config = self._load_config()
        return config.personas
    
    @lru_cache(maxsize=8)
    def get_depth_level(self, depth_id: str) -> Optional[DepthLevel]:
        """Get depth level configuration by ID (with caching).
        
        Args:
            depth_id: Depth level ID
        
        Returns:
            DepthLevel model or None if not found
        """
        config = self._load_config()
        return config.get_depth_level(depth_id)
    
    def list_persona_ids(self) -> List[str]:
        """List all available persona IDs.
        
        Returns:
            List of persona IDs
        """
        config = self._load_config()
        return config.list_personas()
    
    def clear_cache(self) -> None:
        """Clear LRU caches (useful for testing)."""
        self.get_persona.cache_clear()
        self.get_depth_level.cache_clear()


# AC_COMPLETE: AC-PHASE37.2-006 ✅ PersonaLoader with singleton + LRU caching
