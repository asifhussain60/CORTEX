"""
CORTEX 3.0 Track B: Template System Package
===========================================

Complete template system for zero-execution help responses and dynamic content generation.
Integrates template engine, response generator, and template optimizer for intelligent,
context-aware responses without requiring code execution.

Key Components:
- TemplateEngine: Advanced template management and rendering
- ResponseGenerator: Intelligent response generation with context analysis
- TemplateOptimizer: Performance analysis and optimization recommendations

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from .template_engine import (
    TemplateEngine,
    Template,
    TemplateVariable,
    TemplateContext,
    RenderedTemplate,
    TemplateType,
    TemplateFormat
)

from .response_generator import (
    ResponseGenerator,
    ResponseContext,
    GeneratedResponse,
    ResponseType,
    ResponsePriority
)

from .template_optimizer import (
    TemplateOptimizer,
    OptimizationStrategy,
    TemplatePerformanceMetrics,
    UsagePattern,
    OptimizationRecommendation
)

__all__ = [
    # Template Engine
    "TemplateEngine",
    "Template",
    "TemplateVariable", 
    "TemplateContext",
    "RenderedTemplate",
    "TemplateType",
    "TemplateFormat",
    
    # Response Generator
    "ResponseGenerator",
    "ResponseContext",
    "GeneratedResponse",
    "ResponseType",
    "ResponsePriority",
    
    # Template Optimizer
    "TemplateOptimizer",
    "OptimizationStrategy",
    "TemplatePerformanceMetrics",
    "UsagePattern",
    "OptimizationRecommendation"
]

# Package metadata
__version__ = "3.0.0"
__author__ = "Asif Hussain"
__description__ = "CORTEX Track B Template System - Zero-execution response generation"