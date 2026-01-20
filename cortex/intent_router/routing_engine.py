"""Routing Engine - Intent routing infrastructure.

Routes classified intents to appropriate handlers using pattern matching
and fallback strategies.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass, field
from enum import Enum
from cortex.intent_router.classifier import IntentCategory


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
    """Routes intents to handlers.
    
    Maps intent categories to handler functions using pattern matching
    and provides fallback routing for unmatched intents.
    
    Attributes:
        routes: List of registered routes
        intent_handlers: Mapping of intent categories to handler names
    """
    
    def __init__(self):
        """Initialize routing engine."""
        self.routes: List[Route] = []
        self.intent_handlers: Dict[IntentCategory, str] = self._build_default_handlers()
    
    def _build_default_handlers(self) -> Dict[IntentCategory, str]:
        """Build default intent-to-handler mapping."""
        return {
            IntentCategory.CREATE: "CreateHandler",
            IntentCategory.FIX: "FixHandler",
            IntentCategory.ANALYZE: "AnalyzeHandler",
            IntentCategory.OPTIMIZE: "OptimizeHandler",
            IntentCategory.REFACTOR: "RefactorHandler",
            IntentCategory.TEST: "TestHandler",
            IntentCategory.DOCUMENT: "DocumentHandler",
            IntentCategory.MODIFY: "ModifyHandler",
            IntentCategory.QUERY: "QueryHandler",
            IntentCategory.COMMAND: "CommandHandler",
            IntentCategory.NAVIGATION: "NavigationHandler",
        }
    
    def add_route(self, route: Route) -> None:
        """Add a route."""
        self.routes.append(route)
    
    def match(self, intent: str) -> Optional[Route]:
        """Match an intent to a route."""
        for route in self.routes:
            if route.pattern == intent or route.pattern == "*":
                return route
        return None
    
    def route(self, intent: IntentCategory, context: Optional[Dict[str, Any]] = None) -> str:
        """Route an intent to handler.
        
        Args:
            intent: Intent category to route
            context: Optional routing context
            
        Returns:
            Handler name for the intent
        """
        if intent in self.intent_handlers:
            return self.intent_handlers[intent]
        return "fallback_handler"


__all__ = ["Route", "RouteType", "RoutingEngine"]