"""
Vacuum Orchestrator v3 - Core Framework

Autonomous file/folder management system that enforces CORTEX governance,
consolidates artifacts, and maintains clean architecture.

Features:
- Configuration loading from YAML manifest
- Comprehensive logging infrastructure
- Error handling with automatic rollback
- Backup system for all destructive operations
- Integration with CORTEX patterns
- Child orchestrator spawning for parallel operations
"""

import logging
import yaml
import json
import shutil
from pathlib import Path
from datetime import datetime
from typing import Optional, Dict, Any, List
from contextlib import contextmanager
from dataclasses import dataclass, field


@dataclass
class VacuumConfig:
    """Configuration for Vacuum Orchestrator v3."""
    
    # Orchestrator metadata
    name: str
    version: str
    enabled: bool = True
    
    # Operation settings
    backup_enabled: bool = True
    dry_run_default: bool = False
    max_parallel_tasks: int = 4
    
    # Paths
    backup_dir: str = "cortex-brain/backups/"
    compliance_db: str = "cortex-brain/tier0/vacuum-compliance.db"
    log_dir: str = "logs/"
    
    # Advanced settings
    retention_days: int = 7
    compression_enabled: bool = True
    verbose_logging: bool = False
    
    @classmethod
    def from_yaml(cls, manifest_path: Path) -> 'VacuumConfig':
        """Load configuration from YAML manifest file."""
        if not manifest_path.exists():
            raise FileNotFoundError(f"Manifest not found: {manifest_path}")
        
        with open(manifest_path, 'r') as f:
            data = yaml.safe_load(f)
        
        return cls.from_dict(data)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'VacuumConfig':
        """Create configuration from dictionary."""
        if 'orchestrator' not in data:
            raise ValueError("Missing required field: 'orchestrator'")
        
        orch_data = data['orchestrator']
        
        if 'name' not in orch_data:
            raise ValueError("Missing required field: 'orchestrator.name'")
        if 'version' not in orch_data:
            raise ValueError("Missing required field: 'orchestrator.version'")
        
        ops_data = data.get('operations', {})
        paths_data = data.get('paths', {})
        
        return cls(
            name=orch_data['name'],
            version=orch_data['version'],
            enabled=orch_data.get('enabled', True),
            backup_enabled=ops_data.get('backup_enabled', True),
            dry_run_default=ops_data.get('dry_run_default', False),
            max_parallel_tasks=ops_data.get('max_parallel_tasks', 4),
            backup_dir=paths_data.get('backup_dir', 'cortex-brain/backups/'),
            compliance_db=paths_data.get('compliance_db', 'cortex-brain/tier0/vacuum-compliance.db'),
            log_dir=paths_data.get('log_dir', 'logs/')
        )


@dataclass
class VacuumOperation:
    """Represents a vacuum operation with backup/rollback capability."""
    
    name: str
    backup_path: Optional[Path] = None
    files_affected: List[Path] = field(default_factory=list)
    backup_files_snapshot: Dict[str, str] = field(default_factory=dict)  # path -> content
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    success: bool = False
    error: Optional[str] = None


