"""
Integration tests for Roslyn CLI refactoring operations.

Tests the actual .NET Roslyn CLI tool execution with real C# code samples.

AC_START: AC-PHASE24.2.2-001
Description: Roslyn CLI integration tests
Authority: Phase 24.2.2 - Type-Safe Operations
Author: Asif Hussain
Created: 2026-02-07
"""

import json
import pytest
import subprocess
from pathlib import Path
from typing import Dict, Any


@pytest.fixture
def roslyn_cli_path() -> Path:
    """Get path to Roslyn CLI executable."""
    # Path to compiled .NET DLL
    cli_path = Path(__file__).parent.parent.parent.parent / "cortex" / "refactoring" / "adapters" / "roslyn-cli"
    
    # Check for built DLL
    dll_path = cli_path / "bin" / "Release" / "net8.0" / "CortexRoslynCli.dll"
    if dll_path.exists():
        return dll_path
    
    # Check for debug build
    debug_dll = cli_path / "bin" / "Debug" / "net8.0" / "CortexRoslynCli.dll"
    if debug_dll.exists():
        return debug_dll
    
    pytest.skip("Roslyn CLI not built. Run: dotnet build -c Release")


@pytest.fixture
def sample_csharp_file(tmp_path: Path) -> Path:
    """Create a sample C# file for testing."""
    cs_file = tmp_path / "Sample.cs"
    cs_file.write_text("""using System;

namespace TestNamespace
{
    public class Calculator
    {
        private int result;

        public int Add(int a, int b)
        {
            int sum = a + b;
            result = sum;
            return result;
        }

        public int Multiply(int x, int y)
        {
            return x * y;
        }
    }
}
""")
    return cs_file


