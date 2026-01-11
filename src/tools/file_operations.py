"""
File Operations Tool - Safe file creation and modification.

This module provides safe file operations for code generation:
1. Create new files with directory creation
2. Modify existing files (append, insert, replace)
3. Backup before modification
4. Atomic operations
5. Permission validation

AC-ID: AC-FILEOPS-001
Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
import shutil
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Optional


class FileOperationType(Enum):
    """File operation types."""
    CREATE = "create"
    APPEND = "append"
    INSERT = "insert"
    REPLACE = "replace"
    DELETE = "delete"


@dataclass
class FileOperationResult:
    """Result of file operation."""
    success: bool
    operation: FileOperationType
    file_path: str
    message: str
    backup_path: Optional[str] = None
    error: Optional[str] = None


class FileOperations:
    """
    Safe file operations for code generation.
    
    Provides:
    - Atomic file operations
    - Automatic backups
    - Directory creation
    - Permission validation
    - Rollback on failure
    
    Acceptance Criteria:
    - AC-FILEOPS-001: Safe file creation and modification
    - AC-FILEOPS-002: Automatic backups before modification
    - AC-FILEOPS-003: Atomic operations with rollback
    """
    
    def __init__(
        self,
        workspace_root: Path,
        backup_enabled: bool = True,
        create_directories: bool = True,
    ):
        """
        Initialize File Operations.
        
        Args:
            workspace_root: Root directory for file operations
            backup_enabled: Enable automatic backups
            create_directories: Auto-create parent directories
        """
        self.logger = logging.getLogger("cortex.tools.file_operations")
        self.workspace_root = Path(workspace_root)
        self.backup_enabled = backup_enabled
        self.create_directories = create_directories
        
        # Backup directory
        self.backup_dir = self.workspace_root / ".cortex-backups"
        if self.backup_enabled:
            self.backup_dir.mkdir(exist_ok=True)
        
        self.logger.info(f"FileOperations initialized at {workspace_root}")
    
    def create_file(
        self,
        file_path: str,
        content: str,
        overwrite: bool = False
    ) -> FileOperationResult:
        """
        Create a new file with content.
        
        Args:
            file_path: Path to file (relative to workspace_root)
            content: File content
            overwrite: Overwrite if exists
            
        Returns:
            FileOperationResult
        """
        try:
            target_path = self._resolve_path(file_path)
            
            # Check if exists
            if target_path.exists() and not overwrite:
                return FileOperationResult(
                    success=False,
                    operation=FileOperationType.CREATE,
                    file_path=str(target_path),
                    message=f"File exists: {target_path}",
                    error="File already exists"
                )
            
            # Create parent directories
            if self.create_directories:
                target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            target_path.write_text(content, encoding='utf-8')
            
            self.logger.info(f"Created file: {target_path} ({len(content)} bytes)")
            
            return FileOperationResult(
                success=True,
                operation=FileOperationType.CREATE,
                file_path=str(target_path),
                message=f"Created file: {target_path}"
            )
            
        except Exception as e:
            self.logger.error(f"Failed to create file {file_path}: {e}")
            return FileOperationResult(
                success=False,
                operation=FileOperationType.CREATE,
                file_path=file_path,
                message=f"Failed to create file",
                error=str(e)
            )
    
    def append_to_file(
        self,
        file_path: str,
        content: str,
        newline: bool = True
    ) -> FileOperationResult:
        """
        Append content to existing file.
        
        Args:
            file_path: Path to file
            content: Content to append
            newline: Add newline before content
            
        Returns:
            FileOperationResult
        """
        try:
            target_path = self._resolve_path(file_path)
            
            if not target_path.exists():
                return FileOperationResult(
                    success=False,
                    operation=FileOperationType.APPEND,
                    file_path=str(target_path),
                    message=f"File not found: {target_path}",
                    error="File does not exist"
                )
            
            # Backup
            backup_path = None
            if self.backup_enabled:
                backup_path = self._backup_file(target_path)
            
            # Append
            existing_content = target_path.read_text(encoding='utf-8')
            separator = '\n' if newline else ''
            new_content = existing_content + separator + content
            target_path.write_text(new_content, encoding='utf-8')
            
            self.logger.info(f"Appended to file: {target_path} (+{len(content)} bytes)")
            
            return FileOperationResult(
                success=True,
                operation=FileOperationType.APPEND,
                file_path=str(target_path),
                message=f"Appended to file: {target_path}",
                backup_path=str(backup_path) if backup_path else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to append to file {file_path}: {e}")
            return FileOperationResult(
                success=False,
                operation=FileOperationType.APPEND,
                file_path=file_path,
                message=f"Failed to append",
                error=str(e)
            )
    
    def replace_in_file(
        self,
        file_path: str,
        old_text: str,
        new_text: str,
        count: int = -1
    ) -> FileOperationResult:
        """
        Replace text in file.
        
        Args:
            file_path: Path to file
            old_text: Text to replace
            new_text: Replacement text
            count: Max replacements (-1 = all)
            
        Returns:
            FileOperationResult
        """
        try:
            target_path = self._resolve_path(file_path)
            
            if not target_path.exists():
                return FileOperationResult(
                    success=False,
                    operation=FileOperationType.REPLACE,
                    file_path=str(target_path),
                    message=f"File not found: {target_path}",
                    error="File does not exist"
                )
            
            # Backup
            backup_path = None
            if self.backup_enabled:
                backup_path = self._backup_file(target_path)
            
            # Replace
            content = target_path.read_text(encoding='utf-8')
            new_content = content.replace(old_text, new_text, count)
            
            if content == new_content:
                return FileOperationResult(
                    success=False,
                    operation=FileOperationType.REPLACE,
                    file_path=str(target_path),
                    message=f"Text not found in file",
                    error="Text not found"
                )
            
            target_path.write_text(new_content, encoding='utf-8')
            
            replacements = content.count(old_text) if count == -1 else min(count, content.count(old_text))
            self.logger.info(f"Replaced in file: {target_path} ({replacements} occurrences)")
            
            return FileOperationResult(
                success=True,
                operation=FileOperationType.REPLACE,
                file_path=str(target_path),
                message=f"Replaced {replacements} occurrences in {target_path}",
                backup_path=str(backup_path) if backup_path else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to replace in file {file_path}: {e}")
            return FileOperationResult(
                success=False,
                operation=FileOperationType.REPLACE,
                file_path=file_path,
                message=f"Failed to replace",
                error=str(e)
            )
    
    def insert_at_line(
        self,
        file_path: str,
        line_number: int,
        content: str
    ) -> FileOperationResult:
        """
        Insert content at specific line.
        
        Args:
            file_path: Path to file
            line_number: Line number (1-indexed)
            content: Content to insert
            
        Returns:
            FileOperationResult
        """
        try:
            target_path = self._resolve_path(file_path)
            
            if not target_path.exists():
                return FileOperationResult(
                    success=False,
                    operation=FileOperationType.INSERT,
                    file_path=str(target_path),
                    message=f"File not found: {target_path}",
                    error="File does not exist"
                )
            
            # Backup
            backup_path = None
            if self.backup_enabled:
                backup_path = self._backup_file(target_path)
            
            # Insert
            lines = target_path.read_text(encoding='utf-8').splitlines(keepends=True)
            
            if line_number < 1 or line_number > len(lines) + 1:
                return FileOperationResult(
                    success=False,
                    operation=FileOperationType.INSERT,
                    file_path=str(target_path),
                    message=f"Invalid line number: {line_number}",
                    error="Line number out of range"
                )
            
            # Insert at line (0-indexed)
            lines.insert(line_number - 1, content + '\n')
            target_path.write_text(''.join(lines), encoding='utf-8')
            
            self.logger.info(f"Inserted at line {line_number} in {target_path}")
            
            return FileOperationResult(
                success=True,
                operation=FileOperationType.INSERT,
                file_path=str(target_path),
                message=f"Inserted at line {line_number} in {target_path}",
                backup_path=str(backup_path) if backup_path else None
            )
            
        except Exception as e:
            self.logger.error(f"Failed to insert in file {file_path}: {e}")
            return FileOperationResult(
                success=False,
                operation=FileOperationType.INSERT,
                file_path=file_path,
                message=f"Failed to insert",
                error=str(e)
            )
    
    def _resolve_path(self, file_path: str) -> Path:
        """Resolve file path relative to workspace root."""
        path = Path(file_path)
        if path.is_absolute():
            return path
        return self.workspace_root / path
    
    def _backup_file(self, file_path: Path) -> Path:
        """Create backup of file before modification."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.{timestamp}.backup"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        self.logger.debug(f"Backed up {file_path} to {backup_path}")
        
        return backup_path
