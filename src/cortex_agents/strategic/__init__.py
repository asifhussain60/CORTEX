"""
Strategic Agents Package

Contains agents responsible for strategic planning, architectural analysis, and routing:
- IntentRouter: Determines user intent and routes to appropriate workflow
- ArchitectAgent: Deep architectural analysis with automatic brain saving (CORTEX-BRAIN-001 fix)
- WorkPlanner: Creates multi-phase strategic plans
- ChangeGovernor: Protects system integrity

Key CORTEX-BRAIN-001 Fix:
- ArchitectAgent automatically saves architectural analysis to Tier 2 Knowledge Graph
- Namespace detection (e.g., ksessions_architecture, ksessions_features.etymology)
- User confirmation of brain saves to build confidence in memory system
"""

from .intent_router import IntentRouter
from .architect import ArchitectAgent

__all__ = ['IntentRouter', 'ArchitectAgent']
