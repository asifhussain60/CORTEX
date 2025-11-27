#!/usr/bin/env python3
"""
Master Setup Orchestrator

Coordinates complete CORTEX setup and onboarding workflow.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, Any

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from src.operations.dependency_installer import DependencyInstaller, DependencyResult
from src.operations.user_consent_manager import UserConsentManager, ConsentAction
from src.operations.onboarding_orchestrator import OnboardingOrchestrator, OnboardingResult
from src.orchestrators.setup_epm_orchestrator import SetupEPMOrchestrator
from src.operations.policy_scanner import PolicyScanner
from src.validation.policy_validator import PolicyValidator, ViolationSeverity
from src.orchestrators.realignment_orchestrator import RealignmentOrchestrator

logger = logging.getLogger(__name__)


@dataclass
class SetupResult:
    """Complete setup result."""
    success: bool
    phase_results: Dict[str, Any]
    setup_time: float
    completion_report_path: Optional[str]
    errors: list


class MasterSetupOrchestrator:
    """
    Master orchestrator for complete CORTEX setup workflow.
    
    Workflow:
    1. Show introduction (response template)
    2. Request user consent
    3. Install dependencies
    4. Onboard application (analysis + dashboard)
    5. Setup .gitignore
    6. Generate copilot instructions
    7. Create completion report
    """
    
    def __init__(
        self,
        project_root: Path,
        cortex_root: Optional[Path] = None,
        interactive: bool = True
    ):
        self.project_root = Path(project_root)
        self.cortex_root = cortex_root or self._find_cortex_root()
        self.interactive = interactive
        self.project_name = self.project_root.name
    
    def _find_cortex_root(self) -> Path:
        """Find CORTEX installation root."""
        # Check for embedded CORTEX
        if (self.project_root / "CORTEX").exists():
            return self.project_root / "CORTEX"
        
        # Check if we're in CORTEX repo
        if (self.project_root / "cortex-brain").exists():
            return self.project_root
        
        # Check common locations
        common_locations = [
            Path.home() / "PROJECTS" / "CORTEX",
            Path(__file__).parent.parent.parent
        ]
        
        for location in common_locations:
            if (location / "cortex-brain").exists():
                return location
        
        raise FileNotFoundError("CORTEX installation not found")
    
    def execute_full_setup(self) -> SetupResult:
        """
        Execute complete setup workflow with all phases.
        
        Returns:
            SetupResult with all phase results
        """
        start_time = datetime.now()
        phase_results = {}
        errors = []
        
        logger.info("="*70)
        logger.info("🧠 CORTEX Master Setup Orchestrator")
        logger.info("="*70)
        logger.info(f"Project: {self.project_name}")
        logger.info(f"CORTEX: {self.cortex_root}")
        logger.info(f"Interactive: {self.interactive}")
        logger.info("")
        
        try:
            # Phase 0: Introduction (handled by response template)
            # User sees onboarding_introduction template before this runs
            
            # Phase 1: Detect project structure
            logger.info("Phase 1: Detecting project structure...")
            epm = SetupEPMOrchestrator(str(self.project_root))
            detected = epm._detect_project_structure()
            detected['estimated_time'] = self._estimate_time(detected)
            phase_results['detection'] = detected
            logger.info(f"✅ Detected: {detected['language']} / {detected['framework']}")
            
            # Phase 2: User Consent
            logger.info("\nPhase 2: Requesting user consent...")
            consent_mgr = UserConsentManager(self.project_name, self.interactive)
            consent = consent_mgr.request_onboarding_consent(detected)
            phase_results['consent'] = {
                'action': consent.action.value,
                'approved_steps': consent.approved_steps,
                'skipped_steps': consent.skipped_steps
            }
            
            if consent.action == ConsentAction.CANCEL:
                logger.info("❌ Setup cancelled by user")
                return SetupResult(
                    success=False,
                    phase_results=phase_results,
                    setup_time=(datetime.now() - start_time).total_seconds(),
                    completion_report_path=None,
                    errors=["User cancelled setup"]
                )
            
            logger.info(f"✅ User approved: {', '.join(consent.approved_steps)}")
            
            # Phase 3: Install Dependencies
            if self._step_approved("dependencies", consent):
                logger.info("\nPhase 3: Installing dependencies...")
                installer = DependencyInstaller(self.cortex_root)
                dep_result = installer.install_dependencies()
                phase_results['dependencies'] = {
                    'success': dep_result.success,
                    'python_version': dep_result.python_version,
                    'packages_installed': len(dep_result.installed_packages),
                    'venv_created': dep_result.venv_created
                }
                
                if not dep_result.success:
                    errors.extend(dep_result.errors)
                    logger.error("❌ Dependency installation failed")
                    # Continue anyway (non-critical)
                else:
                    logger.info(f"✅ Installed {len(dep_result.installed_packages)} packages")
            else:
                logger.info("\nPhase 3: Skipped (user choice)")
                phase_results['dependencies'] = {'skipped': True}
            
            # Phase 3.5: Policy Validation
            if self._step_approved("policy_validation", consent):
                logger.info("\nPhase 3.5: Policy validation...")
                scanner = PolicyScanner(self.project_root)
                policies = scanner.scan_for_policies()
                
                if not policies:
                    logger.info("⚠️  No policy documents found")
                    if self.interactive:
                        create_starter = input("Create starter policy template? (y/n): ").lower()
                        if create_starter == 'y':
                            template_path = scanner.create_starter_policies()
                            logger.info(f"✅ Created: {template_path}")
                            policies = scanner.scan_for_policies()
                
                if policies:
                    validator = PolicyValidator(self.project_root, self.cortex_root)
                    result = validator.validate()
                    report_path = validator.generate_report(result)
                    
                    phase_results['policy_validation'] = {
                        'success': True,
                        'compliant': result.compliant,
                        'compliance_percentage': result.compliance_percentage,
                        'total_rules': result.total_rules,
                        'passed': result.passed,
                        'failed': result.failed,
                        'report_path': str(report_path)
                    }
                    
                    logger.info(f"\n{result.summary}")
                    logger.info(f"Compliance: {result.compliance_percentage:.1f}%")
                    logger.info(f"Report: {report_path}")
                    
                    # Check for critical violations
                    critical = [v for v in result.violations if v.severity == ViolationSeverity.CRITICAL]
                    if critical:
                        logger.warning(f"\n⚠️  {len(critical)} critical violation(s) detected")
                        logger.warning("   Review report before continuing")
                        if self.interactive:
                            proceed = input("Continue anyway? (y/n): ").lower()
                            if proceed != 'y':
                                logger.info("Setup halted - fix critical violations first")
                                return SetupResult(
                                    success=False,
                                    cortex_root=self.cortex_root,
                                    project_root=self.project_root,
                                    phase_results=phase_results,
                                    setup_time=(datetime.now() - start_time).total_seconds(),
                                    completion_report_path=None,
                                    errors=["Critical policy violations - setup halted by user"]
                                )
                else:
                    phase_results['policy_validation'] = {
                        'success': True,
                        'compliant': True,
                        'message': 'No policies found - using best practices'
                    }
                    logger.info("✅ No policies to validate - using best practices")
            else:
                logger.info("\nPhase 3.5: Skipped (user choice)")
                phase_results['policy_validation'] = {'skipped': True}
            
            # Phase 3.6: Realignment (Auto-fix violations)
            if self._step_approved("realignment", consent):
                logger.info("\nPhase 3.6: Realignment (auto-fix violations)...")
                
                # Only run realignment if policy validation found violations
                policy_result = phase_results.get('policy_validation', {})
                if policy_result.get('failed', 0) > 0:
                    realignment_orch = RealignmentOrchestrator(
                        self.project_root,
                        self.cortex_root,
                        self.interactive
                    )
                    realignment_result = realignment_orch.realign()
                    
                    phase_results['realignment'] = {
                        'success': realignment_result.success,
                        'actions_applied': len(realignment_result.actions_applied),
                        'actions_skipped': len(realignment_result.actions_skipped),
                        'before_compliance': realignment_result.before_compliance,
                        'after_compliance': realignment_result.after_compliance,
                        'report_path': str(realignment_result.report_path) if realignment_result.report_path else None
                    }
                    
                    if realignment_result.success:
                        improvement = realignment_result.after_compliance - realignment_result.before_compliance
                        logger.info(f"✅ Realignment complete")
                        logger.info(f"   Applied: {len(realignment_result.actions_applied)} actions")
                        logger.info(f"   Compliance: {realignment_result.before_compliance:.1f}% → {realignment_result.after_compliance:.1f}% (+{improvement:.1f}%)")
                        if realignment_result.report_path:
                            logger.info(f"   Report: {realignment_result.report_path}")
                    else:
                        logger.warning("⚠️ Realignment had errors")
                        errors.extend(realignment_result.errors)
                else:
                    phase_results['realignment'] = {
                        'success': True,
                        'skipped_reason': 'No violations to fix'
                    }
                    logger.info("✅ No violations detected - realignment not needed")
            else:
                logger.info("\nPhase 3.6: Skipped (user choice)")
                phase_results['realignment'] = {'skipped': True}
            
            # Phase 4: Onboard Application
            if self._step_approved("quality", consent):
                logger.info("\nPhase 4: Onboarding application...")
                onboarding = OnboardingOrchestrator(self.cortex_root)
                onboard_result = onboarding.onboard_application(
                    self.project_root,
                    self.project_name
                )
                phase_results['onboarding'] = {
                    'success': onboard_result.success,
                    'quality_score': onboard_result.quality_score,
                    'security_issues': onboard_result.security_issues,
                    'performance_metrics': onboard_result.performance_metrics,
                    'dashboard_url': onboard_result.dashboard_url
                }
                
                if not onboard_result.success:
                    errors.extend(onboard_result.errors)
                    logger.error("❌ Onboarding failed")
                else:
                    logger.info(f"✅ Analysis complete (Quality: {onboard_result.quality_score:.1f}%)")
            else:
                logger.info("\nPhase 4: Skipped (user choice)")
                phase_results['onboarding'] = {'skipped': True}
            
            # Phase 5: Setup GitIgnore
            if self._step_approved("gitignore", consent):
                logger.info("\nPhase 5: Configuring .gitignore...")
                gitignore_result = self._setup_gitignore()
                phase_results['gitignore'] = gitignore_result
                
                if gitignore_result['success']:
                    logger.info("✅ GitIgnore configured")
                else:
                    logger.warning("⚠️ GitIgnore setup skipped (already configured)")
            else:
                logger.info("\nPhase 5: Skipped (user choice)")
                phase_results['gitignore'] = {'skipped': True}
            
            # Phase 6: Generate Copilot Instructions
            logger.info("\nPhase 6: Generating copilot instructions...")
            epm_result = epm.execute(force=False)
            phase_results['copilot_instructions'] = epm_result
            
            if epm_result['success']:
                logger.info(f"✅ Created: {epm_result['file_path']}")
            else:
                logger.warning("⚠️ Copilot instructions already exist")
            
            # Phase 7: Create Completion Report
            logger.info("\nPhase 7: Generating completion report...")
            report_path = self._create_completion_report(phase_results, start_time)
            phase_results['completion_report'] = report_path
            logger.info(f"✅ Report: {report_path}")
            
            # Success!
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info("")
            logger.info("="*70)
            logger.info(f"✅ CORTEX Setup Complete! ({elapsed:.1f}s)")
            logger.info("="*70)
            
            return SetupResult(
                success=True,
                phase_results=phase_results,
                setup_time=elapsed,
                completion_report_path=report_path,
                errors=errors
            )
            
        except Exception as e:
            logger.error(f"❌ Setup failed: {e}", exc_info=True)
            errors.append(str(e))
            
            elapsed = (datetime.now() - start_time).total_seconds()
            return SetupResult(
                success=False,
                phase_results=phase_results,
                setup_time=elapsed,
                completion_report_path=None,
                errors=errors
            )
    
    def _step_approved(self, step_id: str, consent) -> bool:
        """Check if step was approved by user."""
        if "all" in consent.approved_steps:
            return True
        return step_id in consent.approved_steps
    
    def _estimate_time(self, detected: Dict) -> str:
        """Estimate setup time based on project size."""
        files = detected.get('files', 0)
        
        if files < 50:
            return "3-5 minutes"
        elif files < 200:
            return "5-8 minutes"
        else:
            return "8-12 minutes"
    
    def _setup_gitignore(self) -> Dict:
        """Setup .gitignore to exclude CORTEX/."""
        gitignore_path = self.project_root / ".gitignore"
        cortex_pattern = "# CORTEX AI Assistant (local only)\nCORTEX/\n"
        
        try:
            # Check if .gitignore exists
            if gitignore_path.exists():
                content = gitignore_path.read_text()
                
                # Check if CORTEX/ already excluded
                if "CORTEX/" in content:
                    return {
                        'success': True,
                        'action': 'already_configured',
                        'path': str(gitignore_path)
                    }
                
                # Append CORTEX/ exclusion
                with open(gitignore_path, 'a') as f:
                    f.write(f"\n{cortex_pattern}")
                
                return {
                    'success': True,
                    'action': 'appended',
                    'path': str(gitignore_path)
                }
            else:
                # Create new .gitignore
                gitignore_path.write_text(cortex_pattern)
                
                return {
                    'success': True,
                    'action': 'created',
                    'path': str(gitignore_path)
                }
                
        except Exception as e:
            logger.error(f"Failed to setup .gitignore: {e}")
            return {
                'success': False,
                'error': str(e)
            }
    
    def _create_completion_report(
        self,
        phase_results: Dict,
        start_time: datetime
    ) -> str:
        """Create setup completion report."""
        reports_dir = self.cortex_root / "cortex-brain" / "documents" / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = reports_dir / f"setup-complete-{self.project_name}-{timestamp}.md"
        
        elapsed = (datetime.now() - start_time).total_seconds()
        
        # Build report content
        content = f"""# CORTEX Setup Completion Report

