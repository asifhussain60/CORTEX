"""Tests for MCP Multi-Repo Tools - PHASE-DEPLOYMENT-003-mcp-expansion.

AC-DEP-003-03: Multi-repo tools enable cross-project governance.
Tests 6 multi-repo tools callable via MCP.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestProjectScannerDiscoversRepos:
    """Test project scanner discovers D:\\PROJECTS\\* structure."""

    def test_discovers_project_dirs(self):
        """Should discover project directories."""
        from cortex.mcp.tools.multi_repo.project_scanner import ProjectScanner
        
        scanner = ProjectScanner()
        
        with patch("pathlib.Path.iterdir") as mock_iterdir:
            mock_iterdir.return_value = [
                MagicMock(is_dir=lambda: True, name="CORTEX"),
                MagicMock(is_dir=lambda: True, name="ProjectA"),
                MagicMock(is_dir=lambda: False, name="file.txt"),
            ]
            
            projects = scanner.discover_projects(base_path="D:\\PROJECTS")
        
        assert len(projects) >= 2

    def test_identifies_cortex_enabled_projects(self):
        """Should identify projects with .cortex-version marker."""
        from cortex.mcp.tools.multi_repo.project_scanner import ProjectScanner
        
        scanner = ProjectScanner()
        
        with patch.object(scanner, "_has_cortex_marker") as mock_marker:
            mock_marker.side_effect = lambda p: p == "CORTEX"
            
            with patch.object(scanner, "_list_dirs") as mock_dirs:
                mock_dirs.return_value = ["CORTEX", "ProjectA"]
                
                projects = scanner.discover_projects(base_path="D:\\PROJECTS")
        
        cortex_enabled = [p for p in projects if p.get("cortex_enabled")]
        assert len(cortex_enabled) >= 1

    def test_returns_project_metadata(self):
        """Should return project metadata (name, path, cortex_enabled)."""
        from cortex.mcp.tools.multi_repo.project_scanner import ProjectScanner
        
        scanner = ProjectScanner()
        
        with patch.object(scanner, "_list_dirs") as mock_dirs:
            mock_dirs.return_value = ["CORTEX"]
            
            with patch.object(scanner, "_has_cortex_marker") as mock_marker:
                mock_marker.return_value = True
                
                projects = scanner.discover_projects(base_path="D:\\PROJECTS")
        
        assert "name" in projects[0]
        assert "path" in projects[0]
        assert "cortex_enabled" in projects[0]


class TestContextSwitcherLoadsTier1:
    """Test context switcher loads tier1 rules per project."""

    def test_loads_project_tier1_rules(self):
        """Should load tier1 rules for specified project."""
        from cortex.mcp.tools.multi_repo.context_switcher import ContextSwitcher
        
        switcher = ContextSwitcher()
        
        with patch.object(switcher, "_load_tier1_rules") as mock_load:
            mock_load.return_value = {"domain": "web", "rules": ["DOMAIN-001"]}
            
            context = switcher.switch_context(project_path="D:\\PROJECTS\\WebApp")
        
        assert "tier1_rules" in context
        assert context["tier1_rules"]["domain"] == "web"

    def test_preserves_tier0_rules(self):
        """Should preserve tier0 rules when switching context."""
        from cortex.mcp.tools.multi_repo.context_switcher import ContextSwitcher
        
        switcher = ContextSwitcher()
        
        with patch.object(switcher, "_load_tier1_rules") as mock_t1:
            mock_t1.return_value = {}
            
            with patch.object(switcher, "_get_tier0_rules") as mock_t0:
                mock_t0.return_value = {"rules": ["CORE-008"]}
                
                context = switcher.switch_context(project_path="D:\\PROJECTS\\WebApp")
        
        assert "tier0_rules" in context

    def test_updates_current_project_state(self):
        """Should update current project state."""
        from cortex.mcp.tools.multi_repo.context_switcher import ContextSwitcher
        
        switcher = ContextSwitcher()
        
        with patch.object(switcher, "_load_tier1_rules") as mock_load:
            mock_load.return_value = {}
            
            switcher.switch_context(project_path="D:\\PROJECTS\\WebApp")
        
        assert switcher.current_project == "D:\\PROJECTS\\WebApp"


class TestCrossRepoSearchFindsAcIds:
    """Test cross-repo search finds AC-ID references across repos."""

    def test_finds_ac_id_in_multiple_repos(self):
        """Should find AC-ID references across repositories."""
        from cortex.mcp.tools.multi_repo.cross_repo_search import CrossRepoSearch
        
        search = CrossRepoSearch()
        
        with patch.object(search, "_search_repo") as mock_search:
            mock_search.side_effect = [
                [{"file": "CORTEX/test.py", "line": 10, "match": "AC-INT-001"}],
                [{"file": "WebApp/module.py", "line": 5, "match": "AC-INT-001"}],
            ]
            
            results = search.search_ac_id("AC-INT-001", repos=["CORTEX", "WebApp"])
        
        assert len(results) >= 2

    def test_returns_file_and_line_info(self):
        """Should return file and line information."""
        from cortex.mcp.tools.multi_repo.cross_repo_search import CrossRepoSearch
        
        search = CrossRepoSearch()
        
        with patch.object(search, "_search_repo") as mock_search:
            mock_search.return_value = [
                {"file": "CORTEX/test.py", "line": 10, "match": "AC-INT-001"}
            ]
            
            results = search.search_ac_id("AC-INT-001", repos=["CORTEX"])
        
        assert "file" in results[0]
        assert "line" in results[0]

    def test_supports_wildcard_search(self):
        """Should support wildcard AC-ID search."""
        from cortex.mcp.tools.multi_repo.cross_repo_search import CrossRepoSearch
        
        search = CrossRepoSearch()
        
        with patch.object(search, "_search_repo") as mock_search:
            mock_search.return_value = [
                {"file": "CORTEX/test.py", "line": 10, "match": "AC-INT-001"},
                {"file": "CORTEX/test2.py", "line": 20, "match": "AC-INT-002"},
            ]
            
            results = search.search_ac_id("AC-INT-*", repos=["CORTEX"])
        
        assert len(results) >= 2


class TestSharedAuditQueriesUnifiedDb:
    """Test shared audit queries unified governance.db."""

    def test_queries_unified_database(self):
        """Should query unified governance database."""
        from cortex.mcp.tools.multi_repo.shared_audit import SharedAudit
        
        audit = SharedAudit()
        
        with patch.object(audit, "_query_unified_db") as mock_query:
            mock_query.return_value = [
                {"ac_id": "AC-INT-001", "project": "CORTEX"},
                {"ac_id": "AC-INT-002", "project": "WebApp"},
            ]
            
            results = audit.query(ac_id_pattern="AC-INT-*")
        
        assert len(results) >= 2
        projects = {r["project"] for r in results}
        assert len(projects) >= 2

    def test_filters_by_project(self):
        """Should filter audit entries by project."""
        from cortex.mcp.tools.multi_repo.shared_audit import SharedAudit
        
        audit = SharedAudit()
        
        with patch.object(audit, "_query_unified_db") as mock_query:
            mock_query.return_value = [
                {"ac_id": "AC-INT-001", "project": "CORTEX"},
            ]
            
            results = audit.query(project="CORTEX")
        
        assert all(r["project"] == "CORTEX" for r in results)

    def test_aggregates_cross_project_stats(self):
        """Should aggregate statistics across projects."""
        from cortex.mcp.tools.multi_repo.shared_audit import SharedAudit
        
        audit = SharedAudit()
        
        with patch.object(audit, "_query_unified_db") as mock_query:
            mock_query.return_value = [
                {"ac_id": "AC-INT-001", "project": "CORTEX"},
                {"ac_id": "AC-INT-002", "project": "CORTEX"},
                {"ac_id": "AC-WEB-001", "project": "WebApp"},
            ]
            
            stats = audit.aggregate_stats()
        
        assert "total_entries" in stats
        assert "by_project" in stats


class TestDependencyGraphShowsRelationships:
    """Test dependency graph shows inter-project dependencies."""

    def test_builds_dependency_graph(self):
        """Should build project dependency graph."""
        from cortex.mcp.tools.multi_repo.dependency_graph import DependencyGraph
        
        graph = DependencyGraph()
        
        with patch.object(graph, "_scan_dependencies") as mock_scan:
            mock_scan.return_value = {
                "CORTEX": [],
                "WebApp": ["CORTEX"],
                "Analytics": ["CORTEX", "WebApp"],
            }
            
            result = graph.build(projects=["CORTEX", "WebApp", "Analytics"])
        
        assert "nodes" in result
        assert "edges" in result

    def test_detects_circular_dependencies(self):
        """Should detect circular dependencies."""
        from cortex.mcp.tools.multi_repo.dependency_graph import DependencyGraph
        
        graph = DependencyGraph()
        
        with patch.object(graph, "_scan_dependencies") as mock_scan:
            mock_scan.return_value = {
                "A": ["B"],
                "B": ["C"],
                "C": ["A"],  # Circular
            }
            
            result = graph.build(projects=["A", "B", "C"])
        
        assert result["has_cycles"] is True
        assert "cycles" in result

    def test_returns_topological_order(self):
        """Should return topological order for builds."""
        from cortex.mcp.tools.multi_repo.dependency_graph import DependencyGraph
        
        graph = DependencyGraph()
        
        with patch.object(graph, "_scan_dependencies") as mock_scan:
            mock_scan.return_value = {
                "CORTEX": [],
                "WebApp": ["CORTEX"],
            }
            
            result = graph.build(projects=["CORTEX", "WebApp"])
        
        assert "build_order" in result
        assert result["build_order"].index("CORTEX") < result["build_order"].index("WebApp")


class TestProfileManagerAppliesProfiles:
    """Test profile manager applies governance profiles."""

    def test_applies_profile_to_project(self):
        """Should apply governance profile to project."""
        from cortex.mcp.tools.multi_repo.profile_manager import ProfileManager
        
        manager = ProfileManager()
        
        with patch.object(manager, "_get_profile") as mock_profile:
            mock_profile.return_value = {"name": "FinOps", "rules": ["FIN-001"]}
            
            with patch.object(manager, "_apply_to_project") as mock_apply:
                mock_apply.return_value = {"success": True}
                
                result = manager.apply_profile("FinOps", project_path="D:\\PROJECTS\\FinApp")
        
        assert result["success"] is True

    def test_lists_available_profiles(self):
        """Should list available governance profiles."""
        from cortex.mcp.tools.multi_repo.profile_manager import ProfileManager
        
        manager = ProfileManager()
        
        profiles = manager.list_profiles()
        
        assert len(profiles) >= 1
        assert all("name" in p for p in profiles)

    def test_validates_profile_compatibility(self):
        """Should validate profile compatibility with project."""
        from cortex.mcp.tools.multi_repo.profile_manager import ProfileManager
        
        manager = ProfileManager()
        
        with patch.object(manager, "_check_compatibility") as mock_check:
            mock_check.return_value = {"compatible": True, "warnings": []}
            
            result = manager.validate_profile("FinOps", project_path="D:\\PROJECTS\\FinApp")
        
        assert "compatible" in result
