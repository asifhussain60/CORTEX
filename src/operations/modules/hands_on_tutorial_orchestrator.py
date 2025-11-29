"""
CORTEX Hands-On Tutorial Orchestrator

Interactive tutorial program that teaches users about CORTEX through
practical exercises covering planning, development, and testing.

Author: GitHub Copilot
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from enum import Enum


class TutorialProfile(Enum):
    """Tutorial difficulty profiles."""
    QUICK = "quick"
    STANDARD = "standard"
    COMPREHENSIVE = "comprehensive"


class ModuleStatus(Enum):
    """Module completion status."""
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    SKIPPED = "skipped"


@dataclass
class TutorialModule:
    """Tutorial module definition."""
    id: str
    name: str
    duration_min: int
    exercises: List[str]
    prerequisites: List[str]
    status: ModuleStatus = ModuleStatus.NOT_STARTED


@dataclass
class TutorialProgress:
    """User progress tracking."""
    session_id: str
    profile: TutorialProfile
    started_at: datetime
    completed_modules: List[str]
    current_module: Optional[str]
    total_time_min: int


class HandsOnTutorialOrchestrator:
    """
    Orchestrates interactive hands-on tutorial for CORTEX.
    
    Guides users through:
    1. CORTEX basics (help, context, healthcheck)
    2. Planning workflow (DoR, DoD, security review)
    3. TDD development (RED→GREEN→REFACTOR)
    4. Testing & validation (lint, session reports)
    """
    
    def __init__(self, cortex_root: Path = None):
        """Initialize tutorial orchestrator."""
        self.cortex_root = cortex_root or Path.cwd()
        self.tutorial_guide = self.cortex_root / ".github" / "prompts" / "modules" / "hands-on-tutorial-guide.md"
        self.progress_db = self.cortex_root / "cortex-brain" / "tier1" / "working_memory.db"
        
        self.modules = self._define_modules()
        
    def _define_modules(self) -> Dict[str, TutorialModule]:
        """Define tutorial modules."""
        return {
            "basics": TutorialModule(
                id="basics",
                name="CORTEX Basics",
                duration_min=5,
                exercises=[
                    "explore_capabilities",
                    "check_brain_memory",
                    "system_health_check"
                ],
                prerequisites=[]
            ),
            "planning": TutorialModule(
                id="planning",
                name="Planning Workflow",
                duration_min=7,
                exercises=[
                    "plan_authentication_feature",
                    "review_planning_document",
                    "approve_plan"
                ],
                prerequisites=["basics"]
            ),
            "ado_planning": TutorialModule(
                id="ado_planning",
                name="ADO Work Item Planning",
                duration_min=6,
                exercises=[
                    "create_ado_work_item",
                    "review_git_context",
                    "understand_quality_scoring",
                    "analyze_high_risk_files",
                    "review_sme_suggestions"
                ],
                prerequisites=["basics", "planning"]
            ),
            "tdd": TutorialModule(
                id="tdd",
                name="Development with TDD",
                duration_min=10,
                exercises=[
                    "start_tdd_workflow",
                    "discover_ui_elements",
                    "generate_tests",
                    "run_tests_red",
                    "implement_feature",
                    "run_tests_green",
                    "refactor",
                    "apply_refactoring",
                    "validate_refactoring",
                    "create_git_checkpoint"
                ],
                prerequisites=["basics", "planning"]
            ),
            "testing": TutorialModule(
                id="testing",
                name="Testing & Validation",
                duration_min=7,
                exercises=[
                    "validate_code_quality",
                    "complete_tdd_session",
                    "generate_feedback_report"
                ],
                prerequisites=["basics", "planning", "tdd"]
            )
        }
    
    def start_tutorial(self, profile: TutorialProfile = TutorialProfile.STANDARD) -> Dict[str, Any]:
        """
        Start hands-on tutorial with selected profile.
        
        Args:
            profile: Tutorial difficulty level
            
        Returns:
            Tutorial session info with first module instructions
        """
        session_id = f"tutorial-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # Calculate total duration based on profile
        duration_map = {
            TutorialProfile.QUICK: 15,
            TutorialProfile.STANDARD: 25,
            TutorialProfile.COMPREHENSIVE: 30
        }
        
        # Welcome message
        welcome = self._generate_welcome_message(profile, duration_map[profile])
        
        # Get first module
        first_module = self.modules["basics"]
        first_exercise = self._get_exercise_instructions(first_module.id, first_module.exercises[0])
        
        # Save progress
        progress = TutorialProgress(
            session_id=session_id,
            profile=profile,
            started_at=datetime.now(),
            completed_modules=[],
            current_module="basics",
            total_time_min=0
        )
        self._save_progress(progress)
        
        return {
            "session_id": session_id,
            "profile": profile.value,
            "duration_min": duration_map[profile],
            "welcome_message": welcome,
            "current_module": first_module.name,
            "current_exercise": first_exercise,
            "progress": "0%"
        }
    
    def _generate_welcome_message(self, profile: TutorialProfile, duration: int) -> str:
        """Generate welcome message based on profile."""
        messages = {
            TutorialProfile.QUICK: f"""
