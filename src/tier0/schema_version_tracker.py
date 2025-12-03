"""
Schema Version Tracker

Tracks schema versions for all 3 brain tiers, detects migration needs,
and maintains version history.

Responsibilities:
- Get/set current schema versions per tier
- Detect when migrations are needed
- Track version history
- Log applied migrations
- Define latest available schema versions

Storage:
- Versions stored in Tier 1 metadata table
- Format: JSON with version number and timestamp
- History stored as JSON array

Usage:
    >>> from src.tier0.schema_version_tracker import SchemaVersionTracker
    >>> tracker = SchemaVersionTracker(brain_path="/path/to/cortex-brain")
    >>> version = tracker.get_version('tier2')
    >>> if tracker.needs_migration('tier2', target_version=2):
    ...     # Apply migration
    ...     tracker.record_migration('tier2', 1, 2, 'Add FTS5 support')

Author: Asif Hussain
Phase: 7.3 - Brain Initialization System
"""

import sqlite3
from pathlib import Path
from typing import Dict, Any, List, Optional
from datetime import datetime
import json


class SchemaVersionTracker:
    """
    Tracks schema versions across all 3 brain tiers.
    
    Provides version management, migration detection, and history tracking.
    """
    
    # Latest schema versions (hardcoded based on current schemas)
    LATEST_VERSIONS = {
        'tier1': 1,  # Working Memory schema v1
        'tier2': 1,  # Knowledge Graph schema v1
        'tier3': 1   # Development Context schema v1
    }
    
    def __init__(self, brain_path: str):
        """
        Initialize version tracker with brain path.
        
        Args:
            brain_path: Absolute path to cortex-brain directory
        """
        self.brain_path = Path(brain_path)
        self.tier1_db = self.brain_path / "tier1" / "working_memory.db"
    
    def get_version(self, tier: str) -> int:
        """
        Get current schema version for a tier.
        
        Args:
            tier: Tier name ('tier1', 'tier2', or 'tier3')
            
        Returns:
            Version number (integer), 0 if not set
        """
        if not self.tier1_db.exists():
            return 0
        
        try:
            conn = sqlite3.connect(str(self.tier1_db))
            cursor = conn.cursor()
            
            key = f'schema_version_{tier}'
            cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                data = json.loads(row[0])
                return data.get('version', 0)
            else:
                return 0
                
        except Exception:
            return 0
    
    def set_version(self, tier: str, version: int):
        """
        Set schema version for a tier.
        
        Args:
            tier: Tier name ('tier1', 'tier2', or 'tier3')
            version: Version number to set
        """
        if not self.tier1_db.exists():
            raise FileNotFoundError(f"Tier 1 database not found: {self.tier1_db}")
        
        conn = sqlite3.connect(str(self.tier1_db))
        cursor = conn.cursor()
        
        key = f'schema_version_{tier}'
        value_data = {
            'version': version,
            'updated_at': datetime.now().isoformat()
        }
        value = json.dumps(value_data)
        
        # Insert or update
        cursor.execute("""
            INSERT INTO metadata (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
        """, (key, value, datetime.now().isoformat()))
        
        # Get version history directly from current connection
        history_key = f'schema_version_history_{tier}'
        cursor.execute("SELECT value FROM metadata WHERE key = ?", (history_key,))
        row = cursor.fetchone()
        
        history = json.loads(row[0]) if row else []
        history.append({
            'version': version,
            'timestamp': datetime.now().isoformat()
        })
        
        history_value = json.dumps(history)
        cursor.execute("""
            INSERT INTO metadata (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
        """, (history_key, history_value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def needs_migration(self, tier: str, target_version: int) -> bool:
        """
        Check if migration is needed.
        
        Args:
            tier: Tier name
            target_version: Target version to migrate to
            
        Returns:
            True if current version < target version
        """
        current_version = self.get_version(tier)
        return current_version < target_version
    
    def get_version_history(self, tier: str) -> List[Dict[str, Any]]:
        """
        Get version history for a tier.
        
        Args:
            tier: Tier name
            
        Returns:
            List of version change records with version and timestamp
        """
        if not self.tier1_db.exists():
            return []
        
        try:
            conn = sqlite3.connect(str(self.tier1_db))
            cursor = conn.cursor()
            
            key = f'schema_version_history_{tier}'
            cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return json.loads(row[0])
            else:
                return []
                
        except Exception:
            return []
    
    def record_migration(
        self,
        tier: str,
        from_version: int,
        to_version: int,
        description: str
    ):
        """
        Record a migration in the log.
        
        Args:
            tier: Tier name
            from_version: Version migrated from
            to_version: Version migrated to
            description: Migration description
        """
        if not self.tier1_db.exists():
            raise FileNotFoundError(f"Tier 1 database not found: {self.tier1_db}")
        
        conn = sqlite3.connect(str(self.tier1_db))
        cursor = conn.cursor()
        
        # Get existing migrations directly from connection
        migrations_key = f'schema_migrations_{tier}'
        cursor.execute("SELECT value FROM metadata WHERE key = ?", (migrations_key,))
        row = cursor.fetchone()
        migrations = json.loads(row[0]) if row else []
        
        # Add new migration
        migrations.append({
            'from_version': from_version,
            'to_version': to_version,
            'description': description,
            'applied_at': datetime.now().isoformat()
        })
        
        # Store migrations
        value = json.dumps(migrations)
        cursor.execute("""
            INSERT INTO metadata (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
        """, (migrations_key, value, datetime.now().isoformat()))
        
        # Update current version (inline to avoid nested connection)
        version_key = f'schema_version_{tier}'
        version_data = {
            'version': to_version,
            'updated_at': datetime.now().isoformat()
        }
        version_value = json.dumps(version_data)
        
        cursor.execute("""
            INSERT INTO metadata (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
        """, (version_key, version_value, datetime.now().isoformat()))
        
        # Update version history (inline)
        history_key = f'schema_version_history_{tier}'
        cursor.execute("SELECT value FROM metadata WHERE key = ?", (history_key,))
        row = cursor.fetchone()
        history = json.loads(row[0]) if row else []
        
        history.append({
            'version': to_version,
            'timestamp': datetime.now().isoformat()
        })
        
        history_value = json.dumps(history)
        cursor.execute("""
            INSERT INTO metadata (key, value, updated_at)
            VALUES (?, ?, ?)
            ON CONFLICT(key) DO UPDATE SET
                value = excluded.value,
                updated_at = excluded.updated_at
        """, (history_key, history_value, datetime.now().isoformat()))
        
        conn.commit()
        conn.close()
    
    def get_applied_migrations(self, tier: str) -> List[Dict[str, Any]]:
        """
        Get list of applied migrations for a tier.
        
        Args:
            tier: Tier name
            
        Returns:
            List of migration records
        """
        if not self.tier1_db.exists():
            return []
        
        try:
            conn = sqlite3.connect(str(self.tier1_db))
            cursor = conn.cursor()
            
            key = f'schema_migrations_{tier}'
            cursor.execute("SELECT value FROM metadata WHERE key = ?", (key,))
            row = cursor.fetchone()
            
            conn.close()
            
            if row:
                return json.loads(row[0])
            else:
                return []
                
        except Exception:
            return []
    
    def get_latest_versions(self) -> Dict[str, int]:
        """
        Get latest available schema versions.
        
        Returns hardcoded schema versions based on actual schema files.
        
        Returns:
            Dict with tier names and latest version numbers
        """
        return self.LATEST_VERSIONS.copy()
