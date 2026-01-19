"""
Automated Folder Migration Script Implementation.

Provides the FolderMigrationScript class that automates migration
of files between folder structures with integrity verification.
"""

import hashlib
from dataclasses import dataclass, field
from typing import Dict, List, Any


@dataclass
class FileIntegrityRecord:
    """Record of a file's integrity check."""
    path: str
    original_hash: str
    migrated_hash: str
    status: str


class FolderMigrationScript:
    """Automated script for migrating files between folder structures."""
    
    def __init__(self):
        """Initialize the migration script."""
        self.file_mappings: Dict[str, str] = {}
        self.integrity_checks: List[FileIntegrityRecord] = []
        self.migration_report: Dict[str, Any] = {}
    
    def add_file_mapping(self, source_path: str, target_path: str) -> None:
        """
        Add a file mapping from source to target location.
        
        Args:
            source_path: Current file path
            target_path: New file path after migration
        """
        self.file_mappings[source_path] = target_path
    
    def calculate_file_hash(self, content: str) -> str:
        """
        Calculate SHA256 hash of file content.
        
        Args:
            content: File content
            
        Returns:
            Hexadecimal hash string
        """
        return hashlib.sha256(content.encode()).hexdigest()
    
    def verify_file_integrity(
        self,
        original_content: str,
        migrated_content: str,
        file_path: str
    ) -> FileIntegrityRecord:
        """
        Verify that file content matches before and after migration.
        
        Args:
            original_content: Content before migration
            migrated_content: Content after migration
            file_path: Path to the file
            
        Returns:
            FileIntegrityRecord with status
        """
        original_hash = self.calculate_file_hash(original_content)
        migrated_hash = self.calculate_file_hash(migrated_content)
        
        status = 'OK' if original_hash == migrated_hash else 'MISMATCH'
        
        record = FileIntegrityRecord(
            path=file_path,
            original_hash=original_hash,
            migrated_hash=migrated_hash,
            status=status
        )
        
        self.integrity_checks.append(record)
        return record
    
    def generate_migration_report(self) -> Dict[str, Any]:
        """
        Generate comprehensive migration report.
        
        Returns:
            Dictionary containing migration statistics and details
        """
        total_files = len(self.file_mappings)
        integrity_ok = sum(
            1 for check in self.integrity_checks if check.status == 'OK'
        )
        integrity_mismatches = sum(
            1 for check in self.integrity_checks if check.status == 'MISMATCH'
        )
        
        self.migration_report = {
            'total_files_migrated': total_files,
            'integrity_checks_performed': len(self.integrity_checks),
            'integrity_ok_count': integrity_ok,
            'integrity_mismatch_count': integrity_mismatches,
            'success_rate': (
                integrity_ok / len(self.integrity_checks)
                if self.integrity_checks
                else 0
            ),
            'file_mappings': self.file_mappings,
            'integrity_issues': [
                {
                    'path': check.path,
                    'status': check.status
                }
                for check in self.integrity_checks
                if check.status != 'OK'
            ]
        }
        
        return self.migration_report
    
    def validate_migration_complete(self) -> bool:
        """
        Validate that migration completed successfully.
        
        Returns:
            True if all files migrated with integrity verified, False otherwise
        """
        if not self.file_mappings:
            return False
        
        if len(self.integrity_checks) != len(self.file_mappings):
            return False
        
        return all(check.status == 'OK' for check in self.integrity_checks)
