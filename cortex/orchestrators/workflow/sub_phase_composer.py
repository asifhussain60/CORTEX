"""SubPhaseComposer — Phase 142 DRY Refactor.

Resolves the intent→template mapping for sub-phase execution by deriving from
WorkflowGateway as the single source of truth (SSOT).

DRY design:
  - WorkflowGateway._MODE_TEMPLATE_MAP is canonical (exposed via get_mode_template_map())
  - SubPhaseComposer.INTENT_TEMPLATE_MAP is derived at module load and never hard-coded
  - Extension dict _SUBPHASE_OVERRIDES provides SubPhaseComposer-only additions without
    duplicating the shared core entries

Phase: 142 | Priority: P1 | CORE-035 compliance
Source: GitHub Issue #17 — FB-2026-03-09-074435-004
AC_START: AC-P142-SPC-001
AC_COMPLETE: AC-P142-SPC-001 ✅
"""

from __future__ import annotations

import logging
from typing import Dict, Optional

from cortex.orchestrators.workflow.workflow_gateway import WorkflowGateway

logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────────────────────────────────────
# SubPhaseComposer-only additions (extension point).
# Add here ONLY entries that do not belong in WorkflowGateway._MODE_TEMPLATE_MAP.
# Never re-declare entries already in WorkflowGateway — that would violate CORE-035.
# ─────────────────────────────────────────────────────────────────────────────
_SUBPHASE_OVERRIDES: Dict[str, Optional[str]] = {
    # Example: CAPE sub-phase types that have their own template but aren't
    # top-level WorkflowGateway modes.
    # "CAPE_PLAN": "cape/plan-sub-phase",  # add when needed
}


def _build_intent_template_map() -> Dict[str, str]:
    """Build the intent→template map from WorkflowGateway SSOT + SubPhase overrides.

    Steps:
      1. Fetch the canonical map from WorkflowGateway
      2. Filter out None-mapped entries (non-code-touching modes have no template)
      3. Merge SubPhaseComposer-only overrides (non-destructive — overrides win)

    Returns:
        Dict mapping mode strings to non-null template ID strings.
    """
    base: Dict[str, Optional[str]] = WorkflowGateway.get_mode_template_map()
    # Only keep entries that have a concrete template
    result: Dict[str, str] = {
        mode: template
        for mode, template in base.items()
        if template is not None
    }
    # Apply SubPhaseComposer-specific additions
    for mode, template in _SUBPHASE_OVERRIDES.items():
        if template is not None:
            result[mode] = template
    return result


# Module-level constant — derived from WorkflowGateway SSOT at import time.
# Never mutate this dict; use get_template_for_mode() for safe reads.
INTENT_TEMPLATE_MAP: Dict[str, str] = _build_intent_template_map()


class SubPhaseComposer:
    """Resolves the workflow template for a given intent/mode.

    Uses WorkflowGateway as the single source of truth for intent→template
    mappings, avoiding any duplicated hardcoded dictionary.

    Usage::

        composer = SubPhaseComposer()
        template_id = composer.get_template_for_mode("IMPLEMENT")
        # → "sdlc/implement-workflow"
    """

    #: Canonical intent→template mapping derived from WorkflowGateway (SSOT).
    INTENT_TEMPLATE_MAP: Dict[str, str] = INTENT_TEMPLATE_MAP

    def get_template_for_mode(self, mode: str) -> Optional[str]:
        """Return the workflow template ID for the given mode, or None if not found.

        Args:
            mode: Operation mode string, case-insensitive (e.g. "IMPLEMENT", "fix").

        Returns:
            Template ID string, or None if the mode is not in the map.

        Example::

            composer = SubPhaseComposer()
            assert composer.get_template_for_mode("FIX") == "sdlc/fix-workflow"
            assert composer.get_template_for_mode("unknown") is None
        """
        return self.INTENT_TEMPLATE_MAP.get(mode.upper())
