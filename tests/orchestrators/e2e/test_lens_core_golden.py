"""
CORTEX LENS Golden Tests - Core Capabilities

Authority: AC-GOLDEN-LENS-CORE-001
Tests for core LENS analyzers (AST, Git, Config, API, Database, etc.)

Coverage:
- golden_04: Python AST Analysis
- golden_05: .NET Solution Analysis
- golden_06: Git History Analysis
- golden_07: Config Extraction
- golden_08: API Discovery
- golden_09: Database Schema Analysis
- golden_10: Dependency Graph
- golden_11: Architecture Lens
"""

import pytest
from pathlib import Path

from tests.orchestrators.e2e.test_lens_golden_harness import LENSGoldenTestHarness


class TestLENSCoreCapabilities:
    """Golden tests for LENS core analyzer capabilities."""
    
    @pytest.mark.lens
    @pytest.mark.xfail(reason="RED phase - LENS orchestrator wiring pending")
    def test_golden_04_python_ast_analysis(self, lens_harness: LENSGoldenTestHarness):
        """
        Golden Test 04: Python AST Analysis
        
        Validates:
        - Python file parsing
        - Class extraction (UserService)
        - Method extraction (__init__, authenticate, _verify_password)
        - Complexity metrics calculation
        """
        result = lens_harness.execute_lens_scenario("lens/core/golden_04_python_ast_analysis")
        
        assert result.passed, f"AST analysis failed: {result.diffs}"
        
        # Verify audit trail
        events = lens_harness.get_audit_events()
        assert any(e['activity'] == 'ANALYZE_AST' for e in events)
        assert any(e['activity'] == 'EXTRACT_STRUCTURE' for e in events)
    
    @pytest.mark.lens
    @pytest.mark.xfail(reason="RED phase - LENS orchestrator wiring pending")
    def test_golden_05_dotnet_solution_analysis(self, lens_harness: LENSGoldenTestHarness):
        """
        Golden Test 05: .NET Solution Analysis
        
        Validates:
        - .sln file parsing
        - .csproj parsing
        - Project reference resolution
        - Framework version detection (net8.0)
        """
        result = lens_harness.execute_lens_scenario("lens/core/golden_05_dotnet_solution_analysis")
        
        assert result.passed, f".NET solution analysis failed: {result.diffs}"
    
    @pytest.mark.lens
    @pytest.mark.xfail(reason="RED phase - Git setup required")
    def test_golden_06_git_history_analysis(self, lens_harness: LENSGoldenTestHarness):
        """
        Golden Test 06: Git History Analysis
        
        Validates:
        - Git commit parsing
        - Hotspot detection (auth.py with 3+ changes)
        - Churn calculation
        - Contributor tracking
        """
        result = lens_harness.execute_lens_scenario("lens/core/golden_06_git_history_analysis")
        
        assert result.passed, f"Git history analysis failed: {result.diffs}"
    
    @pytest.mark.lens
    @pytest.mark.xfail(reason="RED phase - Config analyzer wiring pending")
    def test_golden_07_config_extraction(self, lens_harness: LENSGoldenTestHarness):
        """
        Golden Test 07: Config Extraction
        
        Validates:
        - YAML parsing (app.yaml)
        - JSON parsing (secrets.json)
        - .env file parsing
        - Secret detection (API keys, passwords)
        """
        result = lens_harness.execute_lens_scenario("lens/core/golden_07_config_extraction")
        
        assert result.passed, f"Config extraction failed: {result.diffs}"
    
    @pytest.mark.lens
    @pytest.mark.xfail(reason="RED phase - API analyzer wiring pending")
    def test_golden_08_api_discovery(self, lens_harness: LENSGoldenTestHarness):
        """
        Golden Test 08: API Discovery
        
        Validates:
        - OpenAPI 3.0 parsing
        - Endpoint extraction (/users, /users/{id})
        - HTTP method detection (GET, POST)
        - Security scheme extraction (bearerAuth)
        """
        result = lens_harness.execute_lens_scenario("lens/core/golden_08_api_discovery")
        
        assert result.passed, f"API discovery failed: {result.diffs}"
    
    @pytest.mark.lens
    @pytest.mark.xfail(reason="RED phase - Database analyzer wiring pending")
    def test_golden_09_database_schema_analysis(self, lens_harness: LENSGoldenTestHarness):
        """
        Golden Test 09: Database Schema Analysis
        
        Validates:
        - SQL migration parsing
        - Table extraction (users, orders)
        - Foreign key detection
        - Index extraction
        """
        result = lens_harness.execute_lens_scenario("lens/core/golden_09_database_schema_analysis")
        
        assert result.passed, f"Database analysis failed: {result.diffs}"
    
    @pytest.mark.lens
    @pytest.mark.xfail(reason="RED phase - Dependency analyzer wiring pending")
    def test_golden_10_dependency_graph(self, lens_harness: LENSGoldenTestHarness):
        """
        Golden Test 10: Dependency Graph
        
        Validates:
        - requirements.txt parsing (Python deps)
        - package.json parsing (Node.js deps)
        - Multi-ecosystem detection
        - Dependency graph construction
        """
        result = lens_harness.execute_lens_scenario("lens/core/golden_10_dependency_graph")
        
        assert result.passed, f"Dependency graph analysis failed: {result.diffs}"
    
    @pytest.mark.lens
    @pytest.mark.xfail(reason="RED phase - Architecture analyzer wiring pending")
    def test_golden_11_architecture_lens(self, lens_harness: LENSGoldenTestHarness):
        """
        Golden Test 11: Architecture Lens
        
        Validates:
        - Layered architecture detection
        - Repository pattern identification
        - Layer violation detection
        - Component hierarchy building
        """
        result = lens_harness.execute_lens_scenario("lens/core/golden_11_architecture_lens")
        
        assert result.passed, f"Architecture analysis failed: {result.diffs}"


class TestLENSCoreIntegration:
    """Integration tests for core LENS capabilities."""
    
    @pytest.mark.lens
    @pytest.mark.integration
    def test_temp_repo_builder_creates_files(self, temp_repo_builder):
        """Test that TempRepoBuilder creates files correctly."""
        from tests.orchestrators.e2e.test_lens_golden_harness import TempRepoBuilder
        
        builder = temp_repo_builder
        
        files = {
            "src/main.py": "print('hello')",
            "src/utils.py": "def util(): pass",
        }
        
        repo_path = builder.create_repo("test_repo", files)
        
        assert repo_path.exists()
        assert (repo_path / "src" / "main.py").exists()
        assert (repo_path / "src" / "utils.py").read_text() == "def util(): pass"
    
    @pytest.mark.lens
    @pytest.mark.integration
    def test_temp_repo_builder_creates_git_repo(self, temp_repo_builder):
        """Test that TempRepoBuilder creates git repos with commits."""
        builder = temp_repo_builder
        
        files = {"README.md": "# Test"}
        commits = [
            {"message": "Initial commit", "files": ["README.md"]}
        ]
        
        repo_path = builder.create_git_repo("git_repo", files, commits)
        
        assert repo_path.exists()
        assert (repo_path / ".git").exists()
    
    @pytest.mark.lens
    def test_lens_harness_loads_scenario(self, lens_harness: LENSGoldenTestHarness):
        """Test that LENS harness can load scenarios."""
        scenario = lens_harness.load_scenario("lens/core/golden_04_python_ast_analysis")
        
        assert scenario.name == "golden_04_python_ast_analysis"
        assert "analyze Python codebase structure" in scenario.utterance
        assert len(scenario.expected_audit_events) > 0
