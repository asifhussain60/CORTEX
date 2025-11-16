"""
Base Crawler Class for Discovery Report System

All discovery crawlers inherit from this base class, which provides:
- Standard interface for crawling
- Error handling
- Logging
- Timeout management
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging
from datetime import datetime


class BaseCrawler(ABC):
    """
    Abstract base class for all discovery crawlers.
    
    Each crawler analyzes one aspect of the project (files, git, tests, etc.)
    and returns structured data for report generation.
    """
    
    def __init__(self, project_root: str):
        """
        Initialize crawler with project root path.
        
        Args:
            project_root: Absolute path to project root directory
        """
        self.project_root = project_root
        self.logger = logging.getLogger(f"cortex.crawler.{self.get_name()}")
        self.start_time = None
        self.end_time = None
    
    @abstractmethod
    def crawl(self) -> Dict[str, Any]:
        """
        Execute crawler and return discovery data.
        
        Returns:
            Dict containing crawler-specific discovery data
            
        Example structure:
            {
                "success": True,
                "data": {...},
                "errors": [],
                "warnings": []
            }
        """
        pass
    
    @abstractmethod
    def get_name(self) -> str:
        """
        Return crawler name for logging and identification.
        
        Returns:
            Human-readable crawler name (e.g., "File Scanner")
        """
        pass
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute crawler with error handling and timing.
        
        This wraps the crawl() method with standard error handling,
        logging, and performance tracking.
        
        Returns:
            Dict containing:
                - success: bool
                - data: crawler-specific data
                - crawler_name: str
                - execution_time_ms: float
                - errors: list of error messages
        """
        self.start_time = datetime.now()
        self.logger.info(f"Starting {self.get_name()} crawler")
        
        try:
            result = self.crawl()
            self.end_time = datetime.now()
            execution_time = (self.end_time - self.start_time).total_seconds() * 1000
            
            self.logger.info(
                f"{self.get_name()} completed in {execution_time:.2f}ms"
            )
            
            # Ensure standard structure
            if not isinstance(result, dict):
                result = {"data": result}
            
            result.update({
                "success": result.get("success", True),
                "crawler_name": self.get_name(),
                "execution_time_ms": execution_time,
                "timestamp": self.start_time.isoformat()
            })
            
            return result
            
        except Exception as e:
            self.end_time = datetime.now()
            execution_time = (self.end_time - self.start_time).total_seconds() * 1000
            
            self.logger.error(
                f"{self.get_name()} failed after {execution_time:.2f}ms: {str(e)}"
            )
            
            return self.handle_error(e, execution_time)
    
    def handle_error(self, error: Exception, execution_time: float) -> Dict[str, Any]:
        """
        Standard error handling for all crawlers.
        
        Args:
            error: Exception that occurred
            execution_time: Time spent before error (ms)
            
        Returns:
            Dict with error information in standard format
        """
        return {
            "success": False,
            "crawler_name": self.get_name(),
            "error": str(error),
            "error_type": type(error).__name__,
            "execution_time_ms": execution_time,
            "timestamp": self.start_time.isoformat() if self.start_time else None,
            "data": None
        }
    
    def log_warning(self, message: str):
        """Log a warning message."""
        self.logger.warning(f"{self.get_name()}: {message}")
    
    def log_info(self, message: str):
        """Log an info message."""
        self.logger.info(f"{self.get_name()}: {message}")
    
    def log_error(self, message: str):
        """Log an error message."""
        self.logger.error(f"{self.get_name()}: {message}")
