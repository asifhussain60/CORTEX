"""
YAML loaders for CORTEX governance files.

Part of ENH-048: Prompt Unbloating System
Provides lazy-loading YAML parsers with caching and validation.
"""

import yaml
from pathlib import Path
from typing import Optional, Dict, Any, Union, TypeVar
from functools import lru_cache
import time

from cortex.brain.core.models import (
    CoreRulesYAML,
    AuditChecklistYAML,
    ModesYAML,
    ResponseFormatYAML,
)
from cortex.brain.core.models.persona_models import PersonasYAML

# Type variable for generic loader data
T = TypeVar('T', CoreRulesYAML, AuditChecklistYAML, ModesYAML, ResponseFormatYAML, PersonasYAML)


class YAMLLoadError(Exception):
    """Raised when YAML loading fails."""
    pass


class BaseYAMLLoader:
    """Base class for YAML loaders with caching and metrics."""
    
    def __init__(self, file_path: Path) -> None:
        """Initialize loader with file path.
        
        Args:
            file_path: Path to YAML file
            
        Raises:
            YAMLLoadError: If file doesn't exist
        """
        self.file_path = file_path
        if not self.file_path.exists():
            raise YAMLLoadError(f"YAML file not found: {file_path}")
        
        self._load_time_ms: Optional[float] = None
        self._data: Optional[Any] = None
    
    def _load_yaml(self) -> Dict[str, Any]:
        """Load YAML file and measure time.
        
        Returns:
            Parsed YAML data
            
        Raises:
            YAMLLoadError: If YAML parsing fails
        """
        start = time.perf_counter()
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            self._load_time_ms = (time.perf_counter() - start) * 1000
            return data
        except yaml.YAMLError as e:
            raise YAMLLoadError(f"Failed to parse YAML {self.file_path}: {e}")
        except Exception as e:
            raise YAMLLoadError(f"Failed to load YAML {self.file_path}: {e}")
    
    @property
    def load_time_ms(self) -> Optional[float]:
        """Get last load time in milliseconds."""
        return self._load_time_ms


class CoreRulesLoader(BaseYAMLLoader):
    """Loader for core-rules.yaml with validation."""
    
    def load(self) -> CoreRulesYAML:
        """Load and validate core rules YAML.
        
        Returns:
            Validated CoreRulesYAML model
            
        Raises:
            YAMLLoadError: If validation fails
        """
        if self._data is None:
            raw_data = self._load_yaml()
            try:
                self._data = CoreRulesYAML(**raw_data)
            except Exception as e:
                raise YAMLLoadError(f"CoreRules validation failed: {e}")
        
        return self._data
    
    def get_rule_by_id(self, rule_id: str) -> Optional[Any]:
        """Get specific rule by ID.
        
        Args:
            rule_id: Rule ID (e.g., "CORE-008")
            
        Returns:
            CoreRule if found, None otherwise
        """
        data = self.load()
        for rule in data.core_rules:
            if rule.id == rule_id:
                return rule
        
        # Check special rules
        if data.special_rules:
            for rule in data.special_rules:
                if rule.id == rule_id:
                    return rule
        
        return None
    
    def get_rules_by_enforcement(self, level: str) -> list:
        """Get all rules with specific enforcement level.
        
        Args:
            level: Enforcement level (e.g., "BLOCKED")
            
        Returns:
            List of CoreRule objects
        """
        data = self.load()
        rules = []
        
        for rule in data.core_rules:
            if rule.enforcement and rule.enforcement == level:
                rules.append(rule)
        
        if data.special_rules:
            for rule in data.special_rules:
                if rule.enforcement and rule.enforcement == level:
                    rules.append(rule)
        
        return rules


