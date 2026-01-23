"""
WIRE-004 Implementation - Intent Routing Logic

AC-TRANSFORM-001-WIRE-004: Implement intelligent intent routing

This module implements the core routing logic that enables the system to:
- Parse user intents and keywords
- Match intents to appropriate orchestrators
- Score and rank matches by relevance
- Execute with confidence thresholds

Expected Coverage: Enables all 23 orchestrators through intelligent routing
Target Time: 8 hours (EXPRESS LANE - optimized implementation)
Status: Phase 4 Implementation

Author: GitHub Copilot
Date: 2026-01-24
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass

from cortex.orchestrators.core.orchestrator_wiring import (
    OrchestratorWiringRegistry,
    OrchestratorWiringMetadata,
    get_wiring_registry,
)

logger = logging.getLogger(__name__)


@dataclass
class IntentMatch:
    """Represents a matched orchestrator for an intent"""
    domain: str
    confidence_score: float
    matched_keywords: List[str]
    matched_capabilities: List[str]


class IntentRoutingEngine:
    """WIRE-004: Intent Routing Logic"""
    
    def __init__(self, registry: Optional[OrchestratorWiringRegistry] = None):
        """Initialize routing engine.
        
        Args:
            registry: Optional registry instance, defaults to singleton
        """
        self.registry = registry or get_wiring_registry()
        self.logger = logger
        self.confidence_threshold = 0.5
    
    def parse_intent(self, user_input: str) -> Dict[str, Any]:
        """Parse user input to extract intent and keywords.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Dictionary with intent, keywords, action type
        """
        tokens = user_input.lower().split()
        return {
            "raw_input": user_input,
            "tokens": tokens,
            "keywords": tokens,
            "intent": user_input.lower(),
        }
    
    def find_matches(
        self, intent_data: Dict[str, Any]
    ) -> List[IntentMatch]:
        """Find orchestrators matching the intent.
        
        Args:
            intent_data: Parsed intent data
            
        Returns:
            List of matching orchestrators ranked by confidence
        """
        keywords = intent_data.get("keywords", [])
        matches: List[IntentMatch] = []
        
        for keyword in keywords:
            # Try keyword matching
            orchestrators = self.registry.get_by_keyword(keyword)
            for orch_meta in orchestrators:
                # Check if we already have this match
                existing = next(
                    (m for m in matches if m.domain == orch_meta.domain),
                    None
                )
                
                if existing:
                    existing.matched_keywords.append(keyword)
                    existing.confidence_score = min(
                        1.0, existing.confidence_score + 0.1
                    )
                else:
                    matches.append(
                        IntentMatch(
                            domain=orch_meta.domain,
                            confidence_score=0.7,
                            matched_keywords=[keyword],
                            matched_capabilities=[],
                        )
                    )
        
        # Try capability matching
        for token in keywords:
            orchestrators = self.registry.get_by_capability(token)
            for orch_meta in orchestrators:
                existing = next(
                    (m for m in matches if m.domain == orch_meta.domain),
                    None
                )
                
                if existing:
                    existing.matched_capabilities.append(token)
                    existing.confidence_score = min(
                        1.0, existing.confidence_score + 0.15
                    )
                else:
                    matches.append(
                        IntentMatch(
                            domain=orch_meta.domain,
                            confidence_score=0.8,
                            matched_keywords=[],
                            matched_capabilities=[token],
                        )
                    )
        
        # Sort by confidence score
        return sorted(
            matches,
            key=lambda m: m.confidence_score,
            reverse=True
        )
    
    def route_intent(self, user_input: str) -> Optional[IntentMatch]:
        """Route user input to the best matching orchestrator.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Best matching orchestrator or None if no confident match
        """
        intent_data = self.parse_intent(user_input)
        matches = self.find_matches(intent_data)
        
        if not matches:
            self.logger.warning(f"No orchestrator match for: {user_input}")
            return None
        
        best_match = matches[0]
        
        if best_match.confidence_score < self.confidence_threshold:
            self.logger.warning(
                f"Low confidence ({best_match.confidence_score:.2f}) "
                f"for: {user_input}"
            )
            return None
        
        self.logger.info(
            f"Routed '{user_input}' to {best_match.domain} "
            f"(confidence: {best_match.confidence_score:.2f})"
        )
        
        return best_match
    
    def execute_routing(
        self, user_input: str
    ) -> Dict[str, Any]:
        """Execute intent routing with execution.
        
        Args:
            user_input: User's natural language input
            
        Returns:
            Dictionary with routing result and execution status
        """
        match = self.route_intent(user_input)
        
        if not match:
            return {
                "status": "no_match",
                "input": user_input,
                "error": "No confident orchestrator match found",
            }
        
        # Get orchestrator metadata
        metadata = self.registry.get_orchestrator(match.domain)
        
        if not metadata:
            return {
                "status": "orchestrator_not_found",
                "domain": match.domain,
                "error": "Matched orchestrator not in registry",
            }
        
        return {
            "status": "success",
            "input": user_input,
            "matched_domain": match.domain,
            "confidence_score": match.confidence_score,
            "matched_keywords": match.matched_keywords,
            "matched_capabilities": match.matched_capabilities,
            "orchestrator_name": metadata.domain,
            "orchestrator_capabilities": metadata.capabilities,
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get routing engine statistics.
        
        Returns:
            Dictionary with routing statistics
        """
        all_orchs = self.registry.get_wiring_status()
        
        return {
            "total_orchestrators": all_orchs.get("total_wired", 0),
            "by_category": all_orchs.get("by_category", {}),
            "coverage_percentage": all_orchs.get("coverage_percentage", 0),
            "confidence_threshold": self.confidence_threshold,
        }


def create_routing_engine() -> IntentRoutingEngine:
    """Factory function to create routing engine.
    
    Returns:
        New IntentRoutingEngine instance
    """
    return IntentRoutingEngine()


if __name__ == "__main__":
    engine = create_routing_engine()
    
    test_intents = [
        "create new workflow",
        "test this code",
        "analyze project",
        "setup environment",
        "upgrade to latest",
    ]
    
    for intent in test_intents:
        result = engine.execute_routing(intent)
        print(f"\nIntent: {intent}")
        print(f"Result: {result}")