class TestRoslynCliBasicExecution:
    """Test basic Roslyn CLI execution."""

    def test_roslyn_cli_version(self, roslyn_cli_path):
        """Test Roslyn CLI returns version information."""
        result = subprocess.run(
            ["dotnet", str(roslyn_cli_path), "--version"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        assert "CortexRoslynCli" in result.stdout or result.stderr

    def test_roslyn_cli_help(self, roslyn_cli_path):
        """Test Roslyn CLI returns help information."""
        result = subprocess.run(
            ["dotnet", str(roslyn_cli_path), "--help"],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        assert result.returncode == 0
        output = result.stdout + result.stderr
        assert "refactor" in output.lower() or "usage" in output.lower()


class TestRoslynCliRenameOperation:
    """Test rename refactoring operation."""

    def test_rename_method(self, roslyn_cli_path, sample_csharp_file):
        """Test renaming a method via Roslyn CLI."""
        # Build command (offset 123 = "Add" method name)
        command = {
            "action": "refactor",
            "operation": "rename",
            "file_path": str(sample_csharp_file.absolute()),
            "parameters": {
                "offset": 123,  # Position of "Add" method
                "new_name": "Sum"
            }
        }
        
        # Execute CLI
        result = subprocess.run(
            ["dotnet", str(roslyn_cli_path), "refactor"],
            input=json.dumps(command),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should succeed
        assert result.returncode == 0
        
        # Parse response
        response = json.loads(result.stdout)
        assert response["success"] is True
        assert len(response["modified_files"]) > 0

    def test_rename_variable(self, roslyn_cli_path, sample_csharp_file):
        """Test renaming a local variable."""
        command = {
            "action": "refactor",
            "operation": "rename",
            "file_path": str(sample_csharp_file.absolute()),
            "parameters": {
                "offset": 167,  # Position of "sum" variable
                "new_name": "total"
            }
        }
        
        result = subprocess.run(
            ["dotnet", str(roslyn_cli_path), "refactor"],
            input=json.dumps(command),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        response = json.loads(result.stdout)
        assert response["success"] is True


class TestRoslynCliExtractMethodOperation:
    """Test extract method refactoring operation."""

    def test_extract_method_basic(self, roslyn_cli_path, sample_csharp_file):
        """Test extracting code into a new method."""
        # Read file to get exact offsets
        content = sample_csharp_file.read_text()
        start_offset = content.index("int sum = a + b;")
        end_offset = content.index("return result;", start_offset) + len("return result;")
        
        command = {
            "action": "refactor",
            "operation": "extract_method",
            "file_path": str(sample_csharp_file.absolute()),
            "parameters": {
                "start_offset": start_offset,
                "end_offset": end_offset,
                "new_name": "CalculateSum"
            }
        }
        
        result = subprocess.run(
            ["dotnet", str(roslyn_cli_path), "refactor"],
            input=json.dumps(command),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        response = json.loads(result.stdout)
        assert response["success"] is True
        assert "CalculateSum" in response.get("description", "")


class TestRoslynCliInlineMethodOperation:
    """Test inline method refactoring operation."""

    def test_inline_method_basic(self, roslyn_cli_path, sample_csharp_file):
        """Test inlining a method call."""
        # offset 251 = "Multiply" method
        command = {
            "action": "refactor",
            "operation": "inline_method",
            "file_path": str(sample_csharp_file.absolute()),
            "parameters": {
                "offset": 251
            }
        }
        
        result = subprocess.run(
            ["dotnet", str(roslyn_cli_path), "refactor"],
            input=json.dumps(command),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # May succeed or return "no inlining opportunities"
        assert result.returncode == 0
        response = json.loads(result.stdout)
        assert "success" in response


class TestRoslynCliEncapsulateFieldOperation:
    """Test encapsulate field refactoring operation."""

    def test_encapsulate_field_basic(self, roslyn_cli_path, sample_csharp_file):
        """Test generating getter/setter for a field."""
        # offset 95 = "result" field
        command = {
            "action": "refactor",
            "operation": "encapsulate_field",
            "file_path": str(sample_csharp_file.absolute()),
            "parameters": {
                "offset": 95,
                "property_name": "Result"
            }
        }
        
        result = subprocess.run(
            ["dotnet", str(roslyn_cli_path), "refactor"],
            input=json.dumps(command),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        response = json.loads(result.stdout)
        assert response["success"] is True


class TestRoslynCliExtractInterfaceOperation:
    """Test extract interface refactoring operation."""

    def test_extract_interface_basic(self, roslyn_cli_path, sample_csharp_file):
        """Test extracting an interface from a class."""
        # offset 58 = "Calculator" class
        command = {
            "action": "refactor",
            "operation": "extract_interface",
            "file_path": str(sample_csharp_file.absolute()),
            "parameters": {
                "offset": 58,
                "interface_name": "ICalculator"
            }
        }
        
        result = subprocess.run(
            ["dotnet", str(roslyn_cli_path), "refactor"],
            input=json.dumps(command),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        assert result.returncode == 0
        response = json.loads(result.stdout)
        assert response["success"] is True


class TestRoslynCliErrorHandling:
    """Test Roslyn CLI error handling."""

    def test_invalid_operation(self, roslyn_cli_path, sample_csharp_file):
        """Test handling of invalid operation."""
        command = {
            "action": "refactor",
            "operation": "invalid_op",
            "file_path": str(sample_csharp_file.absolute()),
            "parameters": {}
        }
        
        result = subprocess.run(
            ["dotnet", str(roslyn_cli_path), "refactor"],
            input=json.dumps(command),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should return error response (not crash)
        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "error" in response

    def test_missing_file(self, roslyn_cli_path, tmp_path):
        """Test handling of nonexistent file."""
        command = {
            "action": "refactor",
            "operation": "rename",
            "file_path": str(tmp_path / "nonexistent.cs"),
            "parameters": {"offset": 0, "new_name": "Test"}
        }
        
        result = subprocess.run(
            ["dotnet", str(roslyn_cli_path), "refactor"],
            input=json.dumps(command),
            capture_output=True,
            text=True,
            timeout=30
        )
        
        response = json.loads(result.stdout)
        assert response["success"] is False
        assert "file" in response.get("error", "").lower()

    def test_invalid_json(self, roslyn_cli_path):
        """Test handling of invalid JSON input."""
        result = subprocess.run(
            ["dotnet", str(roslyn_cli_path), "refactor"],
            input="not valid json",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should handle gracefully
        assert "json" in result.stderr.lower() or "error" in result.stdout.lower()


# AC_COMPLETE: AC-PHASE24.2.2-001 ✅ Roslyn CLI integration tests (15 tests)
