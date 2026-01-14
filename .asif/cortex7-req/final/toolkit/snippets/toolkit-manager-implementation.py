"""
CORTEX Toolkit Manager - Core Orchestrator
Purpose: Manages toolkit lifecycle (create, update, deprecate tools)
Author: Asif Hussain
Date: 2026-01-14
"""

from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import sqlite3
import yaml
from datetime import datetime, timezone


@dataclass
class ToolSpec:
    """Specification for a new tool"""
    name: str
    tier: str
    category: str
    capability_description: str
    dependencies: List[str]
    file_path: Optional[Path] = None


class ToolkitManager:
    """
    Manages CORTEX Toolkit lifecycle and registry.
    
    Responsibilities:
    - Register new tools in tool_registry.yaml + toolkit.db
    - Check for duplicate/similar tools
    - Manage tool versioning
    - Handle deprecation workflow
    """
    
    def __init__(self, registry_path: Path, db_path: Path):
        self.registry_path = registry_path
        self.db_path = db_path
        self.conn = sqlite3.connect(str(db_path))
        self._ensure_schema()
    
    def _ensure_schema(self):
        """Create toolkit.db schema if not exists"""
        cursor = self.conn.cursor()
        
        # Tool registry table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tool_registry (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL,
                tier TEXT NOT NULL,
                version TEXT NOT NULL,
                capability_description TEXT,
                file_path TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT,
                deprecated_at TEXT,
                usage_count INTEGER DEFAULT 0,
                avg_execution_time_ms REAL
            )
        """)
        
        # Capability embeddings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS capability_embeddings (
                tool_id INTEGER,
                embedding BLOB,
                model_version TEXT,
                created_at TEXT,
                FOREIGN KEY(tool_id) REFERENCES tool_registry(id)
            )
        """)
        
        # Usage analytics table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usage_analytics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tool_id INTEGER,
                timestamp TEXT,
                orchestrator TEXT,
                execution_time_ms REAL,
                success BOOLEAN,
                error_message TEXT,
                FOREIGN KEY(tool_id) REFERENCES tool_registry(id)
            )
        """)
        
        self.conn.commit()
    
    def register_tool(self, spec: ToolSpec) -> bool:
        """
        Register new tool in registry + database.
        
        Args:
            spec: Tool specification
            
        Returns:
            True if registered, False if duplicate exists
        """
        # Check for duplicates
        if self.tool_exists(spec.name):
            return False
        
        # Load current registry
        if self.registry_path.exists():
            registry = yaml.safe_load(self.registry_path.read_text())
        else:
            registry = {"tools": []}
        
        # Add new tool
        tool_entry = {
            "name": spec.name,
            "tier": spec.tier,
            "version": "1.0.0",
            "capability_description": spec.capability_description,
            "file_path": str(spec.file_path),
            "dependencies": spec.dependencies,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
        
        registry["tools"].append(tool_entry)
        
        # Write registry (atomic)
        self.registry_path.write_text(yaml.dump(registry, sort_keys=False))
        
        # Insert into database
        cursor = self.conn.cursor()
        cursor.execute("""
            INSERT INTO tool_registry 
            (name, tier, version, capability_description, file_path, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            spec.name,
            spec.tier,
            "1.0.0",
            spec.capability_description,
            str(spec.file_path),
            datetime.now(timezone.utc).isoformat()
        ))
        self.conn.commit()
        
        return True
    
    def tool_exists(self, name: str) -> bool:
        """Check if tool already registered"""
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM tool_registry WHERE name = ?", (name,))
        count = cursor.fetchone()[0]
        return count > 0
    
    def get_tool(self, name: str) -> Optional[Dict[str, Any]]:
        """Get tool metadata from registry"""
        cursor = self.conn.cursor()
        cursor.execute("""
            SELECT name, tier, version, capability_description, file_path, 
                   created_at, deprecated_at
            FROM tool_registry 
            WHERE name = ?
        """, (name,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        return {
            "name": row[0],
            "tier": row[1],
            "version": row[2],
            "capability_description": row[3],
            "file_path": row[4],
            "created_at": row[5],
            "deprecated": row[6] is not None
        }
    
    def deprecate_tool(self, name: str, replacement: Optional[str] = None) -> bool:
        """Mark tool as deprecated"""
        cursor = self.conn.cursor()
        cursor.execute("""
            UPDATE tool_registry 
            SET deprecated_at = ?,
                updated_at = ?
            WHERE name = ?
        """, (
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat(),
            name
        ))
        self.conn.commit()
        
        # Log to audit trail
        # TODO: Integrate with EnterpriseAuditLogger
        
        return True
    
    def list_tools(self, tier: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all registered tools, optionally filtered by tier"""
        cursor = self.conn.cursor()
        
        if tier:
            cursor.execute("""
                SELECT name, tier, version, capability_description, deprecated_at
                FROM tool_registry
                WHERE tier = ?
                ORDER BY tier, name
            """, (tier,))
        else:
            cursor.execute("""
                SELECT name, tier, version, capability_description, deprecated_at
                FROM tool_registry
                ORDER BY tier, name
            """)
        
        tools = []
        for row in cursor.fetchall():
            tools.append({
                "name": row[0],
                "tier": row[1],
                "version": row[2],
                "capability_description": row[3],
                "deprecated": row[4] is not None
            })
        
        return tools


# ============================================================================
# TESTS
# ============================================================================

import pytest
from pathlib import Path


@pytest.fixture
def toolkit_manager(tmp_path):
    """Create ToolkitManager with temp registry/db"""
    registry_path = tmp_path / "tool_registry.yaml"
    db_path = tmp_path / "toolkit.db"
    return ToolkitManager(registry_path, db_path)


@pytest.mark.unit
def test_register_tool(toolkit_manager, tmp_path):
    """Test registering a new tool"""
    spec = ToolSpec(
        name="test_tool",
        tier="tier0",
        category="test_category",
        capability_description="Test tool for unit testing",
        dependencies=[],
        file_path=tmp_path / "test_tool.py"
    )
    
    success = toolkit_manager.register_tool(spec)
    assert success == True
    
    # Verify registration
    tool = toolkit_manager.get_tool("test_tool")
    assert tool is not None
    assert tool["name"] == "test_tool"
    assert tool["tier"] == "tier0"


@pytest.mark.unit
def test_register_duplicate_tool(toolkit_manager, tmp_path):
    """Test that duplicate registration is blocked"""
    spec = ToolSpec(
        name="duplicate_tool",
        tier="tier0",
        category="test",
        capability_description="Test",
        dependencies=[],
        file_path=tmp_path / "tool.py"
    )
    
    # First registration
    success1 = toolkit_manager.register_tool(spec)
    assert success1 == True
    
    # Second registration (should fail)
    success2 = toolkit_manager.register_tool(spec)
    assert success2 == False
