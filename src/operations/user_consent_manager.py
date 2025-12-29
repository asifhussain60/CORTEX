#!/usr/bin/env python3
"""
User Consent Manager

Handles interactive user consent for CORTEX setup operations.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import logging
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Optional, Dict, Any, List

logger = logging.getLogger(__name__)


class ConsentAction(Enum):
    """User consent actions."""
    APPROVE = "approve"
    SKIP = "skip"
    CANCEL = "cancel"
    CUSTOMIZE = "customize"


@dataclass
class ConsentResult:
    """Result of user consent interaction."""
    action: ConsentAction
    approved_steps: List[str]
    skipped_steps: List[str]
    customizations: Dict[str, Any]
    user_notes: Optional[str] = None


class UserConsentManager:
    """
    Manages interactive user consent for CORTEX onboarding.
    
    Features:
    - Interactive prompts with clear explanations
    - Step-by-step confirmation
    - Customization options
    - Consent tracking
    """
    
    def __init__(self, project_name: str, interactive: bool = True):
        self.project_name = project_name
        self.interactive = interactive
    
    def request_onboarding_consent(
        self,
        detected_info: Dict[str, Any]
    ) -> ConsentResult:
        """
        Request user consent for full onboarding workflow.
        
        Args:
            detected_info: Detected project information
        
        Returns:
            ConsentResult with user decisions
        """
        if not self.interactive:
            # Non-interactive mode: auto-approve all
            return ConsentResult(
                action=ConsentAction.APPROVE,
                approved_steps=["all"],
                skipped_steps=[],
                customizations={}
            )
        
        print("\n" + "="*70)
        print("🧠 CORTEX Setup & Onboarding")
        print("="*70)
        print(f"\nProject: {self.project_name}")
        print(f"Language: {detected_info.get('language', 'Unknown')}")
        print(f"Framework: {detected_info.get('framework', 'None detected')}")
        print(f"Files to analyze: ~{detected_info.get('files', 0)} files")
        print(f"Estimated time: {detected_info.get('estimated_time', '2-5 minutes')}")
        
        print("\n📋 CORTEX will perform the following operations:")
        print("  1. ✅ Install dependencies (Python packages)")
        print("  2. 🔍 Analyze code quality (detect issues, calculate score)")
        print("  3. 🔒 Run security scan (identify vulnerabilities)")
        print("  4. 📊 Collect performance metrics (file sizes, complexity)")
        print("  5. 📈 Generate D3.js dashboard (interactive visualization)")
        print("  6. 💾 Create .github/copilot-instructions.md (auto-context)")
        print("  7. 🛡️ Setup .gitignore (exclude CORTEX/ from git)")
        
        print("\n🔒 Privacy & Safety:")
        print("  • All data stored locally (no cloud uploads)")
        print("  • Dashboard files: cortex-brain/dashboard/")
        print("  • Analysis reports: cortex-brain/documents/reports/")
        print("  • CORTEX/ folder auto-excluded from git commits")
        
        # Main consent prompt
        response = self._prompt(
            "\n❓ Proceed with CORTEX onboarding?",
            options=["Y", "N", "C", "S"],
            default="Y",
            help_text="Y=Yes (proceed), N=No (cancel), C=Customize, S=Skip optional steps"
        )
        
        if response == "N":
            print("\n❌ Onboarding cancelled by user")
            return ConsentResult(
                action=ConsentAction.CANCEL,
                approved_steps=[],
                skipped_steps=["all"],
                customizations={}
            )
        
        if response == "S":
            print("\n⚙️ Select steps to skip:")
            return self._customize_steps(detected_info, skip_mode=True)
        
        if response == "C":
            print("\n⚙️ Customizing onboarding workflow:")
            return self._customize_steps(detected_info, skip_mode=False)
        
        # Full approval
        print("\n✅ User approved full onboarding workflow")
        return ConsentResult(
            action=ConsentAction.APPROVE,
            approved_steps=["all"],
            skipped_steps=[],
            customizations={}
        )
    
    def request_dashboard_consent(self) -> bool:
        """Request specific consent for dashboard generation."""
        if not self.interactive:
            return True
        
        print("\n📊 Dashboard Generation:")
        print("  • Creates interactive D3.js visualization")
        print("  • Saved to: cortex-brain/dashboard/index.html")
        print("  • Includes: Quality charts, security heatmap, performance graphs")
        print("  • File size: ~500 KB (with data)")
        
        response = self._prompt(
            "\n❓ Generate dashboard?",
            options=["Y", "N"],
            default="Y"
        )
        
        return response == "Y"
    
    def request_policy_validation_consent(self, policy_path: str) -> bool:
        """Request consent to validate against policy documents."""
        if not self.interactive:
            return True
        
        print(f"\n📜 Policy Validation:")
        print(f"  • Policy file: {policy_path}")
        print(f"  • CORTEX will validate against: naming conventions, security rules, code standards")
        print(f"  • Generates compliance report")
        
        response = self._prompt(
            "\n❓ Validate against policy?",
            options=["Y", "N"],
            default="Y"
        )
        
        return response == "Y"
    
    def _customize_steps(
        self,
        detected_info: Dict[str, Any],
        skip_mode: bool
    ) -> ConsentResult:
        """Allow user to customize which steps to run."""
        steps = [
            ("dependencies", "Install dependencies"),
            ("quality", "Code quality analysis"),
            ("security", "Security scan"),
            ("performance", "Performance metrics"),
            ("dashboard", "Dashboard generation"),
            ("gitignore", "Setup .gitignore"),
        ]
        
        approved = []
        skipped = []
        customizations = {}
        
        print("\n" + "-"*70)
        for step_id, step_name in steps:
            response = self._prompt(
                f"❓ {step_name}?",
                options=["Y", "N"],
                default="Y" if not skip_mode else "N"
            )
            
            if response == "Y":
                approved.append(step_id)
            else:
                skipped.append(step_id)
        
        action = ConsentAction.APPROVE if len(approved) > 0 else ConsentAction.CANCEL
        
        print(f"\n✅ Approved: {len(approved)} steps")
        print(f"⏭️ Skipped: {len(skipped)} steps")
        
        return ConsentResult(
            action=action,
            approved_steps=approved,
            skipped_steps=skipped,
            customizations=customizations
        )
    
    def _prompt(
        self,
        message: str,
        options: List[str],
        default: str,
        help_text: Optional[str] = None
    ) -> str:
        """Interactive prompt with validation."""
        options_str = "/".join(options)
        
        while True:
            prompt = f"{message} [{options_str}] (default: {default}): "
            
            try:
                response = input(prompt).strip().upper()
                
                if not response:
                    return default
                
                if response in options:
                    return response
                
                if response == "?":
                    if help_text:
                        print(f"\n💡 {help_text}\n")
                    else:
                        print(f"\n💡 Valid options: {', '.join(options)}\n")
                else:
                    print(f"❌ Invalid option. Choose from: {', '.join(options)}")
                    
            except (KeyboardInterrupt, EOFError):
                print("\n\n❌ Cancelled by user")
                return "N"
    
    def confirm_action(
        self,
        action: str,
        consequences: List[str],
        default: bool = True
    ) -> bool:
        """Confirm potentially destructive action with clear consequences."""
        if not self.interactive:
            return default
        
        print(f"\n⚠️ Confirm: {action}")
        print("\n📋 This will:")
        for consequence in consequences:
            print(f"  • {consequence}")
        
        response = self._prompt(
            "\n❓ Proceed?",
            options=["Y", "N"],
            default="Y" if default else "N"
        )
        
        return response == "Y"
    
    def request_policy_validation_consent(self, policy_path: Optional[Path] = None) -> bool:
        """
        Request consent for policy validation
        
        Args:
            policy_path: Path to detected policy document (or None if none found)
        
        Returns:
            True if user approves, False otherwise
        """
        if not self.interactive:
            return True
        
        print("\n" + "=" * 70)
        print("🔒 POLICY VALIDATION")
        print("=" * 70)
        
        if policy_path:
            print(f"\n✅ Found policy document: {policy_path}")
            print("\nCORTEX will validate itself against your policies:")
        else:
            print("\n⚠️  No policy documents found")
            print("\nCORTEX can create a starter policy template with:")
        
        consequences = [
            "Check naming conventions (PascalCase, snake_case, etc.)",
            "Verify security practices (no hardcoded secrets, env vars)",
            "Validate code standards (docstrings, test coverage, linting)",
            "Review architecture patterns (SOLID, layering, error handling)",
            "Generate compliance report with recommendations",
            "Identify critical violations that may block setup"
        ]
        
        return self.confirm_action(
            action="policy validation",
            consequences=consequences,
            default=True
        )


def main():
    """CLI entry point for testing."""
    import sys
    
    # Test consent workflow
    manager = UserConsentManager(
        project_name="TestProject",
        interactive=True
    )
    
    detected_info = {
        "language": "Python",
        "framework": "FastAPI",
        "files": 127,
        "estimated_time": "3-5 minutes"
    }
    
    result = manager.request_onboarding_consent(detected_info)
    
    print(f"\n{'='*70}")
    print(f"Consent Result:")
    print(f"  Action: {result.action.value}")
    print(f"  Approved: {', '.join(result.approved_steps)}")
    print(f"  Skipped: {', '.join(result.skipped_steps)}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
