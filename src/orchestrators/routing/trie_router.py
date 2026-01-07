"""
CORTEX 6.0 - Trie-based Pattern Router

O(1) lookup pattern matching engine for intent routing.
Uses a hybrid Trie + Hash table approach for optimal performance.

Architecture:
- Trie for prefix matching and word-based routing
- Hash table for exact O(1) lookups
- Compiled regex cache for pattern rules
- Priority queue for conflict resolution

Performance targets:
- <5ms lookup time for 100+ orchestrators
- O(1) for exact matches
- O(k) for prefix matches (k = input length)

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from __future__ import annotations
import re
import logging
from typing import Dict, Any, Optional, List, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import threading


class MatchType(str, Enum):
    """Pattern match type."""
    EXACT = "exact"
    PREFIX = "prefix"
    REGEX = "regex"
    KEYWORD = "keyword"
    NONE = "none"


@dataclass
class RouteConfig:
    """Configuration for a single route."""
    orchestrator_id: str
    confidence: float
    match_type: MatchType
    priority: int = 100  # Lower = higher priority
    metadata: Dict[str, Any] = field(default_factory=dict)
    pattern: str = ""  # Original pattern for debugging
    
    def __post_init__(self):
        if not 0 <= self.confidence <= 1.0:
            raise ValueError(f"Confidence must be 0-1, got {self.confidence}")


@dataclass
class RouteMatch:
    """Result of route matching."""
    orchestrator_id: Optional[str]
    confidence: float
    match_type: MatchType
    matched_pattern: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    lookup_time_ms: float = 0.0
    
    @property
    def is_matched(self) -> bool:
        return self.orchestrator_id is not None and self.confidence > 0
    
    @property
    def is_high_confidence(self) -> bool:
        return self.confidence >= 0.9
    
    @classmethod
    def no_match(cls) -> RouteMatch:
        """Factory for no-match result."""
        return cls(
            orchestrator_id=None,
            confidence=0.0,
            match_type=MatchType.NONE
        )


class TrieNode:
    """
    Node in the Trie structure.
    
    Each node represents a word boundary in the input phrase.
    Terminal nodes contain route configurations.
    """
    __slots__ = ['children', 'routes', 'is_terminal', 'word']
    
    def __init__(self, word: str = ""):
        self.children: Dict[str, TrieNode] = {}
        self.routes: List[RouteConfig] = []
        self.is_terminal: bool = False
        self.word: str = word
    
    def add_child(self, word: str) -> TrieNode:
        """Add or get child node for word."""
        if word not in self.children:
            self.children[word] = TrieNode(word)
        return self.children[word]
    
    def get_child(self, word: str) -> Optional[TrieNode]:
        """Get child node for word."""
        return self.children.get(word)


class TrieRouter:
    """
    High-performance Trie-based pattern router.
    
    Provides O(1) exact lookups and O(k) prefix matching where
    k is the number of words in the input.
    
    Architecture:
    
    1. **Exact Hash Table** (O(1))
       - Normalized full phrases mapped directly to routes
       - Used for exact match patterns
    
    2. **Word Trie** (O(k))
       - Word-by-word traversal for prefix/keyword matching
       - Each node can be terminal with routes
    
    3. **Regex Cache** (O(n*m))
       - Pre-compiled regex patterns
       - Only used when Trie lookup fails
       - Cached compilation for performance
    
    4. **Keyword Index** (O(1) + O(m))
       - Inverted index of keywords to routes
       - Fast keyword-based routing
    
    Thread Safety:
    - Read operations are thread-safe
    - Write operations (add_route) use locking
    
    Usage:
        router = TrieRouter()
        router.add_exact_route("plan", "planning_orchestrator")
        router.add_prefix_route("create a plan", "planning_orchestrator")
        router.add_keyword_route(["debug", "fix"], "debug_orchestrator")
        
        match = router.match("plan the authentication system")
        if match.is_matched:
            print(f"Route to: {match.orchestrator_id}")
    """
    
    def __init__(self, enable_logging: bool = True):
        """
        Initialize the Trie router.
        
        Args:
            enable_logging: Enable debug logging
        """
        self.logger = logging.getLogger("cortex.routing.trie")
        self._enable_logging = enable_logging
        
        # Primary data structures
        self._exact_routes: Dict[str, List[RouteConfig]] = {}
        self._trie_root: TrieNode = TrieNode()
        self._keyword_index: Dict[str, List[RouteConfig]] = defaultdict(list)
        self._regex_patterns: List[Tuple[re.Pattern, RouteConfig]] = []
        
        # Thread safety
        self._lock = threading.RLock()
        
        # Statistics
        self._stats = {
            'exact_routes': 0,
            'prefix_routes': 0,
            'keyword_routes': 0,
            'regex_routes': 0,
            'total_lookups': 0,
            'cache_hits': 0
        }
    
    # =========================================================================
    # ROUTE REGISTRATION
    # =========================================================================
    
    def add_exact_route(
        self,
        phrase: str,
        orchestrator_id: str,
        confidence: float = 1.0,
        priority: int = 100,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add an exact match route (O(1) lookup).
        
        Args:
            phrase: Exact phrase to match
            orchestrator_id: Target orchestrator
            confidence: Match confidence (0-1)
            priority: Route priority (lower = higher)
            metadata: Additional route metadata
        """
        with self._lock:
            normalized = self._normalize(phrase)
            
            config = RouteConfig(
                orchestrator_id=orchestrator_id,
                confidence=confidence,
                match_type=MatchType.EXACT,
                priority=priority,
                metadata=metadata or {},
                pattern=phrase
            )
            
            if normalized not in self._exact_routes:
                self._exact_routes[normalized] = []
            self._exact_routes[normalized].append(config)
            
            # Sort by priority
            self._exact_routes[normalized].sort(key=lambda r: r.priority)
            
            self._stats['exact_routes'] += 1
            
            if self._enable_logging:
                self.logger.debug(f"Added exact route: '{phrase}' → {orchestrator_id}")
    
    def add_prefix_route(
        self,
        phrase: str,
        orchestrator_id: str,
        confidence: float = 0.95,
        priority: int = 100,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a prefix match route (O(k) lookup, k = words in phrase).
        
        The input must START with this phrase to match.
        
        Args:
            phrase: Prefix phrase to match
            orchestrator_id: Target orchestrator
            confidence: Match confidence (0-1)
            priority: Route priority (lower = higher)
            metadata: Additional route metadata
        """
        with self._lock:
            words = self._tokenize(phrase)
            
            if not words:
                raise ValueError("Phrase must contain at least one word")
            
            config = RouteConfig(
                orchestrator_id=orchestrator_id,
                confidence=confidence,
                match_type=MatchType.PREFIX,
                priority=priority,
                metadata=metadata or {},
                pattern=phrase
            )
            
            # Traverse/build Trie
            node = self._trie_root
            for word in words:
                node = node.add_child(word)
            
            node.is_terminal = True
            node.routes.append(config)
            node.routes.sort(key=lambda r: r.priority)
            
            self._stats['prefix_routes'] += 1
            
            if self._enable_logging:
                self.logger.debug(f"Added prefix route: '{phrase}' → {orchestrator_id}")
    
    def add_keyword_route(
        self,
        keywords: List[str],
        orchestrator_id: str,
        confidence: float = 0.85,
        priority: int = 100,
        metadata: Optional[Dict[str, Any]] = None,
        require_all: bool = False
    ) -> None:
        """
        Add a keyword-based route.
        
        Matches if input contains ANY (or ALL if require_all=True) of the keywords.
        
        Args:
            keywords: List of trigger keywords
            orchestrator_id: Target orchestrator
            confidence: Match confidence (0-1)
            priority: Route priority (lower = higher)
            metadata: Additional route metadata
            require_all: Require all keywords to be present
        """
        with self._lock:
            config = RouteConfig(
                orchestrator_id=orchestrator_id,
                confidence=confidence,
                match_type=MatchType.KEYWORD,
                priority=priority,
                metadata={**(metadata or {}), 'keywords': keywords, 'require_all': require_all},
                pattern=f"keywords:{','.join(keywords)}"
            )
            
            for keyword in keywords:
                normalized_kw = self._normalize(keyword)
                self._keyword_index[normalized_kw].append(config)
            
            self._stats['keyword_routes'] += 1
            
            if self._enable_logging:
                self.logger.debug(f"Added keyword route: {keywords} → {orchestrator_id}")
    
    def add_regex_route(
        self,
        pattern: str,
        orchestrator_id: str,
        confidence: float = 0.9,
        priority: int = 100,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Add a regex pattern route (fallback, slower).
        
        Args:
            pattern: Regex pattern string
            orchestrator_id: Target orchestrator
            confidence: Match confidence (0-1)
            priority: Route priority (lower = higher)
            metadata: Additional route metadata
        """
        with self._lock:
            try:
                compiled = re.compile(pattern, re.IGNORECASE)
            except re.error as e:
                raise ValueError(f"Invalid regex pattern: {pattern} - {e}")
            
            config = RouteConfig(
                orchestrator_id=orchestrator_id,
                confidence=confidence,
                match_type=MatchType.REGEX,
                priority=priority,
                metadata=metadata or {},
                pattern=pattern
            )
            
            self._regex_patterns.append((compiled, config))
            self._regex_patterns.sort(key=lambda x: x[1].priority)
            
            self._stats['regex_routes'] += 1
            
            if self._enable_logging:
                self.logger.debug(f"Added regex route: '{pattern}' → {orchestrator_id}")
    
    # =========================================================================
    # ROUTE MATCHING
    # =========================================================================
    
    def match(self, input_text: str) -> RouteMatch:
        """
        Match input text against all routes.
        
        Matching order (fastest first):
        1. Exact hash lookup (O(1))
        2. Trie prefix lookup (O(k))
        3. Keyword index lookup (O(w) where w = words in input)
        4. Regex patterns (O(n*m) - fallback)
        
        Args:
            input_text: User input to match
            
        Returns:
            RouteMatch with routing decision
        """
        import time
        start = time.perf_counter()
        
        self._stats['total_lookups'] += 1
        
        if not input_text or not input_text.strip():
            return RouteMatch.no_match()
        
        normalized = self._normalize(input_text)
        
        # 1. Try exact match (O(1))
        result = self._match_exact(normalized)
        if result.is_matched:
            result.lookup_time_ms = (time.perf_counter() - start) * 1000
            self._stats['cache_hits'] += 1
            return result
        
        # 2. Try Trie prefix match (O(k))
        result = self._match_trie(normalized)
        if result.is_matched:
            result.lookup_time_ms = (time.perf_counter() - start) * 1000
            return result
        
        # 3. Try keyword match (O(w))
        result = self._match_keywords(normalized)
        if result.is_matched:
            result.lookup_time_ms = (time.perf_counter() - start) * 1000
            return result
        
        # 4. Try regex patterns (fallback)
        result = self._match_regex(normalized)
        result.lookup_time_ms = (time.perf_counter() - start) * 1000
        return result
    
    def _match_exact(self, normalized: str) -> RouteMatch:
        """O(1) exact match lookup."""
        routes = self._exact_routes.get(normalized)
        if routes:
            route = routes[0]  # Highest priority (pre-sorted)
            return RouteMatch(
                orchestrator_id=route.orchestrator_id,
                confidence=route.confidence,
                match_type=MatchType.EXACT,
                matched_pattern=route.pattern,
                metadata=route.metadata
            )
        return RouteMatch.no_match()
    
    def _match_trie(self, normalized: str) -> RouteMatch:
        """O(k) Trie prefix match lookup."""
        words = normalized.split()
        
        if not words:
            return RouteMatch.no_match()
        
        node = self._trie_root
        best_match: Optional[RouteMatch] = None
        matched_words = []
        
        for word in words:
            child = node.get_child(word)
            if child is None:
                break
            
            node = child
            matched_words.append(word)
            
            if node.is_terminal and node.routes:
                # Found a terminal node with routes
                route = node.routes[0]  # Highest priority
                best_match = RouteMatch(
                    orchestrator_id=route.orchestrator_id,
                    confidence=route.confidence,
                    match_type=MatchType.PREFIX,
                    matched_pattern=route.pattern,
                    metadata=route.metadata
                )
        
        return best_match or RouteMatch.no_match()
    
    def _match_keywords(self, normalized: str) -> RouteMatch:
        """Keyword-based matching."""
        words = set(normalized.split())
        
        # Find all matching keyword routes
        candidate_routes: Dict[str, Tuple[RouteConfig, Set[str]]] = {}
        
        for word in words:
            if word in self._keyword_index:
                for route in self._keyword_index[word]:
                    route_id = id(route)
                    if route_id not in candidate_routes:
                        candidate_routes[route_id] = (route, set())
                    candidate_routes[route_id][1].add(word)
        
        if not candidate_routes:
            return RouteMatch.no_match()
        
        # Filter and sort candidates
        valid_routes = []
        for route, matched_keywords in candidate_routes.values():
            required_keywords = set(k.lower() for k in route.metadata.get('keywords', []))
            require_all = route.metadata.get('require_all', False)
            
            if require_all:
                if matched_keywords >= required_keywords:
                    valid_routes.append(route)
            else:
                valid_routes.append(route)
        
        if valid_routes:
            # Sort by priority, then confidence
            valid_routes.sort(key=lambda r: (r.priority, -r.confidence))
            route = valid_routes[0]
            return RouteMatch(
                orchestrator_id=route.orchestrator_id,
                confidence=route.confidence,
                match_type=MatchType.KEYWORD,
                matched_pattern=route.pattern,
                metadata=route.metadata
            )
        
        return RouteMatch.no_match()
    
    def _match_regex(self, normalized: str) -> RouteMatch:
        """Regex pattern matching (fallback)."""
        for pattern, route in self._regex_patterns:
            if pattern.search(normalized):
                return RouteMatch(
                    orchestrator_id=route.orchestrator_id,
                    confidence=route.confidence,
                    match_type=MatchType.REGEX,
                    matched_pattern=route.pattern,
                    metadata=route.metadata
                )
        
        return RouteMatch.no_match()
    
    # =========================================================================
    # UTILITIES
    # =========================================================================
    
    def _normalize(self, text: str) -> str:
        """Normalize text for matching."""
        return text.strip().lower()
    
    def _tokenize(self, text: str) -> List[str]:
        """Tokenize text into words."""
        return self._normalize(text).split()
    
    def get_stats(self) -> Dict[str, Any]:
        """Get router statistics."""
        return {
            **self._stats,
            'total_routes': (
                self._stats['exact_routes'] +
                self._stats['prefix_routes'] +
                self._stats['keyword_routes'] +
                self._stats['regex_routes']
            )
        }
    
    def clear(self) -> None:
        """Clear all routes."""
        with self._lock:
            self._exact_routes.clear()
            self._trie_root = TrieNode()
            self._keyword_index.clear()
            self._regex_patterns.clear()
            self._stats = {
                'exact_routes': 0,
                'prefix_routes': 0,
                'keyword_routes': 0,
                'regex_routes': 0,
                'total_lookups': 0,
                'cache_hits': 0
            }
    
    def export_routes(self) -> Dict[str, Any]:
        """Export all routes for debugging."""
        return {
            'exact': {
                phrase: [
                    {'orchestrator': r.orchestrator_id, 'confidence': r.confidence, 'priority': r.priority}
                    for r in routes
                ]
                for phrase, routes in self._exact_routes.items()
            },
            'prefix_count': self._stats['prefix_routes'],
            'keyword_count': self._stats['keyword_routes'],
            'regex_count': self._stats['regex_routes'],
            'stats': self.get_stats()
        }


# Module-level instance for global access
_default_router: Optional[TrieRouter] = None


def get_trie_router() -> TrieRouter:
    """Get or create the default Trie router instance."""
    global _default_router
    if _default_router is None:
        _default_router = TrieRouter()
    return _default_router


def set_trie_router(router: TrieRouter) -> None:
    """Set the default Trie router instance."""
    global _default_router
    _default_router = router
