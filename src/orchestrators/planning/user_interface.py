"""
CORTEX Planning Orchestrator - User Interface Bridge

Purpose: Provides interactive UI components for human-in-loop planning workflows
Version: 1.0.0
Author: CORTEX Development Team
Created: 2025-12-29 (Interactive Workflow Wiring - Maintenance Phase 1.5)

This module bridges the gap between interactive_session.py (state machine) and 
user interaction, providing:
- Question prompts with validation
- Multiple choice selections
- Progress indicators
- Approval workflows
- Rich formatting for terminal output

Architecture Pattern:
- Component 5 of 6-component interactive wiring pattern
- Integrates with: interactive_session.py, planning_orchestrator.py
- Implements: User input/output abstraction layer
"""

import logging
import sys
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional, Callable

logger = logging.getLogger(__name__)


def _safe_print(text: str) -> None:
    """
    Print text safely handling Unicode encoding issues on Windows.
    
    Falls back to ASCII-compatible characters if encoding fails.
    """
    try:
        print(text)
    except UnicodeEncodeError:
        # Replace common Unicode symbols with ASCII equivalents
        ascii_text = text
        replacements = {
            '✅': '[OK]',
            '❌': '[X]',
            '⚠️': '[!]',
            '❓': '[?]',
            '📋': '[#]',
            '🔍': '[*]',
            '📁': '[D]',
            '🎉': '[!]',
        }
        for unicode_char, ascii_char in replacements.items():
            ascii_text = ascii_text.replace(unicode_char, ascii_char)
        try:
            print(ascii_text)
        except UnicodeEncodeError:
            # Ultimate fallback: encode with errors='replace'
            print(ascii_text.encode('ascii', 'replace').decode('ascii'))


class PromptType(Enum):
    """Types of user prompts."""
    TEXT = "text"           # Free-form text input
    CHOICE = "choice"       # Single selection from list
    MULTI_CHOICE = "multi"  # Multiple selections from list
    CONFIRM = "confirm"     # Yes/No confirmation
    RATING = "rating"       # Numeric rating (1-5)


@dataclass
class PromptResult:
    """Result from user interaction."""
    prompt_type: PromptType
    value: Any
    raw_input: str
    valid: bool = True
    error_message: Optional[str] = None


