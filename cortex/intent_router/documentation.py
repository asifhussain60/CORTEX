"""Documentation Module - Framework documentation integration.

Author: CORTEX Framework
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class DocumentationEntry:
    """Documentation entry."""
    title: str
    content: str
    category: str = "general"
    tags: List[str] = field(default_factory=list)


class DocumentationManager:
    """Manages framework documentation."""
    
    def __init__(self):
        """Initialize documentation manager."""
        self.entries: Dict[str, DocumentationEntry] = {}
    
    def add_entry(self, key: str, entry: DocumentationEntry) -> None:
        """Add documentation entry.
        
        Args:
            key: Unique key for the entry
            entry: DocumentationEntry to add
        """
        self.entries[key] = entry
    
    def get_entry(self, key: str) -> Optional[DocumentationEntry]:
        """Get documentation entry.
        
        Args:
            key: Key of the entry to retrieve
            
        Returns:
            DocumentationEntry if found, None otherwise
        """
        return self.entries.get(key)
    
    def search(self, query: str) -> List[DocumentationEntry]:
        """Search documentation.
        
        Args:
            query: Search query string
            
        Returns:
            List of matching DocumentationEntry objects
        """
        return [
            entry for entry in self.entries.values()
            if query.lower() in entry.content.lower() or query.lower() in entry.title.lower()
        ]


def get_documentation() -> str:
    """Get framework documentation.
    
    Returns:
        String containing framework documentation
    """
    doc = """# Intent Router Framework Documentation

## Overview

The Intent Router Framework provides intelligent intent classification and routing
for user requests. It supports multiple input modalities and provides comprehensive
classification, disambiguation, and orchestration capabilities.

## Usage

```python
from cortex.intent_router.classifier import IntentClassifier

# Create classifier
classifier = IntentClassifier()

# Classify user intent
result = classifier.classify("Create a new authentication module")
print(f"Intent: {result.primary_intent}")
print(f"Confidence: {result.confidence_score}")
```

## Modules

- **classifier**: Multi-label intent classification with confidence scoring
- **disambiguator**: Disambiguation logic for ambiguous classifications
- **multimodal_processor**: Multi-modal input processing (text, JSON, commands, code, schemas)
- **routing_engine**: Intent routing to appropriate handlers
- **confidence_scorer**: Confidence score computation
- **context_manager**: Conversation context preservation
- **fallback_strategy**: Fallback chains for low-confidence classifications
- **intent_learner**: Learning from feedback to improve accuracy
- **performance_metrics**: Performance tracking and metrics
- **orchestration_integrator**: Integration with orchestrators

## Architecture

The framework follows a pipeline architecture:
1. Input processing (multimodal)
2. Intent classification
3. Disambiguation (if needed)
4. Routing to handlers
5. Orchestrator integration

## Features

- Multi-label classification
- Confidence scoring
- Context awareness
- Multiple input modalities
- Fallback strategies
- Performance metrics
- Learning from feedback
"""
    return doc


__all__ = ["DocumentationEntry", "DocumentationManager", "get_documentation"]
