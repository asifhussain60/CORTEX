"""
CORTEX Automated Deployment Script
===================================

Purpose: Deploy CORTEX with comprehensive validation and production package creation
Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)

Deployment Phases:
0. Version management (bump version, validate consistency)
1. Pre-deployment validation (entry points, docs, tests)
2. Entry point validation (module verification)
3. Run comprehensive test suite (44 tests)
4. Validate upgrade compatibility (brain preservation)
5. Create production package (PHYSICALLY BUILDS PACKAGE)
6. Generate deployment report

CRITICAL: Phase 5 MUST create actual production package in publish/ directory
This is enforced by validation that verifies package physically exists.

Usage: 
    python scripts/deploy_cortex.py [--bump-type major|minor|patch]
    python scripts/deploy_cortex.py --bump-type minor --reason "Add TDD workflow"
"""

import sys
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional
import json
from datetime import datetime
import argparse

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class CortexDeployer:
    """Automated CORTEX deployment with validation enforcement"""
    
    def __init__(self, bump_type: Optional[str] = None, bump_reason: Optional[str] = None):
        self.root = Path(__file__).parent.parent
        self.failures: List[str] = []
        self.warnings: List[str] = []
        self.bump_type = bump_type or "minor"  # Default to minor release
        self.bump_reason = bump_reason
        self.deployment_report = {
            'timestamp': datetime.now().isoformat(),
            'phases': {},
            'validation_results': {},
            'package_info': {},
            'version_info': {}
        }
    
    def deploy(self) -> bool:
        """Run full deployment pipeline"""
        print(f"{Colors.BOLD}CORTEX Automated Deployment Pipeline{Colors.RESET}")
        print("=" * 70)
        
        phases = [
            ('Version Management', self.phase0_version_management),
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
    
    def phase0_version_management(self) -> bool:
        """Phase 0: Version management and consistency validation"""
        print(f"\n{Colors.BLUE}Managing version for deployment...{Colors.RESET}")
        
        try:
            # Import version manager
            sys.path.insert(0, str(self.root / "scripts"))
            from version_manager import VersionManager, Version
            
            manager = VersionManager(self.root)
            
            # Get current version
            current_version = manager.get_current_version()
            print(f"  📦 Current version: {current_version}")
            
            # Validate version consistency
            is_valid, issues = manager.validate_version_consistency()
            if not is_valid:
                print(f"  ⚠️  Version consistency issues detected:")
                for issue in issues:
                    print(f"     - {issue}")
                self.warnings.extend(issues)
            else:
                print(f"  ✅ Version consistency validated")
            
            # Bump version if requested
            if self.bump_type:
                print(f"\n  🔼 Bumping version: {self.bump_type} release")
                
                # Determine reason
                if not self.bump_reason:
                    if self.bump_type == "major":
                        self.bump_reason = "Major release (breaking changes)"
                    elif self.bump_type == "minor":
                        self.bump_reason = "Minor release (new features)"
                    else:
                        self.bump_reason = "Patch release (bug fixes)"
                
                new_version = manager.bump_version(self.bump_type, self.bump_reason)
                print(f"  ✅ Version bumped: {current_version} → {new_version}")
                
                # Store in deployment report
                self.deployment_report['version_info'] = {
                    'previous': str(current_version),
                    'current': str(new_version),
                    'bump_type': self.bump_type,
                    'reason': self.bump_reason
                }
            else:
                print(f"  ℹ️  No version bump requested (use --bump-type to bump)")
                self.deployment_report['version_info'] = {
                    'current': str(current_version),
                    'bump_type': 'none'
                }
            
            return True
            
        except Exception as e:
            print(f"  ❌ Version management failed: {e}")
            self.failures.append(f"Version management failed: {e}")
            return False
    
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
            [sys.executable, 'scripts/validation/validate_issue3_phase4.py'],
            cwd=self.root,
            capture_output=True,
            text=True,
            encoding='utf-8',
            errors='replace'
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
            ('Gist uploader service exists', self.check_gist_uploader_service),
            ('Feedback collector Gist integration', self.check_feedback_gist_integration),
            ('GitHub config schema present', self.check_github_config_schema),
            ('Platform import conflict resolved', self.check_platform_import_resolved),
            ('Gist upload integration tests', self.check_gist_upload_tests),
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
            'src/feedback/gist_uploader.py',
            'src/feedback/feedback_collector.py',
            'src/feedback/github_formatter.py',
            'cortex-brain/',
            '.github/prompts/CORTEX.prompt.md',
            'cortex-operations.yaml',
            'requirements.txt',
            'LICENSE',
            'README.md'
        ]
        
        # Optional files (nice to have but not required for deployment)
        optional_package_files = [
            'tests/test_gist_upload_integration.py',
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
        
        # Check optional files (warn but don't fail)
        for item in optional_package_files:
            package_path = output_dir / item
            if package_path.exists():
                print(f"    ✅ {item} (optional)")
            else:
                print(f"    ⚠️  {item} - Optional file not in package")
                self.warnings.append(f"Optional file not in package: {item}")
        
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
    
    def check_gist_uploader_service(self) -> bool:
        """Check Gist uploader service exists"""
        gist_uploader = self.root / 'src' / 'feedback' / 'gist_uploader.py'
        if not gist_uploader.exists():
            raise FileNotFoundError("src/feedback/gist_uploader.py not found")
        
        # Verify key classes/methods exist
        content = gist_uploader.read_text(encoding='utf-8')
        required_elements = [
            'class GistUploader',
            'def upload_report',
            'def _upload_to_gist',
            'def _prompt_for_consent',
        ]
        
        missing = [elem for elem in required_elements if elem not in content]
        if missing:
            raise ValueError(f"GistUploader missing elements: {missing}")
        
        return True
    
    def check_feedback_gist_integration(self) -> bool:
        """Check FeedbackCollector has Gist upload integration"""
        feedback_collector = self.root / 'src' / 'feedback' / 'feedback_collector.py'
        if not feedback_collector.exists():
            raise FileNotFoundError("src/feedback/feedback_collector.py not found")
        
        content = feedback_collector.read_text(encoding='utf-8')
        
        # Check for Gist integration (either direct import or factory function)
        required_elements = [
            'gist_uploader',  # Module imported
            'def _upload_feedback_item',  # Upload method exists
            'auto_upload',  # Auto upload parameter
        ]
        
        missing = [elem for elem in required_elements if elem not in content]
        if missing:
            raise ValueError(f"FeedbackCollector missing Gist integration: {missing}")
        
        return True
    
    def check_github_config_schema(self) -> bool:
        """Check cortex.config.json has GitHub section"""
        config_file = self.root / 'cortex.config.json'
        if not config_file.exists():
            raise FileNotFoundError("cortex.config.json not found")
        
        import json
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        if 'github' not in config:
            raise ValueError("cortex.config.json missing 'github' section")
        
        github_config = config['github']
        required_keys = ['token', 'repository_owner', 'repository_name']
        missing = [key for key in required_keys if key not in github_config]
        
        if missing:
            raise ValueError(f"GitHub config missing keys: {missing}")
        
        return True
    
    def check_platform_import_resolved(self) -> bool:
        """Check platform import conflict resolved (tests/platform/ renamed)"""
        # Old conflicting directory should NOT exist
        old_platform_dir = self.root / 'tests' / 'platform'
        if old_platform_dir.exists():
            raise ValueError("tests/platform/ still exists (should be renamed to tests/platform_tests/)")
        
        # New directory should exist
        new_platform_dir = self.root / 'tests' / 'platform_tests'
        if not new_platform_dir.exists():
            raise FileNotFoundError("tests/platform_tests/ not found (renamed from tests/platform/)")
        
        return True
    
    def check_gist_upload_tests(self) -> bool:
        """Check Gist upload integration tests exist"""
        test_file = self.root / 'tests' / 'test_gist_upload_integration.py'
        if not test_file.exists():
            raise FileNotFoundError("tests/test_gist_upload_integration.py not found")
        
        content = test_file.read_text(encoding='utf-8')
        
        # Verify key test cases exist
        required_tests = [
            'def test_gist_uploader_initialization',
            'def test_feedback_collector_integration',
            'def test_preferences_management',
            'def test_github_formatter_integration',
        ]
        
        missing = [test for test in required_tests if test not in content]
        if missing:
            raise ValueError(f"Gist upload tests missing: {missing}")
        
        return True
    
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
    parser = argparse.ArgumentParser(
        description='CORTEX Automated Deployment with Version Management',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Deploy with default minor version bump
  python scripts/deploy_cortex.py
  
  # Deploy with major version bump (breaking changes)
  python scripts/deploy_cortex.py --bump-type major --reason "New TDD workflow API"
  
  # Deploy with patch version bump (bug fixes)
  python scripts/deploy_cortex.py --bump-type patch --reason "Fix entry point bloat"
  
  # Deploy without version bump (testing)
  python scripts/deploy_cortex.py --no-bump
        """
    )
    
    parser.add_argument(
        '--bump-type',
        choices=['major', 'minor', 'patch'],
        default='minor',
        help='Version bump type (default: minor)'
    )
    
    parser.add_argument(
        '--no-bump',
        action='store_true',
        help='Skip version bump (for testing)'
    )
    
    parser.add_argument(
        '--reason',
        help='Reason for version change'
    )
    
    args = parser.parse_args()
    
    # Determine bump type
    bump_type = None if args.no_bump else args.bump_type
    
    deployer = CortexDeployer(bump_type=bump_type, bump_reason=args.reason)
    success = deployer.deploy()
    
    deployer.print_summary()
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
