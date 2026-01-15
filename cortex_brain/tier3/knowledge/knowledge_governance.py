"""Knowledge Governance Manager for Tier 3 Knowledge - AC-ID: KN-003-01"""
import json
import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from functools import wraps
import yaml
import re


class KnowledgeGovernanceManager:
    """Manages governance rules and audit tracking for tier3 knowledge."""
    
    VALID_DOMAINS = [
        "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
        "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
        "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
        "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
        "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
    ]
    
    AC_ID_PATTERN = re.compile(r"^AC-[A-Z]+-\d{3}-\d{2}$")
    ENTRY_ID_PATTERN = re.compile(r"^KE-\d+$")
    
    def __init__(self, knowledge_dir: Optional[Path] = None):
        self.ac_id = "KN-003-01"
        self.knowledge_dir = knowledge_dir or Path(__file__).parent
        self.governance_db = Path(__file__).parent.parent.parent / "state" / "governance.db"
        self.rules = self._load_rules()
        self.domain_rules = self._index_rules_by_domain()
        self.critical_rules = self._get_critical_rules()
        self._init_audit_table()
    
    def _load_rules(self) -> Dict[str, Any]:
        """Load governance rules from YAML file."""
        rules_file = self.knowledge_dir / "governance-rules.yaml"
        if not rules_file.exists():
            raise FileNotFoundError(f"Governance rules file not found: {rules_file}")
        with open(rules_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _index_rules_by_domain(self) -> Dict[str, List[Dict[str, Any]]]:
        """Index rules by domain for fast lookup."""
        domain_rules = {d: [] for d in self.VALID_DOMAINS}
        for rule in self.rules.get("rules", []):
            domain = rule.get("domain")
            if domain in self.VALID_DOMAINS:
                domain_rules[domain].append(rule)
        for domain in self.VALID_DOMAINS:
            domain_rules[domain].extend(self.rules.get("global_rules", []))
        return domain_rules
    
    def _get_critical_rules(self) -> List[Dict[str, Any]]:
        """Get all critical severity rules."""
        critical = []
        for rule in self.rules.get("rules", []):
            if rule.get("severity") == "critical" and rule.get("enabled"):
                critical.append(rule)
        for rule in self.rules.get("global_rules", []):
            if rule.get("severity") == "critical" and rule.get("enabled"):
                critical.append(rule)
        return critical
    
    def _init_audit_table(self) -> None:
        """Initialize audit trail table in governance.db."""
        if not self.governance_db.exists():
            self.governance_db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(str(self.governance_db))
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS knowledge_audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id TEXT NOT NULL,
                action TEXT NOT NULL,
                domain TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                changes TEXT,
                user TEXT,
                ac_id TEXT
            )
        """)
        conn.commit()
        conn.close()
    
    def validate_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """Validate entry against governance rules."""
        errors = []
        if not entry.get("entry_id"):
            errors.append("Missing required field: entry_id")
        elif not self.ENTRY_ID_PATTERN.match(entry.get("entry_id", "")):
            errors.append(f"Invalid entry_id format: {entry.get('entry_id')}")
        domain = entry.get("domain")
        if not domain:
            errors.append("Missing required field: domain")
        elif domain not in self.VALID_DOMAINS:
            errors.append(f"Invalid domain: {domain}")
        if not entry.get("title"):
            errors.append("Missing required field: title")
        ac_ids = entry.get("ac_ids", [])
        if isinstance(ac_ids, list):
            for ac_id in ac_ids:
                if not self.AC_ID_PATTERN.match(ac_id):
                    errors.append(f"Invalid AC-ID format: {ac_id}")
        return {"valid": len(errors) == 0, "errors": errors, "entry_id": entry.get("entry_id"), "domain": domain}
    
    def get_rules_for_domain(self, domain: str) -> List[Dict[str, Any]]:
        """Get all governance rules for a domain."""
        return self.domain_rules.get(domain, []) if domain in self.VALID_DOMAINS else []
    
    def get_critical_rules(self) -> List[Dict[str, Any]]:
        """Get all critical governance rules."""
        return self.critical_rules
    
    def log_entry_change(
        self, entry_id: str, action: str, domain: str,
        details: Optional[Dict[str, Any]] = None, user: Optional[str] = None
    ) -> Dict[str, Any]:
        """Log entry change to audit trail."""
        timestamp = datetime.utcnow().isoformat() + "Z"
        changes = json.dumps(details or {})
        conn = sqlite3.connect(str(self.governance_db))
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO knowledge_audit 
                (entry_id, action, domain, timestamp, changes, user, ac_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (entry_id, action, domain, timestamp, changes, user or "system", self.ac_id))
            conn.commit()
            return {"entry_id": entry_id, "action": action, "domain": domain, "timestamp": timestamp, "changes": changes, "ac_id": self.ac_id}
        finally:
            conn.close()
    
    def get_audit_log(
        self, domain: Optional[str] = None, entry_id: Optional[str] = None,
        action: Optional[str] = None, limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve audit log entries."""
        conn = sqlite3.connect(str(self.governance_db))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        try:
            query = "SELECT * FROM knowledge_audit WHERE 1=1"
            params = []
            if domain:
                query += " AND domain = ?"
                params.append(domain)
            if entry_id:
                query += " AND entry_id = ?"
                params.append(entry_id)
            if action:
                query += " AND action = ?"
                params.append(action)
            query += " ORDER BY timestamp DESC LIMIT ?"
            params.append(limit)
            cursor.execute(query, params)
            return [dict(row) for row in cursor.fetchall()]
        finally:
            conn.close()
    
    def track_update(
        self, entry_id: str, old_entry: Dict[str, Any], new_entry: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Track updates to an entry."""
        changes = {}
        all_keys = set(old_entry.keys()) | set(new_entry.keys())
        for key in all_keys:
            if old_entry.get(key) != new_entry.get(key):
                changes[key] = {"old": old_entry.get(key), "new": new_entry.get(key)}
        domain = new_entry.get("domain", old_entry.get("domain"))
        return self.log_entry_change(entry_id, "UPDATE", domain, {"changed_fields": changes, "field_count": len(changes)})
    
    def validate_on_create(self, func):
        """Decorator to validate entry on creation."""
        @wraps(func)
        def wrapper(entry: Dict[str, Any], *args, **kwargs):
            result = self.validate_entry(entry)
            if not result["valid"]:
                raise ValueError(f"Entry validation failed: {result['errors']}")
            self.log_entry_change(entry.get("entry_id"), "CREATE", entry.get("domain"), entry)
            return func(entry, *args, **kwargs)
        return wrapper
    
    def audit_on_change(self, func):
        """Decorator to audit changes on update."""
        @wraps(func)
        def wrapper(entry_id: str, updates: Dict[str, Any], *args, **kwargs):
            result = func(entry_id, updates, *args, **kwargs)
            self.log_entry_change(entry_id, "UPDATE", updates.get("domain", "UNKNOWN"), updates)
            return result
        return wrapper
