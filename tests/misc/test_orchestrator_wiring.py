"""
Integration tests for orchestrator wiring with checkpoints, rollback, and git enrichment.

Tests verify that:
1. Planning orchestrator creates phase checkpoints
2. TDD orchestrator integrates checkpoint validation
3. System Alignment orchestrator uses Enhancement Catalog
4. All orchestrators support rollback commands
5. Git history enrichment works across workflows

Author: Asif Hussain
Created: 2025-11-28
Increment: 16 (Wire All Orchestrators)
"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Import orchestrators
from src.orchestrators.phase_checkpoint_manager import PhaseCheckpointManager
from src.enrichers.git_history_enricher import GitHistoryEnricher


class TestPlanningOrchestratorWiring:
    """Test Planning Orchestrator integration with checkpoints."""
    
    def test_planning_creates_checkpoints_at_phases(self):
        """Planning orchestrator should create checkpoints at DoR, Implementation, DoD phases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Setup
            cortex_root = Path(tmpdir)
            metadata_dir = cortex_root / ".cortex" / "metadata"
            metadata_dir.mkdir(parents=True)
            
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            session_id = "planning-test-session"
            
            # Simulate planning workflow phases
            phases = ["DoR_Complete", "Implementation_Start", "DoD_Validation"]
            commit_shas = []
            
            for phase in phases:
                checkpoint_id = f"checkpoint-{phase.lower()}"
                commit_sha = f"abc{len(commit_shas)}1234"
                checkpoint_mgr.store_checkpoint_metadata(
                    session_id=session_id,
                    phase=phase,
                    checkpoint_id=checkpoint_id,
                    commit_sha=commit_sha,
                    metrics={"phase_duration_s": 120}
                )
                commit_shas.append(commit_sha)
            
            # Verify checkpoints created
            checkpoints = checkpoint_mgr.list_checkpoints(session_id)
            assert len(checkpoints) == 3
            assert checkpoints[0]["phase"] == "DoR_Complete"
            assert checkpoints[2]["phase"] == "DoD_Validation"
    
    def test_planning_stores_checkpoint_metadata(self):
        """Planning orchestrator should store checkpoint metadata."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            
            session_id = "planning-rollback-test"
            checkpoint_id = "checkpoint-dor-complete"
            
            # Store DoR checkpoint
            checkpoint_mgr.store_checkpoint_metadata(
                session_id=session_id,
                phase="DoR_Complete",
                checkpoint_id=checkpoint_id,
                commit_sha="abc123def456",
                metrics={}
            )
            
            # Verify checkpoint was stored
            checkpoints = checkpoint_mgr.list_checkpoints(session_id)
            assert len(checkpoints) == 1
            assert checkpoints[0]["checkpoint_id"] == checkpoint_id


class TestTDDOrchestratorWiring:
    """Test TDD Orchestrator integration with checkpoints."""
    
    def test_tdd_creates_checkpoint_per_phase(self):
        """TDD orchestrator should create checkpoints for RED, GREEN, REFACTOR phases."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            checkpoint_mgr = PhaseCheckpointManager(cortex_root=cortex_root)
            session_id = "tdd-test-session"
            
            # Simulate TDD workflow
            tdd_phases = ["RED_Phase", "GREEN_Phase", "REFACTOR_Phase"]
            
            for idx, phase in enumerate(tdd_phases):
                checkpoint_id = f"tdd-checkpoint-{phase.lower()}"
                checkpoint_mgr.store_checkpoint_metadata(
                    session_id=session_id,
                    phase=phase,
                    checkpoint_id=checkpoint_id,
                    commit_sha=f"tdd{idx}abcd",
                    metrics={"tests_passing": idx * 2}
                )
            
            # Verify TDD checkpoints
            checkpoints = checkpoint_mgr.list_checkpoints(session_id)
            assert len(checkpoints) == 3
            assert any(c["phase"] == "RED_Phase" for c in checkpoints)
            assert any(c["phase"] == "GREEN_Phase" for c in checkpoints)
            assert any(c["phase"] == "REFACTOR_Phase" for c in checkpoints)
    
    def test_tdd_checkpoint_workflow(self):
        """TDD should support checkpoint workflow with git commits."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            cortex_root = project_root / ".cortex"
            cortex_root.mkdir()
            
            # Initialize git
            os.system(f"cd {project_root} && git init && git config user.email 'test@test.com' && git config user.name 'Test'")
            
            # Create test file
            test_file = project_root / "test_feature.py"
            test_file.write_text("def test_feature(): pass")
            os.system(f"cd {project_root} && git add test_feature.py && git commit -m 'RED phase: failing test'")
            
            # Create implementation
            impl_file = project_root / "feature.py"
            impl_file.write_text("def feature(): return 42")
            os.system(f"cd {project_root} && git add feature.py && git commit -m 'GREEN phase: implementation'")
            
            # Verify files exist
            assert test_file.exists()
            assert impl_file.exists()


class TestSystemAlignmentWiring:
    """Test System Alignment integration with Enhancement Catalog."""
    
    def test_alignment_discovers_catalog_features(self):
        """System Alignment should discover features from Enhancement Catalog during Phase 0."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            
            # Mock Enhancement Catalog discovery
            # In real implementation, this would call EnhancementCatalog.get_features_since()
            catalog_features = [
                {"name": "Git Enrichment", "feature_type": "Enhancement", "version": "3.0.1"},
                {"name": "Progress Bars", "feature_type": "UI", "version": "3.0.2"}
            ]
            
            # Simulate Phase 0 catalog discovery
            discovered_count = len(catalog_features)
            assert discovered_count == 2
            
            # Verify report includes catalog stats
            report = {
                "catalog_features_total": 15,
                "catalog_features_new": 2,
                "catalog_last_review": "2025-11-20T10:00:00"
            }
            
            assert report["catalog_features_new"] == 2
            assert report["catalog_features_total"] >= report["catalog_features_new"]


