"""
CORTEX Templates Module

Content population strategy, Jinja2 rendering tools, schema validation,
quality assurance, and template builder/resolver utilities.

"""

from cortex.templates.content_strategy import (
    ContentPopulationStrategy,
    ContentSource,
    TemplateMetadata,
)
from cortex.templates.template_builder import TemplateBuilder
from cortex.templates.template_renderer import TemplateRenderer
from cortex.templates.dashboard_renderer import DashboardTemplateRenderer
from cortex.templates.template_resolver import TemplateResolver
from cortex.templates.template_validator import TemplateValidator
from cortex.templates.template_validation import TemplateContentValidator
from cortex.templates.content_generator import ContentGenerator
from cortex.templates.quality_assurance import QualityAssuranceFramework
from cortex.templates.knowledge_schema import KnowledgeBaseSchema

__all__ = [
    # Content strategy (core registry)
    "ContentPopulationStrategy",
    "TemplateMetadata",
    "ContentSource",
    # Jinja2 rendering & construction
    "TemplateBuilder",
    "TemplateRenderer",
    "DashboardTemplateRenderer",
    "TemplateResolver",
    # Validation
    "TemplateValidator",
    "TemplateContentValidator",
    # Generation & QA
    "ContentGenerator",
    "QualityAssuranceFramework",
    "KnowledgeBaseSchema",
]
