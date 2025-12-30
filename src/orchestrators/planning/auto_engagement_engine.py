"""
Auto-Engagement Engine

Purpose: Automatically determine if user request requires planning based on complexity.
Author: Asif Hussain
Created: 2025-12-30
Version: 1.0.0

Gap Addressed: GAP 2 - Planning Orchestrator Auto-Engagement
- Previous: Manual trigger required (/CORTEX Plan, create a plan)
- New: Automatic engagement based on complexity score

Features:
- Multi-factor complexity analysis (LOC, domains, security, architecture, history)
- Automatic planning engagement for HIGH/CRITICAL complexity
- User override support ("implement without planning")
- Complexity threshold calibration
"""

import logging
import re
from dataclasses import dataclass, field
from datetime import datetime
from enum import IntEnum
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


# ============================================================================
# Plan Complexity Levels
# ============================================================================

class PlanComplexity(IntEnum):
    """Plan complexity tiers for adaptive planning."""
    LOW = 1          # Inline implementation (no planning needed)
    MEDIUM = 2       # Conditional plan (brief planning)
    HIGH = 3         # Incremental plan (detailed planning)
    CRITICAL = 4     # Full plan with security analysis


@dataclass
class EngagementDecision:
    """Result of auto-engagement analysis."""
    should_engage: bool
    complexity: PlanComplexity
    complexity_score: float
    reasoning: str
    factors: List[Dict[str, Any]] = field(default_factory=list)
    override_detected: bool = False
    timestamp: datetime = field(default_factory=datetime.now)


# ============================================================================
# Auto-Engagement Engine
# ============================================================================

