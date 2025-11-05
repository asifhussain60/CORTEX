# Phase 2: Tier 2 (Knowledge Graph - Long-Term Memory)

**Version:** 1.0  
**Date:** 2025-11-05  
**Duration:** 10-12 hours + 1 hour holistic review  
**Dependencies:** Phase 0 + Phase 1 complete + reviewed  
**Storage:** SQLite (`cortex-brain.db` → `knowledge` schema + FTS5)  
**Performance Target:** <100ms pattern queries, <200ms FTS5 search

---

## 🎯 Overview

**Purpose:** Build the long-term memory layer that learns from conversations and accumulates wisdom over time. This tier consolidates patterns from deleted Tier 1 conversations and enables intelligent recommendations.

**Key Deliverables:**
- Pattern learning engine (intent, file relationships, workflows)
- FTS5 full-text search for pattern matching
- Confidence scoring and decay system
- Pattern consolidation from Tier 1 FIFO deletion
- Recommendation engine for agents
- Complete test coverage (28 unit + 6 integration tests)

---

## 📊 What We're Building

### Database Schema (from unified-database-schema.sql)

```sql
-- Knowledge Patterns (with FTS5 for fast text search)
CREATE VIRTUAL TABLE knowledge_patterns USING fts5(
    pattern_id UNINDEXED,
    pattern_type,                       -- intent, file_relationship, workflow, etc.
    pattern_content,                    -- Searchable text description
    keywords,                           -- Comma-separated keywords
    tokenize = 'porter'                 -- Stemming for better search
);

-- Pattern Metadata (relational data)
CREATE TABLE knowledge_pattern_metadata (
    pattern_id TEXT PRIMARY KEY,
    pattern_type TEXT NOT NULL,         -- intent, file_relationship, workflow
    confidence REAL DEFAULT 0.5 CHECK(confidence BETWEEN 0 AND 1),
    success_count INTEGER DEFAULT 0,
    total_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_used TIMESTAMP,
    decay_started BOOLEAN DEFAULT FALSE,
    pinned BOOLEAN DEFAULT FALSE        -- Prevent decay
);

-- File Relationships (which files are modified together)
CREATE TABLE knowledge_file_relationships (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    from_file TEXT NOT NULL,
    to_file TEXT NOT NULL,
    relationship_type TEXT NOT NULL,    -- co_modified, imports, tests, etc.
    confidence REAL DEFAULT 0.5,
    occurrence_count INTEGER DEFAULT 1,
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(from_file, to_file, relationship_type)
);

-- Intent Patterns (which phrases trigger which intents)
CREATE TABLE knowledge_intent_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    phrase TEXT NOT NULL UNIQUE,
    intent TEXT NOT NULL,               -- PLAN, EXECUTE, TEST, etc.
    confidence REAL DEFAULT 0.5,
    success_count INTEGER DEFAULT 0,
    total_count INTEGER DEFAULT 0,
    last_used TIMESTAMP
);

-- Workflow Patterns (successful task sequences)
CREATE TABLE knowledge_workflow_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    workflow_name TEXT NOT NULL UNIQUE,
    workflow_type TEXT,                 -- test_first, feature_creation, etc.
    steps TEXT NOT NULL,                -- JSON array of steps
    success_rate REAL DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    average_duration_hours REAL,
    last_used TIMESTAMP
);

-- Architectural Patterns (project structure learnings)
CREATE TABLE knowledge_architectural_patterns (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pattern_name TEXT NOT NULL UNIQUE,
    pattern_type TEXT,                  -- service_layer, component_structure, etc.
    description TEXT,
    confidence REAL DEFAULT 0.5,
    examples TEXT,                      -- JSON array of example paths
    discovered_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_kp_metadata_type ON knowledge_pattern_metadata(pattern_type);
CREATE INDEX idx_kp_metadata_confidence ON knowledge_pattern_metadata(confidence DESC);
CREATE INDEX idx_kp_metadata_last_used ON knowledge_pattern_metadata(last_used DESC);
CREATE INDEX idx_kfr_from_file ON knowledge_file_relationships(from_file);
CREATE INDEX idx_kfr_to_file ON knowledge_file_relationships(to_file);
CREATE INDEX idx_kfr_confidence ON knowledge_file_relationships(confidence DESC);
CREATE INDEX idx_kip_intent ON knowledge_intent_patterns(intent);
CREATE INDEX idx_kwp_type ON knowledge_workflow_patterns(workflow_type);
```

---

## 🏗️ Implementation Tasks

### Task 1: Knowledge Graph Engine Core
**File:** `CORTEX/src/tier2/knowledge_graph_engine.py`  
**Duration:** 2.5 hours  
**Tests:** 6 unit tests

**Description:**
Core pattern storage and retrieval with FTS5 search.

