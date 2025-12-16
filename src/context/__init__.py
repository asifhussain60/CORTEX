"""
CORTEX Context Injection System

Provides universal workspace context resolution with graceful degradation:
1. Explicit parameters (highest priority)
2. GitHub Copilot context (when available)
3. Environment variables
4. Config file
5. Path.cwd() fallback (with warning)
"""

from .workspace_context import WorkspaceContext
from .context_resolver import resolve_context, ContextResolver
from .copilot_integration import CopilotIntegration

__all__ = [
    'WorkspaceContext',
    'resolve_context',
    'ContextResolver',
    'CopilotIntegration',
]
