"""Tiered Router for CORTEX Planning System 3.0

This module implements LLM-based operation classification into 4 tiers:
- Tier 1: Instant (<2s) - CLI operations, status checks
- Tier 2: Lightweight (<10s) - Single file changes
- Tier 3: Documented (10-60min) - Feature additions
- Tier 4: Complex (>1h) - Architecture changes

Author: Asif Hussain
Version: 3.0.0
Phase: 01 of CORTEX Evolution v3.9
"""

import re
import json
import hashlib
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Dict, Any, Optional, List
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class OperationTier(Enum):
    """Operation complexity tiers."""
    INSTANT = 1      # <2s deterministic
    LIGHTWEIGHT = 2  # <10s single-file
    DOCUMENTED = 3   # 10-60min feature work
    COMPLEX = 4      # >1h architecture work


@dataclass
class RoutingDecision:
    """Result of routing classification."""
    tier: int  # 1-4
    confidence: float  # 0.0-1.0
    reasoning: str
    execution_method: str  # 'instant', 'lightweight', 'documented', 'complex'
    estimated_time: str  # '<2s', '<10s', '10-60min', '>1h'
    requires_planning: bool
    timestamp: datetime = field(default_factory=datetime.now)
    cache_hit: bool = False


@dataclass
class RoutingFeedback:
    """User feedback on routing accuracy."""
    operation: str
    expected_tier: int
    actual_tier: int
    timestamp: datetime = field(default_factory=datetime.now)


class RegexFallback:
    """Regex-based fallback classifier when LLM unavailable."""
    
    TIER_1_PATTERNS = [
        r"^help$",
        r"^healthcheck$",
        r"^version$",
        r"^status$",
        r"^align$",
        r"^cleanup$",
        r"^optimize$",
        r"^feedback$"
    ]
    
    TIER_2_PATTERNS = [
        r"fix typo",
        r"update comment",
        r"add docstring",
        r"rename variable",
        r"format code",
        r"lint fix"
    ]
    
    TIER_3_PATTERNS = [
        r"add feature",
        r"implement.*function",
        r"create.*class",
        r"add.*test",
        r"plan ado story",
        r"start tdd",
        r"authentication",
        r"implement.*"
    ]
    
    TIER_4_PATTERNS = [
        r"redesign",
        r"architecture",
        r"refactor system",
        r"migrate.*database",
        r"plan ado feature",
        r"system maintenance"
    ]
    
    def classify(self, operation: str) -> int:
        """Classify operation using regex patterns."""
        operation_lower = operation.lower().strip()
        
        # Check patterns in order (most specific first)
        for pattern in self.TIER_1_PATTERNS:
            if re.search(pattern, operation_lower, re.IGNORECASE):
                return 1
        
        for pattern in self.TIER_4_PATTERNS:
            if re.search(pattern, operation_lower, re.IGNORECASE):
                return 4
        
        for pattern in self.TIER_3_PATTERNS:
            if re.search(pattern, operation_lower, re.IGNORECASE):
                return 3
        
        for pattern in self.TIER_2_PATTERNS:
            if re.search(pattern, operation_lower, re.IGNORECASE):
                return 2
        
        # Default: Tier 2 (lightweight)
        return 2


