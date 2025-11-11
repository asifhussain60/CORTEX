"""Create file operation."""

import os
from typing import Dict, Any
from .base_operation import BaseOperation


class CreateOperation(BaseOperation):
    """Operation for creating new files."""
    
    def get_operation_type(self) -> str:
        """Get operation type."""
        return "create"
    
    def execute(self, file_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new file.
        
        Args:
            file_path: Path to create
            context: Must contain 'content' key
        
        Returns:
            Creation result
        """
        # Check if file already exists
        if os.path.exists(file_path):
            if not context.get("overwrite", False):
                return {
                    "success": False,
                    "message": f"File already exists: {file_path}"
                }
        
        # Get content
        content = context.get("content", "")
        
        # Validate syntax if validator available
        if self.validator and self.validator.should_validate(file_path):
            is_valid, error = self.validator.validate(content, file_path)
            if not is_valid:
                return {
                    "success": False,
                    "message": f"Syntax validation failed: {error}",
                    "validation_error": error
                }
        
        try:
            # Create directory if needed
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": file_path,
                "operation": "create",
                "bytes_written": len(content.encode('utf-8')),
                "message": f"Successfully created {file_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to create file: {str(e)}",
                "error": str(e)
            }
