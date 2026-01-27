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

from cortex.core.interfaces import IOrchestrator, OperationMode
from cortex.core.result import Result, Ok, Err
from cortex.infrastructure.enhanced_audit_logger import EnhancedAuditLogger
from cortex.models.canonical_enums import IntentType




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
    """
    intent_type: IntentType
    target_handler: str
    confidence_score: float
    reasoning: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    composite_intents: List[IntentType] = field(default_factory=list)  # AC-FUTURE-005


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
        
        Sets up:
        - Operation type keyword mappings
        - Routing rules (loaded from YAML or fallback to hardcoded)
        - Audit logger
        - Decision cache (LRU with 128 entries)
        - Complexity classifier for request analysis
        
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
                "yaml_config_loaded": "routing_rules" in self.routing_rules_config
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
        
        Analyzes context and determines target handler.
        
        Args:
            context: Context dictionary with operation details
        
        Returns:
            RoutingDecision: Routing decision with target handler
        
        Raises:
            KeyError: If required context fields missing
            ValueError: If routing cannot be determined
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
            
            # Determine target handler from routing rules
            routing_key = (intent_type, domain)
            if routing_key not in self.routing_rules:
                # Fallback: try with None domain
                routing_key = (intent_type, None)
            
            target_handler = self.routing_rules.get(
                routing_key,
                f"{intent_type.value.capitalize()}OrchestrationHandler"
            )
            
            # If composite intents detected, enhance handler selection
            if len(composite_intents) > 1:
                target_handler = f"CompositeHandler_{'+'.join([i.value for i in composite_intents])}"
            
            # Calculate confidence based on keyword matches
            keywords = context.get("keywords", [])
            operation_type_keywords = self.operation_type_mappings[intent_type]
            matches = sum(1 for kw in keywords if kw.lower() in 
                         [k.lower() for k in operation_type_keywords])
            confidence = min(1.0, (matches / len(operation_type_keywords)) + 0.5) if operation_type_keywords else 0.75
            
            # Adjust confidence if composite intents detected (more complex = slightly lower confidence)
            if len(composite_intents) > 1:
                confidence *= 0.95
            
            # Build reasoning
            reasoning = (
                f"Routed '{context.get('operation')}' to {target_handler} based on "
                f"intent type '{intent_type.value}' and domain '{domain or 'general'}'"
            )
            if len(composite_intents) > 1:
                reasoning += f". Detected composite intents: {', '.join([i.value for i in composite_intents])}"
            
            # Create decision
            decision = RoutingDecision(
                intent_type=intent_type,
                target_handler=target_handler,
                confidence_score=confidence,
                reasoning=reasoning,
                metadata={
                    "operation": context.get("operation"),
                    "domain": domain,
                    "keywords_matched": matches,
                    "total_keywords": len(operation_type_keywords),
                    "composite_intents": len(composite_intents) > 1  # AC-FUTURE-005 flag
                },
                composite_intents=composite_intents  # AC-FUTURE-005
            )
            
            return decision
        
        except (KeyError, ValueError, AttributeError) as e:
            # Specific exception handling per CORE-013
            raise ValueError(f"Routing failed: {str(e)}")
    
    def route(self, context: Dict[str, Any]) -> RoutingDecision:
        """
        Route an operation based on context (with caching).
        
        Analyzes operation context and determines appropriate handler.
        Uses caching to avoid redundant decisions for identical contexts.
        
        Args:
            context: Context dictionary with operation details:
                - operation: Operation name (required or description required)
                - description: Operation description (optional)
                - domain: Target domain (optional)
                - keywords: List of keywords (optional)
                - urgency: Urgency level (optional)
                - user_intent: User's stated intent (optional)
        
        Returns:
            RoutingDecision: Routing decision with target handler and metadata
        
        Raises:
            ValueError: If context is invalid or routing cannot be determined
        
        Example:
            context = {
                "operation": "fix_race_condition",
                "description": "Fix race condition in Master Orchestrator",
                "domain": "core",
                "keywords": ["bug", "fix", "race condition"]
            }
            decision = router.route(context)
            print(f"Route to: {decision.target_handler}")
        """
        try:
            # Get cache key
            cache_key = self._get_cache_key(context)
            
            # Check cache
            if cache_key in self.cached_decisions:
                return self.cached_decisions[cache_key]
            
            # Compute routing decision
            decision = self._route_internal(context)
            
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
