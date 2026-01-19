"""
Tests for AC-GC-006-01: Profile Library

AC-GC-006-01: Profile Library
- Pre-built profiles for common governance scenarios
- Profiles: strict, baseline, permissive, custom, experimental
- Each profile: intent types, phases, confidence bands, rules
- Library manager: Load, register, search profiles
- Searchable by intent/phase/confidence/rules
- Export/import profiles

CORE Governance Rules:
- CORE-008: TDD (tests before code)
- CORE-011: Type hints (100%)
- CORE-012: Docstrings (Google style)
- CORE-027: Audit trail logging
"""

import pytest
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, field
from enum import Enum


class ProfileLevel(Enum):
    """Profile governance strictness levels."""
    STRICT = "STRICT"          # All CORE rules required
    BASELINE = "BASELINE"      # Essentials + common patterns
    PERMISSIVE = "PERMISSIVE"  # Relaxed, advisory only
    CUSTOM = "CUSTOM"          # User-defined
    EXPERIMENTAL = "EXPERIMENTAL"  # New/experimental rules


@dataclass
class ProfileLibraryEntry:
    """Single profile library entry."""
    name: str
    level: ProfileLevel
    rule_ids: Set[str] = field(default_factory=set)
    description: str = ""
    tags: Set[str] = field(default_factory=set)
    
    def add_rule(self, rule_id: str) -> None:
        """Add rule to profile."""
        self.rule_ids.add(rule_id)
    
    def add_tag(self, tag: str) -> None:
        """Add tag to profile."""
        self.tags.add(tag)


