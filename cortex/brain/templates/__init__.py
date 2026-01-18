"""
PHASE-20: Template Content System

Provides template content population, management, and quality assurance.

Modules:
- content_strategy: Content population strategy and registry
- knowledge_schema: Knowledge base schema definitions
- template_manager: Template rendering and management
- template_validation: Template validation utilities
- content_generator: Content generation utilities
- quality_assurance: QA framework for templates

Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

from .content_strategy import ContentPopulationStrategy
from .knowledge_schema import KnowledgeBaseSchema
from .template_manager import TemplateManager
from .template_validation import TemplateContentValidator
from .content_generator import ContentGenerator
from .quality_assurance import QualityAssuranceFramework

__all__ = [
    'ContentPopulationStrategy',
    'KnowledgeBaseSchema',
    'TemplateManager',
    'TemplateContentValidator',
    'ContentGenerator',
    'QualityAssuranceFramework',
]
