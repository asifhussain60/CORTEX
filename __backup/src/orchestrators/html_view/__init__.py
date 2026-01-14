"""HTML View Orchestrator - Init Module."""

# Validators can be imported independently (no heavy dependencies)
from .validators.html_validator import HTMLValidator, HTMLValidationResult

# Orchestrator imports are conditional (may have dependencies)
try:
    from .html_view_orchestrator import (
        HTMLViewOrchestrator,
        detect_html_view_command
    )
    __all__ = [
        'HTMLViewOrchestrator',
        'detect_html_view_command',
        'HTMLValidator',
        'HTMLValidationResult'
    ]
except ImportError:
    # If dependencies not available, only validators are accessible
    __all__ = ['HTMLValidator', 'HTMLValidationResult']
