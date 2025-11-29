"""
Automatic Conversation Capture System

Automatically captures high-value conversations to Tier 1 working memory.

Purpose:
    - Identify conversations worth preserving
    - Calculate quality scores automatically
    - Capture conversations with metadata
    - Maintain 70-conversation FIFO buffer optimally

Capture Criteria (should_capture_conversation):
    - Length: >10 messages
    - Has code changes: Files modified during conversation
    - Strategic decisions: Architecture, design, planning discussions
    - Problem resolution: Bugs fixed, issues resolved
    - Complexity: Multi-step workflows, agent coordination

Quality Scoring (0-10):
    - Message count (20%): More messages = more context
    - Code changes (25%): Actual implementation work
    - Strategic value (30%): Architecture, patterns, decisions
    - Resolution success (25%): Problems solved

Target: 49+ conversations (70% FIFO capacity) with avg quality 7.5+

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
License: Source-Available (Use Allowed, No Contributions)
"""

import os
import sys
import sqlite3
import json
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
import logging

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

logger = logging.getLogger(__name__)


class ConversationAutoCapture:
    """
    Automatic conversation capture with quality scoring.
    
    Monitors conversations and automatically captures high-value ones
    to Tier 1 working memory with proper metadata and quality scores.
    """
    
    def __init__(self, tier1_db_path: Optional[str] = None):
        """
        Initialize Conversation Auto Capture.
        
        Args:
            tier1_db_path: Path to Tier 1 database
                          (default: cortex-brain/tier1-working-memory.db)
        """
        if tier1_db_path is None:
            brain_dir = os.path.join(os.path.dirname(__file__), '../..', 'cortex-brain')
            tier1_db_path = os.path.join(brain_dir, 'tier1-working-memory.db')
        
        self.tier1_db_path = tier1_db_path
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Ensure Tier 1 database schema exists."""
        with sqlite3.connect(self.tier1_db_path) as conn:
            cursor = conn.cursor()
            
            # Create conversations table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT UNIQUE NOT NULL,
                    title TEXT,
                    message_count INTEGER DEFAULT 0,
                    quality_score REAL DEFAULT 0.0,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    last_updated TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    is_strategic BOOLEAN DEFAULT 0
                )
            """)
            
            # Create messages table if not exists
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                    metadata TEXT,
                    FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id)
                )
            """)
            
            conn.commit()
    
    def should_capture_conversation(
        self,
        messages: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> Tuple[bool, float, str]:
        """
        Determine if conversation should be captured.
        
        Criteria (need 3+ to capture):
        1. Length >10 messages
        2. Has code changes (files modified)
        3. Has strategic decisions (keywords: architecture, design, pattern)
        4. Has problem resolution (keywords: fix, bug, issue, error)
        5. High complexity (multi-agent coordination, TDD workflow)
        
        Args:
            messages: List of conversation messages
            context: Optional context with metadata
        
        Returns:
            Tuple of (should_capture, quality_score, reason)
        """
        if context is None:
            context = {}
        
        # Initialize criteria scores
        criteria_met = 0
        reasons = []
        
        # Criterion 1: Message count >10
        has_sufficient_length = len(messages) > 10
        if has_sufficient_length:
            criteria_met += 1
            reasons.append(f"Sufficient length ({len(messages)} messages)")
        
        # Criterion 2: Has code changes
        has_code_changes = False
        if 'files_modified' in context and context['files_modified']:
            has_code_changes = len(context['files_modified']) > 0
            if has_code_changes:
                criteria_met += 1
                reasons.append(f"Code changes ({len(context['files_modified'])} files)")
        
        # Criterion 3: Strategic decisions
        strategic_keywords = [
            'architecture', 'design', 'pattern', 'workflow', 'plan',
            'roadmap', 'strategy', 'approach', 'structure', 'framework'
        ]
        has_strategic_decisions = self._has_keywords(messages, strategic_keywords)
        if has_strategic_decisions:
            criteria_met += 1
            reasons.append("Strategic decisions detected")
        
        # Criterion 4: Problem resolution
        resolution_keywords = [
            'fix', 'fixed', 'bug', 'error', 'issue', 'resolved',
            'solution', 'solved', 'working', 'success'
        ]
        has_problem_resolution = self._has_keywords(messages, resolution_keywords)
        if has_problem_resolution:
            criteria_met += 1
            reasons.append("Problem resolution detected")
        
        # Criterion 5: High complexity
        complexity_indicators = [
            'agent', 'workflow', 'tdd', 'test', 'integration',
            'multi-step', 'phase', 'milestone', 'implementation'
        ]
        has_high_complexity = self._has_keywords(messages, complexity_indicators)
        if has_high_complexity:
            criteria_met += 1
            reasons.append("High complexity detected")
        
        # Decision: Capture if 3+ criteria met
        should_capture = criteria_met >= 3
        
        # Calculate quality score if capturing
        if should_capture:
            quality_score = self._calculate_quality_score(
                messages=messages,
                context=context,
                has_code_changes=has_code_changes,
                has_strategic_decisions=has_strategic_decisions,
                has_problem_resolution=has_problem_resolution
            )
        else:
            quality_score = 0.0
        
        reason = f"{criteria_met}/5 criteria met: {', '.join(reasons)}" if reasons else "Insufficient criteria"
        
        logger.info(
            f"Conversation capture decision: {'CAPTURE' if should_capture else 'SKIP'} "
            f"({criteria_met}/5 criteria, quality: {quality_score:.1f})"
        )
        
        return should_capture, quality_score, reason
    
    def _has_keywords(self, messages: List[Dict[str, Any]], keywords: List[str]) -> bool:
        """Check if messages contain any of the keywords."""
        for message in messages:
            content = message.get('content', '').lower()
            for keyword in keywords:
                if keyword in content:
                    return True
        return False
    
    def _calculate_quality_score(
        self,
        messages: List[Dict[str, Any]],
        context: Dict[str, Any],
        has_code_changes: bool,
        has_strategic_decisions: bool,
        has_problem_resolution: bool
    ) -> float:
        """
        Calculate quality score (0-10).
        
        Scoring factors:
        - Message count (20%): More messages = more context
        - Code changes (25%): Actual implementation work
        - Strategic value (30%): Architecture, patterns, decisions
        - Resolution success (25%): Problems solved
        
        Args:
            messages: Conversation messages
            context: Conversation context
            has_code_changes: Whether code was changed
            has_strategic_decisions: Whether strategic decisions made
            has_problem_resolution: Whether problems were resolved
        
        Returns:
            Quality score 0-10
        """
        # Message count score (0-2 points)
        # 10 messages = 0, 50+ messages = 2.0
        message_count = len(messages)
        message_score = min(2.0, (message_count - 10) / 20)
        
        # Code changes score (0-2.5 points)
        if has_code_changes:
            files_modified = len(context.get('files_modified', []))
            # 1 file = 1.0, 5+ files = 2.5
            code_score = min(2.5, 1.0 + (files_modified / 4))
        else:
            code_score = 0.0
        
        # Strategic value score (0-3 points)
        strategic_score = 3.0 if has_strategic_decisions else 0.0
        
        # Resolution success score (0-2.5 points)
        resolution_score = 2.5 if has_problem_resolution else 0.0
        
        # Calculate total (0-10)
        quality_score = message_score + code_score + strategic_score + resolution_score
        
        logger.debug(
            f"Quality breakdown: messages={message_score:.1f}, code={code_score:.1f}, "
            f"strategic={strategic_score:.1f}, resolution={resolution_score:.1f}, "
            f"total={quality_score:.1f}"
        )
        
        return round(quality_score, 1)
    
    def capture_conversation(
        self,
        conversation_id: str,
        title: str,
        messages: List[Dict[str, Any]],
        context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Capture conversation to Tier 1 with quality scoring.
        
        Args:
            conversation_id: Unique conversation ID
            title: Conversation title
            messages: List of conversation messages
            context: Optional conversation context
        
        Returns:
            True if captured successfully
        """
        if context is None:
            context = {}
        
        # Check if should capture
        should_capture, quality_score, reason = self.should_capture_conversation(messages, context)
        
        if not should_capture:
            logger.info(f"Skipping conversation capture: {reason}")
            return False
        
        try:
            with sqlite3.connect(self.tier1_db_path) as conn:
                cursor = conn.cursor()
                
                # Check if already exists
                cursor.execute(
                    "SELECT conversation_id FROM conversations WHERE conversation_id = ?",
                    (conversation_id,)
                )
                exists = cursor.fetchone() is not None
                
                if exists:
                    logger.warning(f"Conversation {conversation_id} already captured")
                    return False
                
                # Insert conversation
                is_strategic = quality_score >= 7.5
                metadata_json = json.dumps(context) if context else None
                
                cursor.execute("""
                    INSERT INTO conversations 
                    (conversation_id, title, message_count, quality_score, metadata, is_strategic, created_at, last_updated)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    conversation_id,
                    title,
                    len(messages),
                    quality_score,
                    metadata_json,
                    is_strategic,
                    datetime.now().isoformat(),
                    datetime.now().isoformat()
                ))
                
                # Insert messages
                for message in messages:
                    message_metadata = json.dumps(message.get('metadata', {})) if message.get('metadata') else None
                    cursor.execute("""
                        INSERT INTO messages (conversation_id, role, content, timestamp, metadata)
                        VALUES (?, ?, ?, ?, ?)
                    """, (
                        conversation_id,
                        message.get('role', 'user'),
                        message.get('content', ''),
                        message.get('timestamp', datetime.now().isoformat()),
                        message_metadata
                    ))
                
                conn.commit()
                
                logger.info(
                    f"✅ Captured conversation {conversation_id}: {title} "
                    f"({len(messages)} messages, quality: {quality_score:.1f})"
                )
                
                # Enforce FIFO (keep only 70 most recent)
                self._enforce_fifo_limit(cursor, limit=70)
                conn.commit()
                
                return True
        
        except Exception as e:
            logger.error(f"Failed to capture conversation: {e}")
            return False
    
    def _enforce_fifo_limit(self, cursor, limit: int = 70):
        """
        Enforce FIFO limit by removing oldest conversations.
        
        Args:
            cursor: Database cursor
            limit: Maximum conversations to keep
        """
        # Count conversations
        cursor.execute("SELECT COUNT(*) FROM conversations")
        count = cursor.fetchone()[0]
        
        if count > limit:
            # Delete oldest conversations
            delete_count = count - limit
            cursor.execute("""
                DELETE FROM conversations
                WHERE id IN (
                    SELECT id FROM conversations
                    ORDER BY created_at ASC
                    LIMIT ?
                )
            """, (delete_count,))
            
            # Also delete orphaned messages
            cursor.execute("""
                DELETE FROM messages
                WHERE conversation_id NOT IN (
                    SELECT conversation_id FROM conversations
                )
            """)
            
            logger.info(f"FIFO enforcement: Removed {delete_count} oldest conversations (keeping {limit})")
    
    def get_capture_stats(self) -> Dict[str, Any]:
        """
        Get conversation capture statistics.
        
        Returns:
            Dictionary with capture stats
        """
        try:
            with sqlite3.connect(self.tier1_db_path) as conn:
                cursor = conn.cursor()
                
                # Total conversations
                cursor.execute("SELECT COUNT(*) FROM conversations")
                total = cursor.fetchone()[0]
                
                # Average quality
                cursor.execute("SELECT AVG(quality_score) FROM conversations")
                avg_quality = cursor.fetchone()[0] or 0.0
                
                # Strategic conversations
                cursor.execute("SELECT COUNT(*) FROM conversations WHERE is_strategic = 1")
                strategic_count = cursor.fetchone()[0]
                
                # Capacity utilization
                capacity = 70
                utilization_pct = (total / capacity) * 100
                
                return {
                    'total_conversations': total,
                    'capacity': capacity,
                    'utilization_percent': round(utilization_pct, 1),
                    'average_quality': round(avg_quality, 1),
                    'strategic_conversations': strategic_count,
                    'status': 'healthy' if utilization_pct >= 50 else 'underutilized'
                }
        
        except Exception as e:
            logger.error(f"Failed to get capture stats: {e}")
            return {}


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    capture = ConversationAutoCapture()
    
    # Test conversation
    test_messages = [
        {'role': 'user', 'content': 'Plan authentication feature with JWT'},
        {'role': 'assistant', 'content': 'Let me analyze the architecture...'},
        {'role': 'user', 'content': 'Implement user login endpoint'},
        {'role': 'assistant', 'content': 'Creating authentication service...'},
        {'role': 'user', 'content': 'Add tests for login flow'},
        {'role': 'assistant', 'content': 'Writing unit tests...'},
        {'role': 'user', 'content': 'Fix validation bug'},
        {'role': 'assistant', 'content': 'Fixed validation issue...'},
        {'role': 'user', 'content': 'Test the fix'},
        {'role': 'assistant', 'content': 'Running tests... All passing!'},
        {'role': 'user', 'content': 'Deploy to staging'},
        {'role': 'assistant', 'content': 'Deploying...'}
    ]
    
    test_context = {
        'files_modified': ['src/auth/login.py', 'tests/test_login.py'],
        'workspace_name': 'myapp'
    }
    
    # Test capture
    captured = capture.capture_conversation(
        conversation_id='test-conv-001',
        title='Authentication Feature Implementation',
        messages=test_messages,
        context=test_context
    )
    
    print(f"\nCapture result: {captured}")
    
    # Show stats
    stats = capture.get_capture_stats()
    print(f"\nCapture Stats:")
    print(f"  Total: {stats['total_conversations']}/{stats['capacity']}")
    print(f"  Utilization: {stats['utilization_percent']}%")
    print(f"  Avg Quality: {stats['average_quality']}/10")
    print(f"  Strategic: {stats['strategic_conversations']}")
