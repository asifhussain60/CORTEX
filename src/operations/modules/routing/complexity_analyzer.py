"""
Complexity Analyzer - Multi-dimensional complexity scoring for tiered routing.

Purpose:
    Analyzes user requests and determines planning complexity to enable
    intelligent routing: HIGH→incremental, MEDIUM→conditional, LOW→skeleton.

Features:
    - 4-dimensional scoring: scope (25), dependencies (25), risk (30), uncertainty (20)
    - Complexity tiers: CRITICAL (90-100), HIGH (70-89), MEDIUM (40-69), LOW (20-39), TRIVIAL (0-19)
    - Auto-routing logic: Security/auth/migrations/APIs→incremental planning
    - Integration with TieredRouter for Planning System

Author: Asif Hussain
Date: December 2024
Version: 1.0.0
"""

import re
import json
import logging
from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)


class ComplexityTier(Enum):
    """Complexity tiers for planning routing decisions"""
    CRITICAL = "CRITICAL"     # 90-100: Incremental + TDD mandatory
    HIGH = "HIGH"             # 70-89: Incremental planning recommended
    MEDIUM = "MEDIUM"         # 40-69: Conditional - analyze codebase first
    LOW = "LOW"               # 20-39: Skeleton planning sufficient
    TRIVIAL = "TRIVIAL"       # 0-19: Direct execution, no formal planning