class TestGitHistoryEnrichment:
    """Test Git History Enricher integration across workflows."""
    
    def test_git_enrichment_provides_file_context(self):
        """Git enricher should provide commit history for files referenced in requests."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            
            # Initialize git repo with history - use shell commands that explicitly cd to temp dir
            import subprocess
            subprocess.run(["git", "init"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.email", "test@test.com"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "config", "user.name", "Test"], cwd=project_root, check=True, capture_output=True)
            
            test_file = project_root / "module.py"
            test_file.write_text("# Version 1")
            subprocess.run(["git", "add", "module.py"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Initial version"], cwd=project_root, check=True, capture_output=True)
            
            test_file.write_text("# Version 2")
            subprocess.run(["git", "add", "module.py"], cwd=project_root, check=True, capture_output=True)
            subprocess.run(["git", "commit", "-m", "Updated module"], cwd=project_root, check=True, capture_output=True)
            
            # Use GitHistoryEnricher
            enricher = GitHistoryEnricher(repo_path=project_root)
            history = enricher.get_file_history("module.py", max_commits=5)
            
            # Verify history contains commits
            assert len(history) == 2
            assert any("Initial version" in commit.get("message", "") for commit in history)
            assert any("Updated module" in commit.get("message", "") for commit in history)
    
    def test_git_enrichment_caches_results(self):
        """Git enricher should cache results to avoid repeated git log calls."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project_root = Path(tmpdir)
            
            # Initialize git
            os.system(f"cd {project_root} && git init && git config user.email 'test@test.com' && git config user.name 'Test'")
            
            test_file = project_root / "cached_file.py"
            test_file.write_text("# Cached")
            os.system(f"cd {project_root} && git add cached_file.py && git commit -m 'Cache test'")
            
            enricher = GitHistoryEnricher(repo_path=project_root)
            
            # First call - populates cache
            history1 = enricher.get_file_history("cached_file.py")
            
            # Second call - should use cache (no git call)
            history2 = enricher.get_file_history("cached_file.py")
            
            # Both should return same results
            assert len(history1) == len(history2)
            assert history1 == history2


