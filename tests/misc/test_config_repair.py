"""
Tests for configuration auto-repair system
Automatically fixes common CORTEX config issues

TDD Phase: RED - Tests written first, expected to fail
"""

import pytest
from pathlib import Path
import json
import tempfile
import shutil
import os

from src.utils.config_repair import (
    ConfigRepair,
    RepairResult,
    RepairAction,
    RepairStatus
)


class TestConfigRepair:
    """Test configuration auto-repair functionality"""
    
    @pytest.fixture
    def temp_cortex_dir(self):
        """Create temporary CORTEX directory"""
        temp_dir = tempfile.mkdtemp()
        cortex_dir = Path(temp_dir) / "CORTEX"
        cortex_dir.mkdir()
        
        yield cortex_dir
        
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def valid_config_template(self):
        """Valid config template"""
        return {
            "machines": {
                "example-machine": {
                    "rootPath": "/path/to/CORTEX",
                    "brainPath": "/path/to/CORTEX/cortex-brain"
                }
            },
            "version": "3.2.0",
            "governance": {
                "tdd_enforcement": True,
                "skull_protection": True
            }
        }
    
    def test_repair_initialization(self, temp_cortex_dir):
        """Test ConfigRepair can be initialized"""
        repair = ConfigRepair(root_path=temp_cortex_dir)
        
        assert repair is not None
        assert repair.root_path == temp_cortex_dir
    
    def test_create_missing_directories(self, temp_cortex_dir):
        """Test auto-creation of missing brain directories"""
        repair = ConfigRepair(root_path=temp_cortex_dir)
        result = repair.create_missing_directories()
        
        assert result.status == RepairStatus.SUCCESS
        
        # Check all required directories created
        brain_dir = temp_cortex_dir / "cortex-brain"
        assert brain_dir.exists()
        assert (brain_dir / "tier0").exists()
        assert (brain_dir / "tier1").exists()
        assert (brain_dir / "tier2").exists()
        assert (brain_dir / "tier3").exists()
        assert (brain_dir / "documents").exists()
    
    def test_create_missing_directories_idempotent(self, temp_cortex_dir):
        """Test directory creation is idempotent (safe to run multiple times)"""
        repair = ConfigRepair(root_path=temp_cortex_dir)
        
        # Run twice
        result1 = repair.create_missing_directories()
        result2 = repair.create_missing_directories()
        
        # First run should create directories
        assert result1.status == RepairStatus.SUCCESS
        # Second run should recognize no action needed
        assert result2.status == RepairStatus.NO_ACTION_NEEDED
    
    def test_repair_missing_config_file(self, temp_cortex_dir, valid_config_template):
        """Test creation of missing config file from template"""
        # Create template
        template_path = temp_cortex_dir / "cortex.config.template.json"
        template_path.write_text(json.dumps(valid_config_template, indent=2))
        
        repair = ConfigRepair(root_path=temp_cortex_dir)
        result = repair.repair_config_file()
        
        assert result.status == RepairStatus.SUCCESS
        
        # Check config created
        config_path = temp_cortex_dir / "cortex.config.json"
        assert config_path.exists()
        
        # Verify valid JSON
        config = json.loads(config_path.read_text())
        assert "machines" in config
    
    def test_repair_malformed_json(self, temp_cortex_dir, valid_config_template):
        """Test repair of malformed JSON config"""
        # Create malformed config
        config_path = temp_cortex_dir / "cortex.config.json"
        config_path.write_text("{ invalid json }")
        
        # Create valid template
        template_path = temp_cortex_dir / "cortex.config.template.json"
        template_path.write_text(json.dumps(valid_config_template, indent=2))
        
        repair = ConfigRepair(root_path=temp_cortex_dir)
        result = repair.repair_config_file()
        
        assert result.status == RepairStatus.SUCCESS
        
        # Should backup old file and create new from template
        assert (temp_cortex_dir / "cortex.config.json.backup").exists()
        
        # Verify new config is valid
        config = json.loads(config_path.read_text())
        assert "machines" in config
    
    def test_repair_missing_machines_key(self, temp_cortex_dir):
        """Test repair of config missing 'machines' key"""
        config_path = temp_cortex_dir / "cortex.config.json"
        config_path.write_text(json.dumps({"version": "3.2.0"}))
        
        repair = ConfigRepair(root_path=temp_cortex_dir)
        result = repair.repair_config_structure()
        
        assert result.status == RepairStatus.SUCCESS
        
        # Check machines key added
        config = json.loads(config_path.read_text())
        assert "machines" in config
    
    def test_repair_adds_missing_version(self, temp_cortex_dir):
        """Test repair adds missing version field"""
        config = {"machines": {}}
        config_path = temp_cortex_dir / "cortex.config.json"
        config_path.write_text(json.dumps(config))
        
        repair = ConfigRepair(root_path=temp_cortex_dir)
        result = repair.repair_config_structure()
        
        assert result.status == RepairStatus.SUCCESS
        
        # Check version added
        updated_config = json.loads(config_path.read_text())
        assert "version" in updated_config
    
    def test_fix_file_permissions(self, temp_cortex_dir):
        """Test repair of incorrect file permissions"""
        config_path = temp_cortex_dir / "cortex.config.json"
        config_path.write_text(json.dumps({"machines": {}}))
        
        # Set restrictive permissions
        os.chmod(config_path, 0o000)
        
        repair = ConfigRepair(root_path=temp_cortex_dir)
        result = repair.fix_permissions()
        
        assert result.status == RepairStatus.SUCCESS
        
        # Check permissions fixed (readable)
        assert os.access(config_path, os.R_OK)
    
    def test_repair_action_tracking(self, temp_cortex_dir):
        """Test RepairResult tracks actions taken"""
        repair = ConfigRepair(root_path=temp_cortex_dir)
        result = repair.create_missing_directories()
        
        assert len(result.actions) > 0
        
        # Check action details
        for action in result.actions:
            assert isinstance(action, RepairAction)
            assert action.description is not None
            assert action.target_path is not None
    
    def test_repair_all_comprehensive(self, temp_cortex_dir, valid_config_template):
        """Test comprehensive repair runs all fixes"""
        # Create template
        template_path = temp_cortex_dir / "cortex.config.template.json"
        template_path.write_text(json.dumps(valid_config_template, indent=2))
        
        repair = ConfigRepair(root_path=temp_cortex_dir)
        result = repair.repair_all()
        
        assert result.status in [RepairStatus.SUCCESS, RepairStatus.PARTIAL]
        
        # Check multiple repairs executed
        assert len(result.actions) > 0
    
    def test_repair_preserves_existing_config(self, temp_cortex_dir):
        """Test repair doesn't overwrite valid existing config"""
        valid_config = {
            "machines": {
                "my-machine": {
                    "rootPath": "/custom/path",
                    "brainPath": "/custom/path/cortex-brain"
                }
            },
            "version": "3.2.0"
        }
        
        config_path = temp_cortex_dir / "cortex.config.json"
        config_path.write_text(json.dumps(valid_config, indent=2))
        
        repair = ConfigRepair(root_path=temp_cortex_dir)
        result = repair.repair_config_file()
        
        # Should not modify valid config
        current_config = json.loads(config_path.read_text())
        assert current_config["machines"]["my-machine"]["rootPath"] == "/custom/path"
    
    def test_repair_status_enum(self):
        """Test RepairStatus enum values"""
        assert RepairStatus.SUCCESS.value == "success"
        assert RepairStatus.FAILED.value == "failed"
        assert RepairStatus.PARTIAL.value == "partial"
        assert RepairStatus.NO_ACTION_NEEDED.value == "no_action_needed"
    
    def test_repair_action_creation(self):
        """Test RepairAction dataclass creation"""
        action = RepairAction(
            description="Created missing directory",
            target_path="/path/to/dir",
            action_type="create_directory"
        )
        
        assert action.description == "Created missing directory"
        assert action.target_path == "/path/to/dir"
        assert action.action_type == "create_directory"
    
    def test_repair_result_has_message(self, temp_cortex_dir):
        """Test RepairResult includes human-readable message"""
        repair = ConfigRepair(root_path=temp_cortex_dir)
        result = repair.create_missing_directories()
        
        assert result.message is not None
        assert isinstance(result.message, str)
        assert len(result.message) > 0
    
    def test_backup_config_before_repair(self, temp_cortex_dir):
        """Test config is backed up before dangerous operations"""
        config_path = temp_cortex_dir / "cortex.config.json"
        original_content = '{"machines": {}, "custom_field": "preserve_me"}'
        config_path.write_text(original_content)
        
        repair = ConfigRepair(root_path=temp_cortex_dir)
        backup_path = repair.backup_config()
        
        assert backup_path is not None
        assert backup_path.exists()
        
        # Verify backup has original content
        assert backup_path.read_text() == original_content
    
    def test_repair_validates_after_fix(self, temp_cortex_dir, valid_config_template):
        """Test repair validates config after fixing"""
        template_path = temp_cortex_dir / "cortex.config.template.json"
        template_path.write_text(json.dumps(valid_config_template, indent=2))
        
        repair = ConfigRepair(root_path=temp_cortex_dir)
        result = repair.repair_all()
        
        # Should validate after repair
        config_path = temp_cortex_dir / "cortex.config.json"
        config = json.loads(config_path.read_text())
        
        # Basic structure validation
        assert "machines" in config
        assert isinstance(config["machines"], dict)
    
    def test_repair_handles_readonly_filesystem(self, temp_cortex_dir):
        """Test repair handles read-only filesystem gracefully"""
        repair = ConfigRepair(root_path=temp_cortex_dir)
        
        # Make directory readonly
        os.chmod(temp_cortex_dir, 0o444)
        
        try:
            result = repair.create_missing_directories()
            
            # Should fail gracefully
            assert result.status in [RepairStatus.FAILED, RepairStatus.PARTIAL]
        finally:
            # Restore permissions for cleanup
            os.chmod(temp_cortex_dir, 0o755)
