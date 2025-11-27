"""
Pattern Search Enforcer (Rule #27: Pattern-First Development)

Purpose: Enforce "search before create" pattern to reduce code duplication
Author: CORTEX Development Team
Version: 1.0

Rule #27: Before creating new utilities/helpers:
1. Query Tier 2 Knowledge Graph for similar patterns
2. Search codebase for existing functions
3. Reuse if ≥70% match
4. Only create new if no match OR existing is inadequate

This enforcer automatically runs before code creation and suggests
pattern reuse when appropriate.
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import sqlite3


@dataclass
class PatternMatch:
    """Represents a pattern found in Tier 2"""
    
    pattern_id: str
    name: str
    confidence: float  # 0.0 to 1.0
    description: str
    file_path: str
    code_snippet: Optional[str]
    usage_count: int
    last_used: datetime
    category: str  # "workflow", "code_pattern", "ui_pattern", etc.
    
    def is_reusable(self, threshold: float = 0.70) -> bool:
        """Check if pattern confidence meets reuse threshold"""
        return self.confidence >= threshold


@dataclass
class SearchResult:
    """Result of pattern search operation"""
    
    action: str  # "REUSE" or "CREATE"
    pattern: Optional[PatternMatch]
    message: str
    alternatives: List[PatternMatch]  # Lower confidence matches
    search_time_ms: float
    

class PatternSearchEnforcer:
    """
    Enforce pattern-first development (Rule #27)
    
    Before creating new code:
    1. Search Tier 2 for similar patterns
    2. If found with ≥70% confidence → Suggest reuse
    3. If not found → Allow creation and log new pattern
    4. Track all searches for learning
    """
    
    def __init__(self, 
                 db_path: str = "cortex-brain.db",
                 reuse_threshold: float = 0.70):
        """
        Initialize pattern search enforcer
        
        Args:
            db_path: Path to CORTEX brain SQLite database
            reuse_threshold: Minimum confidence for suggesting reuse (default: 70%)
        """
        self.db_path = db_path
        self.reuse_threshold = reuse_threshold
        self._conn: Optional[sqlite3.Connection] = None
        
    def connect(self) -> None:
        """Connect to Tier 2 pattern database"""
        if not self._conn:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
            
    def disconnect(self) -> None:
        """Disconnect from database"""
        if self._conn:
            self._conn.close()
            self._conn = None
    
    def search_before_create(self, 
                           intent: str, 
                           code_type: str,
                           context: Optional[Dict[str, Any]] = None) -> SearchResult:
        """
        Search for existing patterns before creating new code
        
        Args:
            intent: What the code should accomplish (e.g., "export invoice to PDF")
            code_type: Type of code ("function", "class", "component", "workflow")
            context: Optional context (file path, module, dependencies)
        
        Returns:
            SearchResult with action (REUSE/CREATE) and details
        
        Example:
            >>> enforcer = PatternSearchEnforcer()
            >>> result = enforcer.search_before_create(
            ...     intent="export invoice to PDF",
            ...     code_type="service_method"
            ... )
            >>> if result.action == "REUSE":
            ...     print(f"Reuse {result.pattern.name}")
            >>> else:
            ...     print("Create new implementation")
        """
        import time
        start_time = time.perf_counter()
        
        self.connect()
        
        # Step 1: Query Tier 2 for similar patterns
        similar_patterns = self._search_patterns(intent, code_type, context)
        
        # Step 2: Check if best match meets reuse threshold
        if similar_patterns and similar_patterns[0].is_reusable(self.reuse_threshold):
            best_match = similar_patterns[0]
            search_time_ms = (time.perf_counter() - start_time) * 1000
            
            # Log the successful reuse suggestion
            self._log_pattern_search(
                intent=intent,
                code_type=code_type,
                result="REUSE",
                pattern_id=best_match.pattern_id,
                confidence=best_match.confidence
            )
            
            return SearchResult(
                action="REUSE",
                pattern=best_match,
                message=(
                    f"✅ Found similar pattern: {best_match.name} "
                    f"(confidence: {best_match.confidence:.0%}). "
                    f"Reuse recommended to avoid duplication."
                ),
                alternatives=similar_patterns[1:5],  # Top 4 alternatives
                search_time_ms=search_time_ms
            )
        else:
            # No suitable pattern found - allow creation
            search_time_ms = (time.perf_counter() - start_time) * 1000
            
            # Log the new pattern creation
            self._log_pattern_search(
                intent=intent,
                code_type=code_type,
                result="CREATE",
                pattern_id=None,
                confidence=0.0
            )
            
            return SearchResult(
                action="CREATE",
                pattern=None,
                message=(
                    "🆕 No similar pattern found with sufficient confidence. "
                    "Creating new implementation. "
                    "This pattern will be logged to Tier 2 for future reuse."
                ),
                alternatives=similar_patterns[:5] if similar_patterns else [],
                search_time_ms=search_time_ms
            )
    
    def _search_patterns(self,
                        intent: str,
                        code_type: str,
                        context: Optional[Dict[str, Any]] = None) -> List[PatternMatch]:
        """
        Search Tier 2 patterns using FTS5 semantic search
        
        Args:
            intent: Search query
            code_type: Filter by code type
            context: Additional context for filtering
        
        Returns:
            List of PatternMatch objects sorted by confidence (descending)
        """
        if not self._conn:
            self.connect()
        
        # FTS5 semantic search query
        # Note: Actual implementation depends on Tier 2 schema
        # This is a placeholder that will be implemented in Task 3.2
        
        query = """
        SELECT 
            pattern_id,
            name,
            confidence,
            description,
            file_path,
            code_snippet,
            usage_count,
            last_used,
            category
        FROM patterns
        WHERE category = ? 
            AND (
                name MATCH ?
                OR description MATCH ?
            )
        ORDER BY confidence DESC, usage_count DESC
        LIMIT 10
        """
        
        try:
            cursor = self._conn.execute(query, (code_type, intent, intent))
            rows = cursor.fetchall()
            
            patterns = []
            for row in rows:
                pattern = PatternMatch(
                    pattern_id=row['pattern_id'],
                    name=row['name'],
                    confidence=row['confidence'],
                    description=row['description'],
                    file_path=row['file_path'],
                    code_snippet=row['code_snippet'],
                    usage_count=row['usage_count'],
                    last_used=datetime.fromisoformat(row['last_used']),
                    category=row['category']
                )
                patterns.append(pattern)
            
            return patterns
            
        except sqlite3.OperationalError as e:
            # Table doesn't exist yet (Tier 2 not fully implemented)
            # Return empty list - will be functional after Task 3.2
            return []
    
    def _log_pattern_search(self,
                           intent: str,
                           code_type: str,
                           result: str,
                           pattern_id: Optional[str],
                           confidence: float) -> None:
        """
        Log pattern search to Tier 2 for learning
        
        This helps CORTEX learn:
        - What patterns are searched for most
        - What gets reused vs created new
        - Confidence thresholds effectiveness
        
        Args:
            intent: What was searched for
            code_type: Type of code
            result: "REUSE" or "CREATE"
            pattern_id: ID of pattern if reused
            confidence: Confidence score of match
        """
        if not self._conn:
            self.connect()
        
        try:
            self._conn.execute("""
                INSERT INTO pattern_searches 
                (timestamp, intent, code_type, result, pattern_id, confidence)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                datetime.now().isoformat(),
                intent,
                code_type,
                result,
                pattern_id,
                confidence
            ))
            self._conn.commit()
            
        except sqlite3.OperationalError:
            # Table doesn't exist yet - will be created in Task 3.2
            pass
    
    def get_reuse_statistics(self, days: int = 30) -> Dict[str, Any]:
        """
        Get pattern reuse statistics for the last N days
        
        Args:
            days: Number of days to analyze
        
        Returns:
            Dictionary with reuse metrics
        """
        if not self._conn:
            self.connect()
        
        try:
            cursor = self._conn.execute("""
                SELECT 
                    COUNT(*) as total_searches,
                    SUM(CASE WHEN result = 'REUSE' THEN 1 ELSE 0 END) as reuse_count,
                    SUM(CASE WHEN result = 'CREATE' THEN 1 ELSE 0 END) as create_count,
                    AVG(CASE WHEN result = 'REUSE' THEN confidence ELSE NULL END) as avg_reuse_confidence
                FROM pattern_searches
                WHERE timestamp >= datetime('now', '-{} days')
            """.format(days))
            
            row = cursor.fetchone()
            
            total = row['total_searches'] or 0
            reuse = row['reuse_count'] or 0
            create = row['create_count'] or 0
            
            return {
                'total_searches': total,
                'reuse_count': reuse,
                'create_count': create,
                'reuse_rate': (reuse / total * 100) if total > 0 else 0.0,
                'avg_reuse_confidence': row['avg_reuse_confidence'] or 0.0
            }
            
        except sqlite3.OperationalError:
            # Table doesn't exist yet
            return {
                'total_searches': 0,
                'reuse_count': 0,
                'create_count': 0,
                'reuse_rate': 0.0,
                'avg_reuse_confidence': 0.0
            }
    
    def log_pattern_creation(self,
                            pattern_id: str,
                            name: str,
                            description: str,
                            file_path: str,
                            code_type: str,
                            code_snippet: Optional[str] = None) -> None:
        """
        Log a newly created pattern to Tier 2
        
        When CREATE action is taken, this logs the new pattern
        so it can be reused in the future.
        
        Args:
            pattern_id: Unique pattern identifier
            name: Pattern name
            description: What the pattern does
            file_path: Where the pattern is implemented
            code_type: Type of pattern
            code_snippet: Optional code sample
        """
        if not self._conn:
            self.connect()
        
        try:
            self._conn.execute("""
                INSERT INTO patterns 
                (pattern_id, name, description, file_path, code_snippet, 
                 category, confidence, usage_count, last_used, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern_id,
                name,
                description,
                file_path,
                code_snippet,
                code_type,
                0.80,  # Initial confidence for new patterns
                1,  # Usage count starts at 1
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            self._conn.commit()
            
        except sqlite3.OperationalError:
            # Table doesn't exist yet - will be created in Task 3.2
            pass


# Usage Example
if __name__ == "__main__":
    # Example: Check for existing invoice export pattern before creating new one
    
    enforcer = PatternSearchEnforcer()
    
    result = enforcer.search_before_create(
        intent="export invoice to PDF with custom template",
        code_type="service_method",
        context={
            'module': 'billing',
            'dependencies': ['PDFGenerator', 'InvoiceTemplate']
        }
    )
    
    print(f"Action: {result.action}")
    print(f"Message: {result.message}")
    print(f"Search time: {result.search_time_ms:.1f}ms")
    
    if result.action == "REUSE":
        print(f"\nRecommended pattern: {result.pattern.name}")
        print(f"Confidence: {result.pattern.confidence:.0%}")
        print(f"Location: {result.pattern.file_path}")
        print(f"Used {result.pattern.usage_count} times")
        
        if result.alternatives:
            print(f"\nAlternatives:")
            for alt in result.alternatives:
                print(f"  - {alt.name} ({alt.confidence:.0%})")
    else:
        print("\nCreating new pattern...")
        print("Don't forget to log this pattern for future reuse!")
    
    # Get reuse statistics
    stats = enforcer.get_reuse_statistics(days=30)
    print(f"\n30-day Pattern Reuse Statistics:")
    print(f"  Total searches: {stats['total_searches']}")
    print(f"  Reused: {stats['reuse_count']}")
    print(f"  Created new: {stats['create_count']}")
    print(f"  Reuse rate: {stats['reuse_rate']:.1f}%")
    
    enforcer.disconnect()
