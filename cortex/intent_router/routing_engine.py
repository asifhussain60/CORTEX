"""Routing Engine - Intent routing infrastructure.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum


class RouteType(Enum):
    """Route types."""
    DIRECT = "direct"
    PATTERN = "pattern"
    FALLBACK = "fallback"


@dataclass
class Route:
    """Route definition."""
    name: str
    pattern: str
    handler: Optional[Callable] = None
    route_type: RouteType = RouteType.DIRECT
    metadata: Dict[str, Any] = field(default_factory=dict)


class RoutingEngine:
    """Routes intents to handlers."""
    
    def __init__(self):
        """Initialize routing engine."""
        self.routes: List[Route] = []
    
    def add_route(self, route: Route) -> None:
        """Add a route."""
        self.routes.append(route)
    
    def match(self, intent: str) -> Optional[Route]:
        """Match an intent to a route."""
        for route in self.routes:
            if route.pattern == intent or route.pattern == "*":
                return route
        return None
    
    def route(self, intent: str, context: Optional[Dict[str, Any]] = None) -> Any:
        """Route an intent."""
        route = self.match(intent)
        if route and route.handler:
            return route.handler(intent, context or {})
        return None


__all__ = ["Route", "RouteType", "RoutingEngine"]
