"""
Incremental Writer Utility

Provides incremental file writing without full rewrites for large files.
Part of Phase 4: Incremental Planning System (Deliverable 4.1)

Author: CORTEX TDD Workflow
Created: 2024-01-28
"""

from pathlib import Path
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class IncrementalWriter:
    """
    Utility for incremental file writing without full rewrites.
    
    Prevents data loss during planning by:
    - Creating empty files with metadata first
    - Appending sections incrementally
    - Tracking last section for resumability
    """
    
    def __init__(self, file_path: Path):
        """
        Initialize incremental writer.
        
        Args:
            file_path: Path to file for incremental writing
        """
        self.file_path = file_path
        self.logger = logging.getLogger(__name__)
    
    def create_empty(self, metadata: Dict[str, Any]) -> None:
        """
        Create empty file with metadata only.
        
        Args:
            metadata: Initial metadata (feature_name, created_at, etc.)
        """
        self.logger.info(f"Creating empty plan file: {self.file_path}")
        
        # Ensure parent directory exists
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create YAML structure with metadata
        yaml_content = "metadata:\n"
        for key, value in metadata.items():
            yaml_content += f"  {key}: {value}\n"
        yaml_content += "\nphases:\n"
        
        self.file_path.write_text(yaml_content, encoding='utf-8')
        self.logger.debug(f"Created empty plan with metadata: {list(metadata.keys())}")
    
    def append_section(self, section_name: str, content: str) -> None:
        """
        Append content to specific section.
        
        Args:
            section_name: Section identifier (e.g., "phase_1", "requirements")
            content: Content to append
        """
        self.logger.debug(f"Appending to section '{section_name}' in {self.file_path}")
        
        if not self.file_path.exists():
            raise FileNotFoundError(f"Plan file does not exist: {self.file_path}")
        
        # Append content with proper indentation (YAML list format)
        indented_content = ""
        for line in content.strip().split('\n'):
            if line.strip():
                indented_content += f"  {line}\n"
        
        # Append to file
        with open(self.file_path, 'a', encoding='utf-8') as f:
            f.write(indented_content)
        
        self.logger.debug(f"Appended {len(content)} chars to '{section_name}'")
    
    def get_last_section_count(self, section_name: str) -> int:
        """
        Count items in section for resumability.
        
        Args:
            section_name: Section identifier
        
        Returns:
            Number of items in section
        """
        if not self.file_path.exists():
            return 0
        
        try:
            import yaml
            content = self.file_path.read_text(encoding='utf-8')
            data = yaml.safe_load(content)
            
            if data is None or section_name not in data:
                return 0
            
            section_data = data[section_name]
            
            if isinstance(section_data, list):
                return len(section_data)
            
            return 0
            
        except Exception as e:
            self.logger.error(f"Error counting items in '{section_name}': {e}")
            return 0
