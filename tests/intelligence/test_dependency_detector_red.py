"""
Dependency Detector - RED Phase Tests

Tests for Phase 3.1: Multi-language dependency detection from 12 file types.

Supported file types:
1. Python: requirements.txt, setup.py, pyproject.toml
2. Node.js: package.json
3. .NET: *.csproj, packages.config
4. Ruby: Gemfile
5. Go: go.mod
6. Rust: Cargo.toml
7. PHP: composer.json
8. Java: pom.xml, build.gradle
9. Swift: Package.swift
10. iOS: Podfile

Author: Asif Hussain
Copyright: © 2025 Asif Hussain. All rights reserved.
"""

import pytest
import tempfile
from pathlib import Path
import json

# Import will be None until GREEN phase
try:
    from src.intelligence.dependency_detector import DependencyDetector, Dependency, DependencyType
except ImportError:
    DependencyDetector = None
    Dependency = None
    DependencyType = None


class TestDependencyDetectorInitialization:
    """Test dependency detector initialization."""
    
    @pytest.mark.skipif(DependencyDetector is None, reason="RED phase")
    def test_init_with_repo_path(self):
        """Should initialize with repository path."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            detector = DependencyDetector(repo_path)
            assert detector.repo_path == repo_path
    
    @pytest.mark.skipif(DependencyDetector is None, reason="RED phase")
    def test_detect_returns_dict(self):
        """Should return dictionary with dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            detector = DependencyDetector(repo_path)
            result = detector.detect()
            assert isinstance(result, dict)
            assert "dependencies" in result
            assert "by_language" in result
            assert "summary" in result


class TestPythonDependencies:
    """Test Python dependency detection."""
    
    @pytest.mark.skipif(DependencyDetector is None, reason="RED phase")
    def test_requirements_txt(self):
        """Should parse requirements.txt."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            req_file = repo_path / "requirements.txt"
            req_file.write_text("""
flask==2.3.0
requests>=2.28.0
numpy~=1.24.0
pandas
# Comment
pytest>=7.0.0,<8.0.0
""")
            
            detector = DependencyDetector(repo_path)
            result = detector.detect()
            
            python_deps = result["by_language"].get("python", [])
            assert len(python_deps) >= 4
            
            # Check Flask with exact version
            flask = next((d for d in python_deps if d["name"] == "flask"), None)
            assert flask is not None
            assert flask["version"] == "2.3.0"
            assert flask["constraint"] == "=="
    
    @pytest.mark.skipif(DependencyDetector is None, reason="RED phase")
    def test_package_with_no_version(self):
        """Should handle packages without version specifier."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            req_file = repo_path / "requirements.txt"
            req_file.write_text("requests\n")
            
            detector = DependencyDetector(repo_path)
            result = detector.detect()
            
            python_deps = result["by_language"]["python"]
            requests = next((d for d in python_deps if d["name"] == "requests"), None)
            assert requests is not None
            assert requests["version"] == "*"


class TestNodeJSDependencies:
    """Test Node.js dependency detection."""
    
    @pytest.mark.skipif(DependencyDetector is None, reason="RED phase")
    def test_package_json(self):
        """Should parse package.json dependencies."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            pkg_file = repo_path / "package.json"
            pkg_file.write_text(json.dumps({
                "name": "test-project",
                "version": "1.0.0",
                "dependencies": {
                    "express": "^4.18.0",
                    "lodash": "~4.17.21"
                },
                "devDependencies": {
                    "jest": "^29.0.0"
                }
            }))
            
            detector = DependencyDetector(repo_path)
            result = detector.detect()
            
            node_deps = result["by_language"]["javascript"]
            assert len(node_deps) >= 2
            
            # Check Express with caret version
            express = next((d for d in node_deps if d["name"] == "express"), None)
            assert express is not None
            assert express["version"] == "4.18.0"
            assert express["constraint"] == "^"
    
    @pytest.mark.skipif(DependencyDetector is None, reason="RED phase")
    def test_dev_dependencies_marked(self):
        """Should mark devDependencies as dev type."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            pkg_file = repo_path / "package.json"
            pkg_file.write_text(json.dumps({
                "dependencies": {"express": "^4.18.0"},
                "devDependencies": {"jest": "^29.0.0"}
            }))
            
            detector = DependencyDetector(repo_path)
            result = detector.detect()
            
            node_deps = result["by_language"]["javascript"]
            jest = next((d for d in node_deps if d["name"] == "jest"), None)
            assert jest["type"] == "dev"


