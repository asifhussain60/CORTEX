"""Test suite for safe file rename tool (NAMING-004).

Tests automated file renaming with import updates across codebase.
Phase 7.4, Task NAMING-004
"""

import pytest
from pathlib import Path
import tempfile
import shutil
from cortex.tools.safe_file_rename import (
    SafeFileRenamer,
    RenameResult,
    RenameError,
)


@pytest.fixture
def temp_workspace():
    """Create temporary workspace for testing."""
    temp_dir = tempfile.mkdtemp()
    workspace = Path(temp_dir)
    
    # Create sample file structure
    (workspace / "src").mkdir()
    (workspace / "tests").mkdir()
    
    # Create file to rename
    old_file = workspace / "src" / "old_module_name.py"
    old_file.write_text("""'''Old module docstring.'''

def hello_world():
    return 'Hello from old module'
""")
    
    # Create file that imports the old module
    importer = workspace / "src" / "importer.py"
    importer.write_text("""from old_module_name import hello_world

def use_hello():
    return hello_world()
""")
    
    # Create test file
    test_file = workspace / "tests" / "test_old_module_name.py"
    test_file.write_text("""import pytest
from src.old_module_name import hello_world

def test_hello():
    assert hello_world() == 'Hello from old module'
""")
    
    yield workspace
    shutil.rmtree(temp_dir)


@pytest.fixture
def renamer(temp_workspace):
    """Create renamer instance with temp workspace."""
    return SafeFileRenamer(workspace_root=temp_workspace)


class TestSafeFileRenamer:
    """Test suite for SafeFileRenamer class."""

    def test_renamer_initialization(self, temp_workspace):
        """Test renamer initializes with workspace root."""
        renamer = SafeFileRenamer(workspace_root=temp_workspace)
        assert renamer.workspace_root == temp_workspace
        assert renamer.dry_run is False

    def test_rename_file_basic(self, renamer, temp_workspace):
        """Test basic file rename without imports."""
        old_path = temp_workspace / "src" / "old_module_name.py"
        new_name = "new-module-name.py"
        
        result = renamer.rename_file(old_path, new_name)
        
        assert result.success is True
        assert result.old_path == old_path
        assert result.new_path == temp_workspace / "src" / "new-module-name.py"
        assert result.new_path.exists()
        assert not old_path.exists()

    def test_rename_updates_imports(self, renamer, temp_workspace):
        """Test that imports are updated across codebase."""
        old_path = temp_workspace / "src" / "old_module_name.py"
        new_name = "new-module-name.py"
        
        result = renamer.rename_file(old_path, new_name)
        
        # Check importer was updated
        importer_content = (temp_workspace / "src" / "importer.py").read_text()
        assert "from new_module_name import hello_world" in importer_content
        assert "old_module_name" not in importer_content

    def test_rename_updates_test_files(self, renamer, temp_workspace):
        """Test that test file names and imports are updated."""
        old_path = temp_workspace / "src" / "old_module_name.py"
        new_name = "new-module-name.py"
        
        result = renamer.rename_file(old_path, new_name)
        
        # Check test file was renamed
        old_test = temp_workspace / "tests" / "test_old_module_name.py"
        new_test = temp_workspace / "tests" / "test_new_module_name.py"
        assert not old_test.exists()
        assert new_test.exists()
        
        # Check test imports updated
        test_content = new_test.read_text()
        assert "from src.new_module_name import hello_world" in test_content

    def test_dry_run_mode(self, temp_workspace):
        """Test dry-run mode doesn't actually rename files."""
        renamer = SafeFileRenamer(workspace_root=temp_workspace, dry_run=True)
        old_path = temp_workspace / "src" / "old_module_name.py"
        new_name = "new-module-name.py"
        
        result = renamer.rename_file(old_path, new_name)
        
        assert result.success is True
        assert old_path.exists()  # File should still exist
        assert result.new_path == temp_workspace / "src" / "new-module-name.py"
        assert not result.new_path.exists()  # New path shouldn't exist

    def test_rollback_on_error(self, renamer, temp_workspace):
        """Test rollback restores original state on error."""
        old_path = temp_workspace / "src" / "old_module_name.py"
        
        # Create scenario that will cause error (invalid new name)
        with pytest.raises(RenameError):
            renamer.rename_file(old_path, "../../../etc/passwd")  # Invalid path
        
        # Original file should still exist
        assert old_path.exists()

    def test_find_import_references(self, renamer, temp_workspace):
        """Test finding all files that import a module."""
        old_path = temp_workspace / "src" / "old_module_name.py"
        
        references = renamer.find_import_references(old_path)
        
        assert len(references) >= 2  # importer.py and test file
        assert any("importer.py" in str(ref) for ref in references)
        assert any("test_old_module_name.py" in str(ref) for ref in references)

    def test_update_import_statement(self, renamer, temp_workspace):
        """Test updating import statements in a file."""
        importer = temp_workspace / "src" / "importer.py"
        
        updated = renamer.update_import_statement(
            file_path=importer,
            old_module="old_module_name",
            new_module="new_module_name"
        )
        
        assert updated is True
        content = importer.read_text()
        assert "new_module_name" in content
        assert "old_module_name" not in content
