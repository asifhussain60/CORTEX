"""
Pattern Router - Machine-Readable Intent Routing.

Deterministic pattern matching engine for orchestrator routing without LLM dependency.
Supports exact matches, regex patterns, and confidence scoring.

CORTEX 6.0: Enhanced with Trie-based O(1) routing via TrieRouter integration.

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import re
import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import yaml

# CORTEX 6.0: Import Trie router for O(1) performance
try:
    from .routing.trie_router import TrieRouter, RouteMatch as TrieRouteMatch, MatchType as TrieMatchType
    TRIE_ROUTER_AVAILABLE = True
except ImportError:
    TRIE_ROUTER_AVAILABLE = False


class MatchType(str, Enum):
    """Pattern match type."""
    EXACT = "exact"
    REGEX = "regex"
    FUZZY = "fuzzy"
    NONE = "none"
    PREFIX = "prefix"  # CORTEX 6.0: Added prefix match type
    KEYWORD = "keyword"  # CORTEX 6.0: Added keyword match type


@dataclass
class RoutingRule:
    """Single routing rule definition."""
    pattern: str
    orchestrator_id: str
    confidence: float
    match_type: MatchType
    priority: int = 100  # Lower = higher priority
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        """Validate rule after initialization."""
        if not 0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0-1, got {self.confidence}")
        
        if self.match_type == MatchType.REGEX:
            # Compile regex to validate pattern
            try:
                re.compile(self.pattern, re.IGNORECASE)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {self.pattern} - {e}")


@dataclass
class OrchestratorMatch:
    """Result of pattern matching."""
    orchestrator_id: Optional[str]
    confidence: float
    match_type: MatchType
    matched_pattern: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    lookup_time_ms: float = 0.0  # CORTEX 6.0: Added timing
    
    @property
    def is_matched(self) -> bool:
        """Check if a match was found."""
        return self.orchestrator_id is not None and self.confidence > 0
    
    @property
    def is_high_confidence(self) -> bool:
        """Check if match confidence is high (>= 0.9)."""
        return self.confidence >= 0.9
    
    @classmethod
    def from_trie_match(cls, trie_match: 'TrieRouteMatch') -> 'OrchestratorMatch':
        """Convert TrieRouteMatch to OrchestratorMatch for backwards compatibility."""
        # Map Trie match types to legacy match types
        match_type_map = {
            'exact': MatchType.EXACT,
            'prefix': MatchType.PREFIX,
            'keyword': MatchType.KEYWORD,
            'regex': MatchType.REGEX,
            'none': MatchType.NONE,
        }
        return cls(
            orchestrator_id=trie_match.orchestrator_id,
            confidence=trie_match.confidence,
            match_type=match_type_map.get(trie_match.match_type.value, MatchType.NONE),
            matched_pattern=trie_match.matched_pattern,
            metadata=trie_match.metadata,
            lookup_time_ms=trie_match.lookup_time_ms
        )


class PatternRouter:
    """
    Machine-readable pattern matching engine for intent routing.
    
    Provides deterministic routing without LLM dependency through
    exact pattern matching and regex patterns with confidence scoring.
    
    CORTEX 6.0: Enhanced with Trie-based O(1) routing for improved performance.
    Uses TrieRouter internally when available, falls back to linear search.
    
    Features:
    - Exact string matching (case-insensitive) - O(1) with Trie
    - Prefix matching - O(k) with Trie (k = words in input)
    - Keyword matching - O(w) with Trie (w = words in input)
    - Regex pattern matching - O(n*m) fallback
    - Priority-based rule ordering
    - Confidence scoring
    - Pattern compilation caching
    
    Usage:
        router = PatternRouter('config/master-orchestrator.yaml')
        match = router.match_intent("plan user authentication")
        if match.is_matched:
            print(f"Route to: {match.orchestrator_id}")
    """
    
    def __init__(self, config_path: str, use_trie: bool = True):
        """
        Initialize router with configuration file.
        
        Args:
            config_path: Path to YAML routing configuration
            use_trie: Use Trie-based O(1) routing (CORTEX 6.0 feature)
        """
        self.config_path = Path(config_path)
        self.logger = logging.getLogger("cortex.orchestrators.pattern_router")
        
        # Load rules
        self.rules: List[RoutingRule] = []
        self.fallback_config: Dict[str, Any] = {}
        self._compiled_patterns: Dict[str, re.Pattern] = {}
        
        # CORTEX 6.0: Initialize Trie router if available and enabled
        self._use_trie = use_trie and TRIE_ROUTER_AVAILABLE
        self._trie_router: Optional[TrieRouter] = None
        if self._use_trie:
            self._trie_router = TrieRouter(enable_logging=False)
        
        self._load_routing_rules()
        
        self.logger.info(
            f"PatternRouter initialized with {len(self.rules)} rules"
        )
    
    def _load_routing_rules(self) -> None:
        """
        Load routing rules from YAML configuration.
        
        Raises:
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config is invalid YAML
            ValueError: If rules are invalid
        """
        if not self.config_path.exists():
            raise FileNotFoundError(f"Config not found: {self.config_path}")
        
        with open(self.config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Parse routing rules
        rules_config = config.get('routing_rules', [])
        for idx, rule_dict in enumerate(rules_config):
            try:
                rule = RoutingRule(
                    pattern=rule_dict['pattern'],
                    orchestrator_id=rule_dict['orchestrator'],
                    confidence=rule_dict.get('confidence', 1.0),
                    match_type=MatchType(rule_dict['match_type']),
                    priority=rule_dict.get('priority', 100),
                    metadata=rule_dict.get('metadata', {})
                )
                self.rules.append(rule)
                
                # Pre-compile regex patterns
                if rule.match_type == MatchType.REGEX:
                    self._compiled_patterns[rule.pattern] = re.compile(
                        rule.pattern,
                        re.IGNORECASE
                    )
                
                # CORTEX 6.0: Add rule to Trie router for O(1) lookup
                if self._trie_router is not None:
                    self._add_rule_to_trie(rule)
                
            except Exception as e:
                self.logger.error(
                    f"Failed to parse rule {idx}: {rule_dict} - {e}"
                )
                raise ValueError(f"Invalid routing rule at index {idx}: {e}")
        
        # Sort rules by priority (lower = higher priority)
        self.rules.sort(key=lambda r: r.priority)
        
        # Load fallback configuration
        self.fallback_config = config.get('fallback', {})
        
        self.logger.info(f"Loaded {len(self.rules)} routing rules")
    
    def _add_rule_to_trie(self, rule: RoutingRule) -> None:
        """
        Add a routing rule to the Trie router for O(1) lookup.
        
        CORTEX 6.0: Hybrid routing - Trie for O(1), fallback to regex.
        
        Args:
            rule: Routing rule to add
        """
        if self._trie_router is None:
            return
        
        # Map MatchType to Trie route type
        if rule.match_type == MatchType.EXACT:
            self._trie_router.add_exact_route(
                phrase=rule.pattern.lower(),
                orchestrator_id=rule.orchestrator_id,
                confidence=rule.confidence,
                priority=rule.priority,
                metadata=rule.metadata or {}
            )
        elif rule.match_type == MatchType.REGEX:
            self._trie_router.add_regex_route(
                pattern=rule.pattern,
                orchestrator_id=rule.orchestrator_id,
                confidence=rule.confidence,
                priority=rule.priority,
                metadata=rule.metadata or {}
            )
        # Note: PREFIX and KEYWORD types can be added as needed
    
    def match_intent(self, user_input: str) -> OrchestratorMatch:
        """
        Match user input against routing patterns.
        
        CORTEX 6.0: Uses Trie router for O(1) lookup when available,
        with fallback to traditional regex matching.
        
        Args:
            user_input: User's natural language input
        
        Returns:
            OrchestratorMatch with routing decision
        """
        if not user_input or not user_input.strip():
            return OrchestratorMatch(
                orchestrator_id=None,
                confidence=0.0,
                match_type=MatchType.NONE
            )
        
        # Normalize input
        normalized_input = user_input.strip().lower()
        
        # CORTEX 6.0: Try Trie router first for O(1) performance
        if self._use_trie and self._trie_router is not None:
            trie_match = self._trie_router.match(normalized_input)
            if trie_match.is_matched:
                result = OrchestratorMatch.from_trie_match(trie_match)
                self.logger.info(
                    f"Trie matched: '{user_input}' → {result.orchestrator_id} "
                    f"(confidence={result.confidence:.2f}, "
                    f"type={result.match_type.value})"
                )
                return result
        
        # Fallback: Try each rule in priority order
        for rule in self.rules:
            match_result = self._try_match_rule(normalized_input, rule)
            
            if match_result.is_matched:
                self.logger.info(
                    f"Matched: '{user_input}' → {match_result.orchestrator_id} "
                    f"(confidence={match_result.confidence:.2f}, "
                    f"type={match_result.match_type.value})"
                )
                return match_result
        
        # No match found
        self.logger.debug(f"No match found for: '{user_input}'")
        return OrchestratorMatch(
            orchestrator_id=None,
            confidence=0.0,
            match_type=MatchType.NONE
        )
    
    def _try_match_rule(
        self,
        normalized_input: str,
        rule: RoutingRule
    ) -> OrchestratorMatch:
        """
        Try to match input against a single rule.
        
        Args:
            normalized_input: Normalized user input
            rule: Routing rule to test
        
        Returns:
            OrchestratorMatch (may have confidence=0 if no match)
        """
        if rule.match_type == MatchType.EXACT:
            # Exact pattern match
            pattern_lower = rule.pattern.lower()
            if re.match(f"^{re.escape(pattern_lower)}$", normalized_input):
                return OrchestratorMatch(
                    orchestrator_id=rule.orchestrator_id,
                    confidence=rule.confidence,
                    match_type=MatchType.EXACT,
                    matched_pattern=rule.pattern,
                    metadata=rule.metadata
                )
        
        elif rule.match_type == MatchType.REGEX:
            # Regex pattern match
            compiled_pattern = self._compiled_patterns.get(rule.pattern)
            if compiled_pattern and compiled_pattern.search(normalized_input):
                return OrchestratorMatch(
                    orchestrator_id=rule.orchestrator_id,
                    confidence=rule.confidence,
                    match_type=MatchType.REGEX,
                    matched_pattern=rule.pattern,
                    metadata=rule.metadata
                )
        
        # No match
        return OrchestratorMatch(
            orchestrator_id=None,
            confidence=0.0,
            match_type=MatchType.NONE
        )
    
    def get_orchestrator_patterns(
        self,
        orchestrator_id: str
    ) -> List[RoutingRule]:
        """
        Get all patterns that route to a specific orchestrator.
        
        Args:
            orchestrator_id: Orchestrator identifier
        
        Returns:
            List of routing rules for this orchestrator
        """
        return [
            rule for rule in self.rules
            if rule.orchestrator_id == orchestrator_id
        ]
    
    def validate_patterns(self) -> List[str]:
        """
        Validate all routing patterns for correctness.
        
        Returns:
            List of validation error messages (empty if all valid)
        """
        errors = []
        
        # Check for duplicate exact patterns
        exact_patterns = [
            rule.pattern for rule in self.rules
            if rule.match_type == MatchType.EXACT
        ]
        seen = set()
        for pattern in exact_patterns:
            if pattern in seen:
                errors.append(f"Duplicate exact pattern: {pattern}")
            seen.add(pattern)
        
        # Validate regex patterns compile
        for rule in self.rules:
            if rule.match_type == MatchType.REGEX:
                try:
                    re.compile(rule.pattern, re.IGNORECASE)
                except re.error as e:
                    errors.append(
                        f"Invalid regex pattern: {rule.pattern} - {e}"
                    )
        
        return errors
    
    def reload_config(self) -> None:
        """
        Reload routing configuration from file.
        
        Useful for hot-reloading in development.
        """
        self.logger.info("Reloading routing configuration...")
        
        self.rules.clear()
        self._compiled_patterns.clear()
        
        self._load_routing_rules()
        
        self.logger.info(
            f"Configuration reloaded: {len(self.rules)} rules"
        )
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get router statistics.
        
        Returns:
            Dictionary with router metrics
        """
        exact_count = sum(
            1 for r in self.rules if r.match_type == MatchType.EXACT
        )
        regex_count = sum(
            1 for r in self.rules if r.match_type == MatchType.REGEX
        )
        
        orchestrators = set(r.orchestrator_id for r in self.rules)
        
        return {
            'total_rules': len(self.rules),
            'exact_patterns': exact_count,
            'regex_patterns': regex_count,
            'unique_orchestrators': len(orchestrators),
            'orchestrators': sorted(orchestrators),
            'fallback_enabled': self.fallback_config.get('enabled', False)
        }
