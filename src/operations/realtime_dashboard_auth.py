"""
Real-Time Dashboard Authentication Layer

Provides authentication and authorization for WebSocket connections.

Features:
    - Admin token generation and validation
    - WebSocket middleware authentication
    - Session management with 30-minute timeout
    - Audit logging for admin operations
    - Token revocation support
    - Role-based access control (RBAC)

Security:
    - Tokens are UUID-based (cryptographically random)
    - Automatic token expiration (30 minutes)
    - Audit trail for all authentication events
    - Admin-only access enforcement
    - Session cleanup for expired tokens

Usage:
    # Initialize auth layer
    auth = RealtimeDashboardAuth()
    
    # Generate admin token
    token = auth.generate_token('admin_user', is_admin=True)
    
    # Validate token
    user_info = auth.validate_token(token)
    if user_info and user_info['is_admin']:
        # Grant access
        pass
    
    # Revoke token
    auth.revoke_token(token)

Author: Asif Hussain
Copyright: © 2024-2025 Asif Hussain. All rights reserved.
"""

import logging
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional
from uuid import uuid4
from dataclasses import dataclass
from enum import Enum


logger = logging.getLogger(__name__)


class TokenStatus(Enum):
    """Token status enumeration."""
    ACTIVE = "active"
    EXPIRED = "expired"
    REVOKED = "revoked"


@dataclass
class AuthToken:
    """Authentication token data structure."""
    token: str
    user_id: str
    is_admin: bool
    created_at: datetime
    expires_at: datetime
    status: TokenStatus
    metadata: Dict[str, Any]


@dataclass
class AuditLogEntry:
    """Audit log entry data structure."""
    timestamp: datetime
    user_id: str
    action: str
    resource: str
    success: bool
    ip_address: Optional[str]
    details: Dict[str, Any]