**Project:** {self.project_name}  
**Setup Date:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}  
**Duration:** {elapsed:.1f} seconds  
**Status:** ✅ Success

---

## Phase Results

### 1. Project Detection
- **Language:** {phase_results.get('detection', {}).get('language', 'Unknown')}
- **Framework:** {phase_results.get('detection', {}).get('framework', 'None')}
- **Build System:** {phase_results.get('detection', {}).get('build_system', 'None')}
- **Test Framework:** {phase_results.get('detection', {}).get('test_framework', 'None')}

### 2. User Consent
- **Action:** {phase_results.get('consent', {}).get('action', 'N/A')}
- **Approved Steps:** {', '.join(phase_results.get('consent', {}).get('approved_steps', []))}
- **Skipped Steps:** {', '.join(phase_results.get('consent', {}).get('skipped_steps', []))}

### 3. Dependencies
"""
        
        dep = phase_results.get('dependencies', {})
        if dep.get('skipped'):
            content += "- **Status:** Skipped by user\n"
        else:
            content += f"""- **Status:** {'✅ Success' if dep.get('success') else '❌ Failed'}
- **Python Version:** {dep.get('python_version', 'N/A')}
- **Packages Installed:** {dep.get('packages_installed', 0)}
- **Virtual Environment:** {'✅ Created' if dep.get('venv_created') else 'Existing'}
"""
        
        content += "\n### 4. Application Onboarding\n"
        onboard = phase_results.get('onboarding', {})
        if onboard.get('skipped'):
            content += "- **Status:** Skipped by user\n"
        else:
            content += f"""- **Status:** {'✅ Success' if onboard.get('success') else '❌ Failed'}
