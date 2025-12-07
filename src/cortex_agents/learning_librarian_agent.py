"""
Learning Librarian Agent (Phase 6)
Orchestrates git-based learning library updates via natural language commands.

Workflow:
1. Scan git history for timeframe
2. Filter learning-worthy commits
3. Interactive lesson capture
4. Duplication detection
5. YAML persistence

Triggers:
- "update learning library"
- "capture lessons"
- "document learnings"

Author: Asif Hussain
License: Source-Available
"""

import re
import logging
from dataclasses import dataclass
from typing import Optional, List
from pathlib import Path

from src.operations.modules.learning.git_history_scanner import GitHistoryScanner
from src.operations.modules.learning.commit_filter import CommitFilter
from src.operations.modules.learning.lesson_capture import LessonCapture
from src.operations.modules.learning.duplication_detector import DuplicationDetector
from src.operations.modules.learning.yaml_writer import YAMLWriter

logger = logging.getLogger(__name__)


@dataclass
class LearningLibraryRequest:
    """Request to update learning library."""
    user_message: str
    since_hours: Optional[int] = None
    repo_path: Optional[Path] = None


@dataclass
class LearningLibraryResponse:
    """Response from learning library update."""
    success: bool
    message: str
    lessons_captured: int = 0
    duplicates_skipped: int = 0
    commits_scanned: int = 0


