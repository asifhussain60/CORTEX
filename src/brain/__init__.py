"""
CORTEX 4.0 Brain - Unified Intelligence Layer

Provides unified access to all brain tiers:
- Tier 0: Governance (SKULL rules)
- Tier 1: Working Memory (conversation history)
- Tier 2: Knowledge Graph (pattern learning)
- Tier 3: Development Context (git metrics, repo context)

Usage:
    from src.brain import BrainInterface
    
    brain = BrainInterface(workspace_root)
    brain.tier1.store_conversation(...)
    brain.tier2.store_pattern(...)
    brain.tier3.get_git_metrics(...)

Architecture:
    - Hybrid centralization (shared + per-repo)
    - SQLite storage (lightweight, zero infrastructure)
    - IDE-aware (Visual Studio + VSCode)
    - Namespace isolation for multi-project learning

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Optional
import logging

from .interface import BrainInterface
from .tier0.governance import GovernanceEngine
from .tier1.working_memory import WorkingMemory
from .tier2.knowledge_graph import KnowledgeGraph
from .tier3.dev_context import DevelopmentContext


__all__ = [
    "BrainInterface",
    "GovernanceEngine",
    "WorkingMemory",
    "KnowledgeGraph",
    "DevelopmentContext",
]


__version__ = "4.0.0"


def create_brain(workspace_root: Path, config: Optional[dict] = None) -> BrainInterface:
    """
    Factory function to create brain interface.
    
    Args:
        workspace_root: Root directory of the workspace
        config: Optional configuration overrides
        
    Returns:
        Configured BrainInterface instance
    """
    return BrainInterface(workspace_root, config)
