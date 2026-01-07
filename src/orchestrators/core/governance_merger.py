"""
Governance Merger - 4-Category Governance System.

This module implements the intelligent merger that combines rules from:
1. CORTEX Tier 0 (Core brain protection - SKULL rules)
2. Business Tier 0 (Company compliance rules)
3. Company Best Practices (Engineering standards)
4. Knowledge Best Practices (Learned patterns)

Features:
- 4-tier rule loading with precedence
- Conflict detection and resolution
- Unified instruction set generation
- Rule caching for performance (<50ms merge target)

Author: CORTEX feat03-governance Phase 2-3
Created: 2026-01-08
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Any
import yaml
import hashlib
import json
import time

from src.orchestrators.audit_logger import (
    EnterpriseAuditLogger,
    AuditLevel,
    AuditCategory,
)


class Precedence(Enum):
    """Rule precedence levels."""

    HIGHEST = 0  # Tier 0 - CORTEX Core
    HIGH = 1  # Tier 1 - Business
    MEDIUM = 2  # Tier 2 - Company
    LOW = 3  # Tier 3 - Knowledge


class Severity(Enum):
    """Rule severity levels."""

    BLOCKED = "blocked"
    WARNING = "warning"
    INFO = "info"


@dataclass
class GovernanceRule:
    """Individual governance rule."""

    rule_id: str
    category: str
    severity: str
    name: str
    description: str = ""
    governance_tier: int = 0
    precedence: str = "HIGHEST"
    enforcement: Optional[Dict[str, Any]] = None
    validation: Optional[List[str]] = None
    implementation: Optional[Dict[str, Any]] = None
    examples: Optional[Dict[str, List[str]]] = None
    rationale: Optional[str] = None

    def __post_init__(self):
        """Validate and normalize fields."""
        if isinstance(self.precedence, str):
            # Map precedence string to tier
            precedence_map = {
                "HIGHEST": 0,
                "HIGH": 1,
                "MEDIUM": 2,
                "LOW": 3,
            }
            if self.precedence in precedence_map:
                self.governance_tier = precedence_map[self.precedence]

    def to_dict(self) -> Dict[str, Any]:
        """Convert rule to dictionary."""
        return {
            "rule_id": self.rule_id,
            "category": self.category,
            "severity": self.severity,
            "name": self.name,
            "description": self.description,
            "governance_tier": self.governance_tier,
            "precedence": self.precedence,
            "enforcement": self.enforcement,
            "validation": self.validation,
            "implementation": self.implementation,
            "examples": self.examples,
            "rationale": self.rationale,
        }


@dataclass
class GovernanceConflict:
    """Represents a conflict between governance rules."""

    category: str
    conflict_type: str
    description: str
    rules: List[GovernanceRule]
    resolution_strategy: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert conflict to dictionary."""
        return {
            "category": self.category,
            "conflict_type": self.conflict_type,
            "description": self.description,
            "rules": [r.to_dict() for r in self.rules],
            "resolution_strategy": self.resolution_strategy,
        }


