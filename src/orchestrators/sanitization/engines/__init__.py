"""
Sanitization Engines Package.

Contains specialized engines for the Sanitization Orchestrator v2:
- CodeAnalyzerEngine: File scanning, term extraction, risk classification
- MappingEngine: Generate transformation mappings with approval workflow
- TransformerEngine: Apply transformations with transactional safety
- ValidatorEngine: Build and test validation
- ReportGeneratorEngine: Generate reports and artifacts

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

__version__ = "2.0.0"

# Import engines for easy access - ALL ENGINES IMPLEMENTED ✅
from .code_analyzer_engine import CodeAnalyzerEngine
from .mapping_engine import MappingEngineV2 as MappingEngine
from .transformer_engine import TransformerEngine
from .validator_engine import ValidatorEngine
from .report_generator_engine import ReportGeneratorEngine

__all__ = [
    "CodeAnalyzerEngine",
    "MappingEngine",
    "TransformerEngine",
    "ValidatorEngine",
    "ReportGeneratorEngine"
]
