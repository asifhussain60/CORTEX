"""
Strategic Agents Package

Contains agents responsible for strategic planning and routing:
- IntentRouter: Determines user intent and routes to appropriate workflow
- WorkPlanner: Creates multi-phase strategic plans
- ChangeGovernor: Protects system integrity
"""

from .intent_router import IntentRouter

__all__ = ['IntentRouter']