class LearningLibrarianAgent:
    """
    Specialist agent for git-based learning library updates.
    
    Orchestrates full workflow from git scanning to YAML persistence.
    """
    
    # Natural language triggers
    TRIGGERS = [
        r'\bupdate\s+learning\s+library\b',
        r'\bcapture\s+lessons\b',
        r'\bdocument\s+learnings?\b',
        r'\blearning\s+library\b'
    ]
    
    def __init__(self, repo_path: Optional[Path] = None):
        """
        Initialize learning librarian agent.
        
        Args:
            repo_path: Optional repository path (defaults to cwd)
        """
        self.repo_path = repo_path if repo_path else Path.cwd()
        
    def can_handle(self, request: LearningLibraryRequest) -> bool:
        """
        Check if agent can handle the request.
        
        Args:
            request: User request
            
        Returns:
            True if any trigger matches
        """
        message_lower = request.user_message.lower()
        
        for pattern in self.TRIGGERS:
            if re.search(pattern, message_lower):
                return True
                
        return False
        
    def execute(self, request: LearningLibraryRequest) -> LearningLibraryResponse:
        """
        Execute learning library update workflow.
        
        Full pipeline: scan → filter → capture → dedupe → write
        
        Args:
            request: Learning library update request
            
        Returns:
            LearningLibraryResponse with results
        """
        try:
            # Determine timeframe
            since_hours = self._get_timeframe(request)
            repo_path = request.repo_path if request.repo_path else self.repo_path
            
            logger.info(f"Starting learning library update (last {since_hours}h)")
            
            # Step 1: Scan git history
            scanner = GitHistoryScanner(repo_path=repo_path)
            commits = scanner.scan_commits(since_hours=since_hours)
            
            if not commits:
                return LearningLibraryResponse(
                    success=True,
                    message=f"No commits found in last {since_hours} hours",
                    commits_scanned=0
                )
            
            logger.info(f"Scanned {len(commits)} commits")
            
            # Step 2: Filter learning-worthy candidates
            commit_filter = CommitFilter()
            candidates = commit_filter.filter_learning_candidates(commits)
            
            if not candidates:
                return LearningLibraryResponse(
                    success=True,
                    message=f"No learning-worthy commits found ({len(commits)} scanned)",
                    commits_scanned=len(commits)
                )
            
            logger.info(f"Found {len(candidates)} learning-worthy candidates")
            
            # Step 3-5: Interactive capture, dedupe, write
            lesson_capture = LessonCapture()
            duplication_detector = DuplicationDetector()
            yaml_writer = YAMLWriter()
            
            lessons_captured = 0
            duplicates_skipped = 0
            
            for candidate in candidates:
                # Step 3: Interactive capture
                captured_lesson = lesson_capture.capture_lesson(candidate)
                
                if captured_lesson is None:
                    # User skipped
                    continue
                
                # Step 4: Check for duplicates
                duplicates = duplication_detector.find_duplicates(captured_lesson)
                
                if duplicates:
                    print(f"\n[!] Found {len(duplicates)} potential duplicate(s):")
                    for i, dup in enumerate(duplicates, 1):
                        print(f"  {i}. [{dup.lesson_id}] {dup.problem[:60]}...")
                        print(f"     Similarity: {dup.similarity_score*100:.0f}% - {dup.explanation}")
                    
                    response = input("\nSkip this lesson due to duplicates? (y/n): ").strip().lower()
                    if response == 'y':
                        duplicates_skipped += 1
                        continue
                
                # Step 5: Write to YAML
                lesson_id = yaml_writer.append_lesson(captured_lesson)
                logger.info(f"Captured lesson {lesson_id}")
                lessons_captured += 1
            
            # Generate summary response
            return self._format_response(
                success=True,
                lessons_captured=lessons_captured,
                duplicates_skipped=duplicates_skipped,
                commits_scanned=len(commits)
            )
            
        except Exception as e:
            logger.error(f"Learning library update failed: {e}")
            return LearningLibraryResponse(
                success=False,
                message=f"Update failed: {str(e)}"
            )
            
    def _get_timeframe(self, request: LearningLibraryRequest) -> int:
        """
        Get timeframe in hours from request.
        
        Args:
            request: User request
            
        Returns:
            Timeframe in hours (default 24)
        """
        if request.since_hours is not None:
            return request.since_hours
            
        # Try to extract from message
        extracted = self._extract_timeframe(request.user_message)
        return extracted if extracted else 24
        
    def _extract_timeframe(self, message: str) -> Optional[int]:
        """
        Extract timeframe from natural language message.
        
        Args:
            message: User message
            
        Returns:
            Timeframe in hours, or None if not found
        """
        message_lower = message.lower()
        
        # Check for specific patterns
        if 'last week' in message_lower or 'past week' in message_lower:
            return 168  # 7 days
        elif 'last 48 hours' in message_lower or 'past 48 hours' in message_lower:
            return 48
        elif re.search(r'last\s+(\d+)\s+days?', message_lower):
            match = re.search(r'last\s+(\d+)\s+days?', message_lower)
            days = int(match.group(1))
            return days * 24
        elif re.search(r'last\s+(\d+)\s+hours?', message_lower):
            match = re.search(r'last\s+(\d+)\s+hours?', message_lower)
            return int(match.group(1))
        elif 'past 2 days' in message_lower or 'last 2 days' in message_lower:
            return 48
            
        return None
        
    def _format_response(
        self,
        success: bool,
        lessons_captured: int,
        duplicates_skipped: int,
        commits_scanned: int
    ) -> LearningLibraryResponse:
        """
        Format response message.
        
        Args:
            success: Whether operation succeeded
            lessons_captured: Number of lessons captured
            duplicates_skipped: Number of duplicates skipped
            commits_scanned: Number of commits scanned
            
        Returns:
            Formatted LearningLibraryResponse
        """
        if lessons_captured == 0:
            message = f"No lessons captured from {commits_scanned} commits scanned"
        else:
            message = f"Successfully captured {lessons_captured} lesson(s) from {commits_scanned} commits"
            if duplicates_skipped > 0:
                message += f" ({duplicates_skipped} duplicate(s) skipped)"
        
        return LearningLibraryResponse(
            success=success,
            message=message,
            lessons_captured=lessons_captured,
            duplicates_skipped=duplicates_skipped,
            commits_scanned=commits_scanned
        )
