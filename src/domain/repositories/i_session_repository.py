"""
Session repository interface.

Domain-specific repository interface for TDD session entities.
"""

from abc import abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from .i_repository import IRepository


class ISessionRepository(IRepository['Session']):
    """
    Repository interface for TDD session entities.
    
    Extends generic repository with session-specific queries.
    """
    
    @abstractmethod
    def find_active(self) -> List['Session']:
        """
        Find active sessions.
        
        Returns:
            List of sessions that are currently in progress
        """
        pass
    
    @abstractmethod
    def find_by_feature(self, feature_name: str) -> List['Session']:
        """
        Find sessions by feature name.
        
        Args:
            feature_name: Name of the feature
            
        Returns:
            List of sessions for the specified feature
        """
        pass
    
    @abstractmethod
    def get_session_history(self, session_id: int) -> List[Dict[str, Any]]:
        """
        Get session history.
        
        Args:
            session_id: Session ID
            
        Returns:
            List of history entries for the session
        """
        pass
    
    @abstractmethod
    def get_metrics(self, session_id: int) -> Dict[str, Any]:
        """
        Get session metrics.
        
        Args:
            session_id: Session ID
            
        Returns:
            Dictionary containing session metrics
        """
        pass
    
    @abstractmethod
    def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List['Session']:
        """
        Find sessions by date range.
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of sessions within the date range
        """
        pass
    
    @abstractmethod
    def get_average_cycle_time(self, feature_name: Optional[str] = None) -> float:
        """
        Get average cycle time.
        
        Args:
            feature_name: Optional feature name filter
            
        Returns:
            Average cycle time in seconds
        """
        pass