class PlanningUI:
    """
    User interface bridge for interactive planning sessions.
    
    Provides methods for:
    - Asking questions with validation
    - Presenting choices
    - Displaying progress
    - Formatting output
    - Handling errors gracefully
    """
    
    def __init__(self, colorize: bool = True, verbose: bool = True):
        """
        Initialize UI bridge.
        
        Args:
            colorize: Enable ANSI color codes for terminal output
            verbose: Show detailed progress messages
        """
        self.colorize = colorize and sys.stdout.isatty()
        self.verbose = verbose
        self.logger = logging.getLogger(__name__)
    
    def prompt_text(
        self,
        question: str,
        default: Optional[str] = None,
        validator: Optional[Callable[[str], bool]] = None,
        help_text: Optional[str] = None
    ) -> PromptResult:
        """
        Prompt user for free-form text input.
        
        Args:
            question: Question to ask user
            default: Default value if user presses Enter
            validator: Optional validation function returning True if valid
            help_text: Optional help text shown before prompt
        
        Returns:
            PromptResult with user's text input
        """
        if help_text:
            self._print_info(help_text)
        
        prompt = self._format_question(question)
        if default:
            prompt += f" [default: {default}]"
        prompt += ": "
        
        while True:
            try:
                user_input = input(prompt).strip()
                
                # Use default if empty
                if not user_input and default:
                    user_input = default
                
                # Validate
                if validator and not validator(user_input):
                    self._print_error("Invalid input. Please try again.")
                    continue
                
                return PromptResult(
                    prompt_type=PromptType.TEXT,
                    value=user_input,
                    raw_input=user_input,
                    valid=True
                )
            except (KeyboardInterrupt, EOFError):
                self._print_warning("\nInput cancelled by user")
                return PromptResult(
                    prompt_type=PromptType.TEXT,
                    value=None,
                    raw_input="",
                    valid=False,
                    error_message="User cancelled input"
                )
    
    def prompt_choice(
        self,
        question: str,
        choices: List[str],
        default_index: Optional[int] = None,
        help_text: Optional[str] = None
    ) -> PromptResult:
        """
        Prompt user to select one option from a list.
        
        Args:
            question: Question to ask user
            choices: List of choice strings
            default_index: Index of default choice (0-based)
            help_text: Optional help text shown before prompt
        
        Returns:
            PromptResult with selected choice
        """
        if help_text:
            self._print_info(help_text)
        
        # Display choices
        self._print_header(question)
        for i, choice in enumerate(choices, 1):
            default_marker = " (default)" if default_index is not None and i - 1 == default_index else ""
            print(f"  {i}. {choice}{default_marker}")
        
        prompt = "Enter choice number"
        if default_index is not None:
            prompt += f" [default: {default_index + 1}]"
        prompt += ": "
        
        while True:
            try:
                user_input = input(prompt).strip()
                
                # Use default if empty
                if not user_input and default_index is not None:
                    choice_index = default_index
                else:
                    try:
                        choice_num = int(user_input)
                        if choice_num < 1 or choice_num > len(choices):
                            self._print_error(f"Please enter a number between 1 and {len(choices)}")
                            continue
                        choice_index = choice_num - 1
                    except ValueError:
                        self._print_error("Please enter a valid number")
                        continue
                
                selected_choice = choices[choice_index]
                self._print_success(f"Selected: {selected_choice}")
                
                return PromptResult(
                    prompt_type=PromptType.CHOICE,
                    value=selected_choice,
                    raw_input=user_input,
                    valid=True
                )
            except (KeyboardInterrupt, EOFError):
                self._print_warning("\nSelection cancelled by user")
                return PromptResult(
                    prompt_type=PromptType.CHOICE,
                    value=None,
                    raw_input="",
                    valid=False,
                    error_message="User cancelled selection"
                )
    
    def prompt_confirm(
        self,
        question: str,
        default: bool = False,
        help_text: Optional[str] = None
    ) -> PromptResult:
        """
        Prompt user for yes/no confirmation.
        
        Args:
            question: Question to ask user
            default: Default answer if user presses Enter
            help_text: Optional help text shown before prompt
        
        Returns:
            PromptResult with boolean value
        """
        if help_text:
            self._print_info(help_text)
        
        default_str = "Y/n" if default else "y/N"
        prompt = f"{self._format_question(question)} [{default_str}]: "
        
        while True:
            try:
                user_input = input(prompt).strip().lower()
                
                # Use default if empty
                if not user_input:
                    value = default
                elif user_input in ('y', 'yes'):
                    value = True
                elif user_input in ('n', 'no'):
                    value = False
                else:
                    self._print_error("Please enter 'y' or 'n'")
                    continue
                
                return PromptResult(
                    prompt_type=PromptType.CONFIRM,
                    value=value,
                    raw_input=user_input,
                    valid=True
                )
            except (KeyboardInterrupt, EOFError):
                self._print_warning("\nConfirmation cancelled by user")
                return PromptResult(
                    prompt_type=PromptType.CONFIRM,
                    value=default,
                    raw_input="",
                    valid=False,
                    error_message="User cancelled confirmation"
                )
    
    def display_progress(self, phase: str, step: int, total_steps: int, message: str = ""):
        """
        Display progress indicator.
        
        Args:
            phase: Current phase name
            step: Current step number (1-based)
            total_steps: Total number of steps
            message: Optional progress message
        """
        percent = int((step / total_steps) * 100)
        bar_length = 30
        filled = int((bar_length * step) / total_steps)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        progress_line = f"[{bar}] {percent}% - {phase} ({step}/{total_steps})"
        if message:
            progress_line += f": {message}"
        
        if self.colorize:
            _safe_print(f"\033[36m{progress_line}\033[0m")
        else:
            _safe_print(progress_line)
    
    def display_section(self, title: str, content: Dict[str, Any]):
        """
        Display a formatted section with title and key-value pairs.
        
        Args:
            title: Section title
            content: Dictionary of key-value pairs to display
        """
        self._print_header(title)
        for key, value in content.items():
            print(f"  {key}: {value}")
        print()
    
    # Private formatting methods
    
    def _format_question(self, text: str) -> str:
        """Format question text with optional color."""
        if self.colorize:
            return f"\033[1;34m❓ {text}\033[0m"
        return f"❓ {text}"
    
    def _print_header(self, text: str):
        """Print section header."""
        if self.colorize:
            print(f"\n\033[1;35m{'=' * 60}\033[0m")
            print(f"\033[1;35m{text}\033[0m")
            print(f"\033[1;35m{'=' * 60}\033[0m\n")
        else:
            print(f"\n{'=' * 60}")
            print(text)
            print(f"{'=' * 60}\n")
    
    def _print_success(self, text: str):
        """Print success message."""
        if self.colorize:
            _safe_print(f"\033[32m✅ {text}\033[0m")
        else:
            _safe_print(f"✅ {text}")
    
    def _print_error(self, text: str):
        """Print error message."""
        if self.colorize:
            _safe_print(f"\033[31m❌ {text}\033[0m")
        else:
            _safe_print(f"❌ {text}")
    
    def _print_warning(self, text: str):
        """Print warning message."""
        if self.colorize:
            _safe_print(f"\033[33m⚠️  {text}\033[0m")
        else:
            _safe_print(f"⚠️  {text}")
    
    def _print_info(self, text: str):
        """Print info message."""
        if self.colorize:
            _safe_print(f"\033[36mℹ️  {text}\033[0m")
        else:
            _safe_print(f"ℹ️  {text}")


# Convenience function for quick UI access
def get_planning_ui(colorize: bool = True, verbose: bool = True) -> PlanningUI:
    """
    Factory function to get PlanningUI instance.
    
    Args:
        colorize: Enable ANSI colors
        verbose: Show detailed messages
    
    Returns:
        Configured PlanningUI instance
    """
    return PlanningUI(colorize=colorize, verbose=verbose)
