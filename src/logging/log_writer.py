"""
Log Writer - Async disk I/O with rotation and compression.

Features:
- Async file writes with aiofiles
- Daily rotation by orchestrator
- Size-based rotation
- Gzip compression for rotated files
- Automatic cleanup based on retention policy
"""

import asyncio
import gzip
import json
import logging
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
import threading


logger = logging.getLogger(__name__)


class LogWriter:
    """
    Async log writer with rotation and compression.
    
    File structure:
    {log_dir}/{orchestrator}/{YYYY-MM-DD}-{session}.jsonl
    
    Rotation:
    - Daily (new file per date)
    - Size-based (configurable threshold)
    - Compressed backups (.jsonl.gz)
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize log writer.
        
        Args:
            config: Configuration dictionary:
                - log_dir: Base directory for logs
                - rotation_size_mb: Size threshold for rotation
                - backup_count: Number of backup files to keep
                - compression_enabled: Enable gzip compression
        """
        self.log_dir = Path(config.get("log_dir", "logs/audit"))
        self.rotation_size_mb = config.get("rotation_size_mb", 10)
        self.rotation_size_bytes = self.rotation_size_mb * 1024 * 1024
        self.backup_count = config.get("backup_count", 5)
        self.compression_enabled = config.get("compression_enabled", True)
        
        # Create log directory
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Track open file handles
        self._file_handles: Dict[str, Any] = {}
        self._lock = threading.RLock()
    
    def _get_log_file_path(self, orchestrator: str) -> Path:
        """
        Get log file path for orchestrator with daily rotation.
        
        Args:
            orchestrator: Orchestrator name
            
        Returns:
            Path to log file
        """
        date_str = datetime.now().strftime('%Y-%m-%d')
        orchestrator_dir = self.log_dir / orchestrator
        orchestrator_dir.mkdir(parents=True, exist_ok=True)
        
        return orchestrator_dir / f"{date_str}.jsonl"
    
    def _should_rotate(self, file_path: Path) -> bool:
        """
        Check if file should be rotated based on size.
        
        Args:
            file_path: Path to log file
            
        Returns:
            True if rotation needed
        """
        if not file_path.exists():
            return False
        
        size_bytes = file_path.stat().st_size
        return size_bytes >= self.rotation_size_bytes
    
    def _rotate_file(self, file_path: Path):
        """
        Rotate log file (rename with timestamp).
        
        Args:
            file_path: Path to log file
        """
        if not file_path.exists():
            return
        
        # Generate timestamped backup name
        timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        backup_path = file_path.with_suffix(f'.{timestamp}.jsonl')
        
        # Rename current file
        file_path.rename(backup_path)
        
        # Compress if enabled
        if self.compression_enabled:
            self._compress_file(backup_path)
        
        # Cleanup old backups
        self._cleanup_old_backups(file_path.parent)
    
    def _compress_file(self, file_path: Path):
        """
        Compress file with gzip.
        
        Args:
            file_path: Path to file to compress
        """
        try:
            compressed_path = file_path.with_suffix(file_path.suffix + '.gz')
            
            with open(file_path, 'rb') as f_in:
                with gzip.open(compressed_path, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remove original file
            file_path.unlink()
            
            logger.debug(f"Compressed {file_path} -> {compressed_path}")
        except Exception as e:
            logger.error(f"Compression error for {file_path}: {e}")
    
    def _cleanup_old_backups(self, directory: Path):
        """
        Remove old backup files exceeding backup_count.
        
        Args:
            directory: Directory containing backup files
        """
        try:
            # Find all backup files (with timestamps)
            backup_files = sorted(
                directory.glob('*.*.jsonl*'),
                key=lambda p: p.stat().st_mtime,
                reverse=True  # Newest first
            )
            
            # Remove excess backups
            for backup_file in backup_files[self.backup_count:]:
                backup_file.unlink()
                logger.debug(f"Removed old backup: {backup_file}")
        except Exception as e:
            logger.error(f"Backup cleanup error for {directory}: {e}")
    
    async def write_batch(self, entries: List[Dict[str, Any]]):
        """
        Write batch of log entries asynchronously.
        
        Args:
            entries: List of log entries to write
        """
        if not entries:
            return
        
        # Group entries by orchestrator
        by_orchestrator: Dict[str, List[Dict[str, Any]]] = {}
        for entry in entries:
            orchestrator = entry.get("orchestrator", "unknown")
            if orchestrator not in by_orchestrator:
                by_orchestrator[orchestrator] = []
            by_orchestrator[orchestrator].append(entry)
        
        # Write each orchestrator's entries
        tasks = []
        for orchestrator, orch_entries in by_orchestrator.items():
            tasks.append(self._write_orchestrator_batch(orchestrator, orch_entries))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _write_orchestrator_batch(self, orchestrator: str, entries: List[Dict[str, Any]]):
        """
        Write batch of entries for specific orchestrator.
        
        Args:
            orchestrator: Orchestrator name
            entries: Log entries to write
        """
        try:
            file_path = self._get_log_file_path(orchestrator)
            
            # Check if rotation needed
            if self._should_rotate(file_path):
                self._rotate_file(file_path)
            
            # Write entries
            async with asyncio.Lock():
                with open(file_path, 'a', encoding='utf-8') as f:
                    for entry in entries:
                        json_line = json.dumps(entry, ensure_ascii=False)
                        f.write(json_line + '\n')
        except Exception as e:
            logger.error(f"Write error for {orchestrator}: {e}")
    
    def write_batch_sync(self, entries: List[Dict[str, Any]]):
        """
        Write batch of log entries synchronously.
        
        Args:
            entries: List of log entries to write
        """
        if not entries:
            return
        
        # Group entries by orchestrator
        by_orchestrator: Dict[str, List[Dict[str, Any]]] = {}
        for entry in entries:
            orchestrator = entry.get("orchestrator", "unknown")
            if orchestrator not in by_orchestrator:
                by_orchestrator[orchestrator] = []
            by_orchestrator[orchestrator].append(entry)
        
        # Write each orchestrator's entries
        for orchestrator, orch_entries in by_orchestrator.items():
            self._write_orchestrator_batch_sync(orchestrator, orch_entries)
    
    def _write_orchestrator_batch_sync(self, orchestrator: str, entries: List[Dict[str, Any]]):
        """
        Write batch of entries for specific orchestrator synchronously.
        
        Args:
            orchestrator: Orchestrator name
            entries: Log entries to write
        """
        try:
            file_path = self._get_log_file_path(orchestrator)
            
            # Check if rotation needed
            if self._should_rotate(file_path):
                self._rotate_file(file_path)
            
            # Write entries
            with self._lock:
                with open(file_path, 'a', encoding='utf-8') as f:
                    for entry in entries:
                        json_line = json.dumps(entry, ensure_ascii=False)
                        f.write(json_line + '\n')
        except Exception as e:
            logger.error(f"Sync write error for {orchestrator}: {e}")
    
    async def rotate(self):
        """Manually trigger rotation for all log files."""
        for orchestrator_dir in self.log_dir.iterdir():
            if orchestrator_dir.is_dir():
                for log_file in orchestrator_dir.glob('*.jsonl'):
                    if self._should_rotate(log_file):
                        self._rotate_file(log_file)
    
    async def close(self):
        """Close all file handles and cleanup."""
        # Close any open handles
        with self._lock:
            for handle in self._file_handles.values():
                try:
                    handle.close()
                except Exception:
                    pass
            self._file_handles.clear()
    
    def close_sync(self):
        """Close all file handles synchronously."""
        with self._lock:
            for handle in self._file_handles.values():
                try:
                    handle.close()
                except Exception:
                    pass
            self._file_handles.clear()
