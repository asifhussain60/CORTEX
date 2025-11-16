"""
CORTEX Learning Capture Agent

Automatically captures lessons from:
- Operation failures/successes
- Error patterns and resolutions
- Git commits and code changes
- Ambient daemon events (file changes, terminal errors, VS Code actions)
- SKULL protection violations

This agent ensures CORTEX learns from every mistake and success,
preventing repeated errors.

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import yaml
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
from dataclasses import dataclass, field
import re
import json

logger = logging.getLogger(__name__)


@dataclass
class LearningEvent:
    """Structured learning event for knowledge capture."""
    event_type: str  # 'error', 'fix', 'operation', 'ambient', 'skull_violation'
    severity: str  # 'low', 'medium', 'high', 'critical'
    category: str  # 'platform', 'testing', 'validation', 'encoding', etc.
    timestamp: str
    
    # Event details
    problem: str
    solution: Optional[str] = None
    symptoms: List[str] = field(default_factory=list)
    root_cause: Optional[str] = None
    
    # Context
    file_path: Optional[str] = None
    operation: Optional[str] = None
    error_type: Optional[str] = None
    
    # Learning metadata
    confidence: float = 0.8
    tags: List[str] = field(default_factory=list)
    related_files: List[str] = field(default_factory=list)
    
    def to_lesson_dict(self, lesson_id: str) -> Dict[str, Any]:
        """Convert to lessons-learned.yaml format."""
        lesson = {
            'id': lesson_id,
            'title': self._generate_title(),
            'category': self.category,
            'subcategory': self._infer_subcategory(),
            'severity': self.severity,
            'date': self.timestamp.split('T')[0],
            'problem': self.problem,
            'symptoms': self.symptoms if self.symptoms else ['Issue detected during operation'],
            'confidence': self.confidence,
            'tags': self.tags
        }
        
        if self.root_cause:
            lesson['root_cause'] = self.root_cause
        
        if self.solution:
            lesson['solution'] = self.solution
            lesson['prevention_rules'] = self._generate_prevention_rules()
        
        if self.related_files:
            lesson['related_files'] = self.related_files
        
        if self.error_type:
            lesson['error_type'] = self.error_type
        
        return lesson
    
    def _generate_title(self) -> str:
        """Generate human-readable title from problem."""
        # Extract key issue from problem description
        if 'unicode' in self.problem.lower() or 'encoding' in self.problem.lower():
            return "Platform encoding prevents Unicode character display"
        elif 'skull' in self.problem.lower():
            return "SKULL protection rule violation detected"
        elif 'powershell' in self.problem.lower():
            return f"PowerShell {self.category} issue"
        else:
            # Take first sentence or first 60 chars
            first_sentence = self.problem.split('.')[0]
            return first_sentence[:60] + '...' if len(first_sentence) > 60 else first_sentence
    
    def _infer_subcategory(self) -> str:
        """Infer subcategory from context."""
        if self.event_type == 'ambient':
            return 'ambient-monitoring'
        elif 'windows' in self.tags or 'powershell' in self.tags:
            return 'windows'
        elif 'test' in self.tags:
            return 'testing'
        elif 'encoding' in self.tags or 'unicode' in self.tags:
            return 'encoding'
        else:
            return 'general'
    
    def _generate_prevention_rules(self) -> List[str]:
        """Generate prevention rules from solution."""
        rules = []
        
        if self.solution:
            # Extract actionable rules
            if 'test' in self.solution.lower():
                rules.append("Add tests to verify fix before claiming complete")
            
            if 'unicode' in self.solution.lower() or 'encoding' in self.solution.lower():
                rules.append("Always provide ASCII fallbacks for Unicode characters")
                rules.append("Test print operations on Windows PowerShell")
            
            if 'platform' in self.solution.lower():
                rules.append("Test on all supported platforms (Windows, macOS, Linux)")
            
            # Generic rule based on category
            if self.category == 'validation':
                rules.append("Validate inputs before processing")
            elif self.category == 'platform':
                rules.append("Use platform-aware code paths")
        
        return rules if rules else ["Review similar code for same issue"]


class LearningCaptureAgent:
    """
    Agent that automatically captures lessons learned from various sources.
    
    Sources:
    - Operation execution results (success/failure patterns)
    - Error traces and exceptions
    - Git commit messages and diffs
    - Ambient daemon events (file changes, terminal output, errors)
    - SKULL protection violations
    """
    
    def __init__(self, project_root: Optional[Path] = None):
        """
        Initialize learning capture agent.
        
        Args:
            project_root: Path to CORTEX project root
        """
        self.project_root = project_root or Path(__file__).parent.parent.parent
        self.brain_path = self.project_root / 'cortex-brain'
        self.lessons_file = self.brain_path / 'lessons-learned.yaml'
        self.knowledge_graph_file = self.brain_path / 'knowledge-graph.yaml'
        self.ambient_log = self.brain_path / 'conversation-context.jsonl'
        
        logger.info(f"LearningCaptureAgent initialized | Brain: {self.brain_path}")
    
    def capture_from_operation_result(
        self,
        operation_name: str,
        result: Any,
        context: Dict[str, Any]
    ) -> Optional[LearningEvent]:
        """
        Capture learning from operation execution result.
        
        Args:
            operation_name: Name of operation executed
            result: Operation result object
            context: Execution context
        
        Returns:
            LearningEvent if lesson extracted, None otherwise
        """
        # Check for errors in result
        if hasattr(result, 'errors') and result.errors:
            for error in result.errors:
                event = self._parse_error_for_learning(
                    error=error,
                    operation=operation_name,
                    context=context
                )
                if event:
                    return event
        
        # Check for module failures
        if hasattr(result, 'modules_failed') and result.modules_failed:
            problem = f"Operation '{operation_name}' had {len(result.modules_failed)} failed modules"
            
            # Extract failure details from module results
            symptoms = []
            if hasattr(result, 'module_results'):
                for mod_id in result.modules_failed:
                    mod_result = result.module_results.get(mod_id)
                    if mod_result and hasattr(mod_result, 'message'):
                        symptoms.append(f"{mod_id}: {mod_result.message}")
            
            return LearningEvent(
                event_type='operation',
                severity='high',
                category='orchestration',
                timestamp=datetime.now().isoformat(),
                problem=problem,
                symptoms=symptoms,
                operation=operation_name,
                tags=['operation-failure', operation_name.lower().replace(' ', '-')]
            )
        
        return None
    
    def capture_from_exception(
        self,
        exception: Exception,
        context: Dict[str, Any]
    ) -> Optional[LearningEvent]:
        """
        Capture learning from exception.
        
        Args:
            exception: Exception that occurred
            context: Context when exception occurred
        
        Returns:
            LearningEvent if pattern recognized
        """
        return self._parse_error_for_learning(
            error=str(exception),
            exception_type=type(exception).__name__,
            context=context
        )
    
    def capture_from_ambient_events(
        self,
        lookback_minutes: int = 30
    ) -> List[LearningEvent]:
        """
        Capture learning from recent ambient daemon events.
        
        Args:
            lookback_minutes: How far back to analyze events
        
        Returns:
            List of learning events from ambient monitoring
        """
        if not self.ambient_log.exists():
            return []
        
        events = []
        cutoff = datetime.now().timestamp() - (lookback_minutes * 60)
        
        try:
            with open(self.ambient_log, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        event_time = datetime.fromisoformat(event.get('timestamp', ''))
                        
                        if event_time.timestamp() < cutoff:
                            continue
                        
                        # Analyze event for learning
                        learning = self._analyze_ambient_event(event)
                        if learning:
                            events.append(learning)
                    
                    except (json.JSONDecodeError, ValueError):
                        continue
        
        except Exception as e:
            logger.error(f"Failed to read ambient log: {e}")
        
        return events
    
    def capture_from_git_commit(
        self,
        commit_sha: str,
        commit_message: str,
        files_changed: List[str]
    ) -> Optional[LearningEvent]:
        """
        Capture learning from git commit (fix commits especially).
        
        Args:
            commit_sha: Git commit SHA
            commit_message: Commit message
            files_changed: List of files in commit
        
        Returns:
            LearningEvent if fix pattern detected
        """
        # Detect fix commits
        fix_keywords = ['fix', 'resolve', 'correct', 'patch', 'repair', 'bug']
        is_fix = any(keyword in commit_message.lower() for keyword in fix_keywords)
        
        if not is_fix:
            return None
        
        # Try to infer what was fixed
        problem = self._infer_problem_from_commit(commit_message, files_changed)
        
        if problem:
            return LearningEvent(
                event_type='fix',
                severity='medium',
                category=self._infer_category_from_files(files_changed),
                timestamp=datetime.now().isoformat(),
                problem=problem,
                solution=f"Applied in commit {commit_sha[:8]}",
                related_files=files_changed[:5],  # Limit to 5 files
                tags=['git-fix', 'commit-learning'],
                confidence=0.7  # Lower confidence for inferred lessons
            )
        
        return None
    
    def save_lesson(self, event: LearningEvent) -> bool:
        """
        Save learning event to lessons-learned.yaml.
        
        Args:
            event: Learning event to save
        
        Returns:
            True if saved successfully
        """
        try:
            # Load existing lessons
            if self.lessons_file.exists():
                with open(self.lessons_file, 'r') as f:
                    data = yaml.safe_load(f) or {}
            else:
                data = {
                    'version': '1.0',
                    'last_updated': datetime.now().isoformat(),
                    'total_lessons': 0,
                    'lessons': []
                }
            
            # Generate unique ID
            existing_ids = [l.get('id', '') for l in data.get('lessons', [])]
            lesson_id = self._generate_unique_id(event, existing_ids)
            
            # Convert event to lesson
            lesson = event.to_lesson_dict(lesson_id)
            
            # Check for duplicates
            if self._is_duplicate_lesson(lesson, data.get('lessons', [])):
                logger.info(f"Duplicate lesson detected, skipping: {lesson_id}")
                return False
            
            # Add to lessons
            data['lessons'].append(lesson)
            data['total_lessons'] = len(data['lessons'])
            data['last_updated'] = datetime.now().isoformat()
            
            # Save back to file
            with open(self.lessons_file, 'w') as f:
                yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            
            logger.info(f"✅ Lesson captured: {lesson_id} - {lesson['title']}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to save lesson: {e}")
            return False
    
    def _parse_error_for_learning(
        self,
        error: str,
        exception_type: Optional[str] = None,
        operation: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Optional[LearningEvent]:
        """Parse error message for learning patterns."""
        error_lower = error.lower()
        
        # Unicode/Encoding errors
        if 'unicodeencodeerror' in error_lower or 'charmap' in error_lower or exception_type == 'UnicodeEncodeError':
            return LearningEvent(
                event_type='error',
                severity='high',
                category='platform',
                timestamp=datetime.now().isoformat(),
                problem="Windows PowerShell console cannot display Unicode characters (emoji, box drawing)",
                symptoms=[
                    "'charmap' codec can't encode character",
                    "UnicodeEncodeError on Windows",
                    "Operations fail immediately on header print"
                ],
                root_cause="PowerShell uses cp1252 encoding which lacks Unicode support",
                solution="Implement _safe_print() with platform-aware fallback to ASCII",
                error_type='UnicodeEncodeError',
                operation=operation,
                tags=['unicode', 'encoding', 'windows', 'powershell', 'emoji'],
                confidence=0.95
            )
        
        # SKULL protection violations
        if 'skull' in error_lower:
            return LearningEvent(
                event_type='skull_violation',
                severity='critical',
                category='testing',
                timestamp=datetime.now().isoformat(),
                problem="SKULL protection rule violated - fix claimed without test verification",
                symptoms=[
                    "Tests not run before claiming fix",
                    "Integration claimed without E2E validation"
                ],
                root_cause="Development workflow bypassed test-first requirement",
                solution="Always run tests before claiming completion",
                operation=operation,
                tags=['skull', 'tdd', 'brain-protection', 'testing'],
                confidence=1.0
            )
        
        # Module/dependency errors
        if ('module' in error_lower and 'not found' in error_lower) or 'modulenotfounderror' in error_lower or exception_type == 'ModuleNotFoundError':
            return LearningEvent(
                event_type='error',
                severity='medium',
                category='dependencies',
                timestamp=datetime.now().isoformat(),
                problem="Missing Python module dependency",
                symptoms=[f"ModuleNotFoundError: {error}"],
                solution="Install missing dependency or update requirements.txt",
                error_type='ModuleNotFoundError',
                tags=['dependencies', 'python', 'modules'],
                confidence=0.9
            )
        
        return None
    
    def _analyze_ambient_event(self, event: Dict[str, Any]) -> Optional[LearningEvent]:
        """Analyze ambient daemon event for learning."""
        event_type = event.get('event_type', '')
        
        # Terminal errors
        if event_type == 'terminal_error':
            error_text = event.get('error', '')
            return self._parse_error_for_learning(
                error=error_text,
                context={'ambient': True, 'terminal': event.get('terminal_id')}
            )
        
        # File save patterns (e.g., multiple saves = possible error retry)
        if event_type == 'file_save':
            # Could track patterns of repeated saves to same file
            pass
        
        # VS Code error diagnostics
        if event_type == 'vscode_diagnostic' and event.get('severity') == 'error':
            # Could learn from VS Code error messages
            pass
        
        return None
    
    def _infer_problem_from_commit(
        self,
        message: str,
        files: List[str]
    ) -> Optional[str]:
        """Infer problem description from commit message."""
        # Extract problem from common patterns
        patterns = [
            r'fix[:\s]+(.+)',
            r'resolve[:\s]+(.+)',
            r'correct[:\s]+(.+)',
            r'patch[:\s]+(.+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, message, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        
        # Fallback: use commit message as-is
        return message if len(message) < 200 else message[:200] + '...'
    
    def _infer_category_from_files(self, files: List[str]) -> str:
        """Infer category from files changed."""
        if any('test' in f.lower() for f in files):
            return 'testing'
        elif any('tier0' in f.lower() for f in files):
            return 'governance'
        elif any('agent' in f.lower() for f in files):
            return 'agent-system'
        elif any('operation' in f.lower() for f in files):
            return 'operations'
        else:
            return 'general'
    
    def _generate_unique_id(
        self,
        event: LearningEvent,
        existing_ids: List[str]
    ) -> str:
        """Generate unique lesson ID."""
        # Format: category-subcategory-number
        base_id = f"{event.category}-{event._infer_subcategory()}"
        
        # Find next available number
        counter = 1
        while f"{base_id}-{counter:03d}" in existing_ids:
            counter += 1
        
        return f"{base_id}-{counter:03d}"
    
    def _is_duplicate_lesson(
        self,
        new_lesson: Dict[str, Any],
        existing_lessons: List[Dict[str, Any]]
    ) -> bool:
        """Check if lesson already exists (prevent duplicates)."""
        new_problem = new_lesson.get('problem', '').lower()
        new_title = new_lesson.get('title', '').lower()
        
        for existing in existing_lessons:
            existing_problem = existing.get('problem', '').lower()
            existing_title = existing.get('title', '').lower()
            
            # Check similarity (simple string matching for now)
            if new_problem in existing_problem or existing_problem in new_problem:
                return True
            
            if new_title in existing_title or existing_title in new_title:
                return True
        
        return False


# Convenience functions for quick integration

def capture_operation_learning(
    operation_name: str,
    result: Any,
    context: Dict[str, Any],
    project_root: Optional[Path] = None
) -> bool:
    """
    Quick function to capture learning from operation result.
    
    Args:
        operation_name: Operation that executed
        result: Operation result
        context: Execution context
        project_root: Optional project root path
    
    Returns:
        True if lesson captured
    """
    agent = LearningCaptureAgent(project_root)
    event = agent.capture_from_operation_result(operation_name, result, context)
    
    if event:
        return agent.save_lesson(event)
    
    return False


def capture_exception_learning(
    exception: Exception,
    context: Dict[str, Any],
    project_root: Optional[Path] = None
) -> bool:
    """
    Quick function to capture learning from exception.
    
    Args:
        exception: Exception that occurred
        context: Context when exception occurred
        project_root: Optional project root path
    
    Returns:
        True if lesson captured
    """
    agent = LearningCaptureAgent(project_root)
    event = agent.capture_from_exception(exception, context)
    
    if event:
        return agent.save_lesson(event)
    
    return False
