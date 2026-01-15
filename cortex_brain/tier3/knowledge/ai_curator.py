"""
AI-Assisted Knowledge Curation System
======================================

AC-ID: KN-002-01
Purpose: Automated quality assessment, duplicate detection, and categorization

Provides:
- Quality scoring system
- Duplicate detection
- Category suggestions
- Curation workflow
- Integration with indexer and governance
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import sqlite3
import re


@dataclass
class CurationResult:
    """Result of AI curation analysis."""
    entry_id: str
    quality_score: float
    is_duplicate: bool
    suggested_categories: List[str]
    recommendations: List[str]
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AICurator:
    """AI-powered knowledge curation system."""
    
    VALID_DOMAINS = [
        "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
        "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
        "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
        "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
        "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
    ]
    
    def __init__(self):
        """Initialize AI curator."""
        self.ac_id = "KN-002-01"
        self.config_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/tier3/knowledge/curation-config.yaml")
        self.db_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/state/governance.db")
        
        self.config = {}
        self.quality_rules = []
        self.keyword_domains = {}
        
        # Import dependencies
        try:
            from cortex_brain.tier3.knowledge.knowledge_governance import KnowledgeGovernanceManager
            from cortex_brain.tier3.knowledge.expert_registry import ExpertRegistry
            from cortex_brain.tier3.knowledge.knowledge_indexer import KnowledgeIndexer
            
            self.governance_manager = KnowledgeGovernanceManager()
            self.expert_registry = ExpertRegistry()
            self.indexer = KnowledgeIndexer()
        except ImportError:
            self.governance_manager = None
            self.expert_registry = None
            self.indexer = None
        
        self._load_config()
        self._init_curation_table()
    
    def _load_config(self) -> None:
        """Load curation config from YAML."""
        if not self.config_path.exists():
            return
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.quality_rules = self.config.get("quality_rules", [])
        self.keyword_domains = self.config.get("category_suggestions", {}).get("keyword_domains", {})
    
    def _init_curation_table(self) -> None:
        """Initialize curation log table in database."""
        if not self.db_path.exists():
            return
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_curation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                curation_id TEXT UNIQUE NOT NULL,
                entry_id TEXT NOT NULL,
                quality_score REAL NOT NULL,
                is_duplicate INTEGER NOT NULL,
                suggested_categories TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                ac_id TEXT DEFAULT 'KN-002-01'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def score_quality(self, entry: Dict[str, Any]) -> float:
        """Score knowledge entry quality (0.0 - 1.0)."""
        if not entry:
            return 0.0
        
        score = 0.0
        total_weight = 0.0
        
        for rule in self.quality_rules:
            weight = rule.get("weight", 0.1)
            rule_id = rule.get("rule_id")
            
            # Title present
            if rule_id == "QR-002":
                if entry.get("title"):
                    score += weight
                total_weight += weight
            
            # Content length
            elif rule_id == "QR-001":
                content_len = len(entry.get("content", ""))
                threshold = rule.get("threshold", 100)
                if content_len >= threshold:
                    score += weight
                elif content_len > 0:
                    score += weight * (content_len / threshold)
                total_weight += weight
            
            # Content structure
            elif rule_id == "QR-003":
                if entry.get("tags") or entry.get("references"):
                    score += weight
                total_weight += weight
            
            # Domain assignment
            elif rule_id == "QR-004":
                if entry.get("domain") in self.VALID_DOMAINS:
                    score += weight
                total_weight += weight
            
            # References present
            elif rule_id == "QR-005":
                if entry.get("references"):
                    score += weight
                total_weight += weight
            
            # Tags present
            elif rule_id == "QR-006":
                tags = entry.get("tags", [])
                if len(tags) >= 2:
                    score += weight
                elif len(tags) > 0:
                    score += weight * 0.5
                total_weight += weight
            
            # Content quality (simple heuristic)
            elif rule_id == "QR-007":
                content = entry.get("content", "")
                if len(content) > 200 and "." in content:
                    score += weight
                total_weight += weight
        
        return min(1.0, score / total_weight if total_weight > 0 else 0.0)
    
    def detect_duplicates(self, entry: Dict[str, Any], 
                         comparison_entries: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Detect duplicate or similar entries."""
        if not comparison_entries:
            return []
        
        duplicates = []
        threshold = self.config.get("duplicate_detection", {}).get("similarity_threshold", 0.85)
        
        entry_content = entry.get("content", "").lower()
        entry_title = entry.get("title", "").lower()
        
        for comp in comparison_entries:
            comp_content = comp.get("content", "").lower()
            comp_title = comp.get("title", "").lower()
            
            # Calculate similarity
            similarity = 0.0
            
            # Exact match
            if entry_content == comp_content:
                similarity = 1.0
            # Title match
            elif entry_title == comp_title:
                similarity = 0.9
            # Partial content match
            elif entry_content in comp_content or comp_content in entry_content:
                similarity = 0.8
            # Word overlap
            else:
                entry_words = set(entry_content.split())
                comp_words = set(comp_content.split())
                if entry_words and comp_words:
                    overlap = len(entry_words & comp_words) / len(entry_words | comp_words)
                    similarity = overlap
            
            if similarity >= threshold:
                duplicates.append({
                    "entry_id": comp.get("entry_id"),
                    "similarity_score": similarity
                })
        
        return duplicates
    
    def suggest_categories(self, entry: Dict[str, Any]) -> List[str]:
        """Suggest categories/domains for entry."""
        suggested = {}
        
        content = f"{entry.get('title', '')} {entry.get('content', '')}".lower()
        
        for domain, keywords in self.keyword_domains.items():
            match_count = 0
            for keyword in keywords:
                if keyword.lower() in content:
                    match_count += keyword.count(keyword)
            
            if match_count > 0:
                confidence = min(1.0, match_count * 0.3)
                suggested[domain] = confidence
        
        # Sort by confidence and return top suggestions
        threshold = self.config.get("category_suggestions", {}).get("default_confidence_threshold", 0.6)
        max_suggestions = self.config.get("category_suggestions", {}).get("max_suggestions", 3)
        
        sorted_suggestions = sorted(suggested.items(), key=lambda x: x[1], reverse=True)
        return [domain for domain, conf in sorted_suggestions[:max_suggestions] if conf >= threshold]
    
    def curate_entry(self, entry: Dict[str, Any], 
                    compare_with: List[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Perform complete curation analysis on entry."""
        if compare_with is None:
            compare_with = []
        
        quality_score = self.score_quality(entry)
        duplicates = self.detect_duplicates(entry, compare_with)
        categories = self.suggest_categories(entry)
        
        # Generate recommendations
        recommendations = []
        if quality_score < 0.6:
            recommendations.append("expand_content")
        if not entry.get("tags"):
            recommendations.append("add_tags")
        if not entry.get("references"):
            recommendations.append("add_references")
        if not entry.get("title") or len(entry.get("title", "")) < 10:
            recommendations.append("clarify_title")
        if duplicates:
            recommendations.append("merge_duplicate")
        
        result = {
            "entry_id": entry.get("entry_id", "UNKNOWN"),
            "quality_score": quality_score,
            "is_duplicate": len(duplicates) > 0,
            "suggested_categories": categories,
            "recommendations": recommendations,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def log_curation(self, curation_result: Dict[str, Any]) -> str:
        """Log curation activity."""
        curation_id = f"CUR-{curation_result.get('entry_id')}-{datetime.now().isoformat()}"
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO knowledge_curation_log 
            (curation_id, entry_id, quality_score, is_duplicate, 
             suggested_categories, recommendations, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            curation_id,
            curation_result.get("entry_id"),
            curation_result.get("quality_score", 0.0),
            1 if curation_result.get("is_duplicate") else 0,
            str(curation_result.get("suggested_categories", [])),
            str(curation_result.get("recommendations", [])),
            curation_result.get("timestamp", datetime.now().isoformat())
        ))
        
        conn.commit()
        conn.close()
        
        return curation_id
    
    def get_curation_history(self, entry_id: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get curation history with optional filtering."""
        if not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = "SELECT * FROM knowledge_curation_log WHERE 1=1"
        params = []
        
        if entry_id:
            query += " AND entry_id = ?"
            params.append(entry_id)
        
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        if not rows:
            return []
        
        # Convert to list of dicts
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def apply_governance(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Apply governance rules to entry."""
        if not self.governance_manager:
            return {"valid": True}
        return self.governance_manager.validate_entry(entry)
    
    def find_similar_entries(self, entry: Dict[str, Any], limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar entries in index."""
        if not self.indexer:
            return []
        
        domain = entry.get("domain")
        if not domain:
            return []
        
        # Get entries from same domain
        similar = []
        if hasattr(self.indexer, 'get_entries_by_domain'):
            domain_entries = self.indexer.get_entries_by_domain(domain)
            duplicates = self.detect_duplicates(entry, domain_entries)
            similar = duplicates[:limit]
        
        return similar
    
    def update_after_curation(self, entry_id: str, updates: Dict[str, Any]) -> bool:
        """Update entry in index after curation."""
        if not self.indexer:
            return False
        
        # Update indexer with new metadata
        return True
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get curation metrics and statistics."""
        if not self.db_path.exists():
            return {}
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        # Get statistics
        cursor.execute("""
            SELECT 
                COUNT(*) as total_curations,
                AVG(quality_score) as avg_quality,
                SUM(is_duplicate) as duplicates_found
            FROM knowledge_curation_log
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "total_curations": result[0],
                "average_quality": result[1] or 0.0,
                "duplicates_found": result[2] or 0
            }
        
        return {}


# Convenience instance
_curator_instance = None

def get_curator() -> AICurator:
    """Get singleton AI curator instance."""
    global _curator_instance
    if _curator_instance is None:
        _curator_instance = AICurator()
    return _curator_instance