@dataclass
class UnifiedInstructionSet:
    """Unified instruction set from merged governance rules."""

    rules: List[GovernanceRule]
    version: str = "1.0.0"
    generated_at: Optional[datetime] = None
    tier_count: int = 0
    rule_count: int = 0
    conflicts_resolved: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Calculate metadata."""
        if self.generated_at is None:
            self.generated_at = datetime.now()
        self.rule_count = len(self.rules)
        self.tier_count = len({r.governance_tier for r in self.rules})

    def to_dict(self) -> Dict[str, Any]:
        """Convert unified set to dictionary."""
        return {
            "version": self.version,
            "generated_at": self.generated_at.isoformat() if self.generated_at else None,
            "tier_count": self.tier_count,
            "rule_count": self.rule_count,
            "conflicts_resolved": self.conflicts_resolved,
            "metadata": self.metadata,
            "rules": [r.to_dict() for r in self.rules],
        }

    def to_yaml(self) -> str:
        """Convert unified set to YAML string."""
        return yaml.dump(self.to_dict(), default_flow_style=False, sort_keys=False)


class GovernanceMerger:
    """
    Merges governance rules from all 4 categories.

    This class handles:
    - Loading rules from all tiers (0-3)
    - Detecting conflicts between rules
    - Resolving conflicts using tier precedence
    - Generating unified instruction set
    - Caching rules for performance (<50ms merge target)
    """

    def __init__(
        self,
        governance_root: Optional[Path] = None,
        audit_logger: Optional[EnterpriseAuditLogger] = None,
        enable_cache: bool = True,
    ):
        """
        Initialize governance merger.

        Args:
            governance_root: Root directory for governance files
            audit_logger: Optional audit logger instance
            enable_cache: Enable rule caching for performance
        """
        if governance_root is None:
            # Default to cortex-brain in project root
            # Navigate up from this file to project root
            governance_root = Path(__file__).parent.parent.parent.parent / "cortex-brain"

        self.governance_root = Path(governance_root)
        self.audit_logger = audit_logger or EnterpriseAuditLogger()
        self.enable_cache = enable_cache

        self.core_rules: List[GovernanceRule] = []
        self.business_rules: List[GovernanceRule] = []
        self.company_rules: List[GovernanceRule] = []
        self.knowledge_rules: List[GovernanceRule] = []

        self.all_rules: List[GovernanceRule] = []
        self.conflicts: List[GovernanceConflict] = []

        # Cache structures
        self._rule_cache: Dict[str, List[GovernanceRule]] = {}
        self._file_hashes: Dict[str, str] = {}
        self._cache_timestamps: Dict[str, float] = {}
        self._unified_cache: Optional[UnifiedInstructionSet] = None
        self._cache_hit_count: int = 0
        self._cache_miss_count: int = 0

    def _compute_file_hash(self, file_path: Path) -> str:
        """
        Compute SHA256 hash of file contents.

        Args:
            file_path: Path to file

        Returns:
            Hex digest of file hash
        """
        if not file_path.exists():
            return ""

        hasher = hashlib.sha256()
        with open(file_path, "rb") as f:
            hasher.update(f.read())
        return hasher.hexdigest()

    def _is_cache_valid(self, cache_key: str, file_path: Path) -> bool:
        """
        Check if cached rules are still valid.

        Args:
            cache_key: Cache key for rules
            file_path: Path to governance file

        Returns:
            True if cache is valid, False otherwise
        """
        if not self.enable_cache:
            return False

        if cache_key not in self._rule_cache:
            return False

        if not file_path.exists():
            return False

        # Check file hash
        current_hash = self._compute_file_hash(file_path)
        cached_hash = self._file_hashes.get(str(file_path), "")

        if current_hash != cached_hash:
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.PERFORMANCE,
                component="governance_merger",
                operation="cache_invalidation",
                message=f"Cache invalidated for {cache_key}: file changed",
                correlation_id="FEAT03-P3-T3.2",
            )
            return False

        # Check timestamp (expire after 5 minutes)
        cache_age = time.time() - self._cache_timestamps.get(cache_key, 0)
        if cache_age > 300:  # 5 minutes
            self.audit_logger.log(
                level=AuditLevel.INFO,
                category=AuditCategory.PERFORMANCE,
                component="governance_merger",
                operation="cache_expiration",
                message=f"Cache expired for {cache_key}: {cache_age:.1f}s old",
                correlation_id="FEAT03-P3-T3.2",
            )
            return False

        return True

    def _cache_rules(self, cache_key: str, rules: List[GovernanceRule], file_path: Path):
        """
        Cache loaded rules.

        Args:
            cache_key: Cache key for rules
            rules: List of rules to cache
            file_path: Path to governance file
        """
        if not self.enable_cache:
            return

        self._rule_cache[cache_key] = rules
        self._file_hashes[str(file_path)] = self._compute_file_hash(file_path)
        self._cache_timestamps[cache_key] = time.time()

        self.audit_logger.log(
            level=AuditLevel.TRACE,
            category=AuditCategory.PERFORMANCE,
            component="governance_merger",
            operation="cache_store",
            message=f"Cached {len(rules)} rules for {cache_key}",
            correlation_id="FEAT03-P3-T3.1",
        )

    def _get_cached_rules(self, cache_key: str, file_path: Path) -> Optional[List[GovernanceRule]]:
        """
        Get rules from cache if valid.

        Args:
            cache_key: Cache key for rules
            file_path: Path to governance file

        Returns:
            Cached rules or None if cache invalid
        """
        if not self.enable_cache:
            return None
            
        if self._is_cache_valid(cache_key, file_path):
            self._cache_hit_count += 1
            self.audit_logger.log(
                level=AuditLevel.TRACE,
                category=AuditCategory.PERFORMANCE,
                component="governance_merger",
                operation="cache_hit",
                message=f"Cache hit for {cache_key}",
                correlation_id="FEAT03-P3-T3.1",
            )
            return self._rule_cache[cache_key]

        self._cache_miss_count += 1
        return None

    def clear_cache(self):
        """Clear all cached rules."""
        self._rule_cache.clear()
        self._file_hashes.clear()
        self._cache_timestamps.clear()
        self._unified_cache = None

        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.PERFORMANCE,
            component="governance_merger",
            operation="cache_clear",
            message="All caches cleared",
            correlation_id="FEAT03-P3-T3.2",
        )

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.

        Returns:
            Dictionary with cache stats
        """
        total_requests = self._cache_hit_count + self._cache_miss_count
        hit_rate = (
            self._cache_hit_count / total_requests if total_requests > 0 else 0.0
        )

        return {
            "enabled": self.enable_cache,
            "hit_count": self._cache_hit_count,
            "miss_count": self._cache_miss_count,
            "hit_rate": hit_rate,
            "cached_keys": list(self._rule_cache.keys()),
            "cache_size": len(self._rule_cache),
        }

    def load_core_rules(self) -> List[GovernanceRule]:
        """
        Load CORTEX Tier 0 core rules (SKULL rules).

        Returns:
            List of core governance rules
        """
        core_path = self.governance_root / "tier0" / "governance" / "core-rules.yaml"

        # Check cache first
        cached_rules = self._get_cached_rules("core_rules", core_path)
        if cached_rules is not None:
            self.core_rules = cached_rules
            return cached_rules

        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.EXECUTION,
            component="governance_merger",
            operation="load_core_rules",
            message="Loading Tier 0 core rules",
            correlation_id="FEAT03-P2-T2.2",
        )

        if not core_path.exists():
            self.audit_logger.log(
                level=AuditLevel.WARNING,
                category=AuditCategory.EXECUTION,
                component="governance_merger",
                operation="load_core_rules",
                message=f"Core rules file not found: {core_path}",
                correlation_id="FEAT03-P2-T2.2",
            )
            return []

        with open(core_path, "r") as f:
            data = yaml.safe_load(f)

        rules = []
        for rule_data in data.get("rules", []):
            rule = GovernanceRule(
                rule_id=rule_data.get("rule_id", ""),
                category=rule_data.get("category", ""),
                severity=rule_data.get("severity", ""),
                name=rule_data.get("name", ""),
                description=rule_data.get("description", ""),
                governance_tier=0,
                precedence="HIGHEST",
                enforcement=rule_data.get("enforcement"),
                validation=rule_data.get("validation"),
                implementation=rule_data.get("implementation"),
                examples=rule_data.get("examples"),
                rationale=rule_data.get("rationale"),
            )
            rules.append(rule)

        # Cache the loaded rules
        self._cache_rules("core_rules", rules, core_path)

        self.core_rules = rules
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.EXECUTION,
            component="governance_merger",
            operation="load_core_rules",
            message=f"Loaded {len(rules)} core rules",
            correlation_id="FEAT03-P2-T2.2",
        )
        return rules

    def load_business_rules(self) -> List[GovernanceRule]:
        """
        Load Business Tier 1 rules (company compliance) with caching.

        Returns:
            List of business governance rules
        """
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.EXECUTION,
            component="governance_merger",
            operation="load_business_rules",
            message="Loading Tier 1 business rules",
            correlation_id="FEAT03-P2-T2.2",
        )

        business_path = (
            self.governance_root / "tier1" / "governance" / "business-rules.yaml"
        )
        if not business_path.exists():
            return []

        # Check cache first
        if self.enable_cache:
            cached_rules = self._get_cached_rules("business_rules", business_path)
            if cached_rules is not None:
                self.business_rules = cached_rules
                return cached_rules

        # Load from file
        with open(business_path, "r") as f:
            data = yaml.safe_load(f)

        rules = []
        for rule_data in data.get("rules", []):
            rule = GovernanceRule(
                rule_id=rule_data.get("rule_id", ""),
                category=rule_data.get("category", ""),
                severity=rule_data.get("severity", ""),
                name=rule_data.get("name", ""),
                description=rule_data.get("description", ""),
                governance_tier=1,
                precedence="HIGH",
            )
            rules.append(rule)

        self.business_rules = rules

        # Cache the loaded rules
        if self.enable_cache:
            self._cache_rules("business_rules", rules, business_path)

        return rules

    def load_company_practices(self) -> List[GovernanceRule]:
        """
        Load Company Best Practices (engineering standards) with caching.

        Returns:
            List of company practice rules
        """
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.EXECUTION,
            component="governance_merger",
            operation="load_company_practices",
            message="Loading Tier 2 company practices",
            correlation_id="FEAT03-P2-T2.2",
        )

        practices_path = (
            self.governance_root / "tier2" / "governance" / "company-practices.yaml"
        )
        if not practices_path.exists():
            return []

        # Check cache first
        if self.enable_cache:
            cached_rules = self._get_cached_rules("company_practices", practices_path)
            if cached_rules is not None:
                self.company_rules = cached_rules
                return cached_rules

        # Load from file
        with open(practices_path, "r") as f:
            data = yaml.safe_load(f)

        rules = []
        for rule_data in data.get("rules", []):
            rule = GovernanceRule(
                rule_id=rule_data.get("rule_id", ""),
                category=rule_data.get("category", ""),
                severity=rule_data.get("severity", ""),
                name=rule_data.get("name", ""),
                description=rule_data.get("description", ""),
                governance_tier=2,
                precedence="MEDIUM",
            )
            rules.append(rule)

        self.company_rules = rules

        # Cache the loaded rules
        if self.enable_cache:
            self._cache_rules("company_practices", rules, practices_path)

        return rules

    def load_knowledge_practices(self) -> List[GovernanceRule]:
        """
        Load Knowledge Best Practices (learned patterns) with caching.

        Returns:
            List of knowledge practice rules
        """
        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.EXECUTION,
            component="governance_merger",
            operation="load_knowledge_practices",
            message="Loading Tier 3 knowledge practices",
            correlation_id="FEAT03-P2-T2.2",
        )

        knowledge_path = (
            self.governance_root / "tier3" / "governance" / "knowledge-practices.yaml"
        )
        if not knowledge_path.exists():
            return []

        # Check cache first
        if self.enable_cache:
            cached_rules = self._get_cached_rules("knowledge_practices", knowledge_path)
            if cached_rules is not None:
                self.knowledge_rules = cached_rules
                return cached_rules

        # Load from file
        with open(knowledge_path, "r") as f:
            data = yaml.safe_load(f)

        rules = []
        for rule_data in data.get("rules", []):
            rule = GovernanceRule(
                rule_id=rule_data.get("rule_id", ""),
                category=rule_data.get("category", ""),
                severity=rule_data.get("severity", ""),
                name=rule_data.get("name", ""),
                description=rule_data.get("description", ""),
                governance_tier=3,
                precedence="LOW",
            )
            rules.append(rule)

        self.knowledge_rules = rules

        # Cache the loaded rules
        if self.enable_cache:
            self._cache_rules("knowledge_practices", rules, knowledge_path)

        return rules

    def load_all_rules(self) -> List[GovernanceRule]:
        """
        Load rules from all 4 categories.

        Returns:
            Combined list of all governance rules
        """
        self.load_core_rules()
        self.load_business_rules()
        self.load_company_practices()
        self.load_knowledge_practices()

        self.all_rules = (
            self.core_rules
            + self.business_rules
            + self.company_rules
            + self.knowledge_rules
        )

        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.EXECUTION,
            component="governance_merger",
            operation="load_all_rules",
            message=f"Loaded {len(self.all_rules)} total rules from 4 tiers",
            correlation_id="FEAT03-P2-T2.2",
        )

        return self.all_rules

    def detect_conflicts(self) -> List[GovernanceConflict]:
        """
        Detect conflicts between governance rules.

        Returns:
            List of detected conflicts
        """
        if not self.all_rules:
            self.load_all_rules()

        conflicts = []

        # Group rules by category
        by_category: Dict[str, List[GovernanceRule]] = {}
        for rule in self.all_rules:
            if rule.category not in by_category:
                by_category[rule.category] = []
            by_category[rule.category].append(rule)

        # Check for conflicts within each category
        for category, rules in by_category.items():
            if len(rules) > 1:
                # Check for same rule_id with different properties
                by_id: Dict[str, List[GovernanceRule]] = {}
                for rule in rules:
                    if rule.rule_id not in by_id:
                        by_id[rule.rule_id] = []
                    by_id[rule.rule_id].append(rule)

                for rule_id, rule_list in by_id.items():
                    if len(rule_list) > 1:
                        # Severity mismatch?
                        severities = {r.severity for r in rule_list}
                        if len(severities) > 1:
                            conflict = GovernanceConflict(
                                category=category,
                                conflict_type="severity_mismatch",
                                description=f"Rule {rule_id} has conflicting severities: {severities}",
                                rules=rule_list,
                            )
                            conflicts.append(conflict)

                # Check for conflicting requirements in same category
                if len(rules) > 1 and any("TDD" in r.name for r in rules):
                    tiers = {r.governance_tier for r in rules if "TDD" in r.name}
                    if len(tiers) > 1:
                        tdd_rules = [r for r in rules if "TDD" in r.name]
                        conflict = GovernanceConflict(
                            category=category,
                            conflict_type="requirement_conflict",
                            description=f"TDD requirements conflict across tiers",
                            rules=tdd_rules,
                        )
                        conflicts.append(conflict)

        self.conflicts = conflicts
        return conflicts

    def resolve_conflicts(self) -> List[GovernanceRule]:
        """
        Resolve conflicts using tier precedence strategy.

        Tier 0 (CORTEX Core) always wins.
        If same tier, higher severity wins.

        Returns:
            List of resolved rules (conflicts removed)
        """
        if not self.all_rules:
            self.load_all_rules()

        if not self.conflicts:
            self.detect_conflicts()

        # Start with all rules
        resolved = list(self.all_rules)

        # For each conflict, apply resolution strategy
        for conflict in self.conflicts:
            # Tier precedence: lowest tier number wins
            winner = min(conflict.rules, key=lambda r: r.governance_tier)

            # Remove losers from resolved list
            for rule in conflict.rules:
                if rule != winner and rule in resolved:
                    resolved.remove(rule)

        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.EXECUTION,
            component="governance_merger",
            operation="resolve_conflicts",
            message=f"Resolved {len(self.conflicts)} conflicts, {len(resolved)} rules remain",
            correlation_id="FEAT03-P2-T2.2",
        )

        return resolved

    def generate_unified_instruction_set(self) -> UnifiedInstructionSet:
        """
        Generate unified instruction set from merged rules.

        Returns:
            UnifiedInstructionSet with all resolved rules
        """
        if not self.all_rules:
            self.load_all_rules()

        # Detect and resolve conflicts
        self.detect_conflicts()
        resolved_rules = self.resolve_conflicts()

        # Sort by tier (highest precedence first)
        resolved_rules.sort(key=lambda r: r.governance_tier)

        unified_set = UnifiedInstructionSet(
            rules=resolved_rules,
            version="1.0.0",
            generated_at=datetime.now(),
            conflicts_resolved=len(self.conflicts),
            metadata={
                "core_rules": len(self.core_rules),
                "business_rules": len(self.business_rules),
                "company_rules": len(self.company_rules),
                "knowledge_rules": len(self.knowledge_rules),
            },
        )

        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.EXECUTION,
            component="governance_merger",
            operation="generate_unified_instruction_set",
            message=f"Generated unified instruction set with {len(resolved_rules)} rules",
            correlation_id="FEAT03-P2-T2.2",
        )

        return unified_set

    def merge(self) -> UnifiedInstructionSet:
        """
        Execute full merge workflow.

        This is the main entry point that:
        1. Loads all rules (with caching)
        2. Detects conflicts
        3. Resolves conflicts
        4. Generates unified instruction set (cached)

        Returns:
            UnifiedInstructionSet with all merged rules
        """
        start_time = time.time()

        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.EXECUTION,
            component="governance_merger",
            operation="merge",
            message="Starting governance merge workflow",
            correlation_id="FEAT03-P2-T2.2",
        )

        # Check if we have cached unified set
        if self._unified_cache is not None and self.enable_cache:
            # Verify all tier file caches are still valid
            tier_paths = [
                ("core_rules", self.governance_root / "tier0" / "governance" / "core-rules.yaml"),
                ("business_rules", self.governance_root / "tier1" / "governance" / "business-rules.yaml"),
                ("company_practices", self.governance_root / "tier2" / "governance" / "company-practices.yaml"),
                ("knowledge_practices", self.governance_root / "tier3" / "governance" / "knowledge-practices.yaml"),
            ]
            
            all_valid = True
            for cache_key, file_path in tier_paths:
                # Only validate if file exists
                if file_path.exists() and not self._is_cache_valid(cache_key, file_path):
                    all_valid = False
                    break
            
            if all_valid:
                elapsed = (time.time() - start_time) * 1000  # ms
                self._cache_hit_count += 1  # Count unified merge cache hit
                self.audit_logger.log(
                    level=AuditLevel.INFO,
                    category=AuditCategory.PERFORMANCE,
                    component="governance_merger",
                    operation="merge",
                    message=f"Merge complete (cached): {self._unified_cache.rule_count} rules, {elapsed:.2f}ms",
                    correlation_id="FEAT03-P3-T3.3",
                )
                return self._unified_cache

        unified_set = self.generate_unified_instruction_set()

        # Cache the unified set
        if self.enable_cache:
            self._unified_cache = unified_set

        elapsed = (time.time() - start_time) * 1000  # Convert to ms

        self.audit_logger.log(
            level=AuditLevel.INFO,
            category=AuditCategory.EXECUTION,
            component="governance_merger",
            operation="merge",
            message=f"Merge complete: {unified_set.rule_count} rules, {unified_set.tier_count} tiers, {elapsed:.2f}ms",
            correlation_id="FEAT03-P3-T3.3",
        )

        return unified_set
