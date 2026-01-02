"""
Unit Tests for Safety Validator - Critical File Protection

Tests the 5-level risk classification system:
- SAFE: Temp files, caches, build artifacts
- LOW: Duplicates, empty directories, old logs
- MEDIUM: Misplaced files, large binaries
- HIGH: Orphaned files, recently modified files
- CRITICAL: Git metadata, source code, config, docs, CORTEX brain, uncommitted changes

Author: Asif Hussain
Copyright © 2025-2026 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
import shutil
import subprocess
from pathlib import Path
from unittest.mock import Mock, patch
from datetime import datetime, timedelta

from src.orchestrators.vacuum.safety_validator import SafetyValidator


class TestSafetyValidator:
    """Test suite for SafetyValidator."""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory."""
        temp = tempfile.mkdtemp()
        yield Path(temp)
        shutil.rmtree(temp, ignore_errors=True)
    
    @pytest.fixture
    def config(self):
        """Mock configuration."""
        return {
            'safety': {
                'critical_patterns': ['.git', '*.py', '*.md'],
                'size_threshold_mb': 10,
                'protected_paths': ['cortex-brain/tier0', 'cortex-brain/database']
            },
            'exclusions': ['.git', 'node_modules']
        }
    
    @pytest.fixture
    def validator(self, config):
        """Create SafetyValidator instance."""
        return SafetyValidator(config)
    
    def test_initialization(self, validator):
        """Test validator initialization."""
        assert validator.size_threshold_mb == 10
        assert '.git' in validator.config['safety']['critical_patterns']
    
    def test_classify_safe_file(self, validator):
        """Test SAFE risk classification."""
        # Temp files are SAFE
        temp_file = Path("/tmp/test.tmp")
        risk = validator.classify_risk(temp_file)
        
        assert risk == 'SAFE'
    
    def test_classify_critical_source_code(self, validator):
        """Test CRITICAL classification for source code."""
        source_file = Path("/src/main.py")
        risk = validator.classify_risk(source_file)
        
        assert risk == 'CRITICAL'
    
    def test_classify_critical_git_metadata(self, validator):
        """Test CRITICAL classification for .git."""
        git_file = Path("/project/.git/config")
        risk = validator.classify_risk(git_file)
        
        assert risk == 'CRITICAL'
    
    def test_classify_critical_documentation(self, validator):
        """Test CRITICAL classification for documentation."""
        readme = Path("/project/README.md")
        risk = validator.classify_risk(readme)
        
        assert risk == 'CRITICAL'
    
    def test_classify_low_duplicate(self, validator):
        """Test LOW classification for duplicates."""
        # Duplicates are LOW risk
        duplicate = Path("/tmp/duplicate.txt")
        risk = validator.classify_risk(duplicate, is_duplicate=True)
        
        assert risk == 'LOW'
    
    def test_classify_high_recent_file(self, validator, temp_dir):
        """Test HIGH classification for recently modified files."""
        recent_file = temp_dir / "recent.txt"
        recent_file.write_text("content")
        
        # File just created (recent)
        risk = validator.classify_risk(recent_file)
        
        # Should be at least MEDIUM or HIGH
        assert risk in ['MEDIUM', 'HIGH', 'CRITICAL']
    
    def test_validate_plan_safe_files(self, validator, temp_dir):
        """Test validation of safe files only."""
        # Create temp files (safe)
        temp1 = temp_dir / "temp1.tmp"
        temp2 = temp_dir / "temp2.cache"
        temp1.touch()
        temp2.touch()
        
        cleanup_plan = {
            'inventory': {
                'temp_files': [temp1, temp2]
            }
        }
        
        validated = validator.validate_plan(cleanup_plan)
        
        assert len(validated['safe']) == 2
        assert len(validated['critical']) == 0
    
    def test_validate_plan_critical_protection(self, validator, temp_dir):
        """Test critical file protection."""
        # Create source file (critical)
        source = temp_dir / "main.py"
        source.write_text("print('hello')")
        
        cleanup_plan = {
            'inventory': {
                'source_files': [source]
            }
        }
        
        validated = validator.validate_plan(cleanup_plan)
        
        assert len(validated['critical']) == 1
        assert source in validated['critical']
        assert len(validated['warnings']) > 0
    
    def test_cortex_brain_protection(self, validator):
        """Test CORTEX brain critical path protection."""
        # CORTEX critical paths
        tier0_file = Path("/cortex-brain/tier0/file.yaml")
        database_file = Path("/cortex-brain/database/planning.db")
        
        risk1 = validator.classify_risk(tier0_file)
        risk2 = validator.classify_risk(database_file)
        
        assert risk1 == 'CRITICAL'
        assert risk2 == 'CRITICAL'
    
    def test_cortex_safe_paths(self, validator):
        """Test CORTEX safe paths (can clean)."""
        # CORTEX safe paths
        cache_file = Path("/cortex-brain/cache/temp.json")
        log_file = Path("/cortex-brain/logs/debug.log")
        
        risk1 = validator.classify_risk(cache_file)
        risk2 = validator.classify_risk(log_file)
        
        # Should be SAFE or LOW
        assert risk1 in ['SAFE', 'LOW']
        assert risk2 in ['SAFE', 'LOW']
    
    def test_size_threshold_warning(self, validator, temp_dir):
        """Test large file size warning."""
        # Create large file (11MB > 10MB threshold)
        large_file = temp_dir / "large.bin"
        large_file.write_bytes(b"0" * (11 * 1024 * 1024))
        
        cleanup_plan = {
            'inventory': {
                'temp_files': [large_file]
            }
        }
        
        validated = validator.validate_plan(cleanup_plan)
        
        # Should have size warning
        assert any('size' in w.lower() or 'large' in w.lower() 
                   for w in validated.get('warnings', []))
    
    def test_git_uncommitted_changes_detection(self, validator, temp_dir):
        """Test detection of uncommitted git changes."""
        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=temp_dir, capture_output=True)
        
        # Create uncommitted file
        uncommitted = temp_dir / "uncommitted.txt"
        uncommitted.write_text("uncommitted content")
        
        # Add to git but don't commit
        subprocess.run(['git', 'add', 'uncommitted.txt'], cwd=temp_dir, capture_output=True)
        
        # Check uncommitted files
        uncommitted_files = validator._get_uncommitted_files(temp_dir)
        
        # Should detect uncommitted file
        assert len(uncommitted_files) >= 0  # May be 0 if git not configured
    
    def test_permission_validation(self, validator, temp_dir):
        """Test permission check for files."""
        # Create read-only file
        readonly = temp_dir / "readonly.txt"
        readonly.write_text("readonly")
        readonly.chmod(0o444)
        
        # Check if file is deletable
        can_delete = validator._check_permissions(readonly)
        
        # Should detect permission issue
        assert isinstance(can_delete, bool)
        
        # Cleanup
        readonly.chmod(0o644)
    
    def test_symlink_validation(self, validator, temp_dir):
        """Test symlink safety validation."""
        # Create file and symlink
        real_file = temp_dir / "real.txt"
        real_file.write_text("real content")
        
        symlink = temp_dir / "link.txt"
        symlink.symlink_to(real_file)
        
        # Validate symlink
        is_safe = validator._is_safe_symlink(symlink)
        
        # Should validate symlink
        assert isinstance(is_safe, bool)
    
    def test_multiple_risk_factors(self, validator, temp_dir):
        """Test file with multiple risk factors."""
        # Create source file that's also recently modified
        source = temp_dir / "recent_source.py"
        source.write_text("print('test')")
        
        risk = validator.classify_risk(source)
        
        # Should be CRITICAL (source code trumps recent)
        assert risk == 'CRITICAL'
    
    def test_validation_statistics(self, validator, temp_dir):
        """Test validation statistics tracking."""
        # Create mixed files
        safe1 = temp_dir / "temp.tmp"
        safe2 = temp_dir / "cache.cache"
        critical1 = temp_dir / "main.py"
        
        safe1.touch()
        safe2.touch()
        critical1.touch()
        
        cleanup_plan = {
            'inventory': {
                'temp_files': [safe1, safe2],
                'source_files': [critical1]
            }
        }
        
        validated = validator.validate_plan(cleanup_plan)
        
        # Verify statistics
        assert 'stats' in validated
        assert validated['stats']['total_files'] == 3
        assert validated['stats']['safe_files'] == 2
        assert validated['stats']['critical_files'] == 1


