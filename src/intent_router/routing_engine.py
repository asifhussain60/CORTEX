"""AC-PHX-007-06: Routing Decision Logic"""
from typing import Dict, Optional
from src.intent_router.classifier import IntentCategory

class RoutingEngine:
    """Routes intents to handlers."""
    ROUTING_MAP: Dict[IntentCategory, str] = {
        IntentCategory.CREATE: "CreateHandler",
        IntentCategory.MODIFY: "ModifyHandler",
        IntentCategory.FIX: "FixHandler",
        IntentCategory.ANALYZE: "AnalyzeHandler",
        IntentCategory.OPTIMIZE: "OptimizeHandler",
        IntentCategory.REFACTOR: "RefactorHandler",
        IntentCategory.TEST: "TestHandler",
        IntentCategory.DOCUMENT: "DocumentHandler",
    }
    
    def route(self, intent: IntentCategory) -> Optional[str]:
        """Route intent to handler."""
        return self.ROUTING_MAP.get(intent)
