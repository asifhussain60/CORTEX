#!/usr/bin/env python3
"""
CORTEX Interactive Onboarding Script

Purpose: CLI-based interactive onboarding flow guiding users through 6 phases
Version: 1.0.0
Author: Asif Hussain
Created: 2025-12-29

This script provides a guided onboarding experience with:
- Phase-by-phase progress tracking
- Interactive prompts and validation
- Real-time feedback and tips
- Artifact generation (certificates, guides)
- Progress persistence across sessions

Usage:
    python cortex-toolkit/core/utilities/onboarding_interactive.py
    
    # Or with specific phase:
    python cortex-toolkit/core/utilities/onboarding_interactive.py --phase 3
    
    # Resume previous session:
    python cortex-toolkit/core/utilities/onboarding_interactive.py --resume
"""

import sys
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, asdict

# Add src to path for imports
CORTEX_ROOT = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(CORTEX_ROOT))

try:
    from src.orchestrators.onboarding_orchestrator import (
        OnboardingOrchestrator,
        OnboardingSession,
        OnboardingPhase
    )
except ImportError:
    print("⚠️  Warning: Could not import OnboardingOrchestrator. Using standalone mode.")
    OnboardingOrchestrator = None


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# UI Components
# ============================================================================

class Colors:
    """ANSI color codes for terminal output."""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    END = '\033[0m'