class AutoEngagementEngine:
    """
    Automatically determines if user request requires planning.
    
    Decision Factors (weighted):
    1. Estimated LOC (30% weight)
    2. Number of domains involved (25% weight)
    3. Security/data sensitivity (20% weight)
    4. Architectural changes (15% weight)
    5. Historical failure rate (10% weight)
    
    Thresholds:
    - LOW (0.0-0.3): Inline implementation
    - MEDIUM (0.3-0.6): Conditional planning
    - HIGH (0.6-0.85): Incremental planning
    - CRITICAL (0.85-1.0): Full planning with security review
    
    Usage:
        engine = AutoEngagementEngine()
        decision = engine.should_auto_engage_planning(
            user_message="implement OAuth2 with RBAC",
            context={}
        )
        if decision.should_engage:
            print(f"Auto-engaging planning: {decision.reasoning}")
    """
    
    # Complexity thresholds
    COMPLEXITY_THRESHOLDS = {
        PlanComplexity.LOW: 0.3,
        PlanComplexity.MEDIUM: 0.6,
        PlanComplexity.HIGH: 0.85,
        PlanComplexity.CRITICAL: 1.0
    }
    
    # Factor weights (must sum to 1.0)
    FACTOR_WEIGHTS = {
        "estimated_loc": 0.30,
        "multi_domain": 0.25,
        "security": 0.20,
        "architecture": 0.15,
        "history": 0.10
    }
    
    # Domain keywords for detection
    DOMAIN_KEYWORDS = {
        "auth": ["authentication", "login", "oauth", "jwt", "token", "session", "password", "credentials"],
        "database": ["database", "sql", "orm", "migration", "schema", "table", "query", "postgres", "mysql"],
        "frontend": ["frontend", "ui", "react", "component", "css", "html", "view", "page", "form"],
        "backend": ["backend", "api", "endpoint", "service", "controller", "rest", "graphql"],
        "security": ["security", "encryption", "ssl", "tls", "firewall", "permission", "rbac", "acl"],
        "infrastructure": ["infrastructure", "docker", "kubernetes", "cloud", "aws", "azure", "deploy"],
        "testing": ["testing", "test", "unit", "integration", "e2e", "coverage", "mock"],
        "performance": ["performance", "cache", "optimize", "scale", "load", "throughput", "latency"],
    }
    
    # Security-sensitive keywords
    SECURITY_KEYWORDS = [
        "authentication", "authorization", "password", "credential", "secret", "token",
        "encryption", "decrypt", "ssl", "tls", "certificate", "rbac", "acl", "permission",
        "sensitive", "pii", "gdpr", "compliance", "audit", "security", "vulnerability"
    ]
    
    # Architecture keywords
    ARCHITECTURE_KEYWORDS = [
        "architecture", "redesign", "microservice", "monolith", "refactor entire",
        "restructure", "migrate", "rewrite", "new system", "platform", "framework",
        "integration", "api gateway", "message queue", "event driven", "cqrs"
    ]
    
    # Override patterns (user explicitly wants to skip planning)
    OVERRIDE_PATTERNS = [
        r'without plan',
        r'no plan',
        r'skip plan',
        r'just implement',
        r'directly implement',
        r'quick fix',
        r'simple fix',
        r'don\'t plan',
        r'--no-plan',
    ]

    def __init__(
        self,
        llm_client=None,
        engagement_threshold: float = 0.3,  # Engage for MEDIUM and above
        enable_history_factor: bool = True
    ):
        """
        Initialize Auto-Engagement Engine.
        
        Args:
            llm_client: Optional LLM client for advanced analysis
            engagement_threshold: Minimum score to trigger planning (default: 0.3)
            enable_history_factor: Include historical failure rate in analysis
        """
        self.llm_client = llm_client
        self.engagement_threshold = engagement_threshold
        self.enable_history_factor = enable_history_factor
        
        # Telemetry
        self._total_analyses = 0
        self._engagements = 0
        self._overrides = 0
        
        logger.info(
            f"🎭 Auto-Engagement Engine initialized: "
            f"threshold={engagement_threshold}, history={enable_history_factor}"
        )

    def should_auto_engage_planning(
        self,
        user_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> EngagementDecision:
        """
        Determine if planning should auto-engage for the request.
        
        Args:
            user_message: User's natural language message
            context: Optional context (past failures, workspace info, etc.)
            
        Returns:
            EngagementDecision with should_engage, complexity, and reasoning
        """
        self._total_analyses += 1
        context = context or {}
        factors = []
        
        # Check for override patterns first
        if self._check_override(user_message):
            self._overrides += 1
            return EngagementDecision(
                should_engage=False,
                complexity=PlanComplexity.LOW,
                complexity_score=0.0,
                reasoning="User requested to skip planning",
                override_detected=True
            )
        
        # Calculate complexity score
        complexity_score, factors = self._calculate_complexity_score(
            user_message, context
        )
        
        # Map score to complexity level
        complexity = self._map_to_complexity(complexity_score)
        
        # Determine engagement
        should_engage = complexity_score >= self.engagement_threshold
        
        if should_engage:
            self._engagements += 1
        
        # Generate reasoning
        reasoning = self._generate_reasoning(
            complexity_score, complexity, factors, should_engage
        )
        
        logger.info(
            f"🎯 Auto-engagement analysis: score={complexity_score:.2f}, "
            f"complexity={complexity.name}, engage={should_engage}"
        )
        
        return EngagementDecision(
            should_engage=should_engage,
            complexity=complexity,
            complexity_score=complexity_score,
            reasoning=reasoning,
            factors=factors
        )

    def _calculate_complexity_score(
        self,
        user_message: str,
        context: Dict[str, Any]
    ) -> Tuple[float, List[Dict[str, Any]]]:
        """
        Calculate complexity score using multiple factors.
        
        Returns:
            (score, list of factor contributions)
        """
        score = 0.0
        factors = []
        message_lower = user_message.lower()
        
        # Factor 1: Estimated LOC (30% weight)
        loc_score, loc_factor = self._analyze_loc(message_lower)
        score += loc_score * self.FACTOR_WEIGHTS["estimated_loc"]
        factors.append(loc_factor)
        
        # Factor 2: Multi-domain (25% weight)
        domain_score, domain_factor = self._analyze_domains(message_lower)
        score += domain_score * self.FACTOR_WEIGHTS["multi_domain"]
        factors.append(domain_factor)
        
        # Factor 3: Security implications (20% weight)
        security_score, security_factor = self._analyze_security(message_lower)
        score += security_score * self.FACTOR_WEIGHTS["security"]
        factors.append(security_factor)
        
        # Factor 4: Architecture changes (15% weight)
        arch_score, arch_factor = self._analyze_architecture(message_lower)
        score += arch_score * self.FACTOR_WEIGHTS["architecture"]
        factors.append(arch_factor)
        
        # Factor 5: Historical failures (10% weight)
        if self.enable_history_factor:
            history_score, history_factor = self._analyze_history(context)
            score += history_score * self.FACTOR_WEIGHTS["history"]
            factors.append(history_factor)
        
        return min(score, 1.0), factors

    def _analyze_loc(self, message: str) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze estimated lines of code.
        
        Returns:
            (normalized_score, factor_details)
        """
        # LOC indicators
        high_loc_keywords = [
            "entire", "full", "complete", "comprehensive", "all", "system",
            "platform", "framework", "module", "service layer", "data layer"
        ]
        medium_loc_keywords = [
            "feature", "module", "component", "service", "controller",
            "endpoint", "page", "form", "workflow"
        ]
        low_loc_keywords = [
            "fix", "update", "change", "modify", "tweak", "adjust",
            "rename", "move", "add field", "add method"
        ]
        
        # Count keyword matches
        high_matches = sum(1 for kw in high_loc_keywords if kw in message)
        medium_matches = sum(1 for kw in medium_loc_keywords if kw in message)
        low_matches = sum(1 for kw in low_loc_keywords if kw in message)
        
        # Calculate score
        if high_matches >= 2:
            score = 1.0
            estimated_loc = "500+ lines"
        elif high_matches >= 1 or medium_matches >= 3:
            score = 0.7
            estimated_loc = "200-500 lines"
        elif medium_matches >= 1:
            score = 0.4
            estimated_loc = "50-200 lines"
        else:
            score = 0.1
            estimated_loc = "<50 lines"
        
        return score, {
            "factor": "estimated_loc",
            "score": score,
            "weight": self.FACTOR_WEIGHTS["estimated_loc"],
            "contribution": score * self.FACTOR_WEIGHTS["estimated_loc"],
            "details": {
                "estimated_loc": estimated_loc,
                "high_matches": high_matches,
                "medium_matches": medium_matches,
                "low_matches": low_matches
            }
        }

    def _analyze_domains(self, message: str) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze number of technical domains involved.
        
        Returns:
            (normalized_score, factor_details)
        """
        detected_domains = []
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            if any(kw in message for kw in keywords):
                detected_domains.append(domain)
        
        domain_count = len(detected_domains)
        
        # Score based on domain count
        if domain_count >= 4:
            score = 1.0
        elif domain_count == 3:
            score = 0.8
        elif domain_count == 2:
            score = 0.5
        elif domain_count == 1:
            score = 0.2
        else:
            score = 0.0
        
        return score, {
            "factor": "multi_domain",
            "score": score,
            "weight": self.FACTOR_WEIGHTS["multi_domain"],
            "contribution": score * self.FACTOR_WEIGHTS["multi_domain"],
            "details": {
                "domain_count": domain_count,
                "detected_domains": detected_domains
            }
        }

    def _analyze_security(self, message: str) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze security implications.
        
        Returns:
            (normalized_score, factor_details)
        """
        security_matches = [
            kw for kw in self.SECURITY_KEYWORDS
            if kw in message
        ]
        
        match_count = len(security_matches)
        
        # Score based on security keyword count
        if match_count >= 3:
            score = 1.0
        elif match_count == 2:
            score = 0.8
        elif match_count == 1:
            score = 0.5
        else:
            score = 0.0
        
        return score, {
            "factor": "security",
            "score": score,
            "weight": self.FACTOR_WEIGHTS["security"],
            "contribution": score * self.FACTOR_WEIGHTS["security"],
            "details": {
                "security_keywords": security_matches,
                "match_count": match_count
            }
        }

    def _analyze_architecture(self, message: str) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze architectural change implications.
        
        Returns:
            (normalized_score, factor_details)
        """
        arch_matches = [
            kw for kw in self.ARCHITECTURE_KEYWORDS
            if kw in message
        ]
        
        match_count = len(arch_matches)
        
        # Score based on architecture keyword count
        if match_count >= 2:
            score = 1.0
        elif match_count == 1:
            score = 0.6
        else:
            score = 0.0
        
        return score, {
            "factor": "architecture",
            "score": score,
            "weight": self.FACTOR_WEIGHTS["architecture"],
            "contribution": score * self.FACTOR_WEIGHTS["architecture"],
            "details": {
                "architecture_keywords": arch_matches,
                "match_count": match_count
            }
        }

    def _analyze_history(
        self,
        context: Dict[str, Any]
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Analyze historical failure rate without planning.
        
        Returns:
            (normalized_score, factor_details)
        """
        past_failures = context.get("past_failures", [])
        
        # Count failures without planning
        failures_without_plan = sum(
            1 for f in past_failures
            if not f.get("had_plan", True) and f.get("failed", False)
        )
        
        total_similar = len(past_failures)
        
        if total_similar == 0:
            score = 0.0
        else:
            failure_rate = failures_without_plan / total_similar
            score = min(failure_rate, 1.0)
        
        return score, {
            "factor": "history",
            "score": score,
            "weight": self.FACTOR_WEIGHTS["history"],
            "contribution": score * self.FACTOR_WEIGHTS["history"],
            "details": {
                "failures_without_plan": failures_without_plan,
                "total_similar_tasks": total_similar
            }
        }

    def _check_override(self, message: str) -> bool:
        """Check if user wants to skip planning."""
        message_lower = message.lower()
        
        for pattern in self.OVERRIDE_PATTERNS:
            if re.search(pattern, message_lower, re.IGNORECASE):
                return True
        
        return False

    def _map_to_complexity(self, score: float) -> PlanComplexity:
        """Map complexity score to PlanComplexity enum."""
        if score >= self.COMPLEXITY_THRESHOLDS[PlanComplexity.HIGH]:
            return PlanComplexity.CRITICAL
        elif score >= self.COMPLEXITY_THRESHOLDS[PlanComplexity.MEDIUM]:
            return PlanComplexity.HIGH
        elif score >= self.COMPLEXITY_THRESHOLDS[PlanComplexity.LOW]:
            return PlanComplexity.MEDIUM
        else:
            return PlanComplexity.LOW

    def _generate_reasoning(
        self,
        score: float,
        complexity: PlanComplexity,
        factors: List[Dict[str, Any]],
        should_engage: bool
    ) -> str:
        """Generate human-readable reasoning for the decision."""
        # Find top contributing factors
        sorted_factors = sorted(
            factors,
            key=lambda f: f.get("contribution", 0),
            reverse=True
        )
        
        top_factors = [
            f["factor"].replace("_", " ").title()
            for f in sorted_factors[:3]
            if f.get("contribution", 0) > 0.05
        ]
        
        if should_engage:
            if complexity == PlanComplexity.CRITICAL:
                return (
                    f"🚨 CRITICAL complexity detected (score: {score:.2f}). "
                    f"Key factors: {', '.join(top_factors)}. "
                    f"Full planning with security review required."
                )
            elif complexity == PlanComplexity.HIGH:
                return (
                    f"⚠️ HIGH complexity detected (score: {score:.2f}). "
                    f"Key factors: {', '.join(top_factors)}. "
                    f"Detailed incremental planning recommended."
                )
            else:
                return (
                    f"📋 MEDIUM complexity detected (score: {score:.2f}). "
                    f"Key factors: {', '.join(top_factors)}. "
                    f"Brief planning recommended."
                )
        else:
            return (
                f"✅ LOW complexity (score: {score:.2f}). "
                f"Inline implementation appropriate."
            )

    def get_telemetry(self) -> Dict[str, Any]:
        """Get engine telemetry."""
        return {
            "total_analyses": self._total_analyses,
            "engagements": self._engagements,
            "overrides": self._overrides,
            "engagement_rate": (
                self._engagements / self._total_analyses
                if self._total_analyses > 0 else 0
            ),
            "override_rate": (
                self._overrides / self._total_analyses
                if self._total_analyses > 0 else 0
            )
        }


# ============================================================================
# Integration Helper
# ============================================================================

def create_auto_engagement_engine(
    llm_client=None,
    engagement_threshold: float = 0.3
) -> AutoEngagementEngine:
    """
    Factory function to create auto-engagement engine.
    
    Args:
        llm_client: Optional LLM client for advanced analysis
        engagement_threshold: Minimum score to trigger planning
        
    Returns:
        Configured AutoEngagementEngine instance
    """
    return AutoEngagementEngine(
        llm_client=llm_client,
        engagement_threshold=engagement_threshold
    )
