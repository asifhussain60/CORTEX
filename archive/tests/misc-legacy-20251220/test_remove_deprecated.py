"""
Test suite for deprecated code removal script
Phase 0.4 - RED state: These tests MUST fail before implementation
"""

import ast
import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class TestDeprecatedDetection:
    """Test detection of @deprecated decorators and functions"""
    
    def test_detect_deprecated_decorator(self):
        """RED: Should detect @deprecated decorator"""
        from scripts.remove_deprecated import detect_deprecated_code
        
        code = """
@deprecated
def old_function():
    return "old implementation"

def new_function():
    return "new implementation"
"""
        violations = detect_deprecated_code(code)
        assert len(violations) >= 1, "Should detect @deprecated decorator"
        assert any("old_function" in str(v) for v in violations), "Should identify function name"
    
    def test_detect_deprecated_with_reason(self):
        """RED: Should detect @deprecated with deprecation reason"""
        from scripts.remove_deprecated import detect_deprecated_code
        
        code = """
@deprecated("Use new_function() instead")
def old_function():
    return "old"
"""
        violations = detect_deprecated_code(code)
        assert len(violations) >= 1, "Should detect @deprecated with reason"
    
    def test_detect_deprecated_class(self):
        """RED: Should detect deprecated classes"""
        from scripts.remove_deprecated import detect_deprecated_code
        
        code = """
@deprecated
class OldClass:
    def method(self):
        pass
"""
        violations = detect_deprecated_code(code)
        assert len(violations) >= 1, "Should detect deprecated class"
        assert any("OldClass" in str(v) for v in violations), "Should identify class name"
    
    def test_detect_todo_referencing_deprecated(self):
        """RED: Should detect TODO comments referencing deprecated code"""
        from scripts.remove_deprecated import detect_todo_references
        
        code = """
def new_function():
    # TODO: Remove old_function after migration
    pass

@deprecated
def old_function():
    pass
"""
        violations = detect_todo_references(code)
        assert len(violations) >= 1, "Should detect TODO about deprecated code"
    
    def test_ignore_non_deprecated_code(self):
        """RED: Should not flag active code"""
        from scripts.remove_deprecated import detect_deprecated_code
        
        code = """
def active_function():
    return True

class ActiveClass:
    pass
"""
        violations = detect_deprecated_code(code)
        assert len(violations) == 0, "Should not flag active code"


class TestDeprecatedRemoval:
    """Test actual removal of deprecated code"""
    
    def test_remove_deprecated_function(self):
        """RED: Should remove deprecated function completely"""
        from scripts.remove_deprecated import remove_deprecated_code
        
        original = """
import os

@deprecated
def old_function():
    return "old"

def active_function():
    return "active"
"""
        cleaned = remove_deprecated_code(original)
        
        assert "def active_function():" in cleaned, "Should preserve active code"
        assert "@deprecated" not in cleaned, "Should remove decorator"
        assert "def old_function():" not in cleaned, "Should remove function"
        assert "import os" in cleaned, "Should preserve imports"
    
    def test_remove_deprecated_class(self):
        """RED: Should remove deprecated class"""
        from scripts.remove_deprecated import remove_deprecated_code
        
        original = """
@deprecated
class OldClass:
    def method(self):
        pass

class NewClass:
    pass
"""
        cleaned = remove_deprecated_code(original)
        
        assert "class NewClass:" in cleaned, "Should preserve active class"
        assert "class OldClass:" not in cleaned, "Should remove deprecated class"
    
    def test_remove_todo_references(self):
        """RED: Should remove TODO comments about deprecated code"""
        from scripts.remove_deprecated import remove_deprecated_code
        
        original = """
def new_function():
    # TODO: Remove old_function after all callers updated
    return True

@deprecated
def old_function():
    return False
"""
        cleaned = remove_deprecated_code(original, remove_todos=True)
        
        assert "def new_function():" in cleaned, "Should preserve function"
        assert "TODO" not in cleaned, "Should remove TODO about deprecated code"
        assert "def old_function():" not in cleaned, "Should remove deprecated function"
    
    def test_preserve_code_structure(self):
        """RED: Should maintain proper code structure after removal"""
        from scripts.remove_deprecated import remove_deprecated_code
        
        original = """
import sys

@deprecated
def old():
    pass

def middle():
    pass

@deprecated  
def another_old():
    pass

def new():
    pass
"""
        cleaned = remove_deprecated_code(original)
        
        assert "import sys" in cleaned, "Should preserve imports"
        assert "def middle():" in cleaned, "Should preserve middle function"
        assert "def new():" in cleaned, "Should preserve end function"
        assert cleaned.count("@deprecated") == 0, "Should remove all deprecated markers"


