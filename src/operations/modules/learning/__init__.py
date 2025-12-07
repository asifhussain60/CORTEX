"""
Learning Library Module

Git-based learning capture with interactive refinement.

Components:
- git_history_scanner: Scan git commits for timeframe
- commit_filter: Identify learning-worthy commits using heuristics
- lesson_capture: Interactive prompts for structured lesson input
- duplication_detector: FTS5-based duplicate detection
- yaml_writer: Safe YAML append with validation

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

from .git_history_scanner import GitHistoryScanner, CommitMetadata, scan_commits
from .commit_filter import CommitFilter, Candidate, filter_learning_candidates
from .lesson_capture import LessonCapture, CapturedLesson, ValidationError
from .duplication_detector import DuplicationDetector, DuplicateMatch, extract_keywords
from .yaml_writer import YAMLWriter, SchemaValidationError, generate_lesson_id

__all__ = [
    'GitHistoryScanner',
    'CommitMetadata',
    'scan_commits',
    'CommitFilter',
    'Candidate',
    'filter_learning_candidates',
    'LessonCapture',
    'CapturedLesson',
    'ValidationError',
    'DuplicationDetector',
    'DuplicateMatch',
    'extract_keywords',
    'YAMLWriter',
    'SchemaValidationError',
    'generate_lesson_id',
]
