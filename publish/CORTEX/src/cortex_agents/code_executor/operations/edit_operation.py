"""Edit file operation."""

import os
from typing import Dict, Any
from .base_operation import BaseOperation


class EditOperation(BaseOperation):
    """Operation for editing existing files."""
    
    def get_operation_type(self) -> str:
        """Get operation type."""
        return "edit"
    
    def execute(self, file_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit an existing file.
        
        Args:
            file_path: Path to edit
            context: Must contain 'content' or 'old_string'/'new_string'
        
        Returns:
            Edit result
        """
        # Check file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": f"File not found: {file_path}"
            }
        
        # Backup original file
        backup_path = None
        if self.backup_manager:
            backup_path = self.backup_manager.backup_file(file_path)
        
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Get new content
            new_content = context.get("content")
            
            if new_content is None:
                # Try to get changes (old_string, new_string)
                old_string = context.get("old_string")
                new_string = context.get("new_string")
                
                if old_string is not None and new_string is not None:
                    new_content = original_content.replace(old_string, new_string, 1)
                else:
                    return {
                        "success": False,
                        "message": "No content or old_string/new_string provided"
                    }
            
            # Validate syntax if validator available
            if self.validator and self.validator.should_validate(file_path):
                is_valid, error = self.validator.validate(new_content, file_path)
                if not is_valid:
                    return {
                        "success": False,
                        "message": f"Syntax validation failed: {error}",
                        "validation_error": error,
                        "backup_path": backup_path
                    }
            
            # Write new content
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return {
                "success": True,
                "file_path": file_path,
                "operation": "edit",
                "backup_path": backup_path,
                "bytes_changed": abs(len(new_content.encode('utf-8')) - len(original_content.encode('utf-8'))),
                "message": f"Successfully edited {file_path}"
            }
            
        except Exception as e:
            # Restore from backup on error
            if self.backup_manager and backup_path:
                self.backup_manager.restore_file(backup_path, file_path)
            
            return {
                "success": False,
                "message": f"Failed to edit file: {str(e)}",
                "error": str(e),
                "backup_path": backup_path
            }
