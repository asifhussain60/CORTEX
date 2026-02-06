"""
Coordination Module - Stage routing & orchestrator selection

This module handles:
- Pipeline stage execution
- Orchestrator selection based on intent
- Fallback handling
- Stage transitions
"""

from .coordinator import Coordinator

__all__ = ["Coordinator"]
