"""Tests for cortex-registry-001-migration phase."""
import pytest
from pathlib import Path


class TestRegistryStructure:
    """Test cortex-registry/ folder structure."""
    
    def test_registry_root_exists(self):
        """AC-REG-001: Registry root directory exists."""
        registry_root = Path("cortex-registry")
        assert registry_root.exists(), "cortex-registry/ directory must exist"
        assert registry_root.is_dir(), "cortex-registry/ must be a directory"
    
    def test_plan_type_segregation_directories_exist(self):
        """AC-REG-002: Plan-type segregation directories created."""
        registry_root = Path("cortex-registry")
        required_dirs = ["master", "planning", "ado", "interaction", "domains"]
        
        for dir_name in required_dirs:
            dir_path = registry_root / dir_name
            assert dir_path.exists(), f"{dir_name}/ must exist"
            assert dir_path.is_dir(), f"{dir_name}/ must be a directory"
    
    def test_manifest_exists(self):
        """AC-REG-004: Registry manifest created."""
        manifest_path = Path("cortex-registry") / "manifest.yaml"
        assert manifest_path.exists(), "manifest.yaml must exist"
        
        # Verify it's valid YAML and has required keys
        import yaml
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        
        assert "metadata" in manifest, "manifest.yaml must have metadata section"
        assert "structure" in manifest, "manifest.yaml must have structure section"
        assert "registry_access" in manifest, "manifest.yaml must have registry_access section"
    
    def test_domains_directory_for_multi_domain_support(self):
        """AC-REG-005: Domain segregation support added."""
        domains_path = Path("cortex-registry") / "domains"
        assert domains_path.exists(), "domains/ directory must exist for multi-domain support"
        assert domains_path.is_dir(), "domains/ must be a directory"
    
    def test_registry_plan_type_isolation(self):
        """AC-REG-003: Plan-type segregation prevents mixing."""
        registry_root = Path("cortex-registry")
        
        # Verify each plan-type is isolated
        for plan_type in ["master", "planning", "ado", "interaction"]:
            plan_path = registry_root / plan_type
            assert plan_path.exists(), f"{plan_type}/ must exist"
            # Should not contain other plan types
            for other_type in ["master", "planning", "ado", "interaction"]:
                if other_type != plan_type:
                    assert not (plan_path / other_type).exists(), \
                        f"{plan_type}/ should not contain {other_type}/"
    
    def test_registry_manifest_has_access_rules(self):
        """AC-REG-006: Integration with orchestrators configured."""
        manifest_path = Path("cortex-registry") / "manifest.yaml"
        
        import yaml
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        
        access = manifest.get("registry_access", {})
        required_orchestrators = ["master_orchestrator", "planning_orchestrator", 
                                 "ado_orchestrator", "interaction_orchestrator"]
        
        for orchestrator in required_orchestrators:
            assert orchestrator in access, f"{orchestrator} must have access rules defined"


class TestRegistryMigration:
    """Test migration from _workspaces/roadmap to cortex-registry."""
    
    def test_registry_active_after_migration(self):
        """Registry is marked as active after migration."""
        manifest_path = Path("cortex-registry") / "manifest.yaml"
        
        import yaml
        with open(manifest_path) as f:
            manifest = yaml.safe_load(f)
        
        migration_status = manifest.get("migration_status", {})
        assert migration_status.get("cortex_registry") == "ACTIVE", \
            "cortex_registry must be marked as ACTIVE"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