class RoutingTelemetry:
    """Track routing accuracy and performance."""
    
    def __init__(self):
        self.decisions: List[RoutingDecision] = []
        self.feedback: List[RoutingFeedback] = []
        self.cache_hits = 0
        self.cache_misses = 0
    
    def record_decision(self, decision: RoutingDecision):
        """Record routing decision."""
        self.decisions.append(decision)
        if decision.cache_hit:
            self.cache_hits += 1
        else:
            self.cache_misses += 1
    
    def record_feedback(self, operation: str, expected_tier: int, actual_tier: int):
        """Record user feedback on routing accuracy."""
        feedback = RoutingFeedback(
            operation=operation,
            expected_tier=expected_tier,
            actual_tier=actual_tier,
            timestamp=datetime.now()
        )
        self.feedback.append(feedback)
        logger.info(f"📊 Routing feedback recorded: {operation} - Expected T{expected_tier}, Got T{actual_tier}")
    
    def calculate_accuracy(self, last_n: int = 100) -> float:
        """Calculate routing accuracy over last N operations."""
        if len(self.feedback) == 0:
            return 0.0
        
        last_n = min(last_n, len(self.feedback))
        recent_feedback = self.feedback[-last_n:]
        correct = sum(1 for f in recent_feedback if f.expected_tier == f.actual_tier)
        return correct / last_n
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get telemetry metrics."""
        tier_counts = {1: 0, 2: 0, 3: 0, 4: 0}
        total_confidence = 0.0
        
        for decision in self.decisions:
            tier_counts[decision.tier] += 1
            total_confidence += decision.confidence
        
        avg_confidence = total_confidence / len(self.decisions) if self.decisions else 0.0
        
        return {
            'total_decisions': len(self.decisions),
            'accuracy': self.calculate_accuracy(),
            'tier_distribution': tier_counts,
            'average_confidence': avg_confidence,
            'cache_hit_rate': self.cache_hits / (self.cache_hits + self.cache_misses) if (self.cache_hits + self.cache_misses) > 0 else 0.0
        }


class TieredRouter:
    """LLM-based router for 4-tier operation classification."""
    
    CLASSIFICATION_PROMPT = """
Classify this operation into one of 4 tiers based on complexity:

Operation: {operation}
Context: {context}

Tier 1 (INSTANT): <2s deterministic tasks
- CLI operations (healthcheck, status, align, cleanup, optimize)
- Simple queries (help, version, feedback)
- File reads without processing
Examples: "healthcheck", "help", "get version"

Tier 2 (LIGHTWEIGHT): <10s single-file operations
- Single file edits
- Inline validation
- Quick refactors
- Typo fixes, comment updates
Examples: "fix typo in config.py", "add docstring to function"

Tier 3 (DOCUMENTED): 10-60min feature additions
- New feature implementation
- Multi-file changes with tests
- Single MD plan structure
- ADO stories
Examples: "add user authentication", "implement caching layer", "plan ado story"

Tier 4 (COMPLEX): >1h architecture changes
- System redesigns
- Multi-phase work
- Nested MD plan structure
- ADO features
Examples: "redesign database layer", "implement microservices architecture", "plan ado feature"

