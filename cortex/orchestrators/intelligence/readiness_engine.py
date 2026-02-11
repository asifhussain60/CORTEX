"""
Readiness Engine - Tech Stack Readiness Scoring Algorithm.

Calculates readiness scores for tech stacks based on 4-factor weighted analysis:
- Best practices coverage (40%)
- TDD framework support (30%)
- Security tooling availability (20%)
- Cross-repo usage frequency (10%)

Phase 34B, Week 2, Increment 3:
- Per-tech-stack score calculation
- Threshold-based action logic (PROCEED, WARNING, LEARN)
- Score caching with TTL
- Knowledge base integration

Author: CORTEX Team
Created: 2026-02-06
Authority: Phase 34B specification
"""

import logging
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, Optional, Tuple

from cortex.orchestrators.intelligence.types import ReadinessScore, TechStack

logger = logging.getLogger(__name__)


@dataclass
class ReadinessComponents:
    """Individual readiness component scores."""

    best_practices: float  # 0.0-1.0
    tdd_support: float  # 0.0-1.0
    security_tooling: float  # 0.0-1.0
    cross_repo_usage: float  # 0.0-1.0

    def to_dict(self) -> Dict[str, float]:
        """Convert to dictionary."""
        return {
            "best_practices": self.best_practices,
            "tdd_support": self.tdd_support,
            "security_tooling": self.security_tooling,
            "cross_repo_usage": self.cross_repo_usage,
        }


@dataclass
class ReadinessAction:
    """Action recommendation based on readiness score."""

    action: str  # PROCEED, PROCEED_WITH_WARNING, TRIGGER_LEARNING
    confidence: float  # 0.0-1.0
    recommendations: list = field(default_factory=list)

    def __str__(self) -> str:
        """String representation."""
        return f"{self.action} (confidence: {self.confidence:.2f})"


