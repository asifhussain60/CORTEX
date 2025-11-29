"""
IntentRouter Agent

Routes user requests to appropriate specialist agents based on intent analysis.
Uses Tier 2 Knowledge Graph to find similar past intents and improve routing decisions.

The IntentRouter is the entry point for all user requests - it analyzes the intent,
checks for patterns in past requests, and routes to the most appropriate specialist agent.
"""

from typing import List, Dict, Any, Optional, Tuple
from .base_agent import BaseAgent, AgentRequest, AgentResponse
from .agent_types import (
    AgentType,
    IntentType,
    IntentClassificationResult,
    get_agent_for_intent,
    INTENT_AGENT_MAP
)
from .utils import (
    extract_code_intent,
    parse_priority_keywords,
    normalize_intent
)
from .investigation_router import InvestigationRouter


class IntentRouter(BaseAgent):
    """
    Routes user requests to appropriate specialist agents.
    
    The IntentRouter analyzes user messages to determine intent, queries
    Tier 2 for similar past requests, and makes routing decisions to
    send requests to the most appropriate specialist agent(s).
    
    Features:
    - Multi-keyword intent classification
    - Pattern-based routing using Tier 2
    - Support for multi-agent routing
    - Fallback handling for unknown intents
    - Confidence scoring for routing decisions
    
    Example:
        router = IntentRouter(name="Router", tier1_api, tier2_kg, tier3_context)
        
        request = AgentRequest(
            intent="unknown",  # Will be classified
            context={},
            user_message="Create a new authentication module with tests"
        )
        
        response = router.execute(request)
        # Returns: {
        #   "primary_agent": AgentType.EXECUTOR,
        #   "secondary_agents": [AgentType.TESTER],
        #   "confidence": 0.85
        # }
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None, config=None):
        """Initialize IntentRouter with tier APIs."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        self.routing_history = []  # Track routing decisions for learning
        self.agents = {}  # Registry of available agents for routing
        self.config = config or {}
        self._initialize_agent_registry()
        
        # Initialize Vision orchestrator for automatic image detection
        try:
            from src.tier1.vision_orchestrator import VisionOrchestrator
            self.vision_orchestrator = VisionOrchestrator(self.config)
            self.logger.info("Vision orchestrator initialized - automatic image detection enabled")
        except Exception as e:
            self.logger.warning(f"Could not initialize vision orchestrator: {e}")
            self.vision_orchestrator = None
        
        # Intent classification keywords
        self.INTENT_KEYWORDS = {
            IntentType.PLAN: [
                # Core planning triggers
                "plan", "planning", "feature", "breakdown", "design", "architect",
                # Direct requests
                "plan a feature", "plan this", "plan this feature", "lets plan",
                "let's plan", "help me plan", "need help planning", "can you help me plan",
                "i want to plan", "i need to plan", "start planning", "begin planning",
                "create a plan", "make a plan", "build a plan",
                # Collaborative
                "plan together", "lets plan together", "let's plan together",
                "work with me to plan", "collaborate on planning",
                "help me break this down", "break this down for me", "break this down",
                "help me structure this",
                # Question forms
                "how do i plan", "how should i plan", "how to plan this",
                "what's the best way to plan", "whats the best way to plan",
                "help planning this", "help planning this out",
                # Implicit planning
                "i need a roadmap", "create a roadmap", "build a roadmap", "roadmap",
                "help me organize this work", "how should i approach this",
                "what's the best approach", "whats the best approach",
                "how do i tackle this"
            ],
            IntentType.ARCHITECTURE: [
                # Core architectural analysis triggers (NEW for CORTEX-BRAIN-001 fix)
                "architecture", "architectural", "analyze", "analysis", "crawl", "understand",
                "routing", "navigation", "structure", "layout", "components", "shell",
                "view", "injection", "feature", "directory", "organization", "system",
                "design", "pattern", "flow", "mapping",
                # Direct architecture requests
                "analyze architecture", "understand architecture", "crawl system",
                "analyze structure", "understand structure", "map structure",
                "analyze routing", "understand routing", "map routing",
                "crawl shell", "analyze shell", "understand shell",
                # Investigation patterns  
                "how does this work", "how does", "what is the structure",
                "show me the structure", "explain the architecture",
                "document the architecture", "map the system"
            ],
            IntentType.CODE: ["create", "implement", "build", "add", "make"],
            IntentType.EDIT_FILE: ["edit", "modify", "update", "change", "refactor"],
            IntentType.TEST: ["test", "tdd", "verify"],  # Removed "testing" to avoid conflict with "plan testing"
            IntentType.RUN_TESTS: ["run test", "execute test", "test run"],
            IntentType.FIX: ["fix", "bug", "error", "issue", "problem"],
            IntentType.DEBUG: ["debug", "investigate", "trace", "diagnose"],
            IntentType.HEALTH_CHECK: ["health", "status", "check", "validate"],
            IntentType.RESUME: ["resume", "continue", "restore", "recover"],
            IntentType.SCREENSHOT: ["screenshot", "ui", "screen", "visual"],
            IntentType.COMMIT: ["commit", "git", "push", "save changes"],
            IntentType.COMPLIANCE: ["rule", "governance", "compliance", "policy"],
            # ADO (Azure DevOps) operations (NEW - ADO Integration)
            IntentType.ADO_STORY: [
                "plan ado story", "create ado story", "new ado story", "plan user story",
                "create user story", "new user story", "ado story", "user story"
            ],
            IntentType.ADO_FEATURE: [
                "plan ado feature", "create ado feature", "new ado feature", "plan feature",
                "ado feature"
            ],
            IntentType.ADO_SUMMARY: [
                "generate ado summary", "create work summary", "ado work summary",
                "complete ado work", "ado summary", "work summary"
            ],
            IntentType.CODE_REVIEW: [
                "code review", "review code", "pr review", "review pr", "pull request review",
                "review pull request"
            ],
            # Profile management (NEW - User Profile System 3.2.1)
            IntentType.UPDATE_PROFILE: [
                "update profile", "change profile", "modify profile", "edit profile",
                "update preferences", "change preferences", "modify preferences",
                "update my profile", "change my profile", "update settings",
                "change settings", "profile settings", "update tech stack",
                "change tech stack", "update experience", "change experience",
                "update mode", "change mode", "update interaction", "change interaction",
                # Tech stack specific keywords (Phase 1: User Profile System)
                "switch to azure", "switch to aws", "switch to gcp", "use azure stack",
                "use aws stack", "use gcp stack", "prefer azure", "prefer aws", "prefer gcp",
                "no tech preference", "custom tech stack", "configure stack", "set stack"
            ],
            # Timeframe estimation (NEW - SWAGGER Integration + 3.2.1 Scope Approval Gate)
            IntentType.ESTIMATE: [
                "estimate timeframe", "time estimate", "how long will this take",
                "timeframe", "story points", "sprint estimate", "parallel tracks",
                "timeline comparison", "delivery timeline", "effort estimate",
                "estimate effort", "project timeline", "estimate this", "estimate",
                "how many sprints", "team size estimate", "cost projection",
                "what-if scenarios", "estimate hours", "estimate days"
            ],
            IntentType.TIMEFRAME: [
                "timeframe for", "timeframe estimate", "delivery timeframe",
                "timeframe analysis", "track timeframe"
            ],
            IntentType.STORY_POINTS: [
                "story points for", "calculate story points", "how many points",
                "point estimate", "fibonacci points"
            ],
            IntentType.APPROVE_SCOPE: [
                "approve scope", "confirm scope", "scope approved", "scope looks good",
                "approve estimation scope", "scope is correct", "yes approve",
                "accept scope", "scope confirmation", "validate scope"
            ],
        }
        
        # Intent-based rule context mapping (CORTEX 3.0 - Phase 1)
        # Maps intents to applicable governance rules and behavioral flags
        self.INTENT_RULE_CONTEXT = {
            IntentType.CODE: {
                'rules_to_consider': ['TDD_ENFORCEMENT', 'DEFINITION_OF_DONE'],
                'intelligent_test_determination': True,
                'skip_summary_generation': True,
                'requires_dod_validation': True
            },
            IntentType.IMPLEMENT: {
                'rules_to_consider': ['TDD_ENFORCEMENT', 'DEFINITION_OF_DONE', 'DEFINITION_OF_READY'],
                'intelligent_test_determination': True,
                'skip_summary_generation': True,
                'requires_dor_validation': True,
                'requires_dod_validation': True
            },
            IntentType.ARCHITECTURE: {
                'rules_to_consider': ['CRAWLER_ACTIVATION', 'PATTERN_ANALYSIS'],
                'enable_crawlers': True,
                'skip_summary_generation': False,  # Investigations often need summaries
                'requires_documentation': True
            },
            IntentType.ANALYZE_STRUCTURE: {
                'rules_to_consider': ['CRAWLER_ACTIVATION', 'PATTERN_ANALYSIS'],
                'enable_crawlers': True,
                'skip_summary_generation': False,
                'requires_documentation': True
            },
            IntentType.CRAWL_SYSTEM: {
                'rules_to_consider': ['CRAWLER_ACTIVATION', 'DEEP_ANALYSIS'],
                'enable_crawlers': True,
                'enable_deep_crawl': True,
                'skip_summary_generation': False,
                'requires_documentation': True
            },
            IntentType.FIX: {
                'rules_to_consider': ['DEFINITION_OF_DONE'],  # DoD but not always TDD
                'intelligent_test_determination': True,
                'skip_summary_generation': True,
                'requires_dod_validation': True
            },
            IntentType.DEBUG: {
                'rules_to_consider': ['ROOT_CAUSE_ANALYSIS'],
                'enable_investigation_mode': True,
                'skip_summary_generation': False,  # Debug sessions need summaries
                'requires_documentation': True
            },
            IntentType.PLAN: {
                'rules_to_consider': ['INCREMENTAL_PLAN_GENERATION', 'DEFINITION_OF_READY'],
                'skip_summary_generation': False,  # Plans ARE the deliverable
                'requires_dor_validation': True,
                'create_persistent_artifact': True
            },
            IntentType.FEATURE: {
                'rules_to_consider': ['DEFINITION_OF_READY', 'TDD_ENFORCEMENT', 'DEFINITION_OF_DONE'],
                'intelligent_test_determination': True,
                'skip_summary_generation': True,
                'requires_dor_validation': True,
                'requires_dod_validation': True,
                'requires_planning': True
            },
            IntentType.TEST: {
                'rules_to_consider': ['TDD_ENFORCEMENT', 'TEST_COVERAGE'],
                'skip_summary_generation': True,
                'requires_dod_validation': True
            },
            IntentType.REFACTOR: {
                'rules_to_consider': ['DEFINITION_OF_DONE', 'SOLID_PRINCIPLES'],
                'intelligent_test_determination': True,  # Tests must stay green
                'skip_summary_generation': True,
                'requires_dod_validation': True
            },
            IntentType.EDIT_FILE: {
                'rules_to_consider': ['DEFINITION_OF_DONE'],
                'intelligent_test_determination': True,
                'skip_summary_generation': True,
                'requires_dod_validation': True
            },
            IntentType.HEALTH_CHECK: {
                'rules_to_consider': ['VALIDATION_RULES'],
                'skip_summary_generation': False,  # Health reports are valuable
                'requires_documentation': False
            },
            IntentType.COMMIT: {
                'rules_to_consider': ['DEFINITION_OF_DONE', 'COMMIT_MESSAGE_STANDARDS'],
                'skip_summary_generation': True,
                'requires_dod_validation': True
            },
            IntentType.COMPLIANCE: {
                'rules_to_consider': ['ALL_GOVERNANCE_RULES'],
                'skip_summary_generation': False,
                'requires_documentation': True
            },
            IntentType.SCREENSHOT: {
                'rules_to_consider': ['VISION_ANALYSIS', 'UI_STANDARDS'],
                'enable_vision_api': True,
                'skip_summary_generation': False,
                'requires_documentation': False
            },
            # ADO operations rule context (NEW - ADO Integration)
            IntentType.ADO_STORY: {
                'rules_to_consider': ['DEFINITION_OF_READY', 'ACCEPTANCE_CRITERIA'],
                'skip_summary_generation': False,  # Stories need summaries
                'requires_documentation': True,
                'create_persistent_artifact': True
            },
            IntentType.ADO_FEATURE: {
                'rules_to_consider': ['DEFINITION_OF_READY', 'ACCEPTANCE_CRITERIA'],
                'skip_summary_generation': False,  # Features need summaries
                'requires_documentation': True,
                'create_persistent_artifact': True
            },
            IntentType.ADO_SUMMARY: {
                'rules_to_consider': ['DEFINITION_OF_DONE'],
                'skip_summary_generation': False,  # Summary generation is the point
                'requires_documentation': True,
                'requires_dod_validation': True
            },
            IntentType.CODE_REVIEW: {
                'rules_to_consider': ['CODE_QUALITY', 'SECURITY', 'DEFINITION_OF_DONE'],
                'skip_summary_generation': False,  # Reviews need detailed reports
                'requires_documentation': True
            },
            # User profile management (NEW - User Profile System 3.2.1)
            IntentType.UPDATE_PROFILE: {
                'rules_to_consider': [],  # No governance rules - user preference only
                'skip_summary_generation': True,  # Interactive flow, no summary needed
                'requires_documentation': False
            },
            # Timeframe estimation (NEW - SWAGGER Integration + 3.2.1 Scope Approval Gate)
            IntentType.ESTIMATE: {
                'rules_to_consider': ['DEFINITION_OF_READY', 'DOR_ENFORCEMENT', 'SCOPE_APPROVAL_REQUIRED'],
                'requires_dor_validation': True,  # SWAGGER requires DoR before estimation
                'requires_scope_approval': True,  # NEW 3.2.1: Block estimates without approved scope
                'skip_summary_generation': False,  # Estimates need detailed reports
                'requires_documentation': True,
                'create_persistent_artifact': True,  # Save estimation reports
                'enable_parallel_analysis': True,  # Enable parallel track analysis
                'planner_handoff_on_low_confidence': True  # NEW 3.2.1: Auto-handoff to planner
            },
            IntentType.TIMEFRAME: {
                'rules_to_consider': ['DEFINITION_OF_READY', 'DOR_ENFORCEMENT', 'SCOPE_APPROVAL_REQUIRED'],
                'requires_dor_validation': True,
                'requires_scope_approval': True,  # NEW 3.2.1: Block estimates without approved scope
                'skip_summary_generation': False,
                'requires_documentation': True,
                'create_persistent_artifact': True,
                'enable_parallel_analysis': True,
                'planner_handoff_on_low_confidence': True  # NEW 3.2.1: Auto-handoff to planner
            },
            IntentType.STORY_POINTS: {
                'rules_to_consider': ['DEFINITION_OF_READY', 'DOR_ENFORCEMENT', 'SCOPE_APPROVAL_REQUIRED'],
                'requires_dor_validation': True,
                'requires_scope_approval': True,  # NEW 3.2.1: Block estimates without approved scope
                'skip_summary_generation': False,
                'requires_documentation': True,
                'create_persistent_artifact': True,
                'planner_handoff_on_low_confidence': True  # NEW 3.2.1: Auto-handoff to planner
            },
            IntentType.APPROVE_SCOPE: {
                'rules_to_consider': [],  # No governance rules - user approval action
                'skip_summary_generation': True,  # Direct action, no summary needed
                'requires_documentation': False,  # No documentation artifact needed
                'approval_action': True  # Flag this as approval workflow
            }
        }

    def _initialize_agent_registry(self):
        """Initialize agent registry with available agent types."""
        # Register all available agent types from the mapping
        from .agent_types import INTENT_AGENT_MAP
        
        # Extract unique agent types from intent mapping
        for intent_type, agent_type in INTENT_AGENT_MAP.items():
            if agent_type not in self.agents:
                self.agents[agent_type] = {
                    'type': agent_type,
                    'intents': []
                }
            self.agents[agent_type]['intents'].append(intent_type)
        
        # Initialize investigation router for deep dive analysis
        from src.cortex_agents.health_validator.agent import HealthValidator
        try:
            health_validator = HealthValidator("health-validator", self.tier1, self.tier2, self.tier3)
            self.investigation_router = InvestigationRouter(self, health_validator, self.tier2)
        except Exception as e:
            self.logger.warning(f"Could not initialize investigation router: {e}")
            self.investigation_router = None
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        IntentRouter can handle all requests (it's the entry point).
        
        Args:
            request: The agent request
        
        Returns:
            Always True (router handles everything)
        """
        return True
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Route the request to appropriate specialist agent(s).
        
        Args:
            request: The agent request to route
        
        Returns:
            AgentResponse with routing decision and metadata
        """
        self.log_request(request)
        start_time = self.logger.info("Starting intent routing")
        
        try:
            # Step -1: Load user profile and inject into request (CORTEX 3.2.1)
            if self.tier1 and not request.user_profile:
                try:
                    profile = self.tier1.get_profile()
                    if profile:
                        request.user_profile = profile
                        self.logger.info(f"Loaded user profile: {profile['interaction_mode']}/{profile['experience_level']}")
                    else:
                        # No profile exists - trigger onboarding
                        self.logger.info("No user profile found - onboarding required")
                        return self._trigger_onboarding(request)
                except Exception as e:
                    self.logger.warning(f"Failed to load user profile: {e}")
            
            # Step -0.5: Check for profile update request (CORTEX 3.2.1)
            if self._is_profile_update_request(request.user_message):
                return self._handle_profile_update(request)
            
            # Step 0: Check for images and analyze automatically (PRIORITY)
            if self.vision_orchestrator:
                vision_result = self._process_images(request)
                if vision_result['images_found']:
                    # Inject vision analysis into request context
                    if not request.context:
                        request.context = {}
                    request.context['vision_analysis'] = vision_result
                    
                    # Log image detection
                    self.logger.info(
                        f"Auto-detected {len(vision_result['detected_images'])} image(s), "
                        f"analyzed {vision_result['images_analyzed']}"
                    )
            
            # Check for investigation commands first
            if self._is_investigation_request(request.user_message):
                return self._handle_investigation_request(request)
            
            # Step 1: Classify intent with rule context (CORTEX 3.0 Phase 1)
            classification_result = self._classify_intent_with_rules(request)
            
            # Step 2: Query Tier 2 for similar past intents
            similar_patterns = self._find_similar_intents(request)
            
            # Step 2.5: Suggest relevant patterns before execution (NEW - Pattern Utilization)
            pattern_suggestions = self._suggest_patterns(request, classification_result.intent)
            if pattern_suggestions:
                # Store suggestions in request context for agent use
                if not request.context:
                    request.context = {}
                request.context['pattern_suggestions'] = pattern_suggestions
                self.logger.info(f"Injected {len(pattern_suggestions)} pattern suggestions into request context")
            
            # Step 3: Make routing decision with rule context
            routing_decision = self._make_routing_decision(
                classification_result.intent,  # Extract intent for backward compatibility
                similar_patterns,
                request,
                classification_result  # Pass full classification result
            )
            
            # Step 4: Log routing decision to Tier 1 if conversation exists
            if request.conversation_id and self.tier1:
                self._log_to_conversation(request, routing_decision)
            
            # Step 5: Store routing pattern in Tier 2
            if self.tier2:
                self._store_routing_pattern(request, routing_decision)
            
            # Build response
            response = AgentResponse(
                success=True,
                result=routing_decision,
                message=self._format_routing_message(routing_decision),
                agent_name=self.name,
                metadata={
                    "classified_intent": classification_result.intent.value,
                    "classification_confidence": classification_result.confidence,
                    "rule_context": classification_result.rule_context,
                    "similar_patterns_found": len(similar_patterns),
                    "routing_confidence": routing_decision["confidence"]
                },
                next_actions=[
                    f"Execute {routing_decision['primary_agent'].name} agent"
                ]
            )
            
            self.log_response(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Routing failed: {str(e)}")
            return AgentResponse(
                success=False,
                result=None,
                message=f"Routing failed: {str(e)}",
                agent_name=self.name
            )
    
    def _classify_intent(self, request: AgentRequest) -> IntentType:
        """
        Classify user intent from message text and context.
        
        DEPRECATED: Use _classify_intent_with_rules() for new code.
        This method maintained for backward compatibility.
        
        Args:
            request: The agent request
        
        Returns:
            Classified IntentType
        """
        result = self._classify_intent_with_rules(request)
        return result.intent
    
    def _classify_intent_with_rules(self, request: AgentRequest) -> IntentClassificationResult:
        """
        Classify user intent and attach relevant rule context.
        
        This is the enhanced classification method that returns rich context
        for intelligent rule enforcement. Replaces legacy _classify_intent().
        
        Args:
            request: The agent request
        
        Returns:
            IntentClassificationResult with intent, confidence, and rule context
        """
        message_lower = request.user_message.lower()
        metadata = {}
        
        # Check if there's an image attachment in context - this takes priority
        if request.context:
            # Check for image data in various formats
            has_image = (
                'image_base64' in request.context or
                'image_path' in request.context or
                'image_data' in request.context or
                'screenshot' in request.context or
                any(k.startswith('image') for k in request.context.keys())
            )
            if has_image:
                self.logger.info("Image detected in request context - routing to screenshot analysis")
                intent = IntentType.SCREENSHOT
                confidence = 1.0  # High confidence when image present
                metadata['detection_method'] = 'image_context'
                
                return IntentClassificationResult(
                    intent=intent,
                    confidence=confidence,
                    rule_context=self.INTENT_RULE_CONTEXT.get(intent, {}),
                    metadata=metadata
                )
        
        # If intent already classified and valid (not UNKNOWN), use it
        try:
            normalized = normalize_intent(request.intent)
            if normalized != "unknown":  # Don't return early for UNKNOWN - classify from message
                for intent_type in IntentType:
                    if intent_type.value == normalized:
                        confidence = 0.9  # High confidence from pre-classified intent
                        metadata['detection_method'] = 'pre_classified'
                        
                        return IntentClassificationResult(
                            intent=intent_type,
                            confidence=confidence,
                            rule_context=self.INTENT_RULE_CONTEXT.get(intent_type, {}),
                            metadata=metadata
                        )
        except:
            pass
        
        # Classify based on keywords
        intent_scores = {}
        for intent_type, keywords in self.INTENT_KEYWORDS.items():
            score = 0
            matched_keywords = []
            for keyword in keywords:
                if keyword in message_lower:
                    # Give higher weight to multi-word phrases
                    word_count = len(keyword.split())
                    score += word_count
                    matched_keywords.append(keyword)
            if score > 0:
                intent_scores[intent_type] = {
                    'score': score,
                    'matched_keywords': matched_keywords
                }
        
        # Return highest scoring intent, or UNKNOWN if none found
        if intent_scores:
            best_match = max(intent_scores.items(), key=lambda x: x[1]['score'])
            intent = best_match[0]
            score_data = best_match[1]
            
            # Calculate confidence based on score strength
            max_possible_score = len(message_lower.split())  # Rough estimate
            confidence = min(score_data['score'] / max_possible_score, 1.0)
            confidence = max(confidence, 0.6)  # Minimum confidence for keyword match
            
            metadata['detection_method'] = 'keyword_matching'
            metadata['matched_keywords'] = score_data['matched_keywords']
            metadata['score'] = score_data['score']
            
            return IntentClassificationResult(
                intent=intent,
                confidence=confidence,
                rule_context=self.INTENT_RULE_CONTEXT.get(intent, {}),
                metadata=metadata
            )
        
        # No match found - return UNKNOWN with empty rule context
        intent = IntentType.UNKNOWN
        confidence = 0.0
        metadata['detection_method'] = 'default'
        
        return IntentClassificationResult(
            intent=intent,
            confidence=confidence,
            rule_context={},  # No rules for unknown intent
            metadata=metadata
        )
        return IntentType.UNKNOWN
    
    def _find_similar_intents(
        self,
        request: AgentRequest,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Find similar past intents from Tier 2.
        
        Args:
            request: The agent request
            limit: Maximum number of similar patterns to return
        
        Returns:
            List of similar patterns from Tier 2
        """
        if not self.tier2:
            return []
        
        try:
            # Search Tier 2 for similar requests
            results = self.tier2.search(request.user_message, limit=limit)
            return results if results else []
        except Exception as e:
            self.logger.warning(f"Tier 2 search failed: {str(e)}")
            return []
    
    def _make_routing_decision(
        self,
        intent: IntentType,
        similar_patterns: List[Dict[str, Any]],
        request: AgentRequest,
        classification_result: Optional[IntentClassificationResult] = None
    ) -> Dict[str, Any]:
        """
        Make routing decision based on intent and patterns.
        
        Args:
            intent: Classified intent
            similar_patterns: Similar patterns from Tier 2
            request: Original request
            classification_result: Rich classification result with rule context (CORTEX 3.0)
        
        Returns:
            Routing decision with primary agent, secondary agents, confidence, and rule context
        """
        # Get primary agent for intent
        primary_agent = get_agent_for_intent(intent)
        
        # Determine secondary agents based on message analysis
        secondary_agents = self._identify_secondary_agents(request, intent)
        
        # Calculate confidence based on intent clarity and pattern matches
        confidence = self._calculate_confidence(
            intent,
            similar_patterns,
            request
        )
        
        # If confidence is low and patterns exist, use pattern-based routing
        if confidence < 0.6 and similar_patterns:
            primary_agent = self._infer_agent_from_patterns(similar_patterns)
            confidence = 0.7  # Pattern-based routing gets moderate confidence
        
        # Build routing decision
        decision = {
            "primary_agent": primary_agent,
            "secondary_agents": secondary_agents,
            "confidence": confidence,
            "intent": intent,
            "routing_reason": self._get_routing_reason(
                intent,
                similar_patterns,
                confidence
            )
        }
        
        # Attach rule context if available (CORTEX 3.0 Phase 1)
        if classification_result:
            decision["rule_context"] = classification_result.rule_context
            decision["classification_metadata"] = classification_result.metadata
            decision["classification_confidence"] = classification_result.confidence
        
        return decision
    
    def _identify_secondary_agents(
        self,
        request: AgentRequest,
        primary_intent: IntentType
    ) -> List[AgentType]:
        """
        Identify secondary agents that should also handle this request.
        
        For example, "Create a module with tests" needs both EXECUTOR and TESTER.
        
        Args:
            request: The agent request
            primary_intent: Primary classified intent
        
        Returns:
            List of secondary agent types
        """
        secondary = []
        message_lower = request.user_message.lower()
        
        # Check for test-related keywords
        if primary_intent != IntentType.TEST:
            if any(word in message_lower for word in ["test", "testing", "tdd"]):
                secondary.append(AgentType.TESTER)
        
        # Check for validation keywords
        if "validate" in message_lower or "check" in message_lower:
            if primary_intent not in [IntentType.HEALTH_CHECK, IntentType.VALIDATE]:
                secondary.append(AgentType.VALIDATOR)
        
        # Check for git/commit keywords
        if primary_intent != IntentType.COMMIT:
            if "commit" in message_lower or "git" in message_lower:
                secondary.append(AgentType.COMMITTER)
        
        return secondary
    
    def _calculate_confidence(
        self,
        intent: IntentType,
        similar_patterns: List[Dict[str, Any]],
        request: AgentRequest
    ) -> float:
        """
        Calculate confidence score for routing decision.
        
        Args:
            intent: Classified intent
            similar_patterns: Similar patterns found
            request: Original request
        
        Returns:
            Confidence score (0.0 to 1.0)
        """
        confidence = 0.5  # Base confidence
        
        # Boost if intent is not UNKNOWN
        if intent != IntentType.UNKNOWN:
            confidence += 0.3
        
        # Boost if similar patterns found
        if similar_patterns:
            pattern_boost = min(len(similar_patterns) * 0.05, 0.2)
            confidence += pattern_boost
        
        # Boost if request has clear context
        if request.context and len(request.context) > 0:
            confidence += 0.1
        
        # Cap at 1.0
        return min(confidence, 1.0)
    
    def _infer_agent_from_patterns(
        self,
        patterns: List[Dict[str, Any]]
    ) -> AgentType:
        """
        Infer best agent from similar patterns.
        
        Args:
            patterns: Similar patterns from Tier 2
        
        Returns:
            Inferred agent type
        """
        # Use most common agent from patterns
        # For now, return PLANNER as safe default
        return AgentType.PLANNER
    
    def _get_routing_reason(
        self,
        intent: IntentType,
        similar_patterns: List[Dict[str, Any]],
        confidence: float
    ) -> str:
        """
        Get human-readable routing reason.
        
        Args:
            intent: Classified intent
            similar_patterns: Similar patterns
            confidence: Confidence score
        
        Returns:
            Routing reason string
        """
        if intent == IntentType.UNKNOWN:
            return "Intent unclear, using pattern matching"
        
        if similar_patterns:
            return f"Intent '{intent.value}' matched, {len(similar_patterns)} similar patterns found"
        
        return f"Intent '{intent.value}' classified with {confidence:.0%} confidence"
    
    def _log_to_conversation(
        self,
        request: AgentRequest,
        routing_decision: Dict[str, Any]
    ):
        """Log routing decision to Tier 1 conversation"""
        if not self.tier1:
            return
        
        try:
            message = (
                f"Routing: {routing_decision['intent'].value} → "
                f"{routing_decision['primary_agent'].name} "
                f"(confidence: {routing_decision['confidence']:.0%})"
            )
            self.tier1.process_message(
                request.conversation_id,
                "system",
                message
            )
        except Exception as e:
            self.logger.warning(f"Failed to log to conversation: {str(e)}")
    
    def _store_routing_pattern(
        self,
        request: AgentRequest,
        routing_decision: Dict[str, Any]
    ):
        """Store successful routing pattern in Tier 2"""
        if not self.tier2:
            return
        
        try:
            self.tier2.add_pattern(
                pattern_type="routing",
                title=f"Route: {routing_decision['intent'].value}",
                content=f"Message: {request.user_message[:100]}, "
                        f"Agent: {routing_decision['primary_agent'].name}"
            )
        except Exception as e:
            self.logger.warning(f"Failed to store routing pattern: {str(e)}")
    
    def _format_routing_message(self, routing_decision: Dict[str, Any]) -> str:
        """Format routing decision as human-readable message"""
        primary = routing_decision['primary_agent'].name
        confidence = routing_decision['confidence']
        
        msg = f"Routing to {primary} (confidence: {confidence:.0%})"
        
        if routing_decision.get('secondary_agents'):
            secondary = [a.name for a in routing_decision['secondary_agents']]
            msg += f", also involving: {', '.join(secondary)}"
        
        return msg
    
    def _is_investigation_request(self, message: str) -> bool:
        """Check if message is an investigation request requiring deep analysis"""
        investigation_patterns = [
            r'investigate\s+(?:why\s+)?(?:this\s+)?(?:the\s+)?',
            r'analyze\s+(?:why\s+)?(?:this\s+)?(?:the\s+)?',
            r'find\s+out\s+why',
            r'look\s+into\s+(?:why\s+)?(?:this\s+)?(?:the\s+)?',
            r'debug\s+(?:why\s+)?(?:this\s+)?(?:the\s+)?',
            r'trace\s+(?:why\s+)?(?:this\s+)?(?:the\s+)?'
        ]
        
        message_lower = message.lower()
        import re
        
        for pattern in investigation_patterns:
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def _handle_investigation_request(self, request: AgentRequest) -> AgentResponse:
        """Handle investigation requests using InvestigationRouter"""
        if not self.investigation_router:
            # Fallback to regular routing if investigation router not available
            self.logger.warning("Investigation router not available, falling back to regular routing")
            return self._handle_regular_routing(request)
        
        try:
            # Extract context from request
            context = {
                'current_file': request.metadata.get('current_file'),
                'workspace_root': request.metadata.get('workspace_root', '/Users/asifhussain/PROJECTS/CORTEX'),
                'conversation_id': request.conversation_id
            }
            
            # Use asyncio to handle the async investigation
            import asyncio
            investigation_result = asyncio.run(
                self.investigation_router.handle_investigation(request.user_message, context)
            )
            
            return AgentResponse(
                success=investigation_result.get('success', True),
                result=investigation_result,
                message=self._format_investigation_response(investigation_result),
                agent_name=self.name,
                metadata={
                    "intent_type": "INVESTIGATE",
                    "investigation_phase": investigation_result.get('phase', 'unknown'),
                    "findings_count": investigation_result.get('total_findings', 0)
                },
                context=request.context
            )
            
        except Exception as e:
            self.logger.error(f"Investigation routing failed: {e}")
            # Fallback to regular routing
            return self._handle_regular_routing(request)
    
    def _process_images(self, request: AgentRequest) -> Dict:
        """
        Process images in request with Vision API.
        
        Args:
            request: The agent request to check for images
            
        Returns:
            Vision processing result dictionary
        """
        try:
            # Extract attachments from context if available
            attachments = None
            if request.context:
                attachments = request.context.get('attachments')
            
            # Determine context type for specialized prompts
            context_type = 'generic'
            message_lower = request.user_message.lower()
            
            if 'plan' in message_lower or 'feature' in message_lower:
                context_type = 'planning'
            elif 'error' in message_lower or 'bug' in message_lower or 'debug' in message_lower:
                context_type = 'debugging'
            elif 'ado' in message_lower or 'work item' in message_lower:
                context_type = 'ado'
            
            # Process request with Vision orchestrator
            result = self.vision_orchestrator.process_request(
                user_request=request.user_message,
                attachments=attachments,
                context_type=context_type
            )
            
            return result
            
        except Exception as e:
            self.logger.error(f"Image processing error: {e}", exc_info=True)
            return {
                'images_found': False,
                'images_analyzed': 0,
                'images_failed': 0,
                'errors': [str(e)]
            }
    
    def _handle_regular_routing(self, request: AgentRequest) -> AgentResponse:
        """Handle regular (non-investigation) routing"""
        # Original routing logic
        classified_intent = self._classify_intent(request)
        similar_patterns = self._find_similar_intents(request)
        routing_decision = self._make_routing_decision(classified_intent, similar_patterns, request)
        
        if request.conversation_id and self.tier1:
            self._log_to_conversation(request, routing_decision)
        
        if self.tier2:
            self._store_routing_pattern(request, routing_decision)
        
        return AgentResponse(
            success=True,
            result=routing_decision,
            message=self._format_routing_message(routing_decision),
            agent_name=self.name,
            metadata={
                "classified_intent": classified_intent.value,
                "similar_patterns_found": len(similar_patterns),
                "confidence": routing_decision["confidence"]
            },
            context=request.context
        )
    
    def _format_investigation_response(self, investigation_result: Dict[str, Any]) -> str:
        """Format investigation result as human-readable message"""
        if not investigation_result.get('success', True):
            return f"Investigation failed: {investigation_result.get('error', 'Unknown error')}"
        
        phase = investigation_result.get('phase', 'unknown')
        target = investigation_result.get('target_entity', 'unknown entity')
        
        if phase == 'discovery':
            relationships = investigation_result.get('relationships_found', 0)
            return f"Discovery phase complete for {target}. Found {relationships} relationships. Ready for deep analysis."
        
        elif phase == 'analysis':
            findings = investigation_result.get('findings_count', 0)
            return f"Analysis phase complete for {target}. Generated {findings} findings. Ready for synthesis."
        
        elif phase == 'complete':
            total_findings = investigation_result.get('total_findings', 0)
            summary = investigation_result.get('investigation_summary', 'Investigation completed.')
            return f"Investigation complete: {summary} Total findings: {total_findings}."
        
        else:
            return f"Investigation in progress for {target} (phase: {phase})"
    
    def _suggest_patterns(
        self,
        request: AgentRequest,
        intent_type: IntentType
    ) -> List[Dict[str, Any]]:
        """
        Suggest relevant patterns before agent execution.
        
        Integrates PatternSuggestionEngine to increase pattern utilization.
        This is part of Task 2.1: Increase Pattern Utilization (CORTEX Fix Plan).
        
        Args:
            request: The agent request
            intent_type: Classified intent type
        
        Returns:
            List of pattern suggestions (top 3)
        """
        try:
            # Import pattern suggestion engine
            from src.tier2.pattern_suggestion_engine import PatternSuggestionEngine
            
            # Initialize engine (cached instance could be stored in self for performance)
            if not hasattr(self, '_pattern_engine'):
                self._pattern_engine = PatternSuggestionEngine()
            
            # Get current namespace from context (if available)
            current_namespace = None
            if request.context and 'workspace_name' in request.context:
                current_namespace = f"workspace.{request.context['workspace_name']}"
            elif request.context and 'namespace' in request.context:
                current_namespace = request.context['namespace']
            
            # Suggest patterns
            suggestions = self._pattern_engine.suggest_patterns(
                task_description=request.user_message,
                intent_type=intent_type.value if intent_type else None,
                current_namespace=current_namespace,
                limit=3
            )
            
            if suggestions:
                self.logger.info(
                    f"Pattern suggestion engine returned {len(suggestions)} patterns "
                    f"(top relevance: {suggestions[0]['relevance_score']:.2f})"
                )
            else:
                self.logger.debug("No relevant patterns found for this request")
            
            return suggestions
        
        except Exception as e:
            self.logger.warning(f"Pattern suggestion failed: {e}")
            return []
    
    def _trigger_onboarding(self, request: AgentRequest) -> AgentResponse:
        """
        Trigger onboarding flow for first-time users (CORTEX 3.2.1).
        
        Args:
            request: The agent request
        
        Returns:
            AgentResponse indicating onboarding is required
        """
        return AgentResponse(
            success=True,
            result={"action": "onboarding_required"},
            message="User profile not found. Onboarding orchestrator will be triggered.",
            agent_name=self.name,
            metadata={
                "requires_onboarding": True,
                "original_message": request.user_message
            }
        )
    
    def _is_profile_update_request(self, message: str) -> bool:
        """
        Check if message is a profile update request (CORTEX 3.2.1).
        
        Args:
            message: User message
        
        Returns:
            True if message contains profile update keywords
        """
        message_lower = message.lower()
        
        # Check for explicit profile update keywords
        update_keywords = self.INTENT_KEYWORDS.get(IntentType.UPDATE_PROFILE, [])
        return any(keyword in message_lower for keyword in update_keywords)
    
    def _handle_profile_update(self, request: AgentRequest) -> AgentResponse:
        """
        Handle profile update request by routing to onboarding orchestrator (CORTEX 3.2.1).
        
        Args:
            request: The agent request
        
        Returns:
            AgentResponse indicating profile update is being handled
        """
        return AgentResponse(
            success=True,
            result={"action": "profile_update", "intent": IntentType.UPDATE_PROFILE.value},
            message="Profile update requested. Onboarding orchestrator will handle the update flow.",
            agent_name=self.name,
            metadata={
                "requires_profile_update": True,
                "current_profile": request.user_profile,
                "original_message": request.user_message
            },
            next_actions=[
                "Show profile update options",
                "Allow user to select what to update (experience/mode/tech_stack)",
                "Process updates and confirm"
            ]
        )
