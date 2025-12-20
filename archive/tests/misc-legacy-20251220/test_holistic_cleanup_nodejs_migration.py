"""
Test suite for Node.js to Python migration in Holistic Cleanup Orchestrator

Tests verify that Node.js artifacts (node_modules/, package.json) are:
1. NOT in protected paths (should be cleaned up)
2. Detected as cleanup targets during scanning
3. Removed during cleanup execution

TDD Phase: RED - These tests should FAIL initially
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
from src.operations.modules.cleanup.holistic_cleanup_orchestrator import (
    HolisticCleanupOrchestrator,
    HolisticRepositoryScanner
)


class TestNodeJSCleanupDetection:
    """Test that Node.js artifacts are detected as cleanup targets"""
    
    @pytest.fixture
    def temp_project(self):
        """Create temporary project with Node.js artifacts"""
        temp_dir = tempfile.mkdtemp(prefix="cortex_test_")
        project_path = Path(temp_dir)
        
        # Create node_modules directory with fake packages
        node_modules = project_path / "node_modules"
        node_modules.mkdir()
        (node_modules / "@playwright").mkdir(parents=True)
        (node_modules / "@playwright" / "test").mkdir()
        (node_modules / "@playwright" / "test" / "index.js").write_text("module.exports = {}")
        
        (node_modules / "sql.js").mkdir()
        (node_modules / "sql.js" / "dist").mkdir(parents=True)
        (node_modules / "sql.js" / "dist" / "sql-wasm.js").write_text("// sql.js")
        
        # Create package.json
        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "devDependencies": {
                "@playwright/test": "^1.50.0",
                "sql.js": "^1.12.0"
            }
        }
        (project_path / "package.json").write_text(json.dumps(package_json, indent=2))
        
        # Create package-lock.json
        (project_path / "package-lock.json").write_text('{"lockfileVersion": 3}')
        
        # Create Python equivalents (should be kept)
        (project_path / "requirements.txt").write_text("pytest>=8.0.0\nsqlite3")
        (project_path / "src").mkdir()
        (project_path / "src" / "main.py").write_text("# Main app")
        
        yield project_path
        
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_node_modules_not_in_protected_paths(self, temp_project):
        """
        RED TEST: Verify node_modules/ is NOT in protected paths
        Expected: FAIL (currently protected)
        """
        orchestrator = HolisticCleanupOrchestrator(temp_project)
        
        # Assert node_modules/ is NOT protected
        assert 'node_modules/' not in orchestrator.protected_paths, \
            "node_modules/ should NOT be in protected_paths (should be cleaned up)"
    
    def test_package_json_not_in_protected_paths(self, temp_project):
        """
        RED TEST: Verify package.json is NOT in protected paths
        Expected: FAIL (currently protected)
        """
        orchestrator = HolisticCleanupOrchestrator(temp_project)
        
        # Assert package.json is NOT protected
        assert 'package.json' not in orchestrator.protected_paths, \
            "package.json should NOT be in protected_paths (should be cleaned up)"
    
    def test_scanner_detects_node_modules_as_dependency_cache(self, temp_project):
        """
        RED TEST: Verify scanner categorizes node_modules/ as dependency cache
        Expected: FAIL (currently excluded by protected paths)
        """
        orchestrator = HolisticCleanupOrchestrator(temp_project)
        scanner = HolisticRepositoryScanner(temp_project, orchestrator.protected_paths)
        
        scan_results = scanner.scan_repository()
        
        # Check that node_modules files are in dependency_cache category
        dependency_files = [
            f for f in scan_results.get('categories', {}).get('dependency_cache', [])
            if 'node_modules' in str(f.get('path', ''))
        ]
        
        assert len(dependency_files) > 0, \
            "node_modules/ files should be detected as dependency_cache"
    
    def test_scanner_detects_package_json_as_config_artifact(self, temp_project):
        """
        RED TEST: Verify scanner detects package.json as cleanup target
        Expected: FAIL (currently protected)
        """
        orchestrator = HolisticCleanupOrchestrator(temp_project)
        scanner = HolisticRepositoryScanner(temp_project, orchestrator.protected_paths)
        
        scan_results = scanner.scan_repository()
        
        # Check that package.json is detected in some cleanup category
        all_files = []
        for category, files in scan_results.get('categories', {}).items():
            all_files.extend([f.get('path') for f in files])
        
        package_json_found = any('package.json' in str(f) for f in all_files)
        
        assert package_json_found, \
            "package.json should be detected as cleanup target (config artifact)"
    
    def test_cleanup_manifest_includes_nodejs_artifacts(self, temp_project):
        """
        RED TEST: Verify cleanup manifest includes Node.js artifacts for deletion
        Expected: FAIL (currently protected)
        """
        orchestrator = HolisticCleanupOrchestrator(temp_project)
        
        context = {'dry_run': True}
        result = orchestrator.execute(context)
        
        # Get manifest from result
        manifest = result.data.get('manifest', {})
        
        # Count Node.js related files
        nodejs_files = 0
        for category, category_data in manifest.get('categories', {}).items():
            # category_data is a dict with 'files' key
            if isinstance(category_data, dict):
                files = category_data.get('files', [])
            else:
                files = category_data
            
            for file_info in files:
                if isinstance(file_info, dict):
                    path_str = str(file_info.get('path', ''))
                else:
                    path_str = str(file_info)
                    
                if 'node_modules' in path_str or 'package.json' in path_str or 'package-lock.json' in path_str:
                    nodejs_files += 1
        
        assert nodejs_files > 0, \
            f"Cleanup manifest should include Node.js artifacts for deletion (found {nodejs_files})"
    
    def test_python_files_remain_protected(self, temp_project):
        """
        GREEN TEST: Verify Python source files remain protected
        Expected: PASS (baseline validation)
        """
        orchestrator = HolisticCleanupOrchestrator(temp_project)
        
        # Verify requirements.txt is protected
        assert 'requirements.txt' in orchestrator.protected_paths, \
            "requirements.txt should remain protected"
        
        # Verify src/ is protected
        assert 'src/' in orchestrator.protected_paths, \
            "src/ should remain protected"
    
    def test_estimated_space_savings_includes_nodejs(self, temp_project):
        """
        RED TEST: Verify space savings calculation includes node_modules/
        Expected: FAIL (currently protected)
        """
        orchestrator = HolisticCleanupOrchestrator(temp_project)
        
        context = {'dry_run': True}
        result = orchestrator.execute(context)
        
        statistics = result.data.get('statistics', {})
        total_size = statistics.get('total_size_bytes', 0)
        
        # node_modules/ should contribute significant size
        # In our test, we created files, so size should be > 0
        assert total_size > 100, \
            f"Total cleanup size should include node_modules/ files (got {total_size} bytes)"


class TestNodeJSPackageJsonExclusion:
    """Test specific behavior for package.json detection"""
    
    @pytest.fixture
    def temp_mixed_project(self):
        """Create project with both Python and Node.js files"""
        temp_dir = tempfile.mkdtemp(prefix="cortex_test_mixed_")
        project_path = Path(temp_dir)
        
        # Python setup
        (project_path / "requirements.txt").write_text("pytest\nsqlite3")
        (project_path / "setup.py").write_text("from setuptools import setup\nsetup()")
        
        # Node.js setup
        (project_path / "package.json").write_text('{"name": "test"}')
        (project_path / "node_modules").mkdir()
        
        yield project_path
        
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_package_json_not_protected_with_python_present(self, temp_mixed_project):
        """
        RED TEST: Even with Python files present, package.json should not be protected
        Expected: FAIL
        """
        orchestrator = HolisticCleanupOrchestrator(temp_mixed_project)
        
        assert 'package.json' not in orchestrator.protected_paths, \
            "package.json should not be protected even when Python files exist"
    
    def test_requirements_txt_remains_protected_with_nodejs_present(self, temp_mixed_project):
        """
        GREEN TEST: requirements.txt should remain protected even with Node.js files
        Expected: PASS (baseline)
        """
        orchestrator = HolisticCleanupOrchestrator(temp_mixed_project)
        
        assert 'requirements.txt' in orchestrator.protected_paths, \
            "requirements.txt should remain protected"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
