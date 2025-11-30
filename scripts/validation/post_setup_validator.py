#!/usr/bin/env python3
"""
Post-Setup Validator

Validates that critical CORTEX setup steps are complete after clone/install.
Prevents incomplete deployments that users experience.

Validation Categories:
    1. Entry Point Deployment - .github/prompts/CORTEX.prompt.md exists
    2. Auto-Discovery File - copilot-instructions.md updated with CORTEX entry point
    3. Brain Initialization - Database files created (tier1, tier2, tier3)
    4. Configuration - cortex.config.json properly configured

Usage:
    # Run after setup
    python scripts/validation/post_setup_validator.py
    
    # In setup scripts (automatic)
    from scripts.validation.post_setup_validator import PostSetupValidator
    validator = PostSetupValidator(repo_root)
    success, report = validator.validate()

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple
import json

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


class PostSetupValidator:
    """
    Validates post-setup state to ensure complete deployment.
    
    Checks:
        - Entry point file deployed to .github/prompts/
        - Auto-discovery file (copilot-instructions.md) updated
        - Brain databases initialized
        - Configuration valid
    """
    
    def __init__(self, repo_root: Path):
        """
        Initialize validator.
        
        Args:
            repo_root: Path to CORTEX repository root
        """
        self.repo_root = Path(repo_root)
        self.issues: List[str] = []
        self.warnings: List[str] = []
        
    def validate(self) -> Tuple[bool, Dict]:
        """
        Run all validation checks.
        
        Returns:
            (success, report) where success is True if all critical checks pass
            and report contains detailed validation results
        """
        logger.info("🔍 Running post-setup validation...")
        
        # Critical checks (failures block deployment)
        critical_passed = True
        critical_passed &= self._check_entry_point_deployed()
        critical_passed &= self._check_auto_discovery_updated()
        critical_passed &= self._check_brain_initialized()
        critical_passed &= self._check_configuration()
        
        # Warning checks (don't block but need attention)
        self._check_git_ignore()
        self._check_version_file()
        
        # Generate report
        report = {
            'success': critical_passed,
            'issues': self.issues,
            'warnings': self.warnings,
            'checks': {
                'entry_point': self._check_entry_point_deployed(),
                'auto_discovery': self._check_auto_discovery_updated(),
                'brain_initialized': self._check_brain_initialized(),
                'configuration': self._check_configuration(),
                'git_ignore': len(self.warnings) == 0
            }
        }
        
        # Print summary
        if critical_passed:
            logger.info("✅ Post-setup validation PASSED")
            if self.warnings:
                logger.warning(f"⚠️  {len(self.warnings)} warning(s) found")
        else:
            logger.error(f"❌ Post-setup validation FAILED - {len(self.issues)} critical issue(s)")
            
        return critical_passed, report
    
    def _check_entry_point_deployed(self) -> bool:
        """
        Check that CORTEX.prompt.md is deployed to .github/prompts/.
        
        This file is the main entry point for GitHub Copilot integration.
        
        Returns:
            True if file exists and is valid
        """
        entry_point = self.repo_root / '.github' / 'prompts' / 'CORTEX.prompt.md'
        
        if not entry_point.exists():
            self.issues.append(
                "CRITICAL: .github/prompts/CORTEX.prompt.md not found. "
                "GitHub Copilot won't auto-activate CORTEX."
            )
            return False
            
        # Check file size (should be substantial)
        file_size = entry_point.stat().st_size
        if file_size < 10000:  # Less than 10KB is suspicious
            self.issues.append(
                f"CRITICAL: CORTEX.prompt.md is too small ({file_size} bytes). "
                "File may be corrupted or incomplete."
            )
            return False
            
        logger.info(f"✅ Entry point deployed: {entry_point} ({file_size:,} bytes)")
        return True
    
    def _check_auto_discovery_updated(self) -> bool:
        """
        Check that copilot-instructions.md references CORTEX entry point.
        
        This file enables auto-discovery when users clone the repository.
        
        Returns:
            True if file exists and contains CORTEX reference
        """
        copilot_instructions = self.repo_root / '.github' / 'copilot-instructions.md'
        
        if not copilot_instructions.exists():
            self.issues.append(
                "CRITICAL: .github/copilot-instructions.md not found. "
                "Users won't get auto-discovery after cloning."
            )
            return False
            
        # Check for CORTEX reference
        content = copilot_instructions.read_text(encoding='utf-8')
        
        if 'CORTEX.prompt.md' not in content:
            self.issues.append(
                "CRITICAL: copilot-instructions.md doesn't reference CORTEX.prompt.md. "
                "Add '#file:.github/prompts/CORTEX.prompt.md' to the file."
            )
            return False
            
        logger.info(f"✅ Auto-discovery file updated: {copilot_instructions}")
        return True
    
    def _check_brain_initialized(self) -> bool:
        """
        Check that brain databases are initialized.
        
        Brain files:
            - cortex-brain/tier1-working-memory.db (or tier1/working_memory.db)
            - cortex-brain/tier2-knowledge-graph.db (or tier2/knowledge_graph.db)
            - cortex-brain/tier3-development-context.db (or tier3/context.db)
        
        Returns:
            True if at least one brain database exists
        """
        brain_root = self.repo_root / 'cortex-brain'
        
        if not brain_root.exists():
            self.issues.append(
                "CRITICAL: cortex-brain/ directory not found. "
                "Brain storage missing."
            )
            return False
        
        # Check for database files (any valid structure)
        db_patterns = [
            'tier1-working-memory.db',
            'tier1/working_memory.db',
            'tier2-knowledge-graph.db',
            'tier2/knowledge_graph.db',
            'tier3-development-context.db',
            'tier3/context.db'
        ]
        
        found_dbs = []
        for pattern in db_patterns:
            db_path = brain_root / pattern
            if db_path.exists():
                found_dbs.append(str(db_path.relative_to(self.repo_root)))
        
        if not found_dbs:
            # This is a warning, not critical - databases initialize on first use
            self.warnings.append(
                "Brain databases not initialized yet. "
                "They will be created on first CORTEX operation."
            )
            logger.info("ℹ️  Brain databases will be created on first use")
            return True  # Not critical
        
        logger.info(f"✅ Brain initialized: {len(found_dbs)} database(s) found")
        return True
    
    def _check_configuration(self) -> bool:
        """
        Check that cortex.config.json is properly configured.
        
        Returns:
            True if configuration is valid
        """
        config_file = self.repo_root / 'cortex.config.json'
        
        if not config_file.exists():
            self.issues.append(
                "CRITICAL: cortex.config.json not found. "
                "Copy from cortex.config.template.json and configure."
            )
            return False
        
        try:
            config = json.loads(config_file.read_text(encoding='utf-8'))
            
            # Check for required keys
            required_keys = ['machines', 'mode']
            missing_keys = [key for key in required_keys if key not in config]
            
            if missing_keys:
                self.issues.append(
                    f"CRITICAL: cortex.config.json missing required keys: {', '.join(missing_keys)}"
                )
                return False
            
            # Check machine configuration exists
            if not config.get('machines'):
                self.warnings.append(
                    "No machine configurations found in cortex.config.json. "
                    "Add your machine's hostname and paths."
                )
            
            logger.info(f"✅ Configuration valid: {config_file}")
            return True
            
        except json.JSONDecodeError as e:
            self.issues.append(
                f"CRITICAL: cortex.config.json is invalid JSON: {e}"
            )
            return False
    
    def _check_git_ignore(self) -> None:
        """
        Check that CORTEX folders are properly excluded from git.
        
        Warning only - doesn't block deployment.
        """
        gitignore = self.repo_root / '.gitignore'
        
        if not gitignore.exists():
            self.warnings.append(
                ".gitignore not found. CORTEX folders may be tracked by git. "
                "Create .gitignore with 'CORTEX/' entry if in user repository."
            )
            return
        
        content = gitignore.read_text(encoding='utf-8')
        
        # Check for CORTEX exclusion (only relevant for embedded installations)
        if 'CORTEX/' not in content and 'cortex-brain/' not in content:
            # Only warn if this looks like an embedded installation
            if (self.repo_root.parent / '.git').exists():
                self.warnings.append(
                    ".gitignore doesn't exclude CORTEX/. "
                    "Add 'CORTEX/' to prevent accidental commits in user repositories."
                )
    
    def _check_version_file(self) -> None:
        """
        Check that VERSION file exists and is valid.
        
        Warning only - doesn't block deployment.
        """
        version_file = self.repo_root / 'VERSION'
        
        if not version_file.exists():
            self.warnings.append(
                "VERSION file not found. This may cause version detection issues."
            )
            return
        
        version_text = version_file.read_text(encoding='utf-8').strip()
        
        if not version_text or len(version_text) < 5:
            self.warnings.append(
                f"VERSION file content looks invalid: '{version_text}'"
            )


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Validate CORTEX post-setup state",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        '--repo',
        type=Path,
        default=Path.cwd(),
        help='CORTEX repository root (default: current directory)'
    )
    
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output results as JSON'
    )
    
    args = parser.parse_args()
    
    # Run validation
    validator = PostSetupValidator(args.repo)
    success, report = validator.validate()
    
    # Output results
    if args.json:
        import json
        print(json.dumps(report, indent=2))
    else:
        print("\n" + "=" * 60)
        print("POST-SETUP VALIDATION REPORT")
        print("=" * 60)
        
        if report['issues']:
            print("\n❌ CRITICAL ISSUES:")
            for issue in report['issues']:
                print(f"  • {issue}")
        
        if report['warnings']:
            print("\n⚠️  WARNINGS:")
            for warning in report['warnings']:
                print(f"  • {warning}")
        
        if not report['issues'] and not report['warnings']:
            print("\n✅ All checks passed!")
        
        print("\nCHECK SUMMARY:")
        for check, passed in report['checks'].items():
            status = "✅ PASS" if passed else "❌ FAIL"
            print(f"  {check}: {status}")
        
        print("=" * 60)
    
    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