**Implementation Details:**
```python
import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime

class KnowledgeGraphEngine:
    """Tier 2: Long-term memory with pattern learning"""
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        self.db_path = db_path
    
    def store_pattern(self, pattern_type: str, content: str, 
                     keywords: List[str], confidence: float = 0.5) -> str:
        """
        Store new pattern in knowledge graph
        
        Args:
            pattern_type: intent, file_relationship, workflow, etc.
            content: Searchable text description
            keywords: List of keywords for FTS5 search
            confidence: Initial confidence score (0-1)
        
        Returns:
            pattern_id: UUID of stored pattern
        """
        import uuid
        
        pattern_id = str(uuid.uuid4())
        conn = sqlite3.connect(self.db_path)
        
        # Insert into FTS5 table (searchable)
        conn.execute("""
            INSERT INTO knowledge_patterns 
            (pattern_id, pattern_type, pattern_content, keywords)
            VALUES (?, ?, ?, ?)
        """, (pattern_id, pattern_type, content, ','.join(keywords)))
        
        # Insert metadata (relational)
        conn.execute("""
            INSERT INTO knowledge_pattern_metadata
            (pattern_id, pattern_type, confidence, created_at)
            VALUES (?, ?, ?, ?)
        """, (pattern_id, pattern_type, confidence, datetime.now()))
        
        conn.commit()
        conn.close()
        
        return pattern_id
    
    def search_patterns(self, query: str, pattern_type: Optional[str] = None,
                       limit: int = 10) -> List[Dict]:
        """
        Full-text search for patterns using FTS5
        
        Args:
            query: Search query (FTS5 syntax supported)
            pattern_type: Filter by type (optional)
            limit: Max results
        
        Returns:
            List of matching patterns with metadata
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        if pattern_type:
            sql = """
                SELECT p.pattern_id, p.pattern_type, p.pattern_content, p.keywords,
                       m.confidence, m.last_used, m.success_count
                FROM knowledge_patterns p
                JOIN knowledge_pattern_metadata m ON p.pattern_id = m.pattern_id
                WHERE knowledge_patterns MATCH ? AND p.pattern_type = ?
                ORDER BY rank, m.confidence DESC
                LIMIT ?
            """
            cursor = conn.execute(sql, (query, pattern_type, limit))
        else:
            sql = """
                SELECT p.pattern_id, p.pattern_type, p.pattern_content, p.keywords,
                       m.confidence, m.last_used, m.success_count
                FROM knowledge_patterns p
                JOIN knowledge_pattern_metadata m ON p.pattern_id = m.pattern_id
                WHERE knowledge_patterns MATCH ?
                ORDER BY rank, m.confidence DESC
                LIMIT ?
            """
            cursor = conn.execute(sql, (query, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_pattern_by_id(self, pattern_id: str) -> Optional[Dict]:
        """Get pattern by ID"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT p.pattern_id, p.pattern_type, p.pattern_content, p.keywords,
                   m.confidence, m.success_count, m.total_count, m.last_used
            FROM knowledge_patterns p
            JOIN knowledge_pattern_metadata m ON p.pattern_id = m.pattern_id
            WHERE p.pattern_id = ?
        """, (pattern_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        return dict(row) if row else None
    
    def update_pattern_confidence(self, pattern_id: str, success: bool):
        """
        Update pattern confidence based on usage outcome
        
        Uses Bayesian updating: confidence = successes / total_attempts
        """
        conn = sqlite3.connect(self.db_path)
        
        if success:
            conn.execute("""
                UPDATE knowledge_pattern_metadata
                SET success_count = success_count + 1,
                    total_count = total_count + 1,
                    last_used = ?
                WHERE pattern_id = ?
            """, (datetime.now(), pattern_id))
        else:
            conn.execute("""
                UPDATE knowledge_pattern_metadata
                SET total_count = total_count + 1,
                    last_used = ?
                WHERE pattern_id = ?
            """, (datetime.now(), pattern_id))
        
        # Recalculate confidence
        cursor = conn.execute("""
            SELECT success_count, total_count FROM knowledge_pattern_metadata
            WHERE pattern_id = ?
        """, (pattern_id,))
        
        row = cursor.fetchone()
        if row and row[1] > 0:  # total_count > 0
            new_confidence = row[0] / row[1]  # success_count / total_count
            
            conn.execute("""
                UPDATE knowledge_pattern_metadata
                SET confidence = ?
                WHERE pattern_id = ?
            """, (new_confidence, pattern_id))
        
        conn.commit()
        conn.close()
    
    def get_high_confidence_patterns(self, pattern_type: str, 
                                     min_confidence: float = 0.7,
                                     limit: int = 10) -> List[Dict]:
        """Get patterns with confidence above threshold"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT p.pattern_id, p.pattern_type, p.pattern_content, p.keywords,
                   m.confidence, m.success_count, m.last_used
            FROM knowledge_patterns p
            JOIN knowledge_pattern_metadata m ON p.pattern_id = m.pattern_id
            WHERE m.pattern_type = ? AND m.confidence >= ?
            ORDER BY m.confidence DESC, m.last_used DESC
            LIMIT ?
        """, (pattern_type, min_confidence, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
```

**Success Criteria:**
- [ ] Patterns stored in FTS5 + metadata tables
- [ ] Full-text search works (<100ms)
- [ ] Confidence updates via Bayesian formula
- [ ] High-confidence pattern queries work

---

