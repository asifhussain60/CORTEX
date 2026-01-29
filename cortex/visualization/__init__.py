"""
CORTEX Visualization Package.

Provides visual intelligence dashboards for code repositories through:
- Business language content generation (AST → plain English)
- D3.js interactive visualizations (dependency graphs, timelines)
- Mermaid diagram generation (UML, ERD, state machines)
- Adaptive tab configuration (universal vs CORTEX-specific)
- Context-aware dashboard rendering

Components:
- repository_detector: Detect CORTEX vs external repositories
- dashboard_configuration: Context-aware tab selection
- business_language_generator: AST to business language conversion
- output_manager: Dashboard location routing
- renderers: D3.js and Mermaid visualization renderers
- formatters: Data format conversion for visualizations
- templates: Jinja2 HTML templates for dashboard UI

Authority: CORE-008 (TDD), CORE-011 (Type hints), CORE-012 (Docstrings)
Phase: 14 - LENS Dashboard Implementation
AC-ID: LENS-DASH-001
"""

__version__ = "1.0.0"
__author__ = "Asif Hussain"

# Module exports will be added as components are implemented
__all__ = []
