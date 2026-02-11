"""
Intelligence Routing Wiring Integration.

Connects IntelligenceRoutingEngine to orchestrator wiring system.
Enables MCP-First access to routed prompts and agents.

AC_START: AC-INTELLIGENCE-WIRING-001
Authority: Phase 49 | MCP-FIRST | CORE-035 (Single Source)
"""

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml

from cortex.brain.core.intelligence_routing_engine import (
    IntelligenceRoutingEngine,
    IntentType,
    RoutingDecision,
)

logger = logging.getLogger(__name__)


class IntelligenceRoutingWiring:
    """
    Wires IntelligenceRoutingEngine into orchestrator system.

    Responsibilities:
    - Load wiring configuration
    - Initialize routing engine
    - Provide MCP gateway layer
    - Handle cascading routing
    """

    def __init__(self, wiring_config_path: Optional[Path] = None):
        """
        Initialize intelligence routing wiring.

        Args:
            wiring_config_path: Path to wiring.yaml (if None, uses default)
        """
        self.wiring_config = self._load_wiring_config(wiring_config_path)
        self.routing_engine = IntelligenceRoutingEngine()
        self._routing_cache: Dict[str, RoutingDecision] = {}

        logger.info("IntelligenceRoutingWiring initialized")

    @staticmethod
    def _load_wiring_config(config_path: Optional[Path]) -> Dict[str, Any]:
        """Load wiring configuration."""
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "wiring" / "specifications" / "wiring.yaml"

        try:
            if config_path.exists():
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)
                    logger.info(f"Loaded wiring config from {config_path}")
                    return config or {}
            else:
                logger.warning(f"Wiring config not found: {config_path}")
                return {}
        except Exception as e:
            logger.error(f"Error loading wiring config: {e}")
            return {}

    def route_to_resources(
        self,
        intent: str,
        request: str = "",
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route intent to prompts and agents.

        Args:
            intent: Intent string (e.g., "IMPLEMENT", "ANALYZE")
            request: User request text
            context: Optional context dict

        Returns:
            Dict with routing result including:
                - decision: RoutingDecision object
                - prompt_content: Primary prompt content or None
                - agent_content: Primary agent content or None
                - secondary_prompts: List of secondary prompt contents
                - secondary_agents: List of secondary agent contents
                - context_hints: Context loading hints
        """
        try:
            # Convert intent string to IntentType
            intent_type = self._parse_intent(intent)

            # Get routing decision
            decision = self.routing_engine.route(intent_type, request, context)

            # Load content
            prompt_content = self.routing_engine.get_prompt_content(
                decision.primary_prompt.path
            )
            agent_content = self.routing_engine.get_agent_content(
                decision.primary_agent.path
            )

            secondary_prompts = [
                self.routing_engine.get_prompt_content(p.path)
                for p in decision.secondary_prompts
                if self.routing_engine.get_prompt_content(p.path)
            ]

            secondary_agents = [
                self.routing_engine.get_agent_content(a.path)
                for a in decision.secondary_agents
                if self.routing_engine.get_agent_content(a.path)
            ]

            result = {
                "success": True,
                "decision": decision,
                "prompt_content": prompt_content,
                "agent_content": agent_content,
                "secondary_prompts": secondary_prompts,
                "secondary_agents": secondary_agents,
                "context_hints": decision.context_hints,
                "confidence": decision.confidence_score,
                "requires_unified_intelligence": decision.requires_unified_intelligence,
            }

            logger.info(
                f"Routed {intent} to {decision.primary_prompt.name} + "
                f"{decision.primary_agent.name}"
            )

            return result

        except Exception as e:
            logger.error(f"Error routing intent {intent}: {e}")
            return {
                "success": False,
                "error": str(e),
                "decision": None,
                "prompt_content": None,
                "agent_content": None,
            }

    @staticmethod
    def _parse_intent(intent_str: str) -> IntentType:
        """
        Parse intent string to IntentType.

        Args:
            intent_str: Intent string (e.g., "IMPLEMENT", "implement")

        Returns:
            IntentType or raises ValueError
        """
        intent_upper = intent_str.upper().strip()

        try:
            return IntentType[intent_upper]
        except KeyError:
            # Try partial match
            for intent_type in IntentType:
                if intent_type.value.startswith(intent_upper):
                    return intent_type

            raise ValueError(f"Unknown intent: {intent_str}")

    def get_intent_handler_orchestrator(self, intent: str) -> Optional[str]:
        """
        Get primary orchestrator for intent.

        Args:
            intent: Intent string

        Returns:
            Orchestrator name or None
        """
        try:
            intent_type = self._parse_intent(intent)

            # Map intent to orchestrator in wiring config
            orchestrator_map = {
                IntentType.IMPLEMENT: "TDDOrchestrator",
                IntentType.FIX: "TDDOrchestrator",
                IntentType.REFACTOR: "RefactoringOrchestrator",
                IntentType.ANALYZE: "LENSSynthesis",
                IntentType.AUDIT: "EnforcementOrchestrator",
                IntentType.DESIGN: "ChallengeEngine",
                IntentType.PLAN: "PlanOrchestrator",
                IntentType.ONBOARD: "RepositoryOnboardingOrchestrator",
                IntentType.DEBUG: "DebuggingOrchestrator",
                IntentType.DIGEST: "DigestEnhancementOrchestrator",
            }

            return orchestrator_map.get(intent_type)

        except Exception as e:
            logger.error(f"Error getting orchestrator for intent {intent}: {e}")
            return None

    def get_available_intents(self) -> List[str]:
        """Get list of supported intents."""
        return [i.value for i in IntentType]

    def get_prompts_for_intent(self, intent: str) -> Dict[str, Any]:
        """
        Get all prompts associated with intent.

        Args:
            intent: Intent string

        Returns:
            Dict with prompt metadata
        """
        result = self.route_to_resources(intent)

        if result["success"]:
            return {
                "success": True,
                "primary": {
                    "name": result["decision"].primary_prompt.name,
                    "content": result["prompt_content"],
                    "category": result["decision"].primary_prompt.category.value,
                },
                "secondary": [
                    {
                        "name": prompt_obj.name,
                        "category": prompt_obj.category.value,
                    }
                    for prompt_obj in result["decision"].secondary_prompts
                ],
            }
        else:
            return {"success": False, "error": result.get("error")}

    def get_agents_for_intent(self, intent: str) -> Dict[str, Any]:
        """
        Get all agents associated with intent.

        Args:
            intent: Intent string

        Returns:
            Dict with agent metadata
        """
        result = self.route_to_resources(intent)

        if result["success"]:
            return {
                "success": True,
                "primary": {
                    "name": result["decision"].primary_agent.name,
                    "content": result["agent_content"],
                    "category": result["decision"].primary_agent.category.value,
                    "capabilities": result["decision"].primary_agent.capabilities,
                },
                "secondary": [
                    {
                        "name": agent_obj.name,
                        "category": agent_obj.category.value,
                        "capabilities": agent_obj.capabilities,
                    }
                    for agent_obj in result["decision"].secondary_agents
                ],
            }
        else:
            return {"success": False, "error": result.get("error")}

    def validate_routing_integrity(self) -> Dict[str, Any]:
        """
        Validate that all intents have valid routing paths.

        Returns:
            Validation result with issues list
        """
        issues = []

        for intent in IntentType:
            decision = self.routing_engine.route(intent)

            if decision.primary_prompt is None:
                issues.append(f"No primary prompt for {intent.value}")

            if decision.primary_agent is None:
                issues.append(f"No primary agent for {intent.value}")

            if decision.confidence_score < 0.5:
                issues.append(
                    f"Low confidence ({decision.confidence_score:.2f}) for {intent.value}"
                )

        return {
            "success": len(issues) == 0,
            "total_intents": len(IntentType),
            "validated": len(IntentType) - len(issues),
            "issues": issues,
        }

    def get_wiring_stats(self) -> Dict[str, Any]:
        """Get wiring statistics."""
        engine_stats = self.routing_engine.get_routing_stats()
        integrity = self.validate_routing_integrity()

        return {
            **engine_stats,
            "integrity": integrity,
            "supported_intents": self.get_available_intents(),
        }


# AC_COMPLETE: AC-INTELLIGENCE-WIRING-001 ✅
