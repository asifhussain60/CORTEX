from __future__ import annotations

from typing import List


def resolve_fallback_chain(primary: str) -> List[str]:
    """Produce a fallback chain given a primary.
    Simple heuristic: if primary is openai -> anthropic -> local; if anthropic -> openai -> local; else -> openai -> local.
    """
    if primary == "openai":
        return ["anthropic", "local"]
    if primary == "anthropic":
        return ["openai", "local"]
    return ["openai", "local"]
