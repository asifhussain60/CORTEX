# Tutorial: Hello World Orchestrator

**Time:** 15 minutes | **Level:** Beginner  
**Goal:** Create and run your first CORTEX orchestrator

## Overview

In this tutorial, you'll create a simple "Hello World" orchestrator that demonstrates the basic orchestrator lifecycle: initialization, request handling, and response generation.

## Prerequisites

- CORTEX installed and running
- Basic Python knowledge
- [Quick Start](../../01-getting-started/1-quickstart.md) completed

## Step 1: Create Orchestrator File

Create `src/orchestrators/examples/hello_world.py`:

```python
from cortex.orchestrators.base import OrchestratorBase
from cortex.types import Intent, Response

class HelloWorldOrchestrator(OrchestratorBase):
    """Simple Hello World orchestrator."""
    
    async def process(self, intent: Intent) -> Response:
        """Process intent and return greeting."""
        return Response(
            status="success",
            content=f"Hello, {intent.user_id}! Welcome to CORTEX.",
            metadata={"orchestrator": "hello_world"}
        )
```

## Step 2: Register Orchestrator

Add to `cortex-config.yaml`:

```yaml
orchestrators:
  hello_world:
    module: src.orchestrators.examples.hello_world
    class: HelloWorldOrchestrator
    tier: tier1
```

## Step 3: Test It

```bash
cortex orchestrator execute --orchestrator hello_world --user alice
```

## Expected Output

```
Response:
  status: success
  content: Hello, alice! Welcome to CORTEX.
  metadata:
    orchestrator: hello_world
```

## Next Steps

- [Multi-step Workflow](2-multi-step-workflow.md) - Add state management
- [Error Handling](3-error-handling.md) - Robust error recovery
- [Building Your First Orchestrator](../../01-getting-started/2-first-orchestrator.md) - Full guide

## Troubleshooting

**Module not found:** Ensure PYTHONPATH includes the project root.

**Import errors:** Verify `cortex-config.yaml` has correct module paths.
