"""
Integration tests for LENSOrchestrator with multi-language support.

Tests that LENSOrchestrator correctly routes C# and Python files
through PolyglotAnalyzer.

Authority: ENH-017 Phase 2
"""

import pytest
from pathlib import Path
from cortex.lens.orchestrator import LENSOrchestrator


@pytest.fixture
def temp_repo(tmp_path):
    """Create temporary git repository."""
    repo_path = tmp_path / "test_repo"
    repo_path.mkdir()
    
    # Initialize git
    import subprocess
    subprocess.run(["git", "init"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Test"], cwd=repo_path, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=repo_path, check=True, capture_output=True)
    
    return repo_path


@pytest.fixture
def python_file(temp_repo):
    """Create Python file in repo."""
    file_path = temp_repo / "service.py"
    file_path.write_text('''
def process_data(data):
    """Process the data."""
    return data.upper()

class DataService:
    """Service for data operations."""
    def save(self, data):
        return True
''')
    return file_path


@pytest.fixture
def csharp_file(temp_repo):
    """Create C# file in repo."""
    file_path = temp_repo / "UserController.cs"
    file_path.write_text('''
using System;
using Microsoft.AspNetCore.Mvc;

namespace MyApp.Controllers
{
    public class UserController : Controller
    {
        public string Name { get; set; }
        
        public IActionResult GetUser(int id)
        {
            return Ok(new { Id = id, Name = Name });
        }
    }
}
''')
    return file_path


def test_orchestrator_analyzes_python_file(temp_repo, python_file):
    """Should analyze Python file through PolyglotAnalyzer."""
    orchestrator = LENSOrchestrator(repo_path=temp_repo)
    result = orchestrator.analyze_file(python_file)
    
    # Check AST analysis
    assert "ast_analysis" in result
    ast = result["ast_analysis"]
    
    assert ast["language"] == "Python"
    assert ast["function_count"] == 2  # process_data + save (methods are extracted as functions)
    assert ast["class_count"] == 1
    assert ast["functions"][0]["name"] == "process_data"
    assert ast["classes"][0]["name"] == "DataService"


def test_orchestrator_analyzes_csharp_file(temp_repo, csharp_file):
    """Should analyze C# file through PolyglotAnalyzer."""
    orchestrator = LENSOrchestrator(repo_path=temp_repo)
    result = orchestrator.analyze_file(csharp_file)
    
    # Check AST analysis
    assert "ast_analysis" in result
    ast = result["ast_analysis"]
    
    assert ast["language"] == "C#"
    assert ast["class_count"] == 1
    assert ast["classes"][0]["name"] == "UserController"
    assert ast["classes"][0]["namespace"] == "MyApp.Controllers"
    assert "GetUser" in ast["classes"][0]["methods"]
    assert len(ast["classes"][0]["properties"]) == 1
    assert ast["classes"][0]["properties"][0]["name"] == "Name"
    assert ast["import_count"] == 2  # using System, using Microsoft.AspNetCore.Mvc


def test_orchestrator_handles_unsupported_language(temp_repo):
    """Should handle unsupported file types gracefully."""
    ruby_file = temp_repo / "script.rb"
    ruby_file.write_text('puts "Hello"')
    
    orchestrator = LENSOrchestrator(repo_path=temp_repo)
    result = orchestrator.analyze_file(ruby_file)
    
    # Should still return result but with error
    assert "ast_analysis" in result
    ast = result["ast_analysis"]
    
    assert ast["language"] == "unknown"
    assert "error" in ast
    assert "Unsupported language" in ast["error"]
