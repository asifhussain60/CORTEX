"""Intent Router for semantic intent recognition and routing."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from cortex.brain.domain_brain.intent_classifier import IntentClassifier
from cortex.brain.domain_brain.intent_parser import NLPIntentParser, ParsedIntent
from cortex.brain.domain_brain.intent_router_interface import IIntentRouter


@dataclass
class IntentResult:
    """Result of intent routing."""

    intent: str
    category: str  # "api", "domain", "workflow", "configuration", "diagnostic"
    confidence: float  # 0.0-1.0
    entities: List[Dict[str, str]] = field(default_factory=list)
    handler: Optional[str] = None
    fallback_handlers: List[Dict[str, Any]] = field(default_factory=list)


class IntentRouter(IIntentRouter):
    """Routes natural language intents to appropriate handlers."""

    # Handler mappings
    HANDLERS = {
        "api": "api_handler",
        "domain": "domain_handler",
        "workflow": "workflow_handler",
        "configuration": "config_handler",
        "diagnostic": "diagnostic_handler"
    }

    def __init__(self) -> None:
        """Initialize Intent Router."""
        self.parser = NLPIntentParser()
        self.classifier = IntentClassifier()
        self.history: List[Dict[str, Any]] = []

    def query_intent(self, query: str) -> IntentResult:
        """Query and route an intent.

        Args:
            query: Natural language query string

        Returns:
            IntentResult with routing information
        """
        # Parse intent
        parsed = self.parser.parse(query)

        # Classify intent
        category = self.classifier.classify(query)
        classification = self.classifier.classify_with_confidence(query)

        # Determine handler
        handler = self.HANDLERS.get(category, "default_handler")

        # Build entity list
        entities = [
            {"value": e.value, "type": e.entity_type, "confidence": e.confidence}
            for e in parsed.entities
        ]

        # Determine if fallback needed
        fallback_handlers = []
        if parsed.confidence < 0.70:
            fallback_handlers = self._get_fallback_handlers(category, classification)

        # Create result
        result = IntentResult(
            intent=parsed.intent,
            category=category,
            confidence=parsed.confidence,
            entities=entities,
            handler=handler,
            fallback_handlers=fallback_handlers
        )

        # Record in history
        self._record_history(query, result)

        return result

    def get_history(self) -> List[Dict[str, Any]]:
        """Get intent execution history.

        Returns:
            List of recent intent queries (max 100)
        """
        return self.history[-100:] if self.history else []

    def _get_fallback_handlers(
        self,
        primary_category: str,
        classification: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Get fallback handler chain for uncertain intent.

        Args:
            primary_category: Primary category from classification
            classification: Full classification results with scores

        Returns:
            List of fallback handlers ordered by confidence
        """
        fallback_handlers = []
        scores = classification.get("scores", {})

        # Get all categories sorted by confidence except primary
        sorted_categories = sorted(
            [(cat, conf) for cat, conf in scores.items() if cat != primary_category],
            key=lambda x: x[1],
            reverse=True
        )

        # If all scores are 0, provide default fallback chain
        if all(conf == 0 for _, conf in sorted_categories):
            # Default fallback chain for unrecognized intents
            default_categories = ["diagnostic", "workflow", "domain", "configuration"]
            for category in default_categories:
                if category != primary_category:
                    fallback_handlers.append({
                        "handler": self.HANDLERS.get(category, "default_handler"),
                        "category": category,
                        "confidence": 0.25  # Equal confidence for all fallbacks
                    })
        else:
            # Use actual scores when available
            for category, confidence in sorted_categories:
                if confidence > 0:
                    fallback_handlers.append({
                        "handler": self.HANDLERS.get(category, "default_handler"),
                        "category": category,
                        "confidence": confidence
                    })

        return fallback_handlers

    def _record_history(self, query: str, result: IntentResult) -> None:
        """Record query in history.

        Args:
            query: Original query text
            result: Intent result
        """
        entry = {
            "text": query,
            "intent": result.intent,
            "category": result.category,
            "confidence": result.confidence,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        self.history.append(entry)

        # Keep only last 100 entries
        if len(self.history) > 100:
            self.history = self.history[-100:]
