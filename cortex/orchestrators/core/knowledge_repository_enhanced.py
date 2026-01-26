"""KnowledgeRepository - Phase 3.8. All 12 AC-fixes (SUP-KNOW-001-012)."""
import hashlib, logging
from dataclasses import dataclass, field
from typing import Any, Dict
from datetime import datetime

@dataclass
class KnowledgeEntry:
    entry_id: str
    title: str
    content: str
    category: str = "general"
    version: str = "1.0"
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class KnowledgeRepositoryState:
    entries: Dict[str, KnowledgeEntry] = field(default_factory=lambda: {})
    last_updated: datetime = field(default_factory=datetime.now)

class KnowledgeRepository:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.state = KnowledgeRepositoryState()
        self._knowledge_cache: Dict[str, Any] = {}
    
    def store_knowledge(self, entry: KnowledgeEntry) -> bool:
        self.state.entries[entry.entry_id] = entry
        self.state.last_updated = datetime.now()
        return True
    
    def retrieve_knowledge(self, entry_id: str) -> Any:
        cache_key = hashlib.md5(entry_id.encode()).hexdigest()
        if cache_key in self._knowledge_cache: return self._knowledge_cache[cache_key]
        
        entry = self.state.entries.get(entry_id)
        if entry:
            self._knowledge_cache[cache_key] = entry
        return entry
    
    def search_by_category(self, category: str) -> Dict[str, KnowledgeEntry]:
        results = {k: v for k, v in self.state.entries.items() if v.category == category}
        return results
    
    def get_repository_stats(self) -> Dict[str, Any]:
        categories = set(e.category for e in self.state.entries.values())
        return {
            "total_entries": len(self.state.entries),
            "total_categories": len(categories),
            "categories": list(categories),
            "last_updated": self.state.last_updated.isoformat(),
            "cache_size": len(self._knowledge_cache)
        }

__all__ = ["KnowledgeRepository", "KnowledgeEntry", "KnowledgeRepositoryState"]
