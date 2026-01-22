# Tutorial: Complex Domain Orchestrator

**Time:** 60 minutes | **Level:** Advanced  
**Goal:** Build enterprise-grade orchestrators with full governance integration

## Overview

Complex domain orchestrators handle sophisticated business logic with governance integration, knowledge management, error handling, and observability. This is a capstone tutorial.

## Prerequisites

- All previous tutorials completed
- [Building Your First Orchestrator](../../01-getting-started/2-first-orchestrator.md)
- [Governance Framework](../../02-architecture/governance-rules.md)

## Architecture

```
┌─────────────────────────────────────────┐
│     User Intent (e.g., approval)        │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│      Governance Tier Check (LENS)       │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│    Retrieve Domain Knowledge            │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│    Execute Business Logic               │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│    Apply Governance Rules               │
└──────────────┬──────────────────────────┘
               ↓
┌─────────────────────────────────────────┐
│    Return Response + Audit Trail        │
└─────────────────────────────────────────┘
```

## Implementation

### 1. Define Complex Orchestrator

```python
from cortex.orchestrators.base import OrchestratorBase
from cortex.types import Intent, Response, AuditTrail
from cortex.domain_brain.client import DomainBrainClient
from cortex.governance.rules import GovernanceEngine
from datetime import datetime

class ComplexDomainOrchestrator(OrchestratorBase):
    """Enterprise-grade orchestrator for complex domain."""
    
    def __init__(self, domain: str):
        super().__init__()
        self.domain = domain
        self.knowledge = DomainBrainClient()
        self.governance = GovernanceEngine()
        self.audit_trail = AuditTrail()
    
    async def process(self, intent: Intent) -> Response:
        # Step 1: Log intent
        self.audit_trail.log("INTENT_RECEIVED", {
            "domain": self.domain,
            "user": intent.user_id,
            "timestamp": datetime.utcnow()
        })
        
        # Step 2: Governance check
        governance_result = await self._check_governance(intent)
        if not governance_result.allowed:
            self.audit_trail.log("GOVERNANCE_DENIED", {
                "reason": governance_result.reason
            })
            return Response(
                status="denied",
                content=governance_result.reason,
                metadata={"audit_trail": self.audit_trail.entries}
            )
        
        # Step 3: Retrieve knowledge
        knowledge = await self._get_knowledge(intent)
        if not knowledge:
            return self._handle_no_knowledge(intent)
        
        # Step 4: Business logic
        result = await self._execute_logic(intent, knowledge)
        
        # Step 5: Apply rules
        final_result = await self._apply_rules(intent, result)
        
        # Step 6: Return response with audit trail
        self.audit_trail.log("RESPONSE_GENERATED", {
            "status": "success",
            "timestamp": datetime.utcnow()
        })
        
        return Response(
            status="success",
            content=final_result,
            metadata={
                "knowledge_id": knowledge.id,
                "audit_trail": self.audit_trail.entries,
                "tier": self.tier
            }
        )
    
    async def _check_governance(self, intent: Intent):
        """Check governance constraints."""
        return await self.governance.check(
            tier=self.tier,
            action=intent.action,
            domain=self.domain,
            user=intent.user_id
        )
    
    async def _get_knowledge(self, intent: Intent):
        """Query Domain Brain."""
        return await self.knowledge.query(
            domain=self.domain,
            concept=intent.concept,
            tier=self.tier
        )
    
    async def _execute_logic(self, intent: Intent, knowledge):
        """Your complex business logic."""
        return {
            "processed": True,
            "knowledge_applied": True
        }
    
    async def _apply_rules(self, intent: Intent, result: dict):
        """Apply domain rules."""
        rules = await self.governance.get_rules(
            domain=self.domain,
            tier=self.tier
        )
        
        for rule in rules:
            if rule.applies_to(result):
                result = rule.transform(result)
        
        return result
    
    def _handle_no_knowledge(self, intent: Intent) -> Response:
        """Graceful degradation."""
        self.audit_trail.log("NO_KNOWLEDGE_FOUND", {})
        return Response(
            status="degraded",
            content="Operating in degraded mode",
            metadata={"audit_trail": self.audit_trail.entries}
        )
```

### 2. Error Handling and Resilience

```python
from cortex.resilience.circuit_breaker import CircuitBreaker
from cortex.resilience.retry import retry_async

class ResilientComplexOrchestrator(ComplexDomainOrchestrator):
    def __init__(self, domain: str):
        super().__init__(domain)
        self.circuit_breaker = CircuitBreaker()
    
    @retry_async(max_attempts=3, backoff_factor=2)
    async def _get_knowledge(self, intent: Intent):
        """Retryable knowledge query."""
        return await self.circuit_breaker.call(
            self.knowledge.query,
            domain=self.domain,
            concept=intent.concept,
            tier=self.tier
        )
    
    async def _execute_logic(self, intent: Intent, knowledge):
        """Protected business logic."""
        try:
            return await super()._execute_logic(intent, knowledge)
        except Exception as e:
            self.audit_trail.log("ERROR", {
                "error_type": type(e).__name__,
                "message": str(e)
            })
            raise
```

### 3. Observability and Monitoring

```python
from cortex.observability.metrics import MetricsCollector

class ObservableComplexOrchestrator(ResilientComplexOrchestrator):
    def __init__(self, domain: str):
        super().__init__(domain)
        self.metrics = MetricsCollector()
    
    async def process(self, intent: Intent) -> Response:
        start_time = datetime.utcnow()
        
        try:
            response = await super().process(intent)
            
            # Record metrics
            duration = (datetime.utcnow() - start_time).total_seconds()
            self.metrics.record_duration(
                orchestrator=self.__class__.__name__,
                domain=self.domain,
                status=response.status,
                duration=duration
            )
            
            return response
        except Exception as e:
            self.metrics.record_error(
                orchestrator=self.__class__.__name__,
                domain=self.domain,
                error_type=type(e).__name__
            )
            raise
```

## Integration in Production

```yaml
# cortex-config.yaml
orchestrators:
  payment_approval:
    module: src.orchestrators.domains.payment
    class: PaymentApprovalOrchestrator
    domain: payments
    tier: tier0
    config:
      circuit_breaker_threshold: 5
      circuit_breaker_timeout: 60
      retry_max_attempts: 3
      cache_ttl: 300
```

## Best Practices

1. **Audit everything** - Track all decisions for compliance
2. **Implement governance** - Enforce policies at every step
3. **Cache intelligently** - Balance freshness and performance
4. **Monitor actively** - Track metrics and errors
5. **Test thoroughly** - Cover happy and sad paths
6. **Document decisions** - Record reasoning in metadata

## Testing

```python
import pytest
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_complex_orchestrator_full_flow():
    orchestrator = ComplexDomainOrchestrator("payments")
    orchestrator.governance.check = AsyncMock(return_value={
        "allowed": True
    })
    orchestrator.knowledge.query = AsyncMock(return_value={
        "id": "k1",
        "rules": []
    })
    
    intent = Intent(
        content="approve",
        domain="payments",
        concept="approval",
        user_id="user1",
        action="approve"
    )
    
    response = await orchestrator.process(intent)
    
    assert response.status == "success"
    assert len(response.metadata["audit_trail"]) > 0
```

## Related Resources

- [Building Your First Orchestrator](../../01-getting-started/2-first-orchestrator.md)
- [Governance Framework](../../02-architecture/governance-rules.md)
- [Orchestration Engine](../../02-architecture/3-orchestration-engine.md)
- [Domain Brain](../../02-architecture/4-domain-brain.md)
