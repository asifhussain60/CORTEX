"""
Onboarding Acknowledgment Orchestrator - Sprint 1 Day 3

Manages 3-step governance acknowledgment flow for first-time users.

FLOW STEPS:
1. Welcome & Introduction
   - Greet user
   - Explain CORTEX governance approach
   - Set expectations

2. Rulebook Display
   - Show key governance rules
   - Highlight protection layers
   - Provide examples

3. Explicit Acknowledgment
   - Request confirmation
   - Record acknowledgment
   - Complete onboarding

USAGE:
    from src.orchestrators.onboarding_acknowledgment_orchestrator import OnboardingAcknowledgmentOrchestrator
    
    orchestrator = OnboardingAcknowledgmentOrchestrator()
    
    # Check if user needs onboarding
    if orchestrator.needs_onboarding():
        # Start onboarding flow
        step1 = orchestrator.execute_step_1()
        # ... user proceeds through steps
        orchestrator.record_acknowledgment()

INTEGRATION:
- Called by UnifiedEntryPointOrchestrator for first-time users
- Skipped for returning users (acknowledged_rulebook=1)
- Works alongside WelcomeBannerAgent (banner is per-session, this is one-time)

SPRINT 1 DAY 3-4: First-Time Acknowledgment
Author: Asif Hussain (CORTEX Enhancement System)
Date: November 28, 2025
"""

import logging
from typing import Dict, Any, Optional
from enum import Enum

from src.tier1.user_profile_governance import UserProfileGovernance

logger = logging.getLogger(__name__)


class OnboardingStep(Enum):
    """Onboarding flow steps."""
    WELCOME = 1
    RULEBOOK = 2
    ACKNOWLEDGMENT = 3
    COMPLETE = 4