class RealtimeDashboardAuth:
    """
    Authentication layer for real-time dashboard WebSocket connections.
    
    Features:
        - Token-based authentication (UUID)
        - Session management with expiration
        - Audit logging
        - Token revocation
        - Admin-only access enforcement
    
    Attributes:
        tokens (Dict[str, AuthToken]): Active tokens
        audit_log (List[AuditLogEntry]): Audit log entries
        token_duration (timedelta): Token expiration duration
    """
    
    def __init__(
        self,
        brain_path: Optional[Path] = None,
        token_duration_minutes: int = 30,
        enable_audit_logging: bool = True,
        enable_persistence: bool = True
    ):
        """
        Initialize authentication layer.
        
        Args:
            brain_path: Path to CORTEX brain directory
            token_duration_minutes: Token expiration duration (minutes)
            enable_audit_logging: Enable audit logging
            enable_persistence: Enable database persistence
        """
        self.brain_path = brain_path or Path("cortex-brain")
        self.token_duration = timedelta(minutes=token_duration_minutes)
        self.enable_audit_logging = enable_audit_logging
        self.enable_persistence = enable_persistence
        
        self.tokens: Dict[str, AuthToken] = {}
        self.audit_log: List[AuditLogEntry] = []
        
        # Initialize database if persistence enabled
        if self.enable_persistence:
            self._init_database()
        
        logger.info(f"Initialized RealtimeDashboardAuth (token_duration={token_duration_minutes}m)")
    
    def _init_database(self):
        """Initialize SQLite database for token persistence."""
        db_path = self.brain_path / "tier1" / "dashboard_auth.db"
        db_path.parent.mkdir(parents=True, exist_ok=True)
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            
            # Create tokens table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS tokens (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    is_admin INTEGER NOT NULL,
                    created_at TEXT NOT NULL,
                    expires_at TEXT NOT NULL,
                    status TEXT NOT NULL,
                    metadata TEXT
                )
            """)
            
            # Create audit log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_id TEXT NOT NULL,
                    action TEXT NOT NULL,
                    resource TEXT NOT NULL,
                    success INTEGER NOT NULL,
                    ip_address TEXT,
                    details TEXT
                )
            """)
            
            # Create index on user_id for faster lookups
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_tokens_user_id 
                ON tokens(user_id)
            """)
            
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_log_user_id 
                ON audit_log(user_id)
            """)
            
            conn.commit()
        
        logger.info(f"Database initialized: {db_path}")
    
    def generate_token(
        self,
        user_id: str,
        is_admin: bool = False,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate authentication token.
        
        Args:
            user_id: User identifier
            is_admin: Admin privileges flag
            metadata: Additional token metadata
            
        Returns:
            Authentication token (UUID)
        """
        token = str(uuid4())
        created_at = datetime.now()
        expires_at = created_at + self.token_duration
        
        auth_token = AuthToken(
            token=token,
            user_id=user_id,
            is_admin=is_admin,
            created_at=created_at,
            expires_at=expires_at,
            status=TokenStatus.ACTIVE,
            metadata=metadata or {}
        )
        
        self.tokens[token] = auth_token
        
        # Persist to database
        if self.enable_persistence:
            self._persist_token(auth_token)
        
        # Audit log
        self._log_audit(
            user_id=user_id,
            action="token_generated",
            resource="authentication",
            success=True,
            details={"is_admin": is_admin, "expires_at": expires_at.isoformat()}
        )
        
        logger.info(f"Generated token for user '{user_id}' (admin={is_admin})")
        return token
    
    def validate_token(self, token: str) -> Optional[Dict[str, Any]]:
        """
        Validate authentication token.
        
        Args:
            token: Authentication token
            
        Returns:
            User information if valid, None otherwise
        """
        if token not in self.tokens:
            # Try loading from database
            if self.enable_persistence:
                self._load_token(token)
        
        if token not in self.tokens:
            self._log_audit(
                user_id="unknown",
                action="token_validation",
                resource="authentication",
                success=False,
                details={"reason": "token_not_found"}
            )
            return None
        
        auth_token = self.tokens[token]
        
        # Check expiration
        if datetime.now() > auth_token.expires_at:
            auth_token.status = TokenStatus.EXPIRED
            self._update_token_status(token, TokenStatus.EXPIRED)
            
            self._log_audit(
                user_id=auth_token.user_id,
                action="token_validation",
                resource="authentication",
                success=False,
                details={"reason": "token_expired"}
            )
            return None
        
        # Check status
        if auth_token.status != TokenStatus.ACTIVE:
            self._log_audit(
                user_id=auth_token.user_id,
                action="token_validation",
                resource="authentication",
                success=False,
                details={"reason": f"token_{auth_token.status.value}"}
            )
            return None
        
        # Token valid
        self._log_audit(
            user_id=auth_token.user_id,
            action="token_validation",
            resource="authentication",
            success=True,
            details={"is_admin": auth_token.is_admin}
        )
        
        return {
            'user_id': auth_token.user_id,
            'is_admin': auth_token.is_admin,
            'created_at': auth_token.created_at,
            'expires_at': auth_token.expires_at,
            'metadata': auth_token.metadata
        }
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke authentication token.
        
        Args:
            token: Authentication token
            
        Returns:
            True if revoked, False if not found
        """
        if token not in self.tokens:
            return False
        
        auth_token = self.tokens[token]
        auth_token.status = TokenStatus.REVOKED
        
        # Update database
        self._update_token_status(token, TokenStatus.REVOKED)
        
        # Audit log
        self._log_audit(
            user_id=auth_token.user_id,
            action="token_revoked",
            resource="authentication",
            success=True,
            details={"token": token[:8] + "..."}
        )
        
        logger.info(f"Revoked token for user '{auth_token.user_id}'")
        return True
    
    def cleanup_expired_tokens(self) -> int:
        """
        Clean up expired tokens.
        
        Returns:
            Number of tokens cleaned up
        """
        now = datetime.now()
        expired_tokens = []
        
        for token, auth_token in self.tokens.items():
            if now > auth_token.expires_at:
                expired_tokens.append(token)
                auth_token.status = TokenStatus.EXPIRED
        
        # Remove from memory
        for token in expired_tokens:
            del self.tokens[token]
        
        # Update database
        if self.enable_persistence and expired_tokens:
            self._batch_update_token_status(expired_tokens, TokenStatus.EXPIRED)
        
        if expired_tokens:
            logger.info(f"Cleaned up {len(expired_tokens)} expired tokens")
        
        return len(expired_tokens)
    
    def get_active_sessions(self) -> List[Dict[str, Any]]:
        """
        Get list of active sessions.
        
        Returns:
            List of active session information
        """
        sessions = []
        
        for auth_token in self.tokens.values():
            if auth_token.status == TokenStatus.ACTIVE and datetime.now() < auth_token.expires_at:
                sessions.append({
                    'user_id': auth_token.user_id,
                    'is_admin': auth_token.is_admin,
                    'created_at': auth_token.created_at.isoformat(),
                    'expires_at': auth_token.expires_at.isoformat(),
                    'metadata': auth_token.metadata
                })
        
        return sessions
    
    def _persist_token(self, auth_token: AuthToken):
        """Persist token to database."""
        if not self.enable_persistence:
            return
        
        db_path = self.brain_path / "tier1" / "dashboard_auth.db"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO tokens (token, user_id, is_admin, created_at, expires_at, status, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                auth_token.token,
                auth_token.user_id,
                1 if auth_token.is_admin else 0,
                auth_token.created_at.isoformat(),
                auth_token.expires_at.isoformat(),
                auth_token.status.value,
                str(auth_token.metadata)
            ))
            conn.commit()
    
    def _load_token(self, token: str):
        """Load token from database."""
        if not self.enable_persistence:
            return
        
        db_path = self.brain_path / "tier1" / "dashboard_auth.db"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT user_id, is_admin, created_at, expires_at, status, metadata
                FROM tokens WHERE token = ?
            """, (token,))
            
            row = cursor.fetchone()
            if row:
                auth_token = AuthToken(
                    token=token,
                    user_id=row[0],
                    is_admin=bool(row[1]),
                    created_at=datetime.fromisoformat(row[2]),
                    expires_at=datetime.fromisoformat(row[3]),
                    status=TokenStatus(row[4]),
                    metadata=eval(row[5]) if row[5] else {}
                )
                self.tokens[token] = auth_token
    
    def _update_token_status(self, token: str, status: TokenStatus):
        """Update token status in database."""
        if not self.enable_persistence:
            return
        
        db_path = self.brain_path / "tier1" / "dashboard_auth.db"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE tokens SET status = ? WHERE token = ?
            """, (status.value, token))
            conn.commit()
    
    def _batch_update_token_status(self, tokens: List[str], status: TokenStatus):
        """Batch update token status in database."""
        if not self.enable_persistence:
            return
        
        db_path = self.brain_path / "tier1" / "dashboard_auth.db"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                UPDATE tokens SET status = ? WHERE token = ?
            """, [(status.value, token) for token in tokens])
            conn.commit()
    
    def _log_audit(
        self,
        user_id: str,
        action: str,
        resource: str,
        success: bool,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ):
        """Log audit event."""
        if not self.enable_audit_logging:
            return
        
        entry = AuditLogEntry(
            timestamp=datetime.now(),
            user_id=user_id,
            action=action,
            resource=resource,
            success=success,
            ip_address=ip_address,
            details=details or {}
        )
        
        self.audit_log.append(entry)
        
        # Persist to database
        if self.enable_persistence:
            self._persist_audit_entry(entry)
    
    def _persist_audit_entry(self, entry: AuditLogEntry):
        """Persist audit entry to database."""
        if not self.enable_persistence:
            return
        
        db_path = self.brain_path / "tier1" / "dashboard_auth.db"
        
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO audit_log (timestamp, user_id, action, resource, success, ip_address, details)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                entry.timestamp.isoformat(),
                entry.user_id,
                entry.action,
                entry.resource,
                1 if entry.success else 0,
                entry.ip_address,
                str(entry.details)
            ))
            conn.commit()
    
    def get_audit_log(
        self,
        user_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get audit log entries.
        
        Args:
            user_id: Filter by user ID (optional)
            limit: Maximum number of entries
            
        Returns:
            List of audit log entries
        """
        entries = []
        
        for entry in reversed(self.audit_log[-limit:]):
            if user_id and entry.user_id != user_id:
                continue
            
            entries.append({
                'timestamp': entry.timestamp.isoformat(),
                'user_id': entry.user_id,
                'action': entry.action,
                'resource': entry.resource,
                'success': entry.success,
                'ip_address': entry.ip_address,
                'details': entry.details
            })
        
        return entries


# Example usage
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Initialize auth layer
    auth = RealtimeDashboardAuth()
    
    # Generate admin token
    admin_token = auth.generate_token('admin_user', is_admin=True)
    print(f"Admin token: {admin_token}")
    
    # Validate token
    user_info = auth.validate_token(admin_token)
    print(f"Token valid: {user_info}")
    
    # Get active sessions
    sessions = auth.get_active_sessions()
    print(f"Active sessions: {len(sessions)}")
    
    # Get audit log
    audit_log = auth.get_audit_log()
    print(f"Audit log entries: {len(audit_log)}")
    
    # Revoke token
    auth.revoke_token(admin_token)
    print("Token revoked")
    
    # Validate again (should fail)
    user_info = auth.validate_token(admin_token)
    print(f"Token valid after revocation: {user_info}")
