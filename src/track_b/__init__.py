"""
CORTEX 3.0 Track B (Mac) Implementation
=====================================

Track B focuses on:
- Execution Channel: Ambient daemon, file monitoring, git hooks, terminal tracking
- Intelligent Context: ML code analysis, proactive warnings, pattern detection
- Template Integration: Zero-execution help responses
- macOS Platform Optimization: Zsh integration, Xcode compatibility

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
Repository: https://github.com/asifhussain60/CORTEX
"""

__version__ = "3.0.0-track-b"
__author__ = "Asif Hussain"
__copyright__ = "© 2024-2025 Asif Hussain"

from .execution_channel import AmbientDaemon, FileMonitor, GitMonitor, TerminalTracker
from .intelligent_context import MLCodeAnalyzer, ProactiveWarnings, PatternDetector, ContextInference
from .template_system import TemplateEngine, ResponseGenerator, TemplateOptimizer
from .platform import MacOSOptimizer, ZshIntegration, XcodeCompatibility

__all__ = [
    # Execution Channel
    "AmbientDaemon",
    "FileMonitor", 
    "GitMonitor",
    "TerminalTracker",
    
    # Intelligent Context
    "MLCodeAnalyzer",
    "ProactiveWarnings",
    "PatternDetector",
    "ContextInference",
    
    # Template System
    "TemplateEngine",
    "ResponseGenerator",
    "TemplateOptimizer",
    
    # Platform Optimization
    "MacOSOptimizer",
    "ZshIntegration",
    "XcodeCompatibility",
]