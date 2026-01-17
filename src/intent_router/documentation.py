"""AC-PHX-007-12: Documentation Updates"""

DOCUMENTATION = """
# Intent Router Documentation

## Overview
The Intent Router analyzes natural language and structured input to classify
operation intents into standardized categories:
- CREATE: New feature development
- MODIFY: Existing code changes
- FIX: Bug fixes
- ANALYZE: Code analysis
- OPTIMIZE: Performance improvement
- REFACTOR: Code restructuring
- TEST: Testing operations
- DOCUMENT: Documentation updates

## Modules
- classifier.py: Core classification engine
- multimodal_processor.py: Multi-input modality support
- disambiguator.py: Ambiguity resolution
- confidence_scorer.py: Confidence quantification
- context_manager.py: Conversation context
- routing_engine.py: Intent routing
- fallback_strategy.py: Fallback handling
- intent_learner.py: Learning loop
- performance_metrics.py: Metrics tracking
- orchestration_integrator.py: PHASE-06 integration

## Usage
```python
from src.intent_router.classifier import IntentClassifier

classifier = IntentClassifier()
result = classifier.classify("Create a new authentication module")
print(f"Intent: {result.primary_intent.value}")
print(f"Confidence: {result.confidence_score:.0%}")
```

## API Reference
See individual module docstrings for detailed API documentation.
All modules follow CORTEX governance rules (CORE-008 through CORE-027).
"""

def get_documentation() -> str:
    """Get intent router documentation."""
    return DOCUMENTATION