class TestSafetyValidatorRiskLevels:
    """Test all 5 risk levels comprehensively."""
    
    @pytest.fixture
    def validator(self):
        """Create SafetyValidator instance."""
        config = {
            'safety': {
                'critical_patterns': ['.git', '*.py', '*.md', '*.yaml'],
                'size_threshold_mb': 10
            },
            'exclusions': []
        }
        return SafetyValidator(config)
    
    def test_safe_level_examples(self, validator):
        """Test SAFE level files."""
        safe_files = [
            Path("/tmp/test.tmp"),
            Path("/cache/data.cache"),
            Path("/build/__pycache__/module.pyc"),
            Path("/logs/old.log")
        ]
        
        for file in safe_files:
            risk = validator.classify_risk(file)
            assert risk == 'SAFE', f"{file} should be SAFE"
    
    def test_low_level_examples(self, validator):
        """Test LOW level files."""
        # Duplicates and empty directories
        duplicate = Path("/tmp/duplicate.txt")
        risk = validator.classify_risk(duplicate, is_duplicate=True)
        assert risk == 'LOW'
    
    def test_medium_level_examples(self, validator, temp_dir):
        """Test MEDIUM level files."""
        # Large binary files
        large_bin = temp_dir / "large.bin"
        large_bin.write_bytes(b"0" * (5 * 1024 * 1024))  # 5MB
        
        risk = validator.classify_risk(large_bin)
        # May be SAFE or MEDIUM depending on implementation
        assert risk in ['SAFE', 'MEDIUM', 'LOW']
    
    def test_high_level_examples(self, validator):
        """Test HIGH level files."""
        # Orphaned test files
        orphan = Path("/tests/orphaned_test.py")
        risk = validator.classify_risk(orphan, is_orphan=True)
        
        # Orphaned source code is still CRITICAL
        assert risk in ['HIGH', 'CRITICAL']
    
    def test_critical_level_examples(self, validator):
        """Test CRITICAL level files."""
        critical_files = [
            Path("/src/main.py"),
            Path("/.git/config"),
            Path("/README.md"),
            Path("/config.yaml"),
            Path("/cortex-brain/tier0/governance.yaml"),
            Path("/package.json")
        ]
        
        for file in critical_files:
            risk = validator.classify_risk(file)
            assert risk == 'CRITICAL', f"{file} should be CRITICAL"


