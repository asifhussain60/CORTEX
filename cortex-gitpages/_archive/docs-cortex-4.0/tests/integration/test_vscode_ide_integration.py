"""
Integration tests for GV-003-02: VS Code IDE Integration.

Tests the governance diagnostics provider:
- File analysis and diagnostic generation
- VSCode-compatible diagnostic format
- Real-time validation
- Quick-fix suggestions
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

import pytest


class TestGovernanceDiagnosticsProvider:
    """Test GovernanceDiagnosticsProvider class."""

    @pytest.fixture
    def provider_script(self):
        """Get path to diagnostics provider."""
        return Path(__file__).parent.parent.parent / "src" / "tools" / "vscode-diagnostics-provider.py"

    @pytest.fixture
    def provider_available(self, provider_script):
        """Check if provider script exists."""
        return provider_script.exists()

    def test_provider_script_exists(self, provider_script):
        """Test that diagnostics provider script exists."""
        assert provider_script.exists()

    def test_provider_has_main_class(self, provider_script):
        """Test that provider has main classes."""
        with open(provider_script) as f:
            content = f.read()
        assert "GovernanceDiagnosticsProvider" in content
        assert "GovernanceDiagnostic" in content
        assert "DiagnosticSeverity" in content

    def test_diagnostic_severity_enum(self, provider_script):
        """Test DiagnosticSeverity enum."""
        sys.path.insert(0, str(provider_script.parent))
        import importlib.util
        spec = importlib.util.spec_from_file_location("provider", provider_script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Check enum values (VSCode compatible)
        assert module.DiagnosticSeverity.ERROR.value == 0
        assert module.DiagnosticSeverity.WARNING.value == 1
        assert module.DiagnosticSeverity.INFORMATION.value == 2
        assert module.DiagnosticSeverity.HINT.value == 3

    def test_diagnostic_to_vscode_format(self, provider_script):
        """Test conversion of diagnostic to VSCode format."""
        sys.path.insert(0, str(provider_script.parent))
        import importlib.util
        spec = importlib.util.spec_from_file_location("provider", provider_script)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        diagnostic = module.GovernanceDiagnostic(
            line=5,
            column=10,
            message="Function missing type hints",
            rule_id="CORE-011",
            severity=module.DiagnosticSeverity.WARNING,
            fix_suggestion="Add type hints: def foo(x: int) -> str:",
        )

        vscode_diag = diagnostic.to_vscode_diagnostic()

        # Verify structure
        assert "range" in vscode_diag
        assert "message" in vscode_diag
        assert "severity" in vscode_diag
        assert "source" in vscode_diag

        # Verify values
        assert vscode_diag["range"]["start"]["line"] == 5
        assert vscode_diag["range"]["start"]["character"] == 10
        assert "CORE-011" in vscode_diag["message"]
        assert vscode_diag["severity"] == 1  # WARNING
        assert vscode_diag["source"] == "cortex-governance"


class TestVSCodeExtensionPackage:
    """Test VS Code extension package.json."""

    @pytest.fixture
    def package_json(self):
        """Get path to package.json."""
        return Path(__file__).parent.parent.parent / ".vscode-ext" / "package.json"

    def test_package_json_exists(self, package_json):
        """Test that package.json exists."""
        assert package_json.exists()

    def test_package_json_valid(self, package_json):
        """Test that package.json is valid JSON."""
        with open(package_json) as f:
            data = json.load(f)
        assert data is not None
        assert isinstance(data, dict)

    def test_package_has_required_fields(self, package_json):
        """Test that package.json has required fields."""
        with open(package_json) as f:
            data = json.load(f)

        required_fields = ["name", "displayName", "version", "engines", "main"]
        for field in required_fields:
            assert field in data, f"Missing required field: {field}"

    def test_extension_commands_defined(self, package_json):
        """Test that extension commands are defined."""
        with open(package_json) as f:
            data = json.load(f)

        commands = data.get("contributes", {}).get("commands", [])
        assert len(commands) > 0

        # Check for specific commands
        command_ids = [c.get("command") for c in commands]
        assert "cortex-governance.analyze" in command_ids
        assert "cortex-governance.clearCache" in command_ids


class TestExtensionImplementation:
    """Test extension.ts implementation."""

    @pytest.fixture
    def extension_file(self):
        """Get path to extension.ts."""
        return Path(__file__).parent.parent.parent / ".vscode-ext" / "extension.ts"

    def test_extension_file_exists(self, extension_file):
        """Test that extension.ts exists."""
        assert extension_file.exists()

    def test_extension_has_activate_function(self, extension_file):
        """Test that extension has activate function."""
        with open(extension_file) as f:
            content = f.read()
        assert "export function activate" in content

    def test_extension_has_deactivate_function(self, extension_file):
        """Test that extension has deactivate function."""
        with open(extension_file) as f:
            content = f.read()
        assert "export function deactivate" in content

    def test_extension_registers_commands(self, extension_file):
        """Test that extension registers commands."""
        with open(extension_file) as f:
            content = f.read()
        assert "registerCommand" in content
        assert "cortex-governance.analyze" in content

    def test_extension_listens_to_events(self, extension_file):
        """Test that extension listens to document events."""
        with open(extension_file) as f:
            content = f.read()
        assert "onDidOpenTextDocument" in content or "onDidOpenTextDocument" in content
        assert "onDidSaveTextDocument" in content


class TestAcceptanceCriteriaIDEIntegration:
    """Test acceptance criteria for GV-003-02."""

    @pytest.fixture
    def provider_script(self):
        """Get path to diagnostics provider."""
        return Path(__file__).parent.parent.parent / "src" / "tools" / "vscode-diagnostics-provider.py"

    @pytest.fixture
    def extension_file(self):
        """Get path to extension.ts."""
        return Path(__file__).parent.parent.parent / ".vscode-ext" / "extension.ts"

    def test_ac_1_governance_violations_shown_as_diagnostics(self, provider_script):
        """
        AC Criterion 1: Governance violations shown as diagnostics.
        """
        assert provider_script.exists()

        with open(provider_script) as f:
            content = f.read()

        # Verify diagnostic conversion
        assert "to_vscode_diagnostic" in content
        assert "DiagnosticSeverity" in content
        assert "GovernanceDiagnostic" in content

    def test_ac_2_quick_fixes_available(self, extension_file):
        """
        AC Criterion 2: Quick fixes available for common issues.
        """
        assert extension_file.exists()

        with open(extension_file) as f:
            content = f.read()

        # Verify code action provider for quick fixes
        assert "CodeActionProvider" in content or "codeActions" in content
        assert "fixSuggestion" in content or "Fix:" in content

    def test_ac_3_real_time_validation(self, extension_file):
        """
        AC Criterion 3: Real-time governance diagnostics in VS Code.
        """
        assert extension_file.exists()

        with open(extension_file) as f:
            content = f.read()

        # Verify real-time event listeners
        assert "onDidOpenTextDocument" in content
        assert "onDidSaveTextDocument" in content
        assert "onDidChangeConfiguration" in content


class TestDiagnosticsIntegration:
    """Integration tests for diagnostics with governance CLI."""

    @pytest.fixture
    def test_python_file(self, tmp_path):
        """Create a test Python file."""
        test_file = tmp_path / "test_violations.py"
        test_file.write_text("""
