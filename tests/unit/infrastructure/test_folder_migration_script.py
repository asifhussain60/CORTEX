"""
Unit tests for Automated Folder Migration Script.

Validates the migration script that:
- Migrates files from flat to nested structure
- Verifies file integrity
- Generates comprehensive migration reports
"""

import pytest
from cortex.infrastructure.folder_migration_script import (
    FolderMigrationScript,
    FileIntegrityRecord
)


class TestFolderMigrationScript:
    """Test suite for folder migration script."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.script = FolderMigrationScript()
    
    def test_add_file_mapping(self):
        """Test that file mappings can be added."""
        self.script.add_file_mapping('old/file.py', 'new/file.py')
        
        assert 'old/file.py' in self.script.file_mappings
        assert self.script.file_mappings['old/file.py'] == 'new/file.py'
    
    def test_multiple_file_mappings(self):
        """Test that multiple file mappings can be added."""
        self.script.add_file_mapping('old/file1.py', 'new/file1.py')
        self.script.add_file_mapping('old/file2.py', 'new/file2.py')
        self.script.add_file_mapping('old/file3.py', 'new/file3.py')
        
        assert len(self.script.file_mappings) == 3
    
    def test_calculate_file_hash(self):
        """Test that file hashes can be calculated."""
        content = "def hello(): pass"
        hash1 = self.script.calculate_file_hash(content)
        hash2 = self.script.calculate_file_hash(content)
        
        assert hash1 == hash2
        assert len(hash1) == 64  # SHA256 is 64 hex characters
    
    def test_file_hash_differs_for_different_content(self):
        """Test that different content produces different hashes."""
        hash1 = self.script.calculate_file_hash("content1")
        hash2 = self.script.calculate_file_hash("content2")
        
        assert hash1 != hash2
    
    def test_verify_file_integrity_match(self):
        """Test integrity verification when hashes match."""
        content = "def test(): pass"
        
        record = self.script.verify_file_integrity(
            content,
            content,
            'test.py'
        )
        
        assert record.status == 'OK'
        assert record.original_hash == record.migrated_hash
    
    def test_verify_file_integrity_mismatch(self):
        """Test integrity verification when hashes don't match."""
        original = "def original(): pass"
        modified = "def modified(): pass"
        
        record = self.script.verify_file_integrity(
            original,
            modified,
            'test.py'
        )
        
        assert record.status == 'MISMATCH'
        assert record.original_hash != record.migrated_hash
    
    def test_integrity_check_recorded(self):
        """Test that integrity checks are recorded."""
        self.script.verify_file_integrity(
            "content",
            "content",
            'file1.py'
        )
        self.script.verify_file_integrity(
            "content",
            "content",
            'file2.py'
        )
        
        assert len(self.script.integrity_checks) == 2
    
    def test_generate_migration_report(self):
        """Test that migration report can be generated."""
        self.script.add_file_mapping('old/file.py', 'new/file.py')
        self.script.verify_file_integrity(
            "content",
            "content",
            'file.py'
        )
        
        report = self.script.generate_migration_report()
        
        assert 'total_files_migrated' in report
        assert 'integrity_checks_performed' in report
        assert 'success_rate' in report
        assert report['total_files_migrated'] == 1
    
    def test_migration_report_success_rate_calculation(self):
        """Test that success rate is correctly calculated."""
        self.script.add_file_mapping('file1.py', 'new/file1.py')
        self.script.add_file_mapping('file2.py', 'new/file2.py')
        
        self.script.verify_file_integrity("content", "content", 'file1.py')
        self.script.verify_file_integrity("wrong", "content", 'file2.py')
        
        report = self.script.generate_migration_report()
        
        assert report['success_rate'] == 0.5
        assert report['integrity_ok_count'] == 1
        assert report['integrity_mismatch_count'] == 1
    
    def test_migration_report_includes_file_mappings(self):
        """Test that migration report includes file mappings."""
        self.script.add_file_mapping('old/file.py', 'new/file.py')
        self.script.verify_file_integrity(
            "content",
            "content",
            'file.py'
        )
        
        report = self.script.generate_migration_report()
        
        assert 'file_mappings' in report
        assert len(report['file_mappings']) == 1
    
    def test_migration_report_includes_integrity_issues(self):
        """Test that migration report lists integrity issues."""
        self.script.add_file_mapping('file.py', 'new/file.py')
        self.script.verify_file_integrity(
            "original",
            "modified",
            'file.py'
        )
        
        report = self.script.generate_migration_report()
        
        assert 'integrity_issues' in report
        assert len(report['integrity_issues']) == 1
        assert report['integrity_issues'][0]['status'] == 'MISMATCH'
    
    def test_validate_migration_complete_success(self):
        """Test successful migration validation."""
        self.script.add_file_mapping('file1.py', 'new/file1.py')
        self.script.add_file_mapping('file2.py', 'new/file2.py')
        
        self.script.verify_file_integrity("content", "content", 'file1.py')
        self.script.verify_file_integrity("content", "content", 'file2.py')
        
        assert self.script.validate_migration_complete() is True
    
    def test_validate_migration_complete_with_mismatch(self):
        """Test migration validation fails with integrity mismatch."""
        self.script.add_file_mapping('file.py', 'new/file.py')
        self.script.verify_file_integrity("original", "modified", 'file.py')
        
        assert self.script.validate_migration_complete() is False
    
    def test_validate_migration_complete_with_no_mappings(self):
        """Test migration validation fails when no mappings exist."""
        assert self.script.validate_migration_complete() is False
    
    def test_validate_migration_complete_with_unchecked_files(self):
        """Test migration validation fails with unchecked files."""
        self.script.add_file_mapping('file1.py', 'new/file1.py')
        self.script.add_file_mapping('file2.py', 'new/file2.py')
        
        # Only verify one file
        self.script.verify_file_integrity("content", "content", 'file1.py')
        
        assert self.script.validate_migration_complete() is False
    
    def test_comprehensive_migration_scenario(self):
        """Test comprehensive migration scenario with multiple files."""
        # Setup multiple files
        files = [
            ('src/module1.py', 'src/core/module1.py'),
            ('src/module2.py', 'src/orchestrators/module2.py'),
            ('tests/test_module1.py', 'tests/unit/test_module1.py'),
        ]
        
        for source, target in files:
            self.script.add_file_mapping(source, target)
        
        # Simulate integrity checks
        for source, _ in files:
            self.script.verify_file_integrity("content", "content", source)
        
        # Validate
        report = self.script.generate_migration_report()
        
        assert report['total_files_migrated'] == 3
        assert report['integrity_checks_performed'] == 3
        assert report['success_rate'] == 1.0
        assert self.script.validate_migration_complete() is True