class AuditChecklistLoader(BaseYAMLLoader):
    """Loader for audit-checklist.yaml with validation."""
    
    def load(self) -> AuditChecklistYAML:
        """Load and validate audit checklist YAML.
        
        Returns:
            Validated AuditChecklistYAML model
            
        Raises:
            YAMLLoadError: If validation fails
        """
        if self._data is None:
            raw_data = self._load_yaml()
            try:
                self._data = AuditChecklistYAML(**raw_data)
            except Exception as e:
                raise YAMLLoadError(f"AuditChecklist validation failed: {e}")
        
        return self._data
    
    def get_checks_by_priority(self, priority: str) -> list:
        """Get all checks for specific priority.
        
        Args:
            priority: Priority level (P0, P1, P2, P3)
            
        Returns:
            List of AuditCheck objects
        """
        data = self.load()
        priority_key = priority.upper()
        
        if priority_key in data.priority_checks:
            return data.priority_checks[priority_key].checks
        
        return []
    
    def get_check_by_id(self, check_id: str) -> Optional[Any]:
        """Get specific check by ID.
        
        Args:
            check_id: Check ID (e.g., "P0-001")
            
        Returns:
            AuditCheck if found, None otherwise
        """
        data = self.load()
        
        for priority_category in data.priority_checks.values():
            for check in priority_category.checks:
                if check.id == check_id:
                    return check
        
        return None


class ModesLoader(BaseYAMLLoader):
    """Loader for modes.yaml with validation."""
    
    def load(self) -> ModesYAML:
        """Load and validate modes YAML.
        
        Returns:
            Validated ModesYAML model
            
        Raises:
            YAMLLoadError: If validation fails
        """
        if self._data is None:
            raw_data = self._load_yaml()
            try:
                self._data = ModesYAML(**raw_data)
            except Exception as e:
                raise YAMLLoadError(f"Modes validation failed: {e}")
        
        return self._data
    
    def get_mode(self, mode_name: str) -> Optional[Any]:
        """Get specific mode definition.
        
        Args:
            mode_name: Mode name (e.g., "PRE-FLIGHT", "AUDIT")
            
        Returns:
            ModeDefinition if found, None otherwise
        """
        data = self.load()
        return data.modes.get(mode_name)
    
    def get_all_mode_names(self) -> list:
        """Get list of all mode names.
        
        Returns:
            List of mode names
        """
        data = self.load()
        return list(data.modes.keys())


class ResponseFormatLoader(BaseYAMLLoader):
    """Loader for response-format.yaml with validation."""
    
    def load(self) -> ResponseFormatYAML:
        """Load and validate response format YAML.
        
        Returns:
            Validated ResponseFormatYAML model
            
        Raises:
            YAMLLoadError: If validation fails
        """
        if self._data is None:
            raw_data = self._load_yaml()
            try:
                self._data = ResponseFormatYAML(**raw_data)
            except Exception as e:
                raise YAMLLoadError(f"ResponseFormat validation failed: {e}")
        
        return self._data
    
    def get_header_template(self) -> str:
        """Get response header template.
        
        Returns:
            Header template string
        """
        data = self.load()
        return str(data.header.get("template", ""))
    
    def get_status_icons(self) -> Dict[str, Any]:
        """Get status icon mappings.
        
        Returns:
            Dictionary of status -> icon info
        """
        data = self.load()
        status_icons = data.icons.get("status", {})
        # Extract just the icon strings if nested
        result = {}
        for key, value in status_icons.items():
            if isinstance(value, dict) and 'icon' in value:
                result[key] = value['icon']
            else:
                result[key] = value
        return result


# Global loader registry with lazy initialization
_LOADER_REGISTRY: Dict[str, BaseYAMLLoader] = {}


@lru_cache(maxsize=4)
def get_loader(yaml_type: str, registry_path: Path) -> BaseYAMLLoader:
    """Get or create YAML loader (cached).
    
    Args:
        yaml_type: Type of YAML file (core_rules, audit_checklist, modes, response_format)
        registry_path: Path to cortex-registry/_cortex-master directory
        
    Returns:
        Appropriate YAML loader instance
        
    Raises:
        ValueError: If yaml_type is unknown
        YAMLLoadError: If loader initialization fails
    """
    loaders = {
        "core_rules": (CoreRulesLoader, "governance/core-rules.yaml"),
        "audit_checklist": (AuditChecklistLoader, "governance/audit-checklist.yaml"),
        "modes": (ModesLoader, "meta/modes.yaml"),
        "response_format": (ResponseFormatLoader, "meta/response-format.yaml"),
    }
    
    if yaml_type not in loaders:
        raise ValueError(f"Unknown YAML type: {yaml_type}. Valid types: {list(loaders.keys())}")
    
    loader_class, relative_path = loaders[yaml_type]
    file_path = registry_path / relative_path
    
    return loader_class(file_path)