### Task 2: Pattern Extractor (Tier 1 Integration)
**File:** `CORTEX/src/tier2/pattern_extractor.py`  
**Duration:** 2 hours  
**Tests:** 5 unit tests

**Description:**
Extract patterns from Tier 1 conversations before FIFO deletion.

**Implementation Details:**
```python
from typing import List, Dict
import sqlite3
from collections import Counter

class PatternExtractor:
    """Extract learnable patterns from conversations"""
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        self.db_path = db_path
    
    def extract_intent_pattern(self, conversation_id: str) -> Optional[Dict]:
        """
        Extract intent pattern from conversation
        
        Learns: "add [X]" → PLAN, "continue" → EXECUTE, etc.
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get first user message (contains intent)
        cursor = conn.execute("""
            SELECT content FROM working_memory_messages
            WHERE conversation_id = ? AND role = 'user'
            ORDER BY sequence ASC
            LIMIT 1
        """, (conversation_id,))
        
        row = cursor.fetchone()
        if not row:
            conn.close()
            return None
        
        first_message = row[0].lower()
        
        # Get conversation intent
        cursor = conn.execute("""
            SELECT intent FROM working_memory_conversations
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        intent_row = cursor.fetchone()
        conn.close()
        
        if not intent_row:
            return None
        
        intent = intent_row[0]
        
        # Extract key phrases
        phrases = self._extract_key_phrases(first_message)
        
        return {
            'phrases': phrases,
            'intent': intent,
            'confidence': 0.6  # Initial confidence
        }
    
    def extract_file_relationships(self, conversation_id: str) -> List[Dict]:
        """
        Extract file co-modification patterns
        
        Learns: HostControlPanel.razor often modified with noor-canvas.css
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get all file entities mentioned
        cursor = conn.execute("""
            SELECT entity_value FROM working_memory_entities
            WHERE conversation_id = ? AND entity_type = 'file'
            ORDER BY first_mentioned ASC
        """, (conversation_id,))
        
        files = [row[0] for row in cursor.fetchall()]
        conn.close()
        
        if len(files) < 2:
            return []  # Need at least 2 files for relationship
        
        # Create co-modification pairs
        relationships = []
        for i, file1 in enumerate(files):
            for file2 in files[i+1:]:
                relationships.append({
                    'from_file': file1,
                    'to_file': file2,
                    'relationship_type': 'co_modified',
                    'confidence': 0.5
                })
        
        return relationships
    
    def extract_workflow_pattern(self, conversation_id: str) -> Optional[Dict]:
        """
        Extract workflow pattern (sequence of steps)
        
        Learns: Test-first workflow, feature creation workflow, etc.
        """
        conn = sqlite3.connect(self.db_path)
        
        # Get all messages to analyze workflow
        cursor = conn.execute("""
            SELECT role, content, sequence FROM working_memory_messages
            WHERE conversation_id = ?
            ORDER BY sequence ASC
        """, (conversation_id,))
        
        messages = cursor.fetchall()
        
        # Get conversation outcome
        cursor = conn.execute("""
            SELECT outcome, title FROM working_memory_conversations
            WHERE conversation_id = ?
        """, (conversation_id,))
        
        conv = cursor.fetchone()
        conn.close()
        
        if not conv or not conv[0]:
            return None
        
        outcome = conv[0]
        title = conv[1]
        
        # Detect workflow type from messages
        workflow_type = self._detect_workflow_type(messages)
        
        if not workflow_type:
            return None
        
        # Extract steps
        steps = self._extract_workflow_steps(messages, workflow_type)
        
        return {
            'workflow_name': f"{workflow_type}_{conversation_id[:8]}",
            'workflow_type': workflow_type,
            'steps': steps,
            'outcome': outcome,
            'title': title
        }
    
    def _extract_key_phrases(self, message: str) -> List[str]:
        """Extract key phrases from message"""
        # Simple extraction (can be enhanced with NLP)
        phrases = []
        
        # Extract action verbs + objects
        patterns = [
            r'(add|create|build|implement) ([a-z ]+)',
            r'(fix|debug|resolve) ([a-z ]+)',
            r'(test|verify|validate) ([a-z ]+)',
            r'(plan|design) ([a-z ]+)'
        ]
        
        import re
        for pattern in patterns:
            matches = re.findall(pattern, message)
            phrases.extend([f"{verb} {obj}" for verb, obj in matches])
        
        return phrases[:5]  # Top 5 phrases
    
    def _detect_workflow_type(self, messages: List[tuple]) -> Optional[str]:
        """Detect workflow type from message sequence"""
        content_concat = ' '.join([msg[1].lower() for msg in messages])
        
        if 'test' in content_concat and 'red' in content_concat:
            return 'test_first_tdd'
        
        if 'plan' in content_concat and 'phase' in content_concat:
            return 'multi_phase_planning'
        
        if 'fix' in content_concat or 'bug' in content_concat:
            return 'bug_fix'
        
        if 'feature' in content_concat or 'add' in content_concat:
            return 'feature_creation'
        
        return None
    
    def _extract_workflow_steps(self, messages: List[tuple], 
                               workflow_type: str) -> List[str]:
        """Extract workflow steps from messages"""
        steps = []
        
        # Extract from assistant messages (execution steps)
        for role, content, seq in messages:
            if role == 'assistant':
                # Extract steps (simple heuristic)
                if '1.' in content or 'Step' in content:
                    lines = content.split('\n')
                    steps.extend([l.strip() for l in lines if l.strip().startswith(('1.', '2.', '3.', 'Step'))])
        
        return steps[:10]  # Max 10 steps
    
    def extract_all_patterns(self, conversation_id: str) -> Dict:
        """
        Extract all patterns from conversation (called before FIFO deletion)
        
        Returns:
            Dict with intent, file_relationships, workflow patterns
        """
        return {
            'intent': self.extract_intent_pattern(conversation_id),
            'file_relationships': self.extract_file_relationships(conversation_id),
            'workflow': self.extract_workflow_pattern(conversation_id)
        }
```

