"""
User Path Configuration Model

Pydantic schema for user-customizable file paths and directories.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from typing import Optional, Dict, Any
from pathlib import Path
from pydantic import BaseModel, Field, field_validator


class UserPathConfig(BaseModel):
    """
    User path configuration for customizable file locations.
    
    Attributes:
        test_directory: Where application tests should be created
        reports_directory: Where CORTEX generates reports
        documents_directory: Where CORTEX stores analysis and summaries
        planning_directory: Where feature plans are stored
        temp_directory: Temporary files location
        custom_paths: Additional user-defined paths
    """
    
    test_directory: Optional[str] = Field(
        default=None,
        description="Application test directory (e.g., 'tests/', 'test/', '__tests__/')"
    )
    
    reports_directory: Optional[str] = Field(
        default="cortex-brain/documents/reports",
        description="Where CORTEX generates validation and status reports"
    )
    
    documents_directory: Optional[str] = Field(
        default="cortex-brain/documents",
        description="Base directory for CORTEX-generated documents"
    )
    
    planning_directory: Optional[str] = Field(
        default="cortex-brain/documents/planning",
        description="Feature plans and ADO work items"
    )
    
    analysis_directory: Optional[str] = Field(
        default="cortex-brain/documents/analysis",
        description="Code analysis and architecture documents"
    )
    
    summaries_directory: Optional[str] = Field(
        default="cortex-brain/documents/summaries",
        description="Project summaries and progress reports"
    )
    
    investigations_directory: Optional[str] = Field(
        default="cortex-brain/documents/investigations",
        description="Bug investigations and issue analysis"
    )
    
    temp_directory: Optional[str] = Field(
        default=None,
        description="Temporary files directory"
    )
    
    custom_paths: Dict[str, str] = Field(
        default_factory=dict,
        description="Additional user-defined paths"
    )
    
    @field_validator("test_directory", "reports_directory", "documents_directory", 
                     "planning_directory", "analysis_directory", "summaries_directory",
                     "investigations_directory", "temp_directory")
    @classmethod
    def validate_path(cls, v: Optional[str]) -> Optional[str]:
        """Validate path format (no validation of existence)."""
        if v is None:
            return v
        
        # Basic validation: no invalid characters
        invalid_chars = ['<', '>', '|', '\0']
        if any(char in v for char in invalid_chars):
            raise ValueError(f"Path contains invalid characters: {v}")
        
        return v
    
    def get_test_directory(self, workspace_root: Optional[str] = None) -> str:
        """
        Get absolute test directory path.
        
        Args:
            workspace_root: Repository root (optional)
        
        Returns:
            Absolute path to test directory
        """
        if not self.test_directory:
            return str(Path(workspace_root or ".") / "tests")
        
        test_path = Path(self.test_directory)
        if test_path.is_absolute():
            return str(test_path)
        
        if workspace_root:
            return str(Path(workspace_root) / test_path)
        
        return str(test_path)
    
    def get_documents_directory(self, category: str = "") -> str:
        """
        Get absolute documents directory path for a specific category.
        
        Args:
            category: Document category (reports, analysis, summaries, etc.)
        
        Returns:
            Absolute path to documents directory
        """
        category_map = {
            "reports": self.reports_directory,
            "analysis": self.analysis_directory,
            "summaries": self.summaries_directory,
            "planning": self.planning_directory,
            "investigations": self.investigations_directory
        }
        
        if category and category in category_map:
            return category_map[category]
        
        return self.documents_directory
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for config storage."""
        return self.model_dump()
    
    class Config:
        """Pydantic model configuration."""
        json_schema_extra = {
            "example": {
                "test_directory": "tests",
                "reports_directory": "cortex-brain/documents/reports",
                "documents_directory": "cortex-brain/documents",
                "planning_directory": "cortex-brain/documents/planning",
                "analysis_directory": "cortex-brain/documents/analysis",
                "summaries_directory": "cortex-brain/documents/summaries",
                "investigations_directory": "cortex-brain/documents/investigations",
                "temp_directory": ".cortex-temp",
                "custom_paths": {
                    "logs": "logs",
                    "screenshots": "test-screenshots"
                }
            }
        }
