"""tier_composer.py — Tier Composer stub."""
from __future__ import annotations
from typing import Any


class TierComposer:
    """Composes orchestrator tiers for routing resolution."""

    def compose_tiers(self) -> dict[str, list[str]]:
        """Compose the orchestrator tier map.

        Returns:
            Dict mapping tier names to lists of orchestrator names.
        """
        return {"core": [], "domain": [], "support": []}
