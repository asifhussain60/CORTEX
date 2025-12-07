"""
Interactive Lesson Capture System (Phase 3)
Guides users through structured prompts to capture high-quality lessons from git commits.

Author: Asif Hussain
License: Source-Available
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional, List, Dict, Any
from pathlib import Path
import yaml

from src.operations.modules.learning.commit_filter import Candidate

logger = logging.getLogger(__name__)


class ValidationError(Exception):
    """Raised when lesson validation fails."""
    pass


@dataclass
class CapturedLesson:
    """Structured lesson captured from user input."""
    problem: str
    root_cause: str
    solution: str
    prevention_rules: List[str]
    time_cost: str
    commit_hash: str
    confidence: float
    
    def __post_init__(self):
        """Validate fields after initialization."""
        if not self.problem or len(self.problem.strip()) < 10:
            raise ValidationError("Problem description must be at least 10 characters")
        if not self.time_cost or not self._validate_time_format(self.time_cost):
            raise ValidationError("Time cost must be in format like '2h', '30m', '1.5h'")
        if not self.prevention_rules or len(self.prevention_rules) == 0:
            raise ValidationError("At least one prevention rule required")
            
    @staticmethod
    def _validate_time_format(time_str: str) -> bool:
        """Validate time format (e.g., '2h', '30m', '1.5h')."""
        pattern = r'^\d+\.?\d*[hm]$'
        return bool(re.match(pattern, time_str))


class LessonCapture:
    """Interactive system for capturing structured lessons from git commits."""
    
    def __init__(self, prompts_file: Optional[Path] = None):
        """
        Initialize lesson capture system.
        
        Args:
            prompts_file: Optional path to custom prompts YAML file
        """
        if prompts_file is None:
            # Default to cortex-brain config (4 levels up from this file)
            prompts_file = Path(__file__).parents[4] / "cortex-brain" / "config" / "learning-capture-prompts.yaml"
        
        self.prompts = self._load_prompts(prompts_file)
        
    def _load_prompts(self, prompts_file: Path) -> Dict[str, Dict[str, Any]]:
        """
        Load prompt templates from YAML file.
        
        Args:
            prompts_file: Path to prompts YAML file
            
        Returns:
            Dictionary of prompt configurations
        """
        if prompts_file.exists():
            with open(prompts_file, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
                return config['prompts']
        
        # Fallback if file doesn't exist (shouldn't happen with default path)
        logger.warning(f"Prompts file not found: {prompts_file}, using hardcoded defaults")
        return self._get_default_prompts()
    
    def _get_default_prompts(self) -> Dict[str, Dict[str, Any]]:
        """Get hardcoded default prompts as fallback."""
        return {
            'problem': {
                'question': 'What problem did you encounter? (min 10 chars, or type "skip")',
                'validation': {'min_length': 10}
            },
            'root_cause': {
                'question': 'What was the root cause? (or type "skip")',
                'validation': {'min_length': 5}
            },
            'solution': {
                'question': 'How did you solve it? (or type "skip")',
                'validation': {'min_length': 10}
            },
            'prevention_rules': {
                'question': 'What rules would prevent this in future? (semicolon-separated, or type "skip")',
                'validation': {'min_items': 1},
                'parser': 'semicolon_list'
            },
            'time_cost': {
                'question': 'How much time did this cost? (e.g., 2h, 30m, 1.5h, or type "skip")',
                'validation': {'format': 'time'}
            }
        }
        
    def capture_lesson(self, candidate: Candidate) -> Optional[CapturedLesson]:
        """
        Interactively capture a lesson from a commit candidate.
        
        Args:
            candidate: Commit candidate to capture lesson from
            
        Returns:
            CapturedLesson if successful, None if skipped
        """
        # Display candidate information
        print("\n" + "="*80)
        print(self._format_candidate_display(candidate))
        print("="*80 + "\n")
        
        # Collect responses for each field
        responses = {}
        
        for field in ['problem', 'root_cause', 'solution', 'prevention_rules', 'time_cost']:
            response = self._prompt_for_field(field, candidate)
            
            # User chose to skip
            if response is None:
                return None
                
            responses[field] = response
        
        # Create and validate captured lesson
        try:
            return CapturedLesson(
                problem=responses['problem'],
                root_cause=responses['root_cause'],
                solution=responses['solution'],
                prevention_rules=responses['prevention_rules'],
                time_cost=responses['time_cost'],
                commit_hash=candidate.commit.sha,
                confidence=candidate.confidence_score
            )
        except ValidationError as e:
            print(f"\n[!] Validation failed: {e}")
            return None
            
    def _prompt_for_field(self, field: str, candidate: Candidate) -> Optional[Any]:
        """
        Prompt user for a specific field with validation.
        
        Args:
            field: Field name to prompt for
            candidate: Commit candidate context
            
        Returns:
            User response (parsed according to field type), or None if skipped
        """
        prompt_config = self.prompts[field]
        question = prompt_config['question']
        validation = prompt_config.get('validation', {})
        parser = prompt_config.get('parser', 'string')
        
        while True:
            response = input(f"{question}\n> ").strip()
            
            # Check for skip
            if response.lower() == 'skip':
                return None
                
            # Check for empty input
            if not response:
                print("[!] Input cannot be empty. Please try again or type 'skip'.\n")
                continue
                
            # Validate based on field requirements
            if 'min_length' in validation and len(response) < validation['min_length']:
                print(f"[!] Input must be at least {validation['min_length']} characters. Please try again.\n")
                continue
                
            if 'format' in validation and validation['format'] == 'time':
                if not self._validate_time_format(response):
                    print("[!] Invalid time format. Use format like '2h', '30m', or '1.5h'.\n")
                    continue
                    
            # Parse response according to field type
            if parser == 'semicolon_list':
                parsed = [r.strip() for r in response.split(';') if r.strip()]
                if validation.get('min_items', 0) > 0 and len(parsed) < validation['min_items']:
                    print(f"⚠️ At least {validation['min_items']} item(s) required.\n")
                    continue
                return parsed
            
            return response
            
    def _format_candidate_display(self, candidate: Candidate) -> str:
        """
        Format commit candidate for display to user.
        
        Args:
            candidate: Commit candidate to display
            
        Returns:
            Formatted display string
        """
        commit = candidate.commit
        confidence_pct = f"{candidate.confidence_score * 100:.0f}%"
        matched = ', '.join(k for k, v in candidate.matched_heuristics.items() if v)
        
        display = f"""
[COMMIT CANDIDATE] (Confidence: {confidence_pct})

Hash:     {commit.sha[:8]}
Author:   {commit.author}
Date:     {commit.timestamp}
Message:  {commit.message}

Changes:  {len(commit.files_changed)} files ({commit.lines_added}+ / {commit.lines_deleted}-)
Matched:  {matched}
Reason:   {candidate.explanation}
"""
        return display.strip()
        
    @staticmethod
    def _validate_time_format(time_str: str) -> bool:
        """
        Validate time format (e.g., '2h', '30m', '1.5h').
        
        Args:
            time_str: Time string to validate
            
        Returns:
            True if valid format, False otherwise
        """
        pattern = r'^\d+\.?\d*[hm]$'
        return bool(re.match(pattern, time_str))
