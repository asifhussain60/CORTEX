"""
Agent Discovery Service

AC_START: AC-PHASE27-S3-003
Component: AgentDiscoveryService
Authority: Phase 27 Consolidation (GAP-03)

Objective:
Capability-based agent discovery. Find agents by required capabilities with
ranking by confidence. Supports single and multiple capability queries.

Features:
• Capability-based discovery (single or multiple)
• Ranking by capability match confidence
• Sub-50ms discovery performance
• Integration with AgentCapabilityRegistry

Performance Targets:
• Discovery (single capability): <30ms
• Discovery (multiple capabilities): <50ms

AC_COMPLETE: AC-PHASE27-S3-003
"""

import logging
from typing import List, Dict, Any, Optional
from cortex.brain.persistence.agent_capability_registry import AgentCapabilityRegistry

logger = logging.getLogger(__name__)


# ============================================================================
# AGENT DISCOVERY SERVICE
# ============================================================================


class AgentDiscoveryService:
    """
    Agent Discovery Service: Capability-based agent discovery.
    
    Find agents by required capabilities with ranking. Supports single and
    multiple capability queries with confidence scoring.
    
    Example:
        >>> service = AgentDiscoveryService(registry)
        >>> agents = service.discover_agents(["test_generation"])
        >>> print(agents[0]["agent_id"])
        'tdd_orchestrator'
    """
    
    def __init__(self, capability_registry: AgentCapabilityRegistry):
        """
        Initialize Agent Discovery Service.
        
        Args:
            capability_registry: AgentCapabilityRegistry instance
        """
        self.capability_registry = capability_registry
        logger.info("AgentDiscoveryService initialized")
    
    def discover_agents(
        self,
        required_capabilities: List[str],
        min_confidence: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Discover agents by required capabilities.
        
        Args:
            required_capabilities: List of required capability identifiers
            min_confidence: Minimum match confidence (0.0 to 1.0)
        
        Returns:
            List of agents sorted by match confidence (descending)
        
        Example (single capability):
            >>> agents = service.discover_agents(["test_generation"])
            >>> print(agents[0]["agent_id"])
            'tdd_orchestrator'
        
        Example (multiple capabilities):
            >>> agents = service.discover_agents(
            ...     ["code_refactoring", "extract_method"]
            ... )
            >>> print(agents[0]["agent_id"])
            'refactoring_orchestrator'
        """
        if not required_capabilities:
            return []
        
        # Get all agents
        all_agents = self.capability_registry.get_all_agents()
        
        # Score each agent by capability match
        scored_agents = []
        for agent in all_agents:
            agent_capabilities = set(agent["capabilities"])
            required_set = set(required_capabilities)
            
            # Check if agent has ALL required capabilities
            if required_set.issubset(agent_capabilities):
                # Confidence = (required capabilities met) / (total agent capabilities)
                # Higher confidence for specialists (fewer extra capabilities)
                confidence = len(required_set) / len(agent_capabilities)
                
                scored_agents.append({
                    **agent,
                    "match_confidence": confidence,
                    "matched_capabilities": list(required_set)
                })
        
        # Filter by minimum confidence
        scored_agents = [a for a in scored_agents if a["match_confidence"] >= min_confidence]
        
        # Sort by confidence (descending)
        scored_agents.sort(key=lambda a: a["match_confidence"], reverse=True)
        
        logger.info(
            f"Discovery: {len(scored_agents)} agents found for {required_capabilities}"
        )
        
        return scored_agents
    
    def discover_best_agent(
        self,
        required_capabilities: List[str]
    ) -> Optional[Dict[str, Any]]:
        """
        Discover best agent for required capabilities.
        
        Args:
            required_capabilities: List of required capability identifiers
        
        Returns:
            Best matching agent or None if no match
        
        Example:
            >>> agent = service.discover_best_agent(["security_audit"])
            >>> print(agent["agent_id"])
            'security_checkpoint'
        """
        agents = self.discover_agents(required_capabilities)
        
        if agents:
            return agents[0]
        
        return None
    
    def discover_agents_by_capability(
        self,
        capability: str
    ) -> List[Dict[str, Any]]:
        """
        Discover agents with specific capability.
        
        Args:
            capability: Single capability identifier
        
        Returns:
            List of agents with the capability
        
        Example:
            >>> agents = service.discover_agents_by_capability("code_refactoring")
            >>> print([a["agent_id"] for a in agents])
            ['refactoring_orchestrator']
        """
        return self.capability_registry.find_agents_by_capability(capability)
    
    def get_agent_capabilities(self, agent_id: str) -> Optional[List[str]]:
        """
        Get capabilities for specific agent.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            List of capabilities or None if agent not found
        
        Example:
            >>> caps = service.get_agent_capabilities("tdd_orchestrator")
            >>> print(caps)
            ['test_generation', 'coverage_analysis']
        """
        agent = self.capability_registry.get_agent(agent_id)
        
        if agent:
            return agent["capabilities"]
        
        return None