**Success Criteria:**
- [ ] Intent patterns extracted from first message
- [ ] File relationships detected from entity data
- [ ] Workflow patterns identified (TDD, planning, etc.)
- [ ] All patterns ready for storage in Tier 2

---

### Task 3: File Relationship Manager
**File:** `CORTEX/src/tier2/file_relationship_manager.py`  
**Duration:** 1.5 hours  
**Tests:** 4 unit tests

**Description:**
Track which files are frequently modified together.

**Implementation Details:**
```python
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

class FileRelationshipManager:
    """Manage file co-modification relationships"""
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        self.db_path = db_path
    
    def record_relationship(self, from_file: str, to_file: str,
                          relationship_type: str = 'co_modified'):
        """
        Record file relationship (idempotent)
        
        If exists: Increment occurrence_count, update last_seen
        If new: Create record
        """
        conn = sqlite3.connect(self.db_path)
        
        # Check if exists
        cursor = conn.execute("""
            SELECT id, occurrence_count FROM knowledge_file_relationships
            WHERE from_file = ? AND to_file = ? AND relationship_type = ?
        """, (from_file, to_file, relationship_type))
        
        existing = cursor.fetchone()
        
        if existing:
            # Increment occurrence, update confidence
            new_count = existing[1] + 1
            new_confidence = min(0.95, 0.5 + (new_count * 0.05))  # Cap at 0.95
            
            conn.execute("""
                UPDATE knowledge_file_relationships
                SET occurrence_count = ?,
                    confidence = ?,
                    last_seen = ?
                WHERE id = ?
            """, (new_count, new_confidence, datetime.now(), existing[0]))
        else:
            # Create new relationship
            conn.execute("""
                INSERT INTO knowledge_file_relationships
                (from_file, to_file, relationship_type, confidence, occurrence_count, first_seen, last_seen)
                VALUES (?, ?, ?, 0.5, 1, ?, ?)
            """, (from_file, to_file, relationship_type, datetime.now(), datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_related_files(self, file: str, min_confidence: float = 0.6,
                         limit: int = 5) -> List[Dict]:
        """
        Get files frequently modified with the given file
        
        Example: "HostControlPanel.razor" → Returns noor-canvas.css (75% confidence)
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT to_file, relationship_type, confidence, occurrence_count, last_seen
            FROM knowledge_file_relationships
            WHERE from_file = ? AND confidence >= ?
            ORDER BY confidence DESC, occurrence_count DESC
            LIMIT ?
        """, (file, min_confidence, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
    
    def get_all_relationships(self, min_confidence: float = 0.6) -> List[Dict]:
        """Get all file relationships above confidence threshold"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT from_file, to_file, relationship_type, confidence, occurrence_count
            FROM knowledge_file_relationships
            WHERE confidence >= ?
            ORDER BY confidence DESC
        """, (min_confidence,))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
```

**Success Criteria:**
- [ ] Relationships recorded (idempotent)
- [ ] Confidence increases with occurrence_count
- [ ] Related files query works (<50ms)
- [ ] Confidence threshold filtering accurate

---

### Task 4: Intent Pattern Manager
**File:** `CORTEX/src/tier2/intent_pattern_manager.py`  
**Duration:** 1.5 hours  
**Tests:** 4 unit tests

**Description:**
Learn which phrases trigger which intents.

