"""
CORTEX Knowledge Archive - Personal Cross-Project Learning System

Your personal archive of proven solutions across all projects.

This module manages your knowledge archive - a persistent memory of:
- Successful patterns you've used
- Mistakes you've learned from (anti-patterns)
- PR decisions and their outcomes
- Solutions that worked (and didn't work)

Think of it as "collaborating with Future You" - capture knowledge once,
reuse it forever across all your projects.
"""

import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from dataclasses import dataclass, asdict


@dataclass
class ArchivedPattern:
    """Represents a proven pattern from your past work"""
    pattern_id: str
    pattern_type: str  # workflow, architectural, principle, implementation
    title: str
    description: str
    
    # Confidence & Usage (how well did it work?)
    confidence: float
    usage_count: int = 1
    success_count: int = 0
    failure_count: int = 0
    
    # Archive Metadata
    scope: str = 'personal'  # Your personal archive
    project_name: str = ''   # Which project was this from?
    archived_date: str = ''
    
    # References (where did you use this?)
    pr_references: List[str] = None      # Which PRs used this pattern?
    conversation_links: List[str] = None # Which conversations discussed it?
    
    # Search
    keywords: str = ''
    
    # Timestamps
    created_at: str = ''
    last_used: str = ''
    
    def __post_init__(self):
        if self.pr_references is None:
            self.pr_references = []
        if self.conversation_links is None:
            self.conversation_links = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.last_used:
            self.last_used = datetime.now().isoformat()
        if not self.archived_date:
            self.archived_date = datetime.now().isoformat()


@dataclass
class ArchivedAntiPattern:
    """Represents a mistake you've learned from (what NOT to do)"""
    antipattern_id: str
    antipattern_type: str
    title: str
    description: str
    why_it_failed: str  # Why didn't this work?
    
    # Confidence & Frequency (how sure are you this is bad?)
    confidence: float
    times_encountered: int = 1
    
    # Archive Metadata
    project_name: str = ''      # Where did this fail?
    learned_date: str = ''
    
    # References (where did you encounter this?)
    pr_references: List[str] = None      # Which PRs had this problem?
    similar_patterns: List[str] = None   # Other patterns to avoid
    
    # Timestamps
    created_at: str = ''
    
    def __post_init__(self):
        if self.pr_references is None:
            self.pr_references = []
        if self.similar_patterns is None:
            self.similar_patterns = []
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        if not self.learned_date:
            self.learned_date = datetime.now().isoformat()


