"""
Unit tests for Import Path Update & Validation.

Validates that:
- All import paths are correctly updated after folder migration
- No broken imports exist
- Full test suite passes
"""

import pytest
from cortex.infrastructure.import_path_updater import (
    ImportPathUpdater,
    ImportMapping
)


class TestImportPathUpdate:
    """Test suite for import path updates."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.updater = ImportPathUpdater()
    
    def test_add_import_mapping(self):
        """Test adding an import mapping."""
        self.updater.add_import_mapping(
            "from cortex.core import Orchestrator",
            "from cortex.core.orchestrator import Orchestrator",
            "src/main.py"
        )
        
        assert len(self.updater.import_mappings) == 1
        assert self.updater.import_mappings[0].old_import == \
               "from cortex.core import Orchestrator"
    
    def test_multiple_import_mappings(self):
        """Test adding multiple import mappings."""
        self.updater.add_import_mapping(
            "from cortex.core import X",
            "from cortex.core.module import X",
            "file1.py"
        )
        self.updater.add_import_mapping(
            "from cortex.api import Y",
            "from cortex.api.module import Y",
            "file2.py"
        )
        
        assert len(self.updater.import_mappings) == 2
    
    def test_scan_file_imports(self):
        """Test scanning file imports."""
        imports = [
            "from cortex.core import Orchestrator",
            "from cortex.api import APIHandler",
            "import sys"
        ]
        
        self.updater.scan_file_imports("src/main.py", imports)
        
        assert "src/main.py" in self.updater.files_with_imports
        assert len(self.updater.files_with_imports["src/main.py"]) == 3
    
    def test_update_imports_single_mapping(self):
        """Test updating imports with a single mapping."""
        imports = ["from cortex.core import Orchestrator"]
        self.updater.scan_file_imports("src/main.py", imports)
        self.updater.add_import_mapping(
            "from cortex.core import Orchestrator",
            "from cortex.core.orchestrator import Orchestrator",
            "src/main.py"
        )
        
        updated = self.updater.update_imports()
        
        assert updated["src/main.py"][0] == \
               "from cortex.core.orchestrator import Orchestrator"
    
    def test_update_imports_multiple_mappings(self):
        """Test updating imports with multiple mappings."""
        imports = [
            "from cortex.core import Orchestrator",
            "from cortex.api import APIHandler"
        ]
        self.updater.scan_file_imports("src/main.py", imports)
        self.updater.add_import_mapping(
            "from cortex.core import Orchestrator",
            "from cortex.core.orchestrator import Orchestrator",
            "src/main.py"
        )
        self.updater.add_import_mapping(
            "from cortex.api import APIHandler",
            "from cortex.api.handler import APIHandler",
            "src/main.py"
        )
        
        updated = self.updater.update_imports()
        
        assert updated["src/main.py"][0] == \
               "from cortex.core.orchestrator import Orchestrator"
        assert updated["src/main.py"][1] == \
               "from cortex.api.handler import APIHandler"
    
    def test_update_imports_unmapped_imports_preserved(self):
        """Test that unmapped imports are preserved."""
        imports = [
            "from cortex.core import Orchestrator",
            "import sys"
        ]
        self.updater.scan_file_imports("src/main.py", imports)
        self.updater.add_import_mapping(
            "from cortex.core import Orchestrator",
            "from cortex.core.orchestrator import Orchestrator",
            "src/main.py"
        )
        
        updated = self.updater.update_imports()
        
        assert "import sys" in updated["src/main.py"]
    
    def test_validate_imports_exist(self):
        """Test import validation."""
        modules = ["sys", "os", "src.core.orchestrator"]
        
        assert self.updater.validate_imports_exist(modules) is True
    
    def test_validate_imports_empty_fails(self):
        """Test that empty module names fail validation."""
        modules = ["", "sys"]
        
        assert self.updater.validate_imports_exist(modules) is False
    
    def test_check_no_broken_imports(self):
        """Test checking for broken imports."""
        imports = [
            "from cortex.core import Orchestrator",
            "import sys"
        ]
        self.updater.scan_file_imports("src/main.py", imports)
        self.updater.add_import_mapping(
            "from cortex.core import Orchestrator",
            "from cortex.core.orchestrator import Orchestrator",
            "src/main.py"
        )
        
        assert self.updater.check_no_broken_imports() is True
    
    def test_is_migration_valid_complete(self):
        """Test complete valid migration check."""
        imports = [
            "from cortex.core import Orchestrator",
            "from cortex.api import APIHandler"
        ]
        self.updater.scan_file_imports("src/main.py", imports)
        self.updater.add_import_mapping(
            "from cortex.core import Orchestrator",
            "from cortex.core.orchestrator import Orchestrator",
            "src/main.py"
        )
        self.updater.add_import_mapping(
            "from cortex.api import APIHandler",
            "from cortex.api.handler import APIHandler",
            "src/main.py"
        )
        
        assert self.updater.is_migration_valid() is True
    
    def test_is_migration_valid_no_mappings(self):
        """Test migration validity check fails without mappings."""
        self.updater.scan_file_imports("src/main.py", ["import sys"])
        
        assert self.updater.is_migration_valid() is False
    
    def test_is_migration_valid_no_files(self):
        """Test migration validity check fails without files."""
        self.updater.add_import_mapping("old", "new", "file.py")
        
        assert self.updater.is_migration_valid() is False
    
    def test_run_full_validation(self):
        """Test running full validation suite."""
        imports = ["from cortex.core import Orchestrator"]
        self.updater.scan_file_imports("src/main.py", imports)
        self.updater.add_import_mapping(
            "from cortex.core import Orchestrator",
            "from cortex.core.orchestrator import Orchestrator",
            "src/main.py"
        )
        
        results = self.updater.run_full_validation()
        
        assert 'import_mappings_count' in results
        assert 'files_scanned' in results
        assert 'no_broken_imports' in results
        assert 'all_imports_valid' in results
        assert 'migration_valid' in results
        assert 'test_suite_ready' in results
    
    def test_full_validation_success(self):
        """Test successful full validation."""
        imports = [
            "from cortex.core import Orchestrator",
            "from cortex.api import APIHandler"
        ]
        self.updater.scan_file_imports("src/main.py", imports)
        self.updater.add_import_mapping(
            "from cortex.core import Orchestrator",
            "from cortex.core.orchestrator import Orchestrator",
            "src/main.py"
        )
        self.updater.add_import_mapping(
            "from cortex.api import APIHandler",
            "from cortex.api.handler import APIHandler",
            "src/main.py"
        )
        
        results = self.updater.run_full_validation()
        
        assert results['migration_valid'] is True
        assert results['no_broken_imports'] is True
        assert results['test_suite_ready'] is True
    
    def test_comprehensive_migration_validation(self):
        """Test comprehensive migration validation scenario."""
        # Setup multiple files
        files_and_imports = {
            "src/main.py": [
                "from cortex.core import Orchestrator",
                "from cortex.api import APIHandler"
            ],
            "src/worker.py": [
                "from cortex.brain import Brain",
                "from cortex.tools import Tools"
            ]
        }
        
        # Scan files
        for file_path, imports in files_and_imports.items():
            self.updater.scan_file_imports(file_path, imports)
        
        # Add mappings
        self.updater.add_import_mapping(
            "from cortex.core import Orchestrator",
            "from cortex.core.orchestrator import Orchestrator",
            "src/main.py"
        )
        self.updater.add_import_mapping(
            "from cortex.api import APIHandler",
            "from cortex.api.handler import APIHandler",
            "src/main.py"
        )
        self.updater.add_import_mapping(
            "from cortex.brain import Brain",
            "from cortex.core.brain import Brain",
            "src/worker.py"
        )
        self.updater.add_import_mapping(
            "from cortex.tools import Tools",
            "from cortex.tools.impl import Tools",
            "src/worker.py"
        )
        
        # Validate
        results = self.updater.run_full_validation()
        
        assert results['import_mappings_count'] == 4
        assert results['files_scanned'] == 2
        assert results['migration_valid'] is True
        assert results['all_imports_valid'] is True
