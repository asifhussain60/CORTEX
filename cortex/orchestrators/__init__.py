"""
CORTEX Orchestrators Module

Docker-First Architecture (Phase 2+ Migration):
- core/: Framework orchestrators (master, interaction, intent, tdd)
- domain/: Business domain orchestrators (refactoring, planning, documentation)
- support/: Support orchestrators (onboarding, tool discovery, upgrade)

WIRING: Git-backed YAML (cortex/wiring/specifications/wiring.yaml)
- No database registries
- No SQLite wiring state
- Ephemeral container state only

See: cortex-registry/_cortex-master/phases/completed/2025/ (migration plan)
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class OrchestratorCategory(Enum):
    """Orchestrator category enumeration."""
    CORE = "core"
    DOMAIN = "domain"
    SUPPORT = "support"


@dataclass
class OrchestratorConfig:
    """Orchestrator configuration from YAML wiring."""
    name: str
    module: str
    class_name: str
    category: OrchestratorCategory
    tier: int = 1
    priority: int = 50
    dependencies: List[str] = None
    capabilities: List[str] = None

    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.capabilities is None:
            self.capabilities = []


# Orchestrator counts (from wiring.yaml specification)
# WAVE-7 TRACK-3: Support layer consolidation in progress
# Before: 26 orchestrators (8 core + 6 domain + 12 support)
# After: 15 orchestrators (8 core + 4 domain + 3-4 support)
CORE_ORCHESTRATORS = 8
DOMAIN_ORCHESTRATORS = 4
SUPPORT_ORCHESTRATORS = 4  # Unified: Onboarding, Analysis, Quality, Discovery
ALL_ORCHESTRATORS = CORE_ORCHESTRATORS + DOMAIN_ORCHESTRATORS + SUPPORT_ORCHESTRATORS


def get_orchestrator_count_by_category() -> Dict[str, int]:
    """Get orchestrator counts by category.

    Returns:
        Dictionary with counts per category.
    """
    return {
        "core": CORE_ORCHESTRATORS,
        "domain": DOMAIN_ORCHESTRATORS,
        "support": SUPPORT_ORCHESTRATORS,
        "total": ALL_ORCHESTRATORS,
    }


__all__ = [
    # Configuration
    "OrchestratorConfig",
    "OrchestratorCategory",
    # Constants
    "ALL_ORCHESTRATORS",
    "CORE_ORCHESTRATORS",
    "DOMAIN_ORCHESTRATORS",
    "SUPPORT_ORCHESTRATORS",
    # Functions
    "get_orchestrator_count_by_category",
]