**Implementation Details:**
```python
import sqlite3
from typing import List, Dict, Optional
from datetime import datetime

class IntentPatternManager:
    """Manage intent recognition patterns"""
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        self.db_path = db_path
    
    def record_intent_pattern(self, phrase: str, intent: str, success: bool = True):
        """
        Record intent pattern with outcome
        
        Learns: "add purple button" → PLAN (95% confidence)
        """
        conn = sqlite3.connect(self.db_path)
        
        # Normalize phrase (lowercase, trim)
        phrase_normalized = phrase.lower().strip()
        
        # Check if exists
        cursor = conn.execute("""
            SELECT id, success_count, total_count FROM knowledge_intent_patterns
            WHERE phrase = ?
        """, (phrase_normalized,))
        
        existing = cursor.fetchone()
        
        if existing:
            # Update counts
            new_success = existing[1] + (1 if success else 0)
            new_total = existing[2] + 1
            new_confidence = new_success / new_total if new_total > 0 else 0.5
            
            conn.execute("""
                UPDATE knowledge_intent_patterns
                SET success_count = ?,
                    total_count = ?,
                    confidence = ?,
                    last_used = ?
                WHERE id = ?
            """, (new_success, new_total, new_confidence, datetime.now(), existing[0]))
        else:
            # Create new pattern
            conn.execute("""
                INSERT INTO knowledge_intent_patterns
                (phrase, intent, confidence, success_count, total_count, last_used)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (phrase_normalized, intent, 
                 1.0 if success else 0.5, 
                 1 if success else 0, 
                 1, 
                 datetime.now()))
        
        conn.commit()
        conn.close()
    
    def match_intent(self, phrase: str, min_confidence: float = 0.7) -> Optional[str]:
        """
        Match phrase to intent
        
        Returns:
            intent: PLAN, EXECUTE, TEST, etc. (if confidence >= threshold)
            None: No high-confidence match
        """
        conn = sqlite3.connect(self.db_path)
        phrase_normalized = phrase.lower().strip()
        
        # Exact match first
        cursor = conn.execute("""
            SELECT intent, confidence FROM knowledge_intent_patterns
            WHERE phrase = ? AND confidence >= ?
            ORDER BY confidence DESC
            LIMIT 1
        """, (phrase_normalized, min_confidence))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return row[0]  # intent
        
        # TODO: Fuzzy matching (Phase 4 - use FTS5 similarity)
        return None
    
    def get_patterns_by_intent(self, intent: str, min_confidence: float = 0.7,
                              limit: int = 10) -> List[Dict]:
        """Get all patterns for specific intent"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT phrase, intent, confidence, success_count, total_count
            FROM knowledge_intent_patterns
            WHERE intent = ? AND confidence >= ?
            ORDER BY confidence DESC, total_count DESC
            LIMIT ?
        """, (intent, min_confidence, limit))
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
```

**Success Criteria:**
- [ ] Intent patterns recorded with success/failure
- [ ] Confidence calculated via success_count / total_count
- [ ] Intent matching works with threshold
- [ ] Patterns queryable by intent

---

### Task 5: Confidence Decay System
**File:** `CORTEX/src/tier2/confidence_decay.py`  
**Duration:** 1.5 hours  
**Tests:** 5 unit tests

**Description:**
Implement Rule #12 (pattern confidence decay for unused patterns).

**Implementation Details:**
```python
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict

class ConfidenceDecaySystem:
    """Manage pattern confidence decay (Rule #12)"""
    
    # Decay rules from governance Rule #12
    DECAY_RULES = {
        'unused_60_days': {'threshold_days': 60, 'decay_percent': 10},
        'unused_90_days': {'threshold_days': 90, 'decay_percent': 25},
        'unused_120_days': {'threshold_days': 120, 'action': 'mark_for_deletion'},
        'confidence_below_30': {'threshold': 0.30, 'action': 'auto_delete'}
    }
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        self.db_path = db_path
    
    def apply_decay(self) -> Dict[str, int]:
        """
        Apply confidence decay to unused patterns
        
        Returns:
            Stats: {decayed_count, deleted_count, marked_count}
        """
        stats = {
            'decayed_60': 0,
            'decayed_90': 0,
            'marked_120': 0,
            'deleted_low_confidence': 0
        }
        
        conn = sqlite3.connect(self.db_path)
        now = datetime.now()
        
        # Get all non-pinned patterns
        cursor = conn.execute("""
            SELECT pattern_id, last_used, confidence, pinned
            FROM knowledge_pattern_metadata
            WHERE pinned = FALSE
        """)
        
        patterns = cursor.fetchall()
        
        for pattern_id, last_used, confidence, pinned in patterns:
            if not last_used:
                continue
            
            last_used_dt = datetime.fromisoformat(last_used)
            days_unused = (now - last_used_dt).days
            
            # Apply decay rules
            if days_unused >= 120:
                # Mark for deletion
                conn.execute("""
                    UPDATE knowledge_pattern_metadata
                    SET decay_started = TRUE
                    WHERE pattern_id = ?
                """, (pattern_id,))
                stats['marked_120'] += 1
            
            elif days_unused >= 90:
                # Reduce confidence by 25%
                new_confidence = confidence * 0.75
                conn.execute("""
                    UPDATE knowledge_pattern_metadata
                    SET confidence = ?, decay_started = TRUE
                    WHERE pattern_id = ?
                """, (new_confidence, pattern_id))
                stats['decayed_90'] += 1
            
            elif days_unused >= 60:
                # Reduce confidence by 10%
                new_confidence = confidence * 0.90
                conn.execute("""
                    UPDATE knowledge_pattern_metadata
                    SET confidence = ?, decay_started = TRUE
                    WHERE pattern_id = ?
                """, (new_confidence, pattern_id))
                stats['decayed_60'] += 1
            
            # Check if confidence below threshold
            if confidence < 0.30:
                # Auto-delete
                self._delete_pattern(conn, pattern_id)
                stats['deleted_low_confidence'] += 1
        
        conn.commit()
        conn.close()
        
        return stats
    
    def _delete_pattern(self, conn: sqlite3.Connection, pattern_id: str):
        """Delete pattern from FTS5 and metadata"""
        conn.execute("""
            DELETE FROM knowledge_patterns WHERE pattern_id = ?
        """, (pattern_id,))
        
        conn.execute("""
            DELETE FROM knowledge_pattern_metadata WHERE pattern_id = ?
        """, (pattern_id,))
    
    def pin_pattern(self, pattern_id: str):
        """Pin pattern to prevent decay"""
        conn = sqlite3.connect(self.db_path)
        conn.execute("""
            UPDATE knowledge_pattern_metadata
            SET pinned = TRUE
            WHERE pattern_id = ?
        """, (pattern_id,))
        conn.commit()
        conn.close()
    
    def get_decay_candidates(self) -> List[Dict]:
        """Get patterns marked for decay/deletion"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT pattern_id, pattern_type, confidence, last_used, decay_started
            FROM knowledge_pattern_metadata
            WHERE decay_started = TRUE OR confidence < 0.30
            ORDER BY confidence ASC, last_used ASC
        """)
        
        results = [dict(row) for row in cursor.fetchall()]
        conn.close()
        
        return results
```

