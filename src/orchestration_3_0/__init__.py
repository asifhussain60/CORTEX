"""
CORTEX Orchestration 3.0 Architecture

This package contains the unified CORTEX 3.0 orchestration architecture,
consolidating 35 legacy orchestrators into 10 unified orchestrators.

Key Components:
- core: State machine, DI container, session manager
- orchestrators: 10 unified orchestrators
- multi_tenant: Multi-tenant infrastructure
- session: Session management
- workflows: YAML workflow definitions

Author: Asif Hussain
Version: 3.0.0
Date: December 10, 2025
"""

__version__ = "3.0.0"
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
