"""
CORTEX 3.0 Track B: Platform Package
====================================

macOS platform optimization package for CORTEX Track B.
Provides comprehensive macOS integration and optimization capabilities.

Key Components:
- MacOSOptimizer: System-level macOS optimizations and performance tuning
- ZshIntegration: Advanced Zsh shell integration and command enhancement
- XcodeCompatibility: Comprehensive Xcode integration and build system support

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file for terms
"""

from .macos_optimizer import (
    MacOSOptimizer,
    MacOSSystemInfo,
    OptimizationResult,
    OptimizationLevel,
    MacOSVersion
)

from .zsh_integration import (
    ZshIntegration,
    ZshConfig,
    ZshInstallationResult,
    ZshFeature,
    IntegrationLevel
)

from .xcode_compat import (
    XcodeCompatibility,
    XcodeInstallation,
    XcodeProject,
    BuildResult,
    XcodeVersion,
    ProjectType,
    BuildConfiguration
)

__all__ = [
    # macOS Optimizer
    "MacOSOptimizer",
    "MacOSSystemInfo",
    "OptimizationResult", 
    "OptimizationLevel",
    "MacOSVersion",
    
    # Zsh Integration
    "ZshIntegration",
    "ZshConfig",
    "ZshInstallationResult",
    "ZshFeature",
    "IntegrationLevel",
    
    # Xcode Compatibility
    "XcodeCompatibility",
    "XcodeInstallation",
    "XcodeProject",
    "BuildResult",
    "XcodeVersion",
    "ProjectType",
    "BuildConfiguration"
]

# Package metadata
__version__ = "3.0.0"
__author__ = "Asif Hussain"
__description__ = "CORTEX Track B Platform Package - macOS optimization and integration"