**Success Criteria:**
- [ ] 60-day decay reduces confidence by 10%
- [ ] 90-day decay reduces confidence by 25%
- [ ] 120-day marks for deletion
- [ ] <0.30 confidence triggers auto-delete
- [ ] Pinned patterns exempt from decay

---

### Task 6: Workflow Pattern Manager
**File:** `CORTEX/src/tier2/workflow_pattern_manager.py`  
**Duration:** 1.5 hours  
**Tests:** 4 unit tests

**Description:**
Track successful workflow patterns (TDD, feature creation, etc.).

**Implementation Details:**
```python
import sqlite3
import json
from typing import List, Dict, Optional
from datetime import datetime

class WorkflowPatternManager:
    """Manage workflow patterns (successful task sequences)"""
    
    def __init__(self, db_path: str = "cortex-brain.db"):
        self.db_path = db_path
    
    def record_workflow(self, workflow_name: str, workflow_type: str,
                       steps: List[str], success: bool = True,
                       duration_hours: Optional[float] = None):
        """
        Record workflow pattern with outcome
        
        Example:
            workflow_name: "test_first_fab_button"
            workflow_type: "test_first_tdd"
            steps: ["Write failing test", "Implement minimum code", "Refactor"]
            success: True
            duration_hours: 0.5
        """
        conn = sqlite3.connect(self.db_path)
        
        # Check if exists
        cursor = conn.execute("""
            SELECT id, usage_count, success_rate, average_duration_hours
            FROM knowledge_workflow_patterns
            WHERE workflow_name = ?
        """, (workflow_name,))
        
        existing = cursor.fetchone()
        
        steps_json = json.dumps(steps)
        
        if existing:
            # Update existing workflow
            old_usage = existing[1]
            old_success_rate = existing[2]
            old_avg_duration = existing[3] or 0
            
            new_usage = old_usage + 1
            new_success_rate = ((old_success_rate * old_usage) + (1 if success else 0)) / new_usage
            
            if duration_hours:
                new_avg_duration = ((old_avg_duration * old_usage) + duration_hours) / new_usage
            else:
                new_avg_duration = old_avg_duration
            
            conn.execute("""
                UPDATE knowledge_workflow_patterns
                SET usage_count = ?,
                    success_rate = ?,
                    average_duration_hours = ?,
                    last_used = ?
                WHERE id = ?
            """, (new_usage, new_success_rate, new_avg_duration, datetime.now(), existing[0]))
        else:
            # Create new workflow
            conn.execute("""
                INSERT INTO knowledge_workflow_patterns
                (workflow_name, workflow_type, steps, success_rate, usage_count, 
                 average_duration_hours, last_used)
                VALUES (?, ?, ?, ?, 1, ?, ?)
            """, (workflow_name, workflow_type, steps_json, 
                 1.0 if success else 0.0, 
                 duration_hours, 
                 datetime.now()))
        
        conn.commit()
        conn.close()
    
    def get_workflow_by_type(self, workflow_type: str, 
                            min_success_rate: float = 0.7) -> List[Dict]:
        """
        Get workflows by type with minimum success rate
        
        Example: Get all "test_first_tdd" workflows with >70% success
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT workflow_name, workflow_type, steps, success_rate, 
                   usage_count, average_duration_hours, last_used
            FROM knowledge_workflow_patterns
            WHERE workflow_type = ? AND success_rate >= ?
            ORDER BY success_rate DESC, usage_count DESC
        """, (workflow_type, min_success_rate))
        
        results = []
        for row in cursor.fetchall():
            result = dict(row)
            result['steps'] = json.loads(result['steps'])  # Parse JSON
            results.append(result)
        
        conn.close()
        return results
    
    def recommend_workflow(self, workflow_type: str) -> Optional[Dict]:
        """
        Recommend best workflow for type
        
        Returns workflow with highest success_rate * usage_count score
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        
        cursor = conn.execute("""
            SELECT workflow_name, workflow_type, steps, success_rate, 
                   usage_count, average_duration_hours
            FROM knowledge_workflow_patterns
            WHERE workflow_type = ?
            ORDER BY (success_rate * usage_count) DESC
            LIMIT 1
        """, (workflow_type,))
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            result = dict(row)
            result['steps'] = json.loads(result['steps'])
            return result
        
        return None
```

