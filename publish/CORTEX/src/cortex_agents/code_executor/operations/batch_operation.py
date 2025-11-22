"""Batch file operations."""

from typing import Dict, Any, List
from .base_operation import BaseOperation
from .create_operation import CreateOperation
from .edit_operation import EditOperation
from .delete_operation import DeleteOperation


class BatchOperation(BaseOperation):
    """Operation for executing multiple file operations in batch."""
    
    def __init__(self, backup_manager=None, validator=None):
        """Initialize batch operation with sub-operations."""
        super().__init__(backup_manager, validator)
        self.create_op = CreateOperation(backup_manager, validator)
        self.edit_op = EditOperation(backup_manager, validator)
        self.delete_op = DeleteOperation(backup_manager, validator)
    
    def get_operation_type(self) -> str:
        """Get operation type."""
        return "batch"
    
    def execute(self, file_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute multiple operations in batch.
        
        Args:
            file_path: Not used for batch operations
            context: Must contain 'operations' list
        
        Returns:
            Batch operation results
        """
        operations = context.get("operations", [])
        
        if not operations:
            return {
                "success": False,
                "message": "No operations provided for batch execution"
            }
        
        results = {
            "success": True,
            "files_modified": [],
            "operations_completed": 0,
            "operations_failed": 0,
            "details": []
        }
        
        for op in operations:
            op_type = op.get("operation", "edit")
            file_path = op.get("file_path")
            
            if not file_path:
                results["operations_failed"] += 1
                results["details"].append({
                    "operation": op_type,
                    "success": False,
                    "error": "No file_path provided"
                })
                continue
            
            # Execute operation
            if op_type == "create":
                result = self.create_op.execute(file_path, op)
            elif op_type == "edit":
                result = self.edit_op.execute(file_path, op)
            elif op_type == "delete":
                result = self.delete_op.execute(file_path, op)
            else:
                result = {"success": False, "message": f"Unknown operation: {op_type}"}
            
            # Track results
            if result.get("success"):
                results["operations_completed"] += 1
                if "file_path" in result:
                    results["files_modified"].append(result["file_path"])
            else:
                results["operations_failed"] += 1
                results["success"] = False
            
            results["details"].append({
                "operation": op_type,
                "file_path": file_path,
                **result
            })
        
        results["message"] = (
            f"Batch: {results['operations_completed']} succeeded, "
            f"{results['operations_failed']} failed"
        )
        
        return results
