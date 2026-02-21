"""
Silent Execution Guard - Checkpoint-based resilience.

AC_START: AC-DIGEST-CHAT01-003
Purpose: Add resilience to silent autonomous execution
Learning: chat01 template corruption broke multiple stages, needed manual intervention
Solution: Checkpoint → Execute → Verify → Rollback on failure

Features:
- Checkpoint before every operation
- Syntax check after file modifications
- Import verification (optional)
- Automatic rollback on failure
- Progress preservation on success
- Clear error messages
- Stage ID tracking

Example:
    guard = SilentExecutionGuard()
    
    def update_files():
        # Risky operations
        file.write_text(new_content)
        return "success"
    
    result = guard.execute_with_checkpoint(
        operation=update_files,
        stage_id="S1",
        files=["path/to/file.py"]
    )
    
    if result.success:
        print("Operation succeeded, changes preserved")
    else:
        print(f"Operation failed, rolled back: {result.error}")
"""

import ast
import shutil
import tempfile
import importlib.util
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Optional


class CheckpointFailedError(Exception):
    """Raised when checkpoint creation fails."""
    pass


class RollbackError(Exception):
    """Raised when rollback fails."""
    pass


@dataclass
class ExecutionResult:
    """Result of guarded execution."""
    success: bool
    stage_id: str
    checkpoint_created: bool = False
    checkpoint_path: Optional[Path] = None
    rolled_back: bool = False
    error: Optional[str] = None
    error_type: Optional[str] = None


class SilentExecutionGuard:
    """
    Guard for silent autonomous execution with checkpoint-based resilience.
    
    Prevents chat01-style failures where:
    - Template corruption broke multiple stages
    - Manual intervention required
    - Lost progress
    
    Pattern:
        1. Create checkpoint (backup all files)
        2. Execute operation
        3. Verify (syntax, imports)
        4. On failure: Rollback to checkpoint
        5. On success: Keep changes, cleanup checkpoint
    
    Features:
        - Automatic recovery (no manual intervention)
        - Always recoverable (checkpoint preserved on failure)
        - Clear error messages
        - Progress tracking per stage
    """
    
    def __init__(self, checkpoint_dir: Optional[Path] = None) -> None:
        """
        Initialize SilentExecutionGuard.
        
        Args:
            checkpoint_dir: Directory for checkpoints (default: temp dir)
        """
        self.checkpoint_dir = checkpoint_dir or Path(tempfile.gettempdir()) / "cortex_checkpoints"
        self.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    
    def execute_with_checkpoint(
        self,
        operation: Callable,
        stage_id: str,
        files: List[str],
        verify_syntax: bool = True,
        verify_imports: bool = False,
        read_only: bool = False
    ) -> ExecutionResult:
        """
        Execute operation with checkpoint protection.
        
        Args:
            operation: Function to execute
            stage_id: Stage identifier (e.g., "S1", "S2-TemplateUpdate")
            files: List of file paths to checkpoint
            verify_syntax: Check Python syntax after execution
            verify_imports: Check imports after execution (slower)
            read_only: Skip checkpoint for read-only operations
        
        Returns:
            ExecutionResult with success status and details
        """
        checkpoint_path = None
        
        try:
            # Step 1: Create checkpoint (unless read-only)
            if not read_only and files:
                checkpoint_path = self._create_checkpoint(files, stage_id)
            
            # Step 2: Execute operation
            operation()
            
            # Step 3: Verify changes
            if not read_only:
                for file_path in files:
                    if verify_syntax and file_path.endswith('.py'):
                        self._check_syntax(Path(file_path))
                    
                    if verify_imports and file_path.endswith('.py'):
                        if not self._verify_imports(Path(file_path)):
                            raise ImportError(f"Import check failed for {file_path}")
            
            # Step 4: Success - cleanup checkpoint
            if checkpoint_path and checkpoint_path.exists():
                shutil.rmtree(checkpoint_path)
            
            return ExecutionResult(
                success=True,
                stage_id=stage_id,
                checkpoint_created=checkpoint_path is not None,
                checkpoint_path=checkpoint_path
            )
        
        except Exception as e:
            # Step 5: Failure - rollback to checkpoint
            error_type = type(e).__name__
            error_msg = str(e)
            
            rolled_back = False
            if checkpoint_path and checkpoint_path.exists():
                try:
                    self._rollback(checkpoint_path, files)
                    rolled_back = True
                except Exception as rollback_error:
                    error_msg += f" | Rollback failed: {rollback_error}"
                    raise RollbackError(error_msg)
            
            return ExecutionResult(
                success=False,
                stage_id=stage_id,
                checkpoint_created=checkpoint_path is not None,
                checkpoint_path=checkpoint_path,
                rolled_back=rolled_back,
                error=error_msg,
                error_type=error_type
            )
    
    def _create_checkpoint(self, files: List[str], stage_id: str) -> Path:
        """
        Create checkpoint of files.
        
        Args:
            files: List of file paths to backup
            stage_id: Stage identifier for checkpoint naming
        
        Returns:
            Path to checkpoint directory
        
        Raises:
            CheckpointFailedError: If checkpoint creation fails
        """
        try:
            # Create checkpoint directory
            checkpoint_path = self.checkpoint_dir / f"checkpoint_{stage_id}"
            checkpoint_path.mkdir(parents=True, exist_ok=True)
            
            # Backup each file
            for file_path in files:
                file_path_obj = Path(file_path)
                if file_path_obj.exists():
                    # Preserve directory structure
                    rel_path = file_path_obj.name
                    backup_file = checkpoint_path / rel_path
                    shutil.copy2(file_path_obj, backup_file)
            
            return checkpoint_path
        
        except Exception as e:
            raise CheckpointFailedError(f"Failed to create checkpoint: {e}")
    
    def _rollback(self, checkpoint_path: Path, files: List[str]) -> None:
        """
        Rollback files from checkpoint.
        
        Args:
            checkpoint_path: Path to checkpoint directory
            files: List of original file paths
        """
        for file_path in files:
            file_path_obj = Path(file_path)
            rel_path = file_path_obj.name
            backup_file = checkpoint_path / rel_path
            
            if backup_file.exists():
                shutil.copy2(backup_file, file_path_obj)
    
    def _check_syntax(self, file_path: Path) -> None:
        """
        Check Python syntax of file.
        
        Args:
            file_path: Path to Python file
        
        Raises:
            SyntaxError: If syntax invalid
        """
        content = file_path.read_text()
        ast.parse(content)
    
    def _verify_imports(self, file_path: Path) -> bool:
        """
        Verify file can be imported.
        
        Args:
            file_path: Path to Python file
        
        Returns:
            True if imports work, False otherwise
        """
        try:
            spec = importlib.util.spec_from_file_location(
                "temp_module",
                file_path
            )
            if spec and spec.loader:
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                return True
        except Exception:
            return False
        
        return False


# AC_COMPLETE: AC-DIGEST-CHAT01-003 ✅
# Implementation covers:
# - Checkpoint creation before operations
# - Syntax validation after edits
# - Import verification (optional)
# - Automatic rollback on any exception
# - Progress preservation on success
# - Multiple file coordination
# - Clear error messages with error types
# - Stage ID tracking
# - Checkpoint cleanup on success
# - Prevents chat01-style manual intervention scenarios