def function_without_hints(x):
    except:
        pass
""")
        return test_file

    def test_diagnostics_generated_from_cli_output(self, test_python_file):
        """Test that diagnostics are generated from CLI validation output."""
        cli_script = (
            Path(__file__).parent.parent.parent / "src" / "tools" / "governance-cli.py"
        )

        if not cli_script.exists():
            pytest.skip("CLI script not available")

        # Run CLI validation
        result = subprocess.run(
            ["python3", str(cli_script), "validate", str(test_python_file), "--format", "json"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        # Parse output
        data = json.loads(result.stdout)
        violations = data.get("violations", [])

        # Should have violations
        assert len(violations) > 0

        # Verify violation structure
        for violation in violations:
            assert "rule_id" in violation
            assert "message" in violation
            assert "severity" in violation


class TestConfigurationSettings:
    """Test VS Code configuration settings."""

    @pytest.fixture
    def package_json(self):
        """Get path to package.json."""
        return Path(__file__).parent.parent.parent / ".vscode-ext" / "package.json"

    def test_configuration_properties_defined(self, package_json):
        """Test that configuration properties are defined."""
        with open(package_json) as f:
            data = json.load(f)

        config = data.get("contributes", {}).get("configuration", {})
        properties = config.get("properties", {})

        expected_properties = [
            "cortex-governance.enable",
            "cortex-governance.severity",
            "cortex-governance.autoAnalyze",
            "cortex-governance.validateOnOpen",
            "cortex-governance.showQuickFixes",
        ]

        for prop in expected_properties:
            assert prop in properties, f"Missing configuration: {prop}"

    def test_keybindings_defined(self, package_json):
        """Test that keybindings are defined."""
        with open(package_json) as f:
            data = json.load(f)

        keybindings = data.get("contributes", {}).get("keybindings", [])
        assert len(keybindings) > 0

        # Check for governance analysis keybinding
        analyze_bindings = [kb for kb in keybindings if "cortex-governance.analyze" in kb.get("command", "")]
        assert len(analyze_bindings) > 0
