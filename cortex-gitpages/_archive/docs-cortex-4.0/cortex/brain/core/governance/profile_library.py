"""
Implementation of AC-GC-006-01: Profile Library

Pre-built governance profiles for common scenarios:
- STRICT: All CORE rules required (production)
- BASELINE: Essential rules (recommended default)
- PERMISSIVE: Advisory only (learning/experimental)
- CUSTOM: User-defined profiles
- EXPERIMENTAL: New/trial rules

Provides profile management (register, search, export/import)
and enables quick governance setup without custom configuration.

CORE Governance Rules:
- CORE-005: Path portability (pathlib used for paths)
- CORE-008: TDD (tests created first)
- CORE-011: Type hints (100% coverage)
- CORE-012: Google docstrings
- CORE-027: Audit trail logging
"""

import logging
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
from pathlib import Path


logger = logging.getLogger(__name__)


class ProfileLevel(Enum):
    """
    Profile governance strictness levels.
    
    STRICT: All CORE rules required (production-grade)
    BASELINE: Essential rules (recommended baseline)
    PERMISSIVE: Advisory only (relaxed enforcement)
    CUSTOM: User-defined profiles
    EXPERIMENTAL: New/trial rules
    """
    STRICT = "STRICT"
    BASELINE = "BASELINE"
    PERMISSIVE = "PERMISSIVE"
    CUSTOM = "CUSTOM"
    EXPERIMENTAL = "EXPERIMENTAL"


@dataclass
class ProfileLibraryEntry:
    """
    Single profile library entry.
    
    Attributes:
        name: Profile name
        level: Governance strictness level
        rule_ids: Set of rule IDs in profile
        description: Human-readable description
        tags: Searchable tags (enforcement, production, etc)
    """
    name: str
    level: ProfileLevel
    rule_ids: Set[str] = field(default_factory=set)
    description: str = ""
    tags: Set[str] = field(default_factory=set)
    
    def add_rule(self, rule_id: str) -> None:
        """
        Add rule to profile.
        
        Args:
            rule_id: Rule to add
        """
        self.rule_ids.add(rule_id)
    
    def remove_rule(self, rule_id: str) -> None:
        """
        Remove rule from profile.
        
        Args:
            rule_id: Rule to remove
        """
        self.rule_ids.discard(rule_id)
    
    def add_tag(self, tag: str) -> None:
        """
        Add tag to profile.
        
        Args:
            tag: Tag to add
        """
        self.tags.add(tag)
    
    def to_dict(self) -> Dict[str, any]:
        """
        Convert to dictionary.
        
        Returns:
            Dictionary representation
        """
        return {
            "name": self.name,
            "level": self.level.value,
            "rule_ids": sorted(list(self.rule_ids)),
            "description": self.description,
            "tags": sorted(list(self.tags))
        }


