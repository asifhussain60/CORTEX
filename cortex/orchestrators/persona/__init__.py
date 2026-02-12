"""
Persona System Orchestrators for Role-Adaptive Response Generation

Provides intelligent user role detection, persona-based response formatting,
and cross-session persona persistence.

Authority: Phase 37 specification
"""

from .persona_loader import PersonaLoader

# from .persona_injector import PersonaInjector  # S2
# from .role_resolver import RoleResolver        # S2

__all__ = [
    "PersonaLoader",
    # "PersonaInjector",
    # "RoleResolver",
]
