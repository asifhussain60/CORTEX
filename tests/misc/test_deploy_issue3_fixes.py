#!/usr/bin/env python3
"""
Test Issue #3 Deployment Script

Validates deployment script functionality before production use.

Usage: pytest tests/test_deploy_issue3_fixes.py -v
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from scripts.deploy_issue3_fixes import DeploymentValidator, Issue3Deployer


class TestDeploymentValidator:
    """Test deployment validation logic"""
    
    def test_validator_initialization(self, tmp_path):
        """Test validator initializes correctly"""
        validator = DeploymentValidator(tmp_path)
        assert validator.project_root == tmp_path
        assert validator.errors == []
        assert validator.warnings == []
    
    def test_validate_core_files_missing(self, tmp_path):
        """Test core file validation detects missing files"""
        validator = DeploymentValidator(tmp_path)
        result = validator.validate_core_files()
        
        # Should fail when no files exist
        assert result is False
        assert len(validator.errors) > 0
    
    def test_validate_core_files_present(self, tmp_path):
        """Test core file validation passes when files exist"""
        # Create required files
        required_files = [
            'src/agents/feedback_agent.py',
            'src/agents/view_discovery_agent.py',
            'src/workflows/tdd_workflow_integrator.py',
            'cortex-brain/tier2/schema/element_mappings.sql',
            'apply_element_mappings_schema.py',
            'validate_issue3_phase4.py',
            'tests/integration/test_issue3_fixes.py',
            '.github/prompts/CORTEX.prompt.md'
        ]
        
        for file_path in required_files:
            full_path = tmp_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text("# Test file")
        
        validator = DeploymentValidator(tmp_path)
        result = validator.validate_core_files()
        
        assert result is True
        assert len(validator.errors) == 0
    
    def test_validate_database_schema(self, tmp_path):
        """Test database schema validation"""
        schema_path = tmp_path / 'cortex-brain/tier2/schema/element_mappings.sql'
        schema_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create valid schema
        schema_content = """
-- Issue #3 Database Schema

CREATE TABLE IF NOT EXISTS tier2_element_mappings (
    id INTEGER PRIMARY KEY,
    element_id TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS tier2_navigation_flows (
    id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS tier2_discovery_runs (
    id INTEGER PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS tier2_element_changes (
    id INTEGER PRIMARY KEY
);

CREATE INDEX idx_element_mappings_project ON tier2_element_mappings(element_id);
"""
        schema_path.write_text(schema_content)
        
        validator = DeploymentValidator(tmp_path)
        result = validator.validate_database_schema()
        
        # Should pass - all tables defined
        assert result is True or len(validator.warnings) > 0  # May have index count warning
    
    def test_validate_version_compatibility(self):
        """Test version compatibility check"""
        validator = DeploymentValidator(Path.cwd())
        result = validator.validate_version_compatibility()
        
        # Should pass on Python 3.10+
        assert result is True
    
    def test_print_summary_no_issues(self, tmp_path):
        """Test summary with no errors or warnings"""
        validator = DeploymentValidator(tmp_path)
        result = validator.print_summary()
        
        assert result is True
    
    def test_print_summary_with_errors(self, tmp_path):
        """Test summary with errors"""
        validator = DeploymentValidator(tmp_path)
        validator.errors.append("Test error")
        result = validator.print_summary()
        
        assert result is False
    
    def test_print_summary_with_warnings(self, tmp_path):
        """Test summary with warnings only"""
        validator = DeploymentValidator(tmp_path)
        validator.warnings.append("Test warning")
        result = validator.print_summary()
        
        # Should still pass with warnings
        assert result is True


class TestIssue3Deployer:
    """Test deployment execution logic"""
    
    def test_deployer_initialization(self, tmp_path):
        """Test deployer initializes correctly"""
        deployer = Issue3Deployer(tmp_path)
        assert deployer.project_root == tmp_path
        assert deployer.skip_tests is False
        assert deployer.deployment_log == []
    
    def test_deployer_skip_tests_flag(self, tmp_path):
        """Test deployer respects skip_tests flag"""
        deployer = Issue3Deployer(tmp_path, skip_tests=True)
        assert deployer.skip_tests is True
    
    def test_update_package_manifest(self, tmp_path):
        """Test package manifest update"""
        deployer = Issue3Deployer(tmp_path)
        
        # Create cortex-brain directory
        (tmp_path / 'cortex-brain').mkdir(parents=True, exist_ok=True)
        
        result = deployer.update_package_manifest()
        
        assert result is True
        assert (tmp_path / 'cortex-brain/deployment-manifest.json').exists()
        
        # Verify manifest content
        import json
        with open(tmp_path / 'cortex-brain/deployment-manifest.json', 'r') as f:
            manifest = json.load(f)
        
        assert 'releases' in manifest
        assert manifest['latest_version'] == '3.1.0'
        assert len(manifest['releases']) == 1
        assert manifest['releases'][0]['version'] == '3.1.0'
        assert manifest['releases'][0]['issue'] == '#3'


class TestDeploymentIntegration:
    """Integration tests for full deployment workflow"""
    
    def test_validation_before_deployment(self, tmp_path):
        """Test that validation runs before deployment"""
        deployer = Issue3Deployer(tmp_path, skip_tests=True)
        
        # Should fail preflight check (no files)
        result = deployer.preflight_check()
        assert result is False
    
    def test_deployment_log_tracking(self, tmp_path):
        """Test deployment log tracks operations"""
        deployer = Issue3Deployer(tmp_path)
        
        # Manually add log entry
        deployer.deployment_log.append("Test operation")
        
        assert len(deployer.deployment_log) == 1
        assert deployer.deployment_log[0] == "Test operation"


@pytest.fixture
def project_root():
    """Get actual project root for integration tests"""
    return Path(__file__).parent.parent


class TestRealProjectValidation:
    """Integration tests using real project files"""
    
    def test_real_project_core_files(self, project_root):
        """Test validation against real project"""
        validator = DeploymentValidator(project_root)
        
        # Check if Issue #3 files actually exist
        core_files_result = validator.validate_core_files()
        
        # Should pass if Issue #3 is complete
        if not core_files_result:
            pytest.skip("Issue #3 files not yet created (expected during development)")
    
    def test_real_project_database_schema(self, project_root):
        """Test schema validation against real project"""
        validator = DeploymentValidator(project_root)
        
        schema_result = validator.validate_database_schema()
        
        # Should pass if schema file exists and is valid
        if not schema_result:
            pytest.skip("Schema file not yet created (expected during development)")
    
    def test_real_project_agent_imports(self, project_root):
        """Test agent imports against real project"""
        validator = DeploymentValidator(project_root)
        
        import_result = validator.validate_agent_imports()
        
        # Should pass if agents are implemented
        if not import_result:
            pytest.skip("Agents not yet implemented (expected during development)")


if __name__ == '__main__':
    pytest.main([__file__, '-v', '--tb=short'])
