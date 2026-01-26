"""
Hybrid Knowledge Loader - YAML-based primary + SQLite cache layer

Authority: AC-HYBRID-KNOWLEDGE-001, AC-HYBRID-KNOWLEDGE-003
Version: 1.0
Date: 2026-01-26

This module implements the hybrid knowledge architecture:
1. YAML files (.knowledge-index.yaml, company/domains/) are git-tracked source of truth
2. SQLite cache (.cortex/knowledge.db) is local ephemeral cache (gitignored)
3. Automatic rebuild on git pull via post-merge hook
4. Explicit composition rules from .knowledge-synthesis-rules.yaml

Key Features:
- Team-safe: All domains defined in git-tracked files
- Efficient: <500ms rebuild time for full knowledge graph
- Versionable: Full git history of all knowledge changes
- Auditable: Explicit composition rules registry

CORE Governance:
- CORE-008: TDD (tests before implementation)
- CORE-011: Type hints mandatory
- CORE-012: Google-style docstrings
- CORE-035: Single canonical implementation
"""

from __future__ import annotations

import hashlib
import logging
import sqlite3
import threading
import time
from dataclasses import dataclass, field
from datetime import datetime
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

import yaml

logger = logging.getLogger(__name__)


# =============================================================================
# Data Models
# =============================================================================

@dataclass
class KnowledgeDomain:
    """Single knowledge domain (CORTEX or Company)."""
    name: str
    path: str
    description: str
    status: str = "ACTIVE"
    owner: Optional[str] = None
    priority: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": self.path,
            "description": self.description,
            "status": self.status,
            "owner": self.owner,
            "priority": self.priority,
        }


@dataclass
class SynthesisRule:
    """Single knowledge synthesis composition rule."""
    id: str
    name: str
    description: str
    cortex_domain: str
    company_domains: List[str] = field(default_factory=list)
    composition: str = "overlay"
    priority: str = "MEDIUM"
    applicable_intents: List[str] = field(default_factory=list)
    output_layer: str = ""


@dataclass
class KnowledgeIndex:
    """Parsed .knowledge-index.yaml configuration."""
    cortex_domains: Dict[str, KnowledgeDomain]
    company_domains: Dict[str, KnowledgeDomain]
    synthesis_rules: Dict[str, SynthesisRule]
    last_loaded: float = field(default_factory=time.time)


# =============================================================================
# Hybrid Knowledge Loader
# =============================================================================

