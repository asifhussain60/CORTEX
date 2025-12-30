"""
LLM-Based Intent Classifier

Purpose: Replace regex-based intent routing with semantic LLM classification.
Author: Asif Hussain
Created: 2025-12-30
Version: 1.0.0

Gap Addressed: GAP 1 - Intent Router Quality
- Previous: Keyword matching with 140+ static patterns
- New: LLM-powered semantic understanding with fallback to regex

Features:
- Semantic understanding (handles synonyms, context, typos)
- Few-shot learning from historical patterns
- Confidence scoring with explainability
- Regex fallback for offline mode
- Response caching (5-minute TTL)
"""

import json
import logging
import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Intent Types
# ============================================================================

class IntentType(Enum):
    """Available intent types for classification."""
    PLAN = "plan"
    CODE = "code"
    DEBUG = "debug"
    TEST = "test"
    REFINE = "refine"
    REVIEW = "review"
    SANITIZE = "sanitize"
    MAINTAIN = "maintain"
    ADO = "ado"
    HELP = "help"
    UNKNOWN = "unknown"


@dataclass
class IntentClassificationResult:
    """Result of intent classification."""
    intent: IntentType
    confidence: float
    reasoning: str
    secondary_intents: List[IntentType] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    classification_method: str = "llm"  # "llm" or "regex_fallback"
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# Cache Entry
# ============================================================================

@dataclass
class CacheEntry:
    """Cached classification result."""
    result: IntentClassificationResult
    created_at: datetime
    ttl_seconds: int = 300  # 5 minutes
    
    def is_expired(self) -> bool:
        """Check if cache entry has expired."""
        age = (datetime.now() - self.created_at).total_seconds()
        return age > self.ttl_seconds


# ============================================================================
# LLM Intent Classifier
# ============================================================================

