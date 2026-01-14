"""
AC-AUDIT-006: Per-Repo Isolation

Ensures separate audit databases per repository to prevent cross-repo contamination.
Each repository maintains its own isolated audit trail.

Status: COMPLETE
Author: GitHub Copilot
Version: 1.0.0
"""

import sqlite3
import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List
from dataclasses import dataclass

from src.utils.path_utils import audit_logs_path, project_root


@dataclass
class RepositoryIdentity:
    """Uniquely identifies a repository."""
    repo_id: str  # Unique identifier (hash of URL or name)
    repo_name: str  # Human-readable name
    repo_path: str  # Full filesystem path
    
    def validate(self):
        """Validate repository identity."""
        if not self.repo_id or not isinstance(self.repo_id, str):
            raise ValueError("repo_id must be non-empty string")
        if not self.repo_name or not isinstance(self.repo_name, str):
            raise ValueError("repo_name must be non-empty string")
        if not self.repo_path or not isinstance(self.repo_path, str):
            raise ValueError("repo_path must be non-empty string")


class RepositoryAuditIsolation:
    """
    Manages isolated audit databases per repository.
    Prevents audit events from one repo from contaminating another.
    """
    
    def __init__(
        self,
        audit_base_path: Optional[str] = None,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize repository isolation system.
        
        Args:
            audit_base_path: Base directory for audit databases
            logger: Logger instance
        """
        self.logger = logger or logging.getLogger(__name__)
        
        try:
            self.audit_base_path = Path(audit_base_path or audit_logs_path())
        except Exception:
            # Fallback for testing
            self.audit_base_path = Path(project_root()) / "cortex-brain" / "audit-logs"
        
        self.audit_base_path.mkdir(parents=True, exist_ok=True)
        self._repo_db_cache: Dict[str, str] = {}
    
    @staticmethod
    def generate_repo_id(repo_path: str) -> str:
        """
        Generate unique repo ID from path.
        
        Args:
            repo_path: Repository filesystem path
            
        Returns:
            SHA256 hash of repo path
        """
        repo_hash = hashlib.sha256(repo_path.encode()).hexdigest()
        return repo_hash[:16]  # Use first 16 chars
    
    @staticmethod
    def generate_repo_id_from_url(repo_url: str) -> str:
        """
        Generate unique repo ID from repository URL.
        
        Args:
            repo_url: Repository URL (e.g., https://github.com/user/repo)
            
        Returns:
            SHA256 hash of repo URL
        """
        url_hash = hashlib.sha256(repo_url.encode()).hexdigest()
        return url_hash[:16]
    
    def get_repo_db_path(self, repo_identity: RepositoryIdentity) -> str:
        """
        Get isolated database path for repository.
        
        Args:
            repo_identity: RepositoryIdentity object
            
        Returns:
            Absolute path to repo's audit database
        """
        repo_identity.validate()
        
        db_filename = f"audit_{repo_identity.repo_id}.db"
        db_path = self.audit_base_path / db_filename
        
        # Cache mapping
        self._repo_db_cache[repo_identity.repo_id] = str(db_path)
        
        return str(db_path)
    
    def initialize_repo_db(self, repo_identity: RepositoryIdentity) -> str:
        """
        Initialize isolated database for repository.
        
        Args:
            repo_identity: RepositoryIdentity object
            
        Returns:
            Path to initialized database
        """
        repo_identity.validate()
        
        db_path = self.get_repo_db_path(repo_identity)
        db_path_obj = Path(db_path)
        
        # Create database if not exists
        if not db_path_obj.exists():
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Create audit events table with repo context
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repo_id TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    level TEXT NOT NULL,
                    category TEXT,
                    message TEXT,
                    actor TEXT,
                    resource TEXT,
                    ac_id TEXT,
                    correlation_id TEXT,
                    UNIQUE(repo_id, id)
                )
            """)
            
            # Create metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repo_metadata (
                    repo_id TEXT PRIMARY KEY,
                    repo_name TEXT NOT NULL,
                    repo_path TEXT NOT NULL,
                    created_at TEXT NOT NULL,
                    db_version TEXT NOT NULL
                )
            """)
            
            # Create indexes for query performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_repo_timestamp
                ON audit_events(repo_id, timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_repo_ac_id
                ON audit_events(repo_id, ac_id)
            """)
            
            # Store repository metadata
            cursor.execute("""
                INSERT INTO repo_metadata (repo_id, repo_name, repo_path, created_at, db_version)
                VALUES (?, ?, ?, ?, ?)
            """, (
                repo_identity.repo_id,
                repo_identity.repo_name,
                repo_identity.repo_path,
                datetime.utcnow().isoformat(),
                "1.0"
            ))
            
            conn.commit()
            conn.close()
            
            self.logger.info(
                f"Initialized isolated audit database for repo {repo_identity.repo_name} "
                f"(ID: {repo_identity.repo_id})"
            )
        
        return db_path
    
    def get_repo_metadata(self, repo_db_path: str) -> Optional[Dict]:
        """
        Get repository metadata from database.
        
        Args:
            repo_db_path: Path to repository database
            
        Returns:
            Dict with repo metadata or None if not found
        """
        try:
            if not Path(repo_db_path).exists():
                return None
            
            conn = sqlite3.connect(repo_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM repo_metadata LIMIT 1")
            row = cursor.fetchone()
            
            conn.close()
            
            return dict(row) if row else None
            
        except Exception as e:
            self.logger.error(f"Error retrieving repo metadata: {e}")
            return None
    
    def list_isolated_databases(self) -> List[Dict]:
        """
        List all isolated audit databases.
        
        Returns:
            List of dicts with repo_id, path, and metadata
        """
        databases = []
        
        try:
            if not self.audit_base_path.exists():
                return databases
            
            for db_file in self.audit_base_path.glob("audit_*.db"):
                metadata = self.get_repo_metadata(str(db_file))
                databases.append({
                    "db_file": db_file.name,
                    "db_path": str(db_file),
                    "metadata": metadata
                })
            
        except Exception as e:
            self.logger.error(f"Error listing databases: {e}")
        
        return databases
    
    def verify_isolation(self, repo_db_path: str) -> Dict:
        """
        Verify that database contains only events from its repo.
        
        Args:
            repo_db_path: Path to repository database
            
        Returns:
            Dict with verification results (isolated: bool, details: str)
        """
        try:
            if not Path(repo_db_path).exists():
                return {"isolated": True, "details": "Database doesn't exist yet"}
            
            conn = sqlite3.connect(repo_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            # Get repo_id from metadata
            cursor.execute("SELECT repo_id FROM repo_metadata LIMIT 1")
            metadata_row = cursor.fetchone()
            
            if not metadata_row:
                return {"isolated": False, "details": "No metadata found"}
            
            repo_id = metadata_row["repo_id"]
            
            # Check for events with mismatched repo_id
            cursor.execute(
                "SELECT COUNT(*) as bad_count FROM audit_events WHERE repo_id != ?",
                (repo_id,)
            )
            bad_count = cursor.fetchone()["bad_count"]
            
            conn.close()
            
            if bad_count > 0:
                return {
                    "isolated": False,
                    "details": f"Found {bad_count} events with mismatched repo_id"
                }
            
            return {"isolated": True, "details": "All events properly isolated"}
            
        except Exception as e:
            self.logger.error(f"Error verifying isolation: {e}")
            return {"isolated": False, "details": f"Error: {e}"}
    
    def log_event_to_repo(
        self,
        repo_identity: RepositoryIdentity,
        timestamp: str,
        level: str,
        category: str,
        message: str,
        actor: Optional[str] = None,
        resource: Optional[str] = None,
        ac_id: Optional[str] = None,
        correlation_id: Optional[str] = None
    ) -> bool:
        """
        Log audit event to repository's isolated database.
        
        Args:
            repo_identity: Repository identity
            timestamp: Event timestamp (ISO format)
            level: Log level
            category: Event category
            message: Event message
            actor: Actor performing action
            resource: Resource affected
            ac_id: Associated AC-ID
            correlation_id: Correlation ID for tracing
            
        Returns:
            True if logged successfully
        """
        try:
            repo_db_path = self.initialize_repo_db(repo_identity)
            
            conn = sqlite3.connect(repo_db_path)
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT INTO audit_events
                (repo_id, timestamp, level, category, message, actor, resource, ac_id, correlation_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                repo_identity.repo_id,
                timestamp,
                level,
                category,
                message,
                actor,
                resource,
                ac_id,
                correlation_id
            ))
            
            conn.commit()
            conn.close()
            
            return True
            
        except Exception as e:
            self.logger.error(f"Error logging event to repo {repo_identity.repo_name}: {e}")
            return False
    
    def query_repo_events(
        self,
        repo_db_path: str,
        level: Optional[str] = None,
        ac_id: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict]:
        """
        Query events from isolated repository database.
        
        Args:
            repo_db_path: Path to repository database
            level: Filter by log level
            ac_id: Filter by AC-ID
            limit: Maximum results
            
        Returns:
            List of audit events
        """
        events = []
        
        try:
            if not Path(repo_db_path).exists():
                return events
            
            conn = sqlite3.connect(repo_db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            query = "SELECT * FROM audit_events WHERE 1=1"
            params = []
            
            if level:
                query += " AND level = ?"
                params.append(level)
            
            if ac_id:
                query += " AND ac_id = ?"
                params.append(ac_id)
            
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            
            cursor.execute(query, params)
            
            for row in cursor.fetchall():
                events.append(dict(row))
            
            conn.close()
            
        except Exception as e:
            self.logger.error(f"Error querying repo events: {e}")
        
        return events
