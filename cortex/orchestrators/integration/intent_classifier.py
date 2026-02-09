"""
Intent Classifier - Detect user intent and route to MCP tools.

AC_START: AC-INTEGRATION-001
Description: Implement intent classification to route requests to appropriate MCP tools
Authority: ROOT-CAUSE-ANALYSIS-2026-02-08 (P0: Intent Classification Missing)
"""

from enum import Enum
from typing import Optional, Dict, Any
import re


class UserIntent(Enum):
    """User intent types mapped to MCP tools."""
    IMPLEMENT = "IMPLEMENT"  # → cortex_process_request
    FIX = "FIX"  # → cortex_process_request
    REFACTOR = "REFACTOR"  # → cortex_process_request
    ANALYZE = "ANALYZE"  # → cortex_lens_analyze
    AUDIT = "AUDIT"  # → cortex_lens_analyze + cortex_challenge
    PLAN = "PLAN"  # → cortex_plan_setup + cortex_plan_execute
    QUERY = "QUERY"  # → Informational (no tools required)
    UNKNOWN = "UNKNOWN"  # → Requires clarification


class IntentClassifier:
    """
    Classify user intent from natural language request.
    
    Maps requests to MCP tools for proper routing and enforcement.
    """
    
    # Patterns for each intent type (order matters - more specific first)
    PATTERNS = {
        UserIntent.ANALYZE: [
            r'\b(analyze|review|examine|inspect|understand|explain)\b',
            r'\b(why|how|what)\b(?:\s+.*)?(?Union[work, fail]|cause|is)',
            r'\b(audit|scan)\b(?!\s+code)',
        ],
        UserIntent.IMPLEMENT: [
            r'\b(implement|add|create|build|feature|capability)\b',
            r'\b(setup|initialize|configure)\b(?!\s+(test|check))',
        ],
        UserIntent.FIX: [
            r'\b(fix|broken|error|bug|issue|crash|fail)\b',
            r'\b(debug|troubleshoot|diagnose)\b',
            r'(doesn\'t|doesn\'t|not\s+work|broken)',
        ],
        UserIntent.REFACTOR: [
            r'\b(refactor|improve|optimize|clean|simplify|reorganize)\b',
            r'\b(consolidate|unify|standardize)\b',
        ],
        UserIntent.AUDIT: [
            r'\b(audit|compliance|governance|violations)\b',
            r'\b(health\s+check|security\s+scan)\b',
        ],
        UserIntent.PLAN: [
            r'\b(plan|design|architect|strategy)\b',
            r'\b(phase|stage|milestone|roadmap)\b',
        ],
    }
    
    @classmethod
    def classify(cls, user_request: str) -> UserIntent:
        """
        Classify user intent from request text.
        
        Args:
            user_request: User's natural language request
            
        Returns:
            UserIntent enum value
        """
        if not user_request or not user_request.strip():
            return UserIntent.UNKNOWN
        
        request_lower = user_request.lower()
        scores = {}
        
        # Score each intent based on pattern matches
        for intent, patterns in cls.PATTERNS.items():
            score = 0
            for pattern in patterns:
                matches = re.findall(pattern, request_lower, re.IGNORECASE)
                score += len(matches)
            scores[intent] = score
        
        # Return intent with highest score
        if max(scores.values()) > 0:
            best_intent = max(scores, key=lambda x: scores[x])
            return best_intent
        
        return UserIntent.UNKNOWN
    
    @classmethod
    def get_mcp_tool(cls, intent: UserIntent) -> Optional[str]:
        """
        Get recommended MCP tool for intent.
        
        Args:
            intent: User intent
            
        Returns:
            MCP tool name, or None if no tool recommended
        """
        tool_mapping = {
            UserIntent.IMPLEMENT: "cortex_process_request",
            UserIntent.FIX: "cortex_process_request",
            UserIntent.REFACTOR: "cortex_process_request",
            UserIntent.ANALYZE: "cortex_lens_analyze",
            UserIntent.AUDIT: "cortex_lens_analyze",
            UserIntent.PLAN: "cortex_plan_setup",
            UserIntent.QUERY: None,
            UserIntent.UNKNOWN: None,
        }
        return tool_mapping.get(intent)
    
    @classmethod
    def requires_mcp(cls, intent: UserIntent) -> bool:
        """Check if intent requires MCP tool availability."""
        return intent in [
            UserIntent.IMPLEMENT,
            UserIntent.FIX,
            UserIntent.REFACTOR,
            UserIntent.ANALYZE,
            UserIntent.AUDIT,
            UserIntent.PLAN,
        ]
    
    @classmethod
    def requires_tdd(cls, intent: UserIntent) -> bool:
        """Check if intent requires TDD (tests before code)."""
        return intent in [
            UserIntent.IMPLEMENT,
            UserIntent.FIX,
            UserIntent.REFACTOR,
        ]
    
    @classmethod
    def get_enforcement_level(cls, intent: UserIntent) -> str:
        """
        Get enforcement level for intent.
        
        Returns: "BLOCKING" | "WARNING" | "INFO"
        """
        if cls.requires_mcp(intent):
            return "BLOCKING"
        return "INFO"


# AC_COMPLETE: AC-INTEGRATION-001 ✅
