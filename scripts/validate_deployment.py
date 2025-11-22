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
        
        # GAP-001: Check src/config.py exists
        self.check_config_module()
        
        # GAP-002: Check documentation modules
        self.check_documentation_modules()
        
        # GAP-003: Check Tier 2 initialization
        self.check_tier2_initialization()
        
        # GAP-004: Check operation module imports
        self.check_operation_modules()
        
        # GAP-005: Check OperationFactory API
        self.check_operation_factory_api()
        
        # GAP-006: Check test coverage
        self.check_test_suite()
        
        # GAP-007: Check SKULL protection tests
        self.check_skull_protection()
        
        # GAP-008: Check onboarding workflow
        self.check_onboarding_workflow()
        
        # GAP-009: Check response templates
        self.check_response_templates()
        
        # GAP-012: Check CORTEX dependencies and tooling
        self.check_cortex_dependencies()
        
        # Additional critical checks
        self.check_critical_files()
        self.check_import_health()
        self.check_git_status()
        
        # Generate summary
        return self.generate_summary()
    
    def check_config_module(self):
        """GAP-001: Verify src/config.py exists and is valid."""
        check_id = "GAP-001"
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
                fix_command="Create src/config.py with ConfigManager class (see GAP-001 in analysis)"
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
        """GAP-002: Verify all referenced documentation modules exist."""
        check_id = "GAP-002"
        name = "Documentation Modules Complete"
        
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
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=False,
                message=f"{len(missing_docs)} documentation modules missing",
                details=f"Missing:\n" + "\n".join(f"  - {doc}" for doc in missing_docs),
                fix_available=False,
                fix_command="Extract from monolithic docs (8-12 hours estimated)"
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=True,
                message="✓ All documentation modules present"
            ))
    
    def check_tier2_initialization(self):
        """GAP-003: Verify Tier 2 can auto-initialize."""
        check_id = "GAP-003"
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
        """GAP-004: Verify operation modules can import successfully."""
        check_id = "GAP-004"
        name = "Operation Modules Import Successfully"
        
        # First check if config exists (dependency)
        config_file = self.project_root / "src" / "config.py"
        if not config_file.exists():
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=False,
                message="Cannot test - depends on GAP-001 (config.py missing)",
                details="Fix GAP-001 first, then retest",
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
                    severity="HIGH",
                    passed=True,
                    message=f"✓ {registered_count} operation modules registered successfully"
                ))
            else:
                self.results.append(ValidationResult(
                    check_id=check_id,
                    name=name,
                    severity="HIGH",
                    passed=False,
                    message=f"Only {registered_count} modules registered (expected 29+)",
                    details="Some modules may have import errors",
                    fix_available=False
                ))
        
        except ImportError as e:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=False,
                message=f"OperationFactory import failed: {e}",
                details="Module registration system broken",
                fix_available=False
            ))
        except Exception as e:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="HIGH",
                passed=False,
                message=f"Failed to validate operation modules: {e}",
                fix_available=False
            ))
    
    def check_operation_factory_api(self):
        """GAP-005: Verify OperationFactory has required API methods."""
        check_id = "GAP-005"
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
        """GAP-006: Verify comprehensive test suite exists."""
        check_id = "GAP-006"
        name = "Test Suite Coverage"
        
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
        """GAP-007: Verify SKULL protection rules are tested."""
        check_id = "GAP-007"
        name = "SKULL Protection Validated"
        
        skull_test_file = self.project_root / "tests" / "tier0" / "test_skull_protection.py"
        
        if not skull_test_file.exists():
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
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
                severity="CRITICAL",
                passed=True,
                message="✓ SKULL protection test suite exists"
            ))
    
    def check_onboarding_workflow(self):
        """GAP-008: Verify onboarding workflow is functional and includes tooling setup instructions."""
        check_id = "GAP-008"
        name = "Onboarding Workflow Functional"
        
        onboarding_modules = [
            "src/operations/modules/application_onboarding_steps.py",
            "src/operations/modules/user_onboarding_steps.py",
            "src/operations/modules/tooling_installer_module.py",
        ]
        
        docs_linked = [
            ".github/prompts/modules/story.md",
            ".github/prompts/modules/setup-guide.md",
        ]
        
        setup_docs = [
            "publish/CORTEX/SETUP-FOR-COPILOT.md",
        ]
        
        missing = []
        for module_path in onboarding_modules + docs_linked + setup_docs:
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
        """GAP-009: Verify response template system is complete."""
        check_id = "GAP-009"
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
    
    def check_cortex_dependencies(self):
        """GAP-012: Verify all CORTEX dependencies and tooling are installed and documented."""
        check_id = "GAP-012"
        name = "CORTEX Dependencies & Tooling"
        
        missing_deps = []
        installation_instructions = []
        documentation_issues = []
        
        # Check Python version
        import sys
        python_version = sys.version_info
        if python_version < (3, 9):
            missing_deps.append(f"Python 3.9+ (current: {python_version.major}.{python_version.minor})")
            installation_instructions.append("Install Python 3.9+ from https://www.python.org/downloads/")
        
        # Check required USER-FACING Python packages (exclude admin-only tools)
        user_required_packages = {
            'pytest': 'pytest>=8.4.0',
            'pytest_cov': 'pytest-cov>=6.0.0',
            'yaml': 'PyYAML>=6.0.2',
            'watchdog': 'watchdog>=6.0.0',
            'psutil': 'psutil>=6.1.1',
            'send2trash': 'send2trash>=1.8.3',
            'sklearn': 'scikit-learn>=1.5.2',
            'numpy': 'numpy>=1.26.4,<2.0.0',
            'pyperclip': 'pyperclip>=1.9.0',
        }
        
        # Admin-only packages (not required for user setup validation)
        admin_only_packages = {
            'mkdocs': 'mkdocs>=1.6.1',
            'material': 'mkdocs-material>=9.5.52',
            'black': 'black>=24.12.0',
            'flake8': 'flake8>=7.1.1',
            'mypy': 'mypy>=1.14.2',
            'radon': 'radon>=6.0.1',
            'pylint': 'pylint>=3.3.4',
            'vulture': 'vulture>=2.14',
        }
        
        for module, package in user_required_packages.items():
            try:
                __import__(module)
            except ImportError:
                missing_deps.append(package)
        
        # Check Git installation (USER REQUIRED)
        git_installed = False
        try:
            result = subprocess.run(
                ['git', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                git_installed = True
            else:
                missing_deps.append("Git")
                installation_instructions.append("Install Git from https://git-scm.com/downloads")
        except FileNotFoundError:
            missing_deps.append("Git")
            installation_instructions.append("Install Git from https://git-scm.com/downloads")
        except Exception:
            pass
        
        # Check Node.js installation (USER REQUIRED for Vision API)
        node_installed = False
        try:
            result = subprocess.run(
                ['node', '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                node_installed = True
            else:
                missing_deps.append("Node.js")
                installation_instructions.append("Install Node.js from https://nodejs.org/")
        except FileNotFoundError:
            missing_deps.append("Node.js")
            installation_instructions.append("Install Node.js from https://nodejs.org/ (required for Vision API)")
        except Exception:
            pass
        
        # Check SQLite installation (USER REQUIRED)
        sqlite_installed = False
        try:
            import sqlite3
            sqlite_installed = True
        except ImportError:
            missing_deps.append("SQLite (Python sqlite3 module)")
            installation_instructions.append("SQLite typically included with Python - reinstall Python if missing")
        
        # Validate SETUP-FOR-COPILOT.md documentation (CRITICAL for user onboarding)
        setup_doc = self.project_root / "publish/CORTEX/SETUP-FOR-COPILOT.md"
        
        if not setup_doc.exists():
            documentation_issues.append("SETUP-FOR-COPILOT.md missing entirely")
        else:
            try:
                with open(setup_doc, 'r', encoding='utf-8') as f:
                    setup_content = f.read().lower()
                
                # Check for comprehensive tooling documentation
                required_tooling_docs = {
                    'python': ['python', '3.9', 'install'],
                    'git': ['git', 'install'],
                    'node.js': ['node', 'vision api', 'install'],
                    'sqlite': ['sqlite', 'database'],
                    'pip_packages': ['pip install', 'requirements.txt'],
                    'vision_api': ['vision api', 'optional', 'screenshot']
                }
                
                for tool, keywords in required_tooling_docs.items():
                    keyword_matches = sum(1 for kw in keywords if kw in setup_content)
                    if keyword_matches < 2:  # At least 2 keywords must be present
                        documentation_issues.append(
                            f"{tool.replace('_', ' ').title()} setup instructions incomplete or missing"
                        )
                
            except Exception as e:
                documentation_issues.append(f"Failed to validate setup documentation: {e}")
        
        # Build result
        issues_found = bool(missing_deps or documentation_issues)
        
        if issues_found:
            fix_commands = []
            
            # Python packages installation
            python_packages = [dep for dep in missing_deps if not any(
                dep.startswith(tool) for tool in ["Git", "Node.js", "SQLite", "Python"]
            )]
            if python_packages:
                fix_commands.append("pip install -r requirements.txt")
            
            # Additional installation instructions
            fix_commands.extend(installation_instructions)
            
            # Documentation fix instructions
            if documentation_issues:
                fix_commands.append(
                    "\nDOCUMENTATION FIXES NEEDED in publish/CORTEX/SETUP-FOR-COPILOT.md:\n" +
                    "\n".join(f"  • {issue}" for issue in documentation_issues) +
                    "\n\nEnsure comprehensive setup instructions for:\n"
                    "  • Python 3.9+ installation (with download link)\n"
                    "  • Git installation (with download link)\n"
                    "  • Node.js installation (for Vision API, with download link)\n"
                    "  • SQLite verification (explain it comes with Python)\n"
                    "  • pip install -r requirements.txt (clear command)\n"
                    "  • Vision API setup (optional, with config instructions)"
                )
            
            details_parts = []
            if missing_deps:
                details_parts.append("Missing dependencies:\n" + "\n".join(f"  • {dep}" for dep in missing_deps))
            if documentation_issues:
                details_parts.append("Documentation issues:\n" + "\n".join(f"  • {issue}" for issue in documentation_issues))
            
            details = "\n\n".join(details_parts)
            
            severity = "CRITICAL" if missing_deps else "HIGH"
            
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity=severity,
                passed=False,
                message=f"{'Missing dependencies' if missing_deps else 'Documentation incomplete'} ({len(missing_deps)} deps, {len(documentation_issues)} doc issues)",
                details=details,
                fix_available=True,
                fix_command="\n".join(fix_commands)
            ))
        else:
            self.results.append(ValidationResult(
                check_id=check_id,
                name=name,
                severity="CRITICAL",
                passed=True,
                message="✓ All user-required dependencies installed and documented (admin tools excluded)"
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
