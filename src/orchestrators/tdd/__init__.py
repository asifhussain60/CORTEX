"""
CORTEX 4.0 TDD Orchestrator Module

Unified TDD orchestrator with adaptive learning, clean architecture, and AI-driven capabilities.

Main Components:
- TDDOrchestratorV4: Main orchestrator coordinating RED→GREEN→REFACTOR
- TechnologyDiscoveryEngine: Auto-discover tech stacks and learn patterns
- CleanCodeEnforcer: Enforce SOLID, DRY, KISS, YAGNI principles
- Phase Strategies: RED, GREEN, REFACTOR

Version: 4.0.0
"""

from .tdd_orchestrator_v4 import (
    TDDOrchestratorV4,
    TechnologyDiscoveryEngine,
    CleanCodeEnforcer,
    TDDPhase,
    PhaseResult,
    ValidationResult,
    TechnologyProfile
)

__all__ = [
    'TDDOrchestratorV4',
    'TechnologyDiscoveryEngine',
    'CleanCodeEnforcer',
    'TDDPhase',
    'PhaseResult',
    'ValidationResult',
    'TechnologyProfile'
]

__version__ = '4.0.0'
__author__ = 'CORTEX Development Team'
