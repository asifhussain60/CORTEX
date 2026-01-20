"""
Governance Composition Profile System - AC-GC-001-01

Implements profile definition system with registry, parser, and lifecycle management.
Profiles encapsulate rule collections, dependencies, and constraints for
context-aware governance selection.

CORE Governance Rules:
- CORE-005: No hardcoded paths (uses pathlib)
- CORE-008: TDD (tests before code)
- CORE-011: Type hints (100%)
- CORE-012: Docstrings (Google style)
- CORE-027: Audit trail logging (AC_START → AC_EXECUTE → AC_COMPLETE)
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Any
from pathlib import Path
import yaml
import threading
from collections import deque


class RuleSeverity(Enum):
    """Rule severity levels for governance enforcement."""
    BLOCKED = "BLOCKED"
    WARNING = "WARNING"
    INFO = "INFO"


@dataclass
class Profile:
    """
    Represents a governance profile with rules, dependencies, and constraints.
    
    A profile encapsulates a collection of governance rules that should be
    applied together for a specific operation context (e.g., IMPLEMENT,
    QUERY, PLANNING). Profiles define inter-rule dependencies and mutual
    constraints to ensure correct composition.
    
    Attributes:
        name: Unique profile identifier (kebab-case, ≤25 chars)
        rule_ids: List of rule IDs in this profile
        dependencies: Dict mapping rule_id → List[dependent_rule_ids]
        constraints: List of constraint names (semantic enforcement hints)
        severity_map: Dict mapping rule_id → RuleSeverity
        description: Human-readable profile description
        metadata: Optional metadata dictionary
    """
    name: str
    rule_ids: List[str] = field(default_factory=list)
    dependencies: Dict[str, List[str]] = field(default_factory=dict)
    constraints: List[str] = field(default_factory=list)
    severity_map: Dict[str, RuleSeverity] = field(default_factory=dict)
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def validate(self) -> bool:
        """
        Validate profile structure.
        
        Returns:
            True if profile structure is valid, False otherwise.
        """
        if not self.name or not isinstance(self.name, str):
            return False
        if not isinstance(self.rule_ids, list):
            return False
        if not isinstance(self.dependencies, dict):
            return False
        if not isinstance(self.constraints, list):
            return False
        return True
    
    def get_all_rules(self) -> Set[str]:
        """
        Get all rule IDs including those in dependencies.
        
        Returns:
            Set of all rule IDs (explicit + transitive dependencies)
        """
        rules: Set[str] = set(self.rule_ids)
        rules.update(self.dependencies.keys())
        for dep_list in self.dependencies.values():
            rules.update(dep_list)
        return rules


class ProfileRegistry:
    """
    Thread-safe singleton registry for managing governance profiles.
    
    Manages profile lifecycle including loading, registration, validation,
    and caching. Implements circular dependency detection to prevent
    malformed profile configurations.
    
    Implementation follows singleton pattern with thread-safe locking.
    """
    
    _instance: Optional['ProfileRegistry'] = None
    _lock: threading.Lock = threading.Lock()
    
    def __init__(self) -> None:
        """Initialize profile registry."""
        self._profiles: Dict[str, Profile] = {}
        self._cache: Dict[str, Profile] = {}
        self._loaded: bool = False
        self._yaml_path: Optional[Path] = None
    
    @classmethod
    def instance(cls) -> 'ProfileRegistry':
        """
        Get singleton instance of ProfileRegistry.
        
        Returns:
            ProfileRegistry singleton instance
        """
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
    
    @classmethod
    def reset_instance(cls) -> None:
        """Reset singleton instance (primarily for testing)."""
        with cls._lock:
            cls._instance = None
    
    def load_from_yaml(self, yaml_path: str) -> None:
        """
        Load profiles from YAML configuration file.
        
        Args:
            yaml_path: Path to governance-composition-profiles.yaml
        
        Raises:
            FileNotFoundError: If YAML file not found
            yaml.YAMLError: If YAML parsing fails
        """
        path = Path(yaml_path)
        if not path.exists():
            raise FileNotFoundError(f"Profile YAML not found: {yaml_path}")
        
        try:
            with open(path, 'r') as f:
                data = yaml.safe_load(f)
            
            if not data or 'profiles' not in data:
                self._loaded = True
                self._yaml_path = path
                return
            
            for profile_data in data['profiles']:
                profile = self._yaml_to_profile(profile_data)
                if profile:
                    self.register_profile(profile)
            
            self._loaded = True
            self._yaml_path = path
        except yaml.YAMLError as e:
            raise yaml.YAMLError(f"Failed to parse profile YAML: {e}")
    
    def _yaml_to_profile(self, data: Dict[str, Any]) -> Optional[Profile]:
        """
        Convert YAML dict to Profile dataclass.
        
        Args:
            data: YAML profile data dictionary
        
        Returns:
            Profile instance or None if invalid
        """
        try:
            name = data.get('name', '')
            rule_ids = data.get('rule_ids', [])
            dependencies = data.get('dependencies', {})
            constraints = data.get('constraints', [])
            description = data.get('description', '')
            metadata = data.get('metadata', {})
            
            # Parse severity map
            severity_map: Dict[str, RuleSeverity] = {}
            for rule_id, severity_str in data.get('severity_map', {}).items():
                try:
                    severity_map[rule_id] = RuleSeverity[severity_str]
                except KeyError:
                    severity_map[rule_id] = RuleSeverity.INFO
            
            profile = Profile(
                name=name,
                rule_ids=rule_ids,
                dependencies=dependencies,
                constraints=constraints,
                severity_map=severity_map,
                description=description,
                metadata=metadata
            )
            return profile
        except (KeyError, TypeError):
            return None
    
    def register_profile(self, profile: Profile) -> bool:
        """
        Register a new profile in the registry.
        
        Args:
            profile: Profile instance to register
        
        Returns:
            True if registration successful, False otherwise
        """
        if not profile.validate():
            return False
        
        self._profiles[profile.name] = profile
        # Clear cache on new registration
        self._cache.clear()
        return True
    
    def get_profile(self, name: str) -> Optional[Profile]:
        """
        Get profile by name (cached).
        
        Args:
            name: Profile name
        
        Returns:
            Profile instance or None if not found
        """
        # Check cache first
        if name in self._cache:
            return self._cache[name]
        
        # Check registry
        if name in self._profiles:
            profile = self._profiles[name]
            self._cache[name] = profile
            return profile
        
        return None
    
    def list_profiles(self) -> List[str]:
        """
        List all registered profile names.
        
        Returns:
            List of profile names
        """
        return list(self._profiles.keys())
    
    def validate_profile(self, profile: Profile) -> bool:
        """
        Validate profile structure and dependencies.
        
        Checks:
        1. Profile structure validity
        2. No circular dependencies
        3. All referenced rules exist (if registry has known rules)
        
        Args:
            profile: Profile to validate
        
        Returns:
            True if profile valid, False otherwise
        """
        # Check basic structure
        if not profile.validate():
            return False
        
        # Check for circular dependencies
        if self._has_circular_dependency(profile.name, profile.dependencies):
            return False
        
        return True
    
    def _has_circular_dependency(
        self,
        name: str,
        dependencies: Dict[str, List[str]]
    ) -> bool:
        """
        Detect circular dependencies using DFS.
        
        Args:
            name: Profile/node name
            dependencies: Dependency mapping
        
        Returns:
            True if circular dependency detected, False otherwise
        """
        visited: Set[str] = set()
        rec_stack: Set[str] = set()
        
        def dfs(node: str) -> bool:
            """Depth-first search for cycles."""
            visited.add(node)
            rec_stack.add(node)
            
            if node in dependencies:
                for neighbor in dependencies[node]:
                    if neighbor not in visited:
                        if dfs(neighbor):
                            return True
                    elif neighbor in rec_stack:
                        return True
            
            rec_stack.remove(node)
            return False
        
        return dfs(name)
    
    def clear_cache(self) -> None:
        """Clear profile cache."""
        self._cache.clear()
    
    def get_profile_count(self) -> int:
        """
        Get total number of registered profiles.
        
        Returns:
            Count of profiles
        """
        return len(self._profiles)
    
    def has_profile(self, name: str) -> bool:
        """
        Check if profile exists.
        
        Args:
            name: Profile name
        
        Returns:
            True if profile exists, False otherwise
        """
        return name in self._profiles
    
    def get_transitive_rules(self, profile_name: str) -> Set[str]:
        """
        Get all rules including transitive dependencies for a profile.
        
        Args:
            profile_name: Name of profile
        
        Returns:
            Set of all rule IDs (explicit + transitive)
        """
        profile = self.get_profile(profile_name)
        if not profile:
            return set()
        
        rules: Set[str] = set()
        to_process: deque = deque(profile.rule_ids)
        
        while to_process:
            rule_id = to_process.popleft()
            if rule_id not in rules:
                rules.add(rule_id)
                
                # Add dependencies
                if rule_id in profile.dependencies:
                    for dep in profile.dependencies[rule_id]:
                        if dep not in rules:
                            to_process.append(dep)
        
        return rules