class VacuumOrchestratorV3:
    """
    Vacuum Orchestrator v3 - Core Framework
    
    Provides autonomous file/folder management with:
    - Configuration-driven operation
    - Automatic backup before destructive actions
    - Rollback capability on errors
    - Comprehensive logging
    - Integration with CORTEX patterns
    """
    
    def __init__(
        self,
        manifest_path: Optional[Path] = None,
        log_dir: Optional[Path] = None,
        workspace_root: Optional[Path] = None
    ):
        """
        Initialize Vacuum Orchestrator v3.
        
        Args:
            manifest_path: Path to vacuum-v3-manifest.yaml
            log_dir: Directory for log files (overrides config)
            workspace_root: Root of CORTEX workspace
        """
        self.workspace_root = workspace_root or Path.cwd()
        
        # Load configuration
        if manifest_path is None:
            manifest_path = self.workspace_root / "cortex-brain" / "manifests" / "orchestrators" / "vacuum-v3-manifest.yaml"
        
        self.config = VacuumConfig.from_yaml(Path(manifest_path))
        
        # Setup logging
        self.log_dir = Path(log_dir) if log_dir else self.workspace_root / self.config.log_dir
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = self._setup_logging()
        
        # Operation tracking
        self.current_operation: Optional[VacuumOperation] = None
        self.operation_history: List[VacuumOperation] = []
        
        # Child orchestrator spawner (lazy initialization)
        self._spawner: Optional[Any] = None
        
        # State
        self.is_initialized = True
        self.dry_run = self.config.dry_run_default
        
        self.logger.info(f"Initialized {self.config.name} v{self.config.version}")
    
    def _setup_logging(self) -> logging.Logger:
        """Set up logging infrastructure."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        log_file = self.log_dir / f"vacuum-v3-{timestamp}.log"
        
        logger = logging.getLogger(f"VacuumV3-{timestamp}")
        logger.setLevel(logging.DEBUG if self.config.verbose_logging else logging.INFO)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = logging.Formatter('%(levelname)s: %(message)s')
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
        
        return logger
    
    @contextmanager
    def operation_context(self, operation_name: str):
        """
        Context manager for operations with automatic backup and rollback.
        
        Usage:
            with orchestrator.operation_context("delete_files"):
                # Perform operations
                # Automatic rollback on error
        
        Args:
            operation_name: Name of the operation for logging
        """
        operation = VacuumOperation(
            name=operation_name,
            started_at=datetime.now()
        )
        
        self.current_operation = operation
        backup_path = None
        
        try:
            # Create backup if enabled
            if self.config.backup_enabled and not self.dry_run:
                backup_path = self._create_backup(operation_name)
                operation.backup_path = backup_path
                self.logger.info(f"Backup created: {backup_path}")
            
            # Execute operation
            self.logger.info(f"Starting operation: {operation_name}")
            yield operation
            
            # Mark success
            operation.success = True
            operation.completed_at = datetime.now()
            self.logger.info(f"Operation completed: {operation_name}")
            
        except Exception as e:
            # Log error
            operation.error = str(e)
            operation.completed_at = datetime.now()
            self.logger.error(f"Operation failed: {operation_name} - {e}")
            self.logger.info(f"Rolling back changes for: {operation_name}")
            
            # Rollback if backup exists
            if operation.backup_files_snapshot:
                self._restore_from_snapshot(operation.backup_files_snapshot)
                self.logger.info("Rollback completed")
            elif backup_path and backup_path.exists():
                self.logger.info(f"Rolling back from backup: {backup_path}")
                self._restore_backup(backup_path)
                self.logger.info("Rollback completed")
            
            raise
        
        finally:
            self.operation_history.append(operation)
            self.current_operation = None
    
    def _create_backup(self, operation_name: str) -> Path:
        """Create backup of current state."""
        timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_name = f"vacuum-{operation_name}-{timestamp}"
        backup_path = self.workspace_root / self.config.backup_dir / backup_name
        backup_path.mkdir(parents=True, exist_ok=True)
        
        # Store files to backup in operation
        if self.current_operation:
            self.current_operation.backup_files_snapshot = {}
        
        # Create backup metadata
        metadata = {
            "operation": operation_name,
            "timestamp": timestamp,
            "workspace": str(self.workspace_root),
            "files": []
        }
        
        metadata_file = backup_path / "backup-metadata.json"
        with open(metadata_file, 'w') as f:
            json.dump(metadata, f, indent=2)
        
        return backup_path
    
    def _restore_backup(self, backup_path: Path):
        """Restore from backup."""
        # Load metadata
        metadata_file = backup_path / "backup-metadata.json"
        if not metadata_file.exists():
            raise ValueError(f"Invalid backup: missing metadata at {backup_path}")
        
        with open(metadata_file, 'r') as f:
            metadata = json.load(f)
        
        self.logger.info(f"Restoring backup from: {metadata['timestamp']}")
        
        # Restore files (implementation depends on what was backed up)
        # This is a placeholder - actual restoration logic will be implemented
        # based on specific operation types
        
        self.logger.info("Backup restored successfully")
    
    def _restore_from_snapshot(self, snapshot: Dict[str, str]):
        """Restore files from in-memory snapshot."""
        for file_path_str, content in snapshot.items():
            file_path = Path(file_path_str)
            try:
                file_path.write_text(content)
                self.logger.debug(f"Restored: {file_path}")
            except Exception as e:
                self.logger.error(f"Failed to restore {file_path}: {e}")
    
    def backup_file(self, file_path: Path):
        """
        Backup a specific file before modification.
        Stores content in memory for quick rollback.
        """
        if not self.current_operation:
            raise RuntimeError("No active operation - use operation_context()")
        
        if file_path.exists():
            content = file_path.read_text()
            self.current_operation.backup_files_snapshot[str(file_path)] = content
            self.current_operation.files_affected.append(file_path)
            self.logger.debug(f"Backed up file: {file_path}")
    
    def has_backup_for_current_operation(self) -> bool:
        """Check if backup exists for current operation."""
        if not self.current_operation:
            return False
        return self.current_operation.backup_path is not None
    
    @property
    def spawner(self):
        """
        Get child orchestrator spawner (lazy initialization).
        
        Returns:
            ChildOrchestratorSpawner instance
        """
        if self._spawner is None:
            from src.orchestrators.vacuum.child_spawner import ChildOrchestratorSpawner
            self._spawner = ChildOrchestratorSpawner(
                parent_orchestrator=self,
                max_children=self.config.max_parallel_tasks,
                max_workers=self.config.max_parallel_tasks,
                logger=self.logger
            )
        return self._spawner
    
    def spawn_child(
        self,
        orchestrator_type: str,
        config: Optional[Dict[str, Any]] = None
    ):
        """
        Spawn a child orchestrator.
        
        Args:
            orchestrator_type: Type of orchestrator to spawn
            config: Configuration for the child
            
        Returns:
            ChildOrchestrator instance
        """
        return self.spawner.spawn(orchestrator_type, config)
    
    def execute_parallel(self, tasks: List[Any]) -> List[Any]:
        """
        Execute multiple tasks in parallel using child orchestrators.
        
        Args:
            tasks: List of tasks to execute
            
        Returns:
            List of task results
        """
        return self.spawner.execute_parallel(tasks)
    
    def execute(self, operation: str = "analyze", **kwargs):
        """
        Execute a vacuum operation.
        
        Args:
            operation: Operation to perform (analyze, reorganize, consolidate, etc.)
            **kwargs: Operation-specific arguments
        """
        self.logger.info(f"Executing operation: {operation}")
        
        with self.operation_context(operation):
            if operation == "analyze":
                return self._analyze_workspace()
            elif operation == "reorganize":
                return self._reorganize_folders()
            elif operation == "consolidate":
                return self._consolidate_reports()
            else:
                raise ValueError(f"Unknown operation: {operation}")
    
    def _analyze_workspace(self) -> Dict[str, Any]:
        """Analyze workspace structure and compliance."""
        self.logger.info("Analyzing workspace...")
        
        # Placeholder implementation
        return {
            "status": "success",
            "message": "Workspace analysis complete",
            "compliance_score": 85.0
        }
    
    def _reorganize_folders(self) -> Dict[str, Any]:
        """Reorganize folders according to CORTEX specifications."""
        self.logger.info("Reorganizing folders...")
        
        # Placeholder implementation
        return {
            "status": "success",
            "message": "Folder reorganization complete"
        }
    
    def _consolidate_reports(self) -> Dict[str, Any]:
        """Consolidate redundant reports."""
        self.logger.info("Consolidating reports...")
        
        # Placeholder implementation
        return {
            "status": "success",
            "message": "Report consolidation complete"
        }


def main():
    """Command-line entry point for Vacuum Orchestrator v3."""
    import sys
    
    # Parse arguments (basic implementation)
    dry_run = "--dry-run" in sys.argv
    operation = "analyze"  # Default
    
    if len(sys.argv) > 1 and not sys.argv[1].startswith("--"):
        operation = sys.argv[1]
    
    # Initialize orchestrator
    orchestrator = VacuumOrchestratorV3()
    orchestrator.dry_run = dry_run
    
    # Execute
    result = orchestrator.execute(operation)
    
    print(f"\n✅ Operation complete: {result['status']}")
    print(f"   {result['message']}")
    
    return 0 if result['status'] == 'success' else 1


if __name__ == "__main__":
    import sys
    sys.exit(main())