- **Quality Score:** {onboard.get('quality_score', 0):.1f}%
- **Security Issues:** {onboard.get('security_issues', 0)}
- **Performance Metrics:** {onboard.get('performance_metrics', 0)}
- **Dashboard:** {onboard.get('dashboard_url', 'Not generated')}
"""
        
        content += "\n### 5. GitIgnore Configuration\n"
        gitignore = phase_results.get('gitignore', {})
        if gitignore.get('skipped'):
            content += "- **Status:** Skipped by user\n"
        else:
            content += f"""- **Status:** {'✅ Success' if gitignore.get('success') else '❌ Failed'}
- **Action:** {gitignore.get('action', 'N/A')}
- **Path:** {gitignore.get('path', 'N/A')}
"""
        
        content += "\n### 6. Copilot Instructions\n"
        epm = phase_results.get('copilot_instructions', {})
        content += f"""- **Status:** {'✅ Created' if epm.get('success') else '⚠️ Already exists'}
- **Path:** {epm.get('file_path', 'N/A')}
- **Learning Enabled:** {'Yes' if epm.get('learning_enabled') else 'No'}
"""
        
        # Add Phase 3.5 Policy Validation and Phase 3.6 Realignment
        content += "\n### 3.5. Policy Validation\n"
        policy = phase_results.get('policy_validation', {})
        if policy.get('skipped'):
            content += "- **Status:** Skipped by user\n"
        else:
            content += f"""- **Status:** {'✅ Success' if policy.get('success') else '❌ Failed'}
