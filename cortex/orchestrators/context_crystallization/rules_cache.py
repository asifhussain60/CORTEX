# AC_START: AC-PHASE49-S1-rules_cache
# Description: Rules cache implementation with tier resolution
# Author: Asif Hussain
# Date: 2026-02-08
# Phase: 49, Stage 1, Component: Rules Cache

"""
Rules Cache - Tier-resolved CORTEX rules with caching.

Implements precedence: company_rules > tier1_rules > tier0_rules
Caches rules with 5-minute TTL for performance.
"""

import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class Rule:
    """Single CORTEX rule."""

    id: str
    name: str
    priority: str  # P0, P1, P2
    enforcement_level: str  # BLOCKED, WARNING, PRINCIPLE
    description: str
    scope: str  # Which orchestrators/components


@dataclass
class RulesCache:
    """Cached rules with tier resolution and TTL."""

    tier0_rules: List[Rule] = field(default_factory=list)
    tier1_rules: List[Rule] = field(default_factory=list)
    company_rules: List[Rule] = field(default_factory=list)

    # Merged view (company > tier1 > tier0)
    merged_rules: Dict[str, Rule] = field(default_factory=dict)

    # Cache metadata
    loaded_at: Optional[float] = None
    ttl_seconds: int = 300  # 5 minutes
    cache_hit_count: int = 0
    cache_miss_count: int = 0

    def load(self) -> "RulesCache":
        """Load rules from tier0 → tier1 → company with precedence.

        Returns:
            Self (for chaining)
        """
        logger.info("Loading rules from tiers (tier0 → tier1 → company)")

        # Load tier0 (CORTEX defaults)
        self.tier0_rules = self._load_tier(
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/tier0")
        )
        logger.debug(f"Loaded {len(self.tier0_rules)} tier0 rules")

        # Load tier1 (CORTEX overrides)
        self.tier1_rules = self._load_tier(
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/tier1")
        )
        logger.debug(f"Loaded {len(self.tier1_rules)} tier1 rules")

        # Load company (company-specific rules)
        self.company_rules = self._load_tier(
            Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-registry/company")
        )
        logger.debug(f"Loaded {len(self.company_rules)} company rules")

        # Merge with precedence
        self._merge_rules()
        self.loaded_at = time.time()

        logger.info(
            f"Rules loaded successfully: {len(self.merged_rules)} rules merged "
            f"(tier0={len(self.tier0_rules)}, tier1={len(self.tier1_rules)}, "
            f"company={len(self.company_rules)})"
        )

        return self

    def _load_tier(self, tier_path: Path) -> List[Rule]:
        """Load rules from a tier directory.

        Args:
            tier_path: Path to tier directory

        Returns:
            List of Rule objects
        """
        rules = []

        # For now, return mock rules (actual implementation loads YAML)
        # This is S2 responsibility to refine
        if not tier_path.exists():
            return rules

        # Mock rules for demonstration
        if "tier0" in str(tier_path):
            rules = [
                Rule(
                    id="CORE-008",
                    name="TDD-First",
                    priority="P0",
                    enforcement_level="BLOCKED",
                    description="Tests BEFORE code",
                    scope="All",
                ),
                Rule(
                    id="CORE-002",
                    name="No Markdown Generation",
                    priority="P0",
                    enforcement_level="BLOCKED",
                    description="NO markdown file generation in chat",
                    scope="All",
                ),
            ]

        return rules

    def _merge_rules(self) -> None:
        """Merge rules with company > tier1 > tier0 precedence."""
        self.merged_rules = {}

        # Add tier0 first
        for rule in self.tier0_rules:
            self.merged_rules[rule.id] = rule

        # Override with tier1
        for rule in self.tier1_rules:
            self.merged_rules[rule.id] = rule

        # Override with company
        for rule in self.company_rules:
            self.merged_rules[rule.id] = rule

    def get(self, rule_id: str) -> Optional[Rule]:
        """Get rule by ID (from merged view).

        Args:
            rule_id: Rule ID (e.g., "CORE-008")

        Returns:
            Rule or None
        """
        if not self.is_fresh():
            logger.debug(f"Cache stale ({self.age_seconds():.1f}s > {self.ttl_seconds}s), reloading")
            self.load()

        if rule_id in self.merged_rules:
            self.cache_hit_count += 1
            return self.merged_rules[rule_id]
        else:
            self.cache_miss_count += 1
            return None

    def get_all_by_enforcement(
        self, enforcement_level: str
    ) -> List[Rule]:
        """Get all rules by enforcement level.

        Args:
            enforcement_level: BLOCKED, WARNING, PRINCIPLE

        Returns:
            List of matching rules
        """
        if not self.is_fresh():
            self.load()

        return [
            r for r in self.merged_rules.values()
            if r.enforcement_level == enforcement_level
        ]

    def is_fresh(self) -> bool:
        """Check if cache is still valid (within TTL)."""
        if self.loaded_at is None:
            return False
        return time.time() - self.loaded_at < self.ttl_seconds

    def age_seconds(self) -> float:
        """Get cache age in seconds."""
        if self.loaded_at is None:
            return float("inf")
        return time.time() - self.loaded_at

    def invalidate(self) -> None:
        """Invalidate cache, force reload on next access."""
        self.loaded_at = None
        logger.info("Rules cache invalidated")

    def stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "rules_total": len(self.merged_rules),
            "tier0_count": len(self.tier0_rules),
            "tier1_count": len(self.tier1_rules),
            "company_count": len(self.company_rules),
            "cache_hits": self.cache_hit_count,
            "cache_misses": self.cache_miss_count,
            "hit_rate": (
                self.cache_hit_count / (self.cache_hit_count + self.cache_miss_count)
                if (self.cache_hit_count + self.cache_miss_count) > 0
                else 0
            ),
            "age_seconds": self.age_seconds(),
            "is_fresh": self.is_fresh(),
        }


# AC_COMPLETE: AC-PHASE49-S1-rules_cache ✅
