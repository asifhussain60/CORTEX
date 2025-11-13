"""
Operation Modules Package

All concrete operation modules implementing BaseOperationModule interface.
Each module handles ONE specific operation responsibility (SOLID Single Responsibility Principle).

Covers:
    - Setup operations (platform detection, dependencies, etc.)
    - Story refresh operations (load, transform, save, etc.)
    - Cleanup operations (temp files, logs, etc.)
    - Documentation operations (API docs, design docs, etc.)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

# Setup modules
from .project_validation_module import ProjectValidationModule
from .platform_detection_module import PlatformDetectionModule
from .git_sync_module import GitSyncModule
from .virtual_environment_module import VirtualEnvironmentModule
from .python_dependencies_module import PythonDependenciesModule
from .vision_api_module import VisionAPIModule
from .conversation_tracking_module import ConversationTrackingModule
from .brain_initialization_module import BrainInitializationModule
from .brain_tests_module import BrainTestsModule
from .tooling_verification_module import ToolingVerificationModule
from .setup_completion_module import SetupCompletionModule

# Story refresh modules
from .load_story_template_module import LoadStoryTemplateModule
from .apply_narrator_voice_module import ApplyNarratorVoiceModule
from .validate_story_structure_module import ValidateStoryStructureModule
from .save_story_markdown_module import SaveStoryMarkdownModule
from .update_mkdocs_index_module import UpdateMkDocsIndexModule
from .build_story_preview_module import BuildStoryPreviewModule

# Cleanup modules
from .scan_temporary_files_module import ScanTemporaryFilesModule
from .remove_old_logs_module import RemoveOldLogsModule
from .clear_python_cache_module import ClearPythonCacheModule
from .vacuum_sqlite_databases_module import VacuumSQLiteDatabasesModule
from .remove_orphaned_files_module import RemoveOrphanedFilesModule
from .generate_cleanup_report_module import GenerateCleanupReportModule

# Documentation modules
from .scan_docstrings_module import ScanDocstringsModule
from .generate_api_docs_module import GenerateAPIDocsModule
from .refresh_design_docs_module import RefreshDesignDocsModule
from .build_mkdocs_site_module import BuildMkDocsSiteModule
from .validate_doc_links_module import ValidateDocLinksModule
from .deploy_docs_preview_module import DeployDocsPreviewModule

# Brain protection modules
from .load_protection_rules_module import LoadProtectionRulesModule

# Optimization modules
from .optimization.hardcoded_data_cleaner_module import HardcodedDataCleanerModule

__all__ = [
    # Setup modules
    'ProjectValidationModule',
    'PlatformDetectionModule',
    'GitSyncModule',
    'VirtualEnvironmentModule',
    'PythonDependenciesModule',
    'VisionAPIModule',
    'ConversationTrackingModule',
    'BrainInitializationModule',
    'BrainTestsModule',
    'ToolingVerificationModule',
    'SetupCompletionModule',
    
    # Story refresh modules
    'LoadStoryTemplateModule',
    'ApplyNarratorVoiceModule',
    'ValidateStoryStructureModule',
    'SaveStoryMarkdownModule',
    'UpdateMkDocsIndexModule',
    'BuildStoryPreviewModule',
    
    # Cleanup modules
    'ScanTemporaryFilesModule',
    'RemoveOldLogsModule',
    'ClearPythonCacheModule',
    'VacuumSQLiteDatabasesModule',
    'RemoveOrphanedFilesModule',
    'GenerateCleanupReportModule',
    
    # Documentation modules
    'ScanDocstringsModule',
    'GenerateAPIDocsModule',
    'RefreshDesignDocsModule',
    'BuildMkDocsSiteModule',
    'ValidateDocLinksModule',
    'DeployDocsPreviewModule',
    
    # Brain protection modules
    'LoadProtectionRulesModule',
    
    # Optimization modules
    'HardcodedDataCleanerModule',
]