class ProfileLibrary:
    """
    Manages pre-built governance profiles.
    
    Provides standard profiles (strict, baseline, permissive) and
    allows custom profile registration.
    """
    
    def __init__(self) -> None:
        """Initialize library."""
        self._profiles: Dict[str, ProfileLibraryEntry] = {}
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
        strict.tags = {"enforcement", "production"}
        self._profiles["strict"] = strict
        
        # BASELINE profile: Essential rules
        baseline = ProfileLibraryEntry(
            name="baseline",
            level=ProfileLevel.BASELINE,
            description="Essential governance rules (recommended baseline)"
        )
        baseline.rule_ids = {
            "CORE-008", "CORE-011", "CORE-012", "CORE-027"
        }
        baseline.tags = {"enforcement", "default"}
        self._profiles["baseline"] = baseline
        
        # PERMISSIVE profile: Advisory only
        permissive = ProfileLibraryEntry(
            name="permissive",
            level=ProfileLevel.PERMISSIVE,
            description="Advisory rules (relaxed enforcement)"
        )
        permissive.rule_ids = {"CORE-012", "CORE-027"}
        permissive.tags = {"advisory", "learning"}
        self._profiles["permissive"] = permissive
    
    def register_profile(
        self,
        name: str,
        level: ProfileLevel,
        rule_ids: Set[str],
        description: str = "",
        tags: Set[str] = None
    ) -> None:
        """
        Register new profile.
        
        Args:
            name: Profile name
            level: Governance level
            rule_ids: Set of rule IDs
            description: Profile description
            tags: Optional tags
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
    
    def get_profile(self, name: str) -> Optional[ProfileLibraryEntry]:
        """Get profile by name."""
        return self._profiles.get(name)
    
    def list_profiles(self) -> List[str]:
        """List all profile names."""
        return sorted(self._profiles.keys())
    
    def search_by_level(self, level: ProfileLevel) -> List[str]:
        """Search profiles by level."""
        return [
            name for name, entry in self._profiles.items()
            if entry.level == level
        ]
    
    def search_by_tag(self, tag: str) -> List[str]:
        """Search profiles by tag."""
        return [
            name for name, entry in self._profiles.items()
            if tag in entry.tags
        ]
    
    def search_by_rule(self, rule_id: str) -> List[str]:
        """Search profiles containing rule."""
        return [
            name for name, entry in self._profiles.items()
            if rule_id in entry.rule_ids
        ]
    
    def has_profile(self, name: str) -> bool:
        """Check if profile exists."""
        return name in self._profiles
    
    def profile_count(self) -> int:
        """Get total profile count."""
        return len(self._profiles)
    
    def get_rule_count(self, name: str) -> int:
        """Get rule count for profile."""
        if name not in self._profiles:
            return 0
        return len(self._profiles[name].rule_ids)
    
    def get_all_rules(self) -> Set[str]:
        """Get all unique rules across all profiles."""
        all_rules = set()
        for entry in self._profiles.values():
            all_rules.update(entry.rule_ids)
        return all_rules


class TestProfileLibraryEntry:
    """Tests for ProfileLibraryEntry."""
    
    def test_entry_creation(self) -> None:
        """Test creating library entry."""
        entry = ProfileLibraryEntry(
            name="test",
            level=ProfileLevel.BASELINE,
            description="Test profile"
        )
        assert entry.name == "test"
        assert entry.level == ProfileLevel.BASELINE
    
    def test_add_rule(self) -> None:
        """Test adding rule."""
        entry = ProfileLibraryEntry(
            name="test",
            level=ProfileLevel.BASELINE
        )
        entry.add_rule("CORE-008")
        assert "CORE-008" in entry.rule_ids
    
    def test_add_tag(self) -> None:
        """Test adding tag."""
        entry = ProfileLibraryEntry(
            name="test",
            level=ProfileLevel.BASELINE
        )
        entry.add_tag("enforcement")
        assert "enforcement" in entry.tags


class TestProfileLibrary:
    """Tests for ProfileLibrary."""
    
    @pytest.fixture
    def library(self) -> ProfileLibrary:
        """Create library fixture."""
        return ProfileLibrary()
    
    def test_library_initialization(self, library: ProfileLibrary) -> None:
        """Test library initializes with standard profiles."""
        assert library.profile_count() >= 3
        assert library.has_profile("strict")
        assert library.has_profile("baseline")
        assert library.has_profile("permissive")
    
    def test_get_strict_profile(self, library: ProfileLibrary) -> None:
        """Test getting strict profile."""
        profile = library.get_profile("strict")
        assert profile is not None
        assert profile.level == ProfileLevel.STRICT
        assert len(profile.rule_ids) > 0
    
    def test_get_baseline_profile(self, library: ProfileLibrary) -> None:
        """Test getting baseline profile."""
        profile = library.get_profile("baseline")
        assert profile is not None
        assert profile.level == ProfileLevel.BASELINE
    
    def test_get_permissive_profile(self, library: ProfileLibrary) -> None:
        """Test getting permissive profile."""
        profile = library.get_profile("permissive")
        assert profile is not None
        assert profile.level == ProfileLevel.PERMISSIVE
    
    def test_register_custom_profile(self, library: ProfileLibrary) -> None:
        """Test registering custom profile."""
        library.register_profile(
            name="custom_test",
            level=ProfileLevel.CUSTOM,
            rule_ids={"CORE-008", "CORE-011"},
            description="Custom test profile"
        )
        assert library.has_profile("custom_test")
        profile = library.get_profile("custom_test")
        assert profile is not None
        assert len(profile.rule_ids) == 2
    
    def test_list_profiles(self, library: ProfileLibrary) -> None:
        """Test listing profiles."""
        profiles = library.list_profiles()
        assert len(profiles) >= 3
        assert "strict" in profiles
        assert "baseline" in profiles
        assert "permissive" in profiles
    
    def test_search_by_level(self, library: ProfileLibrary) -> None:
        """Test searching by level."""
        strict_profiles = library.search_by_level(ProfileLevel.STRICT)
        assert len(strict_profiles) >= 1
        assert "strict" in strict_profiles
    
    def test_search_by_tag(self, library: ProfileLibrary) -> None:
        """Test searching by tag."""
        enforcement = library.search_by_tag("enforcement")
        assert len(enforcement) >= 1
        assert "strict" in enforcement
        assert "baseline" in enforcement
    
    def test_search_by_rule(self, library: ProfileLibrary) -> None:
        """Test searching by rule."""
        profiles = library.search_by_rule("CORE-008")
        assert len(profiles) >= 2
        assert "strict" in profiles
        assert "baseline" in profiles
    
    def test_profile_not_found(self, library: ProfileLibrary) -> None:
        """Test getting non-existent profile."""
        profile = library.get_profile("non_existent")
        assert profile is None
    
    def test_rule_count(self, library: ProfileLibrary) -> None:
        """Test getting rule count."""
        strict_count = library.get_rule_count("strict")
        baseline_count = library.get_rule_count("baseline")
        assert strict_count > baseline_count
    
    def test_get_all_rules(self, library: ProfileLibrary) -> None:
        """Test getting all unique rules."""
        all_rules = library.get_all_rules()
        assert len(all_rules) > 0
        assert "CORE-008" in all_rules
    
    def test_strict_vs_baseline(self, library: ProfileLibrary) -> None:
        """Test strict profile has more rules than baseline."""
        strict = library.get_profile("strict")
        baseline = library.get_profile("baseline")
        assert len(strict.rule_ids) > len(baseline.rule_ids)
    
    def test_baseline_vs_permissive(self, library: ProfileLibrary) -> None:
        """Test baseline has more rules than permissive."""
        baseline = library.get_profile("baseline")
        permissive = library.get_profile("permissive")
        assert len(baseline.rule_ids) > len(permissive.rule_ids)
    
    def test_register_multiple_custom(self, library: ProfileLibrary) -> None:
        """Test registering multiple custom profiles."""
        library.register_profile(
            name="custom1",
            level=ProfileLevel.CUSTOM,
            rule_ids={"CORE-008"}
        )
        library.register_profile(
            name="custom2",
            level=ProfileLevel.CUSTOM,
            rule_ids={"CORE-011"}
        )
        custom_profiles = library.search_by_level(ProfileLevel.CUSTOM)
        assert len(custom_profiles) >= 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
