"""Response Template System for CORTEX.

This module provides a unified template-based response system for:
- Instant, zero-execution responses (help, status, etc.)
- Consistent formatting across agents, operations, and plugins
- Verbosity control (concise/detailed/expert)
- Easy maintenance (edit YAML, not code)

Author: Asif Hussain
Version: 1.0
"""

from .template_loader import TemplateLoader, Template
from .template_renderer import TemplateRenderer
from .template_registry import TemplateRegistry

__all__ = [
    "TemplateLoader",
    "Template",
    "TemplateRenderer",
    "TemplateRegistry",
]
