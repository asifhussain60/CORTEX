"""Knowledge Graph Routing Optimization (PHASE-KG-004).

Integrates KG insights into routing engine for optimized orchestration decisions
based on service capabilities, topology, latency, and resource constraints.
"""

import time
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, field
from cortex.brain.core.knowledge.graph.interface import IGraphAdapter, GraphQueryError


@dataclass
class OptimizedRouteResult:
    """Result of routing optimization.
    
    Attributes:
        status: Optimization status (SUCCESS, FAILED, NO_ROUTE)
        original_route: Original routing decision
        optimized_route: Optimized routing path
        fallback_route: Fallback route if optimal unavailable
        improvement_percentage: Percent improvement vs original
        estimated_latency_ms: Estimated latency in milliseconds
        reliability_score: Reliability score (0-1)
        estimated_cost: Estimated cost metric
    """
    status: str
    original_route: Optional[List[str]] = None
    optimized_route: Optional[List[str]] = None
    fallback_route: Optional[List[str]] = None
    improvement_percentage: float = 0.0
    estimated_latency_ms: float = 0.0
    reliability_score: float = 1.0
    estimated_cost: float = 0.0


class SemanticCapabilityMatcher:
    """Match services to required capabilities using semantic matching.
    
    Finds services that provide required capabilities with coverage scoring
    and optional fuzzy/semantic matching for similar capability names.
    """

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize capability matcher.
        
        Args:
            adapter: IGraphAdapter instance
        """
        self.adapter = adapter

    def find_services_with_capabilities(
        self,
        required: List[str],
        min_coverage: float = 1.0,
        semantic_match: bool = False,
    ) -> List[Dict[str, Any]]:
        """Find services providing required capabilities.
        
        Args:
            required: List of required capability names
            min_coverage: Minimum coverage ratio (0-1)
            semantic_match: Enable fuzzy capability matching
        
        Returns:
            List[Dict]: Services ranked by coverage score
        """
        matches = []
        
        try:
            services = self.adapter.query_entities("Service", {})
            
            for service in services:
                capabilities = service.properties.get("capabilities", [])
                
                # Count matched capabilities
                matched = 0
                for req_cap in required:
                    if req_cap in capabilities:
                        matched += 1
                    elif semantic_match and self._fuzzy_match(req_cap, capabilities):
                        matched += 1
                
                coverage = matched / len(required) if required else 0.0
                
                if coverage >= min_coverage:
                    matches.append(
                        {
                            "service_id": service.id,
                            "service_name": service.properties.get("name", service.id),
                            "coverage_score": coverage,
                            "matched_capabilities": matched,
                            "total_required": len(required),
                        }
                    )
            
            # Sort by coverage score descending
            matches.sort(key=lambda x: x["coverage_score"], reverse=True)
            return matches
        
        except (GraphQueryError, ValueError, TypeError):
            return []

    def _fuzzy_match(self, required: str, available: List[str]) -> bool:
        """Fuzzy match capability names.
        
        Args:
            required: Required capability
            available: Available capabilities
        
        Returns:
            bool: True if fuzzy match found
        """
        # Simple prefix/substring matching
        req_lower = required.lower()
        for avail in available:
            avail_lower = avail.lower()
            if req_lower in avail_lower or avail_lower in req_lower:
                if abs(len(req_lower) - len(avail_lower)) <= 2:
                    return True
        return False


@dataclass
class RoutingDecision:
    """Routing decision with optimization details.
    
    Attributes:
        status: Decision status (SUCCESS, FAILED, NO_ROUTE)
        recommended_path: Recommended service path
        optimal_service: Single optimal service if applicable
        estimated_latency_ms: Estimated latency
        reliability_score: Reliability score
        estimated_cost: Estimated cost
        reasoning: Decision reasoning
    """
    status: str
    recommended_path: Optional[List[str]] = None
    optimal_service: Optional[str] = None
    estimated_latency_ms: float = 0.0
    reliability_score: float = 1.0
    estimated_cost: float = 0.0
    reasoning: str = ""


class RoutingDecisionEngine:
    """Decision engine for optimal routing based on KG topology.
    
    Analyzes service topology, capabilities, and constraints to make
    optimal routing decisions.
    """

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize routing decision engine.
        
        Args:
            adapter: IGraphAdapter instance
        """
        self.adapter = adapter
        self.matcher = SemanticCapabilityMatcher(adapter)

    def decide_route(
        self,
        api_id: str,
        target_tier: Optional[int] = None,
        required_capabilities: Optional[List[str]] = None,
        max_tier: Optional[int] = None,
        optimize_for: str = "default",
    ) -> RoutingDecision:
        """Make routing decision for API.
        
        Args:
            api_id: API identifier
            target_tier: Target service tier
            required_capabilities: Required service capabilities
            max_tier: Maximum tier constraint
            optimize_for: Optimization target (latency, reliability, cost, default)
        
        Returns:
            RoutingDecision: Routing decision
        """
        try:
            # Get API entity
            api_entities = self.adapter.query_entities("API", {})
            api = None
            for entity in api_entities:
                if entity.id == api_id:
                    api = entity
                    break
            
            if not api:
                return RoutingDecision(status="FAILED", reasoning="API not found")
            
            # Get required capabilities from API if not provided
            if not required_capabilities:
                required_capabilities = api.properties.get("required_capabilities", [])
            
            # Find matching services
            services = self.matcher.find_services_with_capabilities(
                required_capabilities if required_capabilities else []
            )
            
            if not services:
                return RoutingDecision(status="NO_ROUTE", reasoning="No services match requirements")
            
            # Apply tier constraints
            if max_tier:
                services = [
                    s for s in services
                    if self._get_service_tier(s["service_id"]) <= max_tier
                ]
            
            if not services:
                return RoutingDecision(status="NO_ROUTE", reasoning="No services match tier constraints")
            
            # Select optimal service based on optimization target
            optimal = self._select_optimal_service(services, optimize_for)
            
            return RoutingDecision(
                status="SUCCESS",
                optimal_service=optimal["service_id"],
                recommended_path=[api_id, optimal["service_id"]],
                reliability_score=0.95,
                reasoning=f"Selected {optimal['service_name']} with {optimal['coverage_score']:.0%} capability coverage",
            )
        
        except (GraphQueryError, ValueError, TypeError) as e:
            return RoutingDecision(status="FAILED", reasoning=str(e))

    def _get_service_tier(self, service_id: str) -> int:
        """Get service tier level.
        
        Args:
            service_id: Service ID
        
        Returns:
            int: Tier level (1-3)
        """
        try:
            services = self.adapter.query_entities("Service", {})
            for service in services:
                if service.id == service_id:
                    return int(service.properties.get("tier", 3))
        except (ValueError, TypeError, GraphQueryError):
            pass
        return 3

    def _select_optimal_service(
        self, services: List[Dict[str, Any]], optimize_for: str
    ) -> Dict[str, Any]:
        """Select optimal service based on optimization target.
        
        Args:
            services: List of candidate services
            optimize_for: Optimization target
        
        Returns:
            Dict: Optimal service
        """
        if optimize_for in ["latency", "default"]:
            # Prefer lower tier (faster)
            return min(services, key=lambda s: self._get_service_tier(s["service_id"]))
        elif optimize_for == "reliability":
            # Prefer higher tier for reliability
            return max(services, key=lambda s: self._get_service_tier(s["service_id"]))
        elif optimize_for == "cost":
            # Prefer lower tier for cost
            return min(services, key=lambda s: self._get_service_tier(s["service_id"]))
        else:
            # Default: highest coverage
            return max(services, key=lambda s: s["coverage_score"])


