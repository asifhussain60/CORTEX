"""
Tests for VacuumAutomation

**Authority:** Phase 90 S-90-05
**Author:** Asif Hussain
**Created:** 2026-02-16
"""

from pathlib import Path

import pytest

from cortex.toolkit.cleanup.vacuum import CleanupResult, VacuumAutomation


class TestCleanupResult:
    """Test CleanupResult dataclass."""
    
    def test_cleanup_result_creation(self):
        """Test creating cleanup result."""
        result = CleanupResult(
            strategy="test_cleanup",
            files_removed=10,
            directories_removed=2,
            bytes_freed=1024,
            errors=[],
        )
        
        assert result.strategy == "test_cleanup"
        assert result.files_removed == 10
        assert result.directories_removed == 2
        assert result.bytes_freed == 1024
        assert result.errors == []


class TestVacuumAutomation:
    """Test VacuumAutomation class."""
    
    def test_initialization(self):
        """Test vacuum automation initialization."""
        vacuum = VacuumAutomation()
        
        assert vacuum.workspace_root == Path.cwd()
        assert vacuum.dry_run is False
        assert vacuum.results == {}
    
    def test_initialization_with_dry_run(self, tmp_path):
        """Test initialization with dry run mode."""
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=True)
        
        assert vacuum.workspace_root == tmp_path
        assert vacuum.dry_run is True
    
    def test_cleanup_markdown_sprawl_dry_run(self, tmp_path):
        """Test markdown cleanup in dry run mode."""
        # Create unauthorized markdown file
        unauthorized_md = tmp_path / "summary.md"
        unauthorized_md.write_text("# Test")
        
        # Create allowed markdown file
        allowed_dir = tmp_path / ".github" / "prompts"
        allowed_dir.mkdir(parents=True)
        allowed_md = allowed_dir / "test.md"
        allowed_md.write_text("# Allowed")
        
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=True)
        result = vacuum.cleanup_markdown_sprawl()
        
        assert result.strategy == "markdown_sprawl"
        assert result.files_removed == 1  # Only unauthorized file counted
        assert unauthorized_md.exists()  # Not actually removed in dry run
        assert allowed_md.exists()  # Allowed file untouched
    
    def test_cleanup_markdown_sprawl_real(self, tmp_path):
        """Test markdown cleanup with actual removal."""
        # Create unauthorized markdown file
        unauthorized_md = tmp_path / "summary.md"
        unauthorized_md.write_text("# Test")
        
        # Create allowed markdown file
        allowed_dir = tmp_path / ".github" / "prompts"
        allowed_dir.mkdir(parents=True)
        allowed_md = allowed_dir / "test.md"
        allowed_md.write_text("# Allowed")
        
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=False)
        result = vacuum.cleanup_markdown_sprawl()
        
        assert result.strategy == "markdown_sprawl"
        assert result.files_removed == 1
        assert not unauthorized_md.exists()  # Actually removed
        assert allowed_md.exists()  # Allowed file untouched
    
    def test_cleanup_debug_markers_dry_run(self, tmp_path):
        """Test debug marker cleanup in dry run mode."""
        # Create Python file with debug markers
        py_file = tmp_path / "test.py"
        py_file.write_text(
            "# Normal code\n"
            "# CORTEX_DEBUG: This is debug code\n"
            "def test():\n"
            "    pass  # CORTEX_DEBUG marker\n"
        )
        
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=True)
        result = vacuum.cleanup_debug_markers()
        
        assert result.strategy == "debug_markers"
        assert result.files_removed == 1
        # File should still contain debug markers in dry run
        assert "CORTEX_DEBUG" in py_file.read_text()
    
    def test_cleanup_debug_markers_real(self, tmp_path):
        """Test debug marker cleanup with actual removal."""
        # Create Python file with debug markers
        py_file = tmp_path / "test.py"
        original_content = (
            "# Normal code\n"
            "# CORTEX_DEBUG: This is debug code\n"
            "def test():\n"
            "    pass  # CORTEX_DEBUG marker\n"
        )
        py_file.write_text(original_content)
        
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=False)
        result = vacuum.cleanup_debug_markers()
        
        assert result.strategy == "debug_markers"
        assert result.files_removed == 1
        # Debug markers should be removed
        cleaned_content = py_file.read_text()
        assert "CORTEX_DEBUG" not in cleaned_content
        assert "# Normal code" in cleaned_content
        assert "def test():" in cleaned_content
    
    def test_cleanup_pycache_dry_run(self, tmp_path):
        """Test pycache cleanup in dry run mode."""
        # Create __pycache__ directory
        pycache_dir = tmp_path / "__pycache__"
        pycache_dir.mkdir()
        pyc_file = pycache_dir / "test.cpython-39.pyc"
        pyc_file.write_bytes(b"fake pyc content")
        
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=True)
        result = vacuum.cleanup_pycache()
        
        assert result.strategy == "pycache"
        assert result.directories_removed == 1
        assert pycache_dir.exists()  # Not actually removed in dry run
    
    def test_cleanup_pycache_real(self, tmp_path):
        """Test pycache cleanup with actual removal."""
        # Create __pycache__ directory
        pycache_dir = tmp_path / "__pycache__"
        pycache_dir.mkdir()
        pyc_file = pycache_dir / "test.cpython-39.pyc"
        pyc_file.write_bytes(b"fake pyc content")
        
        # Create standalone .pyc file
        standalone_pyc = tmp_path / "standalone.pyc"
        standalone_pyc.write_bytes(b"standalone pyc")
        
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=False)
        result = vacuum.cleanup_pycache()
        
        assert result.strategy == "pycache"
        assert result.directories_removed == 1
        assert result.files_removed == 1
        assert not pycache_dir.exists()  # Actually removed
        assert not standalone_pyc.exists()  # Actually removed
    
    def test_cleanup_session_data_dry_run(self, tmp_path):
        """Test session data cleanup in dry run mode."""
        # Create pytest cache
        pytest_cache = tmp_path / ".pytest_cache"
        pytest_cache.mkdir()
        cache_file = pytest_cache / "cache.json"
        cache_file.write_text("{}")
        
        # Create log file
        log_file = tmp_path / "test.log"
        log_file.write_text("log content")
        
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=True)
        result = vacuum.cleanup_session_data()
        
        assert result.strategy == "session_data"
        assert result.directories_removed >= 1
        assert result.files_removed >= 1
        assert pytest_cache.exists()  # Not actually removed in dry run
        assert log_file.exists()  # Not actually removed in dry run
    
    def test_cleanup_session_data_real(self, tmp_path):
        """Test session data cleanup with actual removal."""
        # Create pytest cache
        pytest_cache = tmp_path / ".pytest_cache"
        pytest_cache.mkdir()
        cache_file = pytest_cache / "cache.json"
        cache_file.write_text("{}")
        
        # Create log file
        log_file = tmp_path / "test.log"
        log_file.write_text("log content")
        
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=False)
        result = vacuum.cleanup_session_data()
        
        assert result.strategy == "session_data"
        assert result.directories_removed >= 1
        assert result.files_removed >= 1
        assert not pytest_cache.exists()  # Actually removed
        assert not log_file.exists()  # Actually removed
    
    def test_cleanup_build_artifacts_dry_run(self, tmp_path):
        """Test build artifacts cleanup in dry run mode."""
        # Create egg-info directory
        egg_info = tmp_path / "cortex.egg-info"
        egg_info.mkdir()
        egg_file = egg_info / "PKG-INFO"
        egg_file.write_text("metadata")
        
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=True)
        result = vacuum.cleanup_build_artifacts()
        
        assert result.strategy == "build_artifacts"
        assert result.directories_removed == 1
        assert egg_info.exists()  # Not actually removed in dry run
    
    def test_cleanup_build_artifacts_real(self, tmp_path):
        """Test build artifacts cleanup with actual removal."""
        # Create egg-info directory
        egg_info = tmp_path / "cortex.egg-info"
        egg_info.mkdir()
        egg_file = egg_info / "PKG-INFO"
        egg_file.write_text("metadata")
        
        # Create dist directory
        dist_dir = tmp_path / "dist"
        dist_dir.mkdir()
        wheel_file = dist_dir / "cortex-1.0-py3-none-any.whl"
        wheel_file.write_bytes(b"fake wheel")
        
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=False)
        result = vacuum.cleanup_build_artifacts()
        
        assert result.strategy == "build_artifacts"
        assert result.directories_removed == 2
        assert not egg_info.exists()  # Actually removed
        assert not dist_dir.exists()  # Actually removed
    
    def test_cleanup_all(self, tmp_path):
        """Test running all cleanup strategies."""
        # Create various items to clean
        unauthorized_md = tmp_path / "summary.md"
        unauthorized_md.write_text("# Test")
        
        pycache_dir = tmp_path / "__pycache__"
        pycache_dir.mkdir()
        (pycache_dir / "test.pyc").write_bytes(b"pyc")
        
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=True)
        results = vacuum.cleanup_all()
        
        assert len(results) == 5  # 5 strategies
        assert "markdown_sprawl" in results
        assert "debug_markers" in results
        assert "pycache" in results
        assert "session_data" in results
        assert "build_artifacts" in results
    
    def test_generate_report(self, tmp_path):
        """Test generating cleanup report."""
        vacuum = VacuumAutomation(workspace_root=tmp_path, dry_run=True)
        vacuum.results = {
            "test_strategy": CleanupResult(
                strategy="test_strategy",
                files_removed=10,
                directories_removed=2,
                bytes_freed=1024,
                errors=[],
            )
        }
        
        report = vacuum.generate_report()
        
        assert "CORTEX VACUUM AUTOMATION REPORT" in report
        assert "DRY RUN MODE" in report
        assert "test_strategy" in report
        assert "Files: 10" in report
        assert "Directories: 2" in report
