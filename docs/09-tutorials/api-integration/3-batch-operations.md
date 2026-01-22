# Tutorial: Batch Operations

**Time:** 30 minutes | **Level:** Intermediate  
**Goal:** Process multiple items efficiently with batch APIs

## Overview

Batch operations allow processing multiple items in a single request, improving efficiency and reducing overhead. This tutorial covers batch processing patterns.

## Prerequisites

- [REST Client](1-rest-client.md) completed
- Understanding of async/await patterns

## Step 1: Basic Batch API

```python
import asyncio
from typing import List, Dict, Any

class BatchClient:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
    
    async def execute_batch(
        self,
        orchestrator: str,
        items: List[Dict[str, Any]],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """Execute multiple orchestrator calls."""
        tasks = [
            self.execute_single(orchestrator, item, user_id)
            for item in items
        ]
        return await asyncio.gather(*tasks)
    
    async def execute_single(
        self,
        orchestrator: str,
        item: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Execute single orchestrator call."""
        # Implementation with async requests
        return {
            "status": "success",
            "item_id": item.get("id")
        }
```

## Step 2: Batch with Chunking

```python
async def execute_batch_chunked(
    client: BatchClient,
    orchestrator: str,
    items: List[Dict[str, Any]],
    user_id: str,
    chunk_size: int = 10
) -> List[Dict[str, Any]]:
    """Execute batch in chunks."""
    results = []
    
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        chunk_results = await client.execute_batch(
            orchestrator,
            chunk,
            user_id
        )
        results.extend(chunk_results)
    
    return results

# Usage
items = [{"id": i, "content": f"item_{i}"} for i in range(1000)]
results = asyncio.run(
    execute_batch_chunked(
        client,
        "hello_world",
        items,
        "alice",
        chunk_size=50
    )
)
```

## Step 3: Batch with Error Handling

```python
from dataclasses import dataclass

@dataclass
class BatchResult:
    successful: List[Dict[str, Any]]
    failed: List[Dict[str, Any]]

async def execute_batch_safe(
    client: BatchClient,
    orchestrator: str,
    items: List[Dict[str, Any]],
    user_id: str,
    chunk_size: int = 10
) -> BatchResult:
    """Execute batch with error handling."""
    successful = []
    failed = []
    
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i + chunk_size]
        
        try:
            results = await client.execute_batch(
                orchestrator,
                chunk,
                user_id
            )
            
            for result in results:
                if result.get("status") == "success":
                    successful.append(result)
                else:
                    failed.append(result)
        
        except Exception as e:
            # Mark all items in chunk as failed
            for item in chunk:
                failed.append({
                    "id": item.get("id"),
                    "error": str(e)
                })
    
    return BatchResult(
        successful=successful,
        failed=failed
    )
```

## Step 4: Progress Tracking

```python
from typing import Callable

async def execute_batch_with_progress(
    client: BatchClient,
    orchestrator: str,
    items: List[Dict[str, Any]],
    user_id: str,
    chunk_size: int = 10,
    on_progress: Callable[[int, int], None] = None
) -> List[Dict[str, Any]]:
    """Execute batch with progress tracking."""
    results = []
    total = len(items)
    
    for i in range(0, total, chunk_size):
        chunk = items[i:i + chunk_size]
        chunk_results = await client.execute_batch(
            orchestrator,
            chunk,
            user_id
        )
        results.extend(chunk_results)
        
        # Call progress callback
        if on_progress:
            on_progress(min(i + chunk_size, total), total)
    
    return results

# Usage with progress callback
def show_progress(current: int, total: int):
    percent = (current / total) * 100
    print(f"Progress: {current}/{total} ({percent:.1f}%)")

results = asyncio.run(
    execute_batch_with_progress(
        client,
        "hello_world",
        items,
        "alice",
        chunk_size=50,
        on_progress=show_progress
    )
)
```

## Step 5: Result Aggregation

```python
def aggregate_results(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Aggregate batch results."""
    total = len(results)
    successful = sum(1 for r in results if r.get("status") == "success")
    failed = total - successful
    
    return {
        "total": total,
        "successful": successful,
        "failed": failed,
        "success_rate": (successful / total * 100) if total > 0 else 0,
        "results": results
    }

# Usage
aggregated = aggregate_results(results)
print(f"Success rate: {aggregated['success_rate']:.1f}%")
```

## Best Practices

1. **Chunk wisely** - Balance batch size with memory usage
2. **Handle failures** - Don't fail entire batch on single error
3. **Track progress** - Provide feedback for long operations
4. **Aggregate results** - Summarize outcomes meaningfully
5. **Retry failed items** - Implement intelligent retry logic

## Performance Tips

- Use async/await for concurrent requests
- Adjust chunk size based on item size and latency
- Implement backoff for rate limiting
- Monitor memory usage for large batches

## Next Steps

- [REST API Reference](../../03-api-reference/rest-api/0-guide.md) - Full API docs
- [Operations Tutorials](../operations/0-index.md) - Advanced operations
