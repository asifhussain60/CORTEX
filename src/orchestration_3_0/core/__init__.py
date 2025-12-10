"""
Core orchestration infrastructure.

Contains shared components for all orchestrators:
- State Machine: FSM-based workflow execution
- Dependency Container: Auto-wiring and service injection
- Session Manager: State persistence and recovery
- Base Orchestrator: Abstract base class for all orchestrators
"""

__all__ = [
    "BaseOrchestrator",
    "StateMachine",
    "DependencyContainer",
    "SessionManager",
]