def get_cortex_registry_path() -> Path:
    """Get path to cortex-registry/_cortex-master directory.
    
    Returns:
        Path to registry directory
        
    Raises:
        FileNotFoundError: If registry not found
    """
    # Try multiple potential locations
    candidates = [
        Path(__file__).parent.parent.parent.parent.parent / "cortex-registry" / "_cortex-master",
        Path.cwd() / "cortex-registry" / "_cortex-master",
    ]
    
    for candidate in candidates:
        if candidate.exists():
            return candidate
    
    raise FileNotFoundError(
        f"cortex-registry/_cortex-master not found. Tried: {[str(c) for c in candidates]}"
    )


# Convenience functions
def load_core_rules() -> CoreRulesYAML:
    """Load core rules YAML (convenience function).
    
    Returns:
        Validated CoreRulesYAML model
    """
    registry_path = get_cortex_registry_path()
    loader = get_loader("core_rules", registry_path)
    assert isinstance(loader, CoreRulesLoader)
    return loader.load()


def load_audit_checklist() -> AuditChecklistYAML:
    """Load audit checklist YAML (convenience function).
    
    Returns:
        Validated AuditChecklistYAML model
    """
    registry_path = get_cortex_registry_path()
    loader = get_loader("audit_checklist", registry_path)
    assert isinstance(loader, AuditChecklistLoader)
    return loader.load()


def load_modes() -> ModesYAML:
    """Load modes YAML (convenience function).
    
    Returns:
        Validated ModesYAML model
    """
    registry_path = get_cortex_registry_path()
    loader = get_loader("modes", registry_path)
    assert isinstance(loader, ModesLoader)
    return loader.load()


def load_response_format() -> ResponseFormatYAML:
    """Load response format YAML (convenience function).
    
    Returns:
        Validated ResponseFormatYAML model
    """
    registry_path = get_cortex_registry_path()
    loader = get_loader("response_format", registry_path)
    assert isinstance(loader, ResponseFormatLoader)
    return loader.load()


# ============================================================================
# PERSONAS LOADER (Phase 37 - Stage 1)
# ============================================================================

class PersonasLoader(BaseYAMLLoader):
    """Loader for personas.yaml with validation."""
    
    def load(self) -> PersonasYAML:
        """Load and validate personas YAML.
        
        Returns:
            Validated PersonasYAML model
            
        Raises:
            YAMLLoadError: If validation fails
        """
        if self._data is None:
            raw_data = self._load_yaml()
            try:
                self._data = PersonasYAML(**raw_data)
            except Exception as e:
                raise YAMLLoadError(f"Personas validation failed: {e}")
        
        return self._data


# Cache for personas loader (singleton pattern)
_personas_cache: Optional[PersonasYAML] = None


def load_personas() -> PersonasYAML:
    """Load personas YAML with caching (convenience function).
    
    Returns:
        Validated PersonasYAML model
        
    Raises:
        YAMLLoadError: If file not found or validation fails
    """
    global _personas_cache
    
    if _personas_cache is None:
        # Locate personas.yaml in cortex/config/
        import cortex
        cortex_root = Path(cortex.__file__).parent
        personas_path = cortex_root / "config" / "personas.yaml"
        
        if not personas_path.exists():
            raise YAMLLoadError(f"personas.yaml not found at {personas_path}")
        
        loader = PersonasLoader(personas_path)
        _personas_cache = loader.load()
    
    return _personas_cache


def clear_personas_cache() -> None:
    """Clear personas cache (useful for testing)."""
    global _personas_cache
    _personas_cache = None


# Monkey-patch clear_cache as function attribute for testing
load_personas.clear_cache = clear_personas_cache  # type: ignore[attr-defined]


# AC_COMPLETE: AC-PHASE37.1-004 ✅ load_personas() with caching implemented