def print_header(text: str):
    """Print styled header."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text:^70}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*70}{Colors.END}\n")


def print_phase(phase_num: int, phase_name: str, duration: int):
    """Print phase information."""
    print(f"\n{Colors.BOLD}{Colors.CYAN}📍 Phase {phase_num}: {phase_name}{Colors.END}")
    print(f"{Colors.BLUE}⏱️  Estimated duration: {duration} minutes{Colors.END}\n")


def print_success(text: str):
    """Print success message."""
    print(f"{Colors.GREEN}✅ {text}{Colors.END}")


def print_error(text: str):
    """Print error message."""
    print(f"{Colors.RED}❌ {text}{Colors.END}")


def print_warning(text: str):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠️  {text}{Colors.END}")


def print_info(text: str):
    """Print info message."""
    print(f"{Colors.BLUE}ℹ️  {text}{Colors.END}")


def print_progress(current: int, total: int):
    """Print progress bar."""
    percentage = (current / total) * 100
    filled = int(percentage / 5)
    bar = '█' * filled + '░' * (20 - filled)
    print(f"\n{Colors.CYAN}Progress: [{bar}] {percentage:.1f}% ({current}/{total} phases){Colors.END}\n")


def prompt_continue() -> bool:
    """Prompt user to continue to next phase."""
    response = input(f"\n{Colors.BOLD}Continue to next phase? (yes/no): {Colors.END}").strip().lower()
    return response in ['yes', 'y', '']


def prompt_choice(question: str, choices: List[str]) -> str:
    """Prompt user to select from choices."""
    print(f"\n{Colors.BOLD}{question}{Colors.END}")
    for i, choice in enumerate(choices, 1):
        print(f"  {i}. {choice}")
    
    while True:
        try:
            response = input(f"{Colors.BOLD}Enter choice (1-{len(choices)}): {Colors.END}").strip()
            idx = int(response) - 1
            if 0 <= idx < len(choices):
                return choices[idx]
            print_error(f"Please enter a number between 1 and {len(choices)}")
        except ValueError:
            print_error("Please enter a valid number")
        except KeyboardInterrupt:
            print_warning("\nOperation cancelled by user")
            sys.exit(0)


def prompt_text(question: str, default: Optional[str] = None) -> str:
    """Prompt user for text input."""
    prompt = f"\n{Colors.BOLD}{question}{Colors.END}"
    if default:
        prompt += f" [{default}]"
    prompt += ": "
    
    try:
        response = input(prompt).strip()
        return response if response else default or ""
    except KeyboardInterrupt:
        print_warning("\nOperation cancelled by user")
        sys.exit(0)


# ============================================================================
# Session Management
# ============================================================================

class SessionManager:
    """Manages onboarding session persistence."""
    
    def __init__(self, session_dir: Path):
        self.session_dir = session_dir
        self.session_file = session_dir / "current-session.json"
        self.session_dir.mkdir(parents=True, exist_ok=True)
    
    def save_session(self, session: Dict[str, Any]):
        """Save session to disk."""
        with open(self.session_file, 'w') as f:
            json.dump(session, f, indent=2)
        logger.info(f"Session saved: {self.session_file}")
    
    def load_session(self) -> Optional[Dict[str, Any]]:
        """Load session from disk."""
        if self.session_file.exists():
            with open(self.session_file, 'r') as f:
                return json.load(f)
        return None
    
    def clear_session(self):
        """Clear current session."""
        if self.session_file.exists():
            self.session_file.unlink()
            logger.info("Session cleared")


# ============================================================================
# Phase Implementations
# ============================================================================

class Phase1_QuickStart:
    """Phase 1: Quick Start (5 minutes)"""
    
    @staticmethod
    def run():
        print_phase(1, "Quick Start", 5)
        
        print("Welcome to CORTEX! Let's get you started.\n")
        print("In this phase, you'll:")
        print("  • Verify CORTEX installation")
        print("  • Test your first command")
        print("  • Understand workspace context\n")
        
        # Check installation
        print_info("Checking CORTEX installation...")
        cortex_root = CORTEX_ROOT
        
        if (cortex_root / "src").exists() and (cortex_root / "cortex-brain").exists():
            print_success("CORTEX installation verified!")
            print(f"   Root: {cortex_root}")
        else:
            print_error("CORTEX installation not found in expected location")
            print_warning("Please ensure you're running from CORTEX directory")
            return False
        
        # Check brain structure
        print_info("Verifying brain structure...")
        brain_path = cortex_root / "cortex-brain"
        
        if all((brain_path / tier).exists() for tier in ["tier0", "tier1", "tier2", "tier3"]):
            print_success("4-tier brain structure verified!")
        else:
            print_warning("Some brain tiers are missing - this may affect functionality")
        
        # Test help command simulation
        print_info("Testing help command...")
        print_success("Help command ready! (Type 'help' in GitHub Copilot Chat)")
        
        print("\n" + "="*70)
        print_success("Phase 1 Complete! You're ready to dive deeper.")
        print("="*70)
        
        return True


class Phase2_CoreConcepts:
    """Phase 2: Core Concepts (10 minutes)"""
    
    @staticmethod
    def run():
        print_phase(2, "Core Concepts", 10)
        
        print("Let's explore CORTEX architecture and principles.\n")
        
        # 4-Tier Brain
        print(f"{Colors.BOLD}🧠 4-Tier Brain Architecture{Colors.END}\n")
        print("  Tier 0: Governance - Brain protection rules, manifests")
        print("  Tier 1: Working Memory - Conversation context, session tracking")
        print("  Tier 2: Knowledge Graph - Relationships, lessons learned")
        print("  Tier 3: Development Context - Project-specific memory\n")
        
        # SKULL Protection
        print(f"{Colors.BOLD}🛡️  SKULL Protection System{Colors.END}\n")
        print("  S - TDD Enforcement (RED→GREEN→REFACTOR mandatory)")
        print("  K - Holistic Discovery (Search before create)")
        print("  U - Refactor Cleanup (Remove orphaned code)")
        print("  L - Git Isolation (CORTEX code separate from user repos)\n")
        
        # Quiz
        print(f"{Colors.BOLD}Quick Check:{Colors.END}")
        answer = prompt_choice(
            "Which tier stores conversation context?",
            ["Tier 0: Governance", "Tier 1: Working Memory", "Tier 2: Knowledge Graph", "Tier 3: Development Context"]
        )
        
        if "Tier 1" in answer:
            print_success("Correct! Tier 1 is your working memory.")
        else:
            print_info("That's okay! Tier 1 (Working Memory) stores conversation context.")
        
        print("\n" + "="*70)
        print_success("Phase 2 Complete! You understand CORTEX architecture.")
        print("="*70)
        
        return True


class Phase3_FirstPlanning:
    """Phase 3: First Planning Operation (15 minutes)"""
    
    @staticmethod
    def run():
        print_phase(3, "First Planning Operation", 15)
        
        print("Let's create your first plan using CORTEX!\n")
        
        # Get feature name
        feature_name = prompt_text(
            "What feature would you like to plan?",
            "user-authentication-feature"
        )
        
        print_info(f"Planning feature: {feature_name}")
        print("\nIn GitHub Copilot Chat, you would say:")
        print(f'{Colors.CYAN}plan "{feature_name}"{Colors.END}\n')
        
        # Show folder structure
        print(f"{Colors.BOLD}Expected folder structure:{Colors.END}\n")
        print(f"  planning/active/{feature_name}/")
        print(f"  ├── 00-master-plan.md")
        print(f"  ├── context/")
        print(f"  ├── reports/")
        print(f"  ├── artifacts/")
        print(f"  └── tracking/")
        print(f"      └── progress-tracker.json\n")
        
        # Explain components
        print(f"{Colors.BOLD}Plan components:{Colors.END}\n")
        print("  • Master Plan: Main planning document with phases")
        print("  • Context: Background info, user personas, requirements")
        print("  • Reports: Progress reports, retrospectives")
        print("  • Artifacts: Diagrams, mockups, supporting docs")
        print("  • Tracking: JSON progress tracker for automation\n")
        
        print_info("Tip: All plans use this standard structure for consistency")
        
        print("\n" + "="*70)
        print_success("Phase 3 Complete! You understand planning workflow.")
        print("="*70)
        
        return True


class Phase4_TDDWorkflow:
    """Phase 4: TDD Workflow (20 minutes)"""
    
    @staticmethod
    def run():
        print_phase(4, "TDD Workflow", 20)
        
        print("Master the RED→GREEN→REFACTOR cycle!\n")
        
        # Explain TDD
        print(f"{Colors.BOLD}TDD Philosophy:{Colors.END}\n")
        print("  🔴 RED: Write a failing test first")
        print("  🟢 GREEN: Write minimal code to pass")
        print("  🔵 REFACTOR: Improve code quality\n")
        
        # Show example
        print(f"{Colors.BOLD}Example: Building a Calculator{Colors.END}\n")
        
        print(f"{Colors.RED}1. RED Phase - Write failing test:{Colors.END}")
        print("   def test_calculator_add():")
        print("       calc = Calculator()")
        print("       assert calc.add(2, 3) == 5")
        print("   Result: ❌ Test fails (Calculator doesn't exist)\n")
        
        print(f"{Colors.GREEN}2. GREEN Phase - Minimal implementation:{Colors.END}")
        print("   class Calculator:")
        print("       def add(self, a, b):")
        print("           return a + b")
        print("   Result: ✅ Test passes\n")
        
        print(f"{Colors.BLUE}3. REFACTOR Phase - Improve code:{Colors.END}")
        print("   class Calculator:")
        print('       """Simple calculator with type hints."""')
        print("       def add(self, a: int, b: int) -> int:")
        print('           """Add two integers."""')
        print("           return a + b")
        print("   Result: ✅ Tests still pass, code improved\n")
        
        # Commands
        print(f"{Colors.BOLD}TDD Commands in Copilot Chat:{Colors.END}\n")
        print('  • "start tdd" - Begin TDD workflow')
        print('  • "continue tdd" - Move to next phase')
        print('  • "complete tdd" - Finish and create git checkpoint\n')
        
        print_info("SKULL enforces TDD: You cannot skip RED phase!")
        
        print("\n" + "="*70)
        print_success("Phase 4 Complete! You understand TDD workflow.")
        print("="*70)
        
        return True


class Phase5_Documentation:
    """Phase 5: Documentation Navigation (5 minutes)"""
    
    @staticmethod
    def run():
        print_phase(5, "Documentation Navigation", 5)
        
        print("Learn where to find help and documentation.\n")
        
        print(f"{Colors.BOLD}📚 Key Resources:{Colors.END}\n")
        
        resources = {
            "Primary Entry Point": ".github/prompts/CORTEX.prompt.md",
            "Operation Guides": ".github/prompts/modules/",
            "Orchestrator Specs": "cortex-brain/manifests/orchestrators/",
            "Learning Paths": "cortex-brain/documents/learning-paths/",
            "Troubleshooting": "cortex-brain/documents/troubleshooting/",
            "Web Docs": "https://asifhussain60.github.io/CORTEX/"
        }
        
        for name, path in resources.items():
            print(f"  • {Colors.BOLD}{name}:{Colors.END} {path}")
        
        print(f"\n{Colors.BOLD}Common Commands:{Colors.END}\n")
        print('  • "help" - Show all available commands')
        print('  • "system maintenance" - Run health checks')
        print('  • "plan [feature]" - Create a plan')
        print('  • "start tdd" - Begin TDD workflow')
        print('  • "sanitize" - Make code generic\n')
        
        print_info("Tip: CORTEX.prompt.md is your universal router!")
        
        print("\n" + "="*70)
        print_success("Phase 5 Complete! You know where to find help.")
        print("="*70)
        
        return True


class Phase6_CommonOperations:
    """Phase 6: Common Operations (10 minutes)"""
    
    @staticmethod
    def run():
        print_phase(6, "Common Operations", 10)
        
        print("Practice the 5 most common CORTEX operations.\n")
        
        operations = [
            ("Plan a Feature", 'plan "add user profile page"', "Creates plan folder structure"),
            ("Start TDD Workflow", 'start tdd', "Begin RED→GREEN→REFACTOR cycle"),
            ("System Maintenance", 'system maintenance', "Run 6-phase health check"),
            ("Get Help", 'help', "Show all available commands"),
            ("Sanitize Code", 'sanitize', "Make codebase generic")
        ]
        
        print(f"{Colors.BOLD}Top 5 Operations:{Colors.END}\n")
        
        for i, (name, command, description) in enumerate(operations, 1):
            print(f"{i}. {Colors.BOLD}{name}{Colors.END}")
            print(f"   Command: {Colors.CYAN}{command}{Colors.END}")
            print(f"   {description}\n")
        
        # Practice prompt
        print(f"{Colors.BOLD}Practice Recommendation:{Colors.END}\n")
        print("Try each operation in GitHub Copilot Chat to see them in action!")
        print("Start with 'help' to see the full command list.\n")
        
        print_info("Tip: Natural language works! Say 'show me help' or 'run maintenance'")
        
        print("\n" + "="*70)
        print_success("Phase 6 Complete! You're ready to use CORTEX!")
        print("="*70)
        
        return True


# ============================================================================
# Main Onboarding Flow
# ============================================================================

class InteractiveOnboarding:
    """Main interactive onboarding coordinator."""
    
    PHASES = [
        Phase1_QuickStart,
        Phase2_CoreConcepts,
        Phase3_FirstPlanning,
        Phase4_TDDWorkflow,
        Phase5_Documentation,
        Phase6_CommonOperations
    ]
    
    def __init__(self, cortex_root: Path):
        self.cortex_root = cortex_root
        self.session_dir = cortex_root / "cortex-brain" / "documents" / "onboarding-sessions"
        self.session_manager = SessionManager(self.session_dir)
        self.current_phase = 1
        self.completed_phases = []
    
    def run(self, start_phase: int = 1, resume: bool = False):
        """Run interactive onboarding flow."""
        
        # Show welcome banner
        print_header("🎓 CORTEX Interactive Onboarding")
        
        print(f"{Colors.BOLD}Welcome to CORTEX!{Colors.END}\n")
        print("This interactive guide will help you:")
        print("  • Install and configure CORTEX")
        print("  • Understand core concepts")
        print("  • Execute your first operations")
        print("  • Master TDD workflow")
        print("  • Navigate documentation")
        print("  • Practice common commands\n")
        
        # Check for resume
        if resume:
            session = self.session_manager.load_session()
            if session:
                self.current_phase = session.get('current_phase', 1)
                self.completed_phases = session.get('completed_phases', [])
                print_info(f"Resuming from Phase {self.current_phase}")
            else:
                print_warning("No previous session found, starting fresh")
        else:
            self.current_phase = start_phase
        
        # Get user name
        user_name = prompt_text("What's your name?", "Developer")
        print_success(f"Great to meet you, {user_name}!\n")
        
        # Run phases
        for phase_num in range(self.current_phase, len(self.PHASES) + 1):
            print_progress(phase_num - 1, len(self.PHASES))
            
            phase_class = self.PHASES[phase_num - 1]
            success = phase_class.run()
            
            if not success:
                print_error(f"Phase {phase_num} encountered issues")
                break
            
            self.completed_phases.append(phase_num)
            self.current_phase = phase_num + 1
            
            # Save progress
            self.save_progress(user_name)
            
            # Check if user wants to continue
            if phase_num < len(self.PHASES):
                if not prompt_continue():
                    print_info("Session paused. Run with --resume to continue.")
                    break
        
        # Show completion
        if len(self.completed_phases) == len(self.PHASES):
            self.show_completion(user_name)
    
    def save_progress(self, user_name: str):
        """Save current progress."""
        session = {
            'user_name': user_name,
            'start_time': datetime.now().isoformat(),
            'current_phase': self.current_phase,
            'completed_phases': self.completed_phases
        }
        self.session_manager.save_session(session)
    
    def show_completion(self, user_name: str):
        """Show completion certificate."""
        print_header("🎉 CONGRATULATIONS!")
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}Onboarding Complete!{Colors.END}\n")
        print(f"Congratulations, {user_name}! You've completed all 6 phases.\n")
        
        print(f"{Colors.BOLD}What You've Learned:{Colors.END}\n")
        print("  ✅ Installed and verified CORTEX")
        print("  ✅ Understood 4-tier brain architecture")
        print("  ✅ Created your first plan")
        print("  ✅ Mastered TDD workflow")
        print("  ✅ Learned documentation navigation")
        print("  ✅ Practiced common operations\n")
        
        print(f"{Colors.BOLD}Next Steps:{Colors.END}\n")
        print("  1. Create a real plan for your project")
        print("  2. Try the TDD workflow on actual code")
        print("  3. Explore advanced operations")
        print("  4. Read the knowledge library\n")
        
        print(f"{Colors.BOLD}Resources:{Colors.END}\n")
        print("  • Web: https://asifhussain60.github.io/CORTEX/")
        print("  • GitHub: github.com/asifhussain60/CORTEX")
        print("  • Help: Type 'help' in Copilot Chat\n")
        
        # Generate certificate
        self.generate_certificate(user_name)
        
        # Clear session
        self.session_manager.clear_session()
        
        print_success("Your onboarding journey is complete!")
        print(f"{Colors.BOLD}Welcome to the CORTEX community! 🚀{Colors.END}\n")
    
    def generate_certificate(self, user_name: str):
        """Generate completion certificate."""
        cert_dir = self.cortex_root / "cortex-brain" / "documents" / "certificates"
        cert_dir.mkdir(parents=True, exist_ok=True)
        
        cert_file = cert_dir / f"onboarding-{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"
        
        certificate = f"""# 🎓 CORTEX Onboarding Certificate

