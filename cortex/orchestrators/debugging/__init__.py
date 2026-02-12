"""
CORTEX Debug Orchestrator Package
=================================

Universal debugging capabilities for any repository type.
Provides intelligent debug marker injection, log capture, analysis,
and cleanup across multiple languages (JavaScript, Python, TypeScript, etc.)

Author: CORTEX
Version: 1.0.0
Phase: Phase 21.5 - Universal Debugging

Components:
- DebugOrchestrator: Main orchestration coordinator
- DebugInjector: Language-aware marker injection
- DebugCapture: Log collection during execution
- DebugAnalyzer: Race condition and integration issue detection
- DebugCleanup: Safe marker removal
"""

from cortex.orchestrators.debugging.debug_analyzer import DebugAnalyzer
from cortex.orchestrators.debugging.debug_capture import DebugCapture
from cortex.orchestrators.debugging.debug_cleanup import DebugCleanup
from cortex.orchestrators.debugging.debug_injector import DebugInjector
from cortex.orchestrators.debugging.debug_orchestrator import DebugOrchestrator

__all__ = [
    "DebugOrchestrator",
    "DebugInjector",
    "DebugCapture",
    "DebugAnalyzer",
    "DebugCleanup",
]
