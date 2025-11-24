"""
System-level optimization modules for CORTEX.

This package contains meta-level orchestrators that coordinate
multiple optimization operations across different system aspects.
"""

from .optimize_system_orchestrator import OptimizeSystemOrchestrator, register

__all__ = [
    'OptimizeSystemOrchestrator',
    'register'
]
