"""
Multi-application JSON repository implementation.

Provides isolated data storage for multiple dashboard applications
with per-app directory structure for complete data isolation.

This is the Infrastructure layer implementation of Clean Architecture,
providing concrete persistence mechanisms while implementing the
DashboardRepository port defined in the Domain layer.

Directory Structure:
    {root_path}/
        {app_id}/
            metadata.json       # Application metadata
            dashboard_data.json # Dashboard state and tabs

Security: Path traversal protection, validated app IDs only.
"""
import json
import shutil
from pathlib import Path
from typing import Optional, List, Dict
from datetime import datetime

from src.dashboard.domain.entities.dashboard_data import DashboardData
from src.dashboard.domain.entities.application_registry import Application
from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository


class JsonMultiAppRepository(DashboardRepository):
    """
    Multi-application JSON repository for dashboard data persistence.
    
    Implements isolated storage with per-application directories.
    Each application gets its own directory to ensure complete data isolation
    and prevent cross-contamination between different dashboard instances.
    
    This implementation supports the multi-tenancy requirements of the
    dashboard consolidation project, allowing CORTEX and external repositories
    to maintain separate dashboard states while sharing the same codebase.
    
    Thread-safety: Not thread-safe. External synchronization required for
    concurrent access to the same application's data.
    """
    
    # File names used in app directories
    METADATA_FILE = "metadata.json"
    DASHBOARD_DATA_FILE = "dashboard_data.json"
    
    def __init__(self, root_path: str):
        """
        Initialize repository with root storage path.
        
        Args:
            root_path: Base directory for all dashboard data.
                      Creates directory if it doesn't exist.
        """
        self.root_path = Path(root_path)
        self.root_path.mkdir(parents=True, exist_ok=True)
    
    def _get_app_dir(self, app_id: str) -> Path:
        """
        Get application directory path.
        
        Args:
            app_id: Application identifier
            
        Returns:
            Path to application directory
        """
        return self.root_path / app_id
    
    def _validate_app_id_security(self, app_id: str) -> None:
        """
        Validate app ID doesn't contain path traversal attempts.
        
        Defense-in-depth: Application entity also validates, but we
        double-check here as repository is the last line of defense.
        
        Args:
            app_id: Application identifier to validate
            
        Raises:
            ValueError: If app_id contains unsafe characters
        """
        if ".." in app_id or "/" in app_id or "\\" in app_id:
            raise ValueError(f"Invalid app ID (path traversal detected): {app_id}")
    
    def initialize_app(self, app: Application) -> None:
        """
        Initialize directory structure for an application.
        
        Creates app-specific directory and metadata file. This must be called
        before saving dashboard data for a new application.
        
        Args:
            app: Application entity to initialize
            
        Raises:
            ValueError: If app ID contains path traversal attempts
        """
        self._validate_app_id_security(app.id)
        
        app_dir = self._get_app_dir(app.id)
        app_dir.mkdir(parents=True, exist_ok=True)
        
        # Create initial metadata
        metadata = {
            "app_id": app.id,
            "name": app.name,
            "display_name": app.display_name,
            "created_at": datetime.now().isoformat(),
        }
        
        metadata_file = app_dir / self.METADATA_FILE
        self._write_json(metadata_file, metadata)
    
    def _write_json(self, file_path: Path, data: Dict) -> None:
        """Write data to JSON file with consistent formatting."""
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, sort_keys=True)
    
    def _read_json(self, file_path: Path) -> Dict:
        """Read data from JSON file."""
        with open(file_path) as f:
            return json.load(f)
    
    def save(self, data: DashboardData, app_id: str = None) -> None:
        """
        Save dashboard data (implements DashboardRepository.save).
        
        Args:
            data: Dashboard data to persist
            app_id: Optional application identifier (uses data.app_id if None)
            
        Raises:
            ValueError: If application not initialized
        """
        if app_id is None:
            app_id = data.app_id
        
        app_dir = self._get_app_dir(app_id)
        if not app_dir.exists():
            raise ValueError(
                f"Application {app_id} not initialized. "
                f"Call initialize_app() first."
            )
        
        data_file = app_dir / self.DASHBOARD_DATA_FILE
        
        # Add timestamp to persisted data
        data_dict = {
            "app_id": data.app_id,
            "tabs": data.tabs,
            "metadata": data.metadata,
            "last_updated": datetime.now().isoformat()
        }
        
        self._write_json(data_file, data_dict)
    
    def save_for_app(self, app_id: str, dashboard_data: DashboardData) -> None:
        """
        Save dashboard data with explicit app_id (convenience method).
        
        Args:
            app_id: Application identifier
            dashboard_data: Dashboard data to save
        """
        self.save(dashboard_data, app_id=app_id)
    
    def get_by_id(self, app_id: str) -> DashboardData:
        """
        Get dashboard data by ID (implements DashboardRepository.get_by_id).
        
        Args:
            app_id: Application identifier
            
        Returns:
            DashboardData entity
            
        Raises:
            FileNotFoundError: If dashboard not found
        """
        result = self.load(app_id)
        if result is None:
            raise FileNotFoundError(
                f"Dashboard not found for app: {app_id}. "
                f"Ensure application is initialized and has saved data."
            )
        return result
    
    def exists(self, app_id: str) -> bool:
        """
        Check if dashboard exists (implements DashboardRepository.exists).
        
        Args:
            app_id: Application identifier
            
        Returns:
            True if dashboard exists with data
        """
        app_dir = self._get_app_dir(app_id)
        if not app_dir.exists():
            return False
        
        data_file = app_dir / self.DASHBOARD_DATA_FILE
        return data_file.exists()
    
    def load(self, app_id: str) -> Optional[DashboardData]:
        """
        Load dashboard data for specific application.
        
        Args:
            app_id: Application identifier
            
        Returns:
            DashboardData or None if not found
        """
        app_dir = self._get_app_dir(app_id)
        if not app_dir.exists():
            return None
        
        data_file = app_dir / self.DASHBOARD_DATA_FILE
        if not data_file.exists():
            return None
        
        data_dict = self._read_json(data_file)
        
        return DashboardData(
            app_id=data_dict["app_id"],
            tabs=data_dict["tabs"],
            metadata=data_dict["metadata"]
        )
    
    def list_apps(self) -> List[str]:
        """
        List all initialized application IDs.
        
        Returns:
            Sorted list of app IDs that have been initialized
        """
        apps = []
        for item in self.root_path.iterdir():
            if item.is_dir() and (item / self.METADATA_FILE).exists():
                apps.append(item.name)
        return sorted(apps)
    
    def delete_app(self, app_id: str) -> None:
        """
        Delete all data for specified application.
        
        Removes entire app directory including metadata and dashboard data.
        This operation is irreversible.
        
        Args:
            app_id: Application identifier
        """
        app_dir = self._get_app_dir(app_id)
        if app_dir.exists():
            shutil.rmtree(app_dir)
    
    def get_metadata(self, app_id: str) -> Optional[Dict]:
        """
        Get app metadata without loading full dashboard.
        
        Efficient for checking app details without deserializing
        entire dashboard state.
        
        Args:
            app_id: Application identifier
            
        Returns:
            Metadata dict or None if app not initialized
        """
        app_dir = self._get_app_dir(app_id)
        if not app_dir.exists():
            return None
        
        metadata_file = app_dir / self.METADATA_FILE
        if not metadata_file.exists():
            return None
        
        return self._read_json(metadata_file)
    
    def update_metadata(self, app_id: str, metadata: Dict) -> None:
        """
        Update app metadata.
        
        Args:
            app_id: Application identifier
            metadata: New metadata dict
            
        Raises:
            ValueError: If application not initialized
        """
        app_dir = self._get_app_dir(app_id)
        if not app_dir.exists():
            raise ValueError(f"Application {app_id} not initialized")
        
        metadata_file = app_dir / self.METADATA_FILE
        self._write_json(metadata_file, metadata)
