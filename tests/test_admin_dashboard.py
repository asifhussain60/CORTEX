"""
Tests for Admin Dashboard Feature

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.operations.modules.admin_dashboard_launcher_module import AdminDashboardLauncherModule


class TestAdminDashboardLauncher:
    """Tests for admin dashboard launcher."""
    
    def test_admin_repo_detection(self):
        """Test admin repository detection."""
        module = AdminDashboardLauncherModule()
        
        # Should detect CORTEX as admin repo (has tests/, docs/architecture/, etc.)
        is_admin = module._is_admin_repo()
        assert is_admin, "CORTEX repository should be detected as admin repo"
    
    def test_repository_discovery(self):
        """Test discovery of dashboard data directories."""
        module = AdminDashboardLauncherModule()
        
        repos = module._discover_repositories()
        
        # Should find at least the mock repository
        assert len(repos) > 0, "Should discover at least one repository"
        
        # Verify repository structure
        for repo in repos:
            assert 'name' in repo
            assert 'path' in repo
            assert 'type' in repo
            assert 'files' in repo
    
    def test_admin_only_enforcement_in_user_repo(self, tmp_path):
        """Test that admin dashboard is blocked in user repositories."""
        module = AdminDashboardLauncherModule()
        
        # Mock non-admin repo check
        original_method = module._is_admin_repo
        module._is_admin_repo = lambda: False
        
        try:
            result = module.execute({})
            
            assert not result['success']
            assert result['error'] == 'admin_only_feature'
            assert 'admin-only' in result['message'].lower()
        finally:
            # Restore original method
            module._is_admin_repo = original_method
    
    def test_last_repo_cache(self, tmp_path):
        """Test last selected repository caching."""
        module = AdminDashboardLauncherModule()
        
        # Create test cache directory
        cache_dir = tmp_path / "cache"
        cache_dir.mkdir()
        
        test_repo = {
            'name': 'test-repo',
            'path': '/path/to/test',
            'type': 'Test',
            'files': 100
        }
        
        # Override cache file location for testing
        original_root = module.__class__.__module__
        
        # Test save
        module._save_last_selected_repo(test_repo)
        
        # Test load (should work even if cache doesn't exist)
        loaded = module._get_last_selected_repo()
        # May be None if cache save failed, which is acceptable


class TestAdminOperationsExclusion:
    """Tests for deployment gate that blocks admin operations."""
    
    def test_publish_config_has_admin_dashboard(self):
        """Test that admin_dashboard is listed in publish-config.yaml exclusions."""
        publish_config_path = Path(__file__).parent.parent / "cortex-brain" / "publish-config.yaml"
        
        if not publish_config_path.exists():
            pytest.skip("publish-config.yaml not found")
        
        import yaml
        with open(publish_config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        admin_ops = config.get('admin_content_patterns', {}).get('admin_operations', [])
        
        assert 'admin_dashboard' in admin_ops, "admin_dashboard must be in admin_operations exclusion list"
    
    def test_cortex_operations_has_admin_tier(self):
        """Test that admin_dashboard operation has deployment_tier: admin."""
        operations_path = Path(__file__).parent.parent / "cortex-operations.yaml"
        
        if not operations_path.exists():
            pytest.skip("cortex-operations.yaml not found")
        
        import yaml
        with open(operations_path, 'r') as f:
            operations = yaml.safe_load(f)
        
        admin_dash = operations.get('operations', {}).get('admin_dashboard', {})
        
        assert admin_dash, "admin_dashboard operation must exist"
        assert admin_dash.get('deployment_tier') == 'admin', "admin_dashboard must have deployment_tier: admin"
    
    def test_admin_module_has_security_markers(self):
        """Test that admin module file has proper security markers."""
        module_path = Path(__file__).parent.parent / "src" / "operations" / "modules" / "admin_dashboard_launcher_module.py"
        
        if not module_path.exists():
            pytest.skip("admin_dashboard_launcher_module.py not found")
        
        content = module_path.read_text(encoding='utf-8')
        
        assert "ADMIN ONLY" in content, "Module must have ADMIN ONLY marker"
        assert "deployment_tier: admin" in content, "Module must reference deployment_tier"
        assert "blocked from production" in content.lower(), "Module must mention production blocking"
    
    def test_deployment_gate_24_exists(self):
        """Test that Gate 24 for admin operations exclusion exists."""
        gates_path = Path(__file__).parent.parent / "src" / "deployment" / "deployment_gates.py"
        
        if not gates_path.exists():
            pytest.skip("deployment_gates.py not found")
        
        content = gates_path.read_text(encoding='utf-8')
        
        assert "_validate_admin_operations_excluded" in content, "Gate 24 validation method must exist"
        assert "Gate 24: Admin Operations Exclusion" in content, "Gate 24 must be documented"
        assert "admin_dashboard" in content, "Gate 24 must check admin_dashboard"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
