"""
CORTEX Orchestration 3.0 → 4.0 Architecture

This package contains the unified CORTEX 4.0 orchestration architecture,
consolidating 71 legacy orchestrators into 9 domain-driven orchestrators.

Key Components:
- core: State machine, DI container, session manager
- orchestrators: 9 unified orchestrators
- multi_tenant: Multi-tenant infrastructure
- session: Session management
- workflows: YAML workflow definitions

Author: Asif Hussain
Version: 4.0.0
Date: December 10, 2025
"""

__version__ = "4.0.0"
__author__ = "Asif Hussain"

from .core.base_orchestrator import BaseOrchestrator
from .core.state_machine import StateMachine
from .core.dependency_container import DependencyContainer
from .session.session_manager import SessionManager

__all__ = [
    "BaseOrchestrator",
    "StateMachine",
    "DependencyContainer",
    "SessionManager",
]
