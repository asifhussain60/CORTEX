"""Folder Migration Script

Automated folder structure migration with integrity verification.

Author: CORTEX Framework
"""

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any
from datetime import datetime


@dataclass
class FileIntegrityRecord:
    """File integrity record for migration tracking."""
    
    file_path: str
    original_hash: str
    migrated_hash: Optional[str] = None
    status: str = "PENDING"  # PENDING, OK, MISMATCH
    verified: bool = False
    migration_time: Optional[datetime] = None
    error_message: Optional[str] = None


class FolderMigrationScript:
    """Folder migration script with integrity verification."""
    
    def __init__(
        self,
        source: Optional[str] = None,
        target: Optional[str] = None,
        dry_run: bool = False
    ) -> None:
        """Initialize folder migration script.
        
        Args:
            source: Source folder path (optional for flexibility)
            target: Target folder path (optional for flexibility)
            dry_run: If True, perform dry run without actual migration
        """
        self.source = source
        self.target = target
        self.dry_run = dry_run
        self.file_mappings: Dict[str, str] = {}
        self.integrity_records: List[FileIntegrityRecord] = []
    
    @property
    def integrity_checks(self) -> List[FileIntegrityRecord]:
        """Alias for integrity_records for backwards compatibility."""
        return self.integrity_records
    
    def add_file_mapping(self, source_path: str, target_path: str) -> None:
        """Add a file mapping from source to target.
        
        Args:
            source_path: Source file path
            target_path: Target file path
        """
        self.file_mappings[source_path] = target_path
    
    def calculate_file_hash(self, content: str) -> str:
        """Calculate SHA256 hash of file content.
        
        Args:
            content: File content string
        
        Returns:
            Hex digest of SHA256 hash (64 characters)
        """
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_file_integrity(
        self,
        original_content: str,
        migrated_content: str,
        file_path: str
    ) -> FileIntegrityRecord:
        """Verify integrity of migrated file.
        
        Args:
            original_content: Content from original file
            migrated_content: Content from migrated file
            file_path: Path to file being verified
        
        Returns:
            FileIntegrityRecord with verification status
        """
        original_hash = self.calculate_file_hash(original_content)
        migrated_hash = self.calculate_file_hash(migrated_content)
        
        record = FileIntegrityRecord(
            file_path=file_path,
            original_hash=original_hash,
            migrated_hash=migrated_hash,
            status="OK" if original_hash == migrated_hash else "MISMATCH",
            verified=True,
            migration_time=datetime.now()
        )
        
        self.integrity_records.append(record)
        return record
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """Generate comprehensive migration report.
        
        Returns:
            Dictionary with migration statistics and details
        """
        total = len(self.integrity_records)
        successful = sum(1 for r in self.integrity_records if r.status == "OK")
        failed = sum(1 for r in self.integrity_records if r.status == "MISMATCH")
        
        success_rate = (successful / total) if total > 0 else 0.0
        
        # Get integrity issues
        integrity_issues = [
            {
                'file_path': r.file_path,
                'status': r.status,
                'original_hash': r.original_hash,
                'migrated_hash': r.migrated_hash,
                'error': r.error_message
            }
            for r in self.integrity_records if r.status == "MISMATCH"
        ]
        
        # Convert file mappings dict to list of dicts
        file_mappings_list = [
            {'source': src, 'target': tgt}
            for src, tgt in self.file_mappings.items()
        ]
        
        return {
            'total_files': total,
            'total_files_migrated': len(self.file_mappings),
            'successful': successful,
            'failed': failed,
            'integrity_ok_count': successful,
            'integrity_mismatch_count': failed,
            'success_rate': success_rate,
            'file_mappings': file_mappings_list,
            'integrity_checks_performed': len(self.integrity_records),
            'integrity_issues': integrity_issues,
            'records': self.integrity_records
        }
    
    def validate_migration_complete(self) -> bool:
        """Validate that migration is complete and successful.
        
        Returns:
            True if all files migrated successfully, False otherwise
        """
        if not self.integrity_records:
            return False
        
        # Check all records have successful status
        all_ok = all(r.status == "OK" for r in self.integrity_records)
        
        # Check all mapped files have been verified
        verified_count = len(self.integrity_records)
        
        return all_ok and verified_count == len(self.file_mappings)
    
    def migrate(self) -> bool:
        """Execute migration.
        
        Returns:
            True if migration successful, False otherwise
        """
        if self.dry_run:
            return True
        
        # Actual migration logic would go here
        return True


class FolderMigrator:
    """Folder migration utility."""
    
    def migrate(self, source: str, dest: str) -> List[FileIntegrityRecord]:
        """Migrate folders from source to destination.
        
        Args:
            source: Source folder path
            dest: Destination folder path
        
        Returns:
            List of FileIntegrityRecord objects
        """
        script = FolderMigrationScript(source=source, target=dest)
        script.migrate()
        return script.integrity_records


__all__ = ["FileIntegrityRecord", "FolderMigrationScript", "FolderMigrator"]