- **Compliant:** {'Yes' if policy.get('compliant') else 'No'}
- **Compliance Percentage:** {policy.get('compliance_percentage', 100):.1f}%
- **Total Rules:** {policy.get('total_rules', 0)}
- **Passed:** {policy.get('passed', 0)}
- **Failed:** {policy.get('failed', 0)}
- **Report:** {policy.get('report_path', 'N/A')}
"""
        
        content += "\n### 3.6. Realignment (Auto-fix)\n"
        realignment = phase_results.get('realignment', {})
        if realignment.get('skipped'):
            content += "- **Status:** Skipped by user\n"
        elif realignment.get('skipped_reason'):
            content += f"- **Status:** ✅ Skipped ({realignment.get('skipped_reason')})\n"
        else:
            content += f"""- **Status:** {'✅ Success' if realignment.get('success') else '❌ Failed'}
- **Actions Applied:** {realignment.get('actions_applied', 0)}
- **Actions Skipped:** {realignment.get('actions_skipped', 0)}
- **Before Compliance:** {realignment.get('before_compliance', 0):.1f}%
- **After Compliance:** {realignment.get('after_compliance', 0):.1f}%
- **Improvement:** +{realignment.get('after_compliance', 0) - realignment.get('before_compliance', 0):.1f}%
- **Report:** {realignment.get('report_path', 'N/A')}
"""
        
        content += f"""
