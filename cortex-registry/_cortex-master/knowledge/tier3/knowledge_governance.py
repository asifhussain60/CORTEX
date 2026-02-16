"""
Knowledge Governance Manager - Tier 3.

Manages governance rules for tier3 knowledge ecosystem.
Validates entries, tracks updates, and integrates with audit trail.

AC: KN-003-01 - Tier 3 Knowledge Governance
"""

from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
import yaml
import sqlite3


@dataclass
class GovernanceRule:
    """Represents a governance rule for tier3 knowledge."""
    rule_id: str
    domain: str
    rule_type: str
    description: str
    rule_definition: Dict[str, Any]
    severity: str
    enabled: bool


class KnowledgeGovernanceManager:
    """Manages governance rules for tier3 knowledge entries."""
    
    VALID_DOMAINS = [
        "GOVERNANCE", "INTENT-ROUTING", "HALLUCINATION-PREVENTION",
        "EXECUTION-ORCHESTRATION", "DATA-MANAGEMENT", "OBSERVABILITY",
        "SECURITY", "API-DESIGN", "ML-MODELS", "KNOWLEDGE-CURATION",
        "TESTING-VALIDATION", "DEPLOYMENT", "DOCUMENTATION",
        "PERFORMANCE", "ARCHITECTURE", "ERROR-HANDLING"
    ]
    
    def __init__(self) -> None:
        """Initialize governance manager."""
        self._rules: Dict[str, GovernanceRule] = {}
        self._audit_log: List[Dict[str, Any]] = []
        self._load_rules()
    
    def _load_rules(self) -> None:
        """Load governance rules from YAML file."""
        rules_file = Path(__file__).parent / "governance-rules.yaml"
        if rules_file.exists():
            with open(rules_file, 'r') as f:
                data = yaml.safe_load(f)
                for rule_data in data.get("rules", []):
                    rule = GovernanceRule(
                        rule_id=rule_data["rule_id"],
                        domain=rule_data["domain"],
                        rule_type=rule_data["rule_type"],
                        description=rule_data["description"],
                        rule_definition=rule_data.get("rule_definition", {}),
                        severity=rule_data["severity"],
                        enabled=rule_data.get("enabled", True)
                    )
                    self._rules[rule.rule_id] = rule
    
    def validate_entry(self, entry: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate knowledge entry against governance rules.
        
        Args:
            entry: Entry to validate
            
        Returns:
            Validation result with valid flag and errors list
        """
        errors: List[str] = []
        
        # Check required fields
        required_fields = ["entry_id", "domain", "title"]
        for field in required_fields:
            if field not in entry:
                errors.append(f"Missing required field: {field}")
        
        # Validate domain
        if "domain" in entry and entry["domain"] not in self.VALID_DOMAINS:
            errors.append(f"Invalid domain: {entry['domain']}")
        
        # Validate AC-ID format
        if "ac_ids" in entry:
            for ac_id in entry["ac_ids"]:
                if not self._is_valid_ac_id_format(ac_id):
                    errors.append(f"Invalid AC-ID format: {ac_id}")
        
        return {
            "valid": len(errors) == 0,
            "errors": errors
        }
    
    def _is_valid_ac_id_format(self, ac_id: str) -> bool:
        """Check if AC-ID follows standard format."""
        parts = ac_id.split("-")
        return len(parts) >= 3 and parts[0] == "AC"
    
    def get_rules_for_domain(self, domain: str) -> List[GovernanceRule]:
        """
        Get all governance rules for a specific domain.
        
        Args:
            domain: Domain name
            
        Returns:
            List of rules for the domain
        """
        return [
            rule for rule in self._rules.values()
            if rule.domain == domain and rule.enabled
        ]
    
    def get_critical_rules(self) -> List[GovernanceRule]:
        """
        Get all critical severity rules.
        
        Returns:
            List of critical rules
        """
        return [
            rule for rule in self._rules.values()
            if rule.severity == "critical" and rule.enabled
        ]
    
    def audit_log(self, action: str, entry_id: str, details: Dict[str, Any]) -> None:
        """
        Log action to audit trail.
        
        Args:
            action: Action type (create, update, delete)
            entry_id: Entry ID
            details: Action details
        """
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "action": action,
            "entry_id": entry_id,
            "details": details
        }
        self._audit_log.append(log_entry)
    
    def get_audit_log(self, domain: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get audit log entries.
        
        Args:
            domain: Filter by domain (optional)
            
        Returns:
            List of audit log entries
        """
        if domain is None:
            return self._audit_log
        return [
            entry for entry in self._audit_log
            if entry.get("details", {}).get("domain") == domain
        ]
    
    def track_update(self, entry_id: str, old_data: Dict[str, Any], new_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track updates to knowledge entry.
        
        Args:
            entry_id: Entry ID
            old_data: Previous entry data
            new_data: Updated entry data
            
        Returns:
            Update tracking information
        """
        changed_fields = []
        for key in set(old_data.keys()) | set(new_data.keys()):
            if old_data.get(key) != new_data.get(key):
                changed_fields.append(key)
        
        update_info = {
            "entry_id": entry_id,
            "timestamp": datetime.now().isoformat(),
            "changed_fields": changed_fields,
            "old_data": old_data,
            "new_data": new_data
        }
        
        self.audit_log("update", entry_id, update_info)
        return update_info
    
    def validate(self, entry: Dict[str, Any]) -> bool:
        """
        Validate entry decorator method.
        
        Args:
            entry: Entry to validate
            
        Returns:
            True if valid
        """
        result = self.validate_entry(entry)
        return result["valid"]
    
    def audit(self, action: str, entry_id: str) -> None:
        """
        Audit decorator method.
        
        Args:
            action: Action type
            entry_id: Entry ID
        """
        self.audit_log(action, entry_id, {})


__all__ = ["KnowledgeGovernanceManager", "GovernanceRule"]
