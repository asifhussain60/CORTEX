"""
Challenge Engine (Phase 48 Stage 2)

Generates 3 alternative approaches for IMPLEMENT/FIX/REFACTOR requests with:
- Pros/cons analysis
- Effort estimation
- Feasibility ranking
- Recommendation explanation

Author: Asif Hussain
Authority: PHASE-48-IMPLEMENTATION-PLAN.yaml Stage 2
Priority: P0-CRITICAL
AC-ID: AC-PHASE48-S2-IMPL-001
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any
from enum import Enum
import logging
from cortex.core.orchestrator_protocol_mixin import OrchestratorProtocolMixin


logger = logging.getLogger(__name__)


# ============================================================================
# DATA STRUCTURES
# ============================================================================

@dataclass
class AlternativeApproach:
    """A single alternative approach with analysis.
    
    Attributes:
        title: Short title (e.g., "OAuth 2.0 with PKCE")
        description: Detailed description of the approach
        pros: List of advantages (minimum 2)
        cons: List of disadvantages (minimum 2)
        estimated_effort: Time estimate (e.g., "2 days", "1 week")
        feasibility_score: Score from 0.0 (low) to 1.0 (high)
        implementation_notes: Optional technical details
    """
    title: str
    description: str
    pros: List[str]
    cons: List[str]
    estimated_effort: str
    feasibility_score: float
    implementation_notes: str = ""


@dataclass
class Challenge:
    """Challenge with multiple alternative approaches.
    
    Attributes:
        original_request: User's original request
        intent: IMPLEMENT/FIX/REFACTOR
        alternatives: List of 3 alternative approaches (sorted by feasibility)
        recommendation_explanation: Why the first alternative is recommended
    """
    original_request: str
    intent: str
    alternatives: List[AlternativeApproach]
    recommendation_explanation: str


# ============================================================================
# CHALLENGE ENGINE
# ============================================================================

class ChallengeEngine(OrchestratorProtocolMixin):
    """Generates alternative approaches for implementation requests.
    
    Flow:
    1. Analyze request and intent
    2. Generate 3 diverse alternatives
    3. Analyze pros/cons for each
    4. Estimate effort
    5. Calculate feasibility scores
    6. Rank and recommend
    
    Example:
        >>> engine = ChallengeEngine()
        >>> challenge = engine.generate_challenges(
        ...     "Implement user authentication",
        ...     "IMPLEMENT"
        ... )
        >>> print(challenge.alternatives[0].title)
        "JWT Token-Based Authentication"
    """
    
    def __init__(self):
        """Initialize challenge engine."""
        self.intent_strategies = {
            "IMPLEMENT": self._generate_implement_alternatives,
            "FIX": self._generate_fix_alternatives,
            "REFACTOR": self._generate_refactor_alternatives,
        }
    
    def generate_challenges(self, request: str, intent: str) -> Challenge:
        """Generate 3 alternative approaches for the request.
        
        Args:
            request: User's implementation request
            intent: IMPLEMENT/FIX/REFACTOR
        
        Returns:
            Challenge with 3 ranked alternatives and recommendation
        """
        # Select generation strategy based on intent
        generator = self.intent_strategies.get(
            intent,
            self._generate_default_alternatives
        )
        
        # Generate alternatives
        alternatives = generator(request)
        
        # Calculate feasibility scores
        for alt in alternatives:
            alt.feasibility_score = self._calculate_feasibility(alt)
        
        # Sort by feasibility (descending)
        alternatives.sort(key=lambda a: a.feasibility_score, reverse=True)
        
        # Generate recommendation explanation
        explanation = self._generate_recommendation_explanation(
            alternatives[0],
            request,
            intent
        )
        
        return Challenge(
            original_request=request,
            intent=intent,
            alternatives=alternatives,
            recommendation_explanation=explanation
        )
    
    # ========================================================================
    # INTENT-SPECIFIC GENERATORS
    # ========================================================================
    
    def _generate_implement_alternatives(self, request: str) -> List[AlternativeApproach]:
        """Generate alternatives for IMPLEMENT intent."""
        request_lower = request.lower()
        
        # Pattern detection for common implementation requests
        if "auth" in request_lower or "login" in request_lower:
            return self._generate_auth_alternatives()
        elif "cache" in request_lower or "caching" in request_lower:
            return self._generate_caching_alternatives()
        elif "notification" in request_lower or "alert" in request_lower:
            return self._generate_notification_alternatives()
        elif "search" in request_lower:
            return self._generate_search_alternatives()
        elif "payment" in request_lower:
            return self._generate_payment_alternatives()
        else:
            return self._generate_generic_implement_alternatives(request)
    
    def _generate_fix_alternatives(self, request: str) -> List[AlternativeApproach]:
        """Generate alternatives for FIX intent."""
        request_lower = request.lower()
        
        if "sql injection" in request_lower or "injection" in request_lower:
            return self._generate_injection_fix_alternatives()
        elif "memory leak" in request_lower or "leak" in request_lower:
            return self._generate_memory_leak_fix_alternatives()
        elif "performance" in request_lower or "slow" in request_lower:
            return self._generate_performance_fix_alternatives()
        else:
            return self._generate_generic_fix_alternatives(request)
    
    def _generate_refactor_alternatives(self, request: str) -> List[AlternativeApproach]:
        """Generate alternatives for REFACTOR intent."""
        request_lower = request.lower()
        
        if "monolith" in request_lower or "microservice" in request_lower:
            return self._generate_architecture_refactor_alternatives()
        elif "legacy" in request_lower:
            return self._generate_legacy_refactor_alternatives()
        else:
            return self._generate_generic_refactor_alternatives(request)
    
    # ========================================================================
    # DOMAIN-SPECIFIC ALTERNATIVE GENERATORS
    # ========================================================================
    
    def _generate_auth_alternatives(self) -> List[AlternativeApproach]:
        """Generate authentication alternatives."""
        return [
            AlternativeApproach(
                title="JWT Token-Based Authentication",
                description="Stateless authentication using JSON Web Tokens with refresh tokens",
                pros=[
                    "Stateless - no server-side session storage required",
                    "Scalable across multiple servers",
                    "Industry standard with broad library support",
                    "Built-in expiration and claims"
                ],
                cons=[
                    "Cannot revoke tokens before expiration without blacklist",
                    "Token size larger than session IDs",
                    "Requires secure storage on client side"
                ],
                estimated_effort="2-3 days",
                feasibility_score=0.0,  # Will be calculated
                implementation_notes="Use RS256 for production, HS256 for dev"
            ),
            AlternativeApproach(
                title="OAuth 2.0 with Third-Party Provider",
                description="Delegate authentication to OAuth provider (Google, GitHub, Auth0)",
                pros=[
                    "No password management burden",
                    "Reduced security liability",
                    "Social login improves user experience",
                    "Built-in 2FA support"
                ],
                cons=[
                    "Dependency on external service",
                    "More complex initial setup",
                    "Potential vendor lock-in",
                    "Requires internet connectivity"
                ],
                estimated_effort="1-2 days",
                feasibility_score=0.0,
                implementation_notes="Consider Passport.js or similar libraries"
            ),
            AlternativeApproach(
                title="Session-Based Authentication",
                description="Traditional server-side session with secure cookie storage",
                pros=[
                    "Simple to implement and debug",
                    "Easy to revoke sessions",
                    "Well-understood security model",
                    "No client-side storage concerns"
                ],
                cons=[
                    "Requires server-side session storage (Redis, DB)",
                    "Harder to scale horizontally",
                    "Session management overhead",
                    "CSRF protection required"
                ],
                estimated_effort="1-2 days",
                feasibility_score=0.0,
                implementation_notes="Use httpOnly, secure, sameSite cookies"
            )
        ]
    
    def _generate_caching_alternatives(self) -> List[AlternativeApproach]:
        """Generate caching alternatives."""
        return [
            AlternativeApproach(
                title="Redis In-Memory Cache",
                description="Distributed caching with Redis for fast data access",
                pros=[
                    "Very fast (sub-millisecond latency)",
                    "Rich data structures (strings, lists, sets, hashes)",
                    "Distributed caching support",
                    "Built-in TTL and eviction policies"
                ],
                cons=[
                    "Additional infrastructure dependency",
                    "Memory costs for large datasets",
                    "Requires cache invalidation strategy"
                ],
                estimated_effort="2-3 days",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Application-Level Cache (Caffeine/Guava)",
                description="In-process caching library with LRU eviction",
                pros=[
                    "No external dependencies",
                    "Zero network latency",
                    "Simple to implement",
                    "Automatic memory management"
                ],
                cons=[
                    "Not shared across instances",
                    "Limited by application memory",
                    "Lost on restart",
                    "Cannot scale beyond single instance"
                ],
                estimated_effort="1 day",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="CDN + Database Query Cache",
                description="Hybrid approach with CDN for static assets and DB query cache",
                pros=[
                    "Leverage CDN for static content",
                    "Database-level caching reduces query load",
                    "Multi-layer caching strategy",
                    "Cost-effective for read-heavy workloads"
                ],
                cons=[
                    "More complex invalidation logic",
                    "Multiple caching layers to manage",
                    "Potential cache consistency issues"
                ],
                estimated_effort="3-4 days",
                feasibility_score=0.0
            )
        ]
    
    def _generate_notification_alternatives(self) -> List[AlternativeApproach]:
        """Generate notification alternatives."""
        return [
            AlternativeApproach(
                title="WebSocket Real-Time Push",
                description="Persistent WebSocket connections for instant notifications",
                pros=[
                    "True real-time delivery",
                    "Bidirectional communication",
                    "Low latency",
                    "Efficient for high-frequency updates"
                ],
                cons=[
                    "Connection management overhead",
                    "Scaling challenges with many connections",
                    "Requires fallback for connection failures"
                ],
                estimated_effort="3-4 days",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Server-Sent Events (SSE)",
                description="HTTP-based one-way push from server to client",
                pros=[
                    "Simpler than WebSockets",
                    "Built-in reconnection",
                    "Works over HTTP/1.1",
                    "Native browser support"
                ],
                cons=[
                    "One-way only (server to client)",
                    "Limited to text-based data",
                    "Connection limits per domain"
                ],
                estimated_effort="2 days",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Polling with Exponential Backoff",
                description="Client periodically polls server for updates",
                pros=[
                    "Simplest to implement",
                    "No persistent connections",
                    "Works with any HTTP setup",
                    "Easy to debug"
                ],
                cons=[
                    "Not truly real-time",
                    "Higher server load",
                    "Wasted requests when no updates",
                    "Battery drain on mobile"
                ],
                estimated_effort="1 day",
                feasibility_score=0.0
            )
        ]
    
    def _generate_search_alternatives(self) -> List[AlternativeApproach]:
        """Generate search implementation alternatives."""
        return [
            AlternativeApproach(
                title="Elasticsearch Full-Text Search",
                description="Dedicated search engine with advanced features",
                pros=[
                    "Powerful full-text search capabilities",
                    "Faceted search and aggregations",
                    "Horizontal scalability",
                    "Real-time indexing"
                ],
                cons=[
                    "Additional infrastructure to manage",
                    "Learning curve for query DSL",
                    "Resource intensive",
                    "Data duplication (index + database)"
                ],
                estimated_effort="1 week",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Database Full-Text Search (PostgreSQL)",
                description="Use built-in database full-text search",
                pros=[
                    "No additional infrastructure",
                    "ACID transactions with search",
                    "Simple to implement",
                    "No data synchronization needed"
                ],
                cons=[
                    "Limited search capabilities vs Elasticsearch",
                    "Can impact database performance",
                    "Less flexible ranking algorithms"
                ],
                estimated_effort="2-3 days",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Simple LIKE Query with Caching",
                description="Basic SQL LIKE queries with aggressive caching",
                pros=[
                    "Minimal implementation effort",
                    "No new dependencies",
                    "Good enough for small datasets",
                    "Easy to debug"
                ],
                cons=[
                    "Poor performance on large datasets",
                    "No relevance ranking",
                    "Limited search features",
                    "Not scalable long-term"
                ],
                estimated_effort="1 day",
                feasibility_score=0.0
            )
        ]
    
    def _generate_payment_alternatives(self) -> List[AlternativeApproach]:
        """Generate payment processing alternatives."""
        return [
            AlternativeApproach(
                title="Stripe API Integration",
                description="Full-featured payment processor with extensive API",
                pros=[
                    "Comprehensive payment methods",
                    "Excellent documentation and SDKs",
                    "PCI compliance handled",
                    "Robust fraud detection"
                ],
                cons=[
                    "Transaction fees (2.9% + $0.30)",
                    "Vendor lock-in potential",
                    "Some countries not supported"
                ],
                estimated_effort="1 week",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="PayPal SDK Integration",
                description="Popular payment gateway with global reach",
                pros=[
                    "Wide user adoption",
                    "Global currency support",
                    "Buyer protection built-in",
                    "No PCI compliance burden"
                ],
                cons=[
                    "Higher transaction fees in some cases",
                    "User experience requires PayPal account",
                    "Less developer-friendly than Stripe"
                ],
                estimated_effort="1 week",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Braintree (PayPal-owned)",
                description="Developer-friendly with multiple payment methods",
                pros=[
                    "Supports PayPal + credit cards",
                    "Good developer experience",
                    "Flexible payment UI options",
                    "Competitive fees"
                ],
                cons=[
                    "More complex setup than Stripe",
                    "Documentation less comprehensive",
                    "Smaller community"
                ],
                estimated_effort="1 week",
                feasibility_score=0.0
            )
        ]
    
    def _generate_injection_fix_alternatives(self) -> List[AlternativeApproach]:
        """Generate SQL injection fix alternatives."""
        return [
            AlternativeApproach(
                title="Parameterized Queries (Prepared Statements)",
                description="Use parameterized queries for all database operations",
                pros=[
                    "Completely prevents SQL injection",
                    "Performance benefits from query caching",
                    "Industry best practice",
                    "Minimal code changes"
                ],
                cons=[
                    "Requires code refactoring",
                    "Dynamic queries more complex",
                    "May need testing of all queries"
                ],
                estimated_effort="2-3 days",
                feasibility_score=0.0,
                implementation_notes="Use ? placeholders or named parameters"
            ),
            AlternativeApproach(
                title="ORM with Query Builder",
                description="Migrate to ORM that handles escaping automatically",
                pros=[
                    "Automatic SQL injection prevention",
                    "Type safety and validation",
                    "More maintainable code",
                    "Reduced boilerplate"
                ],
                cons=[
                    "Significant refactoring effort",
                    "Learning curve for ORM",
                    "Potential performance overhead",
                    "Complex queries harder to optimize"
                ],
                estimated_effort="1-2 weeks",
                feasibility_score=0.0,
                implementation_notes="Consider SQLAlchemy, TypeORM, or Entity Framework"
            ),
            AlternativeApproach(
                title="Input Validation + Escaping",
                description="Strict input validation with database-specific escaping",
                pros=[
                    "Less invasive changes",
                    "Can be implemented incrementally",
                    "Works with existing code structure"
                ],
                cons=[
                    "Error-prone (easy to miss cases)",
                    "Not recommended by OWASP",
                    "Maintenance burden",
                    "False sense of security"
                ],
                estimated_effort="1 week",
                feasibility_score=0.0,
                implementation_notes="NOT RECOMMENDED - use parameterized queries instead"
            )
        ]
    
    def _generate_memory_leak_fix_alternatives(self) -> List[AlternativeApproach]:
        """Generate memory leak fix alternatives."""
        return [
            AlternativeApproach(
                title="Profiler-Guided Fix",
                description="Use memory profiler to identify and fix root cause",
                pros=[
                    "Identifies actual leak source",
                    "Targeted fix with minimal changes",
                    "Prevents similar leaks",
                    "Best long-term solution"
                ],
                cons=[
                    "Requires profiling tools setup",
                    "Time to analyze heap dumps",
                    "May need production profiling"
                ],
                estimated_effort="3-5 days",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Add Explicit Cleanup Hooks",
                description="Add lifecycle hooks to clean up resources",
                pros=[
                    "Can be done without finding root cause",
                    "Defensive programming approach",
                    "Quick implementation"
                ],
                cons=[
                    "May not fix actual leak",
                    "Band-aid solution",
                    "Maintenance overhead"
                ],
                estimated_effort="1-2 days",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Restart Strategy with Monitoring",
                description="Automated restart when memory threshold reached",
                pros=[
                    "Immediate mitigation",
                    "No code changes required",
                    "Works while root cause is fixed"
                ],
                cons=[
                    "Doesn't fix the leak",
                    "Service disruption on restart",
                    "Masks the real problem",
                    "Not acceptable long-term"
                ],
                estimated_effort="1 day",
                feasibility_score=0.0,
                implementation_notes="TEMPORARY WORKAROUND ONLY"
            )
        ]
    
    def _generate_performance_fix_alternatives(self) -> List[AlternativeApproach]:
        """Generate performance fix alternatives."""
        return [
            AlternativeApproach(
                title="Database Query Optimization",
                description="Add indexes, optimize queries, reduce N+1 queries",
                pros=[
                    "Often highest ROI for performance",
                    "Targeted improvements",
                    "Scalable solution"
                ],
                cons=[
                    "Requires query analysis",
                    "Index maintenance overhead",
                    "May need schema changes"
                ],
                estimated_effort="1 week",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Caching Layer",
                description="Add caching for frequently accessed data",
                pros=[
                    "Dramatic performance improvement",
                    "Reduces database load",
                    "Flexible implementation"
                ],
                cons=[
                    "Cache invalidation complexity",
                    "Additional infrastructure",
                    "Memory costs"
                ],
                estimated_effort="1 week",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Async Processing + Queue",
                description="Move slow operations to background workers",
                pros=[
                    "Improved user experience",
                    "Better resource utilization",
                    "Horizontal scalability"
                ],
                cons=[
                    "More complex architecture",
                    "Eventual consistency",
                    "Harder to debug"
                ],
                estimated_effort="2 weeks",
                feasibility_score=0.0
            )
        ]
    
    def _generate_architecture_refactor_alternatives(self) -> List[AlternativeApproach]:
        """Generate architecture refactoring alternatives."""
        return [
            AlternativeApproach(
                title="Strangler Fig Pattern (Incremental)",
                description="Gradually replace monolith pieces with microservices",
                pros=[
                    "Low risk incremental migration",
                    "Can rollback individual services",
                    "Team can learn gradually",
                    "Business continuity maintained"
                ],
                cons=[
                    "Longer migration timeline",
                    "Temporary complexity increase",
                    "Requires API versioning strategy"
                ],
                estimated_effort="6-12 months",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Modular Monolith",
                description="Keep monolith but enforce module boundaries",
                pros=[
                    "Simpler operations than microservices",
                    "Improved code organization",
                    "Can migrate to microservices later",
                    "Faster implementation"
                ],
                cons=[
                    "Doesn't achieve full microservices benefits",
                    "Still single deployment unit",
                    "Team discipline required"
                ],
                estimated_effort="2-3 months",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Big Bang Rewrite",
                description="Complete rewrite to microservices architecture",
                pros=[
                    "Clean slate architecture",
                    "No legacy tech debt",
                    "Fastest to 'done' if successful"
                ],
                cons=[
                    "Extremely high risk",
                    "Long feature freeze",
                    "High failure rate historically",
                    "Business disruption"
                ],
                estimated_effort="12-18 months",
                feasibility_score=0.0,
                implementation_notes="NOT RECOMMENDED - high failure rate"
            )
        ]
    
    def _generate_legacy_refactor_alternatives(self) -> List[AlternativeApproach]:
        """Generate legacy code refactoring alternatives."""
        return [
            AlternativeApproach(
                title="Test Coverage + Incremental Refactoring",
                description="Add comprehensive tests then refactor incrementally",
                pros=[
                    "Safety net prevents regressions",
                    "Incremental risk management",
                    "Improves testability",
                    "Best practice approach"
                ],
                cons=[
                    "Time investment for tests",
                    "Legacy code hard to test",
                    "Longer timeline"
                ],
                estimated_effort="4-6 weeks",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Facade Pattern Isolation",
                description="Wrap legacy code behind clean interfaces",
                pros=[
                    "Quick isolation of legacy code",
                    "Enables parallel work",
                    "Can rewrite behind facade later",
                    "Minimal risk"
                ],
                cons=[
                    "Adds abstraction layer",
                    "Legacy code still exists",
                    "May hide problems"
                ],
                estimated_effort="2 weeks",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Feature Flag + Shadow Rewrite",
                description="Rewrite while keeping old code, toggle with feature flags",
                pros=[
                    "Can compare new vs old",
                    "Easy rollback",
                    "Production validation"
                ],
                cons=[
                    "Duplicate code temporarily",
                    "Feature flag management",
                    "More complex deployment"
                ],
                estimated_effort="6-8 weeks",
                feasibility_score=0.0
            )
        ]
    
    # ========================================================================
    # GENERIC GENERATORS
    # ========================================================================
    
    def _generate_generic_implement_alternatives(self, request: str) -> List[AlternativeApproach]:
        """Generate generic implementation alternatives."""
        return [
            AlternativeApproach(
                title="Full-Featured Implementation",
                description=f"Complete implementation of {request} with all features",
                pros=[
                    "Comprehensive solution",
                    "Future-proof design",
                    "Meets all requirements"
                ],
                cons=[
                    "Longer implementation time",
                    "Higher complexity",
                    "May be over-engineered"
                ],
                estimated_effort="2 weeks",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="MVP Approach",
                description=f"Minimum viable implementation of {request}",
                pros=[
                    "Faster time to market",
                    "Simpler codebase",
                    "Can iterate based on feedback"
                ],
                cons=[
                    "Limited features initially",
                    "May need significant rework",
                    "Technical debt risk"
                ],
                estimated_effort="1 week",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Third-Party Library/Service",
                description=f"Use existing library or service for {request}",
                pros=[
                    "Fastest implementation",
                    "Battle-tested code",
                    "Maintained by community/vendor"
                ],
                cons=[
                    "External dependency",
                    "Less control",
                    "Potential licensing/cost issues"
                ],
                estimated_effort="3-5 days",
                feasibility_score=0.0
            )
        ]
    
    def _generate_generic_fix_alternatives(self, request: str) -> List[AlternativeApproach]:
        """Generate generic fix alternatives."""
        return [
            AlternativeApproach(
                title="Root Cause Fix",
                description=f"Identify and fix root cause of {request}",
                pros=[
                    "Permanent solution",
                    "Prevents recurrence",
                    "Best long-term approach"
                ],
                cons=[
                    "Takes longer to implement",
                    "May require significant changes",
                    "Root cause may be unclear"
                ],
                estimated_effort="1 week",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Defensive Workaround",
                description=f"Add defensive checks and error handling for {request}",
                pros=[
                    "Quick mitigation",
                    "Low risk",
                    "Can buy time for proper fix"
                ],
                cons=[
                    "Doesn't fix underlying issue",
                    "Technical debt",
                    "May hide real problems"
                ],
                estimated_effort="2-3 days",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Rewrite Affected Component",
                description=f"Rewrite component to eliminate {request}",
                pros=[
                    "Clean slate approach",
                    "Can improve design",
                    "Eliminates legacy issues"
                ],
                cons=[
                    "High effort",
                    "Risk of new bugs",
                    "Requires thorough testing"
                ],
                estimated_effort="2-3 weeks",
                feasibility_score=0.0
            )
        ]
    
    def _generate_generic_refactor_alternatives(self, request: str) -> List[AlternativeApproach]:
        """Generate generic refactoring alternatives."""
        return [
            AlternativeApproach(
                title="Comprehensive Refactoring",
                description=f"Full refactor of {request} with modern patterns",
                pros=[
                    "Significant quality improvement",
                    "Addresses all technical debt",
                    "Long-term maintainability"
                ],
                cons=[
                    "Large effort required",
                    "High testing burden",
                    "Longer timeline"
                ],
                estimated_effort="3-4 weeks",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Incremental Refactoring",
                description=f"Refactor {request} in small, safe steps",
                pros=[
                    "Lower risk",
                    "Can pause/resume",
                    "Easier to review",
                    "Continuous delivery friendly"
                ],
                cons=[
                    "Longer calendar time",
                    "May miss opportunities for bigger improvements",
                    "Requires discipline"
                ],
                estimated_effort="4-6 weeks (spread out)",
                feasibility_score=0.0
            ),
            AlternativeApproach(
                title="Extract and Isolate",
                description=f"Extract {request} into separate module/service",
                pros=[
                    "Isolates complexity",
                    "Enables focused improvements",
                    "Better testability"
                ],
                cons=[
                    "Additional abstraction",
                    "Integration overhead",
                    "May not address root issues"
                ],
                estimated_effort="2 weeks",
                feasibility_score=0.0
            )
        ]
    
    def _generate_default_alternatives(self, request: str) -> List[AlternativeApproach]:
        """Default alternatives for unknown intents."""
        return self._generate_generic_implement_alternatives(request)
    
    # ========================================================================
    # FEASIBILITY CALCULATION
    # ========================================================================
    
    def _calculate_feasibility(self, alternative: AlternativeApproach) -> float:
        """Calculate feasibility score (0.0-1.0) for an alternative.
        
        Factors:
        - Effort (lower is better)
        - Pros/cons ratio
        - Implementation risk
        
        Args:
            alternative: The alternative to score
        
        Returns:
            Feasibility score from 0.0 (low) to 1.0 (high)
        """
        # Factor 1: Effort score (0.0-0.4)
        effort_score = self._score_effort(alternative.estimated_effort)
        
        # Factor 2: Pros/cons ratio (0.0-0.4)
        pros_count = len(alternative.pros)
        cons_count = len(alternative.cons)
        pros_cons_score = min(pros_count / (pros_count + cons_count), 1.0) * 0.4
        
        # Factor 3: Risk penalty (0.0-0.2 deduction)
        risk_penalty = self._calculate_risk_penalty(alternative)
        
        total = effort_score + pros_cons_score - risk_penalty
        return max(0.0, min(1.0, total))  # Clamp to [0.0, 1.0]
    
    def _score_effort(self, estimated_effort: str) -> float:
        """Convert effort estimate to score (0.0-0.4).
        
        Args:
            estimated_effort: Time estimate string (e.g., "2 days", "1 week")
        
        Returns:
            Score from 0.0 (high effort) to 0.4 (low effort)
        """
        effort_lower = estimated_effort.lower()
        
        # Score based on time units
        if "hour" in effort_lower:
            return 0.4  # Hours = very low effort
        elif "day" in effort_lower:
            # Extract number of days
            if "1" in effort_lower or "1-2" in effort_lower:
                return 0.35
            elif "2" in effort_lower or "2-3" in effort_lower:
                return 0.3
            elif "3" in effort_lower or "3-5" in effort_lower:
                return 0.25
            else:
                return 0.2
        elif "week" in effort_lower:
            if "1" in effort_lower:
                return 0.15
            elif "2" in effort_lower:
                return 0.1
            else:
                return 0.05
        elif "month" in effort_lower:
            return 0.0  # Months = very high effort
        else:
            return 0.2  # Unknown, assume moderate
    
    def _calculate_risk_penalty(self, alternative: AlternativeApproach) -> float:
        """Calculate risk penalty based on cons and implementation notes.
        
        Args:
            alternative: The alternative to assess
        
        Returns:
            Risk penalty from 0.0 (low risk) to 0.2 (high risk)
        """
        penalty = 0.0
        
        # Check for high-risk indicators in cons
        high_risk_keywords = [
            "not recommended", "high risk", "high failure rate",
            "extremely", "significant rework", "masks the problem"
        ]
        
        all_text = " ".join(alternative.cons + [alternative.implementation_notes]).lower()
        
        for keyword in high_risk_keywords:
            if keyword in all_text:
                penalty += 0.05
        
        # Cap at 0.2
        return min(0.2, penalty)
    
    # ========================================================================
    # RECOMMENDATION EXPLANATION
    # ========================================================================
    
    def _generate_recommendation_explanation(
        self,
        recommended: AlternativeApproach,
        request: str,
        intent: str
    ) -> str:
        """Generate explanation for why an alternative is recommended.
        
        Args:
            recommended: The recommended alternative (highest feasibility)
            request: Original request
            intent: IMPLEMENT/FIX/REFACTOR
        
        Returns:
            Human-readable recommendation explanation
        """
        score = recommended.feasibility_score
        
        explanation = f"We recommend '{recommended.title}' (feasibility: {score:.2f}) because:\n\n"
        
        # Highlight top 3 pros
        top_pros = recommended.pros[:3]
        explanation += "**Key Advantages:**\n"
        for i, pro in enumerate(top_pros, 1):
            explanation += f"{i}. {pro}\n"
        
        # Mention effort
        explanation += f"\n**Estimated Effort:** {recommended.estimated_effort}\n"
        
        # Address cons
        if recommended.cons:
            explanation += f"\n**Trade-offs to Consider:**\n"
            for con in recommended.cons[:2]:
                explanation += f"- {con}\n"
        
        # Intent-specific guidance
        if intent == "IMPLEMENT":
            explanation += "\nThis approach balances speed to market with long-term maintainability."
        elif intent == "FIX":
            explanation += "\nThis fix addresses the root cause while minimizing risk."
        elif intent == "REFACTOR":
            explanation += "\nThis refactoring strategy maximizes quality improvement with acceptable risk."
        
        return explanation