class ReadinessEngine:
    """
    Calculates readiness scores for tech stacks.

    Scoring algorithm:
    - Best practices coverage: 40% weight
    - TDD framework support: 30% weight
    - Security tooling: 20% weight
    - Cross-repo usage: 10% weight

    Thresholds:
    - ≥0.7: PROCEED (ready for use)
    - 0.5-0.7: PROCEED_WITH_WARNING (usable but gaps exist)
    - <0.5: TRIGGER_LEARNING (requires knowledge acquisition)

    Example:
        >>> engine = ReadinessEngine()
        >>> tech_stack = TechStack(language="python", frameworks=["django"])
        >>> score = engine.calculate_readiness_score(tech_stack)
        >>> if score.action == "PROCEED":
        ...     print(f"Ready! Score: {score.overall}")
    """

    # Default component weights (must sum to 1.0)
    DEFAULT_WEIGHTS = {
        "best_practices": 0.4,
        "tdd_support": 0.3,
        "security_tooling": 0.2,
        "cross_repo_usage": 0.1,
    }

    # Default thresholds
    DEFAULT_THRESHOLDS = {
        "proceed": 0.7,
        "warning": 0.5,
    }

    # Known best practices by language (placeholder - will load from KB)
    KNOWN_BEST_PRACTICES = {
        "python": {
            "count": 45,  # CORTEX has 45+ Python best practices
            "frameworks": {
                "django": 12,
                "flask": 8,
                "fastapi": 10,
                "pytest": 15,
            },
        },
        "javascript": {
            "count": 35,
            "frameworks": {
                "react": 15,
                "vue": 10,
                "express": 8,
                "jest": 12,
            },
        },
        "typescript": {
            "count": 40,
            "frameworks": {
                "angular": 15,
                "nest": 12,
                "react": 15,
            },
        },
        "java": {
            "count": 30,
            "frameworks": {
                "spring": 20,
                "junit": 10,
            },
        },
        "go": {
            "count": 25,
            "frameworks": {
                "gin": 8,
                "gorilla": 6,
            },
        },
        "rust": {
            "count": 20,
            "frameworks": {
                "actix": 8,
                "tokio": 7,
            },
        },
    }

    # TDD framework detection
    TDD_FRAMEWORKS = {
        "python": ["pytest", "unittest", "nose", "tox"],
        "javascript": ["jest", "mocha", "jasmine", "vitest"],
        "typescript": ["jest", "mocha", "vitest"],
        "java": ["junit", "testng"],
        "go": ["testing"],  # Built-in
        "rust": ["cargo test"],  # Built-in
    }

    # Security tools by language
    SECURITY_TOOLS = {
        "python": ["bandit", "safety", "pip-audit", "snyk"],
        "javascript": ["npm audit", "snyk", "eslint-plugin-security"],
        "typescript": ["npm audit", "snyk"],
        "java": ["spotbugs", "pmd", "snyk"],
        "go": ["gosec", "staticcheck"],
        "rust": ["cargo-audit", "cargo-deny"],
    }

    def __init__(
        self,
        weights: Optional[Dict[str, float]] = None,
        thresholds: Optional[Dict[str, float]] = None,
        cache_enabled: bool = True,
        cache_ttl: float = 3600.0,  # 1 hour default
    ):
        """
        Initialize ReadinessEngine.

        Args:
            weights: Custom component weights (must sum to 1.0)
            thresholds: Custom action thresholds
            cache_enabled: Enable score caching
            cache_ttl: Cache time-to-live in seconds
        """
        self.weights = weights or self.DEFAULT_WEIGHTS
        self.thresholds = thresholds or self.DEFAULT_THRESHOLDS
        self.cache_enabled = cache_enabled
        self.cache_ttl = cache_ttl

        # Validate weights sum to 1.0
        if abs(sum(self.weights.values()) - 1.0) > 0.01:
            raise ValueError(f"Weights must sum to 1.0, got {sum(self.weights.values())}")

        # Cache: tech_stack -> (score, timestamp)
        self._cache: Dict[TechStack, Tuple[ReadinessScore, float]] = {}
        self._cache_lock = threading.Lock()

        # Statistics
        self.cache_hits = 0
        self.cache_misses = 0

        logger.debug(f"ReadinessEngine initialized (cache: {cache_enabled}, ttl: {cache_ttl}s)")

    def calculate_readiness_score(self, tech_stack: Optional[TechStack]) -> ReadinessScore:
        """
        Calculate overall readiness score for a tech stack.

        Args:
            tech_stack: Technology stack to evaluate

        Returns:
            ReadinessScore with overall score and action recommendation
        """
        # Handle None/invalid input
        if tech_stack is None or not tech_stack.language:
            return ReadinessScore(
                overall=0.0,
                best_practices=0.0,
                tdd_support=0.0,
                security=0.0,
                usage=0.0,
                action="TRIGGER_LEARNING",
            )

        # Check cache
        if self.cache_enabled:
            cached = self._get_from_cache(tech_stack)
            if cached:
                self.cache_hits += 1
                return cached
            self.cache_misses += 1

        # Calculate component scores
        bp_score = self.calculate_best_practices_score(tech_stack)
        tdd_score = self.calculate_tdd_support_score(tech_stack)
        security_score = self.calculate_security_tooling_score(tech_stack)
        usage_score = self.calculate_cross_repo_usage_score(tech_stack)

        # Calculate weighted overall score
        overall = (
            bp_score * self.weights["best_practices"] +
            tdd_score * self.weights["tdd_support"] +
            security_score * self.weights["security_tooling"] +
            usage_score * self.weights["cross_repo_usage"]
        )

        # Determine action based on thresholds
        if overall >= self.thresholds["proceed"]:
            action = "PROCEED"
        elif overall >= self.thresholds["warning"]:
            action = "PROCEED_WITH_WARNING"
        else:
            action = "TRIGGER_LEARNING"

        # Build score object
        score = ReadinessScore(
            overall=overall,
            best_practices=bp_score,
            tdd_support=tdd_score,
            security=security_score,
            usage=usage_score,
            action=action,
        )

        # Store in cache
        if self.cache_enabled:
            self._store_in_cache(tech_stack, score)

        return score

    def calculate_best_practices_score(self, tech_stack: TechStack) -> float:
        """
        Calculate best practices coverage score.

        Args:
            tech_stack: Technology stack

        Returns:
            Score between 0.0-1.0
        """
        language = tech_stack.language.lower()

        # Load from knowledge base (simplified for skeleton)
        practices = self._load_best_practices(language)

        if not practices:
            # Unknown language - low score
            return 0.2

        total_practices = practices.get("count", 0)

        # Boost score if frameworks are known
        framework_bonus = 0.0
        frameworks_data = practices.get("frameworks", {})
        for framework in tech_stack.frameworks:
            if framework.lower() in frameworks_data:
                framework_bonus += 0.1

        # Base score from language support
        base_score = min(1.0, total_practices / 50.0)  # Normalize to 50 practices

        # Apply framework bonus (capped at 1.0)
        final_score = min(1.0, base_score + framework_bonus)

        return final_score

    def calculate_tdd_support_score(self, tech_stack: TechStack) -> float:
        """
        Calculate TDD framework support score.

        Args:
            tech_stack: Technology stack

        Returns:
            Score between 0.0-1.0
        """
        language = tech_stack.language.lower()

        # Get known TDD frameworks for this language
        known_frameworks = self.TDD_FRAMEWORKS.get(language, [])

        if not known_frameworks:
            return 0.2  # Unknown language

        # Check if any TDD frameworks are present
        detected_count = 0
        for framework in known_frameworks:
            # Check in frameworks list
            if framework in [f.lower() for f in tech_stack.frameworks]:
                detected_count += 1

        # Score based on coverage
        if detected_count == 0:
            return 0.3  # No TDD framework, but language is known
        elif detected_count == 1:
            return 0.7  # One TDD framework
        else:
            return 0.9  # Multiple TDD frameworks

    def calculate_security_tooling_score(self, tech_stack: TechStack) -> float:
        """
        Calculate security tool availability score.

        Args:
            tech_stack: Technology stack

        Returns:
            Score between 0.0-1.0
        """
        language = tech_stack.language.lower()

        # Get known security tools for this language
        known_tools = self.SECURITY_TOOLS.get(language, [])

        if not known_tools:
            return 0.2  # Unknown language

        # Check if any security tools are present in frameworks
        # (frameworks can include linters, formatters, security scanners)
        detected_count = 0
        for tool in known_tools:
            if tool in [f.lower() for f in tech_stack.frameworks]:
                detected_count += 1

        # Score based on tool count
        if detected_count == 0:
            return 0.3  # No security tools
        elif detected_count == 1:
            return 0.6  # One security tool
        elif detected_count == 2:
            return 0.8  # Two security tools
        else:
            return 1.0  # Three or more security tools

    def calculate_cross_repo_usage_score(self, tech_stack: TechStack) -> float:
        """
        Calculate cross-repo usage frequency score.

        Args:
            tech_stack: Technology stack

        Returns:
            Score between 0.0-1.0
        """
        # Get usage statistics (simplified - placeholder)
        usage_stats = self._get_usage_stats(tech_stack)

        count = usage_stats.get("count", 0)
        total = usage_stats.get("total", 1)  # Avoid division by zero

        # Normalize to 0.0-1.0
        return min(1.0, count / max(1, total))

    def _load_best_practices(self, language: str) -> Dict[str, Any]:
        """
        Load best practices from knowledge base.

        Args:
            language: Programming language

        Returns:
            Dictionary of best practices data
        """
        # Simplified - return from KNOWN_BEST_PRACTICES
        # In full implementation, would load from YAML files
        return self.KNOWN_BEST_PRACTICES.get(language, {})

    def _get_usage_stats(self, tech_stack: TechStack) -> Dict[str, int]:
        """
        Get cross-repo usage statistics.

        Args:
            tech_stack: Technology stack

        Returns:
            Dictionary with count and total
        """
        # Placeholder - in full implementation, would query usage database
        # For now, return mock data based on language popularity
        popular_languages = ["python", "javascript", "typescript", "java"]

        if tech_stack.language.lower() in popular_languages:
            return {"count": 7, "total": 10}  # 70% usage
        else:
            return {"count": 2, "total": 10}  # 20% usage

    def _get_from_cache(self, tech_stack: TechStack) -> Optional[ReadinessScore]:
        """Get score from cache if valid."""
        with self._cache_lock:
            if tech_stack not in self._cache:
                return None

            score, timestamp = self._cache[tech_stack]

            # Check if expired
            if time.time() - timestamp > self.cache_ttl:
                del self._cache[tech_stack]
                return None

            return score

    def _store_in_cache(self, tech_stack: TechStack, score: ReadinessScore) -> None:
        """Store score in cache."""
        with self._cache_lock:
            self._cache[tech_stack] = (score, time.time())

    def invalidate_cache(self, tech_stack: Optional[TechStack] = None) -> None:
        """
        Invalidate cache entries.

        Args:
            tech_stack: Specific tech stack to invalidate, or None for all
        """
        with self._cache_lock:
            if tech_stack is None:
                self._cache.clear()
                logger.debug("Cache cleared")
            elif tech_stack in self._cache:
                del self._cache[tech_stack]
                logger.debug(f"Cache invalidated for {tech_stack.language}")

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache statistics.

        Returns:
            Dictionary with cache statistics
        """
        with self._cache_lock:
            return {
                "hits": self.cache_hits,
                "misses": self.cache_misses,
                "hit_rate": self.cache_hits / max(1, self.cache_hits + self.cache_misses),
                "size": len(self._cache),
                "enabled": self.cache_enabled,
            }
