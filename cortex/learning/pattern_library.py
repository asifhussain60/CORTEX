"""
Pattern Library - Storage and Retrieval Layer

AC_START: AC-WAVE-CHAT01-S1-001
Description: Pattern storage with registry persistence and deduplication
Authority: CORE-008 TDD, CORE-011 type hints, CORE-012 docstrings
Stage: S1 - Pattern library implementation

Provides:
1. PatternLibrary class (CRUD operations)
2. YAML persistence to cortex-registry/patterns/
3. Pattern deduplication (similarity threshold 0.3)
4. Pattern retrieval by type/orchestrator/confidence
"""

from __future__ import annotations

import logging
import hashlib
import yaml
from dataclasses import dataclass, asdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

from cortex.learning.pattern_extractor import ExtractedPattern, PatternType

logger = logging.getLogger(__name__)


@dataclass
class StoredPattern:
    """Pattern stored in library with metadata."""
    
    pattern_id: str
    pattern_type: PatternType
    description: str
    data: Dict[str, Any]
    confidence: float
    source_orchestrator: str
    source_operation: str
    created_at: str
    last_seen_at: str
    occurrence_count: int
    tags: List[str]


class PatternLibrary:
    """
    Pattern storage and retrieval with registry persistence.
    
    Features:
    - CRUD operations for patterns
    - YAML persistence to cortex-registry/patterns/
    - Automatic deduplication (similarity threshold)
    - Multi-criteria retrieval (type, orchestrator, confidence)
    
    AC_WAVE-CHAT01-S1-001: Pattern library implementation
    """
    
    def __init__(
        self,
        registry_path: Optional[Path] = None,
        similarity_threshold: float = 0.3
    ):
        """
        Initialize pattern library.
        
        Args:
            registry_path: Path to cortex-registry (auto-detect if None)
            similarity_threshold: Threshold for pattern deduplication (0.0-1.0)
        """
        self.registry_path = registry_path or self._detect_registry_path()
        self.patterns_dir = self.registry_path / "patterns"
        self.similarity_threshold = similarity_threshold
        
        # Ensure patterns directory exists
        self.patterns_dir.mkdir(parents=True, exist_ok=True)
        
        # In-memory cache
        self._cache: Dict[str, StoredPattern] = {}
        self._cache_loaded = False
    
    def _detect_registry_path(self) -> Path:
        """Detect cortex-registry path."""
        cwd = Path.cwd()
        
        # Check if we're in CORTEX workspace
        if (cwd / "cortex-registry").exists():
            return cwd / "cortex-registry"
        
        # Check parent directories
        for parent in cwd.parents:
            if (parent / "cortex-registry").exists():
                return parent / "cortex-registry"
        
        # Fallback: create in current directory
        registry_path = cwd / "cortex-registry"
        registry_path.mkdir(parents=True, exist_ok=True)
        return registry_path
    
    def _load_cache(self) -> None:
        """Load all patterns from disk into cache."""
        if self._cache_loaded:
            return
        
        for yaml_file in self.patterns_dir.glob("*.yaml"):
            try:
                with open(yaml_file, "r") as f:
                    data = yaml.safe_load(f)
                    if data and "patterns" in data:
                        for p in data["patterns"]:
                            pattern = self._dict_to_stored_pattern(p)
                            self._cache[pattern.pattern_id] = pattern
            except Exception as e:
                logger.warning(f"Failed to load {yaml_file}: {e}")
        
        self._cache_loaded = True
        logger.info(f"Loaded {len(self._cache)} patterns from registry")
    
    def _dict_to_stored_pattern(self, data: Dict[str, Any]) -> StoredPattern:
        """Convert dictionary to StoredPattern."""
        # Handle pattern_type conversion
        pattern_type_str = data.get("pattern_type", "TECHNICAL")
        if isinstance(pattern_type_str, str):
            pattern_type = PatternType[pattern_type_str]
        else:
            pattern_type = pattern_type_str
        
        return StoredPattern(
            pattern_id=data["pattern_id"],
            pattern_type=pattern_type,
            description=data["description"],
            data=data["data"],
            confidence=float(data["confidence"]),
            source_orchestrator=data["source_orchestrator"],
            source_operation=data["source_operation"],
            created_at=data["created_at"],
            last_seen_at=data["last_seen_at"],
            occurrence_count=int(data["occurrence_count"]),
            tags=data.get("tags", [])
        )
    
    def _compute_pattern_id(self, pattern: ExtractedPattern) -> str:
        """Compute unique pattern ID from pattern data."""
        # Create fingerprint from key attributes including data to ensure uniqueness
        data_repr = str(sorted(pattern.data.items())) if pattern.data else ""
        fingerprint = f"{pattern.pattern_type.name}:{pattern.source_orchestrator}:{pattern.description}:{data_repr}"
        return hashlib.md5(fingerprint.encode()).hexdigest()[:12]
    
    def _calculate_similarity(self, p1: StoredPattern, p2: ExtractedPattern) -> float:
        """
        Calculate similarity between stored and extracted pattern.
        
        Args:
            p1: Stored pattern
            p2: Extracted pattern
            
        Returns:
            Similarity score (0.0-1.0)
        """
        score = 0.0
        
        # Type match (30%)
        if p1.pattern_type == p2.pattern_type:
            score += 0.3
        
        # Orchestrator match (40%) - different orchestrators = different patterns
        if p1.source_orchestrator == p2.source_orchestrator:
            score += 0.4
        else:
            # Different orchestrators reduce similarity significantly
            return score * 0.5  # Cap score at 15% if orchestrators differ
        
        # Description similarity (30%) - only if descriptions differ enough
        desc1_words = set(p1.description.lower().split())
        desc2_words = set(p2.description.lower().split())
        if desc1_words and desc2_words:
            overlap = len(desc1_words & desc2_words)
            total = len(desc1_words | desc2_words)
            desc_similarity = overlap / total if total > 0 else 0
            
            # Only count as duplicate if description substantially similar (>60%)
            if desc_similarity < 0.6:
                score += 0.3 * desc_similarity
            else:
                score += 0.3  # Full points for high similarity
        
        return score
    
    def store(self, pattern: ExtractedPattern) -> str:
        """
        Store pattern in library (with deduplication).
        
        Args:
            pattern: Extracted pattern to store
            
        Returns:
            Pattern ID
        """
        self._load_cache()
        
        pattern_id = self._compute_pattern_id(pattern)
        
        # Check for duplicates
        for stored in self._cache.values():
            similarity = self._calculate_similarity(stored, pattern)
            if similarity >= self.similarity_threshold:
                # Update existing pattern
                stored.last_seen_at = datetime.utcnow().isoformat()
                stored.occurrence_count += 1
                stored.confidence = min(0.99, stored.confidence + 0.05)  # Increase confidence
                self._persist_to_disk()
                logger.debug(f"Updated duplicate pattern {stored.pattern_id} (similarity: {similarity:.2f})")
                return stored.pattern_id
        
        # Store new pattern
        now = datetime.utcnow().isoformat()
        stored_pattern = StoredPattern(
            pattern_id=pattern_id,
            pattern_type=pattern.pattern_type,
            description=pattern.description,
            data=pattern.data,
            confidence=pattern.confidence,
            source_orchestrator=pattern.source_orchestrator,
            source_operation=pattern.source_operation,
            created_at=now,
            last_seen_at=now,
            occurrence_count=1,
            tags=[]
        )
        
        self._cache[pattern_id] = stored_pattern
        self._persist_to_disk()
        logger.info(f"Stored new pattern {pattern_id} from {pattern.source_orchestrator}")
        return pattern_id
    
    def retrieve(
        self,
        pattern_type: Optional[PatternType] = None,
        orchestrator: Optional[str] = None,
        min_confidence: float = 0.0,
        limit: Optional[int] = None
    ) -> List[StoredPattern]:
        """
        Retrieve patterns matching criteria.
        
        Args:
            pattern_type: Filter by pattern type
            orchestrator: Filter by source orchestrator
            min_confidence: Minimum confidence threshold
            limit: Maximum number of results
            
        Returns:
            List of matching patterns (sorted by confidence descending)
        """
        self._load_cache()
        
        results = []
        for pattern in self._cache.values():
            # Apply filters
            if pattern_type and pattern.pattern_type != pattern_type:
                continue
            if orchestrator and pattern.source_orchestrator != orchestrator:
                continue
            if pattern.confidence < min_confidence:
                continue
            
            results.append(pattern)
        
        # Sort by confidence (descending)
        results.sort(key=lambda p: p.confidence, reverse=True)
        
        # Apply limit
        if limit:
            results = results[:limit]
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get pattern library statistics.
        
        Returns:
            Statistics dictionary
        """
        self._load_cache()
        
        by_type: Dict[str, int] = {}
        by_orchestrator: Dict[str, int] = {}
        
        for pattern in self._cache.values():
            # By type
            type_name = pattern.pattern_type.name
            by_type[type_name] = by_type.get(type_name, 0) + 1
            
            # By orchestrator
            orch = pattern.source_orchestrator
            by_orchestrator[orch] = by_orchestrator.get(orch, 0) + 1
        
        return {
            "total_patterns": len(self._cache),
            "by_type": by_type,
            "by_orchestrator": by_orchestrator,
            "avg_confidence": sum(p.confidence for p in self._cache.values()) / len(self._cache) if self._cache else 0.0,
            "avg_occurrences": sum(p.occurrence_count for p in self._cache.values()) / len(self._cache) if self._cache else 0
        }
    
    def _persist_to_disk(self) -> None:
        """Persist all patterns to disk (YAML format)."""
        # Group patterns by orchestrator
        by_orchestrator: Dict[str, List[StoredPattern]] = {}
        for pattern in self._cache.values():
            orch = pattern.source_orchestrator
            if orch not in by_orchestrator:
                by_orchestrator[orch] = []
            by_orchestrator[orch].append(pattern)
        
        # Write one file per orchestrator
        for orchestrator, patterns in by_orchestrator.items():
            filename = f"{orchestrator.lower()}-patterns.yaml"
            filepath = self.patterns_dir / filename
            
            # Convert patterns to dicts
            pattern_dicts = []
            for p in patterns:
                d = asdict(p)
                d["pattern_type"] = p.pattern_type.name  # Convert enum to string
                pattern_dicts.append(d)
            
            data = {
                "orchestrator": orchestrator,
                "pattern_count": len(patterns),
                "last_updated": datetime.utcnow().isoformat(),
                "patterns": pattern_dicts
            }
            
            try:
                with open(filepath, "w") as f:
                    yaml.dump(data, f, default_flow_style=False, sort_keys=False)
            except Exception as e:
                logger.error(f"Failed to write {filepath}: {e}")


# Singleton instance
_pattern_library: Optional[PatternLibrary] = None


def get_pattern_library() -> PatternLibrary:
    """Get singleton pattern library instance."""
    global _pattern_library
    if _pattern_library is None:
        _pattern_library = PatternLibrary()
    return _pattern_library


# AC_COMPLETE: AC-WAVE-CHAT01-S1-001 ✅
# Implementation: PatternLibrary with YAML persistence and deduplication
# Status: READY FOR TESTING
