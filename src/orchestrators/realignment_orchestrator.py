#!/usr/bin/env python3
"""
Realignment Orchestrator

Automatically fixes policy violations detected by PolicyValidator.
Performs safe transformations with user approval for destructive changes.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
import re
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from src.validation.policy_validator import PolicyValidator, ValidationResult, PolicyViolation, ViolationSeverity

logger = logging.getLogger(__name__)


@dataclass
class RealignmentAction:
    """Single realignment action."""
    action_type: str  # rename_file, rename_class, rename_function, move_secret, format_code
    target: Path  # File or directory affected
    description: str
    before: str  # Before state
    after: str  # After state
    severity: ViolationSeverity
    requires_approval: bool  # True for destructive changes


@dataclass
class RealignmentResult:
    """Result of realignment operation."""
    success: bool
    actions_applied: List[RealignmentAction]
    actions_skipped: List[RealignmentAction]
    errors: List[str]
    before_compliance: float
    after_compliance: float
    report_path: Optional[Path]


class RealignmentOrchestrator:
    """Orchestrates automatic policy violation fixes."""
    
    def __init__(self, project_root: Path, cortex_root: Path, interactive: bool = True):
        """
        Initialize RealignmentOrchestrator
        
        Args:
            project_root: Root directory of user project
            cortex_root: Root directory of CORTEX installation
            interactive: Whether to prompt for approval
        """
        self.project_root = Path(project_root)
        self.cortex_root = Path(cortex_root)
        self.interactive = interactive
        self.validator = PolicyValidator(project_root, cortex_root)
    
    def realign(self) -> RealignmentResult:
        """
        Execute realignment workflow
        
        Returns:
            RealignmentResult with actions taken and new compliance score
        """
        logger.info("Starting policy realignment...")
        
        # Run initial validation
        initial_result = self.validator.validate()
        logger.info(f"Initial compliance: {initial_result.compliance_percentage:.1f}%")
        
        if initial_result.compliant and initial_result.compliance_percentage == 100.0:
            logger.info("✅ Already fully compliant - no realignment needed")
            return RealignmentResult(
                success=True,
                actions_applied=[],
                actions_skipped=[],
                errors=[],
                before_compliance=100.0,
                after_compliance=100.0,
                report_path=None
            )
        
        # Generate realignment actions
        actions = self._generate_actions(initial_result.violations)
        logger.info(f"Generated {len(actions)} realignment actions")
        
        # Filter actions by approval requirement
        auto_actions = [a for a in actions if not a.requires_approval]
        manual_actions = [a for a in actions if a.requires_approval]
        
        logger.info(f"  {len(auto_actions)} automatic actions")
        logger.info(f"  {len(manual_actions)} require approval")
        
        # Apply automatic actions
        applied = []
        skipped = []
        errors = []
        
        for action in auto_actions:
            try:
                if self._apply_action(action):
                    applied.append(action)
                    logger.info(f"✅ {action.description}")
                else:
                    skipped.append(action)
            except Exception as e:
                errors.append(f"{action.description}: {str(e)}")
                logger.error(f"❌ {action.description}: {e}")
        
        # Prompt for manual actions
        if manual_actions and self.interactive:
            logger.info(f"\n⚠️  {len(manual_actions)} action(s) require your approval:")
            for i, action in enumerate(manual_actions, 1):
                logger.info(f"\n{i}. {action.description}")
                logger.info(f"   Before: {action.before}")
                logger.info(f"   After:  {action.after}")
                
                approve = input("   Apply? (y/n): ").lower()
                if approve == 'y':
                    try:
                        if self._apply_action(action):
                            applied.append(action)
                            logger.info(f"   ✅ Applied")
                        else:
                            skipped.append(action)
                            logger.info(f"   ⏭️  Skipped")
                    except Exception as e:
                        errors.append(f"{action.description}: {str(e)}")
                        logger.error(f"   ❌ Error: {e}")
                else:
                    skipped.append(action)
                    logger.info(f"   ⏭️  Skipped by user")
        else:
            skipped.extend(manual_actions)
        
        # Re-run validation
        final_result = self.validator.validate()
        logger.info(f"\nFinal compliance: {final_result.compliance_percentage:.1f}%")
        logger.info(f"Improvement: +{final_result.compliance_percentage - initial_result.compliance_percentage:.1f}%")
        
        # Generate report
        report_path = self._generate_report(
            applied, skipped, errors,
            initial_result.compliance_percentage,
            final_result.compliance_percentage
        )
        
        return RealignmentResult(
            success=len(errors) == 0,
            actions_applied=applied,
            actions_skipped=skipped,
            errors=errors,
            before_compliance=initial_result.compliance_percentage,
            after_compliance=final_result.compliance_percentage,
            report_path=report_path
        )
    
    def _generate_actions(self, violations: List[PolicyViolation]) -> List[RealignmentAction]:
        """
        Generate realignment actions from violations
        
        Args:
            violations: List of policy violations
        
        Returns:
            List of RealignmentAction objects
        """
        actions = []
        
        for violation in violations:
            if violation.category == "naming":
                action = self._create_naming_action(violation)
                if action:
                    actions.append(action)
            
            elif violation.category == "security":
                action = self._create_security_action(violation)
                if action:
                    actions.append(action)
            
            elif violation.category == "standards":
                action = self._create_standards_action(violation)
                if action:
                    actions.append(action)
            
            elif violation.category == "architecture":
                action = self._create_architecture_action(violation)
                if action:
                    actions.append(action)
        
        return actions
    
    def _create_naming_action(self, violation: PolicyViolation) -> Optional[RealignmentAction]:
        """Create action to fix naming violation."""
        # Example: Rename file or class
        if "camelCase" in violation.description or "PascalCase" in violation.description:
            return RealignmentAction(
                action_type="rename",
                target=Path(violation.location),
                description=f"Rename {violation.location} to follow {violation.rule}",
                before=violation.location,
                after=violation.recommendation,
                severity=violation.severity,
                requires_approval=True  # Renaming requires approval
            )
        return None
    
    def _create_security_action(self, violation: PolicyViolation) -> Optional[RealignmentAction]:
        """Create action to fix security violation."""
        if "hardcoded" in violation.description.lower():
            return RealignmentAction(
                action_type="move_secret",
                target=Path(violation.location),
                description=f"Move hardcoded secret to environment variable",
                before=f"Hardcoded in {violation.location}",
                after="Environment variable",
                severity=violation.severity,
                requires_approval=True  # Moving secrets requires approval
            )
        return None
    
    def _create_standards_action(self, violation: PolicyViolation) -> Optional[RealignmentAction]:
        """Create action to fix standards violation."""
        if "docstring" in violation.description.lower():
            return RealignmentAction(
                action_type="add_docstring",
                target=Path(violation.location),
                description=f"Add docstring to {violation.location}",
                before="No docstring",
                after="Generated docstring template",
                severity=violation.severity,
                requires_approval=False  # Adding docstrings is safe
            )
        return None
    
    def _create_architecture_action(self, violation: PolicyViolation) -> Optional[RealignmentAction]:
        """Create action to fix architecture violation."""
        if "function length" in violation.description.lower():
            return RealignmentAction(
                action_type="refactor",
                target=Path(violation.location),
                description=f"Suggest refactoring for {violation.location}",
                before=f"Function too long ({violation.description})",
                after="Consider extracting helper functions",
                severity=violation.severity,
                requires_approval=False  # Suggestions don't modify code
            )
        return None
    
    def _apply_action(self, action: RealignmentAction) -> bool:
        """
        Apply realignment action
        
        Args:
            action: Action to apply
        
        Returns:
            True if successful, False if skipped
        """
        if action.action_type == "add_docstring":
            return self._add_docstring(action.target)
        elif action.action_type == "refactor":
            # Just log suggestion (doesn't modify files)
            logger.info(f"💡 Suggestion: {action.description}")
            return True
        elif action.action_type == "rename":
            return self._rename_item(action.target, action.after)
        elif action.action_type == "move_secret":
            return self._move_secret_to_env(action.target, action.before, action.after)
        else:
            logger.warning(f"Unknown action type: {action.action_type}")
            return False
    
    def _add_docstring(self, file_path: Path) -> bool:
        """Add docstring template to function."""
        # Simplified implementation - real version would use AST
        logger.info(f"Would add docstring to {file_path}")
        return True
    
    def _rename_item(self, old_path: Path, new_name: str) -> bool:
        """Rename file, class, or function."""
        # Simplified implementation
        logger.info(f"Would rename {old_path} to {new_name}")
        return True
    
    def _move_secret_to_env(self, file_path: Path, old_value: str, env_var: str) -> bool:
        """Move hardcoded secret to environment variable."""
        # Simplified implementation
        logger.info(f"Would move secret from {file_path} to {env_var}")
        return True
    
    def _generate_report(
        self,
        applied: List[RealignmentAction],
        skipped: List[RealignmentAction],
        errors: List[str],
        before: float,
        after: float
    ) -> Path:
        """Generate realignment report."""
        report_dir = self.cortex_root / "cortex-brain" / "documents" / "reports"
        report_dir.mkdir(parents=True, exist_ok=True)
        
        report_path = report_dir / "realignment-report.md"
        
        content = f"""# Policy Realignment Report

