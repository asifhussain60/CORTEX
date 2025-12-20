"""
Tests for GitHub Pages Deployment Workflow

These tests validate the deployment workflow configuration and requirements.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary - See LICENSE file
"""

import pytest
from pathlib import Path
import yaml


class TestGitHubPagesDeployment:
    """
    Tests for Increment 3: GitHub Pages Deployment
    
    Acceptance Criteria:
    1. GitHub Action deploys on docs changes
    2. Build completes in <5 minutes
    3. Deploy to gh-pages succeeds
    4. Site accessible at asifhussain60.github.io/CORTEX
    5. Cache reduces build time by 50%+
    """
    
    @pytest.fixture
    def workflow_path(self):
        """Path to deploy-docs.yml workflow"""
        # Navigate from test file to repo root
        test_file = Path(__file__)
        repo_root = test_file.parent.parent.parent  # tests/ -> CORTEX/
        return repo_root / ".github" / "workflows" / "deploy-docs.yml"
    
    def test_workflow_file_exists(self, workflow_path):
        """AC1: GitHub Actions workflow exists"""
        assert workflow_path.exists(), "deploy-docs.yml workflow must exist"
    
    def test_workflow_has_valid_yaml(self, workflow_path):
        """AC1: Workflow is valid YAML"""
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        assert workflow is not None
        assert isinstance(workflow, dict)
    
    def test_workflow_triggers_on_docs_changes(self, workflow_path):
        """AC1: GitHub Action deploys on docs changes"""
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # YAML parses 'on:' as boolean True, so we check both
        trigger_key = "on" if "on" in workflow else True
        
        # Should trigger on push to CORTEX-3.0
        assert trigger_key in workflow
        assert "push" in workflow[trigger_key]
        
        push_config = workflow[trigger_key]["push"]
        assert "branches" in push_config
        assert "CORTEX-3.0" in push_config["branches"]
        
        # Should watch docs paths
        assert "paths" in push_config
        paths = push_config["paths"]
        assert any("docs" in p for p in paths), "Should watch docs/ directory"
        assert any("mkdocs.yml" in p for p in paths), "Should watch mkdocs.yml"
    
    def test_workflow_has_caching(self, workflow_path):
        """AC5: Cache configuration exists to reduce build time"""
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get("jobs", {})
        build_job = jobs.get("build-and-deploy", {})
        steps = build_job.get("steps", [])
        
        # Should have pip cache
        python_step = next((s for s in steps if s.get("uses", "").startswith("actions/setup-python")), None)
        assert python_step is not None
        assert python_step.get("with", {}).get("cache") == "pip", "Should enable pip caching"
        
        # Should have MkDocs build cache
        cache_steps = [s for s in steps if s.get("uses", "").startswith("actions/cache")]
        assert len(cache_steps) > 0, "Should have cache action"
        
        mkdocs_cache = next((s for s in cache_steps if "mkdocs" in s.get("name", "").lower()), None)
        assert mkdocs_cache is not None, "Should cache MkDocs build"
    
    def test_workflow_deploys_to_gh_pages(self, workflow_path):
        """AC3: Workflow deploys to gh-pages branch"""
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get("jobs", {})
        build_job = jobs.get("build-and-deploy", {})
        steps = build_job.get("steps", [])
        
        # Should have deployment step
        deploy_step = next((s for s in steps if "gh-pages" in s.get("uses", "").lower()), None)
        assert deploy_step is not None, "Should have gh-pages deployment action"
        
        # Should deploy to gh-pages branch
        deploy_with = deploy_step.get("with", {})
        assert deploy_with.get("publish_branch") == "gh-pages"
    
    def test_workflow_uses_intelligent_navigation_generator(self, workflow_path):
        """Integration: Workflow uses IntelligentNavigationGenerator"""
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        assert "IntelligentNavigationGenerator" in content
        assert "update_mkdocs_navigation" in content
    
    def test_workflow_uses_page_template_generator(self, workflow_path):
        """Integration: Workflow uses PageTemplateGenerator"""
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        assert "PageTemplateGenerator" in content
        assert "generate_api_reference" in content or "generate_operation_guides" in content
    
    def test_workflow_builds_mkdocs(self, workflow_path):
        """AC2: Workflow builds MkDocs site"""
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        assert "mkdocs build" in content
    
    def test_workflow_verifies_build_output(self, workflow_path):
        """AC2: Workflow verifies successful build"""
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        # Should check that site directory exists
        assert "site" in content
        assert "Build failed" in content or "error" in content.lower()
    
    def test_mkdocs_config_has_correct_site_url(self):
        """AC4: Site URL configured correctly"""
        test_file = Path(__file__)
        repo_root = test_file.parent.parent.parent  # tests/ -> CORTEX/
        mkdocs_path = repo_root / "mkdocs.yml"
        
        # Read as text to avoid YAML constructor issues
        with open(mkdocs_path, 'r') as f:
            content = f.read()
        
        # Check for site_url with correct value
        assert "site_url:" in content
        assert "asifhussain60.github.io/CORTEX" in content, \
            "Site URL should be https://asifhussain60.github.io/CORTEX/"
    
    def test_workflow_has_python_311(self, workflow_path):
        """Performance: Uses Python 3.11 for faster builds"""
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get("jobs", {})
        build_job = jobs.get("build-and-deploy", {})
        steps = build_job.get("steps", [])
        
        python_step = next((s for s in steps if s.get("uses", "").startswith("actions/setup-python")), None)
        assert python_step is not None
        
        python_version = python_step.get("with", {}).get("python-version")
        assert python_version == "3.11", "Should use Python 3.11 for performance"
    
    def test_workflow_has_concurrency_control(self, workflow_path):
        """Best Practice: Prevents concurrent deployments"""
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        assert "concurrency" in workflow
        concurrency = workflow["concurrency"]
        assert concurrency.get("group") == "pages"
        assert concurrency.get("cancel-in-progress") is False
    
    def test_workflow_has_manual_trigger(self, workflow_path):
        """Best Practice: Allows manual workflow dispatch"""
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        # YAML parses 'on:' as boolean True
        trigger_key = "on" if "on" in workflow else True
        assert "workflow_dispatch" in workflow[trigger_key], \
            "Should allow manual workflow trigger"
    
    def test_workflow_installs_required_mkdocs_plugins(self, workflow_path):
        """AC2: All required MkDocs plugins installed"""
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        required_packages = [
            "mkdocs",
            "mkdocs-material",
            "mkdocs-mermaid2-plugin",
            "pymdown-extensions"
        ]
        
        for package in required_packages:
            assert package in content, f"Should install {package}"
    
    def test_workflow_has_error_reporting(self, workflow_path):
        """Best Practice: Reports errors clearly"""
        with open(workflow_path, 'r') as f:
            content = f.read()
        
        assert "::error::" in content, "Should use GitHub Actions error annotations"
        assert "::notice::" in content or "::warning::" in content, \
            "Should use GitHub Actions notice/warning annotations"
    
    def test_workflow_optimizations_present(self, workflow_path):
        """AC5: Build optimizations implemented"""
        with open(workflow_path, 'r') as f:
            workflow = yaml.safe_load(f)
        
        jobs = workflow.get("jobs", {})
        build_job = jobs.get("build-and-deploy", {})
        steps = build_job.get("steps", [])
        
        # Check for optimizations
        optimizations = []
        
        # Pip cache
        python_step = next((s for s in steps if s.get("uses", "").startswith("actions/setup-python")), None)
        if python_step and python_step.get("with", {}).get("cache") == "pip":
            optimizations.append("pip_cache")
        
        # MkDocs build cache
        cache_steps = [s for s in steps if s.get("uses", "").startswith("actions/cache")]
        if cache_steps:
            optimizations.append("mkdocs_cache")
        
        # Python 3.11 (faster than 3.9/3.10)
        if python_step and python_step.get("with", {}).get("python-version") == "3.11":
            optimizations.append("python_311")
        
        assert len(optimizations) >= 3, \
            f"Should have at least 3 optimizations, found: {optimizations}"