🎓 **CORTEX Hands-On Tutorial - Quick Start**

Welcome! You've chosen the {duration}-minute quick start tutorial.

**What You'll Learn:**
✅ Essential CORTEX commands
✅ Basic planning workflow
✅ Simple TDD cycle

**What You'll Build:**
🔐 User authentication feature (simplified)

**Time Commitment:** ~{duration} minutes

Let's begin with Module 1: CORTEX Basics!
            """,
            TutorialProfile.STANDARD: f"""
🎓 **CORTEX Hands-On Tutorial - Standard**

Welcome! You've chosen the {duration}-minute standard tutorial.

**What You'll Learn:**
✅ CORTEX core capabilities
✅ Complete planning workflow (DoR/DoD)
✅ Full TDD cycle (RED→GREEN→REFACTOR)
✅ Testing & validation

**What You'll Build:**
🔐 User authentication feature (complete)

**Time Commitment:** ~{duration} minutes

Let's begin with Module 1: CORTEX Basics!
            """,
            TutorialProfile.COMPREHENSIVE: f"""
🎓 **CORTEX Hands-On Tutorial - Comprehensive**

Welcome! You've chosen the {duration}-minute comprehensive tutorial.

**What You'll Learn:**
✅ Deep understanding of CORTEX architecture
✅ Advanced planning with security review (OWASP)
✅ Full TDD with performance optimization
✅ Production-ready testing & validation

**What You'll Build:**
🔐 User authentication feature (production-ready)

**Time Commitment:** ~{duration} minutes

Let's begin with Module 1: CORTEX Basics!
            """
        }
        
        return messages.get(profile, messages[TutorialProfile.STANDARD])
    
    def _get_exercise_instructions(self, module_id: str, exercise_id: str) -> Dict[str, Any]:
        """Get detailed instructions for specific exercise."""
        
        exercises = {
            "basics": {
                "explore_capabilities": {
                    "title": "Exercise 1.1: Explore CORTEX Capabilities",
                    "task": "Discover what CORTEX can do",
                    "commands": ["help"],
                    "expected_output": "Table of all available commands",
                    "understanding_check": [
                        "Can you find the planning command?",
                        "Can you find the TDD workflow command?",
                        "Can you find the feedback command?"
                    ],
                    "next_command": "Type 'help' to see all CORTEX commands"
                },
                "check_brain_memory": {
                    "title": "Exercise 1.2: Check CORTEX Brain Memory",
                    "task": "See what CORTEX remembers about your workspace",
                    "commands": ["show context"],
                    "expected_output": "Conversation history and context quality score",
                    "understanding_check": [
                        "What's your context quality score?",
                        "How many conversations loaded?",
                        "Is your memory health good?"
                    ],
                    "next_command": "Type 'show context' to see brain memory"
                },
                "system_health_check": {
                    "title": "Exercise 1.3: System Health Check",
                    "task": "Validate CORTEX is working correctly",
                    "commands": ["healthcheck"],
                    "expected_output": "System status (Healthy/Warning/Unhealthy)",
                    "understanding_check": [
                        "Is your CORTEX healthy?",
                        "Are all features available?",
                        "Any warnings to address?"
                    ],
                    "next_command": "Type 'healthcheck' to validate system"
                }
            },
            "planning": {
                "plan_authentication_feature": {
                    "title": "Exercise 2.1: Plan Authentication Feature",
                    "task": "Create a complete plan for user login feature",
                    "commands": ["plan user authentication"],
                    "scenario": """
