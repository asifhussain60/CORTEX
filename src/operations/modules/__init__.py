"""
Operation Modules Package

All concrete operation modules implementing BaseOperationModule interface.
Each module handles ONE specific operation responsibility (SOLID Single Responsibility Principle).

Covers:
    - Setup operations (platform detection, dependencies, etc.)
    - Story refresh operations (load, transform, save, etc.)
    - Future operations (cleanup, testing, documentation, etc.)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

# Setup modules
from .platform_detection_module import PlatformDetectionModule
from .vision_api_module import VisionAPIModule
from .brain_initialization_module import BrainInitializationModule
from .python_dependencies_module import PythonDependenciesModule

# Story refresh modules
from .load_story_template_module import LoadStoryTemplateModule
from .apply_narrator_voice_module import ApplyNarratorVoiceModule
from .validate_story_structure_module import ValidateStoryStructureModule
from .save_story_markdown_module import SaveStoryMarkdownModule
from .update_mkdocs_index_module import UpdateMkdocsIndexModule
from .build_story_preview_module import BuildStoryPreviewModule

__all__ = [
    # Setup modules
    'PlatformDetectionModule',
    'VisionAPIModule',
    'BrainInitializationModule',
    'PythonDependenciesModule',
    
    # Story refresh modules
    'LoadStoryTemplateModule',
    'ApplyNarratorVoiceModule',
    'ValidateStoryStructureModule',
    'SaveStoryMarkdownModule',
    'UpdateMkdocsIndexModule',
    'BuildStoryPreviewModule',
]