class CortexKnowledgeArchive:
    """
    Your Personal Knowledge Archive - Learn Once, Use Forever
    
    Features:
    - Archive successful patterns from your projects
    - Remember mistakes you've made (anti-patterns)
    - Search across all your past work
    - Track what worked and what didn't
    - Cross-project pattern reuse
    
    Benefits:
    - Never rediscover the same solution twice
    - Avoid repeating past mistakes
    - Build your personal "second brain"
    - Accelerate future work with proven patterns
    """
    
    def __init__(self, db_path: str):
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize knowledge archive database schema"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Archived Patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archived_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                
                -- Confidence & Usage
                confidence REAL NOT NULL,
                usage_count INTEGER DEFAULT 1,
                success_count INTEGER DEFAULT 0,
                failure_count INTEGER DEFAULT 0,
                
                -- Archive Metadata
                scope TEXT DEFAULT 'personal',
                project_name TEXT,
                archived_date TEXT,
                
                -- References
                pr_references TEXT,  -- JSON array
                conversation_links TEXT,  -- JSON array
                
                -- Search
                keywords TEXT,
                
                -- Timestamps
                created_at TEXT,
                last_used TEXT
            )
        """)
        
        # Full-text search index for patterns
        cursor.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS archived_patterns_fts USING fts5(
                title, 
                description, 
                keywords,
                content='archived_patterns',
                content_rowid='rowid'
            )
        """)
        
        # Archived Anti-patterns table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archived_antipatterns (
                antipattern_id TEXT PRIMARY KEY,
                antipattern_type TEXT NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                why_it_failed TEXT,
                
                -- Confidence & Frequency
                confidence REAL NOT NULL,
                times_encountered INTEGER DEFAULT 1,
                
                -- Archive Metadata
                project_name TEXT,
                learned_date TEXT,
                
                -- References
                pr_references TEXT,  -- JSON array
                similar_patterns TEXT,  -- JSON array
                
                -- Timestamps
                created_at TEXT
            )
        """)
        
        # Archive Statistics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS archive_stats (
                stat_id TEXT PRIMARY KEY,
                stat_type TEXT NOT NULL,
                stat_name TEXT NOT NULL,
                stat_value REAL,
                metadata TEXT,  -- JSON
                recorded_at TEXT
            )
        """)
        
        # Projects table (track which projects you've archived knowledge from)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS projects (
                project_id TEXT PRIMARY KEY,
                project_name TEXT UNIQUE,
                first_archived TEXT,
                last_archived TEXT,
                pattern_count INTEGER DEFAULT 0,
                antipattern_count INTEGER DEFAULT 0
            )
        """)
        
        conn.commit()
        conn.close()
    
    def add_pattern(self, pattern: ArchivedPattern) -> bool:
        """Archive a successful pattern for future reference"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO archived_patterns 
                (pattern_id, pattern_type, title, description, confidence, 
                 usage_count, success_count, failure_count, scope, project_name,
                 archived_date, pr_references, conversation_links, 
                 keywords, created_at, last_used)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                pattern.pattern_id, pattern.pattern_type, pattern.title,
                pattern.description, pattern.confidence, pattern.usage_count,
                pattern.success_count, pattern.failure_count, pattern.scope,
                pattern.project_name, pattern.archived_date,
                json.dumps(pattern.pr_references),
                json.dumps(pattern.conversation_links), pattern.keywords,
                pattern.created_at, pattern.last_used
            ))
            
            # Update FTS index
            cursor.execute("""
                INSERT OR REPLACE INTO archived_patterns_fts(rowid, title, description, keywords)
                VALUES (
                    (SELECT rowid FROM archived_patterns WHERE pattern_id = ?),
                    ?, ?, ?
                )
            """, (pattern.pattern_id, pattern.title, pattern.description, pattern.keywords))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error archiving pattern: {e}")
            return False
    
    def add_antipattern(self, antipattern: ArchivedAntiPattern) -> bool:
        """Archive a mistake you've learned from"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO archived_antipatterns
                (antipattern_id, antipattern_type, title, description, why_it_failed,
                 confidence, times_encountered, project_name, learned_date,
                 pr_references, similar_patterns, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                antipattern.antipattern_id, antipattern.antipattern_type,
                antipattern.title, antipattern.description, antipattern.why_it_failed,
                antipattern.confidence, antipattern.times_encountered,
                antipattern.project_name, antipattern.learned_date,
                json.dumps(antipattern.pr_references),
                json.dumps(antipattern.similar_patterns), antipattern.created_at
            ))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error archiving anti-pattern: {e}")
            return False
    
    def search_patterns(self, query: str, pattern_type: Optional[str] = None, 
                       limit: int = 10) -> List[ArchivedPattern]:
        """
        Search your archived patterns using full-text search.
        Returns patterns sorted by relevance and confidence.
        """
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Build query
        sql = """
            SELECT p.* FROM archived_patterns p
            INNER JOIN archived_patterns_fts fts ON p.rowid = fts.rowid
            WHERE archived_patterns_fts MATCH ?
        """
        params = [query]
        
        if pattern_type:
            sql += " AND p.pattern_type = ?"
            params.append(pattern_type)
        
        sql += " ORDER BY p.confidence DESC, p.usage_count DESC LIMIT ?"
        params.append(limit)
        
        cursor.execute(sql, params)
        
        patterns = []
        for row in cursor.fetchall():
            patterns.append(ArchivedPattern(
                pattern_id=row[0],
                pattern_type=row[1],
                title=row[2],
                description=row[3],
                confidence=row[4],
                usage_count=row[5],
                success_count=row[6],
                failure_count=row[7],
                scope=row[8],
                project_name=row[9],
                archived_date=row[10],
                pr_references=json.loads(row[11]) if row[11] else [],
                conversation_links=json.loads(row[12]) if row[12] else [],
                keywords=row[13],
                created_at=row[14],
                last_used=row[15]
            ))
        
        conn.close()
        return patterns
    
    def get_pattern(self, pattern_id: str) -> Optional[ArchivedPattern]:
        """Get a specific archived pattern by ID"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM archived_patterns WHERE pattern_id = ?", (pattern_id,))
        row = cursor.fetchone()
        
        if not row:
            conn.close()
            return None
        
        pattern = ArchivedPattern(
            pattern_id=row[0],
            pattern_type=row[1],
            title=row[2],
            description=row[3],
            confidence=row[4],
            usage_count=row[5],
            success_count=row[6],
            failure_count=row[7],
            scope=row[8],
            project_name=row[9],
            archived_date=row[10],
            pr_references=json.loads(row[11]) if row[11] else [],
            conversation_links=json.loads(row[12]) if row[12] else [],
            keywords=row[13],
            created_at=row[14],
            last_used=row[15]
        )
        
        conn.close()
        return pattern
    
    def increment_pattern_usage(self, pattern_id: str, success: bool = True) -> bool:
        """Track when you reuse a pattern (and whether it worked)"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            field = "success_count" if success else "failure_count"
            cursor.execute(f"""
                UPDATE archived_patterns 
                SET usage_count = usage_count + 1,
                    {field} = {field} + 1,
                    last_used = ?
                WHERE pattern_id = ?
            """, (datetime.now().isoformat(), pattern_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error tracking pattern usage: {e}")
            return False
    
    def get_archive_statistics(self) -> Dict[str, Any]:
        """Get statistics about your knowledge archive"""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Count patterns
        cursor.execute("SELECT COUNT(*) FROM archived_patterns")
        pattern_count = cursor.fetchone()[0]
        
        # Count anti-patterns
        cursor.execute("SELECT COUNT(*) FROM archived_antipatterns")
        antipattern_count = cursor.fetchone()[0]
        
        # Average confidence
        cursor.execute("SELECT AVG(confidence) FROM archived_patterns")
        avg_confidence = cursor.fetchone()[0] or 0.0
        
        # Most used patterns
        cursor.execute("""
            SELECT pattern_id, title, usage_count, project_name
            FROM archived_patterns 
            ORDER BY usage_count DESC 
            LIMIT 5
        """)
        top_patterns = [
            {"id": row[0], "title": row[1], "usage": row[2], "from_project": row[3]}
            for row in cursor.fetchall()
        ]
        
        # Project count
        cursor.execute("SELECT COUNT(*) FROM projects")
        project_count = cursor.fetchone()[0]
        
        # Success rate
        cursor.execute("""
            SELECT 
                SUM(success_count) as total_success,
                SUM(failure_count) as total_failure
            FROM archived_patterns
        """)
        success, failure = cursor.fetchone()
        success_rate = (success / (success + failure) * 100) if (success + failure) > 0 else 0
        
        conn.close()
        
        return {
            "total_patterns": pattern_count,
            "total_antipatterns": antipattern_count,
            "average_confidence": round(avg_confidence, 2),
            "success_rate": round(success_rate, 1),
            "top_patterns": top_patterns,
            "projects_tracked": project_count,
            "total_reuses": success + failure if success and failure else 0
        }
    
    def add_project(self, project_id: str, project_name: str) -> bool:
        """Register a project in your archive"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO projects
                (project_id, project_name, first_archived, last_archived, 
                 pattern_count, antipattern_count)
                VALUES (?, ?, ?, ?, 0, 0)
            """, (project_id, project_name, datetime.now().isoformat(), 
                  datetime.now().isoformat()))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error adding project: {e}")
            return False
    
    def update_project_stats(self, project_id: str) -> bool:
        """Update project statistics"""
        try:
            conn = sqlite3.connect(str(self.db_path))
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE projects
                SET last_archived = ?,
                    pattern_count = (SELECT COUNT(*) FROM archived_patterns WHERE project_name = 
                                    (SELECT project_name FROM projects WHERE project_id = ?)),
                    antipattern_count = (SELECT COUNT(*) FROM archived_antipatterns WHERE project_name = 
                                        (SELECT project_name FROM projects WHERE project_id = ?))
                WHERE project_id = ?
            """, (datetime.now().isoformat(), project_id, project_id, project_id))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            print(f"Error updating project stats: {e}")
            return False
