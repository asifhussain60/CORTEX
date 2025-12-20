"""
Setup Script Generator - RED Phase Tests

Tests for Phase 3.2: Generate platform-specific setup scripts.

Generates scripts for:
- Windows PowerShell
- macOS/Linux Bash

Includes:
- Dependency installation commands
- Environment variable setup
- Tool recommendations

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
import json

# Import will be None until GREEN phase
try:
    from src.intelligence.setup_script_generator import SetupScriptGenerator, Platform
except ImportError:
    SetupScriptGenerator = None
    Platform = None


class TestSetupScriptGeneratorInitialization:
    """Test setup script generator initialization."""
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_init_with_dependencies(self):
        """Should initialize with dependency data."""
        deps_data = {
            "by_language": {
                "python": [{"name": "flask", "version": "2.3.0"}]
            }
        }
        generator = SetupScriptGenerator(deps_data)
        assert generator.dependencies == deps_data
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_generate_returns_dict(self):
        """Should return dictionary with scripts for each platform."""
        deps_data = {"by_language": {"python": []}}
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        assert isinstance(result, dict)
        assert "windows" in result
        assert "unix" in result


class TestWindowsPowerShellGeneration:
    """Test Windows PowerShell script generation."""
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_generates_powershell_script(self):
        """Should generate valid PowerShell script."""
        deps_data = {
            "by_language": {
                "python": [{"name": "flask", "version": "2.3.0"}]
            }
        }
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        script = result["windows"]
        assert script.startswith("# Setup script for Windows")
        assert "pip install" in script
        assert "flask==2.3.0" in script
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_includes_python_check(self):
        """Should include Python version check."""
        deps_data = {"by_language": {"python": []}}
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        script = result["windows"]
        assert "python --version" in script or "python.exe --version" in script
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_includes_nodejs_installation(self):
        """Should include Node.js package installation."""
        deps_data = {
            "by_language": {
                "javascript": [
                    {"name": "express", "version": "4.18.0", "constraint": "^"}
                ]
            }
        }
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        script = result["windows"]
        assert "npm install" in script
        assert "express" in script


class TestUnixBashGeneration:
    """Test Unix Bash script generation."""
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_generates_bash_script(self):
        """Should generate valid Bash script."""
        deps_data = {
            "by_language": {
                "python": [{"name": "flask", "version": "2.3.0"}]
            }
        }
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        script = result["unix"]
        assert script.startswith("#!/bin/bash")
        assert "pip install" in script
        assert "flask==2.3.0" in script
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_includes_shebang(self):
        """Should include proper shebang."""
        deps_data = {"by_language": {}}
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        script = result["unix"]
        assert script.startswith("#!/bin/bash")


class TestMultiLanguageSupport:
    """Test multi-language dependency handling."""
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_handles_python_and_nodejs(self):
        """Should generate installation commands for multiple languages."""
        deps_data = {
            "by_language": {
                "python": [{"name": "flask", "version": "2.3.0"}],
                "javascript": [{"name": "express", "version": "4.18.0", "constraint": "^"}]
            }
        }
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        win_script = result["windows"]
        assert "pip install" in win_script
        assert "npm install" in win_script
        
        unix_script = result["unix"]
        assert "pip install" in unix_script
        assert "npm install" in unix_script
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_includes_dotnet_restore(self):
        """Should include dotnet restore for C# projects."""
        deps_data = {
            "by_language": {
                "csharp": [{"name": "Newtonsoft.Json", "version": "13.0.3"}]
            }
        }
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        win_script = result["windows"]
        assert "dotnet restore" in win_script


class TestEnvironmentSetup:
    """Test environment variable setup."""
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_includes_env_var_setup(self):
        """Should include environment variable setup."""
        deps_data = {
            "by_language": {"python": []},
            "env_vars": {
                "FLASK_APP": "app.py",
                "FLASK_ENV": "development"
            }
        }
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        win_script = result["windows"]
        assert "$env:FLASK_APP" in win_script or "setx FLASK_APP" in win_script
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_unix_uses_export(self):
        """Should use export for Unix environment variables."""
        deps_data = {
            "by_language": {},
            "env_vars": {"NODE_ENV": "production"}
        }
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        unix_script = result["unix"]
        assert "export NODE_ENV=" in unix_script


class TestToolRecommendations:
    """Test tool recommendation inclusion."""
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_recommends_python_tools(self):
        """Should recommend Python development tools."""
        deps_data = {"by_language": {"python": []}}
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        win_script = result["windows"]
        # Should mention linters, formatters, or testing tools
        has_recommendations = any(tool in win_script.lower() for tool in ["pylint", "black", "pytest", "mypy"])
        assert has_recommendations
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_recommends_nodejs_tools(self):
        """Should recommend Node.js development tools."""
        deps_data = {"by_language": {"javascript": []}}
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        unix_script = result["unix"]
        # Should mention eslint, prettier, or testing tools
        has_recommendations = any(tool in unix_script.lower() for tool in ["eslint", "prettier", "jest"])
        assert has_recommendations


class TestScriptValidation:
    """Test generated script validation."""
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_no_empty_scripts(self):
        """Should not generate empty scripts."""
        deps_data = {"by_language": {}}
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        assert len(result["windows"]) > 50  # At least has header/comments
        assert len(result["unix"]) > 50
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_scripts_are_strings(self):
        """Should return scripts as strings."""
        deps_data = {"by_language": {"python": []}}
        generator = SetupScriptGenerator(deps_data)
        result = generator.generate()
        
        assert isinstance(result["windows"], str)
        assert isinstance(result["unix"], str)


class TestSaveToFile:
    """Test saving scripts to files."""
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_save_windows_script(self):
        """Should save Windows script to .ps1 file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            deps_data = {"by_language": {"python": []}}
            generator = SetupScriptGenerator(deps_data)
            
            files = generator.save(output_dir)
            
            assert "windows" in files
            assert files["windows"].suffix == ".ps1"
            assert files["windows"].exists()
    
    @pytest.mark.skipif(SetupScriptGenerator is None, reason="RED phase")
    def test_save_unix_script(self):
        """Should save Unix script to .sh file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir)
            deps_data = {"by_language": {"python": []}}
            generator = SetupScriptGenerator(deps_data)
            
            files = generator.save(output_dir)
            
            assert "unix" in files
            assert files["unix"].suffix == ".sh"
            assert files["unix"].exists()
