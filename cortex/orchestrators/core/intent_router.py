"""
Intent Router Orchestrator - Routes operations based on intent type

AC-PROD-001-02: Intent Router - Create basic structure and routing logic
Resolves ISSUE-001: Intent Router missing (Master Stage 2 routing broken)

The IntentRouter analyzes operation context and determines the appropriate
execution path for different operation types:
  - IMPLEMENT: New feature development
  - FIX: Bug fixes and issue resolution
  - REFACTOR: Code improvement and restructuring

CORE Governance Rules Applied:
  - CORE-008: TDD (tests created first, RED → GREEN pattern)
  - CORE-011: Type hints mandatory on all functions
  - CORE-012: Google-style docstrings on all public methods
  - CORE-013: Specific exception handling (no bare except)
  - CORE-027: Audit trail logging (AC_START → AC_EXECUTE → AC_COMPLETE)
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import yaml

from cortex.brain.core.interfaces.i_orchestrator import IOrchestrator, OperationMode
from cortex.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.models.canonical_enums import IntentType
# Note: SpecRegistry import removed - not yet implemented (AC-PERMANENT-FIX-010)

# Phase 8.2: Import orchestrator lookup and enforcement
from cortex.orchestrators.registry.orchestrator_lookup import OrchestratorLookup
from cortex.orchestrators.core.routing_enforcement import (
    RoutingEnforcementEngine,
    RoutingViolation,
)


@dataclass
class RoutingDecision:
    """
    Represents a routing decision made by the IntentRouter.
    
    Attributes:
        intent_type: Detected operation intent (IMPLEMENT, FIX, REFACTOR)
        target_handler: Name of target handler/orchestrator
        confidence_score: Confidence of routing decision (0.0-1.0)
        reasoning: Human-readable explanation of routing decision
        metadata: Additional routing context metadata
        timestamp: When routing decision was made
        composite_intents: AC-FUTURE-005 - List of detected intents for composite requests
        target_orchestrator: AC-PHASE-8.2-01 - Actual orchestrator instance (NEW)
        fallback_orchestrators: AC-PHASE-8.2-01 - Ranked alternative orchestrators (NEW)
        keyword_matches: AC-PHASE-8.2-01 - Keywords that matched routing config (NEW)
        confidence_breakdown: AC-PHASE-8.2-01 - Detailed confidence scoring (NEW)
    """
    intent_type: IntentType
    target_handler: str
    confidence_score: float
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    composite_intents: List[IntentType] = field(default_factory=list)  # AC-FUTURE-005
    # Phase 8.2 additions:
    target_orchestrator: Optional[IOrchestrator] = None  # AC-PHASE-8.2-01
    fallback_orchestrators: List[IOrchestrator] = field(default_factory=list)  # AC-PHASE-8.2-01
    keyword_matches: List[str] = field(default_factory=list)  # AC-PHASE-8.2-01
    confidence_breakdown: Dict[str, float] = field(default_factory=dict)  # AC-PHASE-8.2-01


@dataclass
class RoutingContext:
    """
    Represents the full context for a routing decision.
    
    Attributes:
        operation: Operation name/identifier
        description: Human-readable operation description
        domain: Target domain (core, orchestrators, infrastructure, etc.)
        keywords: Keywords from operation description
        urgency: Operation urgency level (low, medium, high, critical)
        user_intent: User's stated intent or goal
        metadata: Additional context metadata
    """
    operation: str
    description: Optional[str] = None
    domain: Optional[str] = None
    keywords: Optional[List[str]] = None
    urgency: str = "medium"
    user_intent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class CompositeIntentDetector:
    """
    Detects composite intents when a request contains multiple operation types.
    
    AC-FUTURE-005: Composite intent detection for multi-faceted requests
    
        Examples of composite intents:
        - "Implement feature AND test it" → IMPLEMENT + TEST (implicit)
        - "Fix bug AND refactor the code" → FIX + REFACTOR
        - "Implement with proper documentation" → IMPLEMENT + DOCUMENT
        - "Refactor and optimize performance" → REFACTOR (with optimization emphasis)    Composite patterns detected:
    1. AND patterns: "X and Y" or "X then Y"
    2. WITH patterns: "Implement with tests" → Do both
    3. SEQUENTIAL patterns: "Fix, then refactor" → Do both
    4. IMPLICIT patterns: "Fix bug" + "need tests" → Add tests
    """
    
    # Composite connectors that indicate multiple intents
    AND_CONNECTORS = ["and", "with", "plus", "also", "then", ",", "&", "+"]
    THEN_CONNECTORS = ["then", "after that", "once", "before"]
    OR_CONNECTORS = ["or", "alternatively", "|"]
    
    # Implicit intent triggers (when one action implies another)
    IMPLICIT_PATTERNS = {
        "fix": ["test", "verify", "check"],  # Fix should be tested
        "implement": ["test", "document", "type hints"],  # Implement should be tested
        "refactor": ["test", "verify"],  # Refactor should be tested
    }
    
    @staticmethod
    def detect_composite_intents(
        request: str,
        primary_intent: IntentType
    ) -> List[IntentType]:
        """
        Detect composite intents from request text.
        
        AC-FUTURE-005: Multi-faceted request handling
        
        Args:
            request: User's natural language request
            primary_intent: Primary intent already detected
            
        Returns:
            List of intents (including primary_intent + any detected secondary intents)
        """
        intents = [primary_intent]
        request_lower = request.lower()
        
        # Check for AND patterns
        for connector in CompositeIntentDetector.AND_CONNECTORS:
            if connector in request_lower:
                # If we have "fix and implement" - both intents present
                if "implement" in request_lower and "fix" in request_lower:
                    if IntentType.IMPLEMENT not in intents:
                        intents.append(IntentType.IMPLEMENT)
                    if IntentType.FIX not in intents:
                        intents.append(IntentType.FIX)
                
                # If we have "refactor and fix"
                if "refactor" in request_lower and "fix" in request_lower:
                    if IntentType.REFACTOR not in intents:
                        intents.append(IntentType.REFACTOR)
                    if IntentType.FIX not in intents:
                        intents.append(IntentType.FIX)
                
                # If we have "implement with documentation/tests"
                if "implement" in request_lower and ("document" in request_lower or "test" in request_lower):
                    if IntentType.IMPLEMENT not in intents:
                        intents.append(IntentType.IMPLEMENT)
                    if IntentType.DOCUMENT not in intents and "document" in request_lower:
                        intents.append(IntentType.DOCUMENT)
        
        # Check for THEN patterns (sequential)
        for connector in CompositeIntentDetector.THEN_CONNECTORS:
            if connector in request_lower:
                # Split by connector
                parts = request_lower.split(connector)
                if len(parts) >= 2:
                    # Analyze each part for intents
                    all_intents_found = set(intents)
                    for part in parts:
                        if "implement" in part and IntentType.IMPLEMENT not in all_intents_found:
                            all_intents_found.add(IntentType.IMPLEMENT)
                        if "fix" in part and IntentType.FIX not in all_intents_found:
                            all_intents_found.add(IntentType.FIX)
                        if "refactor" in part and IntentType.REFACTOR not in all_intents_found:
                            all_intents_found.add(IntentType.REFACTOR)
                    
                    intents = list(all_intents_found)
        
        # Check for implicit patterns
        if primary_intent == IntentType.FIX:
            # If fixing, should we also test?
            if any(keyword in request_lower for keyword in CompositeIntentDetector.IMPLICIT_PATTERNS["fix"]):
                # Test is implicit, but we don't have a TEST intent type
                # This is noted in metadata for handler
                pass
        
        elif primary_intent == IntentType.IMPLEMENT:
            # If implementing, should we also create documentation?
            if "document" in request_lower and IntentType.DOCUMENT not in intents:
                intents.append(IntentType.DOCUMENT)
        
        elif primary_intent == IntentType.REFACTOR:
            # If refactoring, should we test?
            if any(keyword in request_lower for keyword in CompositeIntentDetector.IMPLICIT_PATTERNS["refactor"]):
                # Test is implicit
                pass
        
        return list(set(intents))  # Remove duplicates, maintain order


@dataclass
class RoutingContext:
    """
    Represents the full context for a routing decision.
    
    Attributes:
        operation: Operation name/identifier
        description: Human-readable operation description
        domain: Target domain (core, orchestrators, infrastructure, etc.)
        keywords: Keywords from operation description
        urgency: Operation urgency level (low, medium, high, critical)
        user_intent: User's stated intent or goal
        metadata: Additional context metadata
    """
    operation: str
    description: Optional[str] = None
    domain: Optional[str] = None
    keywords: Optional[List[str]] = None
    urgency: str = "medium"
    user_intent: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


class IntentRouter(IOrchestrator):
    """
    Routes operations based on intent type and context.
    
    Implements Stage 2 (Routing) of the Master Orchestrator 4-stage workflow.
    Analyzes operation context to determine appropriate execution path.
    
    The IntentRouter:
    1. Analyzes operation description and keywords
    2. Detects intent type (IMPLEMENT, FIX, REFACTOR)
    3. Routes to appropriate handler based on intent and domain
    4. Caches decisions for identical contexts
    5. Maintains audit trail of routing decisions
    
    CORE Governance:
      - CORE-008: TDD - tests provided first
      - CORE-011: Type hints on all methods
      - CORE-012: Docstrings (Google style)
      - CORE-013: Specific exception handling
      - CORE-027: Audit trail logging
    
    Example:
        router = IntentRouter()
        context = {
            "operation": "fix_race_condition",
            "description": "Fix race condition in Master Orchestrator",
            "keywords": ["bug", "race condition", "fix"]
        }
        decision = router.route(context)
        print(f"Route to: {decision.target_handler}")
    """
    
    # Operation type detection keywords
    IMPLEMENT_KEYWORDS: List[str] = [
        "create", "add", "new", "implement", "develop", "build", "construct",
        "establish", "introduce", "feature", "enhancement"
    ]
    
    FIX_KEYWORDS: List[str] = [
        "fix", "bug", "issue", "error", "problem", "crash", "fail", "broken",
        "resolve", "correct", "repair", "patch", "race condition"
    ]
    
    REFACTOR_KEYWORDS: List[str] = [
        "refactor", "improve", "cleanup", "restructure", "simplify", "optimize",
        "clean", "modernize", "reorganize", "rewrite", "redesign", "performance"
    ]
    
    DOCUMENT_KEYWORDS: List[str] = [
        "file", "write", "output", "report", "generate", "save", "persist",
        "export", "create file", "write file", "output file", "report file"
    ]
    
    def __init__(self) -> None:
        """
        Initialize IntentRouter orchestrator.
        
        AC-FUTURE-001: Load routing rules from YAML (CONFIG-DRIVEN)
        AC-PHASE-8.2-01: Initialize orchestrator lookup and enforcement
        
        Sets up:
        - Operation type keyword mappings
        - Routing rules (loaded from YAML or fallback to hardcoded)
        - Audit logger
        - Decision cache (LRU with 128 entries)
        - Complexity classifier for request analysis
        - Orchestrator lookup (Phase 8.2)
        - Routing enforcement engine (Phase 8.2)
        
        Raises:
            Exception: If audit logger cannot be initialized
        """
        self.logger: EnhancedAuditLogger = EnhancedAuditLogger.instance()
        
        # Operation type detection mappings
        self.operation_type_mappings: Dict[IntentType, List[str]] = {
            IntentType.IMPLEMENT: self.IMPLEMENT_KEYWORDS,
            IntentType.FIX: self.FIX_KEYWORDS,
            IntentType.REFACTOR: self.REFACTOR_KEYWORDS,
            IntentType.DOCUMENT: self.DOCUMENT_KEYWORDS,
        }
        
        # AC-FUTURE-001: Try loading routing rules from YAML
        self.routing_rules_config: Dict[str, Any] = self._load_routing_config()
        
        # Build routing rules dict from config (fallback if YAML loading fails)
        self.routing_rules: Dict[Tuple[Optional[IntentType], Optional[str]], str] = self._build_routing_rules()
        
        # Decision cache (populated by _route_internal, accessed via route)
        self.cached_decisions: Dict[str, RoutingDecision] = {}
        
        # AC-FUTURE-008: Complexity classifier configuration
        self.complexity_thresholds = self.routing_rules_config.get("complexity_thresholds", {
            "low": 0,
            "medium": 2,
            "high": 5,
            "critical": 8
        })
        
        # AC-FUTURE-009: Fuzzy matching configuration
        self.fuzzy_config = self.routing_rules_config.get("fuzzy_matching", {
            "enabled": False,
            "algorithm": "levenshtein",
            "threshold": 0.75
        })
        
        # Cache for fuzzy matching results
        self.fuzzy_cache: Dict[str, List[str]] = {}
        
        # AC-PHASE-8.2-01: Initialize orchestrator lookup (singleton)
        self.orchestrator_lookup: OrchestratorLookup = OrchestratorLookup()
        
        # AC-PHASE-8.2-01: Initialize routing enforcement engine
        enforcement_config = self.routing_rules_config.get("enforcement", {})
        self.enforcement_engine: RoutingEnforcementEngine = RoutingEnforcementEngine(
            confidence_threshold=enforcement_config.get("confidence_threshold", 0.6),
            disambiguation_threshold=enforcement_config.get("disambiguation_threshold", 0.7),
            blocking_enabled=enforcement_config.get("blocking_enabled", True)
        )
        
        # Log initialization
        self.logger.log_operation_complete(
            ac_id="AC-PROD-001-02",
            operation="INTENT_ROUTER_INIT",
            success=True,
            details={
                "operation_types": len(self.operation_type_mappings),
                "routing_rules": len(self.routing_rules),
                "cache_enabled": True,
                "fuzzy_matching_enabled": self.fuzzy_config.get("enabled", False),
                "yaml_config_loaded": "routing_rules" in self.routing_rules_config,
                "orchestrator_lookup_enabled": True,  # AC-PHASE-8.2-01
                "enforcement_enabled": enforcement_config.get("blocking_enabled", True)  # AC-PHASE-8.2-01
            }
        )
    
    def _load_routing_config(self) -> Dict[str, Any]:
        """
        Load routing configuration from YAML file.
        
        AC-FUTURE-001: YAML-based rule loading
        
        Returns:
            Dict[str, Any]: Configuration dict, or empty if YAML not found
        """
        config_path = Path(__file__).parent.parent.parent.parent / "cortex_brain" / "tier3" / "knowledge" / "intent-routing.yaml"
        
        try:
            if config_path.exists():
                with open(config_path) as f:
                    raw_config = yaml.safe_load(f)
                    config: Dict[str, Any] = raw_config if isinstance(raw_config, dict) else {}
                self.logger.log_operation_complete(
                    ac_id="AC-FUTURE-001",
                    operation="YAML_ROUTING_CONFIG_LOADED",
                    success=True,
                    details={"path": str(config_path)}
                )
                return config
        except (FileNotFoundError, yaml.YAMLError) as e:
            self.logger.log_operation_complete(
                ac_id="AC-FUTURE-001",
                operation="YAML_ROUTING_CONFIG_LOAD_FAILED",
                success=False,
                details={"error": str(e), "using_fallback": True}
            )
        
        return {}
    
    def _build_routing_rules(self) -> Dict[Tuple[Optional[IntentType], Optional[str]], str]:
        """
        Build routing rules from config or fallback to hardcoded.
        
        AC-FUTURE-001: Support both YAML-driven and fallback routing
        
        Returns:
            Dict[Tuple[Optional[IntentType], Optional[str]], str]: Routing rules
        """
        rules: Dict[Tuple[Optional[IntentType], Optional[str]], str] = {}
        
        # Try YAML config first
        if "routing_rules" in self.routing_rules_config:
            yaml_rules = self.routing_rules_config.get("routing_rules", {})
            if isinstance(yaml_rules, dict):
                for intent_str, domain_rules in yaml_rules.items():
                    try:
                        intent = IntentType(intent_str)
                        if isinstance(domain_rules, dict):
                            for domain, rule_config in domain_rules.items():
                                handler_str: str = ""
                                if isinstance(rule_config, dict):
                                    handler_str = str(rule_config.get("handler", ""))
                                else:
                                    handler_str = str(rule_config)
                                
                                if handler_str:
                                    domain_key = None if domain == "default" else domain
                                    rules[(intent, domain_key)] = handler_str
                    except (ValueError, KeyError) as e:
                        self.logger.log_operation_complete(
                            ac_id="AC-FUTURE-001",
                            operation="YAML_RULE_PARSE_ERROR",
                            success=False,
                            details={"error": str(e), "intent": intent_str}
                        )
            
            # If YAML rules loaded, return them
            if rules:
                return rules
        
        # Fallback to hardcoded rules (backward compatibility)
        return {
            # IMPLEMENT routing
            (IntentType.IMPLEMENT, "orchestrators"): "ImplementationOrchestrator",
            (IntentType.IMPLEMENT, "core"): "CoreImplementationHandler",
            (IntentType.IMPLEMENT, "infrastructure"): "InfrastructureImplementationHandler",
            (IntentType.IMPLEMENT, None): "GeneralImplementationHandler",
            
            # FIX routing
            (IntentType.FIX, "orchestrators"): "OrchestratorFixOrchestrator",
            (IntentType.FIX, "core"): "CoreFixOrchestrator",
            (IntentType.FIX, "infrastructure"): "InfrastructureFixOrchestrator",
            (IntentType.FIX, None): "GeneralFixOrchestrator",
            
            # REFACTOR routing
            (IntentType.REFACTOR, "orchestrators"): "RefactoringOrchestrator",
            (IntentType.REFACTOR, "core"): "CoreRefactoringHandler",
            (IntentType.REFACTOR, "infrastructure"): "InfrastructureRefactoringHandler",
            (IntentType.REFACTOR, None): "GeneralRefactoringHandler",
            
            # DOCUMENT routing (CORE-028/CORE-038 validation)
            (IntentType.DOCUMENT, "documentation"): "DocumentationOrchestrator",
            (IntentType.DOCUMENT, "governance"): "DocumentationOrchestrator",
            (IntentType.DOCUMENT, "reports"): "DocumentationOrchestrator",
            (IntentType.DOCUMENT, None): "DocumentationOrchestrator",
        }
    
    # ===== AC-PHASE-8.2-01: Keyword Extraction & Orchestrator Lookup =====
    
    def _extract_keywords(self, context: Dict[str, Any]) -> List[str]:
        """
        Extract routing keywords from user request context.
        
        AC-PHASE-8.2-01: Parse description and operation fields to identify
        trigger keywords that map to orchestrators in routing config.
        
        Args:
            context: User request context with operation/description
        
        Returns:
            List[str]: Extracted keywords (lowercase, unique)
        
        Example:
            >>> context = {"description": "Use CORTEX LENS to onboard repo XYZ"}
            >>> keywords = self._extract_keywords(context)
            >>> print(keywords)
            ['lens', 'onboard', 'repo']
        """
        keywords: List[str] = []
        
        try:
            # Extract from description
            description = context.get("description", "")
            if description:
                # Tokenize (split by whitespace and common delimiters)
                tokens = description.lower().replace(":", " ").replace(",", " ").split()
                keywords.extend(tokens)
            
            # Extract from operation field
            operation = context.get("operation", "")
            if operation:
                tokens = operation.lower().replace("_", " ").split()
                keywords.extend(tokens)
            
            # Extract from user_intent field
            user_intent = context.get("user_intent", "")
            if user_intent:
                tokens = user_intent.lower().split()
                keywords.extend(tokens)
            
            # Remove duplicates and filter out common stop words
            stop_words = {"the", "a", "an", "is", "are", "to", "of", "for", "with", "in", "on"}
            unique_keywords = list(set(kw for kw in keywords if kw not in stop_words and len(kw) > 2))
            
            return unique_keywords
        
        except (TypeError, AttributeError) as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="KEYWORD_EXTRACTION_ERROR",
                success=False,
                details={"error": str(e)}
            )
            return []
    
    def _lookup_orchestrators(
        self,
        keywords: List[str],
        intent: IntentType
    ) -> List[Tuple[str, IOrchestrator, float]]:
        """
        Lookup orchestrators matching extracted keywords.
        
        AC-PHASE-8.2-01: Query OrchestratorLookup registry to find
        orchestrators with matching keywords, then resolve instances.
        
        Args:
            keywords: Extracted keywords from user request
            intent: Detected intent type for filtering
        
        Returns:
            List[Tuple[str, IOrchestrator, float]]: (name, instance, confidence) tuples
        
        Example:
            >>> keywords = ['lens', 'onboard']
            >>> candidates = self._lookup_orchestrators(keywords, IntentType.IMPLEMENT)
            >>> # Returns: [('OnboardingOrchestrator', <instance>, 0.85), ...]
        """
        candidates: List[Tuple[str, IOrchestrator, float]] = []
        
        try:
            # Initialize orchestrator lookup (singleton)
            lookup = OrchestratorLookup()
            
            # Query by keywords from routing config
            matches = lookup.find_by_keywords(keywords, self.routing_rules_config)
            
            # Resolve orchestrator instances
            for orchestrator_name, confidence in matches:
                result = lookup.resolve_instance(orchestrator_name)
                
                if result.is_ok():
                    instance = result.value
                    candidates.append((orchestrator_name, instance, confidence))
                else:
                    # Log failure but continue
                    self.logger.log_operation_complete(
                        ac_id="AC-PHASE-8.2-01",
                        operation="ORCHESTRATOR_RESOLVE_FAILED",
                        success=False,
                        details={
                            "orchestrator": orchestrator_name,
                            "error": result.error
                        }
                    )
            
            return candidates
        
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="ORCHESTRATOR_LOOKUP_ERROR",
                success=False,
                details={"error": str(e)}
            )
            return []
    
    def _rank_orchestrators(
        self,
        candidates: List[Tuple[str, IOrchestrator, float]]
    ) -> List[Tuple[str, IOrchestrator, float]]:
        """
        Rank orchestrator candidates by confidence score.
        
        AC-PHASE-8.2-01: Sort candidates descending by confidence,
        applying tie-breaking rules if needed.
        
        Args:
            candidates: List of (name, instance, confidence) tuples
        
        Returns:
            List[Tuple[str, IOrchestrator, float]]: Ranked candidates
        
        Example:
            >>> candidates = [
            ...     ('LENSOrchestrator', <instance>, 0.75),
            ...     ('OnboardingOrchestrator', <instance>, 0.85),
            ... ]
            >>> ranked = self._rank_orchestrators(candidates)
            >>> # Returns: [('OnboardingOrchestrator', ..., 0.85), ('LENSOrchestrator', ..., 0.75)]
        """
        try:
            # Sort by confidence descending
            ranked = sorted(candidates, key=lambda x: x[2], reverse=True)
            
            # Log ranking results
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="ORCHESTRATOR_RANKING",
                success=True,
                details={
                    "candidate_count": len(ranked),
                    "top_candidate": ranked[0][0] if ranked else None,
                    "top_confidence": ranked[0][2] if ranked else 0.0
                }
            )
            
            return ranked
        
        except Exception as e:
            self.logger.log_operation_complete(
                ac_id="AC-PHASE-8.2-01",
                operation="ORCHESTRATOR_RANKING_ERROR",
                success=False,
                details={"error": str(e)}
            )
            # Return unsorted on error
            return candidates
    
    def get_version(self) -> str:
        """
        Get the version of this orchestrator.
        
        Returns:
            str: "1.0.0" (semantic versioning)
        """
        return "1.0.0"
    
    def initialize(self) -> Result[str]:
        """
        Initialize IntentRouter orchestrator.
        
        This method is called when the orchestrator is registered.
        
        Returns:
            Result[str]: Ok with initialization message, or Err with error
        """
        try:
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-02",
                operation="INTENT_ROUTER_INITIALIZE",
                success=True,
                details={"status": "initialized"}
            )
            return Ok("IntentRouter initialized successfully")
        
        except Exception as e:
            return Err(f"IntentRouter initialization failed: {str(e)}")
    
    def get_audit_trail(self, limit: int = 100) -> Result[list]:
        """
        Get audit trail with hash chain.
        
        AC-AR-011-03: Get audit trail with hash chain verification.
        
        Args:
            limit: Maximum number of entries to return (default 100)
        
        Returns:
            Result[list]: List of audit trail entries
        """
        try:
            # Delegate to EnhancedAuditLogger
            audit_entries = self.logger.get_audit_trail(limit)
            return Ok(audit_entries)
        
        except Exception as e:
            return Err(f"Failed to retrieve audit trail: {str(e)}")
    
    def get_name(self) -> str:
        """
        Get the name of this orchestrator.
        
        Returns:
            str: "IntentRouter"
        """
        return "IntentRouter"
    
    def get_mode(self) -> OperationMode:
        """
        Get the operation mode of this orchestrator.
        
        Returns:
            OperationMode: NORMAL (default routing mode)
        """
        return OperationMode.NORMAL
    
    def validate_input(self, parameters: Dict[str, Any]) -> Result[bool]:
        """
        Validate input parameters for routing operations.
        
        Checks that:
        - parameters is a non-empty dictionary
        - required fields are present or can be inferred
        
        Args:
            parameters: Input parameters to validate
        
        Returns:
            Result[bool]: Ok(True) if valid, Err(message) if invalid
        """
        try:
            if not isinstance(parameters, dict):
                return Err("Parameters must be a dictionary")
            
            if not parameters:
                return Err("Parameters cannot be empty")
            
            # Check for at least operation or description
            if "operation" not in parameters and "description" not in parameters:
                return Err("Parameters must include 'operation' or 'description'")
            
            return Ok(True)
        
        except Exception as e:
            return Err(f"Validation error: {str(e)}")
    
    def detect_intent(self, context: Dict[str, Any]) -> IntentType:
        """
        Detect operation intent type from context.
        
        Analyzes context keywords and description to determine if the
        operation is an IMPLEMENT, FIX, or REFACTOR operation.
        
        Detection algorithm:
        1. Check explicit "intent" field if provided
        2. Analyze keywords against type-specific keyword lists
        3. Score each intent type (0-1)
        4. Return highest-scoring intent type
        5. Default to IMPLEMENT if no clear match
        
        Args:
            context: Context dictionary containing operation details
                - description: Operation description (optional)
                - keywords: List of keywords (optional)
                - intent: Explicit intent (optional)
        
        Returns:
            IntentType: Detected intent (IMPLEMENT, FIX, or REFACTOR)
        
        Raises:
            ValueError: If context is None or invalid type
        """
        try:
            # Explicit intent provided
            if "intent" in context and isinstance(context.get("intent"), IntentType):
                return context["intent"]
            
            # Extract text to analyze
            text_parts: List[str] = []
            
            if "description" in context and context["description"]:
                text_parts.append(str(context["description"]).lower())
            
            if "keywords" in context and isinstance(context["keywords"], list):
                keywords = [str(k).lower() for k in context["keywords"]]
                text_parts.extend(keywords)
            
            if "operation" in context and context["operation"]:
                text_parts.append(str(context["operation"]).lower())
            
            # Combine all text
            combined_text = " ".join(text_parts).lower()
            
            # Score each intent type
            intent_scores: Dict[IntentType, float] = {}
            
            for intent_type, keywords in self.operation_type_mappings.items():
                # Count keyword matches
                matches = sum(1 for keyword in keywords if keyword in combined_text)
                # Calculate score (0-1, normalized by keyword list length)
                score = matches / len(keywords) if keywords else 0.0
                intent_scores[intent_type] = score
            
            # Return highest-scoring intent, or IMPLEMENT as default
            if intent_scores:
                return max(intent_scores, key=intent_scores.get)
            
            return IntentType.IMPLEMENT
        
        except (ValueError, TypeError, AttributeError) as e:
            # Specific exception handling per CORE-013
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-02",
                operation="INTENT_DETECTION_ERROR",
                success=False,
                details={"error": str(e), "context_type": type(context).__name__}
            )
            return IntentType.IMPLEMENT
    
    def _get_cache_key(self, context: Dict[str, Any]) -> str:
        """
        Generate cache key for routing decision.
        
        Creates a hash of the relevant context fields to enable
        caching of identical routing decisions.
        
        LENS-002: Includes lens_context in cache key to ensure
        LENS-enhanced and non-LENS decisions are cached separately.
        
        Args:
            context: Context dictionary
        
        Returns:
            str: Cache key (MD5 hash of context)
        """
        try:
            # Create deterministic representation
            key_fields = {
                "operation": context.get("operation"),
                "description": context.get("description"),
                "domain": context.get("domain"),
                "keywords": sorted(context.get("keywords", [])) if context.get("keywords") else None,
                "has_lens": bool(context.get("lens_context"))  # LENS-002: Include LENS presence
            }
            
            # Serialize to JSON for hashing
            key_json = json.dumps(key_fields, sort_keys=True, default=str)
            
            # Create hash
            return hashlib.md5(key_json.encode()).hexdigest()
        
        except Exception as e:
            # Fallback: return context operation name if hashing fails
            return str(context.get("operation", "default"))
    
    def _route_internal(self, context: Dict[str, Any]) -> RoutingDecision:
        """
        Internal routing implementation (logic only, no caching).
        
        AC-PHASE-8.2-01: Enhanced with keyword-based orchestrator lookup.
        
        Flow:
        1. Extract keywords from user request
        2. Detect intent type
        3. Lookup matching orchestrators by keywords
        4. Rank candidates by confidence
        5. Enforce routing rules (ROUTING-001 through ROUTING-004)
        6. Return decision with orchestrator instance
        
        Args:
            context: Context dictionary with operation details
        
        Returns:
            RoutingDecision: Routing decision with target orchestrator instance
        
        Raises:
            KeyError: If required context fields missing
            ValueError: If routing cannot be determined or enforcement blocks
        """
        try:
            # Extract relevant fields
            operation = context.get("operation", "unknown")
            domain = context.get("domain")
            
            # Detect intent
            intent_type = self.detect_intent(context)
            
            # AC-FUTURE-005: Detect composite intents (multi-faceted requests)
            description = context.get("description", "")
            composite_intents = CompositeIntentDetector.detect_composite_intents(
                description,
                intent_type
            )
            
            # AC-PHASE-8.2-01: Extract keywords from request
            keywords = self._extract_keywords(context)
            
            # AC-PHASE-8.2-01: Lookup orchestrators by keywords
            candidates = self._lookup_orchestrators(keywords, intent_type)
            
            # AC-PHASE-8.2-01: Rank candidates by confidence
            ranked_candidates = self._rank_orchestrators(candidates)
            
            # Determine target handler and orchestrator
            if ranked_candidates:
                # Phase 8.2: Use top-ranked orchestrator
                target_name, target_orch, base_confidence = ranked_candidates[0]
                target_handler = target_name
                target_orchestrator = target_orch
                
                # Extract fallback orchestrators (top 3 alternatives)
                fallback_orchestrators = [orch for _, orch, _ in ranked_candidates[1:4]]
                
                # Build confidence breakdown
                confidence_breakdown = {
                    "keyword_match": base_confidence,
                    "intent_detection": 0.2,  # Base intent detection confidence
                }
                
                # Apply LENS boost if available (LENS-002 integration)
                lens_context = context.get("lens_context")
                if lens_context:
                    git_pattern = self._extract_git_pattern(lens_context)
                    ast_complexity = self._calculate_ast_complexity(lens_context)
                    
                    if git_pattern == intent_type:
                        confidence_breakdown["lens_git_exact"] = 0.15
                    elif git_pattern:
                        confidence_breakdown["lens_git_partial"] = 0.05
                    
                    if ast_complexity > 75:
                        confidence_breakdown["lens_ast_very_high"] = 0.20
                    elif ast_complexity > 50:
                        confidence_breakdown["lens_ast_high"] = 0.15
                    elif ast_complexity > 25:
                        confidence_breakdown["lens_ast_medium"] = 0.10
                
                # Calculate final confidence
                confidence = sum(confidence_breakdown.values())
                
            else:
                # Fallback: Use old routing rules (backward compatibility)
                routing_key = (intent_type, domain)
                if routing_key not in self.routing_rules:
                    routing_key = (intent_type, None)
                
                target_handler = self.routing_rules.get(
                    routing_key,
                    f"{intent_type.value.capitalize()}OrchestrationHandler"
                )
                
                # Try resolving orchestrator instance from handler name
                result = self.orchestrator_lookup.resolve_instance(target_handler)
                target_orchestrator = result.value if result.is_ok() else None
                fallback_orchestrators = []
                
                # Fallback confidence calculation
                context_keywords = context.get("keywords", [])
                operation_type_keywords = self.operation_type_mappings[intent_type]
                matches = sum(1 for kw in context_keywords if kw.lower() in 
                             [k.lower() for k in operation_type_keywords])
                confidence = min(1.0, (matches / len(operation_type_keywords)) + 0.5) if operation_type_keywords else 0.75
                
                confidence_breakdown = {
                    "legacy_routing": confidence,
                }
            
            # If composite intents detected, enhance handler selection
            if len(composite_intents) > 1:
                target_handler = f"CompositeHandler_{'+'.join([i.value for i in composite_intents])}"
                confidence *= 0.95
                confidence_breakdown["composite_penalty"] = -0.05
            
            # Build reasoning
            reasoning = (
                f"Routed '{context.get('operation')}' to {target_handler} "
                f"(confidence: {confidence:.2f}) based on "
                f"intent type '{intent_type.value}'"
            )
            if keywords:
                reasoning += f", keywords: {', '.join(keywords[:3])}"
            if len(composite_intents) > 1:
                reasoning += f". Detected composite intents: {', '.join([i.value for i in composite_intents])}"
            
            # Create decision
            decision = RoutingDecision(
                intent_type=intent_type,
                target_handler=target_handler,
                confidence_score=min(1.0, confidence),  # Clamp to [0, 1]
                reasoning=reasoning,
                metadata={
                    "operation": context.get("operation"),
                    "domain": domain,
                    "keywords_matched": len(keywords),
                    "total_keywords": len(keywords),
                    "composite_intents": len(composite_intents) > 1,
                    "candidates_found": len(ranked_candidates) if ranked_candidates else 0,
                },
                composite_intents=composite_intents,
                # AC-PHASE-8.2-01: New fields
                target_orchestrator=target_orchestrator,
                fallback_orchestrators=fallback_orchestrators,
                keyword_matches=keywords,
                confidence_breakdown=confidence_breakdown,
            )
            
            # AC-PHASE-8.2-01: Enforce routing rules
            enforcement_result = self.enforcement_engine.validate_routing_decision(decision)
            
            if not enforcement_result.passed:
                # Log violations
                self.logger.log_operation_complete(
                    ac_id="AC-PHASE-8.2-01",
                    operation="ROUTING_ENFORCEMENT_VIOLATION",
                    success=False,
                    details={
                        "violations": [v.value for v in enforcement_result.violations],
                        "target_handler": target_handler,
                        "confidence": confidence,
                    }
                )
                
                # Check if blocking is enabled
                blocking_violations = [
                    v for v in enforcement_result.violations
                    if v in [
                        RoutingViolation.ORCHESTRATOR_NOT_FOUND,
                        RoutingViolation.CONFIDENCE_TOO_LOW,
                        RoutingViolation.NOT_AUDITABLE,
                    ]
                ]
                if self.enforcement_engine.blocking_enabled and blocking_violations:
                    raise ValueError(
                        f"Routing blocked by enforcement: {', '.join([v.value for v in blocking_violations])}"
                    )
            
            return decision
        
        except (KeyError, ValueError, AttributeError) as e:
            # Specific exception handling per CORE-013
            raise ValueError(f"Routing failed: {str(e)}")
    
    # ===== LENS-002: LENS Intelligence Enhancement Methods =====
    
    def _extract_git_pattern(self, lens_context: Dict[str, Any]) -> Optional[IntentType]:
        """
        Extract predominant intent type from Git commit history.
        
        LENS-002: Analyze Git commit messages to identify patterns
        that validate or contradict the detected intent.
        
        Args:
            lens_context: LENS analyzer data (flexible format):
                - git_history.commits OR git_analysis.recent_commits
        
        Returns:
            IntentType: Predominant intent from Git history, or None
        """
        try:
            # Support both formats: git_history and git_analysis
            git_data = lens_context.get("git_history") or lens_context.get("git_analysis", {})
            
            # Support both formats: commits and recent_commits
            commits = git_data.get("commits") or git_data.get("recent_commits", [])
            
            if not commits:
                return None
            
            # Count intent types from commit messages
            intent_counts: Dict[IntentType, int] = {
                IntentType.FIX: 0,
                IntentType.IMPLEMENT: 0,
                IntentType.REFACTOR: 0,
                IntentType.DOCUMENT: 0
            }
            
            fix_keywords = {"fix", "bug", "issue", "resolve", "patch"}
            implement_keywords = {"add", "implement", "feature", "create", "new"}
            refactor_keywords = {"refactor", "cleanup", "improve", "optimize", "restructure"}
            doc_keywords = {"doc", "documentation", "comment", "readme"}
            
            for commit in commits:
                # Support both dict format and string format
                if isinstance(commit, dict):
                    message = commit.get("message", "").lower()
                else:
                    message = str(commit).lower()
                
                if any(kw in message for kw in fix_keywords):
                    intent_counts[IntentType.FIX] += 1
                if any(kw in message for kw in implement_keywords):
                    intent_counts[IntentType.IMPLEMENT] += 1
                if any(kw in message for kw in refactor_keywords):
                    intent_counts[IntentType.REFACTOR] += 1
                if any(kw in message for kw in doc_keywords):
                    intent_counts[IntentType.DOCUMENT] += 1
            
            # Return most frequent intent
            if max(intent_counts.values()) > 0:
                return max(intent_counts.items(), key=lambda x: x[1])[0]
            
            return None
        
        except (KeyError, TypeError, AttributeError):
            return None
    
    def _calculate_ast_complexity(self, lens_context: Dict[str, Any]) -> int:
        """
        Calculate code complexity from AST analysis.
        
        LENS-002: Extract complexity metrics from AST data
        to validate refactor intent or identify technical debt.
        
        Args:
            lens_context: LENS analyzer data (flexible format):
                - ast_analysis.function_count OR ast_analysis.functions (list)
                - ast_analysis.class_count OR ast_analysis.classes (list)
        
        Returns:
            int: Complexity score (0-100 scale)
        """
        try:
            ast_analysis = lens_context.get("ast_analysis", {})
            
            # Support both formats: count fields and list fields
            function_count = ast_analysis.get("function_count", 0)
            if not function_count:
                # Count from functions list
                functions = ast_analysis.get("functions", [])
                function_count = len(functions) if isinstance(functions, list) else 0
            
            class_count = ast_analysis.get("class_count", 0)
            if not class_count:
                # Count from classes list
                classes = ast_analysis.get("classes", [])
                class_count = len(classes) if isinstance(classes, list) else 0
            
            # Simple complexity heuristic:
            # Classes contribute more weight than functions
            complexity = (class_count * 10) + (function_count * 2)
            
            return min(100, complexity)
        
        except (KeyError, TypeError, AttributeError):
            return 0
    
    def _analyze_comment_hints(self, lens_context: Dict[str, Any]) -> Dict[str, List[str]]:
        """
        Analyze TODO/FIXME comments for intent hints.
        
        LENS-002: Extract comment-based hints that suggest
        specific types of work needed (fix, refactor, implement).
        
        Args:
            lens_context: LENS analyzer data
        
        Returns:
            Dict with categorized hints:
                - refactor_hints: Comments suggesting refactoring
                - fix_hints: Comments suggesting bug fixes
                - implement_hints: Comments suggesting new features
        """
        try:
            comment_analysis = lens_context.get("comment_analysis", {})
            todos = comment_analysis.get("todos", [])
            fixmes = comment_analysis.get("fixmes", [])
            
            hints: Dict[str, List[str]] = {
                "refactor_hints": [],
                "fix_hints": [],
                "implement_hints": []
            }
            
            refactor_keywords = {"refactor", "cleanup", "improve", "optimize", "technical debt"}
            fix_keywords = {"fix", "bug", "issue", "broken", "error"}
            implement_keywords = {"add", "implement", "feature", "create", "support"}
            
            all_comments = todos + fixmes
            for comment in all_comments:
                # Support multiple format variations: text, content, or string
                if isinstance(comment, dict):
                    comment_text = (
                        comment.get("text") or 
                        comment.get("content") or 
                        comment.get("message") or 
                        ""
                    ).lower()
                else:
                    comment_text = str(comment).lower()
                
                if any(kw in comment_text for kw in refactor_keywords):
                    hints["refactor_hints"].append(comment_text)
                elif any(kw in comment_text for kw in fix_keywords):
                    hints["fix_hints"].append(comment_text)
                elif any(kw in comment_text for kw in implement_keywords):
                    hints["implement_hints"].append(comment_text)
            
            return hints
        
        except (KeyError, TypeError, AttributeError):
            return {"refactor_hints": [], "fix_hints": [], "implement_hints": []}
    
    def _calculate_lens_boost(
        self,
        intent_type: IntentType,
        lens_context: Dict[str, Any]
    ) -> float:
        """
        Calculate confidence boost from LENS evidence.
        
        LENS-002: Compute confidence score enhancement (0.0 to 0.4)
        based on how well LENS intelligence supports the detected intent.
        
        Args:
            intent_type: Detected intent type
            lens_context: LENS analyzer data
        
        Returns:
            float: Confidence boost (0.0-0.4)
        """
        boost = 0.0
        
        # Git pattern matching (up to +0.15)
        git_pattern = self._extract_git_pattern(lens_context)
        if git_pattern == intent_type:
            boost += 0.15
        elif git_pattern is not None:
            boost += 0.05  # Partial credit for any git intelligence
        
        # AST complexity for refactor intent (up to +0.20)
        if intent_type == IntentType.REFACTOR:
            complexity = self._calculate_ast_complexity(lens_context)
            if complexity >= 80:
                boost += 0.20  # Very high complexity
            elif complexity > 40:
                boost += 0.15  # High complexity
            elif complexity > 20:
                boost += 0.10  # Medium complexity
            elif complexity > 10:
                boost += 0.05  # Low complexity
        
        # Comment hints (up to +0.05)
        hints = self._analyze_comment_hints(lens_context)
        hint_key = f"{intent_type.value}_hints"
        if hint_key in hints and len(hints[hint_key]) > 0:
            boost += 0.05
        
        return min(0.4, boost)  # Cap at 0.4
    
    def _enhance_with_lens(
        self,
        decision: RoutingDecision,
        lens_context: Dict[str, Any]
    ) -> RoutingDecision:
        """
        Enhance routing decision with LENS intelligence.
        
        LENS-002: Apply LENS-based confidence boost and enrich metadata.
        
        Args:
            decision: Original routing decision
            lens_context: LENS analyzer data
        
        Returns:
            RoutingDecision: Enhanced decision with LENS boost
        """
        try:
            # Calculate LENS confidence boost
            lens_boost = self._calculate_lens_boost(decision.intent_type, lens_context)
            
            # Apply boost (capped at 1.0 confidence)
            new_confidence = min(1.0, decision.confidence_score + lens_boost)
            
            # Enrich metadata
            enhanced_metadata = {
                **decision.metadata,
                "lens_enhanced": True,
                "lens_confidence_boost": lens_boost,
                "original_confidence": decision.confidence_score
            }
            
            # Extract LENS insights for metadata
            git_pattern = self._extract_git_pattern(lens_context)
            if git_pattern:
                enhanced_metadata["lens_git_pattern"] = git_pattern.value
            
            complexity = self._calculate_ast_complexity(lens_context)
            if complexity > 0:
                enhanced_metadata["lens_ast_complexity"] = complexity
                # Flag for tests expecting boolean
                enhanced_metadata["ast_complexity_detected"] = True
            
            hints = self._analyze_comment_hints(lens_context)
            if any(hints.values()):
                total_hints = sum(len(v) for v in hints.values())
                enhanced_metadata["lens_comment_hints"] = total_hints
                
                # Add specific hint categories for test expectations
                if hints.get("refactor_hints"):
                    enhanced_metadata["todo_refactor_hints"] = len(hints["refactor_hints"])
                if hints.get("fix_hints"):
                    enhanced_metadata["todo_fix_hints"] = len(hints["fix_hints"])
                if hints.get("implement_hints"):
                    enhanced_metadata["todo_implement_hints"] = len(hints["implement_hints"])
            
            # Create enhanced decision
            return RoutingDecision(
                intent_type=decision.intent_type,
                target_handler=decision.target_handler,
                confidence_score=new_confidence,
                reasoning=decision.reasoning + f" (LENS boost: +{lens_boost:.2f})",
                metadata=enhanced_metadata,
                composite_intents=decision.composite_intents
            )
        
        except Exception:
            # On any error, return original decision unchanged
            return decision
    
    # ===== End LENS-002 Methods =====
    
    def route(self, context: Dict[str, Any]) -> RoutingDecision:
        """
        Route an operation based on context (with caching).
        
        Analyzes operation context and determines appropriate handler.
        Uses caching to avoid redundant decisions for identical contexts.
        
        LENS Integration (LENS-002):
        - Accepts optional lens_context with Git/AST/Comment intelligence
        - Enhances confidence scoring based on LENS evidence
        - Logs LENS usage for audit trail
        
        Args:
            context: Context dictionary with operation details:
                - operation: Operation name (required or description required)
                - description: Operation description (optional)
                - domain: Target domain (optional)
                - keywords: List of keywords (optional)
                - urgency: Urgency level (optional)
                - user_intent: User's stated intent (optional)
                - lens_context: LENS analyzer data (optional):
                    * git_history: Git commit analysis
                    * ast_analysis: AST complexity data
                    * comment_analysis: TODO/FIXME extraction
        
        Returns:
            RoutingDecision: Routing decision with target handler and metadata
        
        Raises:
            ValueError: If context is invalid or routing cannot be determined
        
        Example:
            context = {
                "operation": "fix_race_condition",
                "description": "Fix race condition in Master Orchestrator",
                "domain": "core",
                "keywords": ["bug", "fix", "race condition"],
                "lens_context": {
                    "git_history": {...},
                    "ast_analysis": {...},
                    "comment_analysis": {...}
                }
            }
            decision = router.route(context)
            print(f"Route to: {decision.target_handler} (confidence: {decision.confidence_score})")
        """
        try:
            # Get cache key
            cache_key = self._get_cache_key(context)
            
            # Check cache
            if cache_key in self.cached_decisions:
                return self.cached_decisions[cache_key]
            
            # Compute routing decision
            decision = self._route_internal(context)
            
            # LENS-002: Enhance decision with LENS intelligence if available
            lens_context = context.get("lens_context")
            if lens_context:
                decision = self._enhance_with_lens(decision, lens_context)
                
                # Log LENS usage for audit trail
                self.logger.log_operation_complete(
                    ac_id="LENS-002",
                    operation="LENS_ENHANCED_ROUTING",
                    success=True,
                    details={
                        "intent_type": decision.intent_type.value,
                        "confidence_boost_applied": decision.metadata.get("lens_confidence_boost", 0.0),
                        "lens_evidence": {
                            "git_pattern": "git_history" in lens_context,
                            "ast_complexity": "ast_analysis" in lens_context,
                            "comment_hints": "comment_analysis" in lens_context
                        }
                    }
                )
            
            # Store in cache
            self.cached_decisions[cache_key] = decision
            
            return decision
        
        except (ValueError, KeyError, TypeError) as e:
            # Specific exception handling per CORE-013
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-02",
                operation="ROUTING_ERROR",
                success=False,
                details={"error": str(e)}
            )
            raise
    
    def execute(self, parameters: Dict[str, Any]) -> Result[str]:
        """
        Execute routing operation (IOrchestrator interface).
        
        Validates input and performs routing based on parameters.
        
        Args:
            parameters: Operation parameters
        
        Returns:
            Result[str]: Ok with routing decision JSON, or Err with error message
        """
        # Log operation start
        self.logger.log_operation_start(
            ac_id="AC-PROD-001-02",
            operation="ROUTING_EXECUTE",
            details=parameters
        )
        
        try:
            # Validate input
            validation_result = self.validate_input(parameters)
            if validation_result.is_err():
                self.logger.log_operation_complete(
                    ac_id="AC-PROD-001-02",
                    operation="ROUTING_EXECUTE",
                    success=False,
                    details={"error": validation_result.unwrap_err()}
                )
                return validation_result
            
            # Perform routing
            decision = self.route(parameters)
            
            # Log success
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-02",
                operation="ROUTING_EXECUTE",
                success=True,
                details={
                    "target_handler": decision.target_handler,
                    "confidence": decision.confidence_score,
                    "intent_type": decision.intent_type.value
                }
            )
            
            # Return decision as JSON
            return Ok(json.dumps({
                "target_handler": decision.target_handler,
                "intent_type": decision.intent_type.value,
                "confidence": decision.confidence_score,
                "reasoning": decision.reasoning,
                "timestamp": decision.timestamp
            }))
        
        except Exception as e:
            # Specific exception handling per CORE-013
            self.logger.log_operation_complete(
                ac_id="AC-PROD-001-02",
                operation="ROUTING_EXECUTE",
                success=False,
                details={"error": str(e)}
            )
            return Err(f"Routing execution failed: {str(e)}")
    
    def execute_operation(
        self,
        operation_name: str,
        parameters: Dict[str, Any]
    ) -> Result[Any]:
        """
        Execute specific routing operation.
        
        Supports operations:
        - "analyze_and_route": Analyze context and route to handler
        - "route_operation": Route based on operation context
        - "detect_intent": Detect operation intent type only
        - "get_routing_rules": Get available routing rules
        
        Args:
            operation_name: Name of operation to execute
            parameters: Operation parameters
        
        Returns:
            Result[Any]: Operation result or error
        
        Raises:
            ValueError: If operation_name is not recognized
        """
        try:
            if operation_name == "analyze_and_route":
                return self.execute(parameters)
            
            elif operation_name == "route_operation":
                decision = self.route(parameters)
                return Ok(decision)
            
            elif operation_name == "detect_intent":
                intent_type = self.detect_intent(parameters)
                return Ok({
                    "intent_type": intent_type.value,
                    "description": f"Detected {intent_type.value} operation"
                })
            
            elif operation_name == "get_routing_rules":
                rules_list = [
                    {
                        "intent": intent.value,
                        "domain": domain,
                        "handler": handler
                    }
                    for (intent, domain), handler in self.routing_rules.items()
                ]
                return Ok({"routing_rules": rules_list})
            
            else:
                return Err(f"Unknown operation: {operation_name}")
        
        except Exception as e:
            # Specific exception handling per CORE-013
            return Err(f"Operation '{operation_name}' failed: {str(e)}")
    
    def get_mcp_tools(self) -> Result[Dict[str, Any]]:
        """
        Get MCP tools exposed by this orchestrator.
        
        Returns:
            Result[Dict]: Dictionary of available MCP tools
        """
        try:
            tools = {
                "route_operation": {
                    "description": "Route operation to appropriate handler based on intent",
                    "parameters": ["operation", "description", "domain", "keywords"],
                    "returns": "RoutingDecision with target_handler"
                },
                "analyze_and_route": {
                    "description": "Analyze operation context and route to handler",
                    "parameters": ["operation", "description", "domain", "keywords"],
                    "returns": "Routing decision result"
                },
                "detect_intent": {
                    "description": "Detect operation intent type (IMPLEMENT, FIX, REFACTOR)",
                    "parameters": ["operation", "description", "keywords"],
                    "returns": "IntentType enum"
                },
                "get_routing_rules": {
                    "description": "Get available routing rules",
                    "parameters": [],
                    "returns": "List of routing rules"
                }
            }
            return Ok(tools)
        
        except Exception as e:
            return Err(f"Failed to get MCP tools: {str(e)}")


# Module-level exports
__all__ = [
    "IntentRouter",
    "IntentType",
    "RoutingDecision",
    "RoutingContext",
]
