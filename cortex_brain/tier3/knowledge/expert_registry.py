"""
Expert Registry for Domain Knowledge Validation
===============================================

AC-ID: KN-003-02
Purpose: Registry of domain experts for knowledge validation and curation

Provides:
- Expert lookup and filtering
- Domain-expert mapping
- Validation workflow management
- Integration with governance system
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime
import sqlite3


@dataclass
class Expert:
    """Represents a domain expert."""
    expert_id: str
    name: str
    email: str
    domains: List[str]
    expertise_level: str
    active: bool
    specializations: List[str] = field(default_factory=list)


@dataclass
class ValidationLog:
    """Record of validation activity."""
    validation_id: str
    entry_id: str
    expert_id: str
    domain: str
    timestamp: str
    status: str
    feedback: str


class ExpertRegistry:
    """Registry and management system for domain experts."""
    
    VALID_DOMAINS = [
        "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
        "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
        "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
        "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
        "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
    ]
    
    def __init__(self):
        """Initialize expert registry."""
        self.ac_id = "KN-003-02"
        self.registry_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/tier3/knowledge/expert-registry.yaml")
        self.db_path = Path("/Users/asifhussain/PROJECTS/CORTEX/cortex_brain/state/governance.db")
        
        self.experts: Dict[str, Expert] = {}
        self.domain_index: Dict[str, List[str]] = {}
        self.validation_rules: List[Dict[str, Any]] = []
        
        self._load_registry()
        self._init_validation_table()
    
    def _load_registry(self) -> None:
        """Load experts from YAML registry."""
        if not self.registry_path.exists():
            return
        
        with open(self.registry_path, 'r') as f:
            data = yaml.safe_load(f)
        
        # Load experts
        for expert_data in data.get("experts", []):
            expert = Expert(
                expert_id=expert_data["expert_id"],
                name=expert_data["name"],
                email=expert_data["email"],
                domains=expert_data["domains"],
                expertise_level=expert_data["expertise_level"],
                active=expert_data.get("active", True),
                specializations=expert_data.get("specializations", [])
            )
            self.experts[expert.expert_id] = expert
            
            # Index by domain
            for domain in expert.domains:
                if domain not in self.domain_index:
                    self.domain_index[domain] = []
                self.domain_index[domain].append(expert.expert_id)
        
        # Load validation rules
        self.validation_rules = data.get("validation_rules", [])
    
    def _init_validation_table(self) -> None:
        """Initialize validation log table in database."""
        if not self.db_path.exists():
            return
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS expert_validation_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                validation_id TEXT UNIQUE NOT NULL,
                entry_id TEXT NOT NULL,
                expert_id TEXT NOT NULL,
                domain TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                feedback TEXT,
                ac_id TEXT DEFAULT 'KN-003-02'
            )
        """)
        
        conn.commit()
        conn.close()
    
    def get_expert(self, expert_id: str) -> Optional[Expert]:
        """Get expert by ID."""
        return self.experts.get(expert_id)
    
    def get_experts_by_domain(self, domain: str) -> List[Expert]:
        """Get all experts for a domain."""
        expert_ids = self.domain_index.get(domain, [])
        return [self.experts[eid] for eid in expert_ids if eid in self.experts]
    
    def get_active_experts_for_domain(self, domain: str) -> List[Expert]:
        """Get active experts for a domain."""
        experts = self.get_experts_by_domain(domain)
        return [e for e in experts if e.active]
    
    def get_experts_by_level(self, level: str) -> List[Expert]:
        """Get experts with specific expertise level."""
        return [e for e in self.experts.values() if e.expertise_level == level]
    
    def add_expert(self, expert: Expert) -> bool:
        """Add expert to registry."""
        if expert.expert_id in self.experts:
            return False
        
        self.experts[expert.expert_id] = expert
        
        for domain in expert.domains:
            if domain not in self.domain_index:
                self.domain_index[domain] = []
            self.domain_index[domain].append(expert.expert_id)
        
        return True
    
    def is_expert_for_domain(self, expert_id: str, domain: str) -> bool:
        """Check if expert has expertise in domain."""
        expert = self.experts.get(expert_id)
        if not expert:
            return False
        return domain in expert.domains and expert.active
    
    def can_validate_entry(self, expert_id: str, domain: str) -> bool:
        """Check if expert can validate entry in domain."""
        return self.is_expert_for_domain(expert_id, domain)
    
    def log_validation(self, entry_id: str, expert_id: str, domain: str, 
                      status: str, feedback: str = "") -> str:
        """Log expert validation activity."""
        validation_id = f"VAL-{entry_id}-{expert_id}-{datetime.now().isoformat()}"
        
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO expert_validation_log 
            (validation_id, entry_id, expert_id, domain, timestamp, status, feedback)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (validation_id, entry_id, expert_id, domain, 
              datetime.now().isoformat(), status, feedback))
        
        conn.commit()
        conn.close()
        
        return validation_id
    
    def get_validation_log(self, entry_id: str = None, expert_id: str = None, 
                          domain: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get validation logs with optional filtering."""
        conn = sqlite3.connect(str(self.db_path))
        cursor = conn.cursor()
        
        query = "SELECT * FROM expert_validation_log WHERE 1=1"
        params = []
        
        if entry_id:
            query += " AND entry_id = ?"
            params.append(entry_id)
        
        if expert_id:
            query += " AND expert_id = ?"
            params.append(expert_id)
        
        if domain:
            query += " AND domain = ?"
            params.append(domain)
        
        query += f" LIMIT {limit}"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(zip([col[0] for col in cursor.description], row)) for row in rows] if rows else []
    
    def validate_entry_with_expert(self, entry_id: str, expert_id: str, 
                                   domain: str) -> Dict[str, Any]:
        """Validate entry with expert."""
        if not self.can_validate_entry(expert_id, domain):
            return {
                "valid": False,
                "reason": f"Expert {expert_id} cannot validate domain {domain}"
            }
        
        return {
            "valid": True,
            "expert_id": expert_id,
            "domain": domain,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_all_experts(self) -> List[Expert]:
        """Get all experts in registry."""
        return list(self.experts.values())
    
    def get_expert_count(self) -> int:
        """Get total number of experts."""
        return len(self.experts)
    
    def get_domain_expert_count(self, domain: str) -> int:
        """Get count of experts for domain."""
        return len(self.get_experts_by_domain(domain))
    
    def search_experts(self, query: str) -> List[Expert]:
        """Search experts by name or email."""
        query_lower = query.lower()
        results = []
        
        for expert in self.experts.values():
            if (query_lower in expert.name.lower() or 
                query_lower in expert.email.lower()):
                results.append(expert)
        
        return results
    
    def validate_on_create(self, func: Callable) -> Callable:
        """Decorator: validate entry on creation."""
        def wrapper(entry: Dict[str, Any], domain: str, expert_id: str = None, *args, **kwargs):
            if expert_id and not self.can_validate_entry(expert_id, domain):
                raise ValueError(f"Expert {expert_id} not qualified for domain {domain}")
            return func(entry, domain, expert_id, *args, **kwargs)
        return wrapper
    
    def audit_on_validation(self, func: Callable) -> Callable:
        """Decorator: audit entry validation."""
        def wrapper(entry_id: str, expert_id: str, domain: str, *args, **kwargs):
            result = func(entry_id, expert_id, domain, *args, **kwargs)
            if result:
                self.log_validation(entry_id, expert_id, domain, "validated", 
                                  f"Validation result: {result}")
            return result
        return wrapper


# Convenience instance
_registry_instance = None

def get_registry() -> ExpertRegistry:
    """Get singleton expert registry instance."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = ExpertRegistry()
    return _registry_instance
