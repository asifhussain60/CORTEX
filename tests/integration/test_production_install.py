"""
Integration Tests for Production Package Installation

Tests that CORTEX package installs correctly and all components function
after installation via pip install or wheel.

Test Coverage:
- Package installation (editable and wheel)
- CLI command availability
- Resource loading (templates, configs, brain files)
- Planning system end-to-end workflow
- Cross-platform compatibility

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
Date: December 16, 2025
"""

import subprocess
import sys
import tempfile
import shutil
from pathlib import Path
import pytest
import json


class TestProductionInstall:
    """Test suite for production package installation."""
    
    def test_package_metadata(self):
        """Test that package metadata is correct after installation."""
        result = subprocess.run(
            [sys.executable, "-m", "pip", "show", "cortex-ai"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, "Package not installed"
        output = result.stdout
        
        assert "Name: cortex-ai" in output
        assert "Version: 3.9.0" in output
        assert "Author: Asif Hussain" in output
    
    def test_cli_cortex_command(self):
        """Test that 'cortex' CLI command is available."""
        result = subprocess.run(
            ["cortex", "version"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"cortex command failed: {result.stderr}"
        assert "CORTEX Version" in result.stdout
    
    def test_cli_cortex_plan_command(self):
        """Test that 'cortex-plan' CLI command is available."""
        result = subprocess.run(
            ["cortex-plan", "test simple request"],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"cortex-plan failed: {result.stderr}"
        # Simple request should not create plan (Tier 1)
        assert "Simple request" in result.stdout or "Tier 1" in result.stdout
    
    def test_cli_cortex_plan_complex(self):
        """Test that complex requests create temporary plans."""
        result = subprocess.run(
            ["cortex-plan", "comprehensive analysis of system architecture"],
            capture_output=True,
            text=True,
            cwd=str(Path.cwd())
        )
        
        assert result.returncode == 0, f"cortex-plan failed: {result.stderr}"
        assert "TEMP-PLAN-" in result.stdout, "Plan not created"
        assert "Tier 3" in result.stdout or "DOCUMENTED" in result.stdout
    
    def test_resource_loading_templates(self):
        """Test that response templates load correctly."""
        test_script = """
from src.response_templates import TemplateLoader
from src.utils.resource_resolver import get_root_path

root = get_root_path()
template_file = root / "cortex-brain" / "response-templates.yaml"
loader = TemplateLoader(template_file)

templates = loader.get_template_ids()
assert len(templates) > 0, "No templates loaded"
print(f"Loaded {len(templates)} templates")
"""
        
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Template loading failed: {result.stderr}"
        assert "Loaded" in result.stdout and "templates" in result.stdout
    
    def test_resource_loading_brain_rules(self):
        """Test that brain protection rules load correctly."""
        test_script = """
from src.utils.resource_resolver import get_root_path
import yaml

root = get_root_path()
rules_file = root / "cortex-brain" / "brain-protection-rules.yaml"
assert rules_file.exists(), f"Brain rules not found: {rules_file}"

with open(rules_file, 'r', encoding='utf-8') as f:
    rules = yaml.safe_load(f)

assert 'rules' in rules, "Brain protection rules not loaded"
assert rules['rules']['total_count'] > 0, "No rules found"
print(f"Loaded brain protection rules with {rules['rules']['total_count']} rules")
"""
        
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Brain rules loading failed: {result.stderr}"
        assert "Loaded" in result.stdout and "SKULL rules" in result.stdout
    
    def test_config_loading(self):
        """Test that config system loads correctly."""
        test_script = """
from src.config import config
from pathlib import Path

assert config.root_path is not None, "Root path not set"
assert isinstance(config.root_path, Path), "Root path not Path object"
print(f"Config loaded: {config.root_path}")
"""
        
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"Config loading failed: {result.stderr}"
        assert "Config loaded:" in result.stdout
    
    def test_import_no_errors(self):
        """Test that all major modules import without errors."""
        modules_to_test = [
            "src.entry_point.cortex_entry",
            "src.entry_point.planning_gate",
            "src.utils.resource_resolver",
            "src.config",
            "src.tier0.brain_protector",
            "src.tier1.conversation_memory",
            "src.tier2.knowledge_graph",
            "src.response_templates",
        ]
        
        for module in modules_to_test:
            result = subprocess.run(
                [sys.executable, "-c", f"import {module}; print('OK')"],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Import failed for {module}: {result.stderr}"
            assert "OK" in result.stdout, f"Import incomplete for {module}"
    
    def test_planning_gate_functionality(self):
        """Test that PlanningGate class functions correctly."""
        test_script = """
from src.entry_point.planning_gate import PlanningGate
from pathlib import Path

gate = PlanningGate()
assert gate.cortex_root is not None, "CORTEX root not set"
assert gate.temp_plans_dir.exists(), "Temp plans directory not created"

# Test complexity classification
tier1 = gate._classify_complexity("show version")
tier3 = gate._classify_complexity("comprehensive analysis")

assert tier1 == 1, f"Tier 1 classification failed: {tier1}"
assert tier3 == 3, f"Tier 3 classification failed: {tier3}"

print("PlanningGate functionality OK")
"""
        
        result = subprocess.run(
            [sys.executable, "-c", test_script],
            capture_output=True,
            text=True
        )
        
        assert result.returncode == 0, f"PlanningGate test failed: {result.stderr}"
        assert "functionality OK" in result.stdout


class TestWheelInstall:
    """Test suite for wheel distribution installation."""
    
    @pytest.mark.slow
    def test_build_wheel(self):
        """Test that wheel can be built successfully."""
        result = subprocess.run(
            [sys.executable, "setup.py", "bdist_wheel"],
            capture_output=True,
            text=True,
            cwd=str(Path.cwd())
        )
        
        assert result.returncode == 0, f"Wheel build failed: {result.stderr}"
        
        # Check that wheel was created
        dist_dir = Path.cwd() / "dist"
        wheels = list(dist_dir.glob("cortex_ai-*.whl"))
        assert len(wheels) > 0, "No wheel file created"
    
    @pytest.mark.slow
    def test_build_sdist(self):
        """Test that source distribution can be built successfully."""
        result = subprocess.run(
            [sys.executable, "setup.py", "sdist"],
            capture_output=True,
            text=True,
            cwd=str(Path.cwd())
        )
        
        assert result.returncode == 0, f"sdist build failed: {result.stderr}"
        
        # Check that sdist was created
        dist_dir = Path.cwd() / "dist"
        sdists = list(dist_dir.glob("cortex-ai-*.tar.gz"))
        assert len(sdists) > 0, "No sdist file created"
    
    @pytest.mark.slow
    @pytest.mark.skipif(
        sys.platform != "win32",
        reason="Clean venv test runs on Windows CI"
    )
    def test_install_in_clean_venv(self):
        """Test installation in a clean virtual environment."""
        # This test is marked slow and should run in CI
        # Skipped in normal test runs to avoid time overhead
        with tempfile.TemporaryDirectory() as tmpdir:
            venv_dir = Path(tmpdir) / "test_venv"
            
            # Create venv
            subprocess.run(
                [sys.executable, "-m", "venv", str(venv_dir)],
                check=True
            )
            
            # Get venv python
            if sys.platform == "win32":
                venv_python = venv_dir / "Scripts" / "python.exe"
            else:
                venv_python = venv_dir / "bin" / "python"
            
            # Install wheel
            dist_dir = Path.cwd() / "dist"
            wheels = list(dist_dir.glob("cortex_ai-*.whl"))
            if not wheels:
                pytest.skip("No wheel found - run 'python setup.py bdist_wheel' first")
            
            wheel_path = wheels[0]
            result = subprocess.run(
                [str(venv_python), "-m", "pip", "install", str(wheel_path)],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"Wheel install failed: {result.stderr}"
            
            # Test that CLI works
            result = subprocess.run(
                [str(venv_python), "-m", "cortex", "version"],
                capture_output=True,
                text=True
            )
            
            assert result.returncode == 0, f"CLI test failed: {result.stderr}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
