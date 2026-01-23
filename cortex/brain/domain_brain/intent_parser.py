"""NLP Intent Parser for semantic intent recognition."""

from typing import List, Dict, Any
from dataclasses import dataclass


@dataclass
class IntentEntity:
    """Represents an entity extracted from intent text."""

    value: str
    entity_type: str  # "resource", "domain", "action", "target", etc.
    confidence: float = 1.0


@dataclass
class ParsedIntent:
    """Result of intent parsing."""

    intent: str  # "retrieve", "create", "update", "delete", "execute", etc.
    confidence: float  # 0.0-1.0
    entities: List[IntentEntity]
    raw_text: str


class NLPIntentParser:
    """Parses natural language queries into structured intents."""

    # Intent keywords mapping
    ACTION_KEYWORDS = {
        "get": "retrieve",
        "retrieve": "retrieve",
        "fetch": "retrieve",
        "list": "retrieve",
        "show": "retrieve",
        "view": "retrieve",
        "create": "create",
        "new": "create",
        "make": "create",
        "add": "create",
        "update": "update",
        "modify": "update",
        "change": "update",
        "edit": "update",
        "delete": "delete",
        "remove": "delete",
        "execute": "execute",
        "run": "execute",
        "start": "execute",
        "perform": "execute",
        "monitor": "monitor",
        "check": "monitor",
        "watch": "monitor",
    }

    ENTITY_KEYWORDS = {
        "user": "resource",
        "account": "resource",
        "workflow": "resource",
        "pipeline": "resource",
        "data": "resource",
        "record": "resource",
        "finance": "domain",
        "healthcare": "domain",
        "ecommerce": "domain",
        "batch": "action",
        "health": "target",
        "status": "target",
        "cpu": "target",
        "memory": "target",
    }

    def parse(self, text: str) -> ParsedIntent:
        """Parse natural language text into intent.
        
        Args:
            text: Natural language query string
            
        Returns:
            ParsedIntent with extracted intent, entities, and confidence
            
        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Query text cannot be empty")

        text_lower = text.lower()
        
        # Extract intent action
        detected_action = None
        action_confidence = 0.0
        
        for keyword, action in self.ACTION_KEYWORDS.items():
            if keyword in text_lower:
                detected_action = action
                action_confidence = 0.85
                break
        
        if not detected_action:
            detected_action = "query"
            action_confidence = 0.5

        # Extract entities
        entities = self._extract_entities(text_lower)
        
        # Calculate overall confidence
        base_confidence = action_confidence
        if entities:
            base_confidence = min(1.0, base_confidence + 0.1 * len(entities))
        
        confidence = min(1.0, base_confidence)
        
        return ParsedIntent(
            intent=detected_action,
            confidence=confidence,
            entities=entities,
            raw_text=text
        )

    def _extract_entities(self, text: str) -> List[IntentEntity]:
        """Extract entities from text.
        
        Args:
            text: Lowercase text to extract from
            
        Returns:
            List of identified entities
        """
        entities = []
        found_keywords = set()
        
        for keyword, entity_type in self.ENTITY_KEYWORDS.items():
            if keyword in text and keyword not in found_keywords:
                entities.append(
                    IntentEntity(
                        value=keyword,
                        entity_type=entity_type,
                        confidence=0.8
                    )
                )
                found_keywords.add(keyword)
        
        return entities
