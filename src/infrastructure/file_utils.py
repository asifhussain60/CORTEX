"""
FileUtils - Atomic File Operations
Implements OE-005: All File Writes Must Be Atomic
"""

import os
import shutil
import tempfile
from pathlib import Path
from typing import Union, Optional, Any


class FileUtils:
    """
    Utility class for atomic file operations.
    
    Ensures file writes are atomic (all-or-nothing) to prevent:
    - Partial file writes on crash
    - Corrupted files
    - Lost data on interruption
    
    Pattern: Write to temp file → Rename to target (atomic on POSIX)
    """
    
    def atomic_write(
        self,
        target_path: Union[str, Path],
        content: Union[str, bytes],
        mode: str = 'w',
        encoding: str = 'utf-8'
    ) -> None:
        """
        Write content to file atomically.
        
        Args:
            target_path: Destination file path
            content: Content to write (str or bytes)
            mode: Write mode ('w' for text, 'wb' for binary)
            encoding: Text encoding (ignored for binary mode)
            
        Process:
            1. Write to temporary file in same directory
            2. If write succeeds, rename temp to target (atomic)
            3. If write fails, temp is cleaned up, target unchanged
        """
        target_path = Path(target_path)
        
        # Ensure parent directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create temp file in same directory (for atomic rename)
        temp_fd, temp_path = tempfile.mkstemp(
            dir=target_path.parent,
            prefix=f".{target_path.name}.",
            suffix=".tmp"
        )
        
        try:
            # Write to temp file
            if 'b' in mode:
                # Binary mode
                with os.fdopen(temp_fd, mode) as f:
                    f.write(content)
            else:
                # Text mode
                with os.fdopen(temp_fd, mode, encoding=encoding) as f:
                    f.write(content)
            
            # Atomic rename (POSIX guarantees atomicity)
            os.replace(temp_path, target_path)
            
        except Exception:
            # Clean up temp file on failure
            try:
                os.unlink(temp_path)
            except:
                pass
            raise
    
    def safe_delete(self, file_path: Union[str, Path]) -> bool:
        """
        Safely delete a file.
        
        Args:
            file_path: Path to file to delete
            
        Returns:
            True if deleted, False if file didn't exist
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return False
        
        try:
            file_path.unlink()
            return True
        except Exception:
            return False
    
    def safe_move(
        self,
        source: Union[str, Path],
        dest: Union[str, Path],
        overwrite: bool = False
    ) -> None:
        """
        Safely move a file.
        
        Args:
            source: Source file path
            dest: Destination file path
            overwrite: If True, overwrite destination if it exists
            
        Raises:
            FileExistsError: If dest exists and overwrite=False
        """
        source = Path(source)
        dest = Path(dest)
        
        if dest.exists() and not overwrite:
            raise FileExistsError(f"Destination {dest} already exists")
        
        # Ensure destination directory exists
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Use os.replace for atomic move (if on same filesystem)
        # Falls back to copy+delete for cross-filesystem moves
        shutil.move(str(source), str(dest))
    
    def safe_copy(
        self,
        source: Union[str, Path],
        dest: Union[str, Path],
        overwrite: bool = True
    ) -> None:
        """
        Safely copy a file.
        
        Args:
            source: Source file path
            dest: Destination file path
            overwrite: If True, overwrite destination if it exists
        """
        source = Path(source)
        dest = Path(dest)
        
        if dest.exists() and not overwrite:
            raise FileExistsError(f"Destination {dest} already exists")
        
        # Ensure destination directory exists
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(str(source), str(dest))
    
    def safe_read(
        self,
        file_path: Union[str, Path],
        mode: str = 'r',
        encoding: str = 'utf-8',
        default: Optional[Any] = None
    ) -> Optional[Union[str, bytes]]:
        """
        Safely read a file with optional default value.
        
        Args:
            file_path: Path to file to read
            mode: Read mode ('r' for text, 'rb' for binary)
            encoding: Text encoding (ignored for binary mode)
            default: Value to return if file doesn't exist
            
        Returns:
            File content or default value
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            return default
        
        try:
            if 'b' in mode:
                return file_path.read_bytes()
            else:
                return file_path.read_text(encoding=encoding)
        except Exception:
            return default
    
    def ensure_directory(self, dir_path: Union[str, Path]) -> None:
        """
        Ensure directory exists (create if needed).
        
        Args:
            dir_path: Directory path to ensure exists
        """
        dir_path = Path(dir_path)
        dir_path.mkdir(parents=True, exist_ok=True)