---

## Next Steps

1. **Activate virtual environment** (if created):
   ```bash
   # Windows
   venv\\Scripts\\activate
   
   # Unix/macOS
   source venv/bin/activate
   ```

2. **Start working with CORTEX:**
   ```bash
   # Interactive tutorial (recommended for first-time users)
   tutorial
   
   # Plan a feature
   plan [feature name]
   
   # Start TDD workflow
   start tdd
   
   # Get help
   help
   ```

3. **View dashboard** (if generated):
   - Open: `{onboard.get('dashboard_url', 'cortex-brain/dashboard/index.html')}`

4. **Refresh copilot instructions** after a few sessions:
   ```bash
   cortex refresh instructions
   ```

---

## CORTEX Capabilities

- **Planning System 2.0** - Vision API, DoR/DoD enforcement
- **TDD Mastery** - RED→GREEN→REFACTOR automation
- **View Discovery** - Auto-extract UI element IDs
- **Feedback System** - Structured issue reporting
- **Upgrade System** - Safe upgrades with brain preservation

**Welcome to CORTEX!** 🧠

---

*Generated by CORTEX Master Setup Orchestrator v3.2.0*  
*© 2024-2025 Asif Hussain. All rights reserved.*
"""
        
        report_path.write_text(content, encoding='utf-8')
        return str(report_path)


def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="CORTEX Master Setup Orchestrator")
    parser.add_argument("project_root", help="Project root directory to setup")
    parser.add_argument("--cortex-root", help="CORTEX installation root (auto-detected if not provided)")
    parser.add_argument("--non-interactive", action="store_true", help="Run without user prompts")
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(message)s'
    )
    
    # Run setup
    orchestrator = MasterSetupOrchestrator(
        project_root=Path(args.project_root),
        cortex_root=Path(args.cortex_root) if args.cortex_root else None,
        interactive=not args.non_interactive
    )
    
    result = orchestrator.execute_full_setup()
    
    # Exit with appropriate code
    sys.exit(0 if result.success else 1)


if __name__ == "__main__":
    main()
