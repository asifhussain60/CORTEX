"""
PersonaLoader - YAML-based persona configuration loader

S1: Persona YAML Schema + Loader (20 tests target)
"""

import yaml
from pathlib import Path
from typing import Dict, Optional
from .models import PersonaConfig, DepthConfig, PersonaId, DepthLevel


class PersonaLoader:
    """
    Loads persona and depth configurations from YAML files.
    
    Provides centralized access to persona definitions with caching.
    """

    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize loader with optional custom config path.
        
        Args:
            config_path: Path to personas.yaml. Defaults to bundled file.
        """
        if config_path is None:
            config_path = Path(__file__).parent / "personas.yaml"
        
        self.config_path = config_path
        self._personas_cache: Optional[Dict[str, PersonaConfig]] = None
        self._depths_cache: Optional[Dict[str, DepthConfig]] = None
        self._raw_config = None

    def load(self) -> Dict:
        """
        Load and parse personas.yaml configuration.
        
        Returns:
            Raw YAML configuration dictionary
            
        Raises:
            FileNotFoundError: If personas.yaml not found
            yaml.YAMLError: If YAML parsing fails
        """
        if self._raw_config is not None:
            return self._raw_config
        
        with open(self.config_path, 'r') as f:
            self._raw_config = yaml.safe_load(f)
        
        return self._raw_config

    def get_persona(self, persona_id: str) -> Optional[PersonaConfig]:
        """
        Get persona configuration by ID.
        
        Args:
            persona_id: Persona identifier (e.g., "engineer", "product_owner")
            
        Returns:
            PersonaConfig if found, None otherwise
        """
        personas = self.get_all_personas()
        return personas.get(persona_id)

    def get_all_personas(self) -> Dict[str, PersonaConfig]:
        """
        Get all loaded persona configurations.
        
        Uses caching to avoid repeated YAML parsing.
        
        Returns:
            Dictionary mapping persona IDs to PersonaConfig objects
        """
        if self._personas_cache is not None:
            return self._personas_cache
        
        config = self.load()
        personas_raw = config.get("personas", {})
        
        self._personas_cache = {}
        for persona_id, persona_data in personas_raw.items():
            try:
                self._personas_cache[persona_id] = PersonaConfig(
                    id=PersonaId(persona_id),
                    display_name=persona_data.get("display_name", ""),
                    description=persona_data.get("description", ""),
                    format=persona_data.get("format", ""),
                    depth=DepthLevel(persona_data["depth"]) if persona_data.get("depth") else None,
                    word_limit=persona_data.get("word_limit"),
                    show_code=persona_data.get("show_code", False),
                    show_metrics=persona_data.get("show_metrics", False),
                    metric_types=persona_data.get("metric_types", []),
                    onboarding=persona_data.get("onboarding", False),
                    onboarding_focus=persona_data.get("onboarding_focus", []),
                    trigger_discovery=persona_data.get("trigger_discovery", False),
                )
            except (ValueError, KeyError) as e:
                # Log error but continue loading other personas
                print(f"Warning: Failed to load persona '{persona_id}': {e}")
        
        return self._personas_cache

    def get_depth(self, depth_id: str) -> Optional[DepthConfig]:
        """
        Get depth level configuration by ID.
        
        Args:
            depth_id: Depth identifier (e.g., "executive", "full")
            
        Returns:
            DepthConfig if found, None otherwise
        """
        depths = self.get_all_depths()
        return depths.get(depth_id)

    def get_all_depths(self) -> Dict[str, DepthConfig]:
        """
        Get all loaded depth level configurations.
        
        Uses caching to avoid repeated YAML parsing.
        
        Returns:
            Dictionary mapping depth IDs to DepthConfig objects
        """
        if self._depths_cache is not None:
            return self._depths_cache
        
        config = self.load()
        depths_raw = config.get("depth_levels", {})
        
        self._depths_cache = {}
        for depth_id, depth_data in depths_raw.items():
            try:
                self._depths_cache[depth_id] = DepthConfig(
                    id=DepthLevel(depth_id),
                    description=depth_data.get("description", ""),
                    word_limit=depth_data.get("word_limit"),
                    show_code=depth_data.get("show_code", False),
                    metrics=depth_data.get("metrics", ""),
                )
            except (ValueError, KeyError) as e:
                print(f"Warning: Failed to load depth '{depth_id}': {e}")
        
        return self._depths_cache

    def get_default_persona(self) -> Optional[PersonaConfig]:
        """
        Get default persona (usually 'engineer' or 'unknown').
        
        Returns:
            Default PersonaConfig or None
        """
        # Try engineer first, then unknown
        for pid in ["engineer", "unknown"]:
            persona = self.get_persona(pid)
            if persona:
                return persona
        
        # Fallback to first available
        personas = self.get_all_personas()
        if personas:
            return next(iter(personas.values()))
        
        return None

    def is_valid_persona(self, persona_id: str) -> bool:
        """
        Check if a persona ID is valid.
        
        Args:
            persona_id: Persona identifier to validate
            
        Returns:
            True if persona exists, False otherwise
        """
        return persona_id in self.get_all_personas()

    def is_valid_depth(self, depth_id: str) -> bool:
        """
        Check if a depth ID is valid.
        
        Args:
            depth_id: Depth identifier to validate
            
        Returns:
            True if depth exists, False otherwise
        """
        return depth_id in self.get_all_depths()

    def clear_cache(self):
        """
        Clear internal caches (useful for testing or config reloads).
        """
        self._personas_cache = None
        self._depths_cache = None
        self._raw_config = None