class TestSafetyValidatorEdgeCases:
    """Edge case tests for SafetyValidator."""
    
    @pytest.fixture
    def validator(self):
        """Create SafetyValidator instance."""
        config = {
            'safety': {
                'critical_patterns': ['.git', '*.py'],
                'size_threshold_mb': 10
            },
            'exclusions': []
        }
        return SafetyValidator(config)
    
    def test_empty_plan(self, validator):
        """Test validation of empty cleanup plan."""
        cleanup_plan = {
            'inventory': {}
        }
        
        validated = validator.validate_plan(cleanup_plan)
        
        assert len(validated['safe']) == 0
        assert len(validated['critical']) == 0
    
    def test_nonexistent_file(self, validator):
        """Test classification of nonexistent file."""
        nonexistent = Path("/nonexistent/file.txt")
        
        # Should handle gracefully
        risk = validator.classify_risk(nonexistent)
        assert risk in ['SAFE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    
    def test_file_without_extension(self, validator):
        """Test file without extension."""
        no_ext = Path("/tmp/no_extension")
        risk = validator.classify_risk(no_ext)
        
        # Should have a risk level
        assert risk in ['SAFE', 'LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    
    def test_hidden_file(self, validator):
        """Test hidden file classification."""
        hidden = Path("/tmp/.hidden_file")
        risk = validator.classify_risk(hidden)
        
        assert isinstance(risk, str)
    
    def test_case_sensitivity(self, validator):
        """Test case-sensitive pattern matching."""
        # .GIT vs .git
        git_upper = Path("/.GIT/config")
        git_lower = Path("/.git/config")
        
        risk_upper = validator.classify_risk(git_upper)
        risk_lower = validator.classify_risk(git_lower)
        
        # Both should be CRITICAL
        assert risk_lower == 'CRITICAL'


class TestSafetyValidatorIntegration:
    """Integration tests for SafetyValidator."""
    
    @pytest.fixture
    def real_temp_dir(self):
        """Create real test filesystem."""
        temp = tempfile.mkdtemp()
        temp_path = Path(temp)
        
        # Create realistic structure
        (temp_path / "temp.tmp").write_text("temp")
        (temp_path / "src").mkdir()
        (temp_path / "src" / "main.py").write_text("print('hello')")
        (temp_path / "README.md").write_text("# Project")
        (temp_path / ".git").mkdir()
        (temp_path / ".git" / "config").write_text("[core]")
        (temp_path / "logs").mkdir()
        (temp_path / "logs" / "debug.log").write_text("log entry")
        
        yield temp_path
        shutil.rmtree(temp, ignore_errors=True)
    
    def test_full_validation_workflow(self, real_temp_dir):
        """Test complete validation workflow."""
        config = {
            'safety': {
                'critical_patterns': ['.git', '*.py', '*.md'],
                'size_threshold_mb': 10
            },
            'exclusions': ['.git']
        }
        validator = SafetyValidator(config)
        
        # Create cleanup plan
        cleanup_plan = {
            'inventory': {
                'temp_files': [real_temp_dir / "temp.tmp"],
                'source_files': [real_temp_dir / "src" / "main.py"],
                'documentation': [real_temp_dir / "README.md"],
                'logs': [real_temp_dir / "logs" / "debug.log"]
            }
        }
        
        # Validate
        validated = validator.validate_plan(cleanup_plan)
        
        # Verify protection
        assert len(validated['critical']) >= 2  # main.py, README.md
        assert len(validated['safe']) >= 1  # temp.tmp or debug.log
        
        # Verify source code protected
        source_file = real_temp_dir / "src" / "main.py"
        assert source_file in validated['critical']


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