Response format (JSON):
{{
  "tier": 1-4,
  "confidence": 0.0-1.0,
  "reasoning": "explanation of classification"
}}
"""
    
    def __init__(self, llm_client=None, cache_enabled=True, cache_ttl_seconds=300):
        """Initialize tiered router.
        
        Args:
            llm_client: Optional LLM client for classification (None uses regex fallback)
            cache_enabled: Enable caching of routing decisions
            cache_ttl_seconds: Cache TTL in seconds (default: 5 minutes)
        """
        self.llm_client = llm_client
        self.cache = {} if cache_enabled else None
        self.cache_ttl_seconds = cache_ttl_seconds
        self.telemetry = RoutingTelemetry()
        self.regex_fallback = RegexFallback()
        logger.info("🎭 TieredRouter initialized: LLM=%s, Cache=%s", 
                   "enabled" if llm_client else "regex-fallback", 
                   "enabled" if cache_enabled else "disabled")
    
    def route(self, operation: str, context: Dict[str, Any] = None) -> RoutingDecision:
        """Route operation to appropriate tier (1-4).
        
        Args:
            operation: Operation name/description
            context: Optional context dictionary
            
        Returns:
            RoutingDecision with tier, confidence, reasoning
        """
        start_time = time.perf_counter()
        context = context or {}
        
        # Check cache first
        cache_key = self._get_cache_key(operation, context)
        if self.cache is not None:
            cached_decision = self._get_from_cache(cache_key)
            if cached_decision:
                cached_decision.cache_hit = True
                self.telemetry.record_decision(cached_decision)
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.info(f"🎭 Tiered Router: {operation} → Tier {cached_decision.tier} (CACHED, {elapsed_ms:.1f}ms)")
                return cached_decision
        
        # Classify using LLM or regex fallback
        if self.llm_client:
            tier, confidence, reasoning = self._llm_classify(operation, context)
        else:
            tier = self._regex_fallback_classify(operation)
            confidence = 0.85  # High confidence for regex patterns
            reasoning = "Regex pattern match"
        
        # Build decision
        decision = RoutingDecision(
            tier=tier,
            confidence=confidence,
            reasoning=reasoning,
            execution_method=self._get_execution_method(tier),
            estimated_time=self._get_estimated_time(tier),
            requires_planning=(tier >= 3),
            timestamp=datetime.now(),
            cache_hit=False
        )
        
        # Cache decision
        if self.cache is not None:
            self._save_to_cache(cache_key, decision)
        
        # Record telemetry
        self.telemetry.record_decision(decision)
        
        elapsed_ms = (time.perf_counter() - start_time) * 1000
        logger.info(f"🎭 Tiered Router: {operation} → Tier {tier} ({confidence:.2%} confidence, {elapsed_ms:.1f}ms)")
        
        return decision
    
    def _llm_classify(self, operation: str, context: Dict[str, Any]) -> tuple[int, float, str]:
        """Use LLM to classify operation complexity.
        
        Returns:
            (tier, confidence, reasoning)
        """
        # Format prompt
        prompt = self.CLASSIFICATION_PROMPT.format(
            operation=operation,
            context=json.dumps(context, indent=2)
        )
        
        try:
            # Call LLM (placeholder - actual implementation depends on LLM client)
            # response = self.llm_client.complete(prompt)
            # result = json.loads(response)
            
            # Fallback to regex for now
            logger.warning("LLM classification not yet implemented, using regex fallback")
            tier = self._regex_fallback_classify(operation)
            return tier, 0.85, "Regex pattern match (LLM not available)"
            
        except Exception as e:
            logger.error(f"LLM classification failed: {e}, using regex fallback")
            tier = self._regex_fallback_classify(operation)
            return tier, 0.75, f"Regex fallback due to LLM error"
    
    def _regex_fallback_classify(self, operation: str) -> int:
        """Fallback to regex-based classification."""
        return self.regex_fallback.classify(operation)
    
    def _get_cache_key(self, operation: str, context: Dict[str, Any]) -> str:
        """Generate cache key from operation and context."""
        content = f"{operation}:{json.dumps(context, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_from_cache(self, cache_key: str) -> Optional[RoutingDecision]:
        """Retrieve cached routing decision."""
        if cache_key in self.cache:
            decision, timestamp = self.cache[cache_key]
            age_seconds = (datetime.now() - timestamp).total_seconds()
            if age_seconds < self.cache_ttl_seconds:
                return decision
            else:
                # Expired, remove from cache
                del self.cache[cache_key]
        return None
    
    def _save_to_cache(self, cache_key: str, decision: RoutingDecision):
        """Save routing decision to cache."""
        self.cache[cache_key] = (decision, datetime.now())
    
    def _get_execution_method(self, tier: int) -> str:
        """Get execution method name for tier."""
        methods = {
            1: "instant",
            2: "lightweight",
            3: "documented",
            4: "complex"
        }
        return methods.get(tier, "documented")
    
    def _get_estimated_time(self, tier: int) -> str:
        """Get estimated time for tier."""
        times = {
            1: "<2s",
            2: "<10s",
            3: "10-60min",
            4: ">1h"
        }
        return times.get(tier, "unknown")
    
    def get_telemetry(self) -> Dict[str, Any]:
        """Get routing telemetry metrics."""
        return self.telemetry.get_metrics()
    
    def provide_feedback(self, operation: str, expected_tier: int, actual_tier: int):
        """Provide feedback on routing accuracy for learning."""
        self.telemetry.record_feedback(operation, expected_tier, actual_tier)
