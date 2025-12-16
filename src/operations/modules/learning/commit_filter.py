"""
Commit Filter

Identifies learning-worthy commits using configurable heuristics.
Assigns confidence scores based on line count, test changes, and error keywords.

Features:
- Configurable heuristics (line threshold, keyword patterns, weights)
- Weighted confidence scoring
- Ranked candidate list
- Integration with GitHistoryScanner

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import re
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from pathlib import Path
import logging
import yaml

from .git_history_scanner import CommitMetadata
from src.utils.resource_resolver import get_root_path

logger = logging.getLogger(__name__)


@dataclass
class Candidate:
    """
    Learning-worthy commit candidate.
    
    Attributes:
        commit: Original commit metadata
        confidence_score: Weighted score (0.0-1.0+)
        matched_heuristics: Dict of heuristic_name -> bool
        explanation: Human-readable reason for candidacy
    """
    commit: CommitMetadata
    confidence_score: float
    matched_heuristics: Dict[str, bool] = field(default_factory=dict)
    explanation: str = ""


class CommitFilter:
    """
    Filters commits to identify learning-worthy candidates.
    
    Uses heuristics with weighted scoring:
    - line_count: Threshold 100 lines, weight 0.3
    - test_changes: Test file modifications, weight 0.4
    - error_keywords: fix/bug/error in message, weight 0.5
    - refactor_keywords: refactor/cleanup/optimize, weight 0.3
    
    Example:
        filter = CommitFilter()
        commits = scanner.scan_commits(since_hours=24)
        candidates = filter.filter_learning_candidates(commits)
        
        for candidate in candidates:
            print(f"{candidate.commit.sha}: {candidate.confidence_score:.2f}")
    """
    
    def __init__(self, config_path: Optional[Path] = None):
        """
        Initialize commit filter with configurable heuristics.
        
        Args:
            config_path: Path to heuristics YAML config (optional, defaults to cortex-brain/config/learning-heuristics.yaml)
        """
        if config_path is None:
            # Default to cortex-brain/config/learning-heuristics.yaml
            project_root = get_root_path().parent.parent
            config_path = project_root / "cortex-brain" / "config" / "learning-heuristics.yaml"
        
        self.config = self._load_config(config_path)
    
    def _load_config(self, config_path: Optional[Path]) -> Dict:
        """
        Load heuristics configuration from YAML.
        
        Falls back to default configuration if file not found.
        """
        default_config = {
            'line_count': {
                'threshold': 100,
                'weight': 0.3,
                'description': 'Large commits likely involve significant work'
            },
            'test_changes': {
                'patterns': ['test_*.py', '*_test.py', 'tests/'],
                'weight': 0.4,
                'description': 'Test changes indicate problem-solving'
            },
            'error_keywords': {
                'patterns': ['fix', 'bug', 'error', 'crash', 'fail', 'debug', 'issue'],
                'weight': 0.5,
                'description': 'Error-related commits capture lessons learned'
            },
            'refactor_keywords': {
                'patterns': ['refactor', 'cleanup', 'optimize', 'improve'],
                'weight': 0.3,
                'description': 'Refactorings document better approaches'
            }
        }
        
        if config_path and config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    loaded_config = yaml.safe_load(f)
                    return loaded_config.get('heuristics', default_config)
            except Exception as e:
                logger.warning(f"Failed to load config from {config_path}: {e}")
        
        return default_config
    
    def filter_learning_candidates(self, commits: List[CommitMetadata]) -> List[Candidate]:
        """
        Filter commits to identify learning-worthy candidates.
        
        Args:
            commits: List of commit metadata from scanner
            
        Returns:
            List of Candidate objects, sorted by confidence descending
        """
        candidates = []
        
        for commit in commits:
            # Calculate confidence score and matched heuristics
            score, matched = self._calculate_confidence_score(commit)
            
            # Only include if at least one heuristic matched
            if score > 0:
                explanation = self._generate_explanation(matched)
                candidate = Candidate(
                    commit=commit,
                    confidence_score=score,
                    matched_heuristics=matched,
                    explanation=explanation
                )
                candidates.append(candidate)
        
        # Sort by confidence descending
        candidates.sort(key=lambda c: c.confidence_score, reverse=True)
        
        return candidates
    
    def _calculate_confidence_score(self, commit: CommitMetadata) -> tuple[float, Dict[str, bool]]:
        """
        Calculate weighted confidence score for commit.
        
        Args:
            commit: Commit metadata
            
        Returns:
            Tuple of (score, matched_heuristics_dict)
        """
        score = 0.0
        matched = {}
        
        # Check line_count heuristic
        threshold = self.config['line_count']['threshold']
        weight = self.config['line_count']['weight']
        total_lines = commit.lines_added + commit.lines_deleted
        
        if total_lines >= threshold:
            score += weight
            matched['line_count'] = True
        else:
            matched['line_count'] = False
        
        # Check test_changes heuristic
        test_patterns = self.config['test_changes']['patterns']
        test_weight = self.config['test_changes']['weight']
        
        if self._matches_test_patterns(commit.files_changed, test_patterns):
            score += test_weight
            matched['test_changes'] = True
        else:
            matched['test_changes'] = False
        
        # Check error_keywords heuristic
        error_patterns = self.config['error_keywords']['patterns']
        error_weight = self.config['error_keywords']['weight']
        
        if self._matches_keywords(commit.message, error_patterns):
            score += error_weight
            matched['error_keywords'] = True
        else:
            matched['error_keywords'] = False
        
        # Check refactor_keywords heuristic
        refactor_patterns = self.config['refactor_keywords']['patterns']
        refactor_weight = self.config['refactor_keywords']['weight']
        
        if self._matches_keywords(commit.message, refactor_patterns):
            score += refactor_weight
            matched['refactor_keywords'] = True
        else:
            matched['refactor_keywords'] = False
        
        return score, matched
    
    def _matches_test_patterns(self, files: List[str], patterns: List[str]) -> bool:
        """Check if any file matches test patterns."""
        for file_path in files:
            file_lower = file_path.lower()
            for pattern in patterns:
                pattern_lower = pattern.lower()
                
                # Simple pattern matching (not full glob)
                if pattern_lower.startswith('*'):
                    # Suffix match: *_test.py
                    suffix = pattern_lower[1:]
                    if file_lower.endswith(suffix):
                        return True
                elif pattern_lower.endswith('*'):
                    # Prefix match: test_*
                    prefix = pattern_lower[:-1]
                    file_name = Path(file_path).name.lower()
                    if file_name.startswith(prefix):
                        return True
                elif pattern_lower.endswith('/'):
                    # Directory match: tests/
                    if pattern_lower[:-1] in file_lower:
                        return True
                else:
                    # Exact substring match
                    if pattern_lower in file_lower:
                        return True
        
        return False
    
    def _matches_keywords(self, message: str, keywords: List[str]) -> bool:
        """Check if message contains any keywords (case-insensitive)."""
        message_lower = message.lower()
        
        for keyword in keywords:
            # Use word boundary matching for better accuracy
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, message_lower):
                return True
        
        return False
    
    def _generate_explanation(self, matched: Dict[str, bool]) -> str:
        """Generate human-readable explanation of why commit is a candidate."""
        reasons = []
        
        if matched.get('error_keywords'):
            reasons.append("contains error-related keywords")
        if matched.get('test_changes'):
            reasons.append("modifies test files")
        if matched.get('line_count'):
            reasons.append("large change (>100 lines)")
        if matched.get('refactor_keywords'):
            reasons.append("refactoring work")
        
        if not reasons:
            return "Unknown reason"
        
        return "Candidate because: " + ", ".join(reasons)


def filter_learning_candidates(commits: List[CommitMetadata],
                               config_path: Optional[Path] = None) -> List[Candidate]:
    """
    Convenience function to filter commits for learning candidates.
    
    Args:
        commits: List of commit metadata
        config_path: Optional path to heuristics config
        
    Returns:
        List of Candidate objects, sorted by confidence
    """
    filter_instance = CommitFilter(config_path=config_path)
    return filter_instance.filter_learning_candidates(commits)
