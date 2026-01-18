"""
Multi-Modal Intent Processing - AC-PHX-007-02

Extends intent classification to support multiple input modalities:
- Natural language text descriptions
- Structured intent objects (JSON/dict)
- Command-line style operations
- Code snippets and context
- Domain-specific schemas

CORTEX Governance Rules Applied:
- CORE-008: TDD (tests first)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
- CORE-013: Specific exception handling
- CORE-027: Audit trail logging

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from enum import Enum
import json

from cortex.brain.intent_router.classifier import IntentClassifier, IntentCategory


class InputModality(Enum):
    """Input modality types for intent processing.
    
    Attributes:
        TEXT: Natural language text
        JSON: Structured JSON/dict format
        COMMAND: Command-line style input
        CODE: Code snippet or context
        SCHEMA: Domain-specific schema
    """
    TEXT = "text"
    JSON = "json"
    COMMAND = "command"
    CODE = "code"
    SCHEMA = "schema"


@dataclass
class ModalityInput:
    """Multi-modal input representation.
    
    Attributes:
        modality: Input modality type
        content: Input content
        metadata: Additional metadata (domain, language, etc.)
        source: Source identifier (UI, API, CLI, etc.)
    """
    modality: InputModality
    content: Any
    metadata: Dict[str, Any]
    source: str = "unknown"


class MultiModalIntentProcessor:
    """Processes intent from multiple input modalities.
    
    Supports:
    - Natural language text analysis
    - Structured JSON/dict input
    - Command-line style operations
    - Code snippet analysis
    - Domain-specific schema interpretation
    
    Example:
        processor = MultiModalIntentProcessor()
        
        # Text input
        result1 = processor.process(
            ModalityInput(InputModality.TEXT, "Create a new module", {})
        )
        
        # JSON input
        result2 = processor.process(
            ModalityInput(InputModality.JSON, {
                "operation": "create",
                "target": "module",
                "domain": "orchestrators"
            }, {})
        )
    """
    
    def __init__(self) -> None:
        """Initialize multi-modal processor.
        
        Sets up:
        - Text classifier
        - Modality converters
        - Processing metrics
        """
        self.classifier = IntentClassifier()
        self.metrics: Dict[str, Any] = {
            "total_processed": 0,
            "by_modality": {},
            "conversion_failures": 0,
        }
    
    def process(self, input_data: ModalityInput) -> Dict[str, Any]:
        """Process intent from multi-modal input.
        
        Args:
            input_data: ModalityInput with content and metadata
            
        Returns:
            Dict with classification result
            
        Raises:
            ValueError: If input format is invalid
            RuntimeError: If processing fails
        """
        if not isinstance(input_data, ModalityInput):
            raise ValueError("Input must be ModalityInput instance")
        
        try:
            # Convert modality to text for classification
            text = self._convert_to_text(input_data)
            
            # Classify
            result = self.classifier.classify(text)
            
            # Update metrics
            self.metrics["total_processed"] += 1
            modality_key = input_data.modality.value
            self.metrics["by_modality"][modality_key] = \
                self.metrics["by_modality"].get(modality_key, 0) + 1
            
            return {
                "intent": result.primary_intent.value,
                "confidence": result.confidence_score,
                "signals": [s.value for s in result.detected_signals],
                "keywords": result.keywords,
                "modality": input_data.modality.value,
                "source": input_data.source,
            }
            
        except (ValueError, RuntimeError, TypeError) as e:
            self.metrics["conversion_failures"] += 1
            raise RuntimeError(f"Processing failed for {input_data.modality.value}: {e}") from e
    
    def _convert_to_text(self, input_data: ModalityInput) -> str:
        """Convert multi-modal input to text for classification.
        
        Args:
            input_data: ModalityInput to convert
            
        Returns:
            Text representation for classification
            
        Raises:
            ValueError: If conversion fails
        """
        if input_data.modality == InputModality.TEXT:
            return str(input_data.content)
        
        elif input_data.modality == InputModality.JSON:
            return self._json_to_text(input_data.content)
        
        elif input_data.modality == InputModality.COMMAND:
            return self._command_to_text(input_data.content)
        
        elif input_data.modality == InputModality.CODE:
            return self._code_to_text(input_data.content)
        
        elif input_data.modality == InputModality.SCHEMA:
            return self._schema_to_text(input_data.content)
        
        else:
            raise ValueError(f"Unknown modality: {input_data.modality}")
    
    def _json_to_text(self, json_data: Any) -> str:
        """Convert JSON to text representation.
        
        Args:
            json_data: JSON object or dict
            
        Returns:
            Text description
        """
        if isinstance(json_data, dict):
            operation = json_data.get("operation", "").title()
            target = json_data.get("target", "").title()
            domain = json_data.get("domain", "").title()
            
            parts = [operation, target, domain]
            text = " ".join([p for p in parts if p])
            return text if text else "perform operation"
        
        return str(json_data)
    
    def _command_to_text(self, command: str) -> str:
        """Convert command-line input to text.
        
        Args:
            command: Command string
            
        Returns:
            Text description
        """
        # Parse command-like input: "create --target module --domain orchestrators"
        parts = command.split()
        text_parts = []
        
        i = 0
        while i < len(parts):
            part = parts[i]
            if not part.startswith("--"):
                text_parts.append(part)
            i += 1
        
        return " ".join(text_parts) if text_parts else command
    
    def _code_to_text(self, code: str) -> str:
        """Extract intent from code snippet.
        
        Args:
            code: Code snippet
            
        Returns:
            Intent description
        """
        # Extract class/function names and intent keywords
        keywords = []
        
        if "def " in code:
            keywords.append("create function")
        if "class " in code:
            keywords.append("create class")
        if "import " in code:
            keywords.append("add import")
        if "raise " in code or "Error" in code:
            keywords.append("fix error")
        if "test" in code.lower():
            keywords.append("test")
        
        return " ".join(keywords) if keywords else code[:50]
    
    def _schema_to_text(self, schema: Any) -> str:
        """Interpret domain-specific schema.
        
        Args:
            schema: Schema object
            
        Returns:
            Intent description
        """
        if isinstance(schema, dict):
            schema_type = schema.get("type", "unknown")
            schema_action = schema.get("action", "process")
            return f"{schema_action} {schema_type}"
        
        return str(schema)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get processing metrics.
        
        Returns:
            Dict with processing statistics
        """
        return self.metrics.copy()
