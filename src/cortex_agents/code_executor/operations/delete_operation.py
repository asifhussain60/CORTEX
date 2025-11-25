"""Delete file operation."""

import os
from typing import Dict, Any
from .base_operation import BaseOperation


class DeleteOperation(BaseOperation):
    """Operation for deleting files."""
    
    def get_operation_type(self) -> str:
        """Get operation type."""
        return "delete"
    
    def execute(self, file_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a file.
        
        Args:
            file_path: Path to delete
            context: Must contain 'confirm' = True
        
        Returns:
            Deletion result
        """
        # Check file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": f"File not found: {file_path}"
            }
        
        # Check if we need confirmation
        if not context.get("confirm", False):
            return {
                "success": False,
                "message": "Deletion requires confirmation (set confirm=True)",
                "file_path": file_path
            }
        
        # Backup file before deletion
        backup_path = None
        if self.backup_manager:
            backup_path = self.backup_manager.backup_file(file_path)
        
        try:
            # Get file info before deletion
            file_size = os.path.getsize(file_path)
            
            # Delete file
            os.remove(file_path)
            
            return {
                "success": True,
                "file_path": file_path,
                "operation": "delete",
                "backup_path": backup_path,
                "bytes_deleted": file_size,
                "message": f"Successfully deleted {file_path}"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"Failed to delete file: {str(e)}",
                "error": str(e),
                "backup_path": backup_path
            }
