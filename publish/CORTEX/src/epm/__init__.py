"""
CORTEX EPM (Entry Point Module)

Extensible execution planning and guided workflows for CORTEX operations.
Includes administrative entry points like documentation generator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from .onboarding_step import OnboardingStep, StepStatus, StepResult
from .step_registry import StepRegistry
from .onboarding_orchestrator import OnboardingOrchestrator, OnboardingProfile

# Documentation Generator EPM
from .doc_generator import DocumentationGenerator

__all__ = [
    'OnboardingStep',
    'StepStatus',
    'StepResult',
    'StepRegistry',
    'OnboardingOrchestrator',
    'OnboardingProfile',
    'DocumentationGenerator'
]

__version__ = "1.0.0"