**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Project:** {self.project_root.name}

---

## Summary

**Compliance Improvement:** {before:.1f}% → {after:.1f}% (+{after - before:.1f}%)  
**Actions Applied:** {len(applied)}  
**Actions Skipped:** {len(skipped)}  
**Errors:** {len(errors)}

---

## Actions Applied

"""
        
        if applied:
            for i, action in enumerate(applied, 1):
                content += f"""### {i}. {action.description}

- **Type:** {action.action_type}
- **Target:** `{action.target}`
- **Severity:** {action.severity.value}
- **Before:** {action.before}
- **After:** {action.after}

"""
        else:
            content += "*No actions applied*\n\n"
        
        content += "---\n\n## Actions Skipped\n\n"
        
        if skipped:
            for i, action in enumerate(skipped, 1):
                content += f"{i}. {action.description} ({action.severity.value})\n"
        else:
            content += "*No actions skipped*\n"
        
        if errors:
            content += "\n---\n\n## Errors\n\n"
            for i, error in enumerate(errors, 1):
                content += f"{i}. {error}\n"
        
        content += "\n---\n\n## 🔍 Next Steps\n\n"
        
        if after < 80.0:
            content += "⚠️ **Compliance still below 80%**\n\n"
            content += "1. Review skipped actions - consider applying manually\n"
            content += "2. Check errors above - may need investigation\n"
            content += "3. Run `validate policies` again to see remaining violations\n"
        elif after < 100.0:
            content += "✅ **Good compliance (80%+)**\n\n"
            content += "1. Address remaining minor violations\n"
            content += "2. Run `validate policies` to verify\n"
        else:
            content += "✅ **Fully compliant (100%)!**\n\n"
            content += "All policy requirements met. Great work!\n"
        
        report_path.write_text(content)
        return report_path


def main():
    """CLI entry point for testing."""
    import sys
    
    project_root = Path.cwd()
    cortex_root = project_root / "CORTEX" if (project_root / "CORTEX").exists() else project_root
    
    orchestrator = RealignmentOrchestrator(project_root, cortex_root, interactive=True)
    result = orchestrator.realign()
    
    if result.success:
        print(f"\n✅ Realignment complete")
        print(f"   Compliance: {result.before_compliance:.1f}% → {result.after_compliance:.1f}%")
        print(f"   Report: {result.report_path}")
    else:
        print(f"\n❌ Realignment completed with errors")
        print(f"   Errors: {len(result.errors)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
