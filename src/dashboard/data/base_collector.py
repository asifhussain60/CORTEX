"""
Base Data Collector

Base class for specialized dashboard data collectors.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict, Any, Optional


class BaseDataCollector(ABC):
    """
    Abstract base class for dashboard data collectors.
    
    All specialized collectors inherit from this class and implement
    the collect() method.
    """
    
    def __init__(self, project_root: Path):
        """
        Initialize base collector.
        
        Args:
            project_root: Path to project root directory
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.project_root = Path(project_root)
        self.logger.info(f"{self.__class__.__name__} initialized at {project_root}")
    
    @abstractmethod
    def collect(self) -> Optional[Dict[str, Any]]:
        """
        Collect data for dashboard visualization.
        
        Returns:
            Dictionary with collected data or None if collection fails
            
        Raises:
            NotImplementedError: If subclass doesn't implement this method
        """
        pass
    
    def _file_exists(self, rel_path: str) -> bool:
        """Check if file exists relative to project root."""
        return (self.project_root / rel_path).exists()
    
    def _read_file(self, rel_path: str) -> Optional[str]:
        """
        Read file content relative to project root.
        
        Args:
            rel_path: Relative path from project root
            
        Returns:
            File content as string or None if file doesn't exist
        """
        file_path = self.project_root / rel_path
        if not file_path.exists():
            self.logger.warning(f"File not found: {file_path}")
            return None
        
        try:
            return file_path.read_text(encoding='utf-8')
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return None
    
    def _safe_parse_json(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Safely parse JSON content.
        
        Args:
            content: JSON string
            
        Returns:
            Parsed dict or None if parsing fails
        """
        import json
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            self.logger.error(f"JSON parse error: {e}")
            return None
    
    def _safe_parse_yaml(self, content: str) -> Optional[Dict[str, Any]]:
        """
        Safely parse YAML content.
        
        Args:
            content: YAML string
            
        Returns:
            Parsed dict or None if parsing fails
        """
        try:
            import yaml
            return yaml.safe_load(content)
        except Exception as e:
            self.logger.error(f"YAML parse error: {e}")
            return None
