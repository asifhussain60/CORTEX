"""
TDD Intent Router for Natural Language Command Detection

Automatically routes "implement X" requests to TDD workflow,
enforcing test-first development.

Author: Asif Hussain
Created: 2025-11-21
Phase: TDD Mastery Phase 1 Milestone 1.3
"""

import re
from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from enum import Enum


class Intent(Enum):
    """User intent types."""
    IMPLEMENT = "implement"
    FIX = "fix"
    REFACTOR = "refactor"
    TEST = "test"
    PLAN = "plan"
    REVIEW = "review"
    UNKNOWN = "unknown"


@dataclass
class RouteDecision:
    """Routing decision result."""
    intent: Intent
    should_use_tdd: bool
    workflow: str  # "tdd", "fix", "refactor", "standard"
    confidence: float
    reason: str
    extracted_feature: Optional[str] = None


class TDDIntentRouter:
    """Routes user requests to appropriate workflow based on intent."""
    
    # Intent detection patterns
    IMPLEMENT_PATTERNS = [
        r"implement (\w+)",
        r"add (\w+)",
        r"create (\w+)",
        r"build (\w+)",
        r"develop (\w+)",
        r"write (\w+)",
    ]
    
    FIX_PATTERNS = [
        r"fix (\w+)",
        r"repair (\w+)",
        r"resolve (\w+)",
        r"correct (\w+)",
        r"debug (\w+)",
    ]
    
    REFACTOR_PATTERNS = [
        r"refactor (\w+)",
        r"improve (\w+)",
        r"optimize (\w+)",
        r"clean up (\w+)",
        r"restructure (\w+)",
    ]
    
    TEST_PATTERNS = [
        r"test (\w+)",
        r"write tests? for (\w+)",
        r"add tests? for (\w+)",
        r"generate tests? for (\w+)",
    ]
    
    PLAN_PATTERNS = [
        r"plan (\w+)",
        r"design (\w+)",
        r"architect (\w+)",
        r"let's plan (\w+)",
    ]
    
    # TDD enforcement keywords
    TDD_ENFORCEMENT_KEYWORDS = [
        "authentication",
        "authorization",
        "payment",
        "security",
        "critical",
        "production",
    ]
    
    def __init__(self):
        """Initialize TDD intent router."""
        self.enforce_tdd_always = True  # Tier 0 instinct
    
    def route(self, user_request: str) -> RouteDecision:
        """
        Route user request to appropriate workflow.
        
        Args:
            user_request: Natural language user request
            
        Returns:
            RouteDecision with intent, workflow, and reasoning
        """
        request_lower = user_request.lower().strip()
        
        # Detect intent
        intent = self._detect_intent(request_lower)
        
        # Extract feature name
        feature = self._extract_feature(request_lower, intent)
        
        # Determine if TDD should be used
        should_use_tdd = self._should_use_tdd(intent, feature, request_lower)
        
        # Determine workflow
        workflow = self._determine_workflow(intent, should_use_tdd)
        
        # Calculate confidence
        confidence = self._calculate_confidence(intent, feature, should_use_tdd)
        
        # Generate reasoning
        reason = self._generate_reason(intent, should_use_tdd, feature)
        
        return RouteDecision(
            intent=intent,
            should_use_tdd=should_use_tdd,
            workflow=workflow,
            confidence=confidence,
            reason=reason,
            extracted_feature=feature
        )
    
    def _detect_intent(self, request: str) -> Intent:
        """Detect user intent from request."""
        # Check implement patterns
        for pattern in self.IMPLEMENT_PATTERNS:
            if re.search(pattern, request):
                return Intent.IMPLEMENT
        
        # Check fix patterns
        for pattern in self.FIX_PATTERNS:
            if re.search(pattern, request):
                return Intent.FIX
        
        # Check refactor patterns
        for pattern in self.REFACTOR_PATTERNS:
            if re.search(pattern, request):
                return Intent.REFACTOR
        
        # Check test patterns
        for pattern in self.TEST_PATTERNS:
            if re.search(pattern, request):
                return Intent.TEST
        
        # Check plan patterns
        for pattern in self.PLAN_PATTERNS:
            if re.search(pattern, request):
                return Intent.PLAN
        
        return Intent.UNKNOWN
    
    def _extract_feature(self, request: str, intent: Intent) -> Optional[str]:
        """Extract feature name from request."""
        patterns = []
        
        if intent == Intent.IMPLEMENT:
            patterns = self.IMPLEMENT_PATTERNS
        elif intent == Intent.FIX:
            patterns = self.FIX_PATTERNS
        elif intent == Intent.REFACTOR:
            patterns = self.REFACTOR_PATTERNS
        elif intent == Intent.TEST:
            patterns = self.TEST_PATTERNS
        elif intent == Intent.PLAN:
            patterns = self.PLAN_PATTERNS
        
        for pattern in patterns:
            match = re.search(pattern, request)
            if match:
                return match.group(1)
        
        # Try to extract noun phrases
        words = request.split()
        if len(words) >= 2:
            return " ".join(words[1:3])  # Take next 2 words
        
        return None
    
    def _should_use_tdd(self, intent: Intent, feature: Optional[str], request: str) -> bool:
        """Determine if TDD workflow should be used."""
        # TIER 0: TDD_ENFORCEMENT - Always use TDD for IMPLEMENT
        if intent == Intent.IMPLEMENT:
            return True
        
        # TEST intent should use TDD workflow
        if intent == Intent.TEST:
            return True
        
        # REFACTOR should use TDD (test-protected refactoring)
        if intent == Intent.REFACTOR:
            return True
        
        # Check for critical keywords
        if feature and any(keyword in feature.lower() for keyword in self.TDD_ENFORCEMENT_KEYWORDS):
            return True
        
        if any(keyword in request for keyword in self.TDD_ENFORCEMENT_KEYWORDS):
            return True
        
        # FIX might use TDD if adding new functionality
        if intent == Intent.FIX and ("add" in request or "new" in request):
            return True
        
        return False
    
    def _determine_workflow(self, intent: Intent, should_use_tdd: bool) -> str:
        """Determine which workflow to use."""
        if should_use_tdd:
            return "tdd"
        elif intent == Intent.FIX:
            return "fix"
        elif intent == Intent.REFACTOR:
            return "refactor"
        elif intent == Intent.PLAN:
            return "plan"
        else:
            return "standard"
    
    def _calculate_confidence(self, intent: Intent, feature: Optional[str], should_use_tdd: bool) -> float:
        """Calculate confidence in routing decision."""
        confidence = 0.5
        
        # High confidence for clear intents
        if intent in [Intent.IMPLEMENT, Intent.TEST]:
            confidence = 0.95
        elif intent == Intent.FIX:
            confidence = 0.85
        elif intent == Intent.REFACTOR:
            confidence = 0.80
        
        # Boost if feature extracted
        if feature:
            confidence = min(confidence + 0.05, 1.0)
        
        # Boost if TDD enforcement keywords present
        if should_use_tdd and intent == Intent.IMPLEMENT:
            confidence = min(confidence + 0.05, 1.0)
        
        return confidence
    
    def _generate_reason(self, intent: Intent, should_use_tdd: bool, feature: Optional[str]) -> str:
        """Generate human-readable reasoning."""
        reasons = []
        
        # Intent reason
        if intent == Intent.IMPLEMENT:
            reasons.append("Detected IMPLEMENT intent")
        elif intent == Intent.FIX:
            reasons.append("Detected FIX intent")
        elif intent == Intent.REFACTOR:
            reasons.append("Detected REFACTOR intent")
        elif intent == Intent.TEST:
            reasons.append("Detected TEST intent")
        
        # Feature reason
        if feature:
            reasons.append(f"Feature: '{feature}'")
        
        # TDD reason
        if should_use_tdd:
            if intent == Intent.IMPLEMENT:
                reasons.append("TDD enforced (Tier 0 instinct: TDD_ENFORCEMENT)")
            elif intent == Intent.REFACTOR:
                reasons.append("TDD enforced (test-protected refactoring)")
            elif feature and any(kw in feature.lower() for kw in self.TDD_ENFORCEMENT_KEYWORDS):
                reasons.append(f"TDD enforced (critical feature: {feature})")
            else:
                reasons.append("TDD recommended")
        else:
            reasons.append("TDD not required for this workflow")
        
        return " | ".join(reasons)
    
    def format_tdd_workflow_message(self, decision: RouteDecision) -> str:
        """Format user-facing message for TDD workflow activation."""
        if not decision.should_use_tdd:
            return ""
        
        feature = decision.extracted_feature or "this feature"
        
        message = f"""
🧪 **TDD Workflow Activated**

**Feature:** {feature}
**Intent:** {decision.intent.value.upper()}
**Confidence:** {decision.confidence:.0%}
**Reason:** {decision.reason}

**Workflow Steps:**
1. ❌ **RED Phase:** Generate failing test
2. ✅ **GREEN Phase:** Implement minimal code to pass
3. 🔄 **REFACTOR Phase:** Improve code quality
4. ✔️ **VALIDATE:** Check Definition of Done

Let's start with RED phase - I'll generate a failing test first.
"""
        return message.strip()