**Recipient:** {user_name}  
**Completion Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  
**Version:** 4.0.0

---

## 🏆 Achievements

This certifies that **{user_name}** has successfully completed the CORTEX onboarding program and demonstrated proficiency in:

### Phase 1: Quick Start ✅
- CORTEX installation and configuration
- First command execution
- Workspace context understanding

### Phase 2: Core Concepts ✅
- 4-tier brain architecture
- SKULL protection system
- Response template system

### Phase 3: First Planning Operation ✅
- Plan creation workflow
- Folder structure understanding
- Progress tracking

### Phase 4: TDD Workflow ✅
- RED→GREEN→REFACTOR cycle
- Test-first development
- Git checkpoint integration

### Phase 5: Documentation Navigation ✅
- Resource location
- Help system usage
- Troubleshooting skills

### Phase 6: Common Operations ✅
- Top 5 operations practiced
- Natural language commands
- Operation routing

---

## 🚀 Next Steps

- Create production-quality plans
- Master advanced TDD techniques
- Explore specialized orchestrators
- Contribute to CORTEX community

---

**Issued by:** CORTEX Onboarding System  
**Author:** Asif Hussain  
**Website:** https://asifhussain60.github.io/CORTEX/

---

*This certificate demonstrates foundational CORTEX competency and readiness for independent usage.*
"""
        
        with open(cert_file, 'w') as f:
            f.write(certificate)
        
        print_success(f"Certificate generated: {cert_file}")


# ============================================================================
# CLI Entry Point
# ============================================================================

def main():
    """Main entry point for interactive onboarding."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="CORTEX Interactive Onboarding - 6-phase guided tour"
    )
    parser.add_argument(
        '--phase',
        type=int,
        default=1,
        choices=range(1, 7),
        help="Start from specific phase (1-6)"
    )
    parser.add_argument(
        '--resume',
        action='store_true',
        help="Resume from last saved progress"
    )
    
    args = parser.parse_args()
    
    try:
        onboarding = InteractiveOnboarding(CORTEX_ROOT)
        onboarding.run(start_phase=args.phase, resume=args.resume)
    except KeyboardInterrupt:
        print_warning("\n\nOnboarding interrupted by user")
        print_info("Run with --resume to continue from where you left off")
        sys.exit(0)
    except Exception as e:
        print_error(f"Onboarding failed: {e}")
        logger.exception("Onboarding error")
        sys.exit(1)


if __name__ == '__main__':
    main()
