"""
CORTEX 3.0 Brain Integration for EPM Documentation Generator
Feature 5: Brain-Enhanced Documentation with Pattern Learning and Adaptive Generation

This module integrates the EPM Documentation Generator with CORTEX Brain's knowledge systems,
providing intelligent, adaptive, and learning-based documentation generation capabilities.

Core Components:
- BrainConnector: Interface to CORTEX Brain knowledge graph and databases
- PatternLearningEngine: Learns from documentation patterns and user feedback
- AdaptiveTemplateSystem: Intelligent template selection and optimization
- ContextAwareGenerator: Uses project context for targeted documentation
- QualityFeedbackLoop: Continuous improvement through quality metrics
- BrainEnhancedConfig: Intelligent configuration based on patterns
"""

from .brain_connector import BrainConnector
from .pattern_learning import PatternLearningEngine
from .adaptive_templates import AdaptiveTemplateSystem
from .context_aware import ContextAwareGenerator
from .quality_feedback import QualityFeedbackLoop
from .brain_config import BrainEnhancedConfig
from .brain_api import BrainIntegrationAPI

__all__ = [
    'BrainConnector',
    'PatternLearningEngine', 
    'AdaptiveTemplateSystem',
    'ContextAwareGenerator',
    'QualityFeedbackLoop',
    'BrainEnhancedConfig',
    'BrainIntegrationAPI'
]

__version__ = '1.0.0'
__feature__ = 'Feature 5: CORTEX Brain Integration'
__description__ = 'Intelligent documentation generation with pattern learning and adaptive optimization'