class LLMIntentClassifier:
    """
    LLM-powered intent classifier using GPT-4/Claude.
    
    Features:
    - Semantic understanding (handles synonyms, context)
    - Few-shot learning from historical patterns
    - Confidence scoring with explainability
    - Fallback to regex for offline mode
    
    Usage:
        classifier = LLMIntentClassifier(llm_client=openai_client)
        result = classifier.classify("implement OAuth2 authentication")
        print(result.intent)  # IntentType.CODE
        print(result.confidence)  # 0.95
    """
    
    # LLM prompt for intent classification
    INTENT_CLASSIFICATION_PROMPT = """You are CORTEX, an AI assistant analyzing user requests to determine intent.

## Available Intents

1. **PLAN** - User wants to create a structured plan, design architecture, or strategize
   - Keywords: plan, design, architect, strategy, roadmap, breakdown, organize
   - Examples: "create a plan for...", "how should I approach...", "design the architecture"

2. **CODE** - User wants to write, modify, or implement code
   - Keywords: implement, build, create, code, develop, add feature
   - Examples: "implement authentication", "build the API endpoint", "create a service"

3. **DEBUG** - User wants to fix issues, investigate bugs, or troubleshoot
   - Keywords: debug, fix, troubleshoot, investigate, error, bug, issue
   - Examples: "why is this failing?", "fix the authentication bug", "investigate the crash"

4. **TEST** - User wants to write tests, do TDD, or validate functionality
   - Keywords: test, TDD, validation, coverage, unit test, integration test
   - Examples: "write tests for...", "start TDD", "run tests"

5. **REFINE** - User wants to improve, refactor, or optimize existing code
   - Keywords: refactor, optimize, improve, enhance, clean up, performance
   - Examples: "refactor the service", "optimize the query", "improve code quality"

6. **REVIEW** - User wants code review, analysis, or architectural assessment
   - Keywords: review, analyze, assess, audit, evaluate, check
   - Examples: "review this code", "analyze the architecture", "audit security"

7. **SANITIZE** - User wants to remove sensitive data, anonymize, or clean code
   - Keywords: sanitize, anonymize, clean, remove secrets, redact
   - Examples: "sanitize the codebase", "remove company data", "anonymize"

8. **MAINTAIN** - User wants system maintenance, health checks, or housekeeping
   - Keywords: maintenance, health check, monitor, cleanup, vacuum
   - Examples: "system maintenance", "health check", "run diagnostics"

9. **ADO** - User wants Azure DevOps operations (work items, stories, features)
   - Keywords: ado, story, feature, work item, epic, task, backlog
   - Examples: "create ADO story", "plan ado feature", "add work item"

10. **HELP** - User wants help, documentation, or information about CORTEX
    - Keywords: help, commands, how to, what is, documentation
    - Examples: "show commands", "help", "how do I use CORTEX?"

## User Request
"{user_message}"

## Instructions
Analyze the user request and determine the PRIMARY intent. Consider context, synonyms, and implicit meanings.

Respond with valid JSON (no markdown code blocks):
{{
  "intent": "PLAN|CODE|DEBUG|TEST|REFINE|REVIEW|SANITIZE|MAINTAIN|ADO|HELP|UNKNOWN",
  "confidence": 0.0-1.0,
  "reasoning": "Explain why this intent was chosen (1-2 sentences)",
  "secondary_intents": ["optional", "list", "if", "multiple", "intents", "detected"]
}}

IMPORTANT: 
- High confidence (>0.9) for clear, explicit intents
- Medium confidence (0.7-0.9) for implicit but likely intents  
- Low confidence (<0.7) for ambiguous requests
- Always provide reasoning"""

    # Regex patterns for fallback (when LLM unavailable)
    FALLBACK_PATTERNS = {
        IntentType.PLAN: [
            r'\b(plan|planning|design|architect|strategy|roadmap|breakdown)\b',
            r'\b(how should i|what\'s the best way to|help me organize)\b',
            r'\bcreate a plan\b',
            r'\blet\'s plan\b',
        ],
        IntentType.CODE: [
            r'\b(implement|build|create|code|develop|add)\b.*\b(feature|module|service|class|function)\b',
            r'\b(implement|build|create|code|develop)\b',
        ],
        IntentType.DEBUG: [
            r'\b(debug|fix|troubleshoot|investigate|error|bug|issue|crash)\b',
            r'\b(why is|what\'s wrong|not working)\b',
        ],
        IntentType.TEST: [
            r'\b(test|tdd|validation|coverage|unit test|integration test)\b',
            r'\b(start tdd|run tests|write tests)\b',
        ],
        IntentType.REFINE: [
            r'\b(refactor|optimize|improve|enhance|clean up|performance)\b',
        ],
        IntentType.REVIEW: [
            r'\b(review|analyze|assess|audit|evaluate|check)\b.*\b(code|architecture|security)\b',
        ],
        IntentType.SANITIZE: [
            r'\b(sanitize|anonymize|clean|remove secrets|redact)\b',
            r'\b(make generic|remove company)\b',
        ],
        IntentType.MAINTAIN: [
            r'\b(maintenance|health check|monitor|cleanup|vacuum|diagnostics)\b',
            r'\b(system maintenance|run diagnostics)\b',
        ],
        IntentType.ADO: [
            r'\b(ado|azure devops|work item|story|feature|epic|backlog)\b',
            r'\bplan ado\b',
        ],
        IntentType.HELP: [
            r'\b(help|commands|how to|what is|documentation)\b',
            r'\bshow commands\b',
        ],
    }

    def __init__(
        self,
        llm_client=None,
        cache_enabled: bool = True,
        cache_ttl_seconds: int = 300,
        fallback_enabled: bool = True
    ):
        """
        Initialize LLM Intent Classifier.
        
        Args:
            llm_client: LLM client for API calls (OpenAI, Claude, etc.)
            cache_enabled: Enable response caching
            cache_ttl_seconds: Cache TTL in seconds (default: 5 minutes)
            fallback_enabled: Enable regex fallback when LLM unavailable
        """
        self.llm_client = llm_client
        self.cache_enabled = cache_enabled
        self.cache_ttl_seconds = cache_ttl_seconds
        self.fallback_enabled = fallback_enabled
        
        # Response cache
        self._cache: Dict[str, CacheEntry] = {}
        
        # Telemetry
        self._total_classifications = 0
        self._llm_classifications = 0
        self._fallback_classifications = 0
        self._cache_hits = 0
        
        logger.info(
            f"🎭 LLM Intent Classifier initialized: "
            f"LLM={'enabled' if llm_client else 'disabled'}, "
            f"Cache={'enabled' if cache_enabled else 'disabled'}, "
            f"Fallback={'enabled' if fallback_enabled else 'disabled'}"
        )

    def classify(self, user_message: str) -> IntentClassificationResult:
        """
        Classify user message to determine intent.
        
        Process:
        1. Check cache for previous classification
        2. Attempt LLM classification
        3. Fall back to regex if LLM fails
        
        Args:
            user_message: User's natural language message
            
        Returns:
            IntentClassificationResult with intent, confidence, and metadata
        """
        self._total_classifications += 1
        start_time = time.perf_counter()
        
        # Normalize message
        normalized_message = self._normalize_message(user_message)
        cache_key = self._get_cache_key(normalized_message)
        
        # Step 1: Check cache
        if self.cache_enabled:
            cached_result = self._get_from_cache(cache_key)
            if cached_result:
                self._cache_hits += 1
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.info(
                    f"🎯 Intent classification (CACHED): {cached_result.intent.value} "
                    f"[{cached_result.confidence:.0%}] in {elapsed_ms:.1f}ms"
                )
                return cached_result
        
        # Step 2: Attempt LLM classification
        if self.llm_client:
            try:
                result = self._llm_classify(normalized_message)
                self._llm_classifications += 1
                
                # Cache result
                if self.cache_enabled:
                    self._save_to_cache(cache_key, result)
                
                elapsed_ms = (time.perf_counter() - start_time) * 1000
                logger.info(
                    f"🎯 Intent classification (LLM): {result.intent.value} "
                    f"[{result.confidence:.0%}] in {elapsed_ms:.1f}ms"
                )
                return result
                
            except Exception as e:
                logger.warning(f"LLM classification failed: {e}. Using fallback.")
        
        # Step 3: Fallback to regex
        if self.fallback_enabled:
            result = self._regex_fallback(normalized_message)
            self._fallback_classifications += 1
            
            # Cache fallback result
            if self.cache_enabled:
                self._save_to_cache(cache_key, result)
            
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            logger.info(
                f"🎯 Intent classification (FALLBACK): {result.intent.value} "
                f"[{result.confidence:.0%}] in {elapsed_ms:.1f}ms"
            )
            return result
        
        # No classification possible
        return IntentClassificationResult(
            intent=IntentType.UNKNOWN,
            confidence=0.0,
            reasoning="Unable to classify: LLM unavailable and fallback disabled",
            classification_method="none"
        )

    def _llm_classify(self, message: str) -> IntentClassificationResult:
        """
        Classify using LLM API call.
        
        Args:
            message: Normalized user message
            
        Returns:
            IntentClassificationResult from LLM
        """
        prompt = self.INTENT_CLASSIFICATION_PROMPT.format(user_message=message)
        
        # Call LLM API
        response = self.llm_client.generate(
            prompt=prompt,
            temperature=0.2,  # Low temp for consistency
            max_tokens=300
        )
        
        # Parse JSON response
        try:
            # Handle potential markdown code blocks in response
            response_text = response.strip()
            if response_text.startswith("```"):
                # Extract JSON from markdown code block
                json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', response_text)
                if json_match:
                    response_text = json_match.group(1)
            
            result = json.loads(response_text)
            
            # Map intent string to enum
            intent_str = result.get("intent", "UNKNOWN").upper()
            try:
                intent = IntentType[intent_str]
            except KeyError:
                intent = IntentType.UNKNOWN
            
            # Map secondary intents
            secondary_intents = []
            for si in result.get("secondary_intents", []):
                try:
                    secondary_intents.append(IntentType[si.upper()])
                except KeyError:
                    pass
            
            return IntentClassificationResult(
                intent=intent,
                confidence=float(result.get("confidence", 0.5)),
                reasoning=result.get("reasoning", ""),
                secondary_intents=secondary_intents,
                metadata={"raw_response": result},
                classification_method="llm"
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse LLM response as JSON: {e}")
            raise

    def _regex_fallback(self, message: str) -> IntentClassificationResult:
        """
        Classify using regex patterns (fallback).
        
        Args:
            message: Normalized user message
            
        Returns:
            IntentClassificationResult from regex matching
        """
        message_lower = message.lower()
        
        # Score each intent by pattern matches
        intent_scores: Dict[IntentType, Tuple[int, List[str]]] = {}
        
        for intent, patterns in self.FALLBACK_PATTERNS.items():
            matches = []
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    matches.append(pattern)
            
            if matches:
                intent_scores[intent] = (len(matches), matches)
        
        # Find best match
        if intent_scores:
            best_intent = max(intent_scores.items(), key=lambda x: x[1][0])
            intent = best_intent[0]
            match_count = best_intent[1][0]
            matched_patterns = best_intent[1][1]
            
            # Calculate confidence based on match quality
            confidence = min(0.5 + (match_count * 0.15), 0.85)  # Max 85% for regex
            
            # Find secondary intents
            secondary = [
                i for i, (count, _) in intent_scores.items()
                if i != intent and count > 0
            ]
            
            return IntentClassificationResult(
                intent=intent,
                confidence=confidence,
                reasoning=f"Matched patterns: {matched_patterns[:3]}",
                secondary_intents=secondary[:2],
                metadata={"matched_patterns": matched_patterns},
                classification_method="regex_fallback"
            )
        
        # No matches
        return IntentClassificationResult(
            intent=IntentType.UNKNOWN,
            confidence=0.3,
            reasoning="No patterns matched",
            classification_method="regex_fallback"
        )

    def _normalize_message(self, message: str) -> str:
        """Normalize user message for classification."""
        # Remove meta-directives
        normalized = re.sub(r'follow instructions in.*?\.md', '', message, flags=re.IGNORECASE)
        normalized = re.sub(r'use \*\.prompt\.md', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'reference file:///.*?\s', '', normalized, flags=re.IGNORECASE)
        normalized = re.sub(r'#file:\S+', '', normalized)  # Remove #file: references
        
        # Trim whitespace
        normalized = ' '.join(normalized.split())
        
        return normalized

    def _get_cache_key(self, message: str) -> str:
        """Generate cache key from message."""
        # Simple hash for cache key
        return str(hash(message.lower().strip()))

    def _get_from_cache(self, cache_key: str) -> Optional[IntentClassificationResult]:
        """Get result from cache if not expired."""
        if cache_key in self._cache:
            entry = self._cache[cache_key]
            if not entry.is_expired():
                return entry.result
            else:
                # Remove expired entry
                del self._cache[cache_key]
        return None

    def _save_to_cache(self, cache_key: str, result: IntentClassificationResult):
        """Save result to cache."""
        self._cache[cache_key] = CacheEntry(
            result=result,
            created_at=datetime.now(),
            ttl_seconds=self.cache_ttl_seconds
        )
        
        # Limit cache size (LRU-like cleanup)
        if len(self._cache) > 1000:
            # Remove oldest entries
            sorted_entries = sorted(
                self._cache.items(),
                key=lambda x: x[1].created_at
            )
            for key, _ in sorted_entries[:100]:
                del self._cache[key]

    def get_telemetry(self) -> Dict[str, Any]:
        """Get classification telemetry."""
        return {
            "total_classifications": self._total_classifications,
            "llm_classifications": self._llm_classifications,
            "fallback_classifications": self._fallback_classifications,
            "cache_hits": self._cache_hits,
            "cache_hit_rate": (
                self._cache_hits / self._total_classifications
                if self._total_classifications > 0 else 0
            ),
            "llm_rate": (
                self._llm_classifications / self._total_classifications
                if self._total_classifications > 0 else 0
            ),
            "cache_size": len(self._cache)
        }

    def clear_cache(self):
        """Clear the classification cache."""
        self._cache.clear()
        logger.info("🧹 Intent classification cache cleared")


# ============================================================================
# Integration Helper
# ============================================================================

def create_intent_classifier(
    llm_client=None,
    enable_llm: bool = True,
    enable_cache: bool = True,
    enable_fallback: bool = True
) -> LLMIntentClassifier:
    """
    Factory function to create intent classifier with configuration.
    
    Args:
        llm_client: Optional LLM client (will try to create default if None and enable_llm=True)
        enable_llm: Enable LLM classification
        enable_cache: Enable response caching
        enable_fallback: Enable regex fallback
        
    Returns:
        Configured LLMIntentClassifier instance
    """
    client = None
    
    if enable_llm and llm_client is None:
        # Try to create default LLM client
        try:
            from src.llm.client import create_llm_client
            client = create_llm_client()
            logger.info("✅ Created default LLM client for intent classification")
        except ImportError:
            logger.warning("LLM client module not available. Using fallback only.")
        except Exception as e:
            logger.warning(f"Failed to create LLM client: {e}. Using fallback only.")
    elif llm_client is not None:
        client = llm_client
    
    return LLMIntentClassifier(
        llm_client=client,
        cache_enabled=enable_cache,
        fallback_enabled=enable_fallback
    )
