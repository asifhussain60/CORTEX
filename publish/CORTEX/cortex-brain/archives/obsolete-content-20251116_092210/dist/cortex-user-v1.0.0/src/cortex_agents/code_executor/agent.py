"""CodeExecutor Agent - Coordinator."""

import os
from typing import Dict, Any
from datetime import datetime
from ..base_agent import BaseAgent, AgentRequest, AgentResponse
from ..agent_types import IntentType
from ..utils import safe_get

from .operations import (
    CreateOperation,
    EditOperation,
    DeleteOperation,
    BatchOperation
)
from .validators import SyntaxValidator
from .backup import BackupManager


class CodeExecutor(BaseAgent):
    """
    Executes code changes safely with validation and rollback.
    
    The CodeExecutor performs code modifications including:
    - File creation with template support
    - File editing with backup/rollback
    - File deletion with safety checks
    - Syntax validation before applying changes
    - Integration with HealthValidator
    
    Features:
    - Automatic backups before changes
    - Rollback on validation failures
    - Python syntax checking
    - Operation logging to all tiers
    - Batch operation support
    
    Example:
        executor = CodeExecutor(name="Executor", tier1_api, tier2_kg, tier3_context)
        
        request = AgentRequest(
            intent="execute_code",
            context={
                "operation": "create",
                "file_path": "/path/to/new_file.py",
                "content": "def hello(): pass"
            },
            user_message="Create a new Python file"
        )
        
        response = executor.execute(request)
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize CodeExecutor with tier APIs and operations."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Initialize components
        self.backup_manager = None
        self.validator = SyntaxValidator()
        self.current_operation_id = None
        
        # Initialize operations
        self.create_op = None
        self.edit_op = None
        self.delete_op = None
        self.batch_op = None
        
        # Supported file operations
        self.OPERATIONS = ["create", "edit", "delete", "batch"]
    
    def _initialize_operations(self):
        """Initialize operation handlers with current backup manager."""
        self.create_op = CreateOperation(self.backup_manager, self.validator)
        self.edit_op = EditOperation(self.backup_manager, self.validator)
        self.delete_op = DeleteOperation(self.backup_manager, self.validator)
        self.batch_op = BatchOperation(self.backup_manager, self.validator)
    
    def can_handle(self, request: AgentRequest) -> bool:
        """
        Check if this agent can handle the request.
        
        Args:
            request: The agent request
        
        Returns:
            True if intent is code, implement, or file operations
        """
        valid_intents = [
            IntentType.CODE.value,
            IntentType.IMPLEMENT.value,
            IntentType.CREATE_FILE.value,
            IntentType.EDIT_FILE.value,
            "execute",
            "write",
            "modify",
            "delete_file"
        ]
        return request.intent.lower() in valid_intents
    
    def execute(self, request: AgentRequest) -> AgentResponse:
        """
        Execute code changes safely.
        
        Args:
            request: The agent request
        
        Returns:
            AgentResponse with execution results
        """
        try:
            self.log_request(request)
            self.logger.info("Starting code execution")
            
            # Generate operation ID for tracking
            self.current_operation_id = f"op_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Create backup manager
            self.backup_manager = BackupManager(self.current_operation_id)
            self.backup_manager.create_backup_dir()
            
            # Initialize operations with backup manager
            self._initialize_operations()
            
            # Get operation details
            operation = safe_get(request.context, "operation", default="edit").lower()
            
            if operation not in self.OPERATIONS:
                return AgentResponse(
                    success=False,
                    result=None,
                    message=f"Unknown operation: {operation}. Valid: {self.OPERATIONS}",
                    agent_name=self.name
                )
            
            # Execute the operation
            if operation == "batch":
                result = self._execute_batch(request)
            else:
                result = self._execute_single_operation(request, operation)
            
            # Log to Tier 1 if available
            if self.tier1 and request.conversation_id:
                self.tier1.process_message(
                    request.conversation_id,
                    "agent",
                    f"CodeExecutor: {operation} on {len(result.get('files_modified', []))} files"
                )
            
            # Store operation in Tier 2 for learning
            if self.tier2 and result.get("success"):
                self._store_operation_pattern(operation, result)
            
            response = AgentResponse(
                success=result.get("success", False),
                result=result,
                message=result.get("message", "Operation completed"),
                agent_name=self.name,
                metadata={
                    "operation_id": self.current_operation_id,
                    "backup_dir": self.backup_manager.get_backup_dir(),
                    "operation": operation
                },
                next_actions=self._suggest_next_actions(result)
            )
            
            self.log_response(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Code execution failed: {str(e)}")
            
            # Attempt rollback on error
            if self.backup_manager:
                self.backup_manager.rollback_all()
            
            return AgentResponse(
                success=False,
                result=None,
                message=f"Code execution failed: {str(e)}",
                agent_name=self.name,
                metadata={"operation_id": self.current_operation_id},
                error=str(e)
            )
    
    def _execute_single_operation(
        self,
        request: AgentRequest,
        operation: str
    ) -> Dict[str, Any]:
        """
        Execute a single file operation.
        
        Args:
            request: The agent request
            operation: Operation type (create, edit, delete)
        
        Returns:
            Operation result dictionary
        """
        file_path = safe_get(request.context, "file_path")
        
        if not file_path:
            return {
                "success": False,
                "message": "No file_path provided in context",
                "files_modified": []
            }
        
        # Ensure absolute path
        file_path = os.path.abspath(file_path)
        
        # Execute based on operation type
        if operation == "create":
            result = self.create_op.execute(file_path, request.context)
        elif operation == "edit":
            result = self.edit_op.execute(file_path, request.context)
        elif operation == "delete":
            result = self.delete_op.execute(file_path, request.context)
        else:
            result = {
                "success": False,
                "message": f"Unknown operation: {operation}"
            }
        
        # Add files_modified list for consistency
        if result.get("success") and "files_modified" not in result:
            result["files_modified"] = [file_path]
        elif "files_modified" not in result:
            result["files_modified"] = []
        
        return result
    
    def _execute_batch(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Execute multiple operations in batch.
        
        Args:
            request: The agent request with batch operations
        
        Returns:
            Batch operation results
        """
        return self.batch_op.execute("", request.context)
    
    def _store_operation_pattern(self, operation: str, result: Dict[str, Any]) -> None:
        """
        Store operation pattern in Tier 2 for learning.
        
        Args:
            operation: Operation type
            result: Operation result
        """
        try:
            files_modified = result.get("files_modified", [])
            success_rate = 1.0 if result.get("success") else 0.0
            
            pattern = {
                "type": "code_execution",
                "operation": operation,
                "files_count": len(files_modified),
                "success_rate": success_rate,
                "scope": "cortex"
            }
            
            self.tier2.store_pattern(
                pattern_type="execution",
                pattern_data=pattern,
                confidence=success_rate,
                scope="cortex"
            )
        except Exception:
            # Silently fail - pattern storage is optional
            pass
    
    def _suggest_next_actions(self, result: Dict[str, Any]) -> list:
        """
        Suggest next actions based on operation result.
        
        Args:
            result: Operation result
        
        Returns:
            List of suggested actions
        """
        suggestions = []
        
        if result.get("success"):
            files = result.get("files_modified", [])
            if files:
                suggestions.append(f"Verify changes in {len(files)} file(s)")
                suggestions.append("Run tests to ensure changes work")
                suggestions.append("Commit changes if validation passes")
        else:
            suggestions.append("Review error message")
            if result.get("backup_path"):
                suggestions.append("Restore from backup if needed")
            suggestions.append("Fix issues and retry operation")
        
        return suggestions
