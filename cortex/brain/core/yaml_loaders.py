"""
YAML loaders for CORTEX governance files.

Part of ENH-048: Prompt Unbloating System
Provides lazy-loading YAML parsers with caching and validation.
"""

import time
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional, TypeVar, Union

import yaml

from cortex.brain.core.models import (
    AuditChecklistYAML,
    CoreRulesYAML,
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

    # Additional methods for governance tools
    def get_all_rules(self) -> list:
        """Get all rules (core + special).

        Returns:
            List of all CoreRule objects
        """
        data = self.load()
        rules = list(data.core_rules)
        if data.special_rules:
            rules.extend(data.special_rules)
        return rules

    def get_enforcement_levels(self) -> Dict[str, list]:
        """Get rules grouped by enforcement level.

        Returns:
            Dictionary mapping enforcement level -> list of rules
        """
        data = self.load()
        levels = {}

        for rule in data.core_rules:
            if rule.enforcement:
                if rule.enforcement not in levels:
                    levels[rule.enforcement] = []
                levels[rule.enforcement].append(rule)

        if data.special_rules:
            for rule in data.special_rules:
                if rule.enforcement:
                    if rule.enforcement not in levels:
                        levels[rule.enforcement] = []
                    levels[rule.enforcement].append(rule)

        return levels

    def get_policy_categories(self) -> list:
        """Get list of unique policy enforcement levels.

        Returns:
            List of enforcement level names
        """
        data = self.load()
        levels = set()

        for rule in data.core_rules:
            if rule.enforcement:
                levels.add(rule.enforcement)

        if data.special_rules:
            for rule in data.special_rules:
                if rule.enforcement:
                    levels.add(rule.enforcement)

        return sorted(list(levels))


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


class TierRulesLoader:
    """Loader for Tier 1/2 (project/team) governance rules from database.

    Tier 0: Core rules (YAML, immutable)
    Tier 1: Project-level rules (database, project-scoped)
    Tier 2: Team-level rules (database, team-scoped)
    """

    def __init__(self) -> None:
        """Initialize Tier rules loader."""
        # Lazily loaded database manager
        self._db_manager = None

    def _get_db(self):
        """Get database manager instance (lazy load).

        Returns:
            GovernanceDatabaseManager singleton
        """
        if self._db_manager is None:
            from cortex.brain.core.governance_database import GovernanceDatabaseManager
            self._db_manager = GovernanceDatabaseManager.instance()
            self._db_manager.initialize()
        return self._db_manager

    def get_project_rules(self) -> list:
        """Get all Tier 1 (project-level) rules.

        Returns:
            List of project-level GovernanceRule objects
        """
        db = self._get_db()
        rules = db.list_rules(tier=1)
        return [rule.to_dict() for rule in rules]

    def get_team_rules(self) -> list:
        """Get all Tier 2 (team-level) rules.

        Returns:
            List of team-level GovernanceRule objects
        """
        db = self._get_db()
        rules = db.list_rules(tier=2)
        return [rule.to_dict() for rule in rules]

    def get_rule_by_id(self, rule_id: str, tier: int) -> Optional[Dict[str, Any]]:
        """Get specific rule by ID from Tier 1 or 2.

        Args:
            rule_id: Rule identifier
            tier: Tier level (1 or 2)

        Returns:
            Rule dict if found, None otherwise
        """
        db = self._get_db()
        rule = db.get_rule(rule_id, tier)

        if rule:
            return rule.to_dict()
        return None

    def get_rules_by_category(self, category: str, tier: int = 1) -> list:
        """Get all rules with specific category.

        Args:
            category: Rule category
            tier: Tier level (1 or 2)

        Returns:
            List of rules with given category
        """
        db = self._get_db()
        rules = db.get_rules_by_category(category, tier)
        return [rule.to_dict() for rule in rules]

    def get_rules_by_severity(self, severity: str, tier: int = 1) -> list:
        """Get all rules with specific severity.

        Args:
            severity: Rule severity (CRITICAL, HIGH, MEDIUM, LOW)
            tier: Tier level (1 or 2)

        Returns:
            List of rules with given severity
        """
        db = self._get_db()
        rules = db.get_rules_by_severity(severity, tier)
        return [rule.to_dict() for rule in rules]

    def get_rules_by_enforcement_point(self, enforcement_point: str, tier: int = 1) -> list:
        """Get all rules with specific enforcement point.

        Args:
            enforcement_point: Enforcement point name
            tier: Tier level (1 or 2)

        Returns:
            List of rules with given enforcement point
        """
        db = self._get_db()
        rules = db.get_rules_by_enforcement_point(enforcement_point, tier)
        return [rule.to_dict() for rule in rules]

    def search_rules(self, query_term: str, tier: int = 1) -> list:
        """Search rules by query term.

        Args:
            query_term: Search term (matches name, description, category)
            tier: Tier level (1 or 2)

        Returns:
            List of matching rules
        """
        db = self._get_db()
        rules = db.search_rules(query_term, tier)
        return [rule.to_dict() for rule in rules]

    def get_enforcement_statistics(self) -> Dict[str, Any]:
        """Get statistics about Tier rules.

        Returns:
            Dictionary with rule counts and metrics
        """
        db = self._get_db()

        # Get counts from both tiers
        tier1_rules = db.list_rules(tier=1)
        tier2_rules = db.list_rules(tier=2)

        stats = {
            "total_project_rules": len(tier1_rules),
            "total_team_rules": len(tier2_rules),
            "total_rules": len(tier1_rules) + len(tier2_rules),
            "active_project_rules": sum(1 for r in tier1_rules if r.is_active),
            "active_team_rules": sum(1 for r in tier2_rules if r.is_active),
        }

        return stats


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