class ProfileLibrary:
    """
    Manages pre-built governance profiles.
    
    Provides standard profiles (strict, baseline, permissive) and
    allows custom profile registration and search. Enables quick
    governance setup without custom configuration.
    
    Standard profiles:
    - STRICT: All CORE rules required (CORE-005, 008, 011, 012, 027, 028)
    - BASELINE: Essential rules (CORE-008, 011, 012, 027)
    - PERMISSIVE: Advisory only (CORE-012, 027)
    
    Search by level, tag, or contained rules.
    """
    
    def __init__(self) -> None:
        """Initialize library with standard profiles."""
        self._profiles: Dict[str, ProfileLibraryEntry] = {}
        self._logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")
        self._init_standard_profiles()
    
    def _init_standard_profiles(self) -> None:
        """Initialize standard profiles."""
        # STRICT profile: All CORE rules
        strict = ProfileLibraryEntry(
            name="strict",
            level=ProfileLevel.STRICT,
            description="All CORE governance rules required (strictest)"
        )
        strict.rule_ids = {
            "CORE-005", "CORE-008", "CORE-011", "CORE-012",
            "CORE-027", "CORE-028"
        }
        strict.tags = {"enforcement", "production", "core"}
        self._profiles["strict"] = strict
        self._logger.info("Initialized STRICT profile (6 rules)")
        
        # BASELINE profile: Essential rules
        baseline = ProfileLibraryEntry(
            name="baseline",
            level=ProfileLevel.BASELINE,
            description="Essential governance rules (recommended baseline)"
        )
        baseline.rule_ids = {
            "CORE-008", "CORE-011", "CORE-012", "CORE-027"
        }
        baseline.tags = {"enforcement", "default", "core"}
        self._profiles["baseline"] = baseline
        self._logger.info("Initialized BASELINE profile (4 rules)")
        
        # PERMISSIVE profile: Advisory only
        permissive = ProfileLibraryEntry(
            name="permissive",
            level=ProfileLevel.PERMISSIVE,
            description="Advisory rules (relaxed enforcement)"
        )
        permissive.rule_ids = {"CORE-012", "CORE-027"}
        permissive.tags = {"advisory", "learning", "experimental"}
        self._profiles["permissive"] = permissive
        self._logger.info("Initialized PERMISSIVE profile (2 rules)")
    
    def register_profile(
        self,
        name: str,
        level: ProfileLevel,
        rule_ids: Set[str],
        description: str = "",
        tags: Set[str] = None,
        audit: bool = True
    ) -> None:
        """
        Register new profile in library.
        
        Args:
            name: Profile name
            level: Governance level
            rule_ids: Set of rule IDs
            description: Profile description
            tags: Optional tags for searching
            audit: Whether to log to audit trail
        """
        if tags is None:
            tags = set()
        
        entry = ProfileLibraryEntry(
            name=name,
            level=level,
            rule_ids=rule_ids.copy(),
            description=description,
            tags=tags.copy()
        )
        self._profiles[name] = entry
        
        if audit:
            self._logger.info(
                f"Profile registered: {name}",
                extra={
                    "profile": name,
                    "level": level.value,
                    "rule_count": len(rule_ids),
                    "tags": sorted(list(tags))
                }
            )
    
    def get_profile(self, name: str) -> Optional[ProfileLibraryEntry]:
        """
        Get profile by name (O(1)).
        
        Args:
            name: Profile name
        
        Returns:
            ProfileLibraryEntry or None
        """
        return self._profiles.get(name)
    
    def list_profiles(self) -> List[str]:
        """
        List all profile names (sorted).
        
        Returns:
            Sorted list of profile names
        """
        return sorted(self._profiles.keys())
    
    def has_profile(self, name: str) -> bool:
        """
        Check if profile exists (O(1)).
        
        Args:
            name: Profile name
        
        Returns:
            True if exists
        """
        return name in self._profiles
    
    def search_by_level(self, level: ProfileLevel) -> List[str]:
        """
        Search profiles by governance level.
        
        Args:
            level: ProfileLevel to search for
        
        Returns:
            List of matching profile names
        """
        matches = [
            name for name, entry in self._profiles.items()
            if entry.level == level
        ]
        self._logger.debug(
            f"Search by level: {level.value} found {len(matches)} profiles"
        )
        return matches
    
    def search_by_tag(self, tag: str) -> List[str]:
        """
        Search profiles by tag.
        
        Args:
            tag: Tag to search for
        
        Returns:
            List of matching profile names
        """
        matches = [
            name for name, entry in self._profiles.items()
            if tag in entry.tags
        ]
        self._logger.debug(
            f"Search by tag: {tag} found {len(matches)} profiles"
        )
        return matches
    
    def search_by_rule(self, rule_id: str) -> List[str]:
        """
        Search profiles containing rule.
        
        Args:
            rule_id: Rule ID to search for
        
        Returns:
            List of matching profile names
        """
        matches = [
            name for name, entry in self._profiles.items()
            if rule_id in entry.rule_ids
        ]
        self._logger.debug(
            f"Search by rule: {rule_id} found {len(matches)} profiles"
        )
        return matches
    
    def get_all_tags(self) -> Set[str]:
        """
        Get all unique tags across all profiles.
        
        Returns:
            Set of all tags
        """
        all_tags = set()
        for entry in self._profiles.values():
            all_tags.update(entry.tags)
        return all_tags
    
    def profile_count(self) -> int:
        """
        Get total profile count.
        
        Returns:
            Number of profiles
        """
        return len(self._profiles)
    
    def get_rule_count(self, name: str) -> int:
        """
        Get rule count for profile.
        
        Args:
            name: Profile name
        
        Returns:
            Rule count or 0 if not found
        """
        if name not in self._profiles:
            return 0
        return len(self._profiles[name].rule_ids)
    
    def get_all_rules(self) -> Set[str]:
        """
        Get all unique rules across all profiles.
        
        Returns:
            Set of all rule IDs
        """
        all_rules = set()
        for entry in self._profiles.values():
            all_rules.update(entry.rule_ids)
        return all_rules
    
    def export_to_dict(self) -> Dict[str, Dict[str, any]]:
        """
        Export library to dictionary.
        
        Returns:
            Dictionary of profiles
        """
        return {
            name: entry.to_dict()
            for name, entry in self._profiles.items()
        }
    
    def export_to_json(self) -> str:
        """
        Export library to JSON string.
        
        Returns:
            JSON serialized library
        """
        data = self.export_to_dict()
        return json.dumps(data, indent=2, sort_keys=True)
    
    def export_to_file(self, path: Path) -> None:
        """
        Export library to JSON file.
        
        Args:
            path: Path to write to
        """
        try:
            with open(path, "w") as f:
                f.write(self.export_to_json())
            self._logger.info(
                f"Library exported to: {path}",
                extra={"path": str(path), "profile_count": len(self._profiles)}
            )
        except Exception as e:
            self._logger.error(
                f"Failed to export library: {e}",
                exc_info=True
            )
            raise
    
    def get_statistics(self) -> Dict[str, int]:
        """
        Get library statistics.
        
        Returns:
            Dictionary with counts and metrics
        """
        return {
            "profile_count": self.profile_count(),
            "total_unique_rules": len(self.get_all_rules()),
            "total_unique_tags": len(self.get_all_tags()),
            "strict_profiles": len(self.search_by_level(ProfileLevel.STRICT)),
            "baseline_profiles": len(self.search_by_level(ProfileLevel.BASELINE)),
            "permissive_profiles": len(self.search_by_level(ProfileLevel.PERMISSIVE)),
            "custom_profiles": len(self.search_by_level(ProfileLevel.CUSTOM))
        }
    
    def get_level_pyramid(self) -> Dict[str, List[str]]:
        """
        Get profiles organized by strictness level.
        
        Returns:
            Dictionary mapping level to profile names
        """
        return {
            "STRICT": sorted(self.search_by_level(ProfileLevel.STRICT)),
            "BASELINE": sorted(self.search_by_level(ProfileLevel.BASELINE)),
            "PERMISSIVE": sorted(self.search_by_level(ProfileLevel.PERMISSIVE)),
            "CUSTOM": sorted(self.search_by_level(ProfileLevel.CUSTOM)),
            "EXPERIMENTAL": sorted(self.search_by_level(ProfileLevel.EXPERIMENTAL))
        }
