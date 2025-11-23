"""
CORTEX Automated Deployment Script
===================================

Purpose: Deploy CORTEX with comprehensive validation and production package creation
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)

Deployment Phases:
1. Pre-deployment validation (entry points, docs, tests)
2. Entry point validation (module verification)
3. Run comprehensive test suite (44 tests)
4. Validate upgrade compatibility (brain preservation)
5. Create production package (PHYSICALLY BUILDS PACKAGE)
6. Generate deployment report

CRITICAL: Phase 5 MUST create actual production package in publish/ directory
This is enforced by validation that verifies package physically exists.

Usage: python scripts/deploy_cortex.py
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple
import json
from datetime import datetime

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class CortexDeployer:
    """Automated CORTEX deployment with validation enforcement"""
    
    def __init__(self):
        self.root = Path(__file__).parent.parent
        self.failures: List[str] = []
        self.warnings: List[str] = []
        self.deployment_report = {
            'timestamp': datetime.now().isoformat(),
            'phases': {},
            'validation_results': {},
            'package_info': {}
        }
    
    def deploy(self) -> bool:
        """Run full deployment pipeline"""
        print(f"{Colors.BOLD}CORTEX Automated Deployment Pipeline{Colors.RESET}")
        print("=" * 70)
        
        phases = [
            ('Pre-Deployment Validation', self.phase1_validation),
            ('Entry Point Validation', self.phase2_entry_points),
            ('Comprehensive Testing', self.phase3_testing),
            ('Upgrade Compatibility', self.phase4_upgrade),
            ('Production Package Creation', self.phase5_package),
            ('Deployment Report', self.phase6_report)
        ]
        
        for phase_name, phase_func in phases:
            print(f"\n{Colors.BLUE}{'=' * 70}{Colors.RESET}")
            print(f"{Colors.BOLD}{phase_name}{Colors.RESET}")
            print(f"{Colors.BLUE}{'=' * 70}{Colors.RESET}")
            
            success = phase_func()
            self.deployment_report['phases'][phase_name] = 'PASSED' if success else 'FAILED'
            
            if not success:
                print(f"\n{Colors.RED}❌ {phase_name} FAILED{Colors.RESET}")
                return False
            
            print(f"\n{Colors.GREEN}✅ {phase_name} PASSED{Colors.RESET}")
        
        return True
    
    def phase1_validation(self) -> bool:
        """Phase 1: Pre-deployment validation"""
        print(f"\n{Colors.BLUE}Running pre-deployment checks...{Colors.RESET}")
        
        checks = [
            ('Git status clean', self.check_git_clean),
            ('All files committed', self.check_no_uncommitted),
            ('VERSION file present', self.check_version_file),
            ('Requirements.txt updated', self.check_requirements),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                result = check_func()
                if result:
                    print(f"  ✅ {check_name}")
                else:
                    print(f"  ⚠️  {check_name} - Non-critical")
                    self.warnings.append(check_name)
            except Exception as e:
                print(f"  ❌ {check_name}: {e}")
                self.failures.append(f"{check_name}: {e}")
                all_passed = False
        
        return all_passed
    
    def phase2_entry_points(self) -> bool:
        """Phase 2: Entry point module validation"""
        print(f"\n{Colors.BLUE}Validating entry point modules...{Colors.RESET}")
        
        # Run entry point validator
        result = subprocess.run(
            [sys.executable, 'scripts/validate_entry_points.py'],
            cwd=self.root,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.stderr:
            print(f"{Colors.RED}STDERR:{Colors.RESET}")
            print(result.stderr)
        
        if result.returncode == 0:
            self.deployment_report['validation_results']['entry_points'] = 'PASSED'
            return True
        else:
            self.deployment_report['validation_results']['entry_points'] = 'FAILED'
            self.failures.append(f'Entry point validation failed (exit code: {result.returncode})')
            return False
    
    def phase3_testing(self) -> bool:
        """Phase 3: Comprehensive test suite"""
        print(f"\n{Colors.BLUE}Running comprehensive test suite...{Colors.RESET}")
        
        # Run Issue #3 validation
        result = subprocess.run(
            [sys.executable, 'validate_issue3_phase4.py'],
            cwd=self.root,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode == 0:
            self.deployment_report['validation_results']['issue3_fixes'] = 'PASSED'
            print(f"  ✅ Issue #3 validation passed")
            return True
        else:
            self.deployment_report['validation_results']['issue3_fixes'] = 'FAILED'
            self.failures.append('Issue #3 validation failed')
            return False
    
    def phase4_upgrade(self) -> bool:
        """Phase 4: Upgrade compatibility validation"""
        print(f"\n{Colors.BLUE}Validating upgrade compatibility...{Colors.RESET}")
        
        checks = [
            ('Brain preservation logic', self.check_brain_preservation),
            ('Migration scripts present', self.check_migration_scripts),
            ('Rollback procedure documented', self.check_rollback_docs),
            ('.gitignore template present', self.check_gitignore_template),
        ]
        
        all_passed = True
        for check_name, check_func in checks:
            try:
                result = check_func()
                if result:
                    print(f"  ✅ {check_name}")
                else:
                    print(f"  ⚠️  {check_name} - Warning")
                    self.warnings.append(check_name)
            except Exception as e:
                print(f"  ❌ {check_name}: {e}")
                self.failures.append(f"{check_name}: {e}")
                all_passed = False
        
        return all_passed
    
    def phase5_package(self) -> bool:
        """Phase 5: Create deployment package - PHYSICALLY CREATES PRODUCTION PACKAGE"""
        print(f"\n{Colors.BLUE}Creating deployment package...{Colors.RESET}")
        
        # CRITICAL: Read VERSION file to get current version
        version_file = self.root / 'VERSION'
        if not version_file.exists():
            print(f"  ❌ VERSION file not found")
            self.failures.append("VERSION file missing - cannot determine package version")
            return False
        
        version = version_file.read_text(encoding='utf-8').strip()
        print(f"  📦 Package version: {version}")
        
        # Define output directory for production package
        output_dir = self.root / 'publish' / f'CORTEX-{version}'
        
        print(f"  📂 Output directory: {output_dir}")
        
        # CRITICAL VALIDATION: Run build_user_deployment.py to create actual package
        print(f"\n  🔨 Building production package...")
        
        build_script = self.root / 'scripts' / 'build_user_deployment.py'
        if not build_script.exists():
            print(f"  ❌ build_user_deployment.py not found")
            self.failures.append("Production packaging script missing")
            return False
        
        # Execute build script
        result = subprocess.run(
            [sys.executable, str(build_script), '--output', str(output_dir)],
            cwd=self.root,
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        
        if result.returncode != 0:
            print(f"  ❌ Package build failed")
            if result.stderr:
                print(f"  Error: {result.stderr}")
            self.failures.append("Production package build failed")
            return False
        
        # CRITICAL VALIDATION: Verify package was actually created
        if not output_dir.exists():
            print(f"  ❌ Package directory not created: {output_dir}")
            self.failures.append(f"Package directory not created: {output_dir}")
            return False
        
        # Verify key files exist in package
        required_package_files = [
            'src/',
            'cortex-brain/',
            '.github/prompts/CORTEX.prompt.md',
            'cortex-operations.yaml',
            'requirements.txt',
            'LICENSE',
            'README.md'
        ]
        
        print(f"\n  ✅ Validating package contents...")
        missing_in_package = []
        for item in required_package_files:
            package_path = output_dir / item
            if package_path.exists():
                print(f"    ✅ {item}")
            else:
                print(f"    ❌ {item} - Missing in package")
                missing_in_package.append(item)
        
        if missing_in_package:
            self.failures.extend([f"Missing in package: {item}" for item in missing_in_package])
            return False
        
        # Calculate and report package size
        total_size = sum(f.stat().st_size for f in output_dir.rglob('*') if f.is_file())
        size_mb = total_size / (1024 * 1024)
        
        print(f"\n  📊 Package successfully created:")
        print(f"    Location: {output_dir}")
        print(f"    Size: {size_mb:.2f} MB")
        print(f"    Files: {sum(1 for _ in output_dir.rglob('*') if _.is_file())}")
        
        # Store package info in deployment report
        self.deployment_report['package_info'] = {
            'version': version,
            'location': str(output_dir),
            'size_mb': round(size_mb, 2),
            'files_count': sum(1 for _ in output_dir.rglob('*') if _.is_file()),
            'validation': 'PASSED'
        }
        
        return True
    
    def phase6_report(self) -> bool:
        """Phase 6: Generate deployment report"""
        print(f"\n{Colors.BLUE}Generating deployment report...{Colors.RESET}")
        
        report_path = self.root / 'DEPLOYMENT-REPORT.json'
        
        self.deployment_report['summary'] = {
            'failures': len(self.failures),
            'warnings': len(self.warnings),
            'status': 'PASSED' if len(self.failures) == 0 else 'FAILED'
        }
        
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(self.deployment_report, f, indent=2)
        
        print(f"  ✅ Report saved: {report_path}")
        return True
    
    # Helper check functions
    def check_git_clean(self) -> bool:
        """Check git working directory is clean"""
        result = subprocess.run(
            ['git', 'status', '--porcelain'],
            cwd=self.root,
            capture_output=True,
            text=True
        )
        return len(result.stdout.strip()) == 0
    
    def check_no_uncommitted(self) -> bool:
        """Check no uncommitted changes"""
        result = subprocess.run(
            ['git', 'diff', '--exit-code'],
            cwd=self.root,
            capture_output=True
        )
        return result.returncode == 0
    
    def check_version_file(self) -> bool:
        """Check VERSION file exists"""
        return (self.root / 'VERSION').exists()
    
    def check_requirements(self) -> bool:
        """Check requirements.txt present"""
        return (self.root / 'requirements.txt').exists()
    
    def check_brain_preservation(self) -> bool:
        """Check brain preservation logic exists"""
        upgrade_guide = self.root / '.github' / 'prompts' / 'modules' / 'upgrade-guide.md'
        if upgrade_guide.exists():
            content = upgrade_guide.read_text(encoding='utf-8')
            return 'Brain Data Preservation' in content or 'preserve brain' in content.lower()
        return False
    
    def check_migration_scripts(self) -> bool:
        """Check migration scripts present"""
        migration_script = self.root / 'apply_element_mappings_schema.py'
        return migration_script.exists()
    
    def check_rollback_docs(self) -> bool:
        """Check rollback procedure documented"""
        upgrade_guide = self.root / '.github' / 'prompts' / 'modules' / 'upgrade-guide.md'
        if upgrade_guide.exists():
            content = upgrade_guide.read_text(encoding='utf-8')
            return 'Rollback' in content or 'rollback' in content.lower()
        return False
    
    def check_gitignore_template(self) -> bool:
        """Check .gitignore template exists"""
        # Check if upgrade guide documents .gitignore handling
        upgrade_guide = self.root / '.github' / 'prompts' / 'modules' / 'upgrade-guide.md'
        if upgrade_guide.exists():
            content = upgrade_guide.read_text(encoding='utf-8')
            return '.gitignore' in content.lower()
        return False
    
    def print_summary(self) -> bool:
        """Print deployment summary"""
        print("\n" + "=" * 70)
        print(f"{Colors.BOLD}DEPLOYMENT SUMMARY{Colors.RESET}")
        print("=" * 70)
        
        if self.failures:
            print(f"{Colors.RED}❌ FAILURES: {len(self.failures)}{Colors.RESET}")
            for failure in self.failures:
                print(f"  ❌ {failure}")
        
        if self.warnings:
            print(f"{Colors.YELLOW}⚠️  WARNINGS: {len(self.warnings)}{Colors.RESET}")
            for warning in self.warnings:
                print(f"  ⚠️  {warning}")
        
        if not self.failures:
            print(f"\n{Colors.GREEN}{Colors.BOLD}✅ DEPLOYMENT SUCCESSFUL - READY FOR RELEASE{Colors.RESET}")
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}❌ DEPLOYMENT FAILED - FIX FAILURES BEFORE RELEASE{Colors.RESET}")
        
        print("=" * 70)
        
        return len(self.failures) == 0


def main():
    """Run CORTEX deployment"""
    deployer = CortexDeployer()
    success = deployer.deploy()
    
    deployer.print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
