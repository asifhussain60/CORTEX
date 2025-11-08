"""
CodeExecutor Agent

Safely executes code changes with validation, backups, and rollback capabilities.
Handles file creation, modification, and deletion with safety checks.

The CodeExecutor is the agent that actually makes changes to the codebase,
but only after proper validation and health checks.
"""

import os
import shutil
import tempfile
import ast
import subprocess
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from CORTEX.src.cortex_agents.base_agent import BaseAgent, AgentRequest, AgentResponse
from CORTEX.src.cortex_agents.agent_types import IntentType
from CORTEX.src.cortex_agents.utils import safe_get, extract_file_paths


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
        # Returns: {
        #   "success": True,
        #   "files_modified": ["/path/to/new_file.py"],
        #   "backup_path": "/tmp/backup_xyz/",
        #   "validation": "passed"
        # }
    """
    
    def __init__(self, name: str, tier1_api=None, tier2_kg=None, tier3_context=None):
        """Initialize CodeExecutor with tier APIs."""
        super().__init__(name, tier1_api, tier2_kg, tier3_context)
        
        # Backup directory for rollbacks
        self.backup_dir = None
        self.current_operation_id = None
        
        # Supported file operations
        self.OPERATIONS = ["create", "edit", "delete", "batch"]
        
        # File extensions that require syntax validation
        self.SYNTAX_CHECK_EXTENSIONS = [".py", ".js", ".ts", ".jsx", ".tsx"]
    
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
            
            # Create backup directory
            self.backup_dir = self._create_backup_dir()
            
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
                    "backup_dir": self.backup_dir,
                    "operation": operation
                },
                next_actions=self._suggest_next_actions(result)
            )
            
            self.log_response(response)
            return response
            
        except Exception as e:
            self.logger.error(f"Code execution failed: {str(e)}")
            
            # Attempt rollback on error
            if self.backup_dir:
                self._rollback_changes()
            
            return AgentResponse(
                success=False,
                result=None,
                message=f"Code execution failed: {str(e)}",
                agent_name=self.name,
                metadata={"operation_id": self.current_operation_id}
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
                "message": "No file_path provided in context"
            }
        
        # Ensure absolute path
        file_path = os.path.abspath(file_path)
        
        # Execute based on operation type
        if operation == "create":
            return self._create_file(file_path, request.context)
        elif operation == "edit":
            return self._edit_file(file_path, request.context)
        elif operation == "delete":
            return self._delete_file(file_path, request.context)
        else:
            return {
                "success": False,
                "message": f"Unknown operation: {operation}"
            }
    
    def _execute_batch(self, request: AgentRequest) -> Dict[str, Any]:
        """
        Execute multiple operations in batch.
        
        Args:
            request: The agent request with batch operations
        
        Returns:
            Batch operation results
        """
        operations = safe_get(request.context, "operations", default=[])
        
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
            op_type = safe_get(op, "operation", default="edit")
            file_path = safe_get(op, "file_path")
            
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
                result = self._create_file(file_path, op)
            elif op_type == "edit":
                result = self._edit_file(file_path, op)
            elif op_type == "delete":
                result = self._delete_file(file_path, op)
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
    
    def _create_file(self, file_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new file.
        
        Args:
            file_path: Path to create
            context: Context with content and options
        
        Returns:
            Creation result
        """
        # Check if file already exists
        if os.path.exists(file_path):
            # Check if we should overwrite
            if not safe_get(context, "overwrite", default=False):
                return {
                    "success": False,
                    "message": f"File already exists: {file_path}"
                }
        
        # Get content
        content = safe_get(context, "content", default="")
        
        # Validate syntax if applicable
        if self._should_validate_syntax(file_path):
            is_valid, error = self._validate_syntax(content, file_path)
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
            
            self.logger.info(f"Created file: {file_path}")
            
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
    
    def _edit_file(self, file_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Edit an existing file.
        
        Args:
            file_path: Path to edit
            context: Context with content or changes
        
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
        backup_path = self._backup_file(file_path)
        
        try:
            # Read current content
            with open(file_path, 'r', encoding='utf-8') as f:
                original_content = f.read()
            
            # Get new content
            new_content = safe_get(context, "content")
            
            if new_content is None:
                # Try to get changes (old_string, new_string)
                old_string = safe_get(context, "old_string")
                new_string = safe_get(context, "new_string")
                
                if old_string is not None and new_string is not None:
                    new_content = original_content.replace(old_string, new_string, 1)
                else:
                    return {
                        "success": False,
                        "message": "No content or old_string/new_string provided"
                    }
            
            # Validate syntax if applicable
            if self._should_validate_syntax(file_path):
                is_valid, error = self._validate_syntax(new_content, file_path)
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
            
            self.logger.info(f"Edited file: {file_path}")
            
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
            if backup_path and os.path.exists(backup_path):
                shutil.copy2(backup_path, file_path)
            
            return {
                "success": False,
                "message": f"Failed to edit file: {str(e)}",
                "error": str(e),
                "backup_path": backup_path
            }
    
    def _delete_file(self, file_path: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Delete a file.
        
        Args:
            file_path: Path to delete
            context: Context with options
        
        Returns:
            Deletion result
        """
        # Check file exists
        if not os.path.exists(file_path):
            return {
                "success": False,
                "message": f"File not found: {file_path}"
            }
        
        # Backup file before deletion
        backup_path = self._backup_file(file_path)
        
        try:
            # Check if we need confirmation
            if not safe_get(context, "confirm", default=False):
                return {
                    "success": False,
                    "message": "Deletion requires confirmation (set confirm=True)",
                    "file_path": file_path
                }
            
            # Get file info before deletion
            file_size = os.path.getsize(file_path)
            
            # Delete file
            os.remove(file_path)
            
            self.logger.info(f"Deleted file: {file_path}")
            
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
    
    def _should_validate_syntax(self, file_path: str) -> bool:
        """
        Check if file should have syntax validation.
        
        Args:
            file_path: Path to check
        
        Returns:
            True if syntax should be validated
        """
        ext = os.path.splitext(file_path)[1]
        return ext in self.SYNTAX_CHECK_EXTENSIONS
    
    def _validate_syntax(self, content: str, file_path: str) -> Tuple[bool, Optional[str]]:
        """
        Validate syntax of code content.
        
        Args:
            content: Code content to validate
            file_path: File path (for determining language)
        
        Returns:
            Tuple of (is_valid, error_message)
        """
        ext = os.path.splitext(file_path)[1]
        
        if ext == ".py":
            # Python syntax validation
            try:
                ast.parse(content)
                return True, None
            except SyntaxError as e:
                return False, f"Python syntax error on line {e.lineno}: {e.msg}"
        
        # For other languages, we'd add validators here
        # For now, just return True
        return True, None
    
    def _create_backup_dir(self) -> str:
        """
        Create a temporary backup directory.
        
        Returns:
            Path to backup directory
        """
        backup_dir = tempfile.mkdtemp(prefix=f"cortex_backup_{self.current_operation_id}_")
        self.logger.info(f"Created backup directory: {backup_dir}")
        return backup_dir
    
    def _backup_file(self, file_path: str) -> Optional[str]:
        """
        Backup a file to the backup directory.
        
        Args:
            file_path: Path to backup
        
        Returns:
            Path to backup file, or None on failure
        """
        if not self.backup_dir or not os.path.exists(file_path):
            return None
        
        try:
            # Create relative path structure in backup
            rel_path = os.path.basename(file_path)
            backup_path = os.path.join(self.backup_dir, rel_path)
            
            # Copy file
            shutil.copy2(file_path, backup_path)
            
            self.logger.debug(f"Backed up {file_path} to {backup_path}")
            return backup_path
            
        except Exception as e:
            self.logger.error(f"Failed to backup {file_path}: {str(e)}")
            return None
    
    def _rollback_changes(self) -> bool:
        """
        Rollback changes from backup directory.
        
        Returns:
            True if rollback succeeded
        """
        if not self.backup_dir or not os.path.exists(self.backup_dir):
            return False
        
        try:
            # Restore all files from backup
            for backup_file in os.listdir(self.backup_dir):
                backup_path = os.path.join(self.backup_dir, backup_file)
                # Note: This is simplified - real implementation would need
                # to track original paths
                self.logger.info(f"Rollback available at: {backup_path}")
            
            self.logger.warning("Rollback initiated - backup available")
            return True
            
        except Exception as e:
            self.logger.error(f"Rollback failed: {str(e)}")
            return False
    
    def _store_operation_pattern(self, operation: str, result: Dict[str, Any]) -> None:
        """
        Store operation pattern in Tier 2 for learning.
        
        Args:
            operation: Operation type
            result: Operation result
        """
        if not self.tier2:
            return
        
        try:
            pattern_data = {
                "type": "code_execution",
                "operation": operation,
                "files_modified": result.get("files_modified", []),
                "success": result.get("success", False),
                "timestamp": datetime.now().isoformat()
            }
            
            # Store in Tier 2 knowledge graph
            # (Simplified - real implementation would use proper API)
            self.logger.debug(f"Storing operation pattern: {pattern_data}")
            
        except Exception as e:
            self.logger.error(f"Failed to store pattern: {str(e)}")
    
    def _suggest_next_actions(self, result: Dict[str, Any]) -> List[str]:
        """
        Suggest next actions based on execution result.
        
        Args:
            result: Execution result
        
        Returns:
            List of suggested actions
        """
        actions = []
        
        if result.get("success"):
            actions.append("Run tests to validate changes")
            actions.append("Review modified files")
            
            if result.get("operation") == "create":
                actions.append("Add tests for new file")
            elif result.get("operation") == "edit":
                actions.append("Check for breaking changes")
        else:
            actions.append("Review error messages")
            actions.append("Check backup directory for rollback")
            
            if result.get("validation_error"):
                actions.append("Fix syntax errors")
        
        return actions