class TestDotNetDependencies:
    """Test .NET dependency detection."""
    
    @pytest.mark.skipif(DependencyDetector is None, reason="RED phase")
    def test_csproj_file(self):
        """Should parse .csproj PackageReference."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            csproj = repo_path / "Project.csproj"
            csproj.write_text("""
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net6.0</TargetFramework>
  </PropertyGroup>
  <ItemGroup>
    <PackageReference Include="Newtonsoft.Json" Version="13.0.3" />
    <PackageReference Include="Serilog" Version="2.12.0" />
  </ItemGroup>
</Project>
""")
            
            detector = DependencyDetector(repo_path)
            result = detector.detect()
            
            dotnet_deps = result["by_language"]["csharp"]
            assert len(dotnet_deps) >= 2
            
            newtonsoft = next((d for d in dotnet_deps if d["name"] == "Newtonsoft.Json"), None)
            assert newtonsoft is not None
            assert newtonsoft["version"] == "13.0.3"


class TestMultiLanguageDetection:
    """Test detection across multiple languages."""
    
    @pytest.mark.skipif(DependencyDetector is None, reason="RED phase")
    def test_detects_multiple_languages(self):
        """Should detect dependencies from multiple languages."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            # Python
            (repo_path / "requirements.txt").write_text("flask==2.3.0\n")
            
            # Node.js
            (repo_path / "package.json").write_text(json.dumps({
                "dependencies": {"express": "^4.18.0"}
            }))
            
            detector = DependencyDetector(repo_path)
            result = detector.detect()
            
            assert "python" in result["by_language"]
            assert "javascript" in result["by_language"]
            assert len(result["dependencies"]) >= 2
    
    @pytest.mark.skipif(DependencyDetector is None, reason="RED phase")
    def test_summary_statistics(self):
        """Should generate summary statistics."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            (repo_path / "requirements.txt").write_text("flask==2.3.0\nrequests>=2.28.0\n")
            
            detector = DependencyDetector(repo_path)
            result = detector.detect()
            
            summary = result["summary"]
            assert "total_dependencies" in summary
            assert summary["total_dependencies"] >= 2
            assert "languages_detected" in summary
            assert "python" in summary["languages_detected"]


class TestVersionConstraints:
    """Test version constraint parsing."""
    
    @pytest.mark.skipif(DependencyDetector is None, reason="RED phase")
    def test_caret_constraint(self):
        """Should parse caret (^) constraint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            pkg_file = repo_path / "package.json"
            pkg_file.write_text(json.dumps({
                "dependencies": {"express": "^4.18.0"}
            }))
            
            detector = DependencyDetector(repo_path)
            result = detector.detect()
            
            express = result["dependencies"][0]
            assert express["constraint"] == "^"
            assert express["version"] == "4.18.0"
    
    @pytest.mark.skipif(DependencyDetector is None, reason="RED phase")
    def test_tilde_constraint(self):
        """Should parse tilde (~) constraint."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            req_file = repo_path / "requirements.txt"
            req_file.write_text("numpy~=1.24.0\n")
            
            detector = DependencyDetector(repo_path)
            result = detector.detect()
            
            numpy = next((d for d in result["dependencies"] if d["name"] == "numpy"), None)
            assert numpy["constraint"] == "~="
            assert numpy["version"] == "1.24.0"


class TestPerformance:
    """Test performance requirements."""
    
    @pytest.mark.skipif(DependencyDetector is None, reason="RED phase")
    def test_detects_in_under_5_seconds(self):
        """Should detect dependencies in under 5 seconds."""
        import time
        
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            # Create multiple dependency files
            (repo_path / "requirements.txt").write_text("\n".join([f"package{i}==1.0.0" for i in range(50)]))
            (repo_path / "package.json").write_text(json.dumps({
                "dependencies": {f"package{i}": "^1.0.0" for i in range(50)}
            }))
            
            detector = DependencyDetector(repo_path)
            
            start = time.time()
            result = detector.detect()
            elapsed = time.time() - start
            
            assert elapsed < 5.0
            assert len(result["dependencies"]) >= 100