class OnboardingAcknowledgmentOrchestrator:
    """
    Orchestrates 3-step governance acknowledgment for first-time users.
    
    Features:
    - Progressive disclosure (3 steps)
    - User-paced progression
    - Persistent state tracking
    - Skip for returning users
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize onboarding orchestrator.
        
        Args:
            db_path: Optional custom database path
        """
        self.governance = UserProfileGovernance(db_path=db_path)
        self.current_step = OnboardingStep.WELCOME
        logger.info("OnboardingAcknowledgmentOrchestrator initialized")
    
    def needs_onboarding(self) -> bool:
        """
        Check if user needs to go through onboarding.
        
        Returns:
            True if user hasn't acknowledged rulebook, False otherwise
        """
        return not self.governance.has_acknowledged_rulebook()
    
    def get_onboarding_status(self) -> Dict[str, Any]:
        """
        Get detailed onboarding status for user.
        
        Returns:
            Dict with acknowledgment status and onboarding needs
        """
        return self.governance.get_acknowledgment_status()
    
    def execute_step_1_welcome(self) -> Dict[str, Any]:
        """
        Execute Step 1: Welcome & Introduction.
        
        Returns:
            Dict with welcome content and next step info
        """
        welcome_content = """
# 🧠 Welcome to CORTEX Enhancement System

## Your AI Coding Assistant with Governance

CORTEX is not just another AI assistant - it's a **governed, quality-enforced** development enhancement system.

### What Makes CORTEX Different?

✅ **Transparent Governance:** All operations follow documented rules
✅ **Quality Enforcement:** TDD, SOLID, security standards built-in
✅ **Brain Protection:** Your project knowledge is protected and validated
✅ **Rollback Safety:** Git checkpoints before risky operations
✅ **Compliance Tracking:** Real-time dashboard of rule adherence

### Why Governance Matters

Without governance:
- ❌ AI can make breaking changes without safety nets
- ❌ Code quality degrades over time
- ❌ Technical debt accumulates invisibly
- ❌ No audit trail or rollback mechanism

With CORTEX governance:
- ✅ Every change follows Definition of Ready/Done
- ✅ Automated testing and validation
- ✅ Safe experimentation with rollback points
- ✅ Clear compliance visibility

### What Happens Next?

You'll go through a quick 3-step onboarding:
1. **Welcome** (you are here)
2. **Rulebook Overview** - Key rules explained
3. **Acknowledgment** - Confirm understanding

**This takes 2-3 minutes and happens only once.**

---

**Ready to continue?** Say "next" or "continue" to see the rulebook.
"""
        
        self.current_step = OnboardingStep.RULEBOOK
        
        return {
            "step": 1,
            "title": "Welcome & Introduction",
            "content": welcome_content,
            "next_step": "rulebook",
            "progress": "1/3"
        }
    
    def execute_step_2_rulebook(self) -> Dict[str, Any]:
        """
        Execute Step 2: Rulebook Display.
        
        Returns:
            Dict with rulebook content and next step info
        """
        rulebook_content = """
# 📖 CORTEX Governance Rulebook (Overview)

## The 7 Core Protection Layers

### 1. Definition of Ready (DoR)
**Before starting any feature:**
- ✅ Requirements are clear and documented
- ✅ Acceptance criteria defined
- ✅ Technical approach validated
- ✅ No blockers present

### 2. Definition of Done (DoD)
**Before marking work complete:**
- ✅ Code complete and reviewed
- ✅ Unit tests written (≥80% coverage)
- ✅ Integration tests passing
- ✅ Documentation updated
- ✅ No regressions introduced

### 3. TDD Enforcement
**Test-Driven Development cycle:**
- 🔴 **RED:** Write failing test first
- 🟢 **GREEN:** Write minimal code to pass
- 🔵 **REFACTOR:** Improve design without breaking tests

### 4. Git Checkpoint System
**Before risky operations:**
- ✅ Automatic git checkpoint created
- ✅ Easy rollback if something breaks
- ✅ Safe experimentation encouraged

### 5. SOLID Principles
**Code design standards:**
- **S**ingle Responsibility
- **O**pen/Closed
- **L**iskov Substitution
- **I**nterface Segregation
- **D**ependency Inversion

### 6. Security Standards (OWASP)
**Security by design:**
- ✅ Input validation
- ✅ Authentication/Authorization
- ✅ Sensitive data protection
- ✅ Security scanning

### 7. Brain Integrity
**Your project knowledge:**
- ✅ Context validated before use
- ✅ Lessons learned captured
- ✅ Technical debt tracked
- ✅ Architecture decisions documented

## Quick Commands

| Command | Purpose |
|---------|---------|
| `show rules` | Display full rulebook |
| `compliance` | Check your compliance status |
| `dor` | View Definition of Ready checklist |
| `dod` | View Definition of Done checklist |
| `help` | See all available commands |

## What This Means for You

✅ **You can trust CORTEX** - Every operation is governed
✅ **You stay in control** - Rollback any time
✅ **Quality is built-in** - Not an afterthought
✅ **Compliance is visible** - Real-time dashboard

---

**Full Rulebook:** `cortex-brain/brain-protection-rules.yaml`

**Ready to acknowledge?** Say "acknowledge" or "I understand" to complete onboarding.
"""
        
        self.current_step = OnboardingStep.ACKNOWLEDGMENT
        
        return {
            "step": 2,
            "title": "Rulebook Overview",
            "content": rulebook_content,
            "next_step": "acknowledgment",
            "progress": "2/3"
        }
    
    def execute_step_3_acknowledgment(self) -> Dict[str, Any]:
        """
        Execute Step 3: Acknowledgment.
        
        This step requests explicit acknowledgment from the user.
        
        Returns:
            Dict with acknowledgment prompt and instructions
        """
        acknowledgment_content = """
# ✅ Acknowledgment & Completion

## Confirm Your Understanding

By acknowledging, you confirm that you:

1. ✅ Understand CORTEX operates under governance rules
2. ✅ Agree to follow Definition of Ready/Done workflows
3. ✅ Will use compliance dashboard for status tracking
4. ✅ Know how to access rulebook and help commands

## Your Rights

You always have the right to:
- 📖 Review rules any time: `show rules`
- 📊 Check compliance: `compliance`
- ❓ Ask questions: `help`
- 🔄 Request rollback: Git checkpoints are automatic

## Complete Onboarding

**To acknowledge and complete setup, say:**
- "I acknowledge"
- "I understand and agree"
- "acknowledged"
- "confirm"

---

**Need to review?**
- Say "back" to see rulebook again
- Say "show rules" for full documentation

**Once you acknowledge, you won't see this onboarding again.**  
(But you can always access the rulebook with `show rules`)
"""
        
        self.current_step = OnboardingStep.COMPLETE
        
        return {
            "step": 3,
            "title": "Acknowledgment & Completion",
            "content": acknowledgment_content,
            "next_step": "complete",
            "progress": "3/3"
        }
    
    def record_acknowledgment(self) -> Dict[str, Any]:
        """
        Record user's acknowledgment and complete onboarding.
        
        Returns:
            Dict with success status and completion message
        """
        success = self.governance.mark_rulebook_acknowledged()
        
        if success:
            self.governance.mark_onboarding_completed()
            
            completion_message = """
# 🎉 Onboarding Complete!

✅ **Governance acknowledgment recorded**
✅ **CORTEX is ready to assist you**

## What Happens Now?

- You won't see this onboarding again
- Welcome banner will appear once per session
- All governance rules are active
- Compliance dashboard is available

## Quick Start Commands

Try these commands to get started:
- `help` - See all available commands
- `compliance` - Check your current status
- `show rules` - Review governance rules
- `plan [feature]` - Start feature planning

## Need Help?

- Say `help` any time for command list
- Say `show rules` to review governance
- Say `compliance` to check rule adherence

**Welcome to governed AI development with CORTEX!** 🚀
"""
            
            return {
                "success": True,
                "message": "Onboarding completed successfully",
                "content": completion_message,
                "acknowledged_at": self.governance.get_acknowledgment_status()["acknowledged_at"]
            }
        else:
            return {
                "success": False,
                "message": "Failed to record acknowledgment",
                "error": "Database write failed"
            }
    
    def get_current_step(self) -> OnboardingStep:
        """
        Get the current onboarding step.
        
        Returns:
            OnboardingStep enum value
        """
        return self.current_step
    
    def reset_onboarding(self) -> bool:
        """
        Reset onboarding status (for testing or re-onboarding).
        
        Returns:
            True if successful, False otherwise
        """
        return self.governance.reset_acknowledgment()