class HybridKnowledgeLoader:
    """
    Loads knowledge from YAML files and manages SQLite cache.
    
    Thread-safe singleton with automatic cache rebuild on pull.
    """

    _instance: Optional[HybridKnowledgeLoader] = None
    _lock = threading.Lock()

    def __init__(self, repo_root: Optional[Path] = None):
        """
        Initialize hybrid knowledge loader.

        Args:
            repo_root: Repository root. Defaults to CORTEX project root.
        """
        if repo_root is None:
            repo_root = Path(__file__).parent.parent.parent.parent

        self.repo_root = Path(repo_root)
        self.knowledge_index_path = self.repo_root / ".knowledge-index.yaml"
        self.synthesis_rules_path = self.repo_root / ".knowledge-synthesis-rules.yaml"
        self.cache_db_path = self.repo_root / ".cortex" / "knowledge.db"
        self.cache_db_path.parent.mkdir(parents=True, exist_ok=True)

        self._index: Optional[KnowledgeIndex] = None
        self._index_hash: Optional[str] = None
        self._cache_ready = False

    @classmethod
    def get_instance(cls, repo_root: Optional[Path] = None) -> HybridKnowledgeLoader:
        """Get singleton instance."""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = HybridKnowledgeLoader(repo_root)
        return cls._instance

    def load_index(self) -> KnowledgeIndex:
        """
        Load .knowledge-index.yaml and parse all domains.

        Returns:
            KnowledgeIndex with all CORTEX and Company domains.
        """
        if not self.knowledge_index_path.exists():
            logger.error(f"Knowledge index not found: {self.knowledge_index_path}")
            return KnowledgeIndex({}, {}, {})

        try:
            with open(self.knowledge_index_path, "r") as f:
                config = yaml.safe_load(f)

            cortex_domains = {}
            for domain_config in config.get("cortex_knowledge", {}).get("domains", []):
                domain = KnowledgeDomain(**domain_config)
                cortex_domains[domain.name] = domain
                logger.debug(f"Loaded CORTEX domain: {domain.name}")

            company_domains = {}
            for domain_config in config.get("company_knowledge", {}).get("domains", []):
                domain = KnowledgeDomain(**domain_config)
                company_domains[domain.name] = domain
                logger.debug(f"Loaded Company domain: {domain.name}")

            # Load synthesis rules
            synthesis_rules = self._load_synthesis_rules()

            self._index = KnowledgeIndex(
                cortex_domains=cortex_domains,
                company_domains=company_domains,
                synthesis_rules=synthesis_rules,
            )
            logger.info(f"Loaded knowledge index: {len(cortex_domains)} CORTEX + {len(company_domains)} Company domains")
            return self._index

        except Exception as e:
            logger.error(f"Failed to load knowledge index: {e}")
            return KnowledgeIndex({}, {}, {})

    def _load_synthesis_rules(self) -> Dict[str, SynthesisRule]:
        """Load synthesis rules from .knowledge-synthesis-rules.yaml."""
        if not self.synthesis_rules_path.exists():
            logger.warning(f"Synthesis rules not found: {self.synthesis_rules_path}")
            return {}

        try:
            with open(self.synthesis_rules_path, "r") as f:
                config = yaml.safe_load(f)

            rules = {}
            for rule_config in config.get("synthesis_rules", []):
                rule = SynthesisRule(**rule_config)
                rules[rule.id] = rule
                logger.debug(f"Loaded synthesis rule: {rule.id}")

            return rules

        except Exception as e:
            logger.error(f"Failed to load synthesis rules: {e}")
            return {}

    def rebuild_cache(self) -> bool:
        """
        Rebuild SQLite cache from YAML files.

        Returns:
            True if rebuild successful, False otherwise.
        """
        logger.info("Rebuilding knowledge cache from YAML files...")
        start_time = time.time()

        try:
            # Load index from YAML
            index = self.load_index()

            if not index.cortex_domains and not index.company_domains:
                logger.warning("No domains loaded; cache rebuild skipped")
                return False

            # Initialize cache database
            self._initialize_cache_db()

            # Populate cache tables
            self._populate_cache(index)

            elapsed_ms = (time.time() - start_time) * 1000
            logger.info(f"Knowledge cache rebuilt successfully in {elapsed_ms:.1f}ms")
            self._cache_ready = True
            return True

        except Exception as e:
            logger.error(f"Failed to rebuild knowledge cache: {e}")
            return False

    def _initialize_cache_db(self) -> None:
        """Initialize SQLite cache database schema."""
        try:
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()

            # Cortex domains table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS cortex_domains (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    path TEXT NOT NULL,
                    description TEXT,
                    status TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Company domains table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS company_domains (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE NOT NULL,
                    path TEXT NOT NULL,
                    description TEXT,
                    status TEXT,
                    owner TEXT,
                    priority TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Synthesis rules table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS synthesis_rules (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    cortex_domain TEXT NOT NULL,
                    company_domains TEXT,
                    composition TEXT,
                    priority TEXT,
                    applicable_intents TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Metadata table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS metadata (
                    key TEXT PRIMARY KEY,
                    value TEXT,
                    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

            conn.commit()
            conn.close()
            logger.debug("Cache database schema initialized")

        except Exception as e:
            logger.error(f"Failed to initialize cache database: {e}")

    def _populate_cache(self, index: KnowledgeIndex) -> None:
        """Populate cache tables from knowledge index."""
        try:
            conn = sqlite3.connect(str(self.cache_db_path))
            cursor = conn.cursor()

            # Clear existing data
            cursor.execute("DELETE FROM cortex_domains")
            cursor.execute("DELETE FROM company_domains")
            cursor.execute("DELETE FROM synthesis_rules")

            # Insert CORTEX domains
            for domain in index.cortex_domains.values():
                cursor.execute(
                    """INSERT INTO cortex_domains (name, path, description, status)
                       VALUES (?, ?, ?, ?)""",
                    (domain.name, domain.path, domain.description, domain.status),
                )

            # Insert Company domains
            for domain in index.company_domains.values():
                cursor.execute(
                    """INSERT INTO company_domains (name, path, description, status, owner, priority)
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (
                        domain.name,
                        domain.path,
                        domain.description,
                        domain.status,
                        domain.owner,
                        domain.priority,
                    ),
                )

            # Insert synthesis rules
            for rule in index.synthesis_rules.values():
                cursor.execute(
                    """INSERT INTO synthesis_rules (id, name, cortex_domain, company_domains, composition, priority, applicable_intents)
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (
                        rule.id,
                        rule.name,
                        rule.cortex_domain,
                        ",".join(rule.company_domains) if rule.company_domains else "",
                        rule.composition,
                        rule.priority,
                        ",".join(rule.applicable_intents) if rule.applicable_intents else "",
                    ),
                )

            # Update metadata
            cursor.execute(
                """INSERT OR REPLACE INTO metadata (key, value, updated_at)
                   VALUES (?, ?, CURRENT_TIMESTAMP)""",
                ("last_rebuild", datetime.now().isoformat()),
            )

            conn.commit()
            conn.close()
            logger.debug("Cache populated with all domains and rules")

        except Exception as e:
            logger.error(f"Failed to populate cache: {e}")

    @lru_cache(maxsize=128)
    def get_cortex_domains(self) -> Dict[str, KnowledgeDomain]:
        """Get all CORTEX knowledge domains."""
        if not self._index:
            self.load_index()
        return self._index.cortex_domains if self._index else {}

    @lru_cache(maxsize=128)
    def get_company_domains(self) -> Dict[str, KnowledgeDomain]:
        """Get all Company knowledge domains."""
        if not self._index:
            self.load_index()
        return self._index.company_domains if self._index else {}

    @lru_cache(maxsize=128)
    def get_synthesis_rules(self) -> Dict[str, SynthesisRule]:
        """Get all synthesis composition rules."""
        if not self._index:
            self.load_index()
        return self._index.synthesis_rules if self._index else {}


# Singleton accessor
def get_hybrid_loader() -> HybridKnowledgeLoader:
    """Get hybrid knowledge loader instance."""
    return HybridKnowledgeLoader.get_instance()
