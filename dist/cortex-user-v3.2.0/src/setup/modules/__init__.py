"""
Setup Modules Package

All concrete setup modules implementing BaseSetupModule interface.
Each module handles ONE specific setup responsibility (SOLID Single Responsibility Principle).

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from .platform_detection_module import PlatformDetectionModule
from .vision_api_module import VisionAPIModule
from .brain_initialization_module import BrainInitializationModule
from .python_dependencies_module import PythonDependenciesModule
from .refactoring_tools_module import RefactoringToolsModule
from .smart_refactoring_recommender import SmartRefactoringRecommender

__all__ = [
    'PlatformDetectionModule',
    'VisionAPIModule',
    'BrainInitializationModule',
    'PythonDependenciesModule',
    'RefactoringToolsModule',
    'SmartRefactoringRecommender',
]
