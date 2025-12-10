"""
Documentation Orchestrator - Unified documentation generation

Consolidates 3 legacy files into a single orchestrator.

Components:
- documentation_orchestrator.py: Main orchestrator (200 LOC)
- github_pages_generator.py: GitHub Pages site generation (200 LOC)
- api_doc_generator.py: API documentation (150 LOC)
- report_builder.py: Reports and summaries (150 LOC)

Author: Asif Hussain
Date: December 10, 2025
"""

from .documentation_orchestrator import DocumentationOrchestrator

__all__ = ["DocumentationOrchestrator"]