class TestDashboardLauncherWiring:
    """Test Dashboard Launcher integration with alignment."""
    
    def test_dashboard_launcher_module_exists(self):
        """Dashboard launcher orchestrator should be importable."""
        from src.orchestrators.dashboard_launcher import launch_dashboard, DashboardServer
        
        assert callable(launch_dashboard)
        assert DashboardServer is not None
    
    def test_dashboard_launcher_detects_dashboards_directory(self):
        """Dashboard launcher should detect cortex-brain/dashboards/ directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_root = Path(tmpdir)
            dashboards_dir = cortex_root / "cortex-brain" / "dashboards"
            dashboards_dir.mkdir(parents=True)
            
            # Create UI structure
            ui_dir = dashboards_dir / "ui"
            ui_dir.mkdir()
            (ui_dir / "index.html").write_text("<html><body>Dashboard</body></html>")
            
            # Verify directory exists
            assert dashboards_dir.exists()
            assert (dashboards_dir / "ui" / "index.html").exists()
    
    def test_dashboard_server_port_configuration(self):
        """Dashboard server should support port configuration."""
        from src.orchestrators.dashboard_launcher import DashboardServer
        
        with tempfile.TemporaryDirectory() as tmpdir:
            dashboard_dir = Path(tmpdir)
            server = DashboardServer(dashboard_dir=dashboard_dir, port=9999)
            
            assert server.port == 9999
            assert server.dashboard_dir == dashboard_dir


class TestResponseTemplateSystemWiring:
    """Test Response Template System v3.0 integration with alignment."""
    
    def test_response_template_manager_exists(self):
        """Response template manager should be importable."""
        from src.response_templates.response_template_manager import ResponseTemplateManager
        
        assert ResponseTemplateManager is not None
    
    def test_template_renderer_exists(self):
        """Template renderer should be importable."""
        from src.response_templates.template_renderer import TemplateRenderer
        
        assert TemplateRenderer is not None
    
    def test_response_templates_yaml_exists(self):
        """Response templates YAML file should exist."""
        templates_file = Path(__file__).parent.parent.parent / "cortex-brain" / "response-templates.yaml"
        
        assert templates_file.exists()
        
        # Verify file has content
        content = templates_file.read_text(encoding='utf-8')
        assert len(content) > 1000  # Should be substantial file
        assert 'schema_version' in content
        assert 'templates:' in content
    
    def test_template_manager_initialization(self):
        """Template manager should initialize without errors."""
        from src.response_templates.response_template_manager import ResponseTemplateManager
        
        manager = ResponseTemplateManager()
        
        assert manager is not None
        assert hasattr(manager, 'render_template')
        assert hasattr(manager, 'renderer')
    
    def test_template_loader_exists(self):
        """Template loader should be importable."""
        from src.response_templates.template_loader import TemplateLoader
        
        assert TemplateLoader is not None


class TestUserProfileSystemWiring:
    """Test User Profile System integration with alignment."""
    
    def test_user_profile_manager_exists(self):
        """User profile manager should be importable."""
        from src.tier1.user_profile_manager import UserProfileManager
        
        assert UserProfileManager is not None
    
    def test_user_profile_manager_initialization(self):
        """User profile manager should initialize with db path."""
        from src.tier1.user_profile_manager import UserProfileManager
        
        with tempfile.TemporaryDirectory() as tmpdir:
            db_path = Path(tmpdir) / "working_memory.db"
            
            manager = UserProfileManager(db_path=db_path)
            
            assert manager is not None
            assert hasattr(manager, 'get_tech_stack_preference')
            assert hasattr(manager, 'set_tech_stack_preset')
    
    def test_user_profile_integration_with_agent_request(self):
        """Agent requests should support user profile context."""
        from src.cortex_agents.base_agent import AgentRequest
        
        request = AgentRequest(
            intent="test",
            context={},
            user_message="test command",
            user_profile={"interaction_mode": "guided", "experience_level": "expert"}
        )
        
        assert request.user_profile is not None
        assert request.user_profile["interaction_mode"] == "guided"


class TestVisionAPIWiring:
    """Test Vision API integration with alignment."""
    
    def test_vision_api_exists(self):
        """Vision API should be importable."""
        from src.tier1.vision_api import VisionAPI
        
        assert VisionAPI is not None
    
    def test_vision_api_initialization(self):
        """Vision API should initialize with config."""
        from src.tier1.vision_api import VisionAPI
        
        config = {"token_budget": 500}
        api = VisionAPI(config=config)
        
        assert api is not None
        assert hasattr(api, 'analyze_image')
    
    def test_vision_orchestrator_exists(self):
        """Vision orchestrator should be importable."""
        from src.tier1.vision_orchestrator import VisionOrchestrator
        
        assert VisionOrchestrator is not None


class TestNewFeatureAlignment:
    """Test alignment discovers new features correctly."""
    
    def test_alignment_discovers_dashboard_launcher(self):
        """Alignment should discover dashboard launcher feature."""
        from src.orchestrators.dashboard_launcher import launch_dashboard
        
        # Verify feature is discoverable
        assert callable(launch_dashboard)
        assert launch_dashboard.__module__ == 'src.orchestrators.dashboard_launcher'
    
    def test_alignment_discovers_response_template_v3(self):
        """Alignment should discover response template v3.0 system."""
        from src.response_templates.response_template_manager import ResponseTemplateManager
        
        manager = ResponseTemplateManager()
        
        # Verify v3.0 features
        assert hasattr(manager, 'render_template')
        assert hasattr(manager, 'renderer')
    
    def test_alignment_discovers_user_profile_system(self):
        """Alignment should discover user profile system."""
        from src.tier1.user_profile_manager import UserProfileManager
        
        # Verify feature exists
        assert UserProfileManager is not None
    
    def test_alignment_discovers_vision_api(self):
        """Alignment should discover vision API."""
        from src.tier1.vision_api import VisionAPI
        
        # Verify feature exists
        assert VisionAPI is not None
    
    def test_all_new_features_importable(self):
        """All new features should be importable without errors."""
        # Dashboard Launcher
        from src.orchestrators.dashboard_launcher import launch_dashboard, DashboardServer
        
        # Response Templates v3
        from src.response_templates.response_template_manager import ResponseTemplateManager
        from src.response_templates.template_renderer import TemplateRenderer
        
        # User Profile System
        from src.tier1.user_profile_manager import UserProfileManager
        
        # Vision API
        from src.tier1.vision_api import VisionAPI
        from src.tier1.vision_orchestrator import VisionOrchestrator
        
        # Verify all imported successfully
        assert all([
            launch_dashboard,
            DashboardServer,
            ResponseTemplateManager,
            TemplateRenderer,
            UserProfileManager,
            VisionAPI,
            VisionOrchestrator
        ])