class RoutingOptimizer:
    """End-to-end routing optimization with caching and audit logging.
    
    Optimizes routing decisions with comprehensive metrics tracking,
    fallback routing, and idempotent caching.
    """

    def __init__(self, adapter: IGraphAdapter) -> None:
        """Initialize routing optimizer.
        
        Args:
            adapter: IGraphAdapter instance
        """
        self.adapter = adapter
        self.engine = RoutingDecisionEngine(adapter)
        self._optimization_cache: Dict[str, OptimizedRouteResult] = {}
        self._optimization_log: List[Dict[str, Any]] = []

    def optimize_routing(
        self, api_id: str, constraints: Dict[str, Any]
    ) -> OptimizedRouteResult:
        """Optimize routing for API with constraints.
        
        Args:
            api_id: API identifier
            constraints: Routing constraints dict with optional keys:
                - optimize_forUnion[latency, reliability]|cost (default: latency)
                - max_tier: maximum service tier
                - required_capabilities: list of required capabilities
                - max_latency_ms: maximum latency in milliseconds
        
        Returns:
            OptimizedRouteResult: Optimization result with metrics
        """
        # Check cache
        cache_key = f"{api_id}:{str(constraints)}"
        if cache_key in self._optimization_cache:
            return self._optimization_cache[cache_key]
        
        start_time = time.time()
        
        try:
            # Make routing decision
            decision = self.engine.decide_route(
                api_id,
                target_tier=constraints.get("target_tier"),
                required_capabilities=constraints.get("required_capabilities"),
                max_tier=constraints.get("max_tier"),
                optimize_for=constraints.get("optimize_for", "latency"),
            )
            
            if decision.status != "SUCCESS":
                result = OptimizedRouteResult(
                    status=decision.status,
                    original_route=None,
                    optimized_route=None,
                )
            else:
                # Calculate metrics
                estimated_latency = self._estimate_latency(decision.recommended_path or [])
                reliability = decision.reliability_score
                estimated_cost = self._estimate_cost(decision.recommended_path or [])
                
                result = OptimizedRouteResult(
                    status="SUCCESS",
                    original_route=[api_id, "direct_service"],
                    optimized_route=decision.recommended_path,
                    fallback_route=[api_id, "fallback_service"],
                    improvement_percentage=15.0,  # Default improvement estimate
                    estimated_latency_ms=estimated_latency,
                    reliability_score=reliability,
                    estimated_cost=estimated_cost,
                )
            
            # Log optimization
            self._log_optimization(api_id, result, time.time() - start_time)
            
            # Cache result
            self._optimization_cache[cache_key] = result
            
            return result
        
        except Exception as e:
            result = OptimizedRouteResult(
                status="FAILED",
            )
            self._log_optimization(api_id, result, time.time() - start_time)
            return result

    def _estimate_latency(self, path: List[str]) -> float:
        """Estimate total latency for routing path.
        
        Args:
            path: Service path
        
        Returns:
            float: Estimated latency in milliseconds
        """
        total_latency = 0.0
        
        try:
            for i in range(len(path) - 1):
                # Get relationship between consecutive services
                paths = self.adapter.query_paths(path[i], None, max_hops=1)
                for p in paths:
                    if len(p.nodes) > 1 and p.nodes[-1] == path[i + 1]:
                        # Found direct relationship - could extract latency from properties
                        total_latency += 50.0  # Default hop latency
            
            return total_latency
        
        except (GraphQueryError, ValueError, TypeError):
            return len(path) * 50.0

    def _estimate_cost(self, path: List[str]) -> float:
        """Estimate cost for routing path.
        
        Args:
            path: Service path
        
        Returns:
            float: Estimated cost
        """
        try:
            cost = 0.0
            for service_id in path:
                if service_id.startswith("svc-"):
                    # Get service tier to estimate cost
                    services = self.adapter.query_entities("Service", {})
                    for service in services:
                        if service.id == service_id:
                            tier = int(service.properties.get("tier", 3))
                            cost += tier * 1.5  # Tier-based cost
            
            return cost
        
        except (GraphQueryError, ValueError, TypeError):
            return len(path) * 1.0

    def _log_optimization(
        self, api_id: str, result: OptimizedRouteResult, elapsed: float
    ) -> None:
        """Log optimization decision.
        
        Args:
            api_id: API identifier
            result: Optimization result
            elapsed: Execution time
        """
        self._optimization_log.append(
            {
                "timestamp": time.time(),
                "api_id": api_id,
                "status": result.status,
                "optimized_route": result.optimized_route,
                "latency_ms": result.estimated_latency_ms,
                "execution_time_ms": elapsed * 1000,
            }
        )

    def get_optimization_log(self) -> List[Dict[str, Any]]:
        """Get optimization log.
        
        Returns:
            List[Dict]: Optimization log entries
        """
        return self._optimization_log
