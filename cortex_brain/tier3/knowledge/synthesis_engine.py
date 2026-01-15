"""
Cross-Domain Knowledge Synthesis Engine
========================================

AC-ID: KN-004-01
Purpose: Synthesize knowledge across multiple domains with source attribution

Provides:
- Cross-domain queries
- Knowledge synthesis
- Source attribution and traceability
- Domain relationship graph
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
import sqlite3


@dataclass
class SynthesisResult:
    """Result of knowledge synthesis."""
    synthesis_id: str
    source_domains: List[str]
    synthesized_knowledge: str
    supporting_entries: List[Dict[str, Any]]
    relationships: List[Dict[str, Any]]
    confidence: float
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class SynthesisEngine:
    """Engine for cross-domain knowledge synthesis."""
    
    VALID_DOMAINS = [
        "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
        "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
        "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
        "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
        "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
    ]
    
    def __init__(self):
        """Initialize synthesis engine."""
        self.ac_id = "KN-004-01"
        self.config_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/tier3/knowledge/synthesis-config.yaml")
        self.db_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/state/governance.db")
        
        self.config = {}
        self.relationships = []
        self.synthesis_rules = []
        
        # Import dependencies
        try:
            from cortex_brain.tier3.knowledge.knowledge_governance import KnowledgeGovernanceManager
            from cortex_brain.tier3.knowledge.ai_curator import AICurator
            from cortex_brain.tier3.knowledge.knowledge_indexer import KnowledgeIndexer
            
            self.governance_manager = KnowledgeGovernanceManager()
            self.curator = AICurator()
            self.indexer = KnowledgeIndexer()
        except ImportError:
            self.governance_manager = None
            self.curator = None
            self.indexer = None
        
        self._load_config()
        self._build_relationship_graph()
        self._init_synthesis_table()
    
    def _load_config(self) -> None:
        """Load synthesis config from YAML."""
        if not self.config_path.exists():
            return
        
        with open(self.config_path, 'r') as f:
            self.config = yaml.safe_load(f)
        
        self.relationships = self.config.get("domain_relationships", [])
        self.synthesis_rules = self.config.get("synthesis_rules", [])
    
    def _build_relationship_graph(self) -> None:
        """Build domain relationship graph."""
        self.relationship_graph = {}
        
        for rel in self.relationships:
            source = rel.get("source_domain")
            if source not in self.relationship_graph:
                self.relationship_graph[source] = []
            
            for target in rel.get("target_domains", []):
                self.relationship_graph[source].append({
                    "domain": target.get("domain"),
                    "strength": target.get("strength", 0.5),
                    "description": target.get("description", "")
                })
    
    def _init_synthesis_table(self) -> None:
        """Initialize synthesis log table."""
        if not self.db_path.exists():
            return
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_synthesis_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                synthesis_id TEXT UNIQUE NOT NULL,
                source_domains TEXT NOT NULL,
                synthesized_knowledge TEXT NOT NULL,
                supporting_entries TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp TEXT NOT NULL,
                ac_id TEXT DEFAULT 'KN-004-01'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def query_across_domains(self, query: str, domains: List[str]) -> List[Dict[str, Any]]:
        """Query knowledge across multiple domains."""
        if not domains:
            return []
        
        results = []
        
        # Filter to valid domains
        valid_domains = [d for d in domains if d in self.VALID_DOMAINS]
        
        if not valid_domains:
            return []
        
        # Simulate queries - in real implementation would use indexer
        for domain in valid_domains:
            # Would query indexer for entries in domain
            if self.indexer:
                try:
                    domain_entries = self.indexer.get_entries_by_domain(domain) if hasattr(self.indexer, 'get_entries_by_domain') else []
                    results.extend(domain_entries)
                except:
                    pass
        
        return results
    
    def synthesize(self, entries: List[Dict[str, Any]], source_domains: List[str]) -> Dict[str, Any]:
        """Synthesize knowledge from multiple entries/domains."""
        if not entries:
            return {"synthesis_id": "SYNTH-EMPTY", "synthesized_knowledge": ""}
        
        synthesis_id = f"SYNTH-{datetime.now().isoformat()}"
        
        # Extract unique domains from entries
        actual_domains = set()
        for entry in entries:
            if "domain" in entry:
                actual_domains.add(entry["domain"])
        
        # Find relationships between domains
        used_relationships = []
        for rel in self.relationships:
            source = rel.get("source_domain")
            if source in actual_domains:
                for target in rel.get("target_domains", []):
                    if target.get("domain") in actual_domains:
                        used_relationships.append({
                            "source": source,
                            "target": target.get("domain"),
                            "strength": target.get("strength", 0.5)
                        })
        
        # Calculate confidence based on relationships and domains
        confidence = 0.7 if used_relationships else 0.5
        if len(actual_domains) > 1:
            confidence += 0.15
        confidence = min(1.0, confidence)
        
        # Create synthesized knowledge
        synthesized = ""
        if entries:
            entry_contents = [e.get("content", "") for e in entries if "content" in e]
            synthesized = " ".join(entry_contents[:100])  # Simple concatenation
        
        result = {
            "synthesis_id": synthesis_id,
            "source_domains": list(actual_domains),
            "synthesized_knowledge": synthesized,
            "supporting_entries": [
                {
                    "entry_id": e.get("entry_id", "unknown"),
                    "domain": e.get("domain", "unknown")
                }
                for e in entries
            ],
            "relationships": used_relationships,
            "confidence": confidence,
            "timestamp": datetime.now().isoformat()
        }
        
        return result
    
    def track_sources(self, synthesis_id: str, entries: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Track sources for a synthesis."""
        return {
            "synthesis_id": synthesis_id,
            "sources": [e.get("entry_id") for e in entries],
            "source_count": len(entries),
            "domains": list(set(e.get("domain") for e in entries if "domain" in e))
        }
    
    def get_domain_relationships(self) -> List[Dict[str, Any]]:
        """Get all domain relationships."""
        result = []
        
        for rel in self.relationships:
            source = rel.get("source_domain")
            for target in rel.get("target_domains", []):
                result.append({
                    "source": source,
                    "target": target.get("domain"),
                    "strength": target.get("strength", 0.5),
                    "description": target.get("description", "")
                })
        
        return result
    
    def get_related_domains(self, domain: str) -> List[Dict[str, Any]]:
        """Get domains related to given domain."""
        return self.relationship_graph.get(domain, [])
    
    def search_indexed_entries(self, query: str, domains: List[str] = None) -> List[Dict[str, Any]]:
        """Search indexed entries."""
        if not self.indexer:
            return []
        
        if not domains:
            domains = self.VALID_DOMAINS
        
        # Use indexer to search
        return self.query_across_domains(query, domains)
    
    def apply_governance(self, synthesis: Dict[str, Any]) -> Dict[str, Any]:
        """Apply governance rules to synthesis."""
        if not self.governance_manager:
            return {"valid": True}
        
        # Check synthesis rules
        for rule in self.synthesis_rules:
            if rule.get("rule_id") == "SR-002":  # Source attribution
                if not synthesis.get("supporting_entries"):
                    return {"valid": False, "error": "Missing source attribution"}
            
            if rule.get("rule_id") == "SR-003":  # Confidence threshold
                threshold = rule.get("threshold", 0.65)
                if synthesis.get("confidence", 0.0) < threshold:
                    return {"valid": False, "error": f"Confidence below threshold {threshold}"}
        
        return {"valid": True}
    
    def log_synthesis(self, synthesis: Dict[str, Any]) -> str:
        """Log synthesis activity."""
        synthesis_id = synthesis.get("synthesis_id", f"SYNTH-{datetime.now().isoformat()}")
        
        if not self.db_path.exists():
            return synthesis_id
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO knowledge_synthesis_log 
            (synthesis_id, source_domains, synthesized_knowledge, 
             supporting_entries, confidence, timestamp)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            synthesis_id,
            str(synthesis.get("source_domains", [])),
            synthesis.get("synthesized_knowledge", ""),
            str(synthesis.get("supporting_entries", [])),
            synthesis.get("confidence", 0.0),
            synthesis.get("timestamp", datetime.now().isoformat())
        ))
        
        conn.commit()
        conn.close()
        
        return synthesis_id
    
    def get_synthesis_history(self, domain: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get synthesis history."""
        if not self.db_path.exists():
            return []
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = "SELECT * FROM knowledge_synthesis_log WHERE 1=1"
        params = []
        
        if domain:
            query += " AND source_domains LIKE ?"
            params.append(f"%{domain}%")
        
        query += f" ORDER BY timestamp DESC LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        if not rows:
            return []
        
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in rows]
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get synthesis metrics."""
        if not self.db_path.exists():
            return {}
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                COUNT(*) as total_syntheses,
                AVG(confidence) as avg_confidence,
                COUNT(DISTINCT source_domains) as unique_domain_combinations
            FROM knowledge_synthesis_log
        """)
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return {
                "total_syntheses": result[0],
                "average_confidence": result[1] or 0.0,
                "unique_combinations": result[2] or 0,
                "total_relationships_defined": len(self.relationships)
            }
        
        return {"total_relationships_defined": len(self.relationships)}


# Convenience instance
_engine_instance = None

def get_synthesis_engine() -> SynthesisEngine:
    """Get singleton synthesis engine instance."""
    global _engine_instance
    if _engine_instance is None:
        _engine_instance = SynthesisEngine()
    return _engine_instance
