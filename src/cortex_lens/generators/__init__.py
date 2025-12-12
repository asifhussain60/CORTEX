"""
Dashboard generation and packaging.

Generators:
- NarrativeGenerator: AST-to-Narrative business summaries
- DashboardBuilder: Template-based dashboard construction
- DataInjector: JSON data injection into templates
- Packager: Distribution ZIP creation
"""

from .base import BaseGenerator

__all__ = [
    'BaseGenerator',
]
