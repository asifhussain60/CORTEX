# src.llm.fallback_manager

## Functions

### `resolve_fallback_chain(primary)`

Produce a fallback chain given a primary.
Simple heuristic: if primary is openai -> anthropic -> local; if anthropic -> openai -> local; else -> openai -> local.
