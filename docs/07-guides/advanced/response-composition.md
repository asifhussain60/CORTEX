# Response Composition

**Status:** Production Ready | **Last Updated:** 2026-01-21

Response composition is the process of generating structured responses from orchestrator processing with specific modes and tones.

## Overview

CORTEX supports 6 response modes and 5 response tones for flexible output generation.

## Response Modes

### 1. Standard
Return structured data with metadata.

### 2. Detailed
Include comprehensive information and reasoning.

### 3. Summary
Condensed output with key points only.

### 4. Conversational
Natural language format suitable for chat interfaces.

### 5. Technical
Verbose technical output with debugging information.

### 6. Custom
User-defined response format.

## Response Tones

1. **Professional** - Formal, business-appropriate
2. **Friendly** - Approachable, conversational
3. **Technical** - Precise, developer-focused
4. **Creative** - Imaginative, engaging
5. **Neutral** - Objective, unbiased

## Implementation

```python
from enum import Enum

class ResponseMode(Enum):
    STANDARD = "standard"
    DETAILED = "detailed"
    SUMMARY = "summary"
    CONVERSATIONAL = "conversational"
    TECHNICAL = "technical"
    CUSTOM = "custom"

class ResponseTone(Enum):
    PROFESSIONAL = "professional"
    FRIENDLY = "friendly"
    TECHNICAL = "technical"
    CREATIVE = "creative"
    NEUTRAL = "neutral"

def compose_response(content, mode: ResponseMode, tone: ResponseTone) -> dict:
    """Compose response with specified mode and tone."""
    return {
        "content": content,
        "mode": mode.value,
        "tone": tone.value
    }
```

## Related Resources

- [Orchestration Engine](../../02-architecture/3-orchestration-engine.md)
- [Building Your First Orchestrator](../../01-getting-started/2-first-orchestrator.md)
