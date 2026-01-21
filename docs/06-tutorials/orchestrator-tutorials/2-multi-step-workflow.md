# Tutorial: Multi-step Workflow Orchestrator

**Time:** 30 minutes | **Level:** Intermediate  
**Goal:** Build orchestrators with sequential processing and state management

## Overview

Multi-step workflows are common in enterprise systems. This tutorial shows how to implement orchestrators that process intents through multiple stages with state transitions.

## Prerequisites

- [Hello World](1-hello-world.md) tutorial completed
- Understanding of async/await patterns

## Architecture

```
User Intent
    ↓
Validate Input
    ↓
Process Step 1
    ↓
Process Step 2
    ↓
Generate Response
```

## Step 1: Define Workflow State

Create `src/orchestrators/examples/workflow_state.py`:

```python
from enum import Enum
from dataclasses import dataclass

class WorkflowStage(Enum):
    VALIDATION = "validation"
    PROCESSING = "processing"
    COMPLETION = "completion"

@dataclass
class WorkflowContext:
    stage: WorkflowStage
    data: dict
```

## Step 2: Implement Multi-step Orchestrator

```python
from cortex.orchestrators.base import OrchestratorBase
from cortex.types import Intent, Response

class MultiStepOrchestrator(OrchestratorBase):
    """Multi-step workflow orchestrator."""
    
    async def process(self, intent: Intent) -> Response:
        context = WorkflowContext(
            stage=WorkflowStage.VALIDATION,
            data={}
        )
        
        # Step 1: Validate
        if not self._validate(intent):
            return Response(status="error", content="Invalid input")
        
        context.stage = WorkflowStage.PROCESSING
        
        # Step 2: Process
        result = await self._process_step1(intent)
        context.data["step1_result"] = result
        
        result = await self._process_step2(intent, result)
        context.data["step2_result"] = result
        
        context.stage = WorkflowStage.COMPLETION
        
        return Response(
            status="success",
            content=f"Workflow completed: {context.data}",
            metadata={"stage": context.stage.value}
        )
    
    def _validate(self, intent: Intent) -> bool:
        return len(intent.content) > 0
    
    async def _process_step1(self, intent: Intent) -> dict:
        # Your business logic here
        return {"processed": True}
    
    async def _process_step2(self, intent: Intent, prev_result: dict) -> dict:
        # Your business logic here
        return {"completed": True}
```

## Step 3: Test Workflow

Register in `cortex-config.yaml` and execute:

```bash
cortex orchestrator execute --orchestrator multi_step --content "test data"
```

## Best Practices

1. **Keep stages isolated** - Each stage should be independently testable
2. **Use context objects** - Track state explicitly rather than with side effects
3. **Implement timeouts** - Prevent indefinite processing
4. **Log transitions** - Track workflow progression for debugging

## Error Recovery

Add resilience with retries:

```python
from cortex.resilience.retry import retry_on_exception

@retry_on_exception(max_attempts=3, backoff_factor=1.5)
async def _process_step1(self, intent: Intent) -> dict:
    # Might raise exceptions, will be retried
    return {"processed": True}
```

## Next Steps

- [Error Handling](3-error-handling.md) - Advanced error recovery
- [Knowledge Integration](4-knowledge-integration.md) - Access Domain Brain
