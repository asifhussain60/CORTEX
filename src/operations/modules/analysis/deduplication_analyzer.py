"""
Deduplication Analyzer - AST-powered semantic duplicate detection.

Identifies functionally similar code blocks that could be refactored
into shared utilities or modules.

Copyright © 2025 Asif Hussain. All rights reserved.
"""

from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)


@dataclass
class DuplicateGroup:
    """Group of semantically similar code blocks."""
    similarity_score: float
    locations: List[Dict[str, Any]]  # file, start_line, end_line
    lines_count: int
    recommendation: str


class DeduplicationAnalyzer:
    """Detect semantic code duplicates using AST analysis."""
    
    def __init__(self, ast_engine):
        """
        Initialize deduplication analyzer.
        
        Args:
            ast_engine: AST engine for semantic comparison
        """
        self.ast_engine = ast_engine
        self.min_similarity = 0.85
        self.min_lines = 10
        
    def analyze(self, target_path: Path = None) -> Dict[str, Any]:
        """
        Analyze codebase for semantic duplicates.
        
        Args:
            target_path: Specific directory/file or None for full project
            
        Returns:
            Analysis results with duplicate groups and recommendations
        """
        logger.info(f"Analyzing duplicates in {target_path or 'full project'}")
        
        # Use AST engine for semantic comparison
        # Note: AST engine operates on project_root, target_path used for filtering
        duplicate_groups = self.ast_engine.find_semantic_duplicates(
            similarity_threshold=self.min_similarity,
            min_lines=self.min_lines
        )
        
        # Enrich with recommendations
        enriched_groups = []
        for group in duplicate_groups:
            enriched_groups.append(DuplicateGroup(
                similarity_score=group.get('similarity', 0.0),
                locations=group.get('locations', []),
                lines_count=group.get('lines', 0),
                recommendation=self._generate_recommendation(group)
            ))
            
        return {
            'duplicate_groups': enriched_groups,
            'total_duplicates': len(enriched_groups),
            'total_duplicate_lines': sum(g.lines_count for g in enriched_groups),
            'estimated_cleanup_hours': self._estimate_cleanup_effort(enriched_groups)
        }
        
    def _generate_recommendation(self, group: Dict[str, Any]) -> str:
        """Generate actionable refactoring recommendation."""
        locations = group.get('locations', [])
        
        if len(locations) == 2:
            return (
                f"Extract shared logic into utility function. "
                f"Found in {locations[0].get('file', 'unknown')} "
                f"and {locations[1].get('file', 'unknown')}."
            )
        elif len(locations) > 2:
            return (
                f"Consider creating shared module. "
                f"Duplicate appears in {len(locations)} files."
            )
        else:
            return "Review for refactoring opportunity."
            
    def _estimate_cleanup_effort(self, groups: List[DuplicateGroup]) -> float:
        """
        Estimate cleanup effort in hours.
        
        Args:
            groups: List of duplicate groups
            
        Returns:
            Estimated hours for cleanup
        """
        # 15 minutes per duplicate group (conservative)
        return len(groups) * 0.25
