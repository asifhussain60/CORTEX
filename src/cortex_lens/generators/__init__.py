"""
Dashboard generation and packaging.

Generators:
- NarrativeGenerator: AST-to-Narrative business summaries
- DashboardBuilder: Template-based dashboard construction
- DataInjector: JSON data injection into templates
- Packager: Distribution ZIP creation
- DashboardRenderer: HTML dashboard generation (Phase 4)
- ExportManager: Multi-format export (JSON, MD, CSV, ZIP) (Phase 4)
"""

from .base import BaseGenerator
from .dashboard_renderer import DashboardRenderer
from .export_manager import ExportManager

__all__ = [
    'BaseGenerator',
    'DashboardRenderer',
    'ExportManager',
]
