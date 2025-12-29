"""
Duplication Detection System (Phase 4)
Searches existing lessons using FTS5 full-text search to prevent duplicates.

Features:
- Keyword extraction from captured lessons
- FTS5 full-text search integration with Tier 2 KnowledgeGraph
- Similarity scoring with configurable threshold
- Ranked duplicate matches with merge suggestions

Author: Asif Hussain
License: Source-Available
"""

import re
import logging
from dataclasses import dataclass
from typing import List, Set, Dict, Any
from pathlib import Path

from src.operations.modules.learning.lesson_capture import CapturedLesson
from src.tier2.knowledge_graph import KnowledgeGraph

logger = logging.getLogger(__name__)

# Common English stopwords to filter from keyword extraction
STOPWORDS = {
    'the', 'a', 'an', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by',
    'from', 'as', 'is', 'was', 'are', 'were', 'been', 'be', 'have', 'has',
    'had', 'do', 'does', 'did', 'will', 'would', 'should', 'could', 'may',
    'might', 'must', 'can', 'this', 'that', 'these', 'those', 'i', 'you',
    'he', 'she', 'it', 'we', 'they', 'and', 'or', 'but', 'not', 'no'
}


def extract_keywords(lesson: CapturedLesson) -> List[str]:
    """
    Extract keywords from captured lesson for FTS5 search.
    
    Combines keywords from problem, root_cause, and solution fields.
    Filters stopwords and extracts meaningful terms.
    
    Args:
        lesson: CapturedLesson to extract keywords from
        
    Returns:
        List of unique keywords
    """
    # Combine relevant text fields
    text = f"{lesson.problem} {lesson.root_cause} {lesson.solution}"
    
    # Convert to lowercase and extract words (alphanumeric only)
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())
    
    # Filter stopwords and duplicates
    keywords = [w for w in words if w not in STOPWORDS]
    
    # Return unique keywords maintaining order
    seen: Set[str] = set()
    unique_keywords = []
    for keyword in keywords:
        if keyword not in seen:
            seen.add(keyword)
            unique_keywords.append(keyword)
    
    return unique_keywords


@dataclass
class DuplicateMatch:
    """
    Represents a potential duplicate lesson match.
    
    Attributes:
        lesson_id: ID of existing lesson in lessons-learned.yaml
        problem: Problem description from existing lesson
        solution: Solution description from existing lesson
        similarity_score: Calculated similarity (0.0-1.0)
        explanation: Human-readable explanation of match
    """
    lesson_id: str
    problem: str
    solution: str
    similarity_score: float
    explanation: str


class DuplicationDetector:
    """
    Detects duplicate lessons using FTS5 full-text search.
    
    Integrates with Tier 2 KnowledgeGraph to search existing lessons
    and calculate similarity scores for potential duplicates.
    """
    
    def __init__(self, kg: KnowledgeGraph = None):
        """
        Initialize duplication detector.
        
        Args:
            kg: Optional KnowledgeGraph instance (for testing/injection)
        """
        self.kg = kg if kg is not None else KnowledgeGraph()
        
    def find_duplicates(
        self,
        lesson: CapturedLesson,
        threshold: float = 0.70,
        max_results: int = 5
    ) -> List[DuplicateMatch]:
        """
        Find potential duplicate lessons using FTS5 search.
        
        Args:
            lesson: CapturedLesson to check for duplicates
            threshold: Minimum similarity score to include (0.0-1.0)
            max_results: Maximum number of matches to return
            
        Returns:
            List of DuplicateMatch objects sorted by similarity score (descending)
        """
        # Extract keywords for search query
        keywords = extract_keywords(lesson)
        
        if not keywords:
            logger.warning("No keywords extracted from lesson, skipping duplicate search")
            return []
        
        # Construct FTS5 search query
        search_query = ' '.join(keywords[:10])  # Limit to top 10 keywords
        
        # Search existing lessons using KnowledgeGraph FTS5
        try:
            search_results = self.kg.search_lessons(search_query, limit=max_results * 2)
        except Exception as e:
            logger.error(f"FTS5 search failed: {e}")
            return []
        
        # Calculate similarity scores and filter by threshold
        matches = []
        for result in search_results:
            similarity = self._calculate_similarity(lesson, result)
            
            if similarity >= threshold:
                explanation = self._generate_match_explanation(keywords, result, similarity)
                matches.append(DuplicateMatch(
                    lesson_id=result.get('id', 'unknown'),
                    problem=result.get('problem', ''),
                    solution=result.get('solution', ''),
                    similarity_score=similarity,
                    explanation=explanation
                ))
        
        # Sort by similarity score (highest first) and limit results
        matches.sort(key=lambda m: m.similarity_score, reverse=True)
        return matches[:max_results]
        
    def _calculate_similarity(self, lesson: CapturedLesson, existing: Dict[str, Any]) -> float:
        """
        Calculate similarity score between captured lesson and existing lesson.
        
        Uses keyword overlap and text similarity across problem, root_cause, solution.
        
        Args:
            lesson: Captured lesson to compare
            existing: Existing lesson dict from KnowledgeGraph
            
        Returns:
            Similarity score (0.0-1.0)
        """
        # Extract keywords from both lessons
        lesson_keywords = set(extract_keywords(lesson))
        
        existing_text = f"{existing.get('problem', '')} {existing.get('root_cause', '')} {existing.get('solution', '')}"
        existing_words = re.findall(r'\b[a-z]{3,}\b', existing_text.lower())
        existing_keywords = set(w for w in existing_words if w not in STOPWORDS)
        
        if not lesson_keywords or not existing_keywords:
            return 0.0
        
        # Calculate Jaccard similarity (intersection over union)
        intersection = len(lesson_keywords & existing_keywords)
        union = len(lesson_keywords | existing_keywords)
        
        if union == 0:
            return 0.0
            
        jaccard = intersection / union
        
        # Boost score if problem statements are very similar
        problem_similarity = self._text_similarity(
            lesson.problem.lower(),
            existing.get('problem', '').lower()
        )
        
        # Weighted average (70% keyword overlap, 30% problem similarity)
        final_score = (jaccard * 0.7) + (problem_similarity * 0.3)
        
        return min(final_score, 1.0)
        
    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate simple word-level similarity between two text strings.
        
        Args:
            text1: First text
            text2: Second text
            
        Returns:
            Similarity score (0.0-1.0)
        """
        words1 = set(re.findall(r'\b\w+\b', text1.lower()))
        words2 = set(re.findall(r'\b\w+\b', text2.lower()))
        
        if not words1 or not words2:
            return 0.0
            
        intersection = len(words1 & words2)
        union = len(words1 | words2)
        
        return intersection / union if union > 0 else 0.0
        
    def _generate_match_explanation(
        self,
        query_keywords: List[str],
        result: Dict[str, Any],
        similarity: float
    ) -> str:
        """
        Generate human-readable explanation for duplicate match.
        
        Args:
            query_keywords: Keywords extracted from captured lesson
            result: Search result from KnowledgeGraph
            similarity: Calculated similarity score
            
        Returns:
            Explanation string
        """
        # Find common keywords
        result_text = f"{result.get('problem', '')} {result.get('solution', '')}".lower()
        common = [kw for kw in query_keywords[:5] if kw in result_text]
        
        if len(common) >= 3:
            return f"High keyword overlap ({len(common)} keywords: {', '.join(common[:3])})"
        elif len(common) >= 1:
            return f"Matching keywords: {', '.join(common)}"
        else:
            return f"Similar content ({similarity*100:.0f}% match)"
