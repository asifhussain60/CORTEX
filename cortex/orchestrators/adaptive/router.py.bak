"""Adaptive Router for intelligent task-to-orchestrator routing.

This module implements routing of tasks to appropriate orchestrators based on
context analysis, load balancing, and quality-of-service requirements.

AC-PHX-010-03: Adaptive routing including:
- Route to appropriate orchestrator based on context
- Fallback handling
- Load balancing
- Quality-of-service routing

Author: Asif Hussain
Copyright: © 2025-2026 Asif Hussain. All rights reserved.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
from enum import Enum


class QoSLevel(Enum):
    """Quality of service levels."""
    BEST_EFFORT = "best_effort"
    STANDARD = "standard"
    PREMIUM = "premium"


@dataclass
class Route:
    """Represents a routing decision."""
    orchestrator: str
    path: List[str] = field(default_factory=list)
    fallbacks: List[str] = field(default_factory=list)
    qos_level: QoSLevel = QoSLevel.STANDARD
    timeout: float = 30.0
    metadata: Dict[str, Any] = field(default_factory=dict)


class AdaptiveRouter:
    """Routes tasks to appropriate orchestrators intelligently.
    
    Selects orchestrators based on:
    - Task characteristics
    - Execution context
    - Load balancing
    - QoS requirements
    - Historical performance
    
    Example:
        >>> router = AdaptiveRouter()
        >>> task = {"domain": "planning", "type": "strategy"}
        >>> route = router.route(task)
        >>> print(f"Orchestrator: {route.orchestrator}")
    """
    
    def __init__(self) -> None:
        """Initialize router with domain-to-orchestrator mappings."""
        self._domain_orchestrator_map: Dict[str, List[str]] = {
            "planning": ["PlanningOrchestrator", "MasterOrchestrator"],
            "analysis": ["PlanningOrchestrator", "AnalysisOrchestrator"],
            "integration": ["IntegrationOrchestrator", "MasterOrchestrator"],
            "execution": ["ExecutionOrchestrator", "MasterOrchestrator"],
            "validation": ["ValidationOrchestrator", "PlanningOrchestrator"],
        }
        
        # Load tracking for balancing
        self._orchestrator_load: Dict[str, int] = {}
        
        # Route history
        self._route_history: List[Dict[str, Any]] = []
    
    def route(
        self,
        task: Dict[str, Any],
        context: Optional[Dict[str, Any]] = None
    ) -> Route:
        """Route a task to an appropriate orchestrator.
        
        Args:
            task: Task dictionary with domain, type, etc.
            context: Optional execution context
            
        Returns:
            Route object with orchestrator and fallback info
        """
        domain = task.get("domain", "planning")
        
        # Get candidate orchestrators
        candidates = self._get_candidate_orchestrators(domain)
        
        # Select primary orchestrator with load balancing
        primary = self._select_with_load_balancing(candidates)
        
        # Get fallback options
        fallbacks = [o for o in candidates if o != primary]
        
        # Determine QoS level
        qos = self._determine_qos(task)
        
        # Create route
        route = Route(
            orchestrator=primary,
            path=[primary],
            fallbacks=fallbacks,
            qos_level=qos,
            metadata={
                "domain": domain,
                "selected_at": datetime.now().isoformat(),
                "candidates_count": len(candidates),
            }
        )
        
        # Record route
        self._route_history.append({
            "task_domain": domain,
            "selected": primary,
            "fallbacks": fallbacks,
            "qos": qos.value,
        })
        
        return route
    
    def _get_candidate_orchestrators(self, domain: str) -> List[str]:
        """Get candidate orchestrators for a domain.
        
        Args:
            domain: Task domain
            
        Returns:
            List of candidate orchestrator names
        """
        return self._domain_orchestrator_map.get(domain, ["MasterOrchestrator"])
    
    def _select_with_load_balancing(self, candidates: List[str]) -> str:
        """Select orchestrator with load balancing.
        
        Args:
            candidates: List of candidate orchestrators
            
        Returns:
            Selected orchestrator name
        """
        if not candidates:
            return "MasterOrchestrator"
        
        if len(candidates) == 1:
            return candidates[0]
        
        # Round-robin load balancing
        loads = {o: self._orchestrator_load.get(o, 0) for o in candidates}
        selected = min(candidates, key=lambda o: loads[o])
        
        # Update load
        self._orchestrator_load[selected] = loads[selected] + 1
        
        return selected
    
    def _determine_qos(self, task: Dict[str, Any]) -> QoSLevel:
        """Determine QoS level for task.
        
        Args:
            task: Task dictionary
            
        Returns:
            QoS level
        """
        qos_spec = task.get("qos", {})
        
        if qos_spec.get("priority") == "critical":
            return QoSLevel.PREMIUM
        elif task.get("complexity") == "high":
            return QoSLevel.PREMIUM
        else:
            return QoSLevel.STANDARD
    
    def record_route_result(
        self,
        route: Route,
        success: bool,
        duration: float
    ) -> None:
        """Record the result of a route.
        
        Args:
            route: The route that was used
            success: Whether execution succeeded
            duration: Execution duration in seconds
        """
        # Decrease load on orchestrator
        if route.orchestrator in self._orchestrator_load:
            self._orchestrator_load[route.orchestrator] = max(
                0,
                self._orchestrator_load[route.orchestrator] - 1
            )
    
    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics.
        
        Returns:
            Statistics dictionary
        """
        if not self._route_history:
            return {}
        
        domain_counts: Dict[str, int] = {}
        orchestrator_counts: Dict[str, int] = {}
        
        for record in self._route_history:
            domain = record["task_domain"]
            orch = record["selected"]
            
            domain_counts[domain] = domain_counts.get(domain, 0) + 1
            orchestrator_counts[orch] = orchestrator_counts.get(orch, 0) + 1
        
        return {
            "total_routes": len(self._route_history),
            "by_domain": domain_counts,
            "by_orchestrator": orchestrator_counts,
        }
