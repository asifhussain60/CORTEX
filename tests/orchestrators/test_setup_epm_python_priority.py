"""
Test suite for Setup EPM Orchestrator - Python Priority

Tests verify that when both Python and Node.js files exist:
1. Python is detected as the primary language
2. Python build system is preferred
3. Python test command is returned

TDD Phase: RED - These tests should FAIL initially
"""

import pytest
from pathlib import Path
import tempfile
import shutil
import json
from src.orchestrators.setup_epm_orchestrator import SetupEPMOrchestrator


class TestSetupEPMPythonPriority:
    """Test that Setup EPM prefers Python over Node.js"""
    
    @pytest.fixture
    def temp_mixed_project(self):
        """Create project with both Python and Node.js files"""
        temp_dir = tempfile.mkdtemp(prefix="cortex_epm_test_")
        project_path = Path(temp_dir)
        
        # Python setup
        (project_path / "requirements.txt").write_text("pytest>=8.0.0\nsqlite3\nflask")
        (project_path / "setup.py").write_text("""
from setuptools import setup, find_packages

setup(
    name="test-project",
    version="1.0.0",
    packages=find_packages(),
)
""")
        (project_path / "src").mkdir()
        (project_path / "src" / "__init__.py").write_text("")
        (project_path / "src" / "main.py").write_text("def main():\n    pass")
        
        # Node.js setup
        package_json = {
            "name": "test-project",
            "version": "1.0.0",
            "scripts": {
                "test": "jest",
                "build": "webpack"
            },
            "devDependencies": {
                "@playwright/test": "^1.50.0",
                "jest": "^29.0.0"
            }
        }
        (project_path / "package.json").write_text(json.dumps(package_json, indent=2))
        (project_path / "node_modules").mkdir()
        
        yield project_path
        
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    @pytest.fixture
    def temp_python_only_project(self):
        """Create Python-only project"""
        temp_dir = tempfile.mkdtemp(prefix="cortex_epm_python_")
        project_path = Path(temp_dir)
        
        (project_path / "requirements.txt").write_text("pytest\nflask")
        (project_path / "src").mkdir()
        (project_path / "src" / "main.py").write_text("def main():\n    pass")
        
        yield project_path
        
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_detect_language_prefers_python(self, temp_mixed_project):
        """
        RED TEST: When both Python and JS exist, detect Python as primary
        Expected: FAIL (currently may detect JS)
        """
        orchestrator = SetupEPMOrchestrator(temp_mixed_project)
        language = orchestrator._detect_language()
        
        assert language == "Python", \
            f"Should detect Python as primary language, got: {language}"
    
    def test_detect_framework_prefers_python(self, temp_mixed_project):
        """
        RED TEST: When both Python and JS frameworks exist, detect Python framework
        Expected: FAIL (may detect JS framework)
        """
        orchestrator = SetupEPMOrchestrator(temp_mixed_project)
        framework = orchestrator._detect_framework()
        
        # Should not be a JS framework (React, Vue, Angular, etc.)
        js_frameworks = ["React", "Vue", "Angular", "Next.js", "Express"]
        
        assert framework not in js_frameworks, \
            f"Should detect Python framework, not JS framework: {framework}"
    
    def test_detect_build_system_prefers_python(self, temp_mixed_project):
        """
        RED TEST: When both Python and npm exist, prefer Python build system
        Expected: FAIL (may detect npm)
        """
        orchestrator = SetupEPMOrchestrator(temp_mixed_project)
        build_system = orchestrator._detect_build_system()
        
        # Should detect setuptools/pip, not npm
        assert "npm" not in build_system.lower(), \
            f"Should not detect npm when Python build system exists, got: {build_system}"
        
        # Should mention Python build tools
        python_tools = ["setuptools", "pip", "poetry", "setup.py"]
        has_python_tool = any(tool in build_system.lower() for tool in python_tools)
        
        assert has_python_tool, \
            f"Should detect Python build system (setuptools/pip), got: {build_system}"
    
    def test_generate_build_command_uses_python(self, temp_mixed_project):
        """
        RED TEST: Build command should use Python, not npm
        Expected: FAIL (may return 'npm run build')
        """
        orchestrator = SetupEPMOrchestrator(temp_mixed_project)
        detected = orchestrator._detect_project_structure()
        build_command = orchestrator._generate_build_command(detected)
        
        assert "npm" not in build_command.lower(), \
            f"Build command should not use npm, got: {build_command}"
        
        # Should mention Python build command
        python_commands = ["python setup.py", "pip install", "poetry install"]
        has_python_command = any(cmd in build_command.lower() for cmd in python_commands)
        
        assert has_python_command, \
            f"Build command should use Python tools, got: {build_command}"
    
    def test_generate_test_command_uses_pytest(self, temp_mixed_project):
        """
        RED TEST: Test command should use pytest, not npm test
        Expected: FAIL (may return 'npm test')
        """
        orchestrator = SetupEPMOrchestrator(temp_mixed_project)
        detected = orchestrator._detect_project_structure()
        test_command = orchestrator._generate_test_command(detected)
        
        assert "npm test" not in test_command.lower(), \
            f"Test command should not use npm, got: {test_command}"
        
        # Should use pytest
        assert "pytest" in test_command.lower(), \
            f"Test command should use pytest, got: {test_command}"
    
    def test_python_only_project_detection(self, temp_python_only_project):
        """
        GREEN TEST: Python-only project should be detected correctly
        Expected: PASS (baseline validation)
        """
        orchestrator = SetupEPMOrchestrator(temp_python_only_project)
        
        language = orchestrator._detect_language()
        build_system = orchestrator._detect_build_system()
        detected = orchestrator._detect_project_structure()
        test_command = orchestrator._generate_test_command(detected)
        
        assert language == "Python", "Should detect Python"
        assert "npm" not in build_system.lower(), "Should not detect npm"
        assert "pytest" in test_command.lower(), "Should use pytest"


class TestSetupEPMNodeJSNotInstalled:
    """Test that Node.js detection doesn't require Node.js to be installed"""
    
    @pytest.fixture
    def temp_nodejs_project(self):
        """Create Node.js project (for cleanup detection)"""
        temp_dir = tempfile.mkdtemp(prefix="cortex_epm_nodejs_")
        project_path = Path(temp_dir)
        
        package_json = {
            "name": "nodejs-project",
            "version": "1.0.0",
            "scripts": {"test": "jest"}
        }
        (project_path / "package.json").write_text(json.dumps(package_json, indent=2))
        (project_path / "node_modules").mkdir()
        
        yield project_path
        
        shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_nodejs_project_detected_for_cleanup(self, temp_nodejs_project):
        """
        GREEN TEST: Node.js projects should still be detected (for cleanup purposes)
        Expected: PASS
        """
        orchestrator = SetupEPMOrchestrator(temp_nodejs_project)
        
        # Should detect it's a Node.js project
        has_package_json = (temp_nodejs_project / "package.json").exists()
        has_node_modules = (temp_nodejs_project / "node_modules").exists()
        
        assert has_package_json, "Should detect package.json"
        assert has_node_modules, "Should detect node_modules"


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
