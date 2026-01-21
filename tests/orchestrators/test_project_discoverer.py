"""Tests for Project Discoverer - PHASE-DEPLOYMENT-004-multi-repo-gov.

AC-DEP-004-01: Project discovery scans D:\\PROJECTS\\* and registers projects.
"""

import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch


class TestScanDProjectsFolder:
    """Test scanning D:\\PROJECTS folder for projects."""

    def test_discovers_project_directories(self):
        """Should discover all project directories."""
        from cortex.orchestrators.project_discoverer import ProjectDiscoverer
        
        discoverer = ProjectDiscoverer()
        
        with patch.object(discoverer, "_list_directories") as mock_list:
            mock_list.return_value = ["CORTEX", "KASHKOLE", "KSESSIONS"]
            
            projects = discoverer.scan(base_path="D:\\PROJECTS")
        
        assert len(projects) >= 3

    def test_ignores_hidden_directories(self):
        """Should ignore hidden directories (starting with .)."""
        from cortex.orchestrators.project_discoverer import ProjectDiscoverer
        
        discoverer = ProjectDiscoverer()
        
        with patch.object(discoverer, "_list_directories") as mock_list:
            mock_list.return_value = [".git", "CORTEX", ".vscode"]
            
            projects = discoverer.scan(base_path="D:\\PROJECTS")
        
        project_names = [p["name"] for p in projects]
        assert ".git" not in project_names
        assert ".vscode" not in project_names

    def test_returns_project_metadata(self):
        """Should return project metadata."""
        from cortex.orchestrators.project_discoverer import ProjectDiscoverer
        
        discoverer = ProjectDiscoverer()
        
        with patch.object(discoverer, "_list_directories") as mock_list:
            mock_list.return_value = ["CORTEX"]
            
            with patch.object(discoverer, "_analyze_project") as mock_analyze:
                mock_analyze.return_value = {
                    "name": "CORTEX",
                    "path": "D:\\PROJECTS\\CORTEX",
                    "type": "governance",
                    "has_cortex_config": True,
                }
                
                projects = discoverer.scan(base_path="D:\\PROJECTS")
        
        assert "name" in projects[0]
        assert "path" in projects[0]


class TestDetectCortexConfigYaml:
    """Test detection of .cortex-config.yaml marker."""

    def test_detects_cortex_config_present(self):
        """Should detect when .cortex-config.yaml exists."""
        from cortex.orchestrators.project_discoverer import ProjectDiscoverer
        
        discoverer = ProjectDiscoverer()
        
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = True
            
            result = discoverer.has_cortex_config("D:\\PROJECTS\\CORTEX")
        
        assert result is True

    def test_detects_cortex_config_absent(self):
        """Should detect when .cortex-config.yaml is missing."""
        from cortex.orchestrators.project_discoverer import ProjectDiscoverer
        
        discoverer = ProjectDiscoverer()
        
        with patch("pathlib.Path.exists") as mock_exists:
            mock_exists.return_value = False
            
            result = discoverer.has_cortex_config("D:\\PROJECTS\\OtherProject")
        
        assert result is False


class TestInferProjectType:
    """Test project type inference."""

    def test_infers_financial_type_from_name(self):
        """Should infer financial type from project name."""
        from cortex.orchestrators.project_discoverer import ProjectDiscoverer
        
        discoverer = ProjectDiscoverer()
        
        result = discoverer.infer_project_type("KASHKOLE", indicators=["financial", "payment"])
        
        assert result == "finops"

    def test_infers_auth_type_from_name(self):
        """Should infer auth type from session/auth indicators."""
        from cortex.orchestrators.project_discoverer import ProjectDiscoverer
        
        discoverer = ProjectDiscoverer()
        
        result = discoverer.infer_project_type("KSESSIONS", indicators=["session", "auth"])
        
        assert result == "auth"

    def test_infers_ml_type_from_indicators(self):
        """Should infer ML type from ML indicators."""
        from cortex.orchestrators.project_discoverer import ProjectDiscoverer
        
        discoverer = ProjectDiscoverer()
        
        result = discoverer.infer_project_type("MLProject", indicators=["model", "training"])
        
        assert result == "ml"

    def test_defaults_to_general_type(self):
        """Should default to general type when no match."""
        from cortex.orchestrators.project_discoverer import ProjectDiscoverer
        
        discoverer = ProjectDiscoverer()
        
        result = discoverer.infer_project_type("RandomProject", indicators=[])
        
        assert result == "general"


class TestRegisterProjectsDb:
    """Test project registration in database."""

    def test_registers_project_in_db(self):
        """Should register project in projects.db."""
        from cortex.orchestrators.project_discoverer import ProjectDiscoverer
        
        discoverer = ProjectDiscoverer()
        
        with patch.object(discoverer, "_db_insert") as mock_insert:
            mock_insert.return_value = True
            
            result = discoverer.register_project({
                "project_id": "CORTEX",
                "path": "D:\\PROJECTS\\CORTEX",
                "type": "governance",
                "tier1_profile": "devops",
            })
        
        assert result is True

    def test_updates_existing_project(self):
        """Should update existing project entry."""
        from cortex.orchestrators.project_discoverer import ProjectDiscoverer
        
        discoverer = ProjectDiscoverer()
        
        with patch.object(discoverer, "_db_upsert") as mock_upsert:
            mock_upsert.return_value = True
            
            result = discoverer.register_project({
                "project_id": "CORTEX",
                "path": "D:\\PROJECTS\\CORTEX",
                "type": "governance",
                "tier1_profile": "devops",
            }, update_existing=True)
        
        assert result is True
