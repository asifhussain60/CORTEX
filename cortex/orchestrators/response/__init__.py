"""cortex.orchestrators.response — Response rendering utilities.

Exports the canonical EngagementRenderer for breadcrumb/timeline/stage-pulse
rendering across all orchestrators.

SSOT: .github/templates/cortex-response-templates.md §BLOCK-ENGAGEMENT-*
Phase 85 / chat01.md (2026-03-01) — three-tier engagement system.
"""
from __future__ import annotations

from cortex.orchestrators.response.engagement_renderer import EngagementRenderer

__all__ = ["EngagementRenderer"]
