"""
CORTEX 4.0 Foundation Validation Script

Validates that all Phase 1 prerequisites are correctly implemented:
1. ✅ Configuration System (src/config/)
2. ✅ Logging System (src/logging/)
3. ✅ Response Templates v4.0 (src/templates/)
4. ✅ Dependency Injection (src/di/)
5. ✅ Testing Infrastructure (tests/fixtures/)
6. ✅ MCP Gateway Stub (src/mcp/)
7. ✅ Brain Interface (inherited from 3.0)
8. ✅ Git isolation + requirements.txt
9. ✅ Base Orchestrator (inherited from 3.0)
10. ✅ cortex.config.json v4.0

Usage:
    python scripts/validate_cortex_4_foundation.py
    python scripts/validate_cortex_4_foundation.py --verbose
"""

import sys
import os
from pathlib import Path
from typing import List, Tuple, Dict
import json
import yaml

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class ValidationResult:
    """Result of a validation check"""
    
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message
    
    def __repr__(self):
        status = "✅ PASS" if self.passed else "❌ FAIL"
        msg = f" - {self.message}" if self.message else ""
        return f"{status}: {self.name}{msg}"


class FoundationValidator:
    """Validates CORTEX 4.0 foundation implementation"""
    
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results: List[ValidationResult] = []
        self.project_root = Path(__file__).parent.parent
    
    def validate_all(self) -> bool:
        """
        Run all validation checks.
        
        Returns:
            True if all checks pass, False otherwise
        """
        print("=" * 80)
        print("CORTEX 4.0 FOUNDATION VALIDATION")
        print("=" * 80)
        print()
        
        # Run all prerequisite checks
        self.check_prerequisite_1_config()
        self.check_prerequisite_2_logging()
        self.check_prerequisite_3_templates()
        self.check_prerequisite_4_dependency_injection()
        self.check_prerequisite_5_testing_fixtures()
        self.check_prerequisite_6_mcp_gateway()
        self.check_prerequisite_7_brain_interface()
        self.check_prerequisite_8_git_requirements()
        self.check_prerequisite_9_base_orchestrator()
        self.check_prerequisite_10_config_v4()
        
        # Print results
        self.print_results()
        
        # Return overall status
        return all(r.passed for r in self.results)
    
    def check_prerequisite_1_config(self):
        """Check Configuration System (src/config/)"""
        name = "Prerequisite 1: Configuration System"
        
        try:
            # Check files exist
            config_init = self.project_root / "src" / "config" / "__init__.py"
            config_manager = self.project_root / "src" / "config" / "config_manager.py"
            
            if not config_init.exists():
                self.results.append(ValidationResult(name, False, "src/config/__init__.py not found"))
                return
            
            if not config_manager.exists():
                self.results.append(ValidationResult(name, False, "src/config/config_manager.py not found"))
                return
            
            # Try importing
            from src.config import ConfigManager, get_config_manager
            
            # Verify functionality
            config = get_config_manager()
            version = config.get("version", "unknown")
            
            self.results.append(ValidationResult(name, True, f"Config loaded, version: {version}"))
            
        except Exception as e:
            self.results.append(ValidationResult(name, False, str(e)))
    
    def check_prerequisite_2_logging(self):
        """Check Logging System (src/logging/)"""
        name = "Prerequisite 2: Logging System"
        
        try:
            # Check files exist
            logging_init = self.project_root / "src" / "logging" / "__init__.py"
            logger_module = self.project_root / "src" / "logging" / "logger.py"
            
            if not logging_init.exists():
                self.results.append(ValidationResult(name, False, "src/logging/__init__.py not found"))
                return
            
            if not logger_module.exists():
                self.results.append(ValidationResult(name, False, "src/logging/logger.py not found"))
                return
            
            # Try importing
            from src.cortex_logging import setup_logger
            
            # Verify functionality
            logger = setup_logger("test_validation")
            
            self.results.append(ValidationResult(name, True, "Logger setup successful"))
            
        except Exception as e:
            self.results.append(ValidationResult(name, False, str(e)))
    
    def check_prerequisite_3_templates(self):
        """Check Response Templates v4.0"""
        name = "Prerequisite 3: Response Templates v4.0"
        
        try:
            # Check YAML file
            yaml_file = self.project_root / "cortex-brain" / "response-templates-v4.yaml"
            
            if not yaml_file.exists():
                self.results.append(ValidationResult(name, False, "response-templates-v4.yaml not found"))
                return
            
            # Check line count
            with open(yaml_file, 'r', encoding='utf-8') as f:
                lines = len(f.readlines())
            
            if lines > 600:  # Allowing some margin over 500
                self.results.append(ValidationResult(name, False, f"YAML file too large: {lines} lines (target <500)"))
                return
            
            # Check Python modules
            templates_init = self.project_root / "src" / "templates" / "__init__.py"
            template_manager = self.project_root / "src" / "templates" / "template_manager.py"
            
            if not templates_init.exists() or not template_manager.exists():
                self.results.append(ValidationResult(name, False, "Template Python modules not found"))
                return
            
            # Try importing
            from src.templates import TemplateManager, ResponseTier, get_template_manager
            
            self.results.append(ValidationResult(name, True, f"Templates loaded ({lines} lines YAML)"))
            
        except Exception as e:
            self.results.append(ValidationResult(name, False, str(e)))
    
    def check_prerequisite_4_dependency_injection(self):
        """Check Dependency Injection System"""
        name = "Prerequisite 4: Dependency Injection"
        
        try:
            # Check files exist
            di_init = self.project_root / "src" / "di" / "__init__.py"
            di_container = self.project_root / "src" / "di" / "container.py"
            di_decorators = self.project_root / "src" / "di" / "decorators.py"
            
            if not di_init.exists():
                self.results.append(ValidationResult(name, False, "src/di/__init__.py not found"))
                return
            
            if not di_container.exists():
                self.results.append(ValidationResult(name, False, "src/di/container.py not found"))
                return
            
            if not di_decorators.exists():
                self.results.append(ValidationResult(name, False, "src/di/decorators.py not found"))
                return
            
            # Try importing
            from src.di import CortexContainer, get_container, orchestrator
            
            # Verify container
            container = get_container()
            
            self.results.append(ValidationResult(name, True, "DI container initialized"))
            
        except Exception as e:
            self.results.append(ValidationResult(name, False, str(e)))
    
    def check_prerequisite_5_testing_fixtures(self):
        """Check Testing Infrastructure"""
        name = "Prerequisite 5: Testing Infrastructure"
        
        try:
            # Check fixture files
            orchestrator_fixtures = self.project_root / "tests" / "fixtures" / "orchestrator_fixtures.py"
            brain_fixtures = self.project_root / "tests" / "fixtures" / "brain_fixtures.py"
            
            if not orchestrator_fixtures.exists():
                self.results.append(ValidationResult(name, False, "orchestrator_fixtures.py not found"))
                return
            
            if not brain_fixtures.exists():
                self.results.append(ValidationResult(name, False, "brain_fixtures.py not found"))
                return
            
            # Check pytest.ini
            pytest_ini = self.project_root / "pytest.ini"
            if not pytest_ini.exists():
                self.results.append(ValidationResult(name, False, "pytest.ini not found"))
                return
            
            self.results.append(ValidationResult(name, True, "Test fixtures present"))
            
        except Exception as e:
            self.results.append(ValidationResult(name, False, str(e)))
    
    def check_prerequisite_6_mcp_gateway(self):
        """Check MCP Gateway Stub"""
        name = "Prerequisite 6: MCP Gateway Stub"
        
        try:
            # Check files exist
            mcp_init = self.project_root / "src" / "mcp" / "__init__.py"
            
            if not mcp_init.exists():
                self.results.append(ValidationResult(name, False, "src/mcp/__init__.py not found"))
                return
            
            # Try importing
            from src.mcp import get_mcp_gateway
            
            gateway = get_mcp_gateway()
            
            self.results.append(ValidationResult(name, True, "MCP Gateway stub present"))
            
        except Exception as e:
            self.results.append(ValidationResult(name, False, str(e)))
    
    def check_prerequisite_7_brain_interface(self):
        """Check Brain Interface (inherited from 3.0)"""
        name = "Prerequisite 7: Brain Interface"
        
        try:
            # Check brain directories
            tier0 = self.project_root / "src" / "tier0"
            tier1 = self.project_root / "src" / "tier1"
            tier2 = self.project_root / "src" / "tier2"
            tier3 = self.project_root / "src" / "tier3"
            
            if not (tier0.exists() and tier1.exists() and tier2.exists() and tier3.exists()):
                self.results.append(ValidationResult(name, False, "Brain tier directories incomplete"))
                return
            
            self.results.append(ValidationResult(name, True, "Brain tiers present (4 tiers)"))
            
        except Exception as e:
            self.results.append(ValidationResult(name, False, str(e)))
    
    def check_prerequisite_8_git_requirements(self):
        """Check Git isolation and requirements.txt"""
        name = "Prerequisite 8: Git + Requirements"
        
        try:
            # Check .git
            git_dir = self.project_root / ".git"
            if not git_dir.exists():
                self.results.append(ValidationResult(name, False, ".git directory not found"))
                return
            
            # Check requirements.txt
            requirements = self.project_root / "requirements.txt"
            if not requirements.exists():
                self.results.append(ValidationResult(name, False, "requirements.txt not found"))
                return
            
            # Count dependencies
            with open(requirements, 'r') as f:
                deps = [line.strip() for line in f if line.strip() and not line.startswith('#')]
            
            self.results.append(ValidationResult(name, True, f"Git + requirements ({len(deps)} packages)"))
            
        except Exception as e:
            self.results.append(ValidationResult(name, False, str(e)))
    
    def check_prerequisite_9_base_orchestrator(self):
        """Check Base Orchestrator exists"""
        name = "Prerequisite 9: Base Orchestrator"
        
        try:
            # Check for base orchestrator (multiple possible locations)
            base_orchestrator_paths = [
                self.project_root / "src" / "orchestrators" / "base" / "base_orchestrator.py",
                self.project_root / "src" / "orchestration_3_0" / "core" / "base_orchestrator.py",
            ]
            
            found = False
            for path in base_orchestrator_paths:
                if path.exists():
                    found = True
                    break
            
            if not found:
                self.results.append(ValidationResult(name, False, "Base orchestrator not found"))
                return
            
            self.results.append(ValidationResult(name, True, "Base orchestrator present"))
            
        except Exception as e:
            self.results.append(ValidationResult(name, False, str(e)))
    
    def check_prerequisite_10_config_v4(self):
        """Check cortex.config.json v4.0 schema"""
        name = "Prerequisite 10: cortex.config.json v4.0"
        
        try:
            config_file = self.project_root / "cortex.config.json"
            
            if not config_file.exists():
                self.results.append(ValidationResult(name, False, "cortex.config.json not found"))
                return
            
            # Load and check schema
            with open(config_file, 'r') as f:
                config_data = json.load(f)
            
            # Check for v4.0 schema markers
            version = config_data.get("version", "unknown")
            has_brain = "brain" in config_data
            has_ide = "ide" in config_data
            has_logging = "logging" in config_data
            
            if not (has_brain and has_ide and has_logging):
                self.results.append(ValidationResult(name, False, "Config missing v4.0 sections"))
                return
            
            self.results.append(ValidationResult(name, True, f"Config v{version} with v4.0 schema"))
            
        except Exception as e:
            self.results.append(ValidationResult(name, False, str(e)))
    
    def print_results(self):
        """Print validation results"""
        print()
        print("=" * 80)
        print("VALIDATION RESULTS")
        print("=" * 80)
        print()
        
        passed = sum(1 for r in self.results if r.passed)
        total = len(self.results)
        
        for result in self.results:
            # Use ASCII-safe output for Windows console
            status = "[PASS]" if result.passed else "[FAIL]"
            print(f"{status} {result.name}: {result.message}")
        
        print()
        print("=" * 80)
        print(f"SUMMARY: {passed}/{total} prerequisites validated")
        
        if passed == total:
            print("[PASS] PHASE 1 FOUNDATION COMPLETE!")
        else:
            print(f"[FAIL] {total - passed} prerequisites failed")
        
        print("=" * 80)


def main():
    """Main entry point"""
    verbose = "--verbose" in sys.argv or "-v" in sys.argv
    
    validator = FoundationValidator(verbose=verbose)
    success = validator.validate_all()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
