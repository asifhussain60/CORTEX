"""
Log Manager - Group 2 cleanup (log management).

Handles:
- Application logs (rotation threshold: 10MB)
- Build system logs
- Session-level logs (retain 7 days)
- Refactor session reports (keep 3 most recent)
- Cleanup execution reports (keep 5 most recent)

Priority: MEDIUM (rotation, archiving, old log deletion)
Expected: ~10s execution, 250MB+ freed

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from src.orchestrators.cleanup.cleanup_engine import CleanupEngine


logger = logging.getLogger(__name__)


class LogManager:
    """
    Log management (Group 2) - Rotation, archiving, old log deletion.
    
    Categories:
    - logs: Application logs (rotation threshold: 10MB)
    - build_output: Build system logs
    - session_summaries: Session-level logs (retain 7 days)
    - system_refactor_reports: Refactor reports (keep 3 recent)
    - duplicate_cleanup_reports: Cleanup reports (keep 5 recent)
    """
    
    CATEGORIES = [
        "logs",
        "build_output",
        "session_summaries",
        "system_refactor_reports",
        "duplicate_cleanup_reports"
    ]
    
    def __init__(
        self,
        workspace_root: Path,
        rules_path: Path,
        config: Dict[str, Any]
    ):
        """
        Initialize log manager.
        
        Args:
            workspace_root: Workspace root directory
            rules_path: Path to cleanup-rules.yaml
            config: Orchestrator configuration
        """
        self.workspace_root = workspace_root
        self.rules_path = rules_path
        self.config = config
        
        # Get log rotation threshold from config
        self.rotation_threshold_mb = config.get('modes', {}).get('logs', {}).get(
            'log_rotation_threshold_mb', 10
        )
        
        # Initialize cleanup engine
        self.cleanup_engine = CleanupEngine(workspace_root, rules_path)
        
        logger.info(f"LogManager initialized (rotation threshold: {self.rotation_threshold_mb}MB)")
    
    def execute(self) -> Dict[str, Any]:
        """
        Execute log management.
        
        Returns:
            Cleanup result dictionary
        """
        logger.info("Starting log management (Group 2)")
        
        # Process log categories
        result = self.cleanup_engine.process_categories(self.CATEGORIES)
        
        # Apply log rotation to large logs
        rotated_logs = self._rotate_large_logs()
        
        # Add rotation info to result
        result['log_rotation'] = {
            'rotated_count': len(rotated_logs),
            'rotated_logs': rotated_logs
        }
        
        logger.info(
            f"Log management complete: {result['statistics']['files_deleted']} files, "
            f"{result['statistics']['space_freed_mb']:.2f} MB freed, "
            f"{len(rotated_logs)} logs rotated"
        )
        
        return result
    
    def _rotate_large_logs(self) -> List[Dict[str, Any]]:
        """
        Rotate logs larger than threshold.
        
        Returns:
            List of rotated log info
        """
        rotated = []
        threshold_bytes = self.rotation_threshold_mb * 1024 * 1024
        
        # Find all .log files in workspace
        for log_file in self.workspace_root.rglob('*.log'):
            if self.cleanup_engine._is_protected(log_file):
                continue
            
            try:
                size = log_file.stat().st_size
                if size > threshold_bytes:
                    # Archive the log
                    archive_path = self._archive_log(log_file)
                    
                    rotated.append({
                        'path': str(log_file.relative_to(self.workspace_root)),
                        'size_mb': size / (1024 * 1024),
                        'archived_to': str(archive_path.relative_to(self.workspace_root))
                    })
                    
                    logger.info(f"Rotated log: {log_file} ({size / (1024 * 1024):.2f} MB)")
            
            except Exception as e:
                logger.warning(f"Failed to rotate {log_file}: {e}")
        
        return rotated
    
    def _archive_log(self, log_file: Path) -> Path:
        """
        Archive a log file with timestamp.
        
        Args:
            log_file: Path to log file
        
        Returns:
            Path to archived file
        """
        import shutil
        import gzip
        
        # Create archive directory
        archive_dir = self.workspace_root / 'logs' / 'archive'
        archive_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate archive filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        archive_name = f"{log_file.stem}_{timestamp}.log.gz"
        archive_path = archive_dir / archive_name
        
        # Compress and archive
        with open(log_file, 'rb') as f_in:
            with gzip.open(archive_path, 'wb') as f_out:
                shutil.copyfileobj(f_in, f_out)
        
        # Truncate original log
        log_file.write_text("")
        
        return archive_path
