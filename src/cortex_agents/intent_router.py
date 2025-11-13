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
    get_agent_for_intent,
    INTENT_AGENT_MAP
)
from .utils import (
    extract_code_intent,
    parse_priority_keywords,
    normalize_intent
)


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
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize IntentRouter with tier APIs."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        self.routing_history = []  # Track routing decisions for learning
        self.agents = {}  # Registry of available agents for routing
        
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
        }

    
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
            # Step 1: Classify intent if not already classified
            classified_intent = self._classify_intent(request)
            
            # Step 2: Query Tier 2 for similar past intents
            similar_patterns = self._find_similar_intents(request)
            
            # Step 3: Make routing decision
            routing_decision = self._make_routing_decision(
                classified_intent,
                similar_patterns,
                request
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
                    "classified_intent": classified_intent.value,
                    "similar_patterns_found": len(similar_patterns),
                    "confidence": routing_decision["confidence"]
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
        
        Args:
            request: The agent request
        
        Returns:
            Classified IntentType
        """
        message_lower = request.user_message.lower()
        
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
                return IntentType.SCREENSHOT
        
        # If intent already classified and valid (not UNKNOWN), use it
        try:
            normalized = normalize_intent(request.intent)
            if normalized != "unknown":  # Don't return early for UNKNOWN - classify from message
                for intent_type in IntentType:
                    if intent_type.value == normalized:
                        return intent_type
        except:
            pass
        
        # Classify based on keywords
        intent_scores = {}
        for intent_type, keywords in self.INTENT_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in message_lower:
                    # Give higher weight to multi-word phrases
                    word_count = len(keyword.split())
                    score += word_count
            if score > 0:
                intent_scores[intent_type] = score
        
        # Return highest scoring intent, or UNKNOWN if none found
        if intent_scores:
            return max(intent_scores.items(), key=lambda x: x[1])[0]
        
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
        request: AgentRequest
    ) -> Dict[str, Any]:
        """
        Make routing decision based on intent and patterns.
        
        Args:
            intent: Classified intent
            similar_patterns: Similar patterns from Tier 2
            request: Original request
        
        Returns:
            Routing decision with primary agent, secondary agents, and confidence
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
        
        return {
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
