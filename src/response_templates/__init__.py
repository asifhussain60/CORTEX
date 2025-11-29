"""Response Template System for CORTEX.

This module provides a unified template-based response system for:
- Instant, zero-execution responses (help, status, etc.)
- Consistent formatting across agents, operations, and plugins
- Verbosity control (concise/detailed/expert)
- Easy maintenance (edit YAML, not code)
- Confidence-aware responses (NEW in Lean 3.1)

Author: Asif Hussain
Version: 1.1
"""

from response_templates.template_loader import TemplateLoader, Template
from response_templates.template_renderer import TemplateRenderer
from response_templates.template_registry import TemplateRegistry
from response_templates.confidence_response_generator import ConfidenceResponseGenerator

__all__ = [
    "TemplateLoader",
    "Template",
    "TemplateRenderer",
    "TemplateRegistry",
    "ConfidenceResponseGenerator",
]
