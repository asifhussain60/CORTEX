"""
Raw Request Logger
-----------------
Logs ALL raw user requests and agent responses for debugging and learning purposes.

This module provides privacy-aware logging that:
- Stores complete request/response pairs
- Redacts sensitive information (API keys, passwords, tokens)
- Enables replay for debugging
- Supports learning from user patterns
- Maintains separate log from conversation history (for raw data preservation)

Design Philosophy:
- Privacy First: Automatic redaction of sensitive data
- Debugging: Complete context for issue reproduction
- Learning: Identify user intent patterns and common tasks
- Separation: Raw logs separate from structured conversation history

Example Usage:
    from src.brain.tier1.request_logger import RequestLogger
    
    logger = RequestLogger(db_path="cortex-brain/cortex-brain.db")
    
    # Log raw request/response
    logger.log_raw_request(
        raw_request="Fix the auth bug using my API key abc123xyz",
        raw_response="Fixed authentication issue",
        agent_name="copilot",
        conversation_id="uuid-here"
    )
    # Stored as: "Fix the auth bug using my API key [REDACTED]"
"""

import re
import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging


logger = logging.getLogger(__name__)


class RequestLogger:
    """
    Logger for raw user requests with privacy-aware redaction.
    
    This class stores raw, unprocessed user input for debugging and learning,
    while automatically redacting sensitive information.
    
    Attributes:
        db_path: Path to SQLite database
        redaction_patterns: List of (pattern, replacement) tuples for sensitive data
    """
    
    # Sensitive data patterns (compiled regex patterns)
    SENSITIVE_PATTERNS = [
        # API keys (common formats)
        (re.compile(r'\b[A-Za-z0-9_-]{32,}\b'), '[REDACTED_API_KEY]'),
        (re.compile(r'sk-[A-Za-z0-9]{20,}'), '[REDACTED_API_KEY]'),
        (re.compile(r'ghp_[A-Za-z0-9]{36}'), '[REDACTED_GITHUB_TOKEN]'),
        
        # Passwords (common patterns in text)
        (re.compile(r'password\s*[:=]\s*[^\s]+', re.IGNORECASE), 'password=[REDACTED]'),
        (re.compile(r'passwd\s*[:=]\s*[^\s]+', re.IGNORECASE), 'passwd=[REDACTED]'),
        (re.compile(r'pwd\s*[:=]\s*[^\s]+', re.IGNORECASE), 'pwd=[REDACTED]'),
        
        # Tokens
        (re.compile(r'token\s*[:=]\s*[^\s]+', re.IGNORECASE), 'token=[REDACTED]'),
        (re.compile(r'bearer\s+[A-Za-z0-9_.-]+', re.IGNORECASE), 'bearer [REDACTED]'),
        
        # Email addresses (optional - may be needed for context)
        # (re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'), '[REDACTED_EMAIL]'),
        
        # Credit card numbers
        (re.compile(r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b'), '[REDACTED_CC]'),
        
        # SSH private keys
        (re.compile(r'-----BEGIN (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----.*?-----END (?:RSA |DSA |EC |OPENSSH )?PRIVATE KEY-----', re.DOTALL), '[REDACTED_PRIVATE_KEY]'),
    ]
    
    def __init__(self, db_path: str = "cortex-brain/cortex-brain.db"):
        """
        Initialize request logger.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = Path(db_path)
        self._ensure_table_exists()
    
    def _ensure_table_exists(self):
        """Create raw_requests table if it doesn't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tier1_raw_requests (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT,  -- Link to tier1_conversations (optional)
                agent_name TEXT NOT NULL,
                raw_request TEXT NOT NULL,  -- Original user input (redacted)
                raw_response TEXT NOT NULL,  -- Agent's raw response
                redacted BOOLEAN DEFAULT 0,  -- Whether redaction was applied
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,  -- JSON metadata (session_id, etc.)
                
                FOREIGN KEY (conversation_id) REFERENCES tier1_conversations(id)
            )
        """)
        
        # Create indexes for common queries
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_raw_requests_conv_id
            ON tier1_raw_requests(conversation_id)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_raw_requests_created_at
            ON tier1_raw_requests(created_at DESC)
        """)
        
        conn.commit()
        conn.close()
        
        logger.debug("Ensured tier1_raw_requests table exists")
    
    def redact_sensitive_data(self, text: str) -> tuple[str, bool]:
        """
        Redact sensitive information from text.
        
        Args:
            text: Input text that may contain sensitive data
        
        Returns:
            Tuple of (redacted_text, was_redacted)
        
        Example:
            >>> redacted, changed = logger.redact_sensitive_data(
            ...     "My API key is sk-abc123xyz456"
            ... )
            >>> print(redacted)
            "My API key is [REDACTED_API_KEY]"
            >>> print(changed)
            True
        """
        redacted_text = text
        was_redacted = False
        
        for pattern, replacement in self.SENSITIVE_PATTERNS:
            new_text = pattern.sub(replacement, redacted_text)
            if new_text != redacted_text:
                was_redacted = True
                redacted_text = new_text
        
        return redacted_text, was_redacted
    
    def log_raw_request(
        self,
        raw_request: str,
        raw_response: str,
        agent_name: str,
        conversation_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Log a raw request/response pair with automatic redaction.
        
        Args:
            raw_request: User's raw input (unprocessed)
            raw_response: Agent's raw output (unprocessed)
            agent_name: Name of agent (e.g., "copilot", "claude")
            conversation_id: Optional link to tier1_conversations
            metadata: Optional metadata dict
        
        Returns:
            request_id: Integer ID of logged request
        
        Example:
            req_id = logger.log_raw_request(
                raw_request="Fix bug using password=secret123",
                raw_response="Fixed the bug",
                agent_name="copilot",
                conversation_id="uuid-here"
            )
        """
        # Redact sensitive data
        redacted_request, request_redacted = self.redact_sensitive_data(raw_request)
        redacted_response, response_redacted = self.redact_sensitive_data(raw_response)
        was_redacted = request_redacted or response_redacted
        
        # Convert metadata to JSON
        import json
        metadata_json = json.dumps(metadata) if metadata else None
        
        # Insert into database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO tier1_raw_requests
            (conversation_id, agent_name, raw_request, raw_response, redacted, metadata)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            conversation_id,
            agent_name,
            redacted_request,
            redacted_response,
            1 if was_redacted else 0,
            metadata_json
        ))
        
        request_id = cursor.lastrowid
        conn.commit()
        conn.close()
        
        logger.info(
            f"Logged raw request {request_id}: agent={agent_name}, "
            f"redacted={was_redacted}, conv_id={conversation_id}"
        )
        
        return request_id
    
    def get_raw_request(self, request_id: int) -> Optional[Dict[str, Any]]:
        """
        Get a raw request by ID.
        
        Args:
            request_id: Integer ID of request
        
        Returns:
            Dict with request data or None if not found
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT *
            FROM tier1_raw_requests
            WHERE id = ?
        """, (request_id,))
        
        row = cursor.fetchone()
        conn.close()
        
        if not row:
            return None
        
        import json
        return {
            'id': row['id'],
            'conversation_id': row['conversation_id'],
            'agent_name': row['agent_name'],
            'raw_request': row['raw_request'],
            'raw_response': row['raw_response'],
            'redacted': bool(row['redacted']),
            'created_at': row['created_at'],
            'metadata': json.loads(row['metadata']) if row['metadata'] else None
        }
    
    def get_conversation_raw_logs(
        self,
        conversation_id: str
    ) -> List[Dict[str, Any]]:
        """
        Get all raw logs for a specific conversation.
        
        Args:
            conversation_id: UUID of conversation
        
        Returns:
            List of raw request dicts
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT *
            FROM tier1_raw_requests
            WHERE conversation_id = ?
            ORDER BY created_at ASC
        """, (conversation_id,))
        
        rows = cursor.fetchall()
        conn.close()
        
        import json
        return [{
            'id': row['id'],
            'conversation_id': row['conversation_id'],
            'agent_name': row['agent_name'],
            'raw_request': row['raw_request'],
            'raw_response': row['raw_response'],
            'redacted': bool(row['redacted']),
            'created_at': row['created_at'],
            'metadata': json.loads(row['metadata']) if row['metadata'] else None
        } for row in rows]
    
    def get_recent_raw_logs(
        self,
        limit: int = 50,
        agent_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get recent raw logs (optionally filtered by agent).
        
        Args:
            limit: Maximum results (default 50)
            agent_name: Optional agent name filter
        
        Returns:
            List of raw request dicts
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if agent_name:
            cursor.execute("""
                SELECT *
                FROM tier1_raw_requests
                WHERE agent_name = ?
                ORDER BY created_at DESC
                LIMIT ?
            """, (agent_name, limit))
        else:
            cursor.execute("""
                SELECT *
                FROM tier1_raw_requests
                ORDER BY created_at DESC
                LIMIT ?
            """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        import json
        return [{
            'id': row['id'],
            'conversation_id': row['conversation_id'],
            'agent_name': row['agent_name'],
            'raw_request': row['raw_request'],
            'raw_response': row['raw_response'],
            'redacted': bool(row['redacted']),
            'created_at': row['created_at'],
            'metadata': json.loads(row['metadata']) if row['metadata'] else None
        } for row in rows]
    
    def get_redaction_stats(self) -> Dict[str, Any]:
        """
        Get statistics about redaction activity.
        
        Returns:
            Dict with total logs, redacted count, redaction rate
        
        Example:
            stats = logger.get_redaction_stats()
            print(f"Redaction rate: {stats['redaction_rate']:.1%}")
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM tier1_raw_requests")
        total = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM tier1_raw_requests WHERE redacted = 1")
        redacted = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_logs': total,
            'redacted_logs': redacted,
            'clean_logs': total - redacted,
            'redaction_rate': redacted / total if total > 0 else 0.0
        }


# Convenience function
def get_request_logger(db_path: str = "cortex-brain/cortex-brain.db") -> RequestLogger:
    """
    Convenience function to get a RequestLogger instance.
    
    Args:
        db_path: Path to SQLite database
    
    Returns:
        Initialized RequestLogger instance
    
    Example:
        from src.brain.tier1.request_logger import get_request_logger
        
        logger = get_request_logger()
        logger.log_raw_request(...)
    """
    return RequestLogger(db_path)
