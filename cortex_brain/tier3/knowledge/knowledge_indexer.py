"""
Knowledge Indexer for Tier 3 Knowledge Repository
==================================================
Automatically indexes knowledge entries by domain and AC-ID.
Maintains AC-ID → domain mapping for governance audit trails.
Provides searchable API for knowledge retrieval.

AC-ID: KN-001-02
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from dataclasses import dataclass, asdict, field


@dataclass
class IndexEntry:
    """Represents an indexed knowledge entry."""
    entry_id: str
    domain: str
    title: str
    ac_ids: List[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    quality_score: Optional[float] = None
    file_path: Optional[str] = None


class KnowledgeIndexer:
    """
    Auto-indexing system for Tier 3 knowledge repository.
    
    Features:
    - Builds index on knowledge entry creation/update
    - Maintains AC-ID to domain mapping
    - Provides searchable API
    - Validates consistency
    - Integrates with governance audit
    """
    
    VALID_DOMAINS = [
        "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
        "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
        "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
        "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
        "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
    ]
    
    def __init__(self, knowledge_dir: Optional[Path] = None):
        """
        Initialize knowledge indexer.
        
        Args:
            knowledge_dir: Path to knowledge repository root.
                          Defaults to cortex-brain/tier3/knowledge/
        """
        if knowledge_dir is None:
            knowledge_dir = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex-brain/tier3/knowledge")
        
        self.knowledge_dir = Path(knowledge_dir)
        self.index_file = self.knowledge_dir / ".knowledge-index.json"
        self.entries: List[IndexEntry] = []
        self.ac_id_mapping: Dict[str, Dict[str, str]] = {}
        self.by_domain: Dict[str, List[str]] = {d: [] for d in self.VALID_DOMAINS}
        
        # Load existing index if available
        if self.index_file.exists():
            self._load_index()
        else:
            self._initialize_index()
    
    def _initialize_index(self) -> None:
        """Initialize empty index structure."""
        self.entries = []
        self.ac_id_mapping = {}
        self.by_domain = {d: [] for d in self.VALID_DOMAINS}
        self._save_index()
    
    def _load_index(self) -> None:
        """Load index from disk."""
        try:
            with open(self.index_file, 'r') as f:
                data = json.load(f)
            
            # Restore entries
            self.entries = [
                IndexEntry(**entry) for entry in data.get("entries", [])
            ]
            
            # Restore AC-ID mapping
            self.ac_id_mapping = data.get("ac_id_mapping", {})
            
            # Restore domain index
            self.by_domain = data.get("by_domain", {d: [] for d in self.VALID_DOMAINS})
        except (json.JSONDecodeError, IOError) as e:
            raise RuntimeError(f"Failed to load index: {e}")
    
    def _save_index(self) -> None:
        """Persist index to disk."""
        index_data = {
            "metadata": {
                "version": "1.0",
                "created_at": self._get_first_created_at(),
                "updated_at": datetime.utcnow().isoformat(),
                "entry_count": len(self.entries),
                "ac_id": "KN-001-02"
            },
            "entries": [asdict(entry) for entry in self.entries],
            "ac_id_mapping": self.ac_id_mapping,
            "by_domain": self.by_domain
        }
        
        try:
            with open(self.index_file, 'w') as f:
                json.dump(index_data, f, indent=2)
        except IOError as e:
            raise RuntimeError(f"Failed to save index: {e}")
    
    def _get_first_created_at(self) -> str:
        """Get the creation timestamp of the first entry or current time."""
        if self.entries:
            return self.entries[0].created_at
        return datetime.utcnow().isoformat()
    
    def rebuild_index(self) -> Dict[str, Any]:
        """
        Rebuild index from scratch by scanning knowledge directories.
        
        Returns:
            Dictionary with rebuild results (entries_found, errors)
        """
        self.entries = []
        self.ac_id_mapping = {}
        self.by_domain = {d: [] for d in self.VALID_DOMAINS}
        
        results = {
            "entries_found": 0,
            "errors": [],
            "domains_scanned": 0
        }
        
        # Scan each domain directory
        for domain_dir in self.knowledge_dir.iterdir():
            if not domain_dir.is_dir() or domain_dir.name.startswith("."):
                continue
            
            domain_name = domain_dir.name
            if domain_name not in self.VALID_DOMAINS:
                continue
            
            results["domains_scanned"] += 1
            
            # Look for knowledge entries in domain
            for entry_file in domain_dir.glob("KE-*.md"):
                try:
                    entry = self._parse_entry_file(entry_file, domain_name)
                    if entry:
                        self.entries.append(entry)
                        self.by_domain[domain_name].append(entry.entry_id)
                        
                        # Map AC-IDs
                        for ac_id in entry.ac_ids:
                            self.ac_id_mapping[ac_id] = {
                                "entry_id": entry.entry_id,
                                "domain": domain_name
                            }
                        
                        results["entries_found"] += 1
                except Exception as e:
                    results["errors"].append({
                        "file": str(entry_file),
                        "error": str(e)
                    })
        
        self._save_index()
        return results
    
    def _parse_entry_file(self, file_path: Path, domain: str) -> Optional[IndexEntry]:
        """
        Parse a knowledge entry file.
        
        Args:
            file_path: Path to entry file
            domain: Domain name
            
        Returns:
            Parsed IndexEntry or None
        """
        try:
            with open(file_path, 'r') as f:
                content = f.read()
            
            # Extract entry_id from filename
            entry_id = file_path.stem
            if not entry_id.startswith("KE-"):
                return None
            
            # Extract title from first markdown header
            title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
            title = title_match.group(1) if title_match else entry_id
            
            # Extract AC-IDs from content
            ac_ids = re.findall(r'AC-[A-Z]+-\d{3}-\d{2}', content)
            
            # Extract quality score if present
            quality_score = None
            score_match = re.search(r'Quality Score:\s*([\d.]+)', content)
            if score_match:
                try:
                    quality_score = float(score_match.group(1))
                except ValueError:
                    pass
            
            # Get file modification time as created_at
            created_at = datetime.fromtimestamp(file_path.stat().st_mtime).isoformat()
            
            return IndexEntry(
                entry_id=entry_id,
                domain=domain,
                title=title,
                ac_ids=ac_ids,
                created_at=created_at,
                quality_score=quality_score,
                file_path=str(file_path)
            )
        except Exception as e:
            raise ValueError(f"Failed to parse {file_path}: {e}")
    
    def add_entry(self, entry: IndexEntry) -> None:
        """
        Add a new entry to the index.
        
        Args:
            entry: IndexEntry to add
        """
        if entry.domain not in self.VALID_DOMAINS:
            raise ValueError(f"Invalid domain: {entry.domain}")
        
        # Check for duplicates
        existing = [e for e in self.entries if e.entry_id == entry.entry_id]
        if existing:
            raise ValueError(f"Entry {entry.entry_id} already exists")
        
        self.entries.append(entry)
        self.by_domain[entry.domain].append(entry.entry_id)
        
        # Update AC-ID mapping
        for ac_id in entry.ac_ids:
            self.ac_id_mapping[ac_id] = {
                "entry_id": entry.entry_id,
                "domain": entry.domain
            }
        
        self._save_index()
    
    def update_entry(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing entry.
        
        Args:
            entry_id: ID of entry to update
            updates: Dictionary of fields to update
            
        Returns:
            True if successful, False if entry not found
        """
        for entry in self.entries:
            if entry.entry_id == entry_id:
                # Update fields
                for key, value in updates.items():
                    if hasattr(entry, key):
                        setattr(entry, key, value)
                
                # Rebuild AC-ID mapping if AC-IDs changed
                if "ac_ids" in updates:
                    # Remove old mappings
                    old_ac_ids = [k for k, v in self.ac_id_mapping.items() 
                                 if v["entry_id"] == entry_id]
                    for ac_id in old_ac_ids:
                        del self.ac_id_mapping[ac_id]
                    
                    # Add new mappings
                    for ac_id in entry.ac_ids:
                        self.ac_id_mapping[ac_id] = {
                            "entry_id": entry_id,
                            "domain": entry.domain
                        }
                
                self._save_index()
                return True
        
        return False
    
    def find_entries_by_domain(self, domain: str) -> List[IndexEntry]:
        """
        Find all entries in a domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of entries in domain
        """
        if domain not in self.VALID_DOMAINS:
            raise ValueError(f"Invalid domain: {domain}")
        
        return [e for e in self.entries if e.domain == domain]
    
    def find_entries_by_ac_id(self, ac_id: str) -> List[IndexEntry]:
        """
        Find all entries containing an AC-ID.
        
        Args:
            ac_id: AC-ID to search for
            
        Returns:
            List of entries containing the AC-ID
        """
        return [e for e in self.entries if ac_id in e.ac_ids]
    
    def find_domain_for_ac_id(self, ac_id: str) -> Optional[str]:
        """
        Find the domain containing an AC-ID.
        
        Args:
            ac_id: AC-ID to search for
            
        Returns:
            Domain name or None if not found
        """
        if ac_id in self.ac_id_mapping:
            return self.ac_id_mapping[ac_id]["domain"]
        return None
    
    def search_by_title(self, query: str, case_sensitive: bool = False) -> List[IndexEntry]:
        """
        Search entries by title.
        
        Args:
            query: Search query
            case_sensitive: Whether search is case-sensitive
            
        Returns:
            List of matching entries
        """
        if not case_sensitive:
            query = query.lower()
        
        results = []
        for entry in self.entries:
            title = entry.title if case_sensitive else entry.title.lower()
            if query in title:
                results.append(entry)
        
        return results
    
    def search_by_ac_id(self, ac_id_pattern: str) -> List[str]:
        """
        Search AC-IDs by pattern.
        
        Args:
            ac_id_pattern: Regex pattern to match AC-IDs
            
        Returns:
            List of matching AC-IDs
        """
        pattern = re.compile(ac_id_pattern)
        return [ac_id for ac_id in self.ac_id_mapping.keys() 
                if pattern.match(ac_id)]
    
    def get_index_stats(self) -> Dict[str, Any]:
        """
        Get index statistics.
        
        Returns:
            Dictionary with index stats
        """
        return {
            "total_entries": len(self.entries),
            "total_ac_ids": len(self.ac_id_mapping),
            "domains_populated": len([d for d in self.by_domain.values() if d]),
            "entries_by_domain": {d: len(e) for d, e in self.by_domain.items()},
            "index_file": str(self.index_file),
            "index_size_bytes": self.index_file.stat().st_size if self.index_file.exists() else 0
        }
    
    def validate_consistency(self) -> Dict[str, Any]:
        """
        Validate index consistency.
        
        Returns:
            Validation results with any inconsistencies found
        """
        issues = []
        
        # Check entry count matches metadata
        entries_in_index = len(self.entries)
        
        # Check domain index consistency
        domain_entry_count = sum(len(e) for e in self.by_domain.values())
        if domain_entry_count != entries_in_index:
            issues.append(
                f"Domain index count ({domain_entry_count}) != entries ({entries_in_index})"
            )
        
        # Check for duplicate entries
        entry_ids = [e.entry_id for e in self.entries]
        if len(entry_ids) != len(set(entry_ids)):
            issues.append("Duplicate entry IDs found")
        
        # Check AC-ID mappings
        for entry in self.entries:
            for ac_id in entry.ac_ids:
                if ac_id not in self.ac_id_mapping:
                    issues.append(f"AC-ID {ac_id} missing from mapping")
                elif self.ac_id_mapping[ac_id]["entry_id"] != entry.entry_id:
                    issues.append(f"AC-ID {ac_id} mapping inconsistent")
        
        # Check for orphaned AC-ID mappings
        for ac_id, mapping in self.ac_id_mapping.items():
            entry_exists = any(e.entry_id == mapping["entry_id"] 
                              for e in self.entries)
            if not entry_exists:
                issues.append(f"Orphaned AC-ID mapping: {ac_id}")
        
        return {
            "consistent": len(issues) == 0,
            "issues": issues,
            "entry_count": entries_in_index,
            "ac_id_count": len(self.ac_id_mapping)
        }