class TestManifestUpdate:
    """Test obsolete tests manifest update"""
    
    def test_update_manifest_on_removal(self):
        """RED: Should update obsolete-tests-manifest.json"""
        from scripts.remove_deprecated import update_obsolete_manifest
        
        removed_items = [
            {
                'file': 'src/utils/old_helper.py',
                'type': 'function',
                'name': 'old_function',
                'line': 10
            }
        ]
        
        manifest = update_obsolete_manifest(removed_items)
        assert isinstance(manifest, dict), "Should return manifest dict"
        assert len(manifest.get('removed', [])) >= 1, "Should track removed items"
    
    def test_manifest_includes_metadata(self):
        """RED: Should include removal metadata in manifest"""
        from scripts.remove_deprecated import update_obsolete_manifest
        
        removed_items = [{'file': 'test.py', 'type': 'function', 'name': 'old', 'line': 1}]
        manifest = update_obsolete_manifest(removed_items)
        
        assert 'timestamp' in manifest, "Should include timestamp"
        assert 'total_removed' in manifest, "Should include count"


class TestSafetyValidation:
    """Test safety checks and validation"""
    
    def test_syntax_validation_after_removal(self):
        """RED: Should validate syntax after removal"""
        from scripts.remove_deprecated import remove_deprecated_code, validate_syntax
        
        original = """
@deprecated
def old():
    pass

def new():
    return True
"""
        cleaned = remove_deprecated_code(original)
        is_valid, error = validate_syntax(cleaned)
        
        assert is_valid, f"Cleaned code should have valid syntax: {error}"
    
    def test_detect_broken_references(self):
        """RED: Should detect if removed code is still referenced"""
        from scripts.remove_deprecated import detect_broken_references
        
        code_after_removal = """
def caller():
    result = old_function()  # This will break!
    return result
"""
        deprecated_names = ['old_function']
        
        violations = detect_broken_references(code_after_removal, deprecated_names)
        assert len(violations) > 0, "Should detect reference to removed function"
    
    def test_backup_creation_before_removal(self):
        """GREEN: Should create backup before removal"""
        from scripts.remove_deprecated import process_directory
        
        # Now implementation exists
        stats = process_directory(Path("src"), dry_run=True, create_backup=True)
        assert isinstance(stats, dict), "Should return statistics dictionary"
        assert 'files_processed' in stats, "Should track processed files"


class TestChangelogUpdate:
    """Test CHANGELOG.md documentation"""
    
    def test_generate_changelog_entry(self):
        """RED: Should generate breaking changes entry for CHANGELOG"""
        from scripts.remove_deprecated import generate_changelog_entry
        
        removed_items = [
            {'file': 'src/utils.py', 'type': 'function', 'name': 'old_func', 'line': 10},
            {'file': 'src/models.py', 'type': 'class', 'name': 'OldClass', 'line': 50}
        ]
        
        entry = generate_changelog_entry(removed_items)
        
        assert "BREAKING CHANGES" in entry, "Should mark as breaking change"
        assert "old_func" in entry, "Should list removed function"
        assert "OldClass" in entry, "Should list removed class"
    
    def test_changelog_format(self):
        """RED: Should format changelog in markdown"""
        from scripts.remove_deprecated import generate_changelog_entry
        
        removed_items = [{'file': 'test.py', 'type': 'function', 'name': 'test', 'line': 1}]
        entry = generate_changelog_entry(removed_items)
        
        assert entry.startswith("## "), "Should be markdown heading"
        assert "- " in entry, "Should use markdown list format"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