@dataclass
class ComplexityScore:
    """Result of complexity analysis"""
    total_score: int                    # 0-100 composite score
    tier: ComplexityTier                # Classification
    dimensions: Dict[str, int]          # Individual dimension scores
    rationale: List[str]                # Explanation of scoring
    recommendation: str                 # Actionable routing decision
    triggers: List[str]                 # Auto-route triggers detected
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for serialization"""
        return {
            "total_score": self.total_score,
            "tier": self.tier.value,
            "dimensions": self.dimensions,
            "rationale": self.rationale,
            "recommendation": self.recommendation,
            "triggers": self.triggers
        }


class ComplexityAnalyzer:
    """
    Analyzes planning complexity using 4-dimensional scoring.
    
    Scoring Methodology:
        - Scope Magnitude (25 pts): Files, entities, API endpoints affected
        - Dependencies (25 pts): External services, libraries, breaking changes
        - Risk Level (30 pts): Security, auth, data loss, compliance concerns
        - Uncertainty (20 pts): Ambiguous requirements, unknown tech, R&D needed
    
    Auto-Route Triggers (HIGH complexity):
        - Security patterns: authentication, authorization, encryption
        - Data operations: migrations, schema changes, data loss risk
        - API changes: breaking changes, versioning, contract modifications
        - Critical domains: payment, healthcare, financial calculations
    
    Integration:
        - Called by TieredRouter before classification
        - Influences Tier 3 vs Tier 4 routing decisions
        - Used by Planning Orchestrator for execution mode selection
    """
    
    # Auto-route triggers: Patterns that force HIGH complexity
    CRITICAL_PATTERNS = {
        'security': [
            r'auth(entication|orization)?',
            r'password|credential|secret|token',
            r'encrypt|decrypt|hash|sign',
            r'security|vulnerability|xss|sql\s+injection',
            r'oauth|saml|jwt|sso'
        ],
        'data_operations': [
            r'migrat(e|ion)',
            r'schema\s+change',
            r'data\s+loss',
            r'database\s+(alter|drop|truncate)',
            r'backfill|reseed'
        ],
        'api_breaking': [
            r'breaking\s+change',
            r'api\s+version',
            r'deprecat(e|ion)',
            r'backwards?\s+incompatib',
            r'contract\s+change'
        ],
        'critical_domains': [
            r'payment|billing|transaction',
            r'healthcare|medical|patient',
            r'financial|accounting|audit',
            r'compliance|gdpr|hipaa|pci',
            r'accessibility|a11y|wcag'
        ]
    }
    
    # Trivial patterns: Skip formal planning
    TRIVIAL_PATTERNS = [
        r'simple\s+(getter|setter)',
        r'add\s+logging',
        r'fix\s+typo',
        r'update\s+comment',
        r'format(ting)?',
        r'rename\s+variable',
        r'add\s+todo',
        r'bump\s+version'
    ]
    
    def __init__(self, llm_client=None):
        """
        Initialize complexity analyzer.
        
        Args:
            llm_client: Optional LLM client for semantic analysis (v2.0)
        """
        self.dimension_weights = {
            'scope_magnitude': 25,
            'dependencies': 25,
            'risk_level': 30,
            'uncertainty': 20
        }
        self.llm_client = llm_client
        
        mode = "LLM-enhanced" if llm_client else "regex-based"
        logger.info(f"ComplexityAnalyzer initialized with 4-dimensional scoring ({mode})")
    
    def analyze(
        self,
        user_request: str,
        codebase_context: Optional[Dict] = None
    ) -> ComplexityScore:
        """
        Analyze planning complexity of user request.
        
        Args:
            user_request: User's feature request or task description
            codebase_context: Optional codebase analysis from AST (file count, dependencies, etc.)
        
        Returns:
            ComplexityScore with tier, dimensions, and routing recommendation
        
        Example:
            >>> analyzer = ComplexityAnalyzer()
            >>> score = analyzer.analyze("Add JWT authentication to API")
            >>> print(score.tier)  # HIGH (security trigger detected)
            >>> print(score.recommendation)  # "Use incremental planning with TDD"
        """
        logger.info(f"Analyzing complexity for request: {user_request[:100]}...")
        
        # Check for auto-route triggers FIRST (LLM can override trivial patterns)
        triggers = self._detect_triggers(user_request)
        
        # Only check trivial if no triggers detected
        if not triggers and self._is_trivial(user_request):
            return self._create_trivial_score(user_request)
        
        # Score 4 dimensions
        scope_score = self._score_scope_magnitude(user_request, codebase_context)
        dependency_score = self._score_dependencies(user_request, codebase_context)
        risk_score = self._score_risk_level(user_request, triggers)
        uncertainty_score = self._score_uncertainty(user_request)
        
        # Calculate total score
        total_score = scope_score + dependency_score + risk_score + uncertainty_score
        
        # Apply trigger boost: Auto-route triggers force HIGH tier minimum
        if triggers:
            total_score = max(total_score, 70)  # HIGH tier threshold
            logger.info(f"Auto-route triggers detected: {triggers} - forcing HIGH tier minimum")
        
        # Classify tier
        tier = self._classify_tier(total_score)
        
        # Generate recommendation
        recommendation = self._generate_recommendation(tier, triggers, total_score)
        
        # Generate rationale
        rationale = self._generate_rationale(
            tier=tier,
            dimensions={
                'scope_magnitude': scope_score,
                'dependencies': dependency_score,
                'risk_level': risk_score,
                'uncertainty': uncertainty_score
            },
            triggers=triggers
        )
        
        return ComplexityScore(
            total_score=total_score,
            tier=tier,
            dimensions={
                'scope_magnitude': scope_score,
                'dependencies': dependency_score,
                'risk_level': risk_score,
                'uncertainty': uncertainty_score
            },
            rationale=rationale,
            recommendation=recommendation,
            triggers=triggers
        )
    
    def _is_trivial(self, user_request: str) -> bool:
        """Check if request matches trivial patterns"""
        request_lower = user_request.lower()
        for pattern in self.TRIVIAL_PATTERNS:
            if re.search(pattern, request_lower):
                logger.debug(f"Trivial pattern detected: {pattern}")
                return True
        return False
    
    def _detect_triggers(self, user_request: str) -> List[str]:
        """
        Detect auto-route triggers forcing HIGH complexity.
        
        Uses LLM for semantic understanding with regex fallback.
        """
        # Try LLM-based detection first if available
        if self.llm_client:
            try:
                llm_triggers = self._detect_triggers_llm(user_request)
                if llm_triggers is not None and llm_triggers.get('confidence', 0) >= 0.8:
                    logger.info(f"LLM trigger detection: {llm_triggers['triggers']} (confidence: {llm_triggers['confidence']})")
                    # Return raw triggers from LLM (just category names)
                    return llm_triggers['triggers']
                else:
                    logger.info(f"LLM confidence too low ({llm_triggers.get('confidence', 0)}), falling back to regex")
            except Exception as e:
                logger.warning(f"LLM trigger detection failed: {e}, falling back to regex")
        
        # Fallback to regex-based detection
        return self._detect_triggers_regex(user_request)
    
    def _detect_triggers_llm(self, user_request: str) -> Optional[Dict]:
        """
        LLM-based semantic trigger detection (v2.0).
        
        Args:
            user_request: User's feature request
            
        Returns:
            Dict with keys: triggers (list), confidence (float), reasoning (str)
            None if LLM unavailable
        """
        if not self.llm_client:
            return None
        
        prompt = f"""Analyze feature request for critical complexity triggers:

Request: "{user_request}"