You need to build a login page with:
- Email input field
- Password input field
- "Remember me" checkbox
- Submit button
- "Forgot password" link
                    """,
                    "questions": [
                        "What EXACTLY does this feature do?",
                        "Who are the SPECIFIC users?",
                        "What are the EXACT systems/APIs/databases?",
                        "What are the MEASURABLE limits?",
                        "How do we MEASURE success?",
                        "What files/services MUST exist?",
                        "What security risks exist?"
                    ],
                    "next_command": "Type 'plan user authentication' to start planning"
                },
                "review_planning_document": {
                    "title": "Exercise 2.2: Review Planning Document",
                    "task": "Open and review the generated plan",
                    "file_location": "cortex-brain/documents/planning/features/PLAN-*-authentication.md",
                    "what_to_look_for": [
                        "Phase breakdown (Foundation → Core → Validation)",
                        "Risk analysis section",
                        "Security hardening tasks",
                        "Task generation with acceptance criteria",
                        "Milestone-based implementation plan"
                    ],
                    "next_command": "Open the planning file in VS Code"
                },
                "approve_plan": {
                    "title": "Exercise 2.3: Approve Plan",
                    "task": "Approve the plan to move to implementation",
                    "commands": ["approve plan"],
                    "expected_output": "Plan approved and moved to approved/",
                    "next_command": "Type 'approve plan' to proceed"
                }
            },
            "ado_planning": {
                "create_ado_work_item": {
                    "title": "Exercise 3.1: Create ADO Work Item",
                    "task": "Create Azure DevOps work item with git history integration",
                    "commands": ["plan ado"],
                    "scenario": """
You need to fix a bug in the authentication system:
- File: `src/auth/login.py` (or equivalent in your repo)
- Issue: OAuth users cannot log in after session timeout
- Priority: High
- Type: Bug
                    """,
                    "expected_output": "Work item created with automatic git context enrichment",
                    "learning_objectives": [
                        "Understand work item types (Bug/Story/Task/Feature/Epic)",
                        "Learn priority system (1=High, 2=Medium, 3=Low)",
                        "See automatic file reference detection (backticks)",
                        "Experience Phase 1 git integration"
                    ],
                    "next_command": "Type 'plan ado' and describe the bug"
                },
                "review_git_context": {
                    "title": "Exercise 3.2: Review Git History Context",
                    "task": "Examine the Git History Context section in generated work item",
                    "file_location": "cortex-brain/documents/planning/ado/active/Bug-*.md",
                    "what_to_look_for": [
                        "Quality Score (0-100%) with label",
                        "High-Risk Files Detected section",
                        "SME Suggestions section",
                        "Contributors list with commit counts",
                        "Related Commits with messages"
                    ],
                    "understanding_check": [
                        "What is the quality score for this work item?",
                        "Are any files flagged as high-risk?",
                        "Who is the suggested SME?",
                        "How many contributors worked on related files?",
                        "What were the most recent related commits?"
                    ],
                    "next_command": "Open the generated ADO work item file in VS Code"
                },
                "understand_quality_scoring": {
                    "title": "Exercise 3.3: Understand Quality Scoring",
                    "task": "Learn how git history quality is calculated",
                    "concepts": [
                        "90-100% = Excellent (deep history, active contributors)",
                        "70-89% = Good (solid history, multiple contributors)",
                        "50-69% = Adequate (basic history, few contributors)",
                        "<50% = Weak (sparse or no history)"
                    ],
                    "scoring_factors": [
                        "Number of commits (30 points)",
                        "Number of contributors (25 points)",
                        "Recency of activity (20 points)",
                        "Security scan results (10 points)",
                        "Test coverage (15 points)"
                    ],
                    "real_example": """
For `src/auth/login.py`:
- Recent commits: 18 in 6 months → 30 points
- Contributors: 5 people → 25 points
- Recent activity: 12 days ago → 20 points
- Security scans: Pass → 10 points
- **Total: 85% (Good)**
                    """,
                    "next_command": "Review quality score in your work item"
                },
                "analyze_high_risk_files": {
                    "title": "Exercise 3.4: Analyze High-Risk Files",
                    "task": "Understand why files are flagged as high-risk",
                    "detection_criteria": [
                        "High Churn: >15 commits in 6 months",
                        "Hotfix Pattern: >3 emergency fixes",
                        "Recent Security Fix: <30 days ago",
                        "High Complexity: >500 lines or many dependencies"
                    ],
                    "what_happens": [
                        "Auto-added to acceptance criteria with ⚠️ warning",
                        "Detailed risk analysis in Git History Context",
                        "Recommended actions provided",
                        "SME assignment suggested"
                    ],
                    "example": """
