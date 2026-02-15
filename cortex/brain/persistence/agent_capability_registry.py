"""
Agent Capability Registry

AC_START: AC-PHASE27-S3-002
Component: AgentCapabilityRegistry
Authority: Phase 27 Consolidation (GAP-03)

Objective:
Capability storage and retrieval for agent discovery. Stores agent capabilities
in SQLite with versioning support. Enables capability-based discovery for
systematic agent handoff.

Features:
• SQLite backend with WAL mode (concurrent sessions)
• Capability registration and updates
• Version tracking per agent
• Cross-session persistence
• Metadata storage (agent version, mode, etc.)

Performance Targets:
• Registration: <10ms
• Retrieval: <5ms
• Update: <10ms

AC_COMPLETE: AC-PHASE27-S3-002
"""

import sqlite3
import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime
from threading import Lock

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================


@dataclass
class AgentCapability:
    """Agent capability record."""
    agent_id: str
    agent_name: str
    capabilities: List[str]
    metadata: Dict[str, Any]
    registered_at: str
    updated_at: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)


# ============================================================================
# AGENT CAPABILITY REGISTRY
# ============================================================================


class AgentCapabilityRegistry:
    """
    Agent Capability Registry: Capability storage and retrieval.
    
    Stores agent capabilities in SQLite with version tracking. Enables
    capability-based discovery for systematic agent handoff.
    
    Example:
        >>> registry = AgentCapabilityRegistry()
        >>> registry.register_agent(
        ...     agent_id="tdd_orchestrator",
        ...     agent_name="TDDOrchestrator",
        ...     capabilities=["test_generation", "coverage_analysis"],
        ...     metadata={"version": "1.0"}
        ... )
        >>> agent = registry.get_agent("tdd_orchestrator")
        >>> print(agent["capabilities"])
        ['test_generation', 'coverage_analysis']
    """
    
    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize Agent Capability Registry.
        
        Args:
            db_path: Path to SQLite database (default: cortex/brain/agent_capabilities.db)
        """
        if db_path is None:
            db_path = str(Path(__file__).parent.parent / "agent_capabilities.db")
        
        self.db_path = db_path
        self._lock = Lock()
        self._init_database()
        
        logger.info(f"AgentCapabilityRegistry initialized: {db_path}")
    
    def _init_database(self) -> None:
        """Initialize database schema."""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA journal_mode=WAL")  # Enable Write-Ahead Logging
            
            # Agent capabilities table
            conn.execute("""
                CREATE TABLE IF NOT EXISTS agent_capabilities (
                    agent_id TEXT PRIMARY KEY,
                    agent_name TEXT NOT NULL,
                    capabilities TEXT NOT NULL,
                    metadata TEXT,
                    registered_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            
            # Capability index for fast discovery
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_capabilities
                ON agent_capabilities(capabilities)
            """)
            
            conn.commit()
            conn.close()
    
    def register_agent(
        self,
        agent_id: str,
        agent_name: str,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Register agent with capabilities.
        
        Args:
            agent_id: Unique agent identifier
            agent_name: Human-readable agent name
            capabilities: List of capability identifiers
            metadata: Optional metadata (version, mode, etc.)
        
        Returns:
            Registered agent_id
        
        Example:
            >>> registry.register_agent(
            ...     agent_id="tdd_orchestrator",
            ...     agent_name="TDDOrchestrator",
            ...     capabilities=["test_generation", "coverage_analysis"],
            ...     metadata={"version": "1.0", "mode": "production"}
            ... )
            'tdd_orchestrator'
        """
        if metadata is None:
            metadata = {}
        
        now = datetime.utcnow().isoformat()
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            
            # Check if agent already exists
            cursor = conn.execute(
                "SELECT agent_id FROM agent_capabilities WHERE agent_id = ?",
                (agent_id,)
            )
            exists = cursor.fetchone() is not None
            
            if exists:
                # Update existing agent
                conn.execute("""
                    UPDATE agent_capabilities
                    SET capabilities = ?, metadata = ?, updated_at = ?
                    WHERE agent_id = ?
                """, (
                    json.dumps(capabilities),
                    json.dumps(metadata),
                    now,
                    agent_id
                ))
                logger.info(f"Updated agent: {agent_id}")
            else:
                # Insert new agent
                conn.execute("""
                    INSERT INTO agent_capabilities
                    (agent_id, agent_name, capabilities, metadata, registered_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    agent_id,
                    agent_name,
                    json.dumps(capabilities),
                    json.dumps(metadata),
                    now,
                    now
                ))
                logger.info(f"Registered agent: {agent_id}")
            
            conn.commit()
            conn.close()
        
        return agent_id
    
    def get_agent(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """
        Get agent by ID.
        
        Args:
            agent_id: Agent identifier
        
        Returns:
            Agent record or None if not found
        
        Example:
            >>> agent = registry.get_agent("tdd_orchestrator")
            >>> print(agent["capabilities"])
            ['test_generation', 'coverage_analysis']
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("""
                SELECT * FROM agent_capabilities
                WHERE agent_id = ?
            """, (agent_id,))
            
            row = cursor.fetchone()
            conn.close()
            
            if row is None:
                return None
            
            return {
                "agent_id": row["agent_id"],
                "agent_name": row["agent_name"],
                "capabilities": json.loads(row["capabilities"]),
                "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                "registered_at": row["registered_at"],
                "updated_at": row["updated_at"]
            }
    
    def get_all_agents(self) -> List[Dict[str, Any]]:
        """
        Get all registered agents.
        
        Returns:
            List of all agent records
        
        Example:
            >>> agents = registry.get_all_agents()
            >>> print(len(agents))
            4
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            cursor = conn.execute("SELECT * FROM agent_capabilities")
            rows = cursor.fetchall()
            conn.close()
            
            agents = []
            for row in rows:
                agents.append({
                    "agent_id": row["agent_id"],
                    "agent_name": row["agent_name"],
                    "capabilities": json.loads(row["capabilities"]),
                    "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                    "registered_at": row["registered_at"],
                    "updated_at": row["updated_at"]
                })
            
            return agents
    
    def update_agent_capabilities(
        self,
        agent_id: str,
        capabilities: List[str],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Update agent capabilities.
        
        Args:
            agent_id: Agent identifier
            capabilities: New capability list
            metadata: Optional metadata updates
        
        Returns:
            True if updated, False if agent not found
        
        Example:
            >>> registry.update_agent_capabilities(
            ...     agent_id="tdd_orchestrator",
            ...     capabilities=["test_generation", "coverage_analysis", "mutation_testing"],
            ...     metadata={"version": "1.1"}
            ... )
            True
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            
            # Check if agent exists
            cursor = conn.execute(
                "SELECT agent_id FROM agent_capabilities WHERE agent_id = ?",
                (agent_id,)
            )
            exists = cursor.fetchone() is not None
            
            if not exists:
                conn.close()
                return False
            
            # Update capabilities
            now = datetime.utcnow().isoformat()
            
            if metadata is not None:
                conn.execute("""
                    UPDATE agent_capabilities
                    SET capabilities = ?, metadata = ?, updated_at = ?
                    WHERE agent_id = ?
                """, (
                    json.dumps(capabilities),
                    json.dumps(metadata),
                    now,
                    agent_id
                ))
            else:
                conn.execute("""
                    UPDATE agent_capabilities
                    SET capabilities = ?, updated_at = ?
                    WHERE agent_id = ?
                """, (
                    json.dumps(capabilities),
                    now,
                    agent_id
                ))
            
            conn.commit()
            conn.close()
            
            logger.info(f"Updated capabilities for agent: {agent_id}")
            return True
    
    def find_agents_by_capability(self, capability: str) -> List[Dict[str, Any]]:
        """
        Find agents with specific capability.
        
        Args:
            capability: Capability identifier
        
        Returns:
            List of agents with the capability
        
        Example:
            >>> agents = registry.find_agents_by_capability("test_generation")
            >>> print([a["agent_id"] for a in agents])
            ['tdd_orchestrator']
        """
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            
            # SQLite JSON search using LIKE (capabilities stored as JSON array)
            cursor = conn.execute("""
                SELECT * FROM agent_capabilities
                WHERE capabilities LIKE ?
            """, (f'%"{capability}"%',))
            
            rows = cursor.fetchall()
            conn.close()
            
            agents = []
            for row in rows:
                capabilities = json.loads(row["capabilities"])
                # Verify capability actually present (not substring match)
                if capability in capabilities:
                    agents.append({
                        "agent_id": row["agent_id"],
                        "agent_name": row["agent_name"],
                        "capabilities": capabilities,
                        "metadata": json.loads(row["metadata"]) if row["metadata"] else {},
                        "registered_at": row["registered_at"],
                        "updated_at": row["updated_at"]
                    })
            
            return agents
    
    def close(self) -> None:
        """Close registry (cleanup resources)."""
        logger.info("AgentCapabilityRegistry closed")