Check for these critical patterns:
1. Security: authentication, authorization, encryption, access control, credentials, OAuth, SSO, JWT
2. Data operations: database migrations, schema changes, data loss risk, backfill, reseed
3. API breaking changes: API versioning, deprecation, backwards incompatibility, contract changes
4. Critical domains: payment processing, financial transactions, healthcare/medical, compliance (GDPR/HIPAA/PCI), accessibility

Return JSON with this structure:
{{
    "triggers": ["security", "data_operations", "api_breaking", "critical_domains"],
    "confidence": 0.95,
    "reasoning": "Brief explanation of what patterns were detected"
}}

Only include triggers that are clearly present. Confidence should be 0.8+ for reliable detection."""

        try:
            # Call LLM client (interface to be implemented)
            response = self.llm_client.analyze(prompt)
            
            # Parse JSON response
            if isinstance(response, str):
                result = json.loads(response)
            else:
                result = response
            
            # Validate required fields
            if 'triggers' not in result or 'confidence' not in result:
                logger.warning("LLM response missing required fields")
                return None
            
            return {
                'triggers': result['triggers'],
                'confidence': result['confidence'],
                'reasoning': result.get('reasoning', 'No reasoning provided')
            }
            
        except Exception as e:
            logger.error(f"LLM trigger detection error: {e}")
            return None
    
    def _detect_triggers_regex(self, user_request: str) -> List[str]:
        """Regex-based trigger detection (legacy fallback)."""
        triggers = []
        request_lower = user_request.lower()
        
        for category, patterns in self.CRITICAL_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, request_lower):
                    trigger_name = f"{category}: {pattern}"
                    triggers.append(trigger_name)
                    logger.info(f"Auto-route trigger detected (regex): {trigger_name}")
        
        return triggers
    
    def _score_scope_magnitude(
        self,
        user_request: str,
        codebase_context: Optional[Dict]
    ) -> int:
        """
        Score: 0-25 points
        
        Factors:
            - File count: 1 file (5), 2-5 files (10), 6-10 files (15), 11+ files (25)
            - Entities: Tables/models/services mentioned
            - API endpoints: New routes or modifications
            - Codebase size: Larger codebases = higher complexity
        """
        score = 0
        request_lower = user_request.lower()
        
        # Detect file count indicators
        file_indicators = [
            (r'(?:across|multiple|several)\s+files', 15),
            (r'\d+\s+files?', 10),
            (r'single\s+file', 5),
            (r'new\s+(module|service|component)', 15),
            (r'refactor\s+(entire|all|multiple)', 20)
        ]
        
        for pattern, points in file_indicators:
            if re.search(pattern, request_lower):
                score = max(score, points)
        
        # Detect entity count (tables, models, services)
        entity_patterns = [r'table', r'model', r'service', r'endpoint', r'api', r'controller']
        entity_count = sum(len(re.findall(pattern, request_lower)) for pattern in entity_patterns)
        
        if entity_count >= 5:
            score = max(score, 25)
        elif entity_count >= 3:
            score = max(score, 15)
        elif entity_count >= 1:
            score = max(score, 10)
        
        # Codebase context boost
        if codebase_context:
            file_count = codebase_context.get('file_count', 0)
            if file_count > 100:
                score = min(score + 5, 25)  # Large codebase bonus
        
        logger.debug(f"Scope magnitude score: {score}/25")
        return min(score, 25)
    
    def _score_dependencies(
        self,
        user_request: str,
        codebase_context: Optional[Dict]
    ) -> int:
        """
        Score: 0-25 points
        
        Factors:
            - External services: APIs, databases, message queues
            - New libraries: NPM/pip packages to install
            - Breaking changes: Affects downstream consumers
            - Integration complexity: Multiple systems involved
        """
        score = 0
        request_lower = user_request.lower()
        
        # External service patterns
        external_patterns = [
            (r'(?:integrate|connect|call)\s+(?:api|service|database)', 15),
            (r'third[- ]party', 10),
            (r'external\s+(?:api|service|system)', 15),
            (r'microservice', 12),
            (r'message\s+queue|kafka|rabbitmq|sqs', 15),
            (r'cache|redis|memcached', 10)
        ]
        
        for pattern, points in external_patterns:
            if re.search(pattern, request_lower):
                score = max(score, points)
        
        # Library installation patterns
        if re.search(r'(?:install|add|use)\s+(?:package|library|dependency)', request_lower):
            score = max(score, 10)
        
        # Breaking change patterns
        breaking_patterns = [r'breaking', r'backwards?\s+incompatib', r'major\s+version']
        if any(re.search(p, request_lower) for p in breaking_patterns):
            score = max(score, 20)
        
        # Integration complexity
        integration_keywords = ['integrate', 'sync', 'orchestrat', 'coordinate']
        if any(keyword in request_lower for keyword in integration_keywords):
            score = max(score, 12)
        
        logger.debug(f"Dependencies score: {score}/25")
        return min(score, 25)
    
    def _score_risk_level(
        self,
        user_request: str,
        triggers: List[str]
    ) -> int:
        """
        Score: 0-30 points (highest weight dimension)
        
        Factors:
            - Security concerns: Auth, encryption, vulnerabilities
            - Data loss risk: Migrations, deletions, schema changes
            - Compliance: GDPR, HIPAA, PCI DSS, SOC2
            - Critical domains: Payment, healthcare, financial
            - Auto-route triggers: Detected patterns
        """
        score = 0
        
        # Triggers automatically contribute risk
        if triggers:
            # Each trigger adds 10 points, cap at 30
            score = min(len(triggers) * 10, 30)
            logger.debug(f"Risk from triggers: {score}/30")
            return score
        
        request_lower = user_request.lower()
        
        # Risk patterns (fallback if no triggers)
        risk_patterns = [
            (r'production|live|critical', 20),
            (r'delete|drop|truncate|remove', 25),
            (r'migrate|schema|alter', 20),
            (r'security|vulnerability|exploit', 30),
            (r'user\s+data|personal\s+information|pii', 25),
            (r'performance|scalability|load', 15),
            (r'experiment|prototype|poc', 5)  # Low risk
        ]
        
        for pattern, points in risk_patterns:
            if re.search(pattern, request_lower):
                score = max(score, points)
        
        logger.debug(f"Risk level score: {score}/30")
        return min(score, 30)
    
    def _score_uncertainty(self, user_request: str) -> int:
        """
        Score: 0-20 points
        
        Factors:
            - Ambiguous requirements: "somehow", "maybe", "possibly"
            - Unknown technology: "learn", "research", "explore"
            - R&D needed: "investigate", "experiment", "prototype"
            - Missing details: Short requests, vague descriptions
        """
        score = 0
        request_lower = user_request.lower()
        
        # Ambiguity indicators
        ambiguity_patterns = [
            r'somehow|maybe|possibly|perhaps|might',
            r'not\s+sure|unclear|ambiguous',
            r'figure\s+out|work\s+out',
            r'(?:^|\s)tbd(?:\s|$)|to\s+be\s+determined'
        ]
        
        ambiguity_count = sum(1 for pattern in ambiguity_patterns if re.search(pattern, request_lower))
        score += min(ambiguity_count * 5, 15)
        
        # Unknown technology indicators
        unknown_tech_patterns = [
            r'learn|research|explore|investigate',
            r'new\s+(?:to|tech|framework|library)',
            r'unfamiliar|unknown',
            r'experiment|prototype|poc|proof\s+of\s+concept'
        ]
        
        if any(re.search(p, request_lower) for p in unknown_tech_patterns):
            score = max(score, 12)
        
        # Request length heuristic: Very short requests often lack detail
        word_count = len(user_request.split())
        if word_count < 10:
            score = max(score, 8)  # Likely missing requirements
        elif word_count < 5:
            score = max(score, 15)  # Very likely missing requirements
        
        logger.debug(f"Uncertainty score: {score}/20")
        return min(score, 20)
    
    def _classify_tier(self, total_score: int) -> ComplexityTier:
        """Classify total score into complexity tier"""
        if total_score >= 90:
            return ComplexityTier.CRITICAL
        elif total_score >= 70:
            return ComplexityTier.HIGH
        elif total_score >= 40:
            return ComplexityTier.MEDIUM
        elif total_score >= 20:
            return ComplexityTier.LOW
        else:
            return ComplexityTier.TRIVIAL
    
    def _generate_recommendation(
        self,
        tier: ComplexityTier,
        triggers: List[str],
        total_score: int
    ) -> str:
        """Generate actionable routing recommendation"""
        recommendations = {
            ComplexityTier.CRITICAL: (
                "Use incremental planning with TDD mandatory. Break into phases with "
                "checkpoints. Engage security/compliance review before execution."
            ),
            ComplexityTier.HIGH: (
                "Use incremental planning with TDD. Consider breaking into 2-3 phases "
                "with intermediate validation. Risk assessment recommended."
            ),
            ComplexityTier.MEDIUM: (
                "Analyze codebase with AST first. Use conditional planning - skeleton "
                "if simple, incremental if dependencies found. TDD optional."
            ),
            ComplexityTier.LOW: (
                "Use skeleton planning for structure. Direct implementation sufficient. "
                "Skip TDD unless public API surface."
            ),
            ComplexityTier.TRIVIAL: (
                "Skip formal planning. Direct execution with inline validation. "
                "No test generation needed."
            )
        }
        
        base_recommendation = recommendations[tier]
        
        # Add trigger-specific guidance
        if triggers:
            trigger_guidance = f"\n\n⚠️ Auto-route triggers detected ({len(triggers)}): {', '.join([t.split(':')[0] for t in triggers])}. Mandatory incremental planning enforced."
            return base_recommendation + trigger_guidance
        
        return base_recommendation
    
    def _generate_rationale(
        self,
        tier: ComplexityTier,
        dimensions: Dict[str, int],
        triggers: List[str]
    ) -> List[str]:
        """Generate explanation for complexity classification"""
        rationale = []
        
        # Dimension explanations
        if dimensions['scope_magnitude'] >= 15:
            rationale.append(f"📦 Large scope ({dimensions['scope_magnitude']}/25) - multiple files/entities affected")
        if dimensions['dependencies'] >= 15:
            rationale.append(f"🔗 High dependencies ({dimensions['dependencies']}/25) - external services/breaking changes")
        if dimensions['risk_level'] >= 20:
            rationale.append(f"⚠️ High risk ({dimensions['risk_level']}/30) - security/data loss/compliance concerns")
        if dimensions['uncertainty'] >= 12:
            rationale.append(f"❓ High uncertainty ({dimensions['uncertainty']}/20) - ambiguous requirements/unknown tech")
        
        # Low complexity explanations
        if tier in [ComplexityTier.LOW, ComplexityTier.TRIVIAL]:
            if dimensions['scope_magnitude'] < 10:
                rationale.append(f"✅ Small scope ({dimensions['scope_magnitude']}/25) - single file change")
            if dimensions['risk_level'] < 10:
                rationale.append(f"✅ Low risk ({dimensions['risk_level']}/30) - no critical systems affected")
        
        # Trigger explanations
        if triggers:
            rationale.append(f"🚨 Auto-route triggers: {len(triggers)} critical patterns detected")
        
        return rationale
    
    def _create_trivial_score(self, user_request: str) -> ComplexityScore:
        """Create score for trivial requests"""
        return ComplexityScore(
            total_score=0,
            tier=ComplexityTier.TRIVIAL,
            dimensions={
                'scope_magnitude': 0,
                'dependencies': 0,
                'risk_level': 0,
                'uncertainty': 0
            },
            rationale=[
                "✅ Trivial pattern detected - simple change with no planning overhead",
                f"Pattern match: {user_request[:50]}..."
            ],
            recommendation="Skip formal planning. Direct execution sufficient.",
            triggers=[]
        )


# ============================================================================
# CLI Interface for Standalone Testing
# ============================================================================

if __name__ == "__main__":
    import sys
    import json
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    if len(sys.argv) < 2:
        print("Usage: python complexity_analyzer.py '<user_request>' [--verbose]")
        print("\nExamples:")
        print('  python complexity_analyzer.py "Add JWT authentication to API"')
        print('  python complexity_analyzer.py "Fix typo in README"')
        print('  python complexity_analyzer.py "Migrate database schema for new payment system" --verbose')
        sys.exit(1)
    
    user_request = sys.argv[1]
    verbose = '--verbose' in sys.argv
    
    if verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    print("=" * 80)
    print("CORTEX Complexity Analyzer v1.0.0")
    print("=" * 80)
    print(f"\nUser Request: {user_request}\n")
    
    analyzer = ComplexityAnalyzer()
    score = analyzer.analyze(user_request)
    
    print(f"Complexity Tier: {score.tier.value} ({score.total_score}/100)\n")
    print("Dimension Scores:")
    for dimension, points in score.dimensions.items():
        max_points = analyzer.dimension_weights[dimension]
        bar = "█" * (points * 20 // max_points) + "░" * (20 - (points * 20 // max_points))
        print(f"  {dimension:20s}: {bar} {points}/{max_points}")
    
    print(f"\nRationale:")
    for item in score.rationale:
        print(f"  • {item}")
    
    if score.triggers:
        print(f"\nAuto-Route Triggers:")
        for trigger in score.triggers:
            print(f"  • {trigger}")
    
    print(f"\nRecommendation:")
    print(f"  {score.recommendation}\n")
    
    if verbose:
        print("JSON Output:")
        print(json.dumps(score.to_dict(), indent=2))
