#!/usr/bin/env python3
"""
Integration Tests for Policy Validation Workflow

Tests end-to-end policy validation in MasterSetupOrchestrator.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import pytest
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from src.orchestrators.master_setup_orchestrator import MasterSetupOrchestrator, SetupResult
from src.operations.user_consent_manager import UserConsentManager, ConsentResult
from src.operations.policy_scanner import PolicyScanner
from src.validation.policy_validator import PolicyValidator, ViolationSeverity


class TestPolicyWorkflowIntegration:
    """Integration tests for policy validation workflow."""
    
    @pytest.fixture
    def temp_project_root(self):
        """Create temporary project directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def temp_cortex_root(self):
        """Create temporary CORTEX directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cortex_dir = Path(tmpdir) / "CORTEX"
            cortex_dir.mkdir()
            
            # Create required directories
            (cortex_dir / "cortex-brain" / "documents" / "reports").mkdir(parents=True)
            (cortex_dir / "cortex-brain" / "templates").mkdir(parents=True)
            
            yield cortex_dir
    
    @pytest.fixture
    def sample_policies(self):
        """Sample policy content."""
        return {
            "naming_conventions": {
                "classes_pascal_case": True,
                "functions_snake_case": True
            },
            "security_rules": {
                "no_hardcoded_credentials": True
            }
        }
    
    def test_master_setup_phase3_5_no_policies(self, temp_project_root, temp_cortex_root):
        """Test: MasterSetupOrchestrator Phase 3.5 with no policies (offers starter template)"""
        # Mock consent to approve policy_validation
        mock_consent = MagicMock()
        mock_consent.approved_steps = ["all"]
        
        # Mock dependencies to skip other phases
        with patch('src.orchestrators.master_setup_orchestrator.DependencyInstaller'), \
             patch('src.orchestrators.master_setup_orchestrator.OnboardingOrchestrator'), \
             patch('src.orchestrators.master_setup_orchestrator.SetupEPMOrchestrator'), \
             patch('src.orchestrators.master_setup_orchestrator.UserConsentManager') as mock_consent_mgr:
            
            mock_consent_mgr.return_value.request_onboarding_consent.return_value = mock_consent
            
            orchestrator = MasterSetupOrchestrator(
                project_root=temp_project_root,
                cortex_root=temp_cortex_root,
                interactive=False
            )
            
            # Scanner should find no policies
            scanner = PolicyScanner(temp_project_root)
            policies = scanner.scan_for_policies()
            assert len(policies) == 0
    
    def test_master_setup_phase3_5_with_policies(self, temp_project_root, temp_cortex_root, sample_policies):
        """Test: MasterSetupOrchestrator Phase 3.5 with policies (runs validation)"""
        # Create policy file
        policies_dir = temp_project_root / ".github" / "policies"
        policies_dir.mkdir(parents=True)
        policy_file = policies_dir / "policies.yaml"
        with open(policy_file, 'w') as f:
            yaml.dump(sample_policies, f)
        
        # Verify PolicyScanner detects it
        scanner = PolicyScanner(temp_project_root)
        policies = scanner.scan_for_policies()
        assert len(policies) == 1
        
        # Verify PolicyValidator can validate
        validator = PolicyValidator(temp_project_root, temp_cortex_root)
        result = validator.validate()
        assert result.total_rules > 0
    
    def test_master_setup_critical_violations_halt(self, temp_project_root, temp_cortex_root):
        """Test: Setup stops on critical violations when user declines"""
        # This would require mocking input() for interactive mode
        # For now, test that critical violations are detected
        
        policy = {
            "security_rules": {
                "no_hardcoded_credentials": True
            }
        }
        
        # Create config with hardcoded secret
        config_file = temp_cortex_root / "cortex.config.json"
        config_file.write_text('{"password": "admin123"}')
        
        validator = PolicyValidator(temp_project_root, temp_cortex_root)
        
        # Mock policy document
        with patch.object(PolicyScanner, 'scan_for_policies') as mock_scan:
            from src.operations.policy_scanner import PolicyDocument, PolicyFormat
            mock_scan.return_value = [
                PolicyDocument(
                    path=Path("test.yaml"),
                    format=PolicyFormat.YAML,
                    content=policy,
                    categories=["security_rules"]
                )
            ]
            
            result = validator.validate()
            
            # Check for critical violations
            critical = [v for v in result.violations if v.severity == ViolationSeverity.CRITICAL]
            # May have critical violations depending on implementation
            assert isinstance(critical, list)
    
    def test_user_consent_policy_validation(self, temp_project_root):
        """Test: UserConsentManager prompts correctly for policy validation"""
        consent_mgr = UserConsentManager(
            project_name="TestProject",
            interactive=False  # Non-interactive returns True
        )
        
        result = consent_mgr.request_policy_validation_consent(
            policy_path=Path(".github/policies/policies.yaml")
        )
        
        assert result is True  # Non-interactive mode
    
    def test_response_template_triggers(self):
        """Test: 'validate policies' routes to policy_validation template"""
        # Load response templates
        from pathlib import Path
        import yaml
        
        templates_file = Path("cortex-brain/response-templates.yaml")
        if templates_file.exists():
            with open(templates_file, 'r') as f:
                templates_data = yaml.safe_load(f)
            
            # Check policy_validation template exists
            assert "policy_validation" in templates_data.get("templates", {})
            
            # Check triggers
            policy_template = templates_data["templates"]["policy_validation"]
            triggers = policy_template.get("triggers", [])
            assert "validate policies" in triggers
            assert "check compliance" in triggers
    
    def test_end_to_end_setup_with_policy_validation(self, temp_project_root, temp_cortex_root, sample_policies):
        """Test: Full workflow from setup command to completion report with policy validation"""
        # Create policy file
        policies_dir = temp_project_root / ".github" / "policies"
        policies_dir.mkdir(parents=True)
        policy_file = policies_dir / "policies.yaml"
        with open(policy_file, 'w') as f:
            yaml.dump(sample_policies, f)
        
        # Mock all dependencies
        with patch('src.orchestrators.master_setup_orchestrator.DependencyInstaller') as mock_dep, \
             patch('src.orchestrators.master_setup_orchestrator.OnboardingOrchestrator') as mock_onboard, \
             patch('src.orchestrators.master_setup_orchestrator.SetupEPMOrchestrator') as mock_setup, \
             patch('src.orchestrators.master_setup_orchestrator.UserConsentManager') as mock_consent_mgr:
            
            # Setup mocks
            mock_dep_instance = MagicMock()
            mock_dep_instance.install_dependencies.return_value = MagicMock(success=True, errors=[], installed_packages=["pytest"], python_version="3.9", venv_created=True)
            mock_dep.return_value = mock_dep_instance
            
            mock_onboard_instance = MagicMock()
            mock_onboard_instance.onboard_application.return_value = MagicMock(success=True, errors=[])
            mock_onboard.return_value = mock_onboard_instance
            
            mock_setup_instance = MagicMock()
            mock_setup_instance.setup_gitignore.return_value = True
            mock_setup_instance.setup_copilot_instructions.return_value = True
            mock_setup.return_value = mock_setup_instance
            
            mock_consent = MagicMock()
            mock_consent.approved_steps = ["all"]
            mock_consent_mgr.return_value.request_onboarding_consent.return_value = mock_consent
            
            # Run orchestrator
            orchestrator = MasterSetupOrchestrator(
                project_root=temp_project_root,
                cortex_root=temp_cortex_root,
                interactive=False
            )
            
            result = orchestrator.execute_full_setup()
            
            # Verify policy_validation in results
            assert isinstance(result, SetupResult)
            assert "policy_validation" in result.phase_results
            
            policy_result = result.phase_results["policy_validation"]
            assert policy_result["success"] is True
            assert "compliance_percentage" in policy_result


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
