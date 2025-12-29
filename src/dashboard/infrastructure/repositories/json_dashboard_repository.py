"""
JsonDashboardRepository - JSON File-Based Dashboard Persistence

Concrete implementation of DashboardRepository using JSON files.
Each dashboard is stored as {app_id}.json in the base directory.

Author: Asif Hussain
"""
import json
import re
from pathlib import Path
from typing import Optional

from src.dashboard.domain.repositories.dashboard_repository import DashboardRepository
from src.dashboard.domain.entities.dashboard_data import DashboardData


class JsonDashboardRepository(DashboardRepository):
    """Repository for persisting dashboards to JSON files"""
    
    # Regex for safe app_id (alphanumeric, hyphens, underscores only)
    SAFE_APP_ID_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')
    
    def __init__(self, base_path: Path):
        """
        Initialize repository with base storage path.
        
        Args:
            base_path: Directory where JSON files will be stored
        """
        self._base_path = Path(base_path)
    
    def get_by_id(self, app_id: str) -> DashboardData:
        """
        Load dashboard from JSON file.
        
        Args:
            app_id: Application identifier
            
        Returns:
            DashboardData entity
            
        Raises:
            ValueError: If app_id contains invalid characters
            FileNotFoundError: If dashboard file doesn't exist
            ValueError: If JSON file is corrupted
        """
        self._validate_app_id(app_id)
        file_path = self._get_file_path(app_id)
        
        if not file_path.exists():
            raise FileNotFoundError(f"Dashboard not found for app_id='{app_id}'")
        
        return self._load_from_file(file_path)
    
    def save(self, data: DashboardData) -> None:
        """
        Save dashboard to JSON file.
        
        Args:
            data: DashboardData entity to persist
            
        Raises:
            ValueError: If app_id contains invalid characters
        """
        self._validate_app_id(data.app_id)
        self._base_path.mkdir(parents=True, exist_ok=True)
        
        file_path = self._get_file_path(data.app_id)
        json_data = self._entity_to_dict(data)
        
        with open(file_path, 'w') as f:
            json.dump(json_data, f, indent=2)
    
    def exists(self, app_id: str) -> bool:
        """
        Check if dashboard exists.
        
        Args:
            app_id: Application identifier
            
        Returns:
            True if dashboard file exists, False otherwise
        """
        try:
            self._validate_app_id(app_id)
            file_path = self._get_file_path(app_id)
            return file_path.exists()
        except ValueError:
            return False
    
    def _get_file_path(self, app_id: str) -> Path:
        """Get file path for app_id"""
        return self._base_path / f"{app_id}.json"
    
    def _validate_app_id(self, app_id: str) -> None:
        """
        Validate app_id contains only safe characters.
        
        Raises:
            ValueError: If app_id contains unsafe characters
        """
        if not self.SAFE_APP_ID_PATTERN.match(app_id):
            raise ValueError(
                f"Invalid app_id '{app_id}'. "
                "Only alphanumeric characters, hyphens, and underscores allowed."
            )
    
    def _load_from_file(self, file_path: Path) -> DashboardData:
        """
        Load and deserialize dashboard from JSON file.
        
        Raises:
            ValueError: If JSON is invalid
        """
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            return DashboardData(
                app_id=data["app_id"],
                tabs=data["tabs"],
                metadata=data["metadata"]
            )
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in dashboard file: {e}")
    
    def _entity_to_dict(self, data: DashboardData) -> dict:
        """Convert DashboardData entity to dict for JSON serialization"""
        return {
            "app_id": data.app_id,
            "tabs": data.tabs,
            "metadata": data.metadata
        }