**⚠️ High-Risk Files Detected:**
- `src/auth/login.py` - Requires extra attention
  - **Churn:** 18 commits (threshold: 15)
  - **Hotfixes:** 4 emergency patches (threshold: 3)
  - **Recent Security Fix:** 12 days ago (threshold: 30)

**Recommended Actions:**
- Assign to experienced developer (SME suggestion: John Doe)
- Require code review from 2+ people
- Add comprehensive test coverage
- Consider pair programming
                    """,
                    "understanding_check": [
                        "Why was this file flagged as high-risk?",
                        "What are the specific risk factors?",
                        "What actions are recommended?",
                        "Should this influence work assignment?"
                    ],
                    "next_command": "Review high-risk warnings in your work item"
                },
                "review_sme_suggestions": {
                    "title": "Exercise 3.5: Review SME Suggestions",
                    "task": "Learn how CORTEX identifies subject matter experts",
                    "identification_method": [
                        "Git shortlog analysis: git shortlog -sn -- file.py",
                        "Rank by commit count to specific files",
                        "Consider recency (recent contributors weighted higher)",
                        "Analyze related file expertise"
                    ],
                    "benefits": [
                        "Auto-suggests best person for assignment",
                        "Reduces assignment decision time",
                        "Improves code quality (expert handles complex areas)",
                        "Identifies who should review PR",
                        "Facilitates knowledge transfer"
                    ],
                    "example": """
**💡 Subject Matter Expert Suggestions:**
- **John Doe** (top contributor to authentication module)
  - 42 commits to `src/auth/login.py` (48% of total)
  - Author of recent security fixes
  - Recommended for work assignment

