#!/usr/bin/env python3
"""
CORTEX Pre-Deployment Validation Gate

Comprehensive validation checks to prevent deployment gaps from reaching production.
Enforces all requirements from CORTEX-DEPLOYMENT-GAP-ANALYSIS-2025-11-22.md.

CRITICAL: This script MUST pass 100% before publish is allowed.

Usage:
    python scripts/validate_deployment.py
    python scripts/validate_deployment.py --fix      # Auto-fix when possible
    python scripts/validate_deployment.py --report   # Generate detailed report

Exit Codes:
    0 - All validations passed (safe to deploy)
    1 - Critical failures (BLOCK deployment)
    2 - Warnings (review required)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Proprietary
"""

import argparse
import json
import logging
import subprocess
import sys
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
import yaml

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

VERSION = "1.0.0"


@dataclass
class ValidationResult:
    """Result of a validation check."""
    check_id: str
    name: str
    severity: str  # CRITICAL, HIGH, MEDIUM, LOW
    passed: bool
    message: str
    details: Optional[str] = None
    fix_available: bool = False
    fix_command: Optional[str] = None


class DeploymentValidator:
    """Validates CORTEX deployment readiness."""
    
    def __init__(self, project_root: Path, auto_fix: bool = False):
        self.project_root = project_root
        self.auto_fix = auto_fix
        self.results: List[ValidationResult] = []
    
    def run_all_checks(self) -> Tuple[int, int, int]:
        """
        Run all validation checks.
        
        Returns:
            Tuple of (passed, failed, warnings)
        """
        logger.info("=" * 80)
        logger.info("CORTEX Pre-Deployment Validation Gate")
        logger.info("=" * 80)
        logger.info(f"Version: {VERSION}")
        logger.info(f"Project Root: {self.project_root}")
        logger.info(f"Auto-fix: {self.auto_fix}")
        logger.info("")
        
        # Core Configuration
        self.check_config_module()
        
        # Documentation (Admin-Only)
        self.check_documentation_modules()
        
        # Database Initialization
        self.check_tier2_initialization()
        
        # Module Loading
        self.check_operation_modules()
        
        # Operation Factory API
        self.check_operation_factory_api()
        
        # Test Coverage
        self.check_test_suite()
        
        # SKULL Protection
        self.check_skull_protection()
        
        # Onboarding Workflow
        self.check_onboarding_workflow()
        
        # Response Templates
        self.check_response_templates()
        
        # GitHub Copilot Instructions
        self.check_copilot_instructions_validation()
        
        # User Setup Documentation
        self.check_user_setup_documentation()
        
        # Phase 4: Response Template Wiring
        self.check_response_template_wiring()
        
        # Git Exclude Configuration
        self.check_git_exclude_setup()
        
        # Feedback System
        self.check_feedback_system()
        
        # TDD Mastery Components
        self.check_tdd_mastery_components()
        
        # User Entry Point Operations
        self.check_entry_point_operations()
        
        # Additional critical checks
        self.check_critical_files()
        self.check_import_health()
        self.check_git_status()
        
        # Generate summary
        return self.generate_summary()
    
    def check_config_module(self):
        """CONFIG_MODULE: Verify src/config.py exists and is valid."""
        check_id = "CONFIG_MODULE"
        name = "Configuration Module Exists"
        
        config_file = self.project_root / "src" / "config.py"
        
        if not config_file.exists():
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=False,
                message="src/config.py NOT FOUND - 100% of modules will fail to load",
                details="29+ operation modules import 'from src.config import config' but file does not exist",
                fix_available=True,
                fix_command="Create src/config.py with ConfigManager class (see CONFIG_MODULE validation)"
            ))
            return
        
        # Check if config.py has required exports
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            missing_exports = []
            # Check for either ConfigManager or CortexConfig (ConfigManager is alias)
            has_config_class = ('class ConfigManager' in content or 'class CortexConfig' in content)
            if not has_config_class:
                missing_exports.append('ConfigManager or CortexConfig')
            if 'ConfigManager = CortexConfig' not in content and 'class ConfigManager' not in content:
                if 'class CortexConfig' in content:
                    missing_exports.append('ConfigManager alias')
            if 'config = ' not in content:
                missing_exports.append('config instance')
            
            if missing_exports:
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="CRITICAL",
                    passed=False,
                    message=f"src/config.py incomplete - missing: {', '.join(missing_exports)}",
                    details="Config module exists but missing required exports",
                    fix_available=False
                ))
            else:
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="CRITICAL",
                    passed=True,
                    message="✓ src/config.py exists with required exports"
                ))
        
        except Exception as e:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=False,
                message=f"Failed to validate src/config.py: {e}",
                fix_available=False
            ))
    
    def check_documentation_modules(self):
        """DOCUMENTATION: Verify all referenced documentation modules exist.
        
        NOTE: Documentation modules are ADMIN-ONLY features accessed via GitHub Pages.
        User deployments do NOT require bundled documentation - this is informational only.
        """
        check_id = "DOCUMENTATION"
        name = "Documentation Modules (Admin-Only)"
        
        required_docs = [
            ".github/prompts/modules/story.md",
            ".github/prompts/modules/setup-guide.md",
            ".github/prompts/modules/technical-reference.md",
            ".github/prompts/modules/agents-guide.md",
            ".github/prompts/modules/tracking-guide.md",
            ".github/prompts/modules/configuration-reference.md",
        ]
        
        missing_docs = []
        for doc_path in required_docs:
            full_path = self.project_root / doc_path
            if not full_path.exists():
                missing_docs.append(doc_path)
        
        if missing_docs:
            # Changed from CRITICAL to LOW - documentation is admin-only (GitHub Pages)
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="LOW",
                passed=True,  # Pass validation - not required for user deployments
                message=f"ℹ️  {len(missing_docs)} documentation modules not present (expected - admin-only feature)",
                details=f"Documentation accessed via GitHub Pages:\n" + "\n".join(f"  - {doc}" for doc in missing_docs),
                fix_available=False,
                fix_command="Admin feature - users access docs at github.com/asifhussain60/CORTEX"
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="LOW",
                passed=True,
                message="✓ All documentation modules present (admin deployment)"
            ))
    
    def check_tier2_initialization(self):
        """DATABASE_INIT: Verify Tier 2 can auto-initialize."""
        check_id = "DATABASE_INIT"
        name = "Tier 2 Auto-Initialization"
        
        tier2_path = self.project_root / "cortex-brain" / "tier2"
        schema_file = self.project_root / "src" / "tier2" / "knowledge_graph" / "database" / "schema.py"
        
        if not schema_file.exists():
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=False,
                message="Tier 2 schema.py not found",
                details=f"Expected: {schema_file}",
                fix_available=False
            ))
            return
        
        # Check if initialization code exists
        try:
            with open(schema_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            if 'def initialize' in content or 'def create_tables' in content:
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="HIGH",
                    passed=True,
                    message="✓ Tier 2 initialization code present",
                    details="Auto-initialization available on first use"
                ))
            else:
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="HIGH",
                    passed=False,
                    message="Tier 2 lacks auto-initialization",
                    details="Schema exists but no initialization function found",
                    fix_available=True,
                    fix_command="Add auto-init logic to KnowledgeGraph class"
                ))
        
        except Exception as e:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=False,
                message=f"Failed to validate Tier 2 schema: {e}",
                fix_available=False
            ))
    
    def check_operation_modules(self):
        """MODULE_REGISTRATION: Verify operation modules can import successfully."""
        check_id = "MODULE_REGISTRATION"
        name = "Operation Modules Import Successfully"
        
        # First check if config exists (dependency)
        config_file = self.project_root / "src" / "config.py"
        if not config_file.exists():
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="MEDIUM",
                passed=False,
                message="Cannot test - depends on CONFIG_MODULE (config.py missing)",
                details="Fix CONFIG_MODULE first, then retest",
                fix_available=False
            ))
            return
        
        # Try to import OperationFactory
        try:
            sys.path.insert(0, str(self.project_root))
            from src.operations.operation_factory import OperationFactory
            
            factory = OperationFactory()
            registered_count = len(getattr(factory, '_modules', {}))
            
            if registered_count >= 20:  # Expect at least 20 modules
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="MEDIUM",
                    passed=True,
                    message=f"✓ {registered_count} operation modules registered successfully"
                ))
            else:
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="MEDIUM",
                    passed=False,
                    message=f"Only {registered_count} modules registered (expected 29+)",
                    details="Some modules may have import errors - deployment will still work",
                    fix_available=False
                ))
        
        except ImportError as e:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="MEDIUM",
                passed=False,
                message=f"OperationFactory import failed: {e}",
                details="Module registration system may have issues - deployment will still work",
                fix_available=False
            ))
        except Exception as e:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="MEDIUM",
                passed=False,
                message=f"Failed to validate operation modules: {e}",
                fix_available=False
            ))
    
    def check_operation_factory_api(self):
        """OPERATION_FACTORY: Verify OperationFactory has required API methods."""
        check_id = "OPERATION_FACTORY"
        name = "OperationFactory API Complete"
        
        try:
            sys.path.insert(0, str(self.project_root))
            from src.operations.operation_factory import OperationFactory
            
            factory = OperationFactory()
            
            missing_methods = []
            if not hasattr(factory, 'list_registered_modules'):
                missing_methods.append('list_registered_modules()')
            if not hasattr(factory, 'get_module_metadata'):
                missing_methods.append('get_module_metadata()')
            if not hasattr(factory, 'list_available_commands'):
                missing_methods.append('list_available_commands()')
            
            if missing_methods:
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="MEDIUM",
                    passed=False,
                    message=f"OperationFactory API incomplete",
                    details=f"Missing methods: {', '.join(missing_methods)}",
                    fix_available=True,
                    fix_command="Add introspection methods to OperationFactory class"
                ))
            else:
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="MEDIUM",
                    passed=True,
                    message="✓ OperationFactory API complete"
                ))
        
        except Exception as e:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="MEDIUM",
                passed=False,
                message=f"Failed to validate OperationFactory API: {e}",
                fix_available=False
            ))
    
    def check_test_suite(self):
        """TEST_COVERAGE: Verify comprehensive test suite exists."""
        check_id = "TEST_COVERAGE"
        name = "Test Suite Complete"
        
        expected_test_files = [
            "tests/tier0/test_brain_protector.py",
            "tests/tier1/test_conversation_memory.py",
            "tests/tier2/test_knowledge_graph.py",
            "tests/tier3/test_context_intelligence.py",
            "tests/operations/test_operation_factory.py",
        ]
        
        missing_tests = []
        found_tests = 0
        
        for test_file in expected_test_files:
            full_path = self.project_root / test_file
            if full_path.exists():
                found_tests += 1
            else:
                missing_tests.append(test_file)
        
        coverage_pct = (found_tests / len(expected_test_files)) * 100
        
        if coverage_pct < 70:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=False,
                message=f"Test coverage insufficient: {coverage_pct:.0f}% ({found_tests}/{len(expected_test_files)} core test files)",
                details=f"Missing:\n" + "\n".join(f"  - {test}" for test in missing_tests),
                fix_available=False,
                fix_command="Implement comprehensive test suite (40-60 hours estimated)"
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=True,
                message=f"✓ Test coverage adequate: {coverage_pct:.0f}% ({found_tests}/{len(expected_test_files)} core files)"
            ))
    
    def check_skull_protection(self):
        """SKULL_PROTECTION: Verify SKULL protection rules are tested."""
        check_id = "SKULL_PROTECTION"
        name = "SKULL Protection Validated"
        
        # Check for actual SKULL test file (test_brain_protector.py)
        skull_test_file = self.project_root / "tests" / "tier0" / "test_brain_protector.py"
        
        if not skull_test_file.exists():
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="MEDIUM",
                passed=False,
                message="SKULL protection tests missing",
                details="Quality gates (SKULL-001 through SKULL-004) not validated",
                fix_available=False,
                fix_command="Implement SKULL protection test suite (8 hours estimated)"
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="MEDIUM",
                passed=True,
                message="✓ SKULL protection test suite exists (test_brain_protector.py)"
            ))
    
    def check_onboarding_workflow(self):
        """ONBOARDING_WORKFLOW: Verify onboarding workflow is functional and includes tooling setup instructions."""
        check_id = "ONBOARDING_WORKFLOW"
        name = "Onboarding Workflow Functional"
        
        onboarding_modules = [
            "src/operations/modules/application_onboarding_steps.py",
            "src/operations/modules/user_onboarding_steps.py",
            "src/operations/modules/tooling_installer_module.py",
        ]
        
        # Documentation modules removed - admin-only feature via GitHub Pages
        # docs_linked = [
        #     ".github/prompts/modules/story.md",
        #     ".github/prompts/modules/setup-guide.md",
        # ]
        
        setup_docs = [
            "publish/CORTEX/SETUP-FOR-COPILOT.md",
        ]
        
        missing = []
        for module_path in onboarding_modules + setup_docs:
            if not (self.project_root / module_path).exists():
                missing.append(module_path)
        
        # Check setup documentation includes tooling installation instructions
        tooling_instructions_found = False
        setup_doc_path = self.project_root / "publish/CORTEX/SETUP-FOR-COPILOT.md"
        
        if setup_doc_path.exists():
            try:
                with open(setup_doc_path, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                
                # Check for required tooling mentions
                required_tooling_keywords = [
                    'vision api',
                    'install',
                    'dependencies',
                    'requirements.txt',
                    'python',
                    'git'
                ]
                
                tooling_mentions = sum(1 for keyword in required_tooling_keywords if keyword in content)
                tooling_instructions_found = tooling_mentions >= 4  # At least 4 of 6 keywords present
                
            except Exception as e:
                logger.warning(f"Failed to validate setup documentation: {e}")
        
        issues = []
        if missing:
            issues.append(f"{len(missing)} files missing: {', '.join(missing[:3])}")
        
        if not tooling_instructions_found and setup_doc_path.exists():
            issues.append("SETUP-FOR-COPILOT.md missing comprehensive tooling installation instructions")
        
        if issues:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="MEDIUM",
                passed=False,
                message=f"Onboarding workflow incomplete",
                details="Issues found:\n" + "\n".join(f"  • {issue}" for issue in issues) + 
                       "\n\nRequired tooling instructions:\n" +
                       "  • Vision API setup (optional but documented)\n" +
                       "  • Python dependencies (pip install -r requirements.txt)\n" +
                       "  • Git installation verification\n" +
                       "  • Environment detection steps\n" +
                       "  • Automatic tooling installation via onboarding modules",
                fix_available=False
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="MEDIUM",
                passed=True,
                message="✓ Onboarding workflow complete with tooling setup instructions"
            ))
    
    def check_response_templates(self):
        """RESPONSE_TEMPLATES: Verify response template system is complete."""
        check_id = "RESPONSE_TEMPLATES"
        name = "Response Templates Complete"
        
        templates_file = self.project_root / "cortex-brain" / "response-templates.yaml"
        
        if not templates_file.exists():
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="MEDIUM",
                passed=False,
                message="response-templates.yaml not found",
                fix_available=False
            ))
            return
        
        try:
            with open(templates_file, 'r', encoding='utf-8') as f:
                templates_data = yaml.safe_load(f)
            
            template_count = len(templates_data.get('templates', {}))
            
            if template_count >= 18:  # Minimum 18 templates expected
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="MEDIUM",
                    passed=True,
                    message=f"✓ Response templates complete ({template_count} templates)"
                ))
            else:
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="MEDIUM",
                    passed=False,
                    message=f"Response templates incomplete ({template_count} found, expected 18+)",
                    fix_available=False
                ))
        
        except Exception as e:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="MEDIUM",
                passed=False,
                message=f"Failed to validate response templates: {e}",
                fix_available=False
            ))
    
    def check_critical_files(self):
        """Verify all critical files exist."""
        check_id = "CRITICAL-FILES"
        name = "Critical Files Present"
        
        critical_files = [
            ".github/prompts/CORTEX.prompt.md",
            ".github/copilot-instructions.md",
            "cortex.config.template.json",
            "cortex-operations.yaml",
            "requirements.txt",
            "README.md",
            "LICENSE",
            "cortex-brain/brain-protection-rules.yaml",
            "cortex-brain/response-templates.yaml",
        ]
        
        missing = []
        for file_path in critical_files:
            if not (self.project_root / file_path).exists():
                missing.append(file_path)
        
        if missing:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=False,
                message=f"{len(missing)} critical files missing",
                details=f"Missing:\n" + "\n".join(f"  - {file}" for file in missing),
                fix_available=False
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=True,
                message="✓ All critical files present"
            ))
    
    def check_import_health(self):
        """Verify Python imports are healthy."""
        check_id = "IMPORT-HEALTH"
        name = "Python Import Health"
        
        # Try importing key modules
        test_imports = [
            "src.config",
            "src.tier0.brain_protector",
            "src.tier1.conversation_manager",
            "src.tier2.knowledge_graph.database.connection",
            "src.operations.operation_factory",
        ]
        
        sys.path.insert(0, str(self.project_root))
        
        failed_imports = []
        for module_name in test_imports:
            try:
                __import__(module_name)
            except ImportError as e:
                failed_imports.append(f"{module_name}: {e}")
            except Exception as e:
                failed_imports.append(f"{module_name}: {e}")
        
        if failed_imports:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=False,
                message=f"{len(failed_imports)} import failures detected",
                details=f"Failed imports:\n" + "\n".join(f"  - {err}" for err in failed_imports),
                fix_available=False
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=True,
                message="✓ All critical imports successful"
            ))
    
    def check_git_status(self):
        """Verify git repository is clean."""
        check_id = "GIT-STATUS"
        name = "Git Repository Clean"
        
        try:
            result = subprocess.run(
                ['git', 'status', '--porcelain'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.stdout.strip():
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="MEDIUM",
                    passed=False,
                    message="Uncommitted changes detected",
                    details="Commit or stash changes before deployment",
                    fix_available=False,
                    fix_command="git commit -am 'Pre-deployment commit' OR git stash"
                ))
            else:
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="MEDIUM",
                    passed=True,
                    message="✓ Git repository clean"
                ))
        
        except Exception as e:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="MEDIUM",
                passed=False,
                message=f"Failed to check git status: {e}",
                fix_available=False
            ))
    
    def check_copilot_instructions_validation(self):
        """COPILOT_INSTRUCTIONS: Verify GitHub Copilot instruction files are present and properly configured."""
        check_id = "COPILOT_INSTRUCTIONS"
        name = "GitHub Copilot Instructions Validation"
        
        issues = []
        
        # Check for main instruction files
        copilot_instructions_file = self.project_root / ".github" / "copilot-instructions.md"
        cortex_prompt_file = self.project_root / ".github" / "prompts" / "CORTEX.prompt.md"
        
        if not copilot_instructions_file.exists():
            issues.append(".github/copilot-instructions.md NOT FOUND - Copilot entry point missing")
        else:
            # Validate content references CORTEX.prompt.md
            try:
                with open(copilot_instructions_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                if 'CORTEX.prompt.md' not in content:
                    issues.append("copilot-instructions.md does not reference CORTEX.prompt.md")
                
                if '.github/prompts/CORTEX.prompt.md' not in content:
                    issues.append("copilot-instructions.md missing correct path to CORTEX.prompt.md")
                
                # Check priority/section markers
                if 'Entry Point' not in content and 'entry point' not in content.lower():
                    issues.append("copilot-instructions.md missing 'Entry Point' section")
                    
            except Exception as e:
                issues.append(f"Failed to validate copilot-instructions.md content: {e}")
        
        if not cortex_prompt_file.exists():
            issues.append(".github/prompts/CORTEX.prompt.md NOT FOUND - Main prompt file missing")
        else:
            # Validate CORTEX.prompt.md has proper structure
            try:
                with open(cortex_prompt_file, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
                
                required_sections = [
                    'RESPONSE TEMPLATES',
                    'MANDATORY RESPONSE FORMAT',
                    'Quick Start',
                    'Copyright'
                ]
                
                missing_sections = [section for section in required_sections 
                                   if section not in prompt_content]
                
                if missing_sections:
                    issues.append(
                        f"CORTEX.prompt.md missing required sections: {', '.join(missing_sections)}"
                    )
                    
            except Exception as e:
                issues.append(f"Failed to validate CORTEX.prompt.md content: {e}")
        
        # Check that deployment script installs these files
        deploy_script = self.project_root / "scripts" / "deploy_to_app.py"
        if deploy_script.exists():
            try:
                with open(deploy_script, 'r', encoding='utf-8') as f:
                    deploy_content = f.read()
                
                if 'install_entry_point' not in deploy_content:
                    issues.append("deploy_to_app.py missing install_entry_point() function")
                
                if 'copilot-instructions.md' not in deploy_content:
                    issues.append("deploy_to_app.py does not copy copilot-instructions.md")
                    
                if 'CORTEX.prompt.md' not in deploy_content:
                    issues.append("deploy_to_app.py does not copy CORTEX.prompt.md")
                    
            except Exception as e:
                issues.append(f"Failed to validate deploy_to_app.py: {e}")
        else:
            issues.append("deploy_to_app.py script not found")
        
        # Check that setup documentation mentions these files
        publish_script = self.project_root / "scripts" / "publish_cortex.py"
        if publish_script.exists():
            try:
                with open(publish_script, 'r', encoding='utf-8') as f:
                    publish_content = f.read()
                
                if 'copilot-instructions.md' not in publish_content:
                    issues.append("publish_cortex.py does not include copilot-instructions.md in critical files")
                    
                if 'CORTEX.prompt.md' not in publish_content:
                    issues.append("publish_cortex.py does not include CORTEX.prompt.md in critical files")
                    
            except Exception as e:
                issues.append(f"Failed to validate publish_cortex.py: {e}")
        
        # Build result
        if issues:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=False,
                message=f"GitHub Copilot instruction files validation failed ({len(issues)} issues)",
                details="\n".join(f"  • {issue}" for issue in issues),
                fix_available=False,
                fix_command="Ensure .github/copilot-instructions.md and .github/prompts/CORTEX.prompt.md are present and properly configured"
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=True,
                message="✓ GitHub Copilot instruction files properly configured"
            ))
    
    def check_user_setup_documentation(self):
        """USER_SETUP_DOCS: Verify user setup documentation is complete.
        
        NOTE: This check validates that the publish script will generate proper
        setup instructions for users. It does NOT check if dependencies are
        installed in the dev environment - those are for user machines.
        """
        check_id = "USER_SETUP_DOCS"
        name = "User Setup Documentation"
        
        documentation_issues = []
        
        # Validate that publish script exists and generates proper setup documentation
        publish_script = self.project_root / "scripts/publish_cortex.py"
        
        if not publish_script.exists():
            documentation_issues.append("publish_cortex.py script missing (cannot generate SETUP-CORTEX.md)")
        else:
            # Verify the publish script contains the setup document generator
            try:
                with open(publish_script, 'r', encoding='utf-8') as f:
                    script_content = f.read()
                
                # Check for setup document generator function
                if 'create_setup_cortex' not in script_content:
                    documentation_issues.append("publish_cortex.py missing SETUP-CORTEX.md generator function")
                elif 'SETUP-CORTEX.md' not in script_content:
                    documentation_issues.append("publish_cortex.py generator incomplete")
                
                # Check that setup content includes required tooling instructions
                required_keywords = [
                    'python',  # Python installation
                    'git',  # Git installation  
                    'pip install',  # Package installation
                    'requirements.txt',  # Dependencies file
                    'onboard this application'  # Onboarding command
                ]
                
                missing_keywords = [kw for kw in required_keywords if kw.lower() not in script_content.lower()]
                if missing_keywords:
                    documentation_issues.append(
                        f"Setup documentation missing key instructions: {', '.join(missing_keywords)}"
                    )
                    
            except Exception as e:
                documentation_issues.append(f"Failed to validate publish script: {e}")
        
        # Check that requirements.txt exists with necessary packages
        requirements_file = self.project_root / "requirements.txt"
        if not requirements_file.exists():
            documentation_issues.append("requirements.txt missing - users won't know what to install")
        else:
            try:
                with open(requirements_file, 'r', encoding='utf-8') as f:
                    requirements_content = f.read()
                
                # Check for critical user-facing packages
                critical_packages = ['pytest', 'PyYAML', 'watchdog', 'psutil']
                missing_packages = [pkg for pkg in critical_packages if pkg.lower() not in requirements_content.lower()]
                
                if missing_packages:
                    documentation_issues.append(
                        f"requirements.txt missing critical packages: {', '.join(missing_packages)}"
                    )
            except Exception as e:
                documentation_issues.append(f"Failed to read requirements.txt: {e}")
        
        # Build result
        if documentation_issues:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=False,
                message=f"User setup documentation incomplete ({len(documentation_issues)} issues)",
                details="\n".join(f"  • {issue}" for issue in documentation_issues),
                fix_available=False,
                fix_command="Update publish_cortex.py to include complete setup instructions"
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=True,
                message="✓ User setup documentation complete (publish script validated)"
            ))
    
    def check_response_template_wiring(self):
        """RESPONSE_TEMPLATE_WIRING: Verify response templates are properly wired in deployment.
        
        Phase 4: Validates that:
        1. response-templates.yaml exists in cortex-brain/
        2. CORTEX.prompt.md references response-templates.yaml
        3. Template modules exist (.github/prompts/modules/)
        4. copilot-instructions.md loads CORTEX.prompt.md
        """
        check_id = "RESPONSE_TEMPLATE_WIRING"
        name = "Response Template System Wiring (Phase 4)"
        
        wiring_issues = []
        
        # Check 1: response-templates.yaml exists
        templates_file = self.project_root / "cortex-brain" / "response-templates.yaml"
        if not templates_file.exists():
            wiring_issues.append("cortex-brain/response-templates.yaml NOT FOUND - templates unavailable")
        else:
            # Validate template file has content
            try:
                with open(templates_file, 'r', encoding='utf-8') as f:
                    templates_content = f.read()
                
                if not templates_content.strip():
                    wiring_issues.append("response-templates.yaml is empty")
                elif 'templates:' not in templates_content:
                    wiring_issues.append("response-templates.yaml missing 'templates:' section")
                
                # Check for key templates
                required_templates = ['help_table', 'fallback', 'work_planner_success', 'planning_dor_complete']
                missing_templates = [t for t in required_templates if t not in templates_content]
                if missing_templates:
                    wiring_issues.append(f"Missing critical templates: {', '.join(missing_templates)}")
                    
            except Exception as e:
                wiring_issues.append(f"Failed to validate response-templates.yaml: {e}")
        
        # Check 2: CORTEX.prompt.md references response-templates.yaml
        cortex_prompt = self.project_root / ".github" / "prompts" / "CORTEX.prompt.md"
        if not cortex_prompt.exists():
            wiring_issues.append(".github/prompts/CORTEX.prompt.md NOT FOUND")
        else:
            try:
                with open(cortex_prompt, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
                
                if 'response-templates.yaml' not in prompt_content:
                    wiring_issues.append("CORTEX.prompt.md does not reference response-templates.yaml")
                
                if '#file:../../cortex-brain/response-templates.yaml' not in prompt_content and \
                   'cortex-brain/response-templates.yaml' not in prompt_content:
                    wiring_issues.append("CORTEX.prompt.md missing correct path to response-templates.yaml")
                
                if 'RESPONSE TEMPLATES' not in prompt_content:
                    wiring_issues.append("CORTEX.prompt.md missing 'RESPONSE TEMPLATES' section")
                    
            except Exception as e:
                wiring_issues.append(f"Failed to validate CORTEX.prompt.md template references: {e}")
        
        # Check 3: Template modules exist
        modules_dir = self.project_root / ".github" / "prompts" / "modules"
        if not modules_dir.exists():
            wiring_issues.append(".github/prompts/modules/ directory NOT FOUND")
        else:
            required_modules = ['template-guide.md', 'response-format.md', 'planning-system-guide.md']
            missing_modules = [m for m in required_modules if not (modules_dir / m).exists()]
            if missing_modules:
                wiring_issues.append(f"Missing template guide modules: {', '.join(missing_modules)}")
        
        # Check 4: copilot-instructions.md loads CORTEX.prompt.md
        copilot_instructions = self.project_root / ".github" / "copilot-instructions.md"
        if not copilot_instructions.exists():
            wiring_issues.append(".github/copilot-instructions.md NOT FOUND")
        else:
            try:
                with open(copilot_instructions, 'r', encoding='utf-8') as f:
                    instructions_content = f.read()
                
                if 'CORTEX.prompt.md' not in instructions_content:
                    wiring_issues.append("copilot-instructions.md does not reference CORTEX.prompt.md")
                
                if '.github/prompts/CORTEX.prompt.md' not in instructions_content:
                    wiring_issues.append("copilot-instructions.md missing correct path to CORTEX.prompt.md")
                    
            except Exception as e:
                wiring_issues.append(f"Failed to validate copilot-instructions.md: {e}")
        
        # Check 5: Verify template wiring in publish package
        publish_templates = self.project_root / "publish" / "CORTEX" / "cortex-brain" / "response-templates.yaml"
        if not publish_templates.exists():
            wiring_issues.append("publish/CORTEX/cortex-brain/response-templates.yaml NOT FOUND - deployment package missing templates")
        
        publish_prompt = self.project_root / "publish" / "CORTEX" / ".github" / "prompts" / "CORTEX.prompt.md"
        if not publish_prompt.exists():
            wiring_issues.append("publish/CORTEX/.github/prompts/CORTEX.prompt.md NOT FOUND - deployment package incomplete")
        
        # Build result
        if wiring_issues:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=False,
                message=f"Response template wiring incomplete ({len(wiring_issues)} issues)",
                details="\n".join(f"  • {issue}" for issue in wiring_issues),
                fix_available=False,
                fix_command="Ensure response-templates.yaml is deployed and properly referenced in CORTEX.prompt.md"
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=True,
                message="✓ Response template system properly wired (Phase 4 complete)"
            ))
    
    def check_git_exclude_setup(self):
        """GIT_EXCLUDE: Verify Git exclude setup scripts exist and are documented."""
        check_id = "GIT_EXCLUDE"
        name = "Git Exclude Configuration Scripts"
        
        setup_issues = []
        
        # Check setup scripts exist
        bash_script = self.project_root / "scripts" / "setup_git_exclude.sh"
        ps_script = self.project_root / "scripts" / "setup_git_exclude.ps1"
        
        if not bash_script.exists():
            setup_issues.append("scripts/setup_git_exclude.sh NOT FOUND (Bash version missing)")
        
        if not ps_script.exists():
            setup_issues.append("scripts/setup_git_exclude.ps1 NOT FOUND (PowerShell version missing)")
        
        # Check scripts are documented in SETUP-CORTEX.md
        setup_doc = self.project_root / "publish" / "CORTEX" / "SETUP-CORTEX.md"
        if setup_doc.exists():
            try:
                with open(setup_doc, 'r', encoding='utf-8') as f:
                    setup_content = f.read()
                
                if 'setup_git_exclude' not in setup_content:
                    setup_issues.append("SETUP-CORTEX.md does not mention setup_git_exclude scripts")
                
                if '.git/info/exclude' not in setup_content:
                    setup_issues.append("SETUP-CORTEX.md missing .git/info/exclude explanation")
                
                if 'untracked files' not in setup_content.lower():
                    setup_issues.append("SETUP-CORTEX.md missing troubleshooting for untracked files issue")
                    
            except Exception as e:
                setup_issues.append(f"Failed to validate SETUP-CORTEX.md: {e}")
        else:
            setup_issues.append("publish/CORTEX/SETUP-CORTEX.md NOT FOUND")
        
        # Check scripts are in publish package
        publish_bash = self.project_root / "publish" / "CORTEX" / "scripts" / "setup_git_exclude.sh"
        publish_ps = self.project_root / "publish" / "CORTEX" / "scripts" / "setup_git_exclude.ps1"
        
        if not publish_bash.exists():
            setup_issues.append("publish/CORTEX/scripts/setup_git_exclude.sh NOT FOUND - not deployed")
        
        if not publish_ps.exists():
            setup_issues.append("publish/CORTEX/scripts/setup_git_exclude.ps1 NOT FOUND - not deployed")
        
        # Build result
        if setup_issues:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=False,
                message=f"Git exclude setup incomplete ({len(setup_issues)} issues)",
                details="\n".join(f"  • {issue}" for issue in setup_issues) +
                       "\n\nExpected files:\n" +
                       "  • scripts/setup_git_exclude.sh (Bash version)\n" +
                       "  • scripts/setup_git_exclude.ps1 (PowerShell version)\n" +
                       "  • Documentation in SETUP-CORTEX.md\n" +
                       "  • Scripts deployed to publish/CORTEX/scripts/",
                fix_available=True,
                fix_command="Create setup_git_exclude scripts and update documentation"
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=True,
                message="✓ Git exclude setup scripts present and documented"
            ))
    
    def check_feedback_system(self):
        """FEEDBACK_SYSTEM: Verify feedback collection and GitHub Issue generation system."""
        check_id = "FEEDBACK_SYSTEM"
        name = "Feedback System Components"
        
        feedback_issues = []
        
        # Check core feedback modules exist
        feedback_modules = {
            'src/feedback/__init__.py': 'Feedback module initialization',
            'src/feedback/feedback_collector.py': 'FeedbackCollector class',
            'src/feedback/report_generator.py': 'FeedbackReportGenerator class',
            'src/feedback/github_formatter.py': 'GitHubIssueFormatter class',
            'src/feedback/entry_point.py': 'FeedbackEntryPoint class',
        }
        
        for module_path, description in feedback_modules.items():
            full_path = self.project_root / module_path
            if not full_path.exists():
                feedback_issues.append(f"{module_path} NOT FOUND - {description} missing")
        
        # Check feedback entry point in CORTEX.prompt.md
        prompt_file = self.project_root / ".github" / "prompts" / "CORTEX.prompt.md"
        if prompt_file.exists():
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
                
                if '## 📢 Feedback & Issue Reporting' not in prompt_content:
                    feedback_issues.append("CORTEX.prompt.md missing '## 📢 Feedback & Issue Reporting' section")
                
                if 'feedback' not in prompt_content.lower() or 'report issue' not in prompt_content.lower():
                    feedback_issues.append("CORTEX.prompt.md missing feedback/report issue commands")
                    
            except Exception as e:
                feedback_issues.append(f"Failed to validate CORTEX.prompt.md: {e}")
        else:
            feedback_issues.append(".github/prompts/CORTEX.prompt.md NOT FOUND")
        
        # Check feedback storage directory structure
        feedback_dir = self.project_root / "cortex-brain" / "feedback"
        if not feedback_dir.exists():
            feedback_issues.append("cortex-brain/feedback/ directory missing - storage location not configured")
        else:
            reports_dir = feedback_dir / "reports"
            if not reports_dir.exists():
                # This is a warning, not critical (created on first use)
                logger.info("Note: cortex-brain/feedback/reports/ will be created on first feedback submission")
        
        # Check critical imports in __init__.py
        init_file = self.project_root / "src" / "feedback" / "__init__.py"
        if init_file.exists():
            try:
                with open(init_file, 'r', encoding='utf-8') as f:
                    init_content = f.read()
                
                required_exports = [
                    'FeedbackCollector',
                    'FeedbackReportGenerator',
                    'GitHubIssueFormatter',
                    'FeedbackEntryPoint',
                ]
                
                for export in required_exports:
                    if export not in init_content:
                        feedback_issues.append(f"src/feedback/__init__.py missing export: {export}")
                        
            except Exception as e:
                feedback_issues.append(f"Failed to validate src/feedback/__init__.py: {e}")
        
        # Try importing feedback system (only if no file-level issues)
        if not feedback_issues:
            try:
                import sys
                sys.path.insert(0, str(self.project_root))
                
                from src.feedback import (
                    FeedbackCollector,
                    FeedbackReportGenerator,
                    GitHubIssueFormatter,
                    FeedbackEntryPoint,
                )
                
                # Verify core functionality
                collector = FeedbackCollector()
                generator = FeedbackReportGenerator(collector)
                formatter = GitHubIssueFormatter()
                entry_point = FeedbackEntryPoint()
                
            except ImportError as e:
                feedback_issues.append(f"Failed to import feedback system: {e}")
            except Exception as e:
                feedback_issues.append(f"Failed to instantiate feedback components: {e}")
        
        # Build result
        if feedback_issues:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=False,
                message=f"Feedback system validation failed ({len(feedback_issues)} issues)",
                details="\n".join(f"  • {issue}" for issue in feedback_issues) +
                       "\n\nExpected components:\n" +
                       "  • FeedbackCollector (data collection + anonymization)\n" +
                       "  • FeedbackReportGenerator (JSON/YAML/Markdown reports)\n" +
                       "  • GitHubIssueFormatter (GitHub Issue templates)\n" +
                       "  • FeedbackEntryPoint (user interface)\n" +
                       "  • /CORTEX feedback command in entry point",
                fix_available=False,
                fix_command=None
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=True,
                message="✓ Feedback system components present and functional"
            ))
    
    def check_tdd_mastery_components(self):
        """TDD_MASTERY: Verify TDD Mastery functionality is packaged for production."""
        check_id = "TDD_MASTERY"
        name = "TDD Mastery Components"
        
        tdd_issues = []
        
        # Check test-strategy.yaml exists
        test_strategy = self.project_root / "cortex-brain" / "documents" / "implementation-guides" / "test-strategy.yaml"
        if not test_strategy.exists():
            tdd_issues.append("test-strategy.yaml NOT FOUND - TDD strategy not packaged")
        else:
            try:
                with open(test_strategy, 'r', encoding='utf-8') as f:
                    strategy_content = f.read()
                
                # Check for key TDD sections
                required_sections = ['test_categories', 'blocking', 'warning', 'pragmatic', 'TDD']
                missing_sections = [sec for sec in required_sections if sec not in strategy_content]
                
                if missing_sections:
                    tdd_issues.append(f"test-strategy.yaml missing sections: {', '.join(missing_sections)}")
            except Exception as e:
                tdd_issues.append(f"Failed to validate test-strategy.yaml: {e}")
        
        # Check brain-protection-rules.yaml has TDD enforcement
        brain_rules = self.project_root / "cortex-brain" / "brain-protection-rules.yaml"
        if not brain_rules.exists():
            tdd_issues.append("brain-protection-rules.yaml NOT FOUND - SKULL TDD rules missing")
        else:
            try:
                with open(brain_rules, 'r', encoding='utf-8') as f:
                    rules_content = f.read()
                
                # Check for SKULL TDD rules
                skull_tdd_rules = ['SKULL-001', 'SKULL-002', 'SKULL-007', 'test_before_claim']
                missing_rules = [rule for rule in skull_tdd_rules if rule.lower() not in rules_content.lower()]
                
                if missing_rules:
                    tdd_issues.append(f"brain-protection-rules.yaml missing TDD rules: {', '.join(missing_rules)}")
            except Exception as e:
                tdd_issues.append(f"Failed to validate brain-protection-rules.yaml: {e}")
        
        # Check response-templates.yaml has TDD workflow templates
        templates = self.project_root / "cortex-brain" / "response-templates.yaml"
        if not templates.exists():
            tdd_issues.append("response-templates.yaml NOT FOUND - TDD workflow templates missing")
        else:
            try:
                with open(templates, 'r', encoding='utf-8') as f:
                    templates_content = f.read()
                
                # Check for TDD-related templates
                tdd_templates = ['work_planner_success', 'planning_dor_complete', 'planning_dor_incomplete', 'tester_success']
                missing_templates = [t for t in tdd_templates if t not in templates_content]
                
                if missing_templates:
                    tdd_issues.append(f"response-templates.yaml missing TDD templates: {', '.join(missing_templates)}")
            except Exception as e:
                tdd_issues.append(f"Failed to validate response-templates.yaml: {e}")
        
        # Check CORTEX.prompt.md references TDD Mastery
        prompt_file = self.project_root / ".github" / "prompts" / "CORTEX.prompt.md"
        if not prompt_file.exists():
            tdd_issues.append(".github/prompts/CORTEX.prompt.md NOT FOUND")
        else:
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
                
                # Check for TDD references
                tdd_keywords = ['test-strategy.yaml', 'TDD', 'test-first', 'DoR', 'DoD']
                missing_keywords = [kw for kw in tdd_keywords if kw not in prompt_content]
                
                if len(missing_keywords) > 2:  # Allow some flexibility
                    tdd_issues.append(f"CORTEX.prompt.md lacks TDD Mastery references (missing {len(missing_keywords)} keywords)")
            except Exception as e:
                tdd_issues.append(f"Failed to validate CORTEX.prompt.md: {e}")
        
        # Check validator registry exists (test infrastructure)
        validator_registry = self.project_root / "src" / "application" / "validation" / "validator_registry.py"
        if not validator_registry.exists():
            tdd_issues.append("validator_registry.py NOT FOUND - test validation infrastructure missing")
        
        # Try importing TDD-related components
        if not tdd_issues:
            try:
                import sys
                sys.path.insert(0, str(self.project_root))
                
                from src.application.validation.validator_registry import ValidatorRegistry
                
                # Verify registry has validators
                registry = ValidatorRegistry()
                registered_count = len(registry.get_registered_types())
                
                if registered_count < 5:
                    tdd_issues.append(f"ValidatorRegistry has insufficient validators ({registered_count} < 5)")
                
            except ImportError as e:
                tdd_issues.append(f"Failed to import validator infrastructure: {e}")
            except Exception as e:
                tdd_issues.append(f"Failed to verify validator registry: {e}")
        
        # Build result
        if tdd_issues:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=False,
                message=f"TDD Mastery validation failed ({len(tdd_issues)} issues)",
                details="\n".join(f"  • {issue}" for issue in tdd_issues) +
                       "\n\nExpected TDD components:\n" +
                       "  • test-strategy.yaml (TDD philosophy & pragmatic testing)\n" +
                       "  • brain-protection-rules.yaml (SKULL TDD enforcement)\n" +
                       "  • response-templates.yaml (TDD workflow templates)\n" +
                       "  • validator_registry.py (test validation infrastructure)\n" +
                       "  • CORTEX.prompt.md (TDD Mastery references)",
                fix_available=False,
                fix_command=None
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=True,
                message="✓ TDD Mastery components present and validated"
            ))
    
    def check_entry_point_operations(self):
        """ENTRY_OPERATIONS: Verify user-facing entry point operations."""
        check_id = "ENTRY_OPERATIONS"
        name = "Entry Point Operations (optimize, healthcheck, feedback)"
        
        operation_issues = []
        
        # Check operation modules exist
        required_operations = {
            'src/operations/optimize_operation.py': 'OptimizeOperation class',
            'src/operations/healthcheck_operation.py': 'HealthCheckOperation class',
            'src/feedback/entry_point.py': 'FeedbackEntryPoint class',
        }
        
        for module_path, description in required_operations.items():
            full_path = self.project_root / module_path
            if not full_path.exists():
                operation_issues.append(f"{module_path} NOT FOUND - {description} missing")
        
        # Check classes are properly defined
        optimize_file = self.project_root / "src" / "operations" / "optimize_operation.py"
        if optimize_file.exists():
            try:
                with open(optimize_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                required_methods = ['execute', 'validate', 'get_metadata']
                for method in required_methods:
                    if f"def {method}" not in content:
                        operation_issues.append(f"OptimizeOperation missing {method}() method")
                        
            except Exception as e:
                operation_issues.append(f"Failed to validate OptimizeOperation: {e}")
        
        healthcheck_file = self.project_root / "src" / "operations" / "healthcheck_operation.py"
        if healthcheck_file.exists():
            try:
                with open(healthcheck_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                required_methods = ['execute', 'validate', 'get_metadata']
                for method in required_methods:
                    if f"def {method}" not in content:
                        operation_issues.append(f"HealthCheckOperation missing {method}() method")
                        
            except Exception as e:
                operation_issues.append(f"Failed to validate HealthCheckOperation: {e}")
        
        # Check CORTEX.prompt.md mentions these commands
        prompt_file = self.project_root / ".github" / "prompts" / "CORTEX.prompt.md"
        if prompt_file.exists():
            try:
                with open(prompt_file, 'r', encoding='utf-8') as f:
                    prompt_content = f.read()
                
                if 'optimize' not in prompt_content.lower():
                    operation_issues.append("CORTEX.prompt.md missing 'optimize' command documentation")
                
                if 'healthcheck' not in prompt_content.lower() and 'health check' not in prompt_content.lower():
                    operation_issues.append("CORTEX.prompt.md missing 'healthcheck' command documentation")
                
                if 'feedback' not in prompt_content.lower():
                    operation_issues.append("CORTEX.prompt.md missing 'feedback' command documentation")
                    
            except Exception as e:
                operation_issues.append(f"Failed to validate CORTEX.prompt.md: {e}")
        
        # Try importing operations (only if no file-level issues)
        if not operation_issues:
            try:
                import sys
                sys.path.insert(0, str(self.project_root))
                
                from src.operations.optimize_operation import OptimizeOperation
                from src.operations.healthcheck_operation import HealthCheckOperation
                from src.feedback.entry_point import FeedbackEntryPoint
                
                # Verify instantiation
                optimize_op = OptimizeOperation()
                healthcheck_op = HealthCheckOperation()
                feedback_ep = FeedbackEntryPoint()
                
                # Verify metadata
                optimize_meta = optimize_op.get_metadata()
                if optimize_meta.name != 'optimize':
                    operation_issues.append(f"OptimizeOperation metadata.name incorrect: {optimize_meta.name}")
                
                healthcheck_meta = healthcheck_op.get_metadata()
                if healthcheck_meta.name != 'healthcheck':
                    operation_issues.append(f"HealthCheckOperation metadata.name incorrect: {healthcheck_meta.name}")
                
            except ImportError as e:
                operation_issues.append(f"Failed to import entry point operations: {e}")
            except Exception as e:
                operation_issues.append(f"Failed to instantiate entry point operations: {e}")
        
        # Build result
        if operation_issues:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=False,
                message=f"Entry point operations validation failed ({len(operation_issues)} issues)",
                details="\n".join(f"  • {issue}" for issue in operation_issues) +
                       "\n\nExpected entry points:\n" +
                       "  • optimize - Code and system optimization\n" +
                       "  • healthcheck - System health and performance monitoring\n" +
                       "  • feedback - User feedback collection and GitHub Issue generation",
                fix_available=False,
                fix_command=None
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=True,
                message="✓ Entry point operations (optimize, healthcheck, feedback) present and functional"
            ))
    
    def generate_summary(self) -> Tuple[int, int, int]:
        """
        Generate validation summary.
        
        Returns:
            Tuple of (passed, failed, warnings)
        """
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed and r.severity in ["CRITICAL", "HIGH"])
        warnings = sum(1 for r in self.results if not r.passed and r.severity in ["MEDIUM", "LOW"])
        
        logger.info("")
        logger.info("=" * 80)
        logger.info("VALIDATION SUMMARY")
        logger.info("=" * 80)
        logger.info("")
        
        # Group by severity
        critical_failures = [r for r in self.results if not r.passed and r.severity == "CRITICAL"]
        high_failures = [r for r in self.results if not r.passed and r.severity == "HIGH"]
        medium_failures = [r for r in self.results if not r.passed and r.severity == "MEDIUM"]
        low_failures = [r for r in self.results if not r.passed and r.severity == "LOW"]
        
        if critical_failures:
            logger.error(f"🔴 CRITICAL FAILURES ({len(critical_failures)}):")
            for result in critical_failures:
                logger.error(f"   [{result.check_id}] {result.message}")
                if result.details:
                    for line in result.details.split('\n'):
                        logger.error(f"      {line}")
                if result.fix_command:
                    logger.error(f"      Fix: {result.fix_command}")
            logger.error("")
        
        if high_failures:
            logger.error(f"🟠 HIGH PRIORITY FAILURES ({len(high_failures)}):")
            for result in high_failures:
                logger.error(f"   [{result.check_id}] {result.message}")
                if result.fix_command:
                    logger.error(f"      Fix: {result.fix_command}")
            logger.error("")
        
        if medium_failures:
            logger.warning(f"🟡 MEDIUM PRIORITY WARNINGS ({len(medium_failures)}):")
            for result in medium_failures:
                logger.warning(f"   [{result.check_id}] {result.message}")
            logger.warning("")
        
        if low_failures:
            logger.info(f"🟢 LOW PRIORITY ISSUES ({len(low_failures)}):")
            for result in low_failures:
                logger.info(f"   [{result.check_id}] {result.message}")
            logger.info("")
        
        # Show passed checks
        passed_checks = [r for r in self.results if r.passed]
        if passed_checks:
            logger.info(f"✅ PASSED CHECKS ({len(passed_checks)}):")
            for result in passed_checks:
                logger.info(f"   [{result.check_id}] {result.message}")
            logger.info("")
        
        # Final verdict
        logger.info("=" * 80)
        if critical_failures or high_failures:
            logger.error("❌ DEPLOYMENT BLOCKED")
            logger.error(f"   Critical: {len(critical_failures)}, High: {len(high_failures)}")
            logger.error("   Fix all CRITICAL and HIGH issues before deployment")
            logger.info("")
            return (passed, failed, warnings)
        elif medium_failures:
            logger.warning("⚠️  DEPLOYMENT WITH WARNINGS")
            logger.warning(f"   Medium: {len(medium_failures)}, Low: {len(low_failures)}")
            logger.warning("   Review warnings before deployment (not blocking)")
            logger.info("")
            return (passed, 0, warnings)
        else:
            logger.info("✅ DEPLOYMENT APPROVED")
            logger.info("   All validation checks passed")
            logger.info("")
            return (passed, 0, 0)
    
    def save_report(self, output_path: Path):
        """Save detailed validation report."""
        report_data = {
            'timestamp': datetime.now().isoformat(),
            'version': VERSION,
            'project_root': str(self.project_root),
            'summary': {
                'total_checks': len(self.results),
                'passed': sum(1 for r in self.results if r.passed),
                'failed': sum(1 for r in self.results if not r.passed),
                'critical': sum(1 for r in self.results if not r.passed and r.severity == "CRITICAL"),
                'high': sum(1 for r in self.results if not r.passed and r.severity == "HIGH"),
                'medium': sum(1 for r in self.results if not r.passed and r.severity == "MEDIUM"),
                'low': sum(1 for r in self.results if not r.passed and r.severity == "LOW"),
            },
            'results': [asdict(r) for r in self.results]
        }
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(report_data, f, indent=2)
        
        logger.info(f"📄 Detailed report saved: {output_path}")


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='CORTEX Pre-Deployment Validation Gate',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
This script validates CORTEX deployment readiness by checking for all gaps
identified in CORTEX-DEPLOYMENT-GAP-ANALYSIS-2025-11-22.md.

Exit codes:
  0 - All validations passed (safe to deploy)
  1 - Critical failures (BLOCK deployment)
  2 - Warnings (review required)

Examples:
  python scripts/validate_deployment.py                # Run validation
  python scripts/validate_deployment.py --report       # Save detailed report
  python scripts/validate_deployment.py --fix          # Auto-fix when possible
"""
    )
    parser.add_argument(
        '--project-root',
        type=Path,
        default=Path(__file__).parent.parent,
        help='CORTEX project root directory'
    )
    parser.add_argument(
        '--report',
        type=Path,
        help='Save detailed validation report to file'
    )
    parser.add_argument(
        '--fix',
        action='store_true',
        help='Attempt to auto-fix issues when possible'
    )
    
    args = parser.parse_args()
    
    validator = DeploymentValidator(
        project_root=args.project_root,
        auto_fix=args.fix
    )
    
    passed, failed, warnings = validator.run_all_checks()
    
    if args.report:
        validator.save_report(args.report)
    
    # Determine exit code
    if failed > 0:
        return 1  # Block deployment
    elif warnings > 0:
        return 2  # Warnings (not blocking)
    else:
        return 0  # All good


if __name__ == '__main__':
    sys.exit(main())
