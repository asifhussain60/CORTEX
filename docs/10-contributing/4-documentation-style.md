# Documentation Style Guide

**Status:** Production Ready | **Last Updated:** 2026-01-21

Guidelines for writing CORTEX documentation.

## Principles

- **Clear** - Use simple, direct language
- **Concise** - Avoid unnecessary words
- **Consistent** - Follow established patterns
- **Complete** - Provide necessary context
- **Current** - Keep documentation up-to-date

## Formatting

- Use markdown for all documentation
- Use code blocks for code examples
- Use tables for structured data
- Use headings hierarchically (H1 > H2 > H3)

## Code Examples

```python
# ✅ Good: Clear, runnable example
from cortex.orchestrators import OrchestratorBase

class MyOrchestrator(OrchestratorBase):
    async def process(self, intent):
        return {"status": "success"}

# ❌ Bad: Incomplete, unclear
def process():
    pass
```

## Links

- Use relative links within docs: `[Link Text](../path/to/file.md)`
- Use absolute URLs for external links: `[External](https://example.com)`

## Updates

Always update the "Last Updated" date when modifying documentation.

## Related Resources

- [Contributing Guidelines](1-contributing-guidelines.md)
- [Local Development](../04-guides/deployment/1-local-development.md)