**Success Criteria:**
- [ ] Workflows recorded with steps (JSON)
- [ ] Success rate calculated (weighted average)
- [ ] Average duration tracked
- [ ] Recommendation engine works

---

## 📋 Test Plan (28 Unit + 6 Integration = 34 Total)

### Unit Tests (28 tests)

**KnowledgeGraphEngine (6 tests):**
- [ ] `test_store_pattern()` - Pattern stored in FTS5 + metadata
- [ ] `test_search_patterns()` - FTS5 search works
- [ ] `test_get_pattern_by_id()` - ID lookup works
- [ ] `test_update_confidence()` - Bayesian update accurate
- [ ] `test_get_high_confidence_patterns()` - Filtering works
- [ ] `test_fts5_ranking()` - Search ranking by relevance

**PatternExtractor (5 tests):**
- [ ] `test_extract_intent_pattern()` - Intent extracted from first message
- [ ] `test_extract_file_relationships()` - Co-modification detected
- [ ] `test_extract_workflow_pattern()` - Workflow steps identified
- [ ] `test_extract_all_patterns()` - All patterns extracted
- [ ] `test_empty_conversation()` - Handles empty gracefully

**FileRelationshipManager (4 tests):**
- [ ] `test_record_relationship()` - Relationship recorded (idempotent)
- [ ] `test_confidence_increase()` - Confidence increases with occurrences
- [ ] `test_get_related_files()` - Related files query works
- [ ] `test_get_all_relationships()` - All relationships query works

**IntentPatternManager (4 tests):**
- [ ] `test_record_intent_pattern()` - Pattern recorded with success/failure
- [ ] `test_match_intent()` - Intent matching works
- [ ] `test_confidence_calculation()` - Success rate confidence accurate
- [ ] `test_get_patterns_by_intent()` - Intent filtering works

**ConfidenceDecaySystem (5 tests):**
- [ ] `test_60_day_decay()` - 10% reduction after 60 days
- [ ] `test_90_day_decay()` - 25% reduction after 90 days
- [ ] `test_120_day_marking()` - Marked for deletion after 120 days
- [ ] `test_low_confidence_deletion()` - Auto-delete below 0.30
- [ ] `test_pinned_exemption()` - Pinned patterns exempt

**WorkflowPatternManager (4 tests):**
- [ ] `test_record_workflow()` - Workflow recorded with steps
- [ ] `test_success_rate_calculation()` - Weighted average accurate
- [ ] `test_get_workflow_by_type()` - Type filtering works
- [ ] `test_recommend_workflow()` - Recommendation score works

### Integration Tests (6 tests)

**End-to-End Pattern Learning:**
- [ ] `test_tier1_to_tier2_extraction()` - Conversation → Pattern extraction → Storage
- [ ] `test_fifo_pattern_extraction()` - FIFO deletion triggers pattern learning
- [ ] `test_pattern_search_recommendation()` - Search → Find pattern → Recommend
- [ ] `test_confidence_update_cycle()` - Pattern used → Confidence updated → Re-ranked
- [ ] `test_decay_lifecycle()` - Pattern unused → Decayed → Deleted
- [ ] `test_file_relationship_learning()` - Multiple conversations → Strong relationship

---

## ⚡ Performance Benchmarks

```python
def test_fts5_search_performance():
    """Ensure FTS5 search meets <100ms target"""
    import time
    
    kg = KnowledgeGraphEngine()
    
    # Insert 1000 patterns
    for i in range(1000):
        kg.store_pattern('test', f"Pattern {i} with various keywords", 
                        [f"keyword{i}", "test", "pattern"])
    
    # Measure search time
    start = time.perf_counter()
    results = kg.search_patterns("keyword500 OR test", limit=10)
    elapsed = (time.perf_counter() - start) * 1000
    
    assert elapsed < 100, f"Search took {elapsed}ms (target: <100ms)"
    assert len(results) > 0

def test_pattern_extraction_performance():
    """Ensure pattern extraction meets targets"""
    import time
    
    extractor = PatternExtractor()
    
    # Create conversation with 50 messages
    # ... (setup code)
    
    start = time.perf_counter()
    patterns = extractor.extract_all_patterns(conversation_id)
    elapsed = (time.perf_counter() - start) * 1000
    
    assert elapsed < 200, f"Extraction took {elapsed}ms (target: <200ms)"
```

**Targets:**
- FTS5 search: <100ms
- Pattern extraction: <200ms per conversation
- Confidence update: <10ms
- File relationship query: <50ms

---

## 🎯 Success Criteria

