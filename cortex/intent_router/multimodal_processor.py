"""Multi-Modal Intent Processor - Handle diverse input formats.

Processes multi-modal inputs including text, JSON, commands, code,
and domain-specific schemas. Converts all to text for classification.

Author: CORTEX Framework
"""

import json
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Union

from cortex.intent_router.classifier import IntentClassifier


class InputModality(Enum):
    """Input modality types."""
    TEXT = "text"
    JSON = "json"
    COMMAND = "command"
    CODE = "code"
    SCHEMA = "schema"


@dataclass
class ModalityInput:
    """Multi-modal input container.

    Attributes:
        modality: Type of input modality
        content: Input content (text, dict, etc.)
        metadata: Optional metadata dict
    """
    modality: InputModality
    content: Union[str, Dict[str, Any]]
    metadata: Dict[str, Any]


class MultiModalIntentProcessor:
    """Process multi-modal intent inputs.

    Handles diverse input formats and converts them to text for
    intent classification.

    Attributes:
        classifier: Internal intent classifier
        metrics: Processing metrics dictionary
    """

    def __init__(self):
        """Initialize processor."""
        self.classifier = IntentClassifier()
        self.metrics: Dict[str, Any] = {
            "total_processed": 0,
            "by_modality": {
                "text": 0,
                "json": 0,
                "command": 0,
                "code": 0,
                "schema": 0,
            },
            "conversion_failures": 0,
        }

    def _json_to_text(self, json_data: Dict[str, Any]) -> str:
        """Convert JSON to text.

        Args:
            json_data: JSON dictionary

        Returns:
            Text representation
        """
        if not json_data:
            return "perform operation"

        parts = []
        if "operation" in json_data:
            parts.append(json_data["operation"])
        if "action" in json_data:
            parts.append(json_data["action"])
        if "target" in json_data:
            parts.append(json_data["target"])
        if "domain" in json_data:
            parts.append(json_data["domain"])
        if "type" in json_data:
            parts.append(json_data["type"])

        return " ".join(parts) if parts else "perform operation"

    def _command_to_text(self, command: str) -> str:
        """Convert command to text.

        Args:
            command: Command-line style string

        Returns:
            Text representation
        """
        # Remove flags and extract main action words
        parts = command.split()
        words = [p for p in parts if not p.startswith('--')]
        return " ".join(words)

    def _code_to_text(self, code: str) -> str:
        """Convert code to text.

        Args:
            code: Code snippet

        Returns:
            Text description
        """
        code_lower = code.lower()

        if "def " in code_lower:
            return "create function"
        elif "class " in code_lower:
            return "create class"
        elif "raise " in code_lower or "error" in code_lower:
            return "handle error"
        else:
            return "modify code"

    def _schema_to_text(self, schema: Dict[str, Any]) -> str:
        """Convert schema to text.

        Args:
            schema: Domain-specific schema

        Returns:
            Text representation
        """
        parts = []
        if "action" in schema:
            parts.append(schema["action"])
        if "type" in schema:
            parts.append(schema["type"])

        return " ".join(parts) if parts else "perform operation"

    def process(self, input_data: ModalityInput) -> Dict[str, Any]:
        """Process multi-modal input.

        Args:
            input_data: Input with modality type

        Returns:
            Dictionary with intent, confidence, signals, keywords, modality

        Raises:
            ValueError: If input_data is not ModalityInput
        """
        if not isinstance(input_data, ModalityInput):
            raise ValueError("input_data must be ModalityInput")

        # Track metrics
        self.metrics["total_processed"] += 1
        modality_name = input_data.modality.value
        self.metrics["by_modality"][modality_name] += 1

        # Convert to text based on modality
        try:
            if input_data.modality == InputModality.TEXT:
                text = str(input_data.content)
            elif input_data.modality == InputModality.JSON:
                text = self._json_to_text(input_data.content)
            elif input_data.modality == InputModality.COMMAND:
                text = self._command_to_text(str(input_data.content))
            elif input_data.modality == InputModality.CODE:
                text = self._code_to_text(str(input_data.content))
            elif input_data.modality == InputModality.SCHEMA:
                text = self._schema_to_text(input_data.content)
            else:
                text = str(input_data.content)
        except (TypeError, AttributeError, ValueError) as e:
            self.metrics["conversion_failures"] += 1
            raise ValueError(f"Failed to convert {modality_name}: {e}")

        # Classify
        result = self.classifier.classify(text)

        # Return structured result
        return {
            "intent": result.primary_intent,
            "confidence": result.confidence_score,
            "signals": result.detected_signals,
            "keywords": result.keywords,
            "modality": modality_name,
        }

    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics.

        Returns:
            Metrics dictionary
        """
        return self.metrics


__all__ = ["InputModality", "ModalityInput", "MultiModalIntentProcessor"]
