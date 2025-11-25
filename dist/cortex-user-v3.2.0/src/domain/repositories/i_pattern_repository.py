"""
Pattern repository interface.

Domain-specific repository interface for pattern entities.
"""

from abc import abstractmethod
from typing import List, Optional
from .i_repository import IRepository


class IPatternRepository(IRepository['Pattern']):
    """
    Repository interface for pattern entities.
    
    Extends generic repository with pattern-specific queries.
    """
    
    @abstractmethod
    def find_by_category(self, category: str) -> List['Pattern']:
        """
        Find patterns by category.
        
        Args:
            category: Pattern category (e.g., 'edge_case', 'domain_knowledge')
            
        Returns:
            List of patterns in the category
        """
        pass
    
    @abstractmethod
    def find_by_confidence_threshold(self, min_confidence: float) -> List['Pattern']:
        """
        Find patterns by confidence threshold.
        
        Args:
            min_confidence: Minimum confidence score (0.0-1.0)
            
        Returns:
            List of patterns meeting confidence threshold
        """
        pass
    
    @abstractmethod
    def find_similar(self, pattern_id: int, threshold: float = 0.75) -> List['Pattern']:
        """
        Find similar patterns.
        
        Args:
            pattern_id: Reference pattern ID
            threshold: Similarity threshold (0.0-1.0)
            
        Returns:
            List of patterns similar to the reference
        """
        pass
    
    @abstractmethod
    def update_confidence(self, pattern_id: int, new_confidence: float) -> None:
        """
        Update pattern confidence score.
        
        Args:
            pattern_id: Pattern ID
            new_confidence: New confidence score (0.0-1.0)
        """
        pass
    
    @abstractmethod
    def increment_success_count(self, pattern_id: int) -> None:
        """
        Increment pattern success count.
        
        Args:
            pattern_id: Pattern ID
        """
        pass
    
    @abstractmethod
    def increment_failure_count(self, pattern_id: int) -> None:
        """
        Increment pattern failure count.
        
        Args:
            pattern_id: Pattern ID
        """
        pass
    
    @abstractmethod
    def get_success_rate(self, pattern_id: int) -> float:
        """
        Get pattern success rate.
        
        Args:
            pattern_id: Pattern ID
            
        Returns:
            Success rate as percentage (0.0-100.0)
        """
        pass