**Phase 2 complete when:**
- ✅ All 28 unit tests passing
- ✅ All 6 integration tests passing
- ✅ FTS5 search <100ms (measured)
- ✅ Pattern extraction from Tier 1 works
- ✅ Confidence decay system functional
- ✅ File relationship tracking accurate
- ✅ Workflow recommendations work
- ✅ Integration with Phase 0 + 1 validated
- ✅ Documentation complete
- ✅ **Holistic review passed** ⚠️ MANDATORY

---

## 📖 Documentation Deliverables

1. **API Documentation:** `CORTEX/docs/tier2-knowledge-graph-api.md`
2. **Pattern Types Guide:** `CORTEX/docs/tier2-pattern-types.md`
3. **FTS5 Search Guide:** `CORTEX/docs/tier2-fts5-search-guide.md`
4. **Confidence System:** `CORTEX/docs/tier2-confidence-decay.md`

---

## 🔍 MANDATORY: Holistic Review (Phase 2 Complete)

**⚠️ DO NOT PROCEED TO PHASE 3 UNTIL REVIEW COMPLETE**

### Review Checklist
Reference: `cortex-design/HOLISTIC-REVIEW-PROTOCOL.md` - Phase 2 Section

#### 1. Design Alignment ✅
- [ ] Does pattern learning match KDS Tier 2 design?
- [ ] Is FTS5 search implemented correctly?
- [ ] Does confidence decay follow Rule #12?
- [ ] Is Tier 1 integration seamless?
- [ ] Does pattern extraction preserve semantic meaning?

#### 2. Implementation Quality ✅
- [ ] All 28 unit tests passing?
- [ ] All 6 integration tests passing?
- [ ] Code follows Python best practices?
- [ ] Type hints used consistently?
- [ ] Error handling comprehensive?
- [ ] Logging implemented?

#### 3. Performance Validation ✅
- [ ] FTS5 search <100ms achieved?
- [ ] Pattern extraction <200ms achieved?
- [ ] Confidence updates <10ms achieved?
- [ ] File relationship queries <50ms achieved?

#### 4. Integration with Previous Phases ✅
- [ ] Phase 0 governance accessible?
- [ ] Phase 1 conversations queryable for patterns?
- [ ] FIFO deletion triggers pattern extraction?
- [ ] Database schema compatible?

#### 5. Integration Readiness for Next Phase ✅
- [ ] Phase 3 can query patterns for recommendations?
- [ ] File relationships ready for hotspot analysis?
- [ ] Workflow patterns ready for time estimates?
- [ ] No blocking issues for context intelligence?

#### 6. Adjustments Needed
- [ ] Should more pattern types be added?
- [ ] Should decay thresholds be adjusted?
- [ ] Should FTS5 ranking be tuned?

### Review Output Document
**Create:** `cortex-design/reviews/phase-2-review.md`

### Actions After Review
[Same structure as Phase 0/1]

### Success Metrics for Phase 2
- ✅ All tests passing (34 total)
- ✅ All benchmarks met (<100ms, <200ms, <10ms, <50ms)
- ✅ Pattern extraction working
- ✅ Confidence decay functional
- ✅ Review report created and approved
- ✅ Phase 3 plan updated with learnings

---

## 📊 Phase Timeline

| Day | Tasks | Hours | Cumulative |
|-----|-------|-------|------------|
| 1 | Task 1 (Engine) + Task 2 (Extractor) | 4.5 | 4.5 |
| 2 | Task 3 (File Rel) + Task 4 (Intent) | 3 | 7.5 |
| 3 | Task 5 (Decay) + Task 6 (Workflow) | 3 | 10.5 |
| 4 | Integration Tests + Docs | 2.5 | 13 |
| 5 | **Holistic Review** + Adjustments | 1.5 | 14.5 |

**Total Estimated:** 10-12 hours implementation + 1 hour review + 1 hour adjustments = 12-14 hours

---

## ✅ Phase Completion Checklist

**Implementation:**
- [ ] All tasks complete
- [ ] All 28 unit tests written and passing
- [ ] All 6 integration tests written and passing
- [ ] All benchmarks met
- [ ] Documentation written
- [ ] Code reviewed

**Review:**
- [ ] Holistic review checklist completed
- [ ] Review report written
- [ ] Issues documented
- [ ] Adjustments (if any) implemented
- [ ] Phase 3 plan updated

**Commit:**
- [ ] Implementation committed
- [ ] Review report committed
- [ ] Updated plans committed

**Proceed:**
- [ ] Review status is PASS ✅
- [ ] Team notified of completion
- [ ] Phase 3 ready to start

---

**Status:** Ready for implementation  
**Next:** Phase 3 (Tier 3 - Development Context)  
**Estimated Completion:** 12-14 hours  
**⚠️ CRITICAL:** Complete holistic review before Phase 3!

---

## 🔗 Related Documents

- `HOLISTIC-REVIEW-PROTOCOL.md` - Complete review process
- `phase-1-working-memory.md` - Previous phase
- `phase-3-context-intelligence-updated.md` - Next phase (already exists)
- `DESIGN-IMPROVEMENTS-SUMMARY.md` - Architecture decisions
- `unified-database-schema.sql` - Database schema
- `CORTEX-DNA.md` - Core design principles
