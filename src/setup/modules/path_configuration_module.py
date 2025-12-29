"""
Path Configuration Setup Module

Guides users through configuring repository paths for tests, documents, and other files.
Integrates PathDetector for intelligent path discovery and PathConfigQuestionnaire
for interactive configuration.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any, Optional

from ..base_setup_module import (
    BaseSetupModule,
    SetupModuleMetadata,
    SetupResult,
    SetupStatus,
    SetupPhase
)
from ..models.user_path_config import UserPathConfig
from .path_config_questionnaire import PathConfigQuestionnaire
from .path_detector import PathDetector
from .user_profile_storage import UserProfileStorage


class PathConfigurationModule(BaseSetupModule):
    """
    Setup module for configuring repository path preferences.
    
    Features:
    - Auto-detects existing test directories with confidence scoring
    - Shows framework detection (pytest, Jest, etc.)
    - Interactive questionnaire for path preferences
    - Persists configuration to cortex.config.json
    - Validates configured paths
    
    Dependencies:
    - Requires 'user_profile' module (creates initial config file)
    
    Phase: CORE (runs after user profile setup)
    Priority: 20 (after user profile priority 10)
    """
    
    def __init__(self):
        """Initialize path configuration module."""
        super().__init__()
        self.logger = logging.getLogger(__name__)
        self._config_path: Optional[Path] = None
        self._created_paths: list[Path] = []
    
    @property
    def metadata(self) -> SetupModuleMetadata:
        """Module metadata."""
        return SetupModuleMetadata(
            module_id="path_configuration",
            name="Path Configuration",
            description="Configure repository paths for tests, documents, and other files",
            version="1.0.0",
            author="Asif Hussain",
            phase=SetupPhase.CORE,
            priority=20,
            dependencies=["user_profile"],
            can_skip=True,
            estimated_duration_seconds=120
        )
    
    def validate_prerequisites(self, context: Dict[str, Any]) -> bool:
        """
        Validate that prerequisites are met.
        
        Args:
            context: Setup context
        
        Returns:
            True if prerequisites satisfied
        """
        # Require project root
        if 'project_root' not in context:
            self.logger.error("Missing project_root in context")
            return False
        
        project_root = Path(context['project_root'])
        if not project_root.exists():
            self.logger.error(f"Project root does not exist: {project_root}")
            return False
        
        # Check that config file exists (created by user_profile module)
        config_path = project_root / "cortex.config.json"
        if not config_path.exists():
            self.logger.warning(
                "cortex.config.json not found - user_profile module should run first"
            )
        
        return True
    
    def execute(self, context: Dict[str, Any]) -> SetupResult:
        """
        Execute path configuration setup.
        
        Args:
            context: Setup context
        
        Returns:
            Setup result
        """
        project_root = Path(context['project_root'])
        self._config_path = project_root / "cortex.config.json"
        
        self.logger.info("\n" + "=" * 60)
        self.logger.info("PATH CONFIGURATION")
        self.logger.info("=" * 60)
        
        try:
            # Step 1: Detect existing paths
            self.logger.info("\nStep 1: Scanning repository for existing paths...")
            detector = PathDetector(str(project_root))
            scan_results = detector.scan_repository()
            
            self._log_scan_results(scan_results)
            
            # Step 2: Run interactive questionnaire
            self.logger.info("\nStep 2: Path Configuration Questionnaire")
            self.logger.info("-" * 60)
            
            questionnaire = PathConfigQuestionnaire(str(project_root))
            path_config = questionnaire.run()
            
            if path_config is None:
                return SetupResult(
                    module_id=self.metadata.module_id,
                    status=SetupStatus.SKIPPED,
                    message="User skipped path configuration",
                    duration_ms=0,
                    details={}
                )
            
            # Step 3: Save configuration
            self.logger.info("\nStep 3: Saving path configuration...")
            storage = UserProfileStorage(str(self._config_path))
            storage.save_path_config(path_config)
            
            self.logger.info(f"✓ Path configuration saved to {self._config_path}")
            
            # Step 4: Create configured directories if requested
            created_dirs = self._create_directories(path_config, project_root, context)
            
            # Build result details
            details = {
                'config_path': str(self._config_path),
                'test_directory': path_config.test_directory,
                'documents_root': path_config.documents_root,
                'created_directories': [str(p) for p in created_dirs],
                'scan_results': {
                    'test_directories_found': len(scan_results.get('test_directories', [])),
                    'frameworks_detected': scan_results.get('frameworks', [])
                }
            }
            
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.SUCCESS,
                message=f"✓ Path configuration complete ({len(created_dirs)} directories created)",
                duration_ms=0,
                details=details
            )
            
        except Exception as e:
            self.logger.error(f"Path configuration failed: {e}", exc_info=True)
            return SetupResult(
                module_id=self.metadata.module_id,
                status=SetupStatus.FAILED,
                message=f"Failed to configure paths: {e}",
                duration_ms=0,
                details={'error': str(e)}
            )
    
    def rollback(self, context: Dict[str, Any]) -> bool:
        """
        Rollback path configuration changes.
        
        Args:
            context: Setup context
        
        Returns:
            True if rollback successful
        """
        self.logger.info("Rolling back path configuration...")
        
        # Remove created directories (only if empty)
        for path in reversed(self._created_paths):
            try:
                if path.exists() and path.is_dir():
                    # Only remove if empty
                    if not any(path.iterdir()):
                        path.rmdir()
                        self.logger.info(f"  Removed: {path}")
                    else:
                        self.logger.info(f"  Skipped (not empty): {path}")
            except Exception as e:
                self.logger.warning(f"  Could not remove {path}: {e}")
        
        # Remove path config from cortex.config.json
        if self._config_path and self._config_path.exists():
            try:
                storage = UserProfileStorage(str(self._config_path))
                # Load current config and remove user_paths section
                import json
                with open(self._config_path, 'r') as f:
                    config = json.load(f)
                
                if 'user_paths' in config:
                    del config['user_paths']
                    with open(self._config_path, 'w') as f:
                        json.dump(config, f, indent=2)
                    self.logger.info(f"  Removed path config from {self._config_path}")
            except Exception as e:
                self.logger.warning(f"  Could not remove path config: {e}")
        
        return True
    
    def _log_scan_results(self, scan_results: Dict[str, Any]):
        """Log repository scan results."""
        test_dirs = scan_results.get('test_directories', [])
        
        if test_dirs:
            self.logger.info(f"\n  Found {len(test_dirs)} test director{'y' if len(test_dirs) == 1 else 'ies'}:")
            for test_dir in test_dirs:
                confidence = test_dir.get('confidence', 0)
                framework = test_dir.get('framework', 'Unknown')
                count = test_dir.get('test_count', 0)
                self.logger.info(
                    f"    • {test_dir['path']} "
                    f"[{framework}, {count} tests, {confidence:.0%} confidence]"
                )
        else:
            self.logger.info("  No existing test directories found")
        
        frameworks = scan_results.get('frameworks', [])
        if frameworks:
            self.logger.info(f"  Detected frameworks: {', '.join(frameworks)}")
    
    def _create_directories(
        self,
        path_config: UserPathConfig,
        project_root: Path,
        context: Dict[str, Any]
    ) -> list[Path]:
        """
        Create configured directories if they don't exist.
        
        Args:
            path_config: Path configuration
            project_root: Project root directory
            context: Setup context
        
        Returns:
            List of created directory paths
        """
        created = []
        
        # Only create directories if user chose to in context
        if not context.get('create_directories', True):
            return created
        
        # Test directory
        if path_config.test_directory:
            test_path = project_root / path_config.test_directory
            if not test_path.exists():
                test_path.mkdir(parents=True, exist_ok=True)
                created.append(test_path)
                self._created_paths.append(test_path)
                self.logger.info(f"  ✓ Created: {test_path}")
        
        # Documents root
        if path_config.documents_root:
            docs_path = project_root / path_config.documents_root
            if not docs_path.exists():
                docs_path.mkdir(parents=True, exist_ok=True)
                created.append(docs_path)
                self._created_paths.append(docs_path)
                self.logger.info(f"  ✓ Created: {docs_path}")
            
            # Create document subdirectories
            subdirs = [
                'reports', 'analysis', 'summaries', 
                'investigations', 'planning', 'implementation-guides'
            ]
            for subdir in subdirs:
                subdir_path = docs_path / subdir
                if not subdir_path.exists():
                    subdir_path.mkdir(parents=True, exist_ok=True)
                    created.append(subdir_path)
                    self._created_paths.append(subdir_path)
        
        if created:
            self.logger.info(f"\n✓ Created {len(created)} directories")
        
        return created
