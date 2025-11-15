"""
CORTEX 3.0 Track B: Intelligent Context System
==============================================

The Intelligent Context System provides ML-powered analysis and understanding
of development activity through:
- ML Code Analyzer: Semantic code analysis and quality assessment
- Proactive Warnings: Real-time issue detection and prevention
- Pattern Detector: Development pattern recognition and learning
- Context Inference: Multi-source context understanding and prediction

This module enables CORTEX to understand and anticipate developer needs
through intelligent analysis of code, patterns, and development workflows.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from .ml_code_analyzer import MLCodeAnalyzer, CodeAnalysis, CodeChangeType, CodeElement
from .proactive_warnings import ProactiveWarnings, ProactiveWarning, WarningSeverity, WarningCategory
from .pattern_detector import PatternDetector, DetectedPattern, PatternType, PatternConfidence, PatternContext
from .context_inference import ContextInference, InferredContext, ContextSignal, DevelopmentSession, ContextType, ConfidenceLevel

__all__ = [
    # ML Code Analyzer
    "MLCodeAnalyzer",
    "CodeAnalysis",
    "CodeChangeType", 
    "CodeElement",
    
    # Proactive Warnings
    "ProactiveWarnings",
    "ProactiveWarning",
    "WarningSeverity",
    "WarningCategory",
    
    # Pattern Detector
    "PatternDetector",
    "DetectedPattern",
    "PatternType",
    "PatternConfidence",
    "PatternContext",
    
    # Context Inference
    "ContextInference",
    "InferredContext",
    "ContextSignal",
    "DevelopmentSession",
    "ContextType",
    "ConfidenceLevel",
]