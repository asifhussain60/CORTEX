# Tutorial: Knowledge Integration with Domain Brain

**Time:** 45 minutes | **Level:** Advanced  
**Goal:** Integrate Domain Brain knowledge retrieval and decision making

## Overview

The Domain Brain is CORTEX's knowledge management system. This tutorial shows how to query knowledge, make decisions based on retrieved data, and handle knowledge conflicts.

## Prerequisites

- [Error Handling](3-error-handling.md) completed
- Familiarity with CORTEX architecture
- [Domain Brain Architecture](../../02-architecture/4-domain-brain.md) reviewed

## Step 1: Access Domain Brain

```python
from cortex.orchestrators.base import OrchestratorBase
from cortex.domain_brain.client import DomainBrainClient
from cortex.types import Intent, Response

class KnowledgeOrchestrator(OrchestratorBase):
    def __init__(self):
        super().__init__()
        self.knowledge = DomainBrainClient()
    
    async def process(self, intent: Intent) -> Response:
        # Query knowledge
        knowledge = await self.knowledge.query(
            domain=intent.domain,
            concept=intent.concept,
            tier=self.tier
        )
        
        return Response(
            status="success",
            content=f"Found knowledge: {knowledge}",
            metadata={"knowledge_id": knowledge.id}
        )
```

## Step 2: Decision Making with Knowledge

```python
class DecisionOrchestrator(OrchestratorBase):
    async def process(self, intent: Intent) -> Response:
        # Retrieve relevant knowledge
        knowledge = await self.knowledge.query(
            domain=intent.domain,
            concept=intent.concept,
            tier=self.tier
        )
        
        if not knowledge:
            return self._handle_no_knowledge(intent)
        
        # Make decision based on knowledge
        decision = self._make_decision(intent, knowledge)
        
        return Response(
            status="success",
            content=f"Decision: {decision}",
            metadata={
                "knowledge_id": knowledge.id,
                "confidence": decision.confidence
            }
        )
    
    def _make_decision(self, intent: Intent, knowledge):
        # Your business logic
        return {
            "action": "proceed",
            "confidence": 0.95
        }
```

## Step 3: Handling Knowledge Conflicts

```python
class ConflictResolvingOrchestrator(OrchestratorBase):
    async def process(self, intent: Intent) -> Response:
        # Query with multiple sources
        tier0_knowledge = await self.knowledge.query(
            domain=intent.domain,
            tier="tier0"
        )
        
        tier1_knowledge = await self.knowledge.query(
            domain=intent.domain,
            tier="tier1"
        )
        
        # Resolve conflicts using tier precedence
        resolved = self._resolve_conflicts(
            tier0_knowledge,
            tier1_knowledge
        )
        
        return Response(
            status="success",
            content=f"Resolved knowledge: {resolved}",
            metadata={"resolver": "tier_precedence"}
        )
    
    def _resolve_conflicts(self, tier0, tier1):
        # Tier0 takes precedence
        return tier0 if tier0 else tier1
```

## Step 4: Knowledge Caching

```python
from functools import lru_cache

class CachedKnowledgeOrchestrator(OrchestratorBase):
    @lru_cache(maxsize=1000)
    async def _get_knowledge(self, domain: str, concept: str):
        return await self.knowledge.query(
            domain=domain,
            concept=concept,
            tier=self.tier
        )
    
    async def process(self, intent: Intent) -> Response:
        # Cached query
        knowledge = await self._get_knowledge(
            intent.domain,
            intent.concept
        )
        return Response(status="success", content=f"Knowledge: {knowledge}")
```

## Best Practices

1. **Always check tier precedence** - Tier0 > Tier1 > Tier2
2. **Cache when appropriate** - Avoid repeated queries
3. **Handle missing knowledge** - Provide graceful degradation
4. **Log knowledge queries** - Track usage for insights
5. **Version knowledge** - Use versioning for consistency

## Testing Knowledge Integration

```python
import pytest
from unittest.mock import AsyncMock

@pytest.mark.asyncio
async def test_knowledge_query():
    orchestrator = KnowledgeOrchestrator()
    orchestrator.knowledge.query = AsyncMock(return_value={
        "id": "k1",
        "data": "test"
    })
    
    intent = Intent(
        content="test",
        domain="payments",
        concept="rule_approval",
        user_id="user1"
    )
    
    response = await orchestrator.process(intent)
    assert response.status == "success"
```

## Next Steps

- [Complex Domain](5-complex-domain.md) - Enterprise integration
- [Domain Brain Architecture](../../02-architecture/4-domain-brain.md) - Deep dive
