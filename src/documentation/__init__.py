"""
CORTEX Documentation Generation System
Automated capability discovery and documentation generation
"""

from .discovery.capability_scanner import CapabilityScanner, Capability
from .templates.template_engine import TemplateEngine
from .orchestrator import DocumentationOrchestrator

__version__ = '1.0.0'
__all__ = [
    'CapabilityScanner',
    'Capability',
    'TemplateEngine',
    'DocumentationOrchestrator'
]
