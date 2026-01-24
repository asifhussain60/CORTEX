"""
AI-Assisted Knowledge Curator - Tier 3.

Provides automated quality scoring, duplicate detection, and categorization.

AC: KN-002-01 - AI-Assisted Knowledge Curation
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import hashlib


@dataclass
class CurationResult:
    """Result of AI curation analysis."""
    entry_id: str
    quality_score: float
    is_duplicate: bool
    suggested_categories: List[str]
    recommendations: List[str]


class AICurator:
    """AI-powered knowledge curation system."""
    
    VALID_DOMAINS = [
        "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
        "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
        "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
        "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
        "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
    ]
    
    def __init__(self) -> None:
        """Initialize AI curator."""
        self._quality_rules: Dict[str, Any] = {}
        self._entry_cache: Dict[str, str] = {}  # entry_id -> content_hash
        self._curation_history: List[Dict[str, Any]] = []
        self._load_config()
    
    def _load_config(self) -> None:
        """Load curation configuration."""
        config_file = Path(__file__).parent / "curation-config.yaml"
        if config_file.exists():
            with open(config_file, 'r') as f:
                data = yaml.safe_load(f)
                self._quality_rules = data.get("quality_rules", {})
    
    def score_quality(self, entry: Dict[str, Any]) -> float:
        """
        Calculate quality score for knowledge entry.
        
        Args:
            entry: Entry to score
            
        Returns:
            Quality score (0.0-1.0)
        """
        score = 0.0
        
        # Content length factor (0-0.3)
        content = entry.get("content", "")
        if len(content) > 100:
            score += 0.3
        elif len(content) > 50:
            score += 0.2
        elif len(content) > 20:
            score += 0.1
        
        # Structure factor (0-0.3)
        if "title" in entry and entry["title"]:
            score += 0.1
        if "domain" in entry and entry["domain"] in self.VALID_DOMAINS:
            score += 0.1
        if "ac_ids" in entry and entry["ac_ids"]:
            score += 0.1
        
        # Completeness factor (0-0.4)
        required_fields = ["entry_id", "title", "content", "domain"]
        present_fields = sum(1 for field in required_fields if field in entry and entry[field])
        score += (present_fields / len(required_fields)) * 0.4
        
        return min(score, 1.0)
    
    def detect_duplicates(self, entry: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Detect duplicate entries.
        
        Args:
            entry: Entry to check
            
        Returns:
            List of duplicate matches with similarity scores
        """
        content = entry.get("content", "")
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        duplicates = []
        for entry_id, cached_hash in self._entry_cache.items():
            if cached_hash == content_hash:
                duplicates.append({
                    "entry_id": entry_id,
                    "similarity_score": 1.0
                })
        
        return duplicates
    
    def suggest_categories(self, entry: Dict[str, Any]) -> List[Dict[str, float]]:
        """
        Suggest categories for entry.
        
        Args:
            entry: Entry to categorize
            
        Returns:
            List of category suggestions with confidence scores
        """
        suggestions = []
        content = entry.get("content", "").lower()
        title = entry.get("title", "").lower()
        
        # Simple keyword-based categorization
        domain_keywords = {
            "GOVERNANCE": ["rule", "policy", "compliance", "audit"],
            "SECURITY": ["security", "authentication", "authorization", "encryption"],
            "TESTING-VALIDATION": ["test", "validation", "verification", "assert"],
            "ORCHESTRATION": ["orchestration", "workflow", "execution"],
            "OBSERVABILITY": ["monitoring", "metrics", "logging", "trace"]
        }
        
        for domain, keywords in domain_keywords.items():
            matches = sum(1 for kw in keywords if kw in content or kw in title)
            if matches > 0:
                confidence = min(matches / len(keywords), 1.0)
                suggestions.append({
                    "domain": domain,
                    "confidence": confidence
                })
        
        return sorted(suggestions, key=lambda x: x["confidence"], reverse=True)
    
    def curate_entry(self, entry: Dict[str, Any]) -> CurationResult:
        """
        Perform full curation analysis on entry.
        
        Args:
            entry: Entry to curate
            
        Returns:
            Curation result
        """
        quality_score = self.score_quality(entry)
        duplicates = self.detect_duplicates(entry)
        categories = self.suggest_categories(entry)
        
        recommendations = []
        if quality_score < 0.5:
            recommendations.append("Improve content quality and completeness")
        if len(duplicates) > 0:
            recommendations.append(f"Potential duplicate of {len(duplicates)} entries")
        if not categories:
            recommendations.append("Add domain classification keywords")
        
        # Cache entry
        content = entry.get("content", "")
        content_hash = hashlib.md5(content.encode()).hexdigest()
        self._entry_cache[entry["entry_id"]] = content_hash
        
        # Log curation
        self._curation_history.append({
            "entry_id": entry["entry_id"],
            "timestamp": datetime.now().isoformat(),
            "quality_score": quality_score,
            "is_duplicate": len(duplicates) > 0
        })
        
        return CurationResult(
            entry_id=entry["entry_id"],
            quality_score=quality_score,
            is_duplicate=len(duplicates) > 0,
            suggested_categories=[c["domain"] for c in categories],
            recommendations=recommendations
        )
    
    def get_curation_history(self) -> List[Dict[str, Any]]:
        """
        Get curation history.
        
        Returns:
            List of curation events
        """
        return self._curation_history
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Get curation metrics.
        
        Returns:
            Metrics dictionary
        """
        total_curated = len(self._curation_history)
        avg_quality = sum(h["quality_score"] for h in self._curation_history) / max(total_curated, 1)
        duplicates_found = sum(1 for h in self._curation_history if h["is_duplicate"])
        
        return {
            "total_curated": total_curated,
            "average_quality_score": avg_quality,
            "duplicates_found": duplicates_found
        }


__all__ = ["AICurator", "CurationResult"]
