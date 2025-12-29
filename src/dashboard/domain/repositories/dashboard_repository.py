"""
DashboardRepository Interface

Abstract repository for dashboard data storage.
Defines contract - implementations in infrastructure layer.

This is the "Port" in Ports and Adapters (Hexagonal Architecture).
Domain layer defines the interface, infrastructure layer implements it.

Author: Asif Hussain
"""
from abc import ABC, abstractmethod
from src.dashboard.domain.entities.dashboard_data import DashboardData


class DashboardRepository(ABC):
    """
    Abstract repository for dashboard data storage.
    
    This interface defines the contract for storing and retrieving dashboard data.
    Concrete implementations live in the infrastructure layer (e.g., JsonDashboardRepository).
    
    Methods:
        get_by_id: Retrieve dashboard data for specific application
        save: Persist dashboard data
        exists: Check if dashboard exists for application
    """
    
    @abstractmethod
    def get_by_id(self, app_id: str) -> DashboardData:
        """
        Retrieve dashboard data by application ID.
        
        Args:
            app_id: Unique application identifier
        
        Returns:
            DashboardData entity
        
        Raises:
            FileNotFoundError: If dashboard does not exist for app_id
        """
        pass
    
    @abstractmethod
    def save(self, data: DashboardData) -> None:
        """
        Persist dashboard data.
        
        Args:
            data: DashboardData entity to save
        """
        pass
    
    @abstractmethod
    def exists(self, app_id: str) -> bool:
        """
        Check if dashboard exists for application.
        
        Args:
            app_id: Unique application identifier
        
        Returns:
            True if dashboard exists, False otherwise
        """
        pass
