"""
Knowledge Indexer - Tier 3.

Provides automated indexing of knowledge entries with AC-ID mapping.

AC: KN-001-02 - Auto-Indexing System
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import json


@dataclass
class IndexEntry:
    """Represents an indexed knowledge entry."""
    entry_id: str
    domain: str
    title: str
    ac_ids: List[str]
    created_at: str
    quality_score: Optional[float] = None
    file_path: Optional[str] = None


class KnowledgeIndexer:
    """Automated knowledge indexing system."""
    
    def __init__(self) -> None:
        """Initialize knowledge indexer."""
        self._index_file = Path(__file__).parent / ".knowledge-index.json"
        self._index_data: Dict[str, Any] = {}
        self._load_index()
    
    def _load_index(self) -> None:
        """Load existing index or create new one."""
        if self._index_file.exists():
            with open(self._index_file, 'r') as f:
                self._index_data = json.load(f)
        else:
            self._index_data = {
                "metadata": {
                    "version": "1.0",
                    "created_at": datetime.now().isoformat(),
                    "entry_count": 0,
                    "last_updated": datetime.now().isoformat()
                },
                "entries": [],
                "ac_id_mapping": {},
                "domain_mapping": {}
            }
            self._save_index()
    
    def _save_index(self) -> None:
        """Save index to file."""
        self._index_data["metadata"]["last_updated"] = datetime.now().isoformat()
        with open(self._index_file, 'w') as f:
            json.dump(self._index_data, f, indent=2)
    
    def index_entry(self, entry: Dict[str, Any]) -> bool:
        """
        Index a knowledge entry.
        
        Args:
            entry: Entry to index
            
        Returns:
            True if indexed successfully
        """
        index_entry = {
            "entry_id": entry["entry_id"],
            "domain": entry.get("domain", ""),
            "title": entry.get("title", ""),
            "ac_ids": entry.get("ac_ids", []),
            "created_at": entry.get("created_at", datetime.now().isoformat()),
            "quality_score": entry.get("quality_score"),
            "file_path": entry.get("file_path")
        }
        
        # Add to entries
        self._index_data["entries"].append(index_entry)
        
        # Update AC-ID mapping
        for ac_id in entry.get("ac_ids", []):
            if ac_id not in self._index_data["ac_id_mapping"]:
                self._index_data["ac_id_mapping"][ac_id] = []
            self._index_data["ac_id_mapping"][ac_id].append(entry["entry_id"])
        
        # Update domain mapping
        domain = entry.get("domain", "")
        if domain:
            if domain not in self._index_data["domain_mapping"]:
                self._index_data["domain_mapping"][domain] = []
            self._index_data["domain_mapping"][domain].append(entry["entry_id"])
        
        # Update metadata
        self._index_data["metadata"]["entry_count"] = len(self._index_data["entries"])
        self._save_index()
        
        return True
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        """
        Search index for matching entries.
        
        Args:
            query: Search query
            
        Returns:
            List of matching entries
        """
        query_lower = query.lower()
        results = []
        
        for entry in self._index_data["entries"]:
            if (query_lower in entry["title"].lower() or
                query_lower in entry["domain"].lower() or
                query_lower in entry["entry_id"].lower()):
                results.append(entry)
        
        return results
    
    def search_by_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Search entries by domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of entries in domain
        """
        return [
            entry for entry in self._index_data["entries"]
            if entry["domain"] == domain
        ]
    
    def search_by_ac_id(self, ac_id: str) -> List[Dict[str, Any]]:
        """
        Search entries by AC-ID.
        
        Args:
            ac_id: AC-ID to search
            
        Returns:
            List of entries with AC-ID
        """
        entry_ids = self._index_data["ac_id_mapping"].get(ac_id, [])
        return [
            entry for entry in self._index_data["entries"]
            if entry["entry_id"] in entry_ids
        ]
    
    def get_ac_id_mapping(self, ac_id: str) -> Optional[List[str]]:
        """
        Get entry IDs for AC-ID.
        
        Args:
            ac_id: AC-ID to lookup
            
        Returns:
            List of entry IDs or None
        """
        return self._index_data["ac_id_mapping"].get(ac_id)
    
    def get_entries_for_domain(self, domain: str) -> List[Dict[str, Any]]:
        """
        Get all entries for a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of entries
        """
        return self.search_by_domain(domain)
    
    def rebuild_index(self) -> int:
        """
        Rebuild entire index from knowledge files.
        
        Returns:
            Number of entries indexed
        """
        # Clear existing index
        self._index_data["entries"] = []
        self._index_data["ac_id_mapping"] = {}
        self._index_data["domain_mapping"] = {}
        
        # Re-index would scan knowledge directory
        # For now, just save empty index
        self._index_data["metadata"]["entry_count"] = 0
        self._save_index()
        
        return 0


__all__ = ["KnowledgeIndexer", "IndexEntry"]
