"""
Response Templates v4.0 - Adaptive Minimalism

Exports:
    TemplateManager: Main template orchestration
    ResponseTier: Enum for tier selection
    get_template_manager: Singleton factory
"""

from src.templates.types import ResponseTier, TemplateContext
from src.templates.template_manager import TemplateManager
from src.templates.tier_selector import TierSelector
from src.templates.section_selector import SectionSelector
from src.templates.template_renderer import TemplateRenderer

__all__ = [
    "TemplateManager",
    "ResponseTier",
    "TemplateContext",
    "TierSelector",
    "SectionSelector",
    "TemplateRenderer",
    "get_template_manager",
]

_template_manager_instance = None


def get_template_manager() -> TemplateManager:
    """
    Get or create the singleton TemplateManager instance.
    
    Returns:
        TemplateManager: The singleton template manager
    """
    global _template_manager_instance
    if _template_manager_instance is None:
        _template_manager_instance = TemplateManager()
    return _template_manager_instance