**Contributors to Related Files:**
- John Doe (42 commits) - Primary maintainer
- Jane Smith (28 commits) - Security specialist
- Bob Wilson (15 commits) - OAuth integration
- Alice Johnson (8 commits) - Testing
- Charlie Brown (5 commits) - Documentation
                    """,
                    "understanding_check": [
                        "Who is the suggested SME for this work item?",
                        "Why was this person recommended?",
                        "Who else contributed to related files?",
                        "Who should review the PR?"
                    ],
                    "next_steps": [
                        "Assign work item to suggested SME",
                        "Tag backup SME for code review",
                        "Consult specialized contributors as needed"
                    ],
                    "next_command": "Review SME suggestions in your work item"
                }
            },
            "tdd": {
                "start_tdd_workflow": {
                    "title": "Exercise 3.1: Start TDD Workflow",
                    "task": "Initialize TDD session for authentication feature",
                    "commands": ["start tdd workflow for user authentication"],
                    "expected_output": "Workspace discovered, test framework detected, RED state ready",
                    "next_command": "Type 'start tdd workflow for user authentication'"
                },
                "discover_ui_elements": {
                    "title": "Exercise 3.2: Discover UI Elements",
                    "task": "Auto-discover element IDs before writing tests",
                    "commands": ["discover views in src/Views/Account/Login.cshtml"],
                    "expected_output": "5 elements found with selectors generated",
                    "time_saved": "60+ minutes → <5 minutes",
                    "next_command": "Type 'discover views in [your-login-file]'"
                },
                "generate_tests": {
                    "title": "Exercise 3.3: Generate Tests (RED Phase)",
                    "task": "Create failing tests for login functionality",
                    "commands": ["generate tests for login validation"],
                    "expected_output": "6 tests generated using real element IDs",
                    "next_command": "Type 'generate tests for login validation'"
                },
                "run_tests_red": {
                    "title": "Exercise 3.4: Run Tests (RED State)",
                    "task": "Execute tests to confirm RED state",
                    "commands": ["run tests"],
                    "expected_output": "All tests fail (expected), auto-debug started",
                    "next_command": "Type 'run tests' to execute"
                },
                "implement_feature": {
                    "title": "Exercise 3.5: Implement Feature (GREEN Phase)",
                    "task": "Write code to pass tests",
                    "files_to_create": [
                        "Controllers/AuthController.cs",
                        "Services/AuthenticationService.cs"
                    ],
                    "next_command": "Implement authentication logic in your code editor"
                },
                "run_tests_green": {
                    "title": "Exercise 3.6: Run Tests (GREEN State)",
                    "task": "Verify tests pass after implementation",
                    "commands": ["run tests"],
                    "expected_output": "All tests pass, performance data captured",
                    "next_command": "Type 'run tests' to verify GREEN state"
                },
                "refactor": {
                    "title": "Exercise 3.7: Get Refactoring Suggestions",
                    "task": "Get performance-based refactoring recommendations",
                    "commands": ["suggest refactorings"],
                    "expected_output": "3 performance issues detected with solutions",
                    "next_command": "Type 'suggest refactorings' to see recommendations"
                },
                "apply_refactoring": {
                    "title": "Exercise 3.8: Apply Refactoring",
                    "task": "Implement suggested improvements (add caching)",
                    "next_command": "Add MemoryCache to AuthenticationService"
                },
                "validate_refactoring": {
                    "title": "Exercise 3.9: Validate Refactoring",
                    "task": "Run tests to ensure refactoring didn't break anything",
                    "commands": ["run tests"],
                    "expected_output": "Tests pass, 67% performance improvement",
                    "next_command": "Type 'run tests' to validate"
                },
                "create_git_checkpoint": {
                    "title": "Exercise 3.10: Create Git Checkpoint",
                    "task": "Save your work with SKULL Rule #8 compliance",
                    "commands": ["git checkpoint"],
                    "expected_output": "Checkpoint created, work state preserved",
                    "next_command": "Type 'git checkpoint' to save progress"
                }
            },
            "testing": {
                "validate_code_quality": {
                    "title": "Exercise 4.1: Validate Code Quality",
                    "task": "Run lint validation before completion",
                    "commands": ["validate lint"],
                    "expected_output": "No critical violations, ready for completion",
                    "next_command": "Type 'validate lint' to check quality"
                },
                "complete_tdd_session": {
                    "title": "Exercise 4.2: Complete TDD Session",
                    "task": "Generate session completion report",
                    "commands": ["complete session"],
                    "expected_output": "Before/after metrics, accomplishments listed",
                    "next_command": "Type 'complete session' to generate report"
                },
                "generate_feedback_report": {
                    "title": "Exercise 4.3: Generate Feedback Report",
                    "task": "Share performance metrics with team",
                    "commands": ["generate feedback report"],
                    "expected_output": "8-category metrics, uploaded to GitHub Gist",
                    "next_command": "Type 'generate feedback report' to share"
                }
            }
        }
        
        return exercises.get(module_id, {}).get(exercise_id, {
            "title": "Exercise Not Found",
            "task": "Unknown exercise",
            "next_command": "Contact support"
        })
    
    def next_exercise(self, session_id: str) -> Dict[str, Any]:
        """Move to next exercise in tutorial."""
        progress = self._load_progress(session_id)
        
        if not progress:
            return {"error": "Session not found"}
        
        # Get current module
        current_module = self.modules[progress.current_module]
        
        # Find next exercise or module
        # Implementation would track exercise progress
        
        return {
            "session_id": session_id,
            "next_exercise": "Implementation needed"
        }
    
    def get_progress(self, session_id: str) -> Dict[str, Any]:
        """Get current tutorial progress."""
        progress = self._load_progress(session_id)
        
        if not progress:
            return {"error": "Session not found"}
        
        total_modules = len(self.modules)
        completed = len(progress.completed_modules)
        progress_pct = int((completed / total_modules) * 100)
        
        return {
            "session_id": session_id,
            "profile": progress.profile.value,
            "progress_percentage": progress_pct,
            "completed_modules": progress.completed_modules,
            "current_module": progress.current_module,
            "time_spent_min": progress.total_time_min
        }
    
    def _save_progress(self, progress: TutorialProgress):
        """Save tutorial progress to database."""
        # Implementation would use SQLite database
        pass
    
    def _load_progress(self, session_id: str) -> Optional[TutorialProgress]:
        """Load tutorial progress from database."""
        # Implementation would use SQLite database
        return None


def main():
    """CLI entry point for tutorial orchestrator."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="🎓 CORTEX Hands-On Tutorial - Interactive Learning"
    )
    
    parser.add_argument(
        "--profile",
        type=str,
        choices=["quick", "standard", "comprehensive"],
        default="standard",
        help="Tutorial difficulty profile"
    )
    
    parser.add_argument(
        "--session",
        type=str,
        help="Resume existing session"
    )
    
    args = parser.parse_args()
    
    orchestrator = HandsOnTutorialOrchestrator()
    
    if args.session:
        # Resume session
        progress = orchestrator.get_progress(args.session)
        print(json.dumps(progress, indent=2))
    else:
        # Start new session
        profile = TutorialProfile(args.profile)
        result = orchestrator.start_tutorial(profile